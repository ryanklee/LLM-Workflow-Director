import asyncio
import time
import logging
import uuid
import random
from typing import Dict, Any, List, AsyncGenerator
from unittest.mock import MagicMock
from anthropic import APIStatusError
from src.exceptions import CustomRateLimitError
from functools import lru_cache, wraps
from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def timed_lru_cache(seconds: int, maxsize: int = 128):
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache

class MockClaudeClient:
    class Messages:
        def __init__(self, client):
            self.client = client
            self.client.logger.debug("Initialized Messages class")

        async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any] | AsyncGenerator[Dict[str, Any], None]:
            self.client.logger.debug(f"Messages.create called with model: {model}, max_tokens: {max_tokens}, stream: {stream}")
            return await self.client._create(model, max_tokens, messages, stream)

    def __init__(self, api_key: str = "mock_api_key", base_url: str = "http://localhost:8000", rate_limit: int = 10, reset_time: int = 60, cache_ttl: int = 300, cache_maxsize: int = 100):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.debug(f"Initializing MockClaudeClient {id(self)} with api_key: {api_key[:5]}, base_url: {base_url}, rate_limit: {rate_limit}, reset_time: {reset_time}, cache_ttl: {cache_ttl}, cache_maxsize: {cache_maxsize}")
        
        self.cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)
        
        self.base_url = base_url
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.reset_time = reset_time
        self.calls = 0
        self.last_reset = time.time()
        self.error_mode = False
        self.latency = 0
        self.responses = {}
        self.max_test_tokens = 1000
        self.call_count = 0
        self.error_count = 0
        self.max_errors = 3
        self.messages = self.Messages(self)
        self.context = []
        self.is_shakespearean = False
        self.lock = asyncio.Lock()
        self.logger.debug(f"Finished initialization of MockClaudeClient {id(self)}")

    async def count_tokens(self, text: str) -> int:
        self.logger.debug(f"Counting tokens for text: {text[:50]}...")
        # Simplified token counting for mock purposes
        token_count = len(text.split())
        self.logger.debug(f"Token count: {token_count}")
        return token_count

    async def reset(self):
        self.logger.debug(f"Resetting MockClaudeClient {id(self)}")
        self.calls = 0
        self.last_reset = time.time()
        self.error_mode = False
        self.latency = 0
        self.responses = {}
        self.call_count = 0
        self.error_count = 0
        self.context = []
        self.is_shakespearean = False
        self.logger.debug(f"Finished resetting MockClaudeClient {id(self)}")

    async def set_rate_limit(self, limit: int):
        self.logger.info(f"Setting rate limit to: {limit}")
        self.rate_limit = limit
        self.logger.debug(f"Rate limit updated. New threshold: {self.rate_limit}")

    async def set_error_mode(self, mode: bool):
        self.logger.debug(f"Setting error mode to: {mode}")
        self.error_mode = mode

    async def _check_rate_limit(self):
        current_time = time.time()
        if current_time - self.last_reset >= self.reset_time:
            self.logger.info(f"Resetting call count. Old count: {self.calls}")
            self.calls = 0
            self.last_reset = current_time
        self.calls += 1
        if self.calls > self.rate_limit:
            self.logger.warning(f"Rate limit exceeded. Count: {self.calls}, Threshold: {self.rate_limit}")
            raise CustomRateLimitError("Rate limit exceeded")

    async def reset(self):
        self.logger.debug(f"Resetting MockClaudeClient {id(self)}")
        self.calls = 0
        self.last_reset = time.time()
        self.error_mode = False
        self.latency = 0
        self.responses = {}
        self.call_count = 0
        self.error_count = 0
        self.context = []
        self.logger.debug(f"Finished resetting MockClaudeClient {id(self)}")

    @timed_lru_cache(seconds=300)
    async def _cached_create_message(self, model: str, max_tokens: int, messages: tuple) -> Dict[str, Any]:
        self.logger.debug(f"Cache miss. Generating response for model: {model}, max_tokens: {max_tokens}")
        prompt = messages[-1]['content']
        response = self._generate_response(prompt, model, list(messages))
        if len(response) > max_tokens:
            self.logger.warning(f"Response exceeds max tokens. Truncating. Original length: {len(response)}")
            response = response[:max_tokens] + "..."
        
        wrapped_response = self._apply_response_prefix(response)
        return {
            "id": f"msg_{uuid.uuid4()}",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": wrapped_response}],
            "model": model,
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": sum(len(m["content"]) for m in messages),
                "output_tokens": len(response)
            }
        }

    async def _create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], stream: bool = False) ->  Dict[str, Any] | AsyncGenerator[Dict[str, Any], None]:
        self.logger.debug(f"Creating response for model: {model}, max_tokens: {max_tokens}, stream: {stream}")
        async with self.lock:
            await self._check_rate_limit()
            await asyncio.sleep(self.latency)
            
            self._process_system_message(messages)
            
            if sum(len(m['content']) for m in messages) > self.max_context_length:
                self.logger.warning(f"Total message length exceeds max context length")
                raise ValueError(f"Total message length exceeds maximum context length ({self.max_context_length})")
            
            if self.error_mode:
                self.error_count += 1
                if self.error_count <= self.max_errors:
                    self.logger.error("Simulated API error")
                    raise APIStatusError("Simulated API error", response=MagicMock(), body={})
            
            cache_key = self._generate_cache_key(model, max_tokens, messages)
            cached_response = self.cache.get(cache_key)
            if cached_response:
                self.logger.debug(f"Cache hit for key: {cache_key}")
                return cached_response
            
            self.call_count += 1
            
            if stream:
                async def response_generator():
                    response = await self._cached_create_message(model, max_tokens, tuple(messages))
                    wrapped_response = response['content'][0]['text']
                    for chunk in wrapped_response.split():
                        yield {
                            "type": "content_block_delta",
                            "delta": {
                                "type": "text",
                                "text": chunk
                            }
                        }
                    yield {"type": "message_delta", "delta": {"stop_reason": "end_turn"}}
                return response_generator()
            else:
                response = await self._cached_create_message(model, max_tokens, tuple(messages))
                self.cache[cache_key] = response
                return response

    def _generate_cache_key(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> str:
        return f"{model}:{max_tokens}:{hash(tuple(sorted(message.items())) for message in messages)}"

    def _process_system_message(self, messages: List[Dict[str, str]]) -> None:
        self.logger.info("Processing system message")
        system_message = next((m['content'] for m in messages if m['role'] == 'system'), None)
        if system_message:
            self.logger.info(f"System message found: {system_message[:100]}...")
            self.is_shakespearean = "speak like Shakespeare" in system_message.lower()
            self.logger.info(f"Shakespearean mode set to: {self.is_shakespearean}")
        else:
            self.logger.info("No system message found")
            self.is_shakespearean = False
        self.logger.debug(f"Final Shakespearean mode after processing: {self.is_shakespearean}")
        self.logger.debug(f"System message content: {system_message}")
        self.last_system_message = system_message  # Store the last system message for debugging

    def _generate_response(self, prompt: str, model: str, messages: List[Dict[str, str]]) -> str:
        self.logger.info(f"Generating response for prompt: {prompt[:50]}... using model: {model}")
        
        self._process_system_message(messages)
        self.logger.info(f"Current Shakespearean mode: {self.is_shakespearean}")
        
        context = " ".join(m['content'] for m in messages if m['role'] == 'user')
        self.logger.info(f"Context: {context[:100]}...")
        
        # Check if there's a custom response for this prompt
        response_text = self.responses.get(prompt)
        if response_text:
            self.logger.info(f"Using custom response: {response_text[:50]}...")
        else:
            # Generate a response based on the model and conversation history
            conversation_history = [m['content'] for m in messages if m['role'] in ['user', 'assistant']]
            self.logger.info(f"Generating response based on model: {model}")
            
            if self.is_shakespearean:
                response_text = self._generate_shakespearean_response(prompt)
                self.logger.info(f"Generated Shakespearean response: {response_text[:50]}...")
            else:
                response_text = self._generate_model_specific_response(model, conversation_history)

        # Adjust response length based on the model
        response_text = self._adjust_response_length(response_text, model)

        # Ensure Shakespearean prefix if necessary
        response_text = self._ensure_shakespearean_prefix(response_text)
        self.logger.debug(f"Final generated response for {model}: {response_text}")
        self.last_response = response_text  # Store the last response for debugging
        return response_text

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean:
            if not response_text.startswith("Hark!"):
                response_text = f"Hark! {response_text.lstrip('Hello! ')}"
                self.logger.info(f"Added Shakespearean prefix: {response_text[:50]}...")
            else:
                self.logger.info("Shakespearean prefix already present")
        elif not self.is_shakespearean:
            if not response_text.startswith("Hello!"):
                response_text = f"Hello! {response_text.lstrip('Hark! ')}"
                self.logger.info(f"Added non-Shakespearean prefix: {response_text[:50]}...")
            else:
                self.logger.info("Non-Shakespearean prefix already present")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean:
            if not response_text.startswith("Hark!"):
                response_text = f"Hark! {response_text.lstrip('Hello! ')}"
                self.logger.info(f"Added Shakespearean prefix: {response_text[:50]}...")
            else:
                self.logger.info("Shakespearean prefix already present")
        else:
            if not response_text.startswith("Hello!"):
                response_text = f"Hello! {response_text.lstrip('Hark! ')}"
                self.logger.info(f"Added non-Shakespearean prefix: {response_text[:50]}...")
            else:
                self.logger.info("Non-Shakespearean prefix already present")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        elif not self.is_shakespearean and not response_text.startswith("Hello!"):
            response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Ensured non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    def _generate_model_specific_response(self, model: str, conversation_history: List[str]) -> str:
        if model == 'claude-3-haiku-20240307':
            return f"{' '.join(conversation_history[-1:])[:20]}..."
        elif model == 'claude-3-sonnet-20240229':
            return f"Based on our conversation: {' '.join(conversation_history[-2:])[:40]}..."
        else:  # claude-3-opus-20240229 or default
            return f"Based on our conversation: {' '.join(conversation_history[-3:])}, here's my response: [Generated response]"

    def _adjust_response_length(self, response_text: str, model: str) -> str:
        original_length = len(response_text)
        if model == 'claude-3-haiku-20240307':
            response_text = response_text[:50]  # Shorter response for Haiku
            self.logger.info(f"Truncated Haiku response from {original_length} to {len(response_text)} characters")
        elif model == 'claude-3-sonnet-20240229':
            response_text = response_text[:100]  # Medium-length response for Sonnet
            self.logger.info(f"Truncated Sonnet response from {original_length} to {len(response_text)} characters")
        else:
            self.logger.info(f"Opus response length: {len(response_text)} characters")
        return response_text

    def _generate_shakespearean_response(self, prompt: str) -> str:
        self.logger.info(f"Generating Shakespearean response for prompt: {prompt[:50]}...")
        shakespearean_words = ["thou", "doth", "verily", "forsooth", "prithee", "anon"]
        response = f"Hark! {random.choice(shakespearean_words).capitalize()} {prompt.lower()} "
        response += f"{random.choice(shakespearean_words)} {random.choice(shakespearean_words)} "
        response += f"[Shakespearean response to '{prompt[:20]}...']"
        self.logger.debug(f"Generated Shakespearean response: {response}")
        return response

    def _apply_response_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Applying response prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean:
            if not response_text.startswith("Hark!"):
                response_text = f"Hark! {response_text}"
            self.logger.info(f"Applied Shakespearean prefix: {response_text[:50]}...")
        else:
            if not response_text.startswith("Hello!"):
                response_text = f"Hello! {response_text}"
            self.logger.info(f"Applied non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after prefix application: {response_text[:50]}...")
        return response_text

    def debug_dump(self):
        try:
            state = {
                "is_shakespearean": self.is_shakespearean,
                "last_response": getattr(self, 'last_response', None),
                "last_system_message": getattr(self, 'last_system_message', None),
                "rate_limit_threshold": self.rate_limit_threshold,
                "rate_limit_reset_time": self.rate_limit_reset_time,
                "call_count": self.call_count,
                "last_reset_time": self.last_reset_time,
                "error_mode": self.error_mode,
                "responses_count": len(self.responses)
            }
            self.logger.debug(f"MockClaudeClient state: {state}")
            return state
        except Exception as e:
            self.logger.error(f"Error in debug_dump: {str(e)}", exc_info=True)
            raise

    async def debug_dump(self):
        self.logger.debug("Starting debug_dump method")
        try:
            state = {
                "api_key": self.api_key[:5] + "...",
                "rate_limit_threshold": self.rate_limit_threshold,
                "rate_limit_reset_time": self.rate_limit_reset_time,
                "call_count": self.call_count,
                "last_reset_time": self.last_reset_time,
                "error_mode": self.error_mode,
                "is_shakespearean": self.is_shakespearean,
                "responses_count": len(self.responses),
                "shakespearean_methods": {
                    "_process_system_message": hasattr(self, '_process_system_message'),
                    "_generate_shakespearean_response": hasattr(self, '_generate_shakespearean_response'),
                    "_apply_response_prefix": hasattr(self, '_apply_response_prefix'),
                    "_ensure_shakespearean_prefix": hasattr(self, '_ensure_shakespearean_prefix'),
                    "_set_shakespearean_mode": hasattr(self, '_set_shakespearean_mode')
                },
                "last_response": getattr(self, 'last_response', None),
                "shakespearean_mode_tracking": {
                    "is_shakespearean": self.is_shakespearean,
                    "last_system_message": getattr(self, 'last_system_message', None),
                    "last_shakespearean_response": getattr(self, 'last_shakespearean_response', None)
                },
                "method_implementations": {
                    "_ensure_shakespearean_prefix": self._ensure_shakespearean_prefix.__code__.co_code,
                    "_generate_shakespearean_response": self._generate_shakespearean_response.__code__.co_code,
                    "_apply_response_prefix": self._apply_response_prefix.__code__.co_code if hasattr(self, '_apply_response_prefix') else None
                },
                "shakespearean_prefix_stats": {
                    "total_calls": getattr(self, '_ensure_shakespearean_prefix_calls', 0),
                    "prefixes_added": getattr(self, '_ensure_shakespearean_prefix_added', 0)
                },
                "response_generation_flow": {
                    "system_message_processed": getattr(self, 'system_message_processed', False),
                    "shakespearean_mode_set": getattr(self, 'shakespearean_mode_set', False),
                    "response_generated": getattr(self, 'response_generated', False),
                    "prefix_ensured": getattr(self, 'prefix_ensured', False)
                },
                "cache_info": {
                    "currsize": len(self.cache),
                    "maxsize": self.cache.maxsize,
                    "ttl": self.cache.ttl
                }
            }
            self.logger.debug(f"Debug dump state: {state}")
            return state
        except Exception as e:
            self.logger.error(f"Error in debug_dump: {str(e)}", exc_info=True)
            raise

    def bypass_cache(self):
        self.cache.clear()
        self.logger.info("Cache bypassed and cleared")

    async def debug_dump(self):
        self.logger.debug("Starting debug_dump method")
        try:
            state = {
                "api_key": self.api_key[:5] + "...",
                "rate_limit_threshold": self.rate_limit_threshold,
                "rate_limit_reset_time": self.rate_limit_reset_time,
                "call_count": self.call_count,
                "last_reset_time": self.last_reset_time,
                "error_mode": self.error_mode,
                "is_shakespearean": self.is_shakespearean,
                "responses_count": len(self.responses),
                "shakespearean_methods": {
                    "_process_system_message": hasattr(self, '_process_system_message'),
                    "_generate_shakespearean_response": hasattr(self, '_generate_shakespearean_response'),
                    "_apply_response_prefix": hasattr(self, '_apply_response_prefix'),
                    "_ensure_shakespearean_prefix": hasattr(self, '_ensure_shakespearean_prefix')
                },
                "last_response": getattr(self, 'last_response', None),
                "shakespearean_mode_tracking": {
                    "is_shakespearean": self.is_shakespearean,
                    "last_system_message": getattr(self, 'last_system_message', None),
                    "last_shakespearean_response": getattr(self, 'last_shakespearean_response', None)
                },
                "method_implementations": {
                    "_ensure_shakespearean_prefix": self._ensure_shakespearean_prefix.__code__.co_code,
                    "_generate_shakespearean_response": self._generate_shakespearean_response.__code__.co_code,
                    "_apply_response_prefix": self._apply_response_prefix.__code__.co_code
                }
            }
            self.logger.debug(f"Debug dump state: {state}")
            return state
        except Exception as e:
            self.logger.error(f"Error in debug_dump: {str(e)}", exc_info=True)
            raise

    async def _check_rate_limit(self):
        current_time = time.time()
        if current_time - self.last_reset_time >= self.rate_limit_reset_time:
            self.logger.info(f"Resetting call count. Old count: {self.call_count}")
            self.call_count = 0
            self.last_reset_time = current_time
        if self.call_count >= self.rate_limit_threshold:
            self.logger.warning(f"Rate limit exceeded. Count: {self.call_count}, Threshold: {self.rate_limit_threshold}")
            raise CustomRateLimitError("Rate limit exceeded")

    @timed_lru_cache(seconds=300)
    async def count_tokens(self, text: str) -> int:
        # Simplified token counting for mock purposes
        token_count = len(text.split())
        self.logger.debug(f"Counted {token_count} tokens for text: {text[:50]}...")
        return token_count

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response

    async def set_error_mode(self, mode: bool):
        self.logger.debug(f"Setting error mode to: {mode}")
        self.error_mode = mode

    async def set_latency(self, latency: float):
        self.logger.debug(f"Setting latency to: {latency}")
        self.latency = latency

    async def set_rate_limit(self, threshold: int):
        self.logger.debug(f"Setting rate limit threshold to: {threshold}")
        self.rate_limit_threshold = threshold

    async def reset(self):
        self.logger.debug(f"Resetting MockClaudeClient {id(self)}")
        self.calls = 0
        self.last_reset = asyncio.get_event_loop().time()
        self.error_mode = False
        self.latency = 0.1
        self.responses = {}
        self.call_count = 0
        self.error_count = 0
        self.last_reset_time = time.time()
        self.is_shakespearean = False
        self.logger.debug(f"Finished resetting MockClaudeClient {id(self)}")

    async def get_call_count(self):
        self.logger.debug(f"Current call count: {self.call_count}")
        return self.call_count

    async def get_error_count(self):
        self.logger.debug(f"Current error count: {self.error_count}")
        return self.error_count
import pytest
from src.mock_claude_client import MockClaudeClient

@pytest.mark.asyncio
async def test_create_message():
    client = MockClaudeClient()
    messages = [{"role": "user", "content": "Hello, Claude!"}]
    response = await client.messages.create("claude-3-opus-20240229", 100, messages)
    
    assert response["role"] == "assistant"
    assert isinstance(response["content"], list)
    assert response["content"][0]["type"] == "text"
    assert "Mock response to: Hello, Claude!" in response["content"][0]["text"]

@pytest.mark.asyncio
async def test_count_tokens():
    client = MockClaudeClient()
    text = "This is a test message with 8 tokens."
    result = await client.count_tokens(text)
    
    assert isinstance(result, int)
    assert result == 8

@pytest.mark.asyncio
async def test_rate_limiting():
    client = MockClaudeClient()
    messages = [{"role": "user", "content": "Test message"}]
    
    # Make 10 requests (should be within rate limit)
    for _ in range(10):
        await client.messages.create("claude-3-opus-20240229", 100, messages)
    
    # The 11th request should raise an exception
    with pytest.raises(Exception, match="Rate limit exceeded"):
        await client.messages.create("claude-3-opus-20240229", 100, messages)

@pytest.mark.asyncio
async def test_error_simulation():
    client = MockClaudeClient()
    messages = [{"role": "user", "content": "Test message"}]
    
    # Set error mode
    await client.set_error_mode(True)
    
    # The next request should raise an APIStatusError
    with pytest.raises(Exception, match="Simulated API error"):
        await client.messages.create("claude-3-opus-20240229", 100, messages)

@pytest.mark.asyncio
async def test_reset():
    client = MockClaudeClient()
    messages = [{"role": "user", "content": "Test message"}]
    
    # Make some requests
    for _ in range(5):
        await client.messages.create("claude-3-opus-20240229", 100, messages)
    
    assert client.call_count == 5
    
    await client.reset()
    
    assert client.call_count == 0
    assert client.error_count == 0
    assert client.calls == 0

@pytest.mark.asyncio
async def test_set_response():
    client = MockClaudeClient()
    custom_prompt = "Custom prompt"
    custom_response = "Custom response"
    
    await client.set_response(custom_prompt, custom_response)
    
    messages = [{"role": "user", "content": custom_prompt}]
    response = await client.messages.create("claude-3-opus-20240229", 100, messages)
    
    assert custom_response in response["content"][0]["text"]

@pytest.mark.asyncio
async def test_shakespearean_mode():
    client = MockClaudeClient()
    client.is_shakespearean = True
    
    messages = [{"role": "user", "content": "Hello, Claude!"}]
    response = await client.messages.create("claude-3-opus-20240229", 100, messages)
    
    assert response["content"][0]["text"].startswith("Hark!")

@pytest.mark.asyncio
async def test_streaming_response():
    client = MockClaudeClient()
    messages = [{"role": "user", "content": "Hello, Claude!"}]
    
    async for chunk in await client.messages.create("claude-3-opus-20240229", 100, messages, stream=True):
        assert "type" in chunk
        if chunk["type"] == "content_block_delta":
            assert "delta" in chunk
            assert "text" in chunk["delta"]
        elif chunk["type"] == "message_delta":
            assert "delta" in chunk
            assert "stop_reason" in chunk["delta"]
import asyncio
from typing import Dict, List, Optional

import asyncio
from typing import Dict, List, Any
from anthropic import APIStatusError, RateLimitError
from src.exceptions import CustomRateLimitError

class Messages:
    def __init__(self, client):
        self.client = client

    async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        return await self.client.create(model, max_tokens, messages)

class Messages:
    def __init__(self, client):
        self.client = client

    async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        return await self.client.create(model, max_tokens, messages)

class Messages:
    def __init__(self, client):
        self.client = client

    async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        return await self.client._create(model, max_tokens, messages)

class Messages:
    def __init__(self, client):
        self.client = client

    async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        return await self.client._create(model, max_tokens, messages)

import asyncio
import time
import logging
import uuid
import random
from typing import Dict, Any, List, AsyncGenerator
from unittest.mock import MagicMock
from anthropic import APIStatusError
from src.exceptions import CustomRateLimitError
from cachetools import TTLCache
from threading import Lock

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockClaudeClient:
    class Messages:
        def __init__(self, client):
            self.client = client
            self.client.logger.debug("Initialized Messages class")

        async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any] | AsyncGenerator[Dict[str, Any], None]:
            self.client.logger.debug(f"Messages.create called with model: {model}, max_tokens: {max_tokens}, stream: {stream}")
            return await self.client._create(model, max_tokens, messages, stream)

    def __init__(self, api_key: str = "mock_api_key", rate_limit: int = 10, reset_time: int = 60, cache_ttl: int = 300, cache_maxsize: int = 100):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.debug(f"Initializing MockClaudeClient {id(self)} with api_key: {api_key[:5]}, rate_limit: {rate_limit}, reset_time: {reset_time}")
        
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.reset_time = reset_time
        self.calls = 0
        self.last_reset = time.time()
        self.error_mode = False
        self.latency = 0
        self.responses = {}
        self.max_test_tokens = 1000
        self.call_count = 0
        self.error_count = 0
        self.max_errors = 3
        self.messages = self.Messages(self)
        self.context = []
        self.is_shakespearean = False
        self.lock = asyncio.Lock()
        self.cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)
        self.logger.debug(f"Finished initialization of MockClaudeClient {id(self)}")

    async def set_rate_limit(self, limit: int):
        self.logger.debug(f"Setting rate limit to: {limit}")
        self.rate_limit = limit

    async def set_error_mode(self, mode: bool):
        self.logger.debug(f"Setting error mode to: {mode}")
        self.error_mode = mode

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting custom response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response

    async def set_latency(self, latency: float):
        self.logger.debug(f"Setting latency to: {latency}")
        self.latency = latency

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        elif not self.is_shakespearean and not response_text.startswith("Hello!"):
            response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Ensured non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    async def _create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any] | AsyncGenerator[Dict[str, Any], None]:
        self.logger.debug(f"Creating response for model: {model}, max_tokens: {max_tokens}, stream: {stream}")
        try:
            await self._check_rate_limit()
        except CustomRateLimitError as e:
            self.logger.error(f"Rate limit exceeded: {str(e)}")
            raise

        await asyncio.sleep(self.latency)

        if self.error_mode:
            self.error_count += 1
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                error_response = MagicMock()
                error_response.status_code = 500
                error_response.json.return_value = {"error": {"type": "server_error", "message": "Simulated API error"}}
                raise APIStatusError("Simulated API error", response=error_response)

        self.context.extend(messages)
        prompt = messages[-1]['content']
        self.logger.debug(f"Received prompt: {prompt[:50]}...")
        if len(prompt) > self.max_test_tokens:
            self.logger.warning(f"Prompt exceeds max tokens. Prompt length: {len(prompt)}, Max tokens: {self.max_test_tokens}")
            raise ValueError(f"Test input exceeds maximum allowed tokens ({self.max_test_tokens})")

        response = self._generate_response(prompt, model, messages)
        if len(response) > max_tokens:
            self.logger.warning(f"Response exceeds max tokens. Truncating. Original length: {len(response)}")
            response = response[:max_tokens] + "..."

        self.call_count += 1
        self.logger.debug(f"Returning response: {response[:50]}...")

        result = {
            "id": f"msg_{uuid.uuid4()}",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": response}],
            "model": model,
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": sum(len(m["content"]) for m in messages),
                "output_tokens": len(response)
            }
        }

        if stream:
            async def response_generator():
                for chunk in response.split():
                    yield {"type": "content_block_delta", "delta": {"type": "text", "text": chunk}}
                yield {"type": "message_delta", "delta": {"stop_reason": "end_turn"}}
            return response_generator()
        else:
            return result

    def _generate_response(self, prompt: str, model: str, messages: List[Dict[str, str]]) -> str:
        self.logger.debug(f"Generating response for prompt: {prompt[:50]}... using model: {model}")
        
        self._process_system_message(messages)
        self.logger.debug(f"Current Shakespearean mode: {self.is_shakespearean}")
        
        context = " ".join(m['content'] for m in messages if m['role'] == 'user')
        self.logger.debug(f"Context: {context[:100]}...")
        
        response_text = self.responses.get(prompt)
        if response_text:
            self.logger.debug(f"Using custom response: {response_text[:50]}...")
        else:
            conversation_history = [m['content'] for m in messages if m['role'] in ['user', 'assistant']]
            self.logger.debug(f"Generating response based on model: {model}")
            
            if self.is_shakespearean:
                response_text = self._generate_shakespearean_response(prompt)
                self.logger.debug(f"Generated Shakespearean response: {response_text[:50]}...")
            elif model == 'claude-3-haiku-20240307':
                response_text = f"{' '.join(conversation_history[-1:])[:20]}..."
            elif model == 'claude-3-sonnet-20240229':
                response_text = f"Based on our conversation: {' '.join(conversation_history[-2:])[:40]}..."
            else:  # claude-3-opus-20240229 or default
                response_text = f"Based on our conversation: {' '.join(conversation_history[-3:])}, here's my response: [Generated response]"

        response_text = self._adjust_response_length(response_text, model)
        response_text = self._ensure_shakespearean_prefix(response_text)
        
        self.logger.debug(f"Final generated response for {model}: {response_text[:50]}...")
        return response_text

    def _process_system_message(self, messages: List[Dict[str, str]]) -> None:
        self.logger.debug("Processing system message")
        system_message = next((m['content'] for m in messages if m['role'] == 'system'), None)
        if system_message:
            self.logger.info(f"System message found: {system_message[:100]}...")
            self.is_shakespearean = "speak like Shakespeare" in system_message.lower()
            self.logger.info(f"Shakespearean mode set to: {self.is_shakespearean}")
        else:
            self.logger.info("No system message found")
            self.is_shakespearean = False
        self.logger.debug(f"Final Shakespearean mode after processing: {self.is_shakespearean}")

    def _generate_shakespearean_response(self, prompt: str) -> str:
        self.logger.debug(f"Generating Shakespearean response for prompt: {prompt[:50]}...")
        shakespearean_words = ["thou", "doth", "verily", "forsooth", "prithee", "anon"]
        response = f"Hark! {random.choice(shakespearean_words).capitalize()} {prompt.lower()} "
        response += f"{random.choice(shakespearean_words)} {random.choice(shakespearean_words)} "
        response += f"[Shakespearean response to '{prompt[:20]}...']"
        self.logger.debug(f"Generated Shakespearean response: {response}")
        return response

    def _adjust_response_length(self, response_text: str, model: str) -> str:
        original_length = len(response_text)
        if model == 'claude-3-haiku-20240307':
            response_text = response_text[:50]  # Shorter response for Haiku
            self.logger.debug(f"Truncated Haiku response from {original_length} to {len(response_text)} characters")
        elif model == 'claude-3-sonnet-20240229':
            response_text = response_text[:100]  # Medium-length response for Sonnet
            self.logger.debug(f"Truncated Sonnet response from {original_length} to {len(response_text)} characters")
        else:
            self.logger.debug(f"Opus response length: {len(response_text)} characters")
        return response_text

    async def _check_rate_limit(self):
        current_time = time.time()
        if current_time - self.last_reset > self.reset_time:
            self.calls = 0
            self.last_reset = current_time
            self.logger.debug(f"Rate limit reset. Calls: {self.calls}")

        self.calls += 1
        self.logger.debug(f"Rate limit check. Calls: {self.calls}, Limit: {self.rate_limit}")
        if self.calls > self.rate_limit:
            self.logger.warning(f"Rate limit exceeded. Calls: {self.calls}, Limit: {self.rate_limit}")
            raise CustomRateLimitError("Rate limit exceeded")
        elif self.calls == self.rate_limit:
            self.logger.warning(f"Rate limit reached. Calls: {self.calls}, Limit: {self.rate_limit}")

    async def reset(self):
        self.logger.debug(f"Resetting MockClaudeClient {id(self)}")
        self.calls = 0
        self.last_reset = time.time()
        self.error_mode = False
        self.latency = 0
        self.responses = {}
        self.call_count = 0
        self.error_count = 0
        self.context = []
        self.is_shakespearean = False
        self.logger.debug(f"Finished resetting MockClaudeClient {id(self)}")

    async def count_tokens(self, text: str) -> int:
        # Simplified token counting for mock purposes
        token_count = len(text.split())
        self.logger.debug(f"Token count for text: {token_count}")
        return token_count

    async def debug_dump(self):
        self.logger.debug("Starting debug_dump method")
        try:
            state = {
                "api_key": self.api_key[:5] + "...",
                "rate_limit": self.rate_limit,
                "reset_time": self.reset_time,
                "calls": self.calls,
                "last_reset": self.last_reset,
                "error_mode": self.error_mode,
                "latency": self.latency,
                "max_test_tokens": self.max_test_tokens,
                "call_count": self.call_count,
                "error_count": self.error_count,
                "max_errors": self.max_errors,
                "context_length": len(self.context),
                "responses_count": len(self.responses),
                "is_shakespearean": self.is_shakespearean
            }
            self.logger.debug(f"Debug dump state: {state}")
            return state
        except Exception as e:
            self.logger.error(f"Error in debug_dump: {str(e)}", exc_info=True)
            raise

    def __str__(self):
        return f"MockClaudeClient(call_count={self.call_count}, error_count={self.error_count}, error_mode={self.error_mode})"

    def __repr__(self):
        return self.__str__()

    def _process_system_message(self, messages: List[Dict[str, str]]) -> None:
        self.logger.debug("Processing system message")
        system_message = next((m['content'] for m in messages if m['role'] == 'system'), None)
        if system_message:
            self.logger.info(f"System message found: {system_message[:100]}...")
            shakespearean_score = self._calculate_shakespearean_score(system_message)
            self._set_shakespearean_mode(shakespearean_score > 0.5)
        else:
            self.logger.info("No system message found")
            self._set_shakespearean_mode(False)
        self.logger.debug(f"Shakespearean mode after processing: {self.is_shakespearean}")

    def _calculate_shakespearean_score(self, message: str) -> float:
        shakespearean_keywords = ["shakespeare", "elizabethan", "bard", "iambic pentameter", "sonnet", "thou", "thee", "thy", "hark"]
        message_lower = message.lower()
        score = sum(keyword in message_lower for keyword in shakespearean_keywords) / len(shakespearean_keywords)
        self.logger.debug(f"Calculated Shakespearean score: {score}")
        return score

    def _set_shakespearean_mode(self, is_shakespearean: bool) -> None:
        self.is_shakespearean = is_shakespearean
        self.logger.info(f"Shakespearean mode set to: {self.is_shakespearean}")

    def _apply_response_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Applying response prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean:
            response_text = f"Hark! {response_text.lstrip('Hark! ').lstrip('Hello! ')}"
            self.logger.info(f"Applied Shakespearean prefix: {response_text[:50]}...")
        else:
            response_text = f"Hello! {response_text.lstrip('Hark! ').lstrip('Hello! ')}"
            self.logger.info(f"Applied non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after prefix application: {response_text[:50]}...")
        return response_text

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    async def _create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any] | AsyncGenerator[Dict[str, Any], None]:
        self.logger.info(f"Creating response for model: {model}, max_tokens: {max_tokens}, stream: {stream}")
        try:
            await self._check_rate_limit()
        except CustomRateLimitError as e:
            self.logger.error(f"Rate limit exceeded: {str(e)}")
            raise

        await asyncio.sleep(self.latency)

        if self.error_mode:
            self.error_count += 1
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                error_response = MagicMock()
                error_response.status_code = 500
                error_response.json.return_value = {"error": {"type": "server_error", "message": "Simulated API error"}}
                raise APIStatusError("Simulated API error", response=error_response)

        self.context.extend(messages)
        self._process_system_message(messages)
        prompt = messages[-1]['content']
        self.logger.info(f"Received prompt: {prompt[:50]}...")
        if len(prompt) > self.max_test_tokens:
            self.logger.warning(f"Prompt exceeds max tokens. Prompt length: {len(prompt)}, Max tokens: {self.max_test_tokens}")
            raise ValueError(f"Test input exceeds maximum allowed tokens ({self.max_test_tokens})")

        self.logger.debug(f"Generating response with messages: {messages}")
        response = self._generate_response(prompt, model, messages)
        if len(response) > max_tokens:
            self.logger.warning(f"Response exceeds max tokens. Truncating. Original length: {len(response)}")
            response = response[:max_tokens] + "..."

        self.call_count += 1
        self.logger.info(f"Returning response: {response[:50]}...")

        result = {
            "id": f"msg_{uuid.uuid4()}",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": response}],
            "model": model,
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": sum(len(m["content"]) for m in messages),
                "output_tokens": len(response)
            }
        }

        if stream:
            async def response_generator():
                for chunk in response.split():
                    yield {"type": "content_block_delta", "delta": {"type": "text", "text": chunk}}
                yield {"type": "message_delta", "delta": {"stop_reason": "end_turn"}}
            return response_generator()
        else:
            return result

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        elif not self.is_shakespearean and not response_text.startswith("Hello!"):
            response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Ensured non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    def _generate_response(self, prompt: str, model: str, messages: List[Dict[str, str]]) -> str:
        self.logger.info(f"Generating response for prompt: {prompt[:50]}... using model: {model}")
        
        self._process_system_message(messages)
        self.logger.info(f"Current Shakespearean mode: {self.is_shakespearean}")
        
        context = " ".join(m['content'] for m in messages if m['role'] == 'user')
        self.logger.info(f"Context: {context[:100]}...")
        
        # Check if there's a custom response for this prompt
        response_text = self.responses.get(prompt)
        if response_text:
            self.logger.info(f"Using custom response: {response_text[:50]}...")
        else:
            # Generate a response based on the model and conversation history
            conversation_history = [m['content'] for m in messages if m['role'] in ['user', 'assistant']]
            self.logger.info(f"Generating response based on model: {model}")
            
            if self.is_shakespearean:
                response_text = self._generate_shakespearean_response(prompt)
                self.logger.info(f"Generated Shakespearean response: {response_text[:50]}...")
            elif model == 'claude-3-haiku-20240307':
                response_text = f"{' '.join(conversation_history[-1:])[:20]}..."
            elif model == 'claude-3-sonnet-20240229':
                response_text = f"Based on our conversation: {' '.join(conversation_history[-2:])[:40]}..."
            else:  # claude-3-opus-20240229 or default
                response_text = f"Based on our conversation: {' '.join(conversation_history[-3:])}, here's my response: [Generated response]"

        # Adjust response length based on the model
        original_length = len(response_text)
        if model == 'claude-3-haiku-20240307':
            response_text = response_text[:50]  # Shorter response for Haiku
            self.logger.info(f"Truncated Haiku response from {original_length} to {len(response_text)} characters")
        elif model == 'claude-3-sonnet-20240229':
            response_text = response_text[:100]  # Medium-length response for Sonnet
            self.logger.info(f"Truncated Sonnet response from {original_length} to {len(response_text)} characters")
        else:
            self.logger.info(f"Opus response length: {len(response_text)} characters")

        # Apply response prefix and ensure Shakespearean prefix
        response_text = self._apply_response_prefix(response_text)
        self.logger.debug(f"Final generated response for {model}: {response_text}")
        self.last_response = response_text  # Store the last response for debugging
        return response_text

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        elif not self.is_shakespearean and not response_text.startswith("Hello!"):
            response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Ensured non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        elif not self.is_shakespearean and not response_text.startswith("Hello!"):
            response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Ensured non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        elif not self.is_shakespearean and not response_text.startswith("Hello!"):
            response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Ensured non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        elif not self.is_shakespearean and not response_text.startswith("Hello!"):
            response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Ensured non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Mode: {self.is_shakespearean}")
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
        elif not self.is_shakespearean and not response_text.startswith("Hello!"):
            response_text = f"Hello! {response_text.lstrip('Hark! ')}"
        self.logger.debug(f"Final response: {response_text[:50]}...")
        return response_text

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        elif not self.is_shakespearean and not response_text.startswith("Hello!"):
            response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Ensured non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        elif not self.is_shakespearean and not response_text.startswith("Hello!"):
            response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Ensured non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        elif not self.is_shakespearean and not response_text.startswith("Hello!"):
            response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Ensured non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    def _generate_shakespearean_response(self, prompt: str) -> str:
        self.logger.info(f"Generating Shakespearean response for prompt: {prompt[:50]}...")
        shakespearean_words = ["thou", "doth", "verily", "forsooth", "prithee", "anon"]
        response = f"Hark! {random.choice(shakespearean_words).capitalize()} {prompt.lower()} "
        response += f"{random.choice(shakespearean_words)} {random.choice(shakespearean_words)} "
        response += f"[Shakespearean response to '{prompt[:20]}...']"
        self.logger.debug(f"Generated Shakespearean response: {response}")
        return response

    def _apply_response_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Applying response prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean:
            response_text = f"Hark! {response_text.lstrip('Hark! ').lstrip('Hello! ')}"
            self.logger.info(f"Applied Shakespearean prefix: {response_text[:50]}...")
        else:
            response_text = f"Hello! {response_text.lstrip('Hark! ').lstrip('Hello! ')}"
            self.logger.info(f"Applied non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after prefix application: {response_text[:50]}...")
        return response_text

    def _apply_response_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Applying response prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean:
            response_text = f"Hark! {response_text.lstrip('Hark! ').lstrip('Hello! ')}"
            self.logger.info(f"Applied Shakespearean prefix: {response_text[:50]}...")
        else:
            response_text = f"Hello! {response_text.lstrip('Hark! ').lstrip('Hello! ')}"
            self.logger.info(f"Applied non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after prefix application: {response_text[:50]}...")
        return response_text

    async def debug_dump(self):
        self.logger.debug("Starting debug_dump method")
        try:
            state = {
                "api_key": self.api_key[:5] + "...",
                "rate_limit_threshold": self.rate_limit_threshold,
                "rate_limit_reset_time": self.rate_limit_reset_time,
                "call_count": self.call_count,
                "last_reset_time": self.last_reset_time,
                "error_mode": self.error_mode,
                "is_shakespearean": self.is_shakespearean,
                "responses_count": len(self.responses),
                "shakespearean_methods": {
                    "_process_system_message": hasattr(self, '_process_system_message'),
                    "_generate_shakespearean_response": hasattr(self, '_generate_shakespearean_response'),
                    "_apply_response_prefix": hasattr(self, '_apply_response_prefix'),
                    "_ensure_shakespearean_prefix": hasattr(self, '_ensure_shakespearean_prefix'),
                    "_set_shakespearean_mode": hasattr(self, '_set_shakespearean_mode')
                },
                "last_response": getattr(self, 'last_response', None),
                "shakespearean_mode_tracking": {
                    "is_shakespearean": self.is_shakespearean,
                    "last_system_message": getattr(self, 'last_system_message', None),
                    "last_shakespearean_response": getattr(self, 'last_shakespearean_response', None)
                },
                "method_implementations": {
                    "_ensure_shakespearean_prefix": self._ensure_shakespearean_prefix.__code__.co_code,
                    "_generate_shakespearean_response": self._generate_shakespearean_response.__code__.co_code,
                    "_apply_response_prefix": self._apply_response_prefix.__code__.co_code
                },
                "shakespearean_prefix_stats": {
                    "total_calls": getattr(self, '_ensure_shakespearean_prefix_calls', 0),
                    "prefixes_added": getattr(self, '_ensure_shakespearean_prefix_added', 0)
                }
            }
            self.logger.debug(f"Debug dump state: {state}")
            return state
        except Exception as e:
            self.logger.error(f"Error in debug_dump: {str(e)}", exc_info=True)
            raise

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        elif not self.is_shakespearean and not response_text.startswith("Hello!"):
            response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Ensured non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    async def set_rate_limit(self, limit: int):
        self.logger.debug(f"Setting rate limit to: {limit}")
        self.rate_limit = limit

    async def set_error_mode(self, mode: bool):
        self.logger.debug(f"Setting error mode to: {mode}")
        self.error_mode = mode

    async def set_latency(self, latency: float):
        self.logger.debug(f"Setting latency to: {latency}")
        self.latency = latency

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting custom response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response
        self.logger.debug(f"Custom response set successfully for prompt: {prompt[:50]}...")

    def _generate_response(self, prompt: str, model: str, messages: List[Dict[str, str]]) -> str:
        self.logger.info(f"Generating response for prompt: {prompt[:50]}... using model: {model}")
        self.logger.debug(f"Full messages: {messages}")
        
        system_message = next((m['content'] for m in messages if m['role'] == 'system'), None)
        self.logger.debug(f"System message: {system_message}")
        
        is_shakespearean = False
        if system_message:
            is_shakespearean = "speak like Shakespeare" in system_message.lower()
            self.logger.info(f"Shakespearean mode detected in system message: {is_shakespearean}")
        
        context = " ".join(m['content'] for m in messages if m['role'] == 'user')
        self.logger.info(f"Context: {context[:100]}...")
        
        # Check if there's a custom response for this prompt
        response_text = self.responses.get(prompt)
        if response_text:
            self.logger.info(f"Using custom response: {response_text[:50]}...")
        else:
            # Generate a response based on the model and conversation history
            conversation_history = [m['content'] for m in messages if m['role'] in ['user', 'assistant']]
            self.logger.info(f"Generating response based on model: {model}")
            
            if is_shakespearean:
                response_text = self._generate_shakespearean_response(prompt)
                self.logger.info(f"Generated Shakespearean response: {response_text[:50]}...")
            else:
                if model == 'claude-3-haiku-20240307':
                    response_text = f"{' '.join(conversation_history[-1:])[:20]}..."
                elif model == 'claude-3-sonnet-20240229':
                    response_text = f"{' '.join(conversation_history[-2:])[:40]}..."
                else:  # claude-3-opus-20240229 or default
                    response_text = f"{' '.join(conversation_history[-3:])[:60]}..."

        # Adjust response length based on the model
        original_length = len(response_text)
        if model == 'claude-3-haiku-20240307':
            response_text = response_text[:50]  # Shorter response for Haiku
            self.logger.info(f"Truncated Haiku response from {original_length} to {len(response_text)} characters")
        elif model == 'claude-3-sonnet-20240229':
            response_text = response_text[:100]  # Medium-length response for Sonnet
            self.logger.info(f"Truncated Sonnet response from {original_length} to {len(response_text)} characters")
        else:
            self.logger.info(f"Opus response length: {len(response_text)} characters")

        # Ensure Shakespearean responses always start with "Hark!" and non-Shakespearean with "Hello!"
        if is_shakespearean:
            response_text = f"Hark! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Final Shakespearean response: {response_text[:50]}...")
        else:
            response_text = f"Hello! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Final non-Shakespearean response: {response_text[:50]}...")

        self.logger.debug(f"Final generated response for {model}: {response_text}")
        return response_text

    def _generate_shakespearean_response(self, prompt: str) -> str:
        self.logger.info(f"Generating Shakespearean response for prompt: {prompt[:50]}...")
        shakespearean_words = ["thou", "doth", "verily", "forsooth", "prithee", "anon"]
        response = f"Hark! {random.choice(shakespearean_words).capitalize()} {prompt.lower()} "
        response += f"{random.choice(shakespearean_words)} {random.choice(shakespearean_words)} "
        response += f"[Shakespearean response to '{prompt[:20]}...']"
        self.logger.debug(f"Generated Shakespearean response: {response}")
        return response

    def _generate_shakespearean_response(self, prompt: str) -> str:
        self.logger.info(f"Generating Shakespearean response for prompt: {prompt[:50]}...")
        shakespearean_words = ["thou", "doth", "verily", "forsooth", "prithee", "anon"]
        response = f"{random.choice(shakespearean_words).capitalize()} {prompt.lower()} "
        response += f"{random.choice(shakespearean_words)} {random.choice(shakespearean_words)} "
        response += f"[Shakespearean response to '{prompt[:20]}...']"
        self.logger.debug(f"Generated Shakespearean response: {response}")
        return response

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting custom response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response
        self.logger.debug(f"Custom response set successfully for prompt: {prompt[:50]}...")

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting custom response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response
        self.logger.debug(f"Custom response set successfully for prompt: {prompt[:50]}...")

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting custom response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response

    async def set_rate_limit(self, limit: int):
        self.logger.debug(f"Setting rate limit to: {limit}")
        self.rate_limit = limit

    async def set_error_mode(self, mode: bool):
        self.logger.debug(f"Setting error mode to: {mode}")
        self.error_mode = mode

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response

    async def set_latency(self, latency: float):
        self.logger.debug(f"Setting latency to: {latency}")
        self.latency = latency

    async def set_rate_limit(self, limit: int):
        self.logger.debug(f"Setting rate limit to: {limit}")
        self.rate_limit = limit

    async def set_error_mode(self, mode: bool):
        self.logger.debug(f"Setting error mode to: {mode}")
        self.error_mode = mode

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response

    async def set_latency(self, latency: float):
        self.logger.debug(f"Setting latency to: {latency}")
        self.latency = latency

    async def set_rate_limit(self, limit: int):
        self.logger.debug(f"Setting rate limit to: {limit}")
        self.rate_limit = limit

    async def set_error_mode(self, mode: bool):
        self.logger.debug(f"Setting error mode to: {mode}")
        self.error_mode = mode

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response

    async def set_latency(self, latency: float):
        self.logger.debug(f"Setting latency to: {latency}")
        self.latency = latency

    async def set_rate_limit(self, limit: int):
        self.logger.debug(f"Setting rate limit to: {limit}")
        self.rate_limit = limit

    async def set_error_mode(self, mode: bool):
        self.logger.debug(f"Setting error mode to: {mode}")
        self.error_mode = mode

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response

    async def _create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any] | AsyncGenerator[Dict[str, Any], None]:
        self.logger.info(f"Creating response for model: {model}, max_tokens: {max_tokens}, stream: {stream}")
        try:
            await self._check_rate_limit()
        except CustomRateLimitError as e:
            self.logger.error(f"Rate limit exceeded: {str(e)}")
            raise

        await asyncio.sleep(self.latency)

        if self.error_mode:
            self.error_count += 1
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                error_response = MagicMock()
                error_response.status_code = 500
                error_response.json.return_value = {"error": {"type": "server_error", "message": "Simulated API error"}}
                raise APIStatusError("Simulated API error", response=error_response)

        self.context.extend(messages)
        prompt = messages[-1]['content']
        self.logger.info(f"Received prompt: {prompt[:50]}...")
        if len(prompt) > self.max_test_tokens:
            self.logger.warning(f"Prompt exceeds max tokens. Prompt length: {len(prompt)}, Max tokens: {self.max_test_tokens}")
            raise ValueError(f"Test input exceeds maximum allowed tokens ({self.max_test_tokens})")

        self.logger.debug(f"Generating response with messages: {messages}")
        response = self._generate_response(prompt, model, messages)
        if len(response) > max_tokens:
            self.logger.warning(f"Response exceeds max tokens. Truncating. Original length: {len(response)}")
            response = response[:max_tokens] + "..."

        self.call_count += 1
        self.logger.info(f"Returning response: {response[:50]}...")

        result = {
            "id": f"msg_{uuid.uuid4()}",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": response}],
            "model": model,
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": sum(len(m["content"]) for m in messages),
                "output_tokens": len(response)
            }
        }

        if stream:
            async def response_generator():
                for chunk in response.split():
                    yield {"type": "content_block_delta", "delta": {"type": "text", "text": chunk}}
                yield {"type": "message_delta", "delta": {"stop_reason": "end_turn"}}
            return response_generator()
        else:
            return result

    def _process_system_message(self, messages: List[Dict[str, str]]) -> None:
        system_message = next((m['content'] for m in messages if m['role'] == 'system'), None)
        if system_message:
            self.logger.info(f"Processing system message: {system_message[:100]}...")
            self._set_shakespearean_mode("speak like Shakespeare" in system_message.lower())
        else:
            self.logger.info("No system message found")
            self._set_shakespearean_mode(False)
        self.logger.debug(f"Final Shakespearean mode after processing: {self.is_shakespearean}")

    def _set_shakespearean_mode(self, is_shakespearean: bool) -> None:
        self.is_shakespearean = is_shakespearean
        self.logger.info(f"Shakespearean mode set to: {self.is_shakespearean}")

    def _apply_response_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Applying response prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean:
            if not response_text.startswith("Hark!"):
                response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Applied Shakespearean prefix: {response_text[:50]}...")
        else:
            if not response_text.startswith("Hello!"):
                response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Applied non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after prefix application: {response_text[:50]}...")
        return response_text

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        elif not self.is_shakespearean and not response_text.startswith("Hello!"):
            response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Ensured non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    def _generate_shakespearean_response(self, prompt: str) -> str:
        self.logger.info(f"Generating Shakespearean response for prompt: {prompt[:50]}...")
        shakespearean_words = ["thou", "doth", "verily", "forsooth", "prithee", "anon"]
        response = f"Hark! {random.choice(shakespearean_words).capitalize()} {prompt.lower()} "
        response += f"{random.choice(shakespearean_words)} {random.choice(shakespearean_words)} "
        response += f"[Shakespearean response to '{prompt[:20]}...']"
        self.logger.debug(f"Generated Shakespearean response: {response}")
        return response

    def _set_shakespearean_mode(self, is_shakespearean: bool) -> None:
        self.is_shakespearean = is_shakespearean
        self.logger.info(f"Shakespearean mode set to: {self.is_shakespearean}")

    async def debug_dump(self):
        self.logger.debug("Starting debug_dump method")
        try:
            state = {
                "api_key": self.api_key[:5] + "...",
                "rate_limit_threshold": self.rate_limit_threshold,
                "rate_limit_reset_time": self.rate_limit_reset_time,
                "call_count": self.call_count,
                "last_reset_time": self.last_reset_time,
                "error_mode": self.error_mode,
                "is_shakespearean": self.is_shakespearean,
                "responses_count": len(self.responses),
                "shakespearean_methods": {
                    "_process_system_message": hasattr(self, '_process_system_message'),
                    "_generate_shakespearean_response": hasattr(self, '_generate_shakespearean_response'),
                    "_apply_response_prefix": hasattr(self, '_apply_response_prefix'),
                    "_ensure_shakespearean_prefix": hasattr(self, '_ensure_shakespearean_prefix'),
                    "_set_shakespearean_mode": hasattr(self, '_set_shakespearean_mode')
                },
                "last_response": getattr(self, 'last_response', None),
                "shakespearean_mode_tracking": {
                    "is_shakespearean": self.is_shakespearean,
                    "last_system_message": getattr(self, 'last_system_message', None),
                    "last_shakespearean_response": getattr(self, 'last_shakespearean_response', None)
                },
                "method_implementations": {
                    "_ensure_shakespearean_prefix": self._ensure_shakespearean_prefix.__code__.co_code,
                    "_generate_shakespearean_response": self._generate_shakespearean_response.__code__.co_code,
                    "_apply_response_prefix": self._apply_response_prefix.__code__.co_code if hasattr(self, '_apply_response_prefix') else None
                },
                "shakespearean_prefix_stats": {
                    "total_calls": getattr(self, '_ensure_shakespearean_prefix_calls', 0),
                    "prefixes_added": getattr(self, '_ensure_shakespearean_prefix_added', 0)
                },
                "response_generation_flow": {
                    "system_message_processed": getattr(self, 'system_message_processed', False),
                    "shakespearean_mode_set": getattr(self, 'shakespearean_mode_set', False),
                    "response_generated": getattr(self, 'response_generated', False),
                    "prefix_ensured": getattr(self, 'prefix_ensured', False)
                }
            }
            self.logger.debug(f"Debug dump state: {state}")
            return state
        except Exception as e:
            self.logger.error(f"Error in debug_dump: {str(e)}", exc_info=True)
            raise

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text

    def _generate_shakespearean_response(self, prompt: str) -> str:
        self.logger.info(f"Generating Shakespearean response for prompt: {prompt[:50]}...")
        shakespearean_words = ["thou", "doth", "verily", "forsooth", "prithee", "anon"]
        response = f"Hark! {random.choice(shakespearean_words).capitalize()} {prompt.lower()} "
        response += f"{random.choice(shakespearean_words)} {random.choice(shakespearean_words)} "
        response += f"[Shakespearean response to '{prompt[:20]}...']"
        self.logger.debug(f"Generated Shakespearean response: {response}")
        return response

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting custom response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response
        self.logger.debug(f"Custom response set successfully for prompt: {prompt[:50]}...")

    async def _create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any] | AsyncGenerator[Dict[str, Any], None]:
        self.logger.debug(f"Creating response for model: {model}, max_tokens: {max_tokens}, stream: {stream}")
        
        cache_key = self._generate_cache_key(model, max_tokens, messages)
        cached_response = self.cache.get(cache_key)
        if cached_response:
            self.logger.debug(f"Cache hit for key: {cache_key}")
            return cached_response

        try:
            await self._check_rate_limit()
        except CustomRateLimitError as e:
            self.logger.error(f"Rate limit exceeded: {str(e)}")
            raise

        await asyncio.sleep(self.latency)

        if self.error_mode:
            self.error_count += 1
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                error_response = MagicMock()
                error_response.status_code = 500
                error_response.json.return_value = {"error": {"type": "server_error", "message": "Simulated API error"}}
                raise APIStatusError("Simulated API error", response=error_response)

        self.context.extend(messages)
        prompt = messages[-1]['content']
        self.logger.debug(f"Received prompt: {prompt[:50]}...")
        if len(prompt) > self.max_test_tokens:
            self.logger.warning(f"Prompt exceeds max tokens. Prompt length: {len(prompt)}, Max tokens: {self.max_test_tokens}")
            raise ValueError(f"Test input exceeds maximum allowed tokens ({self.max_test_tokens})")

        response = self._generate_response(prompt, model, messages)
        if len(response) > max_tokens:
            self.logger.warning(f"Response exceeds max tokens. Truncating. Original length: {len(response)}")
            response = response[:max_tokens] + "..."

        self.call_count += 1
        self.logger.debug(f"Returning response: {response[:50]}...")

        result = {
            "id": f"msg_{uuid.uuid4()}",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": response}],
            "model": model,
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": sum(len(m["content"]) for m in messages),
                "output_tokens": len(response)
            }
        }

        self.cache[cache_key] = result
        
        if stream:
            async def response_generator():
                for chunk in response.split():
                    yield {"type": "content_block_delta", "delta": {"type": "text", "text": chunk}}
                yield {"type": "message_delta", "delta": {"stop_reason": "end_turn"}}
            return response_generator()
        else:
            return result

    def _generate_cache_key(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> str:
        return f"{model}:{max_tokens}:{hash(tuple(sorted(message.items())) for message in messages)}"

    def bypass_cache(self):
        self.cache.clear()
        self.logger.info("Cache bypassed and cleared")

    async def _check_rate_limit(self):
        current_time = time.time()
        if current_time - self.last_reset > self.reset_time:
            self.calls = 0
            self.last_reset = current_time
            self.logger.debug(f"Rate limit reset. Calls: {self.calls}")

        self.calls += 1
        self.logger.debug(f"Rate limit check. Calls: {self.calls}, Limit: {self.rate_limit}")
        if self.calls > self.rate_limit:
            self.logger.warning(f"Rate limit exceeded. Calls: {self.calls}, Limit: {self.rate_limit}")
            raise CustomRateLimitError("Rate limit exceeded")
        elif self.calls == self.rate_limit:
            self.logger.warning(f"Rate limit reached. Calls: {self.calls}, Limit: {self.rate_limit}")

    async def reset(self):
        self.logger.debug("Resetting MockClaudeClient")
        self.calls = 0
        self.last_reset = time.time()
        self.error_mode = False
        self.latency = 0
        self.responses = {}
        self.call_count = 0
        self.error_count = 0
        self.context = []
        self.logger.debug("MockClaudeClient reset complete")

    async def count_tokens(self, text: str) -> int:
        # Simplified token counting for mock purposes
        token_count = len(text.split())
        self.logger.debug(f"Token count for text: {token_count}")
        return token_count

    async def set_latency(self, latency: float):
        self.logger.debug(f"Setting latency to: {latency}")
        self.latency = latency

    async def set_rate_limit(self, limit: int):
        self.logger.debug(f"Setting rate limit to: {limit}")
        self.rate_limit = limit

    async def set_error_mode(self, mode: bool):
        self.logger.debug(f"Setting error mode to: {mode}")
        self.error_mode = mode

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response

    async def set_error_mode(self, mode: bool):
        self.logger.debug(f"Setting error mode to: {mode}")
        self.error_mode = mode

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response

    async def set_rate_limit(self, limit: int):
        self.logger.debug(f"Setting rate limit to: {limit}")
        self.rate_limit = limit

    async def debug_dump(self):
        self.logger.debug("Starting debug_dump method")
        try:
            state = {
                "api_key": self.api_key[:5] + "...",
                "rate_limit": self.rate_limit,
                "reset_time": self.reset_time,
                "calls": self.calls,
                "last_reset": self.last_reset,
                "error_mode": self.error_mode,
                "latency": self.latency,
                "max_test_tokens": self.max_test_tokens,
                "call_count": self.call_count,
                "error_count": self.error_count,
                "max_errors": self.max_errors,
                "context_length": len(self.context),
                "responses_count": len(self.responses)
            }
            self.logger.debug(f"Debug dump state: {state}")
            return state
        except Exception as e:
            self.logger.error(f"Error in debug_dump: {str(e)}", exc_info=True)
            raise

    def __str__(self):
        return f"MockClaudeClient(call_count={self.call_count}, error_count={self.error_count}, error_mode={self.error_mode})"

    def __repr__(self):
        return self.__str__()

    async def _create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any] | AsyncGenerator[Dict[str, Any], None]:
        self.logger.debug(f"Creating response for model: {model}, max_tokens: {max_tokens}, stream: {stream}")
        try:
            await self._check_rate_limit()
        except CustomRateLimitError as e:
            self.logger.error(f"Rate limit exceeded: {str(e)}")
            raise

        await asyncio.sleep(self.latency)

        if self.error_mode:
            self.error_count += 1
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                error_response = MagicMock()
                error_response.status_code = 500
                error_response.json.return_value = {"error": {"type": "server_error", "message": "Simulated API error"}}
                raise APIStatusError("Simulated API error", response=error_response)

        self.context.extend(messages)
        prompt = messages[-1]['content']
        self.logger.debug(f"Received prompt: {prompt[:50]}...")
        if len(prompt) > self.max_test_tokens:
            self.logger.warning(f"Prompt exceeds max tokens. Prompt length: {len(prompt)}, Max tokens: {self.max_test_tokens}")
            raise ValueError(f"Test input exceeds maximum allowed tokens ({self.max_test_tokens})")

        response = self._generate_response(prompt, model, messages)
        if len(response) > max_tokens:
            self.logger.warning(f"Response exceeds max tokens. Truncating. Original length: {len(response)}")
            response = response[:max_tokens] + "..."

        self.call_count += 1
        self.logger.debug(f"Returning response: {response[:50]}...")

        if stream:
            async def response_generator():
                for chunk in response.split():
                    yield {"type": "content_block_delta", "delta": {"type": "text", "text": chunk}}
                yield {"type": "message_delta", "delta": {"stop_reason": "end_turn"}}
            return response_generator()
        else:
            return {
                "id": f"msg_{uuid.uuid4()}",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": response}],
                "model": model,
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "usage": {
                    "input_tokens": sum(len(m["content"]) for m in messages),
                    "output_tokens": len(response)
                }
            }

    def _generate_response(self, prompt: str, model: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        self.logger.debug(f"Generating response for prompt: {prompt[:50]}...")
        system_message = next((m['content'] for m in messages if m['role'] == 'system'), None)
        
        if system_message:
            self.logger.debug(f"System message found: {system_message[:50]}...")
            if "speak like Shakespeare" in system_message.lower():
                response_text = "Hark! Thou doth request information. Verily, I shall provide a response most Shakespearean!"
            else:
                response_text = f"Acknowledging system message: {system_message[:30]}..."
        else:
            context = " ".join(m['content'] for m in messages if m['role'] == 'user')
            self.logger.debug(f"Context: {context[:100]}...")
            
            if "summary" in prompt.lower():
                response_text = "Here is a summary of the long context: [Summary content]"
            elif "joke" in prompt.lower():
                response_text = "Sure, here's a joke for you: Why don't scientists trust atoms? Because they make up everything!"
            elif any(word in context.lower() for word in ['hark', 'thou', 'doth']):
                response_text = "Hark! Thou doth request a Shakespearean response, and so I shall provide!"
            else:
                # Check if there's a custom response for this prompt
                response_text = self.responses.get(prompt)
                if not response_text:
                    # Generate a response based on the conversation history
                    conversation_history = [m['content'] for m in messages if m['role'] in ['user', 'assistant']]
                    response_text = f"Based on our conversation: {' '.join(conversation_history[-3:])}, here's my response: [Generated response]"

        self.logger.debug(f"Generated response: {response_text[:50]}...")
        
        return {
            "id": f"msg_{uuid.uuid4()}",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ],
            "model": model,
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": sum(len(m["content"]) for m in messages),
                "output_tokens": len(response_text)
            }
        }

    async def _check_rate_limit(self):
        current_time = time.time()
        if current_time - self.last_reset > self.reset_time:
            self.calls = 0
            self.last_reset = current_time
            self.logger.debug(f"Rate limit reset. Calls: {self.calls}")

        self.calls += 1
        self.logger.debug(f"Rate limit check. Calls: {self.calls}, Limit: {self.rate_limit}")
        if self.calls > self.rate_limit:
            self.logger.warning(f"Rate limit exceeded. Calls: {self.calls}, Limit: {self.rate_limit}")
            raise CustomRateLimitError("Rate limit exceeded")
        elif self.calls == self.rate_limit:
            self.logger.warning(f"Rate limit reached. Calls: {self.calls}, Limit: {self.rate_limit}")

    async def reset(self):
        self.logger.debug("Resetting MockClaudeClient")
        self.calls = 0
        self.last_reset = time.time()
        self.error_mode = False
        self.latency = 0
        self.responses = {}
        self.call_count = 0
        self.error_count = 0
        self.context = []
        self.logger.debug("MockClaudeClient reset complete")

    async def count_tokens(self, text: str) -> int:
        # Simplified token counting for mock purposes
        token_count = len(text.split())
        self.logger.debug(f"Token count for text: {token_count}")
        return token_count

    async def set_latency(self, latency: float):
        self.logger.debug(f"Setting latency to: {latency}")
        self.latency = latency
import asyncio
from typing import Dict, List, Any

import asyncio
import logging
from typing import Dict, Any, List

import asyncio
import logging
from typing import Dict, Any, List
import uuid

class MockClaudeClient:
    class Messages:
        def __init__(self, client):
            self.client = client
            self.client.logger.debug("Initialized Messages class")

        async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
            self.client.logger.debug(f"Messages.create called with model: {model}, max_tokens: {max_tokens}")
            return await self.client._create(model, max_tokens, messages)

    def __init__(self, api_key: str = "mock_api_key", rate_limit: int = 10, reset_time: int = 60, cache_ttl: int = 300, cache_maxsize: int = 100):
        self.api_key = api_key
        self._messages = []
        self.lock = asyncio.Lock()
        self.thread_lock = Lock()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}.{api_key}")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.debug(f"MockClaudeClient initialized with API key: {api_key[:5]}...")
        self.rate_limit_threshold = rate_limit
        self.rate_limit_reset_time = reset_time
        self.call_count = 0
        self.last_reset_time = time.time()
        self.error_mode = False
        self.responses = {}
        self.context = []
        self.is_shakespearean = False
        self.cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)
        self.logger.info(f"MockClaudeClient initialized with rate_limit_threshold: {self.rate_limit_threshold}, rate_limit_reset_time: {self.rate_limit_reset_time}, cache_ttl: {cache_ttl}, cache_maxsize: {cache_maxsize}")
        
        # Add a file handler for persistent logging
        file_handler = logging.FileHandler(f'mock_claude_client_{api_key}.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    @property
    def messages(self):
        if self._messages is None:
            self._messages = self.Messages(self)
            self.logger.debug("Created Messages instance")
        return self._messages

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting custom response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response
        self.logger.debug(f"Custom response set successfully for prompt: {prompt[:50]}...")

    def _generate_response(self, prompt: str, model: str, messages: List[Dict[str, str]]) -> str:
        self.logger.info(f"Generating response for prompt: {prompt[:50]}... using model: {model}")
        
        self._process_system_message(messages)
        self.logger.info(f"Shakespearean mode: {self.is_shakespearean}")
        
        context = " ".join(m['content'] for m in messages if m['role'] == 'user')
        self.logger.info(f"Context: {context[:100]}...")
        
        response_text = self._generate_base_response(prompt, model, messages)
        response_text = self._apply_response_prefix(response_text)
        response_text = self._adjust_response_length(response_text, model)
        response_text = self._ensure_shakespearean_prefix(response_text)
        
        self.logger.debug(f"Final generated response for {model}: {response_text}")
        return response_text

    def _process_system_message(self, messages: List[Dict[str, str]]):
        system_message = next((m['content'] for m in messages if m['role'] == 'system'), None)
        self.logger.info(f"System message: {system_message[:100] if system_message else 'None'}")
        self.is_shakespearean = system_message and "speak like Shakespeare" in system_message.lower()
        self.logger.info(f"Set Shakespearean mode to: {self.is_shakespearean}")

    def _generate_base_response(self, prompt: str, model: str, messages: List[Dict[str, str]]) -> str:
        response_text = self.responses.get(prompt)
        if response_text:
            self.logger.info(f"Using custom response: {response_text[:50]}...")
        else:
            conversation_history = [m['content'] for m in messages if m['role'] in ['user', 'assistant']]
            self.logger.info(f"Generating response based on model: {model}")
            
            if self.is_shakespearean:
                response_text = self._generate_shakespearean_response(prompt)
                self.logger.info(f"Generated Shakespearean response: {response_text[:50]}...")
            elif model == 'claude-3-haiku-20240307':
                response_text = f"{' '.join(conversation_history[-1:])[:20]}..."
            elif model == 'claude-3-sonnet-20240229':
                response_text = f"Based on our conversation: {' '.join(conversation_history[-2:])[:40]}..."
            else:  # claude-3-opus-20240229 or default
                response_text = f"Based on our conversation: {' '.join(conversation_history[-3:])}, here's my response: [Generated response]"
        
        return response_text

    def _apply_response_prefix(self, response_text: str) -> str:
        if self.is_shakespearean:
            if not response_text.startswith("Hark!"):
                response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Applied Shakespearean prefix: {response_text[:50]}...")
        else:
            if not response_text.startswith("Hello!"):
                response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Applied non-Shakespearean prefix: {response_text[:50]}...")
        return response_text

    def _adjust_response_length(self, response_text: str, model: str) -> str:
        original_length = len(response_text)
        if model == 'claude-3-haiku-20240307':
            response_text = response_text[:50]  # Shorter response for Haiku
            self.logger.info(f"Truncated Haiku response from {original_length} to {len(response_text)} characters")
        elif model == 'claude-3-sonnet-20240229':
            response_text = response_text[:100]  # Medium-length response for Sonnet
            self.logger.info(f"Truncated Sonnet response from {original_length} to {len(response_text)} characters")
        else:
            self.logger.info(f"Opus response length: {len(response_text)} characters")
        return response_text

    def _generate_shakespearean_response(self, prompt: str) -> str:
        self.logger.info(f"Generating Shakespearean response for prompt: {prompt[:50]}...")
        shakespearean_words = ["thou", "doth", "verily", "forsooth", "prithee", "anon"]
        response = f"Hark! {random.choice(shakespearean_words).capitalize()}, {prompt.lower()}. "
        response += f"{random.choice(shakespearean_words).capitalize()} {random.choice(shakespearean_words)}, "
        response += f"I say in response to thy query '{prompt[:20]}...' "
        response += f"[Shakespearean response]"  
        self.logger.debug(f"Generated Shakespearean response: {response}")
        return response

    async def debug_dump(self):
        self.logger.debug("Starting debug_dump method")
        try:
            state = {
                "api_key": self.api_key[:5] + "...",
                "rate_limit_threshold": self.rate_limit_threshold,
                "rate_limit_reset_time": self.rate_limit_reset_time,
                "call_count": self.call_count,
                "last_reset_time": self.last_reset_time,
                "error_mode": self.error_mode,
                "context_length": len(self.context),
                "responses_count": len(self.responses),
                "is_shakespearean": self.is_shakespearean,
                "last_system_message": self.context[-2]['content'] if len(self.context) >= 2 and self.context[-2]['role'] == 'system' else None,
                "last_user_message": self.context[-1]['content'] if self.context and self.context[-1]['role'] == 'user' else None,
                "last_response": self.context[-1]['content'] if self.context and self.context[-1]['role'] == 'assistant' else None,
                "shakespearean_methods": {
                    "_apply_response_prefix": hasattr(self, '_apply_response_prefix'),
                    "_ensure_shakespearean_prefix": hasattr(self, '_ensure_shakespearean_prefix'),
                    "_generate_shakespearean_response": hasattr(self, '_generate_shakespearean_response'),
                }
            }
            self.logger.debug(f"Debug dump state: {state}")
            return state
        except Exception as e:
            self.logger.error(f"Error in debug_dump: {str(e)}", exc_info=True)
            raise

    def _generate_shakespearean_response(self, prompt: str) -> str:
        self.logger.info(f"Generating Shakespearean response for prompt: {prompt[:50]}...")
        shakespearean_words = ["thou", "doth", "verily", "forsooth", "prithee", "anon"]
        response = f"Hark! {random.choice(shakespearean_words).capitalize()} {prompt.lower()} "
        response += f"{random.choice(shakespearean_words)} {random.choice(shakespearean_words)} "
        response += f"[Shakespearean response to '{prompt[:20]}...']"
        self.logger.debug(f"Generated Shakespearean response: {response}")
        return response

    def _generate_shakespearean_response(self, prompt: str) -> str:
        self.logger.info(f"Generating Shakespearean response for prompt: {prompt[:50]}...")
        shakespearean_words = ["thou", "doth", "verily", "forsooth", "prithee", "anon"]
        response = f"Hark! {random.choice(shakespearean_words).capitalize()} {prompt.lower()} "
        response += f"{random.choice(shakespearean_words)} {random.choice(shakespearean_words)} "
        response += f"[Shakespearean response to '{prompt[:20]}...']"
        self.logger.debug(f"Generated Shakespearean response: {response}")
        return response

    def _generate_shakespearean_response(self, prompt: str) -> str:
        self.logger.info(f"Generating Shakespearean response for prompt: {prompt[:50]}...")
        shakespearean_words = ["thou", "doth", "verily", "forsooth", "prithee", "anon"]
        response = f"Hark! {random.choice(shakespearean_words).capitalize()} {prompt.lower()} "
        response += f"{random.choice(shakespearean_words)} {random.choice(shakespearean_words)} "
        response += f"[Shakespearean response to '{prompt[:20]}...']"
        self.logger.debug(f"Generated Shakespearean response: {response}")
        return response

    async def set_error_mode(self, mode: bool):
        self.logger.debug(f"Setting error mode to: {mode}")
        self.error_mode = mode

    async def set_rate_limit(self, limit: int):
        self.logger.debug(f"Setting rate limit to: {limit}")
        self.rate_limit_threshold = limit

    @property
    def messages(self):
        return self.Messages(self)

    class Messages:
        def __init__(self, client):
            self.client = client
            self.client.logger.debug("Messages inner class initialized")

        async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any]:
            self.client.logger.debug(f"Creating message with model: {model}, max_tokens: {max_tokens}, stream: {stream}")
            return await self.client.create_message(messages[-1]['content'], max_tokens, model, stream)

    async def create_message(self, prompt: str, max_tokens: int = 1000, model: str = 'claude-3-opus-20240229', stream: bool = False) -> Dict[str, Any]:
        self.logger.info(f"Creating message with prompt: {prompt[:50]}..., stream: {stream}, model: {model}, max_tokens: {max_tokens}")
        async with self.lock:
            with self.thread_lock:
                current_time = time.time()
                if current_time - self.last_reset_time >= self.rate_limit_reset_time:
                    self.logger.info(f"Resetting rate limit. Old count: {self.call_count}")
                    self.call_count = 0
                    self.last_reset_time = current_time

                self.call_count += 1
                self.logger.debug(f"Current call count: {self.call_count}")
                if self.call_count > self.rate_limit_threshold:
                    self.logger.warning(f"Rate limit exceeded. Count: {self.call_count}, Threshold: {self.rate_limit_threshold}")
                    raise CustomRateLimitError("Rate limit exceeded")

                if self.error_mode:
                    self.logger.warning("Error mode is active. Raising APIStatusError.")
                    raise APIStatusError("Simulated API error", response=MagicMock(), body={})

                self.logger.debug(f"Message creation successful. Call count: {self.call_count}")

                message_id = f"msg_{uuid.uuid4()}"
                system_message = next((m['content'] for m in self.context if m['role'] == 'system'), None)
                self.logger.info(f"System message: {system_message[:50] if system_message else 'None'}")
                
                response_text = self._generate_response(prompt, model, self.context + [{'role': 'user', 'content': prompt}])
                mock_response = {
                    'id': message_id,
                    'type': 'message',
                    'role': 'assistant',
                    'content': [
                        {
                            'type': 'text',
                            'text': response_text
                        }
                    ],
                    'model': model,
                    'stop_reason': 'end_turn',
                    'stop_sequence': None,
                    'usage': {
                        'input_tokens': len(prompt.split()),
                        'output_tokens': len(response_text.split())
                    }
                }
                self._messages.append(mock_response)
                self.context.append({'role': 'user', 'content': prompt})
                self.context.append({'role': 'assistant', 'content': response_text})
                self.logger.debug(f"Created message with ID: {message_id}")
                self.logger.info(f"Response text: {response_text[:100]}...")
                
                if stream:
                    async def response_generator():
                        for word in response_text.split():
                            yield {'type': 'content_block_delta', 'delta': {'type': 'text', 'text': word + ' '}}
                        yield {'type': 'message_delta', 'delta': {'stop_reason': 'end_turn'}}
                    self.logger.debug("Returning streaming response")
                    return response_generator()
                else:
                    self.logger.debug("Returning non-streaming response")
                    return mock_response

    async def count_tokens(self, text: str) -> int:
        token_count = len(text.split())
        self.logger.debug(f"Counted {token_count} tokens for text: {text[:50]}...")
        return token_count

    async def debug_dump(self) -> Dict[str, Any]:
        self.logger.debug("Performing debug dump")
        return {
            'api_key': f"{self.api_key[:5]}...",
            'message_count': len(self._messages),
            'last_message': self._messages[-1] if self._messages else None
        }
    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        elif not self.is_shakespearean and not response_text.startswith("Hello!"):
            response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Ensured non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text
    async def set_rate_limit(self, limit: int):
        self.logger.debug(f"Setting rate limit to: {limit}")
        self.rate_limit = limit

    async def set_error_mode(self, mode: bool):
        self.logger.debug(f"Setting error mode to: {mode}")
        self.error_mode = mode

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting custom response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response

    async def set_latency(self, latency: float):
        self.logger.debug(f"Setting latency to: {latency}")
        self.latency = latency

    def _ensure_shakespearean_prefix(self, response_text: str) -> str:
        self.logger.debug(f"Ensuring Shakespearean prefix. Current Shakespearean mode: {self.is_shakespearean}")
        self.logger.debug(f"Original response: {response_text[:50]}...")
        
        if self.is_shakespearean and not response_text.startswith("Hark!"):
            response_text = f"Hark! {response_text.lstrip('Hello! ')}"
            self.logger.info(f"Ensured Shakespearean prefix: {response_text[:50]}...")
        elif not self.is_shakespearean and not response_text.startswith("Hello!"):
            response_text = f"Hello! {response_text.lstrip('Hark! ')}"
            self.logger.info(f"Ensured non-Shakespearean prefix: {response_text[:50]}...")
        
        self.logger.debug(f"Final response after ensuring prefix: {response_text[:50]}...")
        return response_text
    def _generate_response(self, prompt: str, model: str, messages: List[Dict[str, str]]) -> str:
        self.logger.info(f"Generating response for prompt: {prompt[:50]}... using model: {model}")
        
        self._process_system_message(messages)
        self.logger.info(f"Current Shakespearean mode: {self.is_shakespearean}")
        
        context = " ".join(m['content'] for m in messages if m['role'] == 'user')
        self.logger.info(f"Context: {context[:100]}...")
        
        # Check if there's a custom response for this prompt
        response_text = self.responses.get(prompt)
        if response_text:
            self.logger.info(f"Using custom response: {response_text[:50]}...")
        else:
            # Generate a response based on the model and conversation history
            conversation_history = [m['content'] for m in messages if m['role'] in ['user', 'assistant']]
            self.logger.info(f"Generating response based on model: {model}")
            
            if self.is_shakespearean:
                response_text = self._generate_shakespearean_response(prompt)
                self.logger.info(f"Generated Shakespearean response: {response_text[:50]}...")
            elif model == 'claude-3-haiku-20240307':
                response_text = f"{' '.join(conversation_history[-1:])[:20]}..."
            elif model == 'claude-3-sonnet-20240229':
                response_text = f"Based on our conversation: {' '.join(conversation_history[-2:])[:40]}..."
            else:  # claude-3-opus-20240229 or default
                response_text = f"Based on our conversation: {' '.join(conversation_history[-3:])}, here's my response: [Generated response]"

        # Adjust response length based on the model
        response_text = self._adjust_response_length(response_text, model)

        # Ensure Shakespearean prefix if necessary
        response_text = self._ensure_shakespearean_prefix(response_text)
        self.logger.debug(f"Final generated response for {model}: {response_text}")
        return response_text

    def _process_system_message(self, messages: List[Dict[str, str]]) -> None:
        self.logger.debug("Processing system message")
        system_message = next((m['content'] for m in messages if m['role'] == 'system'), None)
        if system_message:
            self.logger.info(f"System message found: {system_message[:100]}...")
            self.is_shakespearean = "speak like Shakespeare" in system_message.lower()
            self.logger.info(f"Shakespearean mode set to: {self.is_shakespearean}")
        else:
            self.logger.info("No system message found")
            self.is_shakespearean = False
        self.logger.debug(f"Final Shakespearean mode after processing: {self.is_shakespearean}")

    def _generate_shakespearean_response(self, prompt: str) -> str:
        self.logger.info(f"Generating Shakespearean response for prompt: {prompt[:50]}...")
        shakespearean_words = ["thou", "doth", "verily", "forsooth", "prithee", "anon"]
        response = f"Hark! {random.choice(shakespearean_words).capitalize()} {prompt.lower()} "
        response += f"{random.choice(shakespearean_words)} {random.choice(shakespearean_words)} "
        response += f"[Shakespearean response to '{prompt[:20]}...']"
        self.logger.debug(f"Generated Shakespearean response: {response}")
        return response

    def _adjust_response_length(self, response_text: str, model: str) -> str:
        original_length = len(response_text)
        if model == 'claude-3-haiku-20240307':
            response_text = response_text[:50]  # Shorter response for Haiku
            self.logger.info(f"Truncated Haiku response from {original_length} to {len(response_text)} characters")
        elif model == 'claude-3-sonnet-20240229':
            response_text = response_text[:100]  # Medium-length response for Sonnet
            self.logger.info(f"Truncated Sonnet response from {original_length} to {len(response_text)} characters")
        else:
            self.logger.info(f"Opus response length: {len(response_text)} characters")
        return response_text
    async def debug_dump(self):
        self.logger.debug("Starting debug_dump method")
        try:
            state = {
                "api_key": self.api_key[:5] + "...",
                "rate_limit": self.rate_limit,
                "reset_time": self.reset_time,
                "calls": self.calls,
                "last_reset": self.last_reset,
                "error_mode": self.error_mode,
                "latency": self.latency,
                "max_test_tokens": self.max_test_tokens,
                "call_count": self.call_count,
                "error_count": self.error_count,
                "max_errors": self.max_errors,
                "context_length": len(self.context),
                "responses_count": len(self.responses),
                "is_shakespearean": self.is_shakespearean
            }
            self.logger.debug(f"Debug dump state: {state}")
            return state
        except Exception as e:
            self.logger.error(f"Error in debug_dump: {str(e)}", exc_info=True)
            raise

    def __str__(self):
        return f"MockClaudeClient(call_count={self.call_count}, error_count={self.error_count}, error_mode={self.error_mode})"

    def __repr__(self):
        return self.__str__()

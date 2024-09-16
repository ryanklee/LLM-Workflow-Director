import asyncio
import time
import logging
import uuid
import aiohttp
from typing import Dict, Any, List, AsyncGenerator
from unittest.mock import MagicMock
from anthropic import APIStatusError
from src.exceptions import CustomRateLimitError

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockClaudeClient:
    class Messages:
        def __init__(self, client):
            self.client = client

        async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any] | AsyncGenerator[Dict[str, Any], None]:
            return await self.client._create(model, max_tokens, messages, stream)

    def __init__(self, api_key: str = "mock_api_key", base_url: str = "https://api.anthropic.com"):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.debug(f"Initializing MockClaudeClient {id(self)} with api_key: {api_key[:5]}, base_url: {base_url}")
        
        self.api_key = api_key
        self.base_url = base_url
        self.messages = self.Messages(self)
        self.calls = 0
        self.last_reset = asyncio.get_event_loop().time()
        self.error_mode = False
        self.latency = 0.1
        self.responses = {}
        self.max_test_tokens = 1000
        self.call_count = 0
        self.error_count = 0
        self.max_errors = 3
        self.max_context_length = 200000
        self.last_reset_time = time.time()
        self.lock = asyncio.Lock()
        self.rate_limit_threshold = 10
        self.rate_limit_reset_time = 60
        
        self.logger.debug(f"Finished initialization of MockClaudeClient {id(self)}")

    async def _create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], stream: bool = False) ->  Dict[str, Any] | AsyncGenerator[Dict[str, Any], None]:
        self.logger.debug(f"Creating response for model: {model}, max_tokens: {max_tokens}, stream: {stream}")
        async with self.lock:
            await self._check_rate_limit()
            await asyncio.sleep(self.latency)
            
            prompt = messages[-1]['content']
            self.logger.debug(f"Received prompt: {prompt[:50]}...")
            if sum(len(m['content']) for m in messages) > self.max_context_length:
                self.logger.warning(f"Total message length exceeds max context length")
                raise ValueError(f"Total message length exceeds maximum context length ({self.max_context_length})")
            
            if self.error_mode:
                self.error_count += 1
                if self.error_count <= self.max_errors:
                    self.logger.error("Simulated API error")
                    raise APIStatusError("Simulated API error", response=MagicMock(), body={})
            
            response = self.responses.get(prompt, "Default mock response")
            if len(response) > max_tokens:
                self.logger.warning(f"Response exceeds max tokens. Truncating. Original length: {len(response)}")
                response = response[:max_tokens] + "..."
            
            self.call_count += 1
            wrapped_response = f"<response>{response}</response>"
            self.logger.debug(f"Returning response: {wrapped_response[:50]}...")

            if stream:
                async def response_generator():
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

    async def _check_rate_limit(self):
        current_time = time.time()
        if current_time - self.last_reset_time >= self.rate_limit_reset_time:
            self.logger.info(f"Resetting call count. Old count: {self.call_count}")
            self.call_count = 0
            self.last_reset_time = current_time
        if self.call_count >= self.rate_limit_threshold:
            self.logger.warning(f"Rate limit exceeded. Count: {self.call_count}, Threshold: {self.rate_limit_threshold}")
            raise CustomRateLimitError("Rate limit exceeded")

    async def count_tokens(self, text: str) -> int:
        # Simplified token counting for mock purposes
        return len(text.split())

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
        self.logger.debug(f"Finished resetting MockClaudeClient {id(self)}")

    async def get_call_count(self):
        self.logger.debug(f"Current call count: {self.call_count}")
        return self.call_count

    async def get_error_count(self):
        self.logger.debug(f"Current error count: {self.error_count}")
        return self.error_count
import asyncio
from typing import Dict, List, Optional
from anthropic import AsyncAnthropic

import asyncio
from typing import Dict, List, Any
from anthropic import APIStatusError, RateLimitError

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

class MockClaudeClient:
    class Messages:
        def __init__(self, client):
            self.client = client
            self.client.logger.debug("Initialized Messages class")

        async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
            self.client.logger.debug(f"Messages.create called with model: {model}, max_tokens: {max_tokens}")
            return await self.client._create(model, max_tokens, messages)

    def __init__(self, api_key: str, rate_limit: int = 10, reset_time: int = 60):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.debug(f"Initializing MockClaudeClient {id(self)} with api_key: {api_key[:5]}...")
        
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.reset_time = reset_time
        self.calls = 0
        self.last_reset = asyncio.get_event_loop().time()
        self.error_mode = False
        self.latency = 0.1
        self.responses = {}
        self.max_test_tokens = 1000
        self.call_count = 0
        self.error_count = 0
        self.max_errors = 3
        self.max_context_length = 200000
        self._messages = None
        self.lock = asyncio.Lock()
        
        self.logger.debug(f"Finished initialization of MockClaudeClient {id(self)}")

    @property
    def messages(self):
        if self._messages is None:
            self._messages = self.Messages(self)
            self.logger.debug("Created Messages instance")
        return self._messages

    async def _create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        self.logger.debug(f"Creating response for model: {model}, max_tokens: {max_tokens}")
        await self._check_rate_limit()
        await asyncio.sleep(self.latency)

        if self.error_mode:
            self.error_count += 1
            if self.error_count <= self.max_errors:
                self.logger.warning(f"Error mode active. Raising APIStatusError. Error count: {self.error_count}")
                raise APIStatusError("Simulated API error", response=MagicMock(), body={})

        prompt = messages[-1]['content']  # Use the last message as the prompt
        self.logger.debug(f"Received prompt: {prompt[:50]}...")
        if sum(len(m['content']) for m in messages) > self.max_context_length:
            self.logger.warning(f"Total message length exceeds max context length")
            raise ValueError(f"Total message length exceeds maximum context length ({self.max_context_length})")

        response = self.responses.get(prompt, "Default mock response")
        if len(response) > max_tokens:
            self.logger.warning(f"Response exceeds max tokens. Truncating. Original length: {len(response)}")
            response = response[:max_tokens] + "..."

        wrapped_response = self._wrap_response(response)
        self.call_count += 1
        self.logger.debug(f"Returning response: {wrapped_response[:50]}...")
        return {
            "content": [{"text": wrapped_response}],
            "model": model,
            "usage": {
                "input_tokens": sum(len(m["content"]) for m in messages),
                "output_tokens": len(response)
            }
        }

class Messages:
    def __init__(self, client):
        self.client = client

    async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        return await self.client.create(model, max_tokens, messages)
        self.messages = Messages(self)
        self.max_context_length = 200000

    async def _create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        self.logger.debug(f"Creating response for model: {model}, max_tokens: {max_tokens}")
        await self._check_rate_limit()
        await asyncio.sleep(self.latency)

        if self.error_mode:
            self.error_count += 1
            if self.error_count <= self.max_errors:
                self.logger.error(f"Simulated API error. Error count: {self.error_count}")
                raise APIStatusError("Simulated API error", response=MagicMock(), body={})

        prompt = messages[-1]['content']  # Use the last message as the prompt
        self.logger.debug(f"Received prompt: {prompt[:50]}... (length: {len(prompt)})")
        if sum(len(m['content']) for m in messages) > self.max_context_length:
            self.logger.warning(f"Total message length exceeds max context length")
            raise ValueError(f"Total message length exceeds maximum context length ({self.max_context_length})")

        response = self.responses.get(prompt, "Default mock response")
        if len(response) > max_tokens:
            self.logger.warning(f"Response exceeds max tokens. Truncating. Original length: {len(response)}")
            response = response[:max_tokens] + "..."

        self.call_count += 1
        self.logger.debug(f"Returning response: {response[:50]}...")
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

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        response = await self.messages.create(model, self.max_test_tokens, [{"role": "user", "content": prompt}])
        return response["content"][0]["text"]

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting response for prompt: {prompt[:50]}...")
        self.responses[prompt] = response
        self.logger.debug(f"Response set successfully for prompt: {prompt[:50]}...")

    async def set_error_mode(self, mode: bool):
        self.error_mode = mode

    async def set_latency(self, latency: float):
        self.latency = latency

    async def set_rate_limit(self, limit: int):
        self.rate_limit_threshold = limit

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        await self._check_rate_limit()
        await asyncio.sleep(self.latency)
        self.call_count += 1
        if self.error_mode:
            self.error_count += 1
            if self.error_count <= self.max_errors:
                raise APIStatusError("Simulated API error", response=None, body={})
        return self.responses.get(prompt, "Default mock response")

    async def count_tokens(self, text: str) -> int:
        self.logger.debug(f"Counting tokens for text: {text[:50]}...")
        url = f"{self.base_url}/v1/tokenize"
        body = {
            "model": "claude-3-opus-20240229",
            "prompt": text
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers={"X-API-Key": self.api_key}) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.debug(f"Token count: {result['token_count']}")
                    return result['token_count']
                else:
                    self.logger.error(f"Error counting tokens: {response.status}")
                    raise APIStatusError(f"Error counting tokens: {response.status}", response=response, body={})

    async def _check_rate_limit(self):
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_reset > self.reset_interval:
            self.calls = 0
            self.last_reset = current_time
        self.calls += 1
        if self.calls > self.rate_limit_threshold:
            raise CustomRateLimitError("Rate limit exceeded")

    async def reset(self):
        self.calls = 0
        self.last_reset = asyncio.get_event_loop().time()
        self.error_mode = False
        self.latency = 0
        self.responses = {}
        self.call_count = 0
        self.error_count = 0

    async def select_model(self, task: str) -> str:
        if "simple" in task.lower():
            return "claude-3-haiku-20240307"
        elif "complex" in task.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

    async def messages_create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], **kwargs) -> Dict:
        await self._check_rate_limit()
        await asyncio.sleep(self.latency)

        if self.error_mode:
            self.error_count += 1
            if self.error_count <= self.max_errors:
                raise APIStatusError("Simulated API error", response=None, body={})

        prompt = messages[0]['content']
        if len(prompt) > self.max_test_tokens:
            raise ValueError(f"Test input exceeds maximum allowed tokens ({self.max_test_tokens})")

        response = self.responses.get(prompt, "Default mock response")
        if len(response) > self.max_test_tokens:
            response = response[:self.max_test_tokens] + "..."

        self.call_count += 1

        return {
            "content": [{"text": response}],
            "model": model,
            "usage": {
                "input_tokens": sum(len(m["content"]) for m in messages) // 4,
                "output_tokens": len(response) // 4
            }
        }

    async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], **kwargs) -> Dict:
        self.logger.debug(f"Creating response for model: {model}, max_tokens: {max_tokens}")
        await self._check_rate_limit()
        await asyncio.sleep(self.latency)

        if self.error_mode:
            self.error_count += 1
            if self.error_count <= self.max_errors:
                self.logger.warning(f"Error mode active. Raising APIStatusError. Error count: {self.error_count}")
                raise APIStatusError("Simulated API error", response=MagicMock(), body={})

        prompt = messages[0]['content']
        self.logger.debug(f"Received prompt: {prompt[:50]}...")
        if len(prompt) > self.max_test_tokens:
            self.logger.warning(f"Prompt exceeds max tokens. Prompt length: {len(prompt)}, Max tokens: {self.max_test_tokens}")
            raise ValueError(f"Test input exceeds maximum allowed tokens ({self.max_test_tokens})")

        response = self.responses.get(prompt, "Default mock response")
        if len(response) > max_tokens:
            self.logger.warning(f"Response exceeds max tokens. Truncating. Original length: {len(response)}")
            response = response[:max_tokens] + "..."

        self.call_count += 1
        self.logger.debug(f"Returning response: {response[:50]}...")
        return {
            "content": [{"text": f"<response>{response}</response>"}],
            "model": model,
            "usage": {
                "input_tokens": sum(len(m["content"]) for m in messages),
                "output_tokens": len(response)
            }
        }

    async def messages(self):
        return self

    async def _check_rate_limit(self):
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_reset > self.reset_interval:
            self.calls = 0
            self.last_reset = current_time

        self.calls += 1
        if self.calls > self.rate_limit:
            raise RateLimitError("Rate limit exceeded", response=MagicMock(), body={})

    def set_error_mode(self, enabled: bool):
        self.error_mode = enabled
        if not enabled:
            self.error_count = 0

    def set_latency(self, latency: float):
        self.latency = latency

    def reset(self):
        self.calls = 0
        self.last_reset = asyncio.get_event_loop().time()
        self.error_mode = False
        self.latency = 0
        self.responses = {}
        self.call_count = 0
        self.error_count = 0

    async def count_tokens(self, text: str) -> int:
        await asyncio.sleep(0.01)  # Simulate a short delay
        return len(text.split())

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        response = await self.create(model, self.max_test_tokens, [{"role": "user", "content": prompt}])
        return response['content'][0]['text']

    async def set_response(self, prompt: str, response: str):
        self.responses[prompt] = response

    async def set_rate_limit(self, limit: int):
        self.rate_limit = limit

    async def get_call_count(self) -> int:
        return self.call_count

    async def get_error_count(self) -> int:
        return self.error_count

    async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        await self._check_rate_limit()
        await asyncio.sleep(self.latency)

        if self.error_mode:
            self.error_count += 1
            if self.error_count <= self.max_errors:
                raise APIStatusError("Simulated API error", response=MagicMock(), body={})

        prompt = messages[0]['content']
        if len(prompt) > self.max_test_tokens:
            raise ValueError(f"Test input exceeds maximum allowed tokens ({self.max_test_tokens})")

        response = self.responses.get(prompt, "Default mock response")
        if len(response) > max_tokens:
            response = response[:max_tokens] + "..."

        self.call_count += 1

        return {
            "content": [{"text": f"<response>{response}</response>"}],
            "model": model,
            "usage": {
                "input_tokens": sum(len(m["content"]) for m in messages),
                "output_tokens": len(response)
            }
        }
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
from typing import Dict, Any, List
from unittest.mock import MagicMock
from anthropic import RateLimitError, APIError, APIStatusError
from src.exceptions import CustomRateLimitError

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockClaudeClient:
    class Messages:
        def __init__(self, client):
            self.client = client
            self.client.logger.debug("Initialized Messages class")

        async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any]:
            self.client.logger.debug(f"Messages.create called with model: {model}, max_tokens: {max_tokens}, stream: {stream}")
            return await self.client._create(model, max_tokens, messages, stream)

    def __init__(self, api_key: str = "mock_api_key", rate_limit: int = 10, reset_time: int = 60):
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
        self.logger.debug(f"Finished initialization of MockClaudeClient {id(self)}")

    def __str__(self):
        return f"MockClaudeClient(call_count={self.call_count}, error_count={self.error_count}, error_mode={self.error_mode})"

    def __repr__(self):
        return self.__str__()

    async def _create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any]:
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
                raise APIStatusError("Simulated API error", response=MagicMock(), body={})

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

    def _generate_response(self, prompt: str, model: str, messages: List[Dict[str, str]]) -> str:
        system_message = next((m['content'] for m in messages if m['role'] == 'system'), None)
        
        if system_message and "speak like Shakespeare" in system_message:
            return "Hark! Thou doth request information about the weather. Verily, I say unto thee, the skies are fair and the breeze gentle."
        
        if "summary" in prompt.lower():
            return "Here is a summary of the long context: [Summary content]"
        elif "joke" in prompt.lower():
            return "Sure, here's a joke for you: Why don't scientists trust atoms? Because they make up everything!"
        elif any(word in prompt.lower() for word in ['hark', 'thou', 'doth']):
            return "Hark! Thou doth request a Shakespearean response, and so I shall provide!"
        else:
            return self.responses.get(prompt, "Default mock response")

    async def debug_dump(self):
        self.logger.debug("Starting debug_dump method")
        try:
            state = {}
            for attr, value in self.__dict__.items():
                if attr != 'logger':
                    state[attr] = str(value)
                    self.logger.debug(f"{attr}: {value}")
            self.logger.debug("Finished debug_dump method")
            return state
        except Exception as e:
            self.logger.error(f"Error in debug_dump: {str(e)}", exc_info=True)
            raise

    def ensure_messages_initialized(self):
        if self._messages is None:
            self.logger.warning("Messages instance not initialized. Initializing now.")
            self._messages = self.Messages(self)
        return self._messages

    async def debug_dump(self):
        self.logger.debug("Starting debug_dump method")
        try:
            state = {}
            for attr, value in self.__dict__.items():
                if attr != 'logger':
                    state[attr] = str(value)
                    self.logger.debug(f"{attr}: {value}")
            self.logger.debug("Finished debug_dump method")
            return state
        except Exception as e:
            self.logger.error(f"Error in debug_dump: {str(e)}", exc_info=True)
            raise

    async def _create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        self.logger.debug(f"_create method called with model: {model}, max_tokens: {max_tokens}")
        # ... (rest of the method implementation)

    def __init__(self, api_key: str, rate_limit: int = 10, reset_time: int = 60):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.debug(f"Starting initialization of MockClaudeClient with api_key: {api_key[:5]}...")
        
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.reset_time = reset_time
        self.calls = 0
        self.last_reset = asyncio.get_event_loop().time()
        self.error_mode = False
        self.latency = 0
        self.responses = {}
        self.max_test_tokens = 1000
        self.call_count = 0
        self.error_count = 0
        self.max_errors = 3
        self._messages = None
        self.logger.debug("Finished initialization of MockClaudeClient")

    async def _create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        self.logger.debug(f"Creating response for model: {model}, max_tokens: {max_tokens}")
        await self._check_rate_limit()
        await asyncio.sleep(self.latency)

        if self.error_mode:
            self.error_count += 1
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                raise APIStatusError("Simulated API error", response=MagicMock(), body={})

        prompt = messages[0]['content']
        self.logger.debug(f"Received prompt: {prompt[:50]}...")
        if len(prompt) > self.max_test_tokens:
            self.logger.warning(f"Prompt exceeds max tokens. Prompt length: {len(prompt)}, Max tokens: {self.max_test_tokens}")
            raise ValueError(f"Test input exceeds maximum allowed tokens ({self.max_test_tokens})")

        response = self.responses.get(prompt, "Default mock response")
        if len(response) > max_tokens:
            self.logger.warning(f"Response exceeds max tokens. Truncating. Original length: {len(response)}")
            response = response[:max_tokens] + "..."

        self.call_count += 1
        self.logger.debug(f"Returning response: {response[:50]}...")
        return {
            "content": [{"text": f"<response>{response}</response>"}],
            "model": model,
            "usage": {
                "input_tokens": sum(len(m["content"]) for m in messages),
                "output_tokens": len(response)
            }
        }

    async def _check_rate_limit(self):
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_reset > self.reset_time:
            self.calls = 0
            self.last_reset = current_time

        self.calls += 1
        if self.calls > self.rate_limit:
            raise CustomRateLimitError("Rate limit exceeded")

    async def set_response(self, prompt: str, response: str):
        self.responses[prompt] = response

    async def set_error_mode(self, mode: bool):
        self.error_mode = mode

    async def set_latency(self, latency: float):
        self.latency = latency

    async def set_rate_limit(self, limit: int):
        self.rate_limit = limit

    async def reset(self):
        self.calls = 0
        self.last_reset = asyncio.get_event_loop().time()
        self.error_mode = False
        self.latency = 0
        self.responses = {}
        self.call_count = 0
        self.error_count = 0

    async def count_tokens(self, text: str) -> int:
        url = f"{self.base_url}/v1/tokenize"
        body = {
            "model": "claude-3-opus-20240229",
            "prompt": text
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body) as response:
                result = await response.json()
                return result['token_count']
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
    def __init__(self, api_key: str = "mock_api_key"):
        self.api_key = api_key
        self._messages = []
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.debug(f"MockClaudeClient initialized with API key: {api_key[:5]}...")
        self.rate_limit_threshold = 10
        self.rate_limit_reset_time = 60
        self.call_count = 0
        self.last_reset_time = time.time()

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
        self.logger.debug(f"Creating message with prompt: {prompt[:50]}..., stream: {stream}, model: {model}, max_tokens: {max_tokens}")
        async with self.lock:
            current_time = time.time()
            if current_time - self.last_reset_time >= self.rate_limit_reset_time:
                self.logger.info(f"Resetting rate limit. Old count: {self.call_count}")
                self.call_count = 0
                self.last_reset_time = current_time

            self.call_count += 1
            self.logger.debug(f"Current call count: {self.call_count}")
            if self.call_count > self.rate_limit_threshold:
                self.logger.warning(f"Rate limit exceeded. Count: {self.call_count}")
                raise CustomRateLimitError("Rate limit exceeded")

            message_id = f"msg_{uuid.uuid4()}"
            mock_response = {
                'id': message_id,
                'type': 'message',
                'role': 'assistant',
                'content': [
                    {
                        'type': 'text',
                        'text': f"Hello! How can I assist you today?"
                    }
                ],
                'model': model,
                'stop_reason': 'end_turn',
                'stop_sequence': None,
                'usage': {
                    'input_tokens': len(prompt.split()),
                    'output_tokens': len("Hello! How can I assist you today?".split())
                }
            }
            self._messages.append(mock_response)
            self.logger.debug(f"Created message with ID: {message_id}")
            
            if stream:
                async def response_generator():
                    yield {'type': 'content_block_delta', 'delta': {'type': 'text', 'text': 'Hello!'}}
                    yield {'type': 'content_block_delta', 'delta': {'type': 'text', 'text': ' How can I assist you today?'}}
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

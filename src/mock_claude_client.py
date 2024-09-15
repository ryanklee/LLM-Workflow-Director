import asyncio
import time
import logging
import uuid
from typing import Dict, Any, List
from unittest.mock import MagicMock
from anthropic import RateLimitError, APIError, APIStatusError
from src.exceptions import RateLimitError as CustomRateLimitError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Messages:
    def __init__(self, client):
        self.client = client
        self.client.logger.debug("Initialized Messages class")

    async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        self.client.logger.debug(f"Messages.create called with model: {model}, max_tokens: {max_tokens}")
        return await self.client._create(model, max_tokens, messages)

import asyncio
import time
import logging
from typing import Dict, Any, List
from unittest.mock import MagicMock
from anthropic import RateLimitError, APIError, APIStatusError
from src.exceptions import RateLimitError as CustomRateLimitError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import asyncio
import time
import logging
import uuid
from typing import Dict, Any, List
from unittest.mock import MagicMock
from anthropic import RateLimitError, APIError, APIStatusError
from src.exceptions import RateLimitError as CustomRateLimitError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import asyncio
import time
import logging
import uuid
from typing import Dict, Any, List
from unittest.mock import MagicMock
from anthropic import RateLimitError, APIError, APIStatusError
from src.exceptions import CustomRateLimitError

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
logger = logging.getLogger(__name__)

class MockClaudeClient:
    class Messages:
        def __init__(self, client):
            self.client = client
            self.client.logger.debug(f"Initialized Messages class for client {id(client)}")

        async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
            self.client.logger.debug(f"Messages.create called with model: {model}, max_tokens: {max_tokens}")
            return await self.client._create(model, max_tokens, messages)

    def __init__(self, api_key: str):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.debug(f"Starting initialization of MockClaudeClient {id(self)} with api_key: {api_key[:5]}...")
        
        self.api_key = api_key
        self.rate_limit_threshold = 5
        self.rate_limit_reset_time = 60
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
        self._messages = self.Messages(self)
        self.last_reset_time = time.time()
        self.lock = asyncio.Lock()
        
        self.logger.debug(f"Finished initialization of MockClaudeClient {id(self)}")

    def __str__(self):
        return f"MockClaudeClient(id={id(self)}, call_count={self.call_count}, error_count={self.error_count}, error_mode={self.error_mode})"

    def __repr__(self):
        return self.__str__()

    @property
    def messages(self):
        self.logger.debug(f"Accessing messages property for client {id(self)}")
        return self._messages

    async def debug_dump(self):
        self.logger.debug(f"Starting debug_dump method for client {id(self)}")
        state = {attr: str(value) for attr, value in self.__dict__.items() if attr != 'logger'}
        self.logger.debug(f"Client state: {state}")
        return state

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

    async def _create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        self.logger.debug(f"Creating response for model: {model}, max_tokens: {max_tokens}")
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
        return len(text.split())

    async def select_model(self, task: str) -> str:
        if "simple" in task.lower():
            return "claude-3-haiku-20240307"
        elif "complex" in task.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

    async def get_call_count(self):
        return self.call_count

    async def get_error_count(self):
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

    def __init__(self, rate_limit: int = 10, reset_time: int = 60):
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
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.debug("Initialized MockClaudeClient")

    @property
    def messages(self):
        if self._messages is None:
            self._messages = self.Messages(self)
            self.logger.debug("Created Messages instance")
        return self._messages
        self.logger = logging.getLogger(__name__)

    async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
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
                self.logger.error("Simulated API error")
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
        return len(text.split())

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
    def __init__(self, api_key: str):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.debug(f"Initializing MockClaudeClient {id(self)} with api_key: {api_key[:5]}...")
        
        self.api_key = api_key
        self.rate_limit = 10
        self.reset_time = 60
        self.calls = 0
        self.last_reset = asyncio.get_event_loop().time()
        self.error_mode = False
        self.latency = 0
        self.responses = {}
        self.max_test_tokens = 1000
        self.call_count = 0
        self.error_count = 0
        self.max_errors = 3
        self.logger.debug(f"Finished initialization of MockClaudeClient {id(self)}")

    def __str__(self):
        return f"MockClaudeClient(call_count={self.call_count}, error_count={self.error_count}, error_mode={self.error_mode})"

    def __repr__(self):
        return self.__str__()

    async def messages(self, model: str, max_tokens: int, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        self.logger.debug(f"Messages method called with model: {model}, max_tokens: {max_tokens}")
        return await self._create(model, max_tokens, messages, **kwargs)

    async def _create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        self.logger.debug(f"Creating response for model: {model}, max_tokens: {max_tokens}")
        await self._check_rate_limit()
        await asyncio.sleep(self.latency)

        if self.error_mode:
            self.error_count += 1
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                raise APIStatusError("Simulated API error", response=MagicMock(), body={})

        prompt = messages[-1]['content']
        self.logger.debug(f"Received prompt: {prompt[:50]}...")
        if sum(len(m['content']) for m in messages) > self.max_test_tokens:
            self.logger.warning(f"Total message length exceeds max test tokens")
            raise ValueError(f"Total message length exceeds maximum test tokens ({self.max_test_tokens})")

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
        return len(text.split())

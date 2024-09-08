import asyncio
import time
import logging
from typing import Dict, Any, List
from unittest.mock import MagicMock
from anthropic import RateLimitError, APIError, APIStatusError
from src.exceptions import RateLimitError as CustomRateLimitError

logging.getLogger(__name__).addHandler(logging.NullHandler())

class MockClaudeClient:
    def __init__(self):
        self.rate_limit_reached = False
        self.error_mode = False
        self.responses = {}
        self.messages = self
        self.max_test_tokens = 1000
        self.call_count = 0
        self.rate_limit_threshold = 5  # Number of calls before rate limiting
        self.last_call_time = 0
        self.latency = 0.1  # Default latency in seconds
        self.logger = logging.getLogger(__name__)

    async def count_tokens(self, text: str) -> int:
        await asyncio.sleep(0.01)  # Simulate a short delay
        return len(text.split())

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        if len(prompt) > self.max_test_tokens:
            raise ValueError(f"Prompt length ({len(prompt)} tokens) exceeds maximum context length of {self.max_test_tokens} tokens")
        response = await self.create(model, self.max_test_tokens, [{"role": "user", "content": prompt}])
        return response.content[0].text

    async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        await self._simulate_latency()
        async with self.lock:
            current_time = time.time()
            if current_time - self.last_call_time >= self.rate_limit_reset_time:
                self.call_count = 0
            self.last_call_time = current_time
            self.call_count += 1
            
            self.logger.debug(f"Call count: {self.call_count}, Threshold: {self.rate_limit_threshold}")
            
            if self.rate_limit_reached or self.call_count > self.rate_limit_threshold:
                self.logger.warning("Rate limit exceeded")
                raise CustomRateLimitError("Rate limit exceeded")
            if self.error_mode:
                self.error_count += 1
                if self.error_count <= self.max_errors:
                    self.logger.error("API error (error mode)")
                    raise APIStatusError("API error", response=MagicMock(), body={})
                else:
                    self.error_mode = False
                    self.error_count = 0
            
            prompt = messages[0]['content']
            if len(prompt) > self.max_test_tokens:
                self.logger.warning(f"Test input exceeds maximum allowed tokens ({self.max_test_tokens})")
                raise ValueError(f"Test input exceeds maximum allowed tokens ({self.max_test_tokens})")
            
            response = self.responses.get(prompt, "Default mock response")
            if len(response) > self.max_test_tokens:
                response = response[:self.max_test_tokens] + "..."
            
            await asyncio.sleep(0.1)  # Simulate some processing time
            
            self.logger.debug(f"Returning response: {response[:50]}...")
            return MagicMock(content=[MagicMock(text=response)])
        self.call_count = 0
        self.rate_limit_threshold = 5  # Number of calls before rate limiting
        self.last_call_time = 0
        self.error_count = 0
        self.max_errors = 3
        self.rate_limit_reset_time = 60  # seconds
        self.latency = 0.1  # Default latency in seconds
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)

    async def count_tokens(self, text: str) -> int:
        await asyncio.sleep(0.01)  # Simulate a short delay
        return len(text.split())

    async def set_response(self, prompt: str, response: str):
        self.responses[prompt] = response

    async def set_rate_limit(self, limit_reached: bool):
        self.rate_limit_reached = limit_reached

    async def set_error_mode(self, error_mode: bool):
        self.error_mode = error_mode

    async def set_latency(self, latency: float):
        self.latency = latency

    async def reset(self):
        self.rate_limit_reached = False
        self.error_mode = False
        self.responses = {}
        self.call_count = 0
        self.last_call_time = 0
        self.error_count = 0
        self.latency = 0.1

    async def messages(self):
        return self

    async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        await self._simulate_latency()
        async with self.lock:
            current_time = time.time()
            if current_time - self.last_call_time >= self.rate_limit_reset_time:
                self.call_count = 0
            self.last_call_time = current_time
            self.call_count += 1
            
            self.logger.debug(f"Call count: {self.call_count}, Threshold: {self.rate_limit_threshold}")
            
            if self.rate_limit_reached or self.call_count > self.rate_limit_threshold:
                self.logger.warning("Rate limit exceeded")
                raise CustomRateLimitError("Rate limit exceeded")
            if self.error_mode:
                self.error_count += 1
                if self.error_count <= self.max_errors:
                    self.logger.error("API error (error mode)")
                    raise APIStatusError("API error", response=MagicMock(), body={})
                else:
                    self.error_mode = False
                    self.error_count = 0
            
            prompt = messages[0]['content']
            if len(prompt) > self.max_test_tokens:
                self.logger.warning(f"Test input exceeds maximum allowed tokens ({self.max_test_tokens})")
                raise ValueError(f"Test input exceeds maximum allowed tokens ({self.max_test_tokens})")
            
            response = self.responses.get(prompt, "Default mock response")
            if len(response) > self.max_test_tokens:
                response = response[:self.max_test_tokens] + "..."
            
            await asyncio.sleep(0.1)  # Simulate some processing time
            
            self.logger.debug(f"Returning response: {response[:50]}...")
            return MagicMock(content=[MagicMock(text=response)])

    async def count_tokens(self, text: str) -> int:
        await asyncio.sleep(0.01)  # Simulate a short delay
        return len(text.split())

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        response = await self.create(model, self.max_test_tokens, [{"role": "user", "content": prompt}])
        return response.content[0].text

    async def count_tokens(self, text: str) -> int:
        # This is a simple approximation. For more accurate results, use a proper tokenizer.
        return len(text.split())

    async def _simulate_latency(self):
        await asyncio.sleep(self.latency)

    async def wait_for_rate_limit_reset(self):
        await asyncio.sleep(self.rate_limit_reset_time)
        self.call_count = 0

    async def set_rate_limit_threshold(self, threshold: int):
        self.rate_limit_threshold = threshold

    async def set_rate_limit_reset_time(self, reset_time: int):
        self.rate_limit_reset_time = reset_time

    async def simulate_concurrent_calls(self, num_calls: int):
        tasks = [self.create("test-model", 100, [{"role": "user", "content": f"Test {i}"}]) for i in range(num_calls)]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def get_call_count(self):
        return self.call_count

    async def get_error_count(self):
        return self.error_count
import asyncio
from typing import Dict, List, Optional
from anthropic import AsyncAnthropic

class MockClaudeClient:
    def __init__(self, rate_limit: int = 10, reset_interval: int = 60):
        self.rate_limit = rate_limit
        self.reset_interval = reset_interval
        self.calls = 0
        self.last_reset = asyncio.get_event_loop().time()
        self.error_mode = False
        self.latency = 0
        self.messages = self  # Add this line to create a 'messages' attribute

    async def messages_create(self, model: str, max_tokens: int, messages: List[Dict[str, str]], **kwargs) -> Dict:
        await self._check_rate_limit()
        await asyncio.sleep(self.latency)

        if self.error_mode:
            raise Exception("Simulated API error")

        response = {
            "content": [{"text": "This is a mock response from Claude."}],
            "model": model,
            "usage": {
                "input_tokens": sum(len(m["content"]) for m in messages) // 4,
                "output_tokens": 10
            }
        }
        return response

    async def _check_rate_limit(self):
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_reset > self.reset_interval:
            self.calls = 0
            self.last_reset = current_time

        self.calls += 1
        if self.calls > self.rate_limit:
            raise Exception("Rate limit exceeded")

    def set_error_mode(self, enabled: bool):
        self.error_mode = enabled

    def set_latency(self, latency: float):
        self.latency = latency

    def reset(self):
        self.calls = 0
        self.last_reset = asyncio.get_event_loop().time()
        self.error_mode = False
        self.latency = 0

    async def count_tokens(self, text: str) -> int:
        # Simple mock implementation
        return len(text.split())

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        response = await self.messages_create(model, 1000, [{"role": "user", "content": prompt}])
        return response["content"][0]["text"]

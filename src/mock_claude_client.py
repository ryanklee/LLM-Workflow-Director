import asyncio
import time
from typing import Dict, Any, List
from anthropic import RateLimitError, APIError

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
        self.error_count = 0
        self.max_errors = 3
        self.rate_limit_reset_time = 60  # seconds
        self.latency = 0.1  # Default latency in seconds

    def set_response(self, prompt: str, response: str):
        self.responses[prompt] = response

    def set_rate_limit(self, limit_reached: bool):
        self.rate_limit_reached = limit_reached

    def set_error_mode(self, error_mode: bool):
        self.error_mode = error_mode

    def set_latency(self, latency: float):
        self.latency = latency

    def reset(self):
        self.rate_limit_reached = False
        self.error_mode = False
        self.responses = {}
        self.call_count = 0
        self.last_call_time = 0
        self.error_count = 0
        self.latency = 0.1

    async def create(self, model: str, max_tokens: int, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        await self._simulate_latency()
        current_time = time.time()
        if current_time - self.last_call_time >= self.rate_limit_reset_time:
            self.call_count = 0
        self.last_call_time = current_time
        self.call_count += 1
        
        if self.rate_limit_reached or self.call_count > self.rate_limit_threshold:
            raise RateLimitError("Rate limit exceeded")
        if self.error_mode:
            self.error_count += 1
            if self.error_count <= self.max_errors:
                raise APIError("API error")
            else:
                self.error_mode = False
                self.error_count = 0
        
        prompt = messages[0]['content']
        if len(prompt) > self.max_test_tokens:
            raise ValueError(f"Test input exceeds maximum allowed tokens ({self.max_test_tokens})")
        
        response = self.responses.get(prompt, "Default mock response")
        if len(response) > self.max_test_tokens:
            response = response[:self.max_test_tokens] + "..."
        
        return {
            "content": [{"text": f"<response>{response}</response>"}],
            "model": model,
            "usage": {"total_tokens": len(response.split())}
        }

    async def _simulate_latency(self):
        await asyncio.sleep(self.latency)

    async def completion(self, prompt: str, model: str, max_tokens_to_sample: int, **kwargs) -> Dict[str, Any]:
        return await self.create(model, max_tokens_to_sample, [{"role": "user", "content": prompt}])

    async def completions(self, prompt: str, model: str, max_tokens_to_sample: int, **kwargs) -> Dict[str, Any]:
        return await self.completion(prompt, model, max_tokens_to_sample, **kwargs)

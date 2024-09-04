from unittest.mock import MagicMock
import time

class MockClaudeClient:
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.messages = MagicMock()
        self.messages.create = self.mock_create
        self.call_count = 0
        self.rate_limit = 10  # Example: 10 calls per minute
        self.last_reset = time.time()

    def mock_create(self, model, max_tokens, messages):
        self.check_rate_limit()
        prompt = messages[0]['content']
        if prompt in self.responses:
            response = self.responses[prompt]
            if isinstance(response, Exception):
                raise response
            return MagicMock(content=[MagicMock(text=response)])
        return MagicMock(content=[MagicMock(text="Default mock response")])

    def add_response(self, prompt, response):
        self.responses[prompt] = response

    def add_error_response(self, prompt, error):
        self.responses[prompt] = error

    def check_rate_limit(self):
        current_time = time.time()
        if current_time - self.last_reset >= 60:
            self.call_count = 0
            self.last_reset = current_time
        
        self.call_count += 1
        if self.call_count > self.rate_limit:
            raise Exception("Rate limit exceeded")

    def reset_call_count(self):
        self.call_count = 0
        self.last_reset = time.time()
from typing import Dict, Any, Optional
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

class MockClaudeClient:
    def __init__(self):
        self.rate_limit_reached = False
        self.error_mode = False
        self.responses = {}
        self.messages = self

    def set_response(self, prompt: str, response: str):
        self.responses[prompt] = response

    def set_rate_limit(self, limit_reached: bool):
        self.rate_limit_reached = limit_reached

    def set_error_mode(self, error_mode: bool):
        self.error_mode = error_mode

    def reset(self):
        self.rate_limit_reached = False
        self.error_mode = False
        self.responses = {}

    def create(self, model: str, max_tokens: int, messages: list) -> Dict[str, Any]:
        if self.rate_limit_reached:
            raise Exception("Rate limit exceeded")
        if self.error_mode:
            raise Exception("API error")
        
        prompt = messages[0]['content']
        response = self.responses.get(prompt, "Default mock response")
        return {
            "content": [{"text": response}],
            "model": model,
            "usage": {"total_tokens": len(response.split())}
        }

    def completion(self, prompt: str, model: str, max_tokens_to_sample: int, **kwargs) -> Dict[str, Any]:
        return self.create(model, max_tokens_to_sample, [{"role": "user", "content": prompt}])

    def completions(self, prompt: str, model: str, max_tokens_to_sample: int, **kwargs) -> Dict[str, Any]:
        return self.completion(prompt, model, max_tokens_to_sample, **kwargs)

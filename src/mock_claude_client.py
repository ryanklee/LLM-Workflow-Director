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

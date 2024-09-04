from unittest.mock import MagicMock

class MockClaudeClient:
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.messages = MagicMock()
        self.messages.create = self.mock_create

    def mock_create(self, model, max_tokens, messages):
        prompt = messages[0]['content']
        response = self.responses.get(prompt, "Default mock response")
        return MagicMock(content=[MagicMock(text=response)])

    def add_response(self, prompt, response):
        self.responses[prompt] = response

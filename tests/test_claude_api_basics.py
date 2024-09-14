import pytest
import logging
from src.exceptions import RateLimitError
from src.claude_manager import ClaudeManager

logger = logging.getLogger(__name__)

@pytest.mark.asyncio
class TestClaudeAPIBasics:
    @pytest.mark.fast
    async def test_claude_api_call(self, claude_manager, mock_claude_client):
        await mock_claude_client.set_response("Intro", "Claude AI")
        response = await claude_manager.generate_response("Intro")
        assert isinstance(response, str)
        assert "<response>" in response
        assert "</response>" in response
        assert "Claude AI" in response

    @pytest.mark.fast
    @pytest.mark.parametrize("task,expected_model", [
        ("simple", "claude-3-haiku-20240307"),
        ("moderate", "claude-3-sonnet-20240229"),
        ("complex", "claude-3-opus-20240229"),
    ])
    async def test_tiered_model_selection(self, claude_manager, task, expected_model):
        assert await claude_manager.select_model(task) == expected_model

    @pytest.mark.fast
    @pytest.mark.asyncio
    async def test_token_counting(self, claude_manager):
        text = "This is a test sentence."
        token_count = await claude_manager.count_tokens(text)
        assert token_count == 5, f"Expected 5 tokens, but got {token_count}"
        
        long_text = "This is a longer test sentence with more tokens to count."
        long_token_count = await claude_manager.count_tokens(long_text)
        assert long_token_count == 11, f"Expected 11 tokens, but got {long_token_count}"
        
        empty_text = ""
        empty_token_count = await claude_manager.count_tokens(empty_text)
        assert empty_token_count == 0, f"Expected 0 tokens for empty string, but got {empty_token_count}"

    @pytest.mark.fast
    @pytest.mark.asyncio
    async def test_generate_response(self, claude_manager):
        prompt = "Tell me a joke"
        response = await claude_manager.generate_response(prompt)
        assert isinstance(response, str), "Response should be a string"
        assert len(response) > 0, "Response should not be empty"
        assert "<response>" in response and "</response>" in response, "Response should be wrapped in <response> tags"

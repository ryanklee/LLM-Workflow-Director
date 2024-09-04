import pytest
from unittest.mock import patch
from src.claude_manager import ClaudeManager
from src.llm_evaluator import LLMEvaluator
from src.mock_claude_client import MockClaudeClient

@pytest.fixture
def mock_claude_client():
    return MockClaudeClient()

@pytest.fixture
def claude_manager(mock_claude_client):
    return ClaudeManager(client=mock_claude_client)

@pytest.fixture
def llm_evaluator():
    return LLMEvaluator()

class TestClaudeAPIIntegration:
    @pytest.mark.fast
    def test_claude_api_call(self, claude_manager, mock_claude_client):
        mock_claude_client.add_response("Intro", "Claude AI")
        response = claude_manager.generate_response("Intro")
        assert "Claude" in response and "AI" in response

    @pytest.mark.fast
    @pytest.mark.parametrize("task,expected_model", [
        ("simple", "claude-3-haiku-20240307"),
        ("moderate", "claude-3-sonnet-20240229"),
        ("complex", "claude-3-opus-20240229"),
    ])
    def test_tiered_model_selection(self, claude_manager, task, expected_model):
        assert claude_manager.select_model(task) == expected_model

    @pytest.mark.fast
    @pytest.mark.parametrize("input_text", ["", "a" * 100100, "<script>", "SSN: 123", 123, "   "])
    def test_input_validation_errors(self, claude_manager, input_text):
        with pytest.raises(ValueError):
            claude_manager.generate_response(input_text)

    @pytest.mark.fast
    def test_valid_inputs(self, claude_manager):
        for input_text in ["Hello", "!@#$"]:
            response = claude_manager.generate_response(input_text)
            assert response

    @pytest.mark.fast
    def test_response_parsing(self, claude_manager, llm_evaluator):
        claude_manager.client.add_response("Test", "Parsed")
        response = claude_manager.generate_response("Test")
        assert "<response>" in response and "</response>" in response
        assert llm_evaluator.evaluate_response(response, "Wrapped in <response> tags")

    @pytest.mark.slow
    def test_retry_mechanism(self, claude_manager):
        claude_manager.client.add_error_response("Test", Exception("Error"))
        claude_manager.client.add_response("Test", "Success")
        response = claude_manager.generate_response("Test")
        assert "Success" in response

    @pytest.mark.slow
    def test_consistency(self, claude_manager):
        claude_manager.client.add_response("France capital", "Paris")
        response1 = claude_manager.generate_response("France capital")
        response2 = claude_manager.generate_response("France capital")
        assert "Paris" in response1 and "Paris" in response2

    @pytest.mark.fast
    def test_rate_limiting(self, claude_manager):
        claude_manager.client.set_rate_limit(True)
        with pytest.raises(Exception, match="Rate limit exceeded"):
            claude_manager.generate_response("Test")
        claude_manager.client.set_rate_limit(False)
        assert claude_manager.generate_response("Test")
import pytest
from src.claude_manager import ClaudeManager
from src.mock_claude_client import MockClaudeClient

# ... (previous code)

def test_mock_claude_client_response(mock_claude_client, claude_manager):
    mock_claude_client.set_response("Test prompt", "Test response")
    response = claude_manager.get_completion("Test prompt", "claude-3-haiku-20240307", 100)
    assert response == "Test response"

def test_mock_claude_client_rate_limit(mock_claude_client, claude_manager):
    mock_claude_client.set_rate_limit(True)
    with pytest.raises(Exception, match="Rate limit exceeded"):
        claude_manager.get_completion("Test prompt", "claude-3-haiku-20240307", 100)

def test_mock_claude_client_error_mode(mock_claude_client, claude_manager):
    mock_claude_client.set_error_mode(True)
    with pytest.raises(Exception, match="API error"):
        claude_manager.get_completion("Test prompt", "claude-3-haiku-20240307", 100)

def test_mock_claude_client_reset(mock_claude_client, claude_manager):
    mock_claude_client.set_rate_limit(True)
    mock_claude_client.set_error_mode(True)
    mock_claude_client.set_response("Test prompt", "Test response")
    
    mock_claude_client.reset()
    
    response = claude_manager.get_completion("Test prompt", "claude-3-haiku-20240307", 100)
    assert response == "Default mock response"

import pytest
from unittest.mock import patch, MagicMock
from src.claude_manager import ClaudeManager
import tenacity
import anthropic
import re
from src.llm_evaluator import LLMEvaluator

@pytest.fixture
def claude_manager():
    return ClaudeManager()

@pytest.fixture
def llm_evaluator():
    return LLMEvaluator()

@pytest.mark.fast
@patch('anthropic.Anthropic')
def test_claude_api_call(mock_anthropic, claude_manager, llm_evaluator):
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="I am Claude, an AI assistant created by Anthropic to be helpful, harmless, and honest.")]
    mock_client.messages.create.return_value = mock_response

    response = claude_manager.generate_response("Introduce yourself")
    
    assert "Claude" in response and "Anthropic" in response
    assert llm_evaluator.evaluate_response(response, "The response should mention Claude and Anthropic")

@pytest.mark.fast
@pytest.mark.parametrize("task,expected_model", [
    ("simple task", "claude-3-haiku-20240307"),
    ("moderate complexity task", "claude-3-sonnet-20240229"),
    ("highly complex task", "claude-3-opus-20240229"),
])
def test_tiered_model_selection(claude_manager, task, expected_model):
    assert claude_manager.select_model(task) == expected_model

@pytest.mark.fast
def test_error_handling(claude_manager):
    with patch.object(claude_manager, 'client') as mock_client:
        mock_client.messages.create.side_effect = Exception("API Error")

        with pytest.raises(Exception):
            claude_manager.generate_response("Test prompt")

@pytest.mark.fast
def test_input_validation(claude_manager):
    # Test with valid input
    assert claude_manager.generate_response("Valid input") == "Valid response"

    # Test various invalid inputs
    invalid_inputs = [
        ("", "Input cannot be empty"),
        ("a" * 100001, "Input exceeds maximum length"),
        ("<script>alert('xss');</script>", "Input contains prohibited content"),
        ("SSN: 123-45-6789", "Input contains sensitive information"),
        (123, "Input must be a string"),
        ("   \n\t   ", "Input cannot be empty or only whitespace"),
    ]

    for invalid_input, error_message in invalid_inputs:
        with pytest.raises(ValueError, match=error_message):
            claude_manager.generate_response(invalid_input)

    # Test with Unicode and special characters (valid inputs)
    valid_inputs = ["こんにちは", "!@#$%^&*()_+-=[]{}|;:,.<>?"]
    for valid_input in valid_inputs:
        assert claude_manager.generate_response(valid_input) == "Valid response"

@pytest.mark.fast
@patch('anthropic.Anthropic')
def test_response_parsing(mock_anthropic, claude_manager, llm_evaluator):
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="<response>Parsed response</response>")]
    mock_client.messages.create.return_value = mock_response

    response = claude_manager.generate_response("Test prompt")
    
    assert re.match(r"<response>.*</response>", response)
    assert llm_evaluator.evaluate_response(response, "The response should be wrapped in <response> tags")

@pytest.mark.slow
@patch('anthropic.Anthropic')
def test_retry_mechanism(mock_anthropic, claude_manager):
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_client.messages.create.side_effect = [
        Exception("Temporary error"),
        MagicMock(content=[MagicMock(text="<response>Successful response</response>")])
    ]

    response = claude_manager.generate_response("Test prompt")
    
    assert "Successful" in response
    assert mock_client.messages.create.call_count == 2

@pytest.mark.slow
@patch('anthropic.Anthropic')
def test_consistency(mock_anthropic, claude_manager, llm_evaluator):
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_responses = [
        MagicMock(content=[MagicMock(text="The capital of France is Paris.")]),
        MagicMock(content=[MagicMock(text="Paris is the capital city of France.")])
    ]
    mock_client.messages.create.side_effect = mock_responses

    response1 = claude_manager.generate_response("What is the capital of France?")
    response2 = claude_manager.generate_response("Tell me the capital of France.")

    assert "Paris" in response1 and "Paris" in response2
    assert llm_evaluator.evaluate_response(response1, "The answer should mention Paris as the capital of France")
    assert llm_evaluator.evaluate_response(response2, "The answer should mention Paris as the capital of France")

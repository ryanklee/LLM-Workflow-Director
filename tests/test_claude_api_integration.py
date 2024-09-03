import pytest
from unittest.mock import patch, MagicMock
from src.claude_manager import ClaudeManager
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
    mock_response.content = [MagicMock(text="Claude by Anthropic")]
    mock_client.messages.create.return_value = mock_response

    response = claude_manager.generate_response("Introduce")
    
    assert "Claude" in response and "Anthropic" in response
    assert llm_evaluator.evaluate_response(response, "Mention Claude and Anthropic")

@pytest.mark.fast
@pytest.mark.parametrize("task,expected_model", [
    ("simple", "claude-3-haiku-20240307"),
    ("moderate", "claude-3-sonnet-20240229"),
    ("complex", "claude-3-opus-20240229"),
])
def test_tiered_model_selection(claude_manager, task, expected_model):
    assert claude_manager.select_model(task) == expected_model

@pytest.mark.fast
def test_input_validation(claude_manager):
    response = claude_manager.generate_response("Valid")
    assert isinstance(response, str)

    invalid_inputs = [
        ("", "empty"),
        ("a" * 100001, "length"),
        ("<script>", "prohibited"),
        ("SSN: 123", "sensitive"),
        (123, "string"),
        ("   ", "whitespace"),
    ]

    for invalid_input, error_type in invalid_inputs:
        with pytest.raises(ValueError):
            claude_manager.generate_response(invalid_input)

    valid_inputs = ["こんにちは", "!@#$%^&*()"]
    for valid_input in valid_inputs:
        response = claude_manager.generate_response(valid_input)
        assert len(response) > 0

@pytest.mark.fast
@patch('anthropic.Anthropic')
def test_response_parsing(mock_anthropic, claude_manager, llm_evaluator):
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="<response>Parsed</response>")]
    mock_client.messages.create.return_value = mock_response

    response = claude_manager.generate_response("Test")
    
    assert "<response>" in response and "</response>" in response
    assert llm_evaluator.evaluate_response(response, "Wrapped in <response> tags")

@pytest.mark.slow
@patch('anthropic.Anthropic')
def test_retry_mechanism(mock_anthropic, claude_manager):
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_client.messages.create.side_effect = [
        Exception("Error"),
        MagicMock(content=[MagicMock(text="Success")])
    ]

    response = claude_manager.generate_response("Test")
    
    assert "Success" in response
    assert mock_client.messages.create.call_count == 2

@pytest.mark.slow
@patch('anthropic.Anthropic')
def test_consistency(mock_anthropic, claude_manager, llm_evaluator):
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_responses = [
        MagicMock(content=[MagicMock(text="Paris, France")]),
        MagicMock(content=[MagicMock(text="Paris, capital of France")])
    ]
    mock_client.messages.create.side_effect = mock_responses

    response1 = claude_manager.generate_response("Capital of France?")
    response2 = claude_manager.generate_response("France capital?")

    assert "Paris" in response1 and "Paris" in response2
    assert llm_evaluator.evaluate_response(response1, "Paris as capital")
    assert llm_evaluator.evaluate_response(response2, "Paris as capital")

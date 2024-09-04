import pytest
from unittest.mock import patch, MagicMock
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

@pytest.mark.fast
def test_claude_api_call(claude_manager, mock_claude_client, llm_evaluator):
    mock_claude_client.add_response("Introduce", "Claude by Anthropic")

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
    with patch.object(claude_manager.messages, 'create') as mock_create:
        mock_create.return_value = MagicMock(content=[MagicMock(text="Valid response")])
    
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
def test_response_parsing(claude_manager, llm_evaluator):
    with patch.object(claude_manager.messages, 'create') as mock_create:
        mock_create.return_value = MagicMock(content=[MagicMock(text="Parsed")])

    response = claude_manager.generate_response("Test")
    
    assert "<response>" in response and "</response>" in response
    assert llm_evaluator.evaluate_response(response, "Wrapped in <response> tags")

@pytest.mark.slow
def test_retry_mechanism(claude_manager):
    with patch.object(claude_manager.messages, 'create') as mock_create:
        mock_create.side_effect = [
            Exception("Error"),
            MagicMock(content=[MagicMock(text="Success")])
        ]

    response = claude_manager.generate_response("Test")
    
    assert "Success" in response
    assert claude_manager.client.messages.create.call_count == 2

@pytest.mark.slow
def test_consistency(claude_manager, llm_evaluator):
    mock_responses = [
        MagicMock(content=[MagicMock(text="Paris, France")]),
        MagicMock(content=[MagicMock(text="Paris, capital of France")])
    ]
    with patch.object(claude_manager.messages, 'create') as mock_create:
        mock_create.side_effect = mock_responses

    response1 = claude_manager.generate_response("Capital of France?")
    response2 = claude_manager.generate_response("France capital?")

    assert "Paris" in response1 and "Paris" in response2
    assert llm_evaluator.evaluate_response(response1, "Paris as capital")
    assert llm_evaluator.evaluate_response(response2, "Paris as capital")

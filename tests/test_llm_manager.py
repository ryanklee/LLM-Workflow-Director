import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_llm():
    with patch('src.llm_manager.llm') as mock_llm:
        mock_model = MagicMock()
        mock_llm.get_model.return_value = mock_model
        yield mock_llm

@pytest.mark.skipif("llm" not in globals(), reason="llm module not available")
def test_llm_manager_initialization(mock_llm):
    from src.llm_manager import LLMManager
    manager = LLMManager()
    assert hasattr(manager, 'model')

@pytest.mark.skipif("llm" not in globals(), reason="llm module not available")
def test_llm_manager_query(mock_llm):
    from src.llm_manager import LLMManager
    manager = LLMManager()
    mock_response = MagicMock()
    mock_response.text.return_value = "Test response"
    manager.model.prompt.return_value = mock_response

    result = manager.query("Test prompt")
    assert result == "Test response"

@pytest.mark.skipif("llm" not in globals(), reason="llm module not available")
def test_llm_manager_query_error(mock_llm):
    from src.llm_manager import LLMManager
    manager = LLMManager()
    manager.model.prompt.side_effect = Exception("Test error")

    result = manager.query("Test prompt")
    assert "Error querying LLM: Test error" in result

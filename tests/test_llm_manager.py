from unittest.mock import patch, MagicMock
from src.llm_manager import LLMManager, llm_spec

@patch('src.llm_manager.llm_spec', None)
def test_llm_manager_initialization_mock_mode():
    manager = LLMManager()
    assert manager.mock_mode == True
    assert manager.model is None

@patch('src.llm_manager.llm_spec', MagicMock())
@patch('src.llm_manager.importlib.import_module')
def test_llm_manager_initialization_llm_mode(mock_import):
    mock_llm = MagicMock()
    mock_model = MagicMock()
    mock_model.name = "TestModel"
    mock_llm.models = [mock_model]
    mock_import.return_value = mock_llm
    
    manager = LLMManager()
    assert manager.mock_mode == False
    assert manager.model == mock_model

def test_llm_manager_query():
    manager = LLMManager()
    result = manager.query("Test prompt")
    assert isinstance(result, str)
    if manager.mock_mode:
        assert result == "Mock response to: Test prompt"
    else:
        assert "LLM response:" in result

@patch('src.llm_manager.llm_spec', MagicMock())
@patch('src.llm_manager.importlib.import_module')
def test_llm_manager_query_error(mock_import):
    mock_llm = MagicMock()
    mock_model = MagicMock()
    mock_model.prompt.side_effect = Exception("Test error")
    mock_llm.models = [mock_model]
    mock_import.return_value = mock_llm
    
    manager = LLMManager()
    result = manager.query("Test prompt")
    assert "Error querying LLM: Test error" in result

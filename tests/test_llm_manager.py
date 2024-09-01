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
    assert result == "Mock response to: Test prompt"

def test_llm_manager_query_with_context():
    manager = LLMManager()
    context = {"key1": "value1", "key2": "value2"}
    result = manager.query("Test prompt", context)
    assert isinstance(result, str)
    assert result == "Mock response to: Test prompt"

@patch('src.llm_manager.llm_spec', MagicMock())
@patch('src.llm_manager.importlib.import_module')
def test_llm_manager_query_error(mock_import):
    mock_llm = MagicMock()
    mock_model = MagicMock()
    mock_model.prompt.side_effect = Exception("Test error")
    mock_llm.models = [mock_model]
    mock_import.return_value = mock_llm
    
    manager = LLMManager()
    manager.mock_mode = False  # Force non-mock mode for this test
    result = manager.query("Test prompt")
    assert result == "Error querying LLM: Test error"

def test_llm_manager_format_prompt():
    manager = LLMManager()
    prompt = "Test prompt"
    context = {"key1": "value1", "key2": "value2"}
    formatted_prompt = manager._format_prompt(prompt, context)
    assert "Context:" in formatted_prompt
    assert "key1: value1" in formatted_prompt
    assert "key2: value2" in formatted_prompt
    assert "Prompt: Test prompt" in formatted_prompt

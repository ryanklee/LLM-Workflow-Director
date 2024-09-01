import pytest
from src.llm_manager import LLMManager

def test_llm_manager_initialization():
    manager = LLMManager()
    assert hasattr(manager, 'mock_mode')

def test_llm_manager_query():
    manager = LLMManager()
    result = manager.query("Test prompt")
    assert isinstance(result, str)
    if manager.mock_mode:
        assert result == "Mock response to: Test prompt"

def test_llm_manager_query_error():
    manager = LLMManager()
    if not manager.mock_mode:
        def mock_prompt(x):
            raise Exception("Test error")
        manager.model.prompt = mock_prompt
    result = manager.query("Test prompt")
    if manager.mock_mode:
        assert result == "Mock response to: Test prompt"
    else:
        assert "Error querying LLM: Test error" in result

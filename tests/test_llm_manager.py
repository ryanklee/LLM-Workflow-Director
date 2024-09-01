import pytest
from src.llm_manager import LLMManager

def test_llm_manager_initialization():
    manager = LLMManager()
    assert hasattr(manager, 'mock_mode')

def test_llm_manager_query():
    manager = LLMManager()
    result = manager.query("Test prompt")
    if manager.mock_mode:
        assert result == "Mock response to: Test prompt"
    else:
        assert isinstance(result, str)

def test_llm_manager_query_error():
    manager = LLMManager()
    if not manager.mock_mode:
        manager.model.prompt = lambda x: (_ for _ in ()).throw(Exception("Test error"))
    result = manager.query("Test prompt")
    if manager.mock_mode:
        assert result == "Mock response to: Test prompt"
    else:
        assert "Error querying LLM: Test error" in result

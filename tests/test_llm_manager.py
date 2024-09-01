from unittest.mock import patch, MagicMock
from src.llm_manager import LLMManager

def test_llm_manager_initialization():
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client:
        manager = LLMManager()
        assert isinstance(manager.client, MagicMock)
        assert isinstance(manager.cache, dict)

@patch('src.llm_manager.LLMMicroserviceClient')
def test_llm_manager_query(mock_client):
    mock_client.return_value.query.return_value = "task_progress: 0.5\nstate_updates: {'key': 'value'}\nactions: action1, action2\nsuggestions: suggestion1, suggestion2\nresponse: Test response"
    manager = LLMManager()
    response = manager.query("Test prompt")
    assert isinstance(response, dict)
    assert 'task_progress' in response
    assert 'state_updates' in response
    assert 'actions' in response
    assert 'suggestions' in response
    assert 'response' in response
    assert 'id' in response

def test_llm_manager_query_with_context():
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client:
        mock_client.return_value.query.return_value = "Test response"
        manager = LLMManager()
        context = {
            "key1": "value1",
            "key2": "value2",
            "workflow_stage": "Test Stage",
            "stage_description": "Test stage description",
            "stage_tasks": ["Task 1", "Task 2"],
            "project_structure_instructions": "Test instructions",
            "coding_conventions": "Test conventions",
            "workflow_config": {
                "stages": [{"name": "Test Stage", "description": "Test description"}],
                "transitions": [{"from": "Test Stage", "to": "Next Stage"}]
            }
        }
        result = manager.query("Test prompt", context)
        assert isinstance(result, str)
        assert "Test response" in result
        assert "(ID:" in result
        mock_client.return_value.query.assert_called_once()
        call_args = mock_client.return_value.query.call_args[0]
        assert "Current Workflow Stage: Test Stage" in call_args[0]
        assert "Stage Description: Test stage description" in call_args[0]
        assert "Task 1" in call_args[0] and "Task 2" in call_args[0]
        assert "Project Structure:" in call_args[0]
        assert "Coding Conventions:" in call_args[0]
        assert "Stages:" in call_args[0] and "Transitions:" in call_args[0]
        assert "Task 1" in call_args[0] and "Task 2" in call_args[0]

def test_llm_manager_error_handling():
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client:
        mock_client.return_value.query.side_effect = [Exception("Test error"), Exception("Retry error"), "Success"]
        manager = LLMManager()
        result = manager.query("Test prompt")
        assert "Success" in result
        assert mock_client.return_value.query.call_count == 3

def test_llm_manager_query_with_tiers():
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client:
        mock_client.return_value.query.side_effect = ["Fast response", "Balanced response", "Powerful response"]
        manager = LLMManager()
        
        fast_result = manager.query("Short prompt", tier='fast')
        balanced_result = manager.query("Medium length prompt", tier='balanced')
        powerful_result = manager.query("Complex prompt", tier='powerful')
        
        assert "Fast response" in fast_result
        assert "Balanced response" in balanced_result
        assert "Powerful response" in powerful_result
        
        assert mock_client.return_value.query.call_count == 3
        mock_client.return_value.query.assert_any_call("Short prompt", None, 'fast')
        mock_client.return_value.query.assert_any_call("Medium length prompt", None, 'balanced')
        mock_client.return_value.query.assert_any_call("Complex prompt", None, 'powerful')

def test_llm_manager_caching():
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client:
        mock_client.return_value.query.side_effect = ["Response 1", "Response 2", "Response 3"]
        manager = LLMManager()
        prompt = "Test prompt"
        context = {"key": "value"}
        
        result1 = manager.query(prompt, context)
        assert "Response 1" in result1
        
        result2 = manager.query(prompt, context)
        assert result2 == result1  # Should return cached result
        
        result3 = manager.query("Different prompt", context)
        assert "Response 2" in result3
        assert result3 != result1
        
        manager.clear_cache()
        result4 = manager.query(prompt, context)
        assert "Response 3" in result4
        assert result4 != result1

def test_evaluate_sufficiency():
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client:
        mock_client.return_value.evaluate_sufficiency.return_value = {
            "is_sufficient": True,
            "reasoning": "All tasks completed"
        }
        manager = LLMManager()
        
        result = manager.evaluate_sufficiency("Test Stage", {"description": "Test"}, {"key": "value"})
        
        assert result["is_sufficient"] == True
        assert result["reasoning"] == "All tasks completed"
        mock_client.return_value.evaluate_sufficiency.assert_called_once_with("Test Stage", {"description": "Test"}, {"key": "value"})

def test_evaluate_sufficiency_error():
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client:
        mock_client.return_value.evaluate_sufficiency.side_effect = Exception("Test error")
        manager = LLMManager()
        
        result = manager.evaluate_sufficiency("Test Stage", {"description": "Test"}, {"key": "value"})
        
        assert result["is_sufficient"] == False
        assert "Error evaluating sufficiency: Test error" in result["reasoning"]

from unittest.mock import patch, MagicMock, ANY
from src.llm_manager import LLMManager, LLMCostOptimizer

def test_llm_manager_initialization():
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client:
        manager = LLMManager()
        assert isinstance(manager.client, MagicMock)
        assert isinstance(manager.cache, dict)
        assert isinstance(manager.cost_optimizer, LLMCostOptimizer)

@patch('src.llm_manager.LLMMicroserviceClient')
def test_llm_manager_query(mock_client):
    mock_client.return_value.query.return_value = "task_progress: 0.5\nstate_updates: {'key': 'value'}\nactions: action1, action2\nsuggestions: suggestion1, suggestion2\nresponse: Test response"
    manager = LLMManager()
    response = manager.query("Test prompt", tier='balanced')
    assert isinstance(response, dict)
    assert 'task_progress' in response
    assert 'state_updates' in response
    assert 'actions' in response
    assert 'suggestions' in response
    assert 'response' in response
    assert 'id' in response
    mock_client.return_value.query.assert_called_once_with(ANY, ANY, 'gpt-3.5-turbo', 500)

def test_llm_manager_get_usage_report():
    manager = LLMManager()
    manager.cost_optimizer.update_usage('fast', 100)
    manager.cost_optimizer.update_usage('balanced', 200)
    manager.cost_optimizer.update_usage('powerful', 300)
    report = manager.get_usage_report()
    assert 'usage_stats' in report
    assert 'total_cost' in report
    assert report['usage_stats']['fast']['count'] == 1
    assert report['usage_stats']['balanced']['count'] == 1
    assert report['usage_stats']['powerful']['count'] == 1

def test_llm_manager_get_optimization_suggestion():
    manager = LLMManager()
    manager.cost_optimizer.update_usage('fast', 100)
    manager.cost_optimizer.update_usage('balanced', 200)
    manager.cost_optimizer.update_usage('powerful', 300)
    suggestion = manager.get_optimization_suggestion()
    assert isinstance(suggestion, str)
    assert len(suggestion) > 0

def test_llm_manager_query_with_tiers():
    mock_client = MagicMock()
    mock_client.query.side_effect = ["Fast response", "Balanced response", "Powerful response"]
    manager = LLMManager()
    manager.client = mock_client
    
    fast_result = manager.query("Short prompt", tier='fast')
    balanced_result = manager.query("Medium length prompt", tier='balanced')
    powerful_result = manager.query("Complex prompt", tier='powerful')
    
    assert isinstance(fast_result, dict) and fast_result.get("response") == "Fast response"
    assert isinstance(balanced_result, dict) and balanced_result.get("response") == "Balanced response"
    assert isinstance(powerful_result, dict) and powerful_result.get("response") == "Powerful response"
    
    assert mock_client.query.call_count == 3
    mock_client.query.assert_any_call(ANY, ANY, 'gpt-3.5-turbo', 100)
    mock_client.query.assert_any_call(ANY, ANY, 'gpt-3.5-turbo', 500)
    mock_client.query.assert_any_call(ANY, ANY, 'gpt-4', 1000)

def test_determine_query_tier():
    manager = LLMManager()
    assert manager.determine_query_tier("Short query") == 'fast'
    assert manager.determine_query_tier("Medium length query with some details about the project") == 'balanced'
    assert manager.determine_query_tier("Complex query that requires detailed analysis of the project structure and implementation of new features") == 'powerful'

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
        assert isinstance(result, dict)
        assert "response" in result
        assert result["response"] == "Test response"
        assert "id" in result
        assert result["id"].startswith("(ID:")
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
        mock_client.return_value.query.side_effect = [
            Exception("Powerful error"),
            Exception("Balanced error"),
            Exception("Fast error")
        ]
        manager = LLMManager()
        result = manager.query("Test prompt", tier='powerful')
        assert isinstance(result, dict)
        assert "error" in result
        assert "Error querying LLM: Fast error" in result["error"]
        assert mock_client.return_value.query.call_count == 3

def test_llm_manager_fallback_to_fast():
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client:
        mock_client.return_value.query.side_effect = [
            Exception("Powerful error"),
            Exception("Balanced error"),
            Exception("Fast error")
        ]
        manager = LLMManager()
        result = manager.query("Test prompt", tier='powerful')
        assert isinstance(result, dict)
        assert "error" in result
        assert "Error querying LLM: Fast error" in result["error"]
        assert mock_client.return_value.query.call_count == 3

def test_llm_manager_query_with_tiers():
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client:
        mock_client.return_value.query.side_effect = ["Fast response", "Balanced response", "Powerful response"]
        manager = LLMManager()
            
        fast_result = manager.query("Short prompt", tier='fast')
        balanced_result = manager.query("Medium length prompt", tier='balanced')
        powerful_result = manager.query("Complex prompt", tier='powerful')
            
        assert isinstance(fast_result, dict) and fast_result.get("response") == "Fast response"
        assert isinstance(balanced_result, dict) and balanced_result.get("response") == "Balanced response"
        assert isinstance(powerful_result, dict) and powerful_result.get("response") == "Powerful response"
        
        assert mock_client.return_value.query.call_count == 3
        mock_client.return_value.query.assert_any_call("Short prompt", None, 'gpt-3.5-turbo', 100)
        mock_client.return_value.query.assert_any_call("Medium length prompt", None, 'gpt-3.5-turbo', 500)
        mock_client.return_value.query.assert_any_call("Complex prompt", None, 'gpt-4', 1000)

def test_determine_query_tier():
    manager = LLMManager()
    assert manager.determine_query_tier("Short query") == 'fast'
    assert manager.determine_query_tier("Medium length query with some details about the project") == 'balanced'
    assert manager.determine_query_tier("Complex query that requires detailed analysis of the project structure and implementation of new features") == 'powerful'

def test_llm_manager_caching():
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client:
        mock_client.return_value.query.side_effect = ["Response 1", "Response 2", "Response 3"]
        manager = LLMManager()
        prompt = "Test prompt"
        context = {"key": "value"}
            
        result1 = manager.query(prompt, context)
        assert isinstance(result1, dict) and result1.get("response") == "Response 1"
            
        result2 = manager.query(prompt, context)
        assert result2 == result1  # Should return cached result
            
        result3 = manager.query("Different prompt", context)
        assert isinstance(result3, dict) and result3.get("response") == "Response 2"
        assert result3 != result1
            
        manager.clear_cache()
        result4 = manager.query(prompt, context)
        assert result4.get("response") == "Response 3"
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

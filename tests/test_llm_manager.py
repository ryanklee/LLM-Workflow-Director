from unittest.mock import patch, MagicMock, ANY
from src.llm_manager import LLMManager, LLMCostOptimizer

def test_llm_manager_initialization():
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client, \
         patch('src.llm_manager.yaml.safe_load') as mock_yaml_load:
        mock_yaml_load.return_value = {
            'tiers': {
                'fast': {'model': 'gpt-3.5-turbo', 'max_tokens': 100},
                'balanced': {'model': 'gpt-3.5-turbo', 'max_tokens': 500},
                'powerful': {'model': 'gpt-4', 'max_tokens': 1000}
            },
            'prompt_templates': {
                'default': 'Default template',
                'sufficiency_evaluation': 'Sufficiency evaluation template'
            }
        }
        manager = LLMManager()
        assert isinstance(manager.client, MagicMock)
        assert isinstance(manager.cache, dict)
        assert isinstance(manager.cost_optimizer, LLMCostOptimizer)
        assert 'default' in manager.prompt_templates
        assert 'sufficiency_evaluation' in manager.prompt_templates

@patch('src.llm_manager.LLMMicroserviceClient')
@patch('anthropic.Anthropic')
@patch('time.time', side_effect=[0, 1])  # Mock start and end times
def test_llm_manager_query(mock_time, mock_anthropic, mock_client):
    mock_anthropic.return_value.messages.create.return_value.content = [type('obj', (object,), {'text': "task_progress: 0.5\nstate_updates: {'key': 'value'}\nactions: action1, action2\nsuggestions: suggestion1, suggestion2\nresponse: Test response"})()]
    manager = LLMManager()
    with patch.object(manager.cost_optimizer, 'select_optimal_tier', return_value='balanced'):
        with patch.object(manager.cost_optimizer, 'update_usage'):
            response = manager.query("Test prompt")
    assert isinstance(response, dict)
    assert 'task_progress' in response
    assert 'state_updates' in response
    assert 'actions' in response
    assert 'suggestions' in response
    assert 'response' in response
    assert 'id' in response
    mock_anthropic.return_value.messages.create.assert_called_once_with(
        model='claude-3-sonnet-20240229',
        max_tokens=4000,
        messages=[{"role": "user", "content": ANY}]
    )
    assert manager.cost_optimizer.usage_stats['balanced']['count'] == 1
    assert manager.cost_optimizer.performance_metrics['balanced']['avg_response_time'] > 0

@patch('src.llm_manager.LLMMicroserviceClient')
@patch('anthropic.Anthropic')
@patch('time.time', side_effect=[0, 1, 2, 3, 4, 5])  # Mock start and end times for multiple attempts
def test_llm_manager_query_with_error(mock_time, mock_anthropic, mock_client):
    mock_anthropic.return_value.messages.create.side_effect = Exception("Test error")
    manager = LLMManager()
    with patch.object(manager.cost_optimizer, 'select_optimal_tier', return_value='balanced'):
        response = manager.query("Test prompt")
    assert 'error' in response
    assert manager.cost_optimizer.usage_stats['fast']['count'] == 1  # Should fall back to 'fast' tier
    assert manager.cost_optimizer.performance_metrics['fast']['success_rate'] < 1.0

def test_llm_manager_tier_selection():
    manager = LLMManager()
    simple_query = "What is 2 + 2?"
    complex_query = "Analyze the implications of quantum computing on modern cryptography systems."
        
    with patch.object(manager, '_process_response', return_value={}):
        with patch.object(manager.cost_optimizer, 'select_optimal_tier', return_value='fast'):
            with patch.object(manager.client, 'query') as mock_query:
                with patch.object(manager.cost_optimizer, 'update_usage'):
                    manager.query(simple_query)
                    mock_query.assert_called_with(ANY, None, ANY, ANY)
        
        with patch.object(manager.cost_optimizer, 'select_optimal_tier', return_value='powerful'):
            with patch.object(manager.client, 'query') as mock_query:
                with patch.object(manager.cost_optimizer, 'update_usage'):
                    manager.query(complex_query)
                    mock_query.assert_called_with(ANY, None, ANY, ANY)
    
    # Check if the tier selection is working as expected
    assert manager.determine_query_tier(simple_query) == 'fast'
    assert manager.determine_query_tier(complex_query) == 'powerful'

def test_llm_manager_get_usage_report():
    manager = LLMManager()
    manager.cost_optimizer.update_usage('fast', 100, 0.5, True)
    manager.cost_optimizer.update_usage('balanced', 200, 1.0, True)
    manager.cost_optimizer.update_usage('powerful', 300, 1.5, True)
    report = manager.get_usage_report()
    assert 'usage_stats' in report
    assert 'total_cost' in report
    assert report['usage_stats']['fast']['count'] == 1
    assert report['usage_stats']['balanced']['count'] == 1
    assert report['usage_stats']['powerful']['count'] == 1

def test_llm_manager_get_optimization_suggestion():
    manager = LLMManager()
    manager.cost_optimizer.update_usage('fast', 100, 0.5, True)
    manager.cost_optimizer.update_usage('balanced', 200, 1.0, True)
    manager.cost_optimizer.update_usage('powerful', 300, 1.5, True)
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
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client, \
         patch('anthropic.Anthropic') as mock_anthropic, \
         patch('time.time', side_effect=[0, 1]):  # Mock start and end times
        mock_anthropic.return_value.messages.create.return_value.content = [type('obj', (object,), {'text': "Test response"})()]
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
        with patch.object(manager.cost_optimizer, 'update_usage'):
            result = manager.query("Test prompt", context)
        assert isinstance(result, dict)
        assert "response" in result
        assert "Test response" in result["response"]
        assert "id" in result
        assert result["id"].startswith("(ID:")
        mock_anthropic.return_value.messages.create.assert_called_once()
        call_args = mock_anthropic.return_value.messages.create.call_args[1]['messages'][0]['content']
        assert "Current Workflow Stage: Test Stage" in call_args
        assert "Stage Description: Test stage description" in call_args
        assert "Task 1" in call_args and "Task 2" in call_args
        assert "Project Structure:" in call_args
        assert "Coding Conventions:" in call_args
        assert "Stages:" in call_args and "Transitions:" in call_args

def test_llm_manager_error_handling():
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client, \
         patch('anthropic.Anthropic') as mock_anthropic:
        mock_anthropic.return_value.messages.create.side_effect = [
            AttributeError("'Anthropic' object has no attribute 'messages'"),
            AttributeError("'Anthropic' object has no attribute 'messages'"),
            AttributeError("'Anthropic' object has no attribute 'messages'")
        ]
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
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client, \
         patch('anthropic.Anthropic') as mock_anthropic:
        mock_anthropic.return_value.messages.create.side_effect = [
            AttributeError("'Anthropic' object has no attribute 'messages'"),
            AttributeError("'Anthropic' object has no attribute 'messages'"),
            AttributeError("'Anthropic' object has no attribute 'messages'")
        ]
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
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client, \
         patch('anthropic.Anthropic') as mock_anthropic, \
         patch('time.time', side_effect=[0, 1, 2, 3, 4, 5, 6, 7]):  # Mock start and end times
        mock_anthropic.return_value.messages.create.side_effect = [
            type('obj', (object,), {'content': [type('obj', (object,), {'text': "Fast response"})()]})(),
            type('obj', (object,), {'content': [type('obj', (object,), {'text': "Balanced response"})()]})(),
            type('obj', (object,), {'content': [type('obj', (object,), {'text': "Powerful response"})()]})()
        ]
        manager = LLMManager()
        
        with patch.object(manager.cost_optimizer, 'update_usage'):
            fast_result = manager.query("Short prompt", tier='fast')
            balanced_result = manager.query("Medium length prompt", tier='balanced')
            powerful_result = manager.query("Complex prompt", tier='powerful')
        
        assert isinstance(fast_result, dict) and "Fast response" in fast_result.get("response", "")
        assert isinstance(balanced_result, dict) and "Balanced response" in balanced_result.get("response", "")
        assert isinstance(powerful_result, dict) and "Powerful response" in powerful_result.get("response", "")
        
        assert mock_anthropic.return_value.messages.create.call_count == 3
        mock_anthropic.return_value.messages.create.assert_any_call(
            model='claude-3-haiku-20240307',
            max_tokens=1000,
            messages=[{"role": "user", "content": ANY}]
        )
        mock_anthropic.return_value.messages.create.assert_any_call(
            model='claude-3-sonnet-20240229',
            max_tokens=4000,
            messages=[{"role": "user", "content": ANY}]
        )
        mock_anthropic.return_value.messages.create.assert_any_call(
            model='claude-3-opus-20240229',
            max_tokens=4000,
            messages=[{"role": "user", "content": ANY}]
        )

def test_determine_query_tier():
    manager = LLMManager()
    assert manager.determine_query_tier("Short query") == 'fast'
    assert manager.determine_query_tier("Medium length query with some details about the project") == 'balanced'
    assert manager.determine_query_tier("Complex query that requires detailed analysis of the project structure and implementation of new features") == 'powerful'

def test_llm_manager_caching():
    with patch('src.llm_manager.LLMMicroserviceClient') as mock_client, \
         patch('anthropic.Anthropic') as mock_anthropic, \
         patch('time.time', side_effect=[0, 1, 2, 3, 4, 5, 6, 7]):  # Mock start and end times
        mock_anthropic.return_value.messages.create.side_effect = [
            type('obj', (object,), {'content': [type('obj', (object,), {'text': "Response 1"})()]}),
            type('obj', (object,), {'content': [type('obj', (object,), {'text': "Response 2"})()]}),
            type('obj', (object,), {'content': [type('obj', (object,), {'text': "Response 3"})()]})
        ]
        manager = LLMManager()
        prompt = "Test prompt"
        context = {"key": "value"}
        
        with patch.object(manager.cost_optimizer, 'update_usage'):
            result1 = manager.query(prompt, context)
            assert isinstance(result1, dict) and "Response 1" in result1.get("response", "")
            
            result2 = manager.query(prompt, context)
            assert result2 == result1  # Should return cached result
            
            result3 = manager.query("Different prompt", context)
            assert isinstance(result3, dict) and "Response 2" in result3.get("response", "")
            assert result3 != result1
            
            manager.clear_cache()
            result4 = manager.query(prompt, context)
            assert "Response 3" in result4.get("response", "")
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

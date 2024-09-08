import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock, ANY
from src.exceptions import RateLimitError
from src.claude_manager import ClaudeManager
from src.llm_manager import LLMManager, LLMCostOptimizer
import logging

# Setup logging
@pytest.fixture(autouse=True)
def setup_logging():
    logging.basicConfig(level=logging.DEBUG)
    yield
    logging.shutdown()

@pytest.fixture
async def mock_claude_manager():
    return AsyncMock(spec=ClaudeManager)

@pytest.fixture
async def llm_manager(mock_claude_manager):
    with patch('src.llm_manager.yaml.safe_load') as mock_yaml_load:
        mock_yaml_load.return_value = {
            'tiers': {
                'fast': {'model': 'claude-3-haiku-20240307', 'max_tokens': 100},
                'balanced': {'model': 'claude-3-sonnet-20240229', 'max_tokens': 500},
                'powerful': {'model': 'claude-3-opus-20240229', 'max_tokens': 1000}
            },
            'prompt_templates': {
                'default': 'Default template',
                'sufficiency_evaluation': 'Sufficiency evaluation template'
            }
        }
        manager = LLMManager(claude_manager=mock_claude_manager)
        return manager

@pytest.mark.asyncio
async def test_llm_manager_initialization(llm_manager):
    assert isinstance(llm_manager.claude_manager, (ClaudeManager, AsyncMock))
    assert isinstance(llm_manager.cache, dict)
    assert isinstance(llm_manager.cost_optimizer, LLMCostOptimizer)
    assert 'default' in llm_manager.prompt_templates
    assert 'sufficiency_evaluation' in llm_manager.prompt_templates

@pytest.mark.asyncio
async def test_llm_manager_query(llm_manager, mock_claude_manager):
    mock_response = "<response>task_progress: 0.5\nstate_updates: {'key': 'value'}\nactions: action1, action2\nsuggestions: suggestion1, suggestion2\nresponse: Test response</response>"
    mock_claude_manager.generate_response.return_value = mock_response
    with patch.object(llm_manager.cost_optimizer, 'select_optimal_tier', return_value='balanced'):
        with patch.object(llm_manager.cost_optimizer, 'update_usage') as mock_update_usage:
            with patch('time.time', side_effect=[0, 1]):
                response = await llm_manager.query("Test prompt")

    assert isinstance(response, dict)
    assert "Test response" in response.get("response", "")
    mock_update_usage.assert_called_once()
    assert all(key in response for key in ['task_progress', 'state_updates', 'actions', 'suggestions', 'response'])
    assert 'id' in response
    mock_claude_manager.generate_response.assert_called_once()
    call_args = mock_claude_manager.generate_response.call_args
    assert call_args is not None
    assert call_args[1]['model'] == 'claude-3-sonnet-20240229'
    mock_update_usage.assert_called_once_with('balanced', ANY, ANY, True)

@pytest.mark.asyncio
async def test_llm_manager_query_with_rate_limit(mock_claude_manager, llm_manager):
    mock_claude_manager.generate_response.side_effect = [
        RateLimitError("Rate limit exceeded"),
        RateLimitError("Rate limit exceeded"),
        "<response>Test response</response>"
    ]
    with patch.object(llm_manager.cost_optimizer, 'select_optimal_tier', return_value='balanced'):
        response = await llm_manager.query("Test prompt")

    assert isinstance(response, dict)
    assert "Test response" in response.get("response", "")
    assert mock_claude_manager.generate_response.call_count == 3

@pytest.mark.asyncio
async def test_llm_manager_query_with_error(mock_claude_manager, llm_manager):
    mock_claude_manager.generate_response.side_effect = Exception("Test error")
    with patch.object(llm_manager.cost_optimizer, 'select_optimal_tier', return_value='balanced'):
        with patch.object(llm_manager.cost_optimizer, 'update_usage') as mock_update_usage:
            response = await llm_manager.query("Test prompt")
    assert 'error' in response
    assert "Error querying LLM:" in response["error"]
    assert mock_update_usage.call_count == 3  # One for each tier: powerful, balanced, fast
    mock_update_usage.assert_any_call('fast', ANY, ANY, False)

@pytest.mark.asyncio
@pytest.mark.parametrize("query,expected_tier", [
    ("What is 2 + 2?", 'fast'),
    ("Analyze the implications of quantum computing on modern cryptography systems.", 'powerful'),
])
async def test_llm_manager_tier_selection(llm_manager, query, expected_tier):
    with patch.object(llm_manager, '_process_response', return_value={}):
        with patch.object(llm_manager.cost_optimizer, 'select_optimal_tier', return_value=expected_tier):
            with patch.object(llm_manager.claude_manager, 'generate_response', return_value="<response>Test response</response>"):
                with patch.object(llm_manager.cost_optimizer, 'update_usage'):
                    await llm_manager.query(query)
                    llm_manager.claude_manager.generate_response.assert_called_once()
    
    assert await llm_manager.determine_query_tier(query) == expected_tier

@pytest.mark.asyncio
@pytest.mark.parametrize("tier,expected_response", [
    ('fast', "Fast response"),
    ('balanced', "Balanced response"),
    ('powerful', "Powerful response"),
])
async def test_llm_manager_query_with_tiers(llm_manager, tier, expected_response):
    with patch.object(llm_manager.claude_manager, 'generate_response', return_value=f"<response>{expected_response}</response>"):
        result = await llm_manager.query(f"{tier} prompt", tier=tier)
        
    assert isinstance(result, dict)
    assert expected_response in result.get("response", "")

@pytest.mark.asyncio
async def test_llm_manager_get_usage_report(llm_manager):
    await llm_manager.cost_optimizer.update_usage('fast', 100, 0.5, True)
    await llm_manager.cost_optimizer.update_usage('balanced', 200, 1.0, True)
    await llm_manager.cost_optimizer.update_usage('powerful', 300, 1.5, True)
    report = await llm_manager.get_usage_report()
    assert all(key in report for key in ['usage_stats', 'total_cost'])
    assert all(report['usage_stats'][tier]['count'] == 1 for tier in ['fast', 'balanced', 'powerful'])

@pytest.mark.asyncio
async def test_llm_manager_get_optimization_suggestion(llm_manager):
    await llm_manager.cost_optimizer.update_usage('fast', 100, 0.5, True)
    await llm_manager.cost_optimizer.update_usage('balanced', 200, 1.0, True)
    await llm_manager.cost_optimizer.update_usage('powerful', 300, 1.5, True)
    suggestion = await llm_manager.get_optimization_suggestion()
    assert isinstance(suggestion, str)
    assert len(suggestion) > 0

@pytest.mark.asyncio
@pytest.mark.parametrize("query,expected_tier", [
    ("Short query", 'fast'),
    ("Medium length query with some details about the project", 'balanced'),
    ("Complex query that requires detailed analysis of the project structure and implementation of new features", 'powerful'),
])
async def test_determine_query_tier(llm_manager, query, expected_tier):
    assert await llm_manager.determine_query_tier(query) == expected_tier

@pytest.mark.asyncio
async def test_evaluate_sufficiency(llm_manager):
    with patch.object(llm_manager, 'query') as mock_query:
        mock_query.return_value = {
            "response": "<evaluation>SUFFICIENT</evaluation><reasoning>All tasks completed</reasoning>"
        }
        
        result = await llm_manager.evaluate_sufficiency("Test Stage", {"description": "Test"}, {"key": "value"})
        
        assert result["is_sufficient"] == True
        assert result["reasoning"] == "All tasks completed"
        mock_query.assert_called_once()

@pytest.mark.asyncio
async def test_evaluate_sufficiency_error(llm_manager):
    with patch.object(llm_manager, 'query') as mock_query:
        mock_query.side_effect = Exception("Test error")
        
        result = await llm_manager.evaluate_sufficiency("Test Stage", {"description": "Test"}, {"key": "value"})
        
        assert result["is_sufficient"] == False
        assert "Error evaluating sufficiency: Test error" in result["reasoning"]

@pytest.mark.asyncio
async def test_llm_manager_query_with_context(llm_manager):
    with patch.object(llm_manager.claude_manager, 'generate_response', return_value="Test response"), \
         patch('time.time', side_effect=[0, 1]):  # Mock start and end times
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
        with patch.object(llm_manager.cost_optimizer, 'update_usage'):
            result = await llm_manager.query("Test prompt", context)
        assert isinstance(result, dict)
        assert "Test response" in result["response"]
        assert result["id"].startswith("(ID:")
        llm_manager.claude_manager.generate_response.assert_called_once()
        call_args = llm_manager.claude_manager.generate_response.call_args[0][0]
        assert all(text in call_args for text in [
            "Current Workflow Stage: Test Stage",
            "Stage Description: Test stage description",
            "Task 1", "Task 2",
            "Project Structure:",
            "Coding Conventions:",
            "Stages:", "Transitions:"
        ])
        assert "key1" in call_args and "value1" in call_args
        assert "key2" in call_args and "value2" in call_args

@pytest.mark.asyncio
async def test_llm_manager_error_handling(llm_manager):
    with patch('anthropic.Anthropic') as mock_anthropic:
        mock_anthropic.return_value.messages.create.side_effect = [
            Exception("Powerful error"),
            Exception("Balanced error"),
            Exception("Fast error")
        ]
        result = await llm_manager.query("Test prompt", tier='powerful')
        assert isinstance(result, dict)
        assert "error" in result
        assert "Error querying LLM:" in result["error"]
        assert mock_anthropic.return_value.messages.create.call_count == 3

@pytest.mark.asyncio
async def test_llm_manager_fallback_to_fast(llm_manager):
    with patch('anthropic.Anthropic') as mock_anthropic:
        mock_anthropic.return_value.messages.create.side_effect = [
            AttributeError("'Anthropic' object has no attribute 'messages'"),
            AttributeError("'Anthropic' object has no attribute 'messages'"),
            AttributeError("'Anthropic' object has no attribute 'messages'")
        ]
        result = await llm_manager.query("Test prompt", tier='powerful')
        assert isinstance(result, dict)
        assert "error" in result
        assert "Error querying LLM:" in result["error"]
        assert mock_anthropic.return_value.messages.create.call_count == 3

@pytest.mark.asyncio
@pytest.mark.parametrize("tier,expected_response", [
    ('fast', "Fast response"),
    ('balanced', "Balanced response"),
    ('powerful', "Powerful response"),
])
async def test_llm_manager_query_with_tiers_and_models(llm_manager, tier, expected_response):
    with patch('anthropic.Anthropic') as mock_anthropic, \
         patch('time.time', side_effect=[0, 1, 2, 3, 4, 5, 6, 7]):  # Mock start and end times
        mock_anthropic.return_value.messages.create.return_value = type('obj', (object,), {'content': [type('obj', (object,), {'text': expected_response})()] })()
    
        with patch.object(llm_manager.cost_optimizer, 'update_usage'):
            result = await llm_manager.query(f"{tier} prompt", tier=tier)
    
        assert isinstance(result, dict)
        assert expected_response in str(result.get("response", ""))
        
        mock_anthropic.return_value.messages.create.assert_called_once_with(
            model=ANY,
            max_tokens=ANY,
            messages=[{"role": "user", "content": ANY}]
        )

@pytest.mark.asyncio
async def test_llm_manager_caching(llm_manager):
    with patch('anthropic.Anthropic') as mock_anthropic, \
         patch('time.time', side_effect=[0, 1, 2, 3, 4, 5, 6, 7]):  # Mock start and end times
        mock_anthropic.return_value.messages.create.side_effect = [
            type('obj', (object,), {'content': [type('obj', (object,), {'text': "Response 1"})()]}),
            type('obj', (object,), {'content': [type('obj', (object,), {'text': "Response 2"})()]}),
            type('obj', (object,), {'content': [type('obj', (object,), {'text': "Response 3"})()]})
        ]
        prompt = "Test prompt"
        context = {"key": "value"}
        
        with patch.object(llm_manager.cost_optimizer, 'update_usage'):
            result1 = await llm_manager.query(prompt, context)
            assert isinstance(result1, dict) and "Response 1" in result1.get("response", "")
            
            result2 = await llm_manager.query(prompt, context)
            assert result2 == result1  # Should return cached result
            
            result3 = await llm_manager.query("Different prompt", context)
            assert isinstance(result3, dict) and "Response 2" in result3.get("response", "")
            assert result3 != result1
            
            await llm_manager.clear_cache()
            result4 = await llm_manager.query(prompt, context)
            assert "Response 3" in result4.get("response", "")
            assert result4 != result1
        
        assert mock_anthropic.return_value.messages.create.call_count == 3
import pytest
from unittest.mock import MagicMock, patch
from src.llm_manager import LLMManager
from src.claude_manager import ClaudeManager

@pytest.fixture
def mock_claude_manager():
    return MagicMock(spec=ClaudeManager)

@pytest.fixture
def llm_manager(mock_claude_manager):
    return LLMManager(claude_manager=mock_claude_manager)

@pytest.mark.asyncio
async def test_query(llm_manager, mock_claude_manager):
    mock_claude_manager.generate_response.return_value = "Test response"
    mock_claude_manager.count_tokens.return_value = 10
    
    response = await llm_manager.query("Test query")
    
    assert response['response'] == "Test response"
    assert 'token_usage' in response
    assert response['token_usage']['total'] == 20  # input + output tokens

@pytest.mark.asyncio
async def test_evaluate_sufficiency(llm_manager, mock_claude_manager):
    mock_claude_manager.generate_response.return_value = "<evaluation>SUFFICIENT</evaluation><reasoning>Test reasoning</reasoning>"
    
    result = await llm_manager.evaluate_sufficiency("test_stage", {}, {})
    
    assert result['is_sufficient'] == True
    assert result['reasoning'] == "Test reasoning"

@pytest.mark.asyncio
async def test_get_optimization_suggestion(llm_manager):
    with patch.object(llm_manager.cost_optimizer, 'suggest_optimization', return_value="Test suggestion"):
        suggestion = await llm_manager.get_optimization_suggestion()
        assert suggestion == "Test suggestion"

@pytest.mark.asyncio
async def test_get_usage_report(llm_manager):
    with patch.object(llm_manager.cost_optimizer, 'get_usage_report', return_value={"test": "report"}):
        report = await llm_manager.get_usage_report()
        assert report == {"test": "report"}

@pytest.mark.asyncio
async def test_calculate_cost(llm_manager):
    cost = await llm_manager.calculate_cost("test_model", 1000)
    assert cost == 0.1  # Assuming the default cost of 0.0001 per token

@pytest.mark.asyncio
async def test_clear_cache(llm_manager):
    llm_manager.cache = {"test": "data"}
    await llm_manager.clear_cache()
    assert llm_manager.cache == {}

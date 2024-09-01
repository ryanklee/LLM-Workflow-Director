from unittest.mock import MagicMock, patch
from src.sufficiency_evaluator import SufficiencyEvaluator

def test_sufficiency_evaluator_initialization():
    mock_llm_manager = MagicMock()
    evaluator = SufficiencyEvaluator(mock_llm_manager)
    assert evaluator.llm_manager == mock_llm_manager

def test_evaluate_stage_sufficiency_sufficient():
    mock_llm_manager = MagicMock()
    mock_llm_manager.query.return_value = "Evaluation: SUFFICIENT\nReasoning: All tasks completed satisfactorily.\nNext Steps: N/A"
    
    evaluator = SufficiencyEvaluator(mock_llm_manager)
    
    stage_name = "Test Stage"
    stage_data = {
        "description": "Test stage description",
        "tasks": ["Task 1", "Task 2"]
    }
    project_state = {"key": "value"}
    
    is_sufficient, reasoning = evaluator.evaluate_stage_sufficiency(stage_name, stage_data, project_state)
    
    assert is_sufficient == True
    assert "All tasks completed satisfactorily" in reasoning
    mock_llm_manager.query.assert_called_once()

def test_evaluate_stage_sufficiency_insufficient():
    mock_llm_manager = MagicMock()
    mock_llm_manager.query.return_value = "Evaluation: INSUFFICIENT\nReasoning: Some tasks are incomplete.\nNext Steps: Complete remaining tasks"
    
    evaluator = SufficiencyEvaluator(mock_llm_manager)
    
    stage_name = "Test Stage"
    stage_data = {
        "description": "Test stage description",
        "tasks": ["Task 1", "Task 2"]
    }
    project_state = {"key": "value"}
    
    is_sufficient, reasoning = evaluator.evaluate_stage_sufficiency(stage_name, stage_data, project_state)
    
    assert is_sufficient == False
    assert "Some tasks are incomplete" in reasoning
    assert "Complete remaining tasks" in reasoning
    mock_llm_manager.query.assert_called_once()

def test_generate_evaluation_prompt():
    mock_llm_manager = MagicMock()
    evaluator = SufficiencyEvaluator(mock_llm_manager)
    
    stage_name = "Test Stage"
    stage_data = {
        "description": "Test stage description",
        "tasks": ["Task 1", "Task 2"]
    }
    project_state = {"key": "value"}
    
    prompt = evaluator._generate_evaluation_prompt(stage_name, stage_data, project_state)
    
    assert "Test Stage" in prompt
    assert "Test stage description" in prompt
    assert "Task 1" in prompt
    assert "Task 2" in prompt
    assert "key: value" in prompt
    assert "Next Steps:" in prompt

def test_parse_sufficiency_response_valid():
    mock_llm_manager = MagicMock()
    evaluator = SufficiencyEvaluator(mock_llm_manager)
    
    response = "Evaluation: SUFFICIENT\nReasoning: All tasks completed satisfactorily.\nNext Steps: N/A"
    is_sufficient, reasoning = evaluator._parse_sufficiency_response(response)
    
    assert is_sufficient == True
    assert "All tasks completed satisfactorily" in reasoning
    assert "Next Steps: N/A" in reasoning

def test_parse_sufficiency_response_invalid():
    mock_llm_manager = MagicMock()
    evaluator = SufficiencyEvaluator(mock_llm_manager)
    
    response = "Invalid response format"
    is_sufficient, reasoning = evaluator._parse_sufficiency_response(response)
    
    assert is_sufficient == False
    assert "Error parsing response" in reasoning

from unittest.mock import MagicMock, patch
from src.sufficiency_evaluator import SufficiencyEvaluator

def test_sufficiency_evaluator_initialization():
    mock_llm_manager = MagicMock()
    evaluator = SufficiencyEvaluator(mock_llm_manager)
    assert evaluator.llm_manager == mock_llm_manager

def test_evaluate_stage_sufficiency_sufficient():
    mock_llm_manager = MagicMock()
    mock_llm_manager.query.return_value = "Evaluation: SUFFICIENT\nReasoning: All tasks completed satisfactorily."
    
    evaluator = SufficiencyEvaluator(mock_llm_manager)
    
    stage_name = "Test Stage"
    stage_data = {
        "description": "Test stage description",
        "tasks": ["Task 1", "Task 2"]
    }
    project_state = {"key": "value"}
    
    result = evaluator.evaluate_stage_sufficiency(stage_name, stage_data, project_state)
    
    assert result == True
    mock_llm_manager.query.assert_called_once()

def test_evaluate_stage_sufficiency_insufficient():
    mock_llm_manager = MagicMock()
    mock_llm_manager.query.return_value = "Evaluation: INSUFFICIENT\nReasoning: Some tasks are incomplete."
    
    evaluator = SufficiencyEvaluator(mock_llm_manager)
    
    stage_name = "Test Stage"
    stage_data = {
        "description": "Test stage description",
        "tasks": ["Task 1", "Task 2"]
    }
    project_state = {"key": "value"}
    
    result = evaluator.evaluate_stage_sufficiency(stage_name, stage_data, project_state)
    
    assert result == False
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

def test_parse_sufficiency_response_valid():
    mock_llm_manager = MagicMock()
    evaluator = SufficiencyEvaluator(mock_llm_manager)
    
    response = "Evaluation: SUFFICIENT\nReasoning: All tasks completed satisfactorily."
    result = evaluator._parse_sufficiency_response(response)
    
    assert result == True

def test_parse_sufficiency_response_invalid():
    mock_llm_manager = MagicMock()
    evaluator = SufficiencyEvaluator(mock_llm_manager)
    
    response = "Invalid response format"
    result = evaluator._parse_sufficiency_response(response)
    
    assert result == False

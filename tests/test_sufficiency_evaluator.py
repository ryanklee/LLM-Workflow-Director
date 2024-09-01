from unittest.mock import MagicMock, patch
from src.sufficiency_evaluator import SufficiencyEvaluator

def test_sufficiency_evaluator_initialization():
    mock_llm_manager = MagicMock()
    evaluator = SufficiencyEvaluator(mock_llm_manager)
    assert evaluator.llm_manager == mock_llm_manager

def test_evaluate_stage_sufficiency_sufficient():
    mock_llm_manager = MagicMock()
    mock_llm_manager.evaluate_sufficiency.return_value = {
        "is_sufficient": True,
        "reasoning": "All tasks completed satisfactorily."
    }
    
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
    mock_llm_manager.evaluate_sufficiency.assert_called_once_with(stage_name, stage_data, project_state)

def test_evaluate_stage_sufficiency_insufficient():
    mock_llm_manager = MagicMock()
    mock_llm_manager.evaluate_sufficiency.return_value = {
        "is_sufficient": False,
        "reasoning": "Some tasks are incomplete. Complete remaining tasks."
    }
    
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
    mock_llm_manager.evaluate_sufficiency.assert_called_once_with(stage_name, stage_data, project_state)

def test_evaluate_stage_sufficiency_error():
    mock_llm_manager = MagicMock()
    mock_llm_manager.evaluate_sufficiency.side_effect = Exception("Test error")
    
    evaluator = SufficiencyEvaluator(mock_llm_manager)
    
    stage_name = "Test Stage"
    stage_data = {
        "description": "Test stage description",
        "tasks": ["Task 1", "Task 2"]
    }
    project_state = {"key": "value"}
    
    is_sufficient, reasoning = evaluator.evaluate_stage_sufficiency(stage_name, stage_data, project_state)
    
    assert is_sufficient == False
    assert "Error evaluating sufficiency" in reasoning
    assert "Test error" in reasoning
    mock_llm_manager.evaluate_sufficiency.assert_called_once_with(stage_name, stage_data, project_state)

def test_evaluate_stage_sufficiency_no_llm_manager():
    evaluator = SufficiencyEvaluator(None)
    
    stage_name = "Test Stage"
    stage_data = {
        "description": "Test stage description",
        "tasks": ["Task 1", "Task 2"]
    }
    project_state = {"key": "value"}
    
    is_sufficient, reasoning = evaluator.evaluate_stage_sufficiency(stage_name, stage_data, project_state)
    
    assert is_sufficient == True
    assert "LLMManager not available" in reasoning


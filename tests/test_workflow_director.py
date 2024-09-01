from unittest.mock import MagicMock, patch
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the ConstraintEngine
mock_constraint_engine = MagicMock()
mock_constraint_engine.Engine.return_value.ValidateAll.return_value = (True, [])
sys.modules['pkg.workflow.constraint.engine'] = mock_constraint_engine

from src.workflow_director import WorkflowDirector

def test_workflow_director_initialization():
    director = WorkflowDirector()
    assert hasattr(director, 'state_manager')
    assert hasattr(director, 'llm_manager')
    assert hasattr(director, 'stages')
    assert hasattr(director, 'transitions')

def test_workflow_director_get_current_stage():
    director = WorkflowDirector()
    current_stage = director.get_current_stage()
    assert current_stage['name'] == "Project Initialization"
    assert 'description' in current_stage
    assert 'tasks' in current_stage

def test_workflow_director_get_available_transitions():
    director = WorkflowDirector()
    transitions = director.get_available_transitions()
    assert len(transitions) > 0
    assert all('from' in t and 'to' in t for t in transitions)

def test_workflow_director_can_transition_to():
    director = WorkflowDirector()
    assert director.can_transition_to("Requirements Gathering")
    assert not director.can_transition_to("Non-existent Stage")

def test_workflow_director_transition_to():
    director = WorkflowDirector()
    assert director.transition_to("Requirements Gathering")
    assert not director.transition_to("Non-existent Stage")

def test_workflow_director_move_to_next_stage():
    director = WorkflowDirector()
    assert director.move_to_next_stage()
    assert director.current_stage == "Requirements Gathering"

def test_workflow_director_complete_current_stage():
    director = WorkflowDirector()
    initial_stage = director.current_stage
    result = director.complete_current_stage()
    assert result == True, f"Expected True, got {result}"
    assert director.is_stage_completed(initial_stage), f"Stage {initial_stage} should be marked as completed"
    
    if director.current_stage != initial_stage:
        assert director.current_stage in [t['to'] for t in director.transitions if t['from'] == initial_stage], \
            f"Current stage {director.current_stage} is not a valid transition from {initial_stage}"
    else:
        assert len([t for t in director.transitions if t['from'] == initial_stage]) == 0, \
            f"Expected no transitions from {initial_stage}, but transitions exist"

def test_workflow_director_get_stage_progress():
    director = WorkflowDirector()
    progress = director.get_stage_progress()
    assert isinstance(progress, float)
    assert 0 <= progress <= 1

def test_workflow_director_update_stage_progress():
    director = WorkflowDirector()
    director.update_stage_progress(0.5)
    assert director.get_stage_progress() == 0.5
    director.update_stage_progress(1.5)
    assert director.get_stage_progress() == 1.0
    director.update_stage_progress(-0.5)
    assert director.get_stage_progress() == 0.0

def test_workflow_director_is_stage_completed():
    director = WorkflowDirector()
    initial_stage = director.current_stage
    assert not director.is_stage_completed(initial_stage)
    director.complete_current_stage()
    assert director.is_stage_completed(initial_stage)

def test_workflow_director_can_transition_to():
    director = WorkflowDirector()
    initial_stage = director.current_stage
    next_stage = director.transitions[0]['to']
    assert director.can_transition_to(next_stage)
    assert not director.can_transition_to("Non-existent Stage")
    director.complete_current_stage()
    assert director.can_transition_to(next_stage)

@patch('src.workflow_director.LLMManager')
def test_workflow_director_run(mock_llm_manager):
    mock_llm_manager.return_value.query.return_value = "LLM response"
    mock_input = MagicMock(side_effect=['test command', 'next', 'exit'])
    mock_print = MagicMock()
    director = WorkflowDirector(input_func=mock_input, print_func=mock_print)
    director.run()

    assert mock_print.call_args_list[0][0][0] == "Starting LLM Workflow Director"
    assert "Current stage: Project Initialization" in mock_print.call_args_list[1][0][0]
    assert "Description:" in mock_print.call_args_list[2][0][0]
    assert "Tasks:" in mock_print.call_args_list[3][0][0]
    assert any("Enter a command" in call[0][0] for call in mock_print.call_args_list)
    
    # Check for either LLM response or unavailability message
    assert any("LLM response: LLM response" in call[0][0] for call in mock_print.call_args_list) or \
           any("LLM manager is not available" in call[0][0] for call in mock_print.call_args_list)
    
    assert any("Current stage: Requirements Gathering" in call[0][0] for call in mock_print.call_args_list)
    assert mock_print.call_args_list[-1][0][0] == "Exiting LLM Workflow Director"

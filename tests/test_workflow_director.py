from unittest.mock import MagicMock, patch, ANY
import sys
import os
import pytest
import subprocess

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the ConstraintEngine
mock_constraint_engine = MagicMock()
mock_constraint_engine.Engine.return_value.ValidateAll.return_value = (True, [])
sys.modules['pkg.workflow.constraint.engine'] = mock_constraint_engine

from src.workflow_director import WorkflowDirector
from src.user_interaction_handler import UserInteractionHandler

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
    print(f"Initial stage: {initial_stage}")
    print(f"All stages: {[stage['name'] for stage in director.config['stages']]}")
    print(f"Initial completed stages: {director.completed_stages}")

    result = director.complete_current_stage()
    print(f"Result of completing initial stage: {result}")
    print(f"Current stage after completion: {director.current_stage}")
    print(f"Completed stages after initial completion: {director.completed_stages}")

    assert result == True, f"Expected True, got {result}"
    assert director.is_stage_completed(initial_stage), f"Stage {initial_stage} should be marked as completed"
    assert director.current_stage != initial_stage, f"Expected to move to a new stage, but still in {initial_stage}"

    # Check if the new current stage is a valid transition from the initial stage
    valid_transitions = [t['to'] for t in director.transitions if t['from'] == initial_stage]
    print(f"Valid transitions from {initial_stage}: {valid_transitions}")
    assert director.current_stage in valid_transitions, \
        f"Current stage {director.current_stage} is not a valid transition from {initial_stage}"

    # Test completing all stages
    all_stages = [stage['name'] for stage in director.config['stages']]
    for i, stage in enumerate(all_stages[1:-1], start=1):  # Start from the second stage, end before the last
        print(f"Completing stage {i}: {stage}")
        result = director.complete_current_stage()
        print(f"Result of completing stage {stage}: {result}")
        print(f"Current stage after completion: {director.current_stage}")
        print(f"Completed stages: {director.completed_stages}")
        assert result == True, f"Expected True for stage {stage}, got {result}"

    # Check if we're in the final stage
    print(f"Final check - Current stage: {director.current_stage}, Expected final stage: {all_stages[-1]}")
    assert director.current_stage == all_stages[-1], f"Expected to be in the final stage {all_stages[-1]}, but in {director.current_stage}"
    
    # Test attempting to complete after the final stage
    post_final_result = director.complete_current_stage()
    print(f"Result of completing after final stage: {post_final_result}")
    print(f"Final current stage: {director.current_stage}")
    print(f"Final completed stages: {director.completed_stages}")
    assert post_final_result == True, "Expected True when attempting to complete after the final stage"
    assert director.current_stage == all_stages[-1], f"Expected to stay in the final stage {all_stages[-1]}, but in {director.current_stage}"

def test_main_script_execution():
    result = subprocess.run(['python', 'src/main.py', 'report', '--format', 'markdown'], 
                            capture_output=True, text=True)
    assert result.returncode == 0, "Script should exit with status code 0"
    assert "Error importing llm module. LLMManager will operate in mock mode." in result.stderr
    assert "# LLM-Workflow Director Project Report" in result.stdout

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
    print(f"Initial stage: {initial_stage}")
    print(f"Next stage: {next_stage}")
    
    assert director.can_transition_to(next_stage), f"Should be able to transition from {initial_stage} to {next_stage}"
    assert not director.can_transition_to("Non-existent Stage"), "Should not be able to transition to a non-existent stage"
    
    print(f"Completing stage: {initial_stage}")
    director.complete_current_stage()
    print(f"Current stage after completion: {director.current_stage}")
    print(f"Completed stages: {director.completed_stages}")
    
    assert director.can_transition_to(next_stage), f"Should be able to transition to {next_stage} after completing {initial_stage}"
    
    print(f"Transitioning to: {next_stage}")
    director.transition_to(next_stage)
    print(f"Current stage after transition: {director.current_stage}")
    
    # Check if we can transition to the current stage
    assert director.can_transition_to(director.current_stage), f"Should be able to transition to the current stage {director.current_stage}"
    
    if len(director.transitions) > 1:
        next_next_stage = director.transitions[1]['to']
        print(f"Next next stage: {next_next_stage}")
        assert director.can_transition_to(next_next_stage), f"Should be able to transition from {next_stage} to {next_next_stage}"
    else:
        print("No more transitions available")

@patch('src.workflow_director.LLMManager')
def test_workflow_director_run(mock_llm_manager):
    mock_llm_manager.return_value.query.return_value = "LLM response"
    mock_user_interaction_handler = MagicMock(spec=UserInteractionHandler)
    mock_user_interaction_handler.prompt_user.side_effect = ['test command', 'next', 'exit']
        
    # Mock the ConventionManager
    with patch('src.workflow_director.ConventionManager') as mock_convention_manager:
        mock_convention_manager.return_value.get_aider_conventions.return_value = "Mocked conventions"
            
        director = WorkflowDirector(user_interaction_handler=mock_user_interaction_handler)
        director.run()

    assert mock_user_interaction_handler.display_message.call_args_list[0][0][0] == "Starting LLM Workflow Director"
    assert any("Current stage: Project Initialization" in call[0][0] for call in mock_user_interaction_handler.display_message.call_args_list)
    assert any("Description:" in call[0][0] for call in mock_user_interaction_handler.display_message.call_args_list)
    assert any("Tasks:" in call[0][0] for call in mock_user_interaction_handler.display_message.call_args_list)
    assert any("Enter a command" in call[0][0] for call in mock_user_interaction_handler.prompt_user.call_args_list)
        
    # Check for LLM response
    assert any("LLM response: LLM response" in call[0][0] for call in mock_user_interaction_handler.display_message.call_args_list)
        
    assert any("Current stage: Requirements Gathering" in call[0][0] for call in mock_user_interaction_handler.display_message.call_args_list)
    assert mock_user_interaction_handler.display_message.call_args_list[-1][0][0] == "Exiting LLM Workflow Director"

@patch('src.workflow_director.LLMManager')
def test_workflow_director_llm_integration(mock_llm_manager):
    mock_llm_manager.return_value.query.return_value = "LLM response: Update task progress"
    mock_user_interaction_handler = MagicMock(spec=UserInteractionHandler)
    mock_user_interaction_handler.prompt_user.side_effect = ['test command', 'exit']

    director = WorkflowDirector(user_interaction_handler=mock_user_interaction_handler)
    director.llm_manager = mock_llm_manager.return_value  # Explicitly set the mocked LLMManager
    
    # Add debug print statements before running
    print("Before run() - LLM Manager:", director.llm_manager)
    print("Before run() - User Interaction Handler:", director.user_interaction_handler)
    
    director.run()

    # Debug print statements after running
    print("After run() - Mock LLM Manager query call count:", mock_llm_manager.return_value.query.call_count)
    print("After run() - Mock LLM Manager query call args:", mock_llm_manager.return_value.query.call_args_list)
    print("After run() - User Interaction Handler prompt_user call count:", mock_user_interaction_handler.prompt_user.call_count)
    print("After run() - User Interaction Handler prompt_user call args:", mock_user_interaction_handler.prompt_user.call_args_list)

    # Check if the query method was called
    assert mock_llm_manager.return_value.query.called, "LLMManager.query was not called"

    # If it was called, check the arguments
    if mock_llm_manager.return_value.query.called:
        mock_llm_manager.return_value.query.assert_called_with("Process this command: test command", context=ANY, tier=ANY)

    mock_user_interaction_handler.display_message.assert_any_call("LLM response: LLM response: Update task progress")
    assert any("LLM response: Update task progress" in call[0][0] for call in mock_user_interaction_handler.display_message.call_args_list)

    # Add more specific assertions to check the LLM integration
    context = director._prepare_llm_context()
    # Add more assertions to check if the LLM response is properly integrated with the workflow

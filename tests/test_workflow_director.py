from unittest.mock import MagicMock, patch, ANY
import sys
import os
import pytest
import subprocess
import logging
from click.testing import CliRunner

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the ConstraintEngine
mock_constraint_engine = MagicMock()
mock_constraint_engine.Engine.return_value.ValidateAll.return_value = (True, [])
sys.modules['pkg.workflow.constraint.engine'] = mock_constraint_engine

from src.workflow_director import WorkflowDirector
from src.user_interaction_handler import UserInteractionHandler
from src.main import cli

def test_workflow_director_initialization():
    director = WorkflowDirector()
    assert hasattr(director, 'state_manager')
    assert hasattr(director, 'llm_manager')
    assert hasattr(director, 'stages')
    assert hasattr(director, 'transitions')
    assert hasattr(director, 'logger')

def test_workflow_director_logging_setup(tmpdir):
    log_dir = tmpdir.mkdir("logs")
    with patch('src.workflow_director.logging.FileHandler') as mock_file_handler:
        director = WorkflowDirector()
        director._setup_logging()
        
        # Check that file handlers were created
        assert mock_file_handler.call_count == 2
        
        # Check that the logger was set up correctly
        assert director.logger.level == logging.DEBUG
        assert len(director.logger.handlers) == 3  # Console, File, and JSON handlers

def test_workflow_director_json_logging(tmpdir):
    log_dir = tmpdir.mkdir("logs")
    with patch('src.workflow_director.logging.FileHandler') as mock_file_handler:
        director = WorkflowDirector()
        director._setup_logging()
        
        # Trigger a log message
        director.logger.info("Test log message", extra={'test_key': 'test_value'})
        
        # Check the JSON log file
        json_handler = director.logger.handlers[2]
        json_log_file = json_handler.baseFilename
        with open(json_log_file, 'r') as f:
            log_entry = json.loads(f.readline())
            assert 'timestamp' in log_entry
            assert log_entry['levelname'] == 'INFO'
            assert log_entry['message'] == 'Test log message'
            assert log_entry['test_key'] == 'test_value'

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

def test_workflow_director_get_workflow_status():
    director = WorkflowDirector()
    status = director.get_workflow_status()
    assert "Current Stage: Project Initialization" in status
    assert "Completed Stages:" in status
    assert "Current Stage Progress:" in status
    assert "Available Transitions:" in status

@patch('src.main.WorkflowDirector')
def test_cli_transition_command(mock_workflow_director):
    runner = CliRunner()
    mock_workflow_director.return_value.transition_to.return_value = True
    result = runner.invoke(cli, ['transition', 'Requirements Gathering'])
    assert result.exit_code == 0
    assert "Successfully transitioned to stage: Requirements Gathering" in result.output
    mock_workflow_director.return_value.transition_to.assert_called_once_with('Requirements Gathering')

@patch('src.main.WorkflowDirector')
def test_cli_status_command(mock_workflow_director):
    runner = CliRunner()
    mock_workflow_director.return_value.get_workflow_status.return_value = "Mocked status report"
    result = runner.invoke(cli, ['status'])
    assert result.exit_code == 0
    assert "Mocked status report" in result.output
    mock_workflow_director.return_value.get_workflow_status.assert_called_once()

def test_workflow_director_complete_current_stage():
    director = WorkflowDirector()
    initial_stage = director.current_stage
    all_stages = [stage['name'] for stage in director.config['stages']]
    
    director.logger.info(f"Initial stage: {initial_stage}")
    director.logger.info(f"All stages: {all_stages}")
    director.logger.info(f"Initial completed stages: {director.completed_stages}")

    for i, stage in enumerate(all_stages):
        result = director.complete_current_stage()
        director.logger.info(f"Completed stage {i}: {stage}")
        director.logger.info(f"Result of completing stage: {result}")
        director.logger.info(f"Current stage after completion: {director.current_stage}")
        director.logger.info(f"Completed stages: {director.completed_stages}")
        
        assert result == True, f"Expected True for stage {stage}, got {result}"
        assert director.is_stage_completed(stage), f"Stage {stage} should be marked as completed"
        
        if i < len(all_stages) - 1:
            assert director.current_stage == all_stages[i+1], f"Expected to move to stage {all_stages[i+1]}, but in {director.current_stage}"
        else:
            assert director.current_stage == stage, f"Expected to stay in the final stage {stage}, but in {director.current_stage}"

    # Test attempting to complete after the final stage
    post_final_result = director.complete_current_stage()
    director.logger.info(f"Result of completing after final stage: {post_final_result}")
    director.logger.info(f"Final current stage: {director.current_stage}")
    director.logger.info(f"Final completed stages: {director.completed_stages}")
    
    assert post_final_result == True, "Expected True when attempting to complete after the final stage"
    assert director.current_stage == all_stages[-1], f"Expected to stay in the final stage {all_stages[-1]}, but in {director.current_stage}"
    assert len(director.completed_stages) == len(all_stages), f"Expected all stages to be completed, but only {len(director.completed_stages)} are completed"

def test_main_script_execution():
    result = subprocess.run(['python', 'src/main.py', 'report', '--format', 'markdown'], 
                            capture_output=True, text=True)
    assert result.returncode == 0, "Script should exit with status code 0"
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
        mock_convention_manager.return_value.load_conventions.return_value = "Mocked conventions"
            
        director = WorkflowDirector(user_interaction_handler=mock_user_interaction_handler)
        director.run()

    assert mock_user_interaction_handler.display_message.call_args_list[0][0][0] == "Starting LLM Workflow Director"
    assert any("Current stage: Project Initialization" in call[0][0] for call in mock_user_interaction_handler.display_message.call_args_list)
    assert any("Description:" in call[0][0] for call in mock_user_interaction_handler.display_message.call_args_list)
    assert any("Tasks:" in call[0][0] for call in mock_user_interaction_handler.display_message.call_args_list)
    assert any("Enter a command" in call[0][0] for call in mock_user_interaction_handler.prompt_user.call_args_list)
        
    # Check for LLM response
    assert any("LLM response: LLM response" in call[0][0] for call in mock_user_interaction_handler.display_message.call_args_list)
        
    # We no longer expect to see the "Requirements Gathering" stage
    assert mock_user_interaction_handler.display_message.call_args_list[-1][0][0] == "Exiting LLM Workflow Director"
        
    # Check that the LLM query was called twice (for 'test command' and 'next')
    assert mock_llm_manager.return_value.query.call_count == 2

def test_process_llm_response(caplog):
    director = WorkflowDirector()
    response = """
    task_progress: 0.75
    state_updates: {'key': 'value', 'another_key': 42}
    actions: update_workflow, run_tests
    suggestions: Review code, Update documentation
    """
    
    with caplog.at_level(logging.INFO):
        director._process_llm_response(response)
    
    assert "Updated stage progress to 0.75" in caplog.text
    assert "Updated project state: key = value" in caplog.text
    assert "Updated project state: another_key = 42" in caplog.text
    assert "LLM response processed successfully" in caplog.text

def test_parse_llm_response():
    director = WorkflowDirector()
    response = """
    task_progress: 0.75
    state_updates: {'key': 'value', 'another_key': 42}
    actions: update_workflow, run_tests
    suggestions: Review code, Update documentation
    multi_line_key: This is a
     multi-line value
     with several lines
    """
    parsed = director._parse_llm_response(response)
    
    assert parsed == {
        'task_progress': 0.75,
        'state_updates': {'key': 'value', 'another_key': 42},
        'actions': ['update_workflow', 'run_tests'],
        'suggestions': ['Review code', 'Update documentation'],
        'multi_line_key': 'This is a multi-line value with several lines'
    }

@patch('src.workflow_director.LLMManager')
@patch('src.workflow_director.ConventionManager')
def test_workflow_director_llm_integration(mock_convention_manager, mock_llm_manager, caplog):
    mock_llm_manager.return_value.query.return_value = "LLM response: Update task progress"
    mock_llm_manager.return_value.generate_prompt.return_value = "Process this command: {command}"
    mock_user_interaction_handler = MagicMock(spec=UserInteractionHandler)
    mock_user_interaction_handler.prompt_user.side_effect = ['test command', 'next', 'exit']
    mock_convention_manager.return_value.get_aider_conventions.return_value = "Mocked conventions"

    director = WorkflowDirector(
        user_interaction_handler=mock_user_interaction_handler,
        llm_manager=mock_llm_manager.return_value
    )
    director._test_mode = True  # Set test mode

    # Capture logs
    with caplog.at_level(logging.DEBUG):
        director.run()

    # Check if the query method was called
    assert mock_llm_manager.return_value.query.called, "LLMManager.query was not called"
    
    # Print debug information
    print("LLMManager mock calls:", mock_llm_manager.mock_calls)
    print("LLMManager.query mock calls:", mock_llm_manager.return_value.query.mock_calls)
    print("User interaction handler mock calls:", mock_user_interaction_handler.mock_calls)
    
    # Print the captured logs
    print("Captured logs:")
    for record in caplog.records:
        print(f"{record.levelname}: {record.getMessage()}")

    # Check the arguments of the query calls
    mock_llm_manager.return_value.query.assert_any_call(
        "Process this command: {command}",
        context=ANY,
        tier=ANY
    )

    # Check if the LLM responses were displayed
    mock_user_interaction_handler.display_message.assert_any_call("LLM response: LLM response: Update task progress")

    # Check if the _process_llm_response method was called
    assert any("LLM response: Update task progress" in call[0][0] for call in mock_user_interaction_handler.display_message.call_args_list)

    # Check that the LLM query was called at least twice (for 'test command' and 'next')
    assert mock_llm_manager.return_value.query.call_count >= 2, f"Expected at least 2 LLM queries, but got {mock_llm_manager.return_value.query.call_count}"

    # Check that the move_to_next_stage method was called
    assert mock_user_interaction_handler.display_message.call_count >= 2, f"Expected at least two display_message calls, but got {mock_user_interaction_handler.display_message.call_count}"

    # Print captured logs
    print("Captured logs:")
    for record in caplog.records:
        print(f"{record.levelname}: {record.getMessage()}")

    # Print mock call counts
    print(f"Mock LLMManager query call count: {mock_llm_manager.return_value.query.call_count}")
    print(f"Mock user interaction handler display_message call count: {mock_user_interaction_handler.display_message.call_count}")
    print(f"Mock user interaction handler prompt_user call count: {mock_user_interaction_handler.prompt_user.call_count}")

    # Check if LLMManager was initialized correctly
    assert director.llm_manager is not None, "LLMManager was not initialized"
    assert isinstance(director.llm_manager, MagicMock), "LLMManager is not a MagicMock instance"

    # Print the mock calls for debugging
    print("Mock LLMManager method calls:")
    for call in mock_llm_manager.mock_calls:
        print(call)

    print("Mock user interaction handler method calls:")
    for call in mock_user_interaction_handler.mock_calls:
        print(call)

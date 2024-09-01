from unittest.mock import MagicMock, patch
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

@patch('src.llm_manager.LLMManager')
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
    assert any("LLM response: LLM response" in call[0][0] for call in mock_print.call_args_list)
    assert any("Current stage: Requirements Gathering" in call[0][0] for call in mock_print.call_args_list)
    assert mock_print.call_args_list[-1][0][0] == "Exiting LLM Workflow Director"

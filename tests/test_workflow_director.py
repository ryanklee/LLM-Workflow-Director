from unittest.mock import MagicMock
from src.workflow_director import WorkflowDirector


def test_workflow_director_initialization():
    director = WorkflowDirector()
    assert hasattr(director, 'state_manager')
    assert hasattr(director, 'llm_manager')


def test_workflow_director_run():
    mock_input = MagicMock(side_effect=['test command', 'exit'])
    mock_print = MagicMock()
    director = WorkflowDirector(input_func=mock_input, print_func=mock_print)
    director.run()

    assert mock_print.call_args_list[0][0][0] == "Starting LLM Workflow Director"
    assert mock_print.call_args_list[1][0][0] == "Current stage: Project Initialization"
    assert mock_print.call_args_list[2][0][0] == "Enter a command (or 'exit' to quit): "
    assert ("LLM response:" in mock_print.call_args_list[3][0][0] or
            "Mock response to:" in mock_print.call_args_list[3][0][0])
    assert mock_print.call_args_list[4][0][0] == "Current stage: Project Initialization"
    assert mock_print.call_args_list[5][0][0] == "Enter a command (or 'exit' to quit): "
    assert mock_print.call_args_list[6][0][0] == "Exiting LLM Workflow Director"

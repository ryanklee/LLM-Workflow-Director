import pytest
from unittest.mock import MagicMock
from src.workflow_director import WorkflowDirector

def test_workflow_director_initialization():
    director = WorkflowDirector()
    assert hasattr(director, 'state_manager')
    assert hasattr(director, 'llm_manager')

def test_workflow_director_run(capsys):
    mock_input = MagicMock(side_effect=['test command', 'exit'])
    director = WorkflowDirector(input_func=mock_input)
    director.run()
    captured = capsys.readouterr()
    assert "Starting LLM Workflow Director" in captured.out
    assert "Enter a command (or 'exit' to quit):" in captured.out
    assert "LLM response:" in captured.out
    assert "Exiting LLM Workflow Director" in captured.out

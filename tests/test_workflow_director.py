import pytest
from src.workflow_director import WorkflowDirector

def test_workflow_director_initialization():
    director = WorkflowDirector()
    assert hasattr(director, 'state_manager')
    assert hasattr(director, 'llm_manager')

def test_workflow_director_run(capsys):
    director = WorkflowDirector()
    director.run()
    captured = capsys.readouterr()
    assert "Starting LLM Workflow Director" in captured.out
    assert "Exiting LLM Workflow Director" in captured.out

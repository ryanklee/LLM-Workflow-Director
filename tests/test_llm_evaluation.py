import pytest
from src.claude_manager import ClaudeManager
from src.mock_claude_client import MockClaudeClient

@pytest.fixture
def claude_manager():
    mock_client = MockClaudeClient()
    return ClaudeManager(client=mock_client)

def test_sufficiency_evaluation(claude_manager):
    mock_client = claude_manager.client
    mock_client.set_response("Evaluate sufficiency: Test project", "The project is sufficient.")
    
    result = claude_manager.evaluate_sufficiency("Test project")
    assert result == "The project is sufficient."

@pytest.mark.parametrize("project_state,expected_decision", [
    ("Requirements gathered", "Proceed to design phase"),
    ("Design completed", "Start implementation"),
    ("Implementation in progress", "Continue implementation"),
    ("Testing completed", "Prepare for deployment"),
])
def test_decision_making(claude_manager, project_state, expected_decision):
    mock_client = claude_manager.client
    mock_client.set_response(f"Make decision based on: {project_state}", expected_decision)

    decision = claude_manager.make_decision(project_state)
    assert expected_decision in decision

def test_complex_evaluation(claude_manager):
    project_data = {
        "requirements": ["Req1", "Req2", "Req3"],
        "design": "Completed",
        "implementation": "75% complete",
        "testing": "Not started"
    }
    mock_client = claude_manager.client
    mock_client.set_response(f"Evaluate project state: {project_data}", "Project is on track but testing should begin soon.")
    
    evaluation = claude_manager.evaluate_project_state(project_data)
    assert "on track" in evaluation.lower()
    assert "testing" in evaluation.lower()

def test_evaluation_with_context(claude_manager):
    context = "Previous phase had delays due to resource constraints."
    project_state = "Implementation started"
    mock_client = claude_manager.client
    mock_client.set_response(f"Evaluate with context - {context} Current state: {project_state}", 
                             "Proceed with caution, monitor resource allocation closely.")
    
    evaluation = claude_manager.evaluate_with_context(context, project_state)
    assert "caution" in evaluation.lower()
    assert "resource" in evaluation.lower()

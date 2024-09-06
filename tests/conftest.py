import pytest
from src.workflow_director import WorkflowDirector
from src.state_manager import StateManager
from src.llm_manager import LLMManager
from src.claude_manager import ClaudeManager

@pytest.fixture
def workflow_director(mock_state_manager, llm_manager):
    return WorkflowDirector(mock_state_manager, llm_manager)

@pytest.fixture
def mock_state_manager():
    return StateManager()

@pytest.fixture
def llm_manager():
    claude_manager = ClaudeManager()
    return LLMManager(claude_manager)

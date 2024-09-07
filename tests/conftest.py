import pytest
from unittest.mock import MagicMock
from src.workflow_director import WorkflowDirector
from src.state_manager import StateManager
from src.llm_manager import LLMManager
from src.claude_manager import ClaudeManager

@pytest.fixture
def mock_logger():
    logger = MagicMock()
    logger.info = MagicMock()
    logger.debug = MagicMock()
    logger.error = MagicMock()
    logger.warning = MagicMock()
    return logger

@pytest.fixture
def workflow_director(mock_state_manager, llm_manager, mock_logger):
    director = WorkflowDirector(state_manager=mock_state_manager, llm_manager=llm_manager, logger=mock_logger)
    assert director.logger is not None, "Logger is None in WorkflowDirector"
    return director

@pytest.fixture
def mock_state_manager():
    return StateManager()

@pytest.fixture
def llm_manager():
    claude_manager = ClaudeManager()
    return LLMManager(claude_manager)

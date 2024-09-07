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

@pytest.fixture(autouse=True)
def reset_mocks(mock_logger, mock_state_manager):
    mock_logger.reset_mock()
    mock_state_manager.reset_mock()
    mock_state_manager.get_state.return_value = {}

@pytest.fixture
def workflow_director(mock_state_manager, llm_manager, mock_logger):
    director = WorkflowDirector(state_manager=mock_state_manager, llm_manager=llm_manager, logger=mock_logger)
    assert director.logger is not None, "Logger is None in WorkflowDirector"
    yield director
    # Reset all mock calls after each test
    mock_logger.reset_mock()

@pytest.fixture
def mock_state_manager():
    state_manager = MagicMock(spec=StateManager)
    state_manager.get_state.return_value = {}
    return state_manager

@pytest.fixture
def llm_manager():
    claude_manager = ClaudeManager()
    return LLMManager(claude_manager)

def test_evaluate_transition_condition(workflow_director, mock_state_manager, mock_logger):
    workflow_director.logger = mock_logger
    workflow_director.state_manager = mock_state_manager

    # Test with existing key
    mock_state_manager.get_state.return_value = {"flag": True}
    transition_with_condition = {"condition": "state.get('flag', False)"}
    result = workflow_director.evaluate_transition_condition(transition_with_condition)
    assert result == True
    
    # Check all expected log calls
    mock_logger.debug.assert_any_call(f"Entering evaluate_transition_condition with transition: {transition_with_condition}")
    mock_logger.debug.assert_any_call("Entering _evaluate_condition_internal with condition: state.get('flag', False), type: transition condition")
    mock_logger.debug.assert_any_call("Current state: {'flag': True}")
    mock_logger.debug.assert_any_call("Evaluating transition condition: state.get('flag', False)")
    mock_logger.debug.assert_any_call("Evaluated transition condition: state.get('flag', False) = True")
    mock_logger.debug.assert_any_call("Evaluation result type: <class 'bool'>")
    mock_logger.debug.assert_any_call("Boolean conversion result: True")
    mock_logger.debug.assert_any_call("Exiting _evaluate_condition_internal")
    mock_logger.debug.assert_any_call("Exiting evaluate_transition_condition with result: True")

def test_evaluate_condition(workflow_director, mock_state_manager, mock_logger):
    workflow_director.logger = mock_logger
    workflow_director.state_manager = mock_state_manager

    # Test with existing keys
    mock_state_manager.get_state.return_value = {"flag": True, "count": 5}
    condition = "state.get('flag', False)"
    result = workflow_director.evaluate_condition(condition)
    assert result == True
    
    # Check all expected log calls
    mock_logger.debug.assert_any_call(f"Entering evaluate_condition with condition: {condition}")
    mock_logger.debug.assert_any_call(f"Entering _evaluate_condition_internal with condition: {condition}, type: condition")
    mock_logger.debug.assert_any_call("Current state: {'flag': True, 'count': 5}")
    mock_logger.debug.assert_any_call(f"Evaluating condition: {condition}")
    mock_logger.debug.assert_any_call(f"Evaluated condition: {condition} = True")
    mock_logger.debug.assert_any_call("Evaluation result type: <class 'bool'>")
    mock_logger.debug.assert_any_call("Boolean conversion result: True")
    mock_logger.debug.assert_any_call("Exiting _evaluate_condition_internal")
    mock_logger.debug.assert_any_call("Exiting evaluate_condition with result: True")

    condition = "state.get('count', 0) > 10"
    result = workflow_director.evaluate_condition(condition)
    assert result == False
    
    # Check all expected log calls
    mock_logger.debug.assert_any_call(f"Entering evaluate_condition with condition: {condition}")
    mock_logger.debug.assert_any_call(f"Entering _evaluate_condition_internal with condition: {condition}, type: condition")
    mock_logger.debug.assert_any_call("Current state: {'flag': True, 'count': 5}")
    mock_logger.debug.assert_any_call(f"Evaluating condition: {condition}")
    mock_logger.debug.assert_any_call(f"Evaluated condition: {condition} = False")
    mock_logger.debug.assert_any_call("Evaluation result type: <class 'bool'>")
    mock_logger.debug.assert_any_call("Boolean conversion result: False")
    mock_logger.debug.assert_any_call("Exiting _evaluate_condition_internal")
    mock_logger.debug.assert_any_call("Exiting evaluate_condition with result: False")

def test_evaluate_condition_false(workflow_director, mock_state_manager, mock_logger):
    workflow_director.logger = mock_logger
    workflow_director.state_manager = mock_state_manager

    mock_state_manager.get_state.return_value = {"flag": False, "count": 3}
    condition = "state.get('flag', True) and state.get('count', 0) > 5"
    result = workflow_director.evaluate_condition(condition)
    assert result == False
    
    # Check all expected log calls
    mock_logger.debug.assert_any_call(f"Entering evaluate_condition with condition: {condition}")
    mock_logger.debug.assert_any_call(f"Entering _evaluate_condition_internal with condition: {condition}, type: condition")
    mock_logger.debug.assert_any_call("Current state: {'flag': False, 'count': 3}")
    mock_logger.debug.assert_any_call(f"Evaluating condition: {condition}")
    mock_logger.debug.assert_any_call(f"Evaluated condition: {condition} = False")
    mock_logger.debug.assert_any_call("Evaluation result type: <class 'bool'>")
    mock_logger.debug.assert_any_call("Boolean conversion result: False")
    mock_logger.debug.assert_any_call("Exiting _evaluate_condition_internal")
    mock_logger.debug.assert_any_call("Exiting evaluate_condition with result: False")
    def test_evaluate_transition_condition(workflow_director, mock_state_manager, mock_logger):
        workflow_director.logger = mock_logger
        workflow_director.state_manager = mock_state_manager

        # Test with existing key
        mock_state_manager.get_state.return_value = {"flag": True}
        transition_with_condition = {"condition": "state.get('flag', False)"}
        result = workflow_director.evaluate_transition_condition(transition_with_condition)
        assert result == True
        
        # Check all expected log calls
        mock_logger.debug.assert_any_call(f"Entering evaluate_transition_condition with transition: {transition_with_condition}")
        mock_logger.debug.assert_any_call("Entering _evaluate_condition_internal with condition: state.get('flag', False), type: transition condition")
        mock_logger.debug.assert_any_call("Current state: {'flag': True}")
        mock_logger.debug.assert_any_call("Evaluating transition condition: state.get('flag', False)")
        mock_logger.debug.assert_any_call("Evaluated transition condition: state.get('flag', False) = True")
        mock_logger.debug.assert_any_call("Exiting evaluate_transition_condition with result: True")

    def test_evaluate_condition(workflow_director, mock_state_manager, mock_logger):
        workflow_director.logger = mock_logger
        workflow_director.state_manager = mock_state_manager

        # Test with existing keys
        mock_state_manager.get_state.return_value = {"flag": True, "count": 5}
        condition = "state.get('flag', False)"
        result = workflow_director.evaluate_condition(condition)
        assert result == True
        
        # Check all expected log calls
        mock_logger.debug.assert_any_call(f"Entering evaluate_condition with condition: {condition}")
        mock_logger.debug.assert_any_call(f"Entering _evaluate_condition_internal with condition: {condition}, type: condition")
        mock_logger.debug.assert_any_call("Current state: {'flag': True, 'count': 5}")
        mock_logger.debug.assert_any_call(f"Evaluating condition: {condition}")
        mock_logger.debug.assert_any_call(f"Evaluated condition: {condition} = True")
        mock_logger.debug.assert_any_call("Exiting evaluate_condition with result: True")

        condition = "state.get('count', 0) > 10"
        result = workflow_director.evaluate_condition(condition)
        assert result == False
        
        # Check all expected log calls
        mock_logger.debug.assert_any_call(f"Entering evaluate_condition with condition: {condition}")
        mock_logger.debug.assert_any_call(f"Entering _evaluate_condition_internal with condition: {condition}, type: condition")
        mock_logger.debug.assert_any_call("Current state: {'flag': True, 'count': 5}")
        mock_logger.debug.assert_any_call(f"Evaluating condition: {condition}")
        mock_logger.debug.assert_any_call(f"Evaluated condition: {condition} = False")
        mock_logger.debug.assert_any_call("Exiting evaluate_condition with result: False")

    def test_evaluate_condition_false(workflow_director, mock_state_manager, mock_logger):
        workflow_director.logger = mock_logger
        workflow_director.state_manager = mock_state_manager

        mock_state_manager.get_state.return_value = {"flag": False, "count": 3}
        condition = "state.get('flag', True) and state.get('count', 0) > 5"
        result = workflow_director.evaluate_condition(condition)
        assert result == False
        
        # Check all expected log calls
        mock_logger.debug.assert_any_call(f"Entering evaluate_condition with condition: {condition}")
        mock_logger.debug.assert_any_call(f"Entering _evaluate_condition_internal with condition: {condition}, type: condition")
        mock_logger.debug.assert_any_call("Current state: {'flag': False, 'count': 3}")
        mock_logger.debug.assert_any_call(f"Evaluating condition: {condition}")
        mock_logger.debug.assert_any_call(f"Evaluated condition: {condition} = False")
        mock_logger.debug.assert_any_call("Exiting evaluate_condition with result: False")

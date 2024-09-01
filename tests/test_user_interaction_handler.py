import pytest
from unittest.mock import MagicMock
from src.user_interaction_handler import UserInteractionHandler

@pytest.fixture
def user_interaction_handler():
    mock_input = MagicMock()
    mock_print = MagicMock()
    return UserInteractionHandler(input_func=mock_input, print_func=mock_print)

def test_prompt_user(user_interaction_handler):
    user_interaction_handler.input_func.return_value = "test input"
    result = user_interaction_handler.prompt_user("Enter something:")
    assert result == "test input"
    user_interaction_handler.print_func.assert_called_once_with("Enter something:", end=' ')

def test_display_message(user_interaction_handler):
    user_interaction_handler.display_message("Test message")
    user_interaction_handler.print_func.assert_called_once_with("Test message")

def test_confirm_action_yes(user_interaction_handler):
    user_interaction_handler.input_func.return_value = "y"
    assert user_interaction_handler.confirm_action("proceed") == True

def test_confirm_action_no(user_interaction_handler):
    user_interaction_handler.input_func.return_value = "n"
    assert user_interaction_handler.confirm_action("proceed") == False

def test_get_user_choice_valid(user_interaction_handler):
    options = ["Option 1", "Option 2", "Option 3"]
    user_interaction_handler.input_func.return_value = "2"
    result = user_interaction_handler.get_user_choice(options)
    assert result == "Option 2"

def test_get_user_choice_invalid_then_valid(user_interaction_handler):
    options = ["Option 1", "Option 2", "Option 3"]
    user_interaction_handler.input_func.side_effect = ["4", "2"]
    result = user_interaction_handler.get_user_choice(options)
    assert result == "Option 2"
    assert user_interaction_handler.print_func.call_count == 7  # 3 options + 1 invalid message + 2 prompts + 1 "Please choose an option:"

def test_handle_error(user_interaction_handler):
    error = ValueError("Test error")
    user_interaction_handler.handle_error(error)
    assert user_interaction_handler.print_func.call_count == 2
    user_interaction_handler.print_func.assert_any_call("An error occurred: Test error")

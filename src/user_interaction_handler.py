import logging
from typing import Any, Callable

class UserInteractionHandler:
    def __init__(self, input_func: Callable = input, print_func: Callable = print):
        self.logger = logging.getLogger(__name__)
        self.input_func = input_func
        self.print_func = print_func

    def prompt_user(self, message: str) -> str:
        self.logger.info(f"Prompting user: {message}")
        self.print_func(message, end=' ')
        user_input = self.input_func()
        self.logger.debug(f"User input received: {user_input}")
        return user_input

    def display_message(self, message: str) -> None:
        self.logger.info(f"Displaying message: {message}")
        self.print_func(message)

    def confirm_action(self, action: str) -> bool:
        response = self.prompt_user(f"Do you want to {action}? (y/n)").lower()
        confirmed = response.startswith('y')
        self.logger.info(f"User {'confirmed' if confirmed else 'declined'} action: {action}")
        return confirmed

    def get_user_choice(self, options: list[str]) -> str:
        self.display_message("Please choose an option:")
        for i, option in enumerate(options, 1):
            self.display_message(f"{i}. {option}")
        while True:
            choice = self.prompt_user("Enter the number of your choice:")
            try:
                index = int(choice) - 1
                if 0 <= index < len(options):
                    selected = options[index]
                    self.logger.info(f"User selected option: {selected}")
                    return selected
                else:
                    self.display_message("Invalid choice. Please try again.")
            except ValueError:
                self.display_message("Invalid input. Please enter a number.")

    def handle_error(self, error: Exception) -> None:
        error_message = f"An error occurred: {str(error)}"
        self.logger.error(error_message)
        self.display_message(error_message)
        self.display_message("Please try again or contact support if the issue persists.")

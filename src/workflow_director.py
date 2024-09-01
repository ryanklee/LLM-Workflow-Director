import logging
from .state_manager import StateManager
from .llm_manager import LLMManager
from .error_handler import ErrorHandler


class WorkflowDirector:
    def __init__(self, input_func=input, print_func=print):
        self.state_manager = StateManager()
        self.llm_manager = LLMManager()
        self.error_handler = ErrorHandler()
        self.input_func = input_func
        self.print_func = print_func
        self.logger = logging.getLogger(__name__)

    def run(self):
        self.logger.info("Starting LLM Workflow Director")
        self.print_func("Starting LLM Workflow Director")
        while True:
            try:
                self.print_func("Enter a command (or 'exit' to quit): ", end='')
                user_input = self.input_func()
                if user_input.lower() == 'exit':
                    break
                response = self.llm_manager.query(user_input)
                self.print_func(f"LLM response: {response}")
            except Exception as e:
                error_message = self.error_handler.handle_error(e)
                self.logger.error(f"Error occurred: {error_message}")
                self.print_func(f"An error occurred: {error_message}")
        self.logger.info("Exiting LLM Workflow Director")
        self.print_func("Exiting LLM Workflow Director")

    def handle_error(self, error):
        return self.error_handler.handle_error(error)

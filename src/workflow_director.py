import logging
import yaml
from .state_manager import StateManager
from .llm_manager import LLMManager
from .error_handler import ErrorHandler


class WorkflowDirector:
    def __init__(self, config_path='src/workflow_config.yaml', input_func=input, print_func=print):
        self.state_manager = StateManager()
        self.llm_manager = LLMManager()
        self.error_handler = ErrorHandler()
        self.input_func = input_func
        self.print_func = print_func
        self.logger = logging.getLogger(__name__)
        self.config = self.load_config(config_path)
        self.current_stage = self.config['stages'][0]['name']

    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as config_file:
                return yaml.safe_load(config_file)
        except Exception as e:
            error_message = self.error_handler.handle_error(e)
            self.logger.error(f"Error loading configuration: {error_message}")
            raise

    def run(self):
        self.logger.info("Starting LLM Workflow Director")
        self.print_func("Starting LLM Workflow Director")
        while True:
            try:
                self.print_func(f"Current stage: {self.current_stage}")
                self.print_func("Enter a command (or 'exit' to quit): ", end='')
                user_input = self.input_func()
                if user_input.lower() == 'exit':
                    break
                elif user_input.lower() == 'next':
                    self.move_to_next_stage()
                else:
                    response = self.llm_manager.query(user_input)
                    self.print_func(f"LLM response: {response}")
            except Exception as e:
                error_message = self.error_handler.handle_error(e)
                self.logger.error(f"Error occurred: {error_message}")
                self.print_func(f"An error occurred: {error_message}")
        self.logger.info("Exiting LLM Workflow Director")
        self.print_func("Exiting LLM Workflow Director")

    def move_to_next_stage(self):
        current_index = next((i for i, stage in enumerate(self.config['stages']) if stage['name'] == self.current_stage), None)
        if current_index is not None and current_index < len(self.config['stages']) - 1:
            next_stage = self.config['stages'][current_index + 1]['name']
            transition = next((t for t in self.config['transitions'] if t['from'] == self.current_stage and t['to'] == next_stage), None)
            if transition:
                self.current_stage = next_stage
                self.print_func(f"Moving to next stage: {self.current_stage}")
                self.print_func(f"Condition: {transition['condition']}")
            else:
                self.print_func("No valid transition found to the next stage.")
        else:
            self.print_func("Already at the final stage.")

    def handle_error(self, error):
        return self.error_handler.handle_error(error)

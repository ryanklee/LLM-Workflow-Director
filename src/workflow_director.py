import logging
import yaml
from .state_manager import StateManager
from .llm_manager import LLMManager
from .error_handler import ErrorHandler


class WorkflowDirector:
    def __init__(self, config_path='src/workflow_config.yaml', input_func=input, print_func=print):
        self.logger = logging.getLogger(__name__)
        self.state_manager = StateManager()
        self.llm_manager = None
        try:
            self.llm_manager = LLMManager()
        except Exception as e:
            self.logger.error(f"Error initializing LLMManager: {str(e)}")
        self.error_handler = ErrorHandler()
        self.input_func = input_func
        self.print_func = print_func
        self.config = self.load_config(config_path)
        self.current_stage = self.config['stages'][0]['name'] if self.config else "Default Stage"
        self.stages = {stage['name']: stage for stage in self.config['stages']}
        self.transitions = self.config['transitions']

    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as config_file:
                return yaml.safe_load(config_file)
        except Exception as e:
            error_message = self.error_handler.handle_error(e)
            self.logger.error(f"Error loading configuration: {error_message}")
            self.logger.warning("Using default configuration")
            return {
                'stages': [{'name': 'Default Stage'}],
                'transitions': []
            }

    def run(self):
        self.logger.info("Starting LLM Workflow Director")
        self.print_func("Starting LLM Workflow Director")
        while True:
            try:
                current_stage = self.get_current_stage()
                self.print_func(f"Current stage: {current_stage['name']}")
                self.print_func(f"Description: {current_stage['description']}")
                self.print_func("Tasks:")
                for task in current_stage['tasks']:
                    self.print_func(f"- {task}")
                self.print_func("Enter a command ('next' for next stage, 'exit' to quit): ", end='')
                user_input = self.input_func()
                if user_input.lower() == 'exit':
                    break
                elif user_input.lower() == 'next':
                    if not self.move_to_next_stage():
                        self.print_func("Cannot move to the next stage. Please complete the current stage's tasks.")
                else:
                    if self.llm_manager:
                        response = self.llm_manager.query(user_input)
                        self.print_func(f"LLM response: {response}")
                    else:
                        self.print_func("LLM manager is not available. Unable to process the command.")
            except Exception as e:
                error_message = self.error_handler.handle_error(e)
                self.logger.error(f"Error occurred: {error_message}")
                self.print_func(f"An error occurred: {error_message}")
        self.logger.info("Exiting LLM Workflow Director")
        self.print_func("Exiting LLM Workflow Director")

    def get_current_stage(self):
        return self.stages[self.current_stage]

    def get_available_transitions(self):
        return [t for t in self.transitions if t['from'] == self.current_stage]

    def can_transition_to(self, next_stage):
        return any(t['to'] == next_stage for t in self.get_available_transitions())

    def transition_to(self, next_stage):
        if self.can_transition_to(next_stage):
            self.current_stage = next_stage
            self.print_func(f"Transitioned to stage: {next_stage}")
            return True
        else:
            self.print_func(f"Cannot transition to stage: {next_stage}")
            return False

    def move_to_next_stage(self):
        available_transitions = self.get_available_transitions()
        if available_transitions:
            next_stage = available_transitions[0]['to']
            return self.transition_to(next_stage)
        else:
            self.print_func("No available transitions from the current stage.")
            return False

    def handle_error(self, error):
        return self.error_handler.handle_error(error)

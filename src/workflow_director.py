import logging
import yaml
from .state_manager import StateManager
from .llm_manager import LLMManager
from .error_handler import ErrorHandler
from src.vectorstore.vector_store import VectorStore


class WorkflowDirector:
    def __init__(self, config_path='src/workflow_config.yaml', input_func=input, print_func=print):
        self.logger = logging.getLogger(__name__)
        self.state_manager = StateManager()
        self.vector_store = VectorStore()
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
        self.stage_progress = {stage: 0.0 for stage in self.stages}
        self.completed_stages = set()

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
                self.print_func(f"Stage progress: {self.get_stage_progress():.2%}")
                self.print_func("Enter a command ('next' for next stage, 'complete' to finish current stage, 'exit' to quit): ", end='')
                user_input = self.input_func()
                if user_input.lower() == 'exit':
                    break
                elif user_input.lower() == 'next':
                    if self.move_to_next_stage():
                        self.print_func(f"Moved to next stage: {self.current_stage}")
                    else:
                        self.print_func("Cannot move to the next stage. Please complete the current stage's tasks.")
                elif user_input.lower() == 'complete':
                    if self.complete_current_stage():
                        self.print_func(f"Completed current stage and moved to: {self.current_stage}")
                    else:
                        self.print_func("Completed current stage. This was the final stage.")
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

    def complete_current_stage(self):
        self.stage_progress[self.current_stage] = 1.0
        self.completed_stages.add(self.current_stage)
        self.print_func(f"Completed stage: {self.current_stage}")
        return self.move_to_next_stage()

    def get_stage_progress(self):
        return self.stage_progress[self.current_stage]

    def update_stage_progress(self, progress):
        self.stage_progress[self.current_stage] = max(0.0, min(1.0, progress))

    def handle_error(self, error):
        return self.error_handler.handle_error(error)

    def is_stage_completed(self, stage_name):
        return stage_name in self.completed_stages

    def can_transition_to(self, next_stage):
        available_transitions = [t for t in self.transitions if t['from'] == self.current_stage and t['to'] == next_stage]
        if not available_transitions:
            return False
        if self.is_stage_completed(self.current_stage):
            return True
        transition = available_transitions[0]
        return 'condition' not in transition or self.evaluate_condition(transition['condition'])

    def evaluate_condition(self, condition):
        # This is a placeholder. In a real implementation, you would evaluate the condition based on the current state.
        return True

    def complete_current_stage(self):
        self.stage_progress[self.current_stage] = 1.0
        self.completed_stages.add(self.current_stage)
        self.print_func(f"Completed stage: {self.current_stage}")
        return self.move_to_next_stage()

    def evaluate_condition(self, condition):
        # This is a placeholder. In a real implementation, you would evaluate the condition based on the current state.
        return True

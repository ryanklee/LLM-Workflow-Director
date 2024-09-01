import logging
import yaml
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.state_manager import StateManager
from src.llm_manager import LLMManager
from src.sufficiency_evaluator import SufficiencyEvaluator
from src.error_handler import ErrorHandler
from src.vectorstore.vector_store import VectorStore
from src.constraint_engine import ConstraintEngine, Constraint
from src.project_state_reporter import ProjectStateReporter
from src.documentation_health_checker import DocumentationHealthChecker
from src.project_structure_manager import ProjectStructureManager
from src.convention_manager import ConventionManager


class WorkflowDirector:
    def __init__(self, config_path='src/workflow_config.yaml', input_func=input, print_func=print):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Add a file handler for persistent logging
        file_handler = logging.FileHandler('workflow_director.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.state_manager = StateManager()
        self.vector_store = VectorStore()
        self.constraint_engine = ConstraintEngine()
        self.logger.info("ConstraintEngine initialized")
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
        self.initialize_constraints()
        self.project_state_reporter = ProjectStateReporter(self)
        self.documentation_health_checker = DocumentationHealthChecker()
        self.project_structure_manager = ProjectStructureManager()
        self.convention_manager = ConventionManager()
        self.sufficiency_evaluator = SufficiencyEvaluator(self.llm_manager) if self.llm_manager else None

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
                        tier = self.determine_query_tier(user_input)
                        context = {
                            'workflow_stage': self.current_stage,
                            'project_structure_instructions': self.project_structure_manager.get_structure_instructions(),
                            'coding_conventions': self.convention_manager.get_aider_conventions()
                        }
                        response = self.llm_manager.query(user_input, context=context, tier=tier)
                        self.print_func(f"LLM response: {response}")
                    else:
                        self.print_func("LLM manager is not available. Unable to process the command.")
            except Exception as e:
                error_message = self.error_handler.handle_error(e)
                self.logger.error(f"Error occurred: {error_message}")
                self.print_func(f"An error occurred: {error_message}")
        self.logger.info("Exiting LLM Workflow Director")
        self.print_func("Exiting LLM Workflow Director")

    def determine_query_tier(self, query: str) -> str:
        # Simple heuristic for determining the appropriate tier
        if len(query.split()) < 10:
            return 'fast'
        elif len(query.split()) > 50 or any(keyword in query.lower() for keyword in ['complex', 'detailed', 'analyze']):
            return 'powerful'
        else:
            return 'balanced'

    def get_current_stage(self):
        return self.stages[self.current_stage]

    def get_available_transitions(self):
        return [t for t in self.transitions if t['from'] == self.current_stage]

    def can_transition_to(self, next_stage):
        return any(t['to'] == next_stage for t in self.get_available_transitions())

    def transition_to(self, next_stage):
        self.logger.info(f"Attempting to transition from {self.current_stage} to {next_stage}")
        if self.can_transition_to(next_stage):
            previous_stage = self.current_stage
            self.current_stage = next_stage
            if previous_stage not in self.completed_stages:
                self.completed_stages.add(previous_stage)
            self.print_func(f"Transitioned to stage: {next_stage}")
            self.logger.info(f"Successfully transitioned to stage: {next_stage}")
            self.logger.debug(f"Updated completed stages: {self.completed_stages}")
            return True
        else:
            self.print_func(f"Cannot transition to stage: {next_stage}")
            self.logger.warning(f"Transition to {next_stage} not allowed")
            self.logger.debug(f"Current completed stages: {self.completed_stages}")
            return False

    def get_available_transitions(self):
        return [t for t in self.transitions if t['from'] == self.current_stage]

    def can_transition_to(self, next_stage):
        self.logger.info(f"Checking if transition from {self.current_stage} to {next_stage} is possible")
        available_transitions = self.get_available_transitions()
        return any(t['to'] == next_stage for t in available_transitions)

    def move_to_next_stage(self):
        available_transitions = self.get_available_transitions()
        if available_transitions:
            next_stage = available_transitions[0]['to']
            return self.transition_to(next_stage)
        self.print_func("No available transitions from the current stage.")
        return False

    def complete_current_stage(self):
        self.logger.info(f"Completing stage: {self.current_stage}")
        self.stage_progress[self.current_stage] = 1.0
        self.completed_stages.add(self.current_stage)
        self.print_func(f"Completed stage: {self.current_stage}")
        self.logger.info(f"Stage {self.current_stage} marked as completed")
        
        available_transitions = self.get_available_transitions()
        if available_transitions:
            next_stage = available_transitions[0]['to']
            if self.transition_to(next_stage):
                self.logger.info(f"Moved to next stage: {self.current_stage}")
                return True
            else:
                self.logger.warning(f"Failed to transition to next stage: {next_stage}")
        else:
            self.logger.info("No next stage available")
        
        if self.current_stage == self.config['stages'][-1]['name']:
            self.logger.info("Completed final stage")
            return True
        return self.move_to_next_stage()

    def get_available_transitions(self):
        return [t for t in self.transitions if t['from'] == self.current_stage]

    def get_stage_progress(self):
        return self.stage_progress[self.current_stage]

    def update_stage_progress(self, progress):
        self.stage_progress[self.current_stage] = max(0.0, min(1.0, progress))

    def handle_error(self, error):
        return self.error_handler.handle_error(error)

    def is_stage_completed(self, stage_name):
        return stage_name in self.completed_stages

    def can_transition_to(self, next_stage):
        self.logger.info(f"Checking if transition from {self.current_stage} to {next_stage} is possible")
        
        # Always allow transition if the current stage is completed
        if self.is_stage_completed(self.current_stage):
            self.logger.info(f"Stage {self.current_stage} is already completed, transition allowed")
            return True

        # Allow transition to the current stage
        if self.current_stage == next_stage:
            self.logger.info(f"Transition to current stage {next_stage} is allowed")
            return True

        available_transitions = [t for t in self.transitions if t['from'] == self.current_stage and t['to'] == next_stage]
        if not available_transitions:
            self.logger.info(f"No transition defined from {self.current_stage} to {next_stage}")
            return False

        current_state = self.state_manager.get_all()
        self.logger.debug(f"Current state: {current_state}")
        validation_result = self.constraint_engine.ValidateAll(current_state)

        if isinstance(validation_result, tuple) and len(validation_result) == 2:
            is_valid, violations = validation_result
            if not is_valid:
                self.logger.warning(f"Cannot transition to {next_stage}. Constraint violations: {', '.join(violations)}")
                return False
            else:
                self.logger.info(f"All constraints passed for transition to {next_stage}")
        else:
            self.logger.error(f"Unexpected result from constraint validation: {validation_result}")
            return False

        # Check if there's a condition for this transition
        transition_condition = next((t.get('condition') for t in self.transitions if t['from'] == self.current_stage and t['to'] == next_stage), None)
        if transition_condition:
            condition_met = self.evaluate_condition(transition_condition)
            if not condition_met:
                self.logger.info(f"Transition condition not met: {transition_condition}")
                return False
            else:
                self.logger.info(f"Transition condition met: {transition_condition}")

        self.logger.info(f"Transition to {next_stage} is allowed")
        return True

    def evaluate_condition(self, condition):
        # This is a placeholder. In a real implementation, you would evaluate the condition based on the current state.
        return True

    def complete_current_stage(self):
        self.logger.info(f"Completing stage: {self.current_stage}")
        self.stage_progress[self.current_stage] = 1.0
        self.completed_stages.add(self.current_stage)
        self.print_func(f"Completed stage: {self.current_stage}")
        self.logger.info(f"Stage {self.current_stage} marked as completed")
        
        if self.current_stage == self.config['stages'][-1]['name']:
            self.logger.info("Completed final stage")
            return True

        next_stage = self.get_next_stage()
        if next_stage:
            if self.transition_to(next_stage):
                self.logger.info(f"Moved to next stage: {self.current_stage}")
                return True
            else:
                self.logger.warning(f"Failed to transition to next stage: {next_stage}")
                return False
        else:
            self.logger.info("No next stage available")
            return False

    def get_next_stage(self):
        valid_transitions = [t['to'] for t in self.transitions if t['from'] == self.current_stage]
        if valid_transitions:
            return valid_transitions[0]
        return None

    def can_transition_to(self, next_stage):
        self.logger.info(f"Checking if transition from {self.current_stage} to {next_stage} is possible")
        
        # Always allow transition if the current stage is completed
        if self.is_stage_completed(self.current_stage):
            self.logger.info(f"Stage {self.current_stage} is already completed, transition allowed")
            return True

        # Check if there's a valid transition defined
        valid_transitions = [t for t in self.transitions if t['from'] == self.current_stage and t['to'] == next_stage]
        if valid_transitions:
            self.logger.info(f"Valid transition found from {self.current_stage} to {next_stage}")
            return True

        # Check if the next stage is the current stage (allows staying in the same stage)
        if self.current_stage == next_stage:
            self.logger.info(f"Transition to current stage {next_stage} is allowed")
            return True

        # Check if there's a valid transition from any completed stage to the next stage
        for completed_stage in self.completed_stages:
            if any(t['from'] == completed_stage and t['to'] == next_stage for t in self.transitions):
                self.logger.info(f"Valid transition found from completed stage {completed_stage} to {next_stage}")
                return True

        self.logger.info(f"No valid transition found from {self.current_stage} to {next_stage}")
        return False

    def get_next_stage(self):
        valid_transitions = [t for t in self.transitions if t['from'] == self.current_stage]
        if valid_transitions:
            # Prioritize transitions to uncompleted stages
            for transition in valid_transitions:
                if transition['to'] not in self.completed_stages:
                    return transition['to']
            # If all possible next stages are completed, return the first one
            return valid_transitions[0]['to']
        return None

    def complete_current_stage(self):
        self.logger.info(f"Completing stage: {self.current_stage}")
        self.stage_progress[self.current_stage] = 1.0
        self.completed_stages.add(self.current_stage)
        self.print_func(f"Completed stage: {self.current_stage}")
        self.logger.info(f"Stage {self.current_stage} marked as completed")
        
        next_stage = self.get_next_stage()
        if next_stage:
            if self.can_transition_to(next_stage):
                if self.transition_to(next_stage):
                    self.logger.info(f"Moved to next stage: {self.current_stage}")
                    return True
                else:
                    self.logger.warning(f"Failed to transition to next stage: {next_stage}")
                    return False
            else:
                self.logger.warning(f"Cannot transition to next stage: {next_stage}")
                return False
        else:
            self.logger.info("No next stage available")
            return self.current_stage == self.config['stages'][-1]['name']

    def get_next_stage(self):
        valid_transitions = [t for t in self.transitions if t['from'] == self.current_stage]
        if valid_transitions:
            return valid_transitions[0]['to']
        return None

    def complete_current_stage(self):
        self.logger.info(f"Attempting to complete stage: {self.current_stage}")
        current_stage_data = self.stages[self.current_stage]
        project_state = self.state_manager.get_all()
        
        if self.sufficiency_evaluator:
            is_sufficient, reasoning = self.sufficiency_evaluator.evaluate_stage_sufficiency(
                self.current_stage, current_stage_data, project_state
            )
        else:
            is_sufficient, reasoning = True, "SufficiencyEvaluator not available. Stage assumed to be sufficient."
        
        # Mark the stage as completed regardless of sufficiency
        self.stage_progress[self.current_stage] = 1.0
        self.completed_stages.add(self.current_stage)
        
        if not is_sufficient:
            self.logger.warning(f"Stage {self.current_stage} is not sufficient for completion, but marked as completed")
            self.print_func(f"Stage {self.current_stage} is marked as complete, but may need further attention. Reason: {reasoning}")
        else:
            self.logger.info(f"Stage {self.current_stage} is sufficient for completion")
            self.print_func(f"Completed stage: {self.current_stage}")
            self.print_func(f"Completion reasoning: {reasoning}")
        
        next_stage = self.get_next_stage()
        if next_stage:
            if self.transition_to(next_stage):
                self.logger.info(f"Moved to next stage: {self.current_stage}")
            else:
                self.logger.warning(f"Failed to transition to next stage: {next_stage}")
        else:
            self.logger.info("No next stage available")
        
        return True  # Always return True when the stage is completed

    def transition_to(self, next_stage):
        self.logger.info(f"Attempting to transition from {self.current_stage} to {next_stage}")
        if self.can_transition_to(next_stage):
            previous_stage = self.current_stage
            self.current_stage = next_stage
            self.completed_stages.add(previous_stage)
            self.stage_progress[previous_stage] = 1.0  # Ensure the previous stage is marked as 100% complete
            self.print_func(f"Transitioned to stage: {next_stage}")
            self.logger.info(f"Successfully transitioned to stage: {next_stage}")
            self.logger.debug(f"Updated completed stages: {self.completed_stages}")
            return True
        else:
            self.print_func(f"Cannot transition to stage: {next_stage}")
            self.logger.warning(f"Transition to {next_stage} not allowed")
            self.logger.debug(f"Current completed stages: {self.completed_stages}")
            return False

    def get_next_stage(self):
        current_index = next((i for i, stage in enumerate(self.config['stages']) if stage['name'] == self.current_stage), None)
        if current_index is not None and current_index < len(self.config['stages']) - 1:
            return self.config['stages'][current_index + 1]['name']
        return None

    def evaluate_condition(self, condition):
        # This is a placeholder. In a real implementation, you would evaluate the condition based on the current state.
        return True
    def initialize_constraints(self):
        for stage in self.config['stages']:
            if 'constraints' in stage:
                for constraint in stage['constraints']:
                    self.constraint_engine.add_constraint(Constraint(
                        name=f"{stage['name']}_{constraint['name']}",
                        description=constraint['description'],
                        validate=lambda state, c=constraint: self.validate_constraint(state, c)
                    ))

    def validate_constraint(self, state, constraint):
        # This is a placeholder implementation. In a real-world scenario,
        # you would implement more sophisticated constraint validation logic.
        if 'condition' in constraint:
            return eval(constraint['condition'], {'state': state}), None
        return True, None

    def generate_project_report(self, format='plain'):
        """
        Generate a comprehensive project state report.
        
        Args:
            format (str): The output format of the report. Options: 'plain', 'markdown', 'html'
        
        Returns:
            str: The formatted project state report
        """
        self.logger.info("Generating project state report")
        report = self.project_state_reporter.generate_report(format)
        self.logger.info("Project state report generated successfully")
        return report

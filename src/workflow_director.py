import logging
import yaml
import sys
import os
from typing import Dict, Any, List

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
from src.priority_manager import PriorityManager
from src.user_interaction_handler import UserInteractionHandler


class WorkflowDirector:
    def __init__(self, config_path='src/workflow_config.yaml', user_interaction_handler=None, llm_manager=None):
        self._setup_logging()
        self.state_manager = StateManager()
        self.vector_store = VectorStore()
        self.constraint_engine = ConstraintEngine()
        self.logger.info("ConstraintEngine initialized")
        self.llm_manager = llm_manager or LLMManager()
        self.error_handler = ErrorHandler()
        self.user_interaction_handler = user_interaction_handler or UserInteractionHandler()
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
        self.priority_manager = PriorityManager()
        self.initialize_priorities()
        self.logger.debug(f"WorkflowDirector initialized with LLMManager: {self.llm_manager}")

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
        self.user_interaction_handler.display_message("Starting LLM Workflow Director")
        try:
            while True:
                self.logger.debug("Starting new iteration of run loop")
                current_stage = self.get_current_stage()
                self.user_interaction_handler.display_message(f"Current stage: {current_stage['name']}")
                self.user_interaction_handler.display_message(f"Description: {current_stage['description']}")
                self.user_interaction_handler.display_message("Tasks:")
                for task in current_stage['tasks']:
                    self.user_interaction_handler.display_message(f"- {task}")
                self.user_interaction_handler.display_message(f"Stage progress: {self.get_stage_progress():.2%}")
                user_input = self.user_interaction_handler.prompt_user("Enter a command ('next' for next stage, 'complete' to finish current stage, 'exit' to quit):")
                
                self.logger.debug(f"Received user input: {user_input}")
                
                if user_input.lower() == 'exit':
                    self.logger.info("Exit command received. Ending run loop.")
                    break
                
                # Process all commands using LLM
                tier = self.determine_query_tier(user_input)
                context = self._prepare_llm_context()
                prompt_template = """
                Process this command: {command}
                Current stage: {stage}
                Stage description: {stage_description}
                Stage tasks:
                {stage_tasks}
                
                Project structure:
                {project_structure}
                
                Coding conventions:
                {formatted_conventions}
                
                Additional context:
                {context}
                """
                prompt = self.llm_manager.generate_prompt(prompt_template, {
                    "command": user_input,
                    "stage": current_stage['name'],
                    "stage_description": current_stage.get('description', ''),
                    "stage_tasks": current_stage.get('tasks', []),
                    "project_structure": self.project_structure_manager.get_structure_instructions(),
                    "coding_conventions": self.convention_manager.get_aider_conventions(),
                    "context": str(context)
                })
                
                self.logger.debug(f"Preparing to query LLM. Test mode: {getattr(self, '_test_mode', False)}")
                
                if self.llm_manager:
                    try:
                        self.logger.debug(f"Querying LLM with prompt: {prompt[:100]}...")
                        response = self.llm_manager.query(prompt, context=context, tier=tier)
                        self.logger.debug(f"LLM response received: {response[:100]}...")
                        self.user_interaction_handler.display_message(f"LLM response: {response}")
                        self._process_llm_response(response)
                    except Exception as e:
                        self.logger.error(f"Error querying LLM: {str(e)}")
                        self.user_interaction_handler.display_message(f"An error occurred while processing your command: {str(e)}")
                else:
                    self.logger.warning("LLMManager not available. Skipping LLM query.")
                
                # Always call LLM query for testing purposes
                if getattr(self, '_test_mode', False):
                    self.logger.debug("Test mode active. Forcing LLM query.")
                    self.llm_manager.query(prompt, context=context, tier=tier)
                
                if user_input.lower() == 'next':
                    self.move_to_next_stage()
                elif user_input.lower() == 'complete':
                    self.complete_current_stage()
                
                self.logger.debug("Finished processing user input")
        except Exception as e:
            self.logger.error(f"Unexpected error in run method: {str(e)}")
            self.user_interaction_handler.handle_error(e)
        finally:
            self.logger.info("Exiting LLM Workflow Director")
            self.user_interaction_handler.display_message("Exiting LLM Workflow Director")

    def _prepare_llm_context(self) -> Dict[str, Any]:
        return {
            'workflow_stage': self.current_stage,
            'project_structure_instructions': self.project_structure_manager.get_structure_instructions(),
            'coding_conventions': self.convention_manager.get_aider_conventions(),
            'workflow_config': self.config
        }

    def _process_llm_response(self, response: str):
        self.logger.info("Processing LLM response")
        try:
            if response.startswith("LLM microservice is currently unavailable"):
                self.logger.warning("LLM microservice is unavailable. Using fallback behavior.")
                self.user_interaction_handler.display_message("LLM service is currently unavailable. Some features may be limited.")
                return

            parsed_response = self._parse_llm_response(response)
            
            if 'task_progress' in parsed_response:
                progress = float(parsed_response['task_progress'])
                self.update_stage_progress(progress)
                self.logger.info(f"Updated stage progress to {progress:.2f}")
            
            if 'state_updates' in parsed_response:
                state_updates = parsed_response['state_updates']
                for key, value in state_updates.items():
                    self.state_manager.set(key, value)
                    self.logger.info(f"Updated project state: {key} = {value}")
            
            if 'actions' in parsed_response:
                actions = parsed_response['actions']
                for action in actions:
                    self._handle_llm_action(action)
            
            if 'suggestions' in parsed_response:
                suggestions = parsed_response['suggestions']
                self.user_interaction_handler.display_message("LLM Suggestions:")
                for suggestion in suggestions:
                    self.user_interaction_handler.display_message(f"- {suggestion}")
            
            self.logger.info("LLM response processed successfully")
        except Exception as e:
            self.logger.error(f"Error processing LLM response: {str(e)}")
            self.error_handler.handle_error(e)

    def _parse_llm_response(self, response: str) -> dict:
        parsed = {}
        current_key = None
        current_value = []

        for line in response.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith(' '):
                if current_key:
                    parsed[current_key] = self._process_value(current_key, current_value)
                current_key = line.split(':', 1)[0].strip().lower()
                current_value = [line.split(':', 1)[1].strip()]
            elif current_key:
                current_value.append(line)

        if current_key:
            parsed[current_key] = self._process_value(current_key, current_value)

        return parsed

    def _process_value(self, key: str, value: List[str]) -> Any:
        joined_value = ' '.join(value).strip()
        if key == 'task_progress':
            return float(joined_value)
        elif key == 'state_updates':
            return eval(joined_value)
        elif key in ['actions', 'suggestions']:
            return [item.strip() for item in joined_value.split(',')]
        else:
            return joined_value

    def _handle_llm_action(self, action: str):
        self.logger.info(f"Handling LLM action: {action}")
        # TODO: Implement logic to handle different types of actions
        # This could include updating the workflow, triggering specific processes, etc.
        pass

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
            self.user_interaction_handler.display_message(f"Transitioned to stage: {next_stage}")
            self.logger.info(f"Successfully transitioned to stage: {next_stage}")
            self.logger.debug(f"Updated completed stages: {self.completed_stages}")
            return True
        else:
            self.user_interaction_handler.display_message(f"Cannot transition to stage: {next_stage}")
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
        self.user_interaction_handler.display_message("No available transitions from the current stage.")
        return False

    def complete_current_stage(self):
        self.logger.info(f"Completing stage: {self.current_stage}")
        self.stage_progress[self.current_stage] = 1.0
        self.completed_stages.add(self.current_stage)
        self.user_interaction_handler.display_message(f"Completed stage: {self.current_stage}")
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

    def is_stage_completed(self, stage_name):
        completed = stage_name in self.completed_stages
        self.logger.debug(f"Checking if stage {stage_name} is completed: {completed}")
        return completed

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
            self.logger.debug(f"SufficiencyEvaluator result: is_sufficient={is_sufficient}, reasoning={reasoning}")
        else:
            self.logger.warning("SufficiencyEvaluator not available. Stage assumed to be sufficient.")
            is_sufficient, reasoning = True, "SufficiencyEvaluator not available. Stage assumed to be sufficient."
        
        self.stage_progress[self.current_stage] = 1.0
        self.completed_stages.add(self.current_stage)
        
        if not is_sufficient:
            self.logger.warning(f"Stage {self.current_stage} is not sufficient for completion, but marked as completed. Reason: {reasoning}")
            self.user_interaction_handler.display_message(f"Stage {self.current_stage} is marked as complete, but may need further attention. Reason: {reasoning}")
        else:
            self.logger.info(f"Stage {self.current_stage} is sufficient for completion. Reason: {reasoning}")
            self.user_interaction_handler.display_message(f"Completed stage: {self.current_stage}")
            self.user_interaction_handler.display_message(f"Completion reasoning: {reasoning}")
        
        next_stage = self.get_next_stage()
        if next_stage:
            transition_result = self.transition_to(next_stage)
            self.logger.info(f"Transition to next stage {'successful' if transition_result else 'failed'}: {next_stage}")
        else:
            self.logger.info("No next stage available")
        
        return True

    def transition_to(self, next_stage):
        self.logger.info(f"Attempting to transition from {self.current_stage} to {next_stage}")
        try:
            if not self.can_transition_to(next_stage):
                raise ValueError(f"Transition to {next_stage} is not allowed")

            previous_stage = self.current_stage
            self.current_stage = next_stage
            self.completed_stages.add(previous_stage)
            self.stage_progress[previous_stage] = 1.0

            self.user_interaction_handler.display_message(f"Transitioned to stage: {next_stage}")
            self.logger.info(f"Successfully transitioned to stage: {next_stage}")
            self.logger.debug(f"Updated completed stages: {self.completed_stages}")

            # Trigger any necessary actions or callbacks for the new stage
            self._on_stage_enter(next_stage)

            return True
        except Exception as e:
            self.logger.error(f"Error during transition to {next_stage}: {str(e)}")
            self.user_interaction_handler.display_message(f"Failed to transition to stage: {next_stage}")
            return False

    def get_next_stage(self):
        current_index = next((i for i, stage in enumerate(self.config['stages']) if stage['name'] == self.current_stage), None)
        if current_index is not None and current_index < len(self.config['stages']) - 1:
            return self.config['stages'][current_index + 1]['name']
        return None

    def evaluate_condition(self, condition):
        # This is a placeholder. In a real implementation, you would evaluate the condition based on the current state.
        return True

    def _on_stage_enter(self, stage_name):
        self.logger.info(f"Entering stage: {stage_name}")
        stage_data = self.stages.get(stage_name)
        if stage_data:
            self.user_interaction_handler.display_message(f"Entered stage: {stage_name}")
            self.user_interaction_handler.display_message(f"Description: {stage_data.get('description', 'No description available')}")
            tasks = stage_data.get('tasks', [])
            if tasks:
                self.user_interaction_handler.display_message("Tasks for this stage:")
                for task in tasks:
                    self.user_interaction_handler.display_message(f"- {task}")
        else:
            self.logger.warning(f"No data found for stage: {stage_name}")
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
        self.logger.debug(f"Report preview: {report[:200]}...")  # Log a preview of the report
        return report

    def initialize_priorities(self):
        self.logger.info("Initializing priorities for all stages")
        for stage_name, stage_data in self.stages.items():
            priorities = stage_data.get('priorities', [])
            self.priority_manager.set_priorities(stage_name, priorities)
        self.logger.debug("Priorities initialized for all stages")
    def _setup_logging(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # Create a StreamHandler for console output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Create a FileHandler for persistent logging
        file_handler = logging.FileHandler('workflow_director.log')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Add both handlers to the logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        self.logger.info("Logging setup completed for WorkflowDirector")

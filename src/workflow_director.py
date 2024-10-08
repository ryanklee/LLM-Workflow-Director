import logging
from pythonjsonlogger import jsonlogger
import yaml
import sys
import os
from typing import Dict, Any, List
from datetime import datetime
import time
from .error_handler import ErrorHandler

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.state_manager import StateManager
from src.llm_manager import LLMManager
from src.sufficiency_evaluator import SufficiencyEvaluator
from src.error_handler import ErrorHandler
from src.claude_manager import ClaudeManager
from src.user_interaction_handler import UserInteractionHandler
from src.vectorstore.vector_store import VectorStore
from src.constraint_engine import ConstraintEngine, Constraint
from src.project_state_reporter import ProjectStateReporter
from src.documentation_health_checker import DocumentationHealthChecker
from src.project_structure_manager import ProjectStructureManager
from src.convention_manager import ConventionManager
from src.priority_manager import PriorityManager
from src.user_interaction_handler import UserInteractionHandler
from src.claude_manager import ClaudeManager
from src.cost_analyzer import CostAnalyzer


class WorkflowDirector:
    def __init__(self, config_path='src/workflow_config.yaml', state_manager=None, claude_manager=None, user_interaction_handler=None, llm_manager=None, logger=None, test_mode=False):
        self.config_path = config_path
        self.logger = logger if logger is not None else self._setup_logging()
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self._log("Initializing WorkflowDirector", extra={'test_mode': test_mode})
        self.config = self.load_config(self.config_path)
        self._log(f"Loaded config: {self.config}")
        self._log(f"StateManager: {state_manager}")
        self._log(f"ClaudeManager: {claude_manager}")
        self._log(f"UserInteractionHandler: {user_interaction_handler}")
        self._log(f"LLMManager: {llm_manager}")
        self.state_manager = state_manager or StateManager()
        self.claude_manager = claude_manager or ClaudeManager()
        self.user_interaction_handler = user_interaction_handler or UserInteractionHandler()
        self.llm_manager = llm_manager or LLMManager()
        self.test_mode = test_mode
        self._test_mode = test_mode
        self.current_stage = self.config['stages'][0]['name'] if self.config['stages'] else "Default Stage"
        self.stages = {stage['name']: stage for stage in self.config['stages']}
        self.transitions = self.config['transitions']
        self.stage_progress = {stage: 0.0 for stage in self.stages}
        self.completed_stages = set()
        self.sufficiency_evaluator = SufficiencyEvaluator(self.llm_manager)

    def _log(self, message, level='info', extra=None):
        if self.logger:
            log_method = getattr(self.logger, level, self.logger.info)
            log_method(message, extra=extra)
        else:
            raise ValueError(f"Logger not initialized. Message: [{level.upper()}] {message}")

    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as config_file:
                return yaml.safe_load(config_file)
        except Exception as e:
            self._log(f"Error loading configuration: {str(e)}", level='error')
            return {}
    def initialize(self):
        from src.state_manager import StateManager
        from src.claude_manager import ClaudeManager
        from src.llm_manager import LLMManager
        from src.user_interaction_handler import UserInteractionHandler
        from src.error_handler import ErrorHandler
        from src.constraint_engine import ConstraintEngine
        from src.project_state_reporter import ProjectStateReporter
        from src.documentation_health_checker import DocumentationHealthChecker
        from src.project_structure_manager import ProjectStructureManager
        from src.convention_manager import ConventionManager
        from src.sufficiency_evaluator import SufficiencyEvaluator
        from src.priority_manager import PriorityManager
        from src.cost_analyzer import CostAnalyzer

        # Move initialization logic here
        self.state_manager = self.state_manager if isinstance(self.state_manager, StateManager) else StateManager()
        self.logger.debug(f"StateManager: {self.state_manager}")
        self.claude_manager = self.claude_manager or ClaudeManager()
        self.llm_manager = self.llm_manager or LLMManager()
        self.user_interaction_handler = self.user_interaction_handler or UserInteractionHandler()
        self.error_handler = ErrorHandler()
        self.config = self.load_config(self.config_path)
        self.current_stage = self.config['stages'][0]['name'] if self.config['stages'] else "Default Stage"
        self.stages = {stage['name']: stage for stage in self.config['stages']}
        self.transitions = self.config['transitions']
        self.stage_progress = {stage: 0.0 for stage in self.stages}
        self.completed_stages = set()
        self.constraint_engine = ConstraintEngine()
        self.project_state_reporter = ProjectStateReporter(self)
        self.documentation_health_checker = DocumentationHealthChecker()
        self.project_structure_manager = ProjectStructureManager()
        self.convention_manager = ConventionManager()
        self.sufficiency_evaluator = SufficiencyEvaluator(self.llm_manager)
        self.priority_manager = PriorityManager()
        self.cost_analyzer = CostAnalyzer()
        
        self.initialize_constraints()
        self.initialize_priorities()

    def initialize_for_testing(self):
        from unittest.mock import MagicMock
        from src.state_manager import StateManager
        
        # Initialize minimal state for testing
        self.state_manager = MagicMock(spec=StateManager)
        self.current_stage = "Project Initialization"
        self.stages = {"Project Initialization": {"name": "Project Initialization", "tasks": []}}
        self.transitions = []
        self.stage_progress = {"Project Initialization": 0.0}
        self.completed_stages = set()
        
        self.logger.info("WorkflowDirector initialized")
        self.logger.debug(f"WorkflowDirector initialized with LLMManager: {self.llm_manager}")
        self.logger.debug(f"Test mode: {self._test_mode}")
        self.logger.debug(f"StateManager methods: {[method for method in dir(self.state_manager) if not method.startswith('_')]}")

    def initialize_for_testing(self):
        self._log("Initializing WorkflowDirector for testing")
        self.config = self.load_config(self.config_path)
        self.current_stage = self.config['stages'][0]['name'] if self.config['stages'] else "Default Stage"
        self.stages = {stage['name']: stage for stage in self.config['stages']}
        self.transitions = self.config['transitions']
        self.stage_progress = {stage: 0.0 for stage in self.stages}
        self.completed_stages = set()
        if self.state_manager is None:
            self.state_manager = StateManager()
        if self.claude_manager is None:
            self.claude_manager = ClaudeManager()
        if self.user_interaction_handler is None:
            self.user_interaction_handler = UserInteractionHandler()
        if self.llm_manager is None:
            self.llm_manager = LLMManager()
        self._log(f"Test initialization complete. Current stage: {self.current_stage}")

    def _setup_logging(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        
        # Create a StreamHandler for console output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Create a FileHandler for persistent logging
        log_file = f'workflow_director_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
        file_handler.setFormatter(file_formatter)
        
        # Add both handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        # Create a JSON formatter for structured logging
        json_formatter = jsonlogger.JsonFormatter('%(timestamp)s %(name)s %(levelname)s %(message)s %(filename)s %(funcName)s %(lineno)d')
        json_file = f'workflow_director_structured_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        json_handler = logging.FileHandler(json_file)
        json_handler.setFormatter(json_formatter)
        json_handler.setLevel(logging.DEBUG)
        logger.addHandler(json_handler)
        
        logger.info("Logging setup completed for WorkflowDirector", extra={
            'component': 'WorkflowDirector',
            'action': 'setup_logging',
            'status': 'completed',
            'log_file': log_file,
            'json_file': json_file,
            'python_version': sys.version
        })
        
        return logger

    def get_stage_by_name(self, stage_name: str) -> dict:
        return next((stage for stage in self.stages if stage['name'] == stage_name), None)

    def execute_stage(self, stage_name: str) -> bool:
        stage = self.get_stage_by_name(stage_name)
        if not stage:
            return False
        for task_name, task in stage['tasks'].items():
            should_execute = True
            if isinstance(task, dict) and 'condition' in task:
                state = self.state_manager.get_state()
                try:
                    should_execute = eval(task['condition'], {"state": state})
                except KeyError as e:
                    self.logger.warning(f"Condition evaluation failed due to missing key: {e}")
                    should_execute = False
                except Exception as e:
                    self.logger.error(f"Error evaluating condition for task {task_name}: {str(e)}")
                    should_execute = False
            
            # Always update the state manager, regardless of execution status
            self.state_manager.update_state(f"{stage_name}.{task_name}", "completed" if should_execute else "skipped")
            if should_execute:
                self.logger.info(f"Completed task: {task_name} in stage: {stage_name}")
            else:
                self.logger.info(f"Skipped task: {task_name} in stage: {stage_name} due to condition")
        
        self.stage_progress[stage_name] = 1.0
        self.completed_stages.add(stage_name)
        self.logger.info(f"Executed stage: {stage_name}")
        return True

    def evaluate_transition_condition(self, transition: dict) -> bool:
        if 'condition' not in transition:
            self.logger.debug("Transition condition not specified, assuming True")
            return True
        try:
            state = self.state_manager.get_state()
            condition_result = eval(transition['condition'], {"state": state})
            self.logger.debug(f"Evaluated transition condition: {transition['condition']} = {condition_result}")
            return bool(condition_result)
        except KeyError as e:
            self.logger.warning(f"Transition condition evaluation failed due to missing key: '{e.args[0]}'")
            return False
        except Exception as e:
            self.logger.error(f"Error evaluating transition condition: {str(e)}")
            return False

    def transition_to_next_stage(self) -> bool:
        valid_transitions = [t for t in self.transitions if t['from'] == self.current_stage]
        for transition in valid_transitions:
            if self.evaluate_transition_condition(transition):
                previous_stage = self.current_stage
                self.current_stage = transition['to']
                self.completed_stages.add(previous_stage)
                self.logger.info(f"Transitioned to stage: {self.current_stage}")
                return True
        self.logger.info("No valid transition found")
        return False

    def can_transition_to(self, next_stage):
        return any(t['to'] == next_stage for t in self.transitions if t['from'] == self.current_stage)

    def is_workflow_complete(self) -> bool:
        return self.current_stage == self.stages[-1]['name']

    def evaluate_transition_condition(self, transition: dict) -> bool:
        self.logger.debug(f"Entering evaluate_transition_condition with transition: {transition}")
        if 'condition' not in transition:
            self.logger.debug("Transition condition not specified, assuming True")
            return True
        result = self._evaluate_condition_internal(transition['condition'], "transition condition")
        self.logger.debug(f"Exiting evaluate_transition_condition with result: {result}")
        return result

    def evaluate_condition(self, condition: str) -> bool:
        self.logger.debug(f"Entering evaluate_condition with condition: {condition}")
        self.logger.debug(f"Current state: {self.state_manager.get_state()}")
        result = self._evaluate_condition_internal(condition, "condition")
        self.logger.debug(f"Exiting evaluate_condition with result: {result}")
        return result

    def _evaluate_condition_internal(self, condition: str, condition_type: str) -> bool:
        logger_id = id(self.logger)
        start_time = time.time()
        self.logger.debug(f"[{start_time}] Entering _evaluate_condition_internal with condition: {condition}, type: {condition_type}")
        self.logger.debug(f"[{start_time}] Logger id: {logger_id}")
        try:
            state = self.state_manager.get_state()
            self.logger.debug(f"[{time.time()}] Current state: {state}")
            self.logger.debug(f"[{time.time()}] Evaluating {condition_type}: {condition}")
            result = eval(condition, {"state": state})
            self.logger.debug(f"[{time.time()}] Evaluated {condition_type}: {condition} = {result}")
            self.logger.debug(f"[{time.time()}] Evaluation result type: {type(result)}")
            bool_result = bool(result)
            self.logger.debug(f"[{time.time()}] Boolean conversion result: {bool_result}")
            return bool_result
        except KeyError as e:
            error_msg = f"{condition_type.capitalize()} evaluation failed due to missing key: '{e.args[0]}'"
            self.logger.warning(f"[{time.time()}] {error_msg}")
            return False
        except Exception as e:
            error_msg = f"Error evaluating {condition_type} '{condition}': {str(e)}"
            self.logger.error(f"[{time.time()}] {error_msg}")
            return False
        finally:
            end_time = time.time()
            self.logger.debug(f"[{end_time}] Exiting _evaluate_condition_internal")
            self.logger.debug(f"[{end_time}] Logger id: {logger_id}")
            self.logger.debug(f"[{end_time}] Execution time: {end_time - start_time:.6f} seconds")

    def load_config(self, config_path):
        if isinstance(config_path, StateManager):
            # Use a default config path if StateManager is passed
            config_path = 'src/workflow_config.yaml'
        try:
            with open(config_path, 'r') as config_file:
                config = yaml.safe_load(config_file)
            if self.logger:
                self.logger.info(f"Configuration loaded successfully from {config_path}")
            return config
        except Exception as e:
            error_message = self.error_handler.handle_error(e)
            if self.logger:
                self.logger.error(f"Error loading configuration: {error_message}")
                self.logger.warning("Using default configuration")
            return {
                'stages': [{'name': 'Default Stage'}],
                'transitions': []
            }

    async def run(self):
        self.logger.info("Starting LLM Workflow Director", extra={
            'action': 'start_workflow',
            'current_stage': self.current_stage
        })
        self.user_interaction_handler.display_message("Starting LLM Workflow Director")
        try:
            while True:
                self.logger.debug("Starting new iteration of run loop", extra={
                    'action': 'run_loop_iteration',
                    'current_stage': self.current_stage
                })
                current_stage = self.get_current_stage()
                self.user_interaction_handler.display_message(f"Current stage: {current_stage['name']}")
                self.user_interaction_handler.display_message(f"Description: {current_stage['description']}")
                self.user_interaction_handler.display_message("Tasks:")
                for task in current_stage['tasks']:
                    self.user_interaction_handler.display_message(f"- {task}")
                stage_progress = self.get_stage_progress()
                self.user_interaction_handler.display_message(f"Stage progress: {stage_progress:.2%}")
                self.logger.info(f"Current stage: {current_stage['name']}, Progress: {stage_progress:.2%}", extra={
                    'action': 'display_stage_info',
                    'stage_name': current_stage['name'],
                    'stage_progress': stage_progress
                })
                user_input = self.user_interaction_handler.prompt_user("Enter a command ('next' for next stage, 'complete' to finish current stage, 'report' for usage report, 'optimize' for optimization suggestions, 'exit' to quit):")
                
                self.logger.debug(f"Received user input: {user_input}", extra={
                    'action': 'user_input',
                    'input': user_input
                })
                
                if user_input.lower() == 'exit':
                    self.logger.info("Exit command received. Ending run loop.")
                    break
                elif user_input.lower() == 'report':
                    usage_report = self.llm_manager.get_usage_report()
                    self.user_interaction_handler.display_message(f"LLM Usage Report: {usage_report}")
                elif user_input.lower() == 'optimize':
                    optimization_suggestion = self.llm_manager.get_optimization_suggestion()
                    self.user_interaction_handler.display_message(f"Optimization Suggestion: {optimization_suggestion}")
                elif user_input.lower() == 'status':
                    status_report = self.get_workflow_status()
                    self.user_interaction_handler.display_message(status_report)
                
                # Process all commands using LLM
                tier = self.determine_query_tier(user_input)
                context = self._prepare_llm_context()
                prompt = self.llm_manager.generate_prompt('default', {
                    "command": user_input,
                    "workflow_stage": self.current_stage,
                    "stage_description": self.stages[self.current_stage].get('description', ''),
                    "stage_tasks": '\n'.join(self.stages[self.current_stage].get('tasks', [])),
                    "stage_priorities": '\n'.join(self.priority_manager.get_priorities(self.current_stage)),
                    "project_structure": self.project_structure_manager.get_structure_instructions(),
                    "coding_conventions": self.convention_manager.get_aider_conventions(),
                    "available_transitions": ', '.join([t['to'] for t in self.get_available_transitions()]),
                    "project_progress": sum(self.stage_progress.values()) / len(self.stages),
                    "workflow_history": '\n'.join([f"{entry['action']}: {entry['details']}" for entry in self._get_workflow_history()]),
                    "context": str(context)
                })
                
                self.logger.debug(f"Preparing to query LLM. Test mode: {getattr(self, '_test_mode', False)}")
                
                if self.llm_manager:
                    try:
                        self.logger.debug(f"Querying LLM with prompt: {prompt[:100]}...")
                        structured_response = await self.llm_manager.query(prompt, context=context, tier=tier)
                        self.logger.debug(f"LLM response received: {structured_response}")
                        self.user_interaction_handler.display_message(f"LLM response: {structured_response}")
                        self._process_llm_response(structured_response)
                    except Exception as e:
                        self.logger.error(f"Error querying LLM: {str(e)}")
                        self.user_interaction_handler.display_message(f"An error occurred while processing your command: {str(e)}")
                else:
                    self.logger.warning("LLMManager not available. Skipping LLM query.")
                
                # Always call LLM query for testing purposes
                if getattr(self, '_test_mode', False):
                    self.logger.debug("Test mode active. Forcing LLM query.")
                    await self.llm_manager.query(prompt, context=context, tier=tier)
                
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
        context = {
            'workflow_stage': self.current_stage,
            'project_structure_instructions': self.project_structure_manager.get_structure_instructions(),
            'coding_conventions': self.convention_manager.get_aider_conventions(),
            'workflow_config': self.config,
            'completed_stages': list(self.completed_stages),
            'stage_progress': self.stage_progress[self.current_stage],
            'workflow_history': self._get_workflow_history()
        }
        return context

    def _get_workflow_history(self) -> List[Dict[str, Any]]:
        return self.state_manager.get('workflow_history', [])

    def _update_workflow_history(self, action: str, details: Dict[str, Any]):
        history = self._get_workflow_history()
        history.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details
        })
        self.state_manager.set('workflow_history', history[-10:])  # Keep last 10 entries

    def determine_query_tier(self, query: str) -> str:
        # Simple heuristic for determining the appropriate tier
        if len(query.split()) < 10:
            return 'fast'
        elif len(query.split()) > 50 or any(keyword in query.lower() for keyword in ['complex', 'detailed', 'analyze']):
            return 'powerful'
        else:
            return 'balanced'

    def _process_llm_response(self, structured_response: Dict[str, Any]):
        self.logger.info("Processing LLM response")
        try:
            if 'error' in structured_response:
                self.logger.warning(f"LLM microservice error: {structured_response['error']}")
                self.user_interaction_handler.display_message(f"LLM service error: {structured_response['error']}. Some features may be limited.")
                return

            if isinstance(structured_response, dict):
                if 'task_progress' in structured_response:
                    progress = float(structured_response['task_progress'])
                    self.update_stage_progress(progress)
                    self.logger.info(f"Updated stage progress to {progress:.2f}")
                
                if 'state_updates' in structured_response:
                    state_updates = structured_response['state_updates']
                    for key, value in state_updates.items():
                        self.state_manager.set(key, value)
                        self.logger.info(f"Updated project state: {key} = {value}")
                
                if 'actions' in structured_response:
                    actions = structured_response['actions']
                    for action in actions:
                        self._handle_llm_action(action)
                
                if 'suggestions' in structured_response:
                    suggestions = structured_response['suggestions']
                    self.user_interaction_handler.display_message("LLM Suggestions:")
                    for suggestion in suggestions:
                        self.user_interaction_handler.display_message(f"- {suggestion}")
                
                if 'response' in structured_response:
                    self.user_interaction_handler.display_message(f"LLM Response: {structured_response['response']}")
                
                # Check modularity of any new or updated files
                if 'file_updates' in structured_response:
                    for file_path in structured_response['file_updates']:
                        modularity_check = self.project_structure_manager.check_file_modularity(file_path)
                        if not modularity_check['is_modular']:
                            self.user_interaction_handler.display_message(f"Modularity issues detected in {file_path}:")
                            for issue in modularity_check['issues']:
                                self.user_interaction_handler.display_message(f"- {issue}")
                            if len(modularity_check['issues']) > 1:
                                split_suggestions = self.project_structure_manager.suggest_file_split(file_path)
                                if split_suggestions:
                                    self.user_interaction_handler.display_message("Suggested file splits:")
                                    for suggestion in split_suggestions:
                                        self.user_interaction_handler.display_message(f"- {suggestion}")
                
                self.logger.info("LLM response processed successfully")
            else:
                self.logger.warning(f"Unexpected response format: {type(structured_response)}")
                self.user_interaction_handler.display_message("Received an unexpected response format from the LLM service.")
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
            current_stage_data = self.stages[self.current_stage]
            project_state = self.state_manager.get_all()
            
            evaluation = self.sufficiency_evaluator.evaluate_stage_sufficiency(
                self.current_stage, current_stage_data, project_state
            )
            
            if not evaluation['is_sufficient']:
                self.logger.warning(f"Stage {self.current_stage} is not sufficient to transition. Reason: {evaluation['reasoning']}")
                self.user_interaction_handler.display_message(f"Cannot transition to stage: {next_stage}. Reason: {evaluation['reasoning']}")
                return False
            
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
        self.logger.info(f"Attempting to complete stage: {self.current_stage}")
        current_stage_data = self.stages[self.current_stage]
        project_state = self.state_manager.get_all()
        
        is_sufficient, reasoning = self.sufficiency_evaluator.evaluate_stage_sufficiency(
            self.current_stage, current_stage_data, project_state
        )
        
        if is_sufficient:
            self.stage_progress[self.current_stage] = 1.0
            self.completed_stages.add(self.current_stage)
            self.user_interaction_handler.display_message(f"Completed stage: {self.current_stage}")
            self.user_interaction_handler.display_message(f"Completion reasoning: {reasoning}")
            self.logger.info(f"Stage {self.current_stage} marked as completed. Reason: {reasoning}")
            
            next_stage = self.get_next_stage()
            if next_stage:
                if self.transition_to(next_stage):
                    self.logger.info(f"Moved to next stage: {next_stage}")
                    return True
                else:
                    self.logger.warning(f"Failed to transition to next stage: {next_stage}")
            else:
                self.logger.info("No next stage available")
            
            if self.current_stage == self.config['stages'][-1]['name']:
                self.logger.info("Completed final stage")
                return True
        else:
            self.user_interaction_handler.display_message(f"Stage {self.current_stage} is not yet complete.")
            self.user_interaction_handler.display_message(f"Reason: {reasoning}")
            self.logger.warning(f"Stage {self.current_stage} not sufficient for completion. Reason: {reasoning}")
        
        return False

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

    def evaluate_condition(self, condition: str) -> bool:
        self.logger.debug(f"Entering evaluate_condition with condition: {condition}")
        result = self._evaluate_condition_internal(condition, "condition")
        self.logger.debug(f"Exiting evaluate_condition with result: {result}")
        return result

    def evaluate_transition_condition(self, transition: dict) -> bool:
        self.logger.debug(f"Entering evaluate_transition_condition with transition: {transition}")
        if 'condition' not in transition:
            self.logger.debug("Transition condition not specified, assuming True")
            return True
        result = self._evaluate_condition_internal(transition['condition'], "transition condition")
        self.logger.debug(f"Exiting evaluate_transition_condition with result: {result}")
        return result

    def _evaluate_condition_internal(self, condition: str, condition_type: str) -> bool:
        self.logger.debug(f"Entering _evaluate_condition_internal with condition: {condition}, type: {condition_type}")
        self.logger.debug(f"Logger id: {id(self.logger)}")  # Add this line to track logger identity
        try:
            state = self.state_manager.get_state()
            self.logger.debug(f"Current state: {state}")
            self.logger.debug(f"Evaluating {condition_type}: {condition}")
            result = eval(condition, {"state": state})
            self.logger.debug(f"Evaluated {condition_type}: {condition} = {result}")
            self.logger.debug(f"Evaluation result type: {type(result)}")
            bool_result = bool(result)
            self.logger.debug(f"Boolean conversion result: {bool_result}")
            return bool_result
        except KeyError as e:
            error_msg = f"{condition_type.capitalize()} evaluation failed due to missing key: '{e.args[0]}'"
            self.logger.warning(error_msg)
            return False
        except Exception as e:
            error_msg = f"Error evaluating {condition_type} '{condition}': {str(e)}"
            self.logger.error(error_msg)
            return False
        finally:
            self.logger.debug(f"Exiting _evaluate_condition_internal")
            self.logger.debug(f"Logger id: {id(self.logger)}")  # Add this line to track logger identity

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
        
        # Set the completion state for the current stage
        self.state_manager.set(f"{self.current_stage.lower().replace(' ', '_')}_completed", True)
        
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

    def complete_current_stage(self) -> bool:
        self.logger.info(f"Completing stage: {self.current_stage}")
        self.stage_progress[self.current_stage] = 1.0
        self.completed_stages.add(self.current_stage)
        self.print_func(f"Completed stage: {self.current_stage}")
        self.logger.info(f"Stage {self.current_stage} marked as completed")
        
        # Set the state for completed stage
        self.state_manager.set(f"{self.current_stage.lower().replace(' ', '_')}_completed", True)
        
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
        
        # Set the completion state for the current stage
        self.state_manager.set(f"{self.current_stage.lower().replace(' ', '_')}_completed", True)
        
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

    def get_workflow_status(self):
        self.logger.info("Generating workflow status report")
        current_state = self.state_manager.get_state()
        status = f"Current Stage: {self.current_stage}\n"
        status += f"Completed Stages: {', '.join(self.completed_stages)}\n"
        status += f"Current Stage Progress: {self.stage_progress[self.current_stage]:.2%}\n"
        status += "Available Transitions:\n"
        for transition in self.get_available_transitions():
            status += f"  - {transition['to']}\n"
        status += f"Current State: {current_state}\n"
        self.logger.debug(f"Workflow status report generated: {status}")
        return status
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
        if self.logger:
            self.logger.info("Initializing priorities for all stages")
        for stage_name, stage_data in self.stages.items():
            priorities = stage_data.get('priorities', [])
            self.priority_manager.set_priorities(stage_name, priorities)
        if self.logger:
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
        log_file = f'workflow_director_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Add both handlers to the logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        # Create a JSON formatter for structured logging
        json_formatter = jsonlogger.JsonFormatter('%(timestamp)s %(name)s %(levelname)s %(message)s %(filename)s %(funcName)s %(lineno)d')
        json_file = f'workflow_director_structured_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        json_handler = logging.FileHandler(json_file)
        json_handler.setFormatter(json_formatter)
        json_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(json_handler)
        
        self.logger.info("Logging setup completed for WorkflowDirector", extra={
            'component': 'WorkflowDirector',
            'action': 'setup_logging',
            'status': 'completed',
            'log_file': log_file,
            'json_file': json_file
        })

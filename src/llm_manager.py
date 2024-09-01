import logging
import time
from typing import Dict, Any, Optional, List
from .error_handler import ErrorHandler
from .llm_microservice_client import LLMMicroserviceClient

class LLMManager:
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.client = LLMMicroserviceClient()

    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None, tier: str = 'balanced') -> Dict[str, Any]:
        self.logger.debug(f"Querying LLM with prompt: {prompt[:50]}... (tier: {tier})")
        cache_key = self._generate_cache_key(prompt, context, tier)
        if cache_key in self.cache:
            self.logger.info(f"Using cached response for prompt: {prompt[:50]}... (tier: {tier})")
            return self.cache[cache_key]

        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                enhanced_prompt = self._enhance_prompt(prompt, context)
                response = self.client.query(enhanced_prompt, context, tier)
                self.logger.debug(f"Received response from LLM: {response[:50]}...")
                structured_response = self._parse_structured_response(response)
                response_with_id = self._add_unique_id(structured_response)
                self.cache[cache_key] = response_with_id
                return response_with_id
            except Exception as e:
                retry_count += 1
                self.logger.warning(f"Error querying LLM microservice (attempt {retry_count}/{max_retries}): {str(e)} (tier: {tier})")
                if retry_count == max_retries:
                    self.logger.error(f"Max retries reached. Returning error message.")
                    return {"error": f"Error querying LLM after {max_retries} attempts: {str(e)}"}
        
        # This line should never be reached, but we'll add it for completeness
        return {"error": "Unexpected error in LLM query"}

    def _structure_response(self, response: str) -> str:
        # This is a placeholder implementation. In a real-world scenario,
        # you would implement more sophisticated response structuring logic.
        structured_response = "task_progress: 0.5\n"
        structured_response += "state_updates: {'key': 'value'}\n"
        structured_response += "actions: update_workflow, run_tests\n"
        structured_response += "suggestions: Review code, Update documentation\n"
        structured_response += f"response: {response}"
        return structured_response

    def _enhance_prompt(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        if context is None:
            return prompt

        workflow_stage = context.get('workflow_stage', 'Unknown')
        stage_description = context.get('stage_description', 'No description available')
        stage_tasks = context.get('stage_tasks', [])
        project_structure = context.get('project_structure_instructions', '')
        coding_conventions = context.get('coding_conventions', '')
        workflow_config = context.get('workflow_config', {})

        enhanced_prompt = f"""
        Current Workflow Stage: {workflow_stage}
        Stage Description: {stage_description}
        Stage Tasks:
        {' '.join(f'- {task}' for task in stage_tasks)}

        Project Structure:
        {project_structure}

        Coding Conventions:
        {coding_conventions}

        Workflow Configuration:
        Stages: {', '.join(stage['name'] for stage in workflow_config.get('stages', []))}
        Transitions: {', '.join(f"{t['from']} -> {t['to']}" for t in workflow_config.get('transitions', []))}

        Given the above context, please respond to the following prompt:

        {prompt}
        """
        self.logger.debug(f"Enhanced prompt generated: {enhanced_prompt[:100]}...")
        return enhanced_prompt

    def _handle_llm_error(self, prompt: str, context: Optional[Dict[str, Any]], tier: str, error_message: str) -> str:
        retry_count = 0
        max_retries = 3
        while retry_count < max_retries:
            try:
                self.logger.info(f"Retrying LLM query (attempt {retry_count + 1}/{max_retries})")
                response = self.client.query(prompt, context, tier)
                self.logger.info(f"Retry successful on attempt {retry_count + 1}")
                return response
            except Exception as retry_e:
                retry_count += 1
                self.logger.error(f"Retry {retry_count} failed: {str(retry_e)}")
        self.logger.critical(f"All retries failed for LLM query. Last error: {error_message}")
        return f"Error querying LLM after {max_retries} attempts: {error_message}"

    def _generate_cache_key(self, prompt: str, context: Optional[Dict[str, Any]] = None, tier: str = 'balanced') -> str:
        if context is None:
            context = {}
        context_str = ','.join(f"{k}:{v}" for k, v in sorted(context.items()))
        return f"{prompt}|{context_str}|{tier}"

    def _add_unique_id(self, response: Dict[str, Any]) -> Dict[str, Any]:
        unique_id = str(hash(str(response) + str(time.time())))
        response['id'] = f"(ID: {unique_id})"
        return response

    def evaluate_sufficiency(self, stage_name: str, stage_data: Dict[str, Any], project_state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Evaluating sufficiency for stage: {stage_name}")
        try:
            result = self.client.evaluate_sufficiency(stage_name, stage_data, project_state)
            self.logger.debug(f"Sufficiency evaluation result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error evaluating sufficiency: {str(e)}")
            return {"is_sufficient": False, "reasoning": f"Error evaluating sufficiency: {str(e)}"}

    def clear_cache(self):
        self.cache.clear()
        self.logger.info("LLM response cache cleared.")

    def evaluate_sufficiency(self, stage_name: str, stage_data: Dict[str, Any], project_state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Evaluating sufficiency for stage: {stage_name}")
        try:
            result = self.client.evaluate_sufficiency(stage_name, stage_data, project_state)
            self.logger.debug(f"Sufficiency evaluation result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error evaluating sufficiency: {str(e)}")
            return {"is_sufficient": False, "reasoning": f"Error evaluating sufficiency: {str(e)}"}

    def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        try:
            structured_response = {}
            current_key = None
            current_value = []

            for line in response.split('\n'):
                line = line.strip()
                if ':' in line and not line.startswith(' '):
                    if current_key:
                        structured_response[current_key] = self._process_value(current_key, current_value)
                    current_key = line.split(':', 1)[0].strip().lower()
                    current_value = [line.split(':', 1)[1].strip()]
                elif current_key:
                    current_value.append(line)

            if current_key:
                structured_response[current_key] = self._process_value(current_key, current_value)

            if not structured_response:
                return {"response": response}

            # If there's only a 'response' key, return it directly
            if len(structured_response) == 1 and 'response' in structured_response:
                return {"response": structured_response['response']}

            return structured_response
        except Exception as e:
            self.logger.error(f"Error parsing structured response: {str(e)}")
            return {"error": str(e), "raw_response": response}

    def _process_value(self, key: str, value: List[str]) -> Any:
        joined_value = ' '.join(value).strip()
        try:
            if key == 'task_progress':
                return float(joined_value)
            elif key == 'state_updates':
                return eval(joined_value)
            elif key in ['actions', 'suggestions']:
                return [item.strip() for item in joined_value.split(',')]
            else:
                return joined_value
        except Exception as e:
            self.logger.error(f"Error processing value for key '{key}': {str(e)}")
            return joined_value

    def evaluate_sufficiency(self, stage_name: str, stage_data: Dict[str, Any], project_state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Evaluating sufficiency for stage: {stage_name}")
        try:
            result = self.client.evaluate_sufficiency(stage_name, stage_data, project_state)
            self.logger.debug(f"Sufficiency evaluation result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error evaluating sufficiency: {str(e)}")
            return {"is_sufficient": False, "reasoning": f"Error evaluating sufficiency: {str(e)}"}

    def generate_prompt(self, template: str, context: Dict[str, Any]) -> str:
        self.logger.debug(f"Generating prompt with template: {template[:50]}...")
        try:
            enhanced_context = self._enhance_context(context)
            prompt = template.format(**enhanced_context)
            self.logger.debug(f"Generated prompt: {prompt[:50]}...")
            return prompt
        except KeyError as e:
            self.logger.error(f"Error generating prompt: Missing key {str(e)}", exc_info=True)
            return f"Error generating prompt: Missing key {str(e)}"
        except Exception as e:
            self.logger.error(f"Unexpected error generating prompt: {str(e)}", exc_info=True)
            return f"Unexpected error generating prompt: {str(e)}"

    def _enhance_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        enhanced_context = context.copy()
        workflow_config = enhanced_context.get('workflow_config', {})
        current_stage = enhanced_context.get('workflow_stage')
        
        if current_stage and 'stages' in workflow_config:
            stage_info = next((s for s in workflow_config['stages'] if s['name'] == current_stage), None)
            if stage_info:
                enhanced_context['stage_description'] = stage_info.get('description', '')
                enhanced_context['stage_tasks'] = stage_info.get('tasks', [])
                enhanced_context['stage_priorities'] = stage_info.get('priorities', [])

        enhanced_context['available_transitions'] = self._get_available_transitions(workflow_config, current_stage)
        enhanced_context['project_progress'] = self._calculate_project_progress(workflow_config, context)

        self.logger.debug(f"Enhanced context: {enhanced_context}")
        return enhanced_context

    def _get_available_transitions(self, workflow_config: Dict[str, Any], current_stage: str) -> List[str]:
        transitions = workflow_config.get('transitions', [])
        return [t['to'] for t in transitions if t['from'] == current_stage]

    def _calculate_project_progress(self, workflow_config: Dict[str, Any], context: Dict[str, Any]) -> float:
        total_stages = len(workflow_config.get('stages', []))
        completed_stages = len(context.get('completed_stages', []))
        return completed_stages / total_stages if total_stages > 0 else 0

    def _enhance_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        enhanced_context = context.copy()
        
        # Add workflow stage information
        if 'workflow_stage' in context:
            stage = context['workflow_stage']
            enhanced_context['stage_description'] = self._get_stage_description(stage)
            enhanced_context['stage_tasks'] = self._get_stage_tasks(stage)
        
        # Add project structure information
        if 'project_structure_instructions' in context:
            enhanced_context['project_structure'] = self._format_project_structure(context['project_structure_instructions'])
        
        # Add coding conventions
        if 'coding_conventions' in context:
            enhanced_context['formatted_conventions'] = self._format_coding_conventions(context['coding_conventions'])
        
        return enhanced_context

    def _get_stage_description(self, stage: str) -> str:
        # This method should retrieve the description of the given stage from the workflow configuration
        # For now, we'll return a placeholder
        return f"Description for stage: {stage}"

    def _get_stage_tasks(self, stage: str) -> List[str]:
        # This method should retrieve the tasks for the given stage from the workflow configuration
        # For now, we'll return a placeholder
        return [f"Task 1 for {stage}", f"Task 2 for {stage}"]

    def _format_project_structure(self, instructions: str) -> str:
        # Format the project structure instructions for better readability in the prompt
        return f"Project Structure:\n{instructions}"

    def _format_coding_conventions(self, conventions: str) -> str:
        # Format the coding conventions for better readability in the prompt
        return f"Coding Conventions:\n{conventions}"

    def _get_stage_tasks(self, stage: str) -> List[str]:
        # This method should retrieve the tasks for the given stage from the workflow configuration
        # For now, we'll return a placeholder
        return [f"Task 1 for {stage}", f"Task 2 for {stage}"]

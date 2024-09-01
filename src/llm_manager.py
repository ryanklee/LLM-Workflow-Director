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

    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None, tier: str = 'balanced') -> str:
        self.logger.debug(f"Querying LLM with prompt: {prompt[:50]}... (tier: {tier})")
        cache_key = self._generate_cache_key(prompt, context, tier)
        if cache_key in self.cache:
            self.logger.info(f"Using cached response for prompt: {prompt[:50]}... (tier: {tier})")
            return self.cache[cache_key]

        try:
            enhanced_prompt = self._enhance_prompt(prompt, context)
            response = self.client.query(enhanced_prompt, context, tier)
            self.logger.debug(f"Received response from LLM: {response[:50]}...")
        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Error querying LLM microservice: {error_message} (tier: {tier})")
            response = self._handle_llm_error(prompt, context, tier, error_message)

        response_with_id = self._add_unique_id(response)
        self.cache[cache_key] = response_with_id
        return response_with_id

    def _enhance_prompt(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        if context is None:
            return prompt

        workflow_stage = context.get('workflow_stage', 'Unknown')
        stage_description = context.get('stage_description', 'No description available')
        stage_tasks = context.get('stage_tasks', [])

        enhanced_prompt = f"""
        Current Workflow Stage: {workflow_stage}
        Stage Description: {stage_description}
        Stage Tasks:
        {' '.join(f'- {task}' for task in stage_tasks)}

        Given the above context, please respond to the following prompt:

        {prompt}
        """
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

    def _add_unique_id(self, response: str) -> str:
        return f"{response} (ID: {hash(response + str(time.time()))})"

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

    def generate_prompt(self, template: str, context: Dict[str, Any]) -> str:
        self.logger.debug(f"Generating prompt with template: {template[:50]}...")
        try:
            # Enhance the context with workflow-specific information
            enhanced_context = self._enhance_context(context)
            prompt = template.format(**enhanced_context)
            self.logger.debug(f"Generated prompt: {prompt[:50]}...")
            return prompt
        except KeyError as e:
            self.logger.error(f"Error generating prompt: Missing key {str(e)}")
            return f"Error generating prompt: Missing key {str(e)}"
        except Exception as e:
            self.logger.error(f"Unexpected error generating prompt: {str(e)}")
            return f"Unexpected error generating prompt: {str(e)}"

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

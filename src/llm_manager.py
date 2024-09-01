import logging
import time
from typing import Dict, Any, Optional
from .error_handler import ErrorHandler
from .llm_microservice_client import LLMMicroserviceClient

class LLMManager:
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.client = LLMMicroserviceClient()

    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None, tier: str = 'balanced') -> str:
        cache_key = self._generate_cache_key(prompt, context, tier)
        if cache_key in self.cache:
            self.logger.info(f"Using cached response for prompt: {prompt[:50]}... (tier: {tier})")
            return self.cache[cache_key]

        try:
            response = self.client.query(prompt, context, tier)
        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Error querying LLM microservice: {error_message} (tier: {tier})")
            response = self._handle_llm_error(prompt, context, tier, error_message)

        response_with_id = self._add_unique_id(response)
        self.cache[cache_key] = response_with_id
        return response_with_id

    def _handle_llm_error(self, prompt: str, context: Optional[Dict[str, Any]], tier: str, error_message: str) -> str:
        retry_count = 0
        max_retries = 3
        while retry_count < max_retries:
            try:
                self.logger.info(f"Retrying LLM query (attempt {retry_count + 1}/{max_retries})")
                response = self.client.query(prompt, context, tier)
                return response
            except Exception as retry_e:
                retry_count += 1
                self.logger.error(f"Retry {retry_count} failed: {str(retry_e)}")
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
        try:
            return self.client.evaluate_sufficiency(stage_name, stage_data, project_state)
        except Exception as e:
            self.logger.error(f"Error evaluating sufficiency: {str(e)}")
            return {"is_sufficient": False, "reasoning": f"Error evaluating sufficiency: {str(e)}"}

import importlib.util
import logging
import time
from typing import Dict, Any, Optional
from .error_handler import ErrorHandler

llm_spec = importlib.util.find_spec("llm")


class LLMManager:
    def __init__(self):
        self.mock_mode = True
        self.models = {}
        self.error_handler = ErrorHandler()
        self.logger = logging.getLogger(__name__)
        self.llm = None
        self.cache = {}

        if llm_spec is not None:
            try:
                self.llm = importlib.import_module("llm")
                self.mock_mode = False
                try:
                    available_models = self.llm.models
                    if available_models:
                        self.models = {
                            'fast': available_models[0],  # Fastest/cheapest model
                            'balanced': available_models[len(available_models)//2],  # Mid-range model
                            'powerful': available_models[-1]  # Most capable model
                        }
                        self.logger.info(f"Using LLM models: {', '.join([f'{k}: {v.name}' for k, v in self.models.items()])}")
                    else:
                        raise AttributeError("No models available")
                except AttributeError:
                    self.logger.warning("No models available. LLMManager will operate in mock mode.")
                    self.mock_mode = True
            except ImportError as e:
                self.logger.error(f"Error importing llm module. LLMManager will operate in mock mode. Error: {str(e)}")

        if self.mock_mode:
            self.logger.info("LLMManager is operating in mock mode.")

    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None, tier: str = 'balanced') -> str:
        cache_key = self._generate_cache_key(prompt, context, tier)
        if cache_key in self.cache:
            self.logger.info(f"Using cached response for prompt: {prompt[:50]}... (tier: {tier})")
            cached_response = self.cache[cache_key]
            return self._add_unique_id(cached_response)

        if self.mock_mode:
            response = f"Mock response to: {prompt} (tier: {tier})"
        else:
            try:
                formatted_prompt = self._format_prompt(prompt, context)
                self.logger.debug(f"Sending prompt to LLM: {formatted_prompt} (tier: {tier})")
                model = self.models.get(tier, self.models['balanced'])
                response = model.prompt(formatted_prompt)
                response = response.text()
            except Exception as e:
                error_message = str(e)
                self.logger.error(f"Error querying LLM: {error_message} (tier: {tier})")
                response = f"Error querying LLM: {error_message}"

        self.cache[cache_key] = response
        return self._add_unique_id(response)

    def _generate_cache_key(self, prompt: str, context: Optional[Dict[str, Any]] = None, tier: str = 'balanced') -> str:
        if context is None:
            context = {}
        context_str = ','.join(f"{k}:{v}" for k, v in sorted(context.items()))
        return f"{prompt}|{context_str}|{tier}"

    def _add_unique_id(self, response: str) -> str:
        return f"{response} (ID: {hash(response + str(time.time()))})"

    def _format_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        if context is None:
            context = {}

        project_structure_instructions = context.get('project_structure_instructions', '')
        coding_conventions = context.get('coding_conventions', '')
        
        formatted_prompt = f"Context:\n"
        for key, value in context.items():
            if key not in ['project_structure_instructions', 'coding_conventions']:
                formatted_prompt += f"{key}: {value}\n"
        
        formatted_prompt += f"\nProject Structure Instructions:\n{project_structure_instructions}\n"
        formatted_prompt += f"\nCoding Conventions:\n{coding_conventions}\n"
        formatted_prompt += f"\nPrompt: {prompt}"
        formatted_prompt += "\n\nPlease ensure that your response adheres to the project structure guidelines and coding conventions provided above."
        
        return formatted_prompt

    def _generate_cache_key(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        if context is None:
            context = {}
        context_str = ','.join(f"{k}:{v}" for k, v in sorted(context.items()))
        return f"{prompt}|{context_str}"

    def clear_cache(self):
        self.cache.clear()
        self.logger.info("LLM response cache cleared.")

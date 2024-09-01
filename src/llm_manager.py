import importlib.util
import logging
from typing import Dict, Any, Optional
from .error_handler import ErrorHandler

llm_spec = importlib.util.find_spec("llm")


class LLMManager:
    def __init__(self):
        self.mock_mode = True
        self.model = None
        self.error_handler = ErrorHandler()
        self.logger = logging.getLogger(__name__)
        self.llm = None
        self.cache = {}

        if llm_spec is not None:
            try:
                self.llm = importlib.import_module("llm")
                self.mock_mode = False
                try:
                    models = self.llm.models
                    if models:
                        self.model = models[0]  # Use the first available model
                        self.logger.info(f"Using LLM model: {self.model.name}")
                    else:
                        raise AttributeError("No models available")
                except AttributeError:
                    self.logger.warning("No models available. LLMManager will operate in mock mode.")
                    self.mock_mode = True
            except ImportError as e:
                self.logger.error(f"Error importing llm module. LLMManager will operate in mock mode. Error: {str(e)}")

        if self.mock_mode:
            self.logger.info("LLMManager is operating in mock mode.")

    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        cache_key = self._generate_cache_key(prompt, context)
        if cache_key in self.cache:
            self.logger.info(f"Using cached response for prompt: {prompt[:50]}...")
            return self.cache[cache_key]

        if self.mock_mode:
            response = f"Mock response to: {prompt}"
        else:
            try:
                formatted_prompt = self._format_prompt(prompt, context)
                self.logger.debug(f"Sending prompt to LLM: {formatted_prompt}")
                response = self.model.prompt(formatted_prompt)
                response = response.text()
            except Exception as e:
                error_message = str(e)
                self.logger.error(f"Error querying LLM: {error_message}")
                response = f"Error querying LLM: {error_message}"

        self.cache[cache_key] = response
        return response

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

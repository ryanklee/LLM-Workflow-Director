import importlib.util
import logging
from typing import Dict, Any
from .error_handler import ErrorHandler

llm_spec = importlib.util.find_spec("llm")


class LLMManager:
    def __init__(self):
        self.mock_mode = True
        self.model = None
        self.error_handler = ErrorHandler()
        self.logger = logging.getLogger(__name__)
        self.llm = None

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

    def query(self, prompt: str, context: Dict[str, Any] = None) -> str:
        if self.mock_mode:
            return f"Mock response to: {prompt}"
        try:
            formatted_prompt = self._format_prompt(prompt, context)
            self.logger.debug(f"Sending prompt to LLM: {formatted_prompt}")
            response = self.model.prompt(formatted_prompt)
            return response.text()
        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Error querying LLM: {error_message}")
            return f"Error querying LLM: {error_message}"

    def _format_prompt(self, prompt: str, context: Dict[str, Any] = None) -> str:
        if context is None:
            return prompt

        formatted_prompt = f"Context:\n"
        for key, value in context.items():
            formatted_prompt += f"{key}: {value}\n"
        formatted_prompt += f"\nPrompt: {prompt}"
        return formatted_prompt

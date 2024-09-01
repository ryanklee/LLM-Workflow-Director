import importlib
import logging
from .error_handler import ErrorHandler

llm_spec = importlib.util.find_spec("llm")

class LLMManager:
    def __init__(self):
        self.mock_mode = True
        self.model = None
        self.error_handler = ErrorHandler()
        self.logger = logging.getLogger(__name__)

        if llm_spec is not None:
            try:
                import llm
                self.mock_mode = False
                try:
                    self.model = llm.get_model()  # Use default model
                    self.logger.info(f"Using default LLM model: {self.model.name}")
                except llm.UnknownModelError:
                    self.logger.warning("Default model not available. LLMManager will operate in mock mode.")
                    self.mock_mode = True
            except ImportError as e:
                self.logger.error(f"Error importing llm module. LLMManager will operate in mock mode. Error: {str(e)}")

        if self.mock_mode:
            self.logger.info("LLMManager is operating in mock mode.")

    def query(self, prompt):
        if self.mock_mode:
            return f"Mock response to: {prompt}"
        try:
            response = self.model.prompt(prompt)
            return response.text()
        except Exception as e:
            error_message = self.error_handler.handle_error(e)
            self.logger.error(f"Error querying LLM: {error_message}")
            return f"Error querying LLM: {error_message}"
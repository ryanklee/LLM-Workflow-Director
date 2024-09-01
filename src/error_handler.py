import logging

class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def handle_error(self, error):
        error_type = type(error).__name__
        error_message = str(error)
        
        self.logger.error(f"Error occurred: {error_type} - {error_message}")
        
        if error_type == "ValueError":
            return "Invalid input provided. Please check your input and try again."
        elif error_type == "FileNotFoundError":
            return "Required file not found. Please ensure all necessary files are present."
        elif error_type == "ConnectionError":
            return "Unable to connect to the LLM service. Please check your internet connection and try again."
        else:
            return f"An unexpected error occurred: {error_message}. Please try again or contact support if the issue persists."

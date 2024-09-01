import llm

class LLMManager:
    def __init__(self):
        try:
            self.model = llm.get_model("gpt-3.5-turbo")  # Using "gpt-3.5-turbo" as a default model
        except llm.UnknownModelError:
            print("Warning: 'gpt-3.5-turbo' model not available. Using first available model.")
            models = llm.get_model_aliases()
            self.model = llm.get_model(next(iter(models)))

    def query(self, prompt):
        try:
            response = self.model.prompt(prompt)
            return response.text()
        except Exception as e:
            return f"Error querying LLM: {str(e)}"

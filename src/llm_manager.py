import llm

class LLMManager:
    def __init__(self):
        try:
            self.model = llm.get_model("gpt3")  # Using "gpt3" as a default model
        except llm.UnknownModelError:
            print("Warning: 'gpt3' model not available. Using first available model.")
            self.model = next(iter(llm.get_models().values()))

    def query(self, prompt):
        try:
            response = self.model.prompt(prompt)
            return response.text()
        except Exception as e:
            return f"Error querying LLM: {str(e)}"

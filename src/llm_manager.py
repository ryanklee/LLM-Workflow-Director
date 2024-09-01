import llm

class LLMManager:
    def __init__(self):
        self.model = llm.get_model("openai")

    def query(self, prompt):
        try:
            response = self.model.prompt(prompt)
            return response.text()
        except Exception as e:
            return f"Error querying LLM: {str(e)}"

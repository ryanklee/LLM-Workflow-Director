import importlib

llm = importlib.util.find_spec("llm")

class LLMManager:
    def __init__(self):
        if llm is None:
            print("Warning: llm module is not available. LLMManager will operate in mock mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
            import llm
            try:
                self.model = llm.get_model("claude-3-opus-20240229")  # Using Claude 3 Opus as the default model
            except llm.UnknownModelError:
                print("Warning: 'claude-3-opus-20240229' model not available. Trying other Claude models.")
                claude_models = ["claude-3-sonnet-20240229", "claude-2.1", "claude-2.0"]
                for model_name in claude_models:
                    try:
                        self.model = llm.get_model(model_name)
                        print(f"Using {model_name} model.")
                        break
                    except llm.UnknownModelError:
                        continue
                else:
                    raise ValueError("No Claude models available. Please install and configure a Claude model.")

    def query(self, prompt):
        if self.mock_mode:
            return f"Mock response to: {prompt}"
        try:
            response = self.model.prompt(prompt)
            return response.text()
        except Exception as e:
            return f"Error querying LLM: {str(e)}"

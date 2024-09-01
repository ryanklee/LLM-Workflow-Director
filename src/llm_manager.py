import importlib

llm_spec = importlib.util.find_spec("llm")

class LLMManager:
    def __init__(self):
        self.mock_mode = True
        self.model = None

        if llm_spec is not None:
            try:
                import llm
                self.mock_mode = False
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
                        print("Warning: No Claude models available. LLMManager will operate in mock mode.")
                        self.mock_mode = True
            except ImportError as e:
                print(f"Warning: Error importing llm module. LLMManager will operate in mock mode. Error: {str(e)}")

        if self.mock_mode:
            print("LLMManager is operating in mock mode.")

    def query(self, prompt):
        if self.mock_mode:
            return f"Mock response to: {prompt}"
        try:
            response = self.model.prompt(prompt)
            return response.text()
        except Exception as e:
            return f"Error querying LLM: {str(e)}"

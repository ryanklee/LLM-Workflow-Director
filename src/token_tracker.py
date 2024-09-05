from typing import Dict

class TokenTracker:
    def __init__(self):
        self.total_tokens: int = 0
        self.tokens_per_task: Dict[str, int] = {}

    def count_tokens(self, text: str) -> int:
        # This is a simplified token counting method.
        # In a real implementation, you'd use a proper tokenizer.
        return len(text.split())

    def add_tokens(self, task_id: str, input_text: str, output_text: str) -> None:
        input_tokens = self.count_tokens(input_text)
        output_tokens = self.count_tokens(output_text)
        total_tokens = input_tokens + output_tokens

        self.total_tokens += total_tokens
        self.tokens_per_task[task_id] = self.tokens_per_task.get(task_id, 0) + total_tokens

    def get_total_tokens(self) -> int:
        return self.total_tokens

    def get_tokens_for_task(self, task_id: str) -> int:
        return self.tokens_per_task.get(task_id, 0)

class TokenOptimizer:
    @staticmethod
    def optimize_prompt(prompt: str) -> str:
        # This is a placeholder for prompt optimization logic
        # In a real implementation, you'd have more sophisticated optimization strategies
        return prompt.strip()

    @staticmethod
    def truncate_response(response: str, max_tokens: int) -> str:
        tokens = response.split()
        if len(tokens) <= max_tokens:
            return response
        return ' '.join(tokens[:max_tokens])

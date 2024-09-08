from typing import Dict
from src.domain_models import TokenUsage, TokenUsagePolicy, TokenOptimizationPolicy

class TokenTracker(TokenUsagePolicy):
    def __init__(self):
        self.token_usage = TokenUsage(total_tokens=0, tokens_per_task={})

    def count_tokens(self, text: str) -> int:
        # This is a simplified token counting method.
        # In a real implementation, you'd use a proper tokenizer.
        return len(text.split())

    def add_tokens(self, task_id: str, input_text: str, output_text: str) -> None:
        input_tokens = self.count_tokens(input_text)
        output_tokens = self.count_tokens(output_text)
        total_tokens = input_tokens + output_tokens

        self.token_usage.total_tokens += total_tokens
        self.token_usage.tokens_per_task[task_id] = self.token_usage.tokens_per_task.get(task_id, 0) + total_tokens

    def get_total_tokens(self) -> int:
        return self.token_usage.total_tokens

    def get_tokens_for_task(self, task_id: str) -> int:
        return self.token_usage.tokens_per_task.get(task_id, 0)

class TokenOptimizer(TokenOptimizationPolicy):
    def optimize_prompt(self, prompt: str) -> str:
        # This is a placeholder for prompt optimization logic
        # In a real implementation, you'd have more sophisticated optimization strategies
        return prompt.strip()

    def truncate_response(self, response: str, max_tokens: int) -> str:
        tokens = response.split()
        if len(tokens) <= max_tokens:
            return response
        return ' '.join(tokens[:max_tokens])
import logging
import asyncio
from typing import Dict

class TokenTracker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.token_usage: Dict[str, int] = {}
        self.total_tokens = 0
        self.lock = asyncio.Lock()

    async def add_tokens(self, task_id: str, input_tokens: int, output_tokens: int):
        async with self.lock:
            total_tokens = input_tokens + output_tokens
            self.token_usage[task_id] = self.token_usage.get(task_id, 0) + total_tokens
            self.total_tokens += total_tokens
            self.logger.info(f"Added {total_tokens} tokens for task {task_id}. Total tokens: {self.total_tokens}")
        # Add this line to ensure the token usage is immediately available
        await self.get_token_usage(task_id)

    async def get_token_usage(self, task_id: str) -> int:
        async with self.lock:
            usage = self.token_usage.get(task_id, 0)
            self.logger.debug(f"Token usage for task {task_id}: {usage}")
            return usage

    async def get_total_token_usage(self) -> int:
        async with self.lock:
            self.logger.debug(f"Total token usage: {self.total_tokens}")
            return self.total_tokens

    async def reset(self):
        async with self.lock:
            self.token_usage.clear()
            self.total_tokens = 0
            self.logger.info("Token usage reset")

    async def count_tokens(self, text: str) -> int:
        # This is a simple approximation. For more accurate results, use a proper tokenizer.
        return len(text.split())

class TokenOptimizer:
    def __init__(self, token_tracker: TokenTracker):
        self.token_tracker = token_tracker
        self.logger = logging.getLogger(__name__)

    async def optimize_prompt(self, prompt: str) -> str:
        # Implement more sophisticated optimization logic here
        words = prompt.split()
        if len(words) > 100:
            return ' '.join(words[:100])
        return prompt

    async def truncate_response(self, response: str, max_tokens: int) -> str:
        tokens = response.split()
        if len(tokens) <= max_tokens:
            return response
        return ' '.join(tokens[:max_tokens])

class TokenOptimizer:
    def __init__(self, token_tracker: TokenTracker):
        self.token_tracker = token_tracker
        self.logger = logging.getLogger(__name__)

    async def suggest_optimization(self, task_id: str) -> str:
        task_tokens = await self.token_tracker.get_token_usage(task_id)
        total_tokens = await self.token_tracker.get_total_token_usage()
        
        if task_tokens > total_tokens * 0.2:  # If task uses more than 20% of total tokens
            return f"Consider optimizing task {task_id} to reduce token usage"
        elif task_tokens < 10:  # If task uses very few tokens
            return f"Task {task_id} uses very few tokens, consider combining with other tasks"
        else:
            return f"Token usage for task {task_id} seems reasonable"

    async def get_overall_efficiency(self) -> float:
        total_tokens = await self.token_tracker.get_total_token_usage()
        num_tasks = len(self.token_tracker.token_usage)
        if num_tasks == 0:
            return 0.0
        return total_tokens / num_tasks

    async def generate_report(self) -> str:
        report = "Token Usage Report:\n"
        report += f"Total Tokens Used: {await self.token_tracker.get_total_token_usage()}\n"
        report += f"Number of Tasks: {len(self.token_tracker.token_usage)}\n"
        report += f"Overall Efficiency: {await self.get_overall_efficiency():.2f} tokens per task\n"
        report += "\nTop 5 Token-Heavy Tasks:\n"
        
        sorted_tasks = sorted(self.token_tracker.token_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        for task_id, tokens in sorted_tasks:
            report += f"- Task {task_id}: {tokens} tokens\n"
        
        return report

    async def optimize_prompt(self, prompt: str) -> str:
        # Implement more sophisticated optimization logic here
        words = prompt.split()
        if len(words) > 100:
            return ' '.join(words[:100])
        return prompt
class TokenTracker:
    def __init__(self):
        self.token_usage = {}
        self.lock = asyncio.Lock()

    async def add_tokens(self, key, input_tokens, output_tokens):
        async with self.lock:
            self.token_usage[key] = self.token_usage.get(key, 0) + input_tokens + output_tokens

    async def get_token_usage(self, key):
        async with self.lock:
            return self.token_usage.get(key, 0)

    async def get_total_token_usage(self):
        async with self.lock:
            return sum(self.token_usage.values())

    async def count_tokens(self, text: str) -> int:
        # This is a simple approximation. For more accurate results, use a proper tokenizer.
        return len(text.split())

    async def reset(self):
        async with self.lock:
            self.token_usage.clear()

class TokenOptimizer:
    def __init__(self, token_tracker):
        self.token_tracker = token_tracker

    async def suggest_optimization(self, task):
        usage = await self.token_tracker.get_token_usage(task)
        if usage > 1000:
            return f"Consider optimizing task {task} to reduce token usage"
        return "No optimization needed"

    async def get_overall_efficiency(self):
        total_tokens = await self.token_tracker.get_total_token_usage()
        num_tasks = len(self.token_tracker.token_usage)
        if num_tasks == 0:
            return 0.0
        return total_tokens / num_tasks

    async def generate_report(self):
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

    async def truncate_response(self, response: str, max_tokens: int) -> str:
        tokens = response.split()
        if len(tokens) <= max_tokens:
            return response
        return ' '.join(tokens[:max_tokens])

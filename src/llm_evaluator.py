import anthropic

class LLMEvaluator:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def build_grader_prompt(self, answer, rubric):
        return f"""Grade this answer based on the rubric:
        <rubric>{rubric}</rubric>
        <answer>{answer}</answer>
        Think through your reasoning in <thinking> tags, then output 'correct' or 'incorrect' in <result> tags."""

    def evaluate_response(self, output, rubric):
        grader_response = self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2048,
            messages=[{"role": "user", "content": self.build_grader_prompt(output, rubric)}]
        ).content[0].text
        return "correct" in grader_response.lower()

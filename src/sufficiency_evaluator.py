import logging
from typing import Dict, Any, Tuple

class SufficiencyEvaluator:
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        self.logger = logging.getLogger(__name__)

    def evaluate_stage_sufficiency(self, stage_name: str, stage_data: Dict[str, Any], project_state: Dict[str, Any]) -> Tuple[bool, str]:
        self.logger.info(f"Evaluating sufficiency for stage: {stage_name}")
        
        prompt = self._generate_evaluation_prompt(stage_name, stage_data, project_state)
        response = self.llm_manager.query(prompt, context=project_state)
        
        is_sufficient, reasoning = self._parse_sufficiency_response(response)
        
        self.logger.info(f"Stage {stage_name} sufficiency evaluation result: {'Sufficient' if is_sufficient else 'Insufficient'}")
        self.logger.debug(f"Reasoning: {reasoning}")
        return is_sufficient, reasoning

    def _generate_evaluation_prompt(self, stage_name: str, stage_data: Dict[str, Any], project_state: Dict[str, Any]) -> str:
        prompt = f"""
        Evaluate the sufficiency of the current stage: {stage_name}

        Stage Description: {stage_data.get('description', 'No description provided')}

        Tasks:
        {self._format_tasks(stage_data.get('tasks', []))}

        Current Project State:
        {self._format_project_state(project_state)}

        Based on the stage description, tasks, and current project state, determine if this stage can be considered complete and sufficient to move to the next stage.

        Provide your evaluation in the following format:
        Evaluation: [SUFFICIENT/INSUFFICIENT]
        Reasoning: [Your detailed reasoning here]
        Next Steps: [If insufficient, provide specific steps to achieve sufficiency]
        """
        return prompt

    def _format_tasks(self, tasks: list) -> str:
        return '\n'.join(f"- {task}" for task in tasks)

    def _format_project_state(self, project_state: Dict[str, Any]) -> str:
        return '\n'.join(f"{key}: {value}" for key, value in project_state.items())

    def _parse_sufficiency_response(self, response: str) -> Tuple[bool, str]:
        if not response or not response.strip():
            self.logger.error("Empty or invalid sufficiency response")
            return False, "Empty or invalid response from LLM"

        try:
            lines = response.split('\n')
            evaluation_line = next((line for line in lines if line.startswith('Evaluation:')), None)
            reasoning_line = next((line for line in lines if line.startswith('Reasoning:')), None)
            next_steps_line = next((line for line in lines if line.startswith('Next Steps:')), None)

            if not evaluation_line or not reasoning_line:
                raise ValueError("Missing required Evaluation or Reasoning in response")

            evaluation = evaluation_line.split(':')[1].strip().upper()
            reasoning = reasoning_line.split(':')[1].strip()
            if next_steps_line:
                reasoning += f"\nNext Steps: {next_steps_line.split(':')[1].strip()}"

            is_sufficient = evaluation == 'SUFFICIENT'
            return is_sufficient, reasoning
        except Exception as e:
            self.logger.error(f"Error parsing sufficiency response: {str(e)}")
            return False, f"Error parsing response: {str(e)}"

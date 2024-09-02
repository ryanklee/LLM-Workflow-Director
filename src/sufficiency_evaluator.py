import logging
from typing import Dict, Any, Tuple, List

class SufficiencyEvaluator:
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        self.logger = logging.getLogger(__name__)

    def evaluate_stage_sufficiency(self, stage_name: str, stage_data: Dict[str, Any], project_state: Dict[str, Any]) -> Tuple[bool, str]:
        self.logger.info(f"Evaluating sufficiency for stage: {stage_name}")
        
        if not self.llm_manager:
            self.logger.warning("LLMManager not available. Assuming stage is sufficient.")
            return True, "LLMManager not available. Stage assumed to be sufficient."
        
        try:
            prompt = self._generate_sufficiency_prompt(stage_name, stage_data, project_state)
            response = self.llm_manager.query(prompt)
            
            is_sufficient, reasoning = self._parse_sufficiency_response(response)
            
            self.logger.info(f"Stage {stage_name} sufficiency evaluation result: {'Sufficient' if is_sufficient else 'Insufficient'}")
            self.logger.debug(f"Reasoning: {reasoning}")
            return is_sufficient, reasoning
        except Exception as e:
            self.logger.error(f"Error evaluating sufficiency: {str(e)}")
            return False, f"Error evaluating sufficiency: {str(e)}"

    def _generate_sufficiency_prompt(self, stage_name: str, stage_data: Dict[str, Any], project_state: Dict[str, Any]) -> str:
        return self.llm_manager.generate_prompt('sufficiency_evaluation', {
            "stage_name": stage_name,
            "stage_description": stage_data.get('description', 'No description provided'),
            "stage_tasks": self._format_tasks(stage_data.get('tasks', [])),
            "project_state": self._format_project_state(project_state),
            "workflow_history": '\n'.join([f"{entry['action']}: {entry['details']}" for entry in self.llm_manager._get_workflow_history()])
        })

    def _format_tasks(self, tasks: List[str]) -> str:
        return "\n".join(f"- {task}" for task in tasks)

    def _format_project_state(self, project_state: Dict[str, Any]) -> str:
        return "\n".join(f"{key}: {value}" for key, value in project_state.items())

    def _parse_sufficiency_response(self, response: str) -> Tuple[bool, str]:
        lines = response.strip().split('\n')
        evaluation = ""
        reasoning = ""
        next_steps = ""

        for line in lines:
            if line.startswith("Evaluation:"):
                evaluation = line.split(":", 1)[1].strip()
            elif line.startswith("Reasoning:"):
                reasoning = line.split(":", 1)[1].strip()
            elif line.startswith("Next Steps:"):
                next_steps = line.split(":", 1)[1].strip()

        is_sufficient = evaluation.upper() == "SUFFICIENT"
        full_reasoning = f"{reasoning}\n\nNext Steps: {next_steps}" if next_steps else reasoning

        return is_sufficient, full_reasoning
import logging
from typing import Dict, Any, Tuple

class SufficiencyEvaluator:
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        self.logger = logging.getLogger(__name__)

    def evaluate_stage_sufficiency(self, stage_name: str, stage_data: Dict[str, Any], project_state: Dict[str, Any]) -> Tuple[bool, str]:
        self.logger.info(f"Evaluating sufficiency for stage: {stage_name}")
        
        if not self.llm_manager:
            self.logger.warning("LLMManager not available. Assuming stage is sufficient.")
            return True, "LLMManager not available. Stage assumed to be sufficient."
        
        try:
            result = self.llm_manager.evaluate_sufficiency(stage_name, stage_data, project_state)
            is_sufficient = result.get('is_sufficient', False)
            reasoning = result.get('reasoning', 'No reasoning provided')
            
            self.logger.info(f"Stage {stage_name} sufficiency evaluation result: {'Sufficient' if is_sufficient else 'Insufficient'}")
            self.logger.debug(f"Reasoning: {reasoning}")
            return is_sufficient, reasoning
        except Exception as e:
            self.logger.error(f"Error evaluating sufficiency: {str(e)}")
            return False, f"Error evaluating sufficiency: {str(e)}"
from typing import Dict, Any
from .llm_manager import LLMManager

class SufficiencyEvaluator:
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager

    def evaluate_stage_sufficiency(self, stage_name: str, stage_data: Dict[str, Any], project_state: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Evaluate the sufficiency of a workflow stage using the LLM.
        
        :param stage_name: The name of the current stage
        :param stage_data: Data related to the current stage
        :param project_state: The current state of the project
        :return: A tuple containing a boolean indicating sufficiency and a string with reasoning
        """
        if not self.llm_manager:
            return True, "LLMManager not available. Stage assumed to be sufficient."
        
        try:
            evaluation = self.llm_manager.evaluate_sufficiency(stage_name, stage_data, project_state)
            return evaluation.get('is_sufficient', False), evaluation.get('reasoning', 'No reasoning provided')
        except Exception as e:
            return False, f"Error evaluating sufficiency: {str(e)}"

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

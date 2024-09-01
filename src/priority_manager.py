import logging
from typing import Dict, Any, List

class PriorityManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.priorities = {}

    def set_priorities(self, stage: str, priorities: List[str]):
        self.logger.info(f"Setting priorities for stage: {stage}")
        self.priorities[stage] = priorities

    def get_priorities(self, stage: str) -> List[str]:
        self.logger.debug(f"Getting priorities for stage: {stage}")
        return self.priorities.get(stage, [])

    def determine_priority(self, stage: str, task: str) -> int:
        priorities = self.get_priorities(stage)
        try:
            return priorities.index(task)
        except ValueError:
            self.logger.warning(f"Task '{task}' not found in priorities for stage '{stage}'")
            return len(priorities)  # Return lowest priority if task not found

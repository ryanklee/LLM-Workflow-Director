import logging
from typing import Dict, Any, List, Tuple, Callable

class Constraint:
    def __init__(self, name: str, description: str, validate: Callable[[Dict[str, Any]], Tuple[bool, str]]):
        self.name = name
        self.description = description
        self.validate = validate

class ConstraintEngine:
    def __init__(self):
        self.constraints: Dict[str, Constraint] = {}
        self.logger = logging.getLogger(__name__)

    def add_constraint(self, constraint: Constraint) -> None:
        if constraint.name in self.constraints:
            self.logger.warning(f"Constraint '{constraint.name}' already exists. Overwriting.")
        self.constraints[constraint.name] = constraint
        self.logger.info(f"Added constraint: {constraint.name}")

    def remove_constraint(self, name: str) -> None:
        if name in self.constraints:
            del self.constraints[name]
            self.logger.info(f"Removed constraint: {name}")
        else:
            self.logger.warning(f"Constraint '{name}' not found. Cannot remove.")

    def validate_all(self, state: Dict[str, Any]) -> Tuple[bool, List[str]]:
        self.logger.info("Validating all constraints")
        valid = True
        violations = []
        for name, constraint in self.constraints.items():
            is_valid, message = constraint.validate(state)
            if not is_valid:
                valid = False
                violations.append(f"{name}: {message}")
                self.logger.warning(f"Constraint violation: {name} - {message}")
        
        if valid:
            self.logger.info("All constraints passed")
        else:
            self.logger.warning(f"Constraint violations: {', '.join(violations)}")
        
        return valid, violations

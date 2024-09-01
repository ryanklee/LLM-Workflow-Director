import os
import yaml
import logging
from typing import Dict, List, Optional, Any

class ProjectStructureManager:
    def __init__(self, config_path: str = 'src/project_structure_config.yaml'):
        self.logger = logging.getLogger(__name__)
        self.config = self.load_config(config_path)
        self.root_dir = os.getcwd()

    def load_config(self, config_path: str) -> Dict:
        try:
            with open(config_path, 'r') as config_file:
                return yaml.safe_load(config_file)
        except Exception as e:
            self.logger.error(f"Error loading project structure configuration: {str(e)}")
            return {}

    def create_project_structure(self) -> None:
        self.logger.info("Creating project structure")
        for directory in self.config.get('directories', []):
            path = os.path.join(self.root_dir, directory)
            os.makedirs(path, exist_ok=True)
            self.logger.debug(f"Created directory: {path}")

        for file_path in self.config.get('files', []):
            path = os.path.join(self.root_dir, file_path)
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    f.write('')
                self.logger.debug(f"Created file: {path}")

    def verify_project_structure(self) -> List[str]:
        self.logger.info("Verifying project structure")
        missing_items = []
        for directory in self.config.get('directories', []):
            path = os.path.join(self.root_dir, directory)
            if not os.path.exists(path):
                missing_items.append(f"Directory: {directory}")

        for file_path in self.config.get('files', []):
            path = os.path.join(self.root_dir, file_path)
            if not os.path.exists(path):
                missing_items.append(f"File: {file_path}")

        return missing_items

    def get_placement_advice(self, file_type: str) -> Optional[str]:
        self.logger.info(f"Getting placement advice for file type: {file_type}")
        placement_rules = self.config.get('placement_rules', {})
        return placement_rules.get(file_type)

    def validate_file_placement(self, file_path: str) -> bool:
        self.logger.info(f"Validating file placement: {file_path}")
        file_type = os.path.splitext(file_path)[1][1:]  # Get file extension without the dot
        expected_location = self.get_placement_advice(file_type)
        if expected_location:
            return file_path.startswith(os.path.join(self.root_dir, expected_location))
        return True  # If no specific rule, assume it's valid

    def check_file_modularity(self, file_path: str) -> Dict[str, Any]:
        self.logger.info(f"Checking file modularity: {file_path}")
        with open(file_path, 'r') as file:
            content = file.read()
            lines = content.split('\n')
        
        modularity_issues = []
        if len(lines) > self.config['modularity_guidelines']['max_file_size']:
            modularity_issues.append(f"File exceeds maximum size of {self.config['modularity_guidelines']['max_file_size']} lines")
        
        # This is a placeholder for complexity calculation. In a real implementation,
        # you would use a proper complexity metric like McCabe complexity.
        if len(set(lines)) > self.config['modularity_guidelines']['max_complexity']:
            modularity_issues.append(f"File may exceed maximum complexity of {self.config['modularity_guidelines']['max_complexity']}")
        
        file_name = os.path.basename(file_path)
        if not file_name.islower() and '_' not in file_name:
            modularity_issues.append("File name does not follow snake_case convention")
        
        if self.config['modularity_guidelines']['file_purpose_comment']:
            if not content.lstrip().startswith('"""') and not content.lstrip().startswith("'''"):
                modularity_issues.append("File is missing a purpose comment at the top")
        
        return {
            "is_modular": len(modularity_issues) == 0,
            "issues": modularity_issues
        }

    def suggest_file_split(self, file_path: str) -> List[str]:
        self.logger.info(f"Suggesting file split for: {file_path}")
        # This is a placeholder implementation. In a real-world scenario,
        # you would implement more sophisticated logic to suggest meaningful splits.
        with open(file_path, 'r') as file:
            content = file.read()
            lines = content.split('\n')
        
        if len(lines) <= self.config['modularity_guidelines']['max_file_size']:
            return []
        
        suggested_splits = []
        current_line = 0
        while current_line < len(lines):
            end_line = min(current_line + self.config['modularity_guidelines']['max_file_size'], len(lines))
            suggested_splits.append(f"{file_path.rsplit('.', 1)[0]}_{len(suggested_splits)+1}.{file_path.rsplit('.', 1)[1]}")
            current_line = end_line
        
        return suggested_splits

    def get_structure_instructions(self) -> str:
        return (
            "Project Structure Instructions:\n"
            f"1. Create the following directories:\n   {', '.join(self.config.get('directories', []))}\n"
            f"2. Create the following files:\n   {', '.join(self.config.get('files', []))}\n"
            "3. Follow these placement rules for new files:\n" +
            '\n'.join([f"   - {k}: {v}" for k, v in self.config.get('placement_rules', {}).items()])
        )

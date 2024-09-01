import os
import yaml
import logging
from typing import Dict, List, Optional

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

    def get_structure_instructions(self) -> str:
        return (
            "Project Structure Instructions:\n"
            f"1. Create the following directories:\n   {', '.join(self.config.get('directories', []))}\n"
            f"2. Create the following files:\n   {', '.join(self.config.get('files', []))}\n"
            "3. Follow these placement rules for new files:\n" +
            '\n'.join([f"   - {k}: {v}" for k, v in self.config.get('placement_rules', {}).items()])
        )

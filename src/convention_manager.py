import yaml
import os

class ConventionManager:
    def __init__(self, config_path='src/coding_conventions.yaml'):
        self.config_path = config_path
        self.conventions = self.load_conventions()

    def load_conventions(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return self.get_default_conventions()

    def get_default_conventions(self):
        return {
            "code_style": {
                "indentation": "4 spaces",
                "max_line_length": 120,
                "naming_conventions": {
                    "classes": "PascalCase",
                    "functions": "snake_case",
                    "variables": "snake_case"
                }
            },
            "documentation": {
                "require_docstrings": True,
                "docstring_style": "Google"
            },
            "testing": {
                "require_unit_tests": True,
                "minimum_test_coverage": 80
            },
            "error_handling": {
                "prefer_specific_exceptions": True,
                "require_descriptive_error_messages": True
            },
            "ddd_tdd_principles": {
                "use_domain_specific_language": True,
                "write_tests_before_implementation": True
            },
            "project_structure": {
                "follow_defined_structure": True
            }
        }

    def generate_conventions_file(self, preview=False):
        conventions = yaml.dump(self.conventions, default_flow_style=False)
        if preview:
            return conventions
        else:
            with open(self.config_path, 'w') as f:
                f.write(conventions)
            return f"Conventions file generated at {self.config_path}"

    def get_aider_conventions(self):
        aider_conventions = [
            "Follow these coding conventions:",
            f"- Use {self.conventions['code_style']['indentation']} for indentation",
            f"- Maximum line length: {self.conventions['code_style']['max_line_length']} characters",
            f"- Use {self.conventions['code_style']['naming_conventions']['classes']} for class names",
            f"- Use {self.conventions['code_style']['naming_conventions']['functions']} for function names",
            f"- Use {self.conventions['code_style']['naming_conventions']['variables']} for variable names",
            f"- {'Require' if self.conventions['documentation']['require_docstrings'] else 'Do not require'} docstrings for all functions, classes, and modules",
            f"- Use {self.conventions['documentation']['docstring_style']} style for docstrings",
            f"- {'Require' if self.conventions['testing']['require_unit_tests'] else 'Do not require'} unit tests for all new functionality",
            f"- Aim for a minimum of {self.conventions['testing']['minimum_test_coverage']}% test coverage",
            "- Prefer specific exceptions over generic ones",
            "- Provide descriptive and actionable error messages",
            "- Use domain-specific language in code and comments",
            "- Write tests before implementing functionality",
            "- Follow the defined project structure"
        ]
        return "\n".join(aider_conventions)
import yaml
from typing import Dict, Any

class ConventionManager:
    def __init__(self):
        self.conventions = self.get_default_conventions()

    def get_default_conventions(self) -> Dict[str, Any]:
        return {
            "code_style": {
                "indentation": "4 spaces",
                "max_line_length": 120,
                "naming_conventions": {
                    "classes": "PascalCase",
                    "functions": "snake_case",
                    "variables": "snake_case"
                }
            },
            "documentation": {
                "require_docstrings": True,
                "docstring_style": "Google"
            },
            "testing": {
                "require_unit_tests": True,
                "minimum_test_coverage": 80
            },
            "error_handling": {
                "prefer_specific_exceptions": True,
                "require_descriptive_error_messages": True
            },
            "ddd_tdd_principles": {
                "use_domain_specific_language": True,
                "write_tests_before_implementation": True
            },
            "project_structure": {
                "follow_defined_structure": True
            }
        }

    def load_conventions(self, file_path: str):
        with open(file_path, 'r') as f:
            self.conventions = yaml.safe_load(f)

    def save_conventions(self, file_path: str):
        with open(file_path, 'w') as f:
            yaml.dump(self.conventions, f, default_flow_style=False)

    def get_aider_conventions(self) -> str:
        aider_conventions = [
            "Follow these coding conventions:",
            f"- Use {self.conventions['code_style']['indentation']} for indentation",
            f"- Maximum line length: {self.conventions['code_style']['max_line_length']} characters",
            f"- Use {self.conventions['code_style']['naming_conventions']['classes']} for class names",
            f"- Use {self.conventions['code_style']['naming_conventions']['functions']} for function names",
            f"- Use {self.conventions['code_style']['naming_conventions']['variables']} for variable names",
            f"- {'Require' if self.conventions['documentation']['require_docstrings'] else 'Do not require'} docstrings for all functions, classes, and modules",
            f"- Use {self.conventions['documentation']['docstring_style']} style for docstrings",
            f"- {'Require' if self.conventions['testing']['require_unit_tests'] else 'Do not require'} unit tests for all new functionality",
            f"- Aim for a minimum of {self.conventions['testing']['minimum_test_coverage']}% test coverage",
            "- Prefer specific exceptions over generic ones",
            "- Provide descriptive and actionable error messages",
            "- Use domain-specific language in code and comments",
            "- Write tests before implementing functionality",
            "- Follow the defined project structure"
        ]
        return "\n".join(aider_conventions)

    def generate_aider_conventions(self) -> str:
        aider_conventions = [
            "Follow these coding conventions:",
            f"- Use {self.conventions['code_style']['indentation']} for indentation",
            f"- Maximum line length: {self.conventions['code_style']['max_line_length']} characters",
            f"- Use {self.conventions['code_style']['naming_conventions']['classes']} for class names",
            f"- Use {self.conventions['code_style']['naming_conventions']['functions']} for function names",
            f"- Use {self.conventions['code_style']['naming_conventions']['variables']} for variable names",
            f"- {'Require' if self.conventions['documentation']['require_docstrings'] else 'Do not require'} docstrings for all functions, classes, and modules",
            f"- Use {self.conventions['documentation']['docstring_style']} style for docstrings",
            f"- {'Require' if self.conventions['testing']['require_unit_tests'] else 'Do not require'} unit tests for all new functionality",
            f"- Aim for a minimum of {self.conventions['testing']['minimum_test_coverage']}% test coverage",
            "- Prefer specific exceptions over generic ones",
            "- Provide descriptive and actionable error messages",
            "- Use domain-specific language in code and comments",
            "- Write tests before implementing functionality",
            "- Follow the defined project structure"
        ]
        return "\n".join(aider_conventions)
import yaml
from typing import Dict, Any

class ConventionManager:
    def __init__(self):
        self.conventions = self.get_default_conventions()

    def get_default_conventions(self) -> Dict[str, Any]:
        return {
            "code_style": {
                "indentation": "4 spaces",
                "max_line_length": 120,
                "naming_conventions": {
                    "classes": "PascalCase",
                    "functions": "snake_case",
                    "variables": "snake_case"
                }
            },
            "documentation": {
                "require_docstrings": True,
                "docstring_style": "Google"
            },
            "testing": {
                "require_unit_tests": True,
                "minimum_test_coverage": 80
            },
            "error_handling": {
                "prefer_specific_exceptions": True,
                "require_descriptive_error_messages": True
            },
            "ddd_tdd_principles": {
                "use_domain_specific_language": True,
                "write_tests_before_implementation": True
            },
            "project_structure": {
                "follow_defined_structure": True
            }
        }

    def load_conventions(self, file_path: str):
        with open(file_path, 'r') as f:
            self.conventions = yaml.safe_load(f)

    def save_conventions(self, file_path: str):
        with open(file_path, 'w') as f:
            yaml.dump(self.conventions, f, default_flow_style=False)

    def generate_aider_conventions(self) -> str:
        aider_conventions = [
            "Follow these coding conventions:",
            f"- Use {self.conventions['code_style']['indentation']} for indentation",
            f"- Maximum line length: {self.conventions['code_style']['max_line_length']} characters",
            f"- Use {self.conventions['code_style']['naming_conventions']['classes']} for class names",
            f"- Use {self.conventions['code_style']['naming_conventions']['functions']} for function names",
            f"- Use {self.conventions['code_style']['naming_conventions']['variables']} for variable names",
            f"- {'Require' if self.conventions['documentation']['require_docstrings'] else 'Do not require'} docstrings for all functions, classes, and modules",
            f"- Use {self.conventions['documentation']['docstring_style']} style for docstrings",
            f"- {'Require' if self.conventions['testing']['require_unit_tests'] else 'Do not require'} unit tests for all new functionality",
            f"- Aim for a minimum of {self.conventions['testing']['minimum_test_coverage']}% test coverage",
            "- Prefer specific exceptions over generic ones",
            "- Provide descriptive and actionable error messages",
            "- Use domain-specific language in code and comments",
            "- Write tests before implementing functionality",
            "- Follow the defined project structure"
        ]
        return "\n".join(aider_conventions)

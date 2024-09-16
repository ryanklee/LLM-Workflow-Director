# Poetry Migration Guide

## Overview
This document outlines the process for migrating the LLM-Workflow Director project from using requirements.txt to Poetry for dependency management.

## Steps

1. Install Poetry
   ```
   pip install poetry
   ```

2. Initialize Poetry in the project
   ```
   cd /path/to/project
   poetry init
   ```

3. Convert requirements.txt to pyproject.toml
   - Manually transfer dependencies from requirements.txt to pyproject.toml
   - Use the following format for each dependency:
     ```toml
     [tool.poetry.dependencies]
     python = "^3.10"
     dependency-name = "^version"
     ```

4. Add development dependencies
   ```toml
   [tool.poetry.dev-dependencies]
   pytest = "^6.2"
   black = "^21.9b0"
   flake8 = "^4.0"
   ```

5. Create dependency groups
   ```toml
   [tool.poetry.group.test]
   optional = true
   [tool.poetry.group.test.dependencies]
   pytest = "^6.2"

   [tool.poetry.group.dev]
   optional = true
   [tool.poetry.group.dev.dependencies]
   black = "^21.9b0"
   flake8 = "^4.0"
   ```

6. Generate lock file
   ```
   poetry lock
   ```

7. Install dependencies
   ```
   poetry install
   ```

8. Update CI/CD configuration
   - Replace pip install commands with poetry install
   - Use poetry run for running tests and other commands

9. Update documentation
   - Add instructions for setting up the project with Poetry
   - Update any existing pip-based instructions to use Poetry

10. Remove requirements.txt
    ```
    git rm requirements.txt
    ```

11. Commit changes
    ```
    git add pyproject.toml poetry.lock docs/poetry_migration.md
    git commit -m "Migrate to Poetry for dependency management"
    ```

## Best Practices

1. Use version ranges instead of exact versions when possible
2. Regularly update dependencies with `poetry update`
3. Use `poetry add` to add new dependencies
4. Use `poetry remove` to remove dependencies
5. Run `poetry check` before committing changes to ensure pyproject.toml is valid

## Troubleshooting

- If you encounter conflicts, try using `poetry update package-name` to update specific packages
- Use `poetry show --tree` to view the dependency tree and identify conflicts
- If a package is not found, check if it's available on PyPI or if you need to add a custom repository

Remember to test thoroughly after migration to ensure all dependencies are correctly installed and the project functions as expected.

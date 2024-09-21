# Getting Started with LLM-Workflow Director

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/llm-workflow-director.git
   cd llm-workflow-director
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install poetry
   poetry install
   ```

## Configuration

1. Copy the example configuration file:
   ```
   cp config.example.yaml config.yaml
   ```

2. Edit `config.yaml` and add your Claude API key:
   ```yaml
   claude_api:
     api_key: "your-api-key-here"
   ```

## Running the LLM-Workflow Director

1. Start the workflow director:
   ```
   python src/main.py
   ```

2. Follow the prompts to initialize a new project or continue an existing one.

## Running Tests

To run the test suite:

```
pytest
```

For more detailed testing information, refer to the [Testing Guidelines](TESTING.md).

## Next Steps

- Review the [Workflow Loop Design](workflow_loop.md) to understand the system's core functionality.
- Explore the [Claude Integration Guide](claude_integration.md) for details on how the system interacts with the Claude API.
- Check out the [Contributing Guidelines](CONTRIBUTING.md) if you're interested in contributing to the project.

## Troubleshooting

If you encounter any issues during setup or execution, please check the following:

1. Ensure all dependencies are correctly installed (`poetry install`).
2. Verify that your Claude API key is correctly set in `config.yaml`.
3. Check the logs in the `logs/` directory for any error messages.

If problems persist, please open an issue on the GitHub repository with a detailed description of the problem and any relevant log output.

Last Updated: 2024-09-21

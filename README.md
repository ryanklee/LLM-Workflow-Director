# LLM-Workflow Director

LLM-Workflow Director is a Python-based tool designed to assist in AI-driven software development. It aims to provide a structured approach to leveraging Large Language Models (LLMs) throughout the development lifecycle.

## Project Goals

- Streamline the integration of LLMs in software development processes
- Provide a configurable workflow system for AI-assisted development
- Maintain project state and progress across different development stages
- Offer a simple interface for developers to interact with LLMs in their workflow
- Implement a robust constraint system to enforce workflow rules and best practices

## Project Status

The LLM-Workflow Director has reached a significant milestone:

- **Dog-food Ready**: The project has now reached a state where it can be used to manage its own development process. This demonstrates the practical applicability of the tool in real-world software development scenarios.

## Key Features

- Configurable workflow stages and transitions
- Integration with LLM microservice for enhanced context-aware prompts and sufficiency evaluation
- State management for tracking project progress
- Command-line interface for easy interaction
- Extensible architecture for custom plugins and LLM models
- Coding conventions management and integration with Aider
- Improved error handling and retry mechanism for LLM queries
- Efficient caching system for LLM responses
- Tiered LLM approach for optimized performance and cost management
- Sophisticated prompt generation based on workflow configuration
- Enhanced logging for better debugging and monitoring
- Sophisticated prompt generation based on workflow configuration
- Enhanced logging for better debugging and monitoring
- Detailed project structure and coding conventions integration in LLM prompts
- Improved logging with separate console and file handlers

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
   pip install -r requirements.txt
   ```

## Usage

To start the LLM Workflow Director:

```
python src/main.py run
```

You can specify a custom configuration file using the `--config` option:

```
python src/main.py run --config path/to/your/config.yaml
```

To generate or manage coding conventions:

```
python src/main.py conventions
```

To preview coding conventions without saving:

```
python src/main.py conventions --preview
```

To generate Aider-compatible coding conventions:

```
python src/main.py aider-conventions
```

During execution, you can enter commands or type 'next' to move to the next workflow stage. Type 'complete' to finish the current stage, or 'exit' to quit the program.

The system now provides more detailed logging information. To view debug logs, set the environment variable `LOGLEVEL=DEBUG` before running the program:

```
LOGLEVEL=DEBUG python src/main.py run
```

### User Confirmation for Workflow Steps

When using the LLM Workflow Director with Aider, you will be prompted for confirmation before each step. You can either:

- Enter 'Y' to proceed with the suggested step
- Provide alternative directions to override the suggested step

This feature allows you to maintain control over the workflow while benefiting from the automated guidance provided by the system.

For detailed usage instructions, refer to the documentation in the `docs/` directory.

## Configuration

Customize the workflow stages and transitions in `src/workflow_config.yaml`. The configuration file defines:

- Stages: Each stage has a name, description, and a list of tasks.
- Transitions: Define how to move between stages, including conditions for transitions.

Example configuration:

```yaml
stages:
  - name: Project Initialization
    description: Set up the initial project structure and environment
    tasks:
      - Create project directory
      - Initialize git repository
      - Set up virtual environment

transitions:
  - from: Project Initialization
    to: Requirements Gathering
    condition: All initial setup tasks completed
```

## Contributing

This project is currently a collaboration between a human developer and an AI assistant. External contributions are not being accepted at this time.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Open-source community for providing essential tools and libraries
- Developers of the LLM models and APIs used in this project

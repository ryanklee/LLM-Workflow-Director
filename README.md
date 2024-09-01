# LLM-Workflow Director

LLM-Workflow Director is a Python-based tool designed to assist in AI-driven software development. It aims to provide a structured approach to leveraging Large Language Models (LLMs) throughout the development lifecycle.

## Project Goals

- Streamline the integration of LLMs in software development processes
- Provide a configurable workflow system for AI-assisted development
- Maintain project state and progress across different development stages
- Offer a simple interface for developers to interact with LLMs in their workflow

## Key Features

- Configurable workflow stages and transitions
- Integration with various LLM models
- State management for tracking project progress
- Command-line interface for easy interaction
- Extensible architecture for custom plugins and LLM models

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

During execution, you can enter commands or type 'next' to move to the next workflow stage. Type 'exit' to quit the program.

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

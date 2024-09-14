# LLM-Workflow Director

LLM-Workflow Director is a Python-based tool designed to assist in AI-driven software development. It provides a structured approach to leveraging Anthropic's Claude models throughout the development lifecycle.

## Quick Start

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/llm-workflow-director.git
   cd llm-workflow-director
   ```

2. Set up a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. Set up your Anthropic API key:
   ```
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

4. Run the LLM Workflow Director:
   ```
   python src/main.py run
   ```

For detailed usage instructions, configuration options, and advanced features, please refer to the [documentation](docs/index.md).

## Key Features

- Configurable workflow stages and transitions
- Direct integration with Anthropic's Claude API
- State management for tracking project progress
- Command-line interface for easy interaction
- Extensible architecture for custom plugins
- Tiered Claude model approach (Haiku, Sonnet, Opus)
- Comprehensive project state reporting and visualization

## Project Status

The LLM-Workflow Director is actively being developed and refined. Current focus areas include:

- Enhancing multi-modal input support
- Improving external tool integration
- Refining adaptive learning for Claude usage
- Optimizing prompt engineering techniques

## Contributing

This project is currently a collaboration between a human developer and an AI assistant. External contributions are not being accepted at this time.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Open-source community for providing essential tools and libraries
- Anthropic for developing the Claude models used in this project

For more detailed information, please refer to the [full documentation](docs/index.md).

Last Updated: 2024-09-14

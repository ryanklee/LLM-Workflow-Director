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
- Domain-specific task testing and performance benchmarking

## Project Status

The LLM-Workflow Director is making significant progress towards its goals:

- **Approaching Dog-food Ready**: The project is advancing towards a state where it can be used to manage its own development process. We have defined clear criteria for "dog-food ready" status and are actively working towards meeting these benchmarks.
- **Core Functionality Implementation**: We have implemented key components such as workflow management, Claude API integration, and basic LLM-driven evaluations.
- **Advanced Features Development**: We are currently in the process of implementing and refining advanced features such as multi-modal input support, external tool integration, adaptive learning for Claude usage, and enhanced prompt engineering techniques.
- **Domain-Specific Task Testing**: We have implemented comprehensive tests for various domain-specific tasks, including code generation, code review, architecture suggestions, and more.
- **Performance Benchmarking**: We have added performance benchmarks for all domain-specific tasks to analyze Claude's performance across different types of tasks.

For a detailed list of criteria for "dog-food ready" status, please refer to the [Dog-food Ready Criteria](docs/dogfood_ready_criteria.md) document.

## Testing

Run the full test suite:
```
pytest
```

To run domain-specific task tests:
```
pytest tests/test_domain_specific_tasks.py
```

To run performance benchmarks:
```
pytest tests/test_domain_specific_tasks.py --benchmark-only
```

## Documentation

For detailed documentation, please refer to the `docs/` directory. Key documents include:
- [Getting Started Guide](docs/getting_started.md)
- [Workflow Configuration](docs/workflow_configuration.md)
- [Claude Integration Guide](docs/claude_integration.md)
- [Testing Guidelines](docs/TESTING.md)
- [Domain-Specific Task Testing](docs/domain_specific_testing.md)

## Contributing

This project is currently a collaboration between a human developer and an AI assistant. External contributions are not being accepted at this time.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Open-source community for providing essential tools and libraries
- Anthropic for developing the Claude models used in this project

For more detailed information, please refer to the [full documentation](docs/index.md).

Last Updated: 2024-09-21

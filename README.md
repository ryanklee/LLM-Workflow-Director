# LLM-Workflow Director

LLM-Workflow Director is a Python-based tool designed to assist in AI-driven software development. It aims to provide a structured approach to leveraging Anthropic's Claude models throughout the development lifecycle.

## Project Goals

- Streamline the integration of Claude models in software development processes
- Provide a configurable workflow system for AI-assisted development
- Maintain project state and progress across different development stages
- Offer a simple interface for developers to interact with Claude models in their workflow
- Implement a robust constraint system to enforce workflow rules and best practices

## Project Status

The LLM-Workflow Director has reached significant milestones:

- **Dog-food Ready**: The project has now reached a state where it can be used to manage its own development process. This demonstrates the practical applicability of the tool in real-world software development scenarios.
- **Advanced Features Implementation**: We are currently in the process of implementing and refining advanced features such as multi-modal input support, external tool integration, adaptive learning for Claude usage, and enhanced prompt engineering techniques.

## Key Features

- Configurable workflow stages and transitions
- Direct integration with Anthropic's Claude API for enhanced context-aware prompts and sufficiency evaluation
- State management for tracking project progress
- Command-line interface for easy interaction
- Extensible architecture for custom plugins
- Coding conventions management and integration with Aider
- Improved error handling and retry mechanism for Claude API queries
- Efficient caching system for Claude API responses
- Tiered Claude model approach for optimized performance and cost management
- Sophisticated prompt generation based on workflow configuration
- Enhanced logging for better debugging and monitoring
- Detailed project structure and coding conventions integration in Claude prompts
- Advanced logging system with:
  - Separate console and file handlers
  - Structured JSON logging with detailed context
  - Timestamped log files for easy tracking
- Comprehensive project state reporting with workflow visualization
- Dynamic context enhancement for Claude prompts based on current workflow state
- Detailed progress tracking and reporting
- Exclusive use of Anthropic's Claude models (Haiku, Sonnet, and Opus) for all LLM interactions
- Optimized prompt engineering techniques for Claude models
- Utilization of Claude's 200k token context window for handling large amounts of context

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
   export ANTHROPIC_API_KEY=your_api_key_here
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

To display the current workflow status:

```
python src/main.py status
```

To transition to a specific workflow stage:

```
python src/main.py transition <stage_name>
```

To generate a project report:

```
python src/main.py report
```

You can specify the report format using the `--format` option (plain, markdown, or html):

```
python src/main.py report --format markdown
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

## Claude API Configuration

Ensure you have set your Anthropic API key as an environment variable:

```
export ANTHROPIC_API_KEY=your_api_key_here
```

The system uses the following Claude models:
- Claude 3 Haiku: Fast and cost-effective
- Claude 3 Sonnet: Balance of speed and intelligence
- Claude 3 Opus: Excels at writing and complex tasks

## Contributing

This project is currently a collaboration between a human developer and an AI assistant. External contributions are not being accepted at this time.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Open-source community for providing essential tools and libraries
- Anthropic for developing the Claude models used in this project
## Testing

### Token Limits in Tests

To ensure consistent and efficient testing, we've implemented a token limit for test inputs and outputs. This limit is defined in the `src/llm_config.yaml` file under the `test_settings` section:

```yaml
test_settings:
  max_test_tokens: 100
```

This limit is enforced in both the `MockClaudeClient` and the actual `ClaudeManager` to simulate real-world constraints and prevent unnecessarily long inputs or outputs in our tests.

Key points:
- Inputs exceeding the token limit will raise a `ValueError`.
- Outputs exceeding the token limit will be truncated and appended with "...".
- This limit applies only to test environments and does not affect production behavior.

When writing tests, keep this limit in mind and design your test cases accordingly. If you need to test with longer inputs or outputs, you may need to adjust the `max_test_tokens` value in the configuration file.

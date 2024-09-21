# LLM-Workflow Director Documentation

## Overview
The LLM-Workflow Director is a Python-based system designed to guide AI-assisted software development processes, emphasizing Domain-Driven Design (DDD) and Test-Driven Development (TDD) principles. The project is currently approaching "dog-food ready" status, where it will be capable of managing its own development process.

## Table of Contents

1. [Getting Started](getting_started.md)
2. [Workflow Loop Design](workflow_loop.md)
3. [Implementation Plan](implementation_plan.md)
4. [Domain Model](domain_model.md)
5. [Requirements](requirements.md)
6. [Workflow Configuration](workflow_configuration.md)
7. [Claude Integration Guide](claude_integration.md)
8. [Claude API Reference](claude_api_reference.md)
9. [Testing Guidelines](TESTING.md)
10. [Contributing Guidelines](CONTRIBUTING.md)
11. [Dog-food Ready Criteria](dogfood_ready_criteria.md)
12. [Project Structure](project_structure.md)
13. [Dependency Management](dependency_management.md)
14. [Contract Testing](contract_testing.md)
15. [Performance Optimization](performance_optimization.md)
16. [Security Best Practices](security_best_practices.md)

## Key Concepts

- **Workflow Stages**: The project is divided into distinct stages, each with specific tasks and objectives.
- **LLM Integration**: The system leverages Anthropic's Claude models for AI-assisted development.
- **State Management**: A robust state management system tracks project progress and artifacts.
- **Constraint Engine**: Enforces rules and best practices throughout the development process.
- **Sufficiency Evaluation**: Uses LLM capabilities to assess the completeness of each stage.
- **Contract Testing**: Ensures consistent behavior between the system and the Claude API.
- **Vector Database**: Utilizes Chroma DB for efficient storage and retrieval of project-related information.
- **Tiered LLM Approach**: Implements a strategy using different Claude models based on task complexity.

## Getting Started

For setup instructions and basic usage, please refer to the [Getting Started](getting_started.md) guide.

## Version Control

This documentation is version-controlled alongside the project code. Each document includes a "Last Updated" timestamp at the bottom. Always refer to the latest version in the repository.

## Feedback and Contributions

While this project is primarily a collaboration between a human developer and an AI assistant, feedback on the documentation is welcome. Please use the issue tracker in the project repository for any suggestions or reports of inconsistencies.

## Recent Updates

- Added Contract Testing documentation
- Included information on the tiered LLM approach
- Updated Testing Guidelines with new best practices
- Added Performance Optimization and Security Best Practices sections

Last Updated: 2024-09-21

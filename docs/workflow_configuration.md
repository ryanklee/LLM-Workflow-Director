# Workflow Configuration Guide

The LLM-Workflow Director uses a YAML-based configuration file to define the structure and flow of the workflow. This document explains the structure and components of the workflow configuration.

## Configuration File Structure

The configuration file (`src/workflow_config.yaml`) consists of two main sections:

1. `stages`: Defines the individual stages of the workflow
2. `transitions`: Specifies the allowed transitions between stages

### Stages

Each stage in the `stages` section has the following properties:

- `name`: A unique identifier for the stage
- `description`: A brief description of the stage's purpose
- `tasks`: A list of tasks to be completed in this stage

Example:

```yaml
stages:
  - name: Project Initialization
    description: Set up the initial project structure and environment
    tasks:
      - Create project directory
      - Initialize git repository
      - Set up virtual environment
```

### Transitions

The `transitions` section defines how the workflow can progress from one stage to another. Each transition has the following properties:

- `from`: The name of the starting stage
- `to`: The name of the destination stage
- `condition`: A description of the condition that must be met to allow this transition

Example:

```yaml
transitions:
  - from: Project Initialization
    to: Requirements Gathering
    condition: All initial setup tasks completed
```

## Best Practices

1. Keep stage names concise and descriptive
2. Ensure that all stages are connected through transitions
3. Define clear and measurable conditions for stage transitions
4. Break down complex stages into smaller, manageable tasks
5. Use consistent naming conventions throughout the configuration

## Extending the Configuration

The workflow configuration can be extended to include additional properties as needed, such as:

- Estimated time for each stage or task
- Required resources or tools for each stage
- Links to relevant documentation or templates

## Example Configuration

Here's a simple example of a complete workflow configuration:

```yaml
stages:
  - name: Project Initialization
    description: Set up the initial project structure and environment
    tasks:
      - Create project directory
      - Initialize git repository
      - Set up virtual environment

  - name: Requirements Gathering
    description: Collect and document project requirements
    tasks:
      - Interview stakeholders
      - Document functional requirements
      - Document non-functional requirements

transitions:
  - from: Project Initialization
    to: Requirements Gathering
    condition: All initial setup tasks completed

  - from: Requirements Gathering
    to: Project Initialization
    condition: Need to restart the project
```

This configuration defines two stages and the allowed transitions between them. You can expand on this structure to create more complex workflows as needed.

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
- `condition`: (Optional) A Python expression that must evaluate to True to allow this transition

If no condition is specified, the transition will be allowed as soon as the 'from' stage is completed and all constraints are satisfied.

Example:

```yaml
transitions:
  - from: Project Initialization
    to: Requirements Gathering
    condition: "'project_directory' in state and state['project_directory']"
  - from: Requirements Gathering
    to: Domain Modeling
    condition: "'requirements_documented' in state and state['requirements_documented']"
```

The WorkflowDirector will evaluate these conditions when determining if a transition is allowed. The condition is a Python expression that has access to the current `state` dictionary. If a stage is marked as completed, transitions from that stage will be allowed regardless of the condition.

Note: Be cautious when writing condition expressions, as they are evaluated using Python's `eval()` function. Ensure that only trusted input is used in these expressions.

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
    priorities:
      - Create project directory
      - Initialize git repository
      - Set up virtual environment

  - name: Requirements Gathering
    description: Collect and document project requirements
    tasks:
      - Interview stakeholders
      - Document functional requirements
      - Document non-functional requirements
    priorities:
      - Interview stakeholders
      - Document functional requirements
      - Document non-functional requirements

  - name: Domain Modeling
    description: Create and refine the domain model
    tasks:
      - Identify key domain concepts
      - Define relationships between concepts
      - Create initial domain model diagram
    priorities:
      - Identify key domain concepts
      - Define relationships between concepts
      - Create initial domain model diagram

transitions:
  - from: Project Initialization
    to: Requirements Gathering
    condition: All initial setup tasks completed

  - from: Requirements Gathering
    to: Domain Modeling
    condition: All requirements documented and approved

  - from: Domain Modeling
    to: Requirements Gathering
    condition: Need to refine requirements based on domain model

  - from: Requirements Gathering
    to: Project Initialization
    condition: Need to restart the project
```

This configuration defines three stages, their tasks, priorities, and the allowed transitions between them. The WorkflowDirector and SufficiencyEvaluator will use this configuration to manage the workflow and determine if a stage is complete.

## LLM Configuration

The LLM configuration is stored in a separate YAML file (`src/llm_config.yaml`) and includes settings for LLM tiers and prompt templates:

```yaml
tiers:
  fast:
    model: gpt-3.5-turbo
    max_tokens: 100
  balanced:
    model: gpt-3.5-turbo
    max_tokens: 500
  powerful:
    model: gpt-4
    max_tokens: 1000

prompt_templates:
  default: |
    Process this command: {command}
    Current stage: {workflow_stage}
    Stage description: {stage_description}
    Stage tasks:
    {stage_tasks}
    Stage priorities:
    {stage_priorities}
    
    Project structure:
    {project_structure}
    
    Coding conventions:
    {coding_conventions}
    
    Available transitions: {available_transitions}
    Project progress: {project_progress:.2%}
    
    Workflow history:
    {workflow_history}
    
    Additional context:
    {context}

  sufficiency_evaluation: |
    Evaluate the sufficiency of the current stage in the workflow:

    Stage Name: {stage_name}
    Stage Description: {stage_description}
    Stage Tasks:
    {stage_tasks}

    Current Project State:
    {project_state}

    Workflow History:
    {workflow_history}

    Based on the stage requirements, current project state, and workflow history, determine if this stage is sufficiently complete to move to the next stage.

    Provide your evaluation in the following format:
    Evaluation: [SUFFICIENT/INSUFFICIENT]
    Reasoning: [Detailed explanation of your evaluation]
    Next Steps: [If insufficient, provide specific steps to achieve sufficiency]
```

This configuration allows for easy customization of LLM settings and prompt templates, enabling context-aware interactions with the LLM throughout the workflow.

## Sufficiency Evaluation

The SufficiencyEvaluator uses the LLM to assess whether a stage is complete and sufficient to move to the next stage. It considers the following factors:

1. Stage description
2. Tasks associated with the stage
3. Current project state

The evaluator generates a prompt for the LLM, which then provides an evaluation in the following format:

```
Evaluation: [SUFFICIENT/INSUFFICIENT]
Reasoning: [Detailed reasoning for the evaluation]
Next Steps: [If insufficient, specific steps to achieve sufficiency]
```

This evaluation is used by the WorkflowDirector to determine whether to complete the current stage and move to the next one, or to remain in the current stage and provide guidance on what needs to be done to achieve sufficiency.

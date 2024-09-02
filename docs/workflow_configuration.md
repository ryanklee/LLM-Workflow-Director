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
    model: claude-3-haiku-20240307
    max_tokens: 1000
  balanced:
    model: claude-3-sonnet-20240229
    max_tokens: 4000
  powerful:
    model: claude-3-opus-20240229
    max_tokens: 4000

prompt_templates:
  default: |
    <context>
    You are Claude, an AI language model. You are currently being directed by an automated LLM-Workflow Director as part of an AI-assisted software development process. The project is currently in the {workflow_stage} stage. Your task is to assist with the current workflow step. Please process the following information and respond accordingly.
    </context>

    Current Workflow Stage: {workflow_stage}
    Stage Description: {stage_description}
    Stage Tasks:
    {stage_tasks}
    Stage Priorities:
    {stage_priorities}
    
    Project Structure:
    {project_structure}
    
    Coding Conventions:
    {coding_conventions}
    
    Available Transitions: {available_transitions}
    Project Progress: {project_progress:.2%}
    
    Workflow History:
    {workflow_history}
    
    Additional Context:
    {context}

    Given the above context, please respond to the following prompt:

    {command}

    Please structure your response using the following XML tags:
    <task_progress>
    [Provide a float value between 0 and 1 indicating the progress of the current task]
    </task_progress>

    <state_updates>
    [Provide any updates to the project state as key-value pairs]
    </state_updates>

    <actions>
    [List any actions that should be taken based on your response]
    </actions>

    <suggestions>
    [Provide any suggestions for the user or the workflow director]
    </suggestions>

    <response>
    [Your main response to the prompt]
    </response>

  sufficiency_evaluation: |
    <context>
    You are Claude, an AI language model. You are currently being directed by an automated LLM-Workflow Director as part of an AI-assisted software development process. Your task is to evaluate the sufficiency of the current stage in the workflow. Please process the following information and provide a detailed evaluation.
    </context>

    Evaluate the sufficiency of the current stage in the workflow:

    Stage Name: {stage_name}
    Stage Description: {stage_description}
    Stage Tasks:
    {stage_tasks}

    Current Project State:
    {project_state}

    Workflow History:
    {workflow_history}

    Based on the stage requirements, current project state, and workflow history, determine if this stage is sufficiently complete to move to the next stage. Consider the following aspects in your evaluation:
    1. Completion of all required tasks
    2. Quality of the work done
    3. Adherence to project standards and conventions
    4. Readiness for the next stage

    Please structure your response using the following XML tags:

    <evaluation>
    [SUFFICIENT or INSUFFICIENT]
    </evaluation>

    <reasoning>
    [Provide a detailed explanation of your evaluation, addressing each of the aspects mentioned above]
    </reasoning>

    <next_steps>
    [If insufficient, provide specific steps to achieve sufficiency. If sufficient, suggest any final touches or preparations for the next stage]
    </next_steps>
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

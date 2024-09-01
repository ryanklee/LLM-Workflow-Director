package workflow

import (
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/aider"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/component"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/constraint"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/direction"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/priority"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/progress"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/state"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/sufficiency"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/user"
)

func NewFileStateManager(projectPath string) component.WorkflowComponent {
	return state.NewFileStateManager(projectPath)
}

func NewBasicConstraintEngine() component.WorkflowComponent {
	return constraint.NewBasicConstraintEngine()
}

func NewBasicPriorityManager() component.WorkflowComponent {
	return priority.NewBasicPriorityManager()
}

func NewBasicDirectionGenerator() component.WorkflowComponent {
	return direction.NewBasicDirectionGenerator()
}

func NewBasicAiderInterface() component.WorkflowComponent {
	return aider.NewBasicAiderInterface()
}

func NewBasicUserInteractionHandler() component.WorkflowComponent {
	return user.NewBasicUserInteractionHandler()
}

func NewBasicProgressTracker() component.WorkflowComponent {
	return progress.NewBasicProgressTracker()
}

func NewLLMEvaluator(ai component.WorkflowComponent) component.WorkflowComponent {
	return sufficiency.NewLLMEvaluator(ai.(aider.AiderInterface))
}

package workflow

import (
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/aider"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/constraint"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/direction"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/priority"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/progress"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/state"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/sufficiency"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/user"
)

// WorkflowMediator coordinates the interactions between workflow components
type WorkflowMediator struct {
	stateManager           state.StateManager
	constraintEngine       constraint.ConstraintEngine
	priorityManager        priority.PriorityManager
	directionGenerator     direction.DirectionGenerator
	aiderInterface         aider.AiderInterface
	userInteractionHandler user.UserInteractionHandler
	progressTracker        progress.ProgressTracker
	sufficiencyEvaluator   sufficiency.Evaluator
}

func NewWorkflowMediator(
	sm state.StateManager,
	ce constraint.ConstraintEngine,
	pm priority.PriorityManager,
	dg direction.DirectionGenerator,
	ai aider.AiderInterface,
	uih user.UserInteractionHandler,
	pt progress.ProgressTracker,
	se sufficiency.Evaluator,
) *WorkflowMediator {
	return &WorkflowMediator{
		stateManager:           sm,
		constraintEngine:       ce,
		priorityManager:        pm,
		directionGenerator:     dg,
		aiderInterface:         ai,
		userInteractionHandler: uih,
		progressTracker:        pt,
		sufficiencyEvaluator:   se,
	}
}

func (wm *WorkflowMediator) ExecuteWorkflow(state interface{}) (interface{}, error) {
	// Implement the workflow logic here, coordinating between components
	// This method will replace the current Run() method in Director
	// ...
}

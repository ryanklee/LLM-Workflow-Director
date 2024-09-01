package workflow

import (
	"errors"
	"time"

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

// Director manages the workflow for LLM-assisted development
type Director struct {
	components []component.WorkflowComponent
	mediator   *WorkflowMediator
}

// NewDirector creates a new Director instance
func NewDirector(
	sm state.StateManager,
	ce constraint.ConstraintEngine,
	pm priority.PriorityManager,
	dg direction.DirectionGenerator,
	ai aider.AiderInterface,
	uih user.UserInteractionHandler,
	pt progress.ProgressTracker,
	se sufficiency.Evaluator,
) *Director {
	mediator := NewWorkflowMediator(sm, ce, pm, dg, ai, uih, pt, se)
	components := []WorkflowComponent{
		sm, ce, pm, dg, ai, uih, pt, se,
	}
	return &Director{
		components: components,
		mediator:   mediator,
	}
}

// Run starts the workflow process
func (d *Director) Run() error {
	state, err := d.mediator.stateManager.GetCurrentState()
	if err != nil {
		return err
	}

	result, err := d.mediator.ExecuteWorkflow(state)
	if err != nil {
		return err
	}

	return d.mediator.stateManager.UpdateState(result)
}

func (d *Director) handleUserInteraction() error {
	// Implement user interaction logic
	return errors.New("user interaction not implemented")
}

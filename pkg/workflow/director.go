package workflow

import (
	"errors"

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
func NewDirector(components ...component.WorkflowComponent) (*Director, error) {
	if len(components) == 0 {
		return nil, errors.New("at least one component is required")
	}

	var sm state.StateManager
	var ce constraint.ConstraintEngine
	var pm priority.PriorityManager
	var dg direction.DirectionGenerator
	var ai aider.AiderInterface
	var uih user.UserInteractionHandler
	var pt progress.ProgressTracker
	var se sufficiency.Evaluator

	for _, comp := range components {
		switch c := comp.(type) {
		case state.StateManager:
			sm = c
		case constraint.ConstraintEngine:
			ce = c
		case priority.PriorityManager:
			pm = c
		case direction.DirectionGenerator:
			dg = c
		case aider.AiderInterface:
			ai = c
		case user.UserInteractionHandler:
			uih = c
		case progress.ProgressTracker:
			pt = c
		case sufficiency.Evaluator:
			se = c
		}
	}

	if sm == nil || ce == nil || pm == nil || dg == nil || ai == nil || uih == nil || pt == nil || se == nil {
		return nil, errors.New("all required components must be provided")
	}

	mediator := NewWorkflowMediator(sm, ce, pm, dg, ai, uih, pt, se)
	return &Director{
		components: components,
		mediator:   mediator,
	}, nil
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

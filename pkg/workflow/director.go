package workflow

import (
	"errors"

	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/aider"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/constraint"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/direction"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/priority"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/progress"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/state"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/user"
)

// Director manages the workflow for LLM-assisted development
type Director struct {
	stateManager           state.StateManager
	constraintEngine       constraint.ConstraintEngine
	priorityManager        priority.PriorityManager
	directionGenerator     direction.DirectionGenerator
	aiderInterface         aider.AiderInterface
	userInteractionHandler user.UserInteractionHandler
	progressTracker        progress.ProgressTracker
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
) *Director {
	return &Director{
		stateManager:        sm,
		constraintEngine:    ce,
		priorityManager:     pm,
		directionGenerator:  dg,
		aiderInterface:      ai,
		userInteractionHandler: uih,
		progressTracker:     pt,
	}
}

// Run starts the workflow process
func (d *Director) Run() error {
	for {
		state, err := d.stateManager.GetCurrentState()
		if err != nil {
			return err
		}

		if d.progressTracker.IsComplete(state) {
			return nil
		}

		if err := d.constraintEngine.Validate(state); err != nil {
			return err
		}

		priorities := d.priorityManager.DeterminePriorities(state)

		directions, err := d.directionGenerator.Generate(state, priorities)
		if err != nil {
			return err
		}

		result, err := d.aiderInterface.Execute(directions)
		if err != nil {
			return err
		}

		if err := d.stateManager.UpdateState(result); err != nil {
			return err
		}

		if d.userInteractionHandler.IsInteractionRequired(state) {
			if err := d.handleUserInteraction(); err != nil {
				return err
			}
		}

		if err := d.progressTracker.UpdateProgress(state); err != nil {
			return err
		}
	}
}

func (d *Director) handleUserInteraction() error {
	// Implement user interaction logic
	return errors.New("user interaction not implemented")
}

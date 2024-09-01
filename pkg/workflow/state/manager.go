package state

import (
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/component"
)

// StateManager defines the interface for managing workflow state
type StateManager interface {
	component.WorkflowComponent
	GetCurrentState() (interface{}, error)
	UpdateState(interface{}) error
}

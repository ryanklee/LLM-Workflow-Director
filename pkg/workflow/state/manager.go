package state

import (
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow"
)

// StateManager defines the interface for managing workflow state
type StateManager interface {
	workflow.WorkflowComponent
	GetCurrentState() (interface{}, error)
	UpdateState(interface{}) error
}

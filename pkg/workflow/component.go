package workflow

// WorkflowComponent defines the common interface for all workflow components
type WorkflowComponent interface {
	Execute(state interface{}) (interface{}, error)
}

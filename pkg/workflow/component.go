package workflow

// WorkflowComponent defines the common interface for all workflow components
type WorkflowComponent interface {
	Name() string
	Execute(state interface{}) (interface{}, error)
}

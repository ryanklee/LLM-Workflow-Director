package priority

// PriorityManager defines the interface for managing priorities
type PriorityManager interface {
	DeterminePriorities(interface{}) interface{}
}

package state

// StateManager defines the interface for managing workflow state
type StateManager interface {
	GetCurrentState() (interface{}, error)
	UpdateState(interface{}) error
}

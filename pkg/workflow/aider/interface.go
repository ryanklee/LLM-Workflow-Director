package aider

// AiderInterface defines the interface for interacting with Aider
type AiderInterface interface {
	Execute(interface{}) (interface{}, error)
}

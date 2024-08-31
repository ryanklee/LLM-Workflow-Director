package progress

// ProgressTracker defines the interface for tracking workflow progress
type ProgressTracker interface {
	IsComplete(interface{}) bool
	UpdateProgress(interface{}) error
}

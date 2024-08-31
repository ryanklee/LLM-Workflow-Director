package user

// UserInteractionHandler defines the interface for handling user interactions
type UserInteractionHandler interface {
	IsInteractionRequired(interface{}) bool
}

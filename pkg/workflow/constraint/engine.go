package constraint

// ConstraintEngine defines the interface for validating constraints
type ConstraintEngine interface {
	Validate(interface{}) error
}

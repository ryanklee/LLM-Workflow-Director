package direction

// DirectionGenerator defines the interface for generating directions
type DirectionGenerator interface {
	Generate(state interface{}, priorities interface{}) (interface{}, error)
}

package sufficiency

// Evaluator defines the interface for performing sufficiency evaluations
type Evaluator interface {
	Evaluate(state interface{}) (bool, string, error)
}

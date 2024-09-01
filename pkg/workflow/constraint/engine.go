package constraint

import (
	"fmt"
	"sync"
)

// Constraint represents a single constraint in the workflow
type Constraint struct {
	Name        string
	Description string
	Validate    func(state map[string]interface{}) (bool, error)
}

// Engine manages and enforces workflow constraints
type Engine struct {
	constraints map[string]Constraint
	mu          sync.RWMutex
}

// NewEngine creates a new ConstraintEngine
func NewEngine() *Engine {
	return &Engine{
		constraints: make(map[string]Constraint),
	}
}

// AddConstraint adds a new constraint to the engine
func (e *Engine) AddConstraint(c Constraint) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	if _, exists := e.constraints[c.Name]; exists {
		return fmt.Errorf("constraint with name '%s' already exists", c.Name)
	}

	e.constraints[c.Name] = c
	return nil
}

// ValidateAll checks all constraints against the given state
func (e *Engine) ValidateAll(state map[string]interface{}) (bool, []string) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	valid := true
	var violations []string

	for _, c := range e.constraints {
		if isValid, err := c.Validate(state); !isValid {
			valid = false
			if err != nil {
				violations = append(violations, fmt.Sprintf("%s: %v", c.Name, err))
			} else {
				violations = append(violations, c.Name)
			}
		}
	}

	// Add project structure validation
	if projectStructure, ok := state["project_structure"].(map[string]interface{}); ok {
		if isValid, err := validateProjectStructure(projectStructure); !isValid {
			valid = false
			violations = append(violations, fmt.Sprintf("ProjectStructure: %v", err))
		}
	}

	return valid, violations
}

func validateProjectStructure(structure map[string]interface{}) (bool, error) {
	requiredDirs := []string{"src", "tests", "docs", "data"}
	requiredFiles := []string{"README.md", "requirements.txt", ".gitignore"}

	for _, dir := range requiredDirs {
		if _, ok := structure[dir]; !ok {
			return false, fmt.Errorf("missing required directory: %s", dir)
		}
	}

	for _, file := range requiredFiles {
		if _, ok := structure[file]; !ok {
			return false, fmt.Errorf("missing required file: %s", file)
		}
	}

	return true, nil
}

// GetConstraint retrieves a constraint by name
func (e *Engine) GetConstraint(name string) (Constraint, bool) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	c, exists := e.constraints[name]
	return c, exists
}

package constraint

import (
	"testing"
)

func TestNewEngine(t *testing.T) {
	engine := NewEngine()
	if engine == nil {
		t.Fatal("NewEngine() returned nil")
	}
	if engine.constraints == nil {
		t.Fatal("Engine constraints map is nil")
	}
}

func TestAddConstraint(t *testing.T) {
	engine := NewEngine()
	c := Constraint{
		Name:        "TestConstraint",
		Description: "A test constraint",
		Validate: func(state map[string]interface{}) (bool, error) {
			return true, nil
		},
	}

	err := engine.AddConstraint(c)
	if err != nil {
		t.Fatalf("Failed to add constraint: %v", err)
	}

	// Try to add the same constraint again
	err = engine.AddConstraint(c)
	if err == nil {
		t.Fatal("Expected error when adding duplicate constraint, got nil")
	}
}

func TestValidateAll(t *testing.T) {
	engine := NewEngine()
	c1 := Constraint{
		Name:        "AlwaysValid",
		Description: "A constraint that's always valid",
		Validate: func(state map[string]interface{}) (bool, error) {
			return true, nil
		},
	}
	c2 := Constraint{
		Name:        "AlwaysInvalid",
		Description: "A constraint that's always invalid",
		Validate: func(state map[string]interface{}) (bool, error) {
			return false, nil
		},
	}

	engine.AddConstraint(c1)
	engine.AddConstraint(c2)

	state := make(map[string]interface{})
	valid, violations := engine.ValidateAll(state)

	if valid {
		t.Fatal("Expected ValidateAll to return false, got true")
	}

	if len(violations) != 1 || violations[0] != "AlwaysInvalid" {
		t.Fatalf("Expected violations to be ['AlwaysInvalid'], got %v", violations)
	}
}

func TestGetConstraint(t *testing.T) {
	engine := NewEngine()
	c := Constraint{
		Name:        "TestConstraint",
		Description: "A test constraint",
		Validate: func(state map[string]interface{}) (bool, error) {
			return true, nil
		},
	}

	engine.AddConstraint(c)

	retrieved, exists := engine.GetConstraint("TestConstraint")
	if !exists {
		t.Fatal("GetConstraint returned false for existing constraint")
	}

	if retrieved.Name != c.Name || retrieved.Description != c.Description {
		t.Fatal("Retrieved constraint does not match the original")
	}

	_, exists = engine.GetConstraint("NonExistentConstraint")
	if exists {
		t.Fatal("GetConstraint returned true for non-existent constraint")
	}
}

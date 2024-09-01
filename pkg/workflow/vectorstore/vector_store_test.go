package vectorstore

import (
	"testing"
)

func TestVectorStore(t *testing.T) {
	vs := NewVectorStore()

	// Test storing and retrieving a vector
	vector := []float64{1.0, 2.0, 3.0}
	vs.Store("test", vector)

	retrieved, err := vs.Retrieve("test")
	if err != nil {
		t.Errorf("Failed to retrieve vector: %v", err)
	}

	if len(retrieved) != len(vector) {
		t.Errorf("Retrieved vector length mismatch. Expected %d, got %d", len(vector), len(retrieved))
	}

	for i, v := range retrieved {
		if v != vector[i] {
			t.Errorf("Retrieved vector mismatch at index %d. Expected %f, got %f", i, vector[i], v)
		}
	}

	// Test retrieving a non-existent vector
	_, err = vs.Retrieve("nonexistent")
	if err == nil {
		t.Error("Expected error when retrieving non-existent vector, got nil")
	}

	// Test deleting a vector
	vs.Delete("test")
	_, err = vs.Retrieve("test")
	if err == nil {
		t.Error("Expected error when retrieving deleted vector, got nil")
	}
}

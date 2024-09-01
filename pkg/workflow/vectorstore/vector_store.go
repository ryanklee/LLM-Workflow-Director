package vectorstore

import (
	"errors"
	"sync"
)

// VectorStore represents an in-memory vector database
type VectorStore struct {
	vectors map[string][]float64
	mu      sync.RWMutex
}

// NewVectorStore creates a new instance of VectorStore
func NewVectorStore() *VectorStore {
	return &VectorStore{
		vectors: make(map[string][]float64),
	}
}

// Store adds or updates a vector in the store
func (vs *VectorStore) Store(key string, vector []float64) {
	vs.mu.Lock()
	defer vs.mu.Unlock()
	vs.vectors[key] = vector
}

// Retrieve gets a vector from the store
func (vs *VectorStore) Retrieve(key string) ([]float64, error) {
	vs.mu.RLock()
	defer vs.mu.RUnlock()
	vector, ok := vs.vectors[key]
	if !ok {
		return nil, errors.New("vector not found")
	}
	return vector, nil
}

// Delete removes a vector from the store
func (vs *VectorStore) Delete(key string) {
	vs.mu.Lock()
	defer vs.mu.Unlock()
	delete(vs.vectors, key)
}

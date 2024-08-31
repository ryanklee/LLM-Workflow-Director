package workflow

import "testing"

func TestNewDirector(t *testing.T) {
    director := NewDirector()
    if director == nil {
        t.Error("NewDirector() returned nil")
    }
}

func TestDirectorRun(t *testing.T) {
    director := NewDirector()
    err := director.Run()
    if err != nil {
        t.Errorf("Director.Run() returned an error: %v", err)
    }
}

package main

import (
	"errors"
	"sync"
)

type Cache struct {
	mu    sync.RWMutex
	items map[string]string
}

func NewCache() *Cache {
	return &Cache{
		items: make(map[string]string),
	}
}

func (c *Cache) Set(key, value string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.items[key] = value
}

func (c *Cache) Get(key string) (string, error) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	if value, ok := c.items[key]; ok {
		return value, nil
	}
	return "", errors.New("key not found in cache")
}

package main

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
)

var (
	llmClient *LLMClient
	cache     *Cache
)

func main() {
	llmClient = NewLLMClient()
	cache = NewCache()

	r := gin.Default()

	r.GET("/health", healthCheck)
	r.POST("/generate", generateLLMResponse)
	r.POST("/evaluate", evaluateSufficiency)
	r.POST("/breakdown", taskBreakdown)
	r.GET("/cache/:key", getCachedResult)

	log.Println("Starting LLM Microservice API...")
	if err := r.Run(":8080"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func healthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"status": "healthy"})
}

func generateLLMResponse(c *gin.Context) {
	var request struct {
		Prompt string `json:"prompt" binding:"required"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Check cache first
	if cachedResponse, err := cache.Get(request.Prompt); err == nil {
		c.JSON(http.StatusOK, gin.H{"response": cachedResponse, "cached": true})
		return
	}

	response, err := llmClient.GenerateResponse(request.Prompt)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Cache the response
	cache.Set(request.Prompt, response)

	c.JSON(http.StatusOK, gin.H{"response": response, "cached": false})
}

func evaluateSufficiency(c *gin.Context) {
	var request struct {
		State string `json:"state" binding:"required"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	sufficient, reason, err := llmClient.EvaluateSufficiency(request.State)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"sufficient": sufficient, "reason": reason})
}

func taskBreakdown(c *gin.Context) {
	var request struct {
		Task string `json:"task" binding:"required"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	subtasks, err := llmClient.BreakdownTask(request.Task)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"subtasks": subtasks})
}

func getCachedResult(c *gin.Context) {
	key := c.Param("key")
	value, err := cache.Get(key)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Key not found in cache"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"value": value})
}

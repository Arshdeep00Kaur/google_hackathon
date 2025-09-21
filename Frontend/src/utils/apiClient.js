// API utilities for backend communication
const API_BASE = 'http://localhost:8000'

class ApiClient {
  constructor() {
    this.baseUrl = API_BASE
  }

  // Health check endpoints
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseUrl}/health`)
      return await response.json()
    } catch (error) {
      console.error('Health check failed:', error)
      throw error
    }
  }

  // Chat job submission
  async submitChatJob(query, userId, sessionId = null, priority = 'normal') {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/jobs/submit-chat-job`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          user_id: userId,
          session_id: sessionId || `session_${userId}_${Date.now()}`,
          priority
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to submit chat job:', error)
      throw error
    }
  }

  // Get job status
  async getJobStatus(jobId) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/jobs/job-status/${jobId}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to get job status:', error)
      throw error
    }
  }

  // Get queue statistics
  async getQueueStats() {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/jobs/queue-stats`)
      return await response.json()
    } catch (error) {
      console.error('Failed to get queue stats:', error)
      throw error
    }
  }

  // Cancel job
  async cancelJob(jobId) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/jobs/cancel-job/${jobId}`, {
        method: 'DELETE'
      })
      return await response.json()
    } catch (error) {
      console.error('Failed to cancel job:', error)
      throw error
    }
  }

  // Document management
  async uploadDocument(file, userId) {
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await fetch(`${this.baseUrl}/api/v1/documents/`, {
        method: 'POST',
        body: formData,
        headers: {
          'X-User-ID': userId // Pass user ID in header
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to upload document:', error)
      throw error
    }
  }

  // Delete document
  async deleteDocument(documentId, userId) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/documents/${documentId}`, {
        method: 'DELETE',
        headers: {
          'X-User-ID': userId
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to delete document:', error)
      throw error
    }
  }

  // Get documents list
  async getDocuments(limit = 10, offset = 0) {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/v1/documents/?limit=${limit}&offset=${offset}`
      )
      return await response.json()
    } catch (error) {
      console.error('Failed to get documents:', error)
      throw error
    }
  }

  // Get specific document
  async getDocument(documentId) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/documents/${documentId}`)
      return await response.json()
    } catch (error) {
      console.error('Failed to get document:', error)
      throw error
    }
  }

  // Query management
  async submitQuery(query, userId, context = null, category = null) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/queries/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          user_id: userId,
          context,
          category
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to submit query:', error)
      throw error
    }
  }

  // Get queries list
  async getQueries(limit = 10, offset = 0, userId = null, status = null) {
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString()
      })
      
      if (userId) params.append('user_id', userId)
      if (status) params.append('status', status)

      const response = await fetch(`${this.baseUrl}/api/v1/queries/?${params}`)
      return await response.json()
    } catch (error) {
      console.error('Failed to get queries:', error)
      throw error
    }
  }

  // Get specific query result
  async getQuery(queryId) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/queries/${queryId}`)
      return await response.json()
    } catch (error) {
      console.error('Failed to get query:', error)
      throw error
    }
  }

  // WebSocket connection helper
  createWebSocket(userId) {
    const wsUrl = `ws://localhost:8000/ws/${userId}`
    return new WebSocket(wsUrl)
  }
}

// Create singleton instance
const apiClient = new ApiClient()

export default apiClient

// Export individual methods for convenience
export const {
  healthCheck,
  submitChatJob,
  getJobStatus,
  getQueueStats,
  cancelJob,
  uploadDocument,
  getDocuments,
  getDocument,
  submitQuery,
  getQueries,
  getQuery,
  createWebSocket
} = apiClient
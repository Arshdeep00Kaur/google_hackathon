import React, { useState, useEffect, useRef } from 'react'
import { useUser, SignedIn, SignedOut, RedirectToSignIn, UserButton } from '@clerk/clerk-react'
import apiClient from '../utils/apiClient'
import './ChatPage.css'

const ChatPage = () => {
  const { user, isLoaded } = useUser()
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentJobId, setCurrentJobId] = useState(null)
  const [queuePosition, setQueuePosition] = useState(null)
  const [estimatedWaitTime, setEstimatedWaitTime] = useState(null)
  const [connected, setConnected] = useState(false)
  const [chatSessions, setChatSessions] = useState([])
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [documents, setDocuments] = useState([])
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [isDragOver, setIsDragOver] = useState(false)
  const [sidebarTab, setSidebarTab] = useState('chats') // 'chats', 'documents', 'settings'
  const [isProcessingFile, setIsProcessingFile] = useState(false)
  
  const messagesEndRef = useRef(null)
  const wsRef = useRef(null)
  const fileInputRef = useRef(null)

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Initialize chat session
  useEffect(() => {
    if (user?.id && isLoaded) {
      initializeChat()
      connectWebSocket()
      loadDocuments()
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [user?.id, isLoaded])

  const initializeChat = () => {
    const sessionId = `session_${user.id}_${Date.now()}`
    setCurrentSessionId(sessionId)
    
    // Load existing chat sessions
    const savedSessions = JSON.parse(localStorage.getItem(`chat_sessions_${user.id}`) || '[]')
    setChatSessions(savedSessions)
    
    // Create new session
    const newSession = {
      id: sessionId,
      title: 'New Chat',
      createdAt: new Date().toISOString(),
      lastMessage: null,
      messageCount: 0
    }
    
    const updatedSessions = [newSession, ...savedSessions]
    setChatSessions(updatedSessions)
    localStorage.setItem(`chat_sessions_${user.id}`, JSON.stringify(updatedSessions))
  }

  const connectWebSocket = () => {
    if (!user?.id) return

    wsRef.current = apiClient.createWebSocket(user.id)

    wsRef.current.onopen = () => {
      setConnected(true)
      console.log('WebSocket connected')
    }

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data)
    }

    wsRef.current.onclose = () => {
      setConnected(false)
      console.log('WebSocket disconnected')
      setTimeout(connectWebSocket, 3000)
    }

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  const handleWebSocketMessage = (data) => {
    switch (data.event) {
      case 'job_status_update':
        if (data.data.job_id === currentJobId) {
          if (data.data.status === 'completed') {
            setIsLoading(false)
            setCurrentJobId(null)
            setQueuePosition(null)
            setEstimatedWaitTime(null)
            fetchJobResult(data.data.job_id)
          } else if (data.data.status === 'failed') {
            setIsLoading(false)
            addMessage('system', 'Sorry, there was an error processing your request. Please try again.')
          }
        }
        break
      
      case 'queue_position_update':
        if (data.data.job_id === currentJobId) {
          setQueuePosition(data.data.position)
          setEstimatedWaitTime(data.data.estimated_wait)
        }
        break
      
      case 'chat_response_chunk':
        handleStreamingResponse(data.data)
        break
      
      default:
        console.log('Unknown WebSocket event:', data.event)
    }
  }

  const handleStreamingResponse = (data) => {
    setMessages(prev => {
      const lastMessage = prev[prev.length - 1]
      if (lastMessage && lastMessage.role === 'assistant' && !lastMessage.completed) {
        return [
          ...prev.slice(0, -1),
          {
            ...lastMessage,
            content: lastMessage.content + data.chunk,
            completed: data.is_final
          }
        ]
      }
      return prev
    })
  }

  const fetchJobResult = async (jobId) => {
    try {
      const jobData = await apiClient.getJobStatus(jobId)
      if (jobData.status === 'completed' && jobData.result) {
        const response = jobData.result.response || jobData.result.data
        const sources = jobData.result.sources || []
        addMessage('assistant', response, sources)
      }
    } catch (error) {
      console.error('Error fetching job result:', error)
      addMessage('system', 'Error retrieving response. Please try again.')
    }
  }

  const loadDocuments = async () => {
    try {
      const response = await apiClient.getDocuments(50, 0)
      setDocuments(response.documents || [])
    } catch (error) {
      console.error('Error loading documents:', error)
    }
  }

  const addMessage = (role, content, sources = null, fileInfo = null) => {
    const newMessage = {
      id: Date.now(),
      role,
      content,
      sources,
      fileInfo,
      timestamp: new Date().toISOString(),
      completed: true
    }
    
    setMessages(prev => {
      const updated = [...prev, newMessage]
      
      // Update session title and save to localStorage
      if (role === 'user' && currentSessionId) {
        updateSessionInfo(content, updated.length)
      }
      
      return updated
    })
  }

  const updateSessionInfo = (lastMessage, messageCount) => {
    const title = lastMessage.length > 50 ? lastMessage.substring(0, 50) + '...' : lastMessage
    
    setChatSessions(prev => {
      const updated = prev.map(session => 
        session.id === currentSessionId 
          ? { ...session, title, lastMessage, messageCount }
          : session
      )
      localStorage.setItem(`chat_sessions_${user.id}`, JSON.stringify(updated))
      return updated
    })
  }

  const submitQuery = async () => {
    if (!inputMessage.trim() || !user?.id || isLoading) return

    const userMessage = inputMessage.trim()
    setInputMessage('')
    setIsLoading(true)

    // Add user message to chat
    addMessage('user', userMessage)

    try {
      const jobData = await apiClient.submitChatJob(
        userMessage,
        user.id,
        currentSessionId,
        'normal'
      )

      setCurrentJobId(jobData.job_id)
      setQueuePosition(jobData.queue_position)
      setEstimatedWaitTime(jobData.estimated_wait_time)
      
      if (jobData.queue_position > 0) {
        addMessage('system', `Processing your query... Position in queue: ${jobData.queue_position}`)
      }
    } catch (error) {
      console.error('Error submitting query:', error)
      setIsLoading(false)
      addMessage('system', 'Error submitting your query. Please check the connection and try again.')
    }
  }

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return
    
    setIsProcessingFile(true)
    
    for (const file of files) {
      try {
        addMessage('system', `Uploading ${file.name}...`)
        
        const response = await apiClient.uploadDocument(file, user.id)
        
        const fileInfo = {
          filename: response.filename,
          category: response.category,
          status: response.status,
          size: file.size
        }
        
        addMessage('system', `✅ Document "${file.name}" uploaded successfully and categorized as: ${response.category}`, null, fileInfo)
        
        setUploadedFiles(prev => [...prev, fileInfo])
        await loadDocuments() // Refresh document list
        
      } catch (error) {
        console.error('Error uploading file:', error)
        addMessage('system', `❌ Failed to upload "${file.name}". Please try again.`)
      }
    }
    
    setIsProcessingFile(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragOver(false)
    const files = Array.from(e.dataTransfer.files)
    handleFileUpload(files)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const selectChatSession = (sessionId) => {
    // Save current session messages
    if (currentSessionId && messages.length > 0) {
      localStorage.setItem(`chat_messages_${currentSessionId}`, JSON.stringify(messages))
    }
    
    // Load selected session messages
    setCurrentSessionId(sessionId)
    const savedMessages = JSON.parse(localStorage.getItem(`chat_messages_${sessionId}`) || '[]')
    setMessages(savedMessages)
  }

  const createNewChat = () => {
    initializeChat()
    setMessages([])
  }

  const deleteDocument = async (documentId) => {
    try {
      await apiClient.deleteDocument(documentId)
      await loadDocuments()
      addMessage('system', 'Document deleted successfully')
    } catch (error) {
      console.error('Error deleting document:', error)
      addMessage('system', 'Failed to delete document')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submitQuery()
    }
  }

  if (!isLoaded) {
    return <div className="chat-loading">Loading...</div>
  }

  return (
    <>
      <SignedIn>
        <div className="chat-container">
          {/* Sidebar */}
          <div className="chat-sidebar">
            <div className="sidebar-header">
              <div className="user-info">
                <UserButton afterSignOutUrl="/" />
                <span className="user-name">{user?.fullName || 'User'}</span>
              </div>
              <div className="connection-status">
                <span className={`status-dot ${connected ? 'connected' : 'disconnected'}`}></span>
                <span className="status-text">{connected ? 'Connected' : 'Connecting...'}</span>
              </div>
            </div>

            {/* Sidebar Tabs */}
            <div className="sidebar-tabs">
              <button 
                className={`tab-button ${sidebarTab === 'chats' ? 'active' : ''}`}
                onClick={() => setSidebarTab('chats')}
              >
                💬 Chats
              </button>
              <button 
                className={`tab-button ${sidebarTab === 'documents' ? 'active' : ''}`}
                onClick={() => setSidebarTab('documents')}
              >
                📄 Documents
              </button>
              <button 
                className={`tab-button ${sidebarTab === 'settings' ? 'active' : ''}`}
                onClick={() => setSidebarTab('settings')}
              >
                ⚙️ Settings
              </button>
            </div>

            {/* Tab Content */}
            <div className="sidebar-content">
              {sidebarTab === 'chats' && (
                <div className="chats-section">
                  <button className="new-chat-btn" onClick={createNewChat}>
                    + New Chat
                  </button>
                  <div className="chat-history">
                    {chatSessions.map(session => (
                      <div 
                        key={session.id}
                        className={`chat-session ${session.id === currentSessionId ? 'active' : ''}`}
                        onClick={() => selectChatSession(session.id)}
                      >
                        <div className="session-title">{session.title}</div>
                        <div className="session-info">
                          {session.messageCount} messages • {new Date(session.createdAt).toLocaleDateString()}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {sidebarTab === 'documents' && (
                <div className="documents-section">
                  <div className="document-upload-area">
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={(e) => handleFileUpload(Array.from(e.target.files))}
                      accept=".pdf,.txt,.doc,.docx"
                      multiple
                      style={{ display: 'none' }}
                    />
                    <button 
                      className="upload-btn"
                      onClick={() => fileInputRef.current?.click()}
                      disabled={isProcessingFile}
                    >
                      {isProcessingFile ? '📤 Processing...' : '📁 Upload Documents'}
                    </button>
                  </div>
                  
                  <div className="documents-list">
                    <h3>Your Documents ({documents.length})</h3>
                    {documents.map(doc => (
                      <div key={doc.document_id} className="document-item">
                        <div className="doc-info">
                          <div className="doc-name">{doc.filename}</div>
                          <div className="doc-details">
                            <span className={`doc-category ${doc.category}`}>{doc.category}</span>
                            <span className="doc-size">{(doc.size / 1024).toFixed(1)}KB</span>
                          </div>
                        </div>
                        <button 
                          className="delete-doc-btn"
                          onClick={() => deleteDocument(doc.document_id)}
                          title="Delete document"
                        >
                          🗑️
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {sidebarTab === 'settings' && (
                <div className="settings-section">
                  <h3>Settings</h3>
                  <div className="setting-item">
                    <label>Model Selection</label>
                    <select>
                      <option>Gemini 1.5 Flash</option>
                      <option>GPT-4</option>
                    </select>
                  </div>
                  <div className="setting-item">
                    <label>Response Length</label>
                    <select>
                      <option>Concise</option>
                      <option>Detailed</option>
                      <option>Comprehensive</option>
                    </select>
                  </div>
                  <div className="setting-item">
                    <label>Auto-scroll</label>
                    <input type="checkbox" defaultChecked />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Main Chat Area */}
          <div className="chat-main">
            {/* Chat Header */}
            <div className="chat-header">
              <h2>LegalX Assistant</h2>
              <div className="header-actions">
                <span className="document-count">{documents.length} documents ready</span>
                {queuePosition !== null && (
                  <span className="queue-info">Queue: {queuePosition} | Wait: {estimatedWaitTime}s</span>
                )}
              </div>
            </div>

            {/* Messages Area */}
            <div 
              className={`messages-area ${isDragOver ? 'drag-over' : ''}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              {isDragOver && (
                <div className="drop-overlay">
                  <div className="drop-message">
                    📁 Drop documents here to upload
                  </div>
                </div>
              )}

              {messages.length === 0 && (
                <div className="welcome-section">
                  <h3>Welcome to LegalX</h3>
                  <p>Upload legal documents and ask questions about them. I'll provide detailed analysis with source citations.</p>
                  
                  <div className="quick-actions">
                    <button onClick={() => fileInputRef.current?.click()}>
                      📁 Upload Document
                    </button>
                    <button onClick={() => setInputMessage("What are the key terms in my contract?")}>
                      💡 Example Query
                    </button>
                  </div>

                  <div className="rag-info">
                    <h4>🔍 How RAG Works Here:</h4>
                    <ul>
                      <li><strong>Upload:</strong> Your documents are processed and vectorized</li>
                      <li><strong>Query:</strong> Ask questions in natural language</li>
                      <li><strong>Retrieve:</strong> AI finds relevant document sections</li>
                      <li><strong>Generate:</strong> Contextual answers with source citations</li>
                    </ul>
                  </div>
                </div>
              )}
              
              {messages.map((message) => (
                <div key={message.id} className={`message ${message.role}`}>
                  <div className="message-content">
                    <div className="message-text">{message.content}</div>
                    
                    {message.sources && message.sources.length > 0 && (
                      <div className="message-sources">
                        <h4>📖 Sources:</h4>
                        {message.sources.map((source, index) => (
                          <div key={index} className="source-item">
                            <span className="source-doc">📄 {source.document_id}</span>
                            {source.page && <span className="source-page">Page {source.page}</span>}
                            {source.relevance_score && (
                              <span className="source-relevance">
                                {(source.relevance_score * 100).toFixed(1)}% match
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {message.fileInfo && (
                      <div className="file-info">
                        <div className="file-details">
                          📄 {message.fileInfo.filename} 
                          <span className={`file-category ${message.fileInfo.category}`}>
                            {message.fileInfo.category}
                          </span>
                        </div>
                      </div>
                    )}

                    <div className="message-time">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="message assistant">
                  <div className="message-content">
                    <div className="typing-indicator">
                      <div className="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                      <span>AI is analyzing your query...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="input-area">
              <div className="input-container">
                <div className="input-actions">
                  <button 
                    className="attach-btn"
                    onClick={() => fileInputRef.current?.click()}
                    title="Attach document"
                  >
                    📎
                  </button>
                </div>
                
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask a question about your legal documents..."
                  disabled={isLoading}
                  className="message-input"
                  rows={1}
                />
                
                <button
                  onClick={submitQuery}
                  disabled={!inputMessage.trim() || isLoading}
                  className="send-btn"
                >
                  {isLoading ? '⏳' : '➤'}
                </button>
              </div>
              
              <div className="input-footer">
                <span className="document-indicator">
                  {documents.length > 0 ? `${documents.length} documents available for context` : 'Upload documents to enable RAG'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </SignedIn>
      
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
    </>
  )
}

export default ChatPage
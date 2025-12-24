import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
  },
})

// Agents
export const listAgents = () => api.get('/api/agents')
export const getAgent = (notebookId) => api.get(`/api/agents/${notebookId}`)
export const getAgentHierarchy = (agentId) => 
  api.get(`/api/agents/${agentId}/hierarchy`)
export const getAgentParent = (agentId) => 
  api.get(`/api/agents/${agentId}/parent`)

// Notebooks
export const getNotebook = (notebookId) => api.get(`/api/notebooks/${notebookId}`)
export const getNotebookContent = (notebookId, format = null) => {
  const url = `/api/notebooks/${notebookId}/content`
  const params = format ? { params: { format } } : {}
  return api.get(url, params)
}
export const deleteNotebook = (notebookId) => api.delete(`/api/notebooks/${notebookId}`)
// Generic agent deletion (works for both MasterAgent and NoteBookAgent)
export const deleteAgent = (agentId) => api.delete(`/api/agents/${agentId}`)
// Reset database to initial state
export const resetDatabase = () => api.post('/api/agents/reset-database')
export const splitNotebook = (notebookId) => api.post(`/api/notebooks/${notebookId}/split`)

// TopLevelAgent Chat
export const chatWithTopLevelAgent = (message, sessionId = null) =>
  api.post('/api/top-level-agent/chat', { message, session_id: sessionId })

// TopLevelAgent Sessions
export const createTopLevelAgentSession = (title = null) =>
  api.post('/api/top-level-agent/sessions', { title })

export const listTopLevelAgentSessions = () =>
  api.get('/api/top-level-agent/sessions')

export const getSessionConversations = (sessionId) =>
  api.get(`/api/sessions/${sessionId}/conversations`)

export const deleteSession = (sessionId) =>
  api.delete(`/api/sessions/${sessionId}`)

// TopLevelAgent Info
export const getTopLevelAgentInfo = () =>
  api.get('/api/top-level-agent/info')

// File Upload
export const uploadFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

// Notebook Creation
export const confirmOutlineAndCreateNotebook = (userRequest, outline, filePath = null, sessionId = null) => {
  return api.post('/api/notebooks/confirm-outline-and-create', {
    user_request: userRequest,
    outline: outline,
    file_path: filePath,
    session_id: sessionId,
  })
}

// Outline Revision
export const reviseOutline = (userRequest, currentOutline, userFeedback, filePath = null) => {
  return api.post('/api/notebooks/revise-outline', {
    user_request: userRequest,
    current_outline: currentOutline,
    user_feedback: userFeedback,
    file_path: filePath,
  })
}

// Agent Instructions
export const getAgentInstructions = (agentId) => {
  return api.get(`/api/agents/${agentId}/instructions`)
}

export const updateAgentInstructions = (agentId, instructions) => {
  return api.put(`/api/agents/${agentId}/instructions`, {
    instructions: instructions,
  })
}

// Agent Tools
export const getAgentTools = (agentId) => {
  return api.get(`/api/agents/${agentId}/tools`)
}

// Agent Chat
export const chatWithAgent = (agentId, message, sessionId = null) => {
  return api.post(`/api/agents/${agentId}/chat`, { message, session_id: sessionId })
}

// Tools
export const listTools = () => {
  return api.get('/api/tools')
}

export const getTool = (toolId) => {
  return api.get(`/api/tools/${toolId}`)
}

export const getAgentAsToolDetails = (toolId) => {
  return api.get(`/api/tools/${toolId}/agent-details`)
}

// Tracing
export const getSessionTracing = (sessionId, limit = 100) => {
  return api.get(`/api/sessions/${sessionId}/tracing`, { params: { limit } })
}

export const clearSessionTracing = (sessionId) => {
  return api.delete(`/api/sessions/${sessionId}/tracing`)
}

export default api


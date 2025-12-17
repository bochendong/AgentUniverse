import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Agents
export const listAgents = () => api.get('/api/agents')
export const getAgent = (notebookId) => api.get(`/api/agents/${notebookId}`)
export const getAgentHierarchy = (agentId) => 
  api.get(`/api/agents/${agentId}/hierarchy`)

// Notebooks
export const getNotebook = (notebookId) => api.get(`/api/notebooks/${notebookId}`)
export const getNotebookContent = (notebookId) => 
  api.get(`/api/notebooks/${notebookId}/content`)
export const deleteNotebook = (notebookId) => api.delete(`/api/notebooks/${notebookId}`)
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

export default api


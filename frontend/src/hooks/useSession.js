import { useState, useEffect, useCallback } from 'react'
import {
  createTopLevelAgentSession,
  listTopLevelAgentSessions,
  getSessionConversations,
  deleteSession,
} from '../api/client'

/**
 * Custom hook for managing chat sessions
 */
export function useSession() {
  const [sessions, setSessions] = useState([])
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [loading, setLoading] = useState(true)

  // Load sessions list
  const loadSessions = useCallback(async () => {
    try {
      const response = await listTopLevelAgentSessions()
      setSessions(response.data.sessions || [])
    } catch (err) {
      console.error('Failed to load sessions:', err)
      throw err
    }
  }, [])

  // Load session conversations
  const loadSessionConversations = useCallback(async (sessionId) => {
    try {
      const response = await getSessionConversations(sessionId)
      const conversations = response.data.conversations || []
      return conversations.map(c => ({ role: c.role, content: c.content }))
    } catch (err) {
      console.error('Failed to load conversations:', err)
      return []
    }
  }, [])

  // Create new session
  const createSession = useCallback(async () => {
    try {
      const response = await createTopLevelAgentSession()
      const newSession = response.data
      setSessions(prev => [newSession, ...prev])
      setCurrentSessionId(newSession.id)
      return newSession
    } catch (err) {
      console.error('Failed to create session:', err)
      throw err
    }
  }, [])

  // Delete session
  const removeSession = useCallback(async (sessionId) => {
    try {
      await deleteSession(sessionId)
      await loadSessions()
      if (currentSessionId === sessionId) {
        setCurrentSessionId(null)
      }
    } catch (err) {
      console.error('Failed to delete session:', err)
      throw err
    }
  }, [currentSessionId, loadSessions])

  // Initialize
  useEffect(() => {
    const init = async () => {
      setLoading(true)
      try {
        await loadSessions()
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [loadSessions])

  return {
    sessions,
    currentSessionId,
    setCurrentSessionId,
    loading,
    loadSessions,
    loadSessionConversations,
    createSession,
    removeSession,
  }
}


import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Box,
  Typography,
  Grid,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  ArrowBack as BackIcon,
  SmartToy as AgentsIcon,
} from '@mui/icons-material'
import { listAgents } from '../api/client'
import AgentCard from '../components/AgentCard'

/**
 * Agents List Page - 苹果风格
 * 显示所有agents的列表，每个agent是一个neon edge card
 */
function AgentsListPage() {
  const navigate = useNavigate()
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadAgents = async () => {
    try {
      setLoading(true)
      const response = await listAgents()
      setAgents(response.data || [])
    } catch (err) {
      console.error('Failed to load agents:', err)
      setError(err.response?.data?.detail || 'Failed to load agents')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAgents()
  }, [])

  const handleDelete = (deletedNotebookId) => {
    // 从列表中移除已删除的agent
    setAgents(agents.filter(agent => agent.notebook_id !== deletedNotebookId))
  }

  if (loading) {
    return (
      <Box
        sx={{
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          bgcolor: '#F5F5F7',
        }}
      >
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        bgcolor: '#F5F5F7',
        overflowY: 'auto',
        overflowX: 'hidden',
      }}
    >
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Box
              sx={{
                bgcolor: '#007AFF',
                borderRadius: 2,
                p: 1.5,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <AgentsIcon sx={{ color: 'white', fontSize: 32 }} />
            </Box>
            <Box>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  color: '#1D1D1F',
                  mb: 0.5,
                }}
              >
                Agents
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: '#86868B',
                }}
              >
                查看系统中所有可用的 agents，了解它们的功能、配置和使用方法
              </Typography>
            </Box>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {agents.length === 0 ? (
          <Box
            sx={{
              textAlign: 'center',
              py: 8,
              bgcolor: 'white',
              borderRadius: 3,
              boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
            }}
          >
            <Typography variant="h6" sx={{ color: '#86868B', mb: 1 }}>
              No agents found
            </Typography>
            <Typography variant="body2" sx={{ color: '#86868B' }}>
              Create a notebook to get started
            </Typography>
          </Box>
        ) : (
          <Grid container spacing={3}>
            {agents.map((agent) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={agent.id}>
                <AgentCard
                  agent={agent}
                  onClick={() => navigate(`/agents/${agent.notebook_id}`)}
                  onDelete={handleDelete}
                />
              </Grid>
            ))}
          </Grid>
        )}
      </Container>
    </Box>
  )
}

export default AgentsListPage


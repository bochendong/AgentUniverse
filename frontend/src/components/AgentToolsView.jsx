import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Grid,
  Pagination,
} from '@mui/material'
import { Build as BuildIcon } from '@mui/icons-material'
import { getAgentTools } from '../api/client'
import ToolCard from './ToolCard'

/**
 * AgentToolsView Component
 * Display tools for a specific agent with pagination (4 tools per page)
 */
function AgentToolsView({ agentId }) {
  const [tools, setTools] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)
  const TOOLS_PER_PAGE = 4

  useEffect(() => {
    if (agentId) {
      loadTools()
      setPage(1) // Reset to first page when agent changes
    } else {
      setTools([])
      setPage(1)
    }
  }, [agentId])

  const loadTools = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await getAgentTools(agentId)
      setTools(response.data.tools || [])
    } catch (err) {
      console.error('Failed to load tools:', err)
      setError(err.response?.data?.detail || 'Failed to load tools')
    } finally {
      setLoading(false)
    }
  }

  // Always render, even if no agentId (will show loading or empty state)

  return (
    <Paper
      sx={{
        p: 3,
        bgcolor: 'white',
        borderRadius: 3,
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
        minHeight: '600px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
        <BuildIcon sx={{ color: '#007AFF', fontSize: 20 }} />
        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            color: '#1D1D1F',
          }}
        >
          Agent Tools
        </Typography>
        {tools.length > 0 && (
          <Typography
            variant="caption"
            sx={{
              color: '#86868B',
              ml: 1,
            }}
          >
            ({tools.length})
          </Typography>
        )}
      </Box>

      {/* Content */}
      <Box sx={{ flex: 1, overflowY: 'auto' }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        ) : !agentId ? (
          <Box
            sx={{
              textAlign: 'center',
              py: 8,
            }}
          >
            <Typography variant="body2" sx={{ color: '#86868B' }}>
              点击左侧层级图中的 agent 查看其 tools
            </Typography>
          </Box>
        ) : tools.length === 0 ? (
          <Box
            sx={{
              textAlign: 'center',
              py: 8,
            }}
          >
            <Typography variant="body2" sx={{ color: '#86868B', fontStyle: 'italic' }}>
              该 agent 没有 tools
            </Typography>
          </Box>
        ) : (
          <>
            {/* Tools Grid - Show only current page */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
              {tools
                .slice((page - 1) * TOOLS_PER_PAGE, page * TOOLS_PER_PAGE)
                .map((tool, index) => (
                  <Grid item xs={12} sm={6} key={tool.id || tool.name || index}>
                    <ToolCard tool={tool} />
                  </Grid>
                ))}
            </Grid>
            
            {/* Pagination */}
            {tools.length > TOOLS_PER_PAGE && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 'auto', pt: 2 }}>
                <Pagination
                  count={Math.ceil(tools.length / TOOLS_PER_PAGE)}
                  page={page}
                  onChange={(event, value) => setPage(value)}
                  color="primary"
                  size="medium"
                  showFirstButton
                  showLastButton
                />
              </Box>
            )}
          </>
        )}
      </Box>
    </Paper>
  )
}

export default AgentToolsView


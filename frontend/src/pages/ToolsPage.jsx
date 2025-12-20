import React, { useState, useEffect } from 'react'
import { Box, Container, Typography, Grid, CircularProgress, Alert, Tabs, Tab } from '@mui/material'
import { Build as BuildIcon } from '@mui/icons-material'
import { listTools } from '../api/client'
import ToolCard from '../components/ToolCard'

/**
 * ToolsPage Component - Display all function tools
 */
function ToolsPage() {
  const [tools, setTools] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedAgentType, setSelectedAgentType] = useState('all')

  useEffect(() => {
    loadTools()
  }, [])

  const loadTools = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await listTools()
      setTools(response.data.tools || [])
    } catch (err) {
      console.error('Failed to load tools:', err)
      setError(err.response?.data?.detail || 'Failed to load tools')
    } finally {
      setLoading(false)
    }
  }

  // Get unique agent types and map display names
  const getAgentTypeLabel = (agentType) => {
    if (agentType === 'AsToolAgent' || agentType === 'SpecializedAgent') {
      return 'As Tool Agent'
    }
    return agentType
  }

  const agentTypes = ['all', ...Array.from(new Set(tools.map(tool => tool.agent_type)))]

  // Filter tools by selected agent type
  const filteredTools = selectedAgentType === 'all'
    ? tools
    : tools.filter(tool => tool.agent_type === selectedAgentType)

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
              <BuildIcon sx={{ color: 'white', fontSize: 32 }} />
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
                Tools
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: '#86868B',
                }}
              >
                查看系统中所有可用的 tools，了解它们的调用方法、输入输出类型和任务描述
              </Typography>
            </Box>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {/* Filter Tabs */}
            <Box sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}>
              <Tabs
                value={selectedAgentType}
                onChange={(e, newValue) => setSelectedAgentType(newValue)}
                sx={{
                  '& .MuiTab-root': {
                    textTransform: 'none',
                    fontWeight: 500,
                    minHeight: 48,
                  },
                }}
              >
                <Tab label="全部" value="all" />
                {agentTypes.filter(type => type !== 'all').map((agentType) => (
                  <Tab key={agentType} label={getAgentTypeLabel(agentType)} value={agentType} />
                ))}
              </Tabs>
            </Box>

            {/* Tools Grid */}
            {filteredTools.length === 0 ? (
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
                  没有找到 tools
                </Typography>
                <Typography variant="body2" sx={{ color: '#86868B' }}>
                  {selectedAgentType === 'all' 
                    ? '系统中还没有注册任何 tools'
                    : `没有属于 ${getAgentTypeLabel(selectedAgentType)} 类型的 tools`}
                </Typography>
              </Box>
            ) : (
              <Grid container spacing={3}>
                {filteredTools.map((tool) => (
                  <Grid item xs={12} sm={6} md={4} key={tool.id}>
                    <ToolCard tool={tool} />
                  </Grid>
                ))}
              </Grid>
            )}
          </>
        )}
      </Container>
    </Box>
  )
}

export default ToolsPage


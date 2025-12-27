import React, { useState, useEffect } from 'react'
import { Box, Container, Typography, Grid, CircularProgress, Alert, Tabs, Tab, Pagination, Button, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions } from '@mui/material'
import { Build as BuildIcon, DeleteSweep as CleanupIcon } from '@mui/icons-material'
import { listTools, cleanupOldTools } from '../api/client'
import ToolCard from '../components/ToolCard'

/**
 * ToolsPage Component - Display all function skills
 */
function ToolsPage() {
  const [tools, setTools] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedAgentType, setSelectedAgentType] = useState('all')
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 6
  const [cleanupDialogOpen, setCleanupDialogOpen] = useState(false)
  const [cleanupLoading, setCleanupLoading] = useState(false)
  const [cleanupResult, setCleanupResult] = useState(null)

  useEffect(() => {
    loadTools()
  }, [])

  // Reset to page 1 when filter changes
  useEffect(() => {
    setCurrentPage(1)
  }, [selectedAgentType])

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

  // Calculate pagination
  const totalPages = Math.ceil(filteredTools.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const paginatedTools = filteredTools.slice(startIndex, endIndex)

  const handlePageChange = (event, value) => {
    setCurrentPage(value)
    // Scroll to top when page changes
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleCleanup = async () => {
    try {
      setCleanupLoading(true)
      setCleanupResult(null)
      const response = await cleanupOldTools()
      setCleanupResult(response.data)
      // Reload tools after cleanup
      await loadTools()
    } catch (err) {
      console.error('Failed to cleanup tools:', err)
      setCleanupResult({
        error: err.response?.data?.detail || err.message || 'Failed to cleanup tools'
      })
    } finally {
      setCleanupLoading(false)
    }
  }

  const handleCleanupDialogClose = () => {
    setCleanupDialogOpen(false)
    setCleanupResult(null)
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
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
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
                  Skills
                </Typography>
                <Typography
                  variant="body1"
                  sx={{
                    color: '#86868B',
                  }}
                >
                  查看系统中所有可用的 skills，了解它们的调用方法、输入输出类型和任务描述
                </Typography>
              </Box>
            </Box>
            <Button
              variant="outlined"
              startIcon={<CleanupIcon />}
              onClick={() => setCleanupDialogOpen(true)}
              sx={{
                borderColor: '#FF6B6B',
                color: '#FF6B6B',
                textTransform: 'none',
                '&:hover': {
                  borderColor: '#FF6B6B',
                  bgcolor: '#FF6B6B15',
                },
              }}
            >
              清理旧工具
            </Button>
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
              <>
                <Grid container spacing={3}>
                  {paginatedTools.map((tool) => (
                    <Grid item xs={12} sm={6} md={4} key={tool.id}>
                      <ToolCard tool={tool} />
                    </Grid>
                  ))}
                </Grid>

                {/* Pagination */}
                {totalPages > 1 && (
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'center',
                      mt: 4,
                      mb: 2,
                    }}
                  >
                    <Pagination
                      count={totalPages}
                      page={currentPage}
                      onChange={handlePageChange}
                      color="primary"
                      size="large"
                      showFirstButton
                      showLastButton
                      sx={{
                        '& .MuiPaginationItem-root': {
                          fontSize: '1rem',
                        },
                        '& .Mui-selected': {
                          fontWeight: 600,
                        },
                      }}
                    />
                  </Box>
                )}
              </>
            )}
          </>
        )}
      </Container>

      {/* Cleanup Dialog */}
      <Dialog
        open={cleanupDialogOpen}
        onClose={handleCleanupDialogClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>清理旧工具</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            此操作将删除数据库中不再注册的旧工具，并重新同步当前注册的工具。
          </DialogContentText>
          
          {cleanupLoading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
              <CircularProgress size={24} />
            </Box>
          )}

          {cleanupResult && !cleanupLoading && (
            <Box>
              {cleanupResult.error ? (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {cleanupResult.error}
                </Alert>
              ) : (
                <>
                  <Alert severity="success" sx={{ mb: 2 }}>
                    清理完成！
                  </Alert>
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>删除的工具数量：</strong> {cleanupResult.deleted_tools?.length || 0}
                    </Typography>
                    {cleanupResult.deleted_tools && cleanupResult.deleted_tools.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" sx={{ mb: 1, fontWeight: 600 }}>
                          已删除的工具：
                        </Typography>
                        {cleanupResult.deleted_tools.map((tool, idx) => (
                          <Typography key={idx} variant="body2" sx={{ ml: 2, color: '#86868B' }}>
                            • {tool.name} ({tool.id})
                          </Typography>
                        ))}
                      </Box>
                    )}
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>当前注册的工具数量：</strong> {cleanupResult.registered_tools_count || 0}
                    </Typography>
                    <Typography variant="body2">
                      <strong>数据库中的工具数量：</strong> {cleanupResult.database_tools_count_after || 0}
                    </Typography>
                  </Box>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCleanupDialogClose} disabled={cleanupLoading}>
            {cleanupResult ? '关闭' : '取消'}
          </Button>
          {!cleanupResult && (
            <Button
              onClick={handleCleanup}
              variant="contained"
              disabled={cleanupLoading}
              sx={{
                bgcolor: '#FF6B6B',
                '&:hover': {
                  bgcolor: '#FF5252',
                },
              }}
            >
              {cleanupLoading ? '清理中...' : '确认清理'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default ToolsPage


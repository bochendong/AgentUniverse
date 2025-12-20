import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  TextField,
  Button,
  Divider,
  Alert,
  Tabs,
  Tab,
  CircularProgress,
  Collapse,
} from '@mui/material'
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Code as CodeIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material'

/**
 * InstructionsEditorInline Component
 * Inline expandable instructions editor
 */
function InstructionsEditorInline({ agentId, expanded, onToggle }) {
  const [instructions, setInstructions] = useState('')
  const [defaultInstructions, setDefaultInstructions] = useState('')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [tabValue, setTabValue] = useState(0) // 0: current, 1: default
  const [wasIncomplete, setWasIncomplete] = useState(false)

  useEffect(() => {
    if (expanded && agentId) {
      loadInstructions()
    }
  }, [expanded, agentId])

  const loadInstructions = async () => {
    try {
      setLoading(true)
      setError(null)
      const { getAgentInstructions } = await import('../api/client')
      const response = await getAgentInstructions(agentId)
      setInstructions(response.data.current_instructions || '')
      setDefaultInstructions(response.data.default_instructions || '')
      setWasIncomplete(response.data.was_incomplete || false)
    } catch (err) {
      console.error('Failed to load instructions:', err)
      setError(err.response?.data?.detail || 'Failed to load instructions')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setError(null)
      const { updateAgentInstructions } = await import('../api/client')
      await updateAgentInstructions(agentId, instructions)
      
      // Reload to get updated instructions
      await loadInstructions()
    } catch (err) {
      console.error('Failed to save instructions:', err)
      setError(err.response?.data?.detail || 'Failed to save instructions')
    } finally {
      setSaving(false)
    }
  }

  const handleResetToDefault = () => {
    if (window.confirm('确定要恢复到默认instructions吗？当前修改将被覆盖。')) {
      setInstructions(defaultInstructions)
      setTabValue(0) // Switch to current tab
    }
  }

  return (
    <Box sx={{ mt: 2 }}>
      <Collapse in={expanded}>
        <Box
          sx={{
            bgcolor: '#F5F5F7',
            borderRadius: 2,
            border: '1px solid rgba(0,0,0,0.1)',
            overflow: 'hidden',
          }}
        >
          {/* Header */}
          <Box
            sx={{
              p: 2,
              bgcolor: 'white',
              borderBottom: '1px solid rgba(0,0,0,0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CodeIcon sx={{ color: '#007AFF', fontSize: 20 }} />
              <Typography
                variant="subtitle1"
                sx={{
                  fontWeight: 600,
                  color: '#1D1D1F',
                }}
              >
                Advanced Mode - Instructions
              </Typography>
            </Box>
            <Button
              size="small"
              onClick={onToggle}
              sx={{
                color: '#86868B',
                textTransform: 'none',
                minWidth: 'auto',
                p: 0.5,
              }}
            >
              <ExpandLessIcon />
            </Button>
          </Box>

          {/* Content */}
          <Box sx={{ p: 2 }}>
            {wasIncomplete && (
              <Alert severity="info" sx={{ mb: 2 }}>
                检测到当前instructions不完整，已自动显示默认值。您可以编辑并保存以更新。
              </Alert>
            )}

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {/* Tabs */}
                <Tabs
                  value={tabValue}
                  onChange={(e, newValue) => setTabValue(newValue)}
                  sx={{
                    borderBottom: '1px solid rgba(0,0,0,0.1)',
                    '& .MuiTab-root': {
                      color: '#86868B',
                      textTransform: 'none',
                      fontWeight: 500,
                      '&.Mui-selected': {
                        color: '#1D1D1F',
                      },
                    },
                    '& .MuiTabs-indicator': {
                      bgcolor: '#007AFF',
                    },
                  }}
                >
                  <Tab label="当前 Instructions" />
                  <Tab label="默认 Instructions（只读）" />
                </Tabs>

                {/* Content Area */}
                <Box
                  sx={{
                    minHeight: '400px',
                    maxHeight: '600px',
                    overflow: 'hidden',
                    display: 'flex',
                    flexDirection: 'column',
                  }}
                >
                  {tabValue === 0 ? (
                    <TextField
                      multiline
                      fullWidth
                      value={instructions}
                      onChange={(e) => setInstructions(e.target.value)}
                      placeholder="输入agent的instructions..."
                      variant="outlined"
                      sx={{
                        flex: 1,
                        '& .MuiOutlinedInput-root': {
                          bgcolor: 'white',
                          color: '#1D1D1F',
                          fontFamily: 'Monaco, "Courier New", monospace',
                          fontSize: '0.875rem',
                          '& fieldset': {
                            borderColor: 'rgba(0,0,0,0.1)',
                          },
                          '&:hover fieldset': {
                            borderColor: 'rgba(0,0,0,0.2)',
                          },
                          '&.Mui-focused fieldset': {
                            borderColor: '#007AFF',
                          },
                        },
                      }}
                      InputProps={{
                        sx: {
                          height: '100%',
                          alignItems: 'flex-start',
                          '& textarea': {
                            overflow: 'auto !important',
                            height: '100% !important',
                          },
                        },
                      }}
                    />
                  ) : (
                    <Box
                      sx={{
                        flex: 1,
                        overflow: 'auto',
                        p: 2,
                        bgcolor: 'white',
                        borderRadius: 1,
                        border: '1px solid rgba(0,0,0,0.1)',
                      }}
                    >
                      <Typography
                        component="pre"
                        sx={{
                          fontFamily: 'Monaco, "Courier New", monospace',
                          fontSize: '0.875rem',
                          color: '#1D1D1F',
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                          margin: 0,
                        }}
                      >
                        {defaultInstructions || 'No default instructions available'}
                      </Typography>
                    </Box>
                  )}
                </Box>

                {/* Actions */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', pt: 1 }}>
                  <Button
                    onClick={handleResetToDefault}
                    disabled={loading || saving || !defaultInstructions}
                    startIcon={<RefreshIcon />}
                    sx={{
                      color: '#86868B',
                      textTransform: 'none',
                      '&:hover': {
                        bgcolor: 'rgba(0,0,0,0.05)',
                      },
                    }}
                  >
                    恢复默认值
                  </Button>
                  <Button
                    onClick={handleSave}
                    disabled={loading || saving}
                    variant="contained"
                    startIcon={saving ? <CircularProgress size={16} /> : <SaveIcon />}
                    sx={{
                      bgcolor: '#007AFF',
                      color: 'white',
                      textTransform: 'none',
                      '&:hover': {
                        bgcolor: '#0051D5',
                      },
                      '&:disabled': {
                        bgcolor: 'rgba(0,0,0,0.1)',
                        color: 'rgba(0,0,0,0.5)',
                      },
                    }}
                  >
                    {saving ? '保存中...' : '保存'}
                  </Button>
                </Box>
              </Box>
            )}
          </Box>
        </Box>
      </Collapse>
    </Box>
  )
}

export default InstructionsEditorInline


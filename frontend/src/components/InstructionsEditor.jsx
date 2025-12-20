import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Divider,
  Alert,
  Tabs,
  Tab,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material'
import {
  Close as CloseIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Code as CodeIcon,
} from '@mui/icons-material'
import { useTheme } from '../contexts/ThemeContext'

/**
 * InstructionsEditor Component
 * Allows users to view and edit agent instructions
 */
function InstructionsEditor({ agentId, open, onClose, onSave }) {
  const theme = useTheme()
  const isDark = theme?.mode === 'dark' || false
  const [instructions, setInstructions] = useState('')
  const [defaultInstructions, setDefaultInstructions] = useState('')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [tabValue, setTabValue] = useState(0) // 0: current, 1: default
  const [responseData, setResponseData] = useState(null) // Store full response

  useEffect(() => {
    if (open && agentId) {
      loadInstructions()
    }
  }, [open, agentId])

  const loadInstructions = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await (await import('../api/client')).getAgentInstructions(agentId)
      setResponseData(response.data)
      setInstructions(response.data.current_instructions || '')
      setDefaultInstructions(response.data.default_instructions || '')
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
      
      if (onSave) {
        onSave(instructions)
      }
      
      onClose()
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

  const handleClose = () => {
    setInstructions('')
    setDefaultInstructions('')
    setError(null)
    setTabValue(0)
    onClose()
  }

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          bgcolor: isDark ? '#343541' : '#FFFFFF',
          minHeight: '80vh',
          maxHeight: '90vh',
        },
      }}
    >
      <DialogTitle
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          pb: 1,
          borderBottom: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CodeIcon sx={{ color: isDark ? '#ececf1' : '#1D1D1F' }} />
          <Typography
            variant="h6"
            sx={{
              fontWeight: 600,
              color: isDark ? '#ececf1' : '#1D1D1F',
            }}
          >
            Agent Instructions (Advanced Mode)
          </Typography>
        </Box>
        <IconButton
          onClick={handleClose}
          sx={{
            color: isDark ? '#8e8ea0' : '#86868B',
            '&:hover': {
              bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
            },
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        {error && (
          <Alert severity="error" sx={{ m: 2, mb: 0 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flex: 1, p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {responseData?.was_incomplete && (
              <Alert severity="info" sx={{ m: 2, mb: 0 }}>
                检测到当前instructions不完整，已自动显示默认值。您可以编辑并保存以更新。
              </Alert>
            )}
            <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
            {/* Tabs */}
            <Tabs
              value={tabValue}
              onChange={(e, newValue) => setTabValue(newValue)}
              sx={{
                borderBottom: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
                '& .MuiTab-root': {
                  color: isDark ? '#8e8ea0' : '#86868B',
                  textTransform: 'none',
                  fontWeight: 500,
                  '&.Mui-selected': {
                    color: isDark ? '#ececf1' : '#1D1D1F',
                  },
                },
                '& .MuiTabs-indicator': {
                  bgcolor: isDark ? '#19c37d' : '#007AFF',
                },
              }}
            >
              <Tab label="当前 Instructions" />
              <Tab label="默认 Instructions（只读）" />
            </Tabs>

            {/* Content */}
            <Box sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
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
                      bgcolor: isDark ? '#40414f' : '#FFFFFF',
                      color: isDark ? '#ececf1' : '#1D1D1F',
                      fontFamily: 'Monaco, "Courier New", monospace',
                      fontSize: '0.875rem',
                      '& fieldset': {
                        borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                      },
                      '&:hover fieldset': {
                        borderColor: isDark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: isDark ? '#19c37d' : '#007AFF',
                      },
                    },
                    '& .MuiInputBase-input': {
                      overflow: 'auto',
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
                    bgcolor: isDark ? '#40414f' : '#F5F5F7',
                  }}
                >
                  <Typography
                    component="pre"
                    sx={{
                      fontFamily: 'Monaco, "Courier New", monospace',
                      fontSize: '0.875rem',
                      color: isDark ? '#ececf1' : '#1D1D1F',
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
          </Box>
          </>
        )}
      </DialogContent>

      <DialogActions
        sx={{
          p: 2,
          borderTop: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
          gap: 1,
        }}
      >
        <Button
          onClick={handleResetToDefault}
          disabled={loading || saving || !defaultInstructions}
          startIcon={<RefreshIcon />}
          sx={{
            color: isDark ? '#8e8ea0' : '#86868B',
            '&:hover': {
              bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
            },
          }}
        >
          恢复默认值
        </Button>
        <Box sx={{ flex: 1 }} />
        <Button
          onClick={handleClose}
          disabled={saving}
          sx={{
            color: isDark ? '#8e8ea0' : '#86868B',
            '&:hover': {
              bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
            },
          }}
        >
          取消
        </Button>
        <Button
          onClick={handleSave}
          disabled={loading || saving}
          variant="contained"
          startIcon={saving ? <CircularProgress size={16} /> : <SaveIcon />}
          sx={{
            bgcolor: isDark ? '#19c37d' : '#007AFF',
            color: 'white',
            '&:hover': {
              bgcolor: isDark ? '#16a269' : '#0051D5',
            },
            '&:disabled': {
              bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
              color: isDark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.5)',
            },
          }}
        >
          {saving ? '保存中...' : '保存'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default InstructionsEditor


import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  IconButton,
  TextField,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  Close as CloseIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Code as CodeIcon,
  Edit as EditIcon,
} from '@mui/icons-material'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

/**
 * AgentInstructionsSidebar Component
 * Sidebar that displays and allows editing of agent instructions
 * Displayed as a regular sidebar panel (can be closed)
 */
function AgentInstructionsSidebar({ agentId, onClose, onSave }) {
  const [instructions, setInstructions] = useState('')
  const [defaultInstructions, setDefaultInstructions] = useState('')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editInstructions, setEditInstructions] = useState('')
  const [wasIncomplete, setWasIncomplete] = useState(false)

  useEffect(() => {
    if (agentId) {
      loadInstructions()
    }
  }, [agentId])

  const loadInstructions = async () => {
    try {
      setLoading(true)
      setError(null)
      const { getAgentInstructions } = await import('../api/client')
      const response = await getAgentInstructions(agentId)
      const currentInstructions = response.data.current_instructions || ''
      setInstructions(currentInstructions)
      setEditInstructions(currentInstructions)
      setDefaultInstructions(response.data.default_instructions || '')
      setWasIncomplete(response.data.was_incomplete || false)
      setIsEditing(false)
    } catch (err) {
      console.error('Failed to load instructions:', err)
      setError(err.response?.data?.detail || 'Failed to load instructions')
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = () => {
    setEditInstructions(instructions)
    setIsEditing(true)
  }

  const handleCancelEdit = () => {
    setEditInstructions(instructions)
    setIsEditing(false)
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setError(null)
      const { updateAgentInstructions } = await import('../api/client')
      await updateAgentInstructions(agentId, editInstructions)
      
      // Update instructions and exit edit mode
      setInstructions(editInstructions)
      setIsEditing(false)
      
      if (onSave) {
        onSave(editInstructions)
      }
    } catch (err) {
      console.error('Failed to save instructions:', err)
      setError(err.response?.data?.detail || 'Failed to save instructions')
    } finally {
      setSaving(false)
    }
  }

  const handleResetToDefault = async () => {
    if (window.confirm('确定要恢复到默认instructions吗？当前修改将被覆盖。')) {
      try {
        setSaving(true)
        setError(null)
        const { updateAgentInstructions } = await import('../api/client')
        await updateAgentInstructions(agentId, defaultInstructions)
        
        // Update instructions
        setInstructions(defaultInstructions)
        setEditInstructions(defaultInstructions)
        setIsEditing(false)
        
        if (onSave) {
          onSave(defaultInstructions)
        }
      } catch (err) {
        console.error('Failed to reset instructions:', err)
        setError(err.response?.data?.detail || 'Failed to reset instructions')
      } finally {
        setSaving(false)
      }
    }
  }

  if (!agentId) {
    return null
  }

  return (
    <Paper
      sx={{
        width: '100%',
        bgcolor: 'white',
        borderRadius: 3,
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
        display: 'flex',
        flexDirection: 'column',
        minHeight: '600px',
      }}
    >
      <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
        {/* Header */}
        <Box
          sx={{
            p: 2,
            borderBottom: '1px solid rgba(0,0,0,0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CodeIcon sx={{ color: '#007AFF', fontSize: 20 }} />
            <Typography
              variant="h6"
              sx={{
                fontWeight: 600,
                color: '#1D1D1F',
              }}
            >
              Agent Instructions
            </Typography>
          </Box>
          {onClose && (
            <IconButton
              onClick={onClose}
              sx={{
                color: '#86868B',
                '&:hover': {
                  bgcolor: 'rgba(0,0,0,0.05)',
                },
              }}
            >
              <CloseIcon />
            </IconButton>
          )}
        </Box>

        {/* Content */}
        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
          {wasIncomplete && (
            <Alert severity="info" sx={{ m: 2, mb: 0 }}>
              检测到当前instructions不完整，已自动显示默认值。您可以编辑并保存以更新。
            </Alert>
          )}

          {error && (
            <Alert severity="error" sx={{ m: 2, mb: 0 }}>
              {error}
            </Alert>
          )}

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : isEditing ? (
            // Edit Mode
            <Box sx={{ display: 'flex', flexDirection: 'column', p: 2 }}>
              <TextField
                multiline
                fullWidth
                value={editInstructions}
                onChange={(e) => setEditInstructions(e.target.value)}
                placeholder="输入agent的instructions..."
                variant="outlined"
                    sx={{
                      mb: 2,
                      minHeight: '400px',
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
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                <Button
                  onClick={handleCancelEdit}
                  disabled={saving}
                  sx={{
                    color: '#86868B',
                    textTransform: 'none',
                    '&:hover': {
                      bgcolor: 'rgba(0,0,0,0.05)',
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
          ) : (
            // View Mode - Markdown render
            <Box sx={{ display: 'flex', flexDirection: 'column' }}>
              <Box
                sx={{
                  p: 2,
                  '& p': {
                    margin: '0.5em 0',
                    color: '#1D1D1F',
                    lineHeight: 1.75,
                  },
                  '& pre': {
                    bgcolor: '#F5F5F7',
                    borderRadius: 2,
                    padding: 2,
                    overflow: 'auto',
                    fontSize: '0.875rem',
                    fontFamily: 'Monaco, "Courier New", monospace',
                    margin: '1em 0',
                    border: '1px solid rgba(0,0,0,0.1)',
                    '& code': {
                      fontFamily: 'Consolas, Monaco, "Courier New", monospace',
                      bgcolor: 'transparent',
                    },
                  },
                  '& code': {
                    bgcolor: '#F5F5F7',
                    padding: '2px 6px',
                    borderRadius: 1,
                    fontSize: '0.9em',
                    fontFamily: 'Consolas, Monaco, "Courier New", monospace',
                    color: '#E83E8C',
                  },
                  '& ul, & ol': {
                    paddingLeft: '1.5em',
                    margin: '0.5em 0',
                  },
                  '& li': {
                    margin: '0.25em 0',
                  },
                  '& h1, & h2, & h3, & h4, & h5, & h6': {
                    marginTop: '1em',
                    marginBottom: '0.5em',
                    fontWeight: 600,
                    color: '#1D1D1F',
                  },
                  '& h1': { fontSize: '2em' },
                  '& h2': { fontSize: '1.5em' },
                  '& h3': { fontSize: '1.25em' },
                  '& blockquote': {
                    borderLeft: '4px solid #007AFF',
                    paddingLeft: '1em',
                    margin: '1em 0',
                    color: '#86868B',
                    fontStyle: 'italic',
                  },
                  '& table': {
                    borderCollapse: 'collapse',
                    width: '100%',
                    margin: '1em 0',
                    '& th, & td': {
                      border: '1px solid rgba(0,0,0,0.1)',
                      padding: '8px',
                    },
                    '& th': {
                      bgcolor: '#F5F5F7',
                      fontWeight: 600,
                    },
                  },
                }}
              >
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {instructions || 'No instructions available'}
                </ReactMarkdown>
              </Box>

              {/* Actions */}
              <Box
                sx={{
                  p: 2,
                  borderTop: '1px solid rgba(0,0,0,0.1)',
                  display: 'flex',
                  gap: 1,
                  justifyContent: 'flex-end',
                }}
              >
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
                  onClick={handleEdit}
                  disabled={loading || saving}
                  variant="contained"
                  startIcon={<EditIcon />}
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
                  修改
                </Button>
              </Box>
            </Box>
          )}
        </Box>
      </Box>
    </Paper>
  )
}

export default AgentInstructionsSidebar


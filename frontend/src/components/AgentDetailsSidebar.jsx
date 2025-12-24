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
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import {
  Close as CloseIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Code as CodeIcon,
  Edit as EditIcon,
  ExpandMore as ExpandMoreIcon,
  Build as BuildIcon,
  Info as InfoIcon,
} from '@mui/icons-material'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { getAgentInstructions, updateAgentInstructions, getAgentTools } from '../api/client'

/**
 * AgentDetailsSidebar Component
 * Displays agent details including tools and instructions
 * Both Tools and Instructions sections are collapsible
 */
function AgentDetailsSidebar({ agentId, onClose, onSave }) {
  const [instructions, setInstructions] = useState('')
  const [defaultInstructions, setDefaultInstructions] = useState('')
  const [tools, setTools] = useState([])
  const [loading, setLoading] = useState(false)
  const [toolsLoading, setToolsLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editInstructions, setEditInstructions] = useState('')
  const [wasIncomplete, setWasIncomplete] = useState(false)
  const [instructionsExpanded, setInstructionsExpanded] = useState(true)
  const [toolsExpanded, setToolsExpanded] = useState(true)

  useEffect(() => {
    if (agentId) {
      loadInstructions()
      loadTools()
    }
  }, [agentId])

  const loadInstructions = async () => {
    try {
      setLoading(true)
      setError(null)
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

  const loadTools = async () => {
    try {
      setToolsLoading(true)
      const response = await getAgentTools(agentId)
      setTools(response.data.tools || [])
    } catch (err) {
      console.error('Failed to load tools:', err)
      // Don't show error for tools, just log it
    } finally {
      setToolsLoading(false)
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
      await updateAgentInstructions(agentId, editInstructions)
      
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

  const handleReset = async () => {
    if (!window.confirm('确定要恢复默认值吗？这将覆盖当前的 instructions。')) {
      return
    }
    
    try {
      setSaving(true)
      setError(null)
      await updateAgentInstructions(agentId, defaultInstructions)
      
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
            <InfoIcon sx={{ color: '#007AFF', fontSize: 20 }} />
            <Typography
              variant="h6"
              sx={{
                fontWeight: 600,
                color: '#1D1D1F',
              }}
            >
              Agent Details
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
        <Box sx={{ display: 'flex', flexDirection: 'column', p: 2, overflowY: 'auto' }}>
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

          {/* Agent Tools Section */}
          <Accordion
            expanded={toolsExpanded}
            onChange={(e, isExpanded) => setToolsExpanded(isExpanded)}
            sx={{
              mb: 2,
              bgcolor: '#F5F5F7',
              '&:before': { display: 'none' },
              boxShadow: 'none',
              border: '1px solid rgba(0,0,0,0.06)',
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon sx={{ color: '#1D1D1F' }} />}
              sx={{
                '& .MuiAccordionSummary-content': {
                  my: 1,
                },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <BuildIcon sx={{ color: '#007AFF', fontSize: 18 }} />
                <Typography
                  sx={{
                    fontWeight: 600,
                    color: '#1D1D1F',
                  }}
                >
                  Agent Skills
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
            </AccordionSummary>
            <AccordionDetails>
              {toolsLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : tools.length === 0 ? (
                <Typography variant="body2" sx={{ color: '#86868B', fontStyle: 'italic' }}>
                  该 agent 没有 skills
                </Typography>
              ) : (
                <Box>
                  {tools.map((tool, index) => (
                    <Box
                      key={index}
                      sx={{
                        mb: 2,
                        pb: 2,
                        borderBottom: index < tools.length - 1 ? '1px solid rgba(0,0,0,0.06)' : 'none',
                      }}
                    >
                      <Typography
                        variant="subtitle2"
                        sx={{
                          fontWeight: 600,
                          color: '#1D1D1F',
                          mb: 0.5,
                        }}
                      >
                        {tool.name}
                      </Typography>
                      {tool.description && (
                        <Typography
                          variant="body2"
                          sx={{
                            color: '#86868B',
                            fontSize: '0.875rem',
                            whiteSpace: 'pre-wrap',
                            lineHeight: 1.5,
                          }}
                        >
                          {tool.description}
                        </Typography>
                      )}
                    </Box>
                  ))}
                </Box>
              )}
            </AccordionDetails>
          </Accordion>

          {/* Agent Instructions Section */}
          <Accordion
            expanded={instructionsExpanded}
            onChange={(e, isExpanded) => setInstructionsExpanded(isExpanded)}
            sx={{
              bgcolor: '#F5F5F7',
              '&:before': { display: 'none' },
              boxShadow: 'none',
              border: '1px solid rgba(0,0,0,0.06)',
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon sx={{ color: '#1D1D1F' }} />}
              sx={{
                '& .MuiAccordionSummary-content': {
                  my: 1,
                },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CodeIcon sx={{ color: '#007AFF', fontSize: 18 }} />
                <Typography
                  sx={{
                    fontWeight: 600,
                    color: '#1D1D1F',
                  }}
                >
                  Agent Instructions
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <CircularProgress />
                </Box>
              ) : isEditing ? (
                // Edit Mode
                <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                  <TextField
                    multiline
                    fullWidth
                    value={editInstructions}
                    onChange={(e) => setEditInstructions(e.target.value)}
                    placeholder="输入agent的instructions..."
                    minRows={10}
                    maxRows={20}
                    sx={{
                      mb: 2,
                      '& .MuiOutlinedInput-root': {
                        fontSize: '0.875rem',
                        fontFamily: 'monospace',
                      },
                    }}
                  />
                  <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                    <Button
                      variant="outlined"
                      onClick={handleCancelEdit}
                      disabled={saving}
                      sx={{
                        textTransform: 'none',
                      }}
                    >
                      取消
                    </Button>
                    <Button
                      variant="contained"
                      onClick={handleSave}
                      disabled={saving}
                      startIcon={saving ? <CircularProgress size={16} /> : <SaveIcon />}
                      sx={{
                        textTransform: 'none',
                        bgcolor: '#007AFF',
                        '&:hover': {
                          bgcolor: '#0051D5',
                        },
                      }}
                    >
                      保存
                    </Button>
                  </Box>
                </Box>
              ) : (
                // View Mode
                <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                  <Box
                    sx={{
                      p: 2,
                      bgcolor: 'white',
                      borderRadius: 2,
                      border: '1px solid rgba(0,0,0,0.06)',
                      mb: 2,
                      minHeight: '200px',
                    }}
                  >
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        p: ({ node, ...props }) => (
                          <Typography variant="body2" sx={{ mb: 1, color: '#1D1D1F', lineHeight: 1.6 }} {...props} />
                        ),
                        h1: ({ node, ...props }) => (
                          <Typography variant="h6" sx={{ mt: 2, mb: 1, fontWeight: 600 }} {...props} />
                        ),
                        h2: ({ node, ...props }) => (
                          <Typography variant="subtitle1" sx={{ mt: 2, mb: 1, fontWeight: 600 }} {...props} />
                        ),
                        h3: ({ node, ...props }) => (
                          <Typography variant="subtitle2" sx={{ mt: 1, mb: 0.5, fontWeight: 600 }} {...props} />
                        ),
                        code: ({ node, inline, ...props }) =>
                          inline ? (
                            <Typography
                              component="span"
                              sx={{
                                bgcolor: '#F5F5F7',
                                px: 0.5,
                                py: 0.25,
                                borderRadius: 1,
                                fontFamily: 'monospace',
                                fontSize: '0.875rem',
                              }}
                              {...props}
                            />
                          ) : (
                            <Box
                              component="pre"
                              sx={{
                                bgcolor: '#F5F5F7',
                                p: 1.5,
                                borderRadius: 1,
                                overflow: 'auto',
                                mb: 1,
                              }}
                              {...props}
                            />
                          ),
                      }}
                    >
                      {instructions || '暂无 instructions'}
                    </ReactMarkdown>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                    {defaultInstructions && defaultInstructions !== instructions && (
                      <Button
                        variant="outlined"
                        onClick={handleReset}
                        disabled={saving}
                        startIcon={<RefreshIcon />}
                        sx={{
                          textTransform: 'none',
                        }}
                      >
                        恢复默认值
                      </Button>
                    )}
                    <Button
                      variant="contained"
                      onClick={handleEdit}
                      startIcon={<EditIcon />}
                      sx={{
                        textTransform: 'none',
                        bgcolor: '#007AFF',
                        '&:hover': {
                          bgcolor: '#0051D5',
                        },
                      }}
                    >
                      修改
                    </Button>
                  </Box>
                </Box>
              )}
            </AccordionDetails>
          </Accordion>
        </Box>
      </Box>
    </Paper>
  )
}

export default AgentDetailsSidebar


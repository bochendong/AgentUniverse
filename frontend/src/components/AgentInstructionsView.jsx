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
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Code as CodeIcon,
  Edit as EditIcon,
} from '@mui/icons-material'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { getAgentInstructions, updateAgentInstructions } from '../api/client'

/**
 * AgentInstructionsView Component
 * Display and edit agent instructions
 */
function AgentInstructionsView({ agentId, onSave }) {
  const [instructions, setInstructions] = useState('')
  const [defaultInstructions, setDefaultInstructions] = useState('')
  const [templateInstructions, setTemplateInstructions] = useState('')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editInstructions, setEditInstructions] = useState('')
  const [wasIncomplete, setWasIncomplete] = useState(false)

  useEffect(() => {
    if (agentId) {
      loadInstructions()
    } else {
      setInstructions('')
      setDefaultInstructions('')
      setIsEditing(false)
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
      setTemplateInstructions(response.data.template_instructions || '')
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

  // Always render, even if no agentId

  return (
    <Paper
      sx={{
        p: 3,
        bgcolor: 'white',
        borderRadius: 3,
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
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
        {!isEditing && instructions && (
          <Box sx={{ display: 'flex', gap: 1 }}>
            {defaultInstructions && defaultInstructions !== instructions && (
              <Button
                variant="outlined"
                onClick={handleReset}
                disabled={saving}
                startIcon={<RefreshIcon />}
                size="small"
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
              size="small"
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
        )}
      </Box>

      {/* Content */}
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

      {!agentId ? (
        <Typography variant="body2" sx={{ color: '#86868B' }}>
          点击左侧层级图中的 agent 查看其 instructions
        </Typography>
      ) : loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : isEditing ? (
        // Edit Mode
        <Box>
          <TextField
            multiline
            fullWidth
            value={editInstructions}
            onChange={(e) => setEditInstructions(e.target.value)}
            placeholder="输入agent的instructions..."
            minRows={15}
            maxRows={25}
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
        // View Mode - Display template instructions with placeholders if available
        <Box
          sx={{
            p: 3,
            bgcolor: '#FFFFFF',
            borderRadius: 2,
            border: '1px solid rgba(0,0,0,0.06)',
            minHeight: '200px',
            '& p': {
              margin: '0.75em 0',
              color: '#1D1D1F',
              lineHeight: 1.75,
              fontSize: '0.9375rem',
            },
            '& p:first-of-type': {
              marginTop: 0,
            },
            '& p:last-of-type': {
              marginBottom: 0,
            },
            '& pre': {
              bgcolor: '#F5F5F7',
              borderRadius: 2,
              padding: '16px',
              overflowX: 'auto',
              fontSize: '0.875rem',
              fontFamily: 'Monaco, "Courier New", monospace',
              margin: '1em 0',
              border: '1px solid rgba(0,0,0,0.08)',
              lineHeight: 1.6,
              '& code': {
                fontFamily: 'Monaco, "Courier New", monospace',
                bgcolor: 'transparent',
                padding: 0,
                fontSize: 'inherit',
                color: '#1D1D1F',
              },
            },
            '& code': {
              bgcolor: '#F5F5F7',
              padding: '3px 6px',
              borderRadius: '4px',
              fontSize: '0.875rem',
              fontFamily: 'Monaco, "Courier New", monospace',
              color: '#E83E8C',
              border: '1px solid rgba(0,0,0,0.06)',
            },
            '& ul, & ol': {
              paddingLeft: '1.75em',
              margin: '0.75em 0',
              '& li': {
                margin: '0.5em 0',
                lineHeight: 1.75,
                color: '#1D1D1F',
                fontSize: '0.9375rem',
              },
            },
            '& h1, & h2, & h3, & h4, & h5, & h6': {
              marginTop: '1.5em',
              marginBottom: '0.75em',
              fontWeight: 600,
              color: '#1D1D1F',
              lineHeight: 1.4,
            },
            '& h1': { 
              fontSize: '1.75rem',
              marginTop: '1em',
              borderBottom: '2px solid rgba(0,0,0,0.08)',
              paddingBottom: '0.5em',
            },
            '& h2': { 
              fontSize: '1.5rem',
              borderBottom: '1px solid rgba(0,0,0,0.06)',
              paddingBottom: '0.4em',
            },
            '& h3': { 
              fontSize: '1.25rem',
            },
            '& h4': { 
              fontSize: '1.125rem',
            },
            '& blockquote': {
              borderLeft: '4px solid #007AFF',
              paddingLeft: '1em',
              marginLeft: 0,
              marginRight: 0,
              marginTop: '1em',
              marginBottom: '1em',
              paddingTop: '0.5em',
              paddingBottom: '0.5em',
              bgcolor: '#F5F5F7',
              borderRadius: '0 4px 4px 0',
              fontStyle: 'italic',
              color: '#1D1D1F',
              '& p': {
                margin: '0.5em 0',
              },
            },
            '& hr': {
              border: 'none',
              borderTop: '1px solid rgba(0,0,0,0.1)',
              margin: '2em 0',
            },
            '& table': {
              borderCollapse: 'collapse',
              width: '100%',
              margin: '1em 0',
              '& th, & td': {
                border: '1px solid rgba(0,0,0,0.1)',
                padding: '8px 12px',
                textAlign: 'left',
              },
              '& th': {
                bgcolor: '#F5F5F7',
                fontWeight: 600,
              },
            },
            '& a': {
              color: '#007AFF',
              textDecoration: 'none',
              '&:hover': {
                textDecoration: 'underline',
              },
            },
            '& strong': {
              fontWeight: 600,
              color: '#1D1D1F',
            },
            '& em': {
              fontStyle: 'italic',
            },
            // Highlight variable placeholders like {agents_list} or {notes}
            '& :not(pre) > code': {
              '&:has-text("{")': {
                // This won't work directly, we need to process the content
              },
            },
          }}
        >
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({ node, children, ...props }) => {
                // Helper function to process text and highlight placeholders
                const processText = (text) => {
                  if (typeof text !== 'string') return text
                  const parts = text.split(/(\{[a-z_]+\})/gi)
                  return parts.map((part, index) => {
                    const isPlaceholder = /^\{[a-z_]+\}$/i.test(part)
                    if (isPlaceholder) {
                      return (
                        <Box
                          key={index}
                          component="span"
                          sx={{
                            bgcolor: '#FFF3CD',
                            color: '#856404',
                            padding: '2px 6px',
                            borderRadius: '4px',
                            fontFamily: 'Monaco, "Courier New", monospace',
                            fontSize: '0.875rem',
                            fontWeight: 600,
                            border: '1px solid #FFE69C',
                            mx: 0.5,
                            display: 'inline-block',
                          }}
                        >
                          {part}
                        </Box>
                      )
                    }
                    return <React.Fragment key={index}>{part}</React.Fragment>
                  })
                }
                
                // Process children recursively
                const processChildren = (children) => {
                  if (typeof children === 'string') {
                    return processText(children)
                  }
                  if (Array.isArray(children)) {
                    return children.map((child, index) => {
                      if (typeof child === 'string') {
                        return <React.Fragment key={index}>{processText(child)}</React.Fragment>
                      }
                      if (React.isValidElement(child)) {
                        return React.cloneElement(child, { key: index }, processChildren(child.props.children))
                      }
                      return <React.Fragment key={index}>{child}</React.Fragment>
                    })
                  }
                  return children
                }
                
                return <Typography component="p" variant="body2" {...props}>{processChildren(children)}</Typography>
              },
              h1: ({ node, ...props }) => (
                <Typography component="h1" variant="h5" {...props} />
              ),
              h2: ({ node, ...props }) => (
                <Typography component="h2" variant="h6" {...props} />
              ),
              h3: ({ node, ...props }) => (
                <Typography component="h3" variant="subtitle1" {...props} />
              ),
              h4: ({ node, ...props }) => (
                <Typography component="h4" variant="subtitle2" {...props} />
              ),
              code: ({ node, inline, className, children, ...props }) => {
                const match = /language-(\w+)/.exec(className || '')
                if (!inline && match) {
                  return (
                    <Box
                      component="pre"
                      sx={{
                        bgcolor: '#F5F5F7',
                        borderRadius: 2,
                        padding: '16px',
                        overflowX: 'auto',
                        fontSize: '0.875rem',
                        fontFamily: 'Monaco, "Courier New", monospace',
                        margin: '1em 0',
                        border: '1px solid rgba(0,0,0,0.08)',
                        lineHeight: 1.6,
                      }}
                      {...props}
                    >
                      <code>{children}</code>
                    </Box>
                  )
                }
                return (
                  <Typography
                    component="code"
                    sx={{
                      bgcolor: '#F5F5F7',
                      padding: '3px 6px',
                      borderRadius: '4px',
                      fontSize: '0.875rem',
                      fontFamily: 'Monaco, "Courier New", monospace',
                      color: '#E83E8C',
                      border: '1px solid rgba(0,0,0,0.06)',
                    }}
                    {...props}
                  >
                    {children}
                  </Typography>
                )
              },
            }}
          >
            {/* Use template instructions if available (with placeholders), otherwise use current instructions */}
            {templateInstructions || instructions || '暂无 instructions'}
          </ReactMarkdown>
        </Box>
      )}
    </Paper>
  )
}

export default AgentInstructionsView


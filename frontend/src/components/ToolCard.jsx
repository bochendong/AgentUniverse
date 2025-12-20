import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Box, Card, CardContent, Typography, Chip, Button, Collapse, IconButton } from '@mui/material'
import { Build as BuildIcon, SmartToy as AgentIcon, Info as InfoIcon, ExpandMore as ExpandMoreIcon, ExpandLess as ExpandLessIcon } from '@mui/icons-material'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

/**
 * ToolCard Component - Display information about a function tool or agent_as_tool
 */
function ToolCard({ tool }) {
  const navigate = useNavigate()
  const isAgentAsTool = tool.tool_type === 'agent_as_tool'
  const [usageExpanded, setUsageExpanded] = useState(false)

  const handleViewDetails = () => {
    if (isAgentAsTool) {
      navigate(`/tools/${tool.id}`)
    }
  }
  const getAgentTypeColor = (agentType) => {
    const colors = {
      'BaseAgent': '#007AFF',
      'MasterAgent': '#007AFF',
      'TopLevelAgent': '#FF6B6B',
      'NoteBookAgent': '#34C759',
      'AsToolAgent': '#34C759',
      'SpecializedAgent': '#34C759', // Backward compatibility
    }
    return colors[agentType] || '#86868B'
  }

  const getAgentTypeLabel = (agentType) => {
    if (agentType === 'AsToolAgent' || agentType === 'SpecializedAgent') {
      return 'As Tool Agent'
    }
    return agentType
  }

  const getOutputTypeColor = (outputType) => {
    if (outputType === 'str') return '#007AFF'
    if (outputType === 'dict' || outputType === 'Dict') return '#FF9500'
    if (outputType === 'bool' || outputType === 'boolean') return '#34C759'
    return '#86868B'
  }

  return (
    <Card
      sx={{
        height: '100%',
        bgcolor: '#FFFFFF',
        border: isAgentAsTool ? '2px solid #34C759' : '1px solid rgba(0,0,0,0.08)',
        borderRadius: 2,
        transition: 'all 0.2s',
        cursor: isAgentAsTool ? 'pointer' : 'default',
        '&:hover': {
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          transform: 'translateY(-2px)',
        },
      }}
      onClick={isAgentAsTool ? handleViewDetails : undefined}
    >
      <CardContent sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
          <Box
            sx={{
              bgcolor: isAgentAsTool ? '#34C75915' : '#007AFF15',
              borderRadius: 2,
              p: 1.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {isAgentAsTool ? (
              <AgentIcon sx={{ color: '#34C759', fontSize: 24 }} />
            ) : (
            <BuildIcon sx={{ color: '#007AFF', fontSize: 24 }} />
            )}
          </Box>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 600,
                color: '#1D1D1F',
                mb: 0.5,
                fontSize: '1.1rem',
              }}
            >
              {tool.name}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
              {isAgentAsTool && (
                <Chip
                  label="Agent as Tool"
                  size="small"
                  sx={{
                    bgcolor: '#34C75915',
                    color: '#34C759',
                    fontWeight: 600,
                    fontSize: '0.7rem',
                    height: 22,
                  }}
                />
              )}
              <Chip
                label={getAgentTypeLabel(tool.agent_type)}
                size="small"
                sx={{
                  bgcolor: `${getAgentTypeColor(tool.agent_type)}15`,
                  color: getAgentTypeColor(tool.agent_type),
                  fontWeight: 500,
                  fontSize: '0.7rem',
                  height: 22,
                }}
              />
              <Chip
                label={`Output: ${tool.output_type}`}
                size="small"
                sx={{
                  bgcolor: `${getOutputTypeColor(tool.output_type)}15`,
                  color: getOutputTypeColor(tool.output_type),
                  fontWeight: 500,
                  fontSize: '0.7rem',
                  height: 22,
                }}
              />
            </Box>
          </Box>
        </Box>

        {/* Description */}
        {tool.description && (
          <Typography
            variant="body2"
            sx={{
              color: '#86868B',
              mb: 2,
              lineHeight: 1.6,
            }}
          >
            {tool.description}
          </Typography>
        )}

        {/* Task */}
        {tool.task && (
          <Box sx={{ mb: 2 }}>
            <Typography
              variant="caption"
              sx={{
                color: '#1D1D1F',
                fontWeight: 600,
                fontSize: '0.75rem',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                mb: 0.5,
                display: 'block',
              }}
            >
              任务
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: '#1D1D1F',
                lineHeight: 1.6,
              }}
            >
              {tool.task}
            </Typography>
          </Box>
        )}

        {/* Call Method */}
        {tool.input_params && Object.keys(tool.input_params).length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography
              variant="caption"
              sx={{
                color: '#1D1D1F',
                fontWeight: 600,
                fontSize: '0.75rem',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                mb: 1,
                display: 'block',
              }}
            >
              调用方法
            </Typography>
            <Box
              sx={{
                p: 1.5,
                bgcolor: '#F5F5F7',
                borderRadius: 1.5,
                border: '1px solid rgba(0,0,0,0.06)',
              }}
            >
              <Typography
                variant="body2"
                sx={{
                  fontFamily: 'monospace',
                  color: '#1D1D1F',
                  fontSize: '0.875rem',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {tool.name}(
                {Object.entries(tool.input_params)
                  .map(([paramName, paramInfo]) => {
                    const optional = !paramInfo.required ? '=None' : ''
                    return `${paramName}${optional}`
                  })
                  .join(', ')}
                )
              </Typography>
            </Box>
          </Box>
        )}

        {/* Output */}
        {tool.output_type && (
          <Box sx={{ mb: 2 }}>
            <Typography
              variant="caption"
              sx={{
                color: '#1D1D1F',
                fontWeight: 600,
                fontSize: '0.75rem',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                mb: 1,
                display: 'block',
              }}
            >
              输出
            </Typography>
            <Box
              sx={{
                p: 1.5,
                bgcolor: '#F5F5F7',
                borderRadius: 1.5,
                border: '1px solid rgba(0,0,0,0.06)',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 600,
                    color: '#1D1D1F',
                    fontFamily: 'monospace',
                    fontSize: '0.875rem',
                  }}
                >
                  {tool.output_type}
                </Typography>
                <Chip
                  label={tool.output_type}
                  size="small"
                  sx={{
                    bgcolor: `${getOutputTypeColor(tool.output_type)}15`,
                    color: getOutputTypeColor(tool.output_type),
                    fontWeight: 500,
                    fontSize: '0.65rem',
                    height: 20,
                  }}
                />
              </Box>
              {tool.output_description && (
                <Typography
                  variant="body2"
                  sx={{
                    color: '#86868B',
                    fontSize: '0.8rem',
                    mt: 0.5,
                  }}
                >
                  {tool.output_description}
                </Typography>
              )}
            </Box>
          </Box>
        )}

        {/* Input Parameters */}
        {tool.input_params && Object.keys(tool.input_params).length > 0 && (
          <Box>
            <Typography
              variant="caption"
              sx={{
                color: '#1D1D1F',
                fontWeight: 600,
                fontSize: '0.75rem',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                mb: 1,
                display: 'block',
              }}
            >
              输入参数
            </Typography>
            {Object.entries(tool.input_params).map(([paramName, paramInfo]) => (
              <Box
                key={paramName}
                sx={{
                  mb: 1.5,
                  pb: 1.5,
                  borderBottom: '1px solid rgba(0,0,0,0.06)',
                  '&:last-child': {
                    borderBottom: 'none',
                    mb: 0,
                    pb: 0,
                  },
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 600,
                      color: '#1D1D1F',
                      fontFamily: 'monospace',
                      fontSize: '0.875rem',
                    }}
                  >
                    {paramName}
                  </Typography>
                  <Chip
                    label={paramInfo.type || 'unknown'}
                    size="small"
                    sx={{
                      bgcolor: '#007AFF15',
                      color: '#007AFF',
                      fontWeight: 500,
                      fontSize: '0.65rem',
                      height: 18,
                    }}
                  />
                  {paramInfo.required && (
                    <Chip
                      label="必需"
                      size="small"
                      sx={{
                        bgcolor: '#FF6B6B15',
                        color: '#FF6B6B',
                        fontWeight: 500,
                        fontSize: '0.65rem',
                        height: 18,
                      }}
                    />
                  )}
                </Box>
                {paramInfo.description && (
                  <Typography
                    variant="body2"
                    sx={{
                      color: '#86868B',
                      fontSize: '0.8rem',
                      ml: 0,
                    }}
                  >
                    {paramInfo.description}
                  </Typography>
                )}
              </Box>
            ))}
          </Box>
        )}

        {/* Usage Documentation */}
        {tool.usage_documentation && (
          <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid rgba(0,0,0,0.08)' }}>
            <Button
              fullWidth
              variant="text"
              size="small"
              onClick={(e) => {
                e.stopPropagation()
                setUsageExpanded(!usageExpanded)
              }}
              endIcon={usageExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              sx={{
                justifyContent: 'space-between',
                color: '#007AFF',
                textTransform: 'none',
                fontWeight: 500,
                '&:hover': {
                  bgcolor: '#007AFF10',
                },
              }}
            >
              使用说明
            </Button>
            <Collapse in={usageExpanded} timeout="auto" unmountOnExit>
              <Box
                sx={{
                  mt: 2,
                  p: 2,
                  bgcolor: '#F5F5F7',
                  borderRadius: 1.5,
                  border: '1px solid rgba(0,0,0,0.06)',
                  '& h3': {
                    fontSize: '1rem',
                    fontWeight: 600,
                    color: '#1D1D1F',
                    mb: 1,
                    mt: 0,
                  },
                  '& p': {
                    margin: '0.5em 0',
                    color: '#1D1D1F',
                    lineHeight: 1.6,
                  },
                  '& code': {
                    bgcolor: 'white',
                    padding: '2px 6px',
                    borderRadius: 1,
                    fontSize: '0.9em',
                    fontFamily: 'monospace',
                    color: '#E83E8C',
                  },
                  '& pre': {
                    bgcolor: 'white',
                    borderRadius: 1,
                    padding: '12px',
                    overflow: 'auto',
                    fontSize: '0.875rem',
                    fontFamily: 'monospace',
                    margin: '0.5em 0',
                    border: '1px solid rgba(0,0,0,0.1)',
                    '& code': {
                      bgcolor: 'transparent',
                      padding: 0,
                    },
                  },
                  '& ul, & ol': {
                    paddingLeft: '1.5em',
                    margin: '0.5em 0',
                  },
                  '& li': {
                    margin: '0.25em 0',
                    color: '#1D1D1F',
                  },
                  '& strong': {
                    color: '#1D1D1F',
                    fontWeight: 600,
                  },
                }}
              >
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {tool.usage_documentation}
                </ReactMarkdown>
              </Box>
            </Collapse>
          </Box>
        )}

        {/* Agent as Tool - View Details Button */}
        {isAgentAsTool && (
          <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid rgba(0,0,0,0.08)' }}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<InfoIcon />}
              onClick={(e) => {
                e.stopPropagation()
                handleViewDetails()
              }}
              sx={{
                width: '100%',
                borderColor: '#34C759',
                color: '#34C759',
                '&:hover': {
                  borderColor: '#34C759',
                  bgcolor: '#34C75915',
                },
              }}
            >
              查看 Agent 详情
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default ToolCard


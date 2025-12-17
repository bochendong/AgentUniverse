import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Container,
  Box,
  Typography,
  CircularProgress,
  Alert,
  Paper,
  Chip,
  Button,
  Divider,
  Grid,
  Card,
  CardContent,
} from '@mui/material'
import {
  ArrowBack as BackIcon,
  MenuBook as NotebookIcon,
  AccountTree as HierarchyIcon,
  SmartToy as AgentIcon,
  Warning as WarningIcon,
  CallSplit as SplitIcon,
} from '@mui/icons-material'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import rehypeRaw from 'rehype-raw'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { prism } from 'react-syntax-highlighter/dist/esm/styles/prism'
import 'katex/dist/katex.min.css'
import { getAgent, getNotebook, getNotebookContent, getAgentHierarchy, splitNotebook } from '../api/client'
import AgentAvatar from '../components/AgentAvatar'
import NotebookContent from '../components/notebook/NotebookContent'

/**
 * Parse agent_card text format to extract description and outline
 */
function parseAgentCard(agentCardText) {
  if (!agentCardText || typeof agentCardText !== 'string') {
    return { description: '', outline: '' }
  }

  const lines = agentCardText.split('\n')
  let description = ''
  let outline = ''
  let currentSection = null
  let inDescription = false
  let inOutline = false

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    
    // Check for description section
    if (line.includes('📝 描述:') || line.includes('📝 描述')) {
      inDescription = true
      inOutline = false
      continue
    }
    
    // Check for outline section
    if (line.includes('📋 大纲:') || line.includes('📋 大纲')) {
      inDescription = false
      inOutline = true
      continue
    }
    
    // Skip separator lines (but not description lines that start with "-")
    if (line.startsWith('=') || (line.startsWith('-') && line.length === 60)) {
      continue
    }
    
    // Skip ID and Parent ID lines
    if (line.startsWith('ID:') || line.startsWith('Parent ID:') || line.startsWith('MasterAgent:')) {
      continue
    }
    
    // Collect description lines
    if (inDescription && line && !line.startsWith('📋')) {
      if (description) description += '\n'
      description += line.replace(/^   /, '') // Remove leading spaces
    }
    
    // Collect outline lines
    if (inOutline && line && !line.startsWith('📝')) {
      if (outline) outline += '\n'
      outline += line
    }
  }

  return {
    description: description.trim(),
    outline: outline.trim(),
  }
}

/**
 * Agent Detail Page - 苹果风格
 * 根据agent类型显示不同内容：
 * - Notebook Agent: 显示笔记内容
 * - Top/Master Agent: 显示层级关系
 */
function AgentDetailPage() {
  const { agentId } = useParams()
  const navigate = useNavigate()
  const [agent, setAgent] = useState(null)
  const [notebook, setNotebook] = useState(null)
  const [notebookContent, setNotebookContent] = useState(null)
  const [hierarchy, setHierarchy] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [splitting, setSplitting] = useState(false)

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        
        // First, get agent info to determine type
        const agentRes = await getAgent(agentId)
        setAgent(agentRes.data)

        // 判断是否是master/top agent
        const isMasterAgent = agentRes.data?.metadata?.is_master_agent || false
        const isTopLevelAgent = agentRes.data?.agent_type === 'top_level_agent'
        const isNotebookAgent = agentRes.data?.metadata?.is_notebook_agent || agentRes.data?.agent_type === 'notebook'

        if (isMasterAgent || isTopLevelAgent) {
          // 加载层级关系
          try {
            const hierarchyRes = await getAgentHierarchy(agentRes.data.id)
            setHierarchy(hierarchyRes.data)
          } catch (err) {
            console.error('Failed to load hierarchy:', err)
          }
        } else if (isNotebookAgent) {
          // Only load notebook data if it's actually a notebook agent
          try {
            const [notebookRes, contentRes] = await Promise.all([
              getNotebook(agentId).catch(() => null),
              getNotebookContent(agentId).catch(() => null),
            ])
            setNotebook(notebookRes?.data || null)
            if (contentRes?.data) {
              // Support both structured and markdown formats
              setNotebookContent(contentRes.data)
            }
          } catch (err) {
            console.error('Failed to load notebook data:', err)
          }
        }
      } catch (err) {
        console.error('Failed to load agent:', err)
        setError(err.response?.data?.detail || 'Failed to load agent')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [agentId])

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

  if (error || !agent) {
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
          <Alert severity="error" sx={{ mb: 3 }}>
            {error || 'Agent not found'}
          </Alert>
          <Button startIcon={<BackIcon />} onClick={() => navigate('/agents')}>
            Back to Agents
          </Button>
        </Container>
      </Box>
    )
  }

  const isMasterAgent = agent.metadata?.is_master_agent || false
  const isTopLevelAgent = agent.agent_type === 'top_level_agent'

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        bgcolor: '#F5F5F7',
        overflowY: 'auto',
        overflowX: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Main Content - Left/Right Layout */}
      <Box
        sx={{
          flex: 1,
          minHeight: 0,
        }}
      >
        <Container
          maxWidth="xl"
          sx={{
            display: 'flex',
            gap: 3,
            py: 3,
            alignItems: 'flex-start',
          }}
        >
          {/* Left Side - Agent Card */}
          <Box
            sx={{
              width: { xs: '100%', md: '400px' },
              flexShrink: 0,
            }}
          >
            {/* Agent Card - Combined */}
            <Paper
              sx={{
                p: 3,
                bgcolor: 'white',
                borderRadius: 3,
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
              }}
            >
              {/* Agent Avatar and Tags */}
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
                <AgentAvatar 
                  seed={agent.avatar_seed} 
                  size={80}
                  sx={{
                    border: `3px solid ${
                      isTopLevelAgent
                        ? '#FF6B6B30'
                        : isMasterAgent
                        ? '#4ECDC430'
                        : '#95E1D330'
                    }`,
                    boxShadow: `0 4px 12px ${
                      isTopLevelAgent
                        ? '#FF6B6B20'
                        : isMasterAgent
                        ? '#4ECDC420'
                        : '#95E1D320'
                    }`,
                    mb: 2,
                  }}
                />
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'center' }}>
                  {isTopLevelAgent && (
                    <Chip
                      label="Top Level"
                      size="small"
                      sx={{
                        bgcolor: '#FF6B6B15',
                        color: '#FF6B6B',
                        fontWeight: 500,
                      }}
                    />
                  )}
                  {isMasterAgent && (
                    <Chip
                      label="Master"
                      size="small"
                      sx={{
                        bgcolor: '#007AFF15',
                        color: '#007AFF',
                        fontWeight: 500,
                      }}
                    />
                  )}
                  {!isTopLevelAgent && !isMasterAgent && (
                    <Chip
                      label="Notebook"
                      size="small"
                      sx={{
                        bgcolor: '#34C75915',
                        color: '#34C759',
                        fontWeight: 500,
                      }}
                    />
                  )}
                </Box>
              </Box>

              {/* Divider */}
              <Divider sx={{ mb: 3, borderColor: 'rgba(0,0,0,0.06)' }} />

              {/* Agent Card Header */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <AgentIcon sx={{ color: '#007AFF', fontSize: 20 }} />
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 600,
                    color: '#1D1D1F',
                    fontSize: '1.1rem',
                  }}
                >
                  Agent Card
                </Typography>
              </Box>

              {/* Display agent_card content */}
              {agent.agent_card ? (
                <Box>
                  {/* Title */}
                  <Box sx={{ mb: 2 }}>
                    <Typography
                      variant="h6"
                      sx={{
                        fontWeight: 600,
                        color: '#1D1D1F',
                        fontSize: '1.1rem',
                        mb: 1,
                      }}
                    >
                      {agent.agent_type === 'master' ? '👑' : '📓'} {agent.agent_card.title || (agent.agent_type === 'master' ? 'Master Agent' : '未命名笔记本')}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, mb: 1 }}>
                      <Typography variant="caption" sx={{ color: '#86868B', fontSize: '0.75rem' }}>
                        ID: {agent.agent_card.agent_id?.substring(0, 8)}...
                      </Typography>
                      {agent.agent_card.parent_agent_id && (
                        <Typography variant="caption" sx={{ color: '#86868B', fontSize: '0.75rem' }}>
                          Parent ID: {agent.agent_card.parent_agent_id.substring(0, 8)}...
                        </Typography>
                      )}
                    </Box>
                  </Box>

                  {/* Description */}
                  {agent.agent_card.description && (
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant="subtitle2"
                        sx={{
                          color: '#86868B',
                          fontWeight: 600,
                          mb: 1.5,
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px',
                          fontSize: '0.7rem',
                        }}
                      >
                        {agent.agent_type === 'master' ? '📚 下辖笔记本简介' : '📝 描述'}
                      </Typography>
                      {agent.agent_type === 'master' ? (
                        // MasterAgent: 显示格式化的笔记本列表
                        <Box>
                          {(() => {
                            // 确保 description 是字符串
                            const description = typeof agent.agent_card.description === 'string' 
                              ? agent.agent_card.description 
                              : String(agent.agent_card.description || '')
                            
                            // 解析 description，提取笔记本名称（过滤掉 MasterAgent）
                            const lines = description.split('\n').filter(line => line.trim().startsWith('-'))
                            const notebookNames = lines
                              .map(line => {
                                // 提取名称：格式为 "- {title}: {desc}" 或 "- {title}"
                                const match = line.trim().match(/^-\s*(.+?)(?:\s*:|$)/)
                                return match ? match[1].trim() : line.trim().replace(/^-\s*/, '')
                              })
                              .filter(name => !name.includes('管理') && !name.includes('个子Agent')) // 过滤掉 MasterAgent
                            
                            if (notebookNames.length === 0) {
                              return (
                                <Typography
                                  variant="body2"
                                  sx={{
                                    color: '#86868B',
                                    fontStyle: 'italic',
                                  }}
                                >
                                  暂无下辖笔记本
                                </Typography>
                              )
                            }
                            
                            return (
                              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                {notebookNames.map((name, index) => (
                                  <Typography
                                    key={index}
                                    variant="body2"
                                    sx={{
                                      color: '#1D1D1F',
                                      lineHeight: 1.6,
                                      pl: 1,
                                    }}
                                  >
                                    • {name}
                                  </Typography>
                                ))}
                              </Box>
                            )
                          })()}
                        </Box>
                      ) : (
                        // NotebookAgent: 显示原始描述
                        <Typography
                          variant="body2"
                          sx={{
                            color: '#1D1D1F',
                            lineHeight: 1.6,
                            whiteSpace: 'pre-line',
                          }}
                        >
                          {agent.agent_card.description}
                        </Typography>
                      )}
                    </Box>
                  )}

                  {/* Outline */}
                  {agent.agent_card.outline && Object.keys(agent.agent_card.outline).length > 0 && (
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant="subtitle2"
                        sx={{
                          color: '#86868B',
                          fontWeight: 600,
                          mb: 1.5,
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px',
                          fontSize: '0.7rem',
                        }}
                      >
                        📋 大纲
                      </Typography>
                      <Box
                        sx={{
                          p: 2.5,
                          bgcolor: '#F5F5F7',
                          borderRadius: 2,
                          border: '1px solid rgba(0,0,0,0.06)',
                        }}
                      >
                        <Typography variant="body2" sx={{ color: '#86868B', mb: 2, fontSize: '0.8rem' }}>
                          共 {Object.keys(agent.agent_card.outline).length} 个章节:
                        </Typography>
                        {Object.entries(agent.agent_card.outline).map(([sectionTitle, sectionDescription], index) => (
                          <Box key={index} sx={{ mb: 2 }}>
                            <Typography
                              variant="body2"
                              sx={{
                                fontWeight: 600,
                                color: '#1D1D1F',
                                mb: 0.5,
                                fontSize: '0.9rem',
                              }}
                            >
                              {index + 1}. {sectionTitle}
                            </Typography>
                            {sectionDescription && (
                              <Typography
                                variant="body2"
                                sx={{
                                  color: '#86868B',
                                  fontSize: '0.85rem',
                                  lineHeight: 1.6,
                                  whiteSpace: 'pre-line',
                                  pl: 2,
                                }}
                              >
                                └─ {sectionDescription}
                              </Typography>
                            )}
                          </Box>
                        ))}
                      </Box>
                    </Box>
                  )}
                </Box>
              ) : (
                <Box
                  sx={{
                    textAlign: 'center',
                    py: 3,
                    color: '#86868B',
                  }}
                >
                  <Typography variant="body2">
                    No agent card available
                  </Typography>
                </Box>
              )}
            </Paper>
          </Box>

          {/* Right Side - Notebook Content or Hierarchy */}
          <Box
            sx={{
              flex: 1,
              minWidth: 0,
            }}
          >
            {isMasterAgent || isTopLevelAgent ? (
              // Hierarchy View for Master/Top Agents
              <Paper
                sx={{
                  p: 3,
                  bgcolor: 'white',
                  borderRadius: 3,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                  <HierarchyIcon sx={{ color: '#007AFF' }} />
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 600,
                      color: '#1D1D1F',
                    }}
                  >
                    Hierarchy Structure
                  </Typography>
                </Box>

                <Box>
                  {hierarchy && hierarchy.children && hierarchy.children.length > 0 ? (
                    <Box>
                      <Typography variant="body2" sx={{ color: '#86868B', mb: 3 }}>
                        This agent manages {hierarchy.children.length} child agent(s)
                      </Typography>
                      <Grid container spacing={2}>
                        {hierarchy.children.map((child, index) => {
                          const isChildMaster = child.agent_type === 'master' || child.metadata?.is_master_agent
                          const isChildNotebook = child.agent_type === 'notebook' || child.metadata?.is_notebook_agent
                          const parsedCard = child.agent_card ? parseAgentCard(child.agent_card) : null
                          const childDescription = child.description || parsedCard?.description || ''
                          const childOutline = parsedCard?.outline || child.content_stats?.outline || ''
                          
                          return (
                            <Grid item xs={12} sm={6} md={4} key={index}>
                              <Card
                                sx={{
                                  bgcolor: '#F5F5F7',
                                  border: '1px solid rgba(0,0,0,0.08)',
                                  borderRadius: 2,
                                  transition: 'all 0.2s',
                                  cursor: 'pointer',
                                  height: '100%',
                                  display: 'flex',
                                  flexDirection: 'column',
                                  '&:hover': {
                                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                                    transform: 'translateY(-2px)',
                                  },
                                }}
                                onClick={() => {
                                  if (child.notebook_id || child.id) {
                                    navigate(`/agents/${child.notebook_id || child.id}`)
                                  }
                                }}
                              >
                                <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, mb: 1.5 }}>
                                    <AgentAvatar
                                      seed={child.id || child.notebook_id || child.agent_name || child.name}
                                      size={40}
                                    />
                                    <Box sx={{ flex: 1, minWidth: 0 }}>
                                      <Typography
                                        variant="subtitle1"
                                        sx={{
                                          fontWeight: 600,
                                          color: '#1D1D1F',
                                          fontSize: '0.9rem',
                                          overflow: 'hidden',
                                          textOverflow: 'ellipsis',
                                          whiteSpace: 'nowrap',
                                        }}
                                      >
                                        {child.agent_name || child.name || 'Child Agent'}
                                      </Typography>
                                    </Box>
                                  </Box>
                                  
                                  {child.notebook_title && (
                                    <Typography
                                      variant="body2"
                                      sx={{
                                        color: '#1D1D1F',
                                        mb: 1,
                                        fontWeight: 500,
                                      }}
                                    >
                                      {child.notebook_title}
                                    </Typography>
                                  )}
                                  
                                  {/* Description */}
                                  {childDescription && (
                                    <Box sx={{ mb: 1.5 }}>
                                      <Typography
                                        variant="caption"
                                        sx={{
                                          color: '#86868B',
                                          fontWeight: 600,
                                          mb: 0.5,
                                          display: 'block',
                                          textTransform: 'uppercase',
                                          fontSize: '0.65rem',
                                        }}
                                      >
                                        📝 描述
                                      </Typography>
                                      <Typography
                                        variant="body2"
                                        sx={{
                                          color: '#1D1D1F',
                                          fontSize: '0.8rem',
                                          lineHeight: 1.5,
                                          display: '-webkit-box',
                                          WebkitLineClamp: 3,
                                          WebkitBoxOrient: 'vertical',
                                          overflow: 'hidden',
                                        }}
                                      >
                                        {childDescription}
                                      </Typography>
                                    </Box>
                                  )}
                                  
                                  {/* Outline for Notebook agents only */}
                                  {isChildNotebook && childOutline && (
                                    <Box sx={{ mb: 1.5 }}>
                                      <Typography
                                        variant="caption"
                                        sx={{
                                          color: '#86868B',
                                          fontWeight: 600,
                                          mb: 0.5,
                                          display: 'block',
                                          textTransform: 'uppercase',
                                          fontSize: '0.65rem',
                                        }}
                                      >
                                        📋 大纲
                                      </Typography>
                                      <Box
                                        sx={{
                                          p: 1.5,
                                          bgcolor: 'white',
                                          borderRadius: 1.5,
                                          border: '1px solid rgba(0,0,0,0.06)',
                                          maxHeight: '120px',
                                          overflow: 'auto',
                                        }}
                                      >
                                        {childOutline.split('\n').slice(0, 5).map((line, lineIndex) => {
                                          if (!line.trim()) return null
                                          
                                          const sectionMatch = line.match(/^(\d+)\.\s+(.+)$/)
                                          if (sectionMatch) {
                                            return (
                                              <Typography
                                                key={lineIndex}
                                                variant="caption"
                                                sx={{
                                                  fontSize: '0.75rem',
                                                  color: '#1D1D1F',
                                                  display: 'block',
                                                  mb: 0.5,
                                                }}
                                              >
                                                • {sectionMatch[2]}
                                              </Typography>
                                            )
                                          }
                                          return null
                                        })}
                                        {childOutline.split('\n').length > 5 && (
                                          <Typography
                                            variant="caption"
                                            sx={{
                                              fontSize: '0.7rem',
                                              color: '#86868B',
                                              fontStyle: 'italic',
                                            }}
                                          >
                                            ... 还有更多章节
                                          </Typography>
                                        )}
                                      </Box>
                                    </Box>
                                  )}
                                  
                                  {/* For MasterAgent: show child notebooks' descriptions */}
                                  {isChildMaster && child.children && child.children.length > 0 && (
                                    <Box sx={{ mb: 1.5 }}>
                                      <Typography
                                        variant="caption"
                                        sx={{
                                          color: '#86868B',
                                          fontWeight: 600,
                                          mb: 0.5,
                                          display: 'block',
                                          textTransform: 'uppercase',
                                          fontSize: '0.65rem',
                                        }}
                                      >
                                        📚 子笔记本
                                      </Typography>
                                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                                        {child.children.slice(0, 3).map((subChild, subIndex) => {
                                          const subParsedCard = subChild.agent_card ? parseAgentCard(subChild.agent_card) : null
                                          const subDescription = subChild.description || subParsedCard?.description || ''
                                          
                                          if (!subDescription) return null
                                          
                                          return (
                                            <Box key={subIndex} sx={{ pl: 1, borderLeft: '2px solid #4ECDC430' }}>
                                              <Typography
                                                variant="caption"
                                                sx={{
                                                  fontSize: '0.7rem',
                                                  fontWeight: 600,
                                                  color: '#1D1D1F',
                                                  display: 'block',
                                                  mb: 0.25,
                                                }}
                                              >
                                                {subChild.agent_name || subChild.name || 'Notebook'}
                                              </Typography>
                                              <Typography
                                                variant="caption"
                                                sx={{
                                                  fontSize: '0.7rem',
                                                  color: '#86868B',
                                                  display: '-webkit-box',
                                                  WebkitLineClamp: 2,
                                                  WebkitBoxOrient: 'vertical',
                                                  overflow: 'hidden',
                                                }}
                                              >
                                                {subDescription}
                                              </Typography>
                                            </Box>
                                          )
                                        })}
                                        {child.children.length > 3 && (
                                          <Typography
                                            variant="caption"
                                            sx={{
                                              fontSize: '0.7rem',
                                              color: '#86868B',
                                              fontStyle: 'italic',
                                            }}
                                          >
                                            ... 还有 {child.children.length - 3} 个笔记本
                                          </Typography>
                                        )}
                                      </Box>
                                    </Box>
                                  )}
                                  
                                  <Box sx={{ mt: 'auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 1 }}>
                                    <Typography
                                      variant="caption"
                                      sx={{ color: '#86868B', fontSize: '0.7rem' }}
                                    >
                                      ID: {(child.notebook_id || child.id || '').substring(0, 8)}...
                                    </Typography>
                                    {child.agent_type && (
                                      <Chip
                                        label={
                                          child.agent_type === 'top_level_agent'
                                            ? 'Top Level'
                                            : child.agent_type === 'master'
                                            ? 'Master'
                                            : child.agent_type === 'notebook'
                                            ? 'Notebook'
                                            : child.type
                                        }
                                        size="small"
                                        sx={{
                                          bgcolor:
                                            child.agent_type === 'top_level_agent'
                                              ? '#FF6B6B15'
                                              : child.agent_type === 'master'
                                              ? '#007AFF15'
                                              : '#34C75915',
                                          color:
                                            child.agent_type === 'top_level_agent'
                                              ? '#FF6B6B'
                                              : child.agent_type === 'master'
                                              ? '#007AFF'
                                              : '#34C759',
                                          fontWeight: 500,
                                          fontSize: '0.7rem',
                                          height: 20,
                                          flexShrink: 0,
                                        }}
                                      />
                                    )}
                                  </Box>
                                </CardContent>
                              </Card>
                            </Grid>
                          )
                        })}
                      </Grid>
                    </Box>
                  ) : (
                    <Box
                      sx={{
                        textAlign: 'center',
                        py: 4,
                        color: '#86868B',
                      }}
                    >
                      <Typography variant="body2">
                        No child agents found
                      </Typography>
                    </Box>
                  )}
                </Box>
              </Paper>
            ) : (
              // Notebook Content View for Notebook Agents
              <Paper
                sx={{
                  p: 3,
                  bgcolor: 'white',
                  borderRadius: 3,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <NotebookIcon sx={{ color: '#007AFF' }} />
                    <Typography
                      variant="h6"
                      sx={{
                        fontWeight: 600,
                        color: '#1D1D1F',
                      }}
                    >
                      Notebook Content
                    </Typography>
                  </Box>
                  
                  {/* Split Recommendation Button */}
                  {agent.should_split && (
                    <Button
                      variant="outlined"
                      startIcon={<SplitIcon />}
                      disabled={splitting}
                      sx={{
                        borderColor: '#FF9500',
                        color: '#FF9500',
                        '&:hover': {
                          borderColor: '#FF9500',
                          bgcolor: '#FF950015',
                        },
                        '&:disabled': {
                          borderColor: '#FF950050',
                          color: '#FF950050',
                        },
                      }}
                      onClick={async () => {
                        if (!window.confirm(
                          `确定要拆分这个笔记本吗？\n\n原因：${agent.split_reason || '章节数或字数超过限制'}\n\n拆分后，当前笔记本将被删除，并创建多个新的笔记本。`
                        )) {
                          return
                        }
                        
                        try {
                          setSplitting(true)
                          const response = await splitNotebook(agent.id)
                          
                          if (response.data?.success) {
                            // Show success message
                            alert(`拆分成功！\n\n${response.data.message || '笔记本已成功拆分'}`)
                            
                            // Navigate to the new master agent if available
                            if (response.data.new_master_agent_id) {
                              navigate(`/agents/${response.data.new_master_agent_id}`)
                            } else {
                              // Otherwise, navigate back to agents list
                              navigate('/agents')
                            }
                          } else {
                            alert(response.data?.message || '拆分失败，请重试')
                          }
                        } catch (err) {
                          console.error('Failed to split notebook:', err)
                          alert(err.response?.data?.detail || err.message || '拆分失败，请重试')
                        } finally {
                          setSplitting(false)
                        }
                      }}
                    >
                      {splitting ? '拆分中...' : '建议拆分'}
                    </Button>
                  )}
                </Box>

                {/* Split Warning Alert */}
                {agent.should_split && (
                  <Alert
                    severity="warning"
                    icon={<WarningIcon />}
                    sx={{
                      mb: 3,
                      bgcolor: '#FF950015',
                      border: '1px solid #FF950030',
                      '& .MuiAlert-icon': {
                        color: '#FF9500',
                      },
                      '& .MuiAlert-message': {
                        color: '#1D1D1F',
                      },
                    }}
                  >
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                      建议拆分笔记本
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#86868B' }}>
                      {agent.split_reason || '章节数或字数超过限制，建议拆分以提高性能和管理效率。'}
                    </Typography>
                  </Alert>
                )}

                <Box
                  sx={{
                    '& p': {
                      margin: '0.5em 0',
                      color: '#1D1D1F',
                      lineHeight: 1.75,
                    },
                    '& pre': {
                      bgcolor: 'white',
                      borderRadius: 2,
                      padding: 2,
                      overflow: 'auto',
                      fontSize: '0.875rem',
                      fontFamily: 'monospace',
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
                  {notebookContent ? (
                    // Check if it's structured data format
                    notebookContent.format === 'structured' ? (
                      // Render structured data using components
                      <NotebookContent content={notebookContent} />
                    ) : typeof notebookContent === 'string' || notebookContent.format === 'markdown' ? (
                      // Fallback to markdown rendering
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm, remarkMath]}
                        rehypePlugins={[rehypeRaw, rehypeKatex]}
                        components={{
                          h3({ node, children, ...props }) {
                            // Check if this is a "定义" heading
                            const text = String(children)
                            if (text.includes('定义')) {
                              return (
                                <h3
                                  {...props}
                                  style={{
                                    fontWeight: 700,
                                    marginTop: '1.5em',
                                    marginBottom: '0.5em',
                                  }}
                                >
                                  {children}
                                </h3>
                              )
                            }
                            return <h3 {...props}>{children}</h3>
                          },
                          div({ node, className, children, ...props }) {
                            // Style definition blocks
                            if (className === 'definition-block') {
                              return (
                                <div
                                  {...props}
                                  style={{
                                    backgroundColor: '#F5F5F7',
                                    padding: '12px 16px',
                                    borderRadius: '8px',
                                    borderLeft: '4px solid #007AFF',
                                    margin: '8px 0',
                                  }}
                                >
                                  {children}
                                </div>
                              )
                            }
                            return <div {...props}>{children}</div>
                          },
                          code({ node, inline, className, children, ...props }) {
                            const match = /language-(\w+)/.exec(className || '')
                            return !inline && match ? (
                              <SyntaxHighlighter
                                style={prism}
                                language={match[1]}
                                PreTag="div"
                                customStyle={{
                                  backgroundColor: 'white',
                                  border: '1px solid rgba(0,0,0,0.1)',
                                  borderRadius: '8px',
                                  padding: '16px',
                                  margin: '1em 0',
                                }}
                                {...props}
                              >
                                {String(children).replace(/\n$/, '')}
                              </SyntaxHighlighter>
                            ) : (
                              <code className={className} {...props}>
                                {children}
                              </code>
                            )
                          },
                        }}
                      >
                        {typeof notebookContent === 'string' ? notebookContent : (notebookContent.content || '')}
                      </ReactMarkdown>
                    ) : (
                      <Typography
                        variant="body1"
                        sx={{
                          color: '#1D1D1F',
                          lineHeight: 1.6,
                        }}
                      >
                        {JSON.stringify(notebookContent, null, 2)}
                      </Typography>
                    )
                  ) : (
                    <Box
                      sx={{
                        textAlign: 'center',
                        py: 4,
                        color: '#86868B',
                      }}
                    >
                      <Typography variant="body2">
                        No notebook content available
                      </Typography>
                    </Box>
                  )}
                </Box>
              </Paper>
            )}
          </Box>
        </Container>
      </Box>
    </Box>
  )
}

export default AgentDetailPage


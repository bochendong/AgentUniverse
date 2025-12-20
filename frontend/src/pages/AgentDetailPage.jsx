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
import { getAgent, getNotebook, getNotebookContent, getAgentHierarchy, splitNotebook, getAgentParent } from '../api/client'
import AgentAvatar from '../components/AgentAvatar'
import NotebookContent from '../components/notebook/NotebookContent'
import InstructionsEditorInline from '../components/InstructionsEditorInline'
import HierarchyGraphView from '../components/HierarchyGraphView'
import AgentToolsView from '../components/AgentToolsView'
import AgentInstructionsView from '../components/AgentInstructionsView'

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
  const [parentAgent, setParentAgent] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [splitting, setSplitting] = useState(false)
  const [showAdvancedMode, setShowAdvancedMode] = useState(false)
  const [selectedAgentId, setSelectedAgentId] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)

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
          // 加载层级关系和parent agent
          try {
            const [hierarchyRes, parentRes] = await Promise.all([
              getAgentHierarchy(agentRes.data.id).catch(() => ({ data: null })),
              getAgentParent(agentRes.data.id).catch(() => ({ data: null })),
            ])
            if (hierarchyRes?.data) {
            setHierarchy(hierarchyRes.data)
            }
            if (parentRes?.data) {
              setParentAgent(parentRes.data)
            }
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
  const isNotebookAgent = agent.metadata?.is_notebook_agent || agent.agent_type === 'notebook'

  // Build current agent data for hierarchy view
  const currentAgentData = {
    id: agent.id,
    notebook_id: agent.id,
    agent_name: agent.agent_name || agent.name,
    name: agent.name,
    agent_type: agent.agent_type,
    metadata: agent.metadata,
    agent_card: agent.agent_card,
    notebook_title: agent.notebook_title,
    description: agent.description,
  }

  const handleAgentClick = (clickedAgent) => {
    // Select the clicked agent to show its tools and instructions
    const clickedAgentId = clickedAgent.id || clickedAgent.notebook_id
    setSelectedAgentId(clickedAgentId)
  }

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
          maxWidth={false}
          sx={{
            display: isNotebookAgent ? 'flex' : 'block',
            gap: 3,
            py: 3,
            alignItems: 'flex-start',
            width: '100%',
            px: 3,
          }}
        >
          {/* Left Side - Agent Card (only for Notebook Agent) */}
          {isNotebookAgent ? (
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

              {/* Agent Card Header with Advance Mode Button */}
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
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
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => setShowAdvancedMode(!showAdvancedMode)}
                  sx={{
                    borderColor: 'rgba(0,0,0,0.2)',
                    color: '#1D1D1F',
                    fontSize: '0.75rem',
                    textTransform: 'none',
                    '&:hover': {
                      borderColor: '#007AFF',
                      bgcolor: 'rgba(0,122,255,0.05)',
                    },
                  }}
                >
                  {showAdvancedMode ? '隐藏' : 'Advanced Mode'}
                </Button>
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

              {/* Advanced Mode - Instructions Editor */}
              <InstructionsEditorInline
                agentId={agentId}
                expanded={showAdvancedMode}
                onToggle={() => setShowAdvancedMode(false)}
              />
            </Paper>
          </Box>
          ) : null}

          {/* Right Side - Notebook Content (for Notebook Agent) or Full Width Hierarchy View (for Top/Master Agent) */}
          {isNotebookAgent ? (
          <Box
            sx={{
              flex: 1,
              minWidth: 0,
            }}
          >
              {/* Notebook Content View for Notebook Agents */}
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
          </Box>
          ) : (
            // Full width layout for Top/Master Agent
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, width: '100%' }}>
              {/* Top row: Hierarchy and Tools side by side */}
              <Box
                sx={{
                  display: 'flex',
                  gap: 3,
                  width: '100%',
                  alignItems: 'stretch', // Make both columns same height
                }}
              >
                {/* Left: Hierarchy View - 50% */}
                <Paper
                  sx={{
                    p: 3,
                    bgcolor: 'white',
                    borderRadius: 3,
                    boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                    flex: 1,
                    width: '50%',
                    minHeight: '600px',
                    display: 'flex',
                    flexDirection: 'column',
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
                      Agent Hierarchy
                    </Typography>
                  </Box>
                  <Box sx={{ flex: 1, overflowY: 'auto' }}>
                    <HierarchyGraphView
                      parentAgent={parentAgent}
                      currentAgent={currentAgentData}
                      children={hierarchy?.children || []}
                      onAgentClick={handleAgentClick}
                      selectedAgentId={selectedAgentId}
                    />
                  </Box>
                </Paper>

                {/* Right: Agent Tools - 50% */}
                <Box sx={{ flex: 1, width: '50%', display: 'flex' }}>
                  <AgentToolsView agentId={selectedAgentId || currentAgentData?.id} />
                </Box>
              </Box>

              {/* Bottom: Agent Instructions */}
              <AgentInstructionsView
                agentId={selectedAgentId || currentAgentData?.id}
                onSave={() => {
                  // Optionally reload after saving
                }}
              />
            </Box>
          )}
        </Container>
      </Box>
    </Box>
  )
}

export default AgentDetailPage


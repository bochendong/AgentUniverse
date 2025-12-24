import React, { useState, useEffect, useRef } from 'react'
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
  TextField,
  Collapse,
  IconButton,
} from '@mui/material'
import {
  ArrowBack as BackIcon,
  MenuBook as NotebookIcon,
  AccountTree as HierarchyIcon,
  SmartToy as AgentIcon,
  Warning as WarningIcon,
  CallSplit as SplitIcon,
  Send as SendIcon,
  Chat as ChatIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  Code as CodeIcon,
  Description as DescriptionIcon,
} from '@mui/icons-material'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import rehypeRaw from 'rehype-raw'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { prism } from 'react-syntax-highlighter/dist/esm/styles/prism'
import 'katex/dist/katex.min.css'
import { getAgent, getNotebook, getNotebookContent, getAgentHierarchy, splitNotebook, getAgentParent, chatWithAgent, getAgentInstructions } from '../api/client'
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
  const [showAdvancedMode, setShowAdvancedMode] = useState(false) // Left side AgentCard Advanced Mode (deprecated, now controls right side)
  const [selectedAgentId, setSelectedAgentId] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showChat, setShowChat] = useState(false)
  const [chatInput, setChatInput] = useState('')
  const [chatMessages, setChatMessages] = useState([])
  const [chatSending, setChatSending] = useState(false)
  const [chatSessionId, setChatSessionId] = useState(null)
  const chatMessagesEndRef = useRef(null)
  const [descriptionExpanded, setDescriptionExpanded] = useState(false)
  const [outlineExpanded, setOutlineExpanded] = useState(false)
  const [showNotebookAdvancedMode, setShowNotebookAdvancedMode] = useState(false)
  const [instructions, setInstructions] = useState('')
  const [loadingInstructions, setLoadingInstructions] = useState(false)
  const [advancedModeMarkdown, setAdvancedModeMarkdown] = useState('')
  const [loadingAdvancedMarkdown, setLoadingAdvancedMarkdown] = useState(false)
  const [showInstructionsView, setShowInstructionsView] = useState(false)
  const [instructionsContent, setInstructionsContent] = useState('')
  const [loadingInstructionsContent, setLoadingInstructionsContent] = useState(false)

  // 重新加载notebook内容的函数
  const reloadNotebookContent = async () => {
    try {
      const contentRes = await getNotebookContent(agentId)
      if (contentRes?.data) {
        setNotebookContent(contentRes.data)
      }
    } catch (err) {
      console.error('Failed to reload notebook content:', err)
    }
  }

  // 当 showNotebookAdvancedMode 或 showAdvancedMode 改变时加载 markdown 格式的 notebook content（包含 XML 标签）
  useEffect(() => {
    const loadAdvancedModeMarkdown = async () => {
      // Load markdown format notebook content if either advanced mode is enabled
      if (!agentId || (!showNotebookAdvancedMode && !showAdvancedMode)) {
        setAdvancedModeMarkdown('')
        return
      }
      try {
        setLoadingAdvancedMarkdown(true)
        // Request markdown format explicitly to get XML tags
        const response = await getNotebookContent(agentId, 'markdown')
        if (response?.data?.content) {
          setAdvancedModeMarkdown(response.data.content)
        } else {
          setAdvancedModeMarkdown('')
        }
      } catch (err) {
        console.error('Failed to load advanced mode markdown:', err)
        setAdvancedModeMarkdown('')
      } finally {
        setLoadingAdvancedMarkdown(false)
      }
    }

    if ((showNotebookAdvancedMode || showAdvancedMode) && agentId) {
      loadAdvancedModeMarkdown()
    } else {
      setAdvancedModeMarkdown('')
    }
  }, [showNotebookAdvancedMode, showAdvancedMode, agentId])

  // 加载 instructions 内容
  const loadInstructionsContent = async () => {
    if (!agentId) return
    try {
      setLoadingInstructionsContent(true)
      const response = await getAgentInstructions(agentId)
      if (response?.data?.current_instructions) {
        setInstructionsContent(response.data.current_instructions)
      } else {
        setInstructionsContent('')
      }
    } catch (err) {
      console.error('Failed to load instructions:', err)
      setInstructionsContent('')
    } finally {
      setLoadingInstructionsContent(false)
    }
  }

  // 当 showInstructionsView 变为 true 时加载 instructions
  useEffect(() => {
    if (showInstructionsView && agentId) {
      loadInstructionsContent()
    }
  }, [showInstructionsView, agentId])

  // 当 agentId 改变时，重置 instructions 相关状态
  useEffect(() => {
    setShowInstructionsView(false)
    setInstructionsContent('')
  }, [agentId])

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

  // Auto-scroll to bottom when chat messages change
  useEffect(() => {
    if (showChat && chatMessagesEndRef.current) {
      chatMessagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [chatMessages, showChat])

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

  const handleChatSend = async () => {
    if (!chatInput.trim() || chatSending) return

    const userMessage = chatInput.trim()
    setChatInput('')
    setChatSending(true)

    // Add user message to chat
    const newMessages = [...chatMessages, { role: 'user', content: userMessage }]
    setChatMessages(newMessages)

    try {
      // Send message to agent
      const response = await chatWithAgent(agentId, userMessage, chatSessionId)
      const agentResponse = response.data.response
      const sessionId = response.data.session_id

      // Update session ID if it's new
      if (!chatSessionId && sessionId) {
        setChatSessionId(sessionId)
      }

      // Add agent response to chat
      setChatMessages([...newMessages, { role: 'assistant', content: agentResponse }])

      // 检查当前agent是否为notebook agent
      const currentAgentIsNotebook = agent?.metadata?.is_notebook_agent || agent?.agent_type === 'notebook'
      
      // 对于notebook agent，在聊天完成后总是尝试刷新内容
      // 因为AI可能使用不同的表达方式，而且用户可能要求更新内容
      if (currentAgentIsNotebook) {
        // 扩展的关键词列表，用于判断是否明确提到了更新操作
        const updateKeywords = [
          '已更新', '已添加', '已修改', '已成功', '已完成',
          '成功添加', '成功更新', '更新成功', '添加成功',
          '笔记已更新', '内容已更新', '已为你添加',
          '已经添加', '已经更新', '已经修改',
          '添加完成', '更新完成', '修改完成',
          '已添加到', '已更新到', '已添加到章节',
          '成功向章节', '字段添加内容', '字段更新',
          '已添加', '已完成添加', '添加了'
        ]
        
        const hasUpdateKeyword = updateKeywords.some(keyword => agentResponse.includes(keyword))
        
        if (hasUpdateKeyword) {
          // 如果检测到明确的更新关键词，快速刷新（500ms）
          console.log('检测到更新关键词，将在500ms后刷新notebook内容')
          setTimeout(() => {
            reloadNotebookContent()
          }, 500)
        } else {
          // 即使没有明确的更新关键词，也延迟刷新（2秒）
          // 这样可以捕获那些AI说"已经添加了"但没有使用标准关键词的情况
          console.log('聊天完成，将在2秒后刷新notebook内容以确保数据最新')
          setTimeout(() => {
            reloadNotebookContent()
          }, 2000)
        }
      }
    } catch (err) {
      console.error('Failed to send message:', err)
      setChatMessages([
        ...newMessages,
        { role: 'assistant', content: `错误: ${err.response?.data?.detail || err.message || '发送消息失败'}` },
      ])
    } finally {
      setChatSending(false)
    }
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
                display: 'flex',
                flexDirection: 'column',
                bgcolor: 'white',
                borderRadius: 3,
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                maxHeight: 'calc(100vh - 120px)',
                overflow: 'hidden',
              }}
            >
              {/* Agent Card - Business Card Style (Fixed) */}
              <Box
                sx={{
                  flexShrink: 0,
                  p: 3,
                  pb: 0,
                }}
              >
                <Box
                  sx={{
                    background: 'linear-gradient(135deg, rgba(0,122,255,0.05) 0%, rgba(0,122,255,0.02) 100%)',
                    borderRadius: 2,
                    p: 3,
                    mb: 3,
                    border: '1px solid rgba(0,0,0,0.05)',
                  }}
                >
                {/* Header: Avatar and Badge */}
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2.5 }}>
                  <AgentAvatar 
                    seed={agent.avatar_seed} 
                    size={64}
                    sx={{
                      border: `2px solid ${
                        isTopLevelAgent
                          ? '#FF6B6B40'
                          : isMasterAgent
                          ? '#4ECDC440'
                          : '#95E1D340'
                      }`,
                      boxShadow: `0 2px 8px ${
                        isTopLevelAgent
                          ? '#FF6B6B15'
                          : isMasterAgent
                          ? '#4ECDC415'
                          : '#95E1D315'
                      }`,
                      flexShrink: 0,
                    }}
                  />
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    {/* Title */}
                    {agent.agent_card && (
                      <Typography
                        variant="h5"
                        sx={{
                          fontWeight: 700,
                          color: '#1D1D1F',
                          fontSize: '1.25rem',
                          mb: 0.5,
                          lineHeight: 1.3,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                        }}
                      >
                        {agent.agent_card.title || (agent.agent_type === 'master' ? 'Master Agent' : '未命名笔记本')}
                      </Typography>
                    )}
                    {/* Badge */}
                    <Box sx={{ display: 'flex', gap: 0.5, mt: 1 }}>
                      {isTopLevelAgent && (
                        <Chip
                          label="Top Level"
                          size="small"
                          sx={{
                            bgcolor: '#FF6B6B',
                            color: 'white',
                            fontWeight: 600,
                            fontSize: '0.7rem',
                            height: '22px',
                          }}
                        />
                      )}
                      {isMasterAgent && (
                        <Chip
                          label="Master"
                          size="small"
                          sx={{
                            bgcolor: '#007AFF',
                            color: 'white',
                            fontWeight: 600,
                            fontSize: '0.7rem',
                            height: '22px',
                          }}
                        />
                      )}
                      {!isTopLevelAgent && !isMasterAgent && (
                        <Chip
                          label="Notebook"
                          size="small"
                          sx={{
                            bgcolor: '#34C759',
                            color: 'white',
                            fontWeight: 600,
                            fontSize: '0.7rem',
                            height: '22px',
                          }}
                        />
                      )}
                    </Box>
                  </Box>
                </Box>

                {/* ID Information */}
                {agent.agent_card && (
                  <Box
                    sx={{
                      pt: 2,
                      borderTop: '1px solid rgba(0,0,0,0.08)',
                      display: 'flex',
                      gap: 2,
                      flexWrap: 'wrap',
                    }}
                  >
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#86868B',
                        fontSize: '0.7rem',
                        fontFamily: 'monospace',
                      }}
                    >
                      ID: {agent.agent_card.agent_id?.substring(0, 8)}...
                    </Typography>
                    {agent.agent_card.parent_agent_id && (
                      <Typography
                        variant="caption"
                        sx={{
                          color: '#86868B',
                          fontSize: '0.7rem',
                          fontFamily: 'monospace',
                        }}
                      >
                        Parent: {agent.agent_card.parent_agent_id.substring(0, 8)}...
                      </Typography>
                    )}
                  </Box>
                )}
                </Box>
              </Box>

              {/* Scrollable Content Area */}
              <Box
                sx={{
                  flex: 1,
                  overflowY: 'auto',
                  overflowX: 'hidden',
                  px: 3,
                  pb: 3,
                }}
              >
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
                  onClick={() => {
                    setShowAdvancedMode(!showAdvancedMode)
                    // Also toggle the right side notebook advanced mode to show instructions
                    setShowNotebookAdvancedMode(!showAdvancedMode)
                  }}
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
                  {/* Description */}
                  {agent.agent_card.description && (
                    <Box sx={{ mb: 3 }}>
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          cursor: 'pointer',
                          mb: 1.5,
                          '&:hover': {
                            opacity: 0.8,
                          },
                        }}
                        onClick={() => setDescriptionExpanded(!descriptionExpanded)}
                      >
                        <Typography
                          variant="subtitle1"
                          sx={{
                            color: '#86868B',
                            fontWeight: 600,
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            fontSize: '0.95rem',
                          }}
                        >
                          {agent.agent_type === 'master' ? '📚 下辖笔记本简介' : '📝 描述'}
                        </Typography>
                        <IconButton
                          size="small"
                          sx={{
                            color: '#86868B',
                            padding: '4px',
                          }}
                        >
                          {descriptionExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                      </Box>
                      <Collapse in={descriptionExpanded}>
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
                      </Collapse>
                    </Box>
                  )}

                  {/* Outline */}
                  {agent.agent_card.outline && Object.keys(agent.agent_card.outline).length > 0 && (
                    <Box sx={{ mb: 3 }}>
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          cursor: 'pointer',
                          mb: 1.5,
                          '&:hover': {
                            opacity: 0.8,
                          },
                        }}
                        onClick={() => setOutlineExpanded(!outlineExpanded)}
                      >
                        <Typography
                          variant="subtitle1"
                          sx={{
                            color: '#86868B',
                            fontWeight: 600,
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            fontSize: '0.95rem',
                          }}
                        >
                          📋 大纲
                        </Typography>
                        <IconButton
                          size="small"
                          sx={{
                            color: '#86868B',
                            padding: '4px',
                          }}
                        >
                          {outlineExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                      </Box>
                      <Collapse in={outlineExpanded}>
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
                      </Collapse>
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

              {/* Advanced Mode - Instructions Editor (disabled, now controlled by right side) */}
              {/* InstructionsEditorInline component removed - instructions now shown in right side Notebook Content area */}
              </Box>
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
                  display: 'flex',
                  flexDirection: 'column',
                  bgcolor: 'white',
                  borderRadius: 3,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                  maxHeight: 'calc(100vh - 120px)',
                  overflow: 'hidden',
                }}
              >
                {/* Header - Fixed */}
                <Box
                  sx={{
                    flexShrink: 0,
                    p: 3,
                    pb: 0,
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {showChat ? (
                        <ChatIcon sx={{ color: '#007AFF' }} />
                      ) : (
                        <NotebookIcon sx={{ color: '#007AFF' }} />
                      )}
                      <Typography
                        variant="h6"
                        sx={{
                          fontWeight: 600,
                          color: '#1D1D1F',
                        }}
                      >
                        {showChat ? `与 ${agent.notebook_title || agent.agent_name} 对话` : 'Notebook Content'}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      {/* Instructions View Button */}
                      {isNotebookAgent && !showChat && !showNotebookAdvancedMode && !showInstructionsView && (
                        <Button
                          variant="outlined"
                          startIcon={<DescriptionIcon />}
                          onClick={() => {
                            setShowInstructionsView(true)
                            if (!instructionsContent) {
                              loadInstructionsContent()
                            }
                          }}
                          sx={{
                            borderColor: '#007AFF',
                            color: '#007AFF',
                            '&:hover': {
                              borderColor: '#0051D5',
                              bgcolor: 'rgba(0,122,255,0.05)',
                            },
                          }}
                        >
                          查看 Instructions
                        </Button>
                      )}

                      {/* Hide Instructions Button */}
                      {isNotebookAgent && !showChat && showInstructionsView && (
                        <Button
                          variant="outlined"
                          onClick={() => {
                            setShowInstructionsView(false)
                          }}
                          sx={{
                            borderColor: '#007AFF',
                            color: '#007AFF',
                            '&:hover': {
                              borderColor: '#0051D5',
                              bgcolor: 'rgba(0,122,255,0.05)',
                            },
                          }}
                        >
                          隐藏 Instructions
                        </Button>
                      )}

                      {/* Advanced Mode indicator - sync with left side button */}
                      {isNotebookAgent && !showChat && showNotebookAdvancedMode && !showInstructionsView && (
                        <Button
                          variant="outlined"
                          onClick={() => {
                            setShowNotebookAdvancedMode(false)
                            setShowAdvancedMode(false)
                          }}
                          sx={{
                            borderColor: '#007AFF',
                            color: '#007AFF',
                            '&:hover': {
                              borderColor: '#0051D5',
                              bgcolor: 'rgba(0,122,255,0.05)',
                            },
                          }}
                        >
                          隐藏 Markdown
                        </Button>
                      )}

                      {/* Refresh Button */}
                      {isNotebookAgent && !showChat && !showNotebookAdvancedMode && !showInstructionsView && (
                        <Button
                          variant="outlined"
                          startIcon={<RefreshIcon />}
                          onClick={reloadNotebookContent}
                          sx={{
                            borderColor: '#86868B',
                            color: '#1D1D1F',
                            '&:hover': {
                              borderColor: '#1D1D1F',
                              bgcolor: 'rgba(0,0,0,0.05)',
                            },
                          }}
                        >
                          刷新内容
                        </Button>
                      )}
                      
                      {/* Chat Toggle Button */}
                      <Button
                        variant={showChat ? "contained" : "outlined"}
                        startIcon={<ChatIcon />}
                        onClick={() => {
                          setShowChat(!showChat)
                          if (showChat) {
                            setShowNotebookAdvancedMode(false)
                            setShowAdvancedMode(false)
                          }
                        }}
                        sx={{
                          borderColor: '#007AFF',
                          color: showChat ? 'white' : '#007AFF',
                          bgcolor: showChat ? '#007AFF' : 'transparent',
                          '&:hover': {
                            borderColor: '#007AFF',
                            bgcolor: showChat ? '#0051D5' : 'rgba(0,122,255,0.05)',
                          },
                        }}
                      >
                        {showChat ? '隐藏对话' : '与 Agent 对话'}
                      </Button>
                      
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
                </Box>
                </Box>

                {/* Scrollable Content Area */}
                <Box
                  sx={{
                    flex: 1,
                    display: showChat ? 'flex' : 'block',
                    flexDirection: showChat ? 'column' : 'initial',
                    minHeight: 0,
                    ...(showChat ? {
                      // When in chat mode, don't scroll the container, let chat interface handle scrolling
                      overflow: 'hidden',
                    } : {
                      // When showing notebook content, allow scrolling
                      overflowY: 'auto',
                      overflowX: 'hidden',
                      px: 3,
                      pb: 3,
                    }),
                  }}
                >

                {/* Split Warning Alert - only show when not in chat mode */}
                {!showChat && agent.should_split && (
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

                {/* Instructions View - show when showInstructionsView is enabled */}
                {!showChat && showInstructionsView && (
                  <Box>
                    {loadingInstructionsContent ? (
                      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                        <CircularProgress />
                      </Box>
                    ) : (
                      <Box
                        component="pre"
                        sx={{
                          fontFamily: 'Monaco, "Courier New", monospace',
                          fontSize: '0.875rem',
                          lineHeight: 1.6,
                          color: '#1D1D1F',
                          backgroundColor: '#F5F5F7',
                          padding: 3,
                          borderRadius: 2,
                          border: '1px solid rgba(0,0,0,0.1)',
                          overflowX: 'auto',
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                          margin: 0,
                        }}
                      >
                        {instructionsContent || '暂无 instructions'}
                      </Box>
                    )}
                  </Box>
                )}

                {/* Advanced Mode - Raw Markdown Notebook Content with XML tags - show when either advanced mode is enabled */}
                {!showChat && !showInstructionsView && (showNotebookAdvancedMode || showAdvancedMode) && (
                  <Box>
                    {loadingAdvancedMarkdown ? (
                      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                        <CircularProgress />
                      </Box>
                    ) : (
                      <Box
                        component="pre"
                        sx={{
                          fontFamily: 'Monaco, "Courier New", monospace',
                          fontSize: '0.875rem',
                          lineHeight: 1.6,
                          color: '#1D1D1F',
                          backgroundColor: '#F5F5F7',
                          padding: 3,
                          borderRadius: 2,
                          border: '1px solid rgba(0,0,0,0.1)',
                          overflowX: 'auto',
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                          margin: 0,
                        }}
                      >
                        {advancedModeMarkdown || '暂无 notebook content'}
                      </Box>
                    )}
                  </Box>
                )}

                {/* Notebook Content - only show when not in chat mode, not in advanced mode, and not showing instructions */}
                {!showChat && !showNotebookAdvancedMode && !showAdvancedMode && !showInstructionsView && (
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
                )}

                {/* Chat Interface - only show when in chat mode */}
                {showChat && (
                  <Box
                    sx={{
                      display: 'flex',
                      flexDirection: 'column',
                      height: 'calc(100vh - 180px)',
                      maxHeight: 'calc(100vh - 180px)',
                      width: '100%',
                      px: 3,
                      pb: 3,
                    }}
                  >
                    {/* Messages Area */}
                    <Box
                      sx={{
                        flex: 1,
                        overflowY: 'auto',
                        mb: 2,
                        p: 2,
                        bgcolor: '#F5F5F7',
                        borderRadius: 2,
                        minHeight: 0,
                      }}
                    >
                      {chatMessages.length === 0 ? (
                        <Box
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            height: '100%',
                            color: '#86868B',
                          }}
                        >
                          <Typography variant="body2">
                            开始与 Agent 对话吧！你可以询问关于笔记本内容的问题。
                          </Typography>
                        </Box>
                      ) : (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                          {chatMessages.map((msg, idx) => (
                            <Box
                              key={idx}
                              sx={{
                                display: 'flex',
                                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                              }}
                            >
                              <Paper
                                sx={{
                                  p: 2,
                                  maxWidth: '80%',
                                  bgcolor: msg.role === 'user' ? '#007AFF' : 'white',
                                  color: msg.role === 'user' ? 'white' : '#1D1D1F',
                                  borderRadius: 2,
                                }}
                              >
                                <ReactMarkdown
                                  remarkPlugins={[remarkGfm, remarkMath]}
                                  rehypePlugins={[rehypeRaw, rehypeKatex]}
                                  components={{
                                    code({ node, inline, className, children, ...props }) {
                                      const match = /language-(\w+)/.exec(className || '')
                                      return !inline && match ? (
                                        <SyntaxHighlighter
                                          style={prism}
                                          language={match[1]}
                                          PreTag="div"
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
                                  {msg.content}
                                </ReactMarkdown>
                              </Paper>
                            </Box>
                          ))}
                          <div ref={chatMessagesEndRef} />
                        </Box>
                      )}
                    </Box>
                    
                    {/* Input Area */}
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <TextField
                        fullWidth
                        multiline
                        maxRows={4}
                        placeholder="输入消息..."
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault()
                            handleChatSend()
                          }
                        }}
                        disabled={chatSending}
                        sx={{
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                          },
                        }}
                      />
                      <Button
                        variant="contained"
                        startIcon={<SendIcon />}
                        onClick={handleChatSend}
                        disabled={!chatInput.trim() || chatSending}
                        sx={{
                          bgcolor: '#007AFF',
                          '&:hover': {
                            bgcolor: '#0051D5',
                          },
                          '&:disabled': {
                            bgcolor: '#86868B',
                          },
                        }}
                      >
                        发送
                      </Button>
                    </Box>
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
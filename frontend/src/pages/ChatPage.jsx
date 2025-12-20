import React, { useState, useEffect, useRef } from 'react'
import { 
  Box, 
  Drawer, 
  List, 
  ListItem, 
  ListItemButton, 
  ListItemText, 
  IconButton, 
  Typography,
  Divider,
  TextField,
  Paper,
  CircularProgress,
  Avatar,
  Fade,
} from '@mui/material'
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Send as SendIcon,
  Stop as StopIcon,
  AttachFile as AttachFileIcon,
  InsertDriveFile as FileIcon,
  Close as CloseIcon,
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useTheme } from '../contexts/ThemeContext'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import 'katex/dist/katex.min.css'
import { 
  chatWithTopLevelAgent, 
  createTopLevelAgentSession, 
  listTopLevelAgentSessions,
  getSessionConversations,
  deleteSession,
  uploadFile,
  confirmOutlineAndCreateNotebook,
  reviseOutline,
  getSessionTracing,
} from '../api/client'
import OutlineConfirmation from '../components/OutlineConfirmation'

/**
 * Chat Page - OpenAI风格
 * 用户与TopLevelAgent聊天的界面
 */
function ChatPage() {
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  const [sessions, setSessions] = useState([])
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [loading, setLoading] = useState(true)
  const [inputMessage, setInputMessage] = useState('')
  const [uploadedFile, setUploadedFile] = useState(null) // { path: string, name: string }
  const [pendingOutline, setPendingOutline] = useState(null) // { outline: object, userRequest: string, filePath: string }
  const [creatingNotebook, setCreatingNotebook] = useState(false)
  const [currentActivity, setCurrentActivity] = useState(null) // Current agent activity from tracing
  const tracingPollIntervalRef = useRef(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const fileInputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Poll tracing information when sending
  useEffect(() => {
    if (sending && currentSessionId) {
      // Start polling
      const pollTracing = async () => {
        try {
          const response = await getSessionTracing(currentSessionId)
          const currentActivity = response.data.current_activity
          if (currentActivity) {
            setCurrentActivity(currentActivity)
          }
        } catch (err) {
          console.error('Failed to poll tracing:', err)
        }
      }

      // Poll immediately and then every 500ms
      pollTracing()
      tracingPollIntervalRef.current = setInterval(pollTracing, 500)
    } else {
      // Stop polling
      if (tracingPollIntervalRef.current) {
        clearInterval(tracingPollIntervalRef.current)
        tracingPollIntervalRef.current = null
      }
      // Clear current activity after a delay
      setTimeout(() => setCurrentActivity(null), 1000)
    }

    return () => {
      if (tracingPollIntervalRef.current) {
        clearInterval(tracingPollIntervalRef.current)
      }
    }
  }, [sending, currentSessionId])

  // 加载会话列表
  const loadSessions = async () => {
    try {
      const response = await listTopLevelAgentSessions()
      setSessions(response.data.sessions || [])
    } catch (err) {
      console.error('Failed to load sessions:', err)
    }
  }

  // 加载会话对话
  const loadSessionConversations = async (sessionId) => {
    try {
      const response = await getSessionConversations(sessionId)
      const conversations = response.data.conversations || []
      setMessages(conversations.map(c => ({ role: c.role, content: c.content })))
    } catch (err) {
      console.error('Failed to load conversations:', err)
      setMessages([])
    }
  }

  // 初始化
  useEffect(() => {
    const init = async () => {
      setLoading(true)
      await loadSessions()
      setLoading(false)
      setMessages([])
      setCurrentSessionId(null)
    }
    init()
  }, [])

  // 创建新会话
  const handleNewChat = async () => {
    try {
      const response = await createTopLevelAgentSession()
      const newSession = response.data
      setSessions([newSession, ...sessions])
      setCurrentSessionId(newSession.id)
      setMessages([])
    } catch (err) {
      console.error('Failed to create session:', err)
      setError('Failed to create new chat')
    }
  }

  // 选择会话
  const handleSelectSession = async (sessionId) => {
    setCurrentSessionId(sessionId)
    await loadSessionConversations(sessionId)
  }

  // 删除会话
  const handleDeleteSession = async (sessionId, e) => {
    e.stopPropagation()
    try {
      await deleteSession(sessionId)
      await loadSessions()
      if (currentSessionId === sessionId) {
        setCurrentSessionId(null)
        setMessages([])
      }
    } catch (err) {
      console.error('Failed to delete session:', err)
    }
  }

  // 格式化日期
  const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    const now = new Date()
    const diff = now - date
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    
    if (days === 0) {
      return 'Today'
    } else if (days === 1) {
      return 'Yesterday'
    } else if (days < 7) {
      return `${days} days ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  const handleSend = async () => {
    if ((!inputMessage.trim() && !uploadedFile) || sending) return
    
    // 如果没有当前会话，创建一个新会话
    let sessionId = currentSessionId
    if (!sessionId) {
      try {
        const response = await createTopLevelAgentSession()
        const newSession = response.data
        sessionId = newSession.id
        setCurrentSessionId(sessionId)
        setSessions([newSession, ...sessions])
      } catch (err) {
        console.error('Failed to create session:', err)
        setError('Failed to create session')
        return
      }
    }

    // 构建用户消息
    let userMessage = inputMessage.trim()
    
    // 如果有上传的文件，将文件信息添加到消息中
    if (uploadedFile) {
      // 更明确地指示使用 handle_file_upload 工具
      const fileInfo = `\n\n我需要上传文件并创建笔记本。\n文件路径：${uploadedFile.path}\n文件名：${uploadedFile.name}\n\n请调用 handle_file_upload 工具，参数为：\n- file_path: "${uploadedFile.path}"\n- user_request: "${userMessage.trim() || '请根据文件内容创建笔记本'}"`
      if (userMessage) {
        userMessage = userMessage + fileInfo
      } else {
        userMessage = `请处理上传的文件并创建笔记本。${fileInfo}`
      }
    }

    // 保存文件路径信息（在清空前）
    const savedFilePath = uploadedFile?.path || null

    setInputMessage('')
    setUploadedFile(null) // 清空上传的文件信息
    setSending(true)
    setError(null)

    // 添加用户消息到界面（显示原始输入，不显示文件路径）
    const displayMessage = inputMessage.trim() || (uploadedFile ? `[已上传文件: ${uploadedFile.name}]` : '')
    const newMessages = [...messages, { role: 'user', content: displayMessage }]
    setMessages(newMessages)

    try {
      // 发送消息给 TopLevelAgent
      const response = await chatWithTopLevelAgent(userMessage, sessionId)
      const agentResponse = response.data.response

      // 检测是否是大纲确认消息（尝试从JSON代码块中提取）
      let outline = null
      try {
        // 尝试从JSON代码块中提取大纲
        const jsonMatch = agentResponse.match(/```json\s*([\s\S]*?)\s*```/)
        if (jsonMatch) {
          const outlineData = JSON.parse(jsonMatch[1])
          outline = outlineData
        }
      } catch (err) {
        // JSON解析失败，尝试文本解析
        outline = parseOutlineFromMessage(agentResponse)
      }
      
      if (outline) {
        // 这是大纲确认消息，显示确认UI
        setPendingOutline({
          outline: outline,
          userRequest: userMessage,
          filePath: savedFilePath,
        })
        // 添加消息到对话中（但不显示JSON部分）
        const displayResponse = agentResponse.replace(/```json\s*[\s\S]*?\s*```/g, '').trim()
        setMessages([
          ...newMessages,
          { role: 'assistant', content: displayResponse },
        ])
      } else {
        // 普通消息，添加到对话中
      setMessages([
        ...newMessages,
        { role: 'assistant', content: agentResponse },
      ])
      }

      // 刷新会话列表
      await loadSessions()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message')
      setMessages(messages)
      console.error('Error sending message:', err)
    } finally {
      setSending(false)
      setTimeout(() => {
        inputRef.current?.focus()
      }, 100)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleStop = () => {
    setSending(false)
  }

  const handleFileUpload = () => {
    fileInputRef.current?.click()
  }

  // 从消息中解析大纲
  const parseOutlineFromMessage = (message) => {
    // 检测是否包含大纲确认标记
    if (!message.includes('📋') && !message.includes('大纲已生成')) {
      return null
    }

    try {
      // 尝试从markdown格式的消息中提取大纲
      // 匹配 "**标题**：{title}" 或 "**标题**：{title}"
      const titleMatch = message.match(/\*\*标题\*\*[：:]\s*(.+?)(?:\n|$)/m)
      if (!titleMatch) {
        return null
      }

      const notebook_title = titleMatch[1].trim()
      
      // 匹配描述（可能在标题之后，章节之前）
      const descMatch = message.match(/\*\*描述\*\*[：:]\s*([\s\S]+?)(?:\*\*章节\*\*|\n\*\*\d+\.|请确认|$)/m)
      const notebook_description = descMatch ? descMatch[1].trim() : ''
      
      // 解析章节 - 匹配 "**1. 章节名**\n描述内容" 格式
      const outlines = {}
      // 先找到章节部分
      const sectionsStart = message.indexOf('**章节**')
      if (sectionsStart >= 0) {
        const sectionsText = message.substring(sectionsStart)
        // 匹配 "**数字. 章节名**\n描述"（描述可能有多行，直到下一个**数字.或结尾）
        const sectionRegex = /\*\*(\d+)\.\s*(.+?)\*\*\s*\n([\s\S]*?)(?=\n\*\*\d+\.|请确认|$)/g
        let match
        while ((match = sectionRegex.exec(sectionsText)) !== null) {
          const title = match[2].trim()
          let description = match[3].trim()
          // 移除末尾的省略号（如果有）
          description = description.replace(/\.\.\.\s*$/, '').trim()
          if (title && description) {
            outlines[title] = description
          }
        }
      }

      if (Object.keys(outlines).length === 0) {
        return null
      }

      return {
        notebook_title,
        notebook_description,
        outlines,
      }
    } catch (err) {
      console.error('Failed to parse outline:', err)
      return null
    }
  }

  // 处理大纲修订
  const handleOutlineRevise = async (feedback) => {
    if (!pendingOutline) return

    setCreatingNotebook(true) // 使用这个状态表示正在处理
    try {
      const response = await reviseOutline(
        pendingOutline.userRequest,
        pendingOutline.outline,
        feedback,
        pendingOutline.filePath
      )

      // 更新pending outline为修订后的版本
      setPendingOutline({
        outline: response.data.outline,
        userRequest: pendingOutline.userRequest,
        filePath: pendingOutline.filePath,
      })

      // 添加修订消息到对话
      setMessages([
        ...messages,
        {
          role: 'assistant',
          content: `根据您的反馈，我已经修改了大纲。\n\n${response.data.outline_info}`,
        },
      ])
    } catch (err) {
      setError(err.response?.data?.detail || '修改大纲失败')
      console.error('Failed to revise outline:', err)
    } finally {
      setCreatingNotebook(false)
    }
  }

  // 处理大纲确认
  const handleOutlineConfirm = async (outline) => {
    if (!pendingOutline) return

    setCreatingNotebook(true)
    
    // 添加用户确认消息到界面
    const confirmMessage = { role: 'user', content: '确认' }
    setMessages([...messages, confirmMessage])
    
    try {
      // 构建包含完整大纲信息的消息
      // 将大纲 JSON 和文件路径包含在消息中，让 TopLevelAgent 能够提取
      const outlineJson = JSON.stringify(outline, null, 2)
      const confirmMessageWithOutline = `确认创建笔记本。

**大纲信息（JSON格式）：**
\`\`\`json
${outlineJson}
\`\`\`

**文件路径：**
${pendingOutline.filePath}

请使用 create_notebook_from_outline 工具创建笔记本。`

      // 发送消息给 TopLevelAgent（它会识别确认并调用工具）
      const response = await chatWithTopLevelAgent(confirmMessageWithOutline, currentSessionId)
      const agentResponse = response.data.response

      // 添加 agent 回复到对话中
      setMessages([
        ...messages,
        confirmMessage,
        { role: 'assistant', content: agentResponse },
      ])

      // 清除pending outline
      setPendingOutline(null)

      // 刷新会话列表
      await loadSessions()
    } catch (err) {
      setError(err.response?.data?.detail || '创建笔记本失败')
      console.error('Failed to create notebook:', err)
      // 恢复消息状态
      setMessages(messages)
    } finally {
      setCreatingNotebook(false)
    }
  }

  // 处理大纲取消
  const handleOutlineCancel = () => {
    setPendingOutline(null)
    // 添加取消消息
    setMessages([
      ...messages,
      {
        role: 'assistant',
        content: '已取消创建笔记本。',
      },
    ])
  }

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    // 检查文件类型
    const allowedTypes = [
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/markdown',
      'text/plain',
    ]
    const allowedExtensions = ['.doc', '.docx', '.md', '.markdown']
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()

    if (
      !allowedTypes.includes(file.type) &&
      !allowedExtensions.includes(fileExtension)
    ) {
      setError('不支持的文件类型。请上传 Word (.doc, .docx) 或 Markdown (.md) 文件。')
      return
    }

    try {
      setError(null)

      // 上传文件到服务器
      const uploadResponse = await uploadFile(file)
      const filePath = uploadResponse.data.path
      const fileName = file.name

      // 保存文件信息，但不自动发送
      setUploadedFile({
        path: filePath,
        name: fileName
      })

      // 如果输入框为空，添加提示文本
      if (!inputMessage.trim()) {
        setInputMessage('请处理上传的文件并创建笔记本')
      }

      // 聚焦到输入框，让用户可以继续编辑
      setTimeout(() => {
        inputRef.current?.focus()
      }, 100)
    } catch (err) {
      console.error('文件上传失败:', err)
      setError(err.response?.data?.detail || `文件上传失败: ${err.message}`)
    } finally {
      // 清空文件输入，允许重复选择同一文件
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const drawerWidth = 260

  const theme = useTheme()
  const isDark = theme.mode === 'dark'

  return (
    <Box
      sx={{
        height: '100%',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: isDark ? '#343541' : '#F5F5F7',
      }}
    >
      {/* Main Content Area */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          minHeight: 0,
          overflow: 'hidden',
        }}
      >
        {/* Sidebar */}
      <Drawer
        variant="persistent"
        open={sidebarOpen}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          position: 'relative',
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            bgcolor: isDark ? '#202123' : '#FFFFFF',
            color: isDark ? '#ececf1' : '#1D1D1F',
            borderRight: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)',
            position: 'relative',
            height: '100%',
            top: 0,
            zIndex: 0,
          },
        }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
          }}
        >
            {/* Sidebar Toggle Button */}
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                p: 1.5,
                borderBottom: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)',
              }}
            >
              <Typography
                variant="subtitle2"
                sx={{
                  fontWeight: 600,
                  color: isDark ? '#ececf1' : '#1D1D1F',
                }}
              >
                Chat History
              </Typography>
              <IconButton
                size="small"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                sx={{
                  color: isDark ? '#ececf1' : '#1D1D1F',
                  '&:hover': {
                    bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                  },
                }}
              >
                {sidebarOpen ? <ChevronLeftIcon /> : <MenuIcon />}
              </IconButton>
            </Box>
            
          {/* New Chat Button */}
          <Box
            sx={{
              p: 2,
              borderBottom: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)',
            }}
          >
            <Box
              onClick={handleNewChat}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                p: 1.5,
                borderRadius: '8px',
                bgcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,122,255,0.08)',
                cursor: 'pointer',
                border: isDark ? 'none' : '1px solid rgba(0,122,255,0.15)',
                '&:hover': {
                  bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,122,255,0.12)',
                  borderColor: isDark ? 'none' : 'rgba(0,122,255,0.25)',
                },
                transition: 'all 0.2s',
              }}
            >
              <AddIcon sx={{ fontSize: 20, color: isDark ? '#ececf1' : '#007AFF' }} />
              <Typography 
                variant="body2" 
                sx={{ 
                  fontWeight: 600,
                  color: isDark ? '#ececf1' : '#007AFF',
                }}
              >
                New chat
              </Typography>
            </Box>
          </Box>

          {/* Sessions List */}
          <Box
            sx={{
              flex: 1,
              overflowY: 'auto',
              '&::-webkit-scrollbar': {
                width: '8px',
              },
              '&::-webkit-scrollbar-track': {
                background: '#202123',
              },
              '&::-webkit-scrollbar-thumb': {
                background: '#565869',
                borderRadius: '4px',
                '&:hover': {
                  background: '#6e6f7f',
                },
              },
            }}
          >
            {loading ? (
              <Box sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="body2" sx={{ color: isDark ? '#8e8ea0' : '#86868B' }}>
                  Loading...
                </Typography>
              </Box>
            ) : sessions.length === 0 ? (
              <Box sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="body2" sx={{ color: isDark ? '#8e8ea0' : '#86868B' }}>
                  No chat history
                </Typography>
              </Box>
            ) : (
              <List sx={{ p: 0 }}>
                {sessions.map((session, index) => (
                  <React.Fragment key={session.id}>
                    {index > 0 && (
                      <Divider 
                        sx={{ 
                          borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)',
                        }} 
                      />
                    )}
                    <ListItem
                      disablePadding
                      sx={{
                        bgcolor: currentSessionId === session.id 
                          ? (isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)')
                          : 'transparent',
                        '&:hover': {
                          bgcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)',
                        },
                      }}
                    >
                      <ListItemButton
                        onClick={() => handleSelectSession(session.id)}
                        sx={{
                          py: 1.5,
                          px: 2,
                          '&:hover': {
                            bgcolor: 'transparent',
                          },
                        }}
                      >
                        <ListItemText
                          primary={
                            <Typography
                              variant="body2"
                              sx={{
                                fontWeight: currentSessionId === session.id ? 600 : 500,
                                color: isDark ? '#ececf1' : '#1D1D1F',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                              }}
                            >
                              {session.title || 'New Chat'}
                            </Typography>
                          }
                          secondary={
                            <Typography
                              variant="caption"
                              sx={{
                                color: isDark ? '#8e8ea0' : '#86868B',
                                fontSize: '0.75rem',
                              }}
                            >
                              {formatDate(session.updated_at)}
                            </Typography>
                          }
                        />
                        <IconButton
                          size="small"
                          onClick={(e) => handleDeleteSession(session.id, e)}
                          sx={{
                            color: isDark ? '#8e8ea0' : '#86868B',
                            '&:hover': {
                              color: isDark ? '#ececf1' : '#1D1D1F',
                              bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                            },
                          }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </ListItemButton>
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            )}
          </Box>

          {/* Settings Button */}
          <Box
            sx={{
              p: 2,
              borderTop: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)',
            }}
          >
            <Box
              onClick={() => navigate('/settings')}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                p: 1.5,
                borderRadius: '8px',
                bgcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)',
                cursor: 'pointer',
                '&:hover': {
                  bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)',
                },
                transition: 'background-color 0.2s',
              }}
            >
              <SettingsIcon sx={{ fontSize: 20, color: isDark ? '#ececf1' : '#1D1D1F' }} />
              <Typography 
                variant="body2" 
                sx={{ 
                  fontWeight: 500,
                  color: isDark ? '#ececf1' : '#1D1D1F',
                }}
              >
                Settings
              </Typography>
            </Box>
          </Box>
        </Box>
      </Drawer>

      {/* Main Chat Area */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          minWidth: 0,
          position: 'relative',
        }}
      >
        {error && (
          <Box
            sx={{
              bgcolor: '#ef4444',
              color: 'white',
              p: 2,
              textAlign: 'center',
            }}
          >
            {error}
          </Box>
        )}

        {/* Messages Container */}
        <Box
          sx={{
            flex: 1,
            overflowY: 'auto',
            overflowX: 'hidden',
            px: { xs: 2, sm: 4 },
            py: 4,
            '&::-webkit-scrollbar': {
              width: '8px',
            },
            '&::-webkit-scrollbar-track': {
              background: isDark ? '#343541' : '#F5F5F7',
            },
            '&::-webkit-scrollbar-thumb': {
              background: isDark ? '#565869' : '#C7C7CC',
              borderRadius: '4px',
              '&:hover': {
                background: isDark ? '#6e6f7f' : '#AEAEB2',
              },
            },
          }}
        >
          {/* Current Activity Indicator */}
          {currentActivity && sending && (
            <Box
              sx={{
                mb: 2,
                p: 2,
                borderRadius: '12px',
                bgcolor: isDark ? 'rgba(59, 130, 246, 0.1)' : 'rgba(59, 130, 246, 0.05)',
                border: `1px solid ${isDark ? 'rgba(59, 130, 246, 0.3)' : 'rgba(59, 130, 246, 0.2)'}`,
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
              }}
            >
              <CircularProgress size={16} sx={{ color: '#3b82f6' }} />
              <Box sx={{ flex: 1 }}>
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 600,
                    color: isDark ? '#93c5fd' : '#1e40af',
                    mb: 0.5,
                  }}
                >
                  {currentActivity.agent_info?.name || 'Agent'} 正在处理...
                </Typography>
                <Typography
                  variant="caption"
                  sx={{
                    color: isDark ? '#9ca3af' : '#6b7280',
                    fontSize: '0.75rem',
                  }}
                >
                  {currentActivity.type === 'agent_run' 
                    ? `处理消息: ${currentActivity.message?.substring(0, 50)}...`
                    : currentActivity.message || '执行中...'}
                </Typography>
              </Box>
            </Box>
          )}

          {messages.length === 0 ? (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                textAlign: 'center',
                px: 2,
              }}
            >
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 600,
                  mb: 2,
                  color: isDark ? '#ececf1' : '#1D1D1F',
                  fontSize: { xs: '1.5rem', sm: '2rem' },
                }}
              >
                TopLevelAgent
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: isDark ? '#8e8ea0' : '#86868B',
                  maxWidth: '600px',
                }}
              >
                How can I help you today?
              </Typography>
            </Box>
          ) : (
            <Box>
              {/* Pending Outline Confirmation */}
              {pendingOutline && (
                <Box sx={{ mb: 2, px: { xs: 0, sm: 2 } }}>
                  <OutlineConfirmation
                    outline={pendingOutline.outline}
                    onConfirm={handleOutlineConfirm}
                    onCancel={handleOutlineCancel}
                    onRevise={handleOutlineRevise}
                    isCreating={creatingNotebook}
                    isRevising={creatingNotebook}
                  />
                </Box>
              )}

              {messages.map((message, index) => (
                <Fade in key={index} timeout={300}>
                  <Box
                    sx={{
                      display: 'flex',
                      gap: 2,
                      py: 3,
                      borderBottom: index < messages.length - 1 
                        ? (isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)')
                        : 'none',
                      bgcolor: message.role === 'user' 
                        ? (isDark ? '#343541' : '#FFFFFF')
                        : (isDark ? '#444654' : '#F5F5F7'),
                      mx: -2,
                      px: 2,
                    }}
                  >
                    <Avatar
                      sx={{
                        width: 32,
                        height: 32,
                        bgcolor: message.role === 'user' 
                          ? (isDark ? '#19c37d' : '#007AFF')
                          : (isDark ? '#ab68ff' : '#5856D6'),
                        flexShrink: 0,
                        color: 'white',
                        fontWeight: 600,
                      }}
                    >
                      {message.role === 'user' ? 'U' : 'AI'}
                    </Avatar>
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      {message.role === 'assistant' ? (
                        <Box
                          sx={{
                            '& p': {
                              margin: '0.5em 0',
                              color: isDark ? '#ececf1' : '#1D1D1F',
                              lineHeight: 1.75,
                            },
                            '& pre': {
                              bgcolor: isDark ? '#1e1e1e' : '#F5F5F7',
                              borderRadius: '8px',
                              padding: '16px',
                              overflow: 'auto',
                              margin: '1em 0',
                              border: isDark ? 'none' : '1px solid rgba(0,0,0,0.1)',
                              '& code': {
                                fontFamily: 'Consolas, Monaco, "Courier New", monospace',
                                color: isDark ? '#ececf1' : '#1D1D1F',
                              },
                            },
                            '& code': {
                              bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                              padding: '2px 6px',
                              borderRadius: '4px',
                              fontSize: '0.9em',
                              fontFamily: 'Consolas, Monaco, "Courier New", monospace',
                              color: isDark ? '#ececf1' : '#1D1D1F',
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
                              color: isDark ? '#ececf1' : '#1D1D1F',
                            },
                            '& blockquote': {
                              borderLeft: `4px solid ${isDark ? '#19c37d' : '#007AFF'}`,
                              paddingLeft: '1em',
                              margin: '1em 0',
                              color: isDark ? '#8e8ea0' : '#86868B',
                            },
                            '& table': {
                              borderCollapse: 'collapse',
                              width: '100%',
                              margin: '1em 0',
                              '& th, & td': {
                                border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
                                padding: '8px',
                                color: isDark ? '#ececf1' : '#1D1D1F',
                              },
                              '& th': {
                                bgcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)',
                                fontWeight: 600,
                              },
                            },
                          }}
                        >
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm, remarkMath]}
                            rehypePlugins={[rehypeKatex]}
                            components={{
                              code({ node, inline, className, children, ...props }) {
                                const match = /language-(\w+)/.exec(className || '')
                                return !inline && match ? (
                                  <SyntaxHighlighter
                                    style={vscDarkPlus}
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
                            {message.content}
                          </ReactMarkdown>
                        </Box>
                      ) : (
                        <Typography
                          sx={{
                            color: isDark ? '#ececf1' : '#1D1D1F',
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word',
                            lineHeight: 1.75,
                          }}
                        >
                          {message.content}
                        </Typography>
                      )}
                    </Box>
                  </Box>
                </Fade>
              ))}
              {sending && (
                <Box
                  sx={{
                    display: 'flex',
                    gap: 2,
                    py: 3,
                    bgcolor: isDark ? '#444654' : '#F5F5F7',
                    mx: -2,
                    px: 2,
                  }}
                >
                  <Avatar
                    sx={{
                      width: 32,
                      height: 32,
                      bgcolor: isDark ? '#ab68ff' : '#5856D6',
                      flexShrink: 0,
                    }}
                  >
                    AI
                  </Avatar>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CircularProgress size={16} sx={{ color: isDark ? '#ececf1' : '#1D1D1F' }} />
                    <Typography sx={{ color: isDark ? '#8e8ea0' : '#86868B', fontSize: '0.875rem' }}>
                      Thinking...
                    </Typography>
                  </Box>
                </Box>
              )}
              <div ref={messagesEndRef} />
            </Box>
          )}
        </Box>

        {/* Input Container */}
        <Box
          sx={{
            borderTop: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)',
            bgcolor: isDark ? '#343541' : '#F5F5F7',
            px: { xs: 2, sm: 4 },
            py: 2,
          }}
        >
          {/* Uploaded file info */}
          {uploadedFile && (
            <Box
              sx={{
                mb: 1.5,
                p: 1.5,
                borderRadius: '8px',
                bgcolor: isDark ? '#40414f' : '#FFFFFF',
                border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
                display: 'flex',
                alignItems: 'center',
                gap: 1,
              }}
            >
              <FileIcon sx={{ fontSize: 20, color: isDark ? '#19c37d' : '#007AFF' }} />
              <Typography
                variant="body2"
                sx={{
                  flex: 1,
                  color: isDark ? '#ececf1' : '#1D1D1F',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {uploadedFile.name}
              </Typography>
              <IconButton
                size="small"
                onClick={() => setUploadedFile(null)}
                sx={{
                  color: isDark ? '#8e8ea0' : '#86868B',
                  '&:hover': {
                    color: isDark ? '#ececf1' : '#1D1D1F',
                    bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                  },
                }}
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            </Box>
          )}
          
          <Paper
            sx={{
              display: 'flex',
              alignItems: 'flex-end',
              gap: 1,
              bgcolor: isDark ? '#40414f' : '#FFFFFF',
              borderRadius: '12px',
              px: 2,
              py: 1,
              border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
              boxShadow: isDark ? 'none' : '0 2px 8px rgba(0,0,0,0.05)',
              '&:focus-within': {
                borderColor: isDark ? '#19c37d' : '#007AFF',
                boxShadow: isDark ? 'none' : '0 2px 12px rgba(0,122,255,0.15)',
              },
            }}
          >
            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".doc,.docx,.md,.markdown"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
            {/* Upload button */}
            <IconButton
              onClick={handleFileUpload}
              disabled={sending}
              sx={{
                color: isDark ? '#8e8ea0' : '#86868B',
                '&:hover': {
                  color: isDark ? '#ececf1' : '#1D1D1F',
                  bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                },
                '&:disabled': {
                  color: isDark ? '#565869' : '#C7C7CC',
                },
              }}
              title="上传笔记 (Word/Markdown)"
            >
              <AttachFileIcon />
            </IconButton>
            <TextField
              inputRef={inputRef}
              fullWidth
              multiline
              maxRows={6}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Message TopLevelAgent..."
              disabled={sending}
              variant="standard"
              InputProps={{
                disableUnderline: true,
                sx: {
                  color: isDark ? '#ececf1' : '#1D1D1F',
                  fontSize: '1rem',
                  '&::placeholder': {
                    color: isDark ? '#8e8ea0' : '#86868B',
                    opacity: 1,
                  },
                },
              }}
              sx={{
                '& .MuiInputBase-root': {
                  color: isDark ? '#ececf1' : '#1D1D1F',
                },
              }}
            />
            <IconButton
              onClick={sending ? handleStop : handleSend}
              disabled={!inputMessage.trim() && !uploadedFile && !sending}
              sx={{
                color: sending ? '#ef4444' : (isDark ? '#19c37d' : '#007AFF'),
                '&:hover': {
                  bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                },
                '&:disabled': {
                  color: isDark ? '#565869' : '#C7C7CC',
                },
              }}
            >
              {sending ? <StopIcon /> : <SendIcon />}
            </IconButton>
          </Paper>
        </Box>
        </Box>
      </Box>
    </Box>
  )
}

export default ChatPage


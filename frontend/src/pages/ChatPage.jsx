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
  Card,
  CardContent,
  CardActionArea,
  Chip,
  Button,
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
  MenuBook as MenuBookIcon,
  ArrowForward as ArrowForwardIcon,
  Image as ImageIcon,
} from '@mui/icons-material'
import { Menu, MenuItem } from '@mui/material'
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
  sourceChatWithTopLevelAgent,
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
import AgentAvatar from '../components/AgentAvatar'

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
  const [uploadedImages, setUploadedImages] = useState([]) // Array of { file: File, preview: string, base64: string }
  const [pendingOutline, setPendingOutline] = useState(null) // { outline: object, userRequest: string, filePath: string }
  const [creatingNotebook, setCreatingNotebook] = useState(false)
  const [currentActivity, setCurrentActivity] = useState(null) // Current agent activity from tracing
  const tracingPollIntervalRef = useRef(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const fileInputRef = useRef(null)
  const imageInputRef = useRef(null)
  const paperInputRef = useRef(null)
  
  
  // 菜单状态
  const [menuAnchorEl, setMenuAnchorEl] = useState(null)
  const menuOpen = Boolean(menuAnchorEl)

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

  // Convert image file to base64
  const imageToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        const base64 = reader.result
        resolve(base64)
      }
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }

  const handleSend = async () => {
    if ((!inputMessage.trim() && !uploadedFile && uploadedImages.length === 0) || sending) return
    
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
    
    // 检查最近的助手消息是否是题目原文，如果是，自动包含题目原文以保持上下文
    const recentQuestionText = messages
      .slice()
      .reverse()
      .find(msg => msg.role === 'assistant' && msg.isQuestionText)
    
    if (recentQuestionText && recentQuestionText.content) {
      // 如果最近的助手消息是题目原文，将题目原文包含在消息中
      // 这样系统就能理解用户指的是哪道题
      userMessage = `以下是之前识别的题目原文：\n\n${recentQuestionText.content}\n\n---\n\n${userMessage}`
    }
    
    // 准备图片数据（base64格式）
    const images = []
    if (uploadedImages.length > 0) {
      for (const img of uploadedImages) {
        if (img.base64) {
          // 检测图片类型
          const mimeType = img.file.type || 'image/jpeg'
          images.push({
            type: "input_image",
            detail: "auto",
            image_url: img.base64, // base64 already includes data:image/...;base64, prefix
          })
        }
      }
    }
    
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
    const savedImages = [...uploadedImages]

    setInputMessage('')
    setUploadedFile(null) // 清空上传的文件信息
    setUploadedImages([]) // 清空上传的图片
    setSending(true)
    setError(null)

    // 添加用户消息到界面（显示原始输入，不显示文件路径）
    const displayMessage = inputMessage.trim() || 
      (uploadedFile ? `[已上传文件: ${uploadedFile.name}]` : '') ||
      (uploadedImages.length > 0 ? `[已上传 ${uploadedImages.length} 张图片]` : '')
    const newMessages = [...messages, { 
      role: 'user', 
      content: displayMessage,
      images: savedImages.length > 0 ? savedImages.map(img => img.preview) : null
    }]
    setMessages(newMessages)

    try {
      // 发送消息给 TopLevelAgent（包含图片）
      const response = await chatWithTopLevelAgent(userMessage, sessionId, images.length > 0 ? images : null)
      const agentResponse = response.data.response
      const structuredData = response.data.structured_data || null

      // 检测是否是大纲确认消息
      // 优先使用 structured_data（来自 API）
      let outline = null
      if (structuredData && structuredData.type === 'outline' && structuredData.outline) {
        outline = structuredData.outline
      } else {
        // 后备方案：尝试从JSON代码块中提取大纲
        try {
          const jsonMatch = agentResponse.match(/```json\s*([\s\S]*?)\s*```/)
          if (jsonMatch) {
            const outlineData = JSON.parse(jsonMatch[1])
            if (outlineData.outline) {
              outline = outlineData.outline
            } else {
              outline = outlineData
            }
          }
        } catch (err) {
          // JSON解析失败，尝试文本解析
          outline = parseOutlineFromMessage(agentResponse)
        }
      }
      
      // 如果有大纲，保存到消息的 structured_data 中（不再使用 pendingOutline）
      if (outline && structuredData && structuredData.type === 'outline') {
        // 保存完整的大纲数据（包括 file_path 和 user_request）
        setMessages([
          ...newMessages,
          { 
            role: 'assistant', 
            content: agentResponse, 
            structured_data: structuredData 
          },
        ])
      } else {
        // 普通消息，添加到对话中（包含结构化数据）
        setMessages([
          ...newMessages,
          { role: 'assistant', content: agentResponse, structured_data: structuredData },
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

  const handleImageUpload = () => {
    imageInputRef.current?.click()
  }

  // 处理菜单点击
  const handleMenuClick = (event) => {
    setMenuAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setMenuAnchorEl(null)
  }

  // 处理添加题目图片
  const handleAddQuestionImage = () => {
    imageInputRef.current?.click()
    handleMenuClose()
  }

  // 处理上传笔记
  const handleAddNotebook = () => {
    fileInputRef.current?.click()
    handleMenuClose()
  }

  // 处理上传论文
  const handleAddPaper = () => {
    paperInputRef.current?.click()
    handleMenuClose()
  }

  // 处理论文上传
  const handlePaperChange = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    // 检查是否为PDF文件
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (fileExtension !== '.pdf' && file.type !== 'application/pdf') {
      setError('请上传PDF格式的论文文件')
      return
    }

    try {
      setError(null)

      // 上传文件到服务器
      const uploadResponse = await uploadFile(file)
      const filePath = uploadResponse.data.path
      const fileName = file.name

      // 保存文件信息
      setUploadedFile({
        path: filePath,
        name: fileName
      })

      // 设置输入消息，自动触发论文处理
      setInputMessage('请根据这篇论文创建笔记')

      // 等待状态更新后自动发送
      setTimeout(() => {
        handleSend()
      }, 100)

    } catch (err) {
      console.error('论文上传失败:', err)
      setError(err.response?.data?.detail || `论文上传失败: ${err.message}`)
    } finally {
      // 清空文件输入，允许重复选择同一文件
      if (paperInputRef.current) {
        paperInputRef.current.value = ''
      }
    }
  }


  // 处理题目图片上传（聊天式流程）
  const handleQuestionImageChange = async (event) => {
    const files = Array.from(event.target.files || [])
    if (files.length === 0) return

    // 只允许一张图片
    const file = files[0]

    // Check file types
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      setError('不支持的文件类型。请上传图片文件（JPEG, PNG, GIF, WebP）。')
      return
    }

    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError(`图片 ${file.name} 太大，最大支持 10MB`)
      return
    }

    try {
      setError(null)
      
      // Create preview
      const preview = URL.createObjectURL(file)
      
      // Convert to base64
      const base64 = await imageToBase64(file)
      
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

      // 准备图片数据
      const images = [{
        type: "input_image",
        detail: "auto",
        image_url: base64,
      }]

      // 添加用户消息（显示图片）
      const userMsg = {
        role: 'user',
        content: '[已上传题目图片]',
        images: [preview],
        isQuestionImage: true, // 标记为题目图片
      }
      setMessages(prev => [...prev, userMsg])

      // 自动发送识别消息
      setSending(true)
      try {
        const response = await sourceChatWithTopLevelAgent(
          "请识别这张图片中的题目，并提取出题目的完整原文。只返回题目原文，不要添加任何解释。",
          sessionId,
          null,
          images
        )
        
        // 添加助手回复（题目原文）
        const assistantMsg = {
          role: 'assistant',
          content: response.data.response,
          isQuestionText: true, // 标记为题目原文
        }
        setMessages(prev => [...prev, assistantMsg])
      } catch (err) {
        console.error('识别题目失败:', err)
        setError(`识别题目失败: ${err.message}`)
        const errorMsg = {
          role: 'assistant',
          content: `错误: ${err.message}`,
        }
        setMessages(prev => [...prev, errorMsg])
      } finally {
        setSending(false)
      }
    } catch (err) {
      console.error('图片处理失败:', err)
      setError(`图片处理失败: ${err.message}`)
    } finally {
      // Clear file input
      if (imageInputRef.current) {
        imageInputRef.current.value = ''
      }
      // 关闭菜单
      setMenuAnchorEl(null)
    }
  }

  // 处理"得到答案"按钮点击
  const handleGetAnswerFromMessage = async (questionText) => {
    if (!questionText || sending) return
    
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

    // 添加用户消息（包含题目原文，确保上下文清晰）
    const userMsg = {
      role: 'user',
      content: `请解答以下题目：\n\n${questionText}\n\n请提供详细的解答过程和最终答案。`,
    }
    setMessages(prev => [...prev, userMsg])

    // 发送请求（使用相同的消息内容，确保上下文一致）
    setSending(true)
    setError(null)
    try {
      const response = await chatWithTopLevelAgent(
        `请解答以下题目：\n\n${questionText}\n\n请提供详细的解答过程和最终答案。`,
        sessionId
      )
      
      // 添加助手回复
      const assistantMsg = {
        role: 'assistant',
        content: response.data.response,
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      console.error('获取答案失败:', err)
      setError(`获取答案失败: ${err.message}`)
      const errorMsg = {
        role: 'assistant',
        content: `错误: ${err.message}`,
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setSending(false)
    }
  }

  // 处理"得到提示"按钮点击
  const handleGetHintFromMessage = async (questionText) => {
    if (!questionText || sending) return
    
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

    // 添加用户消息（包含题目原文，确保上下文清晰）
    const userMsg = {
      role: 'user',
      content: `请为以下题目提供提示（不要直接给出答案，只给提示）：\n\n${questionText}`,
    }
    setMessages(prev => [...prev, userMsg])

    // 发送请求（使用相同的消息内容，确保上下文一致）
    setSending(true)
    setError(null)
    try {
      const response = await chatWithTopLevelAgent(
        `请为以下题目提供提示（不要直接给出答案，只给提示）：\n\n${questionText}`,
        sessionId
      )
      
      // 添加助手回复
      const assistantMsg = {
        role: 'assistant',
        content: response.data.response,
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      console.error('获取提示失败:', err)
      setError(`获取提示失败: ${err.message}`)
      const errorMsg = {
        role: 'assistant',
        content: `错误: ${err.message}`,
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setSending(false)
    }
  }

  // 处理普通图片上传（用于聊天）
  const handleImageChange = async (event) => {
    const files = Array.from(event.target.files || [])
    if (files.length === 0) return

    // Check file types
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    const invalidFiles = files.filter(file => !allowedTypes.includes(file.type))
    
    if (invalidFiles.length > 0) {
      setError('不支持的文件类型。请上传图片文件（JPEG, PNG, GIF, WebP）。')
      return
    }

    try {
      setError(null)
      const newImages = []

      for (const file of files) {
        // Check file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
          setError(`图片 ${file.name} 太大，最大支持 10MB`)
          continue
        }

        // Create preview
        const preview = URL.createObjectURL(file)
        
        // Convert to base64
        const base64 = await imageToBase64(file)
        
        newImages.push({
          file,
          preview,
          base64,
        })
      }

      setUploadedImages(prev => [...prev, ...newImages])
    } catch (err) {
      console.error('图片处理失败:', err)
      setError(`图片处理失败: ${err.message}`)
    } finally {
      // Clear file input
      if (imageInputRef.current) {
        imageInputRef.current.value = ''
      }
    }
  }

  const handleRemoveImage = (index) => {
    setUploadedImages(prev => {
      const newImages = [...prev]
      // Revoke object URL to free memory
      URL.revokeObjectURL(newImages[index].preview)
      newImages.splice(index, 1)
      return newImages
    })
  }

  // 从消息中解析笔记本创建信息
  const parseNotebookCreationInfo = (message) => {
    // 首先尝试解析 JSON 格式的结构化数据（后端返回的格式）
    try {
      // 尝试解析整个消息为 JSON
      const jsonData = JSON.parse(message.trim())
      if (jsonData.status === 'success' && jsonData.notebook_id && jsonData.notebook_title) {
        return {
          notebookId: jsonData.notebook_id,
          notebookTitle: jsonData.notebook_title,
        }
      }
    } catch (e) {
      // 不是 JSON，继续尝试其他方式
    }
    
    // 尝试从消息中提取 JSON 对象（可能消息包含其他文本 + JSON）
    try {
      // 匹配包含 notebook_id 和 notebook_title 的 JSON 对象
      const jsonMatch = message.match(/\{[\s\S]*"notebook_id"[\s\S]*"notebook_title"[\s\S]*\}/)
      if (jsonMatch) {
        const jsonData = JSON.parse(jsonMatch[0])
        // 必须同时满足：status 为 success，且有 notebook_id 和 notebook_title
        if (jsonData.status === 'success' && jsonData.notebook_id && jsonData.notebook_title) {
          return {
            notebookId: jsonData.notebook_id,
            notebookTitle: jsonData.notebook_title,
          }
        }
      }
    } catch (e) {
      // JSON 解析失败
    }
    
    // 后备方案：尝试从文本格式中提取（Agent 可能把 JSON 转换成了文本）
    // 匹配格式：ID: xxx 和 标题: xxx
    try {
      // 匹配 "ID: " 或 "ID：" 后面的 UUID 或短 ID
      const idMatch = message.match(/ID[：:]\s*([a-f0-9\-]+)/i)
      // 匹配 "标题: " 或 "标题：" 后面的内容（到换行或下一个字段为止）
      const titleMatch = message.match(/标题[：:]\s*([^\n\r]+)/i)
      
      if (idMatch && titleMatch) {
        const notebookId = idMatch[1].trim()
        const notebookTitle = titleMatch[1].trim()
        
        // 验证 ID 格式（UUID 或短 ID）
        if (notebookId && notebookTitle && (notebookId.length >= 8 || notebookId.includes('-'))) {
          return {
            notebookId: notebookId,
            notebookTitle: notebookTitle,
          }
        }
      }
    } catch (e) {
      // 文本解析失败
    }
    
    // 如果都失败了，返回 null
    return null
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
      'application/pdf',
    ]
    const allowedExtensions = ['.doc', '.docx', '.md', '.markdown', '.pdf']
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()

    if (
      !allowedTypes.includes(file.type) &&
      !allowedExtensions.includes(fileExtension)
    ) {
      setError('不支持的文件类型。请上传 Word (.doc, .docx)、Markdown (.md) 或 PDF (.pdf) 文件。')
      return
    }

    try {
      setError(null)

      // 上传文件到服务器
      const uploadResponse = await uploadFile(file)
      const filePath = uploadResponse.data.path
      const fileName = file.name

      // 保存文件信息
      setUploadedFile({
        path: filePath,
        name: fileName
      })

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

      // 自动设置消息并发送，生成大纲
      const userMessage = '请根据文件内容创建笔记本'

      // 添加用户消息到界面
      const userMsg = {
        role: 'user',
        content: `[已上传文件: ${fileName}]`,
      }
      setMessages(prev => [...prev, userMsg])

      // 发送请求
      setSending(true)
      try {
        const response = await sourceChatWithTopLevelAgent(
          userMessage,
          sessionId,
          filePath,
          null
        )

        // 添加助手回复
        const assistantMsg = {
          role: 'assistant',
          content: response.data.response,
          structured_data: response.data.structured_data,
        }
        setMessages(prev => [...prev, assistantMsg])

        // 检查是否包含大纲信息
        const structuredData = response.data.structured_data
        if (structuredData && structuredData.type === 'outline' && structuredData.outline) {
          setPendingOutline({
            outline: structuredData.outline,
            userRequest: structuredData.user_request || userMessage,
            filePath: structuredData.file_path || filePath
          })
        }
      } catch (err) {
        console.error('处理文件失败:', err)
        setError(`处理文件失败: ${err.message}`)
        const errorMsg = {
          role: 'assistant',
          content: `错误: ${err.message}`,
        }
        setMessages(prev => [...prev, errorMsg])
      } finally {
        setSending(false)
        setUploadedFile(null) // 清空上传的文件信息
      }

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
                          {(() => {
                            // 检测消息中是否包含纯 JSON（没有代码块包裹）
                            const content = message.content
                            
                            // 检查是否已经包含 JSON 代码块
                            const hasJsonBlock = /```json\s*[\s\S]*?\s*```/.test(content)
                            
                            if (hasJsonBlock) {
                              // 已经有 JSON 代码块，直接用 ReactMarkdown 渲染
                              return (
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
                                  {content}
                                </ReactMarkdown>
                              )
                            }
                            
                            // 尝试检测并格式化纯 JSON（没有代码块包裹）
                            // 匹配 JSON 对象：以 { 开头，以 } 结尾，可能包含换行
                            const jsonObjectRegex = /\{[\s\S]*?\}/
                            const jsonMatch = content.match(jsonObjectRegex)
                            
                            if (jsonMatch) {
                              try {
                                // 尝试解析 JSON
                                const jsonContent = JSON.parse(jsonMatch[0])
                                // 将 JSON 部分替换为格式化的代码块
                                const formattedContent = content.replace(
                                  jsonObjectRegex,
                                  `\`\`\`json\n${JSON.stringify(jsonContent, null, 2)}\n\`\`\``
                                )
                                
                                // 用 ReactMarkdown 渲染（现在包含格式化的 JSON 代码块）
                                return (
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
                                    {formattedContent}
                                  </ReactMarkdown>
                                )
                              } catch (e) {
                                // JSON 解析失败，按普通 Markdown 处理
                              }
                            }
                            
                            // 默认用 ReactMarkdown 渲染（处理 Markdown 格式）
                            return (
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
                                {content}
                              </ReactMarkdown>
                            )
                          })()}
                          
                          {/* 如果是题目原文，显示操作按钮 */}
                          {message.isQuestionText && (
                            <Box sx={{ display: 'flex', gap: 1, mt: 2, flexWrap: 'wrap' }}>
                              <Button
                                variant="contained"
                                size="small"
                                onClick={() => handleGetAnswerFromMessage(message.content)}
                                disabled={sending}
                                sx={{
                                  bgcolor: isDark ? '#19c37d' : '#007AFF',
                                  color: 'white',
                                  '&:hover': {
                                    bgcolor: isDark ? '#16a86a' : '#0051D5',
                                  },
                                  '&:disabled': {
                                    bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                                    color: isDark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.5)',
                                  },
                                }}
                              >
                                得到答案
                              </Button>
                              <Button
                                variant="outlined"
                                size="small"
                                onClick={() => handleGetHintFromMessage(message.content)}
                                disabled={sending}
                                sx={{
                                  borderColor: isDark ? '#19c37d' : '#007AFF',
                                  color: isDark ? '#19c37d' : '#007AFF',
                                  '&:hover': {
                                    borderColor: isDark ? '#16a86a' : '#0051D5',
                                    bgcolor: isDark ? 'rgba(25,195,125,0.1)' : 'rgba(0,122,255,0.1)',
                                  },
                                  '&:disabled': {
                                    borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                                    color: isDark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.5)',
                                  },
                                }}
                              >
                                得到提示
                              </Button>
                            </Box>
                          )}
                        </Box>
                      ) : (
                        <Box>
                          {/* Display images if any */}
                          {message.images && message.images.length > 0 && (
                            <Box
                              sx={{
                                display: 'flex',
                                gap: 1,
                                flexWrap: 'wrap',
                                mb: message.content ? 1.5 : 0,
                              }}
                            >
                              {message.images.map((imgPreview, imgIndex) => (
                                <Box
                                  key={imgIndex}
                                  sx={{
                                    width: 120,
                                    height: 120,
                                    borderRadius: '8px',
                                    overflow: 'hidden',
                                    border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
                                    bgcolor: isDark ? '#40414f' : '#FFFFFF',
                                  }}
                                >
                                  <img
                                    src={imgPreview}
                                    alt={`Upload ${imgIndex + 1}`}
                                    style={{
                                      width: '100%',
                                      height: '100%',
                                      objectFit: 'cover',
                                    }}
                                  />
                                </Box>
                              ))}
                            </Box>
                          )}
                          {/* Display text content */}
                          {message.content && (
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
                      )}
                      
                      {/* 检测并显示大纲卡片 */}
                      {message.role === 'assistant' && message.structured_data && message.structured_data.type === 'outline' && (() => {
                        const outlineData = message.structured_data
                        const outline = outlineData.outline
                        const glowColor = '#007AFF' // 蓝色 - outline
                        
                        const handleOutlineConfirm = async () => {
                          try {
                            setSending(true)
                            setError(null)
                            
                            // 构建确认消息，格式与 TopLevelAgent 期望的一致
                            const outlineJson = JSON.stringify(outline, null, 2)
                            const confirmMessage = `确认创建笔记本。

**大纲信息（JSON格式）：**
\`\`\`json
${outlineJson}
\`\`\`

${outlineData.file_path ? `**文件路径：**\n${outlineData.file_path}\n\n` : ''}请根据此大纲创建笔记本。`
                            
                            const response = await chatWithTopLevelAgent(confirmMessage, sessionId)
                            const agentResponse = response.data.response
                            const newStructuredData = response.data.structured_data || null
                            
                            // 添加确认消息
                            setMessages(prev => [
                              ...prev,
                              { 
                                role: 'user', 
                                content: '确认创建笔记本',
                                structured_data: null 
                              },
                              { 
                                role: 'assistant', 
                                content: agentResponse,
                                structured_data: newStructuredData 
                              },
                            ])
                            
                            await loadSessions()
                          } catch (err) {
                            setError(err.response?.data?.detail || 'Failed to confirm outline')
                            console.error('Error confirming outline:', err)
                          } finally {
                            setSending(false)
                          }
                        }
                        
                        return (
                          <Box sx={{ mt: 2, maxWidth: 500 }}>
                            <Box
                              sx={{
                                position: 'relative',
                                borderRadius: 4,
                                p: 3,
                                bgcolor: isDark ? '#2C2C2E' : 'white',
                                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                overflow: 'hidden',
                                border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)',
                                display: 'flex',
                                flexDirection: 'column',
                                boxShadow: isDark ? '0 4px 16px rgba(0,0,0,0.3)' : '0 4px 16px rgba(0,0,0,0.08)',
                              }}
                            >
                              {/* Glow effect */}
                              <Box
                                sx={{
                                  position: 'absolute',
                                  top: -50,
                                  right: -50,
                                  width: 100,
                                  height: 100,
                                  borderRadius: '50%',
                                  background: `radial-gradient(circle, ${glowColor}40, transparent 70%)`,
                                  filter: 'blur(25px)',
                                  opacity: 0.4,
                                }}
                              />
                              
                              {/* Content */}
                              <Box sx={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column' }}>
                                {/* Header */}
                                <Box sx={{ mb: 2 }}>
                                  <Typography
                                    variant="h6"
                                    sx={{
                                      fontWeight: 600,
                                      color: isDark ? '#ececf1' : '#1D1D1F',
                                      mb: 0.5,
                                    }}
                                  >
                                    📋 大纲已生成
                                  </Typography>
                                  <Typography
                                    variant="body2"
                                    sx={{
                                      color: isDark ? '#8e8ea0' : '#86868B',
                                    }}
                                  >
                                    {outline.notebook_title}
                                  </Typography>
                                </Box>
                                
                                {/* Description */}
                                {outline.notebook_description && (
                                  <Box sx={{ mb: 2 }}>
                                    <Typography
                                      variant="body2"
                                      sx={{
                                        color: isDark ? '#8e8ea0' : '#86868B',
                                        whiteSpace: 'pre-wrap',
                                        lineHeight: 1.6,
                                        display: '-webkit-box',
                                        WebkitLineClamp: 3,
                                        WebkitBoxOrient: 'vertical',
                                        overflow: 'hidden',
                                      }}
                                    >
                                      {outline.notebook_description}
                                    </Typography>
                                  </Box>
                                )}
                                
                                {/* Sections count */}
                                <Box sx={{ mb: 2 }}>
                                  <Typography
                                    variant="body2"
                                    sx={{
                                      color: isDark ? '#8e8ea0' : '#86868B',
                                    }}
                                  >
                                    共 {Object.keys(outline.outlines || {}).length} 个章节
                                  </Typography>
                                </Box>
                                
                                {/* Divider */}
                                <Divider sx={{ my: 1.5, borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)' }} />
                                
                                {/* Actions */}
                                <Box sx={{ display: 'flex', gap: 1.5, justifyContent: 'flex-end' }}>
                                  <Button
                                    variant="outlined"
                                    size="small"
                                    onClick={() => {
                                      // 显示完整大纲确认UI（使用旧的 OutlineConfirmation 组件）
                                      setPendingOutline({
                                        outline: outline,
                                        userRequest: outlineData.user_request || '',
                                        filePath: outlineData.file_path || null,
                                      })
                                    }}
                                    disabled={sending}
                                    sx={{
                                      borderColor: isDark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)',
                                      color: isDark ? '#ececf1' : '#1D1D1F',
                                      '&:hover': {
                                        borderColor: isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)',
                                        bgcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
                                      },
                                    }}
                                  >
                                    查看详情
                                  </Button>
                                  <Button
                                    variant="contained"
                                    size="small"
                                    onClick={handleOutlineConfirm}
                                    disabled={sending}
                                    sx={{
                                      bgcolor: glowColor,
                                      color: 'white',
                                      '&:hover': {
                                        bgcolor: '#0051D5',
                                      },
                                      '&:disabled': {
                                        bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                                        color: isDark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.5)',
                                      },
                                    }}
                                  >
                                    {sending ? '创建中...' : '确认并创建'}
                                  </Button>
                                </Box>
                              </Box>
                            </Box>
                          </Box>
                        )
                      })()}
                      
                      {/* 检测并显示笔记本创建卡片 */}
                      {message.role === 'assistant' && (() => {
                        // 优先使用 structured_data（来自 API）
                        let notebookInfo = null
                        if (message.structured_data && message.structured_data.notebook_id && message.structured_data.notebook_title) {
                          notebookInfo = {
                            notebookId: message.structured_data.notebook_id,
                            notebookTitle: message.structured_data.notebook_title,
                          }
                        } else {
                          // 后备方案：从消息内容中解析
                          notebookInfo = parseNotebookCreationInfo(message.content)
                        }
                        
                        if (notebookInfo) {
                          const glowColor = '#34C759' // 绿色 - notebook agent
                          return (
                            <Box sx={{ mt: 2, maxWidth: 400 }}>
                              <Box
                                onClick={() => navigate(`/agents/${notebookInfo.notebookId}`)}
                                sx={{
                                  position: 'relative',
                                  borderRadius: 4,
                                  p: 3,
                                  bgcolor: isDark ? '#2C2C2E' : 'white',
                                  cursor: 'pointer',
                                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                  overflow: 'hidden',
                                  border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)',
                                  display: 'flex',
                                  flexDirection: 'column',
                                  '&:hover': {
                                    transform: 'translateY(-8px)',
                                    boxShadow: isDark
                                      ? `0 20px 40px ${glowColor}40, 0 0 0 1px ${glowColor}30`
                                      : `0 20px 40px ${glowColor}40, 0 0 0 1px ${glowColor}30`,
                                  },
                                  '&::before': {
                                    content: '""',
                                    position: 'absolute',
                                    inset: -2,
                                    borderRadius: 4,
                                    padding: '2px',
                                    background: `linear-gradient(135deg, ${glowColor}80, ${glowColor}40, transparent, ${glowColor}60)`,
                                    WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
                                    WebkitMaskComposite: 'xor',
                                    maskComposite: 'exclude',
                                    opacity: 0,
                                    transition: 'opacity 0.3s',
                                    zIndex: 0,
                                  },
                                  '&:hover::before': {
                                    opacity: 1,
                                  },
                                  boxShadow: isDark ? '0 4px 16px rgba(0,0,0,0.3)' : '0 4px 16px rgba(0,0,0,0.08)',
                                }}
                              >
                                {/* Glow effect */}
                                <Box
                                  sx={{
                                    position: 'absolute',
                                    top: -50,
                                    right: -50,
                                    width: 100,
                                    height: 100,
                                    borderRadius: '50%',
                                    background: `radial-gradient(circle, ${glowColor}40, transparent 70%)`,
                                    filter: 'blur(25px)',
                                    opacity: 0.4,
                                    transition: 'opacity 0.3s',
                                  }}
                                />
                                <Box
                                  sx={{
                                    position: 'absolute',
                                    bottom: -30,
                                    left: -30,
                                    width: 80,
                                    height: 80,
                                    borderRadius: '50%',
                                    background: `radial-gradient(circle, ${glowColor}30, transparent 70%)`,
                                    filter: 'blur(20px)',
                                    opacity: 0.3,
                                    transition: 'opacity 0.3s',
                                  }}
                                />

                                {/* Content */}
                                <Box sx={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column' }}>
                                  {/* Header Section: Avatar + Title */}
                                  <Box
                                    sx={{
                                      display: 'flex',
                                      alignItems: 'flex-start',
                                      gap: 2,
                                      mb: 2,
                                    }}
                                  >
                                    {/* Agent Avatar */}
                                    <AgentAvatar 
                                      seed={notebookInfo.notebookId} 
                                      size={56}
                                      sx={{
                                        border: `2px solid ${glowColor}30`,
                                        boxShadow: `0 2px 8px ${glowColor}20`,
                                        flexShrink: 0,
                                      }}
                                    />
                                    
                                    {/* Notebook Title */}
                                    <Box sx={{ flex: 1, minWidth: 0, pt: 0.5 }}>
                                      <Typography
                                        variant="h6"
                                        sx={{
                                          fontWeight: 600,
                                          color: isDark ? '#ececf1' : '#1D1D1F',
                                          overflow: 'hidden',
                                          textOverflow: 'ellipsis',
                                          display: '-webkit-box',
                                          WebkitLineClamp: 2,
                                          WebkitBoxOrient: 'vertical',
                                          lineHeight: 1.3,
                                          mb: 0.5,
                                        }}
                                      >
                                        {notebookInfo.notebookTitle}
                                      </Typography>
                                      
                                      <Typography
                                        variant="body2"
                                        sx={{
                                          color: isDark ? '#8e8ea0' : '#86868B',
                                          fontFamily: 'monospace',
                                          fontSize: '0.75rem',
                                          overflow: 'hidden',
                                          textOverflow: 'ellipsis',
                                          whiteSpace: 'nowrap',
                                        }}
                                      >
                                        {notebookInfo.notebookId}
                                      </Typography>
                                    </Box>
                                  </Box>

                                  {/* Divider */}
                                  <Divider sx={{ my: 1.5, borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)' }} />

                                  {/* Tag */}
                                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                    <Chip
                                      label="Notebook"
                                      size="small"
                                      sx={{
                                        bgcolor: `${glowColor}15`,
                                        color: glowColor,
                                        fontWeight: 500,
                                        fontSize: '0.7rem',
                                        height: 24,
                                      }}
                                    />
                                  </Box>
                                </Box>
                              </Box>
                            </Box>
                          )
                        }
                        return null
                      })()}
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
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    {currentActivity ? (
                      <Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                          <CircularProgress size={16} sx={{ color: isDark ? '#ececf1' : '#1D1D1F' }} />
                          <Typography 
                            sx={{ 
                              color: isDark ? '#ececf1' : '#1D1D1F', 
                              fontSize: '0.875rem',
                              fontWeight: 600,
                            }}
                          >
                            {currentActivity.agent_info?.name || 'Agent'}
                            {currentActivity.type === 'tool_call' ? ' 正在调用工具' : ' 正在处理'}
                          </Typography>
                        </Box>
                        <Typography 
                          sx={{ 
                            color: isDark ? '#8e8ea0' : '#86868B', 
                            fontSize: '0.75rem',
                            ml: 3,
                          }}
                        >
                          {currentActivity.type === 'agent_run' 
                            ? `处理消息: ${currentActivity.message?.substring(0, 80)}${currentActivity.message?.length > 80 ? '...' : ''}`
                            : currentActivity.type === 'tool_call'
                            ? (() => {
                                // 从 message 中提取工具名称
                                const toolMatch = currentActivity.message?.match(/Calling tool:\s*(.+?)(?:\s+with|$)/i)
                                const toolName = toolMatch ? toolMatch[1] : '工具'
                                return `调用工具: ${toolName}`
                              })()
                            : currentActivity.message || '执行中...'}
                        </Typography>
                      </Box>
                    ) : (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CircularProgress size={16} sx={{ color: isDark ? '#ececf1' : '#1D1D1F' }} />
                        <Typography sx={{ color: isDark ? '#8e8ea0' : '#86868B', fontSize: '0.875rem' }}>
                          Thinking...
                        </Typography>
                      </Box>
                    )}
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


          {/* Uploaded images preview (for regular chat) */}
          {uploadedImages.length > 0 && (
            <Box
              sx={{
                mb: 1.5,
                display: 'flex',
                gap: 1,
                flexWrap: 'wrap',
              }}
            >
              {uploadedImages.map((img, index) => (
                <Box
                  key={index}
                  sx={{
                    position: 'relative',
                    width: 80,
                    height: 80,
                    borderRadius: '8px',
                    overflow: 'hidden',
                    border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
                    bgcolor: isDark ? '#40414f' : '#FFFFFF',
                  }}
                >
                  <img
                    src={img.preview}
                    alt={`Upload ${index + 1}`}
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                    }}
                  />
                  <IconButton
                    size="small"
                    onClick={() => handleRemoveImage(index)}
                    sx={{
                      position: 'absolute',
                      top: 4,
                      right: 4,
                      bgcolor: 'rgba(0,0,0,0.5)',
                      color: 'white',
                      width: 24,
                      height: 24,
                      '&:hover': {
                        bgcolor: 'rgba(0,0,0,0.7)',
                      },
                    }}
                  >
                    <CloseIcon sx={{ fontSize: 14 }} />
                  </IconButton>
                </Box>
              ))}
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
            {/* Hidden file inputs */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".doc,.docx,.md,.markdown"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
            <input
              ref={imageInputRef}
              type="file"
              accept="image/*"
              style={{ display: 'none' }}
              onChange={handleQuestionImageChange}
            />
            <input
              ref={paperInputRef}
              type="file"
              accept=".pdf,application/pdf"
              style={{ display: 'none' }}
              onChange={handlePaperChange}
            />
            {/* + 号菜单按钮 */}
            <IconButton
              onClick={handleMenuClick}
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
              title="添加"
            >
              <AddIcon />
            </IconButton>
            <Menu
              anchorEl={menuAnchorEl}
              open={menuOpen}
              onClose={handleMenuClose}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'left',
              }}
              transformOrigin={{
                vertical: 'bottom',
                horizontal: 'left',
              }}
            >
              <MenuItem onClick={handleAddQuestionImage}>
                <ImageIcon sx={{ mr: 1, fontSize: 20 }} />
                添加题目图片
              </MenuItem>
              <MenuItem onClick={handleAddNotebook}>
                <AttachFileIcon sx={{ mr: 1, fontSize: 20 }} />
                上传笔记
              </MenuItem>
              <MenuItem onClick={handleAddPaper}>
                <FileIcon sx={{ mr: 1, fontSize: 20 }} />
                上传论文
              </MenuItem>
            </Menu>
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
              disabled={!inputMessage.trim() && !uploadedFile && uploadedImages.length === 0 && !sending}
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


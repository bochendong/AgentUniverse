/**
 * ChatPage Refactored Example
 * 
 * 这是一个重构示例，展示如何使用新提取的组件和hooks重构ChatPage
 * 这个文件仅供参考，实际使用时需要逐步迁移现有代码
 */

import React, { useState, useEffect, useRef } from 'react'
import { Box, Alert } from '@mui/material'
import { useTheme } from '../contexts/ThemeContext'
import { useSession } from '../hooks/useSession'
import { useImageUpload } from '../hooks/useImageUpload'
import SessionSidebar from '../components/chat/SessionSidebar'
import FileViewer from '../components/chat/FileViewer'
// import MessageList from '../components/chat/MessageList'
// import ChatInput from '../components/chat/ChatInput'
import { chatWithTopLevelAgent } from '../api/client'

/**
 * 重构后的ChatPage - 简化版示例
 * 
 * 主要变化：
 * 1. 使用useSession hook管理会话
 * 2. 使用useImageUpload hook管理图片上传
 * 3. 使用SessionSidebar组件替代侧边栏代码
 * 4. 使用FileViewer组件替代文件查看对话框
 * 5. 大幅简化代码，从2700+行减少到约200行
 */
function ChatPageRefactored() {
  const theme = useTheme()
  const isDark = theme.mode === 'dark'

  // 使用自定义hooks
  const {
    sessions,
    currentSessionId,
    setCurrentSessionId,
    loading: sessionsLoading,
    loadSessions,
    loadSessionConversations,
    createSession,
    removeSession,
  } = useSession()

  const {
    uploadedImages,
    handleImageChange,
    removeImage,
    clearImages,
    prepareImagesForAPI,
  } = useImageUpload()

  // 本地状态
  const [messages, setMessages] = useState([])
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [inputMessage, setInputMessage] = useState('')
  const [fileViewerOpen, setFileViewerOpen] = useState(false)
  const [fileViewerContent, setFileViewerContent] = useState(null)
  const [fileViewerLoading, setFileViewerLoading] = useState(false)

  // 处理新会话
  const handleNewChat = async () => {
    try {
      const newSession = await createSession()
      setMessages([])
    } catch (err) {
      setError('Failed to create new chat')
    }
  }

  // 处理选择会话
  const handleSelectSession = async (sessionId) => {
    setCurrentSessionId(sessionId)
    const conversations = await loadSessionConversations(sessionId)
    setMessages(conversations)
  }

  // 处理删除会话
  const handleDeleteSession = async (sessionId, e) => {
    e.stopPropagation()
    await removeSession(sessionId)
    if (currentSessionId === sessionId) {
      setMessages([])
    }
  }

  // 处理发送消息
  const handleSend = async () => {
    if ((!inputMessage.trim() && uploadedImages.length === 0) || sending) return
    
    let sessionId = currentSessionId
    if (!sessionId) {
      try {
        const newSession = await createSession()
        sessionId = newSession.id
      } catch (err) {
        setError('Failed to create session')
        return
      }
    }

    const images = prepareImagesForAPI()
    const userMessage = inputMessage.trim()

    setInputMessage('')
    clearImages()
    setSending(true)
    setError(null)

    // 添加用户消息
    setMessages(prev => [...prev, { 
      role: 'user', 
      content: userMessage || `已上传 ${uploadedImages.length} 张图片`,
      images: uploadedImages.map(img => img.preview),
    }])

    try {
      const response = await chatWithTopLevelAgent(
        userMessage,
        sessionId,
        images.length > 0 ? images : null
      )
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response,
        structured_data: response.data.structured_data,
      }])

      await loadSessions()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message')
    } finally {
      setSending(false)
    }
  }

  // 文件查看器相关
  const handleOpenFileViewer = async (filePath, fileName) => {
    setFileViewerOpen(true)
    setFileViewerLoading(true)
    // ... 加载文件内容
  }

  const handleCloseFileViewer = () => {
    setFileViewerOpen(false)
    setFileViewerContent(null)
  }

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
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          minHeight: 0,
          overflow: 'hidden',
        }}
      >
        {/* 使用SessionSidebar组件 */}
        <SessionSidebar
          open={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
          sessions={sessions}
          currentSessionId={currentSessionId}
          loading={sessionsLoading}
          onNewChat={handleNewChat}
          onSelectSession={handleSelectSession}
          onDeleteSession={handleDeleteSession}
        />

        {/* 主聊天区域 */}
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            minWidth: 0,
          }}
        >
          {error && (
            <Alert severity="error" sx={{ m: 2 }}>
              {error}
            </Alert>
          )}

          {/* TODO: 使用MessageList组件 */}
          <Box sx={{ flex: 1, overflowY: 'auto', p: 2 }}>
            {messages.map((message, index) => (
              <div key={index}>
                {/* 消息渲染 - 将被MessageItem组件替代 */}
                <div>{message.role}: {message.content}</div>
              </div>
            ))}
          </Box>

          {/* TODO: 使用ChatInput组件 */}
          <Box sx={{ p: 2 }}>
            {/* 输入框 - 将被ChatInput组件替代 */}
          </Box>
        </Box>
      </Box>

      {/* 使用FileViewer组件 */}
      <FileViewer
        open={fileViewerOpen}
        onClose={handleCloseFileViewer}
        fileName={fileViewerContent?.filename}
        content={fileViewerContent?.content}
        fileType={fileViewerContent?.file_type}
        loading={fileViewerLoading}
      />
    </Box>
  )
}

export default ChatPageRefactored


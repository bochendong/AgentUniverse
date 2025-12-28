import React, { useEffect, useRef } from 'react'
import { Box, Fade, Avatar, CircularProgress, Typography } from '@mui/material'
import { useTheme } from '../../contexts/ThemeContext'
import MessageItem from './MessageItem'

/**
 * MessageList - Container component for displaying chat messages
 * Handles scrolling and loading states
 */
export default function MessageList({
  messages = [],
  sending = false,
  currentActivity = null,
  onGetAnswer,
  onGetHint,
  onAddToNotebook,
  onOpenFileViewer,
  onOutlineConfirm,
  onOutlineViewDetails,
  isDark: isDarkProp,
}) {
  const theme = useTheme()
  const isDark = isDarkProp !== undefined ? isDarkProp : theme.mode === 'dark'
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, sending])

  return (
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
          {messages.map((message, index) => (
            <Fade in key={index} timeout={300}>
              <MessageItem
                message={message}
                index={index}
                totalMessages={messages.length}
                sending={sending}
                onGetAnswer={onGetAnswer}
                onGetHint={onGetHint}
                onAddToNotebook={onAddToNotebook}
                onOpenFileViewer={onOpenFileViewer}
                onOutlineConfirm={onOutlineConfirm}
                onOutlineViewDetails={onOutlineViewDetails}
                isDark={isDark}
              />
            </Fade>
          ))}

          {/* Loading indicator */}
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
  )
}


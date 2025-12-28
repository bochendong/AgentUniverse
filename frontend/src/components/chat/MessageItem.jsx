import React from 'react'
import {
  Box,
  Avatar,
  Typography,
  Button,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  Divider,
} from '@mui/material'
import {
  InsertDriveFile as FileIcon,
  Visibility as VisibilityIcon,
  MenuBook as MenuBookIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useTheme } from '../../contexts/ThemeContext'
import MarkdownRenderer from './MarkdownRenderer'
import AgentAvatar from '../AgentAvatar'

/**
 * MessageItem - Component for rendering individual chat messages
 * Supports user messages, assistant messages, structured data, files, and images
 */
export default function MessageItem({
  message,
  index,
  totalMessages,
  sending = false,
  onGetAnswer,
  onGetHint,
  onAddToNotebook,
  onOpenFileViewer,
  onOutlineConfirm,
  onOutlineViewDetails,
  isDark: isDarkProp,
}) {
  const navigate = useNavigate()
  const theme = useTheme()
  const isDark = isDarkProp !== undefined ? isDarkProp : theme.mode === 'dark'

  const isUser = message.role === 'user'
  const structuredData = message.structured_data

  return (
    <Box
      sx={{
        display: 'flex',
        gap: 2,
        py: 3,
        borderBottom: index < totalMessages - 1 
          ? (isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)')
          : 'none',
        bgcolor: isUser
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
          bgcolor: isUser
            ? (isDark ? '#19c37d' : '#007AFF')
            : (isDark ? '#ab68ff' : '#5856D6'),
          flexShrink: 0,
          color: 'white',
          fontWeight: 600,
        }}
      >
        {isUser ? 'U' : 'AI'}
      </Avatar>

      <Box sx={{ flex: 1, minWidth: 0 }}>
        {!isUser ? (
          // Assistant message
          <Box>
            <MarkdownRenderer content={message.content} isDark={isDark} />
            
            {/* Question action buttons */}
            {structuredData?.message_type === 'question' && onGetAnswer && (
              <Box sx={{ display: 'flex', gap: 1, mt: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  size="small"
                  onClick={() => onGetAnswer(message.content)}
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
                {onGetHint && (
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => onGetHint(message.content)}
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
                )}
              </Box>
            )}

            {/* Add to notebook button */}
            {structuredData?.message_type === 'add_to_notebook' && onAddToNotebook && (
              <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                <Button
                  variant="contained"
                  size="small"
                  onClick={() => onAddToNotebook(message.content)}
                  disabled={sending}
                  startIcon={<MenuBookIcon />}
                  sx={{
                    bgcolor: '#FF9500',
                    color: 'white',
                    '&:hover': {
                      bgcolor: '#E6850E',
                    },
                    '&:disabled': {
                      bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                      color: isDark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.5)',
                    },
                  }}
                >
                  添加到笔记
                </Button>
              </Box>
            )}

            {/* Outline card */}
            {structuredData?.message_type === 'outline' && (
              <OutlineCard
                outlineData={structuredData}
                outline={structuredData.outline}
                isDark={isDark}
                sending={sending}
                onConfirm={onOutlineConfirm}
                onViewDetails={onOutlineViewDetails}
              />
            )}

            {/* Notebook created card */}
            {structuredData?.message_type === 'notebook_created' && (
              <NotebookCreatedCard
                notebookId={structuredData.notebook_id}
                notebookTitle={structuredData.notebook_title}
                isDark={isDark}
                onNavigate={() => navigate(`/agents/${structuredData.notebook_id}`)}
              />
            )}
          </Box>
        ) : (
          // User message
          <Box>
            {/* File card */}
            {message.fileInfo && onOpenFileViewer && (
              <Card
                sx={{
                  mb: 1.5,
                  maxWidth: 400,
                  bgcolor: isDark ? '#40414f' : '#FFFFFF',
                  border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': {
                    bgcolor: isDark ? '#4a4b5a' : '#F5F5F7',
                    transform: 'translateY(-2px)',
                    boxShadow: isDark 
                      ? '0 4px 12px rgba(0,0,0,0.3)' 
                      : '0 4px 12px rgba(0,0,0,0.1)',
                  },
                }}
                onClick={() => onOpenFileViewer(message.fileInfo.path, message.fileInfo.name)}
              >
                <CardActionArea>
                  <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 1.5, p: 1.5 }}>
                    <FileIcon 
                      sx={{ 
                        fontSize: 24, 
                        color: isDark ? '#19c37d' : '#007AFF',
                        flexShrink: 0,
                      }} 
                    />
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: 600,
                          color: isDark ? '#ececf1' : '#1D1D1F',
                          mb: 0.25,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {message.fileInfo.name}
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{
                          color: isDark ? '#8e8ea0' : '#86868B',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5,
                          fontSize: '0.7rem',
                        }}
                      >
                        <VisibilityIcon sx={{ fontSize: 12 }} />
                        点击查看文件内容
                      </Typography>
                    </Box>
                  </CardContent>
                </CardActionArea>
              </Card>
            )}

            {/* Images */}
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

            {/* Text content */}
            {message.content && !message.fileInfo && (
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
      </Box>
    </Box>
  )
}

/**
 * OutlineCard - Card component for displaying outline information
 */
function OutlineCard({ outlineData, outline, isDark, sending, onConfirm, onViewDetails }) {
  const glowColor = '#007AFF' // 蓝色 - outline

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
            {onViewDetails && (
              <Button
                variant="outlined"
                size="small"
                onClick={() => onViewDetails(outline, outlineData)}
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
            )}
            {onConfirm && (
              <Button
                variant="contained"
                size="small"
                onClick={() => onConfirm(outline, outlineData)}
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
            )}
          </Box>
        </Box>
      </Box>
    </Box>
  )
}

/**
 * NotebookCreatedCard - Card component for displaying notebook creation success
 */
function NotebookCreatedCard({ notebookId, notebookTitle, isDark, onNavigate }) {
  const glowColor = '#34C759' // 绿色 - notebook agent

  if (!notebookId || !notebookTitle) return null

  return (
    <Box sx={{ mt: 2, maxWidth: 400 }}>
      <Box
        onClick={onNavigate}
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
          boxShadow: isDark ? '0 4px 16px rgba(0,0,0,0.3)' : '0 4px 16px rgba(0,0,0,0.08)',
        }}
      >
        {/* Glow effects */}
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
              seed={notebookId} 
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
                {notebookTitle}
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
                {notebookId}
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


import React, { useState } from 'react'
import { 
  Box, 
  Typography, 
  Chip, 
  IconButton, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogContentText, 
  DialogActions, 
  Button,
  CircularProgress,
  Divider,
} from '@mui/material'
import {
  Delete as DeleteIcon,
} from '@mui/icons-material'
import AgentAvatar from './AgentAvatar'
import { deleteNotebook, deleteAgent, getAgent } from '../api/client'

/**
 * Agent Card - Neon Edge Card with Apple Style
 * 重新设计的布局：更清晰的信息层次
 */
function AgentCard({ agent, onClick, onDelete }) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [deleting, setDeleting] = useState(false)
  // 判断agent类型
  const isMasterAgent = agent.metadata?.is_master_agent || false
  const isTopLevelAgent = agent.agent_type === 'top_level_agent'
  
  // 根据类型选择颜色
  const getGlowColor = () => {
    if (isTopLevelAgent) return '#FF6B6B' // 红色
    if (isMasterAgent) return '#007AFF' // 蓝色
    return '#34C759' // 绿色 - notebook agent
  }

  const glowColor = getGlowColor()

  const handleDeleteClick = (e) => {
    e.stopPropagation() // 阻止事件冒泡，避免触发onClick
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    try {
      setDeleting(true)
      
      // 获取agent信息以找到父agent
      let parentAgentId = null
      try {
        const agentInfo = await getAgent(agent.notebook_id)
        if (agentInfo.data?.id) {
          // 这里我们需要获取父agent，但API可能没有直接提供
          // 先删除，后端应该会处理通知
          // 如果需要前端通知，可以调用通知API
        }
      } catch (err) {
        console.warn('Failed to get agent info before delete:', err)
      }
      
      // Use generic deleteAgent API for MasterAgent, deleteNotebook for NoteBookAgent
      // Both APIs handle removing from parent's sub_agent_ids correctly
      if (isMasterAgent) {
        await deleteAgent(agent.notebook_id)
      } else {
        await deleteNotebook(agent.notebook_id)
      }
      setDeleteDialogOpen(false)
      if (onDelete) {
        onDelete(agent.notebook_id)
      }
    } catch (error) {
      console.error('Failed to delete agent:', error)
      alert(error.response?.data?.detail || 'Failed to delete agent')
    } finally {
      setDeleting(false)
    }
  }

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false)
  }

  return (
    <>
    <Box
      onClick={onClick}
      sx={{
        position: 'relative',
        borderRadius: 4,
        p: 3,
        bgcolor: 'white',
        cursor: 'pointer',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        overflow: 'hidden',
        border: '1px solid rgba(0,0,0,0.06)',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        '&:hover': {
          transform: 'translateY(-8px)',
          boxShadow: `0 20px 40px ${glowColor}40, 0 0 0 1px ${glowColor}30`,
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
        boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
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

      {/* Delete Button */}
      <IconButton
        onClick={handleDeleteClick}
        sx={{
          position: 'absolute',
          top: 12,
          right: 12,
          zIndex: 2,
          bgcolor: 'rgba(255, 255, 255, 0.9)',
          color: '#FF3B30',
          width: 32,
          height: 32,
          '&:hover': {
            bgcolor: '#FF3B30',
            color: 'white',
          },
          transition: 'all 0.2s',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}
        size="small"
      >
        <DeleteIcon sx={{ fontSize: 18 }} />
      </IconButton>

      {/* Content - 重新设计的布局 */}
      <Box sx={{ position: 'relative', zIndex: 1, flex: 1, display: 'flex', flexDirection: 'column' }}>
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
            seed={agent.avatar_seed} 
            size={56}
            sx={{
              border: `2px solid ${glowColor}30`,
              boxShadow: `0 2px 8px ${glowColor}20`,
              flexShrink: 0,
            }}
          />
          
          {/* Agent Name - 占据剩余空间 */}
          <Box sx={{ flex: 1, minWidth: 0, pt: 0.5 }}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 600,
                color: '#1D1D1F',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                lineHeight: 1.3,
                mb: 0.5,
              }}
            >
              {agent.agent_name || 'Unnamed Agent'}
            </Typography>
            
            {/* Notebook Title */}
            <Typography
              variant="body2"
              sx={{
                color: '#86868B',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {agent.notebook_title || 'No notebook'}
            </Typography>
          </Box>
        </Box>

        {/* Divider */}
        <Divider sx={{ my: 1.5, borderColor: 'rgba(0,0,0,0.06)' }} />

        {/* Tags Section */}
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1.5 }}>
          {isTopLevelAgent && (
            <Chip
              label="Top Level"
              size="small"
              sx={{
                bgcolor: `${glowColor}15`,
                color: glowColor,
                fontWeight: 500,
                fontSize: '0.7rem',
                height: 24,
              }}
            />
          )}
          {isMasterAgent && (
            <Chip
              label="Master"
              size="small"
              sx={{
                bgcolor: `${glowColor}15`,
                color: glowColor,
                fontWeight: 500,
                fontSize: '0.7rem',
                height: 24,
              }}
            />
          )}
          {!isTopLevelAgent && !isMasterAgent && (
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
          )}
        </Box>

        {/* Description Section - 占据剩余空间 */}
        {isMasterAgent && agent.agent_card?.description ? (
          <Box sx={{ flex: 1, mt: 'auto' }}>
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
                    variant="caption"
                    sx={{
                      color: '#86868B',
                      fontSize: '0.8rem',
                      fontStyle: 'italic',
                    }}
                  >
                    暂无下辖笔记本
                  </Typography>
                )
              }
              
              return (
                <>
                  <Typography
                    variant="caption"
                    sx={{
                      color: '#86868B',
                      fontSize: '0.75rem',
                      fontWeight: 500,
                      mb: 0.5,
                    }}
                  >
                    下辖笔记本：
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                    {notebookNames.map((name, index) => (
                      <Typography
                        key={index}
                        variant="caption"
                        sx={{
                          color: '#1D1D1F',
                          fontSize: '0.8rem',
                          lineHeight: 1.4,
                          pl: 1,
                        }}
                      >
                        • {name}
                      </Typography>
                    ))}
                  </Box>
                </>
              )
            })()}
          </Box>
        ) : agent.description && !isMasterAgent ? (
          <Box sx={{ flex: 1, mt: 'auto' }}>
            <Typography
              variant="caption"
              sx={{
                color: '#86868B',
                display: '-webkit-box',
                WebkitLineClamp: 3,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
                lineHeight: 1.5,
              }}
            >
              {agent.description}
            </Typography>
          </Box>
        ) : null}
      </Box>
    </Box>

    {/* Delete Confirmation Dialog */}
    <Dialog
      open={deleteDialogOpen}
      onClose={handleDeleteCancel}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle sx={{ fontWeight: 600, color: '#1D1D1F' }}>
        Delete Agent
      </DialogTitle>
      <DialogContent>
        <DialogContentText sx={{ color: '#86868B', mb: 1 }}>
          Are you sure you want to delete <strong>{agent.agent_name || 'this agent'}</strong>?
        </DialogContentText>
        {isMasterAgent && (
          <DialogContentText sx={{ color: '#FF3B30', fontSize: '0.875rem', mt: 2 }}>
            ⚠️ This is a Master Agent. All child agents and their notebooks will be deleted recursively.
          </DialogContentText>
        )}
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button 
          onClick={handleDeleteCancel} 
          disabled={deleting}
          sx={{ color: '#86868B' }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleDeleteConfirm}
          disabled={deleting}
          variant="contained"
          sx={{
            bgcolor: '#FF3B30',
            '&:hover': {
              bgcolor: '#D32F2F',
            },
          }}
        >
          {deleting ? (
            <>
              <CircularProgress size={16} sx={{ mr: 1, color: 'white' }} />
              Deleting...
            </>
          ) : (
            'Delete'
          )}
        </Button>
      </DialogActions>
    </Dialog>
    </>
  )
}

export default AgentCard

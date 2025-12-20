import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Divider,
  CircularProgress,
  TextField,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Edit as EditIcon,
  Send as SendIcon,
} from '@mui/icons-material'
import { useTheme } from '../contexts/ThemeContext'

/**
 * OutlineConfirmation Component
 * Displays outline for user confirmation before creating notebook
 * Supports user feedback and revision
 */
function OutlineConfirmation({ 
  outline, 
  onConfirm, 
  onCancel, 
  onRevise,
  isCreating = false,
  isRevising = false 
}) {
  const theme = useTheme()
  const isDark = theme.mode === 'dark'
  const [feedback, setFeedback] = useState('')
  const [showFeedbackInput, setShowFeedbackInput] = useState(false)

  const handleConfirm = () => {
    if (onConfirm) {
      onConfirm(outline)
    }
  }

  const handleCancel = () => {
    if (onCancel) {
      onCancel()
    }
  }

  const handleRevise = () => {
    if (feedback.trim()) {
      if (onRevise) {
        onRevise(feedback.trim())
      }
      setFeedback('')
      setShowFeedbackInput(false)
    }
  }

  return (
    <Paper
      sx={{
        p: 3,
        mb: 2,
        bgcolor: isDark ? '#40414f' : '#FFFFFF',
        border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
        borderRadius: '12px',
      }}
    >
      <Typography
        variant="h6"
        sx={{
          mb: 2,
          fontWeight: 600,
          color: isDark ? '#ececf1' : '#1D1D1F',
        }}
      >
        📋 大纲已生成，请确认
      </Typography>

      <Divider sx={{ mb: 2, borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' }} />

      {/* Notebook Title */}
      <Box sx={{ mb: 2 }}>
        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 600,
            color: isDark ? '#19c37d' : '#007AFF',
            mb: 0.5,
          }}
        >
          标题
        </Typography>
        <Typography
          variant="body1"
          sx={{
            color: isDark ? '#ececf1' : '#1D1D1F',
          }}
        >
          {outline.notebook_title}
        </Typography>
      </Box>

      {/* Notebook Description */}
      {outline.notebook_description && (
        <Box sx={{ mb: 2 }}>
          <Typography
            variant="subtitle1"
            sx={{
              fontWeight: 600,
              color: isDark ? '#19c37d' : '#007AFF',
              mb: 0.5,
            }}
          >
            描述
          </Typography>
          <Typography
            variant="body2"
            sx={{
              color: isDark ? '#8e8ea0' : '#86868B',
              whiteSpace: 'pre-wrap',
              lineHeight: 1.6,
            }}
          >
            {outline.notebook_description}
          </Typography>
        </Box>
      )}

      {/* Sections */}
      <Box sx={{ mb: 3 }}>
        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 600,
            color: isDark ? '#19c37d' : '#007AFF',
            mb: 1,
          }}
        >
          章节 ({Object.keys(outline.outlines || {}).length})
        </Typography>
        
        {Object.entries(outline.outlines || {}).map(([title, description], index) => (
          <Accordion
            key={index}
            sx={{
              mb: 1,
              bgcolor: isDark ? '#343541' : '#F5F5F7',
              '&:before': { display: 'none' },
              boxShadow: 'none',
              border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)',
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon sx={{ color: isDark ? '#ececf1' : '#1D1D1F' }} />}
              sx={{
                '& .MuiAccordionSummary-content': {
                  my: 1.5,
                },
              }}
            >
              <Typography
                sx={{
                  fontWeight: 600,
                  color: isDark ? '#ececf1' : '#1D1D1F',
                }}
              >
                {index + 1}. {title}
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography
                sx={{
                  color: isDark ? '#8e8ea0' : '#86868B',
                  whiteSpace: 'pre-wrap',
                  lineHeight: 1.6,
                }}
              >
                {description}
              </Typography>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>

      {/* Feedback Input */}
      {showFeedbackInput && (
        <Box sx={{ mb: 2 }}>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="请告诉我需要修改的地方，例如：第2章太简单了，需要更详细；需要添加XXX章节；删除第3章等..."
            disabled={isRevising}
            variant="outlined"
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: isDark ? '#343541' : '#FFFFFF',
                color: isDark ? '#ececf1' : '#1D1D1F',
                '& fieldset': {
                  borderColor: isDark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)',
                },
                '&:hover fieldset': {
                  borderColor: isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: isDark ? '#19c37d' : '#007AFF',
                },
              },
            }}
          />
        </Box>
      )}

      {/* Actions */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', flexWrap: 'wrap' }}>
        <Button
          variant="outlined"
          onClick={handleCancel}
          disabled={isCreating || isRevising}
          startIcon={<CancelIcon />}
          sx={{
            borderColor: isDark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)',
            color: isDark ? '#ececf1' : '#1D1D1F',
            '&:hover': {
              borderColor: isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)',
              bgcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
            },
          }}
        >
          取消
        </Button>
        {!showFeedbackInput ? (
          <Button
            variant="outlined"
            onClick={() => setShowFeedbackInput(true)}
            disabled={isCreating || isRevising}
            startIcon={<EditIcon />}
            sx={{
              borderColor: isDark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)',
              color: isDark ? '#ececf1' : '#1D1D1F',
              '&:hover': {
                borderColor: isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)',
                bgcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
              },
            }}
          >
            需要修改
          </Button>
        ) : (
          <Button
            variant="outlined"
            onClick={handleRevise}
            disabled={isCreating || isRevising || !feedback.trim()}
            startIcon={isRevising ? <CircularProgress size={16} /> : <SendIcon />}
            sx={{
              borderColor: isDark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)',
              color: isDark ? '#ececf1' : '#1D1D1F',
              '&:hover': {
                borderColor: isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)',
                bgcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
              },
            }}
          >
            {isRevising ? '修改中...' : '提交修改意见'}
          </Button>
        )}
        <Button
          variant="contained"
          onClick={handleConfirm}
          disabled={isCreating || isRevising || showFeedbackInput}
          startIcon={isCreating ? <CircularProgress size={16} /> : <CheckCircleIcon />}
          sx={{
            bgcolor: isDark ? '#19c37d' : '#007AFF',
            color: 'white',
            '&:hover': {
              bgcolor: isDark ? '#16a269' : '#0051D5',
            },
            '&:disabled': {
              bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
              color: isDark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.5)',
            },
          }}
        >
          {isCreating ? '创建中...' : '确认并创建笔记本'}
        </Button>
      </Box>
    </Paper>
  )
}

export default OutlineConfirmation

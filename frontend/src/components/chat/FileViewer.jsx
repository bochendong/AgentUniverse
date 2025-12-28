import React from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  IconButton,
  Box,
  Typography,
  CircularProgress,
} from '@mui/material'
import {
  InsertDriveFile as FileIcon,
  Close as CloseIcon,
} from '@mui/icons-material'
import { useTheme } from '../../contexts/ThemeContext'

/**
 * FileViewer - Dialog component for viewing file contents
 */
export default function FileViewer({
  open,
  onClose,
  fileName,
  content,
  fileType,
  loading,
}) {
  const theme = useTheme()
  const isDark = theme.mode === 'dark'

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          bgcolor: isDark ? '#343541' : '#FFFFFF',
          color: isDark ? '#ececf1' : '#1D1D1F',
          maxHeight: '80vh',
        },
      }}
    >
      <DialogTitle
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          borderBottom: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
          pb: 2,
        }}
      >
        <FileIcon sx={{ color: isDark ? '#19c37d' : '#007AFF' }} />
        <Typography variant="h6" sx={{ flex: 1 }}>
          {fileName || '文件内容'}
        </Typography>
        <IconButton
          onClick={onClose}
          size="small"
          sx={{
            color: isDark ? '#8e8ea0' : '#86868B',
            '&:hover': {
              bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
            },
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent
        sx={{
          p: 3,
          overflow: 'auto',
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
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
            <CircularProgress size={40} />
          </Box>
        ) : content ? (
          <Box>
            {fileType === 'pdf' ? (
              <Typography
                sx={{
                  color: isDark ? '#8e8ea0' : '#86868B',
                  fontStyle: 'italic',
                }}
              >
                {content}
              </Typography>
            ) : fileType === 'error' ? (
              <Typography
                sx={{
                  color: '#ef4444',
                }}
              >
                {content}
              </Typography>
            ) : (
              <Box
                component="pre"
                sx={{
                  bgcolor: isDark ? '#1e1e1e' : '#F5F5F7',
                  borderRadius: '8px',
                  padding: '16px',
                  overflow: 'auto',
                  border: isDark ? 'none' : '1px solid rgba(0,0,0,0.1)',
                  color: isDark ? '#ececf1' : '#1D1D1F',
                  fontFamily: 'Consolas, Monaco, "Courier New", monospace',
                  fontSize: '0.875rem',
                  lineHeight: 1.6,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  maxHeight: '60vh',
                  m: 0,
                }}
              >
                {content}
              </Box>
            )}
          </Box>
        ) : null}
      </DialogContent>
      <DialogActions
        sx={{
          borderTop: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
          p: 2,
        }}
      >
        <Button
          onClick={onClose}
          sx={{
            color: isDark ? '#ececf1' : '#1D1D1F',
            '&:hover': {
              bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
            },
          }}
        >
          关闭
        </Button>
      </DialogActions>
    </Dialog>
  )
}


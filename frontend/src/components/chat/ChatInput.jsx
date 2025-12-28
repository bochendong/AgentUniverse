import React, { useRef, useState } from 'react'
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Menu,
  MenuItem,
  Typography,
} from '@mui/material'
import {
  Add as AddIcon,
  Send as SendIcon,
  Stop as StopIcon,
  AttachFile as AttachFileIcon,
  InsertDriveFile as FileIcon,
  Image as ImageIcon,
  Close as CloseIcon,
} from '@mui/icons-material'
import { useTheme } from '../../contexts/ThemeContext'

/**
 * ChatInput - Input component for chat messages
 * Supports text input, file upload, image upload, and sending messages
 */
export default function ChatInput({
  value,
  onChange,
  onSend,
  onStop,
  sending = false,
  disabled = false,
  placeholder = "Message...",
  // File upload props
  uploadedFile = null,
  onFileRemove,
  // Image upload props
  uploadedImages = [],
  onImageRemove,
  // File input refs and handlers
  fileInputRef,
  imageInputRef,
  paperInputRef,
  onFileChange,
  onImageChange,
  onPaperChange,
  // Menu handlers
  onAddQuestionImage,
  onAddNotebook,
  onAddPaper,
  isDark: isDarkProp,
}) {
  const theme = useTheme()
  const isDark = isDarkProp !== undefined ? isDarkProp : theme.mode === 'dark'
  const [menuAnchorEl, setMenuAnchorEl] = useState(null)
  const menuOpen = Boolean(menuAnchorEl)

  const handleMenuClick = (event) => {
    setMenuAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setMenuAnchorEl(null)
  }

  const handleAddQuestionImage = () => {
    if (onAddQuestionImage) {
      onAddQuestionImage()
    }
    handleMenuClose()
  }

  const handleAddNotebook = () => {
    if (onAddNotebook) {
      onAddNotebook()
    }
    handleMenuClose()
  }

  const handleAddPaper = () => {
    if (onAddPaper) {
      onAddPaper()
    }
    handleMenuClose()
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (onSend && !disabled && (value.trim() || uploadedImages.length > 0)) {
        onSend()
      }
    }
  }

  const canSend = value.trim() || uploadedFile || uploadedImages.length > 0

  return (
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
          {onFileRemove && (
            <IconButton
              size="small"
              onClick={onFileRemove}
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
          )}
        </Box>
      )}

      {/* Uploaded images preview */}
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
                src={img.preview || img}
                alt={`Upload ${index + 1}`}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                }}
              />
              {onImageRemove && (
                <IconButton
                  size="small"
                  onClick={() => onImageRemove(index)}
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
              )}
            </Box>
          ))}
        </Box>
      )}

      {/* Input container */}
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
        {fileInputRef && (
          <input
            ref={fileInputRef}
            type="file"
            accept=".doc,.docx,.md,.markdown"
            style={{ display: 'none' }}
            onChange={onFileChange}
          />
        )}
        {imageInputRef && (
          <input
            ref={imageInputRef}
            type="file"
            accept="image/*"
            style={{ display: 'none' }}
            onChange={onImageChange}
            multiple
          />
        )}
        {paperInputRef && (
          <input
            ref={paperInputRef}
            type="file"
            accept=".pdf,application/pdf"
            style={{ display: 'none' }}
            onChange={onPaperChange}
          />
        )}

        {/* Add menu button */}
        <IconButton
          onClick={handleMenuClick}
          disabled={sending || disabled}
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

        {/* Menu */}
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
          {onAddQuestionImage && (
            <MenuItem onClick={handleAddQuestionImage}>
              <ImageIcon sx={{ mr: 1, fontSize: 20 }} />
              添加题目图片
            </MenuItem>
          )}
          {onAddNotebook && (
            <MenuItem onClick={handleAddNotebook}>
              <AttachFileIcon sx={{ mr: 1, fontSize: 20 }} />
              上传笔记
            </MenuItem>
          )}
          {onAddPaper && (
            <MenuItem onClick={handleAddPaper}>
              <FileIcon sx={{ mr: 1, fontSize: 20 }} />
              上传论文
            </MenuItem>
          )}
        </Menu>

        {/* Text input */}
        <TextField
          fullWidth
          multiline
          maxRows={6}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={sending || disabled}
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

        {/* Send/Stop button */}
        <IconButton
          onClick={sending && onStop ? onStop : onSend}
          disabled={(!canSend && !sending) || disabled}
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
  )
}


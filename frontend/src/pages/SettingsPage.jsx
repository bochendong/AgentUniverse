import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Paper,
  Switch,
  FormControlLabel,
  Divider,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  ArrowBack as BackIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
  Restore as RestoreIcon,
  Warning as WarningIcon,
} from '@mui/icons-material'
import { useTheme } from '../contexts/ThemeContext'
import { resetDatabase } from '../api/client'

/**
 * Settings Page - 设置页面
 * 包含主题切换等功能
 */
function SettingsPage() {
  const navigate = useNavigate()
  const { mode, toggleTheme } = useTheme()
  const isDark = mode === 'dark'
  const [resetDialogOpen, setResetDialogOpen] = useState(false)
  const [resetting, setResetting] = useState(false)
  const [resetError, setResetError] = useState(null)
  const [resetSuccess, setResetSuccess] = useState(false)

  const handleResetClick = () => {
    setResetDialogOpen(true)
    setResetError(null)
    setResetSuccess(false)
  }

  const handleResetConfirm = async () => {
    try {
      setResetting(true)
      setResetError(null)
      setResetSuccess(false)
      
      const response = await resetDatabase()
      console.log('Database reset successful:', response.data)
      setResetSuccess(true)
      setResetDialogOpen(false)
      
      // Refresh the page after 2 seconds to reload the application state
      setTimeout(() => {
        window.location.reload()
      }, 2000)
    } catch (error) {
      console.error('Failed to reset database:', error)
      setResetError(error.response?.data?.detail || 'Failed to reset database')
    } finally {
      setResetting(false)
    }
  }

  const handleResetCancel = () => {
    setResetDialogOpen(false)
    setResetError(null)
    setResetSuccess(false)
  }

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        bgcolor: 'background.default',
        overflowY: 'auto',
        overflowX: 'hidden',
      }}
    >
      {/* Main Content */}
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Paper
          sx={{
            p: 3,
            bgcolor: 'background.paper',
            borderRadius: 3,
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
          }}
        >
          <Typography
            variant="h6"
            sx={{
              fontWeight: 600,
              color: isDark ? '#ececf1' : '#1D1D1F',
              mb: 3,
            }}
          >
            Settings
          </Typography>

          {/* Theme Toggle Section */}
          <Box sx={{ mb: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              {isDark ? (
                <DarkModeIcon sx={{ mr: 2, color: isDark ? '#ececf1' : '#1D1D1F' }} />
              ) : (
                <LightModeIcon sx={{ mr: 2, color: isDark ? '#ececf1' : '#1D1D1F' }} />
              )}
              <Typography
                variant="subtitle1"
                sx={{
                  fontWeight: 500,
                  color: isDark ? '#ececf1' : '#1D1D1F',
                }}
              >
                Theme
              </Typography>
            </Box>
            <FormControlLabel
              control={
                <Switch
                  checked={isDark}
                  onChange={toggleTheme}
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: '#007AFF',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: '#007AFF',
                    },
                  }}
                />
              }
              label={isDark ? 'Dark Mode' : 'Light Mode'}
              sx={{
                color: isDark ? '#ececf1' : '#1D1D1F',
              }}
            />
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Database Reset Section */}
          <Box sx={{ mb: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <RestoreIcon sx={{ mr: 2, color: '#FF3B30' }} />
              <Typography
                variant="subtitle1"
                sx={{
                  fontWeight: 500,
                  color: isDark ? '#ececf1' : '#1D1D1F',
                }}
              >
                Database Management
              </Typography>
            </Box>
            <Typography
              variant="body2"
              sx={{
                color: isDark ? '#86868B' : '#86868B',
                mb: 2,
              }}
            >
              Reset the database to its initial state. This will:
              <ul style={{ marginTop: 8, marginBottom: 8, paddingLeft: 20 }}>
                <li>Delete all agents (except tools)</li>
                <li>Delete all sessions</li>
                <li>Create TopLevelAgent and MasterAgent with default tools</li>
                <li>Preserve all existing tools</li>
              </ul>
              <strong style={{ color: '#FF3B30' }}>Warning: This action cannot be undone!</strong>
            </Typography>
            <Button
              variant="outlined"
              color="error"
              startIcon={<RestoreIcon />}
              onClick={handleResetClick}
              sx={{
                textTransform: 'none',
                fontWeight: 500,
              }}
            >
              Reset Database
            </Button>
          </Box>
        </Paper>
      </Container>

      {/* Reset Confirmation Dialog */}
      <Dialog
        open={resetDialogOpen}
        onClose={handleResetCancel}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            bgcolor: isDark ? '#202123' : '#FFFFFF',
            color: isDark ? '#ececf1' : '#1D1D1F',
          },
        }}
      >
        <DialogTitle sx={{ fontWeight: 600 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <WarningIcon sx={{ color: '#FF3B30' }} />
            Confirm Database Reset
          </Box>
        </DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ color: isDark ? '#ececf1' : '#1D1D1F', mb: 2 }}>
            Are you sure you want to reset the database? This will:
          </DialogContentText>
          <Box component="ul" sx={{ pl: 3, mb: 2, color: isDark ? '#ececf1' : '#1D1D1F' }}>
            <li>Delete all agents (NoteBookAgents, MasterAgents)</li>
            <li>Delete all sessions and conversations</li>
            <li>Create TopLevelAgent and MasterAgent with default tools</li>
            <li>Preserve all existing tools</li>
          </Box>
          <Alert severity="error" sx={{ mt: 2 }}>
            <strong>This action cannot be undone!</strong> All your agents and sessions will be permanently deleted.
          </Alert>
          {resetError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {resetError}
            </Alert>
          )}
          {resetSuccess && (
            <Alert severity="success" sx={{ mt: 2 }}>
              Database reset successful! The page will refresh shortly.
            </Alert>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button
            onClick={handleResetCancel}
            disabled={resetting}
            sx={{
              color: isDark ? '#86868B' : '#86868B',
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleResetConfirm}
            disabled={resetting || resetSuccess}
            variant="contained"
            color="error"
            startIcon={resetting ? <CircularProgress size={16} color="inherit" /> : <RestoreIcon />}
            sx={{
              bgcolor: '#FF3B30',
              '&:hover': {
                bgcolor: '#D32F2F',
              },
            }}
          >
            {resetting ? 'Resetting...' : resetSuccess ? 'Success!' : 'Reset Database'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default SettingsPage
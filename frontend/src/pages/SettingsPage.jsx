import React from 'react'
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
} from '@mui/material'
import {
  ArrowBack as BackIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
} from '@mui/icons-material'
import { useTheme } from '../contexts/ThemeContext'

/**
 * Settings Page - 设置页面
 * 包含主题切换等功能
 */
function SettingsPage() {
  const navigate = useNavigate()
  const { mode, toggleTheme } = useTheme()

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
              color: 'text.primary',
              mb: 3,
            }}
          >
            Appearance
          </Typography>

          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              p: 2,
              borderRadius: 2,
              bgcolor: 'background.default',
              border: '1px solid rgba(0,0,0,0.06)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              {mode === 'light' ? (
                <LightModeIcon sx={{ color: 'primary.main', fontSize: 28 }} />
              ) : (
                <DarkModeIcon sx={{ color: 'primary.main', fontSize: 28 }} />
              )}
              <Box>
                <Typography
                  variant="subtitle1"
                  sx={{
                    fontWeight: 600,
                    color: 'text.primary',
                    mb: 0.5,
                  }}
                >
                  Theme
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: 'text.secondary',
                    fontSize: '0.875rem',
                  }}
                >
                  {mode === 'light' ? 'Light mode' : 'Dark mode'}
                </Typography>
              </Box>
            </Box>
            <FormControlLabel
              control={
                <Switch
                  checked={mode === 'dark'}
                  onChange={toggleTheme}
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: 'primary.main',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: 'primary.main',
                    },
                  }}
                />
              }
              label=""
            />
          </Box>
        </Paper>
      </Container>
    </Box>
  )
}

export default SettingsPage


import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTheme } from '../contexts/ThemeContext'
import {
  Box,
  AppBar,
  Toolbar,
  Button,
  Avatar,
  Menu,
  MenuItem,
  Typography,
  IconButton,
} from '@mui/material'
import {
  SmartToy as AgentsIcon,
  Info as InfoIcon,
  Login as LoginIcon,
  AccountCircle as AccountIcon,
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
} from '@mui/icons-material'
import AgentAvatar from './AgentAvatar'

/**
 * Chat Header Component
 * 包含导航按钮、登录按钮和用户头像
 */
function ChatHeader({ sidebarOpen, onToggleSidebar }) {
  const navigate = useNavigate()
  const theme = useTheme()
  const isDark = theme.mode === 'dark'
  const [userMenuAnchor, setUserMenuAnchor] = useState(null)
  const [isLoggedIn, setIsLoggedIn] = useState(false) // TODO: 从 auth context 获取
  const [userName, setUserName] = useState('User') // TODO: 从 auth context 获取

  const handleUserMenuOpen = (event) => {
    setUserMenuAnchor(event.currentTarget)
  }

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null)
  }

  const handleLogin = () => {
    // TODO: 实现登录逻辑
    console.log('Login clicked')
    setIsLoggedIn(true)
    setUserName('User')
  }

  const handleLogout = () => {
    // TODO: 实现登出逻辑
    console.log('Logout clicked')
    setIsLoggedIn(false)
    setUserName('User')
    handleUserMenuClose()
  }

  return (
    <AppBar
      position="relative"
      sx={{
        bgcolor: isDark ? '#202123' : '#FFFFFF',
        borderBottom: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)',
        boxShadow: 'none',
        zIndex: (theme) => theme.zIndex.drawer + 1,
      }}
    >
      <Toolbar
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          px: 3,
          minHeight: '64px !important',
        }}
      >
        {/* Left side - Sidebar toggle and Navigation buttons */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton
            onClick={onToggleSidebar}
            sx={{
              color: isDark ? '#ececf1' : '#1D1D1F',
              '&:hover': {
                bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
              },
            }}
          >
            {sidebarOpen ? <ChevronLeftIcon /> : <MenuIcon />}
          </IconButton>
          <Button
            startIcon={<AgentsIcon />}
            onClick={() => navigate('/agents')}
            sx={{
              color: isDark ? '#ececf1' : '#1D1D1F',
              textTransform: 'none',
              fontWeight: 500,
              '&:hover': {
                bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
              },
            }}
          >
            View Agents
          </Button>
          <Button
            startIcon={<InfoIcon />}
            onClick={() => navigate('/top-level-agent')}
            sx={{
              color: isDark ? '#ececf1' : '#1D1D1F',
              textTransform: 'none',
              fontWeight: 500,
              '&:hover': {
                bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
              },
            }}
          >
            TopLevelAgent Info
          </Button>
        </Box>

        {/* Right side - Login/User Avatar */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {isLoggedIn ? (
            <>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  cursor: 'pointer',
                  px: 1.5,
                  py: 0.5,
                  borderRadius: '8px',
                  '&:hover': {
                    bgcolor: 'rgba(255,255,255,0.1)',
                  },
                }}
                onClick={handleUserMenuOpen}
              >
                <AgentAvatar seed={userName} size={32} />
                <Typography
                  variant="body2"
                  sx={{
                    color: '#ececf1',
                    fontWeight: 500,
                  }}
                >
                  {userName}
                </Typography>
              </Box>
              <Menu
                anchorEl={userMenuAnchor}
                open={Boolean(userMenuAnchor)}
                onClose={handleUserMenuClose}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                PaperProps={{
                  sx: {
                    bgcolor: '#202123',
                    border: '1px solid rgba(255,255,255,0.1)',
                    mt: 1,
                    minWidth: 180,
                  },
                }}
              >
                <MenuItem
                  onClick={handleUserMenuClose}
                  sx={{
                    color: '#ececf1',
                    '&:hover': {
                      bgcolor: 'rgba(255,255,255,0.1)',
                    },
                  }}
                >
                  Profile
                </MenuItem>
                <MenuItem
                  onClick={handleUserMenuClose}
                  sx={{
                    color: '#ececf1',
                    '&:hover': {
                      bgcolor: 'rgba(255,255,255,0.1)',
                    },
                  }}
                >
                  Settings
                </MenuItem>
                <MenuItem
                  onClick={handleLogout}
                  sx={{
                    color: '#ececf1',
                    '&:hover': {
                      bgcolor: 'rgba(255,255,255,0.1)',
                    },
                  }}
                >
                  Logout
                </MenuItem>
              </Menu>
            </>
          ) : (
            <Button
              startIcon={<LoginIcon />}
              onClick={handleLogin}
              variant="outlined"
              sx={{
                color: isDark ? '#ececf1' : '#007AFF',
                borderColor: isDark ? 'rgba(255,255,255,0.2)' : '#007AFF',
                textTransform: 'none',
                fontWeight: 500,
                '&:hover': {
                  borderColor: isDark ? 'rgba(255,255,255,0.3)' : '#0051D5',
                  bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,122,255,0.1)',
                },
              }}
            >
              Login
            </Button>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default ChatHeader


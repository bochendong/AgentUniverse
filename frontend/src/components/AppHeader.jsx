import React, { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
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
  Chat as ChatIcon,
  Info as InfoIcon,
  Settings as SettingsIcon,
  AccountCircle as AccountIcon,
  Login as LoginIcon,
  Build as ToolsIcon,
} from '@mui/icons-material'
import AgentAvatar from './AgentAvatar'

/**
 * App Header Component - 统一的网站头部
 * 在所有页面上显示，包含导航和用户菜单
 */
function AppHeader() {
  const navigate = useNavigate()
  const location = useLocation()
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

  const handleNavigate = (path) => {
    navigate(path)
    handleUserMenuClose()
  }

  const isActive = (path) => location.pathname === path

  return (
    <AppBar
      position="fixed"
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
        {/* Left side - Logo and Navigation buttons */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              color: isDark ? '#ececf1' : '#1D1D1F',
              mr: 2,
              cursor: 'pointer',
            }}
            onClick={() => navigate('/')}
          >
            AgentUniverse
          </Typography>
          
          <Button
            startIcon={<ChatIcon />}
            onClick={() => navigate('/')}
            sx={{
              color: isDark ? '#ececf1' : '#1D1D1F',
              textTransform: 'none',
              fontWeight: 500,
              bgcolor: isActive('/') ? (isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)') : 'transparent',
              '&:hover': {
                bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
              },
            }}
          >
            Chat
          </Button>
          
          <Button
            startIcon={<AgentsIcon />}
            onClick={() => navigate('/agents')}
            sx={{
              color: isDark ? '#ececf1' : '#1D1D1F',
              textTransform: 'none',
              fontWeight: 500,
              bgcolor: isActive('/agents') || location.pathname.startsWith('/agents/') 
                ? (isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)') 
                : 'transparent',
              '&:hover': {
                bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
              },
            }}
          >
            Agents
          </Button>
          
          <Button
            startIcon={<InfoIcon />}
            onClick={() => navigate('/top-level-agent')}
            sx={{
              color: isDark ? '#ececf1' : '#1D1D1F',
              textTransform: 'none',
              fontWeight: 500,
              bgcolor: isActive('/top-level-agent') 
                ? (isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)') 
                : 'transparent',
              '&:hover': {
                bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
              },
            }}
          >
            TopLevelAgent
          </Button>
          
          <Button
            startIcon={<ToolsIcon />}
            onClick={() => navigate('/tools')}
            sx={{
              color: isDark ? '#ececf1' : '#1D1D1F',
              textTransform: 'none',
              fontWeight: 500,
              bgcolor: isActive('/tools') 
                ? (isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)') 
                : 'transparent',
              '&:hover': {
                bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
              },
            }}
          >
            Tools
          </Button>
        </Box>

        {/* Right side - Settings and Login/User Avatar */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton
            onClick={() => navigate('/settings')}
            sx={{
              color: isDark ? '#ececf1' : '#1D1D1F',
              '&:hover': {
                bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
              },
            }}
          >
            <SettingsIcon />
          </IconButton>
          
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
                    bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                  },
                }}
                onClick={handleUserMenuOpen}
              >
                <AgentAvatar seed={userName} size={32} />
                <Typography
                  variant="body2"
                  sx={{
                    color: isDark ? '#ececf1' : '#1D1D1F',
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
                    bgcolor: isDark ? '#202123' : '#FFFFFF',
                    border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
                    mt: 1,
                    minWidth: 180,
                  },
                }}
              >
                <MenuItem
                  onClick={handleUserMenuClose}
                  sx={{
                    color: isDark ? '#ececf1' : '#1D1D1F',
                    '&:hover': {
                      bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                    },
                  }}
                >
                  Profile
                </MenuItem>
                <MenuItem
                  onClick={() => handleNavigate('/settings')}
                  sx={{
                    color: isDark ? '#ececf1' : '#1D1D1F',
                    '&:hover': {
                      bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                    },
                  }}
                >
                  Settings
                </MenuItem>
                <MenuItem
                  onClick={handleLogout}
                  sx={{
                    color: isDark ? '#ececf1' : '#1D1D1F',
                    '&:hover': {
                      bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
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

export default AppHeader

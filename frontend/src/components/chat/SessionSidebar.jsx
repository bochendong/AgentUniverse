import React from 'react'
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  IconButton,
  Typography,
  Divider,
} from '@mui/material'
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useTheme } from '../../contexts/ThemeContext'
import { formatDate } from '../../utils/dateFormatter'

/**
 * SessionSidebar - Sidebar component for managing chat sessions
 */
export default function SessionSidebar({
  open,
  onToggle,
  sessions,
  currentSessionId,
  loading,
  onNewChat,
  onSelectSession,
  onDeleteSession,
  drawerWidth = 260,
}) {
  const navigate = useNavigate()
  const theme = useTheme()
  const isDark = theme.mode === 'dark'

  return (
    <Drawer
      variant="persistent"
      open={open}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        position: 'relative',
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          bgcolor: isDark ? '#202123' : '#FFFFFF',
          color: isDark ? '#ececf1' : '#1D1D1F',
          borderRight: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)',
          position: 'relative',
          height: '100%',
          top: 0,
          zIndex: 0,
        },
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
        }}
      >
        {/* Sidebar Toggle Button */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            p: 1.5,
            borderBottom: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)',
          }}
        >
          <Typography
            variant="subtitle2"
            sx={{
              fontWeight: 600,
              color: isDark ? '#ececf1' : '#1D1D1F',
            }}
          >
            Chat History
          </Typography>
          <IconButton
            size="small"
            onClick={onToggle}
            sx={{
              color: isDark ? '#ececf1' : '#1D1D1F',
              '&:hover': {
                bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
              },
            }}
          >
            {open ? <ChevronLeftIcon /> : <MenuIcon />}
          </IconButton>
        </Box>
        
        {/* New Chat Button */}
        <Box
          sx={{
            p: 2,
            borderBottom: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)',
          }}
        >
          <Box
            onClick={onNewChat}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              p: 1.5,
              borderRadius: '8px',
              bgcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,122,255,0.08)',
              cursor: 'pointer',
              border: isDark ? 'none' : '1px solid rgba(0,122,255,0.15)',
              '&:hover': {
                bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,122,255,0.12)',
                borderColor: isDark ? 'none' : 'rgba(0,122,255,0.25)',
              },
              transition: 'all 0.2s',
            }}
          >
            <AddIcon sx={{ fontSize: 20, color: isDark ? '#ececf1' : '#007AFF' }} />
            <Typography 
              variant="body2" 
              sx={{ 
                fontWeight: 600,
                color: isDark ? '#ececf1' : '#007AFF',
              }}
            >
              New chat
            </Typography>
          </Box>
        </Box>

        {/* Sessions List */}
        <Box
          sx={{
            flex: 1,
            overflowY: 'auto',
            '&::-webkit-scrollbar': {
              width: '8px',
            },
            '&::-webkit-scrollbar-track': {
              background: isDark ? '#202123' : '#F5F5F7',
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
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body2" sx={{ color: isDark ? '#8e8ea0' : '#86868B' }}>
                Loading...
              </Typography>
            </Box>
          ) : sessions.length === 0 ? (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body2" sx={{ color: isDark ? '#8e8ea0' : '#86868B' }}>
                No chat history
              </Typography>
            </Box>
          ) : (
            <List sx={{ p: 0 }}>
              {sessions.map((session, index) => (
                <React.Fragment key={session.id}>
                  {index > 0 && (
                    <Divider 
                      sx={{ 
                        borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)',
                      }} 
                    />
                  )}
                  <ListItem
                    disablePadding
                    sx={{
                      bgcolor: currentSessionId === session.id 
                        ? (isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)')
                        : 'transparent',
                      '&:hover': {
                        bgcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)',
                      },
                    }}
                  >
                    <ListItemButton
                      onClick={() => onSelectSession(session.id)}
                      sx={{
                        py: 1.5,
                        px: 2,
                        '&:hover': {
                          bgcolor: 'transparent',
                        },
                      }}
                    >
                      <ListItemText
                        primary={
                          <Typography
                            variant="body2"
                            sx={{
                              fontWeight: currentSessionId === session.id ? 600 : 500,
                              color: isDark ? '#ececf1' : '#1D1D1F',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {session.title || 'New Chat'}
                          </Typography>
                        }
                        secondary={
                          <Typography
                            variant="caption"
                            sx={{
                              color: isDark ? '#8e8ea0' : '#86868B',
                              fontSize: '0.75rem',
                            }}
                          >
                            {formatDate(session.updated_at)}
                          </Typography>
                        }
                      />
                      <IconButton
                        size="small"
                        onClick={(e) => onDeleteSession(session.id, e)}
                        sx={{
                          color: isDark ? '#8e8ea0' : '#86868B',
                          '&:hover': {
                            color: isDark ? '#ececf1' : '#1D1D1F',
                            bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                          },
                        }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </ListItemButton>
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          )}
        </Box>

        {/* Settings Button */}
        <Box
          sx={{
            p: 2,
            borderTop: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)',
          }}
        >
          <Box
            onClick={() => navigate('/settings')}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              p: 1.5,
              borderRadius: '8px',
              bgcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)',
              cursor: 'pointer',
              '&:hover': {
                bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)',
              },
              transition: 'background-color 0.2s',
            }}
          >
            <SettingsIcon sx={{ fontSize: 20, color: isDark ? '#ececf1' : '#1D1D1F' }} />
            <Typography 
              variant="body2" 
              sx={{ 
                fontWeight: 500,
                color: isDark ? '#ececf1' : '#1D1D1F',
              }}
            >
              Settings
            </Typography>
          </Box>
        </Box>
      </Box>
    </Drawer>
  )
}


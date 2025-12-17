import React, { createContext, useContext, useState, useEffect } from 'react'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'

const ThemeContext = createContext()

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeContextProvider')
  }
  return context
}

export const ThemeContextProvider = ({ children }) => {
  const [mode, setMode] = useState(() => {
    // 从 localStorage 读取保存的主题
    const savedMode = localStorage.getItem('themeMode')
    return savedMode || 'dark'
  })

  useEffect(() => {
    // 保存主题到 localStorage
    localStorage.setItem('themeMode', mode)
  }, [mode])

  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'))
  }

  const theme = createTheme({
    palette: {
      mode,
      ...(mode === 'light'
        ? {
            // 浅色主题
            primary: {
              main: '#007AFF',
            },
            background: {
              default: '#FFFFFF',
              paper: '#F5F5F7',
            },
            text: {
              primary: '#1D1D1F',
              secondary: '#86868B',
            },
            // Chat 页面浅色主题
            chat: {
              background: '#F5F5F7',
              sidebar: '#FFFFFF',
              messageUser: '#007AFF',
              messageAssistant: '#E5E5E7',
              text: '#1D1D1F',
              textSecondary: '#86868B',
            },
          }
        : {
            // 深色主题（默认）
            primary: {
              main: '#19c37d',
            },
            background: {
              default: '#343541',
              paper: '#202123',
            },
            text: {
              primary: '#ececf1',
              secondary: '#8e8ea0',
            },
            // Chat 页面深色主题
            chat: {
              background: '#343541',
              sidebar: '#202123',
              messageUser: '#19c37d',
              messageAssistant: '#40414f',
              text: '#ececf1',
              textSecondary: '#8e8ea0',
            },
          }),
    },
    typography: {
      fontFamily: [
        '-apple-system',
        'BlinkMacSystemFont',
        '"Segoe UI"',
        'Roboto',
        '"Helvetica Neue"',
        'Arial',
        'sans-serif',
      ].join(','),
    },
  })

  return (
    <ThemeContext.Provider value={{ mode, toggleTheme }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeContext.Provider>
  )
}


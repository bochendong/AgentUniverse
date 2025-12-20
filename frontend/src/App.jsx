import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Box } from '@mui/material'
import { ThemeContextProvider } from './contexts/ThemeContext'
import AppHeader from './components/AppHeader'
import ChatPage from './pages/ChatPage'
import AgentsListPage from './pages/AgentsListPage'
import AgentDetailPage from './pages/AgentDetailPage'
import TopLevelAgentInfoPage from './pages/TopLevelAgentInfoPage'
import SettingsPage from './pages/SettingsPage'
import ToolsPage from './pages/ToolsPage'
import AgentAsToolDetailPage from './pages/AgentAsToolDetailPage'

function App() {
  return (
    <ThemeContextProvider>
      <Router>
        <Box sx={{ 
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex', 
          flexDirection: 'column',
          overflow: 'hidden',
          bgcolor: 'background.default',
        }}>
          {/* Unified Header */}
          <AppHeader />
          
          {/* Main Content Area */}
          <Box 
            component="main" 
            sx={{ 
              flex: 1,
              minHeight: 0,
              overflow: 'hidden',
              position: 'relative',
              mt: '64px', // Account for fixed header height
            }}
          >
            <Routes>
              <Route path="/" element={<ChatPage />} />
              <Route path="/agents" element={<AgentsListPage />} />
              <Route path="/agents/:agentId" element={<AgentDetailPage />} />
              <Route path="/top-level-agent" element={<TopLevelAgentInfoPage />} />
              <Route path="/tools" element={<ToolsPage />} />
              <Route path="/tools/:toolId" element={<AgentAsToolDetailPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeContextProvider>
  )
}

export default App


import React from 'react'
import { Box, Typography, Paper } from '@mui/material'
import { SmartToy as AgentIcon, ArrowDownward as ArrowDownIcon } from '@mui/icons-material'

/**
 * AgentFlowDiagram Component - Display agent workflow as a flow diagram
 * Shows only the main agent in the center
 */
function AgentFlowDiagram({
  agentName,
  agentClass,
  description,
}) {
  return (
    <Box
      sx={{
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 4,
      }}
    >
      {/* Main Agent */}
      <Paper
        sx={{
          p: 4,
          bgcolor: '#34C759',
          color: 'white',
          borderRadius: 3,
          boxShadow: '0 4px 12px rgba(52, 199, 89, 0.3)',
          minWidth: 300,
          maxWidth: 500,
          textAlign: 'center',
        }}
      >
        <AgentIcon sx={{ fontSize: 48, mb: 1 }} />
        <Typography
          variant="h5"
          sx={{
            fontWeight: 700,
            mb: 0.5,
          }}
        >
          {agentName}
        </Typography>
        <Typography
          variant="body2"
          sx={{
            opacity: 0.9,
            mb: 2,
          }}
        >
          {agentClass}
        </Typography>
        {description && (
          <Typography
            variant="body2"
            sx={{
              opacity: 0.85,
              fontSize: '0.875rem',
            }}
          >
            {description}
          </Typography>
        )}
      </Paper>
    </Box>
  )
}

export default AgentFlowDiagram

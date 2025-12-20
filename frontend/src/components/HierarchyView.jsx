import React from 'react'
import { Box, Paper, Typography, Card, CardContent, Chip } from '@mui/material'
import AgentAvatar from './AgentAvatar'

/**
 * HierarchyView Component
 * Displays agent hierarchy with parent, children, and grandchildren
 */
function HierarchyView({ parentAgent, currentAgent, children, onAgentClick }) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Parent Agent (if exists) */}
      {parentAgent && (
        <Box>
          <Typography variant="subtitle2" sx={{ color: '#86868B', mb: 1.5, fontWeight: 600 }}>
            Parent Agent
          </Typography>
          <AgentCard
            agent={parentAgent}
            onClick={() => onAgentClick(parentAgent)}
          />
        </Box>
      )}

      {/* Current Agent */}
      <Box>
        <Typography variant="subtitle2" sx={{ color: '#86868B', mb: 1.5, fontWeight: 600 }}>
          Current Agent
        </Typography>
        <AgentCard
          agent={currentAgent}
          onClick={() => onAgentClick(currentAgent)}
          highlighted
        />
      </Box>

      {/* Children */}
      {children && children.length > 0 && (
        <Box>
          <Typography variant="subtitle2" sx={{ color: '#86868B', mb: 1.5, fontWeight: 600 }}>
            Child Agents ({children.length})
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {children.map((child, index) => (
              <Box key={child.id || index}>
                <AgentCard
                  agent={child}
                  onClick={() => onAgentClick(child)}
                />
                {/* Grandchildren (children of child) */}
                {child.children && child.children.length > 0 && (
                  <Box sx={{ mt: 2, ml: 4, pl: 2, borderLeft: '2px solid rgba(0,0,0,0.1)' }}>
                    <Typography variant="caption" sx={{ color: '#86868B', mb: 1, display: 'block', fontWeight: 600 }}>
                      Child Agents ({child.children.length})
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      {child.children.map((grandchild, grandIndex) => (
                        <AgentCard
                          key={grandchild.id || grandIndex}
                          agent={grandchild}
                          onClick={() => onAgentClick(grandchild)}
                          size="small"
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </Box>
            ))}
          </Box>
        </Box>
      )}
    </Box>
  )
}

/**
 * AgentCard Component - displays agent information
 */
function AgentCard({ agent, onClick, highlighted = false, size = 'medium' }) {
  const isTopLevel = agent.agent_type === 'top_level_agent'
  const isMaster = agent.agent_type === 'master' || agent.metadata?.is_master_agent
  const isNotebook = agent.agent_type === 'notebook' || agent.metadata?.is_notebook_agent

  const cardHeight = size === 'small' ? 'auto' : '100%'
  const avatarSize = size === 'small' ? 32 : 48

  return (
    <Card
      onClick={onClick}
      sx={{
        bgcolor: highlighted ? '#007AFF15' : '#F5F5F7',
        border: highlighted ? '2px solid #007AFF' : '1px solid rgba(0,0,0,0.08)',
        borderRadius: 2,
        transition: 'all 0.2s',
        cursor: 'pointer',
        height: cardHeight,
        display: 'flex',
        flexDirection: 'column',
        '&:hover': {
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          transform: 'translateY(-2px)',
          borderColor: '#007AFF',
        },
      }}
    >
      <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', p: size === 'small' ? 1.5 : 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, mb: 1 }}>
          <AgentAvatar
            seed={agent.id || agent.notebook_id || agent.agent_name || agent.name}
            size={avatarSize}
          />
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              variant={size === 'small' ? 'body2' : 'subtitle1'}
              sx={{
                fontWeight: 600,
                color: '#1D1D1F',
                fontSize: size === 'small' ? '0.875rem' : '0.95rem',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                mb: 0.5,
              }}
            >
              {agent.notebook_title || agent.agent_name || agent.name || 'Unknown Agent'}
            </Typography>
            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
              {isTopLevel && (
                <Chip
                  label="Top Level"
                  size="small"
                  sx={{
                    bgcolor: '#FF6B6B15',
                    color: '#FF6B6B',
                    fontWeight: 500,
                    fontSize: '0.7rem',
                    height: 20,
                  }}
                />
              )}
              {isMaster && (
                <Chip
                  label="Master"
                  size="small"
                  sx={{
                    bgcolor: '#007AFF15',
                    color: '#007AFF',
                    fontWeight: 500,
                    fontSize: '0.7rem',
                    height: 20,
                  }}
                />
              )}
              {isNotebook && (
                <Chip
                  label="Notebook"
                  size="small"
                  sx={{
                    bgcolor: '#34C75915',
                    color: '#34C759',
                    fontWeight: 500,
                    fontSize: '0.7rem',
                    height: 20,
                  }}
                />
              )}
            </Box>
          </Box>
        </Box>

        {agent.description && (
          <Typography
            variant="body2"
            sx={{
              color: '#86868B',
              fontSize: size === 'small' ? '0.75rem' : '0.85rem',
              lineHeight: 1.5,
              display: '-webkit-box',
              WebkitLineClamp: size === 'small' ? 2 : 3,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              mt: 1,
            }}
          >
            {agent.description}
          </Typography>
        )}

        {size === 'small' && (
          <Typography variant="caption" sx={{ color: '#86868B', fontSize: '0.7rem', mt: 1 }}>
            ID: {(agent.id || agent.notebook_id || '').substring(0, 8)}...
          </Typography>
        )}
      </CardContent>
    </Card>
  )
}

export default HierarchyView


import React, { useRef, useEffect, useState, forwardRef } from 'react'
import { Box, Typography, Card, CardContent, Chip } from '@mui/material'
import AgentAvatar from './AgentAvatar'

/**
 * HierarchyGraphView Component
 * Displays agent hierarchy as a graph with edges connecting nodes
 */
function HierarchyGraphView({ parentAgent, currentAgent, children, onAgentClick, selectedAgentId }) {
  const containerRef = useRef(null)
  const nodeRefs = useRef({})
  const [edges, setEdges] = useState([])
  
  // Build nodes array for rendering
  const nodes = []
  
  // Add parent node if exists
  if (parentAgent) {
    nodes.push({ type: 'parent', agent: parentAgent, level: 0, id: parentAgent.id })
  }
  
  // Add current node
  nodes.push({ type: 'current', agent: currentAgent, level: 1, id: currentAgent.id })
  
  // Add children nodes (only direct children, no grandchildren)
  if (children && children.length > 0) {
    children.forEach((child) => {
      nodes.push({ type: 'child', agent: child, level: 2, parentId: currentAgent.id, id: child.id })
    })
  }

  // Calculate edges based on actual DOM positions
  useEffect(() => {
    if (!containerRef.current) return

    const newEdges = []
    
    nodes.forEach((node) => {
      if (node.parentId) {
        const parentEl = nodeRefs.current[node.parentId]
        const childEl = nodeRefs.current[node.id]
        
        if (parentEl && childEl && containerRef.current) {
          const containerRect = containerRef.current.getBoundingClientRect()
          const parentRect = parentEl.getBoundingClientRect()
          const childRect = childEl.getBoundingClientRect()
          
          // Calculate positions relative to container
          const x1 = parentRect.left - containerRect.left + parentRect.width / 2
          const y1 = parentRect.top - containerRect.top + parentRect.height
          const x2 = childRect.left - containerRect.left + childRect.width / 2
          const y2 = childRect.top - containerRect.top
          
          newEdges.push({
            id: `${node.parentId}-${node.id}`,
            x1,
            y1,
            x2,
            y2,
            isDashed: node.type === 'grandchild',
          })
        }
      }
    })
    
    setEdges(newEdges)
  }, [nodes, parentAgent, currentAgent, children])

  return (
    <Box
      ref={containerRef}
      sx={{
        position: 'relative',
        minHeight: 'calc(100vh - 200px)',
        width: '100%',
        p: 3,
        overflow: 'auto',
      }}
    >
      {/* SVG overlay for drawing edges */}
      <svg
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
          zIndex: 0,
        }}
      >
        {/* Arrow marker definition */}
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="10"
            refX="5"
            refY="5"
            orient="auto"
          >
            <polygon
              points="0 0, 10 5, 0 10"
              fill="#007AFF"
              opacity={0.4}
            />
          </marker>
        </defs>
        
        {/* Render edges */}
        {edges.map((edge) => (
          <line
            key={edge.id}
            x1={edge.x1}
            y1={edge.y1}
            x2={edge.x2}
            y2={edge.y2}
            stroke="#007AFF"
            strokeWidth={2}
            strokeDasharray={edge.isDashed ? '5,5' : '0'}
            opacity={0.4}
            markerEnd="url(#arrowhead)"
          />
        ))}
      </svg>

      {/* Render nodes */}
      <Box
        sx={{
          position: 'relative',
          zIndex: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: 3,
        }}
      >
        {/* Parent level */}
        {parentAgent && (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
            }}
          >
            <AgentNode
              ref={(el) => {
                if (el) {
                  nodeRefs.current[parentAgent.id] = el
                }
              }}
              agent={parentAgent}
              onClick={() => onAgentClick(parentAgent)}
              highlighted={selectedAgentId === parentAgent.id}
              role="parent"
            />
          </Box>
        )}

        {/* Current level */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
          }}
        >
          <AgentNode
            ref={(el) => {
              if (el) {
                nodeRefs.current[currentAgent.id] = el
              }
            }}
            agent={currentAgent}
            onClick={() => onAgentClick(currentAgent)}
            highlighted={selectedAgentId === currentAgent.id}
            isCurrentAgent={true}
          />
        </Box>

        {/* Children level */}
        {children && children.length > 0 && (
          <Box
            sx={{
              display: 'flex',
              flexWrap: 'wrap',
              justifyContent: 'center',
              gap: 2,
              alignItems: 'flex-start',
            }}
          >
            {children.map((child) => (
              <AgentNode
                key={child.id}
                ref={(el) => {
                  if (el) {
                    nodeRefs.current[child.id] = el
                  }
                }}
                agent={child}
                onClick={() => onAgentClick(child)}
                highlighted={selectedAgentId === child.id}
                role="child"
              />
            ))}
          </Box>
        )}
      </Box>
    </Box>
  )
}

/**
 * AgentNode Component - Individual agent card in the graph
 * All agents use the same size for consistency
 */
const AgentNode = React.forwardRef(({ agent, onClick, highlighted = false, isCurrentAgent = false, role = null }, ref) => {
  const isTopLevel = agent.agent_type === 'top_level_agent'
  const isMaster = agent.agent_type === 'master' || agent.metadata?.is_master_agent
  const isNotebook = agent.agent_type === 'notebook' || agent.metadata?.is_notebook_agent

  // All agents use the same size
  const cardWidth = 320
  const avatarSize = 48

  return (
    <Card
      ref={ref}
      onClick={onClick}
      sx={{
        width: cardWidth,
        minHeight: 180,
        bgcolor: highlighted ? '#007AFF15' : '#F5F5F7',
        border: highlighted ? '2px solid #007AFF' : '1px solid rgba(0,0,0,0.08)',
        borderRadius: 2,
        transition: 'all 0.2s',
        cursor: 'pointer',
        position: 'relative',
        zIndex: 2,
        '&:hover': {
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          transform: 'translateY(-2px)',
          borderColor: '#007AFF',
        },
      }}
    >
      <CardContent sx={{ p: 2.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, mb: 1.5 }}>
          <AgentAvatar
            seed={agent.id || agent.notebook_id || agent.agent_name || agent.name}
            size={avatarSize}
          />
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
              <Typography
                variant="subtitle1"
                sx={{
                  fontWeight: 600,
                  color: '#1D1D1F',
                  fontSize: '0.95rem',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {agent.notebook_title || agent.agent_name || agent.name || 'Unknown Agent'}
              </Typography>
              {isCurrentAgent && (
                <Chip
                  label="current agent"
                  size="small"
                  sx={{
                    bgcolor: '#007AFF',
                    color: 'white',
                    fontWeight: 500,
                    fontSize: '0.65rem',
                    height: 18,
                    '& .MuiChip-label': {
                      px: 0.75,
                    },
                  }}
                />
              )}
            </Box>
            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 1 }}>
              {role && (
                <Chip
                  label={role === 'parent' ? 'parent' : 'child'}
                  size="small"
                  sx={{
                    bgcolor: role === 'parent' ? '#FF950015' : '#AF52DE15',
                    color: role === 'parent' ? '#FF9500' : '#AF52DE',
                    fontWeight: 500,
                    fontSize: '0.7rem',
                    height: 20,
                  }}
                />
              )}
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
            
            {/* Description or additional info */}
            {agent.description && (
              <Typography
                variant="body2"
                sx={{
                  color: '#86868B',
                  fontSize: '0.75rem',
                  lineHeight: 1.5,
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  mt: 1,
                  mb: 0.5,
                }}
              >
                {agent.description}
              </Typography>
            )}
            
            {/* For MasterAgent: show children count if available */}
            {isMaster && agent.children && Array.isArray(agent.children) && (
              <Typography
                variant="caption"
                sx={{
                  color: '#86868B',
                  fontSize: '0.7rem',
                  mt: 0.5,
                }}
              >
                管理 {agent.children.length} 个子 Agent
              </Typography>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
})

AgentNode.displayName = 'AgentNode'

export default HierarchyGraphView


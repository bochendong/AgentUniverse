import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  Card,
  CardContent,
  Button,
  Grid,
} from '@mui/material'
import {
  ArrowBack as BackIcon,
  SmartToy as AgentIcon,
  Description as PromptIcon,
  AccountTree as HierarchyIcon,
} from '@mui/icons-material'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { prism } from 'react-syntax-highlighter/dist/esm/styles/prism'
import 'katex/dist/katex.min.css'
import { getTopLevelAgentInfo } from '../api/client'
import AgentAvatar from '../components/AgentAvatar'

function TopLevelAgentInfoPage() {
  const navigate = useNavigate()
  const [info, setInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const loadInfo = async () => {
      try {
        setLoading(true)
        const response = await getTopLevelAgentInfo()
        setInfo(response.data)
      } catch (err) {
        console.error('Failed to load TopLevelAgent info:', err)
        setError(err.response?.data?.detail || 'Failed to load TopLevelAgent info')
      } finally {
        setLoading(false)
      }
    }
    loadInfo()
  }, [])

  if (loading) {
    return (
      <Box
        sx={{
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          bgcolor: '#F5F5F7',
        }}
      >
        <CircularProgress />
      </Box>
    )
  }

  if (error || !info) {
    return (
      <Box
        sx={{
          width: '100%',
          height: '100%',
          bgcolor: '#F5F5F7',
          overflowY: 'auto',
          overflowX: 'hidden',
        }}
      >
        <Container maxWidth="xl" sx={{ py: 4 }}>
          <Alert severity="error" sx={{ mb: 3 }}>
            {error || 'Failed to load TopLevelAgent info'}
          </Alert>
          <Button startIcon={<BackIcon />} onClick={() => navigate('/')}>
            Back to Chat
          </Button>
        </Container>
      </Box>
    )
  }

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        bgcolor: '#F5F5F7',
        overflowY: 'auto',
        overflowX: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          flexShrink: 0,
          bgcolor: 'white',
          borderBottom: '1px solid rgba(0,0,0,0.06)',
          px: 4,
          py: 2,
        }}
      >
        <Container maxWidth="xl">
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <Box
              onClick={() => navigate('/')}
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 40,
                height: 40,
                borderRadius: '50%',
                bgcolor: '#F5F5F7',
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': {
                  bgcolor: '#E5E5E7',
                  transform: 'translateY(-2px)',
                },
              }}
            >
              <BackIcon sx={{ color: '#007AFF' }} />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 700,
                  color: '#1D1D1F',
                  letterSpacing: '-0.5px',
                  mb: 0.5,
                }}
              >
                TopLevelAgent
              </Typography>
              <Typography variant="body2" sx={{ color: '#86868B' }}>
                System Root Coordinator
              </Typography>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* Main Content - Left/Right Layout */}
      <Box
        sx={{
          flex: 1,
          minHeight: 0,
        }}
      >
        <Container
          maxWidth="xl"
          sx={{
            display: 'flex',
            gap: 3,
            py: 3,
            alignItems: 'flex-start',
          }}
        >
          {/* Left Side - Agent Card */}
          <Box
            sx={{
              width: { xs: '100%', md: '400px' },
              flexShrink: 0,
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
            }}
          >
            {/* Agent Card Info */}
            <Paper
              sx={{
                p: 3,
                bgcolor: 'white',
                borderRadius: 3,
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
              }}
            >
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 2 }}>
                <AgentAvatar
                  seed="toplevel-agent"
                  size={80}
                  sx={{
                    border: '3px solid #FF6B6B30',
                    boxShadow: '0 2px 8px #FF6B6B20',
                    mb: 2,
                  }}
                />
                <Chip
                  label="Top Level Agent"
                  sx={{
                    bgcolor: '#FF6B6B15',
                    color: '#FF6B6B',
                    fontWeight: 600,
                    mb: 2,
                  }}
                />
              </Box>

              {/* Agent Card Section */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <AgentIcon sx={{ color: '#007AFF', fontSize: 20 }} />
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 600,
                    color: '#1D1D1F',
                    fontSize: '1.1rem',
                  }}
                >
                  Agent Card
                </Typography>
              </Box>

              {info.agent_card ? (
                <>
                  {info.agent_card.summary && (
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant="subtitle2"
                        sx={{
                          color: '#86868B',
                          fontWeight: 600,
                          mb: 1.5,
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px',
                          fontSize: '0.7rem',
                        }}
                      >
                        Knowledge Summary
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#1D1D1F', lineHeight: 1.6 }}>
                        {info.agent_card.summary}
                      </Typography>
                    </Box>
                  )}

                  {info.agent_card.topics && info.agent_card.topics.length > 0 && (
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant="subtitle2"
                        sx={{
                          color: '#86868B',
                          fontWeight: 600,
                          mb: 1.5,
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px',
                          fontSize: '0.7rem',
                        }}
                      >
                        Content Topics
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {info.agent_card.topics.map((topic, index) => (
                          <Chip
                            key={index}
                            label={topic}
                            size="small"
                            sx={{
                              bgcolor: '#F5F5F7',
                              color: '#1D1D1F',
                              borderRadius: '12px',
                              border: '1px solid rgba(0,0,0,0.1)',
                              fontWeight: 500,
                              fontSize: '0.75rem',
                              height: 24,
                            }}
                          />
                        ))}
                      </Box>
                    </Box>
                  )}

                  {info.agent_card.metadata && Object.keys(info.agent_card.metadata).length > 0 && (
                    <Box>
                      <Typography
                        variant="subtitle2"
                        sx={{
                          color: '#86868B',
                          fontWeight: 600,
                          mb: 1.5,
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px',
                          fontSize: '0.7rem',
                        }}
                      >
                        Metadata
                      </Typography>
                      <Box
                        sx={{
                          '& pre': {
                            bgcolor: 'white',
                            borderRadius: 2,
                            padding: 2,
                            overflow: 'auto',
                            fontSize: '0.875rem',
                            fontFamily: 'monospace',
                            margin: 0,
                            border: '1px solid rgba(0,0,0,0.1)',
                            '& code': {
                              fontFamily: 'Consolas, Monaco, "Courier New", monospace',
                              bgcolor: 'transparent',
                            },
                          },
                        }}
                      >
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            code({ node, inline, className, children, ...props }) {
                              if (!inline) {
                                return (
                                  <SyntaxHighlighter
                                    style={prism}
                                    language="json"
                                    PreTag="div"
                                    customStyle={{
                                      backgroundColor: 'white',
                                      border: '1px solid rgba(0,0,0,0.1)',
                                      borderRadius: '8px',
                                      padding: '16px',
                                      margin: 0,
                                    }}
                                    {...props}
                                  >
                                    {String(children).replace(/\n$/, '')}
                                  </SyntaxHighlighter>
                                )
                              }
                              return (
                                <code className={className} {...props}>
                                  {children}
                                </code>
                              )
                            },
                          }}
                        >
                          {`\`\`\`json\n${JSON.stringify(info.agent_card.metadata, null, 2)}\n\`\`\``}
                        </ReactMarkdown>
                      </Box>
                    </Box>
                  )}

                  {(!info.agent_card.summary && 
                    (!info.agent_card.topics || info.agent_card.topics.length === 0) && 
                    (!info.agent_card.metadata || Object.keys(info.agent_card.metadata).length === 0)) && (
                    <Typography
                      variant="body2"
                      sx={{
                        color: '#86868B',
                        fontStyle: 'italic',
                        textAlign: 'center',
                        mt: 2,
                      }}
                    >
                      No agent card information available.
                    </Typography>
                  )}
                </>
              ) : (
                <Typography
                  variant="body2"
                  sx={{
                    color: '#86868B',
                    fontStyle: 'italic',
                    textAlign: 'center',
                    mt: 2,
                  }}
                >
                  No agent card information available.
                </Typography>
              )}
            </Paper>
          </Box>

          {/* Right Side - Prompt and Child Agents */}
          <Box
            sx={{
              flex: 1,
              minWidth: 0,
              display: 'flex',
              flexDirection: 'column',
              gap: 3,
            }}
          >
            {/* Prompt Section */}
            {info.instructions && (
              <Paper
                sx={{
                  p: 3,
                  bgcolor: 'white',
                  borderRadius: 3,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                  <PromptIcon sx={{ color: '#007AFF' }} />
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 600,
                      color: '#1D1D1F',
                    }}
                  >
                    Prompt / Instructions
                  </Typography>
                </Box>
                <Box
                  sx={{
                    '& p': {
                      margin: '0.5em 0',
                      color: '#1D1D1F',
                      lineHeight: 1.75,
                    },
                    '& pre': {
                      bgcolor: 'white',
                      borderRadius: 2,
                      padding: 2,
                      overflow: 'auto',
                      fontSize: '0.875rem',
                      fontFamily: 'monospace',
                      margin: '1em 0',
                      border: '1px solid rgba(0,0,0,0.1)',
                      '& code': {
                        fontFamily: 'Consolas, Monaco, "Courier New", monospace',
                        bgcolor: 'transparent',
                      },
                    },
                    '& code': {
                      bgcolor: '#F5F5F7',
                      padding: '2px 6px',
                      borderRadius: 1,
                      fontSize: '0.9em',
                      fontFamily: 'Consolas, Monaco, "Courier New", monospace',
                      color: '#E83E8C',
                    },
                    '& ul, & ol': {
                      paddingLeft: '1.5em',
                      margin: '0.5em 0',
                    },
                    '& li': {
                      margin: '0.25em 0',
                    },
                    '& h1, & h2, & h3, & h4, & h5, & h6': {
                      marginTop: '1em',
                      marginBottom: '0.5em',
                      fontWeight: 600,
                      color: '#1D1D1F',
                    },
                    '& h1': { fontSize: '2em' },
                    '& h2': { fontSize: '1.5em' },
                    '& h3': { fontSize: '1.25em' },
                    '& blockquote': {
                      borderLeft: '4px solid #007AFF',
                      paddingLeft: '1em',
                      margin: '1em 0',
                      color: '#86868B',
                      fontStyle: 'italic',
                    },
                    '& table': {
                      borderCollapse: 'collapse',
                      width: '100%',
                      margin: '1em 0',
                      '& th, & td': {
                        border: '1px solid rgba(0,0,0,0.1)',
                        padding: '8px',
                      },
                      '& th': {
                        bgcolor: '#F5F5F7',
                        fontWeight: 600,
                      },
                    },
                  }}
                >
                  {typeof info.instructions === 'string' ? (
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm, remarkMath]}
                      rehypePlugins={[rehypeKatex]}
                      components={{
                        code({ node, inline, className, children, ...props }) {
                          const match = /language-(\w+)/.exec(className || '')
                          return !inline && match ? (
                            <SyntaxHighlighter
                              style={prism}
                              language={match[1]}
                              PreTag="div"
                              customStyle={{
                                backgroundColor: 'white',
                                border: '1px solid rgba(0,0,0,0.1)',
                                borderRadius: '8px',
                                padding: '16px',
                                margin: '1em 0',
                              }}
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          ) : (
                            <code className={className} {...props}>
                              {children}
                            </code>
                          )
                        },
                      }}
                    >
                      {info.instructions}
                    </ReactMarkdown>
                  ) : (
                    <Typography
                      variant="body1"
                      sx={{
                        color: '#1D1D1F',
                        lineHeight: 1.6,
                      }}
                    >
                      {JSON.stringify(info.instructions, null, 2)}
                    </Typography>
                  )}
                </Box>
              </Paper>
            )}

            {/* Child Agents Section */}
            <Paper
              sx={{
                p: 3,
                bgcolor: 'white',
                borderRadius: 3,
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <HierarchyIcon sx={{ color: '#007AFF' }} />
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 600,
                    color: '#1D1D1F',
                  }}
                >
                  Child Agents (Top-Level Agents)
                </Typography>
                <Chip
                  label={info.child_agents?.length || 0}
                  size="small"
                  sx={{
                    bgcolor: '#007AFF15',
                    color: '#007AFF',
                    fontWeight: 600,
                    ml: 1,
                  }}
                />
              </Box>

              {info.child_agents && info.child_agents.length > 0 ? (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {info.child_agents.map((child, index) => (
                    <Card
                      key={child.agent_id || index}
                      sx={{
                        bgcolor: '#F5F5F7',
                        border: '1px solid rgba(0,0,0,0.08)',
                        borderRadius: 2,
                        transition: 'all 0.2s',
                        cursor: 'pointer',
                        '&:hover': {
                          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                          transform: 'translateY(-2px)',
                        },
                      }}
                      onClick={() => {
                        if (child.notebook_id) {
                          navigate(`/agents/${child.notebook_id}`)
                        }
                      }}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
                          <AgentAvatar
                            seed={`agent-${child.agent_id}`}
                            size={48}
                            sx={{
                              border: `2px solid ${
                                child.agent_type === 'master_agent'
                                  ? '#4ECDC430'
                                  : '#95E1D330'
                              }`,
                              boxShadow: `0 2px 8px ${
                                child.agent_type === 'master_agent'
                                  ? '#4ECDC420'
                                  : '#95E1D320'
                              }`,
                            }}
                          />
                          <Box sx={{ flex: 1 }}>
                            <Box sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center', flexWrap: 'wrap' }}>
                              <Typography
                                variant="subtitle1"
                                sx={{
                                  fontWeight: 600,
                                  color: '#1D1D1F',
                                }}
                              >
                                {child.agent_name || 'Unnamed Agent'}
                              </Typography>
                              {child.agent_type === 'master_agent' && (
                                <Chip
                                  label="Master Agent"
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
                              {child.agent_type === 'NOTEBOOK_AGENT' && (
                                <Chip
                                  label="Notebook Agent"
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
                            {child.notebook_title && (
                              <Typography
                                variant="body2"
                                sx={{ color: '#86868B', mb: 1 }}
                              >
                                {child.notebook_title}
                              </Typography>
                            )}
                            {child.knowledge_summary && (
                              <Typography
                                variant="body2"
                                sx={{
                                  color: '#1D1D1F',
                                  mb: 1,
                                  display: '-webkit-box',
                                  WebkitLineClamp: 2,
                                  WebkitBoxOrient: 'vertical',
                                  overflow: 'hidden',
                                }}
                              >
                                {child.knowledge_summary}
                              </Typography>
                            )}
                            {child.content_topics && child.content_topics.length > 0 && (
                              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 1 }}>
                                {child.content_topics.slice(0, 5).map((topic, idx) => (
                                  <Chip
                                    key={idx}
                                    label={topic}
                                    size="small"
                                    sx={{
                                      bgcolor: 'white',
                                      color: '#86868B',
                                      fontSize: '0.7rem',
                                      height: 20,
                                      border: '1px solid rgba(0,0,0,0.1)',
                                    }}
                                  />
                                ))}
                              </Box>
                            )}
                          </Box>
                        </Box>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              ) : (
                <Box
                  sx={{
                    textAlign: 'center',
                    py: 4,
                    color: '#86868B',
                  }}
                >
                  <Typography variant="body2">
                    No child agents found
                  </Typography>
                </Box>
              )}
            </Paper>
          </Box>
        </Container>
      </Box>
    </Box>
  )
}

export default TopLevelAgentInfoPage


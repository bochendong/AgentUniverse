import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  CircularProgress,
  Alert,
  Paper,
  Button,
  Breadcrumbs,
  Link,
  Grid,
} from '@mui/material'
import { ArrowBack as ArrowBackIcon, SmartToy as AgentIcon, Build as BuildIcon } from '@mui/icons-material'
import { getTool, getAgentAsToolDetails } from '../api/client'
import AgentFlowDiagram from '../components/AgentFlowDiagram'

/**
 * AgentAsToolDetailPage Component - Display agent_as_tool details with flow diagram
 */
function AgentAsToolDetailPage() {
  const { toolId } = useParams()
  const navigate = useNavigate()
  const [tool, setTool] = useState(null)
  const [agentDetails, setAgentDetails] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadToolAndDetails()
  }, [toolId])

  const loadToolAndDetails = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load tool info
      const toolResponse = await getTool(toolId)
      const toolData = toolResponse.data

      if (toolData.tool_type !== 'agent_as_tool') {
        setError('This tool is not an agent_as_tool type')
        setLoading(false)
        return
      }

      setTool(toolData)

      // Load agent details
      try {
        const detailsResponse = await getAgentAsToolDetails(toolId)
        setAgentDetails(detailsResponse.data)
      } catch (detailsError) {
        console.warn('Failed to load agent details:', detailsError)
        // Continue without details
      }
    } catch (err) {
      console.error('Failed to load tool:', err)
      setError(err.response?.data?.detail || 'Failed to load tool')
    } finally {
      setLoading(false)
    }
  }

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
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          {/* Breadcrumbs */}
          <Breadcrumbs sx={{ mb: 2 }}>
            <Link
              component="button"
              variant="body2"
              onClick={() => navigate('/tools')}
              sx={{
                color: '#007AFF',
                textDecoration: 'none',
                '&:hover': {
                  textDecoration: 'underline',
                },
                cursor: 'pointer',
              }}
            >
              Skills
            </Link>
            <Typography variant="body2" sx={{ color: '#86868B' }}>
              {tool?.name || 'Loading...'}
            </Typography>
          </Breadcrumbs>

          {/* Title and Back Button */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={() => navigate('/tools')}
              sx={{
                color: '#86868B',
                textTransform: 'none',
                '&:hover': {
                  bgcolor: 'rgba(0,0,0,0.05)',
                },
              }}
            >
              返回
            </Button>
            <Box
              sx={{
                bgcolor: '#34C759',
                borderRadius: 2,
                p: 1.5,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <AgentIcon sx={{ color: 'white', fontSize: 32 }} />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  color: '#1D1D1F',
                  mb: 0.5,
                }}
              >
                {tool?.name || 'Loading...'}
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: '#86868B',
                }}
              >
                {tool?.agent_class_name || ''}
              </Typography>
            </Box>
          </Box>

          {/* Description */}
          {tool?.description && (
            <Paper
              sx={{
                p: 3,
                bgcolor: 'white',
                borderRadius: 2,
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                mb: 3,
              }}
            >
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 600,
                  color: '#1D1D1F',
                  mb: 1,
                }}
              >
                描述
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: '#1D1D1F',
                  lineHeight: 1.6,
                }}
              >
                {tool.description}
              </Typography>
            </Paper>
          )}
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        ) : tool && (
          <>
            {/* Flow Diagram */}
            <Paper
              sx={{
                p: 4,
                bgcolor: 'white',
                borderRadius: 3,
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                mb: 3,
              }}
            >
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 600,
                  color: '#1D1D1F',
                  mb: 3,
                }}
              >
                工作流程图
              </Typography>
              <AgentFlowDiagram
                agentName={tool.name}
                agentClass={tool.agent_class_name}
                description={tool.description}
              />
            </Paper>

            {/* Input/Output Section */}
            <Paper
              sx={{
                p: 4,
                bgcolor: 'white',
                borderRadius: 3,
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                mb: 3,
              }}
            >
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 600,
                  color: '#1D1D1F',
                  mb: 3,
                }}
              >
                输入/输出
              </Typography>

              {/* Input Parameters */}
              {tool.input_params && Object.keys(tool.input_params).length > 0 && (
                <Box sx={{ mb: 4 }}>
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 600,
                      color: '#1D1D1F',
                      mb: 2,
                    }}
                  >
                    输入参数
                  </Typography>
                  {Object.entries(tool.input_params).map(([paramName, paramInfo]) => {
                    const isCustomType = paramInfo.type && 
                      !['str', 'int', 'float', 'bool', 'boolean', 'dict', 'Dict', 'list', 'List'].includes(paramInfo.type)
                    
                    return (
                      <Box
                        key={paramName}
                        sx={{
                          p: 2.5,
                          mb: 2,
                          bgcolor: '#F5F5F7',
                          borderRadius: 2,
                          border: '1px solid rgba(0,0,0,0.06)',
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <Typography
                            variant="body1"
                            sx={{
                              fontWeight: 600,
                              color: '#1D1D1F',
                              fontFamily: 'monospace',
                            }}
                          >
                            {paramName}
                          </Typography>
                          <Typography
                            variant="caption"
                            sx={{
                              bgcolor: '#007AFF15',
                              color: '#007AFF',
                              px: 1.5,
                              py: 0.5,
                              borderRadius: 1,
                              fontWeight: 500,
                            }}
                          >
                            {paramInfo.type || 'unknown'}
                          </Typography>
                          {paramInfo.required && (
                            <Typography
                              variant="caption"
                              sx={{
                                bgcolor: '#FF6B6B15',
                                color: '#FF6B6B',
                                px: 1.5,
                                py: 0.5,
                                borderRadius: 1,
                                fontWeight: 500,
                              }}
                            >
                              必需
                            </Typography>
                          )}
                        </Box>
                        {paramInfo.description && (
                          <Typography
                            variant="body2"
                            sx={{
                              color: '#86868B',
                              mb: isCustomType ? 1.5 : 0,
                            }}
                          >
                            {paramInfo.description}
                          </Typography>
                        )}
                        {isCustomType && (
                          <Box
                            sx={{
                              mt: 1.5,
                              p: 2,
                              bgcolor: 'white',
                              borderRadius: 1.5,
                              border: '1px solid rgba(0,0,0,0.1)',
                            }}
                          >
                            <Typography
                              variant="caption"
                              sx={{
                                color: '#86868B',
                                fontWeight: 600,
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px',
                                mb: 1,
                                display: 'block',
                              }}
                            >
                              结构定义
                            </Typography>
                            <Typography
                              variant="body2"
                              sx={{
                                color: '#1D1D1F',
                                fontFamily: 'monospace',
                                fontSize: '0.875rem',
                                whiteSpace: 'pre-wrap',
                              }}
                            >
                              {getTypeStructure(paramInfo.type)}
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    )
                  })}
                </Box>
              )}

              {/* Output */}
              {tool.output_type && (
                <Box>
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 600,
                      color: '#1D1D1F',
                      mb: 2,
                    }}
                  >
                    输出
                  </Typography>
                  <Box
                    sx={{
                      p: 2.5,
                      bgcolor: '#F5F5F7',
                      borderRadius: 2,
                      border: '1px solid rgba(0,0,0,0.06)',
                    }}
                  >
                    <Typography
                      variant="body1"
                      sx={{
                        fontWeight: 600,
                        color: '#1D1D1F',
                        fontFamily: 'monospace',
                        mb: 1,
                      }}
                    >
                      {tool.output_type}
                    </Typography>
                    {tool.output_description && (
                      <Typography
                        variant="body2"
                        sx={{
                          color: '#86868B',
                          mb: 1.5,
                        }}
                      >
                        {tool.output_description}
                      </Typography>
                    )}
                    {isCustomOutputType(tool.output_type) && (
                      <Box
                        sx={{
                          mt: 1.5,
                          p: 2,
                          bgcolor: 'white',
                          borderRadius: 1.5,
                          border: '1px solid rgba(0,0,0,0.1)',
                        }}
                      >
                        <Typography
                          variant="caption"
                          sx={{
                            color: '#86868B',
                            fontWeight: 600,
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            mb: 1,
                            display: 'block',
                          }}
                        >
                          结构定义
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{
                            color: '#1D1D1F',
                            fontFamily: 'monospace',
                            fontSize: '0.875rem',
                            whiteSpace: 'pre-wrap',
                          }}
                        >
                          {getTypeStructure(tool.output_type)}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </Box>
              )}
            </Paper>

            {/* Sub-agents Section */}
            {agentDetails?.sub_agents && agentDetails.sub_agents.length > 0 && (
              <Paper
                sx={{
                  p: 4,
                  bgcolor: 'white',
                  borderRadius: 3,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                  mb: 3,
                }}
              >
                <Typography
                  variant="h5"
                  sx={{
                    fontWeight: 600,
                    color: '#1D1D1F',
                    mb: 3,
                  }}
                >
                  使用的子 Agents
                </Typography>
                <Grid container spacing={3}>
                  {agentDetails.sub_agents.map((subAgent, idx) => (
                    <Grid item xs={12} sm={6} md={4} key={idx}>
                      <Paper
                        sx={{
                          p: 3,
                          height: '100%',
                          bgcolor: '#34C75915',
                          border: '2px solid #34C759',
                          borderRadius: 2,
                          transition: 'all 0.2s',
                          '&:hover': {
                            boxShadow: '0 4px 12px rgba(52, 199, 89, 0.2)',
                            transform: 'translateY(-2px)',
                          },
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                          <AgentIcon sx={{ color: '#34C759', fontSize: 28 }} />
                          <Typography
                            variant="h6"
                            sx={{
                              fontWeight: 600,
                              color: '#1D1D1F',
                            }}
                          >
                            {subAgent.name}
                          </Typography>
                        </Box>
                        <Typography
                          variant="body2"
                          sx={{
                            color: '#86868B',
                            lineHeight: 1.6,
                          }}
                        >
                          {subAgent.description}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            )}

            {/* Skills Section */}
            {agentDetails?.tools && agentDetails.tools.length > 0 && (
              <Paper
                sx={{
                  p: 4,
                  bgcolor: 'white',
                  borderRadius: 3,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                  mb: 3,
                }}
              >
                <Typography
                  variant="h5"
                  sx={{
                    fontWeight: 600,
                    color: '#1D1D1F',
                    mb: 3,
                  }}
                >
                  使用的工具
                </Typography>
                <Grid container spacing={3}>
                  {agentDetails.tools.map((toolItem, idx) => (
                    <Grid item xs={12} sm={6} md={4} key={idx}>
                      <Paper
                        sx={{
                          p: 3,
                          height: '100%',
                          bgcolor: '#007AFF15',
                          border: '2px solid #007AFF',
                          borderRadius: 2,
                          transition: 'all 0.2s',
                          '&:hover': {
                            boxShadow: '0 4px 12px rgba(0, 122, 255, 0.2)',
                            transform: 'translateY(-2px)',
                          },
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                          <BuildIcon sx={{ color: '#007AFF', fontSize: 28 }} />
                          <Typography
                            variant="h6"
                            sx={{
                              fontWeight: 600,
                              color: '#1D1D1F',
                            }}
                          >
                            {toolItem.name}
                          </Typography>
                        </Box>
                        <Typography
                          variant="body2"
                          sx={{
                            color: '#86868B',
                            lineHeight: 1.6,
                          }}
                        >
                          {toolItem.description}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            )}

            {/* Instructions Section */}
            {agentDetails?.instructions && (
              <Paper
                sx={{
                  p: 4,
                  bgcolor: 'white',
                  borderRadius: 3,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                }}
              >
                <Typography
                  variant="h5"
                  sx={{
                    fontWeight: 600,
                    color: '#1D1D1F',
                    mb: 3,
                  }}
                >
                  Agent Prompt
                </Typography>
                <Box
                  sx={{
                    p: 3,
                    bgcolor: '#F5F5F7',
                    borderRadius: 2,
                    border: '1px solid rgba(0,0,0,0.06)',
                  }}
                >
                  <Typography
                    variant="body2"
                    sx={{
                      color: '#1D1D1F',
                      lineHeight: 1.8,
                      whiteSpace: 'pre-wrap',
                      fontFamily: 'monospace',
                      fontSize: '0.875rem',
                    }}
                  >
                    {agentDetails.instructions}
                  </Typography>
                </Box>
              </Paper>
            )}
          </>
        )}
      </Container>
    </Box>
  )
}

// Helper function to check if output type is custom
function isCustomOutputType(outputType) {
  if (!outputType) return false
  const basicTypes = ['str', 'int', 'float', 'bool', 'boolean', 'dict', 'Dict', 'list', 'List']
  return !basicTypes.some(type => outputType.includes(type))
}

// Helper function to get type structure definition
function getTypeStructure(typeName) {
  const structures = {
    'Outline': `{
  notebook_title: str
  notebook_description: str
  outlines: Dict[str, str]  # 章节名称 -> 章节描述
}`,
    'Section': `{
  section_title: str
  introduction: str
  concept_blocks: List[ConceptBlock]
  standalone_examples: List[Example]
  standalone_notes: List[str]
  summary: str
  exercises: List[Example]
}`,
    'ConceptBlock': `{
  definition: str
  examples: List[Example]
  notes: List[str]
  theorems: List[Theorem]
}`,
    'Example': `{
  question: str
  question_type: str  # multiple_choice, fill_blank, proof, short_answer, code
  answer: str
  options: List[str]  # 仅用于 multiple_choice
  correct_answer: str  # 仅用于 multiple_choice
  blanks: Dict[str, str]  # 仅用于 fill_blank
  proof: str  # 仅用于 proof
  code_answer: str  # 仅用于 code
  explanation: str
}`,
    'Theorem': `{
  theorem: str
  proof: str
  examples: List[Example]
}`,
    'NotebookCreationIntent': `{
  intent_type: str  # full_content, enhancement, knowledge_base, outline_first
  topic_or_theme: str
  content_richness: str  # rich, sparse
  requires_exercises: bool
  additional_requirements: Optional[str]
}`,
    'Dict[str, Section]': `{
  "章节名称1": Section,
  "章节名称2": Section,
  ...
}`,
  }
  
  return structures[typeName] || `自定义类型: ${typeName}\n\n请参考相关文档了解详细结构。`
}

export default AgentAsToolDetailPage

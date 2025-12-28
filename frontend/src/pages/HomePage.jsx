import React, { useEffect, useRef, useState } from 'react'
import { 
  Box, 
  Typography, 
  Button,
  Container,
  Grid,
  Card,
  CardContent,
  useTheme,
  Divider,
  Chip,
} from '@mui/material'
import { 
  Psychology as BrainIcon,
  RocketLaunch as RocketIcon,
  Code as CodeIcon,
  SmartToy as RobotIcon,
  PlayArrow as PlayIcon,
  AutoAwesome as SparklesIcon,
  Extension as ExtensionIcon,
  Hub as HubIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  CloudQueue as CloudIcon,
  IntegrationInstructions as IntegrationIcon,
  Architecture as ArchitectureIcon,
  Business as BusinessIcon,
  Analytics as AnalyticsIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useTheme as useCustomTheme } from '../contexts/ThemeContext'

/**
 * 高端未来感主页
 * 8个独立的section，内容丰富
 */
function HomePage() {
  const navigate = useNavigate()
  const theme = useTheme()
  const { isDark } = useCustomTheme()
  const [titleVisible, setTitleVisible] = useState(false)

  // 标题动画
  useEffect(() => {
    const timer = setTimeout(() => {
      setTitleVisible(true)
    }, 300)
    return () => clearTimeout(timer)
  }, [])

  // 滚动触发动画
  useEffect(() => {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -100px 0px'
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in')
        }
      })
    }, observerOptions)

    const elements = document.querySelectorAll('.scroll-animate')
    elements.forEach(el => observer.observe(el))

    return () => {
      elements.forEach(el => observer.unobserve(el))
    }
  }, [])

  const features = [
    {
      icon: <BrainIcon sx={{ fontSize: 48 }} />,
      title: '智能代理',
      description: '强大的AI代理系统，能够理解复杂任务并自动执行。支持自然语言交互，智能决策和任务分解。',
      color: '#00D9FF',
    },
    {
      icon: <CodeIcon sx={{ fontSize: 48 }} />,
      title: '工具集成',
      description: '丰富的工具生态系统，支持各种功能扩展。轻松集成第三方API、数据库和自定义工具。',
      color: '#0099FF',
    },
    {
      icon: <RobotIcon sx={{ fontSize: 48 }} />,
      title: '自主协作',
      description: '多个代理可以自主协作，完成复杂工作流。智能任务分配和结果汇总，实现高效团队协作。',
      color: '#00FFCC',
    },
    {
      icon: <SparklesIcon sx={{ fontSize: 48 }} />,
      title: '智能编排',
      description: '自动编排多个代理的工作流程，优化执行顺序和资源分配。支持条件分支和循环控制。',
      color: '#00FFFF',
    },
    {
      icon: <ExtensionIcon sx={{ fontSize: 48 }} />,
      title: '插件系统',
      description: '灵活的插件架构，支持自定义功能扩展。开发者可以轻松创建和分享自己的插件。',
      color: '#0099CC',
    },
    {
      icon: <HubIcon sx={{ fontSize: 48 }} />,
      title: '中心化管理',
      description: '统一的代理管理中心，监控所有代理的状态和性能。提供详细的日志和追踪功能。',
      color: '#0066FF',
    },
    {
      icon: <SecurityIcon sx={{ fontSize: 48 }} />,
      title: '安全可靠',
      description: '企业级安全保障，支持权限控制和数据加密。确保代理操作的安全性和合规性。',
      color: '#00AAFF',
    },
    {
      icon: <SpeedIcon sx={{ fontSize: 48 }} />,
      title: '高性能',
      description: '优化的执行引擎，支持并发处理和异步操作。快速响应，高效处理大量任务。',
      color: '#00D9FF',
    },
  ]

  const useCases = [
    {
      title: '自动化工作流',
      description: '将重复性任务自动化，释放团队时间专注于创新工作',
      icon: <BusinessIcon sx={{ fontSize: 40 }} />,
    },
    {
      title: '数据分析',
      description: '智能分析大量数据，提取关键洞察和趋势预测',
      icon: <AnalyticsIcon sx={{ fontSize: 40 }} />,
    },
    {
      title: '客户服务',
      description: '24/7智能客服，快速响应客户问题，提升满意度',
      icon: <RobotIcon sx={{ fontSize: 40 }} />,
    },
    {
      title: '内容生成',
      description: '自动生成高质量内容，包括文档、报告和创意文案',
      icon: <SparklesIcon sx={{ fontSize: 40 }} />,
    },
  ]

  const benefits = [
    '提升工作效率 300%',
    '减少人工错误 90%',
    '24/7 不间断运行',
    '快速响应市场变化',
    '降低运营成本 50%',
    '支持无限扩展',
  ]

  const titleWords = ['Let', 'us', 'build', 'the', 'future', 'of', 'AI']

  return (
    <Box
      sx={{
        minHeight: '100vh',
        position: 'relative',
        overflowX: 'hidden',
        overflowY: 'auto',
        background: isDark
          ? 'linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0d1117 100%)'
          : 'linear-gradient(135deg, #f0f4f8 0%, #e6f0f7 50%, #fafcff 100%)',
      }}
    >
      {/* Section 1: Hero */}
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          px: 3,
          pt: '64px',
          position: 'relative',
        }}
      >
        <Container maxWidth="lg">
          <Box
            sx={{
              textAlign: { xs: 'center', md: 'left' },
              position: 'relative',
            }}
          >
            <Box
              sx={{
                mb: 4,
                display: 'flex',
                flexWrap: 'wrap',
                justifyContent: { xs: 'center', md: 'flex-start' },
                gap: { xs: 1, md: 2 },
              }}
            >
              {titleWords.map((word, index) => (
                <Typography
                  key={index}
                  variant="h1"
                  sx={{
                    fontSize: { xs: '2.5rem', sm: '4rem', md: '6rem', lg: '8rem' },
                    fontWeight: 900,
                    color: isDark ? '#FFFFFF' : '#1a1a1a',
                    lineHeight: 1,
                    opacity: titleVisible ? 1 : 0,
                    transform: titleVisible ? 'translateY(0)' : 'translateY(30px)',
                    transition: `all 0.6s ease ${index * 0.1}s`,
                    '&:hover': {
                      background: 'linear-gradient(135deg, #00D9FF 0%, #0099FF 50%, #0066FF 100%)',
                      backgroundClip: 'text',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      transform: 'scale(1.05)',
                      textShadow: '0 0 30px rgba(0, 217, 255, 0.5)',
                    },
                  }}
                >
                  {word}
                </Typography>
              ))}
            </Box>

            <Box
              sx={{
                mb: 6,
                opacity: titleVisible ? 1 : 0,
                transform: titleVisible ? 'translateY(0)' : 'translateY(20px)',
                transition: 'all 0.8s ease 0.7s',
              }}
            >
              <Typography
                variant="h4"
                sx={{
                  color: isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
                  fontWeight: 300,
                  letterSpacing: 3,
                  fontSize: { xs: '1.2rem', md: '1.5rem' },
                }}
              >
                下一代AI代理平台
              </Typography>
            </Box>

            <Box
              sx={{
                display: 'flex',
                gap: 2,
                justifyContent: { xs: 'center', md: 'flex-start' },
                flexWrap: 'wrap',
                opacity: titleVisible ? 1 : 0,
                transform: titleVisible ? 'translateY(0)' : 'translateY(20px)',
                transition: 'all 0.8s ease 1s',
              }}
            >
              <Button
                variant="contained"
                size="large"
                startIcon={<PlayIcon />}
                onClick={() => navigate('/chat')}
                sx={{
                  px: 5,
                  py: 2,
                  fontSize: '1.1rem',
                  background: 'linear-gradient(135deg, #00D9FF 0%, #0099FF 50%, #0066FF 100%)',
                  color: '#FFFFFF',
                  fontWeight: 600,
                  borderRadius: '50px',
                  boxShadow: '0 10px 40px rgba(0, 217, 255, 0.4), 0 0 20px rgba(0, 153, 255, 0.3)',
                  textTransform: 'none',
                  '&:hover': {
                    transform: 'translateY(-3px) scale(1.05)',
                    boxShadow: '0 15px 50px rgba(0, 217, 255, 0.6), 0 0 30px rgba(0, 153, 255, 0.5)',
                    background: 'linear-gradient(135deg, #00FFFF 0%, #00AAFF 50%, #0077FF 100%)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                开始使用
              </Button>

              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/tools')}
                sx={{
                  px: 5,
                  py: 2,
                  fontSize: '1.1rem',
                  borderColor: isDark ? 'rgba(0, 217, 255, 0.5)' : 'rgba(0, 153, 255, 0.4)',
                  color: isDark ? '#00D9FF' : '#0066FF',
                  fontWeight: 600,
                  borderRadius: '50px',
                  borderWidth: 2,
                  backdropFilter: 'blur(10px)',
                  background: isDark
                    ? 'rgba(0, 217, 255, 0.1)'
                    : 'rgba(0, 153, 255, 0.05)',
                  textTransform: 'none',
                  boxShadow: isDark ? '0 0 20px rgba(0, 217, 255, 0.2)' : 'none',
                  '&:hover': {
                    borderWidth: 2,
                    background: isDark
                      ? 'rgba(0, 217, 255, 0.2)'
                      : 'rgba(0, 153, 255, 0.1)',
                    transform: 'translateY(-3px)',
                    boxShadow: isDark ? '0 0 30px rgba(0, 217, 255, 0.4)' : '0 0 20px rgba(0, 153, 255, 0.3)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                探索工具
              </Button>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* Section 2: Features */}
      <Container 
        maxWidth="lg" 
        sx={{ py: 15, minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
      >
        <Box
          className="scroll-animate"
          sx={{
            opacity: 0,
            transform: 'translateY(50px)',
            transition: 'all 0.8s ease',
            '&.animate-in': {
              opacity: 1,
              transform: 'translateY(0)',
            },
          }}
        >
          <Typography
            variant="h2"
            sx={{
              fontSize: { xs: '2rem', md: '3rem' },
              fontWeight: 800,
              mb: 8,
              textAlign: 'center',
              background: 'linear-gradient(135deg, #00D9FF 0%, #0099FF 50%, #0066FF 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              color: isDark ? '#FFFFFF' : '#1a1a1a',
            }}
          >
            Featured Features
          </Typography>
        </Box>

        <Grid container spacing={4} sx={{ mt: 4 }}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
              <Card
                className="scroll-animate"
                sx={{
                  height: '100%',
                  background: isDark
                    ? 'rgba(255, 255, 255, 0.05)'
                    : 'rgba(255, 255, 255, 0.8)',
                  backdropFilter: 'blur(20px)',
                  border: isDark
                    ? '1px solid rgba(0, 217, 255, 0.2)'
                    : '1px solid rgba(0, 102, 255, 0.15)',
                  borderRadius: '20px',
                  p: 3,
                  transition: 'all 0.4s ease',
                  position: 'relative',
                  overflow: 'hidden',
                  opacity: 0,
                  transform: 'translateY(50px)',
                  '&.animate-in': {
                    opacity: 1,
                    transform: 'translateY(0)',
                    transition: `all 0.8s ease ${index * 0.15}s`,
                  },
                  '&:hover': {
                    transform: 'translateY(-15px)',
                    boxShadow: isDark
                      ? `0 25px 70px rgba(0, 217, 255, 0.4), 0 0 40px rgba(0, 153, 255, 0.3)`
                      : `0 25px 70px rgba(0, 153, 255, 0.2)`,
                    borderColor: feature.color,
                    background: isDark
                      ? 'rgba(255, 255, 255, 0.08)'
                      : 'rgba(255, 255, 255, 0.95)',
                  },
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '3px',
                    background: `linear-gradient(90deg, ${feature.color} 0%, transparent 100%)`,
                    opacity: 0,
                    transition: 'opacity 0.3s ease',
                  },
                  '&:hover::before': {
                    opacity: 1,
                  },
                }}
              >
                <CardContent sx={{ p: 0 }}>
                  <Box
                    sx={{
                      color: feature.color,
                      mb: 2,
                      display: 'inline-block',
                      transition: 'transform 0.3s ease',
                      '&:hover': {
                        transform: 'scale(1.1) rotate(5deg)',
                      },
                    }}
                  >
                    {feature.icon}
                  </Box>
                  <Typography
                    variant="h5"
                    sx={{
                      color: isDark ? '#FFFFFF' : '#1a1a1a',
                      mb: 1.5,
                      fontWeight: 700,
                      fontSize: { xs: '1.2rem', md: '1.4rem' },
                    }}
                  >
                    {feature.title}
                  </Typography>
                  <Typography
                    variant="body2"
                    sx={{
                      color: isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
                      lineHeight: 1.7,
                      fontSize: { xs: '0.875rem', md: '0.95rem' },
                    }}
                  >
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Section 3: Use Cases */}
      <Container 
        maxWidth="lg" 
        sx={{ py: 15, minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
      >
        <Box
          className="scroll-animate"
          sx={{
            opacity: 0,
            transform: 'translateY(50px)',
            transition: 'all 0.8s ease',
            '&.animate-in': {
              opacity: 1,
              transform: 'translateY(0)',
            },
          }}
        >
          <Typography
            variant="h2"
            sx={{
              fontSize: { xs: '2rem', md: '3rem' },
              fontWeight: 800,
              mb: 8,
              textAlign: 'center',
              background: 'linear-gradient(135deg, #00D9FF 0%, #0099FF 50%, #0066FF 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              color: isDark ? '#FFFFFF' : '#1a1a1a',
            }}
          >
            应用场景
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {useCases.map((useCase, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                className="scroll-animate"
                sx={{
                  height: '100%',
                  background: isDark
                    ? 'rgba(255, 255, 255, 0.05)'
                    : 'rgba(255, 255, 255, 0.8)',
                  backdropFilter: 'blur(20px)',
                  border: isDark
                    ? '1px solid rgba(0, 217, 255, 0.2)'
                    : '1px solid rgba(0, 102, 255, 0.15)',
                  borderRadius: '20px',
                  p: 4,
                  textAlign: 'center',
                  opacity: 0,
                  transform: 'translateY(50px)',
                  '&.animate-in': {
                    opacity: 1,
                    transform: 'translateY(0)',
                    transition: `all 0.8s ease ${index * 0.2}s`,
                  },
                  '&:hover': {
                    transform: 'translateY(-10px)',
                    boxShadow: isDark
                      ? '0 20px 60px rgba(0, 217, 255, 0.3), 0 0 30px rgba(0, 153, 255, 0.2)'
                      : '0 20px 60px rgba(0, 153, 255, 0.15)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                <Box
                  sx={{
                    color: '#00D9FF',
                    mb: 2,
                    display: 'flex',
                    justifyContent: 'center',
                  }}
                >
                  {useCase.icon}
                </Box>
                <Typography
                  variant="h5"
                  sx={{
                    color: isDark ? '#FFFFFF' : '#1a1a1a',
                    mb: 2,
                    fontWeight: 700,
                  }}
                >
                  {useCase.title}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
                    lineHeight: 1.8,
                  }}
                >
                  {useCase.description}
                </Typography>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Section 4: Architecture */}
      <Container 
        maxWidth="lg" 
        sx={{ py: 15, minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
      >
        <Grid container spacing={6} alignItems="center">
          <Grid item xs={12} md={6}>
            <Box
              className="scroll-animate"
              sx={{
                opacity: 0,
                transform: 'translateX(-50px)',
                transition: 'all 0.8s ease',
                '&.animate-in': {
                  opacity: 1,
                  transform: 'translateX(0)',
                },
              }}
            >
              <ArchitectureIcon
                sx={{
                  fontSize: 80,
                  color: '#00D9FF',
                  mb: 3,
                  filter: 'drop-shadow(0 0 10px rgba(0, 217, 255, 0.5))',
                }}
              />
              <Typography
                variant="h2"
                sx={{
                  fontSize: { xs: '2rem', md: '3rem' },
                  fontWeight: 800,
                  mb: 3,
                  background: 'linear-gradient(135deg, #00D9FF 0%, #0099FF 50%, #0066FF 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  color: isDark ? '#FFFFFF' : '#1a1a1a',
                }}
              >
                模块化架构
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
                  lineHeight: 1.8,
                  fontSize: '1.1rem',
                  mb: 3,
                }}
              >
                采用模块化设计，每个组件都可以独立开发和部署。支持微服务架构，轻松扩展和维护。
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {['微服务', '容器化', 'API优先', '云原生'].map((tag, i) => (
                  <Chip
                    key={i}
                    label={tag}
                    sx={{
                      background: isDark
                        ? 'rgba(0, 217, 255, 0.2)'
                        : 'rgba(0, 153, 255, 0.1)',
                      color: '#00D9FF',
                      fontWeight: 600,
                      border: isDark ? '1px solid rgba(0, 217, 255, 0.3)' : 'none',
                    }}
                  />
                ))}
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box
              className="scroll-animate"
              sx={{
                opacity: 0,
                transform: 'translateX(50px)',
                transition: 'all 0.8s ease 0.3s',
                '&.animate-in': {
                  opacity: 1,
                  transform: 'translateX(0)',
                },
                p: 4,
                background: isDark
                  ? 'rgba(255, 255, 255, 0.05)'
                  : 'rgba(255, 255, 255, 0.8)',
                borderRadius: '20px',
                border: isDark
                  ? '1px solid rgba(147, 51, 234, 0.2)'
                  : '1px solid rgba(0, 0, 0, 0.1)',
              }}
            >
              <Typography
                variant="h6"
                sx={{
                  color: isDark ? '#FFFFFF' : '#1a1a1a',
                  mb: 2,
                  fontWeight: 700,
                }}
              >
                核心组件
              </Typography>
              {['代理引擎', '工具管理器', '会话管理', '日志系统', '监控中心'].map((component, i) => (
                <Box
                  key={i}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    mb: 1.5,
                  }}
                >
                  <CheckCircleIcon
                    sx={{
                      fontSize: 20,
                      color: '#00FFCC',
                    }}
                  />
                  <Typography
                    variant="body2"
                    sx={{
                      color: isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
                    }}
                  >
                    {component}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Grid>
        </Grid>
      </Container>

      {/* Section 5: Integration */}
      <Container 
        maxWidth="lg" 
        sx={{ py: 15, minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
      >
        <Box
          className="scroll-animate"
          sx={{
            opacity: 0,
            transform: 'translateY(50px)',
            transition: 'all 0.8s ease',
            '&.animate-in': {
              opacity: 1,
              transform: 'translateY(0)',
            },
            textAlign: 'center',
            mb: 8,
          }}
        >
          <IntegrationIcon
            sx={{
              fontSize: 80,
              color: '#0099FF',
              mb: 3,
              filter: 'drop-shadow(0 0 10px rgba(0, 153, 255, 0.5))',
            }}
          />
          <Typography
            variant="h2"
            sx={{
              fontSize: { xs: '2rem', md: '3rem' },
              fontWeight: 800,
              mb: 3,
              background: 'linear-gradient(135deg, #00D9FF 0%, #0099FF 50%, #0066FF 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              color: isDark ? '#FFFFFF' : '#1a1a1a',
            }}
          >
            轻松集成
          </Typography>
          <Typography
            variant="body1"
            sx={{
              color: isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
              lineHeight: 1.8,
              fontSize: '1.1rem',
              maxWidth: 600,
              mx: 'auto',
            }}
          >
            支持多种集成方式，包括REST API、Webhook、SDK等。快速接入现有系统，无需重构。
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {[
            { name: 'REST API', desc: '标准RESTful接口' },
            { name: 'Webhook', desc: '事件驱动集成' },
            { name: 'SDK', desc: '多语言SDK支持' },
            { name: 'CLI', desc: '命令行工具' },
          ].map((item, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                className="scroll-animate"
                sx={{
                  p: 3,
                  textAlign: 'center',
                  background: isDark
                    ? 'rgba(255, 255, 255, 0.05)'
                    : 'rgba(255, 255, 255, 0.8)',
                  border: isDark
                    ? '1px solid rgba(0, 217, 255, 0.2)'
                    : '1px solid rgba(0, 102, 255, 0.15)',
                  borderRadius: '15px',
                  opacity: 0,
                  transform: 'translateY(50px)',
                  '&.animate-in': {
                    opacity: 1,
                    transform: 'translateY(0)',
                    transition: `all 0.8s ease ${index * 0.15}s`,
                  },
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    borderColor: '#0099FF',
                    boxShadow: isDark ? '0 0 20px rgba(0, 153, 255, 0.3)' : '0 0 15px rgba(0, 153, 255, 0.2)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                <Typography
                  variant="h6"
                  sx={{
                    color: isDark ? '#FFFFFF' : '#1a1a1a',
                    mb: 1,
                    fontWeight: 700,
                  }}
                >
                  {item.name}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: isDark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)',
                  }}
                >
                  {item.desc}
                </Typography>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Section 6: Performance */}
      <Container 
        maxWidth="lg" 
        sx={{ py: 15, minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
      >
        <Box
          className="scroll-animate"
          sx={{
            opacity: 0,
            transform: 'translateY(50px)',
            transition: 'all 0.8s ease',
            '&.animate-in': {
              opacity: 1,
              transform: 'translateY(0)',
            },
            textAlign: 'center',
            mb: 8,
          }}
        >
          <SpeedIcon
            sx={{
              fontSize: 80,
              color: '#00FFCC',
              mb: 3,
              filter: 'drop-shadow(0 0 10px rgba(0, 255, 204, 0.5))',
            }}
          />
          <Typography
            variant="h2"
            sx={{
              fontSize: { xs: '2rem', md: '3rem' },
              fontWeight: 800,
              mb: 3,
              background: 'linear-gradient(135deg, #00D9FF 0%, #0099FF 50%, #0066FF 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              color: isDark ? '#FFFFFF' : '#1a1a1a',
            }}
          >
            卓越性能
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {[
            { metric: '< 100ms', label: '平均响应时间' },
            { metric: '10K+', label: '并发请求' },
            { metric: '99.9%', label: '可用性' },
            { metric: '24/7', label: '持续运行' },
          ].map((item, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                className="scroll-animate"
                sx={{
                  p: 4,
                  textAlign: 'center',
                  background: isDark
                    ? 'rgba(255, 255, 255, 0.05)'
                    : 'rgba(255, 255, 255, 0.8)',
                  border: isDark
                    ? '1px solid rgba(0, 217, 255, 0.2)'
                    : '1px solid rgba(0, 102, 255, 0.15)',
                  borderRadius: '20px',
                  opacity: 0,
                  transform: 'translateY(50px)',
                  '&.animate-in': {
                    opacity: 1,
                    transform: 'translateY(0)',
                    transition: `all 0.8s ease ${index * 0.15}s`,
                  },
                  '&:hover': {
                    transform: 'scale(1.05)',
                    borderColor: '#00FFCC',
                    boxShadow: isDark ? '0 0 25px rgba(0, 255, 204, 0.4)' : '0 0 20px rgba(0, 255, 204, 0.3)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                <Typography
                  variant="h3"
                  sx={{
                    fontWeight: 900,
                    mb: 1,
                    background: 'linear-gradient(135deg, #00D9FF 0%, #0099FF 50%, #0066FF 100%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    color: isDark ? '#FFFFFF' : '#1a1a1a',
                  }}
                >
                  {item.metric}
                </Typography>
                <Typography
                  variant="body1"
                  sx={{
                    color: isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
                  }}
                >
                  {item.label}
                </Typography>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Section 7: Benefits */}
      <Container 
        maxWidth="lg" 
        sx={{ py: 15, minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
      >
        <Box
          className="scroll-animate"
          sx={{
            opacity: 0,
            transform: 'translateY(50px)',
            transition: 'all 0.8s ease',
            '&.animate-in': {
              opacity: 1,
              transform: 'translateY(0)',
            },
            textAlign: 'center',
            mb: 8,
          }}
        >
          <Typography
            variant="h2"
            sx={{
              fontSize: { xs: '2rem', md: '3rem' },
              fontWeight: 800,
              mb: 3,
              background: 'linear-gradient(135deg, #00D9FF 0%, #0099FF 50%, #0066FF 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              color: isDark ? '#FFFFFF' : '#1a1a1a',
            }}
          >
            核心优势
          </Typography>
        </Box>

        <Grid container spacing={3}>
          {benefits.map((benefit, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card
                className="scroll-animate"
                sx={{
                  p: 3,
                  background: isDark
                    ? 'rgba(255, 255, 255, 0.05)'
                    : 'rgba(255, 255, 255, 0.8)',
                  border: isDark
                    ? '1px solid rgba(0, 217, 255, 0.2)'
                    : '1px solid rgba(0, 102, 255, 0.15)',
                  borderRadius: '15px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                  opacity: 0,
                  transform: 'translateX(-30px)',
                  '&.animate-in': {
                    opacity: 1,
                    transform: 'translateX(0)',
                    transition: `all 0.8s ease ${index * 0.1}s`,
                  },
                  '&:hover': {
                    transform: 'translateX(10px)',
                    borderColor: '#00D9FF',
                    boxShadow: isDark ? '0 0 20px rgba(0, 217, 255, 0.3)' : '0 0 15px rgba(0, 217, 255, 0.2)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                <CheckCircleIcon
                  sx={{
                    fontSize: 28,
                    color: '#00FFCC',
                    flexShrink: 0,
                    filter: 'drop-shadow(0 0 5px rgba(0, 255, 204, 0.5))',
                  }}
                />
                <Typography
                  variant="h6"
                  sx={{
                    color: isDark ? '#FFFFFF' : '#1a1a1a',
                    fontWeight: 600,
                  }}
                >
                  {benefit}
                </Typography>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Section 8: Stats */}
      <Container 
        maxWidth="lg" 
        sx={{ py: 15, minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
      >
        <Box
          className="scroll-animate"
          sx={{
            display: 'flex',
            justifyContent: 'center',
            gap: { xs: 4, md: 10 },
            flexWrap: 'wrap',
            opacity: 0,
            transform: 'translateY(50px)',
            transition: 'all 0.8s ease',
            '&.animate-in': {
              opacity: 1,
              transform: 'translateY(0)',
            },
          }}
        >
          {[
            { label: '代理数量', value: '∞', icon: <RocketIcon /> },
            { label: '工具集成', value: '50+', icon: <CodeIcon /> },
            { label: '智能协作', value: '100%', icon: <BrainIcon /> },
          ].map((stat, index) => (
            <Box
              key={index}
              sx={{
                textAlign: 'center',
              }}
            >
              <Box
                sx={{
                  color: '#00D9FF',
                  mb: 2,
                  display: 'flex',
                  justifyContent: 'center',
                  fontSize: '3rem',
                  '& svg': {
                    filter: 'drop-shadow(0 0 15px rgba(0, 217, 255, 0.6))',
                  },
                }}
              >
                {stat.icon}
              </Box>
              <Typography
                variant="h2"
                sx={{
                  fontWeight: 900,
                  mb: 1,
                  fontSize: { xs: '2.5rem', md: '4rem' },
                  background: 'linear-gradient(135deg, #00D9FF 0%, #0099FF 50%, #0066FF 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  color: isDark ? '#FFFFFF' : '#1a1a1a',
                }}
              >
                {stat.value}
              </Typography>
              <Typography
                variant="h6"
                sx={{
                  color: isDark ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)',
                  fontWeight: 400,
                  letterSpacing: 2,
                }}
              >
                {stat.label}
              </Typography>
            </Box>
          ))}
        </Box>
      </Container>
    </Box>
  )
}

export default HomePage

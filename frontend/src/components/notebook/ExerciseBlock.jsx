import React, { useState } from 'react'
import { Box, Typography, IconButton, Collapse, Paper } from '@mui/material'
import { ExpandMore as ExpandMoreIcon } from '@mui/icons-material'
import MarkdownText from './MarkdownText'

/**
 * ExerciseBlock - 练习题部分组件（支持5种题目类型）
 */
export default function ExerciseBlock({ exercise }) {
  const [expanded, setExpanded] = useState(false)

  if (!exercise) return null

  // 判断是否有可展开的内容
  const hasExpandableContent = 
    exercise.answer || 
    exercise.proof || 
    exercise.explanation || 
    exercise.code_answer ||
    (exercise.question_type === 'multiple_choice' && exercise.correct_answer) ||
    (exercise.question_type === 'fill_blank' && exercise.answer)

  // 获取题目类型标签
  const getQuestionTypeLabel = (type) => {
    const labels = {
      'multiple_choice': '选择题',
      'fill_blank': '填空题',
      'proof': '证明题',
      'short_answer': '简答题',
      'code': '代码题'
    }
    return labels[type] || '练习题'
  }

  // 渲染选择题
  const renderMultipleChoice = () => {
    if (exercise.question_type !== 'multiple_choice') return null
    return (
      <>
        {exercise.options && exercise.options.length > 0 && (
          <Box sx={{ mt: 1.5, mb: 1 }}>
            {exercise.options.map((option, index) => {
              const optionLabel = String.fromCharCode(65 + index) // A, B, C, D
              const isCorrect = exercise.correct_answer === optionLabel
              return (
                <Box
                  key={index}
                  sx={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    mb: 1,
                    p: 1,
                    borderRadius: '4px',
                    backgroundColor: isCorrect && expanded ? '#E8F5E9' : 'transparent',
                    border: isCorrect && expanded ? '1px solid #4CAF50' : '1px solid transparent',
                  }}
                >
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 600,
                      minWidth: '24px',
                      color: isCorrect && expanded ? '#2E7D32' : '#1D1D1F',
                    }}
                  >
                    {optionLabel}.
                  </Typography>
                  <Typography
                    variant="body2"
                    sx={{
                      color: '#1D1D1F',
                      lineHeight: 1.6,
                      whiteSpace: 'pre-line',
                      fontSize: '0.875rem',
                    }}
                  >
                    {option}
                  </Typography>
                </Box>
              )
            })}
          </Box>
        )}
      </>
    )
  }

  // 渲染填空题题目（高亮显示填空位置）
  const renderFillBlankQuestion = (questionText) => {
    if (exercise.question_type !== 'fill_blank') return questionText
    
    // 解析占位符：[空1]、[空2] 或 {blank1}、{blank2} 等
    const parts = []
    // 匹配 [空数字] 或 {blank数字} 或 {blank字符串} 格式
    const regex = /(\[空\d+\]|\{blank\d+\}|\{blank\w+\})/g
    let lastIndex = 0
    let match
    
    while ((match = regex.exec(questionText)) !== null) {
      // 添加占位符前的文本
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: questionText.substring(lastIndex, match.index)
        })
      }
      
      // 添加占位符
      parts.push({
        type: 'blank',
        placeholder: match[0]
      })
      
      lastIndex = match.index + match[0].length
    }
    
    // 添加剩余文本
    if (lastIndex < questionText.length) {
      parts.push({
        type: 'text',
        content: questionText.substring(lastIndex)
      })
    }
    
    // 如果没有找到占位符，直接返回原文本
    if (parts.length === 0 || parts.every(p => p.type === 'text')) {
      return questionText
    }
    
    return (
      <Box component="span" sx={{ display: 'inline' }}>
        {parts.map((part, idx) => {
          if (part.type === 'text') {
            return <span key={idx}>{part.content}</span>
          } else {
            return (
              <Box
                key={idx}
                component="span"
                sx={{
                  display: 'inline-block',
                  backgroundColor: '#FFF9C4',
                  border: '1px dashed #F57F17',
                  borderRadius: '3px',
                  padding: '2px 6px',
                  margin: '0 2px',
                  fontWeight: 600,
                  color: '#E65100',
                  fontSize: '0.875rem',
                }}
              >
                {part.placeholder}
              </Box>
            )
          }
        })}
      </Box>
    )
  }

  // 渲染代码题
  const renderCode = () => {
    if (exercise.question_type !== 'code' || !exercise.code_answer) return null
    return (
      <>
        <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, mt: 1, color: '#1D1D1F' }}>
          代码答案：
        </Typography>
        <Paper
          elevation={0}
          sx={{
            backgroundColor: '#1E1E1E',
            padding: '12px',
            borderRadius: '4px',
            mb: exercise.explanation ? 2 : 0,
            overflow: 'auto',
          }}
        >
          <Typography
            component="pre"
            sx={{
              color: '#D4D4D4',
              fontFamily: 'Monaco, "Courier New", monospace',
              fontSize: '0.75rem',
              lineHeight: 1.5,
              margin: 0,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {exercise.code_answer}
          </Typography>
        </Paper>
      </>
    )
  }

  return (
    <Box
      sx={{
        backgroundColor: '#FFF3E0',
        padding: '14px 18px',
        borderRadius: '8px',
        borderLeft: '4px solid #FF9800',
        marginBottom: '12px',
      }}
    >
      <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, color: '#1D1D1F' }}>
        {exercise.question_type ? getQuestionTypeLabel(exercise.question_type) : '练习题'}
      </Typography>
      {exercise.question && (
        <>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: hasExpandableContent ? 1 : 0 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#1D1D1F' }}>
                题目：
              </Typography>
              {exercise.question_type === 'fill_blank' ? (
                <Box
                  sx={{
                    color: '#1D1D1F',
                    lineHeight: 1.6,
                    whiteSpace: 'pre-line',
                  }}
                >
                  {renderFillBlankQuestion(exercise.question)}
                </Box>
              ) : (
                <MarkdownText variant="body1" fontSize="0.875rem">
                  {exercise.question}
                </MarkdownText>
              )}
              {exercise.question_type === 'multiple_choice' && renderMultipleChoice()}
            </Box>
            {hasExpandableContent && (
              <IconButton
                size="small"
                onClick={() => setExpanded(!expanded)}
                sx={{
                  color: '#FF9800',
                  padding: '4px',
                  ml: 1,
                  transition: 'transform 0.2s ease',
                  transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 152, 0, 0.1)',
                  },
                }}
              >
                <ExpandMoreIcon />
              </IconButton>
            )}
          </Box>
        </>
      )}
      <Collapse in={expanded}>
        {/* 选择题：显示正确答案和解释 */}
        {exercise.question_type === 'multiple_choice' && (
          <>
            {exercise.correct_answer && (
              <>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, mt: 1, color: '#1D1D1F' }}>
                  正确答案：
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: '#2E7D32', 
                    fontWeight: 600,
                    mb: exercise.explanation ? 1.5 : 0,
                  }}
                >
                  {exercise.correct_answer}
                </Typography>
              </>
            )}
            {exercise.explanation && (
              <>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#1D1D1F' }}>
                  解释：
                </Typography>
                <MarkdownText variant="body1" fontSize="0.875rem">
                  {exercise.explanation}
                </MarkdownText>
              </>
            )}
          </>
        )}

        {/* 填空题：显示每个空的答案和解释 */}
        {exercise.question_type === 'fill_blank' && (
          <>
            {exercise.blanks && (
              <>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, mt: 1, color: '#1D1D1F' }}>
                  答案：
                </Typography>
                <Box sx={{ mb: exercise.explanation || exercise.answer ? 2 : 0 }}>
                  {/* 支持字典格式（新格式）和数组格式（旧格式兼容） */}
                  {typeof exercise.blanks === 'object' && !Array.isArray(exercise.blanks) ? (
                    // 新格式：字典 { "[空1]": "答案1", "[空2]": "答案2" }
                    Object.entries(exercise.blanks).map(([placeholder, answer], index) => (
                      <Box
                        key={index}
                        sx={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          mb: 1,
                          p: 1,
                          borderRadius: '4px',
                          backgroundColor: '#E8F5E9',
                          border: '1px solid #4CAF50',
                        }}
                      >
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 600,
                            minWidth: '80px',
                            color: '#2E7D32',
                            flexShrink: 0,
                          }}
                        >
                          {placeholder}：
                        </Typography>
                        <Box sx={{ flex: 1 }}>
                          <MarkdownText variant="body1" fontSize="0.875rem">
                            {answer}
                          </MarkdownText>
                        </Box>
                      </Box>
                    ))
                  ) : Array.isArray(exercise.blanks) ? (
                    // 旧格式兼容：数组 ["答案1", "答案2"]
                    exercise.blanks.map((blankAnswer, index) => (
                      <Box
                        key={index}
                        sx={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          mb: 1,
                          p: 1,
                          borderRadius: '4px',
                          backgroundColor: '#E8F5E9',
                          border: '1px solid #4CAF50',
                        }}
                      >
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 600,
                            minWidth: '50px',
                            color: '#2E7D32',
                          }}
                        >
                          [空{index + 1}]：
                        </Typography>
                        <Typography
                          variant="body1"
                          sx={{
                            color: '#1D1D1F',
                            lineHeight: 1.6,
                            whiteSpace: 'pre-line',
                            flex: 1,
                          }}
                        >
                          {blankAnswer}
                        </Typography>
                      </Box>
                    ))
                  ) : null}
                </Box>
              </>
            )}
            {exercise.answer && (
              <>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#1D1D1F' }}>
                  完整答案说明：
                </Typography>
                <MarkdownText variant="body1" fontSize="0.875rem" sx={{ mb: exercise.explanation ? 2 : 0 }}>
                  {exercise.answer}
                </MarkdownText>
              </>
            )}
            {exercise.explanation && (
              <>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#1D1D1F' }}>
                  解释：
                </Typography>
                <MarkdownText variant="body1" fontSize="0.875rem">
                  {exercise.explanation}
                </MarkdownText>
              </>
            )}
          </>
        )}

        {/* 证明题：显示答案和证明步骤 */}
        {exercise.question_type === 'proof' && (
          <>
            {exercise.answer && (
              <>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, mt: 1, color: '#1D1D1F' }}>
                  答案：
                </Typography>
                <MarkdownText variant="body1" fontSize="0.875rem" sx={{ mb: exercise.proof ? 2 : 0 }}>
                  {exercise.answer}
                </MarkdownText>
              </>
            )}
            {exercise.proof && (
              <>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#1D1D1F' }}>
                  证明步骤：
                </Typography>
                <MarkdownText variant="body1" fontSize="0.875rem">
                  {exercise.proof}
                </MarkdownText>
              </>
            )}
          </>
        )}

        {/* 简答题：显示答案和解释 */}
        {exercise.question_type === 'short_answer' && (
          <>
            {exercise.answer && (
              <>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, mt: 1, color: '#1D1D1F' }}>
                  答案：
                </Typography>
                <MarkdownText variant="body1" fontSize="0.875rem" sx={{ mb: exercise.explanation ? 2 : 0 }}>
                  {exercise.answer}
                </MarkdownText>
              </>
            )}
            {exercise.explanation && (
              <>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#1D1D1F' }}>
                  解释：
                </Typography>
                <MarkdownText variant="body1" fontSize="0.875rem">
                  {exercise.explanation}
                </MarkdownText>
              </>
            )}
          </>
        )}

        {/* 代码题：显示代码答案和解释 */}
        {exercise.question_type === 'code' && (
          <>
            {renderCode()}
            {exercise.explanation && (
              <>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#1D1D1F' }}>
                  解释：
                </Typography>
                <MarkdownText variant="body1" fontSize="0.875rem">
                  {exercise.explanation}
                </MarkdownText>
              </>
            )}
          </>
        )}

        {/* 兼容旧格式：没有 question_type 的情况 */}
        {!exercise.question_type && (
          <>
            {exercise.answer && (
              <>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, mt: 1, color: '#1D1D1F' }}>
                  答案：
                </Typography>
                <MarkdownText variant="body1" fontSize="0.875rem">
                  {exercise.answer}
                </MarkdownText>
              </>
            )}
            {exercise.proof && (
              <>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#1D1D1F' }}>
                  证明：
                </Typography>
                <MarkdownText variant="body1" fontSize="0.875rem">
                  {exercise.proof}
                </MarkdownText>
              </>
            )}
          </>
        )}
      </Collapse>
    </Box>
  )
}


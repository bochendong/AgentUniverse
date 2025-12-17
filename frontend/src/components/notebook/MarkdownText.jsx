import React from 'react'
import { Box } from '@mui/material'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import 'katex/dist/katex.min.css'

/**
 * MarkdownText - 支持 Markdown、代码和数学公式的文本渲染组件
 */
export default function MarkdownText({ 
  children, 
  variant = 'body2',
  fontSize,
  sx = {},
  inline = false 
}) {
  if (!children) return null

  const baseFontSize = fontSize || (variant === 'body1' ? '0.875rem' : '0.8125rem')

  return (
    <Box
      component={inline ? 'span' : 'div'}
      sx={{
        color: '#1D1D1F',
        lineHeight: 1.6,
        fontSize: baseFontSize,
        '& p': {
          margin: inline ? 0 : '0.5em 0',
          display: inline ? 'inline' : 'block',
        },
        '& code': {
          backgroundColor: 'rgba(0, 0, 0, 0.05)',
          padding: '2px 4px',
          borderRadius: '3px',
          fontSize: '0.9em',
          fontFamily: 'Monaco, "Courier New", monospace',
        },
        ...sx,
      }}
    >
      <ReactMarkdown
        remarkPlugins={[remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          code({ node, inline: codeInline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '')
            return !codeInline && match ? (
              <SyntaxHighlighter
                style={oneLight}
                language={match[1]}
                PreTag="div"
                customStyle={{
                  backgroundColor: 'white',
                  border: '1px solid rgba(0,0,0,0.1)',
                  borderRadius: '6px',
                  padding: '12px',
                  margin: '0.5em 0',
                  fontSize: '0.75rem',
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
        {children}
      </ReactMarkdown>
    </Box>
  )
}

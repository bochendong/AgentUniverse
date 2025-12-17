import React from 'react'
import { Box, Typography } from '@mui/material'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import 'katex/dist/katex.min.css'

/**
 * DefinitionBlock - 定义部分组件（支持 Markdown、代码和数学公式）
 */
export default function DefinitionBlock({ definition }) {
  if (!definition) return null

  return (
    <Box
      sx={{
        backgroundColor: '#F5F5F7',
        padding: '14px 18px',
        borderRadius: '8px',
        borderLeft: '4px solid #007AFF',
        marginBottom: '16px',
      }}
    >
      <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1, color: '#1D1D1F', fontSize: '1rem' }}>
        定义
      </Typography>
      <Box
        sx={{
          color: '#1D1D1F',
          lineHeight: 1.6,
          '& p': {
            margin: '0.5em 0',
          },
          '& code': {
            backgroundColor: 'rgba(0, 0, 0, 0.05)',
            padding: '2px 4px',
            borderRadius: '3px',
            fontSize: '0.9em',
            fontFamily: 'Monaco, "Courier New", monospace',
          },
        }}
      >
        <ReactMarkdown
          remarkPlugins={[remarkMath]}
          rehypePlugins={[rehypeKatex]}
          components={{
            code({ node, inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '')
              return !inline && match ? (
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
          {definition}
        </ReactMarkdown>
      </Box>
    </Box>
  )
}

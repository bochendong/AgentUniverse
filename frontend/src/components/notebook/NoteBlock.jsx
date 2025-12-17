import React from 'react'
import { Box, Typography } from '@mui/material'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import 'katex/dist/katex.min.css'

/**
 * NoteBlock - 注释部分组件（支持 Markdown、代码和数学公式）
 */
export default function NoteBlock({ note, indent = false, showLabel = false }) {
  if (!note) return null

  return (
    <Box
      sx={{
        backgroundColor: '#FFF9E6',
        padding: '12px 16px',
        borderRadius: '8px',
        borderLeft: '4px solid #FFCC00',
        marginBottom: '12px',
        ml: indent ? 2 : 0,
      }}
    >
      {showLabel && (
        <Typography component="span" variant="body2" sx={{ fontWeight: 600, color: '#1D1D1F', fontSize: '0.8125rem', mb: 0.5, display: 'block' }}>
          注释：
        </Typography>
      )}
      <Box
        sx={{
          color: '#1D1D1F',
          lineHeight: 1.6,
          fontSize: '0.8125rem',
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
          {note}
        </ReactMarkdown>
      </Box>
    </Box>
  )
}

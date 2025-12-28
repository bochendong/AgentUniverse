import React from 'react'
import { Box } from '@mui/material'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import 'katex/dist/katex.min.css'
import { useTheme } from '../../contexts/ThemeContext'

/**
 * MarkdownRenderer - Enhanced markdown renderer with code highlighting and math support
 * Supports automatic JSON formatting
 */
export default function MarkdownRenderer({ content, isDark: isDarkProp }) {
  const theme = useTheme()
  const isDark = isDarkProp !== undefined ? isDarkProp : theme.mode === 'dark'

  if (!content) return null

  // Check if content already contains JSON code block
  const hasJsonBlock = /```json\s*[\s\S]*?\s*```/.test(content)
  
  let displayContent = content

  // Try to detect and format pure JSON (not wrapped in code block)
  if (!hasJsonBlock) {
    const jsonObjectRegex = /\{[\s\S]*?\}/
    const jsonMatch = content.match(jsonObjectRegex)
    
    if (jsonMatch) {
      try {
        // Try to parse JSON
        JSON.parse(jsonMatch[0])
        // Replace JSON part with formatted code block
        displayContent = content.replace(
          jsonObjectRegex,
          `\`\`\`json\n${JSON.stringify(JSON.parse(jsonMatch[0]), null, 2)}\n\`\`\``
        )
      } catch (e) {
        // JSON parsing failed, use original content
      }
    }
  }

  return (
    <Box
      sx={{
        '& p': {
          margin: '0.5em 0',
          color: isDark ? '#ececf1' : '#1D1D1F',
          lineHeight: 1.75,
        },
        '& pre': {
          bgcolor: isDark ? '#1e1e1e' : '#F5F5F7',
          borderRadius: '8px',
          padding: '16px',
          overflow: 'auto',
          margin: '1em 0',
          border: isDark ? 'none' : '1px solid rgba(0,0,0,0.1)',
          '& code': {
            fontFamily: 'Consolas, Monaco, "Courier New", monospace',
            color: isDark ? '#ececf1' : '#1D1D1F',
          },
        },
        '& code': {
          bgcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
          padding: '2px 6px',
          borderRadius: '4px',
          fontSize: '0.9em',
          fontFamily: 'Consolas, Monaco, "Courier New", monospace',
          color: isDark ? '#ececf1' : '#1D1D1F',
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
          color: isDark ? '#ececf1' : '#1D1D1F',
        },
        '& blockquote': {
          borderLeft: `4px solid ${isDark ? '#19c37d' : '#007AFF'}`,
          paddingLeft: '1em',
          margin: '1em 0',
          color: isDark ? '#8e8ea0' : '#86868B',
        },
        '& table': {
          borderCollapse: 'collapse',
          width: '100%',
          margin: '1em 0',
          '& th, & td': {
            border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
            padding: '8px',
            color: isDark ? '#ececf1' : '#1D1D1F',
          },
          '& th': {
            bgcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)',
            fontWeight: 600,
          },
        },
      }}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '')
            return !inline && match ? (
              <SyntaxHighlighter
                style={vscDarkPlus}
                language={match[1]}
                PreTag="div"
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
        {displayContent}
      </ReactMarkdown>
    </Box>
  )
}


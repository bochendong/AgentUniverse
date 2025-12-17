import React from 'react'
import { Box, Typography } from '@mui/material'
import ExampleBlock from './ExampleBlock'
import MarkdownText from './MarkdownText'

/**
 * TheoremBlock - 定理部分组件（支持 Markdown、代码和数学公式）
 */
export default function TheoremBlock({ theorem }) {
  if (!theorem) return null

  return (
    <Box sx={{ mb: 2, ml: 2 }}>
      <Box
        sx={{
          backgroundColor: '#F3E5F5',
          padding: '14px 18px',
          borderRadius: '8px',
          borderLeft: '4px solid #AF52DE',
          marginBottom: '12px',
        }}
      >
        <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1, color: '#1D1D1F', fontSize: '1rem' }}>
          定理
        </Typography>
        <Box sx={{ mb: theorem.proof ? 2 : 0 }}>
          <MarkdownText variant="body1" fontSize="0.875rem">
            {theorem.theorem}
          </MarkdownText>
        </Box>
        {theorem.proof && (
          <>
            <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#1D1D1F' }}>
              证明：
            </Typography>
            <MarkdownText variant="body1" fontSize="0.875rem">
              {theorem.proof}
            </MarkdownText>
          </>
        )}
      </Box>
      
      {/* Theorem Examples */}
      {theorem.examples?.map((example, exIndex) => (
        <ExampleBlock key={exIndex} example={example} indent={true} showLabel={false} />
      ))}
    </Box>
  )
}


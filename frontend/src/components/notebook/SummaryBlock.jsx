import React from 'react'
import { Box, Typography } from '@mui/material'
import MarkdownText from './MarkdownText'

/**
 * SummaryBlock - 总结部分组件（支持 Markdown、代码和数学公式）
 */
export default function SummaryBlock({ summary }) {
  if (!summary) return null

  return (
    <Box
      sx={{
        backgroundColor: '#E8F5E9',
        padding: '14px 18px',
        borderRadius: '8px',
        borderLeft: '4px solid #4CAF50',
        marginBottom: '20px',
      }}
    >
      <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1, color: '#1D1D1F', fontSize: '1rem' }}>
        总结
      </Typography>
      <MarkdownText variant="body1" fontSize="0.875rem">
        {summary}
      </MarkdownText>
    </Box>
  )
}


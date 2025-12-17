import React from 'react'
import { Box, Typography } from '@mui/material'
import MarkdownText from './MarkdownText'

/**
 * IntroductionBlock - 介绍部分组件（支持 Markdown、代码和数学公式）
 */
export default function IntroductionBlock({ introduction }) {
  if (!introduction) return null

  return (
    <Box
      sx={{
        backgroundColor: '#FFF4E6',
        padding: '14px 18px',
        borderRadius: '8px',
        borderLeft: '4px solid #FF9500',
        marginBottom: '20px',
      }}
    >
      <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1, color: '#1D1D1F', fontSize: '1rem' }}>
        介绍
      </Typography>
      <MarkdownText variant="body1" fontSize="0.875rem">
        {introduction}
      </MarkdownText>
    </Box>
  )
}

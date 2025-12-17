import React from 'react'
import { Box, Typography } from '@mui/material'
import SectionBlock from './SectionBlock'

/**
 * NotebookContent - 笔记本内容组件（结构化数据渲染）
 */
export default function NotebookContent({ content }) {
  if (!content || content.format !== 'structured') {
    return null
  }

  const { outline, sections } = content

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700 }}>
        {outline?.notebook_title || '未命名笔记本'}
      </Typography>
      
      {outline?.notebook_description && (
        <Box
          sx={{
            backgroundColor: '#E8F4FD',
            padding: '16px 20px',
            borderRadius: '8px',
            borderLeft: '4px solid #007AFF',
            marginBottom: '24px',
          }}
        >
          <Typography variant="body1" sx={{ color: '#1D1D1F', lineHeight: 1.6 }}>
            {outline.notebook_description}
          </Typography>
        </Box>
      )}
      
      {outline?.outlines && Object.keys(outline.outlines).map((sectionTitle) => {
        const section = sections?.[sectionTitle]
        if (!section) return null
        
        return <SectionBlock key={sectionTitle} section={section} />
      })}
    </Box>
  )
}


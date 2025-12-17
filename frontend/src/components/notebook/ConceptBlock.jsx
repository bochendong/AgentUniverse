import React, { useState } from 'react'
import { Box, Typography, IconButton, Collapse } from '@mui/material'
import { ExpandMore as ExpandMoreIcon, ExpandLess as ExpandLessIcon } from '@mui/icons-material'
import DefinitionBlock from './DefinitionBlock'
import ExampleBlock from './ExampleBlock'
import NoteBlock from './NoteBlock'
import TheoremBlock from './TheoremBlock'

/**
 * ConceptBlock - 概念块组件（包含定义、例子、笔记、定理）
 */
export default function ConceptBlock({ block }) {
  const [examplesExpanded, setExamplesExpanded] = useState(false)
  const [notesExpanded, setNotesExpanded] = useState(false)

  if (!block) return null

  const hasExamples = block.examples && block.examples.length > 0
  const examplesCount = block.examples?.length || 0
  const hasNotes = block.notes && block.notes.length > 0
  const notesCount = block.notes?.length || 0

  return (
    <Box sx={{ mb: 3 }}>
      {/* Definition */}
      <DefinitionBlock definition={block.definition} />
      
      {/* Examples - Collapsible */}
      {hasExamples && (
        <Box sx={{ ml: 2, mb: 1 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
              backgroundColor: '#F0F9FF',
              padding: '10px 14px',
              borderRadius: '6px',
              borderLeft: '3px solid #34C759',
              transition: 'all 0.2s ease',
              mb: examplesExpanded ? 1.5 : 0,
              '&:hover': {
                backgroundColor: '#E0F2FE',
                transform: 'translateX(2px)',
              },
            }}
            onClick={() => setExamplesExpanded(!examplesExpanded)}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography 
                variant="subtitle2" 
                sx={{ 
                  fontWeight: 600, 
                  color: '#1D1D1F',
                  fontSize: '0.875rem',
                }}
              >
                例子
              </Typography>
              <Box
                sx={{
                  backgroundColor: '#34C759',
                  color: 'white',
                  borderRadius: '12px',
                  padding: '2px 8px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  minWidth: '24px',
                  textAlign: 'center',
                }}
              >
                {examplesCount}
              </Box>
            </Box>
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation()
                setExamplesExpanded(!examplesExpanded)
              }}
              sx={{
                color: '#34C759',
                padding: '4px',
                transition: 'transform 0.2s ease',
                transform: examplesExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                '&:hover': {
                  backgroundColor: 'rgba(52, 199, 89, 0.1)',
                },
              }}
            >
              <ExpandMoreIcon />
            </IconButton>
          </Box>
          <Collapse in={examplesExpanded}>
            <Box sx={{ mt: 1, ml: 2 }}>
              {block.examples.map((example, exIndex) => (
                <ExampleBlock key={exIndex} example={example} indent={false} showLabel={false} />
              ))}
            </Box>
          </Collapse>
        </Box>
      )}
      
      {/* Notes - Collapsible */}
      {hasNotes && (
        <Box sx={{ ml: 2, mb: 1 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
              backgroundColor: '#FFF9E6',
              padding: '10px 14px',
              borderRadius: '6px',
              borderLeft: '3px solid #FFCC00',
              transition: 'all 0.2s ease',
              mb: notesExpanded ? 1.5 : 0,
              '&:hover': {
                backgroundColor: '#FFF4D6',
                transform: 'translateX(2px)',
              },
            }}
            onClick={() => setNotesExpanded(!notesExpanded)}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography 
                variant="subtitle2" 
                sx={{ 
                  fontWeight: 600, 
                  color: '#1D1D1F',
                  fontSize: '0.875rem',
                }}
              >
                注释
              </Typography>
              <Box
                sx={{
                  backgroundColor: '#FFCC00',
                  color: '#1D1D1F',
                  borderRadius: '12px',
                  padding: '2px 8px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  minWidth: '24px',
                  textAlign: 'center',
                }}
              >
                {notesCount}
              </Box>
            </Box>
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation()
                setNotesExpanded(!notesExpanded)
              }}
              sx={{
                color: '#FFCC00',
                padding: '4px',
                transition: 'transform 0.2s ease',
                transform: notesExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                '&:hover': {
                  backgroundColor: 'rgba(255, 204, 0, 0.1)',
                },
              }}
            >
              <ExpandMoreIcon />
            </IconButton>
          </Box>
          <Collapse in={notesExpanded}>
            <Box sx={{ mt: 1, ml: 2 }}>
              {block.notes.map((note, noteIndex) => (
                <NoteBlock key={noteIndex} note={note} indent={false} showLabel={false} />
              ))}
            </Box>
          </Collapse>
        </Box>
      )}
      
      {/* Theorems */}
      {block.theorems?.map((theorem, thIndex) => (
        <TheoremBlock key={thIndex} theorem={theorem} />
      ))}
    </Box>
  )
}


import React, { useState } from 'react'
import { Box, Typography, Divider, IconButton, Collapse } from '@mui/material'
import { ExpandMore as ExpandMoreIcon, ExpandLess as ExpandLessIcon } from '@mui/icons-material'
import IntroductionBlock from './IntroductionBlock'
import ConceptBlock from './ConceptBlock'
import ExampleBlock from './ExampleBlock'
import NoteBlock from './NoteBlock'
import SummaryBlock from './SummaryBlock'
import ExerciseBlock from './ExerciseBlock'

/**
 * SectionBlock - 章节组件
 */
export default function SectionBlock({ section }) {
  const [standaloneExamplesExpanded, setStandaloneExamplesExpanded] = useState(false)
  const [standaloneNotesExpanded, setStandaloneNotesExpanded] = useState(false)
  const [exercisesExpanded, setExercisesExpanded] = useState(false)

  if (!section) return null

  const hasStandaloneExamples = section.standalone_examples && section.standalone_examples.length > 0
  const standaloneExamplesCount = section.standalone_examples?.length || 0
  const hasStandaloneNotes = section.standalone_notes && section.standalone_notes.length > 0
  const standaloneNotesCount = section.standalone_notes?.length || 0
  const hasExercises = section.exercises && section.exercises.length > 0
  const exercisesCount = section.exercises?.length || 0

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 600, color: '#1D1D1F' }}>
        {section.section_title}
      </Typography>
      
      {/* Introduction */}
      <IntroductionBlock introduction={section.introduction} />
      
      {/* Concept Blocks */}
      {section.concept_blocks?.map((block, blockIndex) => (
        <ConceptBlock key={blockIndex} block={block} />
      ))}
      
      {/* Standalone Examples - Collapsible */}
      {hasStandaloneExamples && (
        <Box sx={{ mb: 2 }}>
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
              mb: standaloneExamplesExpanded ? 1.5 : 0,
              '&:hover': {
                backgroundColor: '#E0F2FE',
                transform: 'translateX(2px)',
              },
            }}
            onClick={() => setStandaloneExamplesExpanded(!standaloneExamplesExpanded)}
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
                独立例子
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
                {standaloneExamplesCount}
              </Box>
            </Box>
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation()
                setStandaloneExamplesExpanded(!standaloneExamplesExpanded)
              }}
              sx={{
                color: '#34C759',
                padding: '4px',
                transition: 'transform 0.2s ease',
                transform: standaloneExamplesExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                '&:hover': {
                  backgroundColor: 'rgba(52, 199, 89, 0.1)',
                },
              }}
            >
              <ExpandMoreIcon />
            </IconButton>
          </Box>
          <Collapse in={standaloneExamplesExpanded}>
            <Box sx={{ mt: 1, ml: 2 }}>
              {section.standalone_examples.map((example, exIndex) => (
                <ExampleBlock key={exIndex} example={example} showLabel={false} />
              ))}
            </Box>
          </Collapse>
        </Box>
      )}
      
      {/* Standalone Notes - Collapsible */}
      {hasStandaloneNotes && (
        <Box sx={{ mb: 2 }}>
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
              mb: standaloneNotesExpanded ? 1.5 : 0,
              '&:hover': {
                backgroundColor: '#FFF4D6',
                transform: 'translateX(2px)',
              },
            }}
            onClick={() => setStandaloneNotesExpanded(!standaloneNotesExpanded)}
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
                独立注释
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
                {standaloneNotesCount}
              </Box>
            </Box>
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation()
                setStandaloneNotesExpanded(!standaloneNotesExpanded)
              }}
              sx={{
                color: '#FFCC00',
                padding: '4px',
                transition: 'transform 0.2s ease',
                transform: standaloneNotesExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                '&:hover': {
                  backgroundColor: 'rgba(255, 204, 0, 0.1)',
                },
              }}
            >
              <ExpandMoreIcon />
            </IconButton>
          </Box>
          <Collapse in={standaloneNotesExpanded}>
            <Box sx={{ mt: 1, ml: 2 }}>
              {section.standalone_notes.map((note, noteIndex) => (
                <NoteBlock key={noteIndex} note={note} showLabel={false} />
              ))}
            </Box>
          </Collapse>
        </Box>
      )}
      
      {/* Summary */}
      <SummaryBlock summary={section.summary} />
      
      {/* Exercises - Collapsible */}
      {hasExercises && (
        <Box sx={{ mb: 2 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
              backgroundColor: '#FFF3E0',
              padding: '10px 14px',
              borderRadius: '6px',
              borderLeft: '3px solid #FF9800',
              transition: 'all 0.2s ease',
              mb: exercisesExpanded ? 1.5 : 0,
              '&:hover': {
                backgroundColor: '#FFE8CC',
                transform: 'translateX(2px)',
              },
            }}
            onClick={() => setExercisesExpanded(!exercisesExpanded)}
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
                练习题
              </Typography>
              <Box
                sx={{
                  backgroundColor: '#FF9800',
                  color: 'white',
                  borderRadius: '12px',
                  padding: '2px 8px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  minWidth: '24px',
                  textAlign: 'center',
                }}
              >
                {exercisesCount}
              </Box>
            </Box>
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation()
                setExercisesExpanded(!exercisesExpanded)
              }}
              sx={{
                color: '#FF9800',
                padding: '4px',
                transition: 'transform 0.2s ease',
                transform: exercisesExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                '&:hover': {
                  backgroundColor: 'rgba(255, 152, 0, 0.1)',
                },
              }}
            >
              <ExpandMoreIcon />
            </IconButton>
          </Box>
          <Collapse in={exercisesExpanded}>
            <Box sx={{ mt: 1 }}>
              {section.exercises.map((exercise, exIndex) => (
                <ExerciseBlock key={exIndex} exercise={exercise} />
              ))}
            </Box>
          </Collapse>
        </Box>
      )}
      
      <Divider sx={{ my: 3 }} />
    </Box>
  )
}


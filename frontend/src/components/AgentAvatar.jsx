import React from 'react'
import { Avatar } from '@mui/material'

/**
 * Agent Avatar组件
 * 使用DiceBear Pixel Art风格生成avatar
 * 
 * @param {string} seed - Avatar种子（用于生成唯一avatar）
 * @param {number} size - Avatar大小（默认40px）
 */
function AgentAvatar({ seed, size = 40, ...props }) {
  const avatarUrl = seed 
    ? `https://api.dicebear.com/9.x/pixel-art/svg?seed=${encodeURIComponent(seed)}`
    : null

  return (
    <Avatar
      src={avatarUrl}
      sx={{ 
        width: size, 
        height: size,
        bgcolor: 'primary.main',
        ...props.sx
      }}
      {...props}
    >
      {!seed && 'A'}
    </Avatar>
  )
}

export default AgentAvatar


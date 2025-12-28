# 前端代码重构计划

## 问题分析

当前前端代码存在以下问题：
1. **文件过大**：多个页面文件超过1000行，ChatPage.jsx达到2708行
2. **缺乏模块化**：大量逻辑和UI混在一起
3. **代码重复**：Markdown渲染、消息解析等逻辑在多处重复
4. **难以维护**：大文件难以理解和修改

## 重构策略

### 1. 目录结构重组

```
frontend/src/
├── components/
│   ├── chat/              # 聊天相关组件（新增）
│   │   ├── SessionSidebar.jsx
│   │   ├── MessageList.jsx
│   │   ├── MessageItem.jsx
│   │   ├── ChatInput.jsx
│   │   ├── FileViewer.jsx
│   │   └── MarkdownRenderer.jsx
│   └── ... (其他组件)
├── hooks/                 # 自定义Hooks（新增）
│   ├── useSession.js
│   ├── useImageUpload.js
│   ├── useFileUpload.js
│   └── useChat.js
├── utils/                 # 工具函数（新增）
│   ├── dateFormatter.js
│   ├── imageUtils.js
│   └── messageParser.js
└── pages/
    └── ChatPage.jsx       # 重构后的页面，只负责组合组件
```

### 2. 已完成的提取

✅ **工具函数**
- `utils/dateFormatter.js` - 日期格式化
- `utils/imageUtils.js` - 图片处理
- `utils/messageParser.js` - 消息解析

✅ **自定义Hooks**
- `hooks/useSession.js` - 会话管理
- `hooks/useImageUpload.js` - 图片上传

✅ **组件**
- `components/chat/MarkdownRenderer.jsx` - Markdown渲染
- `components/chat/FileViewer.jsx` - 文件查看器
- `components/chat/SessionSidebar.jsx` - 会话侧边栏

### 3. 待完成的提取

#### 组件提取
- [ ] `MessageItem.jsx` - 单个消息项（包含结构化数据渲染）
- [ ] `MessageList.jsx` - 消息列表容器
- [ ] `ChatInput.jsx` - 聊天输入框（包含附件上传）

#### Hooks提取
- [ ] `useFileUpload.js` - 文件上传逻辑
- [ ] `useChat.js` - 聊天核心逻辑（发送消息、处理响应等）

### 4. 重构步骤

#### 阶段1：提取基础组件和工具（已完成）
- ✅ 创建目录结构
- ✅ 提取工具函数
- ✅ 提取基础hooks
- ✅ 创建基础组件

#### 阶段2：提取复杂组件（进行中）
- [ ] 提取MessageItem组件
- [ ] 提取ChatInput组件
- [ ] 提取MessageList组件

#### 阶段3：重构ChatPage
- [ ] 使用新的hooks替换原有逻辑
- [ ] 使用新的组件替换原有UI
- [ ] 简化ChatPage为组合层

#### 阶段4：重构其他页面
- [ ] 重构AgentDetailPage.jsx
- [ ] 重构SourceChatPage.jsx（与ChatPage共享组件）
- [ ] 重构其他大文件

## 使用示例

### 重构后的ChatPage结构

```jsx
import React, { useState } from 'react'
import { Box } from '@mui/material'
import { useTheme } from '../contexts/ThemeContext'
import { useSession } from '../hooks/useSession'
import { useImageUpload } from '../hooks/useImageUpload'
import SessionSidebar from '../components/chat/SessionSidebar'
import MessageList from '../components/chat/MessageList'
import ChatInput from '../components/chat/ChatInput'
import FileViewer from '../components/chat/FileViewer'

function ChatPage() {
  const theme = useTheme()
  const session = useSession()
  const imageUpload = useImageUpload()
  // ... 其他状态和逻辑

  return (
    <Box>
      <SessionSidebar {...session} />
      <Box>
        <MessageList messages={messages} />
        <ChatInput {...chatInputProps} />
      </Box>
      <FileViewer {...fileViewerProps} />
    </Box>
  )
}
```

## 优势

1. **可维护性**：每个组件职责单一，易于理解和修改
2. **可重用性**：组件和hooks可在多个页面复用
3. **可测试性**：独立的组件和hooks更容易编写单元测试
4. **代码组织**：清晰的文件结构，易于导航

## 注意事项

- 重构时保持功能不变
- 逐步重构，避免一次性大改
- 确保向后兼容
- 保持代码风格一致


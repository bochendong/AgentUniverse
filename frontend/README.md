# New Frontend

新的前端应用，具有以下特性：

- **Chat页面（OpenAI风格）**：用户与TopLevelAgent聊天的界面，采用OpenAI ChatGPT的UI设计
- **Agents列表页面（苹果风格）**：显示所有agents，每个agent是一个neon edge card
- **Agent详情页面（苹果风格）**：
  - Notebook Agent：显示笔记内容
  - Top/Master Agent：显示层级关系

## 安装和运行

```bash
# 安装依赖
npm install

# 启动开发服务器（端口3001）
npm run dev

# 构建生产版本
npm run build
```

## 技术栈

- React 18
- Material-UI (MUI)
- React Router
- Axios
- React Markdown
- Vite

## 页面说明

### Chat页面 (`/`)
- OpenAI风格的聊天界面
- 支持会话管理（创建、选择、删除）
- 支持Markdown渲染和代码高亮
- 支持数学公式（KaTeX）

### Agents列表页面 (`/agents`)
- 苹果风格的设计
- Neon edge cards展示每个agent
- 根据agent类型显示不同颜色：
  - Top Level Agent: 红色
  - Master Agent: 青色
  - Notebook Agent: 绿色

### Agent详情页面 (`/agents/:agentId`)
- 根据agent类型显示不同内容：
  - **Notebook Agent**: 显示笔记内容
  - **Top/Master Agent**: 显示层级关系（子agents列表）

## 设计风格

- **Chat页面**：采用OpenAI ChatGPT的深色主题设计
- **其他页面**：采用苹果风格的浅色主题设计，包括：
  - 圆角卡片
  - 柔和的阴影
  - 流畅的动画过渡
  - 清晰的层次结构


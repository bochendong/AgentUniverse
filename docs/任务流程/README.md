# 任务流程文档

本文档详细描述了 AgentUniverse 系统中每个任务的触发流程，包括：
- **By Tool**：通过函数工具（Function Tool）触发
- **By Agent**：通过 Agent 转发触发
- **Agent as Tool**：通过 Agent 作为工具（Agent as Tool）触发

## 📚 目录

### 1. [笔记本创建流程](./01-笔记本创建流程.md)
- 从文件创建笔记本
- 从主题创建笔记本（从零生成）
- 大纲生成与确认
- 章节内容生成

### 2. [内容修改流程](./02-内容修改流程.md)
- 通过 ID 修改内容
- 添加新内容
- 删除内容
- 使用修改器 Agent 生成新内容

### 3. [内容优化流程](./03-内容优化流程.md)
- 练习题优化
- 证明优化
- 内容完整性检查

### 4. [大纲修订流程](./04-大纲修订流程.md)
- 大纲修改
- 章节添加/删除
- 章节顺序调整

### 5. [Agent 间通信流程](./05-Agent间通信流程.md)
- TopLevelAgent → MasterAgent
- MasterAgent → NotebookAgent
- 任务分发机制

### 6. [工具类型说明](./06-工具类型说明.md)
- Function Tool（函数工具）
- Agent as Tool（代理作为工具）
- Agent 转发（Agent Communication）

### 7. [设计问题与重构方案](./07-设计问题与重构方案.md)
- 当前设计问题分析
- 统一的重构方案
- 重构步骤和注意事项

### 8. [内容优化重构方案](./08-内容优化重构方案.md)
- RefinementAgent 和 ModifyAgent 逻辑重复问题
- 评估与修改分离的新架构
- 统一使用 Modify Tools 的方案

### 9. [Prompt 片段重构指南](./09-Prompt片段重构指南.md)
- Prompt 重复问题分析
- 公共 prompt 片段的使用方法
- 重构步骤和最佳实践

### 10. [Prompt 重构完成总结](./10-Prompt重构完成总结.md)
- 已完成的重构工作
- 重构效果和对比
- 后续工作建议

## 🏗️ 系统架构概览

```
TopLevelAgent (顶层入口)
    ↓ (通过工具/转发)
MasterAgent (中间协调者)
    ↓ (通过工具/转发)
NotebookAgent (笔记本管理者)
    ↓ (通过工具/Agent as Tool)
Specialized Agents (专业化代理)
```

## 🔄 触发方式对比

| 触发方式 | 使用场景 | 示例 |
|---------|---------|------|
| **By Tool** | 直接操作，简单任务 | `modify_by_id`, `get_content_by_id` |
| **By Agent** | 任务分发，复杂协调 | `send_message` 转发给子 Agent |
| **Agent as Tool** | 需要 AI 推理的复杂任务 | `outline_maker_agent`, `exercise_refinement_agent` |

## 📖 阅读指南

1. **新用户**：建议先阅读 [工具类型说明](./06-工具类型说明.md) 了解基本概念
2. **开发者**：按需查看具体任务的流程文档
3. **调试问题**：查看对应任务的流程图，了解完整的调用链


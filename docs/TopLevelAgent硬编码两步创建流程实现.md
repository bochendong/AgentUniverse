# TopLevelAgent 硬编码两步创建流程实现

## 概述

实现了理想状态下的 notebook 创建流程：
1. **用户上传文件** → TopLevelAgent 生成大纲 → 回复用户
2. **用户通过自然语言确认大纲** → TopLevelAgent 发送大纲和文件路径给 MasterAgent → MasterAgent 创建 notebook

## 实现的功能

### 1. 修改 `handle_file_upload` 工具 (`backend/tools/agent_tools.py`)

**修改前**：
- 验证文件后，发送消息给 MasterAgent，要求其调用 `create_notebook` 工具

**修改后**：
- 验证文件后，直接调用 `outline_maker_agent` 生成大纲
- 返回格式化的 outline 信息供用户确认
- TopLevelAgent 直接与用户交互，不需要通过 MasterAgent

**关键代码**：
```python
# 创建 outline_maker_agent 工具
outline_tool = registry.create_tool(
    "outline_maker_agent",
    agent=top_level_agent,
    file_path=stored_path
)

# 调用 outline_maker_agent 生成大纲
outline_result = await Runner.run(
    outline_tool._agent_instance,
    "请分析文档并生成学习大纲..."
)

# 返回格式化的 outline 信息
```

### 2. 添加 `create_notebook_from_outline` 工具 (`backend/tools/agent_tools.py`)

**功能**：
- TopLevelAgent 用于处理用户确认的大纲
- 将确认的大纲、文件路径和用户请求发送给 MasterAgent
- 直接调用 MasterAgent 的 `create_notebook_with_outline` 工具

**输入参数**：
- `outline`: 确认的大纲对象（字典格式）
- `file_path`: 文件路径
- `user_request`: 用户的原始请求内容

### 3. 添加 `create_notebook_with_outline` 工具 (`backend/tools/agent_tools.py`)

**功能**：
- MasterAgent 用于接收确认的大纲并创建完整的 notebook
- 硬编码流程：
  1. 调用 `notebook_agent_creator` 生成内容
  2. 创建 `NoteBookAgent` 实例
  3. 添加到 MasterAgent 的子 agents 列表

**关键代码**：
```python
# 创建 notebook_agent_creator 工具
notebook_creator_tool = registry.create_tool(
    "notebook_agent_creator",
    agent=master_agent,
    outline=outline_obj,
    file_path=file_path
)

# 运行 agent 生成所有章节
creator_result = await Runner.run(
    creator_agent,
    f"请根据大纲生成完整的notebook内容..."
)

# 从 agent 实例中获取生成的 sections
sections = creator_agent.sections

# 创建 NoteBookAgent 实例
new_notebook = NoteBookAgent(
    outline=outline_obj,
    sections=sections,
    notebook_title=outline_obj.notebook_title,
    parent_agent_id=master_agent.id,
    DB_PATH=master_agent.DB_PATH
)
```

### 4. 更新 Agent 工具列表

**TopLevelAgent** (`backend/agent/TopLevelAgent.py`):
- 添加了 `create_notebook_from_outline` 工具
- 工具列表：`['send_message', 'handle_file_upload', 'create_notebook_from_outline']`

**MasterAgent** (`backend/agent/MasterAgent.py`):
- 添加了 `create_notebook_with_outline` 工具
- 工具列表：`['send_message', 'add_notebook_by_file', 'create_notebook', 'create_notebook_with_outline']`

### 5. 更新 Prompt 文件 (`backend/prompts/top_level_agent.md`)

- 更新了文件上传处理说明
- 添加了硬编码两步流程的详细说明
- 更新了工作流程示例

## 完整流程

### 第一步：生成大纲
1. 用户上传文件："上传这个文件并创建笔记本" + 文件路径
2. TopLevelAgent 调用 `handle_file_upload(file_path, user_request)`
3. 工具内部：
   - 验证文件存在性
   - 调用 `outline_maker_agent` 生成大纲
   - 格式化大纲信息
4. TopLevelAgent 返回大纲给用户："📋 **大纲已生成，请确认：**..."

### 第二步：用户确认并创建
1. 用户通过自然语言确认："确认"、"可以"、"开始创建"等
2. TopLevelAgent 识别确认意图，提取大纲数据
3. TopLevelAgent 调用 `create_notebook_from_outline(outline, file_path, user_request)`
4. 工具内部：
   - 加载 MasterAgent
   - 直接调用 MasterAgent 的 `create_notebook_with_outline` 工具
5. MasterAgent 的 `create_notebook_with_outline` 工具：
   - 调用 `notebook_agent_creator` 生成内容
   - 创建 `NoteBookAgent` 实例
   - 添加到 MasterAgent 的子 agents 列表
6. TopLevelAgent 返回创建结果给用户

## 优势

1. **流程清晰**：TopLevelAgent 直接与用户交互，流程更直观
2. **职责分离**：
   - TopLevelAgent：处理用户交互、生成大纲
   - MasterAgent：创建和管理 notebook
3. **硬编码流程**：两步流程明确，易于维护和调试
4. **自然语言确认**：用户可以通过自然语言确认大纲，体验更好

## 注意事项

1. **大纲数据提取**：TopLevelAgent 需要能够从对话历史中提取 outline JSON 和文件路径
2. **确认意图识别**：需要识别用户的确认意图（"确认"、"可以"、"开始创建"等）
3. **错误处理**：每个步骤都有详细的错误处理和日志

## 相关文件

- `backend/tools/agent_tools.py` - 工具定义
- `backend/agent/TopLevelAgent.py` - TopLevelAgent 实现
- `backend/agent/MasterAgent.py` - MasterAgent 实现
- `backend/prompts/top_level_agent.md` - TopLevelAgent prompt
- `backend/utils/default_instructions.py` - 默认工具列表


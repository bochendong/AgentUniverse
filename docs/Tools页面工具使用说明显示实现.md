# Tools 页面工具使用说明显示实现

## 概述

在 Tools 页面（`ToolsPage`）中添加了工具使用说明的显示功能，用户可以在查看工具列表时看到每个工具的详细使用说明。

## 实现的功能

### 1. 后端 API 增强 (`backend/main.py`)

修改了 `/api/tools` 端点，为每个工具添加 `usage_documentation` 字段：

```python
@app.get("/api/tools")
async def list_tools():
    """List all tools."""
    from backend.tools.tool_registry import get_tool_registry
    from backend.tools.tool_usage_generator import format_tool_usage
    
    tools = get_all_tools()
    registry = get_tool_registry()
    
    # Add usage documentation for each tool
    for tool in tools:
        tool_id = tool.get('id')
        if tool_id:
            metadata = registry.get_tool_metadata(tool_id)
            if metadata:
                usage_doc = format_tool_usage(metadata, 1)
                tool['usage_documentation'] = usage_doc
```

### 2. 工具使用说明生成器更新 (`backend/tools/tool_usage_generator.py`)

将 `_format_tool_usage` 函数改为公共函数 `format_tool_usage`，以便在 API 中使用：

```python
def format_tool_usage(metadata: ToolMetadata, index: int = 1) -> str:
    """Format a single tool's usage documentation."""
    # 生成格式化的 Markdown 使用说明
    # 包括：工具名称、描述、用途、调用方法、输入参数、输出类型等
```

### 3. 前端 ToolCard 组件更新 (`frontend/src/components/ToolCard.jsx`)

添加了可展开的"使用说明"部分：

- **导入依赖**：
  - `ReactMarkdown` 和 `remarkGfm` 用于渲染 Markdown
  - `Collapse` 组件用于展开/收起动画
  - `ExpandMoreIcon` 和 `ExpandLessIcon` 用于展开/收起按钮

- **新增功能**：
  - 添加了 `usageExpanded` 状态来控制展开/收起
  - 添加了"使用说明"按钮，点击可展开/收起使用说明
  - 使用 `ReactMarkdown` 渲染格式化的使用说明
  - 自定义样式使 Markdown 内容美观易读

## 显示内容

工具使用说明包含以下信息：

1. **工具名称**：`### {index}. {name} 工具`
2. **描述**：工具的简要描述
3. **用途**：工具的任务和用途说明
4. **调用方法**：格式化的 Python 函数签名（代码块格式）
5. **输入参数**：每个参数的名称、类型、是否必需、描述
6. **输出类型**：返回值的类型
7. **输出说明**：返回值的详细说明
8. **特殊说明**：对于 Agent as Tool 类型，会显示特殊注意事项

## 用户体验

1. **默认收起**：使用说明默认是收起的，保持卡片简洁
2. **一键展开**：点击"使用说明"按钮即可展开查看详细内容
3. **格式美观**：使用 Markdown 渲染，代码块、列表等格式清晰
4. **响应式设计**：适配不同屏幕尺寸

## 使用示例

### 后端返回的数据格式

```json
{
  "tools": [
    {
      "id": "send_message",
      "name": "send_message",
      "description": "向指定ID的agent发送消息",
      "task": "用于agent之间的通信",
      "usage_documentation": "### 1. send_message 工具\n向指定ID的agent发送消息\n\n**用途**：用于agent之间的通信...",
      ...
    }
  ]
}
```

### 前端显示效果

- 工具卡片显示基本信息（名称、描述、调用方法、输入输出等）
- 点击"使用说明"按钮展开详细的使用文档
- 使用说明以 Markdown 格式渲染，包含代码块、列表等

## 优势

1. **信息完整**：用户可以在 Tools 页面直接查看工具的完整使用说明
2. **格式统一**：使用说明格式与 Agent Instructions 中的格式一致
3. **易于维护**：使用说明从工具元数据自动生成，无需手动维护
4. **用户体验好**：可展开/收起设计，既保持页面简洁，又提供详细信息

## 相关文件

- `backend/main.py` - API 端点修改
- `backend/tools/tool_usage_generator.py` - 使用说明生成器
- `frontend/src/components/ToolCard.jsx` - 工具卡片组件
- `frontend/src/pages/ToolsPage.jsx` - Tools 页面

## 注意事项

1. 确保工具元数据完整：工具必须正确注册并包含完整的元数据
2. 前端依赖：确保 `react-markdown` 和 `remark-gfm` 已安装
3. 性能考虑：如果工具数量很多，可以考虑按需加载使用说明


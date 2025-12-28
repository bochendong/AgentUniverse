# 大纲确认问题修复

## 问题描述

用户点击"确认并创建"后，系统提示"Failed to confirm outline"错误。

## 问题分析

用户确认大纲后，前端发送的消息格式为：
```
确认创建笔记本。

**大纲信息（JSON格式）：**
\`\`\`json
${outlineJson}
\`\`\`

**文件路径：**
${file_path}

请根据此大纲创建笔记本。
```

TopLevelAgent需要：
1. 从消息中提取JSON代码块中的大纲
2. 提取文件路径
3. 使用`send_message`将格式化的JSON消息发送给MasterAgent
4. MasterAgent识别`action: "create_notebook"`并调用`create_notebook`工具

## 解决方案

### 1. 更新TopLevelAgent Prompt

更新了`backend/prompts/top_level_agent.md`，更清楚地指示如何从确认消息中提取信息：

- 明确说明如何从JSON代码块（\`\`\`json ... \`\`\`）中提取大纲
- 明确说明如何从"文件路径："后提取路径
- 提供了详细的示例说明如何调用`send_message`

### 2. 文件路径解析（已修复）

之前已经修复了文件路径解析问题（见BUGFIX_FILE_PATH.md），`create_notebook`工具现在能正确处理相对路径和仅文件名的情况。

## 修改的文件

1. **backend/prompts/top_level_agent.md**
   - 更新了"用户确认后"部分的说明
   - 添加了详细的JSON提取步骤和示例

## 测试建议

1. 上传文件并生成大纲
2. 查看大纲内容
3. 点击"确认并创建"
4. 检查是否成功创建笔记本

如果仍然失败，请检查：
- 后端日志中的错误信息
- TopLevelAgent是否正确提取了JSON
- MasterAgent是否识别了`action: "create_notebook"`
- `create_notebook`工具执行时的错误信息

## 注意事项

1. TopLevelAgent需要通过`send_message`转发给MasterAgent，不能直接调用`create_notebook`（因为该工具只注册在MasterAgent上）
2. 消息格式必须是JSON字符串，包含`action`、`outline`、`file_path`和`user_request`字段
3. 文件路径会被`create_notebook`工具自动解析（支持绝对路径、相对路径和仅文件名）


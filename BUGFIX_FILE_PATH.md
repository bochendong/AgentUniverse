# 文件路径解析问题修复

## 问题描述

用户报告无法生成大纲，错误信息：
```
FileNotFoundError: 文件不存在: 81eacb69_Python.md
```

## 问题分析

1. **文件确实存在**：`uploads/81eacb69_Python.md` 文件确实存在于服务器上
2. **问题原因**：`get_file_content` 函数只能处理绝对路径或相对于当前工作目录的路径
3. **实际情况**：当 Agent 调用 `generate_outline` 工具时，传递的 `file_path` 参数可能是：
   - 相对路径（如 `uploads/81eacb69_Python.md`）
   - 仅文件名（如 `81eacb69_Python.md`）
   - 绝对路径（如 `/Users/.../uploads/81eacb69_Python.md`）

## 解决方案

在 `backend/tools/agent_as_tools/section_creators/utils.py` 中添加了 `_resolve_file_path` 函数，用于智能解析文件路径：

1. **处理绝对路径**：如果路径是绝对路径且文件存在，直接返回
2. **处理相对路径**：如果路径存在（相对于当前工作目录），转换为绝对路径
3. **处理仅文件名**：
   - 首先尝试在当前工作目录查找
   - 然后尝试在项目根目录查找
   - 最后尝试在 `uploads/` 目录查找（这是最常见的情况）

## 修改内容

### 新增函数
- `_resolve_file_path(file_path: str) -> str`：智能解析文件路径

### 修改函数
- `get_file_content(file_path: str) -> str`：使用 `_resolve_file_path` 解析路径
- `detect_file_type(file_path: Optional[str])`：同样支持路径解析

## 测试

路径解析逻辑已通过验证：
- ✅ 绝对路径处理
- ✅ 相对路径处理  
- ✅ 仅文件名处理（在 uploads/ 目录查找）

## 修改的文件

1. **backend/tools/agent_as_tools/section_creators/utils.py**
   - 新增 `_resolve_file_path` 函数：智能解析文件路径
   - 更新 `get_file_content` 函数：使用路径解析
   - 更新 `detect_file_type` 函数：支持路径解析

2. **backend/tools/utils/pdf_processor.py**
   - 更新 `extract_pdf_content` 函数：使用路径解析

3. **backend/api/upload.py**
   - 更新 `get_file_content_endpoint` API：使用路径解析

4. **backend/api/top_level_agent.py**
   - 更新 `source_chat_with_top_level_agent` 函数：PDF和非PDF文件读取都使用路径解析

## 影响范围

此修复影响所有文件读取相关的功能，包括：
- 文件上传后的内容读取
- 大纲生成
- 笔记本创建
- 文件查看功能
- PDF文件处理

## 注意事项

1. 路径解析会按顺序尝试多个位置，确保兼容性
2. 如果所有尝试都失败，会返回原始路径，让调用者处理错误（保持向后兼容）
3. 错误信息中包含原始路径和解析后的路径，便于调试


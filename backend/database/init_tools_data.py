"""Initialize tools database with default tools data."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database.tools_db import init_tools_db, save_tool


def init_default_tools():
    """Initialize database with default tools."""
    init_tools_db()
    
    # Define all tools with their metadata
    tools = [
        {
            'id': 'send_message',
            'name': 'send_message',
            'description': '向指定ID的agent发送消息',
            'task': '用于agent之间的通信，允许一个agent向另一个agent发送消息并获取响应',
            'agent_type': 'BaseAgent',
            'input_params': {
                'id': {'type': 'str', 'description': 'Agent ID', 'required': True},
                'message': {'type': 'str', 'description': '要发送的消息', 'required': True},
            },
            'output_type': 'str',
            'output_description': '返回目标agent处理消息后的完整响应文本。如果agent执行成功，返回agent的执行结果；如果加载agent失败，返回"Error: Failed to load agent with ID {id} from database"；如果执行过程中出现异常，返回"Error sending message: {error_message}"',
        },
        {
            'id': 'add_notebook_by_file',
            'name': 'add_notebook_by_file',
            'description': '根据文件路径，添加一个新的notebook agent（向后兼容版本）',
            'task': '从文件创建notebook agent并添加到MasterAgent的子agents列表中。此工具会自动检测用户意图并选择合适的创建策略。',
            'agent_type': 'MasterAgent',
            'input_params': {
                'file_path': {'type': 'str', 'description': '文件路径（支持 .docx, .md, .txt）', 'required': True},
            },
            'output_type': 'str',
            'output_description': '返回操作结果字符串。成功时返回包含成功信息的消息（如"成功创建notebook agent..."）；失败时返回错误信息（如"创建notebook失败: {error_message}"或"执行失败: {error_message}"）。该工具会自动检测文件内容，选择合适的创建策略（Full Content、Enhancement、Knowledge Base、Outline First）',
        },
        {
            'id': 'create_notebook',
            'name': 'create_notebook',
            'description': '根据用户请求创建notebook agent（支持多种场景）',
            'task': '灵活的工具，支持从文件或主题创建notebook。会自动分析用户意图，选择合适的创建策略。如果是outline_first场景，会先生成大纲供用户确认。',
            'agent_type': 'MasterAgent',
            'input_params': {
                'user_request': {'type': 'str', 'description': '用户的请求内容', 'required': True},
                'file_path': {'type': 'str', 'description': '文件路径（可选，支持 .docx, .md, .txt）', 'required': False},
            },
            'output_type': 'str',
            'output_description': '返回包含大纲信息的markdown格式字符串。格式为："📋 **大纲已生成，请确认：**\n\n{大纲的markdown展示}\n\n**大纲数据（JSON格式，供系统使用）：**\n```json\n{JSON格式的大纲数据}\n```\n\n请确认此大纲是否符合您的需求..."。JSON数据包含notebook_title（字符串）、notebook_description（字符串）和outlines（字典，键值都是字符串）。该输出用于前端展示和用户确认，确认后系统会继续生成完整笔记本内容',
        },
        {
            'id': 'handle_file_upload',
            'name': 'handle_file_upload',
            'description': '处理文件上传：验证文件并发送消息给MasterAgent创建notebook',
            'task': 'TopLevelAgent用于处理用户上传的文件。验证文件存在性，然后向MasterAgent发送消息，要求其调用create_notebook工具来生成大纲供用户确认。',
            'agent_type': 'TopLevelAgent',
            'input_params': {
                'file_path': {'type': 'str', 'description': '上传的文件路径（可能是原始路径或已保存的路径）', 'required': True},
                'user_request': {'type': 'str', 'description': '用户的原始请求内容', 'required': True},
            },
            'output_type': 'str',
            'output_description': '返回MasterAgent执行create_notebook工具后的完整输出字符串。通常是包含大纲信息的markdown格式文本（格式与create_notebook的输出相同），用于前端展示给用户确认。如果文件不存在或处理失败，返回错误信息（如"错误: 文件不存在: {file_path}"或"处理文件上传失败: {error_message}"）',
        },
        {
            'id': 'modify_notes',
            'name': 'modify_notes',
            'description': '修改笔记内容',
            'task': 'NoteBookAgent用于更新其笔记内容，并自动更新instructions以反映新的笔记内容。如果笔记过大，会提示建议拆分。',
            'agent_type': 'NoteBookAgent',
            'input_params': {
                'new_notes': {'type': 'str', 'description': '新的笔记内容', 'required': True},
            },
            'output_type': 'str',
            'output_description': '返回操作结果字符串。正常情况下返回"笔记已更新"。如果检测到笔记需要拆分（章节数>10或字数>3000），返回"笔记已更新。⚠️ 建议拆分：章节数={sections_count}，字数={word_count}（超过限制：章节>10 或 字数>3000）"，提示用户考虑拆分笔记。该工具会自动更新agent的instructions以反映新的笔记内容',
        },
    ]
    
    # Save all tools
    for tool in tools:
        save_tool(
            tool_id=tool['id'],
            name=tool['name'],
            description=tool['description'],
            task=tool['task'],
            agent_type=tool['agent_type'],
            input_params=tool['input_params'],
            output_type=tool['output_type'],
            output_description=tool.get('output_description'),
        )
        print(f"Saved tool: {tool['name']}")
    
    print(f"Successfully initialized {len(tools)} tools")


if __name__ == '__main__':
    init_default_tools()


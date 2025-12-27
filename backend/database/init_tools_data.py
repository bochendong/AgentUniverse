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
            'id': 'create_notebook',
            'name': 'create_notebook',
            'description': '根据确认的大纲创建notebook agent',
            'task': 'MasterAgent用于接收确认的大纲并创建完整的notebook。使用NotebookCreationRouter内部判断意图并选择策略，创建所有章节内容，然后创建NotebookAgent实例。',
            'agent_type': 'MasterAgent',
            'input_params': {
                'outline': {'type': 'str', 'description': '确认的大纲对象（JSON字符串格式，包含notebook_title、notebook_description和outlines字典）', 'required': True},
                'file_path': {'type': 'str', 'description': '文件路径（可选，有文件时提供）', 'required': False},
                'user_request': {'type': 'str', 'description': '用户的原始请求内容', 'required': True},
            },
            'output_type': 'str',
            'output_description': '返回创建结果字符串。成功时返回notebook信息（ID、标题等），失败时返回错误信息。',
        },
        {
            'id': 'generate_outline',
            'name': 'generate_outline',
            'description': '生成学习大纲供用户确认（统一工具）',
            'task': 'TopLevelAgent用于处理用户创建笔记本的请求。根据用户请求的主题，生成学习大纲供用户确认。如果提供了file_path，则从文件生成大纲；否则从主题生成大纲。',
            'agent_type': 'TopLevelAgent',
            'input_params': {
                'user_request': {'type': 'str', 'description': '用户的请求内容', 'required': True},
                'file_path': {'type': 'str', 'description': '文件路径（可选，如果有文件则提供）', 'required': False},
            },
            'output_type': 'str',
            'output_description': '返回包含大纲信息的markdown格式字符串。格式包含大纲的markdown展示和JSON格式的大纲数据。该输出用于前端展示给用户确认。',
        },
        # DEPRECATED: modify_notes tool has been removed - use add_content_to_section or modify_by_id instead
        # {
        #     'id': 'modify_notes',
        #     'name': 'modify_notes',
        #     'description': '修改笔记内容',
        #     'task': 'NoteBookAgent用于更新其笔记内容，并自动更新instructions以反映新的笔记内容。如果笔记过大，会提示建议拆分。',
        #     'agent_type': 'NoteBookAgent',
        #     'input_params': {
        #         'new_notes': {'type': 'str', 'description': '新的笔记内容', 'required': True},
        #     },
        #     'output_type': 'str',
        #     'output_description': '返回操作结果字符串。正常情况下返回"笔记已更新"。如果检测到笔记需要拆分（章节数>10或字数>10000），返回"笔记已更新。⚠️ 建议拆分：章节数={sections_count}，字数={word_count}（超过限制：章节>10 或 字数>10000）"，提示用户考虑拆分笔记。该工具会自动更新agent的instructions以反映新的笔记内容',
        # },
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


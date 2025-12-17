"""Agent function tools - tools that agents can use."""

from typing import TYPE_CHECKING
from agents import function_tool

if TYPE_CHECKING:
    from backend.agent.BaseAgent import BaseAgent
    from backend.agent.MasterAgent import MasterAgent


def create_send_message_tool(agent: 'BaseAgent'):
    """
    Create a send_message tool function for communicating with sub-agents.
    
    Args:
        agent: The agent instance that will use this tool
        
    Returns:
        A function_tool decorated function for sending messages
    """
    @function_tool
    def send_message(id: str, message: str) -> str:
        """向指定ID的agent发送消息
        
        Args:
            id: Agent ID
            message: Message to send
            
        Returns:
            Response from the agent
        """
        # Load agent from database
        target_agent = agent.load_agent_from_db_by_id(id)
        if target_agent is None:
            return f"Error: Failed to load agent with ID {id} from database"
        
        try:
            output = agent.run_async_safely(target_agent.receive_messgae(message))
            return str(output)
        except Exception as e:
            return f"Error sending message: {str(e)}"
    
    return send_message


def create_add_notebook_by_file_tool(master_agent: 'MasterAgent'):
    """
    Create an add_notebook_by_file tool function for MasterAgent.
    
    Args:
        master_agent: The MasterAgent instance that will use this tool
        
    Returns:
        A function_tool decorated function for adding notebook by file
    """
    @function_tool
    def add_notebook_by_file(file_path: str) -> str:
        """根据文件路径，添加一个新的notebook agent
        
        Args:
            file_path: 文件路径（支持 .docx, .md, .txt）
        
        Returns:
            操作结果信息
        """
        from backend.tools.notebook_creator_tool import create_notebook_agent_from_file
        
        async def _create_and_add_notebook():
            """内部异步函数，创建notebook并添加到sub-agents"""
            try:
                new_notebook, success_message = await create_notebook_agent_from_file(
                    file_path=file_path,
                    parent_agent_id=master_agent.id,
                    DB_PATH=master_agent.DB_PATH
                )
                new_notebook.save_to_db()
                
                master_agent._add_sub_agents(new_notebook.id)
                
                return success_message
                
            except Exception as e:
                return f"创建notebook失败: {str(e)}"
        
        # 执行异步函数
        try:
            result = master_agent.run_async_safely(_create_and_add_notebook())
            return result
        except Exception as e:
            return f"执行失败: {str(e)}"
    
    return add_notebook_by_file


def create_handle_file_upload_tool(top_level_agent: 'BaseAgent'):
    """
    Create a handle_file_upload tool function for TopLevelAgent.
    
    Args:
        top_level_agent: The TopLevelAgent instance that will use this tool
        
    Returns:
        A function_tool decorated function for handling file uploads
    """
    from backend.agent.MasterAgent import MasterAgent
    from backend.tools.file_storage import save_uploaded_file
    
    @function_tool
    def handle_file_upload(file_path: str, user_request: str) -> str:
        """处理文件上传：验证文件并发送消息给MasterAgent创建notebook
        
        Args:
            file_path: 上传的文件路径（可能是原始路径或已保存的路径）
            user_request: 用户的原始请求内容
        
        Returns:
            操作结果信息
        """
        import os
        
        try:
            # 确保使用绝对路径
            if not os.path.isabs(file_path):
                stored_path = os.path.abspath(file_path)
            else:
                stored_path = file_path
            
            # 验证文件存在
            if not os.path.exists(stored_path):
                return f"错误: 文件不存在: {stored_path}"
            
            # 如果文件不在 uploads 目录，需要保存（通常前端已经上传了，但为了安全起见检查一下）
            if "uploads" not in stored_path:
                # 文件不在 uploads 目录，保存它
                stored_path = save_uploaded_file(stored_path)
            
            file_name = os.path.basename(stored_path)
            
            # 获取MasterAgent ID（从sub_agent_ids中查找）
            master_agent_id = None
            # 确保 sub_agent_ids 不是 None
            sub_agent_ids = getattr(top_level_agent, 'sub_agent_ids', None) or []
            for agent_id in sub_agent_ids:
                agent = top_level_agent.load_agent_from_db_by_id(agent_id)
                if agent and isinstance(agent, MasterAgent):
                    master_agent_id = agent_id
                    break
            
            if not master_agent_id:
                return "错误: 未找到MasterAgent"
            
            # 构建发送给MasterAgent的消息
            # 使用强制性的指令格式，确保 MasterAgent 必须调用工具
            message_to_master = f"""【文件上传任务 - 必须执行工具调用】

                                用户请求: {user_request}

                                文件信息：
                                - 文件路径: {stored_path}
                                - 文件名: {file_name}

                                【重要指令】
                                你当前没有合适的子 Agent 可以处理此文件。
                                你必须立即调用 add_notebook_by_file 工具创建notebook。
                                不要只回复"我会创建"或"我将处理"，你必须实际调用工具并返回工具的执行结果。

                                立即执行：add_notebook_by_file(file_path="{stored_path}")

                                ⚠️ 注意：此指令要求你实际执行工具调用，不是描述你会做什么。"""
            
            # 使用 send_message 工具发送消息给 MasterAgent
            # 直接调用 receive_messgae，因为 send_message 工具内部也是调用这个方法
            master_agent = top_level_agent.load_agent_from_db_by_id(master_agent_id)
            if not master_agent:
                return "错误: 无法加载MasterAgent"
            
            # Runner.run 应该会自动执行工具调用并等待结果
            output = top_level_agent.run_async_safely(master_agent.receive_messgae(message_to_master))
            output_str = output.final_output if hasattr(output, 'final_output') else str(output)
            return output_str
            
        except Exception as e:
            return f"处理文件上传失败: {str(e)}"
    
    return handle_file_upload


def create_modify_notes_tool(notebook_agent: 'BaseAgent'):
    """
    Create a modify_notes tool function for NoteBookAgent.
    
    Args:
        notebook_agent: The NoteBookAgent instance that will use this tool
        
    Returns:
        A function_tool decorated function for modifying notes
    """
    from backend.prompts.prompt_loader import load_prompt
    
    @function_tool
    def modify_notes(new_notes: str) -> str:
        """修改笔记内容"""
        notebook_agent.notes = new_notes
        # 更新 instructions 以反映新的笔记内容
        instructions = load_prompt(
            "notebook_agent",
            variables={"notes": notebook_agent.notes}
        )
        notebook_agent.instructions = instructions
        # 保存到数据库
        notebook_agent.save_to_db()
        
        # 检测是否需要 split
        if hasattr(notebook_agent, '_check_split'):
            should_split = notebook_agent._check_split()
            if should_split:
                sections_count = len(notebook_agent.sections) if notebook_agent.sections else 0
                word_count = notebook_agent._get_word_count() if hasattr(notebook_agent, '_get_word_count') else 0
                return f"笔记已更新。⚠️ 建议拆分：章节数={sections_count}，字数={word_count}（超过限制：章节>10 或 字数>3000）"
        
        return "笔记已更新"
    
    return modify_notes

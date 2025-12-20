"""Agent function tools - tools that agents can use."""

from typing import TYPE_CHECKING
from agents import function_tool
from backend.tools.tool_registry import register_function_tool

if TYPE_CHECKING:
    from backend.agent.BaseAgent import BaseAgent
    from backend.agent.MasterAgent import MasterAgent


@register_function_tool(
    tool_id="send_message",
    name="send_message",
    description="向指定ID的agent发送消息",
    task="用于agent之间的通信，允许一个agent向另一个agent发送消息并获取响应",
    agent_types=["BaseAgent"],
    input_params={
        "id": {"type": "str", "description": "Agent ID", "required": True},
        "message": {"type": "str", "description": "要发送的消息", "required": True},
    },
    output_type="str",
    output_description="返回目标agent处理消息后的完整响应文本。如果agent执行成功，返回agent的执行结果；如果加载agent失败，返回错误信息；如果执行过程中出现异常，返回错误信息",
    required_agent_attrs=["load_agent_from_db_by_id", "run_async_safely"],
)
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
            id: Agent ID（完整的UUID，不是部分ID）
            message: Message to send

        Returns:
            Response from the agent
        """
        # Validate ID format (should be a valid UUID format)
        if len(id) < 8:
            return f"Error: Agent ID '{id}' is too short. Please use the complete agent ID from the agents list."
        
        # Use AgentManager to wake up the agent (ensures tools are restored)
        from backend.utils.agent_manager import wake_agent
        target_agent = wake_agent(id, db_path=getattr(agent, 'DB_PATH', None))
        
        if target_agent is None:
            # Try to find agent by partial ID match
            try:
                from backend.database.agent_db import load_all_agents
                all_agents = load_all_agents(getattr(agent, 'DB_PATH', None))
                matching_ids = [aid for aid in all_agents.keys() if aid.startswith(id)]
                if matching_ids:
                    if len(matching_ids) == 1:
                        target_agent = wake_agent(matching_ids[0], db_path=getattr(agent, 'DB_PATH', None))
                        if target_agent:
                            return f"Error: Agent ID '{id}' is incomplete. Use the complete ID: {matching_ids[0]}"
                    else:
                        return f"Error: Agent ID '{id}' is ambiguous. Found {len(matching_ids)} matching agents. Please use the complete agent ID from the agents list."
            except Exception:
                pass
            
            return f"Error: Failed to load agent with ID {id} from database. Please check:\n1. The agent ID is correct and complete\n2. The agent exists in the database\n3. For file upload/notebook creation, use 'create_notebook_from_outline' tool instead of 'send_message'"

        # Ensure tools are restored (AgentManager should do this, but double-check)
        if not hasattr(target_agent, 'tools') or target_agent.tools is None:
            from backend.utils.agent_manager import get_agent_manager
            get_agent_manager()._ensure_tools_restored(target_agent)

        try:
            output = agent.run_async_safely(target_agent.receive_messgae(message))
            return str(output)
        except Exception as e:
            return f"Error sending message: {str(e)}"
    
    return send_message


@register_function_tool(
    tool_id="add_notebook_by_file",
    name="add_notebook_by_file",
    description="根据文件路径，添加一个新的notebook agent（向后兼容版本）",
    task="从文件创建notebook agent并添加到MasterAgent的子agents列表中。此工具会自动检测用户意图并选择合适的创建策略。",
    agent_types=["MasterAgent"],
    input_params={
        "file_path": {"type": "str", "description": "文件路径（支持 .docx, .md, .txt）", "required": True},
    },
    output_type="str",
    output_description="返回操作结果字符串。成功时返回包含成功信息的消息；失败时返回错误信息。该工具会自动检测文件内容，选择合适的创建策略",
    required_agent_attrs=["id", "DB_PATH", "_add_sub_agents", "run_async_safely"],
)
def create_add_notebook_by_file_tool(master_agent: 'MasterAgent'):
    """
    Create an add_notebook_by_file tool function for MasterAgent.
    
    注意：此工具保留用于向后兼容。新代码建议使用 create_notebook 工具。
    
    Args:
        master_agent: The MasterAgent instance that will use this tool
        
    Returns:
        A function_tool decorated function for adding notebook by file
    """
    @function_tool
    def add_notebook_by_file(file_path: str) -> str:
        """根据文件路径，添加一个新的notebook agent（向后兼容版本）
        
        此工具会自动检测用户意图并选择合适的创建策略。
        
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


@register_function_tool(
    tool_id="create_notebook",
    name="create_notebook",
    description="根据用户请求创建notebook agent（硬编码两步流程）",
    task="硬编码的两步创建流程：第一步，调用outline_maker_agent生成大纲；第二步，用户确认后，将大纲发送给master agent完成notebook创建。",
    agent_types=["MasterAgent"],
    input_params={
        "user_request": {"type": "str", "description": "用户的请求内容", "required": True},
        "file_path": {"type": "str", "description": "文件路径（必需，支持 .docx, .md, .txt）", "required": True},
    },
    output_type="str",
    output_description="返回包含大纲信息的markdown格式字符串。格式包含大纲的markdown展示和JSON格式的大纲数据。该输出用于前端展示和用户确认，确认后系统会继续生成完整笔记本内容",
    required_agent_attrs=["run_async_safely"],
)
def create_create_notebook_tool(master_agent: 'MasterAgent'):
    """
    Create a create_notebook tool function for MasterAgent.
    
    这是一个更灵活的工具，支持多种创建场景：
    - 从文件创建（自动检测意图）
    - 从主题创建（需要先确认大纲）
    
    Args:
        master_agent: The MasterAgent instance that will use this tool
        
    Returns:
        A function_tool decorated function for creating notebook
    """
    @function_tool
    def create_notebook(
        user_request: str,
        file_path: str = None
    ) -> str:
        """根据用户请求创建notebook agent（硬编码两步流程）
        
        硬编码的两步创建流程：
        1. 第一步：调用 outline_maker_agent 生成大纲（需要 file_path）
        2. 第二步：用户确认后，将大纲发送给 master agent 完成创建
        
        Args:
            user_request: 用户的请求内容（必需）
            file_path: 文件路径（必需，支持 .docx, .md, .txt）
        
        Returns:
            操作结果信息。返回大纲信息供用户确认，确认后系统会继续生成完整笔记本内容
        """
        from backend.tools.tool_registry import get_tool_registry
        from agents import Runner
        import json
        import os
        
        async def _create_notebook():
            """内部异步函数，硬编码两步流程：1) outline_maker_agent 2) master agent创建"""
            try:
                # 第一步：使用 outline_maker_agent 生成大纲
                registry = get_tool_registry()
                
                # 检查是否有文件路径
                if not file_path:
                    return "错误：生成大纲需要文件路径。请提供 file_path 参数。"
                
                # 验证文件是否存在
                if not os.path.exists(file_path):
                    return f"错误：文件不存在。文件路径：{file_path}"
                
                if not os.path.isfile(file_path):
                    return f"错误：路径不是文件。文件路径：{file_path}"
                
                # 创建 outline_maker_agent 工具
                try:
                    outline_tool = registry.create_tool(
                        "outline_maker_agent",
                        agent=master_agent,
                        file_path=file_path
                    )
                except Exception as e:
                    import traceback
                    error_trace = traceback.format_exc()
                    print(f"[create_notebook] 创建 outline_maker_agent 失败: {e}")
                    print(f"错误详情:\n{error_trace}")
                    return f"错误：无法创建 outline_maker_agent 工具。错误信息：{str(e)}\n\n文件路径：{file_path}\n请检查文件是否存在且可读。"
                
                if not outline_tool:
                    return f"错误：无法创建 outline_maker_agent 工具。请检查文件路径是否正确。\n文件路径：{file_path}\n请确认：\n1. 文件是否存在\n2. 文件格式是否支持（.docx, .md, .txt）\n3. 文件是否有读取权限"
                
                # 调用 outline_maker_agent 生成大纲
                print(f"[create_notebook] 调用 outline_maker_agent 生成大纲，文件路径: {file_path}")
                outline_result = await Runner.run(
                    outline_tool._agent_instance,
                    "请分析文档并生成学习大纲，包括笔记本描述（描述包含什么知识、不包含什么知识、知识边界和定位）"
                )
                
                if not outline_result or not outline_result.final_output:
                    return "错误：outline_maker_agent 未能生成大纲"
                
                outline = outline_result.final_output
                
                # 格式化大纲信息
                outline_info_lines = [
                    f"# {outline.notebook_title}",
                    "",
                    f"**描述**：{outline.notebook_description}",
                    "",
                    "## 章节结构",
                    ""
                ]
                
                for idx, (section_title, section_desc) in enumerate(outline.outlines.items(), 1):
                    outline_info_lines.append(f"### {idx}. {section_title}")
                    outline_info_lines.append(f"{section_desc}")
                    outline_info_lines.append("")
                
                outline_info = "\n".join(outline_info_lines)
                
                # 将大纲转换为字典以便序列化
                outline_dict = {
                    "notebook_title": outline.notebook_title,
                    "notebook_description": outline.notebook_description,
                    "outlines": outline.outlines
                }
                
                # 返回大纲信息，包含结构化的JSON数据（用于前端解析）
                # 使用特殊标记让前端知道这是大纲确认请求
                return f"""📋 **大纲已生成，请确认：**

{outline_info}

**大纲数据（JSON格式，供系统使用）：**
```json
{json.dumps(outline_dict, ensure_ascii=False, indent=2)}
```

请确认此大纲是否符合您的需求。如果不满意，请告诉我需要修改的地方。确认后我将根据大纲生成完整的笔记本内容。"""
                
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                return f"生成大纲失败: {str(e)}\n\n错误详情:\n{error_trace}"
        
        # 执行异步函数
        try:
            result = master_agent.run_async_safely(_create_notebook())
            return result
        except Exception as e:
            return f"执行失败: {str(e)}"
    
    return create_notebook


@register_function_tool(
    tool_id="create_notebook_with_outline",
    name="create_notebook_with_outline",
    description="根据确认的大纲创建notebook agent（硬编码流程）",
    task="MasterAgent用于接收确认的大纲并创建完整的notebook。硬编码流程：调用notebook_agent_creator生成内容，然后创建NoteBookAgent实例。",
    agent_types=["MasterAgent"],
    input_params={
        "outline": {"type": "str", "description": "确认的大纲对象（JSON字符串格式，包含notebook_title、notebook_description和outlines字典）", "required": True},
        "file_path": {"type": "str", "description": "文件路径", "required": True},
        "user_request": {"type": "str", "description": "用户的原始请求内容", "required": True},
    },
    output_type="str",
    output_description="返回创建结果字符串。成功时返回notebook信息（ID、标题等），失败时返回错误信息。",
    required_agent_attrs=["id", "DB_PATH", "_add_sub_agents", "run_async_safely"],
)
def create_create_notebook_with_outline_tool(master_agent: 'MasterAgent'):
    """
    Create a create_notebook_with_outline tool function for MasterAgent.
    
    Args:
        master_agent: The MasterAgent instance that will use this tool
        
    Returns:
        A function_tool decorated function for creating notebook from confirmed outline
    """
    from backend.agent.specialized.NotebookModels import Outline
    from backend.tools.tool_registry import get_tool_registry
    from agents import Runner
    
    @function_tool
    def create_notebook_with_outline(outline: str, file_path: str, user_request: str) -> str:
        """根据确认的大纲创建notebook agent（硬编码流程）
        
        硬编码流程：
        1. 调用 notebook_agent_creator 生成完整内容
        2. 创建 NoteBookAgent 实例
        3. 添加到 MasterAgent 的子 agents 列表
        
        Args:
            outline: 确认的大纲对象（JSON字符串格式，包含notebook_title、notebook_description和outlines字典）
            file_path: 文件路径
            user_request: 用户的原始请求内容
        
        Returns:
            创建结果信息
        """
        import json
        
        # 解析 JSON 字符串
        try:
            if isinstance(outline, str):
                outline_dict = json.loads(outline)
            elif isinstance(outline, dict):
                outline_dict = outline
            else:
                return f"错误：大纲格式不正确，期望JSON字符串或字典类型，收到：{type(outline)}"
        except json.JSONDecodeError as e:
            return f"错误：大纲JSON格式不正确：{str(e)}"
        
        async def _create_notebook():
            """内部异步函数，创建notebook"""
            try:
                # 将字典转换为 Outline 对象
                outline_obj = Outline(
                    notebook_title=outline_dict.get("notebook_title", ""),
                    notebook_description=outline_dict.get("notebook_description", ""),
                    outlines=outline_dict.get("outlines", {})
                )
                
                # 第一步：使用 notebook_agent_creator 生成完整内容
                registry = get_tool_registry()
                
                # 创建 notebook_agent_creator 工具
                notebook_creator_tool = registry.create_tool(
                    "notebook_agent_creator",
                    agent=master_agent,
                    outline=outline_obj,
                    file_path=file_path
                )
                
                if not notebook_creator_tool:
                    return "错误：无法创建 notebook_agent_creator 工具。"
                
                # 调用 notebook_agent_creator 生成内容
                print(f"[create_notebook_with_outline] 调用 notebook_agent_creator 生成内容")
                creator_agent = notebook_creator_tool._agent_instance
                
                # 运行 agent 生成所有章节
                creator_result = await Runner.run(
                    creator_agent,
                    f"请根据大纲生成完整的notebook内容。用户请求：{user_request}"
                )
                
                # 从 agent 实例中获取生成的 sections
                if not hasattr(creator_agent, 'sections') or not creator_agent.sections:
                    return "错误：notebook_agent_creator 未能生成内容。请检查 agent 是否正确执行。"
                
                sections = creator_agent.sections  # Dict[str, Section]
                
                # 第二步：创建 NoteBookAgent 实例
                from backend.agent.NoteBookAgent import NoteBookAgent
                
                new_notebook = NoteBookAgent(
                    outline=outline_obj,
                    sections=sections,
                    notebook_title=outline_obj.notebook_title,
                    parent_agent_id=master_agent.id,
                    DB_PATH=master_agent.DB_PATH
                )
                
                # 保存到数据库
                new_notebook.save_to_db()
                
                # 添加到 MasterAgent 的子 agents 列表
                master_agent._add_sub_agents(new_notebook.id)
                
                success_message = f"""✅ **笔记本创建成功！**

**标题**：{outline_obj.notebook_title}
**ID**：{new_notebook.id[:8]}...
**章节数**：{len(sections)}

笔记本已创建并添加到系统中。"""
                
                return success_message
                
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                return f"创建notebook失败: {str(e)}\n\n错误详情:\n{error_trace}"
        
        # 执行异步函数
        try:
            result = master_agent.run_async_safely(_create_notebook())
            return result
        except Exception as e:
            return f"执行失败: {str(e)}"
    
    return create_notebook_with_outline


@register_function_tool(
    tool_id="handle_file_upload",
    name="handle_file_upload",
    description="处理文件上传：验证文件并生成大纲供用户确认",
    task="TopLevelAgent用于处理用户上传的文件。验证文件存在性，然后调用outline_maker_agent生成大纲，返回给用户确认。",
    agent_types=["TopLevelAgent"],
    input_params={
        "file_path": {"type": "str", "description": "上传的文件路径（可能是原始路径或已保存的路径）", "required": True},
        "user_request": {"type": "str", "description": "用户的原始请求内容", "required": True},
    },
    output_type="str",
    output_description="返回包含大纲信息的markdown格式字符串。格式包含大纲的markdown展示和JSON格式的大纲数据。该输出用于前端展示给用户确认。如果文件不存在或处理失败，返回错误信息",
    required_agent_attrs=["run_async_safely"],
)
def create_handle_file_upload_tool(top_level_agent: 'BaseAgent'):
    """
    Create a handle_file_upload tool function for TopLevelAgent.
    
    Args:
        top_level_agent: The TopLevelAgent instance that will use this tool
        
    Returns:
        A function_tool decorated function for handling file uploads
    """
    from backend.tools.file_storage import save_uploaded_file
    from backend.tools.tool_registry import get_tool_registry
    from agents import Runner
    import json
    
    @function_tool
    def handle_file_upload(file_path: str, user_request: str) -> str:
        """处理文件上传：验证文件并生成大纲供用户确认
        
        Args:
            file_path: 上传的文件路径（可能是原始路径或已保存的路径）
            user_request: 用户的原始请求内容
        
        Returns:
            包含大纲信息的markdown格式字符串，供用户确认
        """
        import os
        
        async def _generate_outline():
            """内部异步函数，生成大纲"""
            try:
                # 确保使用绝对路径
                if not os.path.isabs(file_path):
                    stored_path = os.path.abspath(file_path)
                else:
                    stored_path = file_path
                
                # 验证文件存在
                if not os.path.exists(stored_path):
                    return f"错误: 文件不存在: {stored_path}"
                
                # 如果文件不在 uploads 目录，需要保存
                if "uploads" not in stored_path:
                    stored_path = save_uploaded_file(stored_path)
                
                # 第一步：使用 outline_maker_agent 生成大纲
                registry = get_tool_registry()
                
                # 验证文件是否存在
                if not os.path.exists(stored_path):
                    return f"错误：文件不存在。文件路径：{stored_path}"
                
                if not os.path.isfile(stored_path):
                    return f"错误：路径不是文件。文件路径：{stored_path}"
                
                # 检查 outline_maker_agent 是否已注册
                if "outline_maker_agent" not in registry._agent_as_tools:
                    return f"错误：outline_maker_agent 未注册。请检查工具系统是否正确初始化。"
                
                metadata = registry._agent_as_tools["outline_maker_agent"]
                if not metadata.agent_class:
                    return f"错误：outline_maker_agent 的 agent_class 未设置。agent_class_name: {metadata.agent_class_name}"
                
                # 创建 outline_maker_agent 工具
                try:
                    print(f"[handle_file_upload] 尝试创建 outline_maker_agent，文件路径: {stored_path}")
                    print(f"[handle_file_upload] Agent class: {metadata.agent_class}")
                    print(f"[handle_file_upload] Agent class name: {metadata.agent_class_name}")
                    
                    outline_tool = registry.create_tool(
                        "outline_maker_agent",
                        agent=top_level_agent,
                        file_path=stored_path
                    )
                    
                    print(f"[handle_file_upload] create_tool 返回: {outline_tool}")
                    
                except FileNotFoundError as e:
                    return f"错误：文件不存在。\n文件路径：{stored_path}\n错误详情：{str(e)}"
                except IOError as e:
                    return f"错误：读取文件失败。\n文件路径：{stored_path}\n错误详情：{str(e)}\n请检查文件格式和编码。"
                except Exception as e:
                    import traceback
                    error_trace = traceback.format_exc()
                    print(f"[handle_file_upload] 创建 outline_maker_agent 失败: {e}")
                    print(f"错误详情:\n{error_trace}")
                    return f"错误：无法创建 outline_maker_agent 工具。\n错误类型：{type(e).__name__}\n错误信息：{str(e)}\n文件路径：{stored_path}\n\n请检查：\n1. 文件是否存在\n2. 文件格式是否支持（.docx, .md, .txt）\n3. 文件是否有读取权限\n4. 文件编码是否正确"
                
                if not outline_tool:
                    # 检查为什么返回 None - 提供详细的诊断信息
                    error_details = []
                    error_details.append(f"文件路径：{stored_path}")
                    
                    if "outline_maker_agent" not in registry._agent_as_tools:
                        error_details.append("原因：outline_maker_agent 未在工具注册表中注册")
                        error_details.append("建议：请重启后端服务以确保工具系统正确初始化")
                    else:
                        metadata = registry._agent_as_tools["outline_maker_agent"]
                        error_details.append(f"注册状态：已注册")
                        error_details.append(f"Agent class name: {metadata.agent_class_name}")
                        
                        if not metadata.agent_class:
                            error_details.append("原因：agent_class 未设置")
                            error_details.append("建议：请检查 register_specialized_agents.py 是否正确导入 OutlineMakerAgent")
                        else:
                            error_details.append(f"Agent class: {metadata.agent_class}")
                            error_details.append("原因：创建 agent 实例时失败（可能是文件读取错误）")
                            error_details.append("建议：请检查后端控制台的详细错误日志")
                    
                    return f"错误：无法创建 outline_maker_agent 工具。\n\n" + "\n".join(error_details)
                
                # 调用 outline_maker_agent 生成大纲
                print(f"[handle_file_upload] 调用 outline_maker_agent 生成大纲，文件路径: {stored_path}")
                outline_result = await Runner.run(
                    outline_tool._agent_instance,
                    "请分析文档并生成学习大纲，包括笔记本描述（描述包含什么知识、不包含什么知识、知识边界和定位）"
                )
                
                if not outline_result or not outline_result.final_output:
                    return "错误：outline_maker_agent 未能生成大纲"
                
                outline = outline_result.final_output
                
                # 格式化大纲信息
                outline_info_lines = [
                    f"# {outline.notebook_title}",
                    "",
                    f"**描述**：{outline.notebook_description}",
                    "",
                    "## 章节结构",
                    ""
                ]
                
                for idx, (section_title, section_desc) in enumerate(outline.outlines.items(), 1):
                    outline_info_lines.append(f"### {idx}. {section_title}")
                    outline_info_lines.append(f"{section_desc}")
                    outline_info_lines.append("")
                
                outline_info = "\n".join(outline_info_lines)
                
                # 将大纲转换为字典以便序列化
                outline_dict = {
                    "notebook_title": outline.notebook_title,
                    "notebook_description": outline.notebook_description,
                    "outlines": outline.outlines
                }
                
                # 返回大纲信息，包含结构化的JSON数据（用于前端解析）
                # 同时保存文件路径，以便后续创建时使用
                return f"""📋 **大纲已生成，请确认：**

{outline_info}

**大纲数据（JSON格式，供系统使用）：**
```json
{json.dumps(outline_dict, ensure_ascii=False, indent=2)}
```

**文件路径（供后续创建使用）：**
{stored_path}

请确认此大纲是否符合您的需求。如果不满意，请告诉我需要修改的地方。确认后我将根据大纲生成完整的笔记本内容。"""
                
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                return f"生成大纲失败: {str(e)}\n\n错误详情:\n{error_trace}"
        
        # 执行异步函数
        try:
            result = top_level_agent.run_async_safely(_generate_outline())
            return result
        except Exception as e:
            return f"处理文件上传失败: {str(e)}"
    
    return handle_file_upload


@register_function_tool(
    tool_id="create_notebook_from_outline",
    name="create_notebook_from_outline",
    description="【重要】当用户确认大纲后，使用此工具创建notebook。此工具会自动查找MasterAgent并调用其create_notebook_with_outline工具。不要使用send_message工具。",
    task="TopLevelAgent用于处理用户确认的大纲。当用户通过自然语言（如'确认'、'可以'、'开始创建'）确认大纲后，必须使用此工具。此工具会自动：1) 查找或创建MasterAgent，2) 调用MasterAgent的create_notebook_with_outline工具，3) 返回创建结果。",
    agent_types=["TopLevelAgent"],
    input_params={
        "outline": {"type": "str", "description": "确认的大纲对象（JSON字符串格式，包含notebook_title、notebook_description和outlines字典）。必须从用户消息或对话历史中提取完整的大纲JSON。", "required": True},
        "file_path": {"type": "str", "description": "文件路径（从用户消息或对话历史中提取）", "required": True},
        "user_request": {"type": "str", "description": "用户的原始请求内容", "required": True},
    },
    output_type="str",
    output_description="返回MasterAgent执行创建后的完整输出字符串。包含创建结果和notebook信息。",
    required_agent_attrs=["sub_agent_ids", "load_agent_from_db_by_id", "run_async_safely"],
)
def create_create_notebook_from_outline_tool(top_level_agent: 'BaseAgent'):
    """
    Create a create_notebook_from_outline tool function for TopLevelAgent.
    
    Args:
        top_level_agent: The TopLevelAgent instance that will use this tool
        
    Returns:
        A function_tool decorated function for creating notebook from confirmed outline
    """
    from backend.agent.MasterAgent import MasterAgent
    import json
    
    @function_tool
    def create_notebook_from_outline(outline: str, file_path: str, user_request: str) -> str:
        """根据确认的大纲创建notebook：将大纲和文件路径发送给MasterAgent完成创建
        
        Args:
            outline: 确认的大纲对象（JSON字符串格式，必须包含 notebook_title、notebook_description 和 outlines）
            file_path: 文件路径
            user_request: 用户的原始请求内容
        
        Returns:
            创建结果信息
        """
        import json
        
        # 解析 JSON 字符串
        try:
            if isinstance(outline, str):
                outline_dict = json.loads(outline)
            elif isinstance(outline, dict):
                outline_dict = outline
            else:
                return f"错误：大纲格式不正确，期望JSON字符串或字典类型，收到：{type(outline)}\n\n收到的大纲内容：{str(outline)[:500]}"
        except json.JSONDecodeError as e:
            return f"错误：大纲JSON格式不正确：{str(e)}\n\n收到的大纲内容：{str(outline)[:500]}"
        
        # 验证大纲完整性
        print(f"[create_notebook_from_outline] 收到参数:")
        print(f"  - outline 类型: {type(outline_dict)}")
        print(f"  - outline 内容: {str(outline_dict)[:500]}...")  # 只打印前500字符
        print(f"  - file_path: {file_path}")
        print(f"  - user_request: {user_request[:200]}...")
        
        if not isinstance(outline_dict, dict):
            return f"错误：大纲格式不正确，期望字典类型，收到：{type(outline_dict)}\n\n收到的大纲内容：{str(outline_dict)[:500]}"
        
        required_fields = ['notebook_title', 'notebook_description', 'outlines']
        missing_fields = [field for field in required_fields if field not in outline_dict]
        if missing_fields:
            return f"错误：大纲缺少必需字段：{', '.join(missing_fields)}。\n\n收到的大纲字段：{list(outline_dict.keys())}\n\n大纲内容预览：{str(outline_dict)[:500]}"
        
        if not isinstance(outline_dict.get('outlines'), dict):
            return f"错误：outlines 字段必须是字典类型，收到：{type(outline_dict.get('outlines'))}\n\noutlines 内容：{str(outline_dict.get('outlines'))[:500]}"
        
        outlines_dict = outline_dict.get('outlines', {})
        if len(outlines_dict) == 0:
            return "错误：outlines 字典为空，必须包含至少一个章节"
        
        print(f"[create_notebook_from_outline] 验证通过，大纲包含 {len(outlines_dict)} 个章节")
        print(f"[create_notebook_from_outline] 章节标题: {list(outlines_dict.keys())}")
        print(f"[create_notebook_from_outline] notebook_title: {outline_dict.get('notebook_title')}")
        print(f"[create_notebook_from_outline] notebook_description 长度: {len(outline_dict.get('notebook_description', ''))} 字符")
        
        async def _create_notebook():
            """内部异步函数，发送大纲给MasterAgent创建"""
            try:
                # 获取MasterAgent - 使用更可靠的查找策略
                master_agent_id = None
                master_agent = None
                
                print(f"[create_notebook_from_outline] 开始查找 MasterAgent")
                print(f"  - TopLevelAgent ID: {top_level_agent.id}")
                print(f"  - TopLevelAgent DB_PATH: {getattr(top_level_agent, 'DB_PATH', None)}")
                
                # 策略1: 从数据库加载所有 MasterAgent，查找 parent_agent_id 匹配的
                print(f"[create_notebook_from_outline] 策略1: 从数据库查找 MasterAgent...")
                try:
                    from backend.database.agent_db import load_all_agents
                    all_agents = load_all_agents(getattr(top_level_agent, 'DB_PATH', None))
                    print(f"  - 数据库中共有 {len(all_agents)} 个 agents")
                    
                    for agent_id, agent in all_agents.items():
                        if isinstance(agent, MasterAgent):
                            parent_id = getattr(agent, 'parent_agent_id', None)
                            print(f"  - 找到 MasterAgent: {agent_id}, parent_id: {parent_id}")
                            if parent_id == top_level_agent.id:
                                master_agent_id = agent_id
                                master_agent = agent
                                print(f"  ✓ 找到匹配的 MasterAgent: {agent_id}")
                                # 确保它在 sub_agent_ids 中
                                sub_agent_ids = getattr(top_level_agent, 'sub_agent_ids', None) or []
                                if agent_id not in sub_agent_ids:
                                    print(f"  - 添加 MasterAgent 到 sub_agent_ids")
                                    top_level_agent._add_sub_agents(agent_id)
                                    top_level_agent.save_to_db()
                                break
                except Exception as e:
                    print(f"  ✗ 从数据库查找失败: {e}")
                    import traceback
                    traceback.print_exc()
                
                # 策略2: 如果策略1失败，从 sub_agent_ids 中查找
                if not master_agent:
                    print(f"[create_notebook_from_outline] 策略2: 从 sub_agent_ids 查找...")
                    sub_agent_ids = getattr(top_level_agent, 'sub_agent_ids', None) or []
                    print(f"  - sub_agent_ids: {sub_agent_ids}")
                    
                    for agent_id in sub_agent_ids:
                        try:
                            agent = top_level_agent.load_agent_from_db_by_id(agent_id)
                            if agent and isinstance(agent, MasterAgent):
                                master_agent_id = agent_id
                                master_agent = agent
                                print(f"  ✓ 从 sub_agent_ids 找到 MasterAgent: {agent_id}")
                                break
                        except Exception as e:
                            print(f"  ✗ 加载 agent {agent_id} 失败: {e}")
                            continue
                
                # 策略3: 如果还是没找到，说明系统配置有问题，不应该创建新的
                # 因为 MasterAgent 应该在 TopLevelAgent 初始化时或 get_top_level_agent() 时创建
                if not master_agent:
                    print(f"[create_notebook_from_outline] 策略3: 未找到 MasterAgent，但不应在此处创建")
                    print(f"  提示: MasterAgent 应该在 TopLevelAgent 初始化时创建")
                    print(f"  建议: 请检查数据库和 TopLevelAgent 的配置")
                    return f"错误: 无法找到MasterAgent。\n\n这通常不应该发生，因为MasterAgent应该在系统初始化时创建。\n\n请检查：\n1. TopLevelAgent是否正确初始化\n2. 数据库是否正常\n3. 系统是否需要重启以重新初始化"
                
                if not master_agent:
                    return "错误: 未找到MasterAgent且无法创建新的MasterAgent。请检查系统配置。"
                
                print(f"[create_notebook_from_outline] ✓ MasterAgent 已找到/创建: {master_agent_id}")
                print(f"  - MasterAgent name: {master_agent.name}")
                print(f"  - MasterAgent tools: {len(master_agent.tools) if master_agent.tools else 0}")
                
                # 直接调用 MasterAgent 的 create_notebook_with_outline 函数逻辑
                # 由于 FunctionTool 对象不能直接调用，我们直接执行函数内部的逻辑
                from backend.agent.specialized.NotebookModels import Outline
                from backend.tools.tool_registry import get_tool_registry
                from agents import Runner
                import json
                
                # 将字典转换为 Outline 对象
                outline_obj = Outline(
                    notebook_title=outline_dict.get("notebook_title", ""),
                    notebook_description=outline_dict.get("notebook_description", ""),
                    outlines=outline_dict.get("outlines", {})
                )
                
                async def _create_notebook_direct():
                    """直接执行 create_notebook_with_outline 的逻辑"""
                    try:
                        # 第一步：使用 notebook_agent_creator 生成完整内容
                        registry = get_tool_registry()
                        
                        # 创建 notebook_agent_creator 工具
                        notebook_creator_tool = registry.create_tool(
                            "notebook_agent_creator",
                            agent=master_agent,
                            outline=outline_obj,
                            file_path=file_path
                        )
                        
                        if not notebook_creator_tool:
                            return "错误：无法创建 notebook_agent_creator 工具。"
                        
                        # 调用 notebook_agent_creator 生成内容
                        print(f"[create_notebook_from_outline] 调用 notebook_agent_creator 生成内容")
                        creator_agent = notebook_creator_tool._agent_instance
                        
                        # 运行 agent 生成所有章节
                        creator_result = await Runner.run(
                            creator_agent,
                            f"请根据大纲生成完整的notebook内容。用户请求：{user_request}"
                        )
                        
                        # 从 agent 实例中获取生成的 sections
                        if not hasattr(creator_agent, 'sections') or not creator_agent.sections:
                            return "错误：notebook_agent_creator 未能生成内容。请检查 agent 是否正确执行。"
                        
                        sections = creator_agent.sections  # Dict[str, Section]
                        
                        # 第二步：创建 NoteBookAgent 实例
                        from backend.agent.NoteBookAgent import NoteBookAgent
                        
                        new_notebook = NoteBookAgent(
                            outline=outline_obj,
                            sections=sections,
                            notebook_title=outline_obj.notebook_title,
                            parent_agent_id=master_agent.id,
                            DB_PATH=master_agent.DB_PATH
                        )
                        
                        # 保存到数据库
                        new_notebook.save_to_db()
                        
                        # 添加到 MasterAgent 的子 agents 列表
                        master_agent._add_sub_agents(new_notebook.id)
                        
                        success_message = f"""✅ **笔记本创建成功！**

**标题**：{outline_obj.notebook_title}
**ID**：{new_notebook.id[:8]}...
**章节数**：{len(sections)}

笔记本已创建并添加到系统中。"""
                        
                        return success_message
                        
                    except Exception as e:
                        import traceback
                        error_trace = traceback.format_exc()
                        return f"创建notebook失败: {str(e)}\n\n错误详情:\n{error_trace}"
                
                # 执行异步函数
                print(f"[create_notebook_from_outline] 调用 MasterAgent 的 create_notebook_with_outline 逻辑")
                result = master_agent.run_async_safely(_create_notebook_direct())
                return result
                
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                return f"创建notebook失败: {str(e)}\n\n错误详情:\n{error_trace}"
        
        # 执行异步函数
        try:
            result = top_level_agent.run_async_safely(_create_notebook())
            return result
        except Exception as e:
            return f"执行失败: {str(e)}"
    
    return create_notebook_from_outline


@register_function_tool(
    tool_id="modify_notes",
    name="modify_notes",
    description="修改笔记内容",
    task="NoteBookAgent用于更新其笔记内容，并自动更新instructions以反映新的笔记内容。如果笔记过大，会提示建议拆分。",
    agent_types=["NoteBookAgent"],
    input_params={
        "new_notes": {"type": "str", "description": "新的笔记内容", "required": True},
    },
    output_type="str",
    output_description="返回操作结果字符串。正常情况下返回'笔记已更新'。如果检测到笔记需要拆分（章节数>10或字数>3000），返回提示信息。该工具会自动更新agent的instructions以反映新的笔记内容",
    required_agent_attrs=["notes", "instructions", "save_to_db"],
)
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

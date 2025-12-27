"""Notebook creation tools - Notebook创建相关工具"""

from typing import TYPE_CHECKING
from agents import function_tool
from backend.tools.tool_registry import register_function_tool

if TYPE_CHECKING:
    from backend.agent.BaseAgent import BaseAgent
    from backend.agent.MasterAgent import MasterAgent


@register_function_tool(
    tool_id="create_notebook",
    name="create_notebook",
    description="根据确认的大纲创建notebook agent",
    task="MasterAgent用于接收确认的大纲并创建完整的notebook。使用NotebookCreationRouter内部判断意图并选择策略，创建所有章节内容，然后创建NotebookAgent实例。",
    agent_types=["MasterAgent"],
    input_params={
        "outline": {"type": "str", "description": "确认的大纲对象（JSON字符串格式，包含notebook_title、notebook_description和outlines字典）", "required": True},
        "file_path": {"type": "str", "description": "文件路径（可选，有文件时提供）", "required": False},
        "user_request": {"type": "str", "description": "用户的原始请求内容", "required": True},
    },
    output_type="str",
    output_description="返回创建结果字符串。成功时返回notebook信息（ID、标题等），失败时返回错误信息。",
    required_agent_attrs=["id", "DB_PATH", "_add_sub_agents", "run_async_safely"],
)
def create_create_notebook_tool(master_agent: 'MasterAgent'):
    """
    Create a create_notebook tool function for MasterAgent.
    
    根据确认的大纲创建notebook agent。使用NotebookCreationRouter内部判断意图并选择策略。
    
    Args:
        master_agent: The MasterAgent instance that will use this tool
        
    Returns:
        A function_tool decorated function for creating notebook
    """
    @function_tool
    def create_notebook(
        outline: str,
        file_path: str = None,
        user_request: str = ""
    ) -> str:
        """根据确认的大纲创建notebook agent
        
        使用NotebookCreationRouter内部判断意图并选择策略，创建所有章节内容。
        
        Args:
            outline: 确认的大纲对象（JSON字符串格式，包含notebook_title、notebook_description和outlines字典）
            file_path: 文件路径（可选，有文件时提供）
            user_request: 用户的原始请求内容
        
        Returns:
            创建结果信息
        """
        import json
        from backend.models import Outline
        from backend.agent.specialized.NotebookCreationRouter import NotebookCreationRouter
        
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
                
                # 使用 NotebookCreationRouter 创建笔记本
                router = NotebookCreationRouter()
                notebook, message = await router.route_and_create(
                    user_request=user_request,
                    confirmed_outline=outline_obj,
                    file_path=file_path,
                    parent_agent_id=master_agent.id,
                    DB_PATH=master_agent.DB_PATH
                )
                
                # 添加到 MasterAgent 的子 agents 列表
                master_agent._add_sub_agents(notebook.id)
                
                # 返回包含结构化数据的 JSON 字符串，方便前端解析
                result_data = {
                    "status": "success",
                    "message": message,
                    "notebook_id": notebook.id,
                    "notebook_title": notebook.notebook_title or outline_obj.notebook_title,
                }
                return json.dumps(result_data, ensure_ascii=False)
                
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
    
    return create_notebook


@register_function_tool(
    tool_id="generate_outline",
    name="generate_outline",
    description="生成学习大纲供用户确认（无文件场景）",
    task="TopLevelAgent用于处理用户创建笔记本的请求（无文件上传）。根据用户请求的主题，生成学习大纲供用户确认。如果提供了file_path，则从文件生成大纲；否则从主题生成大纲。",
    agent_types=["TopLevelAgent"],
    input_params={
        "user_request": {"type": "str", "description": "用户的请求内容", "required": True},
        "file_path": {"type": "str", "description": "文件路径（可选，如果有文件则提供）", "required": False},
    },
    output_type="str",
    output_description="返回包含大纲信息的markdown格式字符串。格式包含大纲的markdown展示和JSON格式的大纲数据。该输出用于前端展示给用户确认。",
    required_agent_attrs=["run_async_safely"],
)
def create_generate_outline_tool(top_level_agent: 'BaseAgent'):
    """
    Create a generate_outline tool function for TopLevelAgent.
    
    Args:
        top_level_agent: The TopLevelAgent instance that will use this tool
        
    Returns:
        A function_tool decorated function for generating outline
    """
    from backend.tools.function_tools.notebook_creator_tool import generate_outline_for_confirmation
    import json
    
    @function_tool
    def generate_outline(user_request: str, file_path: str = None) -> str:
        """生成学习大纲供用户确认（无文件场景）
        
        Args:
            user_request: 用户的请求内容（必需）
            file_path: 文件路径（可选，如果有文件则提供）
        
        Returns:
            包含大纲信息的markdown格式字符串，供用户确认
        """
        async def _generate_outline():
            """内部异步函数，生成大纲"""
            try:
                # 调用 generate_outline_for_confirmation 生成大纲
                outline, outline_info = await generate_outline_for_confirmation(
                    user_request=user_request,
                    file_path=file_path if file_path and file_path.strip() else None
                )
                
                # 将大纲转换为字典以便序列化
                outline_dict = {
                    "notebook_title": outline.notebook_title,
                    "notebook_description": outline.notebook_description,
                    "outlines": outline.outlines
                }
                
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
                
                outline_info_formatted = "\n".join(outline_info_lines)
                
                # 返回包含结构化数据的 JSON 字符串，方便前端解析
                result_data = {
                    "type": "outline",
                    "outline": outline_dict,
                    "file_path": file_path if file_path and file_path.strip() else None,
                    "user_request": user_request,
                }
                
                # 同时返回用户友好的文本消息
                result_text = f"""📋 **大纲已生成，请确认：**

{outline_info_formatted}"""
                
                # 如果有文件路径，也包含在结果中
                if file_path and file_path.strip():
                    result_text += f"\n\n**文件路径（供后续创建使用）：**\n{file_path}"
                
                result_text += "\n\n请确认此大纲是否符合您的需求。如果不满意，请告诉我需要修改的地方。确认后我将根据大纲生成完整的笔记本内容。"
                
                # 返回 JSON 字符串，包含结构化数据和文本消息
                result_data["message"] = result_text
                return json.dumps(result_data, ensure_ascii=False)
                
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                return f"生成大纲失败: {str(e)}\n\n错误详情:\n{error_trace}"
        
        # 执行异步函数
        try:
            result = top_level_agent.run_async_safely(_generate_outline())
            return result
        except Exception as e:
            return f"生成大纲失败: {str(e)}"
    
    return generate_outline

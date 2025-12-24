"""Tool for creating notebook agents - supports multiple creation strategies."""

import asyncio
import os
from typing import Optional, Tuple
from agents import Runner

from backend.agent.NoteBookAgent import NoteBookAgent
from backend.tools.agent_as_tools.NotebookCreator import (
    OutlineMakerAgent,
    NotebookCreator,
)
from backend.models import Section, Outline
from backend.agent.specialized.NotebookCreationRouter import NotebookCreationRouter


async def generate_outline_for_confirmation(
    user_request: str,
    file_path: Optional[str] = None
) -> Tuple[Outline, str]:
    """
    生成大纲供用户确认（所有场景统一使用）
    
    这是第一步：先生成大纲，让用户确认后再生成内容。
    
    Args:
        user_request: 用户的请求内容
        file_path: 文件路径（如果有）
        
    Returns:
        Tuple of (Outline对象, 格式化的大纲信息字符串)
    """
    router = NotebookCreationRouter()
    return await router.generate_outline(
        user_request=user_request,
        file_path=file_path
    )


async def create_notebook_agent(
    user_request: str,
    confirmed_outline: Outline,
    file_path: Optional[str] = None,
    parent_agent_id: Optional[str] = None,
    DB_PATH: Optional[str] = None,
    output_path: Optional[str] = None
) -> Tuple[NoteBookAgent, str]:
    """
    创建笔记本agent（第二步：使用已确认的大纲生成内容）
    
    这个函数会根据用户意图，选择合适的创建策略：
    - full_content: 丰满笔记，只需稍作修改
    - enhancement: 稀疏笔记，需要大量增强
    - knowledge_base: 论文/条例等，不需要练习题
    - outline_first: 只有主题，从大纲生成内容
    
    Args:
        user_request: 用户的请求内容
        confirmed_outline: 已确认的大纲（必需）
        file_path: 文件路径（如果有）
        parent_agent_id: ID of the parent agent (optional)
        DB_PATH: Database path (optional)
        output_path: Output path for the generated notebook markdown (optional)
    
    Returns:
        Tuple of (NoteBookAgent instance, success message)
    
    Raises:
        Exception: If notebook creation fails
    """
    router = NotebookCreationRouter()
    
    try:
        notebook, message = await router.route_and_create(
            user_request=user_request,
            confirmed_outline=confirmed_outline,
            file_path=file_path,
            parent_agent_id=parent_agent_id,
            DB_PATH=DB_PATH,
            output_path=output_path
        )
        
        return notebook, message
        
    except Exception as e:
        raise Exception(f"创建笔记本失败: {str(e)}")


async def create_notebook_agent_from_file(
    file_path: str,
    parent_agent_id: Optional[str] = None,
    DB_PATH: Optional[str] = None,
    output_path: Optional[str] = None
) -> Tuple[NoteBookAgent, str]:
    """
    Create a notebook agent from a file (legacy function, for backward compatibility).
    
    注意：此函数保留用于向后兼容。新代码应该使用 create_notebook_agent。
    此函数会使用默认策略（自动检测意图）。
    
    Args:
        file_path: Path to the input file (supports .docx, .md, .txt)
        parent_agent_id: ID of the parent agent (optional)
        DB_PATH: Database path (optional)
        output_path: Output path for the generated notebook markdown (optional)
                    If not provided, will be generated based on input file path
    
    Returns:
        Tuple of (NoteBookAgent instance, success message)
    
    Raises:
        Exception: If notebook creation fails
    """
    # 注意：这个函数保留用于向后兼容，但现在应该使用新的流程
    # 如果直接调用此函数，会跳过用户确认步骤（自动确认）
    # 正常流程应该：generate_outline_for_confirmation -> 用户确认 -> create_notebook_agent
    
    # 使用新的路由系统：先生成大纲，然后自动确认并创建（向后兼容）
    router = NotebookCreationRouter()
    
    # 第一步：生成大纲
    outline, outline_info = await router.generate_outline(
        user_request=f"请根据文件创建笔记本: {file_path}",
        file_path=file_path
    )
    
    # 第二步：使用大纲创建笔记本（自动确认，向后兼容 - 不推荐，应该让用户确认）
    notebook, message = await router.route_and_create(
        user_request=f"请根据文件创建笔记本: {file_path}",
        confirmed_outline=outline,
        file_path=file_path,
        parent_agent_id=parent_agent_id,
        DB_PATH=DB_PATH,
        output_path=output_path
    )
    
    return notebook, message


async def create_notebook_agent_from_file_legacy(
    file_path: str,
    parent_agent_id: Optional[str] = None,
    DB_PATH: Optional[str] = None,
    output_path: Optional[str] = None
) -> Tuple[NoteBookAgent, str]:
    """
    Create a notebook agent from a file by generating outline and sections (original implementation).
    
    这是原始的实现，保留用于特殊场景或测试。
    
    Args:
        file_path: Path to the input file (supports .docx, .md, .txt)
        parent_agent_id: ID of the parent agent (optional)
        DB_PATH: Database path (optional)
        output_path: Output path for the generated notebook markdown (optional)
                    If not provided, will be generated based on input file path
    
    Returns:
        Tuple of (NoteBookAgent instance, success message)
    
    Raises:
        Exception: If notebook creation fails
    """
    # Generate output path if not provided
    if not output_path:
        file_dir = os.path.dirname(file_path) if os.path.dirname(file_path) else "."
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(file_dir, f"{file_name}_notebook.md")
    
    # 创建大纲生成agent
    outline_agent = OutlineMakerAgent(file_path)
    
    # 生成大纲（包含 notebook_description）
    outline_result = await Runner.run(outline_agent, "请分析文档并生成学习大纲，包括笔记本描述（描述包含什么知识、不包含什么知识、知识边界和定位）")
    
    if not outline_result or not outline_result.final_output:
        raise ValueError("无法生成大纲")
    
    outline = outline_result.final_output
    
    # 打印生成的描述信息
    if hasattr(outline, 'notebook_description') and outline.notebook_description:
        print(f"\n📝 笔记本描述: {outline.notebook_description[:100]}...\n")
    
    # 创建notebook生成器（使用新架构）
    notebook_creator = NotebookCreator(
        outline=outline,
        file_path=file_path,
        output_path=output_path
    )
    
    # 生成所有章节（新架构会自动处理并行和日志）
    sections = await notebook_creator.create_all_sections()
    
    # 创建NoteBookAgent实例
    new_notebook = NoteBookAgent(
        outline=outline,
        sections=sections,
        notebook_title=outline.notebook_title,
        parent_agent_id=parent_agent_id,
        DB_PATH=DB_PATH
    )
    
    success_message = f"成功创建notebook agent (ID: {new_notebook.id[:8]}...), 内容已生成"
    
    return new_notebook, success_message

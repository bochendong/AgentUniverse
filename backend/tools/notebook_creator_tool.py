"""Tool for creating notebook agents - supports multiple creation strategies."""

import asyncio
import os
from typing import Optional, Tuple
from agents import Runner

from backend.agent.NoteBookAgent import NoteBookAgent
from backend.agent.specialized.NoteBookCreator import (
    OutlineMakerAgent,
    NoteBookAgentCreator,
)
from backend.agent.specialized.NotebookModels import Section, Outline
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
    
    # 创建notebook生成agent
    notebook_creator = NoteBookAgentCreator(
        outline=outline,
        file_path=file_path,
        output_path=output_path
    )
    
    # 生成所有章节（并行处理）
    all_sections = list(outline.outlines.items())
    print(f"\n开始并行生成 {len(all_sections)} 个章节...\n")
    
    async def create_section_with_logging(notebook_creator, section_title: str, section_desc: str, idx: int, total: int) -> Tuple[str, Optional[Section], Optional[Exception]]:
        """
        创建单个章节并返回结果
        
        Returns:
            Tuple of (section_title, section_data or None, exception or None)
        """
        print(f"[{idx}/{total}] 开始生成章节: {section_title}...")
        try:
            section_data = await notebook_creator._create_section(
                section_title=section_title,
                section_description=section_desc
            )
            print(f"  ✓ 章节 '{section_title}' 生成完成")
            return (section_title, section_data, None)
        except Exception as e:
            print(f"  ✗ 章节 '{section_title}' 生成失败: {str(e)}")
            return (section_title, None, e)
    
    # 并行生成所有章节
    section_tasks = [
        create_section_with_logging(
            notebook_creator, 
            section_title, 
            section_desc, 
            idx + 1, 
            len(all_sections)
        )
        for idx, (section_title, section_desc) in enumerate(all_sections)
    ]
    
    # 使用 asyncio.gather 并行执行所有章节生成任务
    results = await asyncio.gather(*section_tasks, return_exceptions=False)
    
    # 处理结果，按照原始顺序保存到 sections 字典中
    for section_title, section_data, error in results:
        if error is None and section_data is not None:
            notebook_creator.sections[section_title] = section_data
        else:
            # 如果章节生成失败，可以选择跳过或记录错误
            print(f"  警告: 章节 '{section_title}' 未能成功生成，将被跳过")
    
    print(f"\n✓ 所有章节生成完成！成功: {len(notebook_creator.sections)}/{len(all_sections)}\n")
    
    sections = notebook_creator.sections
    
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

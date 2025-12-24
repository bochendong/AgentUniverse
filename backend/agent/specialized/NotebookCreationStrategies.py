"""NotebookCreationStrategies - 不同的笔记本创建策略"""

import os
import asyncio
from typing import Optional, Dict, Tuple
from agents import Runner

from backend.agent.NoteBookAgent import NoteBookAgent
from backend.tools.agent_as_tools.NotebookCreator import (
    OutlineMakerAgent,
    NotebookCreator
)
from backend.tools.agent_as_tools.section_creators.utils import get_file_content
from backend.models import (
    Outline,
    Section,
    NotebookCreationIntent
)


async def create_full_content_notebook(
    intent: NotebookCreationIntent,
    outline: Outline,
    parent_agent_id: Optional[str] = None,
    DB_PATH: Optional[str] = None,
    output_path: Optional[str] = None
) -> Tuple[NoteBookAgent, str]:
    """
    策略1: 从丰满内容创建笔记本
    
    适用于：内容丰满的笔记，只需稍作修改和优化
    
    Args:
        intent: 创建意图
        outline: 已确认的大纲
        parent_agent_id: 父agent ID
        DB_PATH: 数据库路径
        output_path: 输出路径
        
    Returns:
        (NoteBookAgent实例, 成功消息)
    """
    if not intent.file_path:
        raise ValueError("full_content策略需要文件路径")
    
    # 生成输出路径
    if not output_path:
        file_dir = os.path.dirname(intent.file_path) if os.path.dirname(intent.file_path) else "."
        file_name = os.path.splitext(os.path.basename(intent.file_path))[0]
        output_path = os.path.join(file_dir, f"{file_name}_notebook.md")
    
    # 创建notebook生成器（使用新架构）
    notebook_creator = NotebookCreator(
        outline=outline,
        file_path=intent.file_path,
        output_path=output_path,
        force_creator_type='well_formed'  # 强制使用 well_formed 创建器
    )
    
    # 生成所有章节
    sections = await notebook_creator.create_all_sections()
    
    # 创建NoteBookAgent实例
    new_notebook = NoteBookAgent(
        outline=outline,
        sections=sections,
        notebook_title=outline.notebook_title,
        parent_agent_id=parent_agent_id,
        DB_PATH=DB_PATH
    )
    
    success_message = f"成功创建notebook agent (ID: {new_notebook.id[:8]}...), 内容已生成（丰满内容策略）"
    return new_notebook, success_message


async def create_enhanced_notebook(
    intent: NotebookCreationIntent,
    outline: Outline,
    parent_agent_id: Optional[str] = None,
    DB_PATH: Optional[str] = None,
    output_path: Optional[str] = None
) -> Tuple[NoteBookAgent, str]:
    """
    策略2: 从稀疏内容创建笔记本，需要大量增强
    
    适用于：内容稀疏的笔记/PPT，需要补充大量内容
    
    Args:
        intent: 创建意图
        outline: 已确认的大纲
        parent_agent_id: 父agent ID
        DB_PATH: 数据库路径
        output_path: 输出路径
        
    Returns:
        (NoteBookAgent实例, 成功消息)
    """
    if not intent.file_path:
        raise ValueError("enhancement策略需要文件路径")
    
    # 生成输出路径
    if not output_path:
        file_dir = os.path.dirname(intent.file_path) if os.path.dirname(intent.file_path) else "."
        file_name = os.path.splitext(os.path.basename(intent.file_path))[0]
        output_path = os.path.join(file_dir, f"{file_name}_notebook.md")
    
    # 创建notebook生成器（使用新架构，从零生成模式会自动处理内容增强）
    notebook_creator = NotebookCreator(
        outline=outline,
        file_path=intent.file_path,
        output_path=output_path,
        force_creator_type='from_scratch'  # 使用 from_scratch 创建器，会自动参考原文件并增强
    )
    
    # 生成所有章节
    sections = await notebook_creator.create_all_sections()
    
    # 创建NoteBookAgent实例
    new_notebook = NoteBookAgent(
        outline=outline,
        sections=sections,
        notebook_title=outline.notebook_title,
        parent_agent_id=parent_agent_id,
        DB_PATH=DB_PATH
    )
    
    success_message = f"成功创建notebook agent (ID: {new_notebook.id[:8]}...), 内容已生成（内容增强策略）"
    return new_notebook, success_message


async def create_knowledge_base_notebook(
    intent: NotebookCreationIntent,
    outline: Outline,
    parent_agent_id: Optional[str] = None,
    DB_PATH: Optional[str] = None,
    output_path: Optional[str] = None
) -> Tuple[NoteBookAgent, str]:
    """
    策略3: 创建知识库型笔记本（不需要练习题）
    
    适用于：论文、条例、生活内容等，只需记录知识，不需要练习
    
    Args:
        intent: 创建意图
        outline: 已确认的大纲
        parent_agent_id: 父agent ID
        DB_PATH: 数据库路径
        output_path: 输出路径
        
    Returns:
        (NoteBookAgent实例, 成功消息)
    """
    if not intent.file_path:
        raise ValueError("knowledge_base策略需要文件路径")
    
    # 生成输出路径
    if not output_path:
        file_dir = os.path.dirname(intent.file_path) if os.path.dirname(intent.file_path) else "."
        file_name = os.path.splitext(os.path.basename(intent.file_path))[0]
        output_path = os.path.join(file_dir, f"{file_name}_notebook.md")
    
    # 创建notebook生成器（使用新架构，根据文件类型自动选择）
    # 如果是 PDF，会自动使用 PaperSectionCreator
    notebook_creator = NotebookCreator(
        outline=outline,
        file_path=intent.file_path,
        output_path=output_path
        # 不指定 force_creator_type，让路由器自动检测
    )
    
    # 生成所有章节
    sections = await notebook_creator.create_all_sections()
    
    # 确保所有章节都没有练习题（知识库不需要）
    for section in sections.values():
        section.exercises = []
    
    # 创建NoteBookAgent实例
    new_notebook = NoteBookAgent(
        outline=outline,
        sections=sections,
        notebook_title=outline.notebook_title,
        parent_agent_id=parent_agent_id,
        DB_PATH=DB_PATH
    )
    
    success_message = f"成功创建知识库notebook agent (ID: {new_notebook.id[:8]}...), 内容已生成（知识库策略，无练习题）"
    return new_notebook, success_message


async def create_outline_first_notebook(
    intent: NotebookCreationIntent,
    outline: Outline,
    parent_agent_id: Optional[str] = None,
    DB_PATH: Optional[str] = None,
    output_path: Optional[str] = None
) -> Tuple[NoteBookAgent, str]:
    """
    策略4: 大纲优先创建笔记本（从主题创建）
    
    适用于：只有主题描述，根据已确认的大纲生成内容
    
    Args:
        intent: 创建意图
        outline: 已确认的大纲
        parent_agent_id: 父agent ID
        DB_PATH: 数据库路径
        output_path: 输出路径
        
    Returns:
        (NoteBookAgent实例, 成功消息)
    """
    
    # 生成输出路径
    if not output_path:
        topic_safe = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in (intent.topic_or_theme or outline.notebook_title))
        topic_safe = topic_safe[:50].strip().replace(' ', '_')
        output_path = f"./{topic_safe}_notebook.md"
    
    # 创建notebook生成器（使用新架构，无文件模式）
    notebook_creator = NotebookCreator(
        outline=outline,
        file_path=None,  # 无文件，从零生成
        output_path=output_path,
        force_creator_type='from_scratch'  # 明确使用 from_scratch 创建器
    )
    
    # 生成所有章节
    sections = await notebook_creator.create_all_sections()
    
    # 创建NoteBookAgent实例
    new_notebook = NoteBookAgent(
        outline=outline,
        sections=sections,
        notebook_title=outline.notebook_title,
        parent_agent_id=parent_agent_id,
        DB_PATH=DB_PATH
    )
    
    success_message = f"成功创建notebook agent (ID: {new_notebook.id[:8]}...), 内容已生成（大纲优先策略）"
    return new_notebook, success_message

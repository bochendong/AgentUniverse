"""NotebookCreationStrategies - 不同的笔记本创建策略"""

import os
import asyncio
from typing import Optional, Dict, Tuple
from agents import Runner

from backend.agent.NoteBookAgent import NoteBookAgent
from backend.agent.specialized.NoteBookCreator import (
    OutlineMakerAgent,
    NoteBookAgentCreator,
    get_file_content
)
from backend.agent.specialized.NotebookModels import (
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
    
    # 创建notebook生成agent
    notebook_creator = NoteBookAgentCreator(
        outline=outline,
        file_path=intent.file_path,
        output_path=output_path
    )
    
    # 生成所有章节（并行处理）
    all_sections = list(outline.outlines.items())
    
    async def create_section_with_logging(
        notebook_creator, 
        section_title: str, 
        section_desc: str, 
        idx: int, 
        total: int
    ) -> Tuple[str, Optional[Section], Optional[Exception]]:
        """创建单个章节并返回结果"""
        try:
            section_data = await notebook_creator._create_section(
                section_title=section_title,
                section_description=section_desc
            )
            return (section_title, section_data, None)
        except Exception as e:
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
    
    results = await asyncio.gather(*section_tasks, return_exceptions=False)
    
    # 处理结果
    for section_title, section_data, error in results:
        if error is None and section_data is not None:
            notebook_creator.sections[section_title] = section_data
        else:
            print(f"  警告: 章节 '{section_title}' 未能成功生成，将被跳过")
    
    sections = notebook_creator.sections
    
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
    
    # 创建notebook生成agent（使用增强模式）
    notebook_creator = NoteBookAgentCreator(
        outline=outline,
        file_path=intent.file_path,
        output_path=output_path
    )
    
    # 修改_create_section方法以支持增强模式（通过修改instructions）
    # 注意：这里我们需要创建一个增强版本的section创建方法
    # 由于NoteBookAgentCreator的设计，我们需要在创建时传递增强指令
    
    # 生成所有章节（并行处理）
    all_sections = list(outline.outlines.items())
    
    async def create_enhanced_section(
        notebook_creator, 
        section_title: str, 
        section_desc: str, 
        idx: int, 
        total: int
    ) -> Tuple[str, Optional[Section], Optional[Exception]]:
        """创建增强的章节内容"""
        try:
            # 增强section描述，添加内容增强要求
            enhanced_description = f"""{section_desc}

【重要：内容增强要求】
这是一个内容增强任务。原文档内容可能不够丰满，你必须：
1. 从原文档中提取相关的基础内容和概念
2. **大量补充**：添加详细的定义说明、更多例子（每个概念至少3-5个例子）、详细解释、完整的证明步骤等
3. 如果原文档只有概念名称或关键词，需要补充完整的定义和详细说明
4. 如果原文档缺少例子，必须添加3-5个相关例子（包括各种类型的题目：选择题、填空题、证明题等）
5. 如果原文档缺少练习题，必须为每个主要概念添加至少2-3个练习题
6. 确保内容充实、详细、完整，适合系统性学习
7. 不要只依赖原文档的稀疏内容，要主动补充和扩展，使内容达到完整学习材料的标准"""
            
            # 使用增强的描述调用_create_section
            section_data = await notebook_creator._create_section(
                section_title=section_title,
                section_description=enhanced_description
            )
            
            return (section_title, section_data, None)
        except Exception as e:
            return (section_title, None, e)
    
    # 并行生成所有章节
    section_tasks = [
        create_enhanced_section(
            notebook_creator, 
            section_title, 
            section_desc, 
            idx + 1, 
            len(all_sections)
        )
        for idx, (section_title, section_desc) in enumerate(all_sections)
    ]
    
    results = await asyncio.gather(*section_tasks, return_exceptions=False)
    
    # 处理结果
    for section_title, section_data, error in results:
        if error is None and section_data is not None:
            notebook_creator.sections[section_title] = section_data
        else:
            print(f"  警告: 章节 '{section_title}' 未能成功生成，将被跳过")
    
    sections = notebook_creator.sections
    
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
    
    # 创建知识库型内容生成agent（不需要练习题）
    # 我们需要创建一个特殊的section creator，不生成exercises
    notebook_creator = NoteBookAgentCreator(
        outline=outline,
        file_path=intent.file_path,
        output_path=output_path
    )
    
    # 生成所有章节（使用知识库模式）
    all_sections = list(outline.outlines.items())
    
    async def create_knowledge_base_section(
        notebook_creator, 
        section_title: str, 
        section_desc: str, 
        idx: int, 
        total: int
    ) -> Tuple[str, Optional[Section], Optional[Exception]]:
        """创建知识库型章节（不包含练习题）"""
        try:
            # 使用原始的_create_section方法，但我们需要在生成后移除exercises
            section_data = await notebook_creator._create_section(
                section_title=section_title,
                section_description=section_desc
            )
            
            # 移除练习题（知识库不需要）
            section_data.exercises = []
            
            # 同时简化examples，只保留必要的说明性例子，不需要题目型的例子
            # 可以保留examples，但应该更多是说明性的，而不是练习题
            
            return (section_title, section_data, None)
        except Exception as e:
            return (section_title, None, e)
    
    # 并行生成所有章节
    section_tasks = [
        create_knowledge_base_section(
            notebook_creator, 
            section_title, 
            section_desc, 
            idx + 1, 
            len(all_sections)
        )
        for idx, (section_title, section_desc) in enumerate(all_sections)
    ]
    
    results = await asyncio.gather(*section_tasks, return_exceptions=False)
    
    # 处理结果
    for section_title, section_data, error in results:
        if error is None and section_data is not None:
            notebook_creator.sections[section_title] = section_data
        else:
            print(f"  警告: 章节 '{section_title}' 未能成功生成，将被跳过")
    
    sections = notebook_creator.sections
    
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
    
    # 大纲已确认，开始生成内容
    # 注意：这种情况下没有原始文件，我们需要根据大纲和主题生成内容
    # 这里我们需要一个特殊的content generator，不依赖文件
    
    # 暂时使用空的文件路径（我们需要修改NoteBookAgentCreator支持无文件模式）
    # 为了兼容性，我们创建一个临时文件或者修改creator支持无文件模式
    # 这里我们采用一个简化的方法：创建一个基于主题的内容生成
    
    # 生成输出路径
    if not output_path:
        topic_safe = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in (intent.topic_or_theme or outline.notebook_title))
        topic_safe = topic_safe[:50].strip().replace(' ', '_')
        output_path = f"./{topic_safe}_notebook.md"
    
    # 创建基于主题的内容生成agent
    # 由于NoteBookAgentCreator需要文件路径，我们这里创建一个简化版本
    # 或者，我们可以传递一个包含主题信息的"虚拟文件内容"
    
    # 为了兼容现有代码，我们创建一个临时文件
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
    temp_file.write(f"# {outline.notebook_title}\n\n{outline.notebook_description}\n\n")
    if intent.topic_or_theme:
        temp_file.write(f"主题: {intent.topic_or_theme}\n")
    temp_file.write(f"用户描述: {intent.user_description}\n")
    temp_file.close()
    temp_file_path = temp_file.name
    
    try:
        # 创建notebook生成agent
        notebook_creator = NoteBookAgentCreator(
            outline=outline,
            file_path=temp_file_path,
            output_path=output_path
        )
        
        # 生成所有章节（并行处理）
        all_sections = list(outline.outlines.items())
        
        async def create_section_from_topic(
            notebook_creator, 
            section_title: str, 
            section_desc: str, 
            idx: int, 
            total: int
        ) -> Tuple[str, Optional[Section], Optional[Exception]]:
            """从主题创建章节内容（不依赖原始文件）"""
            try:
                section_data = await notebook_creator._create_section(
                    section_title=section_title,
                    section_description=section_desc
                )
                return (section_title, section_data, None)
            except Exception as e:
                return (section_title, None, e)
        
        # 并行生成所有章节
        section_tasks = [
            create_section_from_topic(
                notebook_creator, 
                section_title, 
                section_desc, 
                idx + 1, 
                len(all_sections)
            )
            for idx, (section_title, section_desc) in enumerate(all_sections)
        ]
        
        results = await asyncio.gather(*section_tasks, return_exceptions=False)
        
        # 处理结果
        for section_title, section_data, error in results:
            if error is None and section_data is not None:
                notebook_creator.sections[section_title] = section_data
            else:
                print(f"  警告: 章节 '{section_title}' 未能成功生成，将被跳过")
        
        sections = notebook_creator.sections
        
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
        
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_file_path)
        except Exception:
            pass

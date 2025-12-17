"""Tool for creating notebook agents from files."""

import os
from typing import Optional, Tuple
from agents import Runner

from backend.agent.NoteBookAgent import NoteBookAgent
from backend.agent.specialized.NoteBookCreator import (
    OutlineMakerAgent,
    NoteBookAgentCreator,
)


async def create_notebook_agent_from_file(
    file_path: str,
    parent_agent_id: Optional[str] = None,
    DB_PATH: Optional[str] = None,
    output_path: Optional[str] = None
) -> Tuple[NoteBookAgent, str]:
    """
    Create a notebook agent from a file by generating outline and sections.
    
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
    
    # 生成所有章节
    all_sections = list(outline.outlines.keys())
    print(f"\n开始生成 {len(all_sections)} 个章节...\n")
    
    for idx, (section_title, section_desc) in enumerate(outline.outlines.items(), 1):
        print(f"[{idx}/{len(all_sections)}] 正在生成章节: {section_title}...")
        try:
            section_data = await notebook_creator._create_section(
                section_title=section_title,
                section_description=section_desc
            )
            print(f"  ✓ 章节 '{section_title}' 生成完成")
        except Exception as e:
            print(f"  ✗ 章节 '{section_title}' 生成失败: {str(e)}")
    
    print(f"\n✓ 所有章节生成完成！\n")
    
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

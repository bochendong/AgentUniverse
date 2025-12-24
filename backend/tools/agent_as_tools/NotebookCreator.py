"""NotebookCreator - 笔记本创建器（新架构）

使用 SectionCreatorRouter 根据文件类型和质量自动选择合适的章节创建器。
"""

import os
import asyncio
from typing import Optional, Dict
from backend.models import Outline, Section
from .section_creators import SectionCreatorRouter


class NotebookCreator:
    """笔记本创建器
    
    根据大纲创建完整的笔记本内容，使用路由器自动选择合适的章节创建策略。
    """
    
    def __init__(
        self,
        outline: Outline,
        file_path: Optional[str] = None,
        output_path: Optional[str] = None,
        force_creator_type: Optional[str] = None
    ):
        """初始化笔记本创建器
        
        Args:
            outline: 笔记本大纲
            file_path: 文件路径（如果有）
            output_path: 输出路径（可选）
            force_creator_type: 强制使用指定的创建器类型（用于测试或特殊场景）
        """
        self.outline = outline
        self.file_path = file_path
        self.output_path = output_path
        self.sections: Dict[str, Section] = {}
        
        # 创建路由器
        self.router = SectionCreatorRouter(
            outline=outline,
            file_path=file_path,
            force_creator_type=force_creator_type
        )
    
    async def create_all_sections(self) -> Dict[str, Section]:
        """创建所有章节
        
        Returns:
            章节字典，键为章节标题，值为 Section 对象
        """
        all_sections = list(self.outline.outlines.items())
        total = len(all_sections)
        
        # 获取创建器
        creator = self.router.get_creator()
        creator_type = creator.get_creator_type()
        
        print(f"\n[NotebookCreator] 使用创建器类型: {creator_type}")
        print(f"[NotebookCreator] 开始创建 {total} 个章节...\n")
        
        # 并行创建所有章节
        async def create_section_with_logging(
            section_title: str,
            section_desc: str,
            idx: int
        ) -> tuple[str, Optional[Section], Optional[Exception]]:
            """创建单个章节并返回结果"""
            try:
                print(f"[{idx}/{total}] 正在创建章节: {section_title}")
                section_data = await creator.create_section(
                    section_title=section_title,
                    section_description=section_desc,
                    section_index=idx,
                    total_sections=total
                )
                print(f"[{idx}/{total}] ✓ 章节 '{section_title}' 创建完成\n")
                return (section_title, section_data, None)
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"[{idx}/{total}] ✗ 章节 '{section_title}' 创建失败: {e}\n{error_trace}\n")
                return (section_title, None, e)
        
        # 并行生成所有章节
        section_tasks = [
            create_section_with_logging(section_title, section_desc, idx + 1)
            for idx, (section_title, section_desc) in enumerate(all_sections)
        ]
        
        results = await asyncio.gather(*section_tasks, return_exceptions=False)
        
        # 处理结果
        for section_title, section_data, error in results:
            if error is None and section_data is not None:
                self.sections[section_title] = section_data
            else:
                print(f"  警告: 章节 '{section_title}' 未能成功生成，将被跳过")
        
        print(f"\n[NotebookCreator] 章节创建完成，成功: {len(self.sections)}/{total}")
        
        return self.sections
    
    def write_to_file(self) -> str:
        """将生成的章节内容写入文件
        
        Returns:
            成功消息
        """
        if not self.output_path:
            return "未指定输出路径，无法写入文件"
        
        try:
            # 从已生成的 sections 生成标准 markdown（使用与 NoteBookAgent 相同的方法）
            from backend.tools.utils import generate_markdown_from_agent
            
            # 创建一个临时的 NoteBookAgent-like 对象来生成 markdown
            if self.sections and self.outline:
                # 生成标准格式的 markdown（包含 XML 标签）
                markdown = generate_markdown_from_agent(type('TempAgent', (), {
                    'outline': self.outline,
                    'sections': self.sections,
                    'notebook_title': self.outline.notebook_title
                })(), include_ids=True)
            else:
                return "没有可写入的内容，请先调用 create_all_sections()"
            
            # 确保输出目录存在
            output_dir = os.path.dirname(self.output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            with open(self.output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            return f"文件已成功写入到: {self.output_path}"
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return f"写入文件时出错: {str(e)}\n{error_trace}"


# 向后兼容：保留 OutlineMakerAgent（用于生成大纲）
from agents import Agent, Runner, AgentOutputSchema
from backend.config.model_config import get_model_settings, get_model_name
from .section_creators.utils import get_file_content


class OutlineMakerAgent(Agent):
    """
    接受一个文件路径（word document 或 markdown document），输出一个大纲结构
    生成 5-6 个主要章节，覆盖该主题的核心内容
    """
    
    def __init__(self, file_path: str):
        self.name = "OutlineMakerAgent"
        self.file_path = file_path
        file_content = get_file_content(file_path)
        
        instructions = f"""
你是一个专业的内容分析专家。请分析文档内容，生成一个清晰、详细的学习大纲。

**文档内容**

{file_content}

**任务要求**

1. **生成笔记本描述（notebook_description）**：
   - 描述这个笔记本包含什么知识领域、核心概念和主题
   - 明确说明不包含哪些内容，确定笔记本的知识边界
   - 说明这个笔记本在整个知识体系中的定位
   - 长度建议：200-300字

2. **生成 5-6 个主要章节的大纲**，每个章节应该：

   - **描述详细明确**：说明包含哪些定义、概念、关键词、例子、定理、证明，以及明确说明不包含哪些内容
   
   - **边界清晰**：章节之间不重叠、不遗漏，每个内容只属于一个章节
   
   - **长度合理**：每个章节包含2-4个主要概念，不超过原文档的1/3，至少包含一个完整主题
   
   - **逻辑递进**：从基础到进阶，第一个章节只包含最基础的定义和概念

**输出格式**

{{
  "notebook_title": "文档标题（字符串）",
  "notebook_description": "笔记本描述（字符串，200-300字），说明包含什么知识、不包含什么知识、知识边界和定位",
  "outlines": {{
    "章节名称1": "详细的章节描述（字符串，至少100字）",
    "章节名称2": "详细的章节描述（字符串，至少100字）",
    ...
  }}
}}

**数据类型要求**

- notebook_title: 字符串
- notebook_description: 字符串，200-300字，描述知识边界和定位
- outlines: 字典，键和值都是字符串
- 章节描述必须是字符串，不能是字典或对象
- 每个章节描述至少100字，明确说明包含和不包含的内容
"""
        
        # Get model settings from config
        model_name = get_model_name()
        model_settings = get_model_settings()
        
        super().__init__(
            name="OutlineMakerAgent",
            instructions=instructions,
            output_type=AgentOutputSchema(Outline, strict_json_schema=False),
            model=model_name,
            model_settings=model_settings
        )

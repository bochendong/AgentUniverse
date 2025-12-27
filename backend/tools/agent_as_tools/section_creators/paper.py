"""Paper Section Creator - 处理论文"""

from typing import Optional
from agents import Agent, Runner, AgentOutputSchema
from backend.models import Outline, Section
from backend.config.model_config import get_section_maker_model_settings, get_model_name
from .base import BaseSectionCreator
from .utils import get_file_content


class PaperSectionCreator(BaseSectionCreator):
    """处理论文的创建器
    
    适用于：
    - 用户上传的是学术论文（PDF）
    - 主要任务是提取论文中的知识点、方法、结论等
    - 不需要练习题，主要是知识记录
    """
    
    def get_creator_type(self) -> str:
        return "paper"
    
    async def create_section(
        self,
        section_title: str,
        section_description: str,
        section_index: int,
        total_sections: int
    ) -> Section:
        """从论文中提取章节内容"""
        
        if not self.file_path:
            raise ValueError("PaperSectionCreator 需要文件路径")
        
        # 读取文件内容（支持PDF、DOCX、MD等格式）
        try:
            file_content = get_file_content(self.file_path)
        except Exception as e:
            # 如果文件读取失败，抛出异常
            raise ValueError(f"无法读取文件内容: {self.file_path}, 错误: {str(e)}")
        
        # 获取所有章节信息
        all_sections = list(self.outline.outlines.keys())
        
        # 构建 prompt
        notebook_desc = self.notebook_description or '（未提供笔记本描述）'
        section_list = '\n'.join([
            f"  {i+1}. {title}: {desc[:60]}..." 
            for i, (title, desc) in enumerate(self.outline.outlines.items())
        ])
        
        instructions = f"""
你是一个专业的学术论文分析专家。从论文中提取知识点，生成结构化的知识记录（不是学习材料，而是知识库）。

**笔记本整体描述**

{notebook_desc}

**章节信息**

- 标题: {section_title}
- 描述: {section_description}
- 位置: 第 {section_index}/{total_sections} 章

**章节边界**

- 严格按照笔记本整体描述和章节描述提取内容，只包含属于此章节的内容
- 确保内容符合笔记本的知识边界（参考上面的笔记本整体描述）
- 参考所有章节列表，避免重复：

{section_list}

**论文内容**

{file_content}

**提取要求**

1. **提取知识点**：
   - 识别论文中与本章节相关的核心概念、方法、结论等
   - 提取关键定义、定理、算法、实验结果等
   - 记录重要的数学公式、符号说明等

2. **组织结构**：
   - 将提取的内容组织成清晰的概念块（ConceptBlock）
   - 每个概念块包含：definition（定义/说明）、notes（重要笔记）、theorems（定理/结论）
   - **不需要练习题（exercises）**

3. **内容完整性**：
   - 确保提取的内容完整、准确
   - 保持论文中的关键信息
   - 可以适当补充说明，帮助理解

**输出结构**

返回一个 Section 对象，包含：

1. **introduction**（介绍）：本章节在论文中的位置、主要内容概述

2. **concept_blocks**（概念块列表）：
   - 每个概念块包含：
     * **definition**：概念定义、方法说明、关键信息
     * **notes**：重要笔记、注意事项、实验结果等
     * **theorems**：定理、结论、重要公式等（包含 proof 和 examples）
   - **不需要 examples（例子）**，因为这是知识记录，不是学习材料

3. **standalone_notes**（独立笔记，可选）：不属于特定定义的笔记

4. **summary**（总结）：本章节的关键要点、重要结论

5. **exercises**（练习题）：**留空，知识库不需要练习题**

**重要要求**：
- 这是知识记录，不是学习材料
- 重点在于知识点的组织、分类和记录
- 不需要练习题、选择题等学习元素
- 保持论文中的关键信息，确保准确性
"""
        
        # 创建 Agent
        model_name = get_model_name()
        model_settings = get_section_maker_model_settings()
        
        section_agent = Agent(
            instructions=instructions,
            name=section_title,
            model=model_name,
            output_type=AgentOutputSchema(Section, strict_json_schema=False),
            model_settings=model_settings
        )
        
        # 生成章节
        response = await Runner.run(
            section_agent,
            f"请从论文中提取章节 '{section_title}' 的知识点"
        )
        
        section_data = response.final_output
        
        # 确保没有练习题（知识库不需要）
        section_data.exercises = []
        
        return section_data


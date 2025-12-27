"""Well Formed Note Section Creator - 处理完善的笔记"""

from typing import Optional
from agents import Agent, Runner, AgentOutputSchema
from backend.models import Outline, Section
from backend.config.model_config import get_section_maker_model_settings, get_model_name
from .base import BaseSectionCreator
from .utils import get_file_content

# 导入公共 prompt 片段
from backend.prompts.common_prompt_snippets import (
    QUESTION_TYPE_REQUIREMENTS,
    PROOF_QUALITY_REQUIREMENTS,
    SECTION_OUTPUT_STRUCTURE,
    CONCEPT_BLOCKS_BASIC_REQUIREMENTS
)


class WellFormedNoteSectionCreator(BaseSectionCreator):
    """处理完善笔记的创建器
    
    适用于：
    - 用户上传的笔记内容完善、结构清晰
    - 内容已经有详细定义、例子、证明等
    - 主要任务是提取和结构化，可能只需要少量优化
    """
    
    def get_creator_type(self) -> str:
        return "well_formed_note"
    
    async def create_section(
        self,
        section_title: str,
        section_description: str,
        section_index: int,
        total_sections: int
    ) -> Section:
        """从完善的笔记中提取和结构化章节内容"""
        
        if not self.file_path:
            raise ValueError("WellFormedNoteSectionCreator 需要文件路径")
        
        # 读取文件内容
        file_content = get_file_content(self.file_path)
        
        # 获取所有章节信息
        all_sections = list(self.outline.outlines.keys())
        
        # 构建 prompt
        notebook_desc = self.notebook_description or '（未提供笔记本描述）'
        section_list = '\n'.join([
            f"  {i+1}. {title}: {desc[:60]}..." 
            for i, (title, desc) in enumerate(self.outline.outlines.items())
        ])
        
        instructions = f"""
你是一个专业的教育内容创作者。从原始文档中提取并优化章节内容，生成结构化的学习材料。

**笔记本整体描述**

{notebook_desc}

**章节信息**

- 标题: {section_title}
- 描述: {section_description}
- 位置: 第 {section_index}/{total_sections} 章

**章节边界**

- 严格按照笔记本整体描述和章节描述提取内容，只包含属于此章节的内容
- 确保内容符合笔记本的知识边界（参考上面的笔记本整体描述）
- 如果章节描述或笔记本描述明确说"不包含XXX"，则XXX不应出现
- 参考所有章节列表，避免重复：

{section_list}

**原始文档**

{file_content}

**内容定位与提取（重要，必须严格执行）**

在开始提取内容之前，你必须先在整个原始文档中搜索和定位所有与本章节相关的内容：

1. **关键词搜索**：
   - 根据章节标题（"{section_title}"）中的关键词，在原始文档中搜索相关内容
   - 根据章节描述中的关键词和概念，在原始文档中搜索相关内容
   - 注意：相关内容可能分散在文档的不同位置，必须仔细查找

2. **内容识别**：
   - 识别所有与本章节相关的段落、定义、例子、笔记、定理、证明、练习题等
   - 即使内容在文档中的表述方式与章节标题不完全一致，只要内容相关就应该提取
   - 例如：如果章节标题是"整数存储"，而文档中用的是"Integer（整数）"，两者都应该被视为相关内容

3. **完整性检查**：
   - 列出所有在原始文档中找到的相关内容点
   - 确保没有遗漏任何相关内容
   - 如果发现某些内容可能属于本章节但不确定，应该提取并保留（可以后续优化）

4. **章节边界判断**：
   - 参考所有章节列表，避免与其他章节的内容重复
   - 如果某个内容可能属于多个章节，根据章节描述的匹配度和内容的相关性来判断

**内容提取与优化**

1. **完整性**：基于上述定位结果，提取所有属于此章节的定义、例子、笔记、定理、证明等，确保没有遗漏任何已定位的内容

2. **内容关联**：定义后面紧跟着的例子/笔记/定理/证明 → 关联到该定义

3. **内容增强**：
   - 如果定义不够清晰，补充说明和解释
   - 如果例子缺少解答，补充完整解答步骤
   - 如果内容已经很完善，保持原样，只做格式优化

{SECTION_OUTPUT_STRUCTURE}

{CONCEPT_BLOCKS_BASIC_REQUIREMENTS}

**提取场景的特殊要求**：
- 如果原文档中只有定理没有明确定义，应该将定理关联到相关的定义，或者为该定理创建一个包含相关定义说明的concept_block

{QUESTION_TYPE_REQUIREMENTS}

{PROOF_QUALITY_REQUIREMENTS}

**重要要求**：
- 保持原文档的核心内容和格式
- 如果原文档中某个定义后面有多个例子，必须全部提取
- 如果原文档中有定理和证明标记，且与章节相关，必须提取
- 按照原文档顺序组织内容：定义 → 相关例子/笔记/定理/证明 → 下一个定义
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
            f"请为章节 '{section_title}' 提取并优化内容"
        )
        
        section_data = response.final_output
        
        # 注意：根据重构方案，这里不再调用 RefinementOrchestrator
        # 优化将在 NotebookAgent 创建后统一进行（通过 ContentEvaluationAgent 评估后修复）
        
        return section_data


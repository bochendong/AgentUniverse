"""From Scratch Section Creator - 从零生成章节内容"""

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
    CODE_AND_MATH_FORMAT_REQUIREMENTS,
    SECTION_OUTPUT_STRUCTURE,
    CONCEPT_BLOCKS_DETAILED_REQUIREMENTS_FROM_SCRATCH,
    EXERCISES_DETAILED_REQUIREMENTS_FROM_SCRATCH
)


class FromScratchSectionCreator(BaseSectionCreator):
    """从零生成章节内容的创建器
    
    适用于：
    - 用户没有上传任何文件
    - 用户上传的文件内容质量较低，需要完全重新生成
    """
    
    def get_creator_type(self) -> str:
        return "from_scratch"
    
    async def create_section(
        self,
        section_title: str,
        section_description: str,
        section_index: int,
        total_sections: int
    ) -> Section:
        """从零生成章节内容"""
        
        # 获取文件内容（如果有，作为参考）
        file_content = ""
        has_reference = False
        if self.file_path:
            try:
                file_content = get_file_content(self.file_path)
                has_reference = True
            except Exception:
                file_content = ""
        
        # 获取所有章节信息
        all_sections = list(self.outline.outlines.keys())
        
        # 构建 prompt
        notebook_desc = self.notebook_description or '（未提供笔记本描述）'
        section_list = '\n'.join([
            f"  {i+1}. {title}: {desc[:60]}..." 
            for i, (title, desc) in enumerate(self.outline.outlines.items())
        ])
        
        # 根据是否有参考文件，生成不同的指导
        if has_reference:
            reference_instructions = f"""
**参考文档（可选）**

以下内容来自用户上传的文件，你可以参考，但**必须根据章节描述和笔记本描述生成完整的内容**，不能只依赖参考文档：

{file_content[:2000]}{'...' if len(file_content) > 2000 else ''}

**重要**：参考文档可能内容不完整或质量不高，你需要：
1. 识别参考文档中与本章节相关的内容
2. **补充和完善**：添加详细的定义、例子、说明、练习题等
3. 确保生成的内容完整、准确、适合学习
"""
        else:
            reference_instructions = """
**⚠️ 重要：无原始文档模式**

当前没有提供原始文档，你需要**从零开始生成**完整的章节内容。这是创建高质量学习笔记的关键时刻。
"""
        
        instructions = f"""
你是一个专业的教育内容创作者。从零开始生成完整的章节内容，生成结构化的学习材料。

**笔记本整体描述**

{notebook_desc}

**章节信息**

- 标题: {section_title}
- 描述: {section_description}
- 位置: 第 {section_index}/{total_sections} 章

**章节边界**

- 严格按照笔记本整体描述和章节描述生成内容，只包含属于此章节的内容
- 确保内容符合笔记本的知识边界（参考上面的笔记本整体描述）
- 如果章节描述或笔记本描述明确说"不包含XXX"，则XXX不应出现
- 参考所有章节列表，避免重复：

{section_list}

{reference_instructions}

**生成要求（必须严格遵守）**

1. **必须生成完整的 ConceptBlock（概念块）**：
   - 根据章节标题和描述，识别本章节需要讲解的**所有核心概念**
   - 为每个核心概念创建一个 ConceptBlock，包含：
     * **definition（定义）**：清晰、准确、完整的定义，必须包含所有关键要素
     * **examples（例子）**：每个定义至少包含1-2个例子，帮助理解
     * **notes（笔记）**：补充说明、注意事项、常见误区等
     * **theorems（定理）**：如果概念有相关定理，包含定理和详细证明
   
2. **内容完整性**：
   - 不能只生成证明题，必须包含：
     * 基础概念的定义（ConceptBlock）
     * 理解性例子（选择题、填空题、简答题）
     * 应用性例子（代码题，如果适用）
     * 进阶内容（证明题、定理）
   - 确保内容从易到难，循序渐进

3. **内容质量**：
   - 定义必须准确、完整，不能省略关键要素
   - 例子必须具体、易懂，帮助理解概念
   - 说明必须清晰，解释为什么、怎么用、注意什么

{CODE_AND_MATH_FORMAT_REQUIREMENTS}

{SECTION_OUTPUT_STRUCTURE}

{CONCEPT_BLOCKS_DETAILED_REQUIREMENTS_FROM_SCRATCH}

{EXERCISES_DETAILED_REQUIREMENTS_FROM_SCRATCH}

{QUESTION_TYPE_REQUIREMENTS}

{PROOF_QUALITY_REQUIREMENTS}

**重要要求**：
- 按照逻辑顺序组织内容：基础概念 → 进阶概念 → 应用和练习
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
            f"请为章节 '{section_title}' 创建完整内容"
        )
        
        section_data = response.final_output
        
        # 注意：根据重构方案，这里不再调用 RefinementOrchestrator
        # 优化将在 NotebookAgent 创建后统一进行（通过 ContentEvaluationAgent 评估后修复）
        
        return section_data


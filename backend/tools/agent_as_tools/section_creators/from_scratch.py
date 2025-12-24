"""From Scratch Section Creator - 从零生成章节内容"""

from typing import Optional
from agents import Agent, Runner, AgentOutputSchema
from backend.models import Outline, Section
from backend.config.model_config import get_section_maker_model_settings, get_model_name
from .base import BaseSectionCreator
from .utils import get_file_content


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
        
        # 代码和数学公式格式说明
        code_math_format_instructions = """
**代码和数学公式格式要求（重要）**：
- **代码块**：所有代码必须使用 Markdown 代码块格式
  - 行内代码：使用反引号包裹，如 `code`
  - 代码块：使用三个反引号包裹，并指定语言
- **数学公式**：所有数学公式必须使用 LaTeX 格式
  - **行内公式**：使用单个美元符号包裹，格式为 `$公式内容$`
  - **块级公式**：使用两个美元符号包裹，格式为 `$$公式内容$$`
  - **重要规则**：所有数学符号、变量、集合等都必须在公式标记内
"""
        
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
   
2. **第一章的特殊要求**：
   - 如果这是第一章（位置: 第 1/{total_sections} 章），**必须包含所有基础概念的定义**
   - 不能直接使用高级概念，必须先定义基础概念
   - 例如：如果章节提到"策略 $\\pi$"、"价值函数 $V^{{\\pi}}$"，必须先定义：
     * 什么是强化学习
     * 什么是MDP（马尔可夫决策过程）
     * 什么是策略（policy）
     * 什么是回报（return）
     * 什么是价值函数
   - 每个基础概念都要有独立的 ConceptBlock，包含定义、例子、说明

3. **内容完整性**：
   - 不能只生成证明题，必须包含：
     * 基础概念的定义（ConceptBlock）
     * 理解性例子（选择题、填空题、简答题）
     * 应用性例子（代码题，如果适用）
     * 进阶内容（证明题、定理）
   - 确保内容从易到难，循序渐进

4. **内容质量**：
   - 定义必须准确、完整，不能省略关键要素
   - 例子必须具体、易懂，帮助理解概念
   - 说明必须清晰，解释为什么、怎么用、注意什么

{code_math_format_instructions}

**输出结构**

返回一个 Section 对象，包含：

1. **introduction**（介绍）：为什么学习、有什么用、解决什么问题、在知识体系中的位置
   - **重要**：introduction字段只能包含介绍性文本，**不能包含例子、选择题、练习题、题目等任何需要答题的内容**

2. **concept_blocks**（概念块列表）：
   - **⚠️ 这是最重要的部分，必须严格遵守**：
     * 你必须为章节描述中提到的每个核心概念创建一个 ConceptBlock
     * **每个概念块必须包含一个 definition（定义）字段，这是必需字段，不能为空**
     * **定义必须完整、准确，不能省略关键要素**
     * **每个定义后面必须关联 examples（例子列表），至少1-2个例子帮助理解**
     * **每个定义后面应该关联 notes（笔记列表），说明注意事项、常见误区等**
   
   - **第一章的特殊要求**：
     * 如果这是第一章，必须包含所有基础概念的定义
     * 不能直接使用高级概念（如 $V^{{\\pi}}$、$Q^{{\\pi}}$、$\\pi$），必须先定义基础概念
     * 每个基础概念都要有独立的 ConceptBlock
   
   - 定义后面关联的 examples（例子列表，每个 Example 必须是以下5种题目类型之一）
   - 定义后面关联的 notes（笔记列表）
   - 定义后面关联的 theorems（定理列表，每个 Theorem 包含 theorem、proof、examples）

3. **standalone_examples**（独立例子，可选）

4. **standalone_notes**（独立笔记，可选）

5. **summary**（总结）：如何学好、常见误区、通用解题思路、证明格式、学习建议、关键要点

6. **exercises**（练习题）：每个练习必须是以下5种题目类型之一
   - **⚠️ 重要：练习题必须多样化，不能只有一种类型**
   - **必须包含**：
     * 选择题：至少1-2题，测试基础概念理解
     * 填空题：至少1-2题，测试定义记忆
     * 简答题：至少1-2题，测试概念理解
     * 证明题：根据章节内容决定，但不能只有证明题
     * 代码题：如果适用（如编程相关章节）
   - **第一章的特殊要求**：
     * 必须特别注重基础概念的理解题
     * 不能直接跳到高级证明题
     * 必须先有基础理解题，再有进阶证明题

**题目类型要求（examples 和 exercises 都必须使用以下5种类型之一）**

1. **选择题 (multiple_choice)**：question_type="multiple_choice", question, options (4个), correct_answer, explanation
2. **填空题 (fill_blank)**：question_type="fill_blank", question (使用[空1]、[空2]等占位符), blanks (字典), explanation
3. **证明题 (proof)**：question_type="proof", question, answer, proof (详细步骤), explanation
4. **简答题 (short_answer)**：question_type="short_answer", question, answer, explanation
5. **代码题 (code)**：question_type="code", question, code_answer, explanation

**证明质量要求（重要，必须严格遵守）**：
- 所有proof必须包含详细的中间步骤，不能跳过关键推理
- 必须明确引用使用的公式、定理、定义（要写出具体的公式内容）
- 对于涉及计算的证明，必须展示详细的计算过程
- 每一步推理都要有清晰说明
- 使用标记使步骤清晰（如"步骤1"、"步骤2"）
- 证明必须完整详细，达到教学标准，便于初学者理解
- **所有数学符号、变量、集合等都必须用LaTeX公式标记包裹**

**重要要求**：
- 每个例子和练习都必须明确指定 question_type，不能为null
- 保持题目的多样性和合理性，根据内容特点选择合适的题目类型
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
        
        # 优化内容（使用 RefinementOrchestrator）
        print(f"[优化] 开始优化章节 '{section_title}' 的内容...")
        from backend.tools.agent_as_tools.refinement_agents import RefinementOrchestrator
        orchestrator = RefinementOrchestrator(
            section=section_data,
            section_context=f"{section_description}\n\n章节介绍: {section_data.introduction[:500]}"
        )
        section_data = await orchestrator.refine_all()
        print(f"[优化] 章节 '{section_title}' 内容优化完成")
        
        return section_data


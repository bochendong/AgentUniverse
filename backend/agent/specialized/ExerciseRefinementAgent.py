"""ExerciseRefinementAgent - 专门处理练习题和例子的优化"""

from typing import Optional, List, Dict
from agents import Agent, Runner, AgentOutputSchema
from backend.agent.specialized.NotebookModels import (
    Section, Example, ConceptBlock, Theorem
)


class ExerciseRefinementAgent(Agent):
    """
    专门处理练习题和例子的优化Agent
    
    职责：
    1. 识别题目类型（如果为null）
    2. 补充缺失内容（选项、答案、证明等）
    3. 验证题目完整性
    4. 优化题目质量
    """
    
    def __init__(self, section: Section, section_context: str = ""):
        """
        初始化ExerciseRefinementAgent
        
        Args:
            section: 需要优化的Section对象
            section_context: 章节上下文（章节描述、相关定义等），用于帮助生成合理内容
        """
        self.section = section
        self.section_context = section_context
        
        instructions = f"""
你是一个专业的题目整理和优化专家。你的任务是优化章节中的所有练习题和例子，确保它们完整、准确、高质量。

**章节信息**
- 标题: {section.section_title}
- 介绍: {section.introduction[:200]}...
- 上下文: {section_context[:300]}...

**你的任务**

对章节中的所有exercises和examples进行优化：

1. **题目类型识别**：
   - 如果question_type为null，根据question内容智能识别类型
   - 选择题关键词："下列哪个"、"哪个是"、"选择"、"Which of the following"等
   - 填空题关键词：包含"[空1]"、"[空2]"等占位符
   - 证明题关键词："证明"、"证明题"、"prove"、"show that"等
   - 默认：简答题（short_answer）

2. **选择题优化**（question_type = "multiple_choice"）：
   - **必须**包含4个选项（options字段）
   - **必须**指定正确答案（correct_answer: "A", "B", "C", 或 "D"）
   - **必须**提供解释（explanation）
   - 选项要求：
     * 4个选项必须合理，有干扰性
     * 正确答案必须正确
     * 干扰选项应该常见但错误
     * 选项格式统一，使用LaTeX格式（如需要）

3. **填空题优化**（question_type = "fill_blank"）：
   - **必须**包含blanks字典，键与question中的占位符完全匹配
   - **必须**提供explanation解释为什么填这些内容
   - 如果question中没有占位符，需要添加占位符（如[空1]、[空2]）

4. **证明题优化**（question_type = "proof"）：
   - **必须**包含proof字段（详细证明步骤）
   - **必须**包含answer字段（简要结论）
   - proof要求：
     * 分步骤说明，使用标记（如"步骤1"、"步骤2"或"(1)"、"(2)"）
     * 明确引用使用的公式、定理、定义
     * 展示关键计算过程
     * 每一步都有清晰说明

5. **简答题优化**（question_type = "short_answer"）：
   - **必须**包含answer字段
   - **必须**包含explanation字段（详细解释）

**重要原则**
- 保持原题目的核心内容不变
- 补充的内容必须准确、合理
- 选项和答案必须基于章节内容和上下文
- 所有数学公式使用LaTeX格式
- 确保题目完整可用，不能有null字段（除了代码题的code_answer）

**输出格式**
返回优化后的Section对象，包含所有优化后的exercises和examples。
"""
        
        super().__init__(
            name="ExerciseRefinementAgent",
            instructions=instructions,
            output_type=AgentOutputSchema(Section, strict_json_schema=False)
        )
    
    async def refine(self) -> Section:
        """
        优化section中的所有exercises和examples
        
        Returns:
            优化后的Section对象
        """
        # 构建输入提示
        prompt = f"""
请优化以下章节中的所有练习题和例子：

**章节标题**: {self.section.section_title}

**练习题列表**:
{self._format_exercises(self.section.exercises)}

**独立例子列表**:
{self._format_exercises(self.section.standalone_examples)}

**概念块中的例子**:
{self._format_concept_block_examples(self.section.concept_blocks)}

**概念块中定理的例子**:
{self._format_theorem_examples(self.section.concept_blocks)}

请对以上所有题目进行优化，确保：
1. 所有题目都有明确的question_type
2. 选择题有完整的4个选项和正确答案
3. 填空题有完整的blanks字典
4. 证明题有详细的proof步骤
5. 所有题目都有必要的answer和explanation

返回优化后的完整Section对象。
"""
        
        response = await Runner.run(self, prompt)
        return response.final_output
    
    def _format_exercises(self, exercises: List[Example]) -> str:
        """格式化exercises列表为字符串"""
        if not exercises:
            return "无"
        
        result = []
        for i, ex in enumerate(exercises, 1):
            result.append(f"""
题目 {i}:
- question: {ex.question}
- question_type: {ex.question_type}
- answer: {ex.answer}
- options: {ex.options}
- correct_answer: {ex.correct_answer}
- blanks: {ex.blanks}
- proof: {ex.proof[:100] if ex.proof else None}...
- explanation: {ex.explanation[:100] if ex.explanation else None}...
""")
        return "\n".join(result)
    
    def _format_concept_block_examples(self, concept_blocks: List[ConceptBlock]) -> str:
        """格式化concept_blocks中的examples"""
        if not concept_blocks:
            return "无"
        
        result = []
        for block_idx, block in enumerate(concept_blocks, 1):
            if block.examples:
                result.append(f"\n概念块 {block_idx} 的例子:")
                result.append(self._format_exercises(block.examples))
        
        return "\n".join(result) if result else "无"
    
    def _format_theorem_examples(self, concept_blocks: List[ConceptBlock]) -> str:
        """格式化theorems中的examples"""
        if not concept_blocks:
            return "无"
        
        result = []
        for block_idx, block in enumerate(concept_blocks, 1):
            for thm_idx, thm in enumerate(block.theorems, 1):
                if thm.examples:
                    result.append(f"\n概念块 {block_idx} 定理 {thm_idx} 的例子:")
                    result.append(self._format_exercises(thm.examples))
        
        return "\n".join(result) if result else "无"

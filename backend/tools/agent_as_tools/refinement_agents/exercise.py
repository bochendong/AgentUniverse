"""Exercise Refinement Agent - 优化练习题和例子"""

from typing import List
from agents import Agent, Runner, AgentOutputSchema
from backend.models import Section, Example, ConceptBlock
from backend.config.model_config import get_model_settings, get_model_name
from .base import BaseRefinementAgent

# 导入公共 prompt 片段
from backend.prompts.common_prompt_snippets import (
    QUESTION_TYPE_IDENTIFICATION,
    MULTIPLE_CHOICE_REQUIREMENTS,
    FILL_BLANK_REQUIREMENTS,
    PROOF_EXERCISE_REQUIREMENTS,
    SHORT_ANSWER_REQUIREMENTS,
    LATEX_FORMAT_REQUIREMENTS
)


class ExerciseRefinementAgent(BaseRefinementAgent):
    """
    专门处理练习题和例子的优化Agent
    
    职责：
    1. 识别题目类型（如果为null）
    2. 补充缺失内容（选项、答案、证明等）
    3. 验证题目完整性
    4. 优化题目质量
    """
    
    def get_refiner_type(self) -> str:
        return "exercise"
    
    def get_refinement_target(self) -> str:
        return "练习题和例子"
    
    async def refine(self) -> Section:
        """优化section中的所有exercises和examples"""
        
        # 构建 Agent
        model_name = get_model_name()
        model_settings = get_model_settings()
        
        instructions = f"""
你是一个专业的题目整理和优化专家。你的任务是优化章节中的所有练习题和例子，确保它们完整、准确、高质量。

**章节信息**
- 标题: {self.section.section_title}
- 介绍: {self.section.introduction[:200]}...
- 上下文: {self.section_context[:300]}...

**你的任务**

对章节中的所有exercises和examples进行优化：

{QUESTION_TYPE_IDENTIFICATION}

{MULTIPLE_CHOICE_REQUIREMENTS}

{FILL_BLANK_REQUIREMENTS}

{PROOF_EXERCISE_REQUIREMENTS}

{SHORT_ANSWER_REQUIREMENTS}

**重要原则**
- 保持原题目的核心内容不变
- 补充的内容必须准确、合理
- 选项和答案必须基于章节内容和上下文
- {LATEX_FORMAT_REQUIREMENTS}
- 确保题目完整可用，不能有null字段（除了代码题的code_answer）

**输出格式**
返回优化后的Section对象，包含所有优化后的exercises和examples。
"""
        
        exercise_agent = Agent(
            name="ExerciseRefinementAgent",
            instructions=instructions,
            output_type=AgentOutputSchema(Section, strict_json_schema=False),
            model=model_name,
            model_settings=model_settings
        )
        
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
        
        response = await Runner.run(exercise_agent, prompt)
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



"""Proof Refinement Agent - 优化证明"""

from typing import List
from agents import Agent, Runner, AgentOutputSchema
from backend.models import Section, ConceptBlock
from backend.config.model_config import get_model_settings, get_model_name
from .base import BaseRefinementAgent


class ProofRefinementAgent(BaseRefinementAgent):
    """
    专门处理证明的优化Agent
    
    职责：
    1. 检查证明完整性
    2. 补充中间步骤
    3. 添加公式引用
    4. 优化证明结构
    """
    
    def get_refiner_type(self) -> str:
        return "proof"
    
    def get_refinement_target(self) -> str:
        return "证明"
    
    async def refine(self) -> Section:
        """优化section中的所有proof"""
        
        # 构建 Agent
        model_name = get_model_name()
        model_settings = get_model_settings()
        
        instructions = f"""
你是一个专业的数学证明优化专家。你的任务是优化章节中的所有证明，确保它们详细、清晰、易于理解。

**章节信息**
- 标题: {self.section.section_title}
- 介绍: {self.section.introduction[:200]}...
- 上下文: {self.section_context[:300]}...

**你的任务**

对章节中的所有proof进行优化：

1. **Theorem的proof优化**（concept_blocks中的theorems）：
   - 检查proof是否存在且完整
   - 如果proof过于简略，补充详细步骤
   - 确保包含：
     * 分步骤说明（使用"步骤1"、"步骤2"或"(1)"、"(2)"标记）
     * 明确引用使用的公式、定理、定义（不能只说"根据公式"，要具体说明）
     * 展示关键计算过程，不能省略中间步骤
     * 每一步都有清晰的推理说明

2. **Exercise的proof优化**（exercises和examples中question_type="proof"的题目）：
   - 检查proof是否存在且完整
   - 如果proof过于简略，补充详细步骤
   - 确保符合证明题的标准

**证明质量标准**

一个高质量的证明应该：
- ✅ 有清晰的步骤划分和标记
- ✅ 明确引用公式（如："由公式...可得..."，需要写出具体的公式内容）
- ✅ 展示计算过程（不能只说"根据XX公式得到XX结果"）
- ✅ 每一步都有推理说明
- ✅ 使用LaTeX格式表示数学公式
- ✅ 便于初学者理解

**示例：不好的证明**
> 根据逆元公式，左边为 $ba$，右边为 $ab$，所以 $ab=ba$。

**示例：好的证明**
> **步骤1：** 对等式两边同时取逆。由于在群中，如果两个元素相等，则它们的逆元也相等，列出相应的等式
> 
> **步骤2：** 应用乘积的逆元公式，明确说明使用的公式，并展示计算过程
> - 左边：详细计算步骤
> - 右边：详细计算步骤
> 
> **步骤3：** 得出结论

**重要原则**
- 保持原证明的核心逻辑不变
- 补充的内容必须准确、合理
- 公式引用必须具体明确
- **所有数学公式必须使用LaTeX格式，严格遵循以下规则**：
  * 行内公式：使用单个美元符号 `$...$` 包裹，公式内容不能包含换行符
  * 块级公式：使用两个美元符号 `$$...$$` 包裹，公式前后必须有空行
  * 确保所有数学符号、变量、集合等都用公式标记包裹（例如：有理数集合、自然数集合等都要用公式标记而不是直接写字母）
  * 不要在公式标记内外混用文本，错误做法是直接写"有理数集 Q"，正确做法是"有理数集"后面跟公式标记包裹的数学符号
  * 公式中不要有多余的换行，如果需要多行公式，使用适当的LaTeX环境（如 `align`、`matrix` 等）
- 确保证明达到教学标准，便于初学者理解

**输出格式**
返回优化后的Section对象，包含所有优化后的proof。
"""
        
        proof_agent = Agent(
            name="ProofRefinementAgent",
            instructions=instructions,
            output_type=AgentOutputSchema(Section, strict_json_schema=False),
            model=model_name,
            model_settings=model_settings
        )
        
        # 构建输入提示
        prompt = f"""
请优化以下章节中的所有证明：

**章节标题**: {self.section.section_title}

**定理列表**:
{self._format_theorems(self.section.concept_blocks)}

**证明题列表**:
{self._format_proof_exercises(self.section)}

请对以上所有证明进行优化，确保：
1. 所有证明都有详细的步骤说明
2. 明确引用使用的公式和定理
3. 展示关键计算过程
4. 使用步骤标记使结构清晰
5. 便于初学者理解

返回优化后的完整Section对象。
"""
        
        response = await Runner.run(proof_agent, prompt)
        return response.final_output
    
    def _format_theorems(self, concept_blocks: List[ConceptBlock]) -> str:
        """格式化theorems列表"""
        if not concept_blocks:
            return "无"
        
        result = []
        for block_idx, block in enumerate(concept_blocks, 1):
            for thm_idx, thm in enumerate(block.theorems, 1):
                proof_preview = thm.proof[:200] + "..." if thm.proof and len(thm.proof) > 200 else (thm.proof or "无")
                result.append(f"""
概念块 {block_idx} - 定理 {thm_idx}:
- theorem: {thm.theorem}
- proof: {proof_preview}
""")
        
        return "\n".join(result)
    
    def _format_proof_exercises(self, section: Section) -> str:
        """格式化所有证明题"""
        result = []
        
        # exercises中的证明题
        proof_exercises = [ex for ex in section.exercises if ex.question_type == "proof"]
        if proof_exercises:
            result.append("练习题中的证明题:")
            for i, ex in enumerate(proof_exercises, 1):
                proof_preview = ex.proof[:200] + "..." if ex.proof and len(ex.proof) > 200 else (ex.proof or "无")
                result.append(f"""
  题目 {i}:
  - question: {ex.question}
  - answer: {ex.answer}
  - proof: {proof_preview}
""")
        
        # standalone_examples中的证明题
        proof_examples = [ex for ex in section.standalone_examples if ex.question_type == "proof"]
        if proof_examples:
            result.append("\n独立例子中的证明题:")
            for i, ex in enumerate(proof_examples, 1):
                proof_preview = ex.proof[:200] + "..." if ex.proof and len(ex.proof) > 200 else (ex.proof or "无")
                result.append(f"""
  例子 {i}:
  - question: {ex.question}
  - answer: {ex.answer}
  - proof: {proof_preview}
""")
        
        # concept_blocks中的证明题
        for block_idx, block in enumerate(self.section.concept_blocks, 1):
            proof_examples = [ex for ex in block.examples if ex.question_type == "proof"]
            if proof_examples:
                result.append(f"\n概念块 {block_idx} 中的证明题:")
                for i, ex in enumerate(proof_examples, 1):
                    proof_preview = ex.proof[:200] + "..." if ex.proof and len(ex.proof) > 200 else (ex.proof or "无")
                    result.append(f"""
  例子 {i}:
  - question: {ex.question}
  - answer: {ex.answer}
  - proof: {proof_preview}
""")
        
        return "\n".join(result) if result else "无"


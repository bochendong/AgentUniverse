"""Well Formed Note Section Creator - 处理完善的笔记"""

from typing import Optional
from agents import Agent, Runner, AgentOutputSchema
from backend.models import Outline, Section
from backend.config.model_config import get_section_maker_model_settings, get_model_name
from .base import BaseSectionCreator
from .utils import get_file_content


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

**输出结构**

返回一个 Section 对象，包含：

1. **introduction**（介绍）：为什么学习、有什么用、解决什么问题、在知识体系中的位置
   - **重要**：introduction字段只能包含介绍性文本，**不能包含例子、选择题、练习题、题目等任何需要答题的内容**

2. **concept_blocks**（概念块列表）：
   - **重要**：每个概念块必须包含一个 definition（定义）字段，这是必需字段，不能为空
   - 如果原文档中只有定理没有明确定义，应该将定理关联到相关的定义，或者为该定理创建一个包含相关定义说明的concept_block
   - 定义后面关联的 examples（例子列表，每个 Example 必须是以下5种题目类型之一）
   - 定义后面关联的 notes（笔记列表）
   - 定义后面关联的 theorems（定理列表，每个 Theorem 包含 theorem、proof、examples）

3. **standalone_examples**（独立例子，可选）

4. **standalone_notes**（独立笔记，可选）

5. **summary**（总结）：如何学好、常见误区、通用解题思路、证明格式、学习建议、关键要点

6. **exercises**（练习题）：每个练习必须是以下5种题目类型之一

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
- 如果原文档的证明过于简略，必须补充完整，使其达到教学标准
- **所有数学符号、变量、集合等都必须用LaTeX公式标记包裹**

**重要要求**：
- 每个例子和练习都必须明确指定 question_type，不能为null
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


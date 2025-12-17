"""NotebookAgentCreator - 从文件生成笔记内容的 Agent 系统"""

import os
import uuid
from typing import Optional, List, Literal, Dict
from agents import Agent, Runner, function_tool, AgentOutputSchema
from pydantic import BaseModel, ConfigDict


class Outline(BaseModel):
    """大纲结构"""
    model_config = ConfigDict(strict=False)
    
    notebook_title: str
    notebook_description: str  # 描述笔记本包含什么知识和不包含什么知识，确定笔记本的边界
    outlines: dict[str, str]


class Example(BaseModel):
    """
    例子及其答案、证明
    支持5种题目类型：选择题、填空题、证明题、简答题、代码题
    """
    model_config = ConfigDict(strict=False)
    
    # 题目基本信息
    question_type: Optional[Literal["multiple_choice", "fill_blank", "proof", "short_answer", "code"]] = None  # 题目类型
    question: str  # 题目/例子内容（必需）
    
    # 通用字段
    answer: Optional[str] = None  # 答案内容（通用，用于简答题、填空题等）
    explanation: Optional[str] = None  # 解释（用于选择题、填空题、简答题）
    proof: Optional[str] = None  # 证明步骤（用于证明题）
    
    # 选择题专用字段
    options: Optional[List[str]] = None  # 选项列表（选择题用，4个选项）
    correct_answer: Optional[str] = None  # 正确答案（选择题用，如 "A", "B", "C", "D"）
    
    # 填空题专用字段
    blanks: Optional[Dict[str, str]] = None  # 填空题答案字典（填空题用）
    # 格式：{"[空1]": "答案1", "[空2]": "答案2", ...} 或 {"blank1": "答案1", "blank2": "答案2", ...}
    # 键必须与 question 中的占位符完全匹配
    
    # 代码题专用字段
    code_answer: Optional[str] = None  # 代码答案（代码题用）


class Theorem(BaseModel):
    """定理及其证明"""
    model_config = ConfigDict(strict=False)
    theorem: str  # 定理内容（必需）
    proof: Optional[str] = None  # 证明内容（可选）
    examples: list[Example] = []  # 该定理相关的例子（可选）


class ConceptBlock(BaseModel):
    """概念块：一个定义及其相关的例子、笔记、定理等"""
    model_config = ConfigDict(strict=False)
    definition: str  # 定义（必需）
    examples: list[Example] = []  # 相关例子列表
    notes: list[str] = []  # 相关笔记/注意点（可选）
    theorems: list[Theorem] = []  # 相关定理列表


class Section(BaseModel):
    """章节结构"""
    model_config = ConfigDict(strict=False)
    section_title: str
    introduction: str  # 介绍
    concept_blocks: list[ConceptBlock]  # 概念块列表
    standalone_examples: list[Example] = []  # 独立例子（可选）
    standalone_notes: list[str] = []  # 独立笔记（可选）
    summary: str  # 总结
    exercises: list[Example] = []  # 练习题


def get_file_content(file_path: str) -> str:
    """读取文件内容，支持 .docx 和 .txt/.md 文件"""
    if file_path.endswith('.docx'):
        try:
            from docx import Document
            doc = Document(file_path)
            content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return content
        except ImportError:
            raise ImportError("需要安装 python-docx 库来读取 .docx 文件: pip install python-docx")
    else:
        # 读取文本文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content


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
        
        super().__init__(
            name="OutlineMakerAgent",
            instructions=instructions,
            output_type=AgentOutputSchema(Outline, strict_json_schema=False)
        )


class NoteBookAgentCreator(Agent):
    """
    接受一个 Outline，输出一个完整的 notebook 内容
    每个 section 对应 notebook 中的一个章节
    """
    
    def __init__(self, outline: Outline, file_path: str, output_path: Optional[str] = None):
        self.name = "NoteBookAgentCreator"
        self.outline = outline
        self.file_path = file_path
        self.output_path = output_path
        self.sections = {}
        
        # 创建工具函数
        @function_tool
        def write_to_file(markdown_content: str) -> str:
            """将 markdown 内容写入到指定的输出文件"""
            if not self.output_path:
                return "未指定输出路径，无法写入文件"
            try:
                # 确保输出目录存在
                output_dir = os.path.dirname(self.output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                
                with open(self.output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                return f"文件已成功写入到: {self.output_path}"
            except Exception as e:
                return f"写入文件时出错: {str(e)}"
        
        # 创建章节的辅助方法
        async def _create_section(section_title: str, section_description: str) -> Section:
            """创建章节内容的辅助方法"""
            file_content = get_file_content(self.file_path)
            
            # 获取所有章节信息，帮助判断内容归属
            all_sections = list(self.outline.outlines.keys())
            try:
                current_section_index = all_sections.index(section_title)
            except ValueError:
                current_section_index = -1
            
            # 代码和数学公式格式说明（避免 f-string 中的特殊字符问题）
            code_math_format_instructions = """
4. **代码和数学公式格式要求（重要）**：
   - **代码块**：所有代码必须使用 Markdown 代码块格式
     - 行内代码：使用反引号包裹，如 `code`
     - 代码块：使用三个反引号包裹，并指定语言，如：
       ```
       ```python
       def hello():
           print("Hello")
       ```
       ```
     - 支持的代码块语言标识：python, javascript, java, cpp, c, html, css, sql, json, yaml, bash, shell 等
   
   - **数学公式**：所有数学公式必须使用 LaTeX 格式
     - 行内公式：使用单个美元符号包裹，如 $x^2 + y^2 = r^2$
     - 块级公式：使用两个美元符号包裹，如：
       $$
       \int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
       $$
     - 常用数学符号示例：
       - 分数：$\frac{a}{b}$ 或 $\dfrac{a}{b}$
       - 根号：$\sqrt{x}$ 或 $\sqrt[n]{x}$
       - 求和：$\sum_{i=1}^{n} x_i$
       - 积分：$\int_{a}^{b} f(x) dx$
       - 极限：$\lim_{x \to \infty} f(x)$
       - 矩阵：$\begin{pmatrix} a & b \\ c & d \end{pmatrix}$
   
   - **应用范围**：以下所有字段中的代码和数学公式都必须正确标记：
     - definition（定义）
     - question（题目）
     - answer（答案）
     - explanation（解释）
     - proof（证明）
     - notes（笔记）
     - introduction（介绍）
     - summary（总结）
     - theorem（定理）
"""

            instructions = f"""
你是一个专业的教育内容创作者。从原始文档中提取并优化章节内容，生成结构化的学习材料。

**笔记本整体描述**

{self.outline.notebook_description if hasattr(self.outline, 'notebook_description') and self.outline.notebook_description else '（未提供笔记本描述）'}

**章节信息**

- 标题: {section_title}
- 描述: {section_description}
- 位置: 第 {current_section_index + 1}/{len(all_sections)} 章

**章节边界**

- 严格按照笔记本整体描述和章节描述提取内容，只包含属于此章节的内容
- 确保内容符合笔记本的知识边界（参考上面的笔记本整体描述）
- 如果章节描述或笔记本描述明确说"不包含XXX"，则XXX不应出现
- 参考所有章节列表，避免重复：

{chr(10).join([f"  {i+1}. {title}: {desc[:60]}..." for i, (title, desc) in enumerate(self.outline.outlines.items())])}

**原始文档**

{file_content}

**内容提取与优化**

1. **完整性**：提取所有属于此章节的定义、例子、笔记、定理、证明等，不能遗漏

2. **内容关联**：定义后面紧跟着的例子/笔记/定理/证明 → 关联到该定义

3. **内容增强**：
   - 如果定义不够清晰，补充说明和解释
   - 如果例子缺少解答，补充完整解答步骤
   - 如果证明过于简略，补充中间步骤和推理说明
   - 修复格式问题（特殊字符、数学公式等），使用标准LaTeX格式
   - 改进语言表达，使内容更清晰易懂

{code_math_format_instructions}

**输出结构**

返回一个 Section 对象，包含：

1. **introduction**（介绍）：为什么学习、有什么用、解决什么问题、在知识体系中的位置

2. **concept_blocks**（概念块列表）：
   - **重要**：每个概念块必须包含一个 definition（定义）字段，这是必需字段，不能为空
   - 如果原文档中只有定理没有明确定义，应该将定理关联到相关的定义，或者为该定理创建一个包含相关定义说明的concept_block
   - 定义后面关联的 examples（例子列表，每个 Example 必须是以下5种题目类型之一）
   - 定义后面关联的 notes（笔记列表）
   - 定义后面关联的 theorems（定理列表，每个 Theorem 包含 theorem、proof、examples）
   - 每个concept_block的结构：{{"definition": "定义内容（必需）", "examples": [...], "notes": [...], "theorems": [...]}}

3. **standalone_examples**（独立例子，可选）：不属于特定定义的例子，必须是以下5种题目类型之一

4. **standalone_notes**（独立笔记，可选）：不属于特定定义的笔记

5. **summary**（总结）：如何学好、常见误区、通用解题思路、证明格式、学习建议、关键要点

6. **exercises**（练习题）：每个练习必须是以下5种题目类型之一

**题目类型要求（examples 和 exercises 都必须使用以下5种类型之一）**

每个 Example 对象必须指定 question_type 字段，并包含相应的字段：

1. **选择题 (multiple_choice)**：
   - question_type: "multiple_choice"
   - question: 题目内容
   - options: 4个选项的列表，如 ["选项A内容", "选项B内容", "选项C内容", "选项D内容"]
   - correct_answer: 正确答案，如 "A", "B", "C", 或 "D"
   - explanation: 解释为什么选择这个答案

2. **填空题 (fill_blank)**：
   - question_type: "fill_blank"
   - question: 题目内容，**必须**使用占位符来明确标识每个填空位置
     占位符格式：使用 [空1]、[空2]、[空3] 等来标记填空位置
     例如："函数 f(x) = [空1]x^2 + [空2]x + [空3] 的导数是 [空4]"
   - blanks: 填空题答案字典，键是占位符（必须与 question 中的占位符完全匹配），值是对应的答案
     例如：如果 question = "函数 f(x) = [空1]x^2 + [空2]x + [空3]"
     则 blanks = {{"[空1]": "2", "[空2]": "3", "[空3]": "1"}}
     注意：字典的键必须与 question 中的占位符完全一致（包括方括号）
     这种方式比数组更清晰，因为不需要依赖顺序，每个占位符直接对应其答案
   - answer: 可选的完整答案说明（用于详细解释）
   - explanation: 解释为什么填这些内容

3. **证明题 (proof)**：
   - question_type: "proof"
   - question: 需要证明的命题或问题
   - answer: 简要答案或结论
   - proof: 详细的证明步骤，必须完整清晰

4. **简答题 (short_answer)**：
   - question_type: "short_answer"
   - question: 题目内容
   - answer: 正确答案
   - explanation: 详细的解释和说明

5. **代码题 (code)**：
   - question_type: "code"
   - question: 题目内容（只对需要代码的课程才有）
   - code_answer: 完整的代码答案
   - explanation: 可选的代码解释（可选）

**重要**：
- 每个例子和练习都必须明确指定 question_type
- 根据题目类型，只填写相应的字段（如选择题填写 options 和 correct_answer，填空题填写 blanks）
- 保持题目的多样性和合理性，根据内容特点选择合适的题目类型

**重要要求**

- 保持原文档的核心内容和格式
- 如果原文档中某个定义后面有多个例子，必须全部提取
- 如果原文档中有定理和证明标记，且与章节相关，必须提取
- 例子如果缺少解答，必须补充完整解答
- 按照原文档顺序组织内容：定义 → 相关例子/笔记/定理/证明 → 下一个定义
"""
            
            section_agent = Agent(
                instructions=instructions, 
                name=section_title, 
                output_type=AgentOutputSchema(Section, strict_json_schema=False)
            )
            
            response = await Runner.run(section_agent, f"请为章节 '{section_title}' 创建完整内容")
            section_data = response.final_output
            self.sections[section_title] = section_data
            
            return section_data
        
        @function_tool
        async def section_maker(section_title: str, section_description: str) -> str:
            """
            接受一个 section title 和 description，输出该 section 的 notebook 内容
            
            Args:
                section_title: 章节标题
                section_description: 章节描述
            
            Returns:
                章节创建完成的确认信息
            """
            section_data = await _create_section(section_title, section_description)
            return f"章节 '{section_title}' 已创建完成"
        
        self.write_to_file = write_to_file
        self.section_maker = section_maker
        self._create_section = _create_section  # 保存为实例方法以便直接调用
        
        instructions = f"""
你是一个专业的笔记生成助手。你的任务是：

1. 根据提供的大纲（Outline），为每个章节调用 section_maker 工具来生成详细内容

2. 大纲信息：
   - 标题: {outline.notebook_title}
   - 描述: {outline.notebook_description}
   - 章节: {list(outline.outlines.keys())}

3. 对于大纲中的每个章节，你需要：
   - 调用 section_maker 工具，传入章节标题和描述
   - 等待所有章节都生成完成

4. 最后，将所有章节内容组合成完整的 markdown 格式，并调用 write_to_file 工具保存到文件

Markdown格式要求：
- 使用 # 作为主标题（notebook_title）
- 使用 ## 作为章节标题（section_title）
- 每个章节包含：介绍、概念块（定义+例子+笔记+定理+证明+答案）、总结、练习题
- 按照原文档顺序组织，定义后面跟着相关例子、笔记、定理、证明、答案等
- 格式清晰，易于阅读

请开始处理所有章节。
"""
        
        super().__init__(
            name="NoteBookAgentCreator",
            instructions=instructions,
            tools=[self.section_maker, self.write_to_file]
        )


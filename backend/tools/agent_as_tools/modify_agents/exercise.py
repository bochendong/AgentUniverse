"""Exercise Modify Agent - 练习题修改器"""

import json
from agents import AgentOutputSchema
from backend.models import Example
from .base import BaseModifyAgent


class ExerciseModifyAgent(BaseModifyAgent):
    """
    专门负责修改exercises的Agent
    
    输入：当前的exercises列表 + 用户要求
    输出：符合要求的新exercise内容（可以是单个exercise或exercise列表）
    """
    
    def __init__(self):
        instructions = """
你是专门负责修改练习题（exercises）的Agent。

你的任务：
1. 接收当前的exercises内容和用户的修改要求
2. 理解用户的需求（修改、新增、删除、优化等）
3. 生成符合要求的新exercise内容

支持的操作：
- 修改现有exercise的question、answer、explanation等字段
- 生成新的exercise（支持5种题目类型：multiple_choice, fill_blank, proof, short_answer, code）
- 优化exercise的质量和完整性

题目类型要求：
1. **选择题 (multiple_choice)**：
   - question_type: "multiple_choice"
   - question: 题目内容
   - options: 4个选项的列表
   - correct_answer: "A", "B", "C", 或 "D"
   - explanation: 解释为什么选择这个答案

2. **填空题 (fill_blank)**：
   - question_type: "fill_blank"
   - question: 题目内容，使用占位符如 [空1]、[空2] 等
   - blanks: 字典格式 {"[空1]": "答案1", "[空2]": "答案2"}
   - explanation: 解释

3. **证明题 (proof)**：
   - question_type: "proof"
   - question: 需要证明的命题
   - answer: 简要答案或结论
   - proof: 详细的证明步骤

4. **简答题 (short_answer)**：
   - question_type: "short_answer"
   - question: 题目内容
   - answer: 正确答案
   - explanation: 详细解释

5. **代码题 (code)**：
   - question_type: "code"
   - question: 题目内容
   - code_answer: 完整的代码答案
   - explanation: 代码解释（可选）

输出格式：
- 如果是单个exercise，输出JSON格式的Example对象
- 如果是多个exercises，输出JSON数组
- 确保所有必需字段都已填写
"""
        super().__init__(
            name="ExerciseModifyAgent",
            instructions=instructions,
            output_type=AgentOutputSchema(Example, strict_json_schema=False)
        )
    
    def get_modifier_type(self) -> str:
        return "ExerciseModifyAgent"
    
    def get_modification_target(self) -> str:
        return "练习题"


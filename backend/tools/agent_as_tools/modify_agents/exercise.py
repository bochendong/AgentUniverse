"""Exercise Modify Agent - 练习题修改器"""

import json
from agents import AgentOutputSchema
from backend.models import Example
from .base import BaseModifyAgent

# 导入公共 prompt 片段
from backend.prompts.common_prompt_snippets import (
    QUESTION_TYPE_REQUIREMENTS
)


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

{QUESTION_TYPE_REQUIREMENTS}

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



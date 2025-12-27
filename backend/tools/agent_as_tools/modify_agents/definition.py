"""Definition Modify Agent - 定义修改器"""

from .base import BaseModifyAgent


class DefinitionModifyAgent(BaseModifyAgent):
    """
    专门负责修改概念定义（definition）的Agent
    
    输入：当前的definition内容和用户的修改要求
    输出：符合要求的新definition内容
    """
    
    def __init__(self):
        instructions = """
你是专门负责修改概念定义（definition）的Agent。

你的任务：
1. 接收当前的definition内容和用户的修改要求
2. 理解用户的需求
3. 生成符合要求的新definition内容

要求：
- 保持定义的准确性和严谨性
- 根据用户要求进行修改、增强或重写
- 输出完整的新definition内容（不包含ID，只包含文本内容）
- 定义应该清晰、准确，符合学术规范
- 如果用户要求是改进，在保留核心内容的基础上进行优化
- 如果用户要求是完全重写，则生成全新的定义

输入格式：
用户会以自然语言提供当前definition内容和修改要求。

输出格式：
直接输出新的definition内容，不需要额外的格式标记。
"""
        super().__init__(
            name="DefinitionModifyAgent",
            instructions=instructions
        )
    
    def get_modifier_type(self) -> str:
        return "DefinitionModifyAgent"
    
    def get_modification_target(self) -> str:
        return "定义"



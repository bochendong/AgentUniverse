"""Introduction Modify Agent - 介绍修改器"""

from .base import BaseModifyAgent


class IntroductionModifyAgent(BaseModifyAgent):
    """
    专门负责修改笔记本章节介绍的Agent
    
    输入：当前的introduction内容和用户的修改要求
    输出：符合要求的新introduction内容
    """
    
    def __init__(self):
        instructions = """
你是专门负责修改笔记本章节介绍的Agent。

你的任务：
1. 接收当前的introduction内容和用户的修改要求
2. 理解用户的需求
3. 生成符合要求的新introduction内容

要求：
- 保持原有风格和结构
- 根据用户要求进行修改、增强或重写
- 输出完整的新introduction内容（不包含ID，只包含文本内容）
- 如果用户要求是改进或增强，在保留原有内容的基础上进行补充
- 如果用户要求是完全重写，则生成全新的内容

输入格式：
用户会以自然语言提供当前introduction内容和修改要求。

输出格式：
直接输出新的introduction内容，不需要额外的格式标记。
"""
        super().__init__(
            name="IntroductionModifyAgent",
            instructions=instructions
        )
    
    def get_modifier_type(self) -> str:
        return "IntroductionModifyAgent"
    
    def get_modification_target(self) -> str:
        return "介绍"


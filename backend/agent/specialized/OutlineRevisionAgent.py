"""OutlineRevisionAgent - 根据用户反馈修改大纲的Agent"""

from typing import Optional
from agents import Agent, Runner, AgentOutputSchema
from backend.agent.specialized.NotebookModels import Outline


class OutlineRevisionAgent(Agent):
    """
    大纲修订Agent - 根据用户反馈修改现有大纲
    
    支持：
    - 修改章节标题
    - 修改章节描述
    - 添加新章节
    - 删除章节
    - 调整章节顺序
    - 根据反馈重新生成大纲内容
    """
    
    def __init__(self, current_outline: Outline, user_feedback: str):
        """
        初始化大纲修订Agent
        
        Args:
            current_outline: 当前的大纲
            user_feedback: 用户的反馈意见
        """
        self.name = "OutlineRevisionAgent"
        self.current_outline = current_outline
        self.user_feedback = user_feedback
        
        # 格式化当前大纲信息
        outline_info = f"""
**当前大纲**

标题：{current_outline.notebook_title}
描述：{current_outline.notebook_description}

章节：
"""
        for i, (title, desc) in enumerate(current_outline.outlines.items(), 1):
            outline_info += f"\n{i}. {title}\n   {desc[:200]}{'...' if len(desc) > 200 else ''}\n"
        
        instructions = f"""
你是一个专业的学习内容规划专家。用户对当前的大纲提出了反馈意见，你需要根据反馈修改大纲。

**当前大纲**

标题：{current_outline.notebook_title}
描述：{current_outline.notebook_description}

章节：
"""
        for i, (title, desc) in enumerate(current_outline.outlines.items(), 1):
            instructions += f"\n{i}. {title}\n   {desc}\n"
        
        instructions += f"""

**用户反馈**

{user_feedback}

**任务要求**

1. **仔细分析用户反馈**：
   - 用户是否想要修改某些章节？
   - 用户是否想要添加新章节？
   - 用户是否想要删除某些章节？
   - 用户是否想要调整章节顺序？
   - 用户是否对标题或描述有意见？

2. **修改大纲**：
   - 根据反馈进行相应的修改
   - 保持大纲的逻辑性和完整性
   - 确保章节之间不重复、不遗漏
   - 如果用户要求添加内容，确保新内容符合主题

3. **输出格式**：
   - 保持与原始大纲相同的结构
   - 如果用户没有明确要求修改某些部分，保持原样
   - 如果用户要求修改，确保修改后的内容符合用户期望

**输出要求**

返回一个修改后的Outline对象，包含：
- notebook_title: 标题（如果需要修改则修改，否则保持原样）
- notebook_description: 描述（如果需要修改则修改，否则保持原样）
- outlines: 章节字典（根据反馈进行相应修改）

请根据用户反馈修改大纲。
"""
        
        super().__init__(
            name="OutlineRevisionAgent",
            instructions=instructions,
            output_type=AgentOutputSchema(Outline, strict_json_schema=False)
        )

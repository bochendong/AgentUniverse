"""NotebookCreationRouter - 笔记本创建路由Agent，根据意图选择合适的创建策略"""

from typing import Optional, Tuple
from agents import Agent, Runner, function_tool

from backend.agent.NoteBookAgent import NoteBookAgent
from backend.tools.agent_as_tools.IntentExtractionAgent import IntentExtractionAgent
from backend.agent.specialized.NotebookCreationStrategies import (
    create_full_content_notebook,
    create_enhanced_notebook,
    create_knowledge_base_notebook,
    create_outline_first_notebook
)
from backend.models import (
    NotebookCreationIntent,
    Outline
)


class NotebookCreationRouter:
    """
    笔记本创建路由器
    
    根据用户意图选择合适的创建策略，并执行创建流程
    """
    
    def __init__(self):
        self.name = "NotebookCreationRouter"
    
    async def generate_outline(
        self,
        user_request: str,
        file_path: Optional[str] = None
    ) -> Tuple[Outline, str]:
        """
        生成大纲供用户确认（所有场景统一使用）
        
        Args:
            user_request: 用户请求内容
            file_path: 文件路径（如果有）
            
        Returns:
            (Outline对象, 格式化的大纲信息字符串)
        """
        # 步骤1: 提取意图
        intent_agent = IntentExtractionAgent(
            user_request=user_request,
            file_path=file_path
        )
        
        intent_result = await Runner.run(
            intent_agent,
            "请分析用户请求，提取笔记本创建意图"
        )
        
        if not intent_result or not intent_result.final_output:
            raise ValueError("无法提取创建意图")
        
        intent: NotebookCreationIntent = intent_result.final_output
        
        print(f"\n[路由] 检测到意图类型: {intent.intent_type}")
        if intent.topic_or_theme:
            print(f"[路由] 主题: {intent.topic_or_theme}")
        if intent.additional_requirements:
            print(f"[路由] 额外要求: {intent.additional_requirements}\n")
        
        # 步骤2: 根据意图类型生成相应的大纲
        from agents import Agent, AgentOutputSchema
        from backend.models import Outline
        from backend.tools.agent_as_tools.section_creators.utils import get_file_content
        
        if intent.intent_type == "knowledge_base":
            # 知识库类型：生成知识库结构大纲
            if not file_path:
                raise ValueError("knowledge_base策略需要文件路径")
            
            file_content = get_file_content(file_path)
            
            # Get model settings from config
            from backend.config.model_config import get_model_settings, get_model_name
            model_name = get_model_name()
            model_settings = get_model_settings()
            
            outline_agent = Agent(
                name="KnowledgeBaseOutlineAgent",
                model=model_name,  # 显式传递 model 参数
                instructions=f"""
你是一个知识库内容分析专家。请分析文档内容，生成一个知识库结构（不是学习材料，而是知识记录）。

**文档内容**
{file_content}

**任务要求**

1. **生成笔记本描述（notebook_description）**：
   - 描述这个知识库包含什么知识领域、核心内容
   - 说明这是知识记录，不是学习材料（不需要练习题）
   - 长度建议：200-300字

2. **生成章节结构**：
   - 根据文档的自然结构或主题划分章节
   - 章节数量：3-8个，根据内容复杂度决定
   - 每个章节描述：说明该章节包含哪些知识点、概念、信息
   - 章节之间应该逻辑清晰，便于查找和回顾

**重要**：
- 这不是学习材料，是知识记录
- 不需要考虑练习题、例子等学习元素
- 重点在于知识点的组织、分类和记录

**输出格式**
{{
  "notebook_title": "文档标题（字符串）",
  "notebook_description": "知识库描述（字符串，200-300字）",
  "outlines": {{
    "章节名称1": "章节描述（说明包含哪些知识点）",
    "章节名称2": "章节描述",
    ...
  }}
}}
""",
                output_type=AgentOutputSchema(Outline, strict_json_schema=False),
                model_settings=model_settings
            )
            
            outline_result = await Runner.run(
                outline_agent,
                "请分析文档并生成知识库结构大纲"
            )
            
        elif file_path:
            # 有文件：使用OutlineMakerAgent从文件生成大纲
            from backend.tools.agent_as_tools.NotebookCreator import OutlineMakerAgent
            outline_agent = OutlineMakerAgent(file_path)
            outline_result = await Runner.run(
                outline_agent, 
                "请分析文档并生成学习大纲，包括笔记本描述（描述包含什么知识、不包含什么知识、知识边界和定位）"
            )
        else:
            # 没有文件：从主题生成大纲
            topic = intent.topic_or_theme or user_request.strip()[:100]
            
            # Get model settings from config
            from backend.config.model_config import get_model_settings, get_model_name
            model_name = get_model_name()
            model_settings = get_model_settings()
            print(f"[TopicOutlineAgent] 使用模型: {model_name}")
            
            outline_agent = Agent(
                name="TopicOutlineAgent",
                model=model_name,  # 显式传递 model 参数
                instructions=f"""
你是一个专业的学习内容规划专家。请根据用户提供的主题，草拟一个学习大纲。

**用户主题**
{topic}

**用户描述**
{user_request}

**任务要求**

1. **生成笔记本描述（notebook_description）**：
   - 描述这个笔记本包含什么知识领域、核心概念和主题
   - 明确说明不包含哪些内容，确定笔记本的知识边界
   - 说明这个笔记本在整个知识体系中的定位
   - 长度建议：200-300字

2. **生成 5-6 个主要章节的大纲**，每个章节应该：
   - **描述详细明确**：说明包含哪些定义、概念、关键词、例子、定理、证明
   - **边界清晰**：章节之间不重叠、不遗漏
   - **长度合理**：每个章节包含2-4个主要概念
   - **逻辑递进**：从基础到进阶，第一个章节只包含最基础的定义和概念

**输出格式**
{{
  "notebook_title": "笔记本标题（字符串）",
  "notebook_description": "笔记本描述（字符串，200-300字）",
  "outlines": {{
    "章节名称1": "详细的章节描述（字符串，至少100字）",
    "章节名称2": "详细的章节描述（字符串，至少100字）",
    ...
  }}
}}
""",
                output_type=AgentOutputSchema(Outline, strict_json_schema=False),
                model_settings=model_settings
            )
            
            outline_result = await Runner.run(
                outline_agent,
                f"请为主题'{topic}'草拟一个学习大纲"
            )
        
        if not outline_result or not outline_result.final_output:
            raise ValueError("无法生成大纲")
        
        outline = outline_result.final_output
        
        # 格式化为用户友好的字符串
        outline_info = f"""📋 **大纲已生成，请确认：**

**标题**：{outline.notebook_title}

**描述**：{outline.notebook_description}

**章节**：
"""
        for i, (title, desc) in enumerate(outline.outlines.items(), 1):
            outline_info += f"\n**{i}. {title}**\n{desc[:150]}{'...' if len(desc) > 150 else ''}\n"
        
        outline_info += "\n请确认此大纲是否符合您的需求。确认后我将根据大纲生成完整的笔记本内容。"
        
        return outline, outline_info
    
    async def route_and_create(
        self,
        user_request: str,
        confirmed_outline: Outline,
        file_path: Optional[str] = None,
        parent_agent_id: Optional[str] = None,
        DB_PATH: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> Tuple[NoteBookAgent, str]:
        """
        根据已确认的大纲创建笔记本
        
        Args:
            user_request: 用户请求内容
            confirmed_outline: 已确认的大纲（必需）
            file_path: 文件路径（如果有）
            parent_agent_id: 父agent ID
            DB_PATH: 数据库路径
            output_path: 输出路径
            
        Returns:
            (NoteBookAgent实例, 成功消息)
        """
        # 步骤1: 提取意图（用于确定使用哪个策略）
        intent_agent = IntentExtractionAgent(
            user_request=user_request,
            file_path=file_path
        )
        
        intent_result = await Runner.run(
            intent_agent,
            "请分析用户请求，提取笔记本创建意图"
        )
        
        if not intent_result or not intent_result.final_output:
            raise ValueError("无法提取创建意图")
        
        intent: NotebookCreationIntent = intent_result.final_output
        
        print(f"\n[路由] 使用已确认的大纲，意图类型: {intent.intent_type}")
        if intent.additional_requirements:
            print(f"[路由] 额外要求: {intent.additional_requirements}\n")
        
        # 步骤2: 根据意图类型路由到相应的策略（所有策略都接受已确认的大纲）
        if intent.intent_type == "full_content":
            notebook, message = await create_full_content_notebook(
                intent=intent,
                outline=confirmed_outline,
                parent_agent_id=parent_agent_id,
                DB_PATH=DB_PATH,
                output_path=output_path
            )
            
        elif intent.intent_type == "enhancement":
            notebook, message = await create_enhanced_notebook(
                intent=intent,
                outline=confirmed_outline,
                parent_agent_id=parent_agent_id,
                DB_PATH=DB_PATH,
                output_path=output_path
            )
            
        elif intent.intent_type == "knowledge_base":
            notebook, message = await create_knowledge_base_notebook(
                intent=intent,
                outline=confirmed_outline,
                parent_agent_id=parent_agent_id,
                DB_PATH=DB_PATH,
                output_path=output_path
            )
            
        elif intent.intent_type == "outline_first":
            notebook, message = await create_outline_first_notebook(
                intent=intent,
                outline=confirmed_outline,
                parent_agent_id=parent_agent_id,
                DB_PATH=DB_PATH,
                output_path=output_path
            )
            
        else:
            raise ValueError(f"未知的意图类型: {intent.intent_type}")
        
        return notebook, message
    

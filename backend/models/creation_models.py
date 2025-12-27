"""Notebook creation workflow models - 笔记本创建流程模型"""

from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict


class NotebookCreationIntent(BaseModel):
    """笔记本创建意图"""
    model_config = ConfigDict(strict=False)
    
    intent_type: Literal[
        "full_content",      # 场景1: 丰满笔记，只需稍作修改
        "enhancement",       # 场景2: 不丰满笔记，需要添加内容
        "knowledge_base",    # 场景3: 论文/条例等，不需要练习题
        "outline_first"      # 场景4: 只有主题，需先确认大纲
    ]
    
    # 通用信息
    file_path: Optional[str] = None  # 文件路径（如果有）
    user_description: str  # 用户描述或请求内容
    topic_or_theme: Optional[str] = None  # 主题（场景4时使用）
    
    # 意图特定信息
    content_richness: Optional[Literal["rich", "sparse"]] = None  # 内容丰满度（场景1、2）
    requires_exercises: Optional[bool] = True  # 是否需要练习题（场景3）
    outline_confirmed: Optional[bool] = False  # 大纲是否已确认（场景4）
    
    # 附加要求
    additional_requirements: Optional[str] = None  # 用户的额外要求


class NotebookSplit(BaseModel):
    """单个拆分后的 Notebook 计划"""
    model_config = ConfigDict(strict=False)
    
    notebook_title: str  # 新 Notebook 的标题
    notebook_description: str  # 新 Notebook 的描述（说明包含什么知识、不包含什么知识、知识边界）
    section_titles: List[str]  # 包含的章节标题列表


class SplitPlan(BaseModel):
    """拆分计划"""
    model_config = ConfigDict(strict=False)
    
    master_agent_title: str  # 新 MasterAgent 的标题
    master_agent_description: str  # 新 MasterAgent 的描述
    notebooks: List[NotebookSplit]  # 拆分后的 Notebook 列表


class NotebookCreationResult(BaseModel):
    """笔记本创建结果"""
    model_config = ConfigDict(strict=False)
    
    status: Literal["success", "error"]  # 创建状态
    message: str  # 用户友好的消息文本
    notebook_id: Optional[str] = None  # 笔记本 ID（成功时提供）
    notebook_title: Optional[str] = None  # 笔记本标题（成功时提供）
    error: Optional[str] = None  # 错误信息（失败时提供）

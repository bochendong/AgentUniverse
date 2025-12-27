"""Pydantic models for API requests and responses."""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum


class ChatRequest(BaseModel):
    """普通聊天请求 - 只支持文本消息"""
    message: str
    session_id: Optional[str] = None


class SourceChatRequest(BaseModel):
    """带文件的聊天请求 - 支持文件上传和图片"""
    message: str
    session_id: Optional[str] = None
    file_path: Optional[str] = None  # 上传的文件路径
    images: Optional[List[Dict[str, Any]]] = None  # List of image objects: [{"type": "input_image", "image_url": "data:image/...;base64,..."}]


class MessageType(str, Enum):
    """消息类型枚举"""
    REGULAR = "regular"  # 普通消息
    OUTLINE = "outline"  # 大纲
    NOTEBOOK_CREATED = "notebook_created"  # 笔记本创建完成
    QUESTION = "question"  # 题目
    ADD_TO_NOTEBOOK = "add_to_notebook"  # 值得添加到笔记的内容


class StructuredMessageData(BaseModel):
    """结构化消息数据 - 用于前端根据消息类型渲染不同的UI"""
    message_type: MessageType = Field(..., description="消息类型，用于前端判断如何渲染UI")
    
    # 大纲相关字段（message_type = "outline"）
    outline: Optional[Dict] = Field(None, description="大纲内容（当 message_type 为 outline 时）")
    file_path: Optional[str] = Field(None, description="文件路径（当 message_type 为 outline 时）")
    user_request: Optional[str] = Field(None, description="用户请求（当 message_type 为 outline 时）")
    
    # 笔记本创建相关字段（message_type = "notebook_created"）
    notebook_id: Optional[str] = Field(None, description="笔记本ID（当 message_type 为 notebook_created 时）")
    notebook_title: Optional[str] = Field(None, description="笔记本标题（当 message_type 为 notebook_created 时）")
    
    # 题目相关字段（message_type = "question"）
    question_text: Optional[str] = Field(None, description="题目文本（当 message_type 为 question 时）")
    
    # 添加到笔记相关字段（message_type = "add_to_notebook"）
    content_summary: Optional[str] = Field(None, description="内容摘要（当 message_type 为 add_to_notebook 时）")


class ChatResponse(BaseModel):
    response: str
    session_id: str
    structured_data: Optional[StructuredMessageData] = None  # 结构化数据（如果有）


class SessionCreateRequest(BaseModel):
    title: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class ConversationsResponse(BaseModel):
    conversations: List[Dict[str, str]]


class TracingResponse(BaseModel):
    traces: List[Dict]
    current_activity: Optional[Dict] = None


class UpdateInstructionsRequest(BaseModel):
    instructions: str

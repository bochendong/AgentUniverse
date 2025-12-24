"""Pydantic models for API requests and responses."""

from typing import Optional, List, Dict
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


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

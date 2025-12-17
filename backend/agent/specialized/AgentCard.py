"""Agent Card data structure."""

from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict


class AgentCard(BaseModel):
    """Agent Card data structure for displaying agent information."""
    model_config = ConfigDict(strict=False)
    
    title: str  # Notebook title
    agent_id: str  # Agent ID
    parent_agent_id: Optional[str] = None  # Parent agent ID
    description: str  # Notebook description
    outline: Dict[str, str]  # Section titles and descriptions

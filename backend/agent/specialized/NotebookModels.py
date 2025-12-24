"""Compatibility layer for old pickled objects - 兼容旧版本的序列化对象

这个文件是为了兼容数据库中旧的序列化对象而保留的。
新的代码应该直接从 backend.models 导入。
"""

# Re-export all models from backend.models for backward compatibility
from backend.models import (
    Outline,
    Section,
    ConceptBlock,
    Theorem,
    Example,
    NotebookCreationIntent,
    NotebookSplit,
    SplitPlan,
    AgentCard,
)

__all__ = [
    "Outline",
    "Section",
    "ConceptBlock",
    "Theorem",
    "Example",
    "NotebookCreationIntent",
    "NotebookSplit",
    "SplitPlan",
    "AgentCard",
]

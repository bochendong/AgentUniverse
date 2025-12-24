"""Specialized agent implementations."""

# Import agent-as-tools from tools folder (these are used as tools by other agents)
from backend.tools.agent_as_tools.NotebookCreator import (
    NotebookCreator,
    OutlineMakerAgent,
)
from backend.tools.agent_as_tools.refinement_agents import (
    ExerciseRefinementAgent,
    ProofRefinementAgent
)
from backend.tools.agent_as_tools.IntentExtractionAgent import IntentExtractionAgent
from backend.tools.agent_as_tools.OutlineRevisionAgent import OutlineRevisionAgent

# Import other specialized agents (these are NOT used as tools, but are standalone agents)
from backend.models import (
    Outline,
    Section,
    ConceptBlock,
    Theorem,
    Example,
    NotebookCreationIntent,
    AgentCard,
)
from backend.agent.specialized.NotebookCreationRouter import NotebookCreationRouter
from backend.agent.specialized.NotebookModifyAgent import NotebookModifyAgent
from backend.tools.agent_as_tools.modify_agents import (
    IntroductionModifyAgent,
    ExerciseModifyAgent,
    DefinitionModifyAgent,
    SummaryModifyAgent
)

__all__ = [
    "NotebookCreator",
    "OutlineMakerAgent",
    "Outline",
    "Section",
    "ConceptBlock",
    "Theorem",
    "Example",
    "NotebookCreationIntent",
    "AgentCard",
    "ExerciseRefinementAgent",
    "ProofRefinementAgent",
    "IntentExtractionAgent",
    "NotebookCreationRouter",
    "OutlineRevisionAgent",
    "NotebookModifyAgent",
    "IntroductionModifyAgent",
    "ExerciseModifyAgent",
    "DefinitionModifyAgent",
    "SummaryModifyAgent",
]

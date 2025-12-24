"""Agent as tools - specialized agents that are used as tools by other agents."""

# Import all agent-as-tool agents to make them available
from backend.tools.agent_as_tools.NotebookCreator import (
    OutlineMakerAgent,
    NotebookCreator,
)
from backend.tools.agent_as_tools.refinement_agents import (
    ExerciseRefinementAgent,
    ProofRefinementAgent,
    RefinementOrchestrator
)
from backend.tools.agent_as_tools.IntentExtractionAgent import IntentExtractionAgent
from backend.tools.agent_as_tools.OutlineRevisionAgent import OutlineRevisionAgent

__all__ = [
    "OutlineMakerAgent",
    "NotebookCreator",
    "ExerciseRefinementAgent",
    "ProofRefinementAgent",
    "RefinementOrchestrator",
    "IntentExtractionAgent",
    "OutlineRevisionAgent",
]

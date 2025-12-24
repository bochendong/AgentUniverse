"""Notebooks API routes."""

from fastapi import APIRouter, HTTPException
from backend.database.agent_db import load_agent, delete_agent
from backend.agent.NoteBookAgent import NoteBookAgent
from backend.agent.BaseAgent import AgentType
from backend.api.utils import _serialize_agent_card
from backend.tools.utils import generate_markdown_from_agent

router = APIRouter(prefix="/api/notebooks", tags=["notebooks"])


@router.get("/{notebook_id}")
async def get_notebook(notebook_id: str):
    """Get notebook agent by ID."""
    try:
        agent = load_agent(notebook_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Notebook not found")
        
        if not isinstance(agent, NoteBookAgent):
            agent_type = getattr(agent, 'type', 'Unknown')
            if isinstance(agent_type, AgentType):
                agent_type_str = agent_type.value
            else:
                agent_type_str = str(agent_type)
            raise HTTPException(
                status_code=400, 
                detail=f"Agent is not a NoteBookAgent (type: {agent_type_str}). Use /api/agents/{notebook_id} for agent details."
            )
        
        # Check if split is recommended
        should_split = False
        split_reason = None
        if hasattr(agent, '_check_split'):
            should_split = agent._check_split()
            if should_split:
                sections_count = len(agent.sections) if agent.sections else 0
                word_count = agent._get_word_count() if hasattr(agent, '_get_word_count') else 0
                reasons = []
                if sections_count > 10:
                    reasons.append(f"章节数({sections_count}) > 10")
                if word_count > 3000:
                    reasons.append(f"字数({word_count}) > 3000")
                split_reason = "; ".join(reasons)
        
        return {
            "id": agent.id,
            "title": getattr(agent, 'notebook_title', ''),
            "description": getattr(agent, 'notebook_description', ''),
            "agent_card": _serialize_agent_card(agent.agent_card()) if hasattr(agent, 'agent_card') and callable(getattr(agent, 'agent_card')) else None,
            "should_split": should_split,
            "split_reason": split_reason,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting notebook: {str(e)}")


@router.get("/{notebook_id}/content")
async def get_notebook_content(notebook_id: str, format: str = None):
    """Get notebook content as structured data (JSON) or markdown fallback.
    
    Args:
        notebook_id: The notebook ID
        format: Optional format parameter. If set to 'markdown', always returns markdown format with XML tags.
                Otherwise returns structured data if available, or markdown as fallback.
    """
    try:
        # Clear cache to ensure we get the latest data from database
        try:
            from backend.utils.agent_manager import get_agent_manager
            get_agent_manager().clear_cache(notebook_id)
        except Exception:
            pass  # If AgentManager is not available, continue with load_agent
        
        # Force reload from database (bypass any potential caching)
        agent = load_agent(notebook_id, db_path=None)
        
        # Verify agent was loaded correctly
        if not agent:
            raise HTTPException(status_code=404, detail="Notebook not found")
        
        if not isinstance(agent, NoteBookAgent):
            agent_type = getattr(agent, 'type', 'Unknown')
            if isinstance(agent_type, AgentType):
                agent_type_str = agent_type.value
            else:
                agent_type_str = str(agent_type)
            raise HTTPException(
                status_code=400, 
                detail=f"Agent is not a NoteBookAgent (type: {agent_type_str}). Use /api/agents/{notebook_id} for agent details."
            )
        
        # If format is explicitly requested as markdown, always return markdown
        if format and format.lower() == 'markdown':
            content = generate_markdown_from_agent(agent, include_ids=True)
            return {
                "format": "markdown",
                "content": content
            }
        
        # Return structured data if available
        # Important: Check if sections is not empty (after modify_notes, sections might be cleared)
        has_sections = hasattr(agent, 'sections') and agent.sections and len(agent.sections) > 0
        has_outline = hasattr(agent, 'outline') and agent.outline
        
        if has_outline and has_sections:
            # Convert Pydantic models to dict for JSON serialization
            outline_dict = {
                "notebook_title": agent.outline.notebook_title,
                "notebook_description": getattr(agent.outline, 'notebook_description', ''),
                "outlines": agent.outline.outlines
            }
            
            sections_dict = {}
            for section_title, section_data in agent.sections.items():
                sections_dict[section_title] = {
                    "section_title": section_data.section_title,
                    "introduction": section_data.introduction,
                    "concept_blocks": [
                        {
                            "definition": block.definition,
                            "examples": [
                                {
                                    "question": ex.question,
                                    "answer": ex.answer,
                                    "proof": ex.proof
                                }
                                for ex in block.examples
                            ],
                            "notes": block.notes,
                            "theorems": [
                                {
                                    "theorem": th.theorem,
                                    "proof": th.proof,
                                    "examples": [
                                        {
                                            "question": ex.question,
                                            "answer": ex.answer,
                                            "proof": ex.proof
                                        }
                                        for ex in th.examples
                                    ]
                                }
                                for th in block.theorems
                            ]
                        }
                        for block in section_data.concept_blocks
                    ],
                    "standalone_examples": [
                        {
                            "question": ex.question,
                            "answer": ex.answer,
                            "proof": ex.proof
                        }
                        for ex in section_data.standalone_examples
                    ],
                    "standalone_notes": section_data.standalone_notes,
                    "summary": section_data.summary,
                    "exercises": [
                        {
                            "question": ex.question,
                            "answer": ex.answer,
                            "proof": ex.proof
                        }
                        for ex in section_data.exercises
                    ]
                }
            
            return {
                "format": "structured",
                "outline": outline_dict,
                "sections": sections_dict
            }
        else:
            # Fallback to markdown if no structured data
            content = generate_markdown_from_agent(agent)
            return {
                "format": "markdown",
                "content": content
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting notebook content: {str(e)}")


@router.post("/{notebook_id}/split")
async def split_notebook(notebook_id: str):
    """Split a notebook into multiple smaller notebooks."""
    try:
        agent = load_agent(notebook_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Notebook not found")
        
        if not isinstance(agent, NoteBookAgent):
            agent_type = getattr(agent, 'type', 'Unknown')
            if isinstance(agent_type, AgentType):
                agent_type_str = agent_type.value
            else:
                agent_type_str = str(agent_type)
            raise HTTPException(
                status_code=400, 
                detail=f"Agent is not a NoteBookAgent (type: {agent_type_str}). Cannot split."
            )
        
        # Check if split is recommended
        if not agent._check_split():
            return {
                "success": False,
                "message": "当前笔记本不需要拆分（章节数 <= 10 且字数 <= 3000）"
            }
        
        # Execute split
        result = await agent._execute_split()
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error splitting notebook: {str(e)}")


@router.delete("/{notebook_id}")
async def delete_notebook(notebook_id: str):
    """Delete a notebook agent."""
    try:
        agent = load_agent(notebook_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Notebook not found")
        
        # Remove from parent's sub_agent_ids
        if hasattr(agent, 'parent_agent_id') and agent.parent_agent_id:
            parent = load_agent(agent.parent_agent_id)
            if parent:
                parent._remove_sub_agent_by_id(notebook_id)
                # Ensure parent is saved after removing sub_agent
                parent.save_to_db()
        
        # Delete the agent
        deleted = delete_agent(notebook_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete notebook")
        
        return {"message": "Notebook deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting notebook: {str(e)}")

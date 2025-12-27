"""Agents API routes."""

from fastapi import APIRouter, HTTPException
from backend.api.utils import get_top_level_agent, _serialize_agent_card
from backend.agent.TopLevelAgent import TopLevelAgent
from backend.agent.MasterAgent import MasterAgent
from backend.agent.NoteBookAgent import NoteBookAgent
from backend.agent.BaseAgent import AgentType
from backend.database.agent_db import load_agent, load_all_agents, delete_agent, get_db_path
from backend.api.models import UpdateInstructionsRequest, ChatRequest, ChatResponse
from backend.utils.default_instructions import get_default_instructions
from backend.prompts.prompt_loader import load_prompt
import json
import sqlite3
from backend.database.agent_db import get_db_path
from backend.database.tools_db import get_tools_by_names

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("")
async def list_agents():
    """List all agents."""
    try:
        # Ensure TopLevelAgent is initialized (this will create it if it doesn't exist)
        get_top_level_agent()

        agents = load_all_agents()
        agent_list = []
        
        # Find TopLevelAgent and its MasterAgent
        top_level_agent_id = None
        valid_master_agent_id = None
        
        # First pass: find TopLevelAgent and its MasterAgent
        for agent_id, agent in agents.items():
            if isinstance(agent, TopLevelAgent):
                top_level_agent_id = agent_id
                # Get the MasterAgent from TopLevelAgent's sub_agent_ids
                sub_agent_ids = getattr(agent, 'sub_agent_ids', None) or []
                for sub_id in sub_agent_ids:
                    try:
                        sub_agent = agent.load_agent_from_db_by_id(sub_id)
                        if isinstance(sub_agent, MasterAgent):
                            valid_master_agent_id = sub_id
                            break
                    except Exception:
                        continue
                break
        
        # If not found in sub_agent_ids, search database
        if top_level_agent_id and not valid_master_agent_id:
            for agent_id, agent in agents.items():
                if isinstance(agent, MasterAgent):
                    parent_id = getattr(agent, 'parent_agent_id', None)
                    if parent_id == top_level_agent_id:
                        valid_master_agent_id = agent_id
                        break
        
        # Second pass: collect agents, filtering duplicate MasterAgents
        for agent_id, agent in agents.items():
            # Include TopLevelAgent in the list
            # For MasterAgents, only include the one that belongs to TopLevelAgent
            if isinstance(agent, MasterAgent):
                if agent_id != valid_master_agent_id:
                    # Skip duplicate MasterAgent
                    continue
            
            agent_type = getattr(agent, 'type', 'Unknown')
            if isinstance(agent_type, AgentType):
                agent_type_str = agent_type.value
            else:
                agent_type_str = str(agent_type)
            
            # Determine if it's a MasterAgent or NoteBookAgent
            is_master = isinstance(agent, MasterAgent)
            is_notebook = isinstance(agent, NoteBookAgent)
            is_top_level = isinstance(agent, TopLevelAgent)
            
            # Convert agent_type to frontend format
            if is_top_level:
                agent_type_frontend = 'top_level_agent'
            elif is_master:
                agent_type_frontend = 'master'
            elif is_notebook:
                agent_type_frontend = 'notebook'
            else:
                agent_type_frontend = agent_type_str.lower().replace(' ', '_')
            
            # Build agent data for frontend
            agent_data = {
                'id': agent_id,
                'notebook_id': agent_id,  # Frontend uses notebook_id
                'agent_name': getattr(agent, 'name', 'Unknown'),
                'agent_type': agent_type_frontend,
                'type': agent_type_str,
                'name': getattr(agent, 'name', 'Unknown'),
                'metadata': {
                    'is_master_agent': is_master,
                    'is_top_level_agent': is_top_level,
                    'is_notebook_agent': is_notebook,
                },
                'avatar_seed': agent_id,  # Use agent_id as seed for avatar
                'agent_card': _serialize_agent_card(agent.agent_card()) if hasattr(agent, 'agent_card') and callable(getattr(agent, 'agent_card')) else None,
            }
            
            # Add notebook-specific fields if it's a NoteBookAgent
            if is_notebook:
                agent_data['notebook_title'] = getattr(agent, 'notebook_title', '')
                agent_data['description'] = getattr(agent, 'notebook_description', '')
            else:
                agent_data['notebook_title'] = ''
                agent_data['description'] = ''
            
            agent_list.append(agent_data)
        
        # Frontend expects an array directly in response.data
        return agent_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing agents: {str(e)}")


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent by ID."""
    try:
        agent = load_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent_type = getattr(agent, 'type', 'Unknown')
        if isinstance(agent_type, AgentType):
            agent_type_str = agent_type.value
        else:
            agent_type_str = str(agent_type)
        
        # Determine if it's a MasterAgent or NoteBookAgent
        is_master = isinstance(agent, MasterAgent)
        is_notebook = isinstance(agent, NoteBookAgent)
        is_top_level = isinstance(agent, TopLevelAgent)
        
        # Convert agent_type to frontend format
        if is_top_level:
            agent_type_frontend = 'top_level_agent'
        elif is_master:
            agent_type_frontend = 'master'
        elif is_notebook:
            agent_type_frontend = 'notebook'
        else:
            agent_type_frontend = agent_type_str.lower().replace(' ', '_')
        
        # Build agent data for frontend (same format as list_agents)
        agent_data = {
            'id': agent.id,
            'notebook_id': agent.id,  # Frontend uses notebook_id
            'agent_name': getattr(agent, 'name', 'Unknown'),
            'agent_type': agent_type_frontend,
            'type': agent_type_str,
            'name': getattr(agent, 'name', 'Unknown'),
            'metadata': {
                'is_master_agent': is_master,
                'is_top_level_agent': is_top_level,
                'is_notebook_agent': is_notebook,
            },
            'avatar_seed': agent.id,  # Use agent_id as seed for avatar
            'agent_card': _serialize_agent_card(agent.agent_card()) if hasattr(agent, 'agent_card') and callable(getattr(agent, 'agent_card')) else None,
        }
        
        # Add notebook-specific fields if it's a NoteBookAgent
        if is_notebook:
            agent_data['notebook_title'] = getattr(agent, 'notebook_title', '')
            agent_data['description'] = getattr(agent, 'notebook_description', '')
            
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
                    if word_count > 10000:
                        reasons.append(f"字数({word_count}) > 10000")
                    split_reason = "; ".join(reasons)
            
            agent_data['should_split'] = should_split
            agent_data['split_reason'] = split_reason
        else:
            agent_data['notebook_title'] = ''
            agent_data['description'] = ''
            agent_data['should_split'] = False
            agent_data['split_reason'] = None
        
        return agent_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent: {str(e)}")


@router.get("/{agent_id}/parent")
async def get_agent_parent(agent_id: str):
    """Get parent agent of an agent."""
    try:
        agent = load_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        parent_agent_id = getattr(agent, 'parent_agent_id', None)
        if not parent_agent_id:
            raise HTTPException(status_code=404, detail="Agent has no parent")
        
        parent_agent = load_agent(parent_agent_id)
        if not parent_agent:
            raise HTTPException(status_code=404, detail="Parent agent not found")
        
        # Get agent type
        parent_type = getattr(parent_agent, 'type', 'Unknown')
        if isinstance(parent_type, AgentType):
            parent_type_str = parent_type.value
        else:
            parent_type_str = str(parent_type)
        
        # Determine if it's a MasterAgent, NoteBookAgent, or TopLevelAgent
        is_master = isinstance(parent_agent, MasterAgent)
        is_notebook = isinstance(parent_agent, NoteBookAgent)
        is_top_level = isinstance(parent_agent, TopLevelAgent)
        
        # Convert to frontend format
        if is_top_level:
            agent_type_frontend = 'top_level_agent'
        elif is_master:
            agent_type_frontend = 'master'
        elif is_notebook:
            agent_type_frontend = 'notebook'
        else:
            agent_type_frontend = parent_type_str.lower().replace(' ', '_')
        
        # Build parent agent data for frontend
        parent_data = {
            'id': parent_agent.id,
            'notebook_id': parent_agent.id,
            'agent_name': getattr(parent_agent, 'name', 'Unknown'),
            'name': getattr(parent_agent, 'name', 'Unknown'),
            'type': parent_type_str,
            'agent_type': agent_type_frontend,
            'metadata': {
                'is_master_agent': is_master,
                'is_top_level_agent': is_top_level,
                'is_notebook_agent': is_notebook,
            },
            'avatar_seed': parent_agent.id,
            'agent_card': _serialize_agent_card(parent_agent.agent_card()) if hasattr(parent_agent, 'agent_card') and callable(getattr(parent_agent, 'agent_card')) else None,
        }
        
        # Add notebook-specific fields if it's a NoteBookAgent
        if is_notebook:
            parent_data['notebook_title'] = getattr(parent_agent, 'notebook_title', '')
            parent_data['description'] = getattr(parent_agent, 'notebook_description', '')
        elif is_master:
            parent_data['description'] = ''
        
        return parent_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting parent agent: {str(e)}")


@router.get("/{agent_id}/hierarchy")
async def get_agent_hierarchy(agent_id: str):
    """Get agent hierarchy."""
    try:
        agent = load_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Build hierarchy
        agent_type = getattr(agent, 'type', 'Unknown')
        if isinstance(agent_type, AgentType):
            agent_type_str = agent_type.value
        else:
            agent_type_str = str(agent_type)
        
        hierarchy = {
            "id": agent.id,
            "type": agent_type_str,
            "name": getattr(agent, 'name', 'Unknown'),
            "children": []
        }
        
        # Load sub-agents
        sub_agent_ids = getattr(agent, 'sub_agent_ids', None) or []
        if sub_agent_ids:
            for sub_id in sub_agent_ids:
                try:
                    sub_agent = agent.load_agent_from_db_by_id(sub_id)
                except Exception:
                    # Agent not found (may have been deleted), skip it
                    # TODO: Clean up orphaned sub_agent_ids
                    continue
                if sub_agent:
                    sub_type = getattr(sub_agent, 'type', 'Unknown')
                    if isinstance(sub_type, AgentType):
                        sub_type_str = sub_type.value
                    else:
                        sub_type_str = str(sub_type)
                    
                    # Determine agent type for frontend format
                    is_master = isinstance(sub_agent, MasterAgent)
                    is_notebook = isinstance(sub_agent, NoteBookAgent)
                    is_top_level = isinstance(sub_agent, TopLevelAgent)
                    
                    # Convert to frontend format
                    if is_top_level:
                        agent_type_frontend = 'top_level_agent'
                    elif is_master:
                        agent_type_frontend = 'master'
                    elif is_notebook:
                        agent_type_frontend = 'notebook'
                    else:
                        agent_type_frontend = sub_type_str.lower().replace(' ', '_')
                    
                    child_data = {
                        "id": sub_agent.id,
                        "notebook_id": sub_agent.id,  # Frontend uses notebook_id
                        "agent_name": getattr(sub_agent, 'name', 'Unknown'),
                        "name": getattr(sub_agent, 'name', 'Unknown'),  # Keep for backward compatibility
                        "type": sub_type_str,
                        "agent_type": agent_type_frontend,
                        "metadata": {
                            "is_master_agent": is_master,
                            "is_top_level_agent": is_top_level,
                            "is_notebook_agent": is_notebook,
                        },
                        "agent_card": _serialize_agent_card(sub_agent.agent_card()) if hasattr(sub_agent, 'agent_card') and callable(getattr(sub_agent, 'agent_card')) else None,
                    }
                    
                    # Add notebook-specific fields if it's a NoteBookAgent
                    if is_notebook:
                        child_data['notebook_title'] = getattr(sub_agent, 'notebook_title', '')
                        child_data['description'] = getattr(sub_agent, 'notebook_description', '')
                    elif is_master:
                        # For MasterAgent, get description from agent_card or empty
                        child_data['description'] = ''
                        # Load children for MasterAgent
                        child_sub_agent_ids = getattr(sub_agent, 'sub_agent_ids', None) or []
                        if child_sub_agent_ids:
                            child_data['children'] = []
                            for child_id in child_sub_agent_ids:
                                try:
                                    child_agent = sub_agent.load_agent_from_db_by_id(child_id)
                                except Exception:
                                    # Agent not found (may have been deleted), skip it
                                    continue
                                if child_agent:
                                    child_is_notebook = isinstance(child_agent, NoteBookAgent)
                                    child_is_master = isinstance(child_agent, MasterAgent)
                                    child_agent_type = 'notebook' if child_is_notebook else ('master' if child_is_master else 'unknown')
                                    
                                    child_info = {
                                        "id": child_agent.id,
                                        "notebook_id": child_agent.id,
                                        "agent_name": getattr(child_agent, 'name', 'Unknown'),
                                        "name": getattr(child_agent, 'name', 'Unknown'),
                                        "agent_type": child_agent_type,
                                        "agent_card": _serialize_agent_card(child_agent.agent_card()) if hasattr(child_agent, 'agent_card') and callable(getattr(child_agent, 'agent_card')) else None,
                                    }
                                    
                                    if child_is_notebook:
                                        child_info['notebook_title'] = getattr(child_agent, 'notebook_title', '')
                                        child_info['description'] = getattr(child_agent, 'notebook_description', '')
                                    
                                    child_data['children'].append(child_info)
                    
                    hierarchy["children"].append(child_data)
        
        return hierarchy
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting hierarchy: {str(e)}")


@router.get("/{agent_id}/instructions")
async def get_agent_instructions(agent_id: str):
    """Get agent instructions (current and default)."""
    try:
        agent = load_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Determine agent type for getting default instructions
        is_master = isinstance(agent, MasterAgent)
        is_notebook = isinstance(agent, NoteBookAgent)
        is_top_level = isinstance(agent, TopLevelAgent)
        
        if is_top_level:
            agent_type = 'top_level_agent'
            template_name = 'top_level_agent'
        elif is_master:
            agent_type = 'master'
            template_name = 'master_agent'
        elif is_notebook:
            agent_type = 'notebook'
            template_name = 'notebook_agent'
        else:
            agent_type = 'base'
            template_name = None
        
        # Get template instructions (with placeholders like {agents_list} or {notes})
        template_instructions = load_prompt(template_name) if template_name else ''
        
        # Get default instructions (with variables replaced)
        default_instructions = get_default_instructions(agent_type, agent)
        
        # For NoteBookAgent, always use default_instructions (which has notes and tools_usage properly replaced)
        # For other agents, use stored instructions if available and not too short
        if is_notebook:
            # Always use freshly generated instructions for notebook agents to ensure notes and tools_usage are replaced
            current_instructions = default_instructions
            was_incomplete = False
        else:
            # Get current instructions from stored value
            current_instructions = getattr(agent, 'instructions', '') or ''
            # Check if current instructions are incomplete (significantly shorter than default)
            was_incomplete = False
            if len(current_instructions) < len(default_instructions) * 0.5:
                was_incomplete = True
                # If incomplete, use default as current for display
                current_instructions = default_instructions
        
        return {
            'current_instructions': current_instructions,
            'default_instructions': default_instructions,
            'template_instructions': template_instructions,  # Template with placeholders
            'was_incomplete': was_incomplete,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting instructions: {str(e)}")


@router.put("/{agent_id}/instructions")
async def update_agent_instructions(agent_id: str, request: UpdateInstructionsRequest):
    """Update agent instructions."""
    try:
        agent = load_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Update instructions
        agent.instructions = request.instructions
        agent.save_to_db()
        
        return {'message': 'Instructions updated successfully'}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating instructions: {str(e)}")


@router.get("/{agent_id}/tools")
async def get_agent_tools(agent_id: str):
    """Get agent tools information with full metadata from database."""
    try:
        # Load agent to verify it exists
        agent = load_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get tool_ids directly from database
        db_path = get_db_path(agent.DB_PATH if hasattr(agent, 'DB_PATH') else None)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get tool_ids column
        tool_ids_json = None
        try:
            cursor.execute("SELECT tool_ids FROM agents WHERE id = ?", (agent_id,))
            row = cursor.fetchone()
            if row and row[0]:
                tool_ids_json = row[0]
        except sqlite3.OperationalError:
            # Column doesn't exist, use empty list
            tool_ids_json = '[]'
        
        conn.close()
        
        # Parse tool_ids
        tool_ids = []
        if tool_ids_json and tool_ids_json != '[]':
            try:
                tool_ids = json.loads(tool_ids_json)
            except (json.JSONDecodeError, TypeError):
                tool_ids = []
        
        # Get tools metadata from database by names
        if tool_ids:
            tools_info = get_tools_by_names(tool_ids)
        else:
            tools_info = []
        
        return {'tools': tools_info}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tools: {str(e)}")


@router.post("/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_agent(agent_id: str, request: ChatRequest):
    """Chat with a specific agent (NotebookAgent, MasterAgent, etc.)."""
    try:
        # Use AgentManager to wake up the agent (ensures tools are restored)
        from backend.utils.agent_manager import wake_agent
        agent = wake_agent(agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
        
        # Ensure tools is not None (critical for Runner.run)
        if not hasattr(agent, 'tools') or agent.tools is None:
            # Try to recreate tools
            if hasattr(agent, '_recreate_tools'):
                try:
                    agent._recreate_tools()
                except Exception as e:
                    print(f"Warning: Failed to recreate tools: {e}")
                    agent.tools = []
            else:
                agent.tools = []
        
        # For NoteBookAgent, always ensure instructions are up-to-date (with notes and tools_usage replaced)
        # This is critical because instructions may contain {notes} placeholder from database
        if isinstance(agent, NoteBookAgent):
            # Check if instructions contain placeholders that need to be replaced
            if hasattr(agent, 'instructions') and ("{notes}" in agent.instructions or "{tools_usage}" in agent.instructions):
                print(f"[chat_with_agent] NoteBookAgent {agent_id} has placeholders in instructions, updating...")
                try:
                    agent._recreate_tools()  # This will update instructions with notes and tools_usage
                    print(f"[chat_with_agent] Updated NoteBookAgent instructions, length: {len(agent.instructions)}")
                except Exception as e:
                    print(f"[chat_with_agent] Warning: Failed to update NoteBookAgent instructions: {e}")
                    import traceback
                    traceback.print_exc()
        
        # Create session if not provided
        session_id = request.session_id
        if not session_id:
            from backend.database.session_db import create_session
            session_data = create_session()
            session_id = session_data['id']
        
        # Create SQLiteSession for maintaining conversation context
        from agents import SQLiteSession, Runner
        from backend.database.agent_db import get_db_path
        import os
        
        db_path = get_db_path(agent.DB_PATH if hasattr(agent, 'DB_PATH') else None)
        db_dir = os.path.dirname(db_path)
        session_db_path = os.path.join(db_dir, "session_history.db")
        
        # Ensure directory exists
        os.makedirs(db_dir, exist_ok=True)
        
        # Create SQLiteSession instance - this will maintain conversation history
        session = SQLiteSession(session_id, session_db_path)
        
        # Add user message to session (for our own tracking)
        from backend.database.session_db import add_conversation
        add_conversation(session_id, "user", request.message)
        
        # DEBUG: Log agent instructions before running (especially for NoteBookAgent)
        print(f"\n{'='*80}")
        print(f"[chat_with_agent] DEBUG: About to run agent {agent_id}")
        print(f"[chat_with_agent] Agent type: {type(agent).__name__}")
        if hasattr(agent, 'instructions'):
            instructions_preview = agent.instructions[:500] if agent.instructions else "NONE/EMPTY"
            print(f"[chat_with_agent] Agent instructions (first 500 chars):\n{instructions_preview}")
            if isinstance(agent, NoteBookAgent):
                if "{notes}" in agent.instructions:
                    print(f"[chat_with_agent] ⚠️  WARNING: Instructions still contain {{notes}} placeholder!")
                if "{tools_usage}" in agent.instructions:
                    print(f"[chat_with_agent] ⚠️  WARNING: Instructions still contain {{tools_usage}} placeholder!")
                print(f"[chat_with_agent] Full instructions length: {len(agent.instructions) if agent.instructions else 0}")
                # Also check notes
                notes_preview = agent.notes[:200] if hasattr(agent, 'notes') and agent.notes else "NONE/EMPTY"
                print(f"[chat_with_agent] Agent notes (first 200 chars):\n{notes_preview}")
        else:
            print(f"[chat_with_agent] Agent has no instructions attribute!")
        print(f"{'='*80}\n")
        
        # Run agent with tracing and tool logging hooks
        from backend.utils.tracing_collector import track_agent_run
        from backend.utils.tool_logging_hooks import ToolLoggingHook
        
        tool_logging_hook = ToolLoggingHook()
        with track_agent_run(session_id, agent, request.message):
            result = await Runner.run(agent, request.message, session=session, hooks=tool_logging_hook)
        
        # Extract response
        if hasattr(result, 'final_output'):
            response_text = result.final_output
        else:
            response_text = str(result)
        
        # Add assistant response to session
        add_conversation(session_id, "assistant", response_text)
        
        return ChatResponse(response=response_text, session_id=session_id)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in chat with agent {agent_id}: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}\n\nTraceback: {error_trace}")


@router.delete("/{agent_id}")
async def delete_agent_endpoint(agent_id: str):
    """Delete an agent (MasterAgent or NoteBookAgent)."""
    try:
        agent = load_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if trying to delete TopLevelAgent (not allowed)
        if isinstance(agent, TopLevelAgent):
            raise HTTPException(status_code=400, detail="Cannot delete TopLevelAgent")
        
        # For MasterAgent: recursively delete all sub-agents first
        if isinstance(agent, MasterAgent):
            sub_agent_ids = getattr(agent, 'sub_agent_ids', None) or []
            # IMPORTANT: Create a copy of the list since we'll be deleting agents
            for sub_id in list(sub_agent_ids):
                try:
                    sub_agent = load_agent(sub_id)
                    if sub_agent:
                        # Recursively delete sub-agent by calling this endpoint again
                        # This ensures proper cleanup (removing from parent's sub_agent_ids, etc.)
                        # Note: This will also remove sub_id from current agent's sub_agent_ids
                        await delete_agent_endpoint(sub_id)
                    else:
                        # Sub-agent doesn't exist, remove from sub_agent_ids
                        agent._remove_sub_agent_by_id(sub_id)
                except HTTPException as e:
                    # If sub-agent was already deleted or not found, continue
                    print(f"Warning: Sub-agent {sub_id} not found or already deleted: {e.detail}")
                    # Remove from sub_agent_ids if it's still there
                    if sub_id in (getattr(agent, 'sub_agent_ids', None) or []):
                        agent._remove_sub_agent_by_id(sub_id)
                except Exception as e:
                    print(f"Warning: Failed to delete sub-agent {sub_id}: {e}")
                    # Continue deleting other sub-agents even if one fails
        
        # Remove from parent's sub_agent_ids (if has parent)
        # IMPORTANT: Do this BEFORE deleting from database, so parent can still find the agent
        if hasattr(agent, 'parent_agent_id') and agent.parent_agent_id:
            parent = load_agent(agent.parent_agent_id)
            if parent:
                parent._remove_sub_agent_by_id(agent_id)
                # Double-check: ensure parent is saved after removing sub_agent
                parent.save_to_db()
        
        # Delete the agent from database
        deleted = delete_agent(agent_id, agent.DB_PATH if hasattr(agent, 'DB_PATH') else None)
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete agent from database")
        
        return {"message": "Agent deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting agent: {str(e)}")


@router.post("/reset-database")
async def reset_database():
    """Reset database to initial state: delete all agents and sessions, create TopLevelAgent and MasterAgent."""
    try:
        import sqlite3
        from backend.database.session_db import delete_session, list_sessions
        from backend.utils.agent_manager import get_agent_manager
        
        db_path = get_db_path()
        
        # Step 1: Clear AgentManager cache
        agent_manager = get_agent_manager()
        agent_manager._agent_cache.clear()
        print("[reset_database] Cleared AgentManager cache")
        
        # Step 2: Delete all agents from database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all agent IDs
        cursor.execute("SELECT id FROM agents")
        agent_ids = [row[0] for row in cursor.fetchall()]
        print(f"[reset_database] Found {len(agent_ids)} agents to delete")
        
        # Delete all agents
        cursor.execute("DELETE FROM agents")
        deleted_agents_count = cursor.rowcount
        conn.commit()
        conn.close()
        print(f"[reset_database] Deleted {deleted_agents_count} agents from database")
        
        # Step 3: Delete all sessions
        sessions = list_sessions(db_path)
        deleted_sessions_count = 0
        for session in sessions:
            if delete_session(session['id'], db_path):
                deleted_sessions_count += 1
        print(f"[reset_database] Deleted {deleted_sessions_count} sessions")
        
        # Step 4: Create TopLevelAgent (which will create MasterAgent automatically)
        # TopLevelAgent.__init__ will check for existing MasterAgent and create one if needed
        top_level_agent = TopLevelAgent(DB_PATH=db_path)
        top_level_agent.save_to_db()
        
        # Verify MasterAgent was created
        master_agent_id = None
        if top_level_agent.sub_agent_ids:
            master_agent_id = top_level_agent.sub_agent_ids[0]
        
        # Step 5: Initialize tools database (if not already initialized)
        # IMPORTANT: This only updates/inserts default tools using INSERT OR REPLACE,
        # it does NOT delete existing tools that are not in the default list.
        # This preserves all custom tools while ensuring default tools are available.
        from backend.database.init_tools_data import init_default_tools
        try:
            init_default_tools()
            print("[reset_database] Tools database initialized/updated (existing tools preserved)")
        except Exception as e:
            print(f"[reset_database] Warning: Failed to initialize tools: {e}")
        
        # Update the global TopLevelAgent instance in utils
        from backend.api.utils import get_top_level_agent
        # Clear the global cache so it will reload the new TopLevelAgent
        import backend.api.utils
        backend.api.utils._top_level_agent = None
        get_top_level_agent()  # This will reload the newly created TopLevelAgent
        
        return {
            "message": "Database reset successfully",
            "deleted_agents": deleted_agents_count,
            "deleted_sessions": deleted_sessions_count,
            "top_level_agent_id": top_level_agent.id,
            "master_agent_id": master_agent_id
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error resetting database: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error resetting database: {str(e)}")

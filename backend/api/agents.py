"""Agents API routes."""

from fastapi import APIRouter, HTTPException
from backend.api.utils import get_top_level_agent, _serialize_agent_card
from backend.agent.TopLevelAgent import TopLevelAgent
from backend.agent.MasterAgent import MasterAgent
from backend.agent.NoteBookAgent import NoteBookAgent
from backend.agent.BaseAgent import AgentType
from backend.database.agent_db import load_agent, load_all_agents
from backend.api.models import UpdateInstructionsRequest
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
            # Skip TopLevelAgent itself (it's not shown in the list)
            if isinstance(agent, TopLevelAgent):
                continue
            
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
                    if word_count > 3000:
                        reasons.append(f"字数({word_count}) > 3000")
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
                sub_agent = agent.load_agent_from_db_by_id(sub_id)
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
                                child_agent = sub_agent.load_agent_from_db_by_id(child_id)
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
        
        # Get current instructions
        current_instructions = getattr(agent, 'instructions', '') or ''
        
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

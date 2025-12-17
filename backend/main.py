"""FastAPI main application for AgentUniverse backend."""

import os
import uuid
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents import Runner

from backend.agent.TopLevelAgent import TopLevelAgent
from backend.agent.NoteBookAgent import NoteBookAgent
from backend.agent.BaseAgent import AgentType
from backend.database.agent_db import (
    load_agent,
    load_all_agents,
    delete_agent,
    get_agent_info_summary,
)
from backend.database.session_db import (
    create_session,
    get_session,
    list_sessions,
    delete_session,
    add_conversation,
    get_conversations,
)
from backend.tools.agent_utils import get_all_agent_info, generate_markdown_from_agent
from backend.tools.file_storage import save_uploaded_file, ensure_upload_dir
from backend.agent.specialized.AgentCard import AgentCard


def _serialize_agent_card(agent_card_result):
    """Serialize agent_card result to dict (handles both AgentCard objects and strings)."""
    if agent_card_result is None:
        return None
    if isinstance(agent_card_result, AgentCard):
        return agent_card_result.model_dump()
    # For backward compatibility with string-based agent_card (e.g., MasterAgent)
    return agent_card_result


# Initialize FastAPI app
app = FastAPI(title="AgentUniverse API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global TopLevelAgent instance (singleton pattern)
_top_level_agent: Optional[TopLevelAgent] = None


def get_top_level_agent() -> TopLevelAgent:
    """Get or create the TopLevelAgent instance."""
    global _top_level_agent
    if _top_level_agent is None:
        # Try to load from database first (look for TopLevel agent)
        agents = load_all_agents()
        for agent_id, agent in agents.items():
            if isinstance(agent, TopLevelAgent):
                _top_level_agent = agent
                # Ensure sub_agent_ids is not None after loading
                if not hasattr(_top_level_agent, 'sub_agent_ids') or _top_level_agent.sub_agent_ids is None:
                    _top_level_agent.sub_agent_ids = []
                break
        
        # If not found in database, create new one
        if _top_level_agent is None:
            _top_level_agent = TopLevelAgent()
            _top_level_agent.save_to_db()
        else:
            # Ensure sub_agent_ids is not None (safety check after loading from DB)
            if not hasattr(_top_level_agent, 'sub_agent_ids') or _top_level_agent.sub_agent_ids is None:
                _top_level_agent.sub_agent_ids = []
                _top_level_agent.save_to_db()
            
            # Ensure TopLevelAgent has a MasterAgent sub-agent
            # Check if it has any MasterAgent in sub_agent_ids
            has_master_agent = False
            from backend.agent.MasterAgent import MasterAgent
            sub_agent_ids = getattr(_top_level_agent, 'sub_agent_ids', None) or []
            for sub_id in sub_agent_ids:
                sub_agent = _top_level_agent.load_agent_from_db_by_id(sub_id)
                if sub_agent and isinstance(sub_agent, MasterAgent):
                    has_master_agent = True
                    break
            
            # If no MasterAgent found, create one
            if not has_master_agent:
                root_master = MasterAgent("Top Master Agent", parent_agent_id=_top_level_agent.id, DB_PATH=_top_level_agent.DB_PATH)
                root_master.save_to_db()
                _top_level_agent._add_sub_agents(root_master.id)
                # Update instructions
                agent_dict = _top_level_agent._load_sub_agents_dict()
                from backend.tools.agent_utils import get_all_agent_info
                from backend.prompts.prompt_loader import load_prompt
                instructions = load_prompt(
                    "top_level_agent",
                    variables={"agents_list": get_all_agent_info(agent_dict)}
                )
                _top_level_agent.instructions = instructions
                _top_level_agent.save_to_db()
    
    # Final safety check before returning
    if not hasattr(_top_level_agent, 'sub_agent_ids') or _top_level_agent.sub_agent_ids is None:
        _top_level_agent.sub_agent_ids = []
        _top_level_agent.save_to_db()
    
    # Ensure tools is not None
    if not hasattr(_top_level_agent, 'tools') or _top_level_agent.tools is None:
        if hasattr(_top_level_agent, '_recreate_tools'):
            try:
                _top_level_agent._recreate_tools()
            except Exception as e:
                print(f"Warning: Failed to recreate tools in get_top_level_agent: {e}")
                _top_level_agent.tools = []
        else:
            _top_level_agent.tools = []
    
    return _top_level_agent


# Request/Response Models
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


# API Routes

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AgentUniverse API", "version": "1.0.0"}


@app.get("/api/top-level-agent/info")
async def get_top_level_agent_info():
    """Get TopLevelAgent information."""
    try:
        from backend.agent.MasterAgent import MasterAgent
        from backend.agent.NoteBookAgent import NoteBookAgent
        
        agent = get_top_level_agent()
        agent_dict = agent._load_sub_agents_dict()
        info_text = get_all_agent_info(agent_dict)
        
        # Build structured response similar to hierarchy endpoint
        child_agents = []
        sub_agent_ids = getattr(agent, 'sub_agent_ids', None) or []
        
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
                    agent_type_frontend = 'master_agent'
                elif is_notebook:
                    agent_type_frontend = 'NOTEBOOK_AGENT'
                else:
                    agent_type_frontend = sub_type_str.lower().replace(' ', '_')
                
                # Get agent card
                agent_card = None
                if hasattr(sub_agent, 'agent_card') and callable(getattr(sub_agent, 'agent_card')):
                    try:
                        agent_card = _serialize_agent_card(sub_agent.agent_card())
                    except:
                        pass
                
                child_data = {
                    "agent_id": sub_agent.id,
                    "notebook_id": sub_agent.id,
                    "agent_name": getattr(sub_agent, 'name', 'Unknown'),
                    "name": getattr(sub_agent, 'name', 'Unknown'),
                    "type": sub_type_str,
                    "agent_type": agent_type_frontend,
                    "agent_card": agent_card,
                }
                
                # Add notebook-specific fields if it's a NoteBookAgent
                if is_notebook:
                    child_data['notebook_title'] = getattr(sub_agent, 'notebook_title', '')
                    child_data['description'] = getattr(sub_agent, 'notebook_description', '')
                    # Extract from agent_card if available
                    if agent_card:
                        if isinstance(agent_card, dict):
                            child_data['knowledge_summary'] = agent_card.get('summary', '')
                            child_data['content_topics'] = agent_card.get('topics', [])
                elif is_master:
                    child_data['description'] = ''
                    # Extract from agent_card if available
                    if agent_card and isinstance(agent_card, dict):
                        child_data['knowledge_summary'] = agent_card.get('summary', '')
                        child_data['content_topics'] = agent_card.get('topics', [])
                
                child_agents.append(child_data)
        
        # Get agent card for TopLevelAgent itself
        top_level_agent_card = None
        if hasattr(agent, 'agent_card') and callable(getattr(agent, 'agent_card')):
            try:
                top_level_agent_card = _serialize_agent_card(agent.agent_card())
            except:
                pass
        
        return {
            "instructions": agent.instructions,
            "agent_card": top_level_agent_card,
            "child_agents": child_agents,
            "info": info_text  # Keep for backward compatibility
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent info: {str(e)}")


@app.post("/api/top-level-agent/chat", response_model=ChatResponse)
async def chat_with_top_level_agent(request: ChatRequest):
    """Chat with TopLevelAgent."""
    try:
        agent = get_top_level_agent()
        
        # Ensure sub_agent_ids is not None
        if not hasattr(agent, 'sub_agent_ids') or agent.sub_agent_ids is None:
            agent.sub_agent_ids = []
            agent.save_to_db()
        
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
        
        # Create session if not provided
        session_id = request.session_id
        if not session_id:
            session_data = create_session()
            session_id = session_data['id']
        
        # Add user message to session
        add_conversation(session_id, "user", request.message)
        
        # Run agent
        result = await Runner.run(agent, request.message)
        
        # Extract response
        if hasattr(result, 'final_output'):
            response_text = str(result.final_output)
        else:
            response_text = str(result)
        
        # Add agent response to session
        add_conversation(session_id, "assistant", response_text)
        
        return ChatResponse(response=response_text, session_id=session_id)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in chat: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}\n\nTraceback: {error_trace}")


@app.post("/api/top-level-agent/sessions", response_model=SessionResponse)
async def create_top_level_agent_session(request: SessionCreateRequest):
    """Create a new chat session."""
    try:
        session_data = create_session(title=request.title)
        return SessionResponse(**session_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@app.get("/api/top-level-agent/sessions")
async def list_top_level_agent_sessions():
    """List all chat sessions."""
    try:
        sessions = list_sessions()
        return {"sessions": sessions}
    except Exception as e:
        import traceback
        error_detail = f"Error listing sessions: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/api/sessions/{session_id}/conversations")
async def get_session_conversations(session_id: str):
    """Get all conversations for a session."""
    try:
        conversations = get_conversations(session_id)
        return ConversationsResponse(conversations=conversations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversations: {str(e)}")


@app.delete("/api/sessions/{session_id}")
async def delete_session_endpoint(session_id: str):
    """Delete a session."""
    try:
        deleted = delete_session(session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")


def _serialize_agent_card(agent_card_result):
    """Serialize agent_card result to dict (handles both AgentCard objects and strings)."""
    if agent_card_result is None:
        return None
    if isinstance(agent_card_result, AgentCard):
        return agent_card_result.model_dump()
    # For backward compatibility with string-based agent_card (e.g., MasterAgent)
    return agent_card_result


@app.get("/api/agents")
async def list_agents():
    """List all agents."""
    try:
        # Ensure TopLevelAgent is initialized (this will create it if it doesn't exist)
        get_top_level_agent()
        
        agents = load_all_agents()
        agent_list = []
        for agent_id, agent in agents.items():
            agent_type = getattr(agent, 'type', 'Unknown')
            if isinstance(agent_type, AgentType):
                agent_type_str = agent_type.value
            else:
                agent_type_str = str(agent_type)
            
            # Determine if it's a MasterAgent or NoteBookAgent
            from backend.agent.MasterAgent import MasterAgent
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


@app.get("/api/agents/{agent_id}")
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
        from backend.agent.MasterAgent import MasterAgent
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


@app.get("/api/agents/{agent_id}/hierarchy")
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
            from backend.agent.MasterAgent import MasterAgent
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


@app.get("/api/notebooks/{notebook_id}")
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


@app.get("/api/notebooks/{notebook_id}/content")
async def get_notebook_content(notebook_id: str):
    """Get notebook content as structured data (JSON) or markdown fallback."""
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
        
        # Return structured data if available
        if hasattr(agent, 'outline') and hasattr(agent, 'sections') and agent.outline and agent.sections:
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


@app.post("/api/notebooks/{notebook_id}/split")
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


@app.delete("/api/notebooks/{notebook_id}")
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
        
        # Delete the agent
        deleted = delete_agent(notebook_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Notebook not found")
        
        return {"message": "Notebook deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting notebook: {str(e)}")


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the server."""
    try:
        # Ensure upload directory exists
        ensure_upload_dir()
        
        # Read file content
        file_content = await file.read()
        
        # Save file
        stored_path = save_uploaded_file(file.filename, file_content)
        
        return {
            "filename": os.path.basename(stored_path),
            "path": stored_path,
            "message": "File uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

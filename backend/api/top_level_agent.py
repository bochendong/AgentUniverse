"""TopLevelAgent API routes."""

from fastapi import APIRouter, HTTPException
from agents import Runner, SQLiteSession
from backend.api.models import ChatRequest, ChatResponse, SessionCreateRequest, SessionResponse
from backend.api.utils import get_top_level_agent, _serialize_agent_card
from backend.agent.TopLevelAgent import TopLevelAgent
from backend.agent.MasterAgent import MasterAgent
from backend.agent.NoteBookAgent import NoteBookAgent
from backend.agent.BaseAgent import AgentType
from backend.tools.agent_utils import get_all_agent_info
from backend.database.session_db import create_session
from backend.utils.tracing_collector import track_agent_run
from backend.database.agent_db import get_db_path
from backend.database.session_db import add_conversation
import os

router = APIRouter(prefix="/api/top-level-agent", tags=["top-level-agent"])


@router.post("/sessions", response_model=SessionResponse)
async def create_top_level_agent_session(request: SessionCreateRequest):
    """Create a new chat session."""
    try:
        session_data = create_session(title=request.title)
        return SessionResponse(**session_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@router.get("/sessions")
async def list_top_level_agent_sessions():
    """List all chat sessions."""
    try:
        from backend.database.session_db import list_sessions
        sessions = list_sessions()
        return {"sessions": sessions}
    except Exception as e:
        import traceback
        error_detail = f"Error listing sessions: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/info")
async def get_top_level_agent_info():
    """Get TopLevelAgent information."""
    try:
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


@router.post("/chat", response_model=ChatResponse)
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
        
        # Create SQLiteSession for maintaining conversation context
        # Use the same database directory as our session_db
        db_path = get_db_path()
        db_dir = os.path.dirname(db_path)
        session_db_path = os.path.join(db_dir, "session_history.db")
        
        # Ensure directory exists
        os.makedirs(db_dir, exist_ok=True)
        
        # Create SQLiteSession instance - this will maintain conversation history
        session = SQLiteSession(session_id, session_db_path)
        
        # Add user message to session (for our own tracking)
        from backend.database.session_db import add_conversation
        add_conversation(session_id, "user", request.message)
        
        # Run agent with tracing
        with track_agent_run(session_id, agent, request.message):
            result = await Runner.run(agent, request.message, session=session)
        
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
        print(f"Error in chat: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}\n\nTraceback: {error_trace}")

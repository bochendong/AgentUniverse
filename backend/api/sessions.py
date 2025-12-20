"""Session management API routes."""

from fastapi import APIRouter, HTTPException
from backend.api.models import SessionCreateRequest, SessionResponse, ConversationsResponse, TracingResponse
from backend.database.session_db import (
    create_session,
    list_sessions,
    delete_session,
    get_conversations,
)
from backend.utils.tracing_collector import get_traces, get_current_activity, clear_traces

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse)
async def create_top_level_agent_session(request: SessionCreateRequest):
    """Create a new session."""
    try:
        session_data = create_session(title=request.title)
        return SessionResponse(**session_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@router.get("")
async def list_top_level_agent_sessions():
    """List all sessions."""
    try:
        sessions = list_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")


@router.get("/{session_id}/conversations", response_model=ConversationsResponse)
async def get_session_conversations(session_id: str):
    """Get conversations for a session."""
    try:
        conversations = get_conversations(session_id)
        return ConversationsResponse(conversations=conversations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversations: {str(e)}")


@router.get("/{session_id}/tracing", response_model=TracingResponse)
async def get_session_tracing(session_id: str, limit: int = 100):
    """Get tracing information for a session."""
    try:
        traces = get_traces(session_id, limit=limit)
        current_activity = get_current_activity(session_id)
        return TracingResponse(traces=traces, current_activity=current_activity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tracing: {str(e)}")


@router.delete("/{session_id}/tracing")
async def clear_session_tracing(session_id: str):
    """Clear tracing information for a session."""
    try:
        clear_traces(session_id)
        return {"message": "Tracing cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing tracing: {str(e)}")


@router.delete("/{session_id}")
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

"""
Tracing Collector Module
Collects tracing information from agent execution and stores it for frontend display.
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict
import threading
import contextvars
import uuid

# In-memory storage for traces (keyed by session_id)
_traces: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
_traces_lock = threading.Lock()

# Context variable to track current trace
_current_trace: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('current_trace', default=None)
# Context variable to track current session_id
_current_session: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('current_session', default=None)


class TracingContext:
    """Context manager to track agent execution."""
    
    def __init__(self, session_id: str, agent: Any, message: str, activity_type: str = "agent_run"):
        self.session_id = session_id
        self.agent = agent
        self.message = message
        self.activity_type = activity_type
        self.activity_id = str(uuid.uuid4())
        self.started_at = None
        self.ended_at = None
        
    def __enter__(self):
        self.started_at = datetime.now()
        
        # Extract agent info
        agent_info = {
            'name': getattr(self.agent, 'name', None) or getattr(self.agent, '_name', 'Unknown'),
            'id': getattr(self.agent, 'id', None),
            'agent_type': str(getattr(self.agent, 'type', None) or getattr(self.agent, 'agent_type', 'unknown')),
        }
        
        activity = {
            'id': self.activity_id,
            'type': self.activity_type,
            'session_id': self.session_id,
            'agent_info': agent_info,
            'message': self.message[:200] if len(self.message) > 200 else self.message,  # Truncate long messages
            'started_at': self.started_at.isoformat(),
            'ended_at': None,
            'status': 'running',
            'timestamp': self.started_at.isoformat(),
        }
        
        with _traces_lock:
            _traces[self.session_id].append(activity)
        
        # Set context variables
        _current_trace.set(self.activity_id)
        _current_session.set(self.session_id)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ended_at = datetime.now()
        
        # Update activity status
        with _traces_lock:
            session_traces = _traces.get(self.session_id, [])
            for activity in reversed(session_traces):
                if activity.get('id') == self.activity_id:
                    activity['ended_at'] = self.ended_at.isoformat()
                    activity['status'] = 'completed' if exc_type is None else 'failed'
                    activity['error'] = str(exc_val) if exc_val else None
                    break
        
        # Clear context variables
        _current_trace.set(None)
        # Keep session_id in context for nested calls
        
        return False  # Don't suppress exceptions


def track_agent_run(session_id: str, agent: Any, message: str):
    """Track an agent run."""
    return TracingContext(session_id, agent, message, "agent_run")


def track_tool_call(session_id: str, agent: Any, tool_name: str, tool_args: Dict[str, Any] = None):
    """Track a tool call."""
    message = f"Calling tool: {tool_name}"
    if tool_args:
        message += f" with args: {str(tool_args)[:100]}"
    return TracingContext(session_id, agent, message, "tool_call")


def get_current_session_id() -> Optional[str]:
    """Get current session ID from context."""
    return _current_session.get()


def get_traces(session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get traces for a session."""
    with _traces_lock:
        return _traces.get(session_id, [])[-limit:]


def get_current_activity(session_id: str) -> Optional[Dict[str, Any]]:
    """Get current activity for a session."""
    with _traces_lock:
        session_traces = _traces.get(session_id, [])
        # Find the most recent active (not ended) activity
        for activity in reversed(session_traces):
            if activity.get('status') == 'running' and not activity.get('ended_at'):
                return activity
    return None


def clear_traces(session_id: str):
    """Clear traces for a session."""
    with _traces_lock:
        if session_id in _traces:
            del _traces[session_id]


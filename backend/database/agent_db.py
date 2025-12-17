"""Agent database operations using SQLite."""

import sqlite3
import pickle
import json
import os
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from pathlib import Path

# Import agent classes only for type checking to avoid circular imports
if TYPE_CHECKING:
    from backend.agent.BaseAgent import BaseAgent, AgentType
    from backend.agent.MasterAgent import MasterAgent
    from backend.agent.NoteBookAgent import NoteBookAgent
    from backend.agent.TopLevelAgent import TopLevelAgent


# Default DB path - stored in backend/database/db/ directory
DB_DIR = os.path.join(os.path.dirname(__file__), "db")
DEFAULT_DB_PATH = os.path.join(DB_DIR, "agent_data.db")


def get_db_path(db_path: Optional[str] = None) -> str:
    """Get database path, using default if not provided."""
    if db_path:
        return db_path
    # Ensure the db directory exists
    os.makedirs(DB_DIR, exist_ok=True)
    return DEFAULT_DB_PATH


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize the database with agents table."""
    db_path = get_db_path(db_path)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create agents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            parent_agent_id TEXT,
            sub_agent_ids TEXT,
            data BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def save_agent(agent: Any, db_path: Optional[str] = None) -> bool:
    """
    Save an agent to the database.
    
    Args:
        agent: The agent object to save
        db_path: Optional database path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Import AgentType locally to avoid circular import
        from backend.agent.BaseAgent import AgentType
        
        db_path = get_db_path(db_path)
        init_db(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Temporarily remove tools before serialization (function_tool cannot be pickled)
        original_tools = getattr(agent, 'tools', None)
        agent.tools = None
        
        try:
            # Serialize agent data using pickle
            agent_data = pickle.dumps(agent)
        finally:
            # Restore tools after serialization
            agent.tools = original_tools
        
        # Get sub_agent_ids as JSON string
        sub_agent_ids_json = json.dumps(getattr(agent, 'sub_agent_ids', []))
        
        # Get agent type - handle both AgentType enum and string
        agent_type = getattr(agent, 'type', AgentType.BASE_AGENT)
        if isinstance(agent_type, AgentType):
            agent_type_str = agent_type.value
        else:
            # Handle legacy string types or convert to string
            agent_type_str = str(agent_type) if agent_type else AgentType.BASE_AGENT.value
        
        # Check if agent exists
        cursor.execute("SELECT id FROM agents WHERE id = ?", (agent.id,))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing agent
            cursor.execute("""
                UPDATE agents 
                SET type = ?, name = ?, parent_agent_id = ?, sub_agent_ids = ?, 
                    data = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                agent_type_str,
                getattr(agent, 'name', ''),
                getattr(agent, 'parent_agent_id', None),
                sub_agent_ids_json,
                agent_data,
                agent.id
            ))
        else:
            # Insert new agent
            cursor.execute("""
                INSERT INTO agents (id, type, name, parent_agent_id, sub_agent_ids, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                agent.id,
                agent_type_str,
                getattr(agent, 'name', ''),
                getattr(agent, 'parent_agent_id', None),
                sub_agent_ids_json,
                agent_data
            ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving agent: {str(e)}")
        return False


def load_agent(agent_id: str, db_path: Optional[str] = None) -> Optional[Any]:
    """
    Load an agent from the database by ID, verifying the type matches.
    
    Args:
        agent_id: The agent ID to load
        db_path: Optional database path
        
    Returns:
        The loaded agent object (BaseAgent or subclass), or None if not found
    """
    try:
        # Import agent classes locally to avoid circular import
        from backend.agent.BaseAgent import BaseAgent, AgentType
        from backend.agent.MasterAgent import MasterAgent
        from backend.agent.NoteBookAgent import NoteBookAgent
        from backend.agent.TopLevelAgent import TopLevelAgent
        
        db_path = get_db_path(db_path)
        
        if not os.path.exists(db_path):
            return None
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get both type and data
        cursor.execute("SELECT type, data FROM agents WHERE id = ?", (agent_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            expected_type, agent_data = row
            
            # Deserialize agent data
            agent = pickle.loads(agent_data)
            
            # Verify the loaded agent is a BaseAgent instance
            if not isinstance(agent, BaseAgent):
                return None
            
            # Convert string type from DB to AgentType enum if needed
            actual_type = getattr(agent, 'type', None)
            if isinstance(actual_type, AgentType):
                actual_type_str = actual_type.value
            else:
                actual_type_str = str(actual_type) if actual_type else None
            
            # Map expected type to class for validation
            type_to_class = {
                AgentType.BASE_AGENT.value: BaseAgent,
                AgentType.MASTER.value: MasterAgent,
                AgentType.NOTEBOOK.value: NoteBookAgent,
                AgentType.TOP_LEVEL.value: TopLevelAgent,
            }
            
            # Verify the agent is of the correct class type
            expected_class = type_to_class.get(expected_type, BaseAgent)
            
            # Recreate tools after loading (tools were removed before serialization)
            # This needs to be done after loading because function_tool cannot be pickled
            if hasattr(agent, '_recreate_tools'):
                try:
                    agent._recreate_tools()
                except Exception:
                    pass
            
            # Ensure type is set as AgentType enum if it's a string
            if not isinstance(actual_type, AgentType) and actual_type_str:
                # Try to map string back to enum
                for agent_type_enum in AgentType:
                    if agent_type_enum.value == actual_type_str:
                        agent.type = agent_type_enum
                        break
            
            # Ensure sub_agent_ids is not None (safety check)
            if not hasattr(agent, 'sub_agent_ids') or agent.sub_agent_ids is None:
                agent.sub_agent_ids = []
            
            # Ensure tools is not None (safety check)
            # Tools are recreated by _recreate_tools, but if that fails, ensure it's at least an empty list
            if not hasattr(agent, 'tools') or agent.tools is None:
                agent.tools = []
            
            return agent
        
        return None
    except Exception as e:
        print(f"Error loading agent {agent_id}: {str(e)}")
        return None


def load_all_agents(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load all agents from the database.
    
    Args:
        db_path: Optional database path
        
    Returns:
        Dictionary mapping agent IDs to agent objects
    """
    try:
        db_path = get_db_path(db_path)
        
        if not os.path.exists(db_path):
            return {}
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, data FROM agents")
        rows = cursor.fetchall()
        
        conn.close()
        
        agents = {}
        for agent_id, agent_data in rows:
            try:
                agent = pickle.loads(agent_data)
                agents[agent_id] = agent
            except Exception as e:
                print(f"Error deserializing agent {agent_id}: {str(e)}")
        
        return agents
    except Exception as e:
        print(f"Error loading all agents: {str(e)}")
        return {}


def delete_agent(agent_id: str, db_path: Optional[str] = None) -> bool:
    """
    Delete an agent from the database.
    
    Args:
        agent_id: The agent ID to delete
        db_path: Optional database path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db_path = get_db_path(db_path)
        
        if not os.path.exists(db_path):
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
        conn.commit()
        
        deleted = cursor.rowcount > 0
        conn.close()
        
        return deleted
    except Exception as e:
        print(f"Error deleting agent {agent_id}: {str(e)}")
        return False


def get_agent_info_summary(db_path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Get summary information about all agents (without loading full objects).
    
    Args:
        db_path: Optional database path
        
    Returns:
        Dictionary mapping agent IDs to summary info
    """
    try:
        db_path = get_db_path(db_path)
        
        if not os.path.exists(db_path):
            return {}
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, type, name, parent_agent_id, sub_agent_ids 
            FROM agents
        """)
        rows = cursor.fetchall()
        
        conn.close()
        
        summary = {}
        for row in rows:
            agent_id, agent_type, name, parent_id, sub_agent_ids_json = row
            sub_agent_ids = json.loads(sub_agent_ids_json) if sub_agent_ids_json else []
            summary[agent_id] = {
                'type': agent_type,
                'name': name,
                'parent_agent_id': parent_id,
                'sub_agent_ids': sub_agent_ids
            }
        
        return summary
    except Exception as e:
        print(f"Error getting agent info summary: {str(e)}")
        return {}

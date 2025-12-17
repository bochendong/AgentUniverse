"""Agent Database Manager - provides high-level API for agent database operations."""

import os
from typing import Optional, TYPE_CHECKING
from pathlib import Path

from backend.database.agent_db import (
    init_db,
    save_agent,
    load_agent,
    delete_agent as db_delete_agent,
    get_db_path,
)

# Import agent classes only for type checking to avoid circular imports
if TYPE_CHECKING:
    from backend.agent.BaseAgent import BaseAgent


class AgentDBManager:
    """Manager class for agent database operations.
    
    Provides a clean API for creating, loading, updating, and deleting agents.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the AgentDBManager.
        
        Args:
            db_path: Optional database path. If not provided, uses default path
                    in backend/database/db/ directory.
        """
        if db_path is None:
            # Use default path in backend/database/db/ directory
            db_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "backend",
                "database",
                "db"
            )
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "agent_data.db")
        
        self.db_path = db_path
        # Initialize database if it doesn't exist
        init_db(self.db_path)
    
    def create_new(self, agent: 'BaseAgent') -> bool:
        """
        Create a new agent in the database.
        
        Args:
            agent: The agent object to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if agent already exists
            existing = load_agent(agent.id, self.db_path)
            if existing is not None:
                print(f"Warning: Agent with ID {agent.id} already exists. Use update_agent() to update.")
                return False
            
            # Set the agent's DB_PATH to match this manager's path
            agent.DB_PATH = self.db_path
            
            # Save the agent
            return save_agent(agent, self.db_path)
        except Exception as e:
            print(f"Error creating agent: {str(e)}")
            return False
    
    def load_agent_by_id(self, agent_id: str) -> Optional['BaseAgent']:
        """
        Load an agent from the database by ID.
        
        Args:
            agent_id: The agent ID to load
            
        Returns:
            The loaded agent object, or None if not found
        """
        try:
            agent = load_agent(agent_id, self.db_path)
            if agent:
                # Set the agent's DB_PATH to match this manager's path
                agent.DB_PATH = self.db_path
            return agent
        except Exception as e:
            print(f"Error loading agent {agent_id}: {str(e)}")
            return None
    
    def update_agent(self, agent: 'BaseAgent') -> bool:
        """
        Update an existing agent in the database.
        
        Args:
            agent: The agent object to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if agent exists
            existing = load_agent(agent.id, self.db_path)
            if existing is None:
                print(f"Warning: Agent with ID {agent.id} does not exist. Use create_new() to create.")
                return False
            
            # Set the agent's DB_PATH to match this manager's path
            agent.DB_PATH = self.db_path
            
            # Save the agent (save_agent handles both insert and update)
            return save_agent(agent, self.db_path)
        except Exception as e:
            print(f"Error updating agent: {str(e)}")
            return False
    
    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent from the database.
        
        Args:
            agent_id: The agent ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return db_delete_agent(agent_id, self.db_path)
        except Exception as e:
            print(f"Error deleting agent {agent_id}: {str(e)}")
            return False
    
    def get_db_path(self) -> str:
        """
        Get the database path used by this manager.
        
        Returns:
            The database path
        """
        return self.db_path

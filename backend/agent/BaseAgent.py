"""BaseAgent - base class for all agent implementations."""

import uuid
import asyncio
import concurrent.futures
from enum import Enum
from typing import Dict, Any, List, Optional
from agents import Agent, Runner
from backend.database.agent_db import get_agent_info_summary
from backend.database import AgentDBManager


class AgentType(Enum):
    """Agent type enumeration."""
    BASE_AGENT = "Base Agent"
    MASTER = "Master"
    NOTEBOOK = "NoteBook"
    TOP_LEVEL = "TopLevel"
    
    def __str__(self) -> str:
        """Return the string value of the enum."""
        return self.value


class BaseAgent(Agent):
    """Base class for all agents in the system.
    
    Provides common functionality:
    - UUID-based ID generation
    - Message receiving and processing
    - Common tool functions (send_message)
    """
    
    def __init__(
        self,
        name: str,
        instructions: str,
        tools: Optional[List] = None,
        mcp_config: Optional[Dict] = None,
        agent_type: AgentType = AgentType.BASE_AGENT,
        sub_agent_ids: Optional[List[str]] = None,
        parent_agent_id: Optional[str] = None,
        DB_PATH: Optional[str] = None,
    ):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name
            instructions: Agent instructions/prompt
            tools: List of tool functions
            mcp_config: MCP configuration dictionary
            agent_type: Agent type (default: AgentType.BASE_AGENT)
            sub_agent_ids: Initial list of sub-agent IDs (optional)
            parent_agent_id: ID of the parent agent (optional), Top Agent does not have parent agent
            DB_PATH: Database path (optional)
        """
        # Generate unique ID
        self.id = str(uuid.uuid4())
        
        # Store parent agent ID
        self.parent_agent_id = parent_agent_id
        
        # Initialize agent list for managing sub-agents (if needed)
        self.sub_agent_ids = sub_agent_ids if sub_agent_ids is not None else []

        # Set type (use provided type or default)
        self.type = agent_type
        self.DB_PATH = DB_PATH
        
        # Initialize the base Agent class
        super().__init__(
            name=name,
            instructions=instructions,
            tools=tools or [],
            mcp_config=mcp_config or {}
        )
    
    def _get_db_manager(self) -> AgentDBManager:
        """
        Get or create an AgentDBManager instance for this agent.
        
        Returns:
            AgentDBManager instance configured with this agent's DB_PATH
        """
        return AgentDBManager(db_path=self.DB_PATH)
    
    def _recreate_tools(self):
        """
        Recreate tools after loading from database (tools cannot be pickled).
        
        Base implementation: creates send_message tool if agent has sub-agents.
        Subclasses should override this method to add their specific tools.
        """
        # Default: only create send_message tool if agent has sub-agents
        sub_agent_ids = getattr(self, 'sub_agent_ids', None) or []
        if sub_agent_ids:
            send_message = self._create_send_message_tool()
            self.tools = [send_message]
        else:
            self.tools = []
    
    async def receive_messgae(self, message: str):
        """
        Receive and process a message.
        
        Args:
            message: The message to process
            
        Returns:
            The result of processing the message
        """
        result = await Runner.run(self, message)
        return result
    
    def run_async_safely(self, coro):
        """
        Safely run an async coroutine from a synchronous context.
        Handles different event loop states (running, not running, or doesn't exist).
        
        Args:
            coro: The coroutine to run
            
        Returns:
            The result of the coroutine
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            if loop.is_running():
                # If event loop is already running, create a new one in a separate thread
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    def run_in_new_loop():
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            return new_loop.run_until_complete(coro)
                        finally:
                            new_loop.close()
                    
                    future = executor.submit(run_in_new_loop)
                    return future.result()
            else:
                # Event loop exists but is not running, use it directly
                return loop.run_until_complete(coro)
        except Exception as e:
            raise RuntimeError(f"Error running async function: {str(e)}") from e
    
    def _create_send_message_tool(self):
        """
        Create a send_message tool function for communicating with sub-agents.
        
        Returns:
            A function_tool decorated function for sending messages
        """
        # Import here to avoid circular import
        from backend.tools.agent_tools import create_send_message_tool
        return create_send_message_tool(self)
    
    def _add_sub_agents(self, id: str) -> None:
        """
        Add a sub-agent ID to the list if it doesn't already exist.
        
        Args:
            id: Agent ID to add
        """
        if id not in self.sub_agent_ids:
            self.sub_agent_ids.append(id)
            # Save to database after adding
            self.save_to_db()

    def _remove_sub_agent_by_id(self, id: str) -> None:
        """
        Remove a sub-agent ID from the list.
        
        Args:
            id: Agent ID to remove
        """
        sub_agent_ids = getattr(self, 'sub_agent_ids', None) or []
        if id in sub_agent_ids:
            sub_agent_ids.remove(id)
            self.sub_agent_ids = sub_agent_ids
            # Save to database after removing
            self.save_to_db()

    def save_to_db(self) -> None:
        """
        Save the agent to the database.
        Uses AgentDBManager to handle create/update logic.
        First tries to update, if agent doesn't exist, creates it.
        """
        db_manager = self._get_db_manager()
        # Try to update first (most common case)
        success = db_manager.update_agent(self)
        # If update failed because agent doesn't exist, create it
        if not success:
            db_manager.create_new(self)

    def load_agent_from_db_by_id(self, agent_id: str) -> Optional['BaseAgent']:
        """
        Load an agent from the database by ID.
        The agent type is determined from the database and the correct class is loaded.
        
        Args:
            agent_id: The agent ID to load
            
        Returns:
            The loaded agent object (BaseAgent or subclass), or None if not found
        """
        db_manager = self._get_db_manager()
        return db_manager.load_agent_by_id(agent_id)

    def _get_sub_agent_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all sub-agents from the database.
        
        Returns:
            Dictionary mapping agent IDs to summary info
        """
        summary = get_agent_info_summary(self.DB_PATH)
        # Filter to only include sub-agents
        sub_agent_ids = getattr(self, 'sub_agent_ids', None) or []
        sub_agent_info = {
            agent_id: info 
            for agent_id, info in summary.items() 
            if agent_id in sub_agent_ids
        }
        return sub_agent_info

    def change_parent_id(self, new_parent_id: Optional[str]) -> None:
        """
        Change the parent agent ID and save to database.
        
        Args:
            new_parent_id: New parent agent ID (can be None to remove parent)
        """
        old_parent_id = self.parent_agent_id
        self.parent_agent_id = new_parent_id
        
        # If had an old parent, remove self from old parent's sub_agent_ids
        if old_parent_id:
            old_parent = self.load_agent_from_db_by_id(old_parent_id)
            if old_parent:
                old_parent._remove_sub_agent_by_id(self.id)
        
        # If has a new parent, add self to new parent's sub_agent_ids
        if new_parent_id:
            new_parent = self.load_agent_from_db_by_id(new_parent_id)
            if new_parent:
                new_parent._add_sub_agents(self.id)
        
        # Save self to database
        self.save_to_db()



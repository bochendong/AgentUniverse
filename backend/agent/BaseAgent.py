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
    NOTEBOOK_MODIFY = "NoteBookModify"
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
        
        # Get model name from config
        from backend.config.model_config import get_model_name
        model_name = get_model_name()
        
        # Debug: Print model being used (only for TopLevelAgent to avoid spam)
        if agent_type == AgentType.TOP_LEVEL:
            print(f"[BaseAgent] TopLevelAgent 使用模型: {model_name}")
        
        # Initialize the base Agent class
        # 直接使用 model 参数，SDK 会自动为 GPT-5 模型应用默认的 reasoning 和 verbosity 设置
        super().__init__(
            name=name,
            instructions=instructions,
            tools=tools or [],
            mcp_config=mcp_config or {},
            model=model_name
        )
    
    def _get_db_manager(self) -> AgentDBManager:
        """
        Get or create an AgentDBManager instance for this agent.
        
        Returns:
            AgentDBManager instance configured with this agent's DB_PATH
        """
        return AgentDBManager(db_path=self.DB_PATH)
    
    def _recreate_tools_from_db(self, tool_ids: List[str], db_path: Optional[str] = None):
        """
        Recreate tools from database using tool IDs.
        
        Args:
            tool_ids: List of tool names/IDs from database
            db_path: Optional database path
        """
        from backend.tools.tool_registry import get_tool_registry

        registry = get_tool_registry()
        tools = []
        for tool_id in tool_ids:
            # For function tools, no kwargs needed
            # For agent_as_tool, they need runtime parameters, so skip them here
            # agent_as_tool should be created on-demand with proper parameters
            metadata = registry.get_tool_metadata(tool_id)
            if metadata and metadata.tool_type == "agent_as_tool":
                # Skip agent_as_tool - they need runtime parameters
                # They should be created explicitly when needed
                print(f"[_recreate_tools_from_db] Skipping agent_as_tool: {tool_id}")
                continue

            tool = registry.create_tool(tool_id, self)
            if tool:
                tools.append(tool)
                print(f"[_recreate_tools_from_db] Successfully created tool: {tool_id}")
            else:
                print(f"[_recreate_tools_from_db] Failed to create tool: {tool_id}")
        self.tools = tools
        print(f"[_recreate_tools_from_db] Total tools created: {len(tools)}")
    
    def _recreate_tools(self):
        """
        Recreate tools after loading from database (tools cannot be pickled).
        
        Base implementation: loads tools from database using tool_ids.
        If no tool_ids in database, creates send_message tool if agent has sub-agents.
        """
        # Try to load tools from database first
        tool_ids = self._get_tool_ids_from_db()
        if tool_ids:
            self._recreate_tools_from_db(tool_ids)
        else:
            # Fallback: create send_message tool if agent has sub-agents
            sub_agent_ids = getattr(self, 'sub_agent_ids', None) or []
            if sub_agent_ids:
                from backend.tools.tool_registry import get_tool_registry
                registry = get_tool_registry()
                send_message = registry.create_tool("send_message", self)
                if send_message:
                    self.tools = [send_message]
                else:
                    self.tools = []
            else:
                self.tools = []
    
    def _get_tool_ids_from_db(self) -> List[str]:
        """Get tool_ids from database."""
        import json
        import sqlite3
        from backend.database.agent_db import get_db_path
        
        db_path = get_db_path(self.DB_PATH if hasattr(self, 'DB_PATH') else None)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        tool_ids_json = None
        try:
            cursor.execute("SELECT tool_ids FROM agents WHERE id = ?", (self.id,))
            row = cursor.fetchone()
            if row and row[0]:
                tool_ids_json = row[0]
        except sqlite3.OperationalError:
            pass
        
        conn.close()
        
        if tool_ids_json and tool_ids_json != '[]':
            try:
                return json.loads(tool_ids_json)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def add_tool(self, tool_id: str):
        """Dynamically add a tool to this agent."""
        from backend.tools.tool_registry import get_tool_registry
        
        registry = get_tool_registry()
        tool = registry.create_tool(tool_id, self)
        if tool:
            if self.tools is None:
                self.tools = []
            self.tools.append(tool)
            self._save_tool_ids_to_db()
            return True
        return False
    
    def remove_tool(self, tool_id: str):
        """Dynamically remove a tool from this agent."""
        if self.tools:
            # Remove tool by checking _tool_id attribute
            self.tools = [
                t for t in self.tools 
                if getattr(t, '_tool_id', None) != tool_id
            ]
            self._save_tool_ids_to_db()
    
    def _save_tool_ids_to_db(self):
        """Save current tool_ids to database."""
        import json
        import sqlite3
        from backend.database.agent_db import get_db_path
        
        # Extract tool_ids from current tools
        tool_ids = []
        if self.tools:
            for tool in self.tools:
                tool_id = getattr(tool, '_tool_id', None)
                if tool_id:
                    tool_ids.append(tool_id)
        
        db_path = get_db_path(self.DB_PATH if hasattr(self, 'DB_PATH') else None)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        tool_ids_json = json.dumps(tool_ids, ensure_ascii=False)
        cursor.execute(
            "UPDATE agents SET tool_ids = ? WHERE id = ?",
            (tool_ids_json, self.id)
        )
        
        conn.commit()
        conn.close()
    
    async def receive_messgae(self, message: str):
        """
        Receive and process a message.
        
        Args:
            message: The message to process
            
        Returns:
            The result of processing the message
        """
        # Try to get session_id from context (set by tracing_collector)
        from backend.utils.tracing_collector import get_current_session_id, track_agent_run
        
        session_id = get_current_session_id()
        
        # Add tool logging hook
        from backend.utils.tool_logging_hooks import ToolLoggingHook
        tool_logging_hook = ToolLoggingHook()
        
        if session_id:
            # Track this agent run if we have a session_id
            with track_agent_run(session_id, self, message):
                result = await Runner.run(self, message, hooks=tool_logging_hook)
        else:
            # No session_id, run without tracing but with tool logging
            result = await Runner.run(self, message, hooks=tool_logging_hook)
        
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
        from backend.tools.tool_registry import get_tool_registry
        registry = get_tool_registry()
        return registry.create_tool("send_message", self)
    
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
            # IMPORTANT: Must save to ensure parent's sub_agent_ids is updated in database
            self.save_to_db()
            print(f"[_remove_sub_agent_by_id] Removed {id} from {self.id}.sub_agent_ids. New list: {self.sub_agent_ids}")
        else:
            print(f"[_remove_sub_agent_by_id] Warning: {id} not found in {self.id}.sub_agent_ids (current: {sub_agent_ids})")

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
        
        This method now uses AgentManager to ensure tools are properly restored
        and to avoid unnecessary database writes.
        
        Args:
            agent_id: The agent ID to load
            
        Returns:
            The loaded agent object (BaseAgent or subclass), or None if not found
        """
        # Use AgentManager for consistent wake-up behavior
        from backend.utils.agent_manager import wake_agent
        return wake_agent(agent_id, db_path=getattr(self, 'DB_PATH', None))

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



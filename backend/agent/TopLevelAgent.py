"""TopLevelAgent - simplified implementation following the effective design pattern."""

from typing import Dict, Any, Optional

from backend.agent.BaseAgent import BaseAgent, AgentType
from backend.agent.MasterAgent import MasterAgent
from backend.tools.agent_utils import get_all_agent_info
from backend.prompts.prompt_loader import load_prompt


class TopLevelAgent(BaseAgent):
    """Top-level agent that manages the root MasterAgent."""
    
    def __init__(self, DB_PATH: Optional[str] = None):
        # Load prompt from file (will update after creating MasterAgent)
        instructions = load_prompt(
            "top_level_agent",
            variables={"agents_list": get_all_agent_info({})}
        )
        
        # Initialize the base class first (this creates self.id)
        super().__init__(
            name="TopLevelAgent",
            instructions=instructions,
            tools=None,  # Will create after initialization
            mcp_config={},
            agent_type=AgentType.TOP_LEVEL,
            parent_agent_id=None,  # Top level has no parent
            DB_PATH=DB_PATH
        )
        
        # Save to database after initialization
        self.save_to_db()
        
        # Create root MasterAgent after we have self.id
        root_master = MasterAgent("Top Master Agent", parent_agent_id=self.id, DB_PATH=self.DB_PATH)
        
        # Save root master to database
        root_master.save_to_db()
        
        # Add root master to sub_agent_ids
        self._add_sub_agents(root_master.id)
        
        # Update instructions with actual agent list
        agent_dict = self._load_sub_agents_dict()
        instructions = load_prompt(
            "top_level_agent",
            variables={"agents_list": get_all_agent_info(agent_dict)}
        )
        self.instructions = instructions
        
        # Create tools
        # Import here to avoid circular import
        from backend.tools.agent_tools import create_handle_file_upload_tool
        send_message = self._create_send_message_tool()
        handle_file_upload = create_handle_file_upload_tool(self)
        
        # Set tools list
        self.tools = [send_message, handle_file_upload]
    
    def _recreate_tools(self):
        """Recreate tools after loading from database (tools cannot be pickled)."""
        from backend.tools.agent_tools import create_handle_file_upload_tool
        send_message = self._create_send_message_tool()
        handle_file_upload = create_handle_file_upload_tool(self)
        self.tools = [send_message, handle_file_upload]
    
    def _load_sub_agents_dict(self) -> Dict[str, Any]:
        """
        Load all sub-agents from database and return as dictionary.
        
        Returns:
            Dictionary mapping agent IDs to agent objects (never None, always a dict)
        """
        agent_dict = {}
        try:
            sub_agent_ids = getattr(self, 'sub_agent_ids', None) or []
            for agent_id in sub_agent_ids:
                try:
                    agent = self.load_agent_from_db_by_id(agent_id)
                    if agent:
                        agent_dict[agent_id] = agent
                except Exception:
                    # Skip agents that can't be loaded
                    continue
        except Exception:
            # Return empty dict if anything goes wrong
            pass
        return agent_dict
    
    def agent_card(self) -> str:
        """返回agent card信息"""
        agent_dict = self._load_sub_agents_dict()
        return get_all_agent_info(agent_dict)


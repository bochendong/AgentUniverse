"""TopLevelAgent - simplified implementation following the effective design pattern."""

from typing import Dict, Any, Optional

from backend.agent.BaseAgent import BaseAgent, AgentType
from backend.agent.MasterAgent import MasterAgent
from backend.tools.utils import get_all_agent_info
from backend.prompts.prompt_loader import load_prompt
from agents import AgentOutputSchema
from backend.api.models import StructuredMessageData
from backend.config.model_config import get_model_settings


class TopLevelAgent(BaseAgent):
    """Top-level agent that manages the root MasterAgent."""
    
    def __init__(self, DB_PATH: Optional[str] = None):
        # Set output_type for structured output
        # This allows the agent to return StructuredMessageData directly
        output_type = AgentOutputSchema(StructuredMessageData, strict_json_schema=False)
        
        # Initialize the base class first (this creates self.id)
        super().__init__(
            name="TopLevelAgent",
            instructions="",  # Will update after tools are created
            tools=None,  # Will create after initialization
            mcp_config={},
            agent_type=AgentType.TOP_LEVEL,
            parent_agent_id=None,  # Top level has no parent
            DB_PATH=DB_PATH,
            output_type=output_type
        )
        
        # Save to database after initialization
        self.save_to_db()
        
        # Check if MasterAgent already exists before creating
        from backend.database.agent_db import load_all_agents
        existing_master_agent_id = None
        all_agents = load_all_agents(self.DB_PATH)
        for agent_id, agent in all_agents.items():
            if isinstance(agent, MasterAgent):
                parent_id = getattr(agent, 'parent_agent_id', None)
                if parent_id == self.id:
                    existing_master_agent_id = agent_id
                    print(f"[TopLevelAgent.__init__] Found existing MasterAgent: {agent_id}")
                    break
        
        if existing_master_agent_id:
            # Use existing MasterAgent
            self._add_sub_agents(existing_master_agent_id)
            print(f"[TopLevelAgent.__init__] Using existing MasterAgent: {existing_master_agent_id}")
        else:
            # Create root MasterAgent after we have self.id
            root_master = MasterAgent("Top Master Agent", parent_agent_id=self.id, DB_PATH=self.DB_PATH)
            
            # Save root master to database
            root_master.save_to_db()
            
            # Add root master to sub_agent_ids
            self._add_sub_agents(root_master.id)
            print(f"[TopLevelAgent.__init__] Created new MasterAgent: {root_master.id}")
        
        # Create tools using registry
        from backend.tools.tool_registry import get_tool_registry
        registry = get_tool_registry()
        
        send_message = registry.create_tool("send_message", self)
        generate_outline = registry.create_tool("generate_outline", self)
        
        # Set tools list
        self.tools = [t for t in [send_message, generate_outline] if t is not None]
        
        # Update instructions with actual agent list and tool usage
        agent_dict = self._load_sub_agents_dict()
        tool_ids = ['send_message', 'generate_outline']
        instructions = load_prompt(
            "top_level_agent",
            variables={"agents_list": get_all_agent_info(agent_dict)},
            tool_ids=tool_ids
        )
        self.instructions = instructions
    
    def _recreate_tools(self):
        """Recreate tools after loading from database (tools cannot be pickled)."""
        # Default tool IDs for TopLevelAgent
        default_tool_ids = ['send_message', 'generate_outline']
        self._recreate_tools_from_db(default_tool_ids)
        
        # Ensure tool_ids are saved to database (important for API to return correct tools)
        import json
        import sqlite3
        from backend.database.agent_db import get_db_path
        db_path = get_db_path(self.DB_PATH if hasattr(self, 'DB_PATH') else None)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        tool_ids_json = json.dumps(default_tool_ids, ensure_ascii=False)
        cursor.execute(
            "UPDATE agents SET tool_ids = ? WHERE id = ?",
            (tool_ids_json, self.id)
        )
        conn.commit()
        conn.close()
        print(f"[TopLevelAgent._recreate_tools] Saved tool_ids to database: {default_tool_ids}")
        
        # Update instructions after recreating tools (to ensure latest prompt is used)
        agent_dict = self._load_sub_agents_dict()
        from backend.tools.utils import get_all_agent_info
        from backend.prompts.prompt_loader import load_prompt
        # TopLevelAgent only manages MasterAgent directly, so max_depth=1 to avoid showing NotebookAgents
        instructions = load_prompt(
            "top_level_agent",
            variables={"agents_list": get_all_agent_info(agent_dict, indent_level=0, max_depth=1)},
            tool_ids=default_tool_ids
        )
        self.instructions = instructions
        print(f"[TopLevelAgent._recreate_tools] Updated instructions (length: {len(instructions)})")
    
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


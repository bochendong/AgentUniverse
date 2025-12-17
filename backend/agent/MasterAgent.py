"""MasterAgent - simplified implementation following the effective design pattern."""

from typing import Dict, Any, Optional

from backend.agent.BaseAgent import BaseAgent, AgentType
from backend.agent.specialized.AgentCard import AgentCard
from backend.tools.agent_utils import get_all_agent_info
from backend.prompts.prompt_loader import load_prompt


class MasterAgent(BaseAgent):
    """Master agent that can manage multiple notebook agents."""
    
    def __init__(self, name: str, parent_agent_id: Optional[str] = None, DB_PATH: Optional[str] = None):
        """
        Initialize MasterAgent.
        
        Args:
            name: Agent name
            parent_agent_id: ID of the parent agent (optional)
            DB_PATH: Database path (optional)
        """
        self.name = name
        
        # Load prompt from file
        instructions = load_prompt(
            "master_agent",
            variables={"agents_list": get_all_agent_info({})}
        )
        
        # Initialize the base class first
        super().__init__(
            name=name,
            instructions=instructions,
            tools=None,  # Will create after initialization
            mcp_config={},
            agent_type=AgentType.MASTER,
            parent_agent_id=parent_agent_id,
            DB_PATH=DB_PATH
        )
        
        # Create tools (needs self to be initialized)
        # Import here to avoid circular import
        from backend.tools.agent_tools import create_add_notebook_by_file_tool
        send_message = self._create_send_message_tool()
        add_notebook_by_file = create_add_notebook_by_file_tool(self)
        
        # Set tools list
        self.tools = [send_message, add_notebook_by_file]
        
        # Save to database after tools are set
        self.save_to_db()
    
    def _recreate_tools(self):
        """Recreate tools after loading from database (tools cannot be pickled)."""
        from backend.tools.agent_tools import create_add_notebook_by_file_tool
        send_message = self._create_send_message_tool()
        add_notebook_by_file = create_add_notebook_by_file_tool(self)
        self.tools = [send_message, add_notebook_by_file]

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
    
    def agent_card(self) -> AgentCard:
        """
        返回agent card信息，只包含描述，不包含大纲。
        描述内容为管理的所有子agent的概览信息。
        
        Returns:
            AgentCard对象，包含标题、描述等信息
        """
        agent_dict = self._load_sub_agents_dict()
        
        # Build description from sub-agents
        descriptions = []
        if agent_dict:
            for agent_id, agent in agent_dict.items():
                agent_type = type(agent).__name__
                if agent_type == "NoteBookAgent":
                    title = getattr(agent, 'notebook_title', '未命名笔记本')
                    desc = getattr(agent, 'notebook_description', '')
                    if desc:
                        descriptions.append(f"- {title}: {desc[:100]}..." if len(desc) > 100 else f"- {title}: {desc}")
                    else:
                        descriptions.append(f"- {title}")
                elif agent_type == "MasterAgent":
                    name = getattr(agent, 'name', 'MasterAgent')
                    sub_agent_ids = getattr(agent, 'sub_agent_ids', None) or []
                    descriptions.append(f"- {name} (管理 {len(sub_agent_ids)} 个子Agent)")
        
        description_text = "\n".join(descriptions) if descriptions else "暂无子Agent"
        
        return AgentCard(
            title=self.name,
            agent_id=self.id,
            parent_agent_id=self.parent_agent_id,
            description=description_text,
            outline={}  # MasterAgent 没有大纲
        )


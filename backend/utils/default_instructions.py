"""Utility functions to get default instructions for agents."""

from typing import Optional, Any
from backend.prompts.prompt_loader import load_prompt
from backend.tools.agent_utils import get_all_agent_info


def get_default_instructions(agent_type: str, agent: Optional[Any] = None) -> str:
    """
    Get default instructions for an agent type.
    
    Args:
        agent_type: Agent type ('top_level_agent', 'master', 'notebook')
        agent: Optional agent instance (needed for notebook agents to get notes)
        
    Returns:
        Default instructions string
    """
    # Default tool IDs for each agent type
    tool_ids_map = {
        'top_level_agent': ['send_message', 'handle_file_upload', 'create_notebook_from_outline'],
        'master': ['send_message', 'add_notebook_by_file', 'create_notebook', 'create_notebook_with_outline'],
        'notebook': ['modify_notes'],
    }
    
    tool_ids = tool_ids_map.get(agent_type, [])
    
    if agent_type == 'top_level_agent':
        # For top level agent, we need current agent list
        if agent:
            agent_dict = agent._load_sub_agents_dict() if hasattr(agent, '_load_sub_agents_dict') else {}
            agents_list = get_all_agent_info(agent_dict)
        else:
            agents_list = get_all_agent_info({})
        return load_prompt(
            "top_level_agent", 
            variables={"agents_list": agents_list},
            tool_ids=tool_ids
        )
    
    elif agent_type == 'master':
        # For master agent, we need current agent list
        if agent:
            agent_dict = agent._load_sub_agents_dict() if hasattr(agent, '_load_sub_agents_dict') else {}
            agents_list = get_all_agent_info(agent_dict)
        else:
            agents_list = get_all_agent_info({})
        return load_prompt(
            "master_agent", 
            variables={"agents_list": agents_list},
            tool_ids=tool_ids
        )
    
    elif agent_type == 'notebook':
        # For notebook agent, we need notes content
        if agent and hasattr(agent, 'notes'):
            notes = agent.notes or ""
        else:
            notes = ""
        return load_prompt(
            "notebook_agent", 
            variables={"notes": notes},
            tool_ids=tool_ids
        )
    
    else:
        return ""



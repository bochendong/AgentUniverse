"""Utility functions to get default instructions for agents."""

from typing import Optional, Any
from backend.prompts.prompt_loader import load_prompt
from backend.tools.utils import get_all_agent_info


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
        'notebook': ['modify_by_id', 'get_content_by_id', 'add_content_to_section'],
    }
    
    tool_ids = tool_ids_map.get(agent_type, [])
    
    if agent_type == 'top_level_agent':
        # For top level agent, we need current agent list
        # TopLevelAgent only manages MasterAgent directly, so max_depth=1 to avoid showing NotebookAgents
        if agent:
            agent_dict = agent._load_sub_agents_dict() if hasattr(agent, '_load_sub_agents_dict') else {}
            agents_list = get_all_agent_info(agent_dict, indent_level=0, max_depth=1)
        else:
            agents_list = get_all_agent_info({}, indent_level=0, max_depth=1)
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
        # For notebook agent, generate notes content from sections (same as Advanced Mode)
        # This ensures we always have the latest notes with XML tags
        if agent and hasattr(agent, 'sections') and hasattr(agent, 'outline'):
            from backend.tools.utils import generate_markdown_from_agent
            # Generate notes with XML tags (same as Advanced Mode does)
            notes = generate_markdown_from_agent(agent, include_ids=True)
            print(f"[get_default_instructions] Generated notebook notes from sections, length: {len(notes) if notes else 0}")
        elif agent and hasattr(agent, 'notes'):
            # Fallback to agent.notes if sections/outline not available
            notes = agent.notes if agent.notes is not None else ""
            print(f"[get_default_instructions] Using agent.notes, length: {len(notes) if notes else 0}")
        else:
            notes = ""
            print(f"[get_default_instructions] Notebook agent has no notes or sections/outline")
        
        result = load_prompt(
            "notebook_agent", 
            variables={"notes": notes},
            agent_instance=agent,  # Pass agent instance to properly generate tools_usage
            tool_ids=tool_ids
        )
        
        # Verify notes were replaced
        if "{notes}" in result:
            print(f"[get_default_instructions] WARNING: {{notes}} placeholder was NOT replaced in instructions!")
        else:
            print(f"[get_default_instructions] Successfully replaced {{notes}} placeholder in instructions")
        
        return result
    
    else:
        return ""



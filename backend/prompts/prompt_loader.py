"""Simple prompt loader for backend agents."""

import os
from pathlib import Path
from typing import Optional, Any


def load_prompt(
    prompt_name: str, 
    variables: dict = None, 
    agent_instance: Optional[Any] = None,
    tool_ids: Optional[list] = None
) -> str:
    """
    Load a prompt template from file and format it with variables.
    
    Args:
        prompt_name: Name of the prompt file (without .md extension)
        variables: Dictionary of variables to format into the prompt
        agent_instance: Optional agent instance (for generating tool usage)
        tool_ids: Optional list of tool IDs (for generating tool usage without agent instance)
        
    Returns:
        Formatted prompt string
    """
    # Get the prompts directory (backend/prompts)
    current_file = Path(__file__)
    prompts_dir = current_file.parent.parent / "prompts"
    prompt_path = prompts_dir / f"{prompt_name}.md"
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    # Generate tool usage if needed
    if "{tools_usage}" in template:
        from backend.tools.tool_usage_generator import (
            generate_tool_usage_section,
            generate_tools_usage_for_agent
        )
        
        if agent_instance:
            tools_usage = generate_tools_usage_for_agent(agent_instance)
        elif tool_ids:
            tools_usage = generate_tool_usage_section(tool_ids)
        else:
            tools_usage = ""
        
        # Add tools_usage to variables
        if variables is None:
            variables = {}
        variables["tools_usage"] = tools_usage
    
    # Format with variables if provided
    if variables:
        try:
            return template.format(**variables)
        except KeyError as e:
            # If variable is missing, return template as-is (but with tools_usage replaced)
            return template
    
    return template


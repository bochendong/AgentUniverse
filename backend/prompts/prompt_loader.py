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
    
    # Initialize variables dict if None
    if variables is None:
        variables = {}
    
    # Generate tool usage if needed
    if "{tools_usage}" in template:
        try:
            from backend.tools.utils import (
                generate_tool_usage_section,
                generate_tools_usage_for_agent
            )
            
            if agent_instance:
                # Prefer agent_instance if provided (more accurate tool filtering)
                tools_usage = generate_tools_usage_for_agent(agent_instance)
            elif tool_ids:
                # Fallback to tool_ids if agent_instance not provided
                tools_usage = generate_tool_usage_section(tool_ids, agent_instance=agent_instance)
            else:
                tools_usage = ""
            
            # Add tools_usage to variables
            variables["tools_usage"] = tools_usage
        except Exception as e:
            # If generating tools_usage fails, use empty string
            print(f"[load_prompt] Error generating tools_usage: {e}")
            import traceback
            traceback.print_exc()
            variables["tools_usage"] = ""
    
    # Format with variables if provided
    # Use manual replacement instead of .format() to avoid issues with { } in notes content (JSON, code blocks, etc.)
    if variables:
        try:
            # Debug: print variables being used
            print(f"[load_prompt] Replacing placeholders in template '{prompt_name}' with variables: {list(variables.keys())}")
            if "notes" in variables:
                notes_preview = str(variables["notes"])[:100] if variables["notes"] else "EMPTY/NONE"
                print(f"[load_prompt] notes value (first 100 chars): {notes_preview}")
            
            # Manual replacement: replace each placeholder individually to avoid conflicts with { } in variable values
            result = template
            for var_name, var_value in variables.items():
                placeholder = "{" + var_name + "}"
                # Convert var_value to string if not already
                var_str = str(var_value) if var_value is not None else ""
                result = result.replace(placeholder, var_str)
            
            # Verify that all expected placeholders were replaced
            import re
            # Find remaining placeholders (simple variable names like {notes}, {tools_usage})
            remaining_placeholders = re.findall(r'\{([a-z_]+)\}', result, re.IGNORECASE)
            # Filter out known variables that should have been replaced
            expected_placeholders = set(variables.keys())
            unexpected_remaining = [p for p in remaining_placeholders if p in expected_placeholders]
            
            if unexpected_remaining:
                # Log warning if expected placeholders remain (should not happen)
                print(f"[load_prompt] WARNING: Expected placeholders were not replaced: {unexpected_remaining}")
                print(f"[load_prompt] Available variables were: {list(variables.keys())}")
            else:
                print(f"[load_prompt] Successfully replaced all expected placeholders in template '{prompt_name}'")
                if remaining_placeholders:
                    # Log info about other { } patterns that remain (likely in code blocks/JSON in notes)
                    print(f"[load_prompt] Note: Template contains other {{ }} patterns (likely in code blocks): {set(remaining_placeholders) - expected_placeholders}")
            
            return result
        except Exception as e:
            # Catch any errors during replacement
            print(f"[load_prompt] Unexpected error replacing placeholders in template '{prompt_name}': {e}")
            print(f"[load_prompt] Variables: {list(variables.keys())}")
            import traceback
            traceback.print_exc()
            return template
    
    return template


"""Simple prompt loader for backend agents."""

import os
from pathlib import Path


def load_prompt(prompt_name: str, variables: dict = None) -> str:
    """
    Load a prompt template from file and format it with variables.
    
    Args:
        prompt_name: Name of the prompt file (without .md extension)
        variables: Dictionary of variables to format into the prompt
        
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
    
    # Format with variables if provided
    if variables:
        try:
            return template.format(**variables)
        except KeyError as e:
            # If variable is missing, return template as-is
            return template
    
    return template


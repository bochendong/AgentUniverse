"""
Utility functions to extract outline information from messages.
"""
import json
import re
from typing import Optional, Dict, Any


def extract_outline_from_message(message: str) -> Optional[Dict[str, Any]]:
    """
    Extract outline JSON from a message.
    
    Looks for JSON code blocks in the message and tries to parse them as outline.
    
    Args:
        message: The message text to extract outline from
        
    Returns:
        Outline dictionary if found, None otherwise
    """
    # Try to find JSON code block
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', message)
    if json_match:
        try:
            outline_data = json.loads(json_match.group(1))
            # Validate outline structure
            if isinstance(outline_data, dict) and 'notebook_title' in outline_data and 'outlines' in outline_data:
                return outline_data
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON without code block markers
    json_match = re.search(r'\{[\s\S]*"notebook_title"[\s\S]*"outlines"[\s\S]*\}', message)
    if json_match:
        try:
            outline_data = json.loads(json_match.group(0))
            if isinstance(outline_data, dict) and 'notebook_title' in outline_data and 'outlines' in outline_data:
                return outline_data
        except json.JSONDecodeError:
            pass
    
    return None


def extract_file_path_from_message(message: str) -> Optional[str]:
    """
    Extract file path from a message.
    
    Looks for file path patterns in the message.
    
    Args:
        message: The message text to extract file path from
        
    Returns:
        File path if found, None otherwise
    """
    # Look for "文件路径：" or "file_path:" followed by a path
    patterns = [
        r'文件路径[：:]\s*(.+?)(?:\n|$)',
        r'file_path[：:]\s*(.+?)(?:\n|$)',
        r'文件路径[：:]\s*`(.+?)`',
        r'file_path[：:]\s*`(.+?)`',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message, re.MULTILINE)
        if match:
            file_path = match.group(1).strip()
            # Remove markdown code markers if present
            file_path = file_path.strip('`').strip()
            if file_path:
                return file_path
    
    return None


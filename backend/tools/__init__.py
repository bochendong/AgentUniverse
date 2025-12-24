"""Tools package - utility functions and agent tools."""

from backend.tools.utils import (
    get_all_agent_info,
    generate_markdown_from_agent,
    save_uploaded_file,
    ensure_upload_dir,
    register_all_specialized_agents,
    generate_tools_usage_for_agent,
)
from backend.tools.tool_registry import get_tool_registry, register_function_tool, register_agent_as_tool
from backend.tools.tool_discovery import discover_and_register_tools, init_tool_system

# Import function_tools to trigger tool registration
import backend.tools.function_tools  # noqa: F401

__all__ = [
    "get_all_agent_info",
    "generate_markdown_from_agent",
    "save_uploaded_file",
    "ensure_upload_dir",
    "register_all_specialized_agents",
    "generate_tools_usage_for_agent",
    "get_tool_registry",
    "register_function_tool",
    "register_agent_as_tool",
    "discover_and_register_tools",
    "init_tool_system",
]


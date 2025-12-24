"""Tool discovery and auto-registration."""

import importlib
import pkgutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def discover_and_register_tools():
    """Automatically discover and register all tools."""
    from backend.tools.tool_registry import get_tool_registry
    
    registry = get_tool_registry()
    
    # Import agent_tools module to trigger registration
    # All tools are registered via decorators when the module is imported
    try:
        import backend.tools.function_tools  # noqa: F401
        logger.info("Loaded tools from agent_tools")
    except Exception as e:
        logger.warning(f"Failed to load agent_tools: {e}")
    
    # Import specialized agents registration module
    try:
        # Import the registration module which registers all specialized agents
        # The module will auto-register when imported
        from backend.tools.utils import register_all_specialized_agents
        register_all_specialized_agents()
        logger.info("Loaded specialized agents as tools")
    except Exception as e:
        logger.warning(f"Failed to load specialized agents: {e}")
    
    # Sync to database
    try:
        registry.sync_to_database()
        logger.info(f"Synced {len(registry.list_tools())} tools to database")
    except Exception as e:
        logger.warning(f"Failed to sync tools to database: {e}")
    
    return registry


def init_tool_system():
    """Initialize the tool system - call this at application startup."""
    return discover_and_register_tools()

"""Tool logging hooks for tracking tool usage and errors."""

import logging
import json
import traceback
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Try to import hooks - handle different versions of agents package
try:
    from agents import RunHooks, RunContextWrapper, Agent, Tool
    RunHooksBase = RunHooks
except ImportError:
    try:
        from agents import RunHooksBase, RunContextWrapper, Agent, Tool
    except ImportError:
        # Fallback: try importing from a hooks submodule
        try:
            from agents.hooks import RunHooksBase, RunContextWrapper
            from agents import Agent, Tool
        except ImportError:
            # If all imports fail, we'll need to make this optional
            RunHooksBase = None
            RunContextWrapper = Any
            Agent = Any
            Tool = Any


if RunHooksBase is None:
    # If hooks are not available, create a dummy class
    class ToolLoggingHook:
        """Hook to log tool usage and errors (disabled - hooks not available)."""
        def __init__(self):
            pass
        async def on_tool_start(self, *args, **kwargs):
            pass
        async def on_tool_end(self, *args, **kwargs):
            pass
else:
    class ToolLoggingHook(RunHooksBase):
        """Hook to log tool usage and errors."""
        
        def __init__(self):
            """Initialize the tool logging hook."""
            super().__init__()
        
        async def on_tool_start(
            self,
            context: RunContextWrapper[Any],
            agent: Agent,
            tool: Tool,
        ) -> None:
            """Called immediately before a local tool is invoked."""
            tool_name = getattr(tool, 'name', 'unknown')
            tool_id = getattr(tool, '_tool_id', None)
            
            # Get agent info
            agent_name = getattr(agent, 'name', 'unknown')
            agent_id = getattr(agent, 'id', None)
            
            logger.info(
                f"Tool invocation started: tool={tool_name} (id={tool_id}), "
                f"agent={agent_name} (id={agent_id[:8] if agent_id else None})"
            )
            
            # Track tool call in tracing system
            from backend.utils.tracing_collector import get_current_session_id, track_tool_call
            session_id = get_current_session_id()
            if session_id:
                # Store the context manager in the tool for cleanup in on_tool_end
                tool._tracing_context = track_tool_call(session_id, agent, tool_name)
                tool._tracing_context.__enter__()
        
        async def on_tool_end(
            self,
            context: RunContextWrapper[Any],
            agent: Agent,
            tool: Tool,
            result: str,
        ) -> None:
            """Called immediately after a local tool is invoked."""
            tool_name = getattr(tool, 'name', 'unknown')
            tool_id = getattr(tool, '_tool_id', None)
            
            # Get agent info
            agent_name = getattr(agent, 'name', 'unknown')
            agent_id = getattr(agent, 'id', None)
            
            # Truncate long results for logging
            result_preview = result[:200] if len(result) > 200 else result
            
            logger.info(
                f"Tool invocation completed: tool={tool_name} (id={tool_id}), "
                f"agent={agent_name} (id={agent_id[:8] if agent_id else None}), "
                f"result_length={len(result)}, result_preview={result_preview}"
            )
            
            # End tool call tracking in tracing system
            if hasattr(tool, '_tracing_context'):
                try:
                    tool._tracing_context.__exit__(None, None, None)
                except Exception as e:
                    logger.warning(f"Failed to end tool call tracking: {e}")
                finally:
                    # Clean up
                    if hasattr(tool, '_tracing_context'):
                        delattr(tool, '_tracing_context')


def wrap_function_tool_with_logging(tool, tool_id: Optional[str] = None):
    """
    Wrap a FunctionTool's on_invoke_tool to add logging for errors.
    
    Args:
        tool: The FunctionTool instance
        tool_id: Optional tool ID for logging
    
    Returns:
        The wrapped tool (same instance, modified in place)
    """
    from agents import FunctionTool
    
    if not isinstance(tool, FunctionTool):
        return tool
    
    # Store original on_invoke_tool
    original_on_invoke = tool.on_invoke_tool
    
    # Get tool info for logging
    tool_name = tool.name
    tool_id = tool_id or getattr(tool, '_tool_id', None)
    
    async def logged_on_invoke_tool(context, params_json: str) -> Any:
        """Wrapped on_invoke_tool with error logging."""
        try:
            # Parse params for logging (truncate if too long)
            try:
                params_dict = json.loads(params_json) if params_json else {}
                params_preview = json.dumps(params_dict, ensure_ascii=False)[:200]
            except:
                params_preview = params_json[:200] if params_json else "{}"
            
            # Get agent info from context if available
            agent_name = "unknown"
            agent_id = None
            if hasattr(context, 'agent'):
                agent_name = getattr(context.agent, 'name', 'unknown')
                agent_id = getattr(context.agent, 'id', None)
            
            logger.info(
                f"Invoking tool: tool={tool_name} (id={tool_id}), "
                f"agent={agent_name} (id={agent_id[:8] if agent_id else None}), "
                f"params={params_preview}"
            )
            
            # Call original on_invoke_tool
            result = await original_on_invoke(context, params_json)
            
            # Log success
            result_preview = str(result)[:200] if result else "None"
            logger.info(
                f"Tool invocation succeeded: tool={tool_name} (id={tool_id}), "
                f"agent={agent_name} (id={agent_id[:8] if agent_id else None}), "
                f"result_length={len(str(result)) if result else 0}, "
                f"result_preview={result_preview}"
            )
            
            return result
            
        except Exception as e:
            # Log error with full traceback
            error_msg = str(e)
            error_trace = traceback.format_exc()
            
            # Get agent info from context if available
            agent_name = "unknown"
            agent_id = None
            if hasattr(context, 'agent'):
                agent_name = getattr(context.agent, 'name', 'unknown')
                agent_id = getattr(context.agent, 'id', None)
            
            logger.error(
                f"Tool invocation failed: tool={tool_name} (id={tool_id}), "
                f"agent={agent_name} (id={agent_id[:8] if agent_id else None}), "
                f"error={error_msg}",
                exc_info=True
            )
            
            # Re-raise the exception (let the framework handle it)
            raise
    
    # Replace on_invoke_tool with wrapped version
    tool.on_invoke_tool = logged_on_invoke_tool
    
    return tool


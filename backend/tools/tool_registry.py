"""Tool Registry - Centralized tool registration and management system."""

from typing import Dict, List, Optional, Callable, Any, Type
from dataclasses import dataclass, field
from agents import function_tool


@dataclass
class ParamInfo:
    """Parameter information."""
    type: str
    description: str
    required: bool = True


@dataclass
class ToolMetadata:
    """Tool metadata."""
    tool_id: str
    name: str
    description: str
    task: str
    agent_types: List[str] = field(default_factory=list)
    input_params: Dict[str, ParamInfo] = field(default_factory=dict)
    output_type: str = "str"
    output_description: Optional[str] = None
    tool_type: str = "function"  # "function" or "agent_as_tool"
    creator_func: Optional[Callable] = None
    required_agent_attrs: List[str] = field(default_factory=list)
    condition_func: Optional[Callable] = None


@dataclass
class AgentAsToolMetadata(ToolMetadata):
    """Agent as Tool metadata."""
    agent_class_name: str = ""
    agent_class: Optional[Type] = None
    agent_init_params: Optional[Dict] = None


class ToolRegistry:
    """Tool Registry - manages all tools."""
    
    _instance: Optional['ToolRegistry'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._function_tools: Dict[str, ToolMetadata] = {}
        self._agent_as_tools: Dict[str, AgentAsToolMetadata] = {}
        self._initialized = True
    
    def register_function_tool(
        self,
        tool_id: str,
        creator_func: Callable,
        metadata: ToolMetadata
    ):
        """Register a function tool."""
        metadata.creator_func = creator_func
        metadata.tool_id = tool_id
        metadata.tool_type = "function"
        self._function_tools[tool_id] = metadata
    
    def register_agent_as_tool(
        self,
        tool_id: str,
        agent_class: Type,
        metadata: AgentAsToolMetadata
    ):
        """Register an agent as tool."""
        # Use the agent_class directly - don't try to find base class
        # The agent_class passed in is the actual class we want to use
        # (e.g., OutlineMakerAgent, not Agent)
        metadata.agent_class = agent_class
        metadata.tool_id = tool_id
        metadata.tool_type = "agent_as_tool"
        metadata.agent_class_name = agent_class.__name__
        self._agent_as_tools[tool_id] = metadata
        print(f"[Registry] Registered agent as tool: {tool_id} ({agent_class.__name__})")
    
    def create_tool(self, tool_id: str, agent: Any, **kwargs) -> Optional[Any]:
        """Create a tool instance.
        
        Returns:
            Tool instance if successful, None if failed.
            Check backend logs for detailed error information.
        """
        # Check function tools first
        if tool_id in self._function_tools:
            metadata = self._function_tools[tool_id]
            if metadata.creator_func:
                try:
                    # Check if agent has required attributes
                    for attr in metadata.required_agent_attrs:
                        if not hasattr(agent, attr):
                            print(f"[ToolRegistry] Agent missing required attribute '{attr}' for tool {tool_id}")
                            print(f"[ToolRegistry] Agent type: {type(agent).__name__}, Agent has: {dir(agent)}")
                            return None
                    
                    # Check condition function
                    if metadata.condition_func:
                        if not metadata.condition_func(agent):
                            print(f"[ToolRegistry] Condition function failed for tool {tool_id}")
                            return None
                    
                    # Create tool instance
                    print(f"[ToolRegistry] Creating tool {tool_id} for agent {type(agent).__name__}")
                    tool = metadata.creator_func(agent)
                    # Attach tool_id for tracking
                    if hasattr(tool, '__dict__'):
                        tool.__dict__['_tool_id'] = tool_id
                    print(f"[ToolRegistry] Successfully created tool {tool_id}")
                    return tool
                except Exception as e:
                    print(f"[ToolRegistry] Failed to create tool {tool_id}: {e}")
                    import traceback
                    traceback.print_exc()
                    return None
            else:
                print(f"[ToolRegistry] Tool {tool_id} has no creator_func")
                return None
        else:
            print(f"[ToolRegistry] Tool {tool_id} not found in function_tools. Available tools: {list(self._function_tools.keys())}")
        
        # Check agent as tools
        if tool_id in self._agent_as_tools:
            metadata = self._agent_as_tools[tool_id]
            try:
                # Validate required parameters
                for param_name, param_info in metadata.input_params.items():
                    if param_info.required and param_name not in kwargs:
                        print(f"[ToolRegistry] Missing required parameter '{param_name}' for agent_as_tool {tool_id}")
                        return None
                
                # Get the agent class
                agent_class = metadata.agent_class
                if not agent_class:
                    print(f"[ToolRegistry] Agent class not found for {tool_id}")
                    return None
                
                # Prepare arguments for agent initialization
                # Only include parameters that are in input_params
                agent_kwargs = {}
                for param_name in metadata.input_params.keys():
                    if param_name in kwargs:
                        agent_kwargs[param_name] = kwargs[param_name]
                
                # Create agent instance
                try:
                    agent_instance = agent_class(**agent_kwargs)
                except Exception as e:
                    # Agent initialization failed
                    import traceback
                    error_trace = traceback.format_exc()
                    print(f"[ToolRegistry] Failed to initialize agent {tool_id} ({agent_class.__name__}): {e}")
                    print(f"参数: {agent_kwargs}")
                    print(f"错误详情:\n{error_trace}")
                    raise  # Re-raise to be caught by outer exception handler
                
                # Convert agent to tool using as_tool() method
                tool = agent_instance.as_tool(
                    tool_name=metadata.name,
                    tool_description=metadata.description
                )
                
                # Attach tool_id for tracking
                if hasattr(tool, '__dict__'):
                    tool.__dict__['_tool_id'] = tool_id
                    tool.__dict__['_agent_instance'] = agent_instance  # Keep reference to agent
                
                return tool
                
            except TypeError as e:
                # Wrong arguments for agent initialization
                print(f"[ToolRegistry] Failed to create agent_as_tool {tool_id}: Wrong arguments - {e}")
                print(f"参数: {agent_kwargs}")
                import traceback
                traceback.print_exc()
                return None
            except (FileNotFoundError, IOError, OSError) as e:
                # File or IO related errors
                print(f"[ToolRegistry] Failed to create agent_as_tool {tool_id}: File/IO error - {e}")
                print(f"参数: {agent_kwargs}")
                import traceback
                traceback.print_exc()
                # Return None but the error should be logged
                return None
            except Exception as e:
                print(f"[ToolRegistry] Failed to create agent_as_tool {tool_id}: {e}")
                print(f"参数: {agent_kwargs}")
                import traceback
                traceback.print_exc()
                return None
        
        return None
    
    def get_tool_metadata(self, tool_id: str) -> Optional[ToolMetadata]:
        """Get tool metadata."""
        if tool_id in self._function_tools:
            return self._function_tools[tool_id]
        if tool_id in self._agent_as_tools:
            return self._agent_as_tools[tool_id]
        return None
    
    def list_tools(self) -> List[str]:
        """List all registered tool IDs."""
        return list(self._function_tools.keys()) + list(self._agent_as_tools.keys())
    
    def get_all_metadata(self) -> Dict[str, ToolMetadata]:
        """Get all tool metadata."""
        result = {}
        result.update(self._function_tools)
        result.update(self._agent_as_tools)
        return result
    
    def sync_to_database(self, db_path: Optional[str] = None):
        """Sync tool metadata to database."""
        from backend.database.tools_db import save_tool
        
        # Sync function tools
        for tool_id, metadata in self._function_tools.items():
            # Convert ParamInfo to dict for database
            input_params_dict = {}
            for param_name, param_info in metadata.input_params.items():
                input_params_dict[param_name] = {
                    'type': param_info.type,
                    'description': param_info.description,
                    'required': param_info.required
                }
            
            save_tool(
                tool_id=tool_id,
                name=metadata.name,
                description=metadata.description,
                task=metadata.task,
                agent_type=",".join(metadata.agent_types) if metadata.agent_types else "BaseAgent",
                input_params=input_params_dict,
                output_type=metadata.output_type,
                output_description=metadata.output_description,
                tool_type="function",
            )
        
        # Sync agent as tools
        for tool_id, metadata in self._agent_as_tools.items():
            # Convert ParamInfo to dict for database
            input_params_dict = {}
            for param_name, param_info in metadata.input_params.items():
                input_params_dict[param_name] = {
                    'type': param_info.type,
                    'description': param_info.description,
                    'required': param_info.required
                }
            
            save_tool(
                tool_id=tool_id,
                name=metadata.name,
                description=metadata.description,
                task=metadata.task,
                agent_type=",".join(metadata.agent_types) if metadata.agent_types else "AsToolAgent",
                input_params=input_params_dict,
                output_type=metadata.output_type,
                output_description=metadata.output_description,
                tool_type="agent_as_tool",
                agent_class_name=metadata.agent_class_name,
            )


# Global registry instance
_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


# Decorator functions
def register_function_tool(
    tool_id: str,
    name: str,
    description: str,
    task: str,
    agent_types: List[str] = None,
    input_params: Dict[str, Dict] = None,
    output_type: str = "str",
    output_description: Optional[str] = None,
    required_agent_attrs: List[str] = None,
    condition_func: Optional[Callable] = None,
):
    """
    Decorator to register a function tool.
    
    Usage:
        @register_function_tool(
            tool_id="my_tool",
            name="my_tool",
            description="My tool",
            task="Does something",
            agent_types=["BaseAgent"],
            input_params={"param1": {"type": "str", "description": "Param 1", "required": True}},
            output_type="str"
        )
        def create_my_tool(agent):
            @function_tool
            def my_tool(param1: str) -> str:
                return f"Result: {param1}"
            return my_tool
    """
    def decorator(creator_func: Callable):
        registry = get_tool_registry()
        
        # Convert input_params dict to ParamInfo objects
        param_infos = {}
        if input_params:
            for param_name, param_dict in input_params.items():
                param_infos[param_name] = ParamInfo(
                    type=param_dict.get("type", "str"),
                    description=param_dict.get("description", ""),
                    required=param_dict.get("required", True)
                )
        
        metadata = ToolMetadata(
            tool_id=tool_id,
            name=name,
            description=description,
            task=task,
            agent_types=agent_types or [],
            input_params=param_infos,
            output_type=output_type,
            output_description=output_description,
            required_agent_attrs=required_agent_attrs or [],
            condition_func=condition_func,
        )
        
        registry.register_function_tool(tool_id, creator_func, metadata)
        return creator_func
    
    return decorator


def register_agent_as_tool(
    tool_id: str,
    name: str,
    description: str,
    task: str,
    agent_types: List[str] = None,
    input_params: Dict[str, Dict] = None,
    output_type: str = "str",
    output_description: Optional[str] = None,
):
    """
    Decorator to register an agent as tool.
    
    Usage:
        @register_agent_as_tool(
            tool_id="my_agent",
            name="my_agent",
            description="My agent",
            task="Does something",
            agent_types=["MasterAgent"],
            input_params={"input": {"type": "str", "description": "Input", "required": True}},
            output_type="str"
        )
        class MyAgent(Agent):
            def __init__(self, input: str):
                super().__init__(name="MyAgent", instructions="...")
    """
    def decorator(agent_class: Type):
        registry = get_tool_registry()
        
        # Convert input_params dict to ParamInfo objects
        param_infos = {}
        if input_params:
            for param_name, param_dict in input_params.items():
                param_infos[param_name] = ParamInfo(
                    type=param_dict.get("type", "str"),
                    description=param_dict.get("description", ""),
                    required=param_dict.get("required", True)
                )
        
        # Get the original class name (if it's a wrapper, get base class name)
        original_class_name = agent_class.__name__
        if hasattr(agent_class, '__bases__') and len(agent_class.__bases__) > 0:
            base_class = agent_class.__bases__[0]
            if base_class.__name__ != 'object' and 'Registered' not in base_class.__name__:
                original_class_name = base_class.__name__
        
        metadata = AgentAsToolMetadata(
            tool_id=tool_id,
            name=name,
            description=description,
            task=task,
            agent_types=agent_types or [],
            input_params=param_infos,
            output_type=output_type,
            output_description=output_description,
            agent_class_name=original_class_name,
        )
        
        registry.register_agent_as_tool(tool_id, agent_class, metadata)
        return agent_class
    
    return decorator

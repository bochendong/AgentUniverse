"""Generate tool usage documentation from tool metadata."""

from typing import List, Optional, Dict, Any
from backend.tools.tool_registry import get_tool_registry, ToolMetadata


def generate_tool_usage_section(tool_ids: List[str], agent_instance: Optional[Any] = None) -> str:
    """
    Generate a formatted tool usage section from tool IDs.
    
    Args:
        tool_ids: List of tool IDs to generate usage for
        agent_instance: Optional agent instance (for checking tool availability)
        
    Returns:
        Formatted markdown string with tool usage instructions
    """
    registry = get_tool_registry()
    sections = []
    
    for idx, tool_id in enumerate(tool_ids, 1):
        metadata = registry.get_tool_metadata(tool_id)
        if not metadata:
            continue
        
        # Check if tool is available for this agent
        if agent_instance:
            # Check required agent attributes
            if metadata.required_agent_attrs:
                if not all(hasattr(agent_instance, attr) for attr in metadata.required_agent_attrs):
                    continue
            
            # Check condition function
            if metadata.condition_func:
                if not metadata.condition_func(agent_instance):
                    continue
        
        tool_usage = format_tool_usage(metadata, idx)
        sections.append(tool_usage)
    
    if not sections:
        return ""
    
    return "\n\n".join(sections)


def format_tool_usage(metadata: ToolMetadata, index: int = 1) -> str:
    """Format a single tool's usage documentation.
    
    Args:
        metadata: Tool metadata
        index: Optional index number (default: 1)
        
    Returns:
        Formatted markdown string with tool usage instructions
    """
    lines = []
    
    # Tool header
    lines.append(f"### {index}. {metadata.name} 工具")
    
    # Description
    if metadata.description:
        lines.append(f"{metadata.description}")
    
    # Task
    if metadata.task:
        lines.append(f"\n**用途**：{metadata.task}")
    
    # Call signature
    lines.append("\n**调用方法**：")
    lines.append("```python")
    
    # Build function signature
    param_parts = []
    for param_name, param_info in metadata.input_params.items():
        param_str = param_name
        if not param_info.required:
            param_str += "=None"  # Optional parameter
        param_parts.append(param_str)
    
    signature = f"{metadata.name}({', '.join(param_parts)})"
    lines.append(signature)
    lines.append("```")
    
    # Input parameters
    if metadata.input_params:
        lines.append("\n**输入参数**：")
        for param_name, param_info in metadata.input_params.items():
            required_mark = "（必需）" if param_info.required else "（可选）"
            lines.append(f"- `{param_name}` ({param_info.type}){required_mark}：{param_info.description}")
    
    # Output
    lines.append(f"\n**输出类型**：`{metadata.output_type}`")
    if metadata.output_description:
        lines.append(f"\n**输出说明**：{metadata.output_description}")
    
    # Special notes for agent_as_tool
    if metadata.tool_type == "agent_as_tool":
        lines.append("\n**注意**：这是一个 Agent as Tool，需要提供运行时参数来创建 Agent 实例。")
    
    return "\n".join(lines)


def generate_tools_usage_for_agent(agent_instance: Any) -> str:
    """
    Generate tool usage section for a specific agent instance.
    
    This will check which tools are available for the agent and generate
    usage documentation only for those tools.
    
    Args:
        agent_instance: The agent instance
        
    Returns:
        Formatted markdown string with tool usage instructions
    """
    # Get tool IDs from agent's tools
    tool_ids = []
    if hasattr(agent_instance, 'tools') and agent_instance.tools:
        for tool in agent_instance.tools:
            if hasattr(tool, '__dict__') and '_tool_id' in tool.__dict__:
                tool_ids.append(tool.__dict__['_tool_id'])
            elif hasattr(tool, 'name'):
                # Fallback: try to find by name
                registry = get_tool_registry()
                all_tools = registry.list_tools()
                for tool_id in all_tools:
                    metadata = registry.get_tool_metadata(tool_id)
                    if metadata and metadata.name == tool.name:
                        tool_ids.append(tool_id)
                        break
    
    if not tool_ids:
        return ""
    
    return generate_tool_usage_section(tool_ids, agent_instance)


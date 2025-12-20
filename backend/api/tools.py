"""Tools API routes."""

from fastapi import APIRouter, HTTPException
from backend.database.tools_db import get_all_tools, get_tool
from backend.tools.tool_registry import get_tool_registry
from backend.tools.tool_discovery import init_tool_system
from backend.tools.tool_usage_generator import format_tool_usage

router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.post("/sync")
async def sync_tools():
    """Force sync all tools from registry to database."""
    try:
        init_tool_system()
        return {'message': 'Tools synced successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing tools: {str(e)}")


@router.get("")
async def list_tools():
    """List all tools."""
    try:
        tools = get_all_tools()
        registry = get_tool_registry()
        
        # Add usage documentation for each tool
        for tool in tools:
            tool_id = tool.get('id')
            if tool_id:
                metadata = registry.get_tool_metadata(tool_id)
                if metadata:
                    # Generate usage documentation
                    usage_doc = format_tool_usage(metadata, 1)  # index doesn't matter for single tool
                    tool['usage_documentation'] = usage_doc
        
        return {'tools': tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tools: {str(e)}")


@router.get("/{tool_id}")
async def get_tool(tool_id: str):
    """Get a tool by ID."""
    try:
        tool = get_tool(tool_id)
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        return tool
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tool: {str(e)}")


@router.get("/{tool_id}/agent-details")
async def get_agent_as_tool_details(tool_id: str):
    """Get detailed information about an agent_as_tool, including its instructions and sub-agents."""
    try:
        registry = get_tool_registry()
        metadata = registry.get_tool_metadata(tool_id)
        
        # Determine tool_type and agent_class_name
        tool_type = None
        agent_class_name = None
        
        tool = get_tool(tool_id)
        if tool:
            tool_type = tool.get('tool_type', 'function')
            agent_class_name = tool.get('agent_class_name')
        
        # Fallback to registry if database data is incomplete
        if metadata:
            if not tool_type or tool_type == 'function':
                tool_type = getattr(metadata, 'tool_type', 'function')
            if not agent_class_name:
                agent_class_name = getattr(metadata, 'agent_class_name', None)
        
        if not tool and not metadata:
            raise HTTPException(status_code=404, detail=f"Tool not found: {tool_id}")
        
        # Check if it's an agent_as_tool type
        if tool_type != 'agent_as_tool':
            raise HTTPException(
                status_code=400, 
                detail=f"This tool is not an agent_as_tool type. Got tool_type: {tool_type}, tool_id: {tool_id}"
            )
        
        if not agent_class_name:
            raise HTTPException(
                status_code=400, 
                detail=f"Agent class name not found for this tool. tool_id: {tool_id}, tool_type: {tool_type}. Please ensure the tool is properly registered."
            )
        
        # Import the agent class dynamically
        try:
            if agent_class_name == 'OutlineMakerAgent':
                from backend.agent.specialized.NoteBookCreator import OutlineMakerAgent
                AgentClass = OutlineMakerAgent
            elif agent_class_name == 'NoteBookAgentCreator':
                from backend.agent.specialized.NoteBookCreator import NoteBookAgentCreator
                AgentClass = NoteBookAgentCreator
            elif agent_class_name == 'ExerciseRefinementAgent':
                from backend.agent.specialized.ExerciseRefinementAgent import ExerciseRefinementAgent
                AgentClass = ExerciseRefinementAgent
            elif agent_class_name == 'ProofRefinementAgent':
                from backend.agent.specialized.ProofRefinementAgent import ProofRefinementAgent
                AgentClass = ProofRefinementAgent
            elif agent_class_name == 'IntentExtractionAgent':
                from backend.agent.specialized.IntentExtractionAgent import IntentExtractionAgent
                AgentClass = IntentExtractionAgent
            elif agent_class_name == 'OutlineRevisionAgent':
                from backend.agent.specialized.OutlineRevisionAgent import OutlineRevisionAgent
                AgentClass = OutlineRevisionAgent
            else:
                raise HTTPException(status_code=400, detail=f"Unknown agent class: {agent_class_name}")
        except ImportError as e:
            raise HTTPException(status_code=500, detail=f"Failed to import agent class: {str(e)}")
        
        # Get agent information
        agent_info = {
            'tool_id': tool_id,
            'tool_name': tool.get('name') if tool else None,
            'agent_class_name': agent_class_name,
            'description': tool.get('description') if tool else None,
            'task': tool.get('task') if tool else None,
            'instructions': None,
            'tools': [],
            'sub_agents': [],
        }
        
        # Try to get instructions from class docstring or __init__ docstring
        if hasattr(AgentClass, '__doc__') and AgentClass.__doc__:
            agent_info['instructions'] = AgentClass.__doc__.strip()
        
        # Check if agent has tools (for NoteBookAgentCreator, it has section_maker and write_to_file)
        if hasattr(AgentClass, '__init__'):
            import inspect
            init_signature = inspect.signature(AgentClass.__init__)
            # Check if the agent uses tools internally
            if agent_class_name == 'NoteBookAgentCreator':
                agent_info['tools'] = [
                    {
                        'name': 'section_maker',
                        'description': '接受一个 section title 和 description，输出该 section 的 notebook 内容',
                        'type': 'function_tool'
                    },
                    {
                        'name': 'write_to_file',
                        'description': '将 markdown 内容写入到指定的输出文件',
                        'type': 'function_tool'
                    }
                ]
                agent_info['sub_agents'] = [
                    {
                        'name': 'ExerciseRefinementAgent',
                        'description': '优化练习题和例子的Agent',
                        'type': 'specialized_agent'
                    },
                    {
                        'name': 'ProofRefinementAgent',
                        'description': '优化数学证明的Agent',
                        'type': 'specialized_agent'
                    }
                ]
        
        return agent_info
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Error getting agent details: {str(e)}\n\nTraceback: {error_trace}")

"""Tools API routes."""

from fastapi import APIRouter, HTTPException
from backend.database.tools_db import get_all_tools, get_tool as get_tool_from_db
from backend.tools.tool_registry import get_tool_registry
from backend.tools.tool_discovery import init_tool_system
from backend.tools.utils import generate_tools_usage_for_agent
from backend.tools.utils.tool_usage_generator import format_tool_usage

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
        tool = get_tool_from_db(tool_id)
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
        
        tool = get_tool_from_db(tool_id)
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
                from backend.tools.agent_as_tools.NotebookCreator import OutlineMakerAgent
                AgentClass = OutlineMakerAgent
            elif agent_class_name == 'NoteBookAgentCreator':
                # 向后兼容：NoteBookAgentCreator 已被 NotebookCreator 替代
                # NotebookCreator 不是 Agent，所以这里保留旧引用但标记为已废弃
                raise HTTPException(
                    status_code=400, 
                    detail="NoteBookAgentCreator 已被废弃，请使用 NotebookCreator（通过 NotebookCreationStrategies）"
                )
            elif agent_class_name == 'ExerciseRefinementAgent':
                from backend.tools.agent_as_tools.refinement_agents import ExerciseRefinementAgent
                AgentClass = ExerciseRefinementAgent
            elif agent_class_name == 'ProofRefinementAgent':
                from backend.tools.agent_as_tools.refinement_agents import ProofRefinementAgent
                AgentClass = ProofRefinementAgent
            elif agent_class_name == 'IntentExtractionAgent':
                from backend.tools.agent_as_tools.IntentExtractionAgent import IntentExtractionAgent
                AgentClass = IntentExtractionAgent
            elif agent_class_name == 'OutlineRevisionAgent':
                from backend.tools.agent_as_tools.OutlineRevisionAgent import OutlineRevisionAgent
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
            'prompt_template': None,
            'tools': [],
            'sub_agents': [],
        }
        
        # Try to get instructions by creating a sample agent instance
        # This will give us the actual prompt used by the agent
        try:
            if agent_class_name == 'OutlineMakerAgent':
                # OutlineMakerAgent needs file_path
                import tempfile
                import os
                # Create a temporary empty file for testing
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
                temp_file.write("# Test Document\n\nThis is a test document.")
                temp_file.close()
                try:
                    sample_agent = AgentClass(temp_file.name)
                    if hasattr(sample_agent, 'instructions'):
                        agent_info['instructions'] = sample_agent.instructions
                        agent_info['prompt_template'] = sample_agent.instructions  # For now, same as instructions
                finally:
                    os.unlink(temp_file.name)
            elif agent_class_name == 'NoteBookAgentCreator':
                # NoteBookAgentCreator 已被废弃，跳过
                agent_info['instructions'] = "[已废弃] NoteBookAgentCreator 已被 NotebookCreator 替代"
                agent_info['prompt_template'] = "[已废弃]"
            elif agent_class_name in ['ExerciseRefinementAgent', 'ProofRefinementAgent']:
                # These are BaseRefinementAgent, not Agent class
                # They don't have instructions directly, but they create internal Agent
                # We can create a sample instance to get the internal agent's instructions
                from backend.models import Section
                sample_section = Section(
                    section_title="示例章节",
                    introduction="这是一个示例章节的介绍",
                    concept_blocks=[],
                    summary=""
                )
                try:
                    sample_refiner = AgentClass(sample_section, section_context="示例上下文")
                    # New RefinementAgent uses internal Agent, so we can't directly get instructions
                    # But we can describe what it does
                    if agent_class_name == 'ExerciseRefinementAgent':
                        agent_info['instructions'] = "[RefinementAgent] 优化练习题和例子，识别题目类型，补充缺失内容，验证完整性"
                    elif agent_class_name == 'ProofRefinementAgent':
                        agent_info['instructions'] = "[RefinementAgent] 优化数学证明，补充中间步骤，添加公式引用，优化证明结构"
                    agent_info['prompt_template'] = agent_info['instructions']
                except Exception as create_error:
                    print(f"[get_agent_as_tool_details] Error creating {agent_class_name} instance: {create_error}")
                    import traceback
                    traceback.print_exc()
            elif agent_class_name == 'IntentExtractionAgent':
                # IntentExtractionAgent needs user_request and optional file_path
                sample_agent = AgentClass("示例用户请求", file_path=None)
                if hasattr(sample_agent, 'instructions'):
                    agent_info['instructions'] = sample_agent.instructions
                    agent_info['prompt_template'] = sample_agent.instructions
            elif agent_class_name == 'OutlineRevisionAgent':
                # OutlineRevisionAgent needs outline and revision_request
                from backend.models import Outline
                sample_outline = Outline(
                    notebook_title="示例笔记本",
                    notebook_description="示例描述",
                    outlines={"章节1": "描述1"}
                )
                sample_agent = AgentClass(sample_outline, "示例修改请求")
                if hasattr(sample_agent, 'instructions'):
                    agent_info['instructions'] = sample_agent.instructions
                    agent_info['prompt_template'] = sample_agent.instructions
        except Exception as e:
            print(f"[get_agent_as_tool_details] Failed to create sample agent for instructions: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to docstring
            if hasattr(AgentClass, '__doc__') and AgentClass.__doc__:
                agent_info['instructions'] = AgentClass.__doc__.strip()
                agent_info['prompt_template'] = AgentClass.__doc__.strip()
        
        # If still no instructions, try docstring
        if not agent_info['instructions']:
            if hasattr(AgentClass, '__doc__') and AgentClass.__doc__:
                agent_info['instructions'] = AgentClass.__doc__.strip()
                agent_info['prompt_template'] = AgentClass.__doc__.strip()
        
        # Log what we got
        if agent_info['instructions']:
            print(f"[get_agent_as_tool_details] Successfully retrieved instructions for {agent_class_name} (length: {len(agent_info['instructions'])})")
        else:
            print(f"[get_agent_as_tool_details] Warning: No instructions found for {agent_class_name}")
        
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

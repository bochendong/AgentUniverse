"""Communication tools - agent间通信工具"""

from typing import TYPE_CHECKING
from agents import function_tool
from backend.tools.tool_registry import register_function_tool

if TYPE_CHECKING:
    from backend.agent.BaseAgent import BaseAgent


@register_function_tool(
    tool_id="send_message",
    name="send_message",
    description="向指定ID的agent发送消息",
    task="用于agent之间的通信，允许一个agent向另一个agent发送消息并获取响应",
    agent_types=["BaseAgent"],
    input_params={
        "id": {"type": "str", "description": "Agent ID", "required": True},
        "message": {"type": "str", "description": "要发送的消息", "required": True},
    },
    output_type="str",
    output_description="返回目标agent处理消息后的完整响应文本。如果agent执行成功，返回agent的执行结果；如果加载agent失败，返回错误信息；如果执行过程中出现异常，返回错误信息",
    required_agent_attrs=["load_agent_from_db_by_id", "run_async_safely"],
)
def create_send_message_tool(agent: 'BaseAgent'):
    """
    Create a send_message tool function for communicating with sub-agents.
    
    Args:
        agent: The agent instance that will use this tool
        
    Returns:
        A function_tool decorated function for sending messages
    """
    @function_tool
    def send_message(id: str, message: str) -> str:
        """向指定ID的agent发送消息

        Args:
            id: Agent ID（完整的UUID，不是部分ID）
            message: Message to send

        Returns:
            Response from the agent
        """
        # Validate ID format (should be a valid UUID format)
        if len(id) < 8:
            return f"Error: Agent ID '{id}' is too short. Please use the complete agent ID from the agents list."
        
        # Use AgentManager to wake up the agent (ensures tools are restored)
        from backend.utils.agent_manager import wake_agent
        target_agent = wake_agent(id, db_path=getattr(agent, 'DB_PATH', None))
        
        if target_agent is None:
            # Try to find agent by partial ID match
            try:
                from backend.database.agent_db import load_all_agents
                all_agents = load_all_agents(getattr(agent, 'DB_PATH', None))
                matching_ids = [aid for aid in all_agents.keys() if aid.startswith(id)]
                if matching_ids:
                    if len(matching_ids) == 1:
                        target_agent = wake_agent(matching_ids[0], db_path=getattr(agent, 'DB_PATH', None))
                        if target_agent:
                            return f"Error: Agent ID '{id}' is incomplete. Use the complete ID: {matching_ids[0]}"
                    else:
                        return f"Error: Agent ID '{id}' is ambiguous. Found {len(matching_ids)} matching agents. Please use the complete agent ID from the agents list."
            except Exception:
                pass
            
            return f"Error: Failed to load agent with ID {id} from database. Please check:\n1. The agent ID is correct and complete\n2. The agent exists in the database\n3. For notebook creation, use 'generate_outline' to generate outline, then use 'send_message' to send action='create_notebook' message to MasterAgent"

        # Ensure tools are restored (AgentManager should do this, but double-check)
        if not hasattr(target_agent, 'tools') or target_agent.tools is None:
            from backend.utils.agent_manager import get_agent_manager
            get_agent_manager()._ensure_tools_restored(target_agent)

        try:
            output = agent.run_async_safely(target_agent.receive_messgae(message))
            return str(output)
        except Exception as e:
            return f"Error sending message: {str(e)}"
    
    return send_message

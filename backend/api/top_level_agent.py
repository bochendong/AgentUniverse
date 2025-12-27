"""TopLevelAgent API routes."""

from fastapi import APIRouter, HTTPException
from agents import Runner, SQLiteSession, RunConfig
from backend.api.models import (
    ChatRequest, SourceChatRequest, ChatResponse, SessionCreateRequest, SessionResponse,
    StructuredMessageData, MessageType, ConversationsResponse
)
from backend.api.utils import get_top_level_agent, _serialize_agent_card
from backend.agent.TopLevelAgent import TopLevelAgent
from backend.agent.MasterAgent import MasterAgent
from backend.agent.NoteBookAgent import NoteBookAgent
from backend.agent.BaseAgent import AgentType
from backend.tools.utils import get_all_agent_info
from backend.database.session_db import create_session, list_sessions, delete_session, get_conversations
from backend.utils.tracing_collector import track_agent_run
from backend.database.agent_db import get_db_path
from backend.database.session_db import add_conversation
from typing import Optional
import os
import base64
import json
import re

router = APIRouter(prefix="/api/top-level-agent", tags=["top-level-agent"])


@router.get("/info")
async def get_top_level_agent_info():
    """Get information about the TopLevelAgent."""
    try:
        agent = get_top_level_agent()
        
        # Ensure sub_agent_ids is not None
        if not hasattr(agent, 'sub_agent_ids') or agent.sub_agent_ids is None:
            agent.sub_agent_ids = []
            agent.save_to_db()
        
        # Ensure tools is not None (critical for Runner.run)
        if not hasattr(agent, 'tools') or agent.tools is None:
            # Try to recreate tools
            if hasattr(agent, '_recreate_tools'):
                try:
                    agent._recreate_tools()
                except Exception as e:
                    print(f"Warning: Failed to recreate tools: {e}")
                    agent.tools = []
                else:
                    agent.tools = []
        
        # Get all agent info for the card
        all_agent_info = get_all_agent_info()
        
        # Serialize agent card
        agent_card = _serialize_agent_card(agent.get_agent_card(all_agent_info))
        
        return {
            "agent": agent_card,
            "sub_agents": all_agent_info
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error getting agent info: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error getting agent info: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_top_level_agent(request: ChatRequest):
    """普通聊天 - 只支持文本消息，使用session管理对话历史"""
    try:
        # 确保使用最新的 .env 文件中的 API key
        try:
            from dotenv import load_dotenv
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            env_path = project_root / ".env"
            if env_path.exists():
                load_dotenv(env_path, override=True)
        except Exception:
            pass  # 如果无法加载 .env，继续使用系统环境变量
        
        agent = get_top_level_agent()
        
        # Ensure sub_agent_ids is not None
        if not hasattr(agent, 'sub_agent_ids') or agent.sub_agent_ids is None:
            agent.sub_agent_ids = []
            agent.save_to_db()
        
        # Ensure tools is not None (critical for Runner.run)
        if not hasattr(agent, 'tools') or agent.tools is None:
            # Try to recreate tools
            if hasattr(agent, '_recreate_tools'):
                try:
                    agent._recreate_tools()
                except Exception as e:
                    print(f"Warning: Failed to recreate tools: {e}")
                    agent.tools = []
            else:
                agent.tools = []
        
        # Create session if not provided
        session_id = request.session_id
        if not session_id:
            session_data = create_session()
            session_id = session_data['id']
        
        # Create SQLiteSession for maintaining conversation context
        db_path = get_db_path()
        db_dir = os.path.dirname(db_path)
        session_db_path = os.path.join(db_dir, "session_history.db")
        
        # Ensure directory exists
        os.makedirs(db_dir, exist_ok=True)
        
        # Create SQLiteSession instance - this will maintain conversation history
        session = SQLiteSession(session_id, session_db_path)
        
        # Add user message to session (for our own tracking)
        from backend.database.session_db import add_conversation
        add_conversation(session_id, "user", request.message)
        
        # Use simple string message with session (no images, no files)
        runner_message = request.message
        
        # Run agent with tracing and tool logging hooks
        from backend.utils.tool_logging_hooks import ToolLoggingHook
        from backend.utils.tracing_collector import track_agent_run
        
        tool_logging_hook = ToolLoggingHook()
        with track_agent_run(session_id, agent, request.message):
            result = await Runner.run(agent, runner_message, session=session, hooks=tool_logging_hook)
        
        # Extract response and structured data
        response_text, structured_data = _extract_response(result, user_message=request.message)
        
        # Add assistant response to session
        add_conversation(session_id, "assistant", response_text)
        
        return ChatResponse(response=response_text, session_id=session_id, structured_data=structured_data)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in chat: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}\n\nTraceback: {error_trace}")


@router.post("/source-chat", response_model=ChatResponse)
async def source_chat_with_top_level_agent(request: SourceChatRequest):
    """带文件的聊天 - 支持文件上传和图片，手动管理对话历史"""
    try:
        # 检查环境变量中的 API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="OPENAI_API_KEY 环境变量未设置。请确保在启动服务器前设置了正确的 API key。"
            )
        if not api_key.startswith('sk-'):
            raise HTTPException(
                status_code=500,
                detail=f"OPENAI_API_KEY 格式不正确。API key 应该以 'sk-' 开头，但当前值以 '{api_key[:10]}...' 开头。"
            )
        
        agent = get_top_level_agent()
        
        # Ensure sub_agent_ids is not None
        if not hasattr(agent, 'sub_agent_ids') or agent.sub_agent_ids is None:
            agent.sub_agent_ids = []
            agent.save_to_db()
        
        # Ensure tools is not None (critical for Runner.run)
        if not hasattr(agent, 'tools') or agent.tools is None:
            # Try to recreate tools
            if hasattr(agent, '_recreate_tools'):
                try:
                    agent._recreate_tools()
                except Exception as e:
                    print(f"Warning: Failed to recreate tools: {e}")
                    agent.tools = []
            else:
                agent.tools = []
        
        # Create session if not provided
        session_id = request.session_id
        if not session_id:
            session_data = create_session()
            session_id = session_data['id']
        
        # Build user message
        user_message = request.message or ""
        
        # Prepare file content if file_path is provided
        # 参考示例代码，使用 input_file 类型处理文件上传
        file_content_item = None
        if request.file_path:
            file_name = os.path.basename(request.file_path)
            file_ext = os.path.splitext(request.file_path)[1].lower()
            
            # Read file and convert to base64
            try:
                with open(request.file_path, "rb") as f:
                    file_bytes = f.read()
                    file_content_b64 = base64.b64encode(file_bytes).decode("utf-8")
                
                # Determine MIME type based on file extension
                if file_ext == '.pdf':
                    file_mime_type = "application/pdf"
                elif file_ext in ['.doc', '.docx']:
                    file_mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                elif file_ext in ['.md', '.markdown']:
                    file_mime_type = "text/markdown"
                else:
                    file_mime_type = "application/octet-stream"
                
                # 创建 input_file 类型的消息内容（参考 Pdf.md 示例）
                file_content_item = {
                    "type": "input_file",
                    "file_data": f"data:{file_mime_type};base64,{file_content_b64}",
                    "filename": file_name,
                }
            except Exception as e:
                print(f"Warning: Failed to read file {request.file_path}: {e}")
                # Fallback to old method if file reading fails
                file_info = f"\n\n我需要上传文件并创建笔记本。\n文件路径：{request.file_path}\n文件名：{file_name}\n\n请调用 generate_outline 工具，参数为：\n- file_path: \"{request.file_path}\"\n- user_request: \"{user_message.strip() or '请根据文件内容创建笔记本'}\""
                user_message = user_message + file_info if user_message.strip() else f"请处理上传的文件并创建笔记本。{file_info}"
                file_content_item = None
        
        # Create SQLiteSession for maintaining conversation context
        # This will automatically manage conversation history
        db_path = get_db_path()
        db_dir = os.path.dirname(db_path)
        session_db_path = os.path.join(db_dir, "session_history.db")
        os.makedirs(db_dir, exist_ok=True)
        session = SQLiteSession(session_id, session_db_path)
        
        # Add user message to our own tracking database
        from backend.database.session_db import add_conversation
        add_conversation(session_id, "user", user_message if user_message.strip() else "[文件/图片消息]")
        
        # Build new messages for current request
        # 参考示例代码，使用 session_input_callback 处理文件/图片上传
        # Check if we have images or files that need special handling
        has_file_or_image = (file_content_item is not None) or (request.images and len(request.images) > 0)
        
        if has_file_or_image:
            # 如果有文件或图片，使用 session with session_input_callback
            # 这样可以合并列表输入（文件/图片）与会话历史
            
            # Build message array: first message with file/images, then text message
            # 参考示例代码的格式
            content_items = []
            
            # 添加文件（如果有）
            if file_content_item:
                content_items.append(file_content_item)
            
            # 添加图片（如果有）
            if request.images and len(request.images) > 0:
                content_items.extend(request.images)
            
            # 构建消息数组
            messages_for_runner = [
                {
                    "role": "user",
                    "content": content_items,  # List of file/image objects
                }
            ]
            
            # Add text message if provided
            if user_message and user_message.strip():
                messages_for_runner.append({
                    "role": "user",
                    "content": user_message,
                })
            
            # Define session_input_callback to merge list input with session history
            # 参考示例代码中的实现
            async def session_input_callback(new_input, history):
                """
                将新的列表输入（包含文件/图片）与已有的对话历史合并
                
                Args:
                    new_input: 新的输入（列表格式，包含文件/图片）
                    history: 已有的对话历史（从session获取）
                
                Returns:
                    合并后的输入列表
                """
                # 将历史记录和新的输入合并
                return history + new_input
            
            runner_message = messages_for_runner
            use_session = True
            use_callback = True
            
            # Store user message (without file/images) to database for tracking
            # 文件/图片内容不存储在数据库中，只存储文本消息
            add_conversation(session_id, "user", user_message if user_message.strip() else "[文件/图片消息]")
        else:
            # No images, just text message - use session normally
            runner_message = user_message
            use_session = True
            use_callback = False
            
            # Store user message to database for tracking
            add_conversation(session_id, "user", user_message)
        
        # Run agent with tracing and tool logging hooks
        from backend.utils.tool_logging_hooks import ToolLoggingHook
        from backend.utils.tracing_collector import track_agent_run
        
        tool_logging_hook = ToolLoggingHook()
        with track_agent_run(session_id, agent, user_message):
            if use_session and use_callback:
                # Use session with callback for file/image inputs
                result = await Runner.run(
                    agent,
                    runner_message,
                    session=session,
                    hooks=tool_logging_hook,
                    run_config=RunConfig(session_input_callback=session_input_callback)
                )
            elif use_session:
                # Use session normally for text-only messages
                result = await Runner.run(agent, runner_message, session=session, hooks=tool_logging_hook)
            else:
                # Fallback: manual history management (should not happen now)
                result = await Runner.run(agent, runner_message, session=None, hooks=tool_logging_hook)
        
        # Extract response and structured data
        response_text, structured_data = _extract_response(result, user_message=user_message)
        
        # Add assistant response to session
        add_conversation(session_id, "assistant", response_text)
        
        return ChatResponse(response=response_text, session_id=session_id, structured_data=structured_data)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in source-chat: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error in source-chat: {str(e)}\n\nTraceback: {error_trace}")


def _extract_response(result, user_message: str = None):
    """
    提取响应和结构化数据的辅助函数
    根据响应内容智能判断消息类型，返回结构化的消息数据
    
    Args:
        result: Runner.run 的结果
        user_message: 用户消息（用于判断上下文）
    
    Returns:
        (response_text, structured_data): 响应文本和结构化数据
    """
    response_text = None
    response_text = None
    structured_data = None
    
    if hasattr(result, 'final_output'):
        final_output = result.final_output
        
        # Check if final_output is a structured object (Pydantic model or dict)
        if isinstance(final_output, dict):
            structured_data = _parse_structured_output(final_output, user_message)
            response_text = _generate_user_friendly_message(final_output, structured_data)
        elif hasattr(final_output, '__dict__'):
            # Pydantic model or similar
            try:
                # Try to convert to dict
                if hasattr(final_output, 'model_dump'):
                    output_dict = final_output.model_dump()
                elif hasattr(final_output, 'dict'):
                    output_dict = final_output.dict()
                else:
                    output_dict = final_output.__dict__
                
                structured_data = _parse_structured_output(output_dict, user_message)
                response_text = _generate_user_friendly_message(output_dict, structured_data)
            except:
                response_text = str(final_output)
        else:
            # Try to parse as JSON string (from create_notebook or generate_outline tool)
            try:
                if isinstance(final_output, str):
                    # 尝试解析 JSON 字符串
                    parsed = json.loads(final_output)
                    if isinstance(parsed, dict):
                        structured_data = _parse_structured_output(parsed, user_message)
                        response_text = _generate_user_friendly_message(parsed, structured_data)
                    else:
                        response_text = final_output
                else:
                    response_text = str(final_output)
            except (json.JSONDecodeError, ValueError):
                # 不是 JSON，尝试从文本中提取结构化信息
                response_text = str(final_output)
                structured_data = _parse_text_for_structure(response_text, user_message)
    else:
        response_text = str(result)
        structured_data = _parse_text_for_structure(response_text, user_message)
    
    return response_text, structured_data

def _parse_structured_output(output_dict: dict, user_message: str = None) -> Optional[StructuredMessageData]:
    """
    解析结构化输出，判断消息类型
    
    Args:
        output_dict: 输出字典
        user_message: 用户消息（用于上下文判断）
    
    Returns:
        StructuredMessageData 对象或 None
    """
    # 检查是否是笔记本创建结果
    if 'notebook_id' in output_dict and 'notebook_title' in output_dict:
        return StructuredMessageData(
            message_type=MessageType.NOTEBOOK_CREATED,
            notebook_id=output_dict.get('notebook_id'),
            notebook_title=output_dict.get('notebook_title')
        )
    
    # 检查是否是大纲生成结果
    if output_dict.get('type') == 'outline' and 'outline' in output_dict:
        return StructuredMessageData(
            message_type=MessageType.OUTLINE,
            outline=output_dict.get('outline'),
            file_path=output_dict.get('file_path'),
            user_request=output_dict.get('user_request')
        )
    
    # 检查是否包含大纲结构（即使没有 type 字段）
    if 'outline' in output_dict or 'outlines' in output_dict:
        outline = output_dict.get('outline') or output_dict.get('outlines')
        return StructuredMessageData(
            message_type=MessageType.OUTLINE,
            outline=outline if isinstance(outline, dict) else {'outlines': outline},
            file_path=output_dict.get('file_path'),
            user_request=output_dict.get('user_request')
        )
    
    return None


def _parse_text_for_structure(text: str, user_message: str = None) -> Optional[StructuredMessageData]:
    """
    从文本中解析结构化信息
    
    Args:
        text: 响应文本
        user_message: 用户消息（用于上下文判断）
    
    Returns:
        StructuredMessageData 对象或 None
    """
    # 检查是否包含题目关键词（用于识别题目）
    question_keywords = ['题目', '问题', 'question', '题目内容', '题目文本', '题目原文']
    if any(keyword in text.lower() for keyword in question_keywords):
        # 尝试提取题目文本
        question_match = re.search(r'题目[：:]\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if question_match:
            return StructuredMessageData(
                message_type=MessageType.QUESTION,
                question_text=question_match.group(1).strip()
            )
    
    # 检查是否包含笔记本创建信息
    notebook_match = re.search(r'笔记本[：:]\s*ID[：:]\s*([^\n]+)\n.*标题[：:]\s*([^\n]+)', text)
    if notebook_match:
        return StructuredMessageData(
            message_type=MessageType.NOTEBOOK_CREATED,
            notebook_id=notebook_match.group(1).strip(),
            notebook_title=notebook_match.group(2).strip()
        )
    
    # 检查是否包含大纲（JSON代码块）
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
    if json_match:
        try:
            parsed = json.loads(json_match.group(1))
            if isinstance(parsed, dict) and ('outline' in parsed or 'outlines' in parsed):
                return StructuredMessageData(
                    message_type=MessageType.OUTLINE,
                    outline=parsed.get('outline') or parsed.get('outlines'),
                    file_path=parsed.get('file_path'),
                    user_request=parsed.get('user_request')
                )
        except:
            pass
    
    # 检查是否值得添加到笔记（包含定义、概念、解释等）
    valuable_keywords = ['定义', '概念', '定理', '证明', '例子', '总结', '要点']
    if any(keyword in text for keyword in valuable_keywords) and len(text) > 100:
        return StructuredMessageData(
            message_type=MessageType.ADD_TO_NOTEBOOK,
            content_summary=text[:200] + "..." if len(text) > 200 else text
        )
    
    return None


def _generate_user_friendly_message(output_dict: dict, structured_data: Optional[StructuredMessageData] = None) -> str:
    """
    根据结构化数据生成用户友好的消息文本
    
    Args:
        output_dict: 输出字典
        structured_data: 结构化数据
    
    Returns:
        用户友好的消息文本
    """
    if structured_data:
        if structured_data.message_type == MessageType.NOTEBOOK_CREATED:
            return f"✅ 已成功创建笔记本！\n\n**标题：** {structured_data.notebook_title}\n**ID：** {structured_data.notebook_id}"
        
        elif structured_data.message_type == MessageType.OUTLINE:
            # 使用工具返回的消息，如果没有则生成默认消息
            if 'message' in output_dict:
                return output_dict['message']
            return "📋 我已经为您生成了笔记本大纲，请查看并确认。"
        
        elif structured_data.message_type == MessageType.QUESTION:
            return output_dict.get('message', str(output_dict))
        
        elif structured_data.message_type == MessageType.ADD_TO_NOTEBOOK:
            return str(output_dict)
    
    # 默认返回原始输出
    return str(output_dict)


@router.post("/sessions", response_model=SessionResponse)
async def create_top_level_agent_session(request: SessionCreateRequest):
    """Create a new session for TopLevelAgent."""
    try:
        session_data = create_session(title=request.title if hasattr(request, 'title') else None)
        return SessionResponse(**session_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@router.get("/sessions")
async def list_top_level_agent_sessions():
    """List all sessions for TopLevelAgent."""
    try:
        sessions = list_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")


@router.get("/sessions/{session_id}/conversations", response_model=ConversationsResponse)
async def get_top_level_agent_session_conversations(session_id: str):
    """Get conversations for a specific session."""
    try:
        conversations = get_conversations(session_id)
        return ConversationsResponse(conversations=conversations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversations: {str(e)}")


@router.delete("/sessions/{session_id}")
async def delete_top_level_agent_session(session_id: str):
    """Delete a session."""
    try:
        success = delete_session(session_id)
        if success:
            return {"message": "Session deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

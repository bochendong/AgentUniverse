"""Notebook content management tools - Notebook内容管理工具"""

from typing import TYPE_CHECKING, Literal, Optional
from agents import function_tool
from backend.tools.tool_registry import register_function_tool

if TYPE_CHECKING:
    from backend.agent.BaseAgent import BaseAgent


@register_function_tool(
    tool_id="get_content_by_id",
    name="get_content_by_id",
    description="通过ID获取笔记内容信息",
    task="用于查看指定ID的内容的当前状态和结构，便于确定如何修改。",
    agent_types=["NoteBookAgent"],
    input_params={
        "content_id": {"type": "str", "description": "内容ID（如 field_abc123, section_def456）", "required": True},
    },
    output_type="str",
    output_description="返回JSON字符串，包含内容的当前状态、类型和ID信息",
    required_agent_attrs=["sections"],
)
def create_get_content_by_id_tool(notebook_agent: 'BaseAgent'):
    """
    Create a get_content_by_id tool function for NoteBookAgent.
    
    Args:
        notebook_agent: The NoteBookAgent instance that will use this tool
        
    Returns:
        A function_tool decorated function for getting content by ID
    """
    import json
    from backend.utils.content_id_utils import locate_by_id
    
    @function_tool
    def get_content_by_id(content_id: str) -> str:
        """通过ID获取内容信息"""
        try:
            # 定位内容
            result = locate_by_id(notebook_agent, content_id)
            
            if result is None:
                return json.dumps({
                    "error": f"未找到ID为 '{content_id}' 的内容",
                    "content_id": content_id
                }, ensure_ascii=False)
            
            content_obj, object_type, field_name = result
            
            # 构建返回信息
            info = {
                "content_id": content_id,
                "object_type": object_type,
                "field_name": field_name,
            }
            
            # 根据对象类型提取内容
            if field_name:
                # 字段ID，返回字段值
                if hasattr(content_obj, field_name):
                    info["content"] = getattr(content_obj, field_name)
                else:
                    info["error"] = f"对象没有 '{field_name}' 字段"
            else:
                # 对象ID，返回对象的基本信息
                if object_type == "section":
                    info["section_title"] = content_obj.section_title
                    info["content"] = {
                        "section_title": content_obj.section_title,
                        "introduction": content_obj.introduction[:200] + "..." if len(content_obj.introduction) > 200 else content_obj.introduction,
                        "summary": content_obj.summary[:200] + "..." if len(content_obj.summary) > 200 else content_obj.summary,
                    }
                elif object_type == "concept_block":
                    info["content"] = {
                        "definition": content_obj.definition[:200] + "..." if len(content_obj.definition) > 200 else content_obj.definition,
                    }
                elif object_type == "example":
                    info["content"] = {
                        "question": content_obj.question,
                        "answer": content_obj.answer,
                        "question_type": getattr(content_obj, 'question_type', None),
                    }
                elif object_type == "theorem":
                    info["content"] = {
                        "theorem": content_obj.theorem[:200] + "..." if len(content_obj.theorem) > 200 else content_obj.theorem,
                        "proof": content_obj.proof[:200] + "..." if content_obj.proof and len(content_obj.proof) > 200 else content_obj.proof,
                    }
                else:
                    info["content"] = str(content_obj)[:500]
            
            return json.dumps(info, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({
                "error": f"获取内容时出错: {str(e)}",
                "content_id": content_id
            }, ensure_ascii=False)
    
    return get_content_by_id


@register_function_tool(
    tool_id="modify_by_id",
    name="modify_by_id",
    description="通过ID修改笔记内容（统一的接口，支持create/update/delete）",
    task="NoteBookAgent用于通过ID精确修改笔记的特定部分，支持创建、更新、删除操作。修改后自动重新生成notes并同步outline。",
    agent_types=["NoteBookAgent"],
    input_params={
        "content_id": {"type": "str", "description": "内容ID（update/delete时必需，create时不需要）", "required": False},
        "operation_type": {"type": "str", "description": "操作类型：'create'（新增）、'update'（修改）、'delete'（删除）", "required": True},
        "field_name": {"type": "str", "description": "字段名（update时必需，如 'introduction', 'answer'）", "required": False},
        "content_type": {"type": "str", "description": "内容类型（create时必需，如 'concept_block', 'example', 'note'）", "required": False},
        "parent_id": {"type": "str", "description": "父级ID（create时必需，如 section_id 或 concept_block_id）", "required": False},
        "position": {"type": "str", "description": "插入位置（create时可选）：'before'（之前）、'after'（之后）、'append'（追加，默认）", "required": False},
        "target_index": {"type": "int", "description": "目标索引（create时可选，用于列表定位）", "required": False},
        "new_content": {"type": "str", "description": "新内容（create和update时必需，字符串字段直接传内容，对象传JSON字符串）", "required": False},
        "update_mode": {"type": "str", "description": "更新模式（update时可选，仅用于字符串字段）：'append'（追加）、'prepend'（前置）、'replace'（替换，默认）", "required": False},
    },
    output_type="str",
    output_description="返回操作结果字符串。如果是create操作，包含新生成的ID",
    required_agent_attrs=["sections", "outline", "save_to_db"],
)
def create_modify_by_id_tool(notebook_agent: 'BaseAgent'):
    """
    Create a modify_by_id tool function for NoteBookAgent.
    
    Args:
        notebook_agent: The NoteBookAgent instance that will use this tool
        
    Returns:
        A function_tool decorated function for modifying content by ID
    """
    import json
    from backend.utils.content_id_utils import locate_by_id, generate_content_id, assign_ids_to_new_content
    from backend.models import Section, ConceptBlock, Example, Theorem
    
    def _sync_outline_from_sections():
        """同步 outline 以匹配当前的 sections"""
        if not notebook_agent.outline:
            from backend.models import Outline
            notebook_agent.outline = Outline(
                notebook_title=notebook_agent.notebook_title or "",
                notebook_description=getattr(notebook_agent, 'notebook_description', '') or "",
                outlines={}
            )
        
        # 同步 notebook_title 和 notebook_description
        if notebook_agent.notebook_title:
            notebook_agent.outline.notebook_title = notebook_agent.notebook_title
        if hasattr(notebook_agent, 'notebook_description') and notebook_agent.notebook_description:
            notebook_agent.outline.notebook_description = notebook_agent.notebook_description
        
        # 同步章节列表
        current_section_titles = set(notebook_agent.sections.keys()) if notebook_agent.sections else set()
        outline_section_titles = set(notebook_agent.outline.outlines.keys()) if notebook_agent.outline and notebook_agent.outline.outlines else set()
        
        # 处理章节标题改变
        for old_title, section in list(notebook_agent.sections.items()):
            if section.section_title != old_title:
                new_title = section.section_title
                if old_title in notebook_agent.outline.outlines:
                    notebook_agent.outline.outlines[new_title] = notebook_agent.outline.outlines.pop(old_title)
                notebook_agent.sections[new_title] = notebook_agent.sections.pop(old_title)
        
        # 添加新章节
        for section_title in current_section_titles:
            if section_title not in outline_section_titles:
                section = notebook_agent.sections[section_title]
                description = section.introduction[:200] if section.introduction else f"章节：{section_title}"
                notebook_agent.outline.outlines[section_title] = description
        
        # 删除不存在的章节
        for section_title in outline_section_titles - current_section_titles:
            notebook_agent.outline.outlines.pop(section_title, None)
    
    def _sync_notes_from_sections():
        """从结构化数据重新生成 notes，并同步更新 outline"""
        # 同步 outline（检测并更新）
        _sync_outline_from_sections()
        
        # 确保所有内容有ID
        from backend.utils.content_id_utils import ensure_ids
        ensure_ids(notebook_agent)
        
        # 生成markdown (with IDs included so AI can use modify_by_id tool)
        from backend.tools.utils import generate_markdown_from_agent
        notebook_agent.notes = generate_markdown_from_agent(notebook_agent, include_ids=True)
        
        # 保存到数据库
        notebook_agent.save_to_db()
        
        # 清除AgentManager缓存，确保API获取最新数据
        try:
            from backend.utils.agent_manager import get_agent_manager
            get_agent_manager().clear_cache(notebook_agent.id)
        except Exception:
            pass
    
    @function_tool
    def modify_by_id(
        content_id: Optional[str] = None,
        operation_type: Literal["create", "update", "delete"] = "update",
        field_name: Optional[str] = None,
        content_type: Optional[str] = None,
        parent_id: Optional[str] = None,
        position: Literal["before", "after", "append"] = "append",
        target_index: Optional[int] = None,
        new_content: Optional[str] = None,
        update_mode: Literal["append", "prepend", "replace"] = "replace"
    ) -> str:
        """通过ID修改笔记内容"""
        try:
            # 验证参数
            if operation_type == "update" or operation_type == "delete":
                if not content_id:
                    return f"错误：{operation_type} 操作需要提供 content_id"
            
            if operation_type == "create":
                if not content_type:
                    return "错误：create 操作需要提供 content_type"
                if not parent_id:
                    return "错误：create 操作需要提供 parent_id"
                if not new_content:
                    return "错误：create 操作需要提供 new_content"
            
            if operation_type == "update":
                if not field_name:
                    return "错误：update 操作需要提供 field_name"
                if not new_content:
                    return "错误：update 操作需要提供 new_content"
            
            # 执行操作
            if operation_type == "update":
                # 定位内容
                result = locate_by_id(notebook_agent, content_id)
                if result is None:
                    return f"错误：未找到ID为 '{content_id}' 的内容"
                
                content_obj, object_type, existing_field_name = result
                
                # 如果定位到的是字段ID，应该更新该字段
                if existing_field_name:
                    if existing_field_name != field_name:
                        return f"错误：ID '{content_id}' 对应的是 '{existing_field_name}' 字段，不是 '{field_name}' 字段"
                    # 获取现有值
                    old_value = getattr(content_obj, field_name, "")
                    
                    # 处理字符串字段的append/prepend/replace
                    if isinstance(old_value, str) and isinstance(new_content, str):
                        if update_mode == 'append':
                            new_value = old_value + "\n\n" + new_content if old_value else new_content
                        elif update_mode == 'prepend':
                            new_value = new_content + "\n\n" + old_value if old_value else new_content
                        else:  # replace (默认)
                            new_value = new_content
                    else:
                        new_value = new_content
                    
                    setattr(content_obj, field_name, new_value)
                    result_msg = f"成功更新 {object_type} 的 {field_name} 字段（{update_mode}模式）"
                else:
                    # 如果定位到的是对象ID，更新指定的字段
                    if not hasattr(content_obj, field_name):
                        return f"错误：{object_type} 对象没有 '{field_name}' 字段"
                    # 获取现有值
                    old_value = getattr(content_obj, field_name, "")
                    
                    # 处理字符串字段的append/prepend/replace
                    if isinstance(old_value, str) and isinstance(new_content, str):
                        if update_mode == 'append':
                            new_value = old_value + "\n\n" + new_content if old_value else new_content
                        elif update_mode == 'prepend':
                            new_value = new_content + "\n\n" + old_value if old_value else new_content
                        else:  # replace (默认)
                            new_value = new_content
                    else:
                        new_value = new_content
                    
                    setattr(content_obj, field_name, new_value)
                    result_msg = f"成功更新 {object_type} 的 {field_name} 字段（{update_mode}模式）"
                
                # 同步数据（重新生成notes和更新outline）
                _sync_notes_from_sections()
                
                return result_msg
            
            elif operation_type == "delete":
                # TODO: 实现删除功能
                return "删除功能正在实现中"
            
            elif operation_type == "create":
                # 定位父对象
                result = locate_by_id(notebook_agent, parent_id)
                if result is None:
                    return f"错误：未找到父ID为 '{parent_id}' 的内容"
                
                parent_obj, parent_type, _ = result
                new_id = None
                
                if content_type == "example":
                    try:
                        example_dict = json.loads(new_content)
                        new_example = Example(**example_dict)
                        assign_ids_to_new_content(new_example, parent_id, "example")
                        
                        if hasattr(parent_obj, 'examples'):
                            if position == "append":
                                parent_obj.examples.append(new_example)
                            elif position == "before" and target_index is not None:
                                parent_obj.examples.insert(target_index, new_example)
                            elif position == "after" and target_index is not None:
                                parent_obj.examples.insert(target_index + 1, new_example)
                            else:
                                parent_obj.examples.append(new_example)
                        else:
                            return f"错误：{parent_type} 对象没有 examples 列表"
                        
                        new_id = new_example.id
                    except Exception as e:
                        return f"错误：创建 Example 对象失败：{str(e)}"
                
                elif content_type == "concept_block":
                    try:
                        cb_dict = json.loads(new_content)
                        new_cb = ConceptBlock(**cb_dict)
                        assign_ids_to_new_content(new_cb, parent_id, "concept_block")
                        
                        if hasattr(parent_obj, 'concept_blocks'):
                            if position == "append":
                                parent_obj.concept_blocks.append(new_cb)
                            elif position == "before" and target_index is not None:
                                parent_obj.concept_blocks.insert(target_index, new_cb)
                            elif position == "after" and target_index is not None:
                                parent_obj.concept_blocks.insert(target_index + 1, new_cb)
                            else:
                                parent_obj.concept_blocks.append(new_cb)
                        else:
                            return f"错误：{parent_type} 对象没有 concept_blocks 列表"
                        
                        new_id = new_cb.id
                    except Exception as e:
                        return f"错误：创建 ConceptBlock 对象失败：{str(e)}"
                
                else:
                    return f"错误：不支持创建类型 '{content_type}'"
                
                # 同步数据
                _sync_notes_from_sections()
                
                return f"成功创建 {content_type}，新ID：{new_id}"
            
            else:
                return f"错误：不支持的操作类型 '{operation_type}'"
        
        except Exception as e:
            import traceback
            return f"错误：修改操作失败：{str(e)}\n{traceback.format_exc()}"
    
    return modify_by_id


@register_function_tool(
    tool_id="add_content_to_section",
    name="add_content_to_section",
    description="向指定章节的字段或block添加内容（便捷工具）",
    task="NoteBookAgent用于向章节字段或concept_block添加内容，支持append/prepend操作，自动定位section和字段。",
    agent_types=["NoteBookAgent"],
    input_params={
        "section_title": {"type": "str", "description": "章节标题（如'1. PPO基础与背景'）", "required": True},
        "field_name": {"type": "str", "description": "字段名：'introduction'、'summary'、'definition'（需要concept_block_index）、'standalone_notes'", "required": True},
        "new_content": {"type": "str", "description": "要添加的内容（纯文本）", "required": True},
        "position": {"type": "str", "description": "添加位置：'append'（追加）、'prepend'（前置）、'replace'（替换）", "required": False},
        "concept_block_index": {"type": "int", "description": "概念块索引（仅当field_name='definition'时必需，从0开始，表示第几个concept_block）", "required": False},
    },
    output_type="str",
    output_description="返回操作结果字符串",
    required_agent_attrs=["sections"],
)
def create_add_content_to_section_tool(notebook_agent: 'BaseAgent'):
    """
    Create an add_content_to_section tool function for NoteBookAgent.
    
    Args:
        notebook_agent: The NoteBookAgent instance that will use this tool
        
    Returns:
        A function_tool decorated function for adding content to section fields
    """
    from backend.utils.content_id_utils import ensure_ids
    
    def _sync_outline_from_sections():
        """同步 outline 以匹配当前的 sections"""
        if not notebook_agent.outline:
            from backend.models import Outline
            notebook_agent.outline = Outline(
                notebook_title=notebook_agent.notebook_title or "",
                notebook_description=getattr(notebook_agent, 'notebook_description', '') or "",
                outlines={}
            )
        
        # 同步 notebook_title 和 notebook_description
        if notebook_agent.notebook_title:
            notebook_agent.outline.notebook_title = notebook_agent.notebook_title
        if hasattr(notebook_agent, 'notebook_description') and notebook_agent.notebook_description:
            notebook_agent.outline.notebook_description = notebook_agent.notebook_description
        
        # 同步章节列表
        current_section_titles = set(notebook_agent.sections.keys()) if notebook_agent.sections else set()
        outline_section_titles = set(notebook_agent.outline.outlines.keys()) if notebook_agent.outline and notebook_agent.outline.outlines else set()
        
        # 处理章节标题改变
        for old_title, section in list(notebook_agent.sections.items()):
            if section.section_title != old_title:
                new_title = section.section_title
                if old_title in notebook_agent.outline.outlines:
                    notebook_agent.outline.outlines[new_title] = notebook_agent.outline.outlines.pop(old_title)
                notebook_agent.sections[new_title] = notebook_agent.sections.pop(old_title)
        
        # 添加新章节
        for section_title in current_section_titles:
            if section_title not in outline_section_titles:
                section = notebook_agent.sections[section_title]
                description = section.introduction[:200] if section.introduction else f"章节：{section_title}"
                notebook_agent.outline.outlines[section_title] = description
        
        # 删除不存在的章节
        for section_title in outline_section_titles - current_section_titles:
            notebook_agent.outline.outlines.pop(section_title, None)
    
    def _sync_notes_from_sections():
        """从结构化数据重新生成 notes，并同步更新 outline"""
        # 同步 outline（检测并更新）
        _sync_outline_from_sections()
        
        # 确保所有内容有ID
        ensure_ids(notebook_agent)
        
        # 生成markdown (with IDs included so AI can use modify_by_id tool)
        from backend.tools.utils import generate_markdown_from_agent
        notebook_agent.notes = generate_markdown_from_agent(notebook_agent, include_ids=True)
        
        # 保存到数据库
        notebook_agent.save_to_db()
        
        # 清除AgentManager缓存，确保API获取最新数据
        try:
            from backend.utils.agent_manager import get_agent_manager
            get_agent_manager().clear_cache(notebook_agent.id)
        except Exception:
            pass
    
    @function_tool
    def add_content_to_section(
        section_title: str,
        field_name: str,
        new_content: str,
        position: Literal["append", "prepend", "replace"] = "append",
        concept_block_index: Optional[int] = None
    ) -> str:
        """向指定章节的字段或block添加内容"""
        # 定位section
        if not notebook_agent.sections or section_title not in notebook_agent.sections:
            return f"错误：未找到章节 '{section_title}'"
        
        section = notebook_agent.sections[section_title]
        
        # 处理不同字段类型
        if field_name == 'introduction' or field_name == 'summary':
            # 字符串字段：introduction 或 summary
            old_value = getattr(section, field_name, "")
            
            # 根据position合并内容
            if position == 'append':
                new_value = old_value + "\n\n" + new_content if old_value else new_content
            elif position == 'prepend':
                new_value = new_content + "\n\n" + old_value if old_value else new_content
            else:  # replace
                new_value = new_content
            
            # 更新字段
            setattr(section, field_name, new_value)
            result_msg = f"成功向章节 '{section_title}' 的 {field_name} 字段添加内容（{position}模式）"
        
        elif field_name == 'definition':
            # concept_block 的 definition 字段
            if concept_block_index is None:
                return f"错误：字段名 'definition' 需要提供 concept_block_index 参数（从0开始，表示第几个concept_block）"
            
            if not hasattr(section, 'concept_blocks') or not section.concept_blocks:
                return f"错误：章节 '{section_title}' 没有 concept_blocks"
            
            if concept_block_index < 0 or concept_block_index >= len(section.concept_blocks):
                return f"错误：concept_block_index {concept_block_index} 超出范围。章节 '{section_title}' 共有 {len(section.concept_blocks)} 个 concept_blocks（索引范围：0-{len(section.concept_blocks)-1}）"
            
            concept_block = section.concept_blocks[concept_block_index]
            old_value = getattr(concept_block, 'definition', "")
            
            # 根据position合并内容
            if position == 'append':
                new_value = old_value + "\n\n" + new_content if old_value else new_content
            elif position == 'prepend':
                new_value = new_content + "\n\n" + old_value if old_value else new_content
            else:  # replace
                new_value = new_content
            
            # 更新字段
            concept_block.definition = new_value
            result_msg = f"成功向章节 '{section_title}' 的第 {concept_block_index + 1} 个 concept_block 的 definition 字段添加内容（{position}模式）"
        
        elif field_name == 'standalone_notes':
            # standalone_notes 是字符串列表
            if not hasattr(section, 'standalone_notes'):
                section.standalone_notes = []
            
            if position == 'append':
                section.standalone_notes.append(new_content)
                result_msg = f"成功向章节 '{section_title}' 的 standalone_notes 列表追加新的笔记"
            elif position == 'prepend':
                section.standalone_notes.insert(0, new_content)
                result_msg = f"成功向章节 '{section_title}' 的 standalone_notes 列表前置新的笔记"
            else:  # replace
                section.standalone_notes = [new_content]
                result_msg = f"成功替换章节 '{section_title}' 的 standalone_notes 列表"
        
        else:
            return f"错误：字段名 '{field_name}' 不支持。支持：introduction, summary, definition（需要concept_block_index）, standalone_notes"
        
        # 同步notes和outline
        _sync_notes_from_sections()
        
        return result_msg
    
    return add_content_to_section

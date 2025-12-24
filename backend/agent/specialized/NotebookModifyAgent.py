"""NotebookModifyAgent - specialized agent for coordinating notebook modifications."""

from typing import Optional
from agents import ModelSettings
from backend.agent.BaseAgent import BaseAgent, AgentType
from backend.tools.agent_as_tools.modify_agents import (
    IntroductionModifyAgent,
    ExerciseModifyAgent,
    DefinitionModifyAgent,
    SummaryModifyAgent
)
from backend.prompts.prompt_loader import load_prompt


class NotebookModifyAgent(BaseAgent):
    """
    专门负责协调笔记修改的Agent
    
    使用 Agent as Tool 模式，将专门的修改agent转换为工具
    
    职责：
    1. 接收来自NotebookAgent的修改请求
    2. 读取带ID的notes，识别需要修改的部分
    3. 根据修改类型调用相应的工具（子agent转换为工具）
    4. 执行实际的修改操作（使用统一的modify_by_id工具）
    """
    
    def __init__(
        self,
        notebook_agent_id: str,  # 关联的NotebookAgent ID
        parent_agent_id: Optional[str] = None,
        DB_PATH: Optional[str] = None
    ):
        self.notebook_agent_id = notebook_agent_id
        
        # 加载关联的NotebookAgent以获取notes
        notebook_agent = self.load_agent_from_db_by_id(notebook_agent_id)
        if not notebook_agent:
            raise ValueError(f"无法找到ID为 {notebook_agent_id} 的NotebookAgent")
        
        # 确保notes包含ID信息
        if hasattr(notebook_agent, 'sections') and notebook_agent.sections:
            from backend.utils.content_id_utils import ensure_ids
            ensure_ids(notebook_agent)
        
        # 生成带ID的markdown
        from backend.tools.utils import generate_markdown_from_agent
        notes_with_ids = generate_markdown_from_agent(notebook_agent, include_ids=True)
        
        # 创建专门的子agent
        introduction_agent = IntroductionModifyAgent()
        exercise_agent = ExerciseModifyAgent()
        definition_agent = DefinitionModifyAgent()
        summary_agent = SummaryModifyAgent()
        
        # 创建modify_by_id和get_content_by_id工具
        from backend.tools.tool_registry import get_tool_registry
        registry = get_tool_registry()
        
        # 注意：这些工具需要notebook_agent实例，但我们在这里使用一个特殊的包装
        # 由于工具创建需要agent实例，我们需要在工具内部动态加载notebook_agent
        modify_by_id_tool = self._create_modify_by_id_tool(notebook_agent_id)
        get_content_by_id_tool = self._create_get_content_by_id_tool(notebook_agent_id)
        
        # 将子agent转换为工具（Agent as Tool模式，参考 openai-cookbook）
        tools = [
            modify_by_id_tool,
            get_content_by_id_tool,
            introduction_agent.as_tool(
                tool_name="modify_introduction",
                tool_description="修改章节的introduction内容。输入：当前introduction内容和用户要求。输出：新的introduction内容（纯文本）"
            ),
            exercise_agent.as_tool(
                tool_name="modify_exercise",
                tool_description="修改或生成练习题。输入：当前exercises内容和用户要求。输出：新的exercise内容（JSON格式的Example对象或数组）"
            ),
            definition_agent.as_tool(
                tool_name="modify_definition",
                tool_description="修改概念定义。输入：当前definition内容和用户要求。输出：新的definition内容（纯文本）"
            ),
            summary_agent.as_tool(
                tool_name="modify_summary",
                tool_description="修改章节总结。输入：当前summary内容和用户要求。输出：新的summary内容（纯文本）"
            ),
        ]
        
        # 加载instructions（可以从prompt文件加载，或使用内联instructions）
        instructions = f"""
你是专门负责修改笔记的Agent。

**关联的笔记本**：
- Notebook ID: {notebook_agent_id}
- 标题: {notebook_agent.notebook_title or '未命名'}

**笔记内容（包含ID标记）**：
{notes_with_ids}

**你的职责**：
1. 读取带ID的notes（notes中包含ID标记，格式：<!-- id: field_abc123 -->）
2. 分析用户请求，识别需要修改的部分
3. 根据修改类型调用相应的工具：
   - 修改introduction → 使用 modify_introduction 工具
   - 修改exercises → 使用 modify_exercise 工具
   - 修改definition → 使用 modify_definition 工具
   - 修改summary → 使用 modify_summary 工具
4. 获取工具返回的新内容后，使用 modify_by_id 工具执行实际的修改操作

**工作流程**：
1. 从notes中识别需要修改的部分及其ID（通过HTML注释 <!-- id: ... -->）
2. 使用 get_content_by_id 获取当前内容
3. 调用相应的修改工具（如 modify_introduction）生成新内容
4. 使用 modify_by_id 工具执行修改（operation_type="update"）

**对于新增操作**：
1. 识别要添加的内容类型和位置（parent_id）
2. 调用相应的修改工具生成新内容
3. 使用 modify_by_id 工具执行新增（operation_type="create", 需要提供content_type和parent_id）

**对于删除操作**：
1. 识别要删除的内容ID
2. 使用 modify_by_id 工具执行删除（operation_type="delete"）

**重要提示**：
- notes中的ID标记格式为：<!-- id: field_abc123 -->
- 使用get_content_by_id查看内容时，会返回包含object_type和field_name的信息
- 修改时使用modify_by_id，传入正确的content_id和field_name
- 新增内容时，确保提供parent_id（父级ID）和content_type（内容类型）
"""
        
        # 初始化BaseAgent
        super().__init__(
            name=f"NotebookModifyAgent_{notebook_agent_id[:8]}",
            instructions=instructions,
            tools=tools,
            mcp_config={},
            agent_type=AgentType.NOTEBOOK_MODIFY,
            parent_agent_id=parent_agent_id,
            DB_PATH=DB_PATH
        )
        
        # 保存notebook_agent_id到数据库
        self.save_to_db()
    
    def _create_modify_by_id_tool(self, notebook_agent_id: str):
        """创建modify_by_id工具，包装以便在工具内部动态加载notebook_agent"""
        from agents import function_tool
        from backend.utils.content_id_utils import locate_by_id, assign_ids_to_new_content
        from backend.models import Example, ConceptBlock
        import json
        from typing import Literal, Optional
        
        # 保存引用以便在闭包中使用
        agent_instance = self
        
        @function_tool
        def modify_by_id(
            content_id: Optional[str] = None,
            operation_type: Literal["create", "update", "delete"] = "update",
            field_name: Optional[str] = None,
            content_type: Optional[str] = None,
            parent_id: Optional[str] = None,
            position: Literal["before", "after", "append"] = "append",
            target_index: Optional[int] = None,
            new_content: Optional[str] = None
        ) -> str:
            """通过ID修改笔记内容（统一的接口，支持create/update/delete）"""
            # 动态加载notebook_agent
            notebook_agent = agent_instance.load_agent_from_db_by_id(notebook_agent_id)
            if not notebook_agent:
                return f"错误：无法找到ID为 {notebook_agent_id} 的NotebookAgent"
            
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
                
                # 执行操作（调用notebook_agent的工具）
                # 实际上，我们应该直接操作notebook_agent的数据结构
                if operation_type == "update":
                    result = locate_by_id(notebook_agent, content_id)
                    if result is None:
                        return f"错误：未找到ID为 '{content_id}' 的内容"
                    
                    content_obj, object_type, existing_field_name = result
                    
                    if existing_field_name:
                        if existing_field_name != field_name:
                            return f"错误：ID '{content_id}' 对应的是 '{existing_field_name}' 字段，不是 '{field_name}' 字段"
                        setattr(content_obj, field_name, new_content)
                        result_msg = f"成功更新 {object_type} 的 {field_name} 字段"
                    else:
                        if not hasattr(content_obj, field_name):
                            return f"错误：{object_type} 对象没有 '{field_name}' 字段"
                        setattr(content_obj, field_name, new_content)
                        result_msg = f"成功更新 {object_type} 的 {field_name} 字段"
                    
                    # 同步数据
                    agent_instance._sync_notes_from_sections(notebook_agent)
                    return result_msg
                
                elif operation_type == "delete":
                    return "删除功能正在实现中"
                
                elif operation_type == "create":
                    result = locate_by_id(notebook_agent, parent_id)
                    if result is None:
                        return f"错误：未找到父ID为 '{parent_id}' 的内容"
                    
                    parent_obj, parent_type, _ = result
                    
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
                    
                    # 同步数据（这会自动清除缓存）
                    agent_instance._sync_notes_from_sections(notebook_agent)
                    return f"成功创建 {content_type}，新ID：{new_id}"
                
                else:
                    return f"错误：不支持的操作类型 '{operation_type}'"
            
            except Exception as e:
                import traceback
                return f"错误：修改操作失败：{str(e)}\n{traceback.format_exc()}"
        
        return modify_by_id
    
    def _create_get_content_by_id_tool(self, notebook_agent_id: str):
        """创建get_content_by_id工具"""
        from agents import function_tool
        from backend.utils.content_id_utils import locate_by_id
        import json
        
        # 保存引用以便在闭包中使用
        agent_instance = self
        
        @function_tool
        def get_content_by_id(content_id: str) -> str:
            """通过ID获取内容信息"""
            # 动态加载notebook_agent
            notebook_agent = agent_instance.load_agent_from_db_by_id(notebook_agent_id)
            if not notebook_agent:
                return json.dumps({
                    "error": f"无法找到ID为 {notebook_agent_id} 的NotebookAgent",
                    "content_id": content_id
                }, ensure_ascii=False)
            
            try:
                result = locate_by_id(notebook_agent, content_id)
                
                if result is None:
                    return json.dumps({
                        "error": f"未找到ID为 '{content_id}' 的内容",
                        "content_id": content_id
                    }, ensure_ascii=False)
                
                content_obj, object_type, field_name = result
                
                info = {
                    "content_id": content_id,
                    "object_type": object_type,
                    "field_name": field_name,
                }
                
                if field_name:
                    if hasattr(content_obj, field_name):
                        info["content"] = getattr(content_obj, field_name)
                    else:
                        info["error"] = f"对象没有 '{field_name}' 字段"
                else:
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
    
    def _sync_notes_from_sections(self, notebook_agent):
        """从结构化数据重新生成 notes，并同步更新 outline"""
        def _sync_outline_from_sections():
            """同步 outline 以匹配当前的 sections"""
            if not notebook_agent.outline:
                from backend.models import Outline
                notebook_agent.outline = Outline(
                    notebook_title=notebook_agent.notebook_title or "",
                    notebook_description=getattr(notebook_agent, 'notebook_description', '') or "",
                    outlines={}
                )
            
            if notebook_agent.notebook_title:
                notebook_agent.outline.notebook_title = notebook_agent.notebook_title
            if hasattr(notebook_agent, 'notebook_description') and notebook_agent.notebook_description:
                notebook_agent.outline.notebook_description = notebook_agent.notebook_description
            
            current_section_titles = set(notebook_agent.sections.keys()) if notebook_agent.sections else set()
            outline_section_titles = set(notebook_agent.outline.outlines.keys()) if notebook_agent.outline and notebook_agent.outline.outlines else set()
            
            for old_title, section in list(notebook_agent.sections.items()):
                if section.section_title != old_title:
                    new_title = section.section_title
                    if old_title in notebook_agent.outline.outlines:
                        notebook_agent.outline.outlines[new_title] = notebook_agent.outline.outlines.pop(old_title)
                    notebook_agent.sections[new_title] = notebook_agent.sections.pop(old_title)
            
            for section_title in current_section_titles:
                if section_title not in outline_section_titles:
                    section = notebook_agent.sections[section_title]
                    description = section.introduction[:200] if section.introduction else f"章节：{section_title}"
                    notebook_agent.outline.outlines[section_title] = description
            
            for section_title in outline_section_titles - current_section_titles:
                notebook_agent.outline.outlines.pop(section_title, None)
        
        # 同步 outline
        _sync_outline_from_sections()
        
        # 使用现有的工具函数从结构化数据生成 markdown
        from backend.tools.utils import generate_markdown_from_agent
        notebook_agent.notes = generate_markdown_from_agent(notebook_agent, include_ids=True)
        
        # 更新 instructions
        from backend.prompts.prompt_loader import load_prompt
        tool_ids = ['modify_by_id', 'get_content_by_id', 'add_content_to_section']
        notebook_agent.instructions = load_prompt(
            "notebook_agent",
            variables={"notes": notebook_agent.notes},
            agent_instance=notebook_agent,  # Pass agent instance to properly generate tools_usage
            tool_ids=tool_ids
        )
        
        # 保存到数据库
        notebook_agent.save_to_db()
        
        # 清除AgentManager缓存，确保API获取最新数据
        try:
            from backend.utils.agent_manager import get_agent_manager
            get_agent_manager().clear_cache(notebook_agent.id)
        except Exception:
            pass  # 如果AgentManager不可用，忽略错误


"""Agent utility functions for information display and markdown generation."""

from typing import Dict, Any, TYPE_CHECKING

# Import only for type checking to avoid circular import
if TYPE_CHECKING:
    from backend.agent.BaseAgent import BaseAgent
    from backend.agent.NoteBookAgent import NoteBookAgent
    from backend.models import Outline, Section


def get_all_agent_info(agent_dict: Dict[str, Any], indent_level: int = 0, max_depth: int = 3) -> str:
    """
    Recursively get all agent info in agent_dict by calling each agent's agent_card() method.
    Maximum depth is 3 levels (0, 1, 2)
    """
    # Ensure agent_dict is not None
    if agent_dict is None:
        agent_dict = {}
    if not agent_dict:
        return "暂无Agent" if indent_level == 0 else ""
    
    # 如果超过最大深度，停止递归
    if indent_level >= max_depth:
        return ""
    
    indent = "  " * indent_level
    agent_info_list = []
    
    for agent_id, agent in agent_dict.items():
        agent_type = type(agent).__name__
        
        # 获取 agent card 信息
        if hasattr(agent, 'agent_card'):
            try:
                card_content = agent.agent_card()
            except Exception as e:
                card_content = f"Error getting agent card: {str(e)}"
        else:
            card_content = f"Agent type: {agent_type}, ID: {agent_id[:8]}"
        
        # 格式化显示 agent card
        # 重要：显示完整的 agent_id，不要截断，因为 TopLevelAgent 需要使用完整 ID 调用 send_message
        if agent_type == "MasterAgent":
            agent_info = f"{indent}- ID: {agent_id}\n{_format_agent_card(card_content, indent + '  ')}"
            agent_info_list.append(agent_info)
            
            # 递归获取子 Agent 信息（最多到第3层）
            # Use _load_sub_agents_dict() if available, otherwise try sub_agent_ids
            child_dict = None
            if hasattr(agent, '_load_sub_agents_dict'):
                try:
                    child_dict = agent._load_sub_agents_dict()
                except:
                    pass
            
            if child_dict and indent_level < max_depth - 1:
                child_info = get_all_agent_info(child_dict, indent_level + 1, max_depth)
                if child_info:
                    agent_info_list.append(child_info)
            elif child_dict:
                # 达到最大深度，只显示数量
                child_count = len(child_dict)
                agent_info_list.append(f"{indent}  ... (还有 {child_count} 个子 Agent，已到达最大深度)")
                    
        elif agent_type == "NoteBookAgent":
            agent_info = f"{indent}- ID: {agent_id}\n{_format_agent_card(card_content, indent + '  ')}"
            agent_info_list.append(agent_info)
        else:
            agent_info = f"{indent}- ID: {agent_id}\n{_format_agent_card(card_content, indent + '  ')}"
            agent_info_list.append(agent_info)
    
    return "\n".join(agent_info_list) if agent_info_list else ""


def _format_agent_card(card_content: Any, indent: str) -> str:
    """
    Format agent card content with proper indentation.
    
    Args:
        card_content: The content from agent_card() method
        indent: Indentation string
    
    Returns:
        Formatted string with proper indentation
    """
    if not card_content:
        return f"{indent}(Empty card)"
    
    # Handle AgentCard objects
    from backend.models import AgentCard
    if isinstance(card_content, AgentCard):
        # Convert AgentCard to string representation
        card_str = f"Title: {card_content.title}\n"
        card_str += f"ID: {card_content.agent_id}\n"
        if card_content.parent_agent_id:
            card_str += f"Parent ID: {card_content.parent_agent_id}\n"
        card_str += f"\nDescription:\n{card_content.description}\n"
        if card_content.outline:
            card_str += f"\nOutline:\n"
            for section_title, section_desc in card_content.outline.items():
                card_str += f"- {section_title}: {section_desc}\n"
        card_content = card_str
    
    # Ensure card_content is a string
    if not isinstance(card_content, str):
        card_content = str(card_content)
    
    # Split by lines and add indentation
    lines = card_content.split('\n')
    indented_lines = [f"{indent}{line}" for line in lines]
    return "\n".join(indented_lines)


def generate_markdown_from_agent(agent: Any, include_ids: bool = True) -> str:
    """
    Generate markdown content from an agent.
    
    - If the agent is a NoteBookAgent, generates markdown from its sections content
    - For other agents, uses their agent_card() method
    
    Args:
        agent: The agent to generate markdown from
        include_ids: Whether to include ID information in XML tags (default: True)
                    For NoteBookAgent, IDs are needed for modify_by_id tool to work
        
    Returns:
        Markdown formatted string
    """
    # Import locally to avoid circular import
    from backend.agent.BaseAgent import BaseAgent
    from backend.agent.NoteBookAgent import NoteBookAgent
    
    if isinstance(agent, NoteBookAgent):
        # For NoteBookAgent, generate markdown from sections
        # IMPORTANT: include_ids should be True by default so AI can use modify_by_id tool
        return _generate_markdown_from_notebook_agent(agent, include_ids=include_ids)
    else:
        # For other agents, use agent_card()
        if hasattr(agent, 'agent_card'):
            try:
                card_content = agent.agent_card()
                # Handle AgentCard objects
                from backend.models import AgentCard
                if isinstance(card_content, AgentCard):
                    # Convert AgentCard to markdown format
                    markdown = f"# Agent Card\n\n"
                    markdown += f"**Title:** {card_content.title}\n\n"
                    markdown += f"**ID:** {card_content.agent_id}\n\n"
                    if card_content.parent_agent_id:
                        markdown += f"**Parent ID:** {card_content.parent_agent_id}\n\n"
                    markdown += f"**Description:**\n\n{card_content.description}\n\n"
                    if card_content.outline:
                        markdown += f"**Outline:**\n\n"
                        for section_title, section_desc in card_content.outline.items():
                            markdown += f"- **{section_title}:** {section_desc}\n"
                    return markdown
                else:
                    # Convert agent card to markdown format (string)
                    return f"# Agent Card\n\n{card_content}"
            except Exception as e:
                return f"# Agent Card\n\nError getting agent card: {str(e)}"
        else:
            agent_type = type(agent).__name__
            return f"# Agent Information\n\n**Type:** {agent_type}\n**ID:** {agent.id}\n"


def _format_example_to_markdown(example, label="例子", include_ids: bool = True) -> str:
    """
    将 Example 对象格式化为 markdown 字符串，支持5种题目类型
    
    Args:
        example: Example 对象
        label: 题目标签（如"例子"、"练习题"）
        include_ids: Whether to include ID information in XML tags (default: True)
        
    Returns:
        Markdown 格式的字符串
    """
    question_type_labels = {
        'multiple_choice': '选择题',
        'fill_blank': '填空题',
        'proof': '证明题',
        'short_answer': '简答题',
        'code': '代码题'
    }
    
    type_label = question_type_labels.get(example.question_type, label) if hasattr(example, 'question_type') and example.question_type else label
    markdown = f"#### {type_label}\n"
    if include_ids and hasattr(example, 'id') and example.id:
        markdown += f"<ExampleItem id=\"{example.id}\">\n"
    else:
        markdown += "<ExampleItem>\n"
    markdown += "\n"
    
    if example.question:
        markdown += f"**题目：**\n"
        if include_ids and hasattr(example, 'question_id') and example.question_id:
            markdown += f"<Question id=\"{example.question_id}\">\n"
        else:
            markdown += "<Question>\n"
        markdown += f"{example.question}\n"
        markdown += "</Question>\n\n"
    
    # 选择题
    if hasattr(example, 'question_type') and example.question_type == 'multiple_choice':
        if hasattr(example, 'options') and example.options:
            markdown += "**选项：**\n\n"
            for i, option in enumerate(example.options):
                option_label = chr(65 + i)  # A, B, C, D
                markdown += f"{option_label}. {option}\n\n"
        if hasattr(example, 'correct_answer') and example.correct_answer:
            markdown += f"**正确答案：** {example.correct_answer}\n\n"
        if hasattr(example, 'explanation') and example.explanation:
            markdown += f"**解释：**\n"
            if include_ids and hasattr(example, 'explanation_id') and example.explanation_id:
                markdown += f"<Explanation id=\"{example.explanation_id}\">\n"
            else:
                markdown += "<Explanation>\n"
            markdown += f"{example.explanation}\n"
            markdown += "</Explanation>\n\n"
    
    # 填空题
    elif hasattr(example, 'question_type') and example.question_type == 'fill_blank':
        if hasattr(example, 'blanks') and example.blanks:
            markdown += "**答案：**\n\n"
            # 支持字典格式（新格式）和数组格式（旧格式兼容）
            if isinstance(example.blanks, dict):
                # 新格式：字典 { "[空1]": "答案1", "[空2]": "答案2" }
                for placeholder, answer in example.blanks.items():
                    markdown += f"{placeholder}：{answer}\n\n"
            elif isinstance(example.blanks, list):
                # 旧格式兼容：数组 ["答案1", "答案2"]
                for i, blank_answer in enumerate(example.blanks):
                    markdown += f"[空{i+1}]：{blank_answer}\n\n"
        if hasattr(example, 'answer') and example.answer:
            markdown += f"**完整答案说明：**\n"
            if include_ids and hasattr(example, 'answer_id') and example.answer_id:
                markdown += f"<Answer id=\"{example.answer_id}\">\n"
            else:
                markdown += "<Answer>\n"
            markdown += f"{example.answer}\n"
            markdown += "</Answer>\n\n"
        if hasattr(example, 'explanation') and example.explanation:
            markdown += f"**解释：**\n"
            if include_ids and hasattr(example, 'explanation_id') and example.explanation_id:
                markdown += f"<Explanation id=\"{example.explanation_id}\">\n"
            else:
                markdown += "<Explanation>\n"
            markdown += f"{example.explanation}\n"
            markdown += "</Explanation>\n\n"
    
    # 证明题
    elif hasattr(example, 'question_type') and example.question_type == 'proof':
        if hasattr(example, 'answer') and example.answer:
            markdown += f"**答案：**\n"
            if include_ids and hasattr(example, 'answer_id') and example.answer_id:
                markdown += f"<Answer id=\"{example.answer_id}\">\n"
            else:
                markdown += "<Answer>\n"
            markdown += f"{example.answer}\n"
            markdown += "</Answer>\n\n"
        if hasattr(example, 'proof') and example.proof:
            markdown += f"**证明步骤：**\n"
            if include_ids and hasattr(example, 'proof_id') and example.proof_id:
                markdown += f"<Proof id=\"{example.proof_id}\">\n"
            else:
                markdown += "<Proof>\n"
            markdown += f"{example.proof}\n"
            markdown += "</Proof>\n\n"
    
    # 简答题
    elif hasattr(example, 'question_type') and example.question_type == 'short_answer':
        if hasattr(example, 'answer') and example.answer:
            markdown += f"**答案：**\n"
            if include_ids and hasattr(example, 'answer_id') and example.answer_id:
                markdown += f"<Answer id=\"{example.answer_id}\">\n"
            else:
                markdown += "<Answer>\n"
            markdown += f"{example.answer}\n"
            markdown += "</Answer>\n\n"
        if hasattr(example, 'explanation') and example.explanation:
            markdown += f"**解释：**\n"
            if include_ids and hasattr(example, 'explanation_id') and example.explanation_id:
                markdown += f"<Explanation id=\"{example.explanation_id}\">\n"
            else:
                markdown += "<Explanation>\n"
            markdown += f"{example.explanation}\n"
            markdown += "</Explanation>\n\n"
    
    # 代码题
    elif hasattr(example, 'question_type') and example.question_type == 'code':
        if hasattr(example, 'code_answer') and example.code_answer:
            markdown += "**代码答案：**\n"
            if include_ids and hasattr(example, 'answer_id') and example.answer_id:
                markdown += f"<Answer id=\"{example.answer_id}\">\n"
            else:
                markdown += "<Answer>\n"
            markdown += "\n```\n"
            markdown += f"{example.code_answer}\n"
            markdown += "```\n"
            markdown += "</Answer>\n\n"
        if hasattr(example, 'explanation') and example.explanation:
            markdown += f"**解释：**\n"
            if include_ids and hasattr(example, 'explanation_id') and example.explanation_id:
                markdown += f"<Explanation id=\"{example.explanation_id}\">\n"
            else:
                markdown += "<Explanation>\n"
            markdown += f"{example.explanation}\n"
            markdown += "</Explanation>\n\n"
    
    # 兼容旧格式（没有 question_type 的情况）
    else:
        if hasattr(example, 'answer') and example.answer:
            markdown += f"**答案：**\n"
            if include_ids and hasattr(example, 'answer_id') and example.answer_id:
                markdown += f"<Answer id=\"{example.answer_id}\">\n"
            else:
                markdown += "<Answer>\n"
            markdown += f"{example.answer}\n"
            markdown += "</Answer>\n\n"
        if hasattr(example, 'proof') and example.proof:
            markdown += f"**证明：**\n"
            if include_ids and hasattr(example, 'proof_id') and example.proof_id:
                markdown += f"<Proof id=\"{example.proof_id}\">\n"
            else:
                markdown += "<Proof>\n"
            markdown += f"{example.proof}\n"
            markdown += "</Proof>\n\n"
    
    markdown += "</ExampleItem>\n\n"
    return markdown


def _generate_markdown_from_notebook_agent(notebook_agent: 'NoteBookAgent', include_ids: bool = True) -> str:
    """
    Generate markdown content from a NoteBookAgent's outline and sections.
    
    Args:
        notebook_agent: The NoteBookAgent instance
        include_ids: Whether to include ID information in XML tags (default: True)
        
    Returns:
        Markdown formatted string with notebook content (with XML tags for IDs when include_ids=True)
    """
    outline = notebook_agent.outline
    sections = notebook_agent.sections
    
    if not sections or not outline:
        # Fallback to notes if no structured data
        if hasattr(notebook_agent, 'notes') and notebook_agent.notes:
            return notebook_agent.notes
        return f"# {notebook_agent.notebook_title or '未命名笔记本'}\n\n"
    
    if not outline.outlines:
        return f"# {outline.notebook_title}\n\n"
    
    markdown_content = f"# {outline.notebook_title}\n\n"
    
    # Generate sections in the order defined in outline
    for section_title in outline.outlines.keys():
        if section_title not in sections:
            continue
            
        section_data = sections[section_title]
        
        # Section 标签（在章节标题之前）
        if include_ids and hasattr(section_data, 'id') and section_data.id:
            markdown_content += f"<Section id=\"{section_data.id}\">\n"
        else:
            markdown_content += "<Section>\n"
        
        # 章节标题
        markdown_content += f"## {section_data.section_title}\n\n"
        
        # 介绍（包含ID）
        if include_ids and hasattr(section_data, 'introduction_id') and section_data.introduction_id:
            markdown_content += f"<Introduction id=\"{section_data.introduction_id}\">\n"
        else:
            markdown_content += "<Introduction>\n"
        markdown_content += f"{section_data.introduction}\n"
        markdown_content += "</Introduction>\n\n"
        
        # 概念块
        for block in section_data.concept_blocks:
            # ConceptBlock 标签（在定义之前）
            if include_ids and hasattr(block, 'id') and block.id:
                markdown_content += f"<ConceptBlock id=\"{block.id}\">\n"
            else:
                markdown_content += "<ConceptBlock>\n"
            
            # 定义（包含ID）- 只有当 definition 不为空时才显示标题和内容
            if block.definition and block.definition.strip():
                markdown_content += f"### **定义**\n"
                if include_ids and hasattr(block, 'definition_id') and block.definition_id:
                    markdown_content += f"<Definition id=\"{block.definition_id}\">\n"
                else:
                    markdown_content += "<Definition>\n"
                markdown_content += f"{block.definition}\n"
                markdown_content += "</Definition>\n\n"
            elif include_ids and hasattr(block, 'definition_id') and block.definition_id:
                # definition 为空但有 ID，创建一个空的 Definition 标签（不显示标题）
                markdown_content += f"<Definition id=\"{block.definition_id}\"></Definition>\n\n"
            
            # 例子（在 ConceptBlock 内部）
            if block.examples:
                markdown_content += "<Examples>\n"
                for example in block.examples:
                    markdown_content += _format_example_to_markdown(example, "例子", include_ids=include_ids)
                markdown_content += "</Examples>\n\n"
            
            # 笔记（在 ConceptBlock 内部）
            for note in block.notes:
                markdown_content += f"**注意：**\n\n{note}\n\n"
            
            # 定理（在 ConceptBlock 内部）
            for theorem in block.theorems:
                markdown_content += f"### 定理\n"
                if include_ids and hasattr(theorem, 'theorem_id') and theorem.theorem_id:
                    markdown_content += f"<Theorem id=\"{theorem.theorem_id}\">\n"
                else:
                    markdown_content += "<Theorem>\n"
                markdown_content += f"{theorem.theorem}\n"
                if theorem.proof:
                    if include_ids and hasattr(theorem, 'proof_id') and theorem.proof_id:
                        markdown_content += f"<Proof id=\"{theorem.proof_id}\">\n"
                    else:
                        markdown_content += "<Proof>\n"
                    markdown_content += f"{theorem.proof}\n"
                    markdown_content += "</Proof>\n"
                markdown_content += "</Theorem>\n\n"
                if theorem.examples:
                    markdown_content += "<Examples>\n"
                    for example in theorem.examples:
                        markdown_content += _format_example_to_markdown(example, "例子", include_ids=include_ids)
                    markdown_content += "</Examples>\n\n"
            
            # 关闭 ConceptBlock 标签
            markdown_content += "</ConceptBlock>\n\n"
        
        # 独立例子
        if section_data.standalone_examples:
            markdown_content += "<Examples>\n"
            for example in section_data.standalone_examples:
                markdown_content += _format_example_to_markdown(example, "例子", include_ids=include_ids)
            markdown_content += "</Examples>\n\n"
        
        # 独立笔记
        for note in section_data.standalone_notes:
            markdown_content += f"**注意：**\n\n{note}\n\n"
        
        # 总结（包含ID）
        markdown_content += f"### 总结\n"
        if include_ids and hasattr(section_data, 'summary_id') and section_data.summary_id:
            markdown_content += f"<Summary id=\"{section_data.summary_id}\">\n"
        else:
            markdown_content += "<Summary>\n"
        markdown_content += f"{section_data.summary}\n"
        markdown_content += "</Summary>\n\n"
        
        # 练习题
        if section_data.exercises:
            markdown_content += "<Exercises>\n"
            for exercise in section_data.exercises:
                markdown_content += _format_example_to_markdown(exercise, "练习题", include_ids=include_ids)
            markdown_content += "</Exercises>\n\n"
        
        # 关闭Section标签
        markdown_content += "</Section>\n\n"
        markdown_content += "---\n\n"
    
    return markdown_content

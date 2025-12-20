"""Agent utility functions for information display and markdown generation."""

from typing import Dict, Any, TYPE_CHECKING

# Import only for type checking to avoid circular import
if TYPE_CHECKING:
    from backend.agent.BaseAgent import BaseAgent
    from backend.agent.NoteBookAgent import NoteBookAgent
    from backend.agent.specialized.NotebookModels import Outline, Section


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
        if agent_type == "MasterAgent":
            agent_info = f"{indent}- ID: {agent_id[:8]}...\n{_format_agent_card(card_content, indent + '  ')}"
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
            agent_info = f"{indent}- ID: {agent_id[:8]}...\n{_format_agent_card(card_content, indent + '  ')}"
            agent_info_list.append(agent_info)
        else:
            agent_info = f"{indent}- ID: {agent_id[:8]}...\n{_format_agent_card(card_content, indent + '  ')}"
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
    from backend.agent.specialized.AgentCard import AgentCard
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


def generate_markdown_from_agent(agent: Any) -> str:
    """
    Generate markdown content from an agent.
    
    - If the agent is a NoteBookAgent, generates markdown from its sections content
    - For other agents, uses their agent_card() method
    
    Args:
        agent: The agent to generate markdown from
        
    Returns:
        Markdown formatted string
    """
    # Import locally to avoid circular import
    from backend.agent.BaseAgent import BaseAgent
    from backend.agent.NoteBookAgent import NoteBookAgent
    
    if isinstance(agent, NoteBookAgent):
        # For NoteBookAgent, generate markdown from sections
        return _generate_markdown_from_notebook_agent(agent)
    else:
        # For other agents, use agent_card()
        if hasattr(agent, 'agent_card'):
            try:
                card_content = agent.agent_card()
                # Handle AgentCard objects
                from backend.agent.specialized.AgentCard import AgentCard
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


def _format_example_to_markdown(example, label="例子") -> str:
    """
    将 Example 对象格式化为 markdown 字符串，支持5种题目类型
    
    Args:
        example: Example 对象
        label: 题目标签（如"例子"、"练习题"）
        
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
    markdown = f"#### {type_label}\n\n"
    
    if example.question:
        markdown += f"**题目：**\n\n{example.question}\n\n"
    
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
            markdown += f"**解释：**\n\n{example.explanation}\n\n"
    
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
            markdown += f"**完整答案说明：**\n\n{example.answer}\n\n"
        if hasattr(example, 'explanation') and example.explanation:
            markdown += f"**解释：**\n\n{example.explanation}\n\n"
    
    # 证明题
    elif hasattr(example, 'question_type') and example.question_type == 'proof':
        if hasattr(example, 'answer') and example.answer:
            markdown += f"**答案：**\n\n{example.answer}\n\n"
        if hasattr(example, 'proof') and example.proof:
            markdown += f"**证明步骤：**\n\n{example.proof}\n\n"
    
    # 简答题
    elif hasattr(example, 'question_type') and example.question_type == 'short_answer':
        if hasattr(example, 'answer') and example.answer:
            markdown += f"**答案：**\n\n{example.answer}\n\n"
        if hasattr(example, 'explanation') and example.explanation:
            markdown += f"**解释：**\n\n{example.explanation}\n\n"
    
    # 代码题
    elif hasattr(example, 'question_type') and example.question_type == 'code':
        if hasattr(example, 'code_answer') and example.code_answer:
            markdown += "**代码答案：**\n\n```\n"
            markdown += f"{example.code_answer}\n"
            markdown += "```\n\n"
        if hasattr(example, 'explanation') and example.explanation:
            markdown += f"**解释：**\n\n{example.explanation}\n\n"
    
    # 兼容旧格式
    else:
        if hasattr(example, 'answer') and example.answer:
            markdown += f"**答案：**\n\n{example.answer}\n\n"
        if hasattr(example, 'proof') and example.proof:
            markdown += f"**证明：**\n\n{example.proof}\n\n"
    
    return markdown


def _generate_markdown_from_notebook_agent(notebook_agent: 'NoteBookAgent') -> str:
    """
    Generate markdown content from a NoteBookAgent's outline and sections.
    
    Args:
        notebook_agent: The NoteBookAgent instance
        
    Returns:
        Markdown formatted string with notebook content
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
        
        # 章节标题
        markdown_content += f"## {section_data.section_title}\n\n"
        
        # 介绍
        markdown_content += f"### 介绍\n\n{section_data.introduction}\n\n"
        
        # 概念块
        for block in section_data.concept_blocks:
            # 定义 - 使用 HTML div 来设置背景色
            markdown_content += f"### **定义**\n\n"
            markdown_content += f"<div class='definition-block'>\n\n"
            markdown_content += f"{block.definition}\n\n"
            markdown_content += f"</div>\n\n"
            
            # 例子
            for example in block.examples:
                markdown_content += _format_example_to_markdown(example, "例子")
            
            # 笔记
            for note in block.notes:
                markdown_content += f"**注意：**\n\n{note}\n\n"
            
            # 定理
            for theorem in block.theorems:
                markdown_content += f"### 定理\n\n{theorem.theorem}\n\n"
                if theorem.proof:
                    markdown_content += f"**证明：**\n\n{theorem.proof}\n\n"
                for example in theorem.examples:
                    markdown_content += _format_example_to_markdown(example, "例子")
        
        # 独立例子
        if section_data.standalone_examples:
            for example in section_data.standalone_examples:
                markdown_content += _format_example_to_markdown(example, "例子")
        
        # 独立笔记
        for note in section_data.standalone_notes:
            markdown_content += f"**注意：**\n\n{note}\n\n"
        
        # 总结
        markdown_content += f"### 总结\n\n{section_data.summary}\n\n"
        
        # 练习题
        if section_data.exercises:
            for exercise in section_data.exercises:
                markdown_content += _format_example_to_markdown(exercise, "练习题")
        
        markdown_content += "\n---\n\n"
    
    return markdown_content

"""NotebookSplitter - Agent for splitting large notebooks into smaller ones."""

from typing import List
from agents import Agent, Runner, AgentOutputSchema
from backend.models import NotebookSplit, SplitPlan


class SplitPlanAgent(Agent):
    """
    Agent for generating a split plan for a large notebook.
    Analyzes the notebook's sections and creates a plan to split it into smaller notebooks.
    """
    
    def __init__(self, notebook_title: str, notebook_description: str, section_titles: List[str], sections_content: dict):
        """
        Initialize SplitPlanAgent.
        
        Args:
            notebook_title: Original notebook title
            notebook_description: Original notebook description
            section_titles: List of section titles in the notebook
            sections_content: Dictionary mapping section titles to their descriptions/content
        """
        self.name = "SplitPlanAgent"
        
        # Build sections info string
        sections_info = []
        for title in section_titles:
            desc = sections_content.get(title, "")
            sections_info.append(f"- **{title}**: {desc[:200]}..." if len(desc) > 200 else f"- **{title}**: {desc}")
        sections_info_str = "\n".join(sections_info)
        
        instructions = f"""
你是一个专业的内容组织专家。请分析一个大型笔记本的内容，将其拆分成多个更小、更易管理的笔记本。

**原始笔记本信息**

- **标题**: {notebook_title}
- **描述**: {notebook_description}
- **章节数量**: {len(section_titles)}
- **章节列表**:
{sections_info_str}

**任务要求**

1. **生成新 MasterAgent 的标题和描述**：
   - 标题应该概括所有拆分后的笔记本的共同主题
   - 描述应该说明这个 MasterAgent 管理的所有笔记本的整体知识范围

2. **将章节合理分配到多个 Notebook**：
   - 章节应该按照主题相关性分组
   - 确保每个 Notebook 都有清晰的知识边界
   - 每个 Notebook 的标题应该反映其包含的章节主题
   - 每个 Notebook 的描述应该说明：
     * 包含哪些知识领域和概念
     * 不包含哪些内容（明确边界）
     * 在整个知识体系中的定位

3. **拆分原则**：
   - 相关主题的章节应该放在同一个 Notebook
   - 基础内容应该在前面的 Notebook
   - 进阶内容应该在后面的 Notebook
   - 每个 Notebook 应该是一个相对独立的知识单元

**输出格式**

{{
  "master_agent_title": "MasterAgent 标题",
  "master_agent_description": "MasterAgent 描述（说明管理的所有笔记本的整体知识范围）",
  "notebooks": [
    {{
      "notebook_title": "Notebook 1 标题",
      "notebook_description": "Notebook 1 描述（说明包含什么知识、不包含什么知识、知识边界）",
      "section_titles": ["章节1", "章节2", ...]
    }},
    {{
      "notebook_title": "Notebook 2 标题",
      "notebook_description": "Notebook 2 描述",
      "section_titles": ["章节3", "章节4", ...]
    }}
  ]
}}

**注意事项**

- 确保所有章节都被分配到某个 Notebook（不能遗漏）
- 每个章节只能属于一个 Notebook（不能重复）
- 每个 Notebook 的描述应该清晰明确，至少 100 字
"""
        
        # Get model settings from config
        from backend.config.model_config import get_model_settings, get_model_name
        model_name = get_model_name()
        model_settings = get_model_settings()
        
        super().__init__(
            name="SplitPlanAgent",
            instructions=instructions,
            output_type=AgentOutputSchema(SplitPlan, strict_json_schema=False),
            model=model_name,  # 显式传递 model 参数
            model_settings=model_settings
        )

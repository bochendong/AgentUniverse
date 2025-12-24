"""Register specialized agents as agent_as_tool."""

from backend.tools.tool_registry import get_tool_registry, AgentAsToolMetadata, ParamInfo
from backend.tools.agent_as_tools.NotebookCreator import (
    OutlineMakerAgent,
    NotebookCreator,
)
from backend.tools.agent_as_tools.refinement_agents import (
    ExerciseRefinementAgent,
    ProofRefinementAgent
)
from backend.tools.agent_as_tools.IntentExtractionAgent import IntentExtractionAgent
from backend.tools.agent_as_tools.OutlineRevisionAgent import OutlineRevisionAgent


def register_all_specialized_agents():
    """Register all specialized agents as agent_as_tool."""
    registry = get_tool_registry()
    
    # Register OutlineMakerAgent
    metadata = AgentAsToolMetadata(
        tool_id="outline_maker_agent",
        name="outline_maker_agent",
        description="从文件生成学习大纲的Agent。接受文件路径，分析文档内容，生成包含5-6个主要章节的详细大纲结构。",
        task="分析文档内容（支持.docx、.md、.txt格式），生成学习大纲，包括笔记本标题、描述和章节结构。每个章节包含详细的描述，说明包含哪些定义、概念、例子、定理等。",
        agent_types=["AsToolAgent"],
        input_params={
            "file_path": ParamInfo(
                type="str",
                description="文件路径（支持.docx、.md、.txt格式）",
                required=True
            ),
        },
        output_type="Outline",
        output_description="返回Outline对象，包含notebook_title（字符串）、notebook_description（字符串，200-300字）和outlines（字典，键为章节名称，值为章节描述字符串，至少100字）",
        agent_class_name="OutlineMakerAgent",
    )
    registry.register_agent_as_tool("outline_maker_agent", OutlineMakerAgent, metadata)
    
    # NoteBookAgentCreator 已被废弃，不再注册
    # 新的架构使用 NotebookCreator（不是 Agent），通过 NotebookCreationStrategies 使用
    # 如果需要，可以在这里注册一个包装 Agent，但目前不需要
    pass
    
    # Register ExerciseRefinementAgent
    metadata = AgentAsToolMetadata(
        tool_id="exercise_refinement_agent",
        name="exercise_refinement_agent",
        description="优化练习题和例子的Agent。识别题目类型，补充缺失内容（选项、答案、证明等），验证题目完整性。",
        task="优化章节中的所有练习题和例子，确保：1) 所有题目都有明确的question_type（multiple_choice、fill_blank、proof、short_answer、code）；2) 选择题有完整的4个选项和正确答案；3) 填空题有完整的blanks字典；4) 证明题有详细的proof步骤；5) 所有题目都有必要的answer和explanation。",
        agent_types=["AsToolAgent"],
        input_params={
            "section": ParamInfo(
                type="Section",
                description="需要优化的Section对象",
                required=True
            ),
            "section_context": ParamInfo(
                type="str",
                description="章节上下文（章节描述、相关定义等），用于帮助生成合理内容",
                required=False
            ),
        },
        output_type="Section",
        output_description="返回优化后的Section对象，包含所有优化后的exercises和examples。所有题目类型都已识别，缺失内容已补充，题目完整性已验证。",
        agent_class_name="ExerciseRefinementAgent",
    )
    registry.register_agent_as_tool("exercise_refinement_agent", ExerciseRefinementAgent, metadata)
    
    # Register ProofRefinementAgent
    metadata = AgentAsToolMetadata(
        tool_id="proof_refinement_agent",
        name="proof_refinement_agent",
        description="优化数学证明的Agent。检查证明完整性，补充中间步骤，添加公式引用，优化证明结构。",
        task="优化章节中的所有证明（包括theorems中的proof和exercises中question_type='proof'的题目），确保：1) 证明有详细的步骤说明（使用'步骤1'、'步骤2'等标记）；2) 明确引用使用的公式、定理、定义（不能只说'根据公式'）；3) 展示关键计算过程，不省略中间步骤；4) 每一步都有清晰的推理说明；5) 使用LaTeX格式表示数学公式。",
        agent_types=["AsToolAgent"],
        input_params={
            "section": ParamInfo(
                type="Section",
                description="需要优化的Section对象",
                required=True
            ),
            "section_context": ParamInfo(
                type="str",
                description="章节上下文（章节描述、相关定义等）",
                required=False
            ),
        },
        output_type="Section",
        output_description="返回优化后的Section对象，包含所有优化后的proof。所有证明都达到教学标准，便于初学者理解。",
        agent_class_name="ProofRefinementAgent",
    )
    registry.register_agent_as_tool("proof_refinement_agent", ProofRefinementAgent, metadata)
    
    # Register IntentExtractionAgent
    metadata = AgentAsToolMetadata(
        tool_id="intent_extraction_agent",
        name="intent_extraction_agent",
        description="意图提取Agent。分析用户请求，确定笔记本创建意图（full_content、enhancement、knowledge_base、outline_first）。",
        task="分析用户的请求和文件内容（如果有），确定用户想要创建什么类型的笔记本。支持4种场景：1) full_content：上传丰满笔记，只需稍作修改；2) enhancement：上传不丰满笔记/PPT，需要添加更多内容；3) knowledge_base：上传论文/条例等，只需记住，不需要练习题；4) outline_first：只有主题描述，需先确认大纲。",
        agent_types=["AsToolAgent"],
        input_params={
            "user_request": ParamInfo(
                type="str",
                description="用户的请求内容",
                required=True
            ),
            "file_path": ParamInfo(
                type="str",
                description="文件路径（可选）",
                required=False
            ),
        },
        output_type="NotebookCreationIntent",
        output_description="返回NotebookCreationIntent对象，包含intent_type（'full_content'、'enhancement'、'knowledge_base'或'outline_first'）、topic_or_theme（主题字符串）、content_richness（'rich'或'sparse'）、requires_exercises（布尔值）、additional_requirements（额外要求字符串，可选）等字段。",
        agent_class_name="IntentExtractionAgent",
    )
    registry.register_agent_as_tool("intent_extraction_agent", IntentExtractionAgent, metadata)
    
    # Register OutlineRevisionAgent
    metadata = AgentAsToolMetadata(
        tool_id="outline_revision_agent",
        name="outline_revision_agent",
        description="大纲修订Agent。根据用户反馈修改现有大纲，支持修改章节标题、描述、添加/删除章节、调整顺序等。",
        task="根据用户的反馈意见修改现有大纲。支持：1) 修改章节标题和描述；2) 添加新章节；3) 删除章节；4) 调整章节顺序；5) 根据反馈重新生成大纲内容。保持大纲的逻辑性和完整性，确保章节之间不重复、不遗漏。",
        agent_types=["AsToolAgent"],
        input_params={
            "current_outline": ParamInfo(
                type="Outline",
                description="当前的大纲对象",
                required=True
            ),
            "user_feedback": ParamInfo(
                type="str",
                description="用户的反馈意见",
                required=True
            ),
        },
        output_type="Outline",
        output_description="返回修改后的Outline对象，包含notebook_title、notebook_description和outlines字典。根据用户反馈进行了相应修改，如果用户没有明确要求修改某些部分，则保持原样。",
        agent_class_name="OutlineRevisionAgent",
    )
    registry.register_agent_as_tool("outline_revision_agent", OutlineRevisionAgent, metadata)


# Auto-register when module is imported
register_all_specialized_agents()

"""Initialize specialized agents as agent_as_tool type in tools database."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database.tools_db import init_tools_db, save_tool


def init_specialized_agents_as_tools():
    """Initialize database with specialized agents as agent_as_tool type."""
    init_tools_db()
    
    # Define all specialized agents with their metadata
    specialized_agents = [
        {
            'id': 'outline_maker_agent',
            'name': 'outline_maker_agent',
            'description': '从文件生成学习大纲的Agent。接受文件路径，分析文档内容，生成包含5-6个主要章节的详细大纲结构。',
            'task': '分析文档内容（支持.docx、.md、.txt格式），生成学习大纲，包括笔记本标题、描述和章节结构。每个章节包含详细的描述，说明包含哪些定义、概念、例子、定理等。',
            'agent_type': 'AsToolAgent',
            'input_params': {
                'file_path': {
                    'type': 'str',
                    'description': '文件路径（支持.docx、.md、.txt格式）',
                    'required': True
                },
            },
            'output_type': 'Outline',
            'output_description': '返回Outline对象，包含notebook_title（字符串）、notebook_description（字符串，200-300字）和outlines（字典，键为章节名称，值为章节描述字符串，至少100字）',
            'agent_class_name': 'OutlineMakerAgent',
        },
        {
            'id': 'notebook_agent_creator',
            'name': 'notebook_agent_creator',
            'description': '根据大纲生成完整笔记本内容的Agent。接受大纲、文件路径等参数，为每个章节生成详细的学习材料。',
            'task': '根据提供的大纲（Outline），为每个章节生成详细内容，包括介绍、概念块（定义+例子+笔记+定理+证明）、总结、练习题。使用ExerciseRefinementAgent和ProofRefinementAgent优化内容质量。',
            'agent_type': 'AsToolAgent',
            'input_params': {
                'outline': {
                    'type': 'Outline',
                    'description': '已确认的大纲对象（包含notebook_title、notebook_description和outlines字典）',
                    'required': True
                },
                'file_path': {
                    'type': 'str',
                    'description': '原始文件路径（用于提取内容）',
                    'required': True
                },
                'output_path': {
                    'type': 'str',
                    'description': '输出markdown文件路径（可选）',
                    'required': False
                },
            },
            'output_type': 'Dict[str, Section]',
            'output_description': '返回一个字典，键为章节标题，值为Section对象。每个Section包含introduction、concept_blocks、standalone_examples、standalone_notes、summary、exercises等字段。',
            'agent_class_name': 'NoteBookAgentCreator',
        },
        {
            'id': 'exercise_refinement_agent',
            'name': 'exercise_refinement_agent',
            'description': '优化练习题和例子的Agent。识别题目类型，补充缺失内容（选项、答案、证明等），验证题目完整性。',
            'task': '优化章节中的所有练习题和例子，确保：1) 所有题目都有明确的question_type（multiple_choice、fill_blank、proof、short_answer、code）；2) 选择题有完整的4个选项和正确答案；3) 填空题有完整的blanks字典；4) 证明题有详细的proof步骤；5) 所有题目都有必要的answer和explanation。',
            'agent_type': 'AsToolAgent',
            'input_params': {
                'section': {
                    'type': 'Section',
                    'description': '需要优化的Section对象',
                    'required': True
                },
                'section_context': {
                    'type': 'str',
                    'description': '章节上下文（章节描述、相关定义等），用于帮助生成合理内容',
                    'required': False
                },
            },
            'output_type': 'Section',
            'output_description': '返回优化后的Section对象，包含所有优化后的exercises和examples。所有题目类型都已识别，缺失内容已补充，题目完整性已验证。',
            'agent_class_name': 'ExerciseRefinementAgent',
        },
        {
            'id': 'proof_refinement_agent',
            'name': 'proof_refinement_agent',
            'description': '优化数学证明的Agent。检查证明完整性，补充中间步骤，添加公式引用，优化证明结构。',
            'task': '优化章节中的所有证明（包括theorems中的proof和exercises中question_type="proof"的题目），确保：1) 证明有详细的步骤说明（使用"步骤1"、"步骤2"等标记）；2) 明确引用使用的公式、定理、定义（不能只说"根据公式"）；3) 展示关键计算过程，不省略中间步骤；4) 每一步都有清晰的推理说明；5) 使用LaTeX格式表示数学公式。',
            'agent_type': 'AsToolAgent',
            'input_params': {
                'section': {
                    'type': 'Section',
                    'description': '需要优化的Section对象',
                    'required': True
                },
                'section_context': {
                    'type': 'str',
                    'description': '章节上下文（章节描述、相关定义等）',
                    'required': False
                },
            },
            'output_type': 'Section',
            'output_description': '返回优化后的Section对象，包含所有优化后的proof。所有证明都达到教学标准，便于初学者理解。',
            'agent_class_name': 'ProofRefinementAgent',
        },
        {
            'id': 'intent_extraction_agent',
            'name': 'intent_extraction_agent',
            'description': '意图提取Agent。分析用户请求，确定笔记本创建意图（full_content、enhancement、knowledge_base、outline_first）。',
            'task': '分析用户的请求和文件内容（如果有），确定用户想要创建什么类型的笔记本。支持4种场景：1) full_content：上传丰满笔记，只需稍作修改；2) enhancement：上传不丰满笔记/PPT，需要添加更多内容；3) knowledge_base：上传论文/条例等，只需记住，不需要练习题；4) outline_first：只有主题描述，需先确认大纲。',
            'agent_type': 'AsToolAgent',
            'input_params': {
                'user_request': {
                    'type': 'str',
                    'description': '用户的请求内容',
                    'required': True
                },
                'file_path': {
                    'type': 'str',
                    'description': '文件路径（可选）',
                    'required': False
                },
            },
            'output_type': 'NotebookCreationIntent',
            'output_description': '返回NotebookCreationIntent对象，包含intent_type（"full_content"、"enhancement"、"knowledge_base"或"outline_first"）、topic_or_theme（主题字符串）、content_richness（"rich"或"sparse"）、requires_exercises（布尔值）、additional_requirements（额外要求字符串，可选）等字段。',
            'agent_class_name': 'IntentExtractionAgent',
        },
        {
            'id': 'outline_revision_agent',
            'name': 'outline_revision_agent',
            'description': '大纲修订Agent。根据用户反馈修改现有大纲，支持修改章节标题、描述、添加/删除章节、调整顺序等。',
            'task': '根据用户的反馈意见修改现有大纲。支持：1) 修改章节标题和描述；2) 添加新章节；3) 删除章节；4) 调整章节顺序；5) 根据反馈重新生成大纲内容。保持大纲的逻辑性和完整性，确保章节之间不重复、不遗漏。',
            'agent_type': 'AsToolAgent',
            'input_params': {
                'current_outline': {
                    'type': 'Outline',
                    'description': '当前的大纲对象',
                    'required': True
                },
                'user_feedback': {
                    'type': 'str',
                    'description': '用户的反馈意见',
                    'required': True
                },
            },
            'output_type': 'Outline',
            'output_description': '返回修改后的Outline对象，包含notebook_title、notebook_description和outlines字典。根据用户反馈进行了相应修改，如果用户没有明确要求修改某些部分，则保持原样。',
            'agent_class_name': 'OutlineRevisionAgent',
        },
    ]
    
    # Save all specialized agents as agent_as_tool type
    for agent in specialized_agents:
        save_tool(
            tool_id=agent['id'],
            name=agent['name'],
            description=agent['description'],
            task=agent['task'],
            agent_type=agent['agent_type'],
            input_params=agent['input_params'],
            output_type=agent['output_type'],
            output_description=agent.get('output_description'),
            tool_type='agent_as_tool',
            agent_class_name=agent['agent_class_name'],
        )
        print(f"Saved agent as tool: {agent['name']} ({agent['agent_class_name']})")
    
    print(f"Successfully initialized {len(specialized_agents)} specialized agents as tools")


if __name__ == '__main__':
    init_specialized_agents_as_tools()

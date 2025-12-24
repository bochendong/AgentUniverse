"""IntentExtractionAgent - 意图提取Agent，分析用户请求并确定创建意图"""

from typing import Optional
from agents import Agent, Runner, AgentOutputSchema
from backend.models import NotebookCreationIntent


class IntentExtractionAgent(Agent):
    """
    意图提取Agent - 分析用户请求，确定笔记本创建意图
    
    支持4种场景：
    1. full_content: 上传丰满笔记，只需稍作修改
    2. enhancement: 上传不丰满笔记/PPT，需要添加更多内容
    3. knowledge_base: 上传论文/条例等，只需记住，不需要练习题
    4. outline_first: 只有主题描述，需先确认大纲
    """
    
    def __init__(self, user_request: str, file_path: Optional[str] = None):
        """
        初始化意图提取Agent
        
        Args:
            user_request: 用户的请求内容
            file_path: 文件路径（如果有）
        """
        self.name = "IntentExtractionAgent"
        self.user_request = user_request
        self.file_path = file_path
        
        # 读取文件内容（如果有）
        file_content_preview = ""
        if file_path:
            try:
                from backend.tools.agent_as_tools.section_creators.utils import get_file_content
                full_content = get_file_content(file_path)
                # 只取前1000字符作为预览，避免上下文过长
                file_content_preview = full_content[:1000]
                if len(full_content) > 1000:
                    file_content_preview += f"\n\n[文件内容较长，已截取前1000字符，总长度: {len(full_content)}字符]"
            except Exception as e:
                file_content_preview = f"[无法读取文件: {str(e)}]"
        
        instructions = f"""
你是一个专业的意图分析专家。你的任务是分析用户的请求，确定用户想要创建什么类型的笔记本，以及如何创建。

**用户请求**
{user_request}

**文件信息**（如果有）
{'文件路径: ' + file_path if file_path else '无文件上传'}

**文件内容预览**（如果有）
{file_content_preview if file_content_preview else '无文件内容'}

**四种创建场景**

1. **full_content（丰满内容）**：
   - 用户上传了文件，且文件内容比较丰满（包含定义、例子、证明、练习题等完整内容）
   - 只需要对现有内容稍作修改、格式化和优化即可
   - 用户可能说："创建笔记"、"根据这个文件创建笔记本"等
   - 特征：文件内容完整，包含大量结构化的学习材料

2. **enhancement（内容增强）**：
   - 用户上传了文件，但内容不够丰满（可能是PPT、简要笔记、只有大纲等）
   - 需要大量补充内容：添加更多例子、详细解释、练习题等
   - 用户可能说："帮我完善这个笔记"、"这个PPT内容太简单，需要补充"、"根据这个大纲生成详细内容"等
   - 特征：文件内容稀疏，缺少详细说明、例子或练习题

3. **knowledge_base（知识库）**：
   - 用户上传了论文、条例、生活内容、实时资讯等
   - 只需要记住并创建agent，不需要练习题
   - 内容应该以知识记录为主，而不是学习材料
   - 用户可能说："记住这篇论文"、"保存这个条例"、"创建知识库"、"不需要练习题"等
   - 特征：用户明确表示不需要练习，或内容类型不适合练习（论文、条例等）

4. **outline_first（大纲优先）**：
   - 用户没有上传文件，只有主题描述
   - 需要先草拟大纲，等用户确认后再生成
   - 用户可能说："创建一个关于Python的笔记"、"我想学群论，帮我创建笔记本"等
   - 特征：没有文件，只有主题/话题描述

**分析要求**

1. **确定intent_type**：根据上述场景判断属于哪一种
2. **提取topic_or_theme**：如果是outline_first，提取主题；如果有文件，尝试从文件名和内容提取主题
3. **评估content_richness**：如果有文件，评估内容是"rich"（丰满）还是"sparse"（稀疏）
4. **判断requires_exercises**：默认True，除非用户明确表示不需要或属于知识库类型
5. **记录additional_requirements**：用户的额外要求或特殊说明

**输出要求**

请仔细分析用户请求和文件内容，输出一个准确的NotebookCreationIntent对象。
"""
        
        # Get model settings from config
        from backend.config.model_config import get_model_settings, get_model_name
        model_name = get_model_name()  # 确保获取正确的模型名称
        model_settings = get_model_settings(model_name=model_name)  # 显式传递模型名称
        
        # Debug: Print model being used
        # 检查 ModelSettings 的所有属性
        print(f"[IntentExtractionAgent] ModelSettings 属性: {dir(model_settings)}")
        model_attr = getattr(model_settings, 'model', None) or getattr(model_settings, '_model', None) or 'N/A'
        print(f"[IntentExtractionAgent] 使用模型: {model_attr} (期望: {model_name})")
        verbosity_attr = getattr(model_settings, 'verbosity', None) or getattr(model_settings, '_verbosity', None) or 'N/A'
        print(f"[IntentExtractionAgent] verbosity: {verbosity_attr}")
        
        # ModelSettings 不接受 model 参数，模型名称通过 Agent 的 model 参数传递
        # 这里只需要确保 verbosity 正确即可
        
        # 同时显式传递 model 参数，确保 Agent SDK 使用正确的模型
        from backend.config.model_config import get_model_name
        explicit_model = get_model_name()
        
        super().__init__(
            name="IntentExtractionAgent",
            instructions=instructions,
            output_type=AgentOutputSchema(NotebookCreationIntent, strict_json_schema=False),
            model=explicit_model,  # 显式传递 model 参数
            model_settings=model_settings
        )
        
        # 验证 Agent 实际使用的模型
        if hasattr(self, 'model'):
            print(f"[IntentExtractionAgent] Agent.model 属性: {self.model}")
        if hasattr(self, 'model_settings') and self.model_settings:
            actual_model = getattr(self.model_settings, 'model', None) or getattr(self.model_settings, '_model', None)
            print(f"[IntentExtractionAgent] Agent.model_settings.model: {actual_model}")

"""Notebook data models - 提取到单独文件以避免循环导入"""

from typing import Optional, List, Literal, Dict
from pydantic import BaseModel, ConfigDict


class Outline(BaseModel):
    """大纲结构"""
    model_config = ConfigDict(strict=False)
    
    notebook_title: str
    notebook_description: str  # 描述笔记本包含什么知识和不包含什么知识，确定笔记本的边界
    outlines: dict[str, str]


class Example(BaseModel):
    """
    例子及其答案、证明
    支持5种题目类型：选择题、填空题、证明题、简答题、代码题
    """
    model_config = ConfigDict(strict=False)
    
    # 题目基本信息
    question_type: Optional[Literal["multiple_choice", "fill_blank", "proof", "short_answer", "code"]] = None  # 题目类型
    question: str  # 题目/例子内容（必需）
    
    # 通用字段
    answer: Optional[str] = None  # 答案内容（通用，用于简答题、填空题等）
    explanation: Optional[str] = None  # 解释（用于选择题、填空题、简答题）
    proof: Optional[str] = None  # 证明步骤（用于证明题）
    
    # 选择题专用字段
    options: Optional[List[str]] = None  # 选项列表（选择题用，4个选项）
    correct_answer: Optional[str] = None  # 正确答案（选择题用，如 "A", "B", "C", "D"）
    
    # 填空题专用字段
    blanks: Optional[Dict[str, str]] = None  # 填空题答案字典（填空题用）
    # 格式：{"[空1]": "答案1", "[空2]": "答案2", ...} 或 {"blank1": "答案1", "blank2": "答案2", ...}
    # 键必须与 question 中的占位符完全匹配
    
    # 代码题专用字段
    code_answer: Optional[str] = None  # 代码答案（代码题用）


class Theorem(BaseModel):
    """定理及其证明"""
    model_config = ConfigDict(strict=False)
    theorem: str  # 定理内容（必需）
    proof: Optional[str] = None  # 证明内容（可选）
    examples: list[Example] = []  # 该定理相关的例子（可选）


class ConceptBlock(BaseModel):
    """概念块：一个定义及其相关的例子、笔记、定理等"""
    model_config = ConfigDict(strict=False)
    definition: str  # 定义（必需）
    examples: list[Example] = []  # 相关例子列表
    notes: list[str] = []  # 相关笔记/注意点（可选）
    theorems: list[Theorem] = []  # 相关定理列表


class Section(BaseModel):
    """章节结构"""
    model_config = ConfigDict(strict=False)
    section_title: str
    introduction: str  # 介绍
    concept_blocks: list[ConceptBlock]  # 概念块列表
    standalone_examples: list[Example] = []  # 独立例子（可选）
    standalone_notes: list[str] = []  # 独立笔记（可选）
    summary: str  # 总结
    exercises: list[Example] = []  # 练习题


class NotebookCreationIntent(BaseModel):
    """笔记本创建意图"""
    model_config = ConfigDict(strict=False)
    
    intent_type: Literal[
        "full_content",      # 场景1: 丰满笔记，只需稍作修改
        "enhancement",       # 场景2: 不丰满笔记，需要添加内容
        "knowledge_base",    # 场景3: 论文/条例等，不需要练习题
        "outline_first"      # 场景4: 只有主题，需先确认大纲
    ]
    
    # 通用信息
    file_path: Optional[str] = None  # 文件路径（如果有）
    user_description: str  # 用户描述或请求内容
    topic_or_theme: Optional[str] = None  # 主题（场景4时使用）
    
    # 意图特定信息
    content_richness: Optional[Literal["rich", "sparse"]] = None  # 内容丰满度（场景1、2）
    requires_exercises: Optional[bool] = True  # 是否需要练习题（场景3）
    outline_confirmed: Optional[bool] = False  # 大纲是否已确认（场景4）
    
    # 附加要求
    additional_requirements: Optional[str] = None  # 用户的额外要求

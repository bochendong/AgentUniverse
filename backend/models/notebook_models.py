"""Notebook content structure models - 笔记本内容结构模型"""

from __future__ import annotations

from typing import Optional, List, Literal, Dict
from pydantic import BaseModel, ConfigDict


class Example(BaseModel):
    """
    例子及其答案、证明
    支持5种题目类型：选择题、填空题、证明题、简答题、代码题
    """
    model_config = ConfigDict(strict=False)
    
    # ID字段（用于精确定位，支持向后兼容）
    id: Optional[str] = None  # 唯一ID，如 "example_abc123"
    question_id: Optional[str] = None  # question字段的ID
    answer_id: Optional[str] = None  # answer字段的ID
    explanation_id: Optional[str] = None  # explanation字段的ID
    proof_id: Optional[str] = None  # proof字段的ID
    
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
    
    # ID字段（用于精确定位，支持向后兼容）
    id: Optional[str] = None  # 唯一ID，如 "theorem_def456"
    theorem_id: Optional[str] = None  # theorem字段的ID
    proof_id: Optional[str] = None  # proof字段的ID
    
    theorem: str  # 定理内容（必需）
    proof: Optional[str] = None  # 证明内容（可选）
    examples: List[Example] = []  # 该定理相关的例子（可选）


class ConceptBlock(BaseModel):
    """概念块：一个定义及其相关的例子、笔记、定理等"""
    model_config = ConfigDict(strict=False)
    
    # ID字段（用于精确定位，支持向后兼容）
    id: Optional[str] = None  # 唯一ID，如 "concept_block_ghi789"
    definition_id: Optional[str] = None  # definition字段的ID
    
    definition: str  # 定义（必需）
    examples: List[Example] = []  # 相关例子列表
    notes: List[str] = []  # 相关笔记/注意点（可选）
    theorems: List[Theorem] = []  # 相关定理列表


class Section(BaseModel):
    """章节结构"""
    model_config = ConfigDict(strict=False)
    
    # ID字段（用于精确定位，支持向后兼容）
    id: Optional[str] = None  # 唯一ID，如 "section_jkl012"
    section_title_id: Optional[str] = None  # section_title字段的ID
    introduction_id: Optional[str] = None  # introduction字段的ID
    summary_id: Optional[str] = None  # summary字段的ID
    
    section_title: str
    introduction: str  # 介绍
    concept_blocks: List[ConceptBlock]  # 概念块列表
    standalone_examples: List[Example] = []  # 独立例子（可选）
    standalone_notes: List[str] = []  # 独立笔记/注意点（可选）
    summary: str  # 总结
    exercises: List[Example] = []  # 练习题


class Outline(BaseModel):
    """大纲结构"""
    model_config = ConfigDict(strict=False)
    
    notebook_title: str
    notebook_description: str  # 描述笔记本包含什么知识和不包含什么知识，确定笔记本的边界
    outlines: Dict[str, str]

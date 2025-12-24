"""Content ID utilities for notebook modification system.

This module provides functions for generating and managing content IDs,
which are used to precisely locate and modify specific parts of notebook content.
"""

import uuid
from typing import Optional, Tuple, Any, Dict
from backend.models import (
    Section, ConceptBlock, Example, Theorem
)


def generate_content_id(content_type: str, parent_id: Optional[str] = None) -> str:
    """
    生成内容ID
    
    格式：{content_type}_{short_uuid}
    如果提供parent_id，格式：{parent_id}_{content_type}_{short_uuid}
    
    Args:
        content_type: 内容类型（section, concept_block, example, field等）
        parent_id: 父级ID（可选，用于生成层级ID）
    
    Returns:
        唯一ID字符串
    
    示例：
        generate_content_id("section")  # "section_abc12345"
        generate_content_id("field", "section_abc12345")  # "section_abc12345_field_def67890"
    """
    short_uuid = str(uuid.uuid4())[:8]
    if parent_id:
        return f"{parent_id}_{content_type}_{short_uuid}"
    return f"{content_type}_{short_uuid}"


def locate_by_id(notebook_agent: Any, content_id: str) -> Optional[Tuple[Any, str, Optional[str]]]:
    """
    通过ID定位内容
    
    Args:
        notebook_agent: NoteBookAgent 实例
        content_id: 内容ID（如 "section_abc123", "field_def456"）
    
    Returns:
        (content_object, object_type, field_name) 元组，如果找到
        - content_object: 找到的内容对象（Section, ConceptBlock, Example等）
        - object_type: 对象类型（"section", "concept_block", "example", "theorem"等）
        - field_name: 字段名（如果是字段ID，否则为None）
        None 如果未找到
    """
    if not hasattr(notebook_agent, 'sections') or not notebook_agent.sections:
        return None
    
    # 遍历所有 sections
    for section_title, section in notebook_agent.sections.items():
        # 检查 section ID
        if hasattr(section, 'id') and section.id == content_id:
            return (section, 'section', None)
        
        # 检查 section 的字段ID
        for field_name in ['section_title', 'introduction', 'summary']:
            field_id_attr = f"{field_name}_id"
            if hasattr(section, field_id_attr) and getattr(section, field_id_attr) == content_id:
                return (section, 'section', field_name)
        
        # 检查 concept_blocks
        if hasattr(section, 'concept_blocks'):
            for cb in section.concept_blocks:
                # 检查 concept_block ID
                if hasattr(cb, 'id') and cb.id == content_id:
                    return (cb, 'concept_block', None)
                
                # 检查 definition_id
                if hasattr(cb, 'definition_id') and cb.definition_id == content_id:
                    return (cb, 'concept_block', 'definition')
                
                # 检查 examples
                if hasattr(cb, 'examples'):
                    for ex in cb.examples:
                        # 检查 example ID
                        if hasattr(ex, 'id') and ex.id == content_id:
                            return (ex, 'example', None)
                        
                        # 检查 example 的字段ID
                        for ex_field in ['question', 'answer', 'explanation', 'proof']:
                            field_id_attr = f"{ex_field}_id"
                            if hasattr(ex, field_id_attr) and getattr(ex, field_id_attr) == content_id:
                                return (ex, 'example', ex_field)
                
                # 检查 theorems
                if hasattr(cb, 'theorems'):
                    for th in cb.theorems:
                        # 检查 theorem ID
                        if hasattr(th, 'id') and th.id == content_id:
                            return (th, 'theorem', None)
                        
                        # 检查 theorem 的字段ID
                        if hasattr(th, 'theorem_id') and th.theorem_id == content_id:
                            return (th, 'theorem', 'theorem')
                        if hasattr(th, 'proof_id') and th.proof_id == content_id:
                            return (th, 'theorem', 'proof')
        
        # 检查 standalone_examples
        if hasattr(section, 'standalone_examples'):
            for ex in section.standalone_examples:
                if hasattr(ex, 'id') and ex.id == content_id:
                    return (ex, 'example', None)
                for ex_field in ['question', 'answer', 'explanation', 'proof']:
                    field_id_attr = f"{ex_field}_id"
                    if hasattr(ex, field_id_attr) and getattr(ex, field_id_attr) == content_id:
                        return (ex, 'example', ex_field)
        
        # 检查 exercises
        if hasattr(section, 'exercises'):
            for ex in section.exercises:
                if hasattr(ex, 'id') and ex.id == content_id:
                    return (ex, 'example', None)
                for ex_field in ['question', 'answer', 'explanation', 'proof']:
                    field_id_attr = f"{ex_field}_id"
                    if hasattr(ex, field_id_attr) and getattr(ex, field_id_attr) == content_id:
                        return (ex, 'example', ex_field)
    
    return None


def ensure_ids(notebook_agent: Any) -> None:
    """
    确保所有内容都有ID（用于向后兼容，为旧数据生成ID）
    
    遍历notebook_agent的所有内容，为缺少ID的部分生成ID。
    
    Args:
        notebook_agent: NoteBookAgent 实例
    """
    if not hasattr(notebook_agent, 'sections') or not notebook_agent.sections:
        return
    
    notebook_id = notebook_agent.id if hasattr(notebook_agent, 'id') else None
    
    for section_title, section in notebook_agent.sections.items():
        # 为 section 生成 ID
        if not hasattr(section, 'id') or not section.id:
            section.id = generate_content_id("section", notebook_id)
        
        # 为 section 的字段生成 ID
        section_id = section.id
        
        if not hasattr(section, 'section_title_id') or not section.section_title_id:
            section.section_title_id = generate_content_id("field", section_id)
        
        if not hasattr(section, 'introduction_id') or not section.introduction_id:
            section.introduction_id = generate_content_id("field", section_id)
        
        if not hasattr(section, 'summary_id') or not section.summary_id:
            section.summary_id = generate_content_id("field", section_id)
        
        # 为 concept_blocks 生成 ID
        if hasattr(section, 'concept_blocks'):
            for cb in section.concept_blocks:
                if not hasattr(cb, 'id') or not cb.id:
                    cb.id = generate_content_id("concept_block", section_id)
                
                cb_id = cb.id
                
                if not hasattr(cb, 'definition_id') or not cb.definition_id:
                    cb.definition_id = generate_content_id("field", cb_id)
                
                # 为 examples 生成 ID
                if hasattr(cb, 'examples'):
                    for ex in cb.examples:
                        if not hasattr(ex, 'id') or not ex.id:
                            ex.id = generate_content_id("example", cb_id)
                        
                        ex_id = ex.id
                        for field in ['question', 'answer', 'explanation', 'proof']:
                            field_id_attr = f"{field}_id"
                            if not hasattr(ex, field_id_attr) or not getattr(ex, field_id_attr):
                                setattr(ex, field_id_attr, generate_content_id("field", ex_id))
                
                # 为 theorems 生成 ID
                if hasattr(cb, 'theorems'):
                    for th in cb.theorems:
                        if not hasattr(th, 'id') or not th.id:
                            th.id = generate_content_id("theorem", cb_id)
                        
                        th_id = th.id
                        
                        if not hasattr(th, 'theorem_id') or not th.theorem_id:
                            th.theorem_id = generate_content_id("field", th_id)
                        
                        if not hasattr(th, 'proof_id') or not th.proof_id:
                            th.proof_id = generate_content_id("field", th_id)
                        
                        # 为 theorem 的 examples 生成 ID
                        if hasattr(th, 'examples'):
                            for ex in th.examples:
                                if not hasattr(ex, 'id') or not ex.id:
                                    ex.id = generate_content_id("example", th_id)
                                
                                ex_id = ex.id
                                for field in ['question', 'answer', 'explanation', 'proof']:
                                    field_id_attr = f"{field}_id"
                                    if not hasattr(ex, field_id_attr) or not getattr(ex, field_id_attr):
                                        setattr(ex, field_id_attr, generate_content_id("field", ex_id))
        
        # 为 standalone_examples 生成 ID
        if hasattr(section, 'standalone_examples'):
            for ex in section.standalone_examples:
                if not hasattr(ex, 'id') or not ex.id:
                    ex.id = generate_content_id("example", section_id)
                
                ex_id = ex.id
                for field in ['question', 'answer', 'explanation', 'proof']:
                    field_id_attr = f"{field}_id"
                    if not hasattr(ex, field_id_attr) or not getattr(ex, field_id_attr):
                        setattr(ex, field_id_attr, generate_content_id("field", ex_id))
        
        # 为 exercises 生成 ID
        if hasattr(section, 'exercises'):
            for ex in section.exercises:
                if not hasattr(ex, 'id') or not ex.id:
                    ex.id = generate_content_id("example", section_id)
                
                ex_id = ex.id
                for field in ['question', 'answer', 'explanation', 'proof']:
                    field_id_attr = f"{field}_id"
                    if not hasattr(ex, field_id_attr) or not getattr(ex, field_id_attr):
                        setattr(ex, field_id_attr, generate_content_id("field", ex_id))


def assign_ids_to_new_content(content_obj: Any, parent_id: Optional[str] = None, content_type: Optional[str] = None) -> None:
    """
    为新创建的内容对象分配ID
    
    Args:
        content_obj: 内容对象（Section, ConceptBlock, Example, Theorem等）
        parent_id: 父级ID（可选）
        content_type: 内容类型（可选，如果不提供则从对象类型推断）
    """
    if content_type is None:
        content_type = type(content_obj).__name__.lower()
        # 转换为下划线格式
        content_type = ''.join(['_' + c.lower() if c.isupper() else c for c in content_type]).lstrip('_')
    
    # 为对象本身生成ID
    if not hasattr(content_obj, 'id') or not content_obj.id:
        content_obj.id = generate_content_id(content_type, parent_id)
    
    obj_id = content_obj.id
    
    # 根据对象类型分配字段ID
    if isinstance(content_obj, Section):
        if not content_obj.section_title_id:
            content_obj.section_title_id = generate_content_id("field", obj_id)
        if not content_obj.introduction_id:
            content_obj.introduction_id = generate_content_id("field", obj_id)
        if not content_obj.summary_id:
            content_obj.summary_id = generate_content_id("field", obj_id)
        
        # 递归处理 concept_blocks, standalone_examples, exercises
        for cb in content_obj.concept_blocks:
            assign_ids_to_new_content(cb, obj_id, "concept_block")
        for ex in content_obj.standalone_examples:
            assign_ids_to_new_content(ex, obj_id, "example")
        for ex in content_obj.exercises:
            assign_ids_to_new_content(ex, obj_id, "example")
    
    elif isinstance(content_obj, ConceptBlock):
        if not content_obj.definition_id:
            content_obj.definition_id = generate_content_id("field", obj_id)
        
        for ex in content_obj.examples:
            assign_ids_to_new_content(ex, obj_id, "example")
        for th in content_obj.theorems:
            assign_ids_to_new_content(th, obj_id, "theorem")
    
    elif isinstance(content_obj, Example):
        for field in ['question', 'answer', 'explanation', 'proof']:
            field_id_attr = f"{field}_id"
            if not hasattr(content_obj, field_id_attr) or not getattr(content_obj, field_id_attr):
                setattr(content_obj, field_id_attr, generate_content_id("field", obj_id))
    
    elif isinstance(content_obj, Theorem):
        if not content_obj.theorem_id:
            content_obj.theorem_id = generate_content_id("field", obj_id)
        if not content_obj.proof_id:
            content_obj.proof_id = generate_content_id("field", obj_id)
        
        for ex in content_obj.examples:
            assign_ids_to_new_content(ex, obj_id, "example")


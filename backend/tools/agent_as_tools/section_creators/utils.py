"""Section Creator Utilities - 工具函数"""

import os
from typing import Optional, Tuple, Literal


def get_file_content(file_path: str) -> str:
    """读取文件内容，支持多种文件格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件内容字符串
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 路径不是文件
        IOError: 读取失败
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    if not os.path.isfile(file_path):
        raise ValueError(f"路径不是文件: {file_path}")
    
    # 根据文件扩展名选择读取方式
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.docx':
        try:
            from docx import Document
            doc = Document(file_path)
            content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return content
        except ImportError:
            raise ImportError("需要安装 python-docx 库来读取 .docx 文件: pip install python-docx")
        except Exception as e:
            raise IOError(f"读取 .docx 文件失败: {file_path}, 错误: {str(e)}")
    
    elif file_ext in ['.md', '.txt', '.markdown']:
        # 读取文本文件
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
                return content
            except Exception as e:
                raise IOError(f"读取文件失败（编码问题）: {file_path}, 错误: {str(e)}")
        except Exception as e:
            raise IOError(f"读取文件失败: {file_path}, 错误: {str(e)}")
    
    elif file_ext == '.pdf':
        # PDF 文件（未来扩展）
        raise NotImplementedError("PDF 文件支持尚未实现")
    
    elif file_ext in ['.pptx', '.ppt']:
        # PPT 文件（未来扩展）
        raise NotImplementedError("PPT 文件支持尚未实现")
    
    else:
        raise ValueError(f"不支持的文件格式: {file_ext}")


def detect_file_type(file_path: Optional[str]) -> Optional[Literal['docx', 'md', 'txt', 'pdf', 'pptx', 'ppt']]:
    """检测文件类型
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件类型字符串，如果文件不存在或无法检测则返回 None
    """
    if not file_path:
        return None
    
    if not os.path.exists(file_path):
        return None
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.docx':
        return 'docx'
    elif file_ext in ['.md', '.markdown']:
        return 'md'
    elif file_ext == '.txt':
        return 'txt'
    elif file_ext == '.pdf':
        return 'pdf'
    elif file_ext in ['.pptx', '.ppt']:
        return 'pptx'
    else:
        return None


def assess_content_quality(content: str) -> Tuple[Literal['well_formed', 'sparse', 'unknown'], float]:
    """评估内容质量
    
    根据内容的结构、完整性、详细程度等评估内容质量
    
    Args:
        content: 文件内容
        
    Returns:
        (质量等级, 质量分数 0-1)
        - well_formed: 内容完善，结构清晰，有详细定义和例子
        - sparse: 内容稀疏，只有大纲或关键词
        - unknown: 无法确定
    """
    if not content or len(content.strip()) == 0:
        return ('unknown', 0.0)
    
    content_lower = content.lower()
    
    # 检查指标
    has_definitions = any(keyword in content_lower for keyword in ['定义', 'definition', '什么是', '是指'])
    has_examples = any(keyword in content_lower for keyword in ['例子', 'example', '例如', '比如'])
    has_proofs = any(keyword in content_lower for keyword in ['证明', 'proof', '推导', '证明步骤'])
    has_exercises = any(keyword in content_lower for keyword in ['练习', 'exercise', '题目', '习题'])
    
    # 检查结构标记
    has_sections = any(marker in content for marker in ['##', '###', '章节', 'section'])
    has_lists = content.count('\n-') + content.count('\n*') + content.count('\n1.') > 5
    
    # 计算质量分数
    score = 0.0
    if has_definitions:
        score += 0.2
    if has_examples:
        score += 0.2
    if has_proofs:
        score += 0.2
    if has_exercises:
        score += 0.15
    if has_sections:
        score += 0.15
    if has_lists:
        score += 0.1
    
    # 检查内容长度（相对指标）
    if len(content) > 5000:
        score += 0.1
    elif len(content) > 2000:
        score += 0.05
    
    # 判断质量等级
    if score >= 0.7:
        return ('well_formed', min(score, 1.0))
    elif score >= 0.3:
        return ('sparse', score)
    else:
        return ('unknown', score)


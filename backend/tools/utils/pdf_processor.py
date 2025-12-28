"""PDF处理工具 - 使用agents库处理PDF文件"""

import os
import base64
import asyncio
from typing import Optional
from agents import Agent, Runner
from backend.config.model_config import get_model_name, get_model_settings


async def extract_pdf_content(file_path: str) -> str:
    """
    使用agents库的input_file功能提取PDF内容
    
    参考 openai-cookbook/Pdf.md 的实现方式
    
    Args:
        file_path: PDF文件路径（可以是绝对路径、相对路径或文件名）
        
    Returns:
        PDF内容的文本表示
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件不是PDF格式
        Exception: 提取失败
    """
    # 解析文件路径（支持相对路径和仅文件名）
    from backend.tools.agent_as_tools.section_creators.utils import _resolve_file_path
    resolved_path = _resolve_file_path(file_path)
    
    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"PDF文件不存在: {file_path} (解析后: {resolved_path})")
    
    if not os.path.isfile(resolved_path):
        raise ValueError(f"路径不是文件: {file_path} (解析后: {resolved_path})")
    
    file_ext = os.path.splitext(resolved_path)[1].lower()
    if file_ext != '.pdf':
        raise ValueError(f"文件不是PDF格式: {file_ext}")
    
    try:
        # 读取PDF文件并转换为base64
        with open(resolved_path, "rb") as f:
            pdf_bytes = f.read()
        
        b64_file = base64.b64encode(pdf_bytes).decode("utf-8")
        filename = os.path.basename(resolved_path)
        
        # 创建Agent用于提取PDF内容
        model_name = get_model_name()
        model_settings = get_model_settings()
        
        pdf_agent = Agent(
            name="PDFExtractor",
            instructions="""你是一个专业的PDF文档分析专家。你的任务是提取PDF文件中的文本内容，并组织成结构化的格式。

请仔细阅读PDF文件，提取以下内容：
1. 标题和作者信息
2. 摘要（Abstract）
3. 主要章节和内容
4. 关键概念、定义、定理
5. 实验方法和结果
6. 结论

请将提取的内容组织成清晰的文本格式，保持原有的结构和层次。""",
            model=model_name,
            model_settings=model_settings
        )
        
        # 使用input_file功能处理PDF
        result = await Runner.run(
            pdf_agent,
            [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_file",
                            "file_data": f"data:application/pdf;base64,{b64_file}",
                            "filename": filename,
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": "请提取并总结这个PDF文件的主要内容，包括标题、摘要、主要章节和关键概念。请用清晰的结构化文本格式输出。",
                },
            ],
        )
        
        # 返回提取的内容
        if result and result.final_output:
            return result.final_output
        else:
            raise Exception("PDF内容提取失败：未返回有效内容")
            
    except Exception as e:
        raise Exception(f"提取PDF内容失败: {str(e)}")


def file_to_base64(file_path: str) -> str:
    """
    将文件转换为base64编码（辅助函数）
    
    Args:
        file_path: 文件路径
        
    Returns:
        base64编码的字符串
    """
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


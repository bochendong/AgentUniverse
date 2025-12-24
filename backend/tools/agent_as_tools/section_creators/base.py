"""Base Section Creator - 章节创建器抽象基类"""

from abc import ABC, abstractmethod
from typing import Optional
from backend.models import Outline, Section


class BaseSectionCreator(ABC):
    """章节创建器抽象基类
    
    所有具体的章节创建器都应该继承这个基类，实现统一的接口。
    """
    
    def __init__(
        self,
        outline: Outline,
        file_path: Optional[str] = None,
        notebook_description: Optional[str] = None
    ):
        """初始化章节创建器
        
        Args:
            outline: 笔记本大纲
            file_path: 文件路径（如果有）
            notebook_description: 笔记本描述（如果有）
        """
        self.outline = outline
        self.file_path = file_path
        self.notebook_description = notebook_description or (
            outline.notebook_description if hasattr(outline, 'notebook_description') else None
        )
    
    @abstractmethod
    async def create_section(
        self,
        section_title: str,
        section_description: str,
        section_index: int,
        total_sections: int
    ) -> Section:
        """创建单个章节
        
        Args:
            section_title: 章节标题
            section_description: 章节描述
            section_index: 章节索引（从1开始）
            total_sections: 总章节数
            
        Returns:
            Section 对象
        """
        pass
    
    @abstractmethod
    def get_creator_type(self) -> str:
        """获取创建器类型名称
        
        Returns:
            创建器类型字符串（用于日志和调试）
        """
        pass


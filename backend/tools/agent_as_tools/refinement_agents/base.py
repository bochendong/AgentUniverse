"""Base Refinement Agent - 内容优化器抽象基类"""

from abc import ABC, abstractmethod
from typing import Optional
from backend.models import Section


class BaseRefinementAgent(ABC):
    """内容优化器抽象基类
    
    所有具体的内容优化器都应该继承这个基类，实现统一的接口。
    """
    
    def __init__(
        self,
        section: Section,
        section_context: str = ""
    ):
        """初始化内容优化器
        
        Args:
            section: 需要优化的 Section 对象
            section_context: 章节上下文（章节描述、相关定义等）
        """
        self.section = section
        self.section_context = section_context
    
    @abstractmethod
    async def refine(self) -> Section:
        """优化 Section 内容
        
        Returns:
            优化后的 Section 对象
        """
        pass
    
    @abstractmethod
    def get_refiner_type(self) -> str:
        """获取优化器类型名称
        
        Returns:
            优化器类型字符串（用于日志和调试）
        """
        pass
    
    @abstractmethod
    def get_refinement_target(self) -> str:
        """获取优化目标描述
        
        Returns:
            优化目标描述字符串（例如："练习题和例子"、"证明"等）
        """
        pass


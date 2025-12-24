"""Base Modify Agent - 内容修改器抽象基类"""

from abc import ABC, abstractmethod
from agents import Agent
from backend.config.model_config import get_model_settings, get_model_name


class BaseModifyAgent(ABC, Agent):
    """内容修改器抽象基类
    
    所有具体的内容修改器都应该继承这个基类，实现统一的接口。
    """
    
    def __init__(
        self,
        name: str,
        instructions: str,
        output_type=None
    ):
        """初始化内容修改器
        
        Args:
            name: Agent 名称
            instructions: Agent 指令
            output_type: 输出类型（可选，用于需要结构化输出的场景）
        """
        # Get model settings from config
        model_name = get_model_name()
        model_settings = get_model_settings()
        
        # 调用 Agent 的 __init__
        super().__init__(
            name=name,
            instructions=instructions,
            model=model_name,
            model_settings=model_settings,
            output_type=output_type
        )
    
    @abstractmethod
    def get_modifier_type(self) -> str:
        """获取修改器类型名称
        
        Returns:
            修改器类型字符串（用于日志和调试）
        """
        pass
    
    @abstractmethod
    def get_modification_target(self) -> str:
        """获取修改目标描述
        
        Returns:
            修改目标描述字符串（例如："定义"、"介绍"、"总结"、"练习题"等）
        """
        pass


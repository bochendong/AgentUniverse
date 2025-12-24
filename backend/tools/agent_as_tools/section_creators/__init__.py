"""Section Creators - 章节创建器模块

这个模块提供了不同场景下的章节创建器实现：
- BaseSectionCreator: 抽象基类
- SectionCreatorRouter: 路由器，根据文件类型和质量选择合适的创建器
- WellFormedNoteSectionCreator: 处理完善的笔记
- FromScratchSectionCreator: 从零生成内容
- PaperSectionCreator: 处理论文
- PPTSectionCreator: 处理PPT（未来扩展）
"""

from .base import BaseSectionCreator
from .router import SectionCreatorRouter
from .well_formed_note import WellFormedNoteSectionCreator
from .from_scratch import FromScratchSectionCreator
from .paper import PaperSectionCreator

__all__ = [
    "BaseSectionCreator",
    "SectionCreatorRouter",
    "WellFormedNoteSectionCreator",
    "FromScratchSectionCreator",
    "PaperSectionCreator",
]


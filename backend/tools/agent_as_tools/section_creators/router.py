"""Section Creator Router - 章节创建器路由器"""

from typing import Optional, Literal
from backend.models import Outline
from .base import BaseSectionCreator
from .well_formed_note import WellFormedNoteSectionCreator
from .from_scratch import FromScratchSectionCreator
from .paper import PaperSectionCreator
from .utils import detect_file_type, get_file_content, assess_content_quality


class SectionCreatorRouter:
    """章节创建器路由器
    
    根据文件类型和内容质量，自动选择合适的章节创建器。
    
    支持的流程：
    1. 完善的笔记（well_formed）→ WellFormedNoteSectionCreator
    2. 无文件/从零生成 → FromScratchSectionCreator
    3. 论文（pdf）→ PaperSectionCreator
    4. PPT（pptx/ppt）→ 未来扩展
    """
    
    def __init__(
        self,
        outline: Outline,
        file_path: Optional[str] = None,
        force_creator_type: Optional[Literal['well_formed', 'from_scratch', 'paper', 'ppt']] = None
    ):
        """初始化路由器
        
        Args:
            outline: 笔记本大纲
            file_path: 文件路径（如果有）
            force_creator_type: 强制使用指定的创建器类型（用于测试或特殊场景）
        """
        self.outline = outline
        self.file_path = file_path
        self.force_creator_type = force_creator_type
        self._creator: Optional[BaseSectionCreator] = None
    
    def get_creator(self) -> BaseSectionCreator:
        """获取合适的章节创建器
        
        Returns:
            BaseSectionCreator 实例
        """
        if self._creator is not None:
            return self._creator
        
        # 如果强制指定了创建器类型
        if self.force_creator_type:
            self._creator = self._create_creator_by_type(self.force_creator_type)
            return self._creator
        
        # 自动检测和选择
        if not self.file_path:
            # 流程2：无文件，从零生成
            print("[Router] 检测到无文件，使用 FromScratchSectionCreator")
            self._creator = FromScratchSectionCreator(
                outline=self.outline,
                file_path=None
            )
            return self._creator
        
        # 检测文件类型
        file_type = detect_file_type(self.file_path)
        
        if file_type == 'pdf':
            # 流程3：论文
            print("[Router] 检测到 PDF 文件，使用 PaperSectionCreator")
            self._creator = PaperSectionCreator(
                outline=self.outline,
                file_path=self.file_path
            )
            return self._creator
        
        elif file_type in ['pptx', 'ppt']:
            # 流程4：PPT（未来扩展）
            raise NotImplementedError("PPT 文件支持尚未实现")
        
        else:
            # 流程1：完善的笔记或其他文本文件
            # 需要评估内容质量
            try:
                content = get_file_content(self.file_path)
                quality, score = assess_content_quality(content)
                
                print(f"[Router] 文件类型: {file_type}, 内容质量: {quality} (分数: {score:.2f})")
                
                if quality == 'well_formed':
                    # 内容完善，可能不需要重写
                    print("[Router] 使用 WellFormedNoteSectionCreator")
                    self._creator = WellFormedNoteSectionCreator(
                        outline=self.outline,
                        file_path=self.file_path
                    )
                else:
                    # 内容稀疏或未知，使用从零生成（但会参考原文件）
                    print("[Router] 内容质量较低，使用 FromScratchSectionCreator（会参考原文件）")
                    self._creator = FromScratchSectionCreator(
                        outline=self.outline,
                        file_path=self.file_path
                    )
                
                return self._creator
                
            except Exception as e:
                print(f"[Router] 读取文件失败: {e}，使用 FromScratchSectionCreator")
                # 如果读取失败，回退到从零生成
                self._creator = FromScratchSectionCreator(
                    outline=self.outline,
                    file_path=None
                )
                return self._creator
    
    def _create_creator_by_type(
        self,
        creator_type: Literal['well_formed', 'from_scratch', 'paper', 'ppt']
    ) -> BaseSectionCreator:
        """根据类型创建创建器（用于强制指定类型）"""
        if creator_type == 'well_formed':
            return WellFormedNoteSectionCreator(
                outline=self.outline,
                file_path=self.file_path
            )
        elif creator_type == 'from_scratch':
            return FromScratchSectionCreator(
                outline=self.outline,
                file_path=self.file_path
            )
        elif creator_type == 'paper':
            return PaperSectionCreator(
                outline=self.outline,
                file_path=self.file_path
            )
        elif creator_type == 'ppt':
            raise NotImplementedError("PPT 文件支持尚未实现")
        else:
            raise ValueError(f"未知的创建器类型: {creator_type}")


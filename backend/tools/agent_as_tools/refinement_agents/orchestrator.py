"""Refinement Orchestrator - 内容优化协调器"""

from typing import List, Optional
from backend.models import Section
from .base import BaseRefinementAgent
from .exercise import ExerciseRefinementAgent
from .proof import ProofRefinementAgent


class RefinementOrchestrator:
    """内容优化协调器
    
    统一管理所有内容优化器，按顺序调用它们来优化 Section。
    
    当前支持的优化器：
    1. ExerciseRefinementAgent - 优化练习题和例子
    2. ProofRefinementAgent - 优化证明
    """
    
    def __init__(
        self,
        section: Section,
        section_context: str = "",
        enabled_refiners: Optional[List[str]] = None
    ):
        """初始化协调器
        
        Args:
            section: 需要优化的 Section 对象
            section_context: 章节上下文
            enabled_refiners: 启用的优化器列表（None 表示全部启用）
                            可选值：["exercise", "proof"]
        """
        self.section = section
        self.section_context = section_context
        self.enabled_refiners = enabled_refiners or ["exercise", "proof"]
        self._refiners: List[BaseRefinementAgent] = []
    
    def _create_refiners(self) -> List[BaseRefinementAgent]:
        """创建所有需要的优化器
        
        Returns:
            优化器列表
        """
        if self._refiners:
            return self._refiners
        
        refiners = []
        
        if "exercise" in self.enabled_refiners:
            refiners.append(ExerciseRefinementAgent(
                section=self.section,
                section_context=self.section_context
            ))
        
        if "proof" in self.enabled_refiners:
            refiners.append(ProofRefinementAgent(
                section=self.section,
                section_context=self.section_context
            ))
        
        self._refiners = refiners
        return refiners
    
    async def refine_all(self) -> Section:
        """按顺序调用所有优化器优化 Section
        
        Returns:
            优化后的 Section 对象
        """
        refiners = self._create_refiners()
        
        if not refiners:
            print("[RefinementOrchestrator] 没有启用的优化器，跳过优化")
            return self.section
        
        print(f"[RefinementOrchestrator] 开始优化，使用 {len(refiners)} 个优化器")
        
        current_section = self.section
        
        for idx, refiner in enumerate(refiners, 1):
            refiner_type = refiner.get_refiner_type()
            target = refiner.get_refinement_target()
            
            print(f"[{idx}/{len(refiners)}] 开始优化: {target} ({refiner_type})...")
            
            try:
                # 更新 refiner 的 section（因为前一个优化器可能已经修改了 section）
                refiner.section = current_section
                
                current_section = await refiner.refine()
                print(f"[{idx}/{len(refiners)}] ✓ {target} 优化完成")
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"[{idx}/{len(refiners)}] ✗ {target} 优化失败: {e}\n{error_trace}")
                # 继续执行下一个优化器，不中断流程
        
        print(f"[RefinementOrchestrator] 所有优化完成")
        
        return current_section


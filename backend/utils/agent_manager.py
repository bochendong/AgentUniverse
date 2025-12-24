"""Agent Manager - Unified agent wake-up and tools restoration system.

This module provides a centralized way to:
1. Wake up agents from database without unnecessary writes
2. Ensure tools are properly restored when agents are loaded
3. Cache agents in memory to avoid repeated database reads
"""

from typing import Optional, Dict, Any
from backend.agent.BaseAgent import BaseAgent
from backend.database.agent_db import load_agent, save_agent
from backend.tools.tool_registry import get_tool_registry


class AgentManager:
    """Manages agent wake-up, caching, and tools restoration."""
    
    def __init__(self):
        # In-memory cache: agent_id -> agent instance
        self._agent_cache: Dict[str, BaseAgent] = {}
        # Track which agents have been modified (need to save)
        self._modified_agents: set = set()
    
    def wake_agent(
        self, 
        agent_id: str, 
        db_path: Optional[str] = None,
        force_reload: bool = False
    ) -> Optional[BaseAgent]:
        """
        Wake up an agent from database, ensuring tools are restored.
        
        This method:
        1. Checks cache first (unless force_reload=True)
        2. Loads from database if not in cache
        3. Ensures tools are properly restored
        4. Does NOT save to database unless agent was actually modified
        
        Args:
            agent_id: The agent ID to wake up
            db_path: Optional database path
            force_reload: If True, reload from database even if cached
            
        Returns:
            The agent instance, or None if not found
        """
        # Check cache first (unless force_reload)
        if not force_reload and agent_id in self._agent_cache:
            agent = self._agent_cache[agent_id]
            # Update model settings (config may have changed)
            self._update_model_settings(agent)
            # Ensure tools are still valid (they might have been cleared)
            if not hasattr(agent, 'tools') or agent.tools is None:
                self._ensure_tools_restored(agent)
            return agent
        
        # Load from database
        agent = load_agent(agent_id, db_path=db_path)
        if agent is None:
            return None
        
        # Update model settings from config (important: agents loaded from DB may have old model settings)
        self._update_model_settings(agent)
        
        # Ensure tools are restored (load_agent should do this, but double-check)
        self._ensure_tools_restored(agent)
        
        # Cache the agent
        self._agent_cache[agent_id] = agent
        
        return agent
    
    def _update_model_settings(self, agent: BaseAgent) -> None:
        """
        更新 Agent 的模型设置（从数据库加载的 Agent 可能使用旧的模型设置）
        
        Args:
            agent: The agent instance
        """
        try:
            from backend.config.model_config import get_model_name
            model_name = get_model_name()
            
            # 检查当前模型是否与配置一致
            current_model = None
            if hasattr(agent, 'model') and agent.model:
                current_model = agent.model
            elif hasattr(agent, 'model_settings') and agent.model_settings:
                if hasattr(agent.model_settings, 'model'):
                    current_model = agent.model_settings.model
            
            # 如果模型不一致，更新它
            if current_model != model_name:
                print(f"[AgentManager] 更新 Agent {agent.id[:8]}... 的模型: {current_model} -> {model_name}")
                
                # 尝试直接设置 model 属性（Agent 类可能支持这个）
                if hasattr(agent, 'model'):
                    agent.model = model_name
                
                # 如果 Agent 有 model_settings 属性，也更新它
                if hasattr(agent, 'model_settings'):
                    from backend.config.model_config import get_model_settings
                    agent.model_settings = get_model_settings()
                
                # 标记为已修改，以便保存到数据库
                self._modified_agents.add(agent.id)
            else:
                # 即使模型一致，也确保 model_settings 是最新的（可能包含 reasoning、verbosity 等设置）
                if hasattr(agent, 'model_settings'):
                    from backend.config.model_config import get_model_settings
                    new_settings = get_model_settings()
                    
                    # 检查是否需要更新
                    needs_update = False
                    
                    # 检查 reasoning 设置
                    if hasattr(new_settings, 'reasoning') and hasattr(agent.model_settings, 'reasoning'):
                        if agent.model_settings.reasoning != new_settings.reasoning:
                            needs_update = True
                    elif hasattr(new_settings, 'reasoning') and not hasattr(agent.model_settings, 'reasoning'):
                        needs_update = True
                    elif not hasattr(new_settings, 'reasoning') and hasattr(agent.model_settings, 'reasoning'):
                        needs_update = True
                    
                    # 检查 verbosity 设置
                    if hasattr(new_settings, 'verbosity') and hasattr(agent.model_settings, 'verbosity'):
                        if agent.model_settings.verbosity != new_settings.verbosity:
                            needs_update = True
                    elif hasattr(new_settings, 'verbosity') and not hasattr(agent.model_settings, 'verbosity'):
                        needs_update = True
                    
                    # 如果模型名称不同，也需要更新
                    if hasattr(new_settings, 'model') and hasattr(agent.model_settings, 'model'):
                        if agent.model_settings.model != new_settings.model:
                            needs_update = True
                    
                    if needs_update:
                        print(f"[AgentManager] 更新 Agent {agent.id[:8]}... 的 model_settings（模型: {current_model or 'N/A'}）")
                        agent.model_settings = new_settings
                        self._modified_agents.add(agent.id)
        except Exception as e:
            print(f"[AgentManager] 更新模型设置失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _ensure_tools_restored(self, agent: BaseAgent) -> None:
        """
        Ensure agent's tools are properly restored.
        
        This method checks if tools exist and are valid, and restores them if needed.
        It does NOT save to database unless tools were actually recreated.
        
        Args:
            agent: The agent instance
        """
        # If tools already exist and are valid, no need to restore
        if hasattr(agent, 'tools') and agent.tools is not None and len(agent.tools) > 0:
            # But for TopLevelAgent, MasterAgent and NoteBookAgent, we should still update instructions to ensure latest prompt
            from backend.agent.TopLevelAgent import TopLevelAgent
            from backend.agent.MasterAgent import MasterAgent
            from backend.agent.NoteBookAgent import NoteBookAgent
            
            if isinstance(agent, TopLevelAgent):
                # TopLevelAgent's _recreate_tools already updates instructions, but let's ensure it's called
                if hasattr(agent, '_recreate_tools'):
                    try:
                        agent._recreate_tools()
                    except Exception as e:
                        print(f"[AgentManager] Error updating TopLevelAgent instructions: {e}")
            elif isinstance(agent, MasterAgent):
                # For MasterAgent, always ensure instructions are updated (to refresh agents_list with current sub-agents)
                # This ensures the "你管理的 Agent" section shows the latest NotebookAgents (skills)
                if hasattr(agent, '_recreate_tools'):
                    try:
                        agent._recreate_tools()
                        print(f"[AgentManager] Updated MasterAgent instructions, length: {len(agent.instructions)}")
                    except Exception as e:
                        print(f"[AgentManager] Error updating MasterAgent instructions: {e}")
                        import traceback
                        traceback.print_exc()
            elif isinstance(agent, NoteBookAgent):
                # For NoteBookAgent, always ensure instructions are updated (to replace {notes} and {tools_usage})
                # Check if instructions contain placeholders
                if hasattr(agent, 'instructions') and ("{notes}" in agent.instructions or "{tools_usage}" in agent.instructions):
                    print(f"[AgentManager] NoteBookAgent {agent.id} has placeholders in instructions, updating...")
                    if hasattr(agent, '_recreate_tools'):
                        try:
                            agent._recreate_tools()
                            print(f"[AgentManager] Updated NoteBookAgent instructions, length: {len(agent.instructions)}")
                        except Exception as e:
                            print(f"[AgentManager] Error updating NoteBookAgent instructions: {e}")
                            import traceback
                            traceback.print_exc()
            return
        
        # Try to restore tools from database
        tool_ids = agent._get_tool_ids_from_db()
        if tool_ids:
            # Restore tools from database
            try:
                agent._recreate_tools_from_db(tool_ids)
                if agent.tools and len(agent.tools) > 0:
                    # For TopLevelAgent, also update instructions
                    from backend.agent.TopLevelAgent import TopLevelAgent
                    if isinstance(agent, TopLevelAgent) and hasattr(agent, '_recreate_tools'):
                        try:
                            agent._recreate_tools()  # This will update instructions
                        except Exception as e:
                            print(f"[AgentManager] Error updating TopLevelAgent instructions: {e}")
                    return  # Successfully restored
            except Exception as e:
                print(f"[AgentManager] Error restoring tools from DB for {agent.id}: {e}")
        
        # Fallback: use default _recreate_tools
        if hasattr(agent, '_recreate_tools'):
            try:
                agent._recreate_tools()
                # Mark as modified if tools were recreated (may need to save tool_ids)
                if agent.tools and len(agent.tools) > 0:
                    self._modified_agents.add(agent.id)
            except Exception as e:
                print(f"[AgentManager] Error in _recreate_tools for {agent.id}: {e}")
                agent.tools = []
        else:
            agent.tools = []
    
    def mark_modified(self, agent_id: str) -> None:
        """Mark an agent as modified (needs to be saved)."""
        self._modified_agents.add(agent_id)
    
    def save_if_modified(self, agent: BaseAgent) -> bool:
        """
        Save agent to database only if it was marked as modified.
        
        Args:
            agent: The agent instance
            
        Returns:
            True if saved, False if not modified
        """
        if agent.id in self._modified_agents:
            save_agent(agent, db_path=getattr(agent, 'DB_PATH', None))
            self._modified_agents.discard(agent.id)
            return True
        return False
    
    def save_all_modified(self) -> int:
        """
        Save all modified agents to database.
        
        Returns:
            Number of agents saved
        """
        saved_count = 0
        for agent_id in list(self._modified_agents):
            if agent_id in self._agent_cache:
                agent = self._agent_cache[agent_id]
                save_agent(agent, db_path=getattr(agent, 'DB_PATH', None))
                saved_count += 1
            self._modified_agents.discard(agent_id)
        return saved_count
    
    def clear_cache(self, agent_id: Optional[str] = None) -> None:
        """
        Clear agent cache.
        
        Args:
            agent_id: If provided, clear only this agent. Otherwise clear all.
        """
        if agent_id:
            self._agent_cache.pop(agent_id, None)
            self._modified_agents.discard(agent_id)
        else:
            self._agent_cache.clear()
            self._modified_agents.clear()
    
    def get_cached_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent from cache without loading from database."""
        return self._agent_cache.get(agent_id)


# Global singleton instance
_agent_manager: Optional[AgentManager] = None


def get_agent_manager() -> AgentManager:
    """Get the global AgentManager instance."""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager()
    return _agent_manager


def wake_agent(agent_id: str, db_path: Optional[str] = None, force_reload: bool = False) -> Optional[BaseAgent]:
    """
    Convenience function to wake up an agent.
    
    Args:
        agent_id: The agent ID to wake up
        db_path: Optional database path
        force_reload: If True, reload from database even if cached
        
    Returns:
        The agent instance, or None if not found
    """
    return get_agent_manager().wake_agent(agent_id, db_path, force_reload)

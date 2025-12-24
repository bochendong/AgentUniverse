"""Utility functions for API routes."""

from typing import Optional
from backend.agent.TopLevelAgent import TopLevelAgent
from backend.agent.MasterAgent import MasterAgent
from backend.database.agent_db import load_all_agents
from backend.models import AgentCard


def _serialize_agent_card(agent_card_result):
    """Serialize agent_card result to dict (handles both AgentCard objects and strings)."""
    if agent_card_result is None:
        return None
    if isinstance(agent_card_result, AgentCard):
        return agent_card_result.model_dump()
    # For backward compatibility with string-based agent_card (e.g., MasterAgent)
    return agent_card_result


# Global TopLevelAgent instance (singleton pattern)
_top_level_agent: Optional[TopLevelAgent] = None


def get_top_level_agent() -> TopLevelAgent:
    """Get or create the TopLevelAgent instance."""
    global _top_level_agent
    if _top_level_agent is None:
        # Use AgentManager to wake up TopLevelAgent
        from backend.utils.agent_manager import get_agent_manager, wake_agent
        
        # Try to find TopLevelAgent in database
        agents = load_all_agents()
        top_level_agent_id = None
        for agent_id, agent in agents.items():
            if isinstance(agent, TopLevelAgent):
                top_level_agent_id = agent_id
                break
        
        if top_level_agent_id:
            # Wake up existing TopLevelAgent
            _top_level_agent = wake_agent(top_level_agent_id)
            # Force update model settings for TopLevelAgent (important: may have old model from DB)
            from backend.utils.agent_manager import get_agent_manager
            get_agent_manager()._update_model_settings(_top_level_agent)
        else:
            # Create new one
            _top_level_agent = TopLevelAgent()
            _top_level_agent.save_to_db()
            # Cache it
            get_agent_manager()._agent_cache[_top_level_agent.id] = _top_level_agent
        
        # Ensure sub_agent_ids is not None after loading
        if not hasattr(_top_level_agent, 'sub_agent_ids') or _top_level_agent.sub_agent_ids is None:
            _top_level_agent.sub_agent_ids = []
            # Only save if this is a real change (not just initialization)
            if _top_level_agent.id:
                get_agent_manager().mark_modified(_top_level_agent.id)
        
        # Ensure tools are restored
        from backend.utils.agent_manager import get_agent_manager
        get_agent_manager()._ensure_tools_restored(_top_level_agent)
        
        # Ensure TopLevelAgent has a MasterAgent sub-agent
        # Check if it has any MasterAgent in sub_agent_ids OR in database
        has_master_agent = False
        master_agent_id = None
        # Note: load_all_agents is already imported at the top of the file
        
        # First check sub_agent_ids
        sub_agent_ids = getattr(_top_level_agent, 'sub_agent_ids', None) or []
        for sub_id in sub_agent_ids:
            try:
                from backend.utils.agent_manager import wake_agent
                sub_agent = wake_agent(sub_id, db_path=_top_level_agent.DB_PATH)
                if sub_agent and isinstance(sub_agent, MasterAgent):
                    has_master_agent = True
                    master_agent_id = sub_id
                    print(f"[get_top_level_agent] Found MasterAgent in sub_agent_ids: {sub_id}")
                    break
            except Exception:
                continue
        
        # If not found in sub_agent_ids, check database for MasterAgent with matching parent_agent_id
        if not has_master_agent:
            all_agents = load_all_agents(_top_level_agent.DB_PATH)
            for agent_id, agent in all_agents.items():
                if isinstance(agent, MasterAgent):
                    parent_id = getattr(agent, 'parent_agent_id', None)
                    if parent_id == _top_level_agent.id:
                        has_master_agent = True
                        master_agent_id = agent_id
                        print(f"[get_top_level_agent] Found MasterAgent in database: {agent_id}")
                        # Add to sub_agent_ids if not already there
                        if agent_id not in sub_agent_ids:
                            _top_level_agent._add_sub_agents(agent_id)
                            from backend.utils.agent_manager import get_agent_manager
                            get_agent_manager().mark_modified(_top_level_agent.id)
                        break
        
        # If still no MasterAgent found, create one (but only if we really don't have one)
        if not has_master_agent:
            print(f"[get_top_level_agent] No MasterAgent found, creating new one...")
            root_master = MasterAgent("Top Master Agent", parent_agent_id=_top_level_agent.id, DB_PATH=_top_level_agent.DB_PATH)
            # New MasterAgent should be saved immediately (it doesn't exist in DB yet)
            root_master.save_to_db()
            # Cache it
            from backend.utils.agent_manager import get_agent_manager
            get_agent_manager()._agent_cache[root_master.id] = root_master
            
            _top_level_agent._add_sub_agents(root_master.id)
            master_agent_id = root_master.id
            print(f"[get_top_level_agent] Created new MasterAgent: {master_agent_id}")
            # Update instructions
            agent_dict = _top_level_agent._load_sub_agents_dict()
            from backend.tools.utils import get_all_agent_info
            from backend.prompts.prompt_loader import load_prompt
            instructions = load_prompt(
                "top_level_agent",
                variables={"agents_list": get_all_agent_info(agent_dict)}
            )
            _top_level_agent.instructions = instructions
            get_agent_manager().mark_modified(_top_level_agent.id)
        else:
            print(f"[get_top_level_agent] Using existing MasterAgent: {master_agent_id}")
            
            # Clean up: Remove duplicate MasterAgents from sub_agent_ids
            # Keep only the one we found
            cleaned_sub_agent_ids = []
            duplicate_master_agent_ids = []
            for sub_id in sub_agent_ids:
                try:
                    from backend.utils.agent_manager import wake_agent
                    sub_agent = wake_agent(sub_id, db_path=_top_level_agent.DB_PATH)
                    if isinstance(sub_agent, MasterAgent):
                        # Only keep the one we found
                        if sub_id == master_agent_id:
                            cleaned_sub_agent_ids.append(sub_id)
                        else:
                            duplicate_master_agent_ids.append(sub_id)
                            print(f"[get_top_level_agent] Found duplicate MasterAgent: {sub_id}")
                    else:
                        # Keep non-MasterAgent agents
                        cleaned_sub_agent_ids.append(sub_id)
                except Exception:
                    # Skip agents that can't be loaded
                    continue
            
            # Update sub_agent_ids if it changed
            if set(cleaned_sub_agent_ids) != set(sub_agent_ids):
                _top_level_agent.sub_agent_ids = cleaned_sub_agent_ids
                from backend.utils.agent_manager import get_agent_manager
                get_agent_manager().mark_modified(_top_level_agent.id)
                print(f"[get_top_level_agent] Cleaned up sub_agent_ids. Removed {len(duplicate_master_agent_ids)} duplicate MasterAgent(s).")
            
            # Clean up: Delete duplicate MasterAgents that have no children
            if duplicate_master_agent_ids:
                print(f"[get_top_level_agent] Cleaning up duplicate MasterAgents from database...")
                for dup_id in duplicate_master_agent_ids:
                    try:
                        from backend.utils.agent_manager import wake_agent
                        dup_agent = wake_agent(dup_id, db_path=_top_level_agent.DB_PATH)
                        if dup_agent:
                            # Check if it has any children
                            dup_sub_agent_ids = getattr(dup_agent, 'sub_agent_ids', None) or []
                            if len(dup_sub_agent_ids) == 0:
                                # No children, safe to delete
                                from backend.database.agent_db import delete_agent
                                if delete_agent(dup_id, _top_level_agent.DB_PATH):
                                    print(f"[get_top_level_agent] Deleted duplicate MasterAgent with no children: {dup_id}")
                                else:
                                    print(f"[get_top_level_agent] Failed to delete duplicate MasterAgent: {dup_id}")
                            else:
                                print(f"[get_top_level_agent] Skipping deletion of MasterAgent {dup_id} (has {len(dup_sub_agent_ids)} children)")
                    except Exception as e:
                        print(f"[get_top_level_agent] Error cleaning up duplicate MasterAgent {dup_id}: {e}")
                
                # Also check database for other MasterAgents with same parent_agent_id
                all_agents = load_all_agents(_top_level_agent.DB_PATH)
                for agent_id, agent in all_agents.items():
                    if isinstance(agent, MasterAgent) and agent_id != master_agent_id:
                        parent_id = getattr(agent, 'parent_agent_id', None)
                        if parent_id == _top_level_agent.id:
                            # Found another duplicate MasterAgent
                            dup_sub_agent_ids = getattr(agent, 'sub_agent_ids', None) or []
                            if len(dup_sub_agent_ids) == 0:
                                # No children, safe to delete
                                from backend.database.agent_db import delete_agent
                                if delete_agent(agent_id, _top_level_agent.DB_PATH):
                                    print(f"[get_top_level_agent] Deleted duplicate MasterAgent from database: {agent_id}")
                                else:
                                    print(f"[get_top_level_agent] Failed to delete duplicate MasterAgent: {agent_id}")
    
    # Final safety check before returning
    if not hasattr(_top_level_agent, 'sub_agent_ids') or _top_level_agent.sub_agent_ids is None:
        _top_level_agent.sub_agent_ids = []
        from backend.utils.agent_manager import get_agent_manager
        get_agent_manager().mark_modified(_top_level_agent.id)
    
    # Ensure tools is not None (AgentManager should have done this, but double-check)
    from backend.utils.agent_manager import get_agent_manager
    agent_manager = get_agent_manager()
    agent_manager._ensure_tools_restored(_top_level_agent)
    
    # Ensure model settings are up-to-date (important: agents loaded from DB may have old model)
    agent_manager._update_model_settings(_top_level_agent)
    
    # Save any modifications at the end (only if actually modified)
    agent_manager.save_if_modified(_top_level_agent)
    
    return _top_level_agent

"""NoteBookAgent - simplified implementation following the effective design pattern."""

from typing import Optional, Dict

from backend.agent.BaseAgent import BaseAgent, AgentType
from backend.models import Outline, Section
from backend.models import AgentCard
from backend.prompts.prompt_loader import load_prompt

class NoteBookAgent(BaseAgent):
    """Notebook agent that manages notebook content."""
    
    def __init__(
        self, 
        messgae: str = "",
        outline: Optional[Outline] = None,
        sections: Optional[Dict[str, Section]] = None,
        notebook_title: Optional[str] = None,
        parent_agent_id: Optional[str] = None,
        DB_PATH: Optional[str] = None
    ):
        """
        Initialize NoteBookAgent.
        
        Args:
            messgae: Legacy parameter for markdown content (for backward compatibility)
            outline: Outline structure containing notebook title and section descriptions
            sections: Dictionary mapping section titles to Section objects
            notebook_title: Notebook title (if provided, will override outline.notebook_title)
            parent_agent_id: ID of the parent agent (optional)
            DB_PATH: Database path (optional)
        """
        # Store outline and sections if provided
        self.outline = outline
        self.sections = sections or {}
        
        # Determine notebook_title: use provided parameter, or extract from outline, or default
        if notebook_title:
            self.notebook_title = notebook_title
        elif outline and outline.notebook_title:
            self.notebook_title = outline.notebook_title
        else:
            self.notebook_title = ""
        
        # Store notebook_description from outline if available
        self.notebook_description = ""
        if outline and hasattr(outline, 'notebook_description'):
            self.notebook_description = outline.notebook_description
        
        # Generate markdown content from outline and sections, or use provided message
        # For now, set a placeholder - we'll generate from sections after super().__init__
        if messgae:
            self.notes = messgae
        else:
            self.notes = ""  # Will be generated after super().__init__ if outline and sections are available
        
        # Load prompt from file
        instructions = load_prompt(
            "notebook_agent",
            variables={"notes": self.notes}
        )
        
        # Initialize the base class first (this creates self.id)
        super().__init__(
            name="NoteBookAgent_temp",  # Temporary name, will update after id is created
            instructions=instructions,
            tools=None,  # Will create after initialization
            mcp_config={},
            agent_type=AgentType.NOTEBOOK,
            parent_agent_id=parent_agent_id,
            DB_PATH=DB_PATH
        )
        
        # Update name with actual ID (use notebook title if available)
        if self.notebook_title:
            # Clean title for use in name (remove special characters)
            clean_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in self.notebook_title)
            clean_title = clean_title[:20].strip().replace(' ', '_')
            self.name = f"NoteBookAgent_{clean_title}_{self.id[:8]}"
        else:
            self.name = f"NoteBookAgent_{self.id[:8]}"
        
        # Ensure all content has IDs (for backward compatibility and new content)
        if self.sections:
            from backend.utils.content_id_utils import ensure_ids
            ensure_ids(self)
        
        # Generate notes from outline and sections if available (after super().__init__)
        # IMPORTANT: Always generate notes with IDs included so AI can use modify_by_id tool
        if self.outline and self.sections and not self.notes:
            # Import here to avoid circular import
            from backend.tools.utils import generate_markdown_from_agent
            self.notes = generate_markdown_from_agent(self, include_ids=True)
        
        # Save to database after initialization
        self.save_to_db()
        
        # Create tools using registry
        from backend.tools.tool_registry import get_tool_registry
        registry = get_tool_registry()
        
        modify_by_id = registry.create_tool("modify_by_id", self)
        get_content_by_id = registry.create_tool("get_content_by_id", self)
        add_content_to_section = registry.create_tool("add_content_to_section", self)
        
        # Set tools list
        self.tools = [t for t in [modify_by_id, get_content_by_id, add_content_to_section] if t is not None]
        
        # Update instructions with generated notes (with IDs) and tool usage
        # IMPORTANT: Ensure notes include IDs for modify_by_id tool to work
        # If notes don't have IDs, regenerate them with IDs included
        if self.sections and self.outline:
            from backend.tools.utils import generate_markdown_from_agent
            notes_with_ids = generate_markdown_from_agent(self, include_ids=True)
            # Only update if notes changed (to avoid unnecessary updates)
            if notes_with_ids != self.notes:
                self.notes = notes_with_ids
        
        tool_ids = ['modify_by_id', 'get_content_by_id', 'add_content_to_section']
        # Ensure notes is passed as string (not None)
        notes_value = self.notes if self.notes is not None else ""
        instructions = load_prompt(
            "notebook_agent",
            variables={"notes": notes_value},
            agent_instance=self,  # Pass agent instance to properly generate tools_usage
            tool_ids=tool_ids
        )
        self.instructions = instructions
        # Save updated instructions to database
        self.save_to_db()
    
    def _recreate_tools(self):
        """Recreate tools after loading from database (tools cannot be pickled)."""
        # Ensure IDs exist (for backward compatibility)
        if self.sections:
            from backend.utils.content_id_utils import ensure_ids
            ensure_ids(self)
        
        # Regenerate notes with IDs included so AI can use modify_by_id tool
        notes_regenerated = False
        if self.sections and self.outline:
            from backend.tools.utils import generate_markdown_from_agent
            new_notes = generate_markdown_from_agent(self, include_ids=True)
            # Only update if notes actually changed (to avoid unnecessary saves)
            if new_notes != self.notes:
                self.notes = new_notes
                notes_regenerated = True
        
        # Ensure notes is not None (default to empty string)
        if self.notes is None:
            self.notes = ""
        
        # Always use the new default tool IDs (ignore old tool_ids from database)
        # This ensures we don't try to create deprecated modify_notes tool
        default_tool_ids = ['modify_by_id', 'get_content_by_id', 'add_content_to_section']
        self._recreate_tools_from_db(default_tool_ids)
        
        # Update tool_ids in database to new defaults (fix old data that had modify_notes)
        # This ensures next time we load, we won't try to create modify_notes
        import json
        import sqlite3
        from backend.database.agent_db import get_db_path
        db_path = get_db_path(self.DB_PATH if hasattr(self, 'DB_PATH') else None)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        tool_ids_json = json.dumps(default_tool_ids, ensure_ascii=False)
        cursor.execute(
            "UPDATE agents SET tool_ids = ? WHERE id = ?",
            (tool_ids_json, self.id)
        )
        conn.commit()
        conn.close()
        
        # Update instructions with notes that include IDs
        from backend.prompts.prompt_loader import load_prompt
        # Ensure notes is passed as string (not None)
        notes_value = self.notes if self.notes is not None else ""
        print(f"[NoteBookAgent._recreate_tools] Updating instructions, notes length: {len(notes_value) if notes_value else 0}")
        print(f"[NoteBookAgent._recreate_tools] Notes preview (first 200 chars): {notes_value[:200] if notes_value else 'EMPTY'}")
        
        instructions = load_prompt(
            "notebook_agent",
            variables={"notes": notes_value},
            agent_instance=self,  # Pass agent instance to properly generate tools_usage
            tool_ids=default_tool_ids
        )
        
        # Verify instructions were updated
        print(f"[NoteBookAgent._recreate_tools] Generated instructions length: {len(instructions)}")
        if "{notes}" in instructions:
            print(f"[NoteBookAgent._recreate_tools] ❌ ERROR: Instructions still contain {{notes}} placeholder after load_prompt!")
            print(f"[NoteBookAgent._recreate_tools] Instructions preview (first 500 chars): {instructions[:500]}")
        if "{tools_usage}" in instructions:
            print(f"[NoteBookAgent._recreate_tools] ❌ ERROR: Instructions still contain {{tools_usage}} placeholder after load_prompt!")
        if "{notes}" not in instructions and "{tools_usage}" not in instructions:
            print(f"[NoteBookAgent._recreate_tools] ✅ Successfully replaced all placeholders in instructions")
        
        self.instructions = instructions
        
        # Always save to database after updating instructions (to persist updated instructions with notes and tools_usage)
        print(f"[NoteBookAgent._recreate_tools] Saving updated instructions to database...")
        self.save_to_db()
        print(f"[NoteBookAgent._recreate_tools] ✅ Saved instructions to database (length: {len(self.instructions)})")
    
    def _get_word_count(self) -> int:
        """
        Calculate the character/word count from notes content.
        For mixed Chinese and English content, counts characters more accurately.
        
        Returns:
            Approximate character/word count in the notes
        """
        if not hasattr(self, 'notes') or not self.notes:
            return 0
        
        # Count characters (better for mixed Chinese/English content)
        # Chinese characters are typically counted as words, so character count
        # is a better approximation for Chinese content
        # Remove markdown formatting characters for more accurate count
        import re
        
        # Remove markdown headers, bold, italic, code blocks, links
        text = re.sub(r'#{1,6}\s+', '', self.notes)  # Remove headers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove italic
        text = re.sub(r'`([^`]+)`', r'\1', text)  # Remove inline code
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Remove links
        text = re.sub(r'```[\s\S]*?```', '', text)  # Remove code blocks
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Count characters (excluding spaces for Chinese, but including for English words)
        # Simple approach: count all non-whitespace characters
        char_count = len([c for c in text if not c.isspace()])
        
        return char_count
    
    def _check_split(self) -> bool:
        """
        Check if the notebook agent should be split.
        
        Conditions for split:
        - Number of sections > 10
        - Word count > 3000
        
        Returns:
            True if split is recommended, False otherwise
        """
        # Check sections count
        sections_count = len(self.sections) if self.sections else 0
        
        # Calculate word count
        word_count = self._get_word_count()
        
        # Check if split conditions are met
        should_split = sections_count > 10 or word_count > 3000
        
        if should_split:
            # TODO: Send notification to user to confirm split
            # This can be implemented through notification_system
            # For now, we just return True to indicate split is recommended
            print(f"⚠️ Split recommended for notebook '{self.notebook_title}': "
                  f"sections={sections_count}, words={word_count}")
        
        return should_split

    async def _execute_split(self):
        """
        Execute the split operation: split this notebook into multiple smaller notebooks.
        
        Steps:
        1. Use SplitPlanAgent to generate a split plan
        2. Create a new MasterAgent to manage the split notebooks
        3. Create new NoteBookAgents for each planned notebook, moving corresponding sections
        4. Update parent_master_agent's sub_agent_ids (remove self, add new master)
        5. Delete this agent from database
        """
        from agents import Runner
        from backend.agent.specialized.NotebookSplitter import SplitPlanAgent
        from backend.agent.MasterAgent import MasterAgent
        from backend.models import Outline, SplitPlan
        
        # Step 1: Generate split plan using SplitPlanAgent
        # Prepare section information for the agent
        section_titles = list(self.sections.keys()) if self.sections else []
        sections_content = {}
        if self.outline and self.outline.outlines:
            # Use outline descriptions
            sections_content = dict(self.outline.outlines)
        else:
            # Fallback: use section titles as descriptions
            sections_content = {title: f"Section: {title}" for title in section_titles}
        
        # Create and run SplitPlanAgent
        split_agent = SplitPlanAgent(
            notebook_title=self.notebook_title or "未命名笔记本",
            notebook_description=self.notebook_description or "",
            section_titles=section_titles,
            sections_content=sections_content
        )
        
        split_result = await Runner.run(
            split_agent,
            "请分析这个笔记本的内容，生成一个合理的拆分计划，将章节分配到多个更小的笔记本中。"
        )
        
        if not split_result or not split_result.final_output:
            raise ValueError("无法生成拆分计划")
        
        split_plan = split_result.final_output
        
        # Step 2: Create new MasterAgent
        new_master_agent = MasterAgent(
            name=split_plan.master_agent_title,
            parent_agent_id=self.parent_agent_id,
            DB_PATH=self.DB_PATH
        )
        
        # Step 3: Create new NoteBookAgents for each planned notebook
        new_notebook_agents = []
        for notebook_plan in split_plan.notebooks:
            # Extract sections for this notebook
            notebook_sections = {}
            notebook_outline_dict = {}
            
            for section_title in notebook_plan.section_titles:
                if section_title in self.sections:
                    # Move the section to new notebook
                    notebook_sections[section_title] = self.sections[section_title]
                    # Get section description from original outline
                    if self.outline and self.outline.outlines and section_title in self.outline.outlines:
                        notebook_outline_dict[section_title] = self.outline.outlines[section_title]
                    else:
                        notebook_outline_dict[section_title] = f"Section: {section_title}"
            
            # Create new Outline for this notebook
            new_outline = Outline(
                notebook_title=notebook_plan.notebook_title,
                notebook_description=notebook_plan.notebook_description,
                outlines=notebook_outline_dict
            )
            
            # Create new NoteBookAgent
            # Note: NoteBookAgent.__init__ will automatically:
            # 1. Generate notes from outline and sections (via generate_markdown_from_agent)
            # 2. Save to database (via save_to_db)
            new_notebook = NoteBookAgent(
                outline=new_outline,
                sections=notebook_sections,
                notebook_title=notebook_plan.notebook_title,
                parent_agent_id=new_master_agent.id,
                DB_PATH=self.DB_PATH
            )
            
            # Verify that the notebook was saved and has content
            if not new_notebook.id:
                raise ValueError(f"Failed to create notebook: {notebook_plan.notebook_title}")
            
            # Verify notes were generated
            if not new_notebook.notes:
                # Regenerate notes if not already generated
                from backend.tools.utils import generate_markdown_from_agent
                new_notebook.notes = generate_markdown_from_agent(new_notebook, include_ids=True)
                new_notebook.save_to_db()
            
            new_notebook_agents.append(new_notebook)
            # Add to master agent's sub_agent_ids
            if not hasattr(new_master_agent, 'sub_agent_ids') or new_master_agent.sub_agent_ids is None:
                new_master_agent.sub_agent_ids = []
            new_master_agent.sub_agent_ids.append(new_notebook.id)
        
        # Save master agent with updated sub_agent_ids
        new_master_agent.save_to_db()
        
        # Step 4: Update parent_master_agent's sub_agent_ids
        if self.parent_agent_id:
            parent_agent = self.load_agent_from_db_by_id(self.parent_agent_id)
            if parent_agent:
                # Remove self from parent's sub_agent_ids
                parent_sub_agent_ids = getattr(parent_agent, 'sub_agent_ids', None) or []
                if self.id in parent_sub_agent_ids:
                    parent_sub_agent_ids.remove(self.id)
                    parent_agent.sub_agent_ids = parent_sub_agent_ids
                # Add new master agent to parent's sub_agent_ids
                if new_master_agent.id not in parent_sub_agent_ids:
                    parent_sub_agent_ids.append(new_master_agent.id)
                    parent_agent.sub_agent_ids = parent_sub_agent_ids
                parent_agent.save_to_db()
        
        # Step 5: Delete this agent from database
        db_manager = self._get_db_manager()
        db_manager.delete_agent(self.id)
        
        return {
            "success": True,
            "new_master_agent_id": new_master_agent.id,
            "new_notebook_ids": [nb.id for nb in new_notebook_agents],
            "message": f"成功拆分笔记本：创建了 {len(new_notebook_agents)} 个新笔记本，由 MasterAgent '{split_plan.master_agent_title}' 管理"
        }


    def agent_card(self) -> AgentCard:
        """
        返回agent card信息，格式像名片一样展示notebook信息
        
        Returns:
            AgentCard对象，包含标题、描述、大纲等信息
        """
        # 确定notebook标题
        title = self.notebook_title or (self.outline.notebook_title if self.outline else "未命名笔记本")
        
        # 获取笔记本描述：优先使用 self.notebook_description，如果没有则从 outline 获取
        notebook_description = ""
        if hasattr(self, 'notebook_description') and self.notebook_description:
            notebook_description = self.notebook_description
        elif self.outline and hasattr(self.outline, 'notebook_description') and self.outline.notebook_description:
            notebook_description = self.outline.notebook_description
        
        # 获取大纲信息
        outline_dict = {}
        if self.outline and self.outline.outlines:
            outline_dict = self.outline.outlines
        
        return AgentCard(
            title=title,
            agent_id=self.id,
            parent_agent_id=self.parent_agent_id,
            description=notebook_description,
            outline=outline_dict
        )
    
    def get_or_create_modify_agent(self):
        """
        获取或创建关联的NotebookModifyAgent
        
        Returns:
            NotebookModifyAgent实例
        """
        from backend.agent.specialized.NotebookModifyAgent import NotebookModifyAgent
        
        # 检查是否已有modify_agent_id
        if hasattr(self, 'modify_agent_id') and self.modify_agent_id:
            try:
                modify_agent = self.load_agent_from_db_by_id(self.modify_agent_id)
                if modify_agent:
                    return modify_agent
            except Exception:
                # 如果加载失败，创建新的
                pass
        
        # 创建新的NotebookModifyAgent
        modify_agent = NotebookModifyAgent(
            notebook_agent_id=self.id,
            parent_agent_id=self.parent_agent_id,
            DB_PATH=self.DB_PATH
        )
        
        # 保存modify_agent_id到当前agent
        self.modify_agent_id = modify_agent.id
        self.save_to_db()
        
        return modify_agent



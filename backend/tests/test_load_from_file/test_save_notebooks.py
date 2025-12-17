"""Test script to directly create notebooks and save their contents."""

import asyncio
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.agent.TopLevelAgent import TopLevelAgent
from backend.agent.MasterAgent import MasterAgent
from backend.agent.NoteBookAgent import NoteBookAgent
from backend.database.agent_db import init_db, load_all_agents
from backend.database.session_db import init_session_db
from backend.tools.notebook_creator_tool import create_notebook_agent_from_file
from backend.tools.agent_utils import generate_markdown_from_agent


async def main():
    """Main test function."""
    # Create test database
    temp_dir = tempfile.mkdtemp(prefix="agent_test_db_")
    test_db_path = os.path.join(temp_dir, "test_agent_data.db")
    
    try:
        # Initialize test database
        init_db(test_db_path)
        init_session_db(test_db_path)
        
        print("=" * 80)
        print("Test: Create Notebooks and Save Contents")
        print("=" * 80)
        print(f"Test DB: {test_db_path}\n")
        
        # Get test files
        test_dir = Path(__file__).parent
        python_file = test_dir / "test_file" / "Python.md"
        
        if not python_file.exists():
            print(f"✗ Error: {python_file} not found")
            return
        
        python_path = str(python_file.absolute())
        
        # Create TopLevelAgent with test DB
        print("[1] Creating TopLevelAgent...")
        top_agent = TopLevelAgent(DB_PATH=test_db_path)
        print(f"✓ TopLevelAgent created (ID: {top_agent.id[:8]}...)\n")
        
        # Get MasterAgent
        master_agent = None
        for sub_id in top_agent.sub_agent_ids:
            agent = top_agent.load_agent_from_db_by_id(sub_id)
            if agent and isinstance(agent, MasterAgent):
                master_agent = agent
                break
        
        if not master_agent:
            print("✗ Error: MasterAgent not found")
            return
        
        print(f"✓ MasterAgent found (ID: {master_agent.id[:8]}...)\n")
        
        # Directly create notebook using the tool function
        print("[2] Creating notebook from Python.md...")
        print(f"  File: {python_path}\n")
        
        try:
            new_notebook, success_message = await create_notebook_agent_from_file(
                file_path=python_path,
                parent_agent_id=master_agent.id,
                DB_PATH=test_db_path
            )
            
            # Save notebook to database
            new_notebook.save_to_db()
            
            # Add to MasterAgent's sub_agent_ids
            master_agent._add_sub_agents(new_notebook.id)
            master_agent.save_to_db()
            
            print(f"✓ Notebook created successfully!")
            print(f"  Notebook ID: {new_notebook.id[:8]}...")
            print(f"  Title: {new_notebook.notebook_title}")
            print(f"  Success message: {success_message[:200] if len(success_message) > 200 else success_message}\n")
            
        except Exception as e:
            print(f"✗ Error creating notebook: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Wait a bit for any async operations
        await asyncio.sleep(2)
        
        # Load all agents and find notebooks
        print("[3] Finding all notebooks...")
        all_agents = load_all_agents(test_db_path)
        notebook_agents = {}
        for agent_id, agent in all_agents.items():
            if isinstance(agent, NoteBookAgent):
                title = agent.notebook_title or f"Notebook_{agent_id[:8]}"
                notebook_agents[title] = agent
        
        print(f"✓ Found {len(notebook_agents)} NotebookAgent(s):")
        for title in notebook_agents.keys():
            print(f"  - {title}\n")
        
        if len(notebook_agents) == 0:
            print("⚠ Warning: No notebooks found")
            return
        
        # Save notebook contents
        print("[4] Saving notebook contents to output directory...")
        output_dir = test_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        for notebook_title, notebook_agent in notebook_agents.items():
            # Clean title for filename
            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in notebook_title)
            safe_title = safe_title.replace(' ', '_')[:50]
            
            # Generate markdown content using the generator tool
            try:
                markdown_content = generate_markdown_from_agent(notebook_agent)
            except Exception as e:
                print(f"  ⚠ Error generating markdown: {e}")
                # Fallback to raw notes
                markdown_content = notebook_agent.notes if hasattr(notebook_agent, 'notes') and notebook_agent.notes else "# No content\n"
            
            # Save notebook content (markdown)
            notes_file = output_dir / f"{safe_title}_notes.md"
            with open(notes_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"✓ Saved notebook content: {notes_file.name} ({len(markdown_content)} chars)")
            
            # Save raw notes if different
            if hasattr(notebook_agent, 'notes') and notebook_agent.notes:
                if notebook_agent.notes != markdown_content:
                    raw_notes_file = output_dir / f"{safe_title}_raw_notes.md"
                    with open(raw_notes_file, 'w', encoding='utf-8') as f:
                        f.write(notebook_agent.notes)
                    print(f"✓ Saved raw notes: {raw_notes_file.name}")
            
            # Save agent card
            card_file = output_dir / f"{safe_title}_agent_card.txt"
            card_content = notebook_agent.agent_card() if hasattr(notebook_agent, 'agent_card') else ""
            with open(card_file, 'w', encoding='utf-8') as f:
                f.write(card_content)
            print(f"✓ Saved agent card: {card_file.name}")
            
            # Save notebook outline if available
            if hasattr(notebook_agent, 'outline') and notebook_agent.outline:
                outline_file = output_dir / f"{safe_title}_outline.json"
                import json
                try:
                    outline_dict = {}
                    if hasattr(notebook_agent.outline, 'notebook_title'):
                        outline_dict['notebook_title'] = notebook_agent.outline.notebook_title
                    if hasattr(notebook_agent.outline, 'notebook_description'):
                        outline_dict['notebook_description'] = notebook_agent.outline.notebook_description
                    if hasattr(notebook_agent.outline, 'outlines'):
                        outline_dict['outlines'] = notebook_agent.outline.outlines
                    
                    with open(outline_file, 'w', encoding='utf-8') as f:
                        json.dump(outline_dict, f, ensure_ascii=False, indent=2)
                    print(f"✓ Saved outline: {outline_file.name}")
                except Exception as e:
                    print(f"  ⚠ Could not save outline: {e}")
            
            # Save sections if available
            if hasattr(notebook_agent, 'sections') and notebook_agent.sections:
                sections_file = output_dir / f"{safe_title}_sections_info.txt"
                with open(sections_file, 'w', encoding='utf-8') as f:
                    f.write(f"Number of sections: {len(notebook_agent.sections)}\n\n")
                    for section_title, section in notebook_agent.sections.items():
                        f.write(f"Section: {section_title}\n")
                        if hasattr(section, 'section_title'):
                            f.write(f"  Title: {section.section_title}\n")
                        f.write("\n")
                print(f"✓ Saved sections info: {sections_file.name}")
        
        # Save MasterAgent card
        master_card_file = output_dir / "master_agent_card.txt"
        with open(master_card_file, 'w', encoding='utf-8') as f:
            f.write(master_agent.agent_card())
        print(f"✓ Saved MasterAgent card: {master_card_file.name}")
        
        # Save TopLevelAgent card
        top_card_file = output_dir / "toplevel_agent_card.txt"
        with open(top_card_file, 'w', encoding='utf-8') as f:
            f.write(top_agent.agent_card())
        print(f"✓ Saved TopLevelAgent card: {top_card_file.name}")
        
        print(f"\n{'=' * 80}")
        print(f"✓ Test completed! All contents saved to: {output_dir}")
        print(f"{'=' * 80}\n")
        
    finally:
        # Optionally keep test DB for inspection (comment out to auto-delete)
        # if os.path.exists(temp_dir):
        #     shutil.rmtree(temp_dir, ignore_errors=True)
        pass


if __name__ == "__main__":
    asyncio.run(main())

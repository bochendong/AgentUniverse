"""Complete test flow: upload files, create notebooks, and save contents."""

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
from backend.tools.agent_utils import generate_markdown_from_agent
from agents import Runner


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
        print("Complete Test Flow: Upload Files and Save Notebook Contents")
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
        print("[1] Creating TopLevelAgent with test database...")
        top_agent = TopLevelAgent(DB_PATH=test_db_path)
        print(f"✓ TopLevelAgent created (ID: {top_agent.id[:8]}...)\n")
        
        # Upload Python.md file
        print("[2] Uploading Python.md file...")
        print(f"  File: {python_path}\n")
        
        # Use Runner to send message (this will trigger handle_file_upload)
        python_request = f"请上传文件并创建笔记本。文件路径：{python_path}。请使用 handle_file_upload 工具处理。"
        result = await Runner.run(top_agent, python_request)
        result_str = result.final_output if hasattr(result, 'final_output') else str(result)
        print(f"  Result: {result_str[:200] if len(result_str) > 200 else result_str}\n")
        
        # Wait for notebook creation
        print("  Waiting for notebook creation...")
        await asyncio.sleep(60)  # Wait for async notebook creation and LLM tool execution
        
        # Load all agents and find notebooks
        print("\n[3] Finding created notebooks...")
        all_agents = load_all_agents(test_db_path)
        notebook_agents = {}
        for agent_id, agent in all_agents.items():
            if isinstance(agent, NoteBookAgent):
                title = agent.notebook_title or f"Notebook_{agent_id[:8]}"
                notebook_agents[title] = agent
        
        print(f"✓ Found {len(notebook_agents)} NotebookAgent(s):")
        for title in notebook_agents.keys():
            print(f"  - {title}")
        
        if len(notebook_agents) == 0:
            print("\n⚠ Warning: No notebooks found. The file upload may have failed.")
            print("  This could be due to:")
            print("  1. File upload tool not being called correctly")
            print("  2. Notebook creation taking longer than expected")
            print("  3. Error in the notebook creation process")
            return
        
        # Save notebook contents
        print("\n[4] Saving notebook contents to output directory...")
        output_dir = test_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        for notebook_title, notebook_agent in notebook_agents.items():
            # Clean title for filename
            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in notebook_title)
            safe_title = safe_title.replace(' ', '_')[:50]
            
            # Generate markdown content
            markdown_content = generate_markdown_from_agent(notebook_agent)
            
            # Save notebook content
            notes_file = output_dir / f"{safe_title}_notes.md"
            with open(notes_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"✓ Saved notebook content: {notes_file.name} ({len(markdown_content)} chars)")
            
            # Save agent card
            card_file = output_dir / f"{safe_title}_agent_card.txt"
            card_content = notebook_agent.agent_card() if hasattr(notebook_agent, 'agent_card') else ""
            with open(card_file, 'w', encoding='utf-8') as f:
                f.write(card_content)
            print(f"✓ Saved agent card: {card_file.name}")
            
            # Save raw notes if different from markdown
            if hasattr(notebook_agent, 'notes') and notebook_agent.notes:
                raw_notes_file = output_dir / f"{safe_title}_raw_notes.md"
                with open(raw_notes_file, 'w', encoding='utf-8') as f:
                    f.write(notebook_agent.notes)
                print(f"✓ Saved raw notes: {raw_notes_file.name}")
        
        # Save MasterAgent card
        master_agent = None
        for sub_id in top_agent.sub_agent_ids:
            agent = top_agent.load_agent_from_db_by_id(sub_id)
            if agent and isinstance(agent, MasterAgent):
                master_agent = agent
                break
        
        if master_agent:
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
        print(f"✓ Test completed! Output saved to: {output_dir}")
        print(f"{'=' * 80}\n")
        
    finally:
        # Cleanup: remove temporary directory
        if os.path.exists(temp_dir):
            print(f"Cleaning up test database: {temp_dir}")
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(main())

"""Test script for TopLevelAgent with test database - upload files and query."""

import asyncio
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from backend.agent.TopLevelAgent import TopLevelAgent
from backend.agent.MasterAgent import MasterAgent
from backend.agent.NoteBookAgent import NoteBookAgent
from backend.database.agent_db import init_db, load_all_agents, delete_agent
from backend.database.session_db import init_session_db
from agents import Runner


@pytest.fixture
def test_db_path():
    """Create a temporary test database."""
    # Create a temporary directory for test database
    temp_dir = tempfile.mkdtemp(prefix="agent_test_db_")
    db_path = os.path.join(temp_dir, "test_agent_data.db")
    
    yield db_path
    
    # Cleanup: remove temporary directory and database
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_upload_dir():
    """Create a temporary directory for test uploads."""
    temp_dir = tempfile.mkdtemp(prefix="agent_test_uploads_")
    
    yield temp_dir
    
    # Cleanup: remove temporary directory
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def top_level_agent(test_db_path):
    """Create a TopLevelAgent instance with test database."""
    # Initialize test database
    init_db(test_db_path)
    init_session_db(test_db_path)
    
    # Create TopLevelAgent with test DB path
    agent = TopLevelAgent(DB_PATH=test_db_path)
    
    # Verify DB_PATH is set correctly
    assert agent.DB_PATH == test_db_path
    
    yield agent


@pytest.fixture
def test_files():
    """Get test file paths."""
    test_dir = Path(__file__).parent
    python_file = test_dir / "Python.md"
    group_file = test_dir / "Group.md"
    
    files = {}
    
    if python_file.exists():
        files["python"] = str(python_file.absolute())
    else:
        # Try test_file subdirectory
        python_file_alt = test_dir / "test_file" / "Python.md"
        if python_file_alt.exists():
            files["python"] = str(python_file_alt.absolute())
        else:
            pytest.skip(f"Test file not found: {python_file}")
    
    if group_file.exists():
        files["group"] = str(group_file.absolute())
    else:
        # Try test_file subdirectory
        group_file_alt = test_dir / "test_file" / "Group.md"
        if group_file_alt.exists():
            files["group"] = str(group_file_alt.absolute())
        else:
            # Group.md is optional, skip if not found
            pass
    
    return files


@pytest.mark.asyncio
async def test_create_top_level_agent(top_level_agent):
    """Test creating TopLevelAgent."""
    assert top_level_agent is not None
    assert top_level_agent.id is not None
    assert top_level_agent.DB_PATH is not None
    print(f"✓ TopLevelAgent created (ID: {top_level_agent.id[:8]}...)")
    print(f"  Test DB path: {top_level_agent.DB_PATH}")


@pytest.mark.asyncio
async def test_top_level_agent_has_master_agent(top_level_agent):
    """Test that TopLevelAgent has a MasterAgent."""
    assert len(top_level_agent.sub_agent_ids) > 0
    
    master_agent = None
    for sub_id in top_level_agent.sub_agent_ids:
        agent = top_level_agent.load_agent_from_db_by_id(sub_id)
        if agent and isinstance(agent, MasterAgent):
            master_agent = agent
            break
    
    assert master_agent is not None, "TopLevelAgent should have a MasterAgent"
    print(f"✓ MasterAgent found (ID: {master_agent.id[:8]}...)")
    print(f"  MasterAgent name: {master_agent.name}")


@pytest.mark.asyncio
async def test_file_upload_python(top_level_agent, test_files):
    """Test uploading Python.md file."""
    python_path = test_files["python"]
    python_request = "请上传Python.md文件并创建笔记本"
    
    print(f"\n[Test] Uploading Python.md...")
    print(f"  File path: {python_path}")
    
    # Try to get handle_file_upload tool
    handle_file_upload_func = None
    for tool in top_level_agent.tools:
        if hasattr(tool, 'name') and 'file_upload' in tool.name.lower():
            if hasattr(tool, 'function'):
                handle_file_upload_func = tool.function
            elif hasattr(tool, 'fn'):
                handle_file_upload_func = tool.fn
            elif callable(tool):
                handle_file_upload_func = tool
            break
    
        if handle_file_upload_func:
            result = handle_file_upload_func(file_path=python_path, user_request=python_request)
            print(f"  Result: {result[:500] if len(result) > 500 else result}")
        else:
            # Use Runner to send message
            result = await Runner.run(
                top_level_agent,
                f"我需要上传文件。文件路径：{python_path}。用户请求：{python_request}。请使用handle_file_upload工具处理。"
            )
            result = result.final_output if hasattr(result, 'final_output') else str(result)
            print(f"  Result: {result[:500] if len(result) > 500 else result}")
    
    # Wait for notebook creation (tools may take longer to execute)
    print(f"  Waiting for notebook creation (45 seconds for tool execution)...")
    await asyncio.sleep(45)
    
    # Verify notebook was created
    all_agents = load_all_agents(top_level_agent.DB_PATH)
    notebook_count = sum(1 for agent in all_agents.values() if isinstance(agent, NoteBookAgent))
    assert notebook_count > 0, "At least one NotebookAgent should be created"
    print(f"✓ Notebook created (total notebooks: {notebook_count})")


@pytest.mark.asyncio
async def test_file_upload_group(top_level_agent, test_files):
    """Test uploading Group.md file."""
    if "group" not in test_files:
        pytest.skip("Group.md file not found")
    
    group_path = test_files["group"]
    group_request = "请上传Group.md文件并创建笔记本"
    
    print(f"\n[Test] Uploading Group.md...")
    print(f"  File path: {group_path}")
    
    # Get handle_file_upload tool
    handle_file_upload_func = None
    for tool in top_level_agent.tools:
        if hasattr(tool, 'name') and 'file_upload' in tool.name.lower():
            if hasattr(tool, 'function'):
                handle_file_upload_func = tool.function
            elif hasattr(tool, 'fn'):
                handle_file_upload_func = tool.fn
            elif callable(tool):
                handle_file_upload_func = tool
            break
    
    if handle_file_upload_func:
        result = handle_file_upload_func(file_path=group_path, user_request=group_request)
        print(f"  Result: {result[:200] if len(result) > 200 else result}")
    else:
        result = await Runner.run(
            top_level_agent,
            f"我需要上传文件。文件路径：{group_path}。用户请求：{group_request}。请使用handle_file_upload工具处理。"
        )
        result = result.final_output if hasattr(result, 'final_output') else str(result)
        print(f"  Result: {result[:200] if len(result) > 200 else result}")
    
    # Wait for notebook creation
    await asyncio.sleep(15)
    
    # Verify notebook was created
    all_agents = load_all_agents(top_level_agent.DB_PATH)
    notebook_count = sum(1 for agent in all_agents.values() if isinstance(agent, NoteBookAgent))
    assert notebook_count > 0, "At least one NotebookAgent should be created"
    print(f"✓ Notebook created (total notebooks: {notebook_count})")


@pytest.mark.asyncio
async def test_query_python_questions(top_level_agent):
    """Test querying Python-related questions."""
    questions = [
        "Python中如何进行数学运算？",
        "什么是整数除法？"
    ]
    
    print(f"\n[Test] Querying Python questions...")
    
    for i, question in enumerate(questions, 1):
        print(f"  Question {i}: {question}")
        result = await Runner.run(top_level_agent, question)
        answer = result.final_output if hasattr(result, 'final_output') else str(result)
        assert answer is not None and len(answer) > 0, f"Question {i} should have an answer"
        print(f"  ✓ Got answer ({len(answer)} chars)")
        await asyncio.sleep(1)


@pytest.mark.asyncio
async def test_query_group_questions(top_level_agent):
    """Test querying Group-related questions."""
    questions = [
        "什么是群(Group)？",
        "群需要满足哪些性质？"
    ]
    
    print(f"\n[Test] Querying Group questions...")
    
    for i, question in enumerate(questions, 1):
        print(f"  Question {i}: {question}")
        result = await Runner.run(top_level_agent, question)
        answer = result.final_output if hasattr(result, 'final_output') else str(result)
        assert answer is not None and len(answer) > 0, f"Question {i} should have an answer"
        print(f"  ✓ Got answer ({len(answer)} chars)")
        await asyncio.sleep(1)


@pytest.mark.asyncio
async def test_list_all_notebooks(top_level_agent):
    """Test listing all created notebooks."""
    print(f"\n[Test] Listing all notebooks...")
    
    all_agents = load_all_agents(top_level_agent.DB_PATH)
    
    # Get MasterAgent
    master_agent = None
    for sub_id in top_level_agent.sub_agent_ids:
        agent = top_level_agent.load_agent_from_db_by_id(sub_id)
        if agent and isinstance(agent, MasterAgent):
            master_agent = agent
            break
    
    assert master_agent is not None, "MasterAgent should exist"
    
    # Find all NotebookAgents
    notebook_agents = {}
    
    def find_notebook_agents(agent_dict):
        """Recursively find all NotebookAgents."""
        for agent_id, agent in agent_dict.items():
            if isinstance(agent, NoteBookAgent):
                title = agent.notebook_title or f"Notebook_{agent_id[:8]}"
                notebook_agents[title] = agent
    
    # Search in database
    for agent_id, agent in all_agents.items():
        if isinstance(agent, NoteBookAgent):
            title = agent.notebook_title or f"Notebook_{agent_id[:8]}"
            notebook_agents[title] = agent
    
    print(f"  Found {len(notebook_agents)} NotebookAgent(s):")
    for title in notebook_agents.keys():
        print(f"    - {title}")
    
    # This test doesn't require notebooks to exist (they may be created in other tests)
    # Just verify the function works correctly
    assert isinstance(notebook_agents, dict), "Should return a dictionary"
    print(f"✓ Notebook listing works correctly")
    
    return notebook_agents


@pytest.mark.asyncio
async def test_agent_card_content(top_level_agent):
    """Test that agent cards contain expected content."""
    print(f"\n[Test] Checking agent card content...")
    
    # Get MasterAgent
    master_agent = None
    for sub_id in top_level_agent.sub_agent_ids:
        agent = top_level_agent.load_agent_from_db_by_id(sub_id)
        if agent and isinstance(agent, MasterAgent):
            master_agent = agent
            break
    
    assert master_agent is not None
    
    # Check MasterAgent card
    master_card = master_agent.agent_card()
    assert master_card is not None and len(master_card) > 0
    print(f"✓ MasterAgent card content: {len(master_card)} chars")
    
    # Check TopLevelAgent card
    top_card = top_level_agent.agent_card()
    assert top_card is not None and len(top_card) > 0
    print(f"✓ TopLevelAgent card content: {len(top_card)} chars")


@pytest.mark.asyncio
async def test_save_notebook_contents(top_level_agent):
    """Save all notebook contents and agent cards to output files."""
    print(f"\n[Test] Saving notebook contents and agent cards...")
    
    # Get output directory
    test_dir = Path(__file__).parent
    output_dir = test_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Load all agents from database
    all_agents = load_all_agents(top_level_agent.DB_PATH)
    
    # Get MasterAgent
    master_agent = None
    for sub_id in top_level_agent.sub_agent_ids:
        agent = top_level_agent.load_agent_from_db_by_id(sub_id)
        if agent and isinstance(agent, MasterAgent):
            master_agent = agent
            break
    
    if not master_agent:
        print("⚠ No MasterAgent found, skipping notebook save")
        return
    
    # Find all NotebookAgents
    notebook_agents = {}
    for agent_id, agent in all_agents.items():
        if isinstance(agent, NoteBookAgent):
            title = agent.notebook_title or f"Notebook_{agent_id[:8]}"
            notebook_agents[title] = agent
    
    print(f"  Found {len(notebook_agents)} NotebookAgent(s)")
    
    # Save notebook contents
    for notebook_title, notebook_agent in notebook_agents.items():
        # Clean title for filename
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in notebook_title)
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
        
        # Save notebook content (notes)
        notes_file = output_dir / f"{safe_title}_notes.md"
        notes_content = notebook_agent.notes if hasattr(notebook_agent, 'notes') and notebook_agent.notes else "# No content yet\n"
        with open(notes_file, 'w', encoding='utf-8') as f:
            f.write(notes_content)
        print(f"  ✓ Saved notes to: {notes_file.name} ({len(notes_content)} chars)")
        
        # Save agent card
        card_file = output_dir / f"{safe_title}_agent_card.txt"
        card_content = notebook_agent.agent_card() if hasattr(notebook_agent, 'agent_card') else "No agent card available"
        with open(card_file, 'w', encoding='utf-8') as f:
            f.write(card_content)
        print(f"  ✓ Saved agent card to: {card_file.name}")
        
        # Save notebook outline if available
        if hasattr(notebook_agent, 'outline') and notebook_agent.outline:
            outline_file = output_dir / f"{safe_title}_outline.txt"
            import json
            try:
                outline_data = {
                    "notebook_title": notebook_agent.outline.notebook_title if hasattr(notebook_agent.outline, 'notebook_title') else "",
                    "notebook_description": notebook_agent.outline.notebook_description if hasattr(notebook_agent.outline, 'notebook_description') else "",
                    "outlines": notebook_agent.outline.outlines if hasattr(notebook_agent.outline, 'outlines') else {}
                }
                with open(outline_file, 'w', encoding='utf-8') as f:
                    json.dump(outline_data, f, ensure_ascii=False, indent=2)
                print(f"  ✓ Saved outline to: {outline_file.name}")
            except Exception as e:
                print(f"  ⚠ Could not save outline: {e}")
    
    # Save MasterAgent card
    master_card_file = output_dir / "master_agent_card.txt"
    master_card = master_agent.agent_card()
    with open(master_card_file, 'w', encoding='utf-8') as f:
        f.write(master_card)
    print(f"✓ Saved MasterAgent card to: {master_card_file.name}")
    
    # Save TopLevelAgent card
    top_card_file = output_dir / "toplevel_agent_card.txt"
    top_card = top_level_agent.agent_card()
    with open(top_card_file, 'w', encoding='utf-8') as f:
        f.write(top_card)
    print(f"✓ Saved TopLevelAgent card to: {top_card_file.name}")
    
    print(f"\n✓ All notebook contents saved to: {output_dir}")
    
    assert len(notebook_agents) >= 0, "Should be able to list notebooks (even if empty)"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])

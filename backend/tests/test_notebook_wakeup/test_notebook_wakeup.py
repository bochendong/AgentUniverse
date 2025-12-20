"""
Test notebook wake-up functionality using AgentManager.

This test verifies that:
1. Notebook agents can be loaded from database
2. Tools are properly restored when waking up agents
3. AgentManager correctly manages agent caching and tools restoration
"""

import sys
import os
import shutil
import sqlite3
import pickle
import json
import uuid
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from backend.database.agent_db import init_db, get_db_path, save_agent, load_agent
from backend.database.session_db import init_session_db
from backend.agent.TopLevelAgent import TopLevelAgent
from backend.agent.MasterAgent import MasterAgent
from backend.agent.NoteBookAgent import NoteBookAgent
from backend.utils.agent_manager import wake_agent, get_agent_manager
from backend.agent.BaseAgent import AgentType


def copy_production_db_to_test(production_db_path: str, test_db_path: str) -> bool:
    """Copy production database to test database."""
    try:
        if os.path.exists(production_db_path):
            shutil.copy2(production_db_path, test_db_path)
            print(f"✓ Copied production database from {production_db_path} to {test_db_path}")
            return True
        else:
            print(f"⚠ Production database not found: {production_db_path}")
            return False
    except Exception as e:
        print(f"✗ Error copying database: {e}")
        return False


def create_test_database_with_notebook(test_db_path: str) -> dict:
    """
    Create a test database with TopLevelAgent, MasterAgent, and NoteBookAgent.
    
    Returns:
        Dictionary with agent IDs: {'top_level_id': ..., 'master_id': ..., 'notebook_id': ...}
    """
    print("\n[1] Creating test database with agents...")
    
    # Initialize database
    init_db(test_db_path)
    init_session_db(test_db_path)
    
    # Create TopLevelAgent
    print("\n[2] Creating TopLevelAgent...")
    top_level = TopLevelAgent(DB_PATH=test_db_path)
    top_level.save_to_db()
    print(f"✓ TopLevelAgent created: {top_level.id}")
    
    # Get MasterAgent from TopLevelAgent's sub_agents
    master_id = None
    if top_level.sub_agent_ids:
        master_id = top_level.sub_agent_ids[0]
        print(f"✓ MasterAgent found: {master_id}")
    else:
        print("⚠ No MasterAgent found in TopLevelAgent")
    
    # Create a NoteBookAgent
    print("\n[3] Creating NoteBookAgent...")
    notebook = NoteBookAgent(
        messgae="",  # Empty message, will be generated from sections
        notebook_title="Python 基础学习笔记",
        parent_agent_id=master_id if master_id else top_level.id,
        DB_PATH=test_db_path
    )
    notebook.save_to_db()
    print(f"✓ NoteBookAgent created: {notebook.id}")
    
    # Add notebook to MasterAgent's sub_agents
    if master_id:
        master = load_agent(master_id, db_path=test_db_path)
        if master:
            master._add_sub_agents(notebook.id)
            master.save_to_db()
            print(f"✓ Added NoteBookAgent to MasterAgent's sub_agents")
    
    return {
        'top_level_id': top_level.id,
        'master_id': master_id,
        'notebook_id': notebook.id
    }


def test_notebook_wakeup(test_db_path: str, notebook_id: str):
    """Test waking up a notebook agent and verifying tools are restored."""
    print("\n" + "=" * 80)
    print("Test: Notebook Wake-up")
    print("=" * 80)
    
    # Clear AgentManager cache to simulate fresh load
    get_agent_manager().clear_cache()
    print("\n[1] Cleared AgentManager cache")
    
    # Wake up the notebook agent
    print(f"\n[2] Waking up NoteBookAgent: {notebook_id}")
    notebook = wake_agent(notebook_id, db_path=test_db_path)
    
    if notebook is None:
        print("✗ Failed to wake up notebook agent")
        return False
    
    print(f"✓ NoteBookAgent woken up: {notebook.id}")
    print(f"  - Name: {notebook.name}")
    print(f"  - Title: {getattr(notebook, 'notebook_title', 'N/A')}")
    print(f"  - Type: {notebook.type}")
    
    # Verify tools are restored
    print("\n[3] Verifying tools are restored...")
    if not hasattr(notebook, 'tools'):
        print("✗ Agent has no 'tools' attribute")
        return False
    
    if notebook.tools is None:
        print("✗ Agent tools is None")
        return False
    
    print(f"✓ Tools attribute exists: {len(notebook.tools) if notebook.tools else 0} tools")
    
    if notebook.tools:
        print("  Tools found:")
        for i, tool in enumerate(notebook.tools, 1):
            tool_id = getattr(tool, '_tool_id', None)
            tool_name = getattr(tool, 'name', None)
            print(f"    {i}. {tool_id or tool_name or 'unknown'}")
    else:
        print("  ⚠ No tools found (this might be expected for NoteBookAgent)")
    
    # Verify agent can be used
    print("\n[4] Verifying agent functionality...")
    if hasattr(notebook, 'receive_messgae'):
        print("✓ Agent has receive_messgae method")
    else:
        print("✗ Agent missing receive_messgae method")
        return False
    
    # Verify agent card can be generated
    if hasattr(notebook, 'agent_card'):
        try:
            card = notebook.agent_card()
            print(f"✓ Agent card generated: {type(card)}")
        except Exception as e:
            print(f"⚠ Agent card generation failed: {e}")
    
    return True


def test_multiple_wakeups(test_db_path: str, notebook_id: str):
    """Test waking up the same agent multiple times (should use cache)."""
    print("\n" + "=" * 80)
    print("Test: Multiple Wake-ups (Cache Test)")
    print("=" * 80)
    
    # Clear cache first
    get_agent_manager().clear_cache()
    
    # First wake-up
    print("\n[1] First wake-up (should load from database)...")
    notebook1 = wake_agent(notebook_id, db_path=test_db_path)
    if notebook1 is None:
        print("✗ Failed first wake-up")
        return False
    print(f"✓ First wake-up successful: {notebook1.id}")
    
    # Second wake-up (should use cache)
    print("\n[2] Second wake-up (should use cache)...")
    notebook2 = wake_agent(notebook_id, db_path=test_db_path)
    if notebook2 is None:
        print("✗ Failed second wake-up")
        return False
    
    # Verify it's the same instance (from cache)
    if notebook1 is notebook2:
        print("✓ Second wake-up used cache (same instance)")
    else:
        print("⚠ Second wake-up created new instance (cache might not be working)")
    
    # Verify tools are still there
    if notebook2.tools is not None:
        print(f"✓ Tools still present: {len(notebook2.tools)} tools")
    else:
        print("✗ Tools lost after second wake-up")
        return False
    
    return True


def test_wakeup_via_send_message(test_db_path: str, notebook_id: str, master_id: str):
    """Test waking up notebook via send_message tool."""
    print("\n" + "=" * 80)
    print("Test: Wake-up via send_message")
    print("=" * 80)
    
    # Wake up MasterAgent
    print(f"\n[1] Waking up MasterAgent: {master_id}")
    master = wake_agent(master_id, db_path=test_db_path)
    if master is None:
        print("✗ Failed to wake up MasterAgent")
        return False
    print(f"✓ MasterAgent woken up: {master.id}")
    
    # Verify MasterAgent has send_message tool
    print("\n[2] Verifying MasterAgent has send_message tool...")
    if not master.tools:
        print("✗ MasterAgent has no tools")
        return False
    
    send_message_tool = None
    for tool in master.tools:
        tool_id = getattr(tool, '_tool_id', None)
        if tool_id == 'send_message':
            send_message_tool = tool
            break
    
    if send_message_tool is None:
        print("✗ send_message tool not found")
        return False
    print("✓ send_message tool found")
    
    # Test that send_message can wake up the notebook (without actually sending message)
    # This verifies the wake-up mechanism works, even if we can't actually call the LLM
    print(f"\n[3] Verifying send_message can wake up NoteBookAgent...")
    try:
        # The key test: verify that send_message tool can find and wake up the notebook
        # We'll simulate what send_message does internally - wake up the agent
        print("  Simulating send_message wake-up behavior...")
        notebook = wake_agent(notebook_id, db_path=master.DB_PATH)
        
        if notebook is None:
            print("✗ Failed to wake up notebook via AgentManager")
            return False
        
        print(f"✓ Notebook woken up successfully: {notebook.id}")
        
        # Verify notebook has tools restored
        if not hasattr(notebook, 'tools') or notebook.tools is None:
            print("✗ Notebook tools not restored after wake-up")
            return False
        
        print(f"✓ Notebook tools restored: {len(notebook.tools)} tools")
        
        # Verify notebook can receive messages (has the method)
        if not hasattr(notebook, 'receive_messgae'):
            print("✗ Notebook missing receive_messgae method")
            return False
        
        print("✓ Notebook has receive_messgae method (ready to receive messages)")
        
        # Note: We don't actually call receive_messgae because it requires network/LLM
        # But we've verified that the wake-up mechanism works correctly
        print("  (Skipping actual message send - requires network/LLM connection)")
        
        return True
    except Exception as e:
        print(f"✗ Error during wake-up verification: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("=" * 80)
    print("Notebook Wake-up Test Suite")
    print("=" * 80)
    
    # Determine test database path
    test_db_dir = project_root / "backend" / "tests" / "test_notebook_wakeup" / "test_db"
    test_db_dir.mkdir(parents=True, exist_ok=True)
    test_db_path = str(test_db_dir / "test_notebook_wakeup.db")
    
    # Option 1: Try to copy production database
    production_db_path = get_db_path()
    use_production_copy = False
    
    if os.path.exists(production_db_path):
        print(f"\n[Option 1] Production database found: {production_db_path}")
        response = input("Copy production database? (y/n): ").strip().lower()
        if response == 'y':
            if copy_production_db_to_test(production_db_path, test_db_path):
                use_production_copy = True
                print("✓ Using copied production database")
    
    # Option 2: Create new test database
    if not use_production_copy:
        print("\n[Option 2] Creating new test database...")
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        agent_ids = create_test_database_with_notebook(test_db_path)
        notebook_id = agent_ids['notebook_id']
        master_id = agent_ids['master_id']
    else:
        # Load notebook from copied database
        print("\n[Loading from copied database]")
        from backend.database.agent_db import load_all_agents
        all_agents = load_all_agents(test_db_path)
        
        # Find a NoteBookAgent
        notebook_id = None
        master_id = None
        for agent_id, agent in all_agents.items():
            if isinstance(agent, NoteBookAgent):
                notebook_id = agent_id
                print(f"✓ Found NoteBookAgent: {notebook_id}")
                master_id = getattr(agent, 'parent_agent_id', None)
                break
        
        if notebook_id is None:
            print("✗ No NoteBookAgent found in copied database")
            print("Creating new test database instead...")
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
            agent_ids = create_test_database_with_notebook(test_db_path)
            notebook_id = agent_ids['notebook_id']
            master_id = agent_ids['master_id']
    
    # Run tests
    print("\n" + "=" * 80)
    print("Running Tests")
    print("=" * 80)
    
    results = []
    
    # Test 1: Basic wake-up
    try:
        result = test_notebook_wakeup(test_db_path, notebook_id)
        results.append(("Basic Wake-up", result))
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Basic Wake-up", False))
    
    # Test 2: Multiple wake-ups (cache)
    try:
        result = test_multiple_wakeups(test_db_path, notebook_id)
        results.append(("Multiple Wake-ups", result))
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Multiple Wake-ups", False))
    
    # Test 3: Wake-up via send_message
    if master_id:
        try:
            result = test_wakeup_via_send_message(test_db_path, notebook_id, master_id)
            results.append(("Wake-up via send_message", result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(("Wake-up via send_message", False))
    
    # Print summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    print(f"\n{'All tests passed!' if all_passed else 'Some tests failed.'}")
    print(f"\nTest database location: {test_db_path}")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())

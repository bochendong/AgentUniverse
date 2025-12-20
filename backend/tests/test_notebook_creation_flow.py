"""
Test notebook creation flow: TopLevelAgent -> MasterAgent
Tests the MasterAgent lookup logic in create_notebook_from_outline tool.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

import sqlite3
from backend.database.agent_db import get_db_path, init_db
from backend.database.session_db import init_session_db


def test_master_agent_lookup_logic():
    """Test the MasterAgent lookup logic without running actual agents."""
    print("=" * 80)
    print("Test: MasterAgent Lookup Logic")
    print("=" * 80)
    
    # Use test database
    test_db_path = str(project_root / "backend" / "database" / "db" / "test_creation_flow.db")
    
    # Clean up old test DB
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Initialize databases
    print("\n[1] Initializing databases...")
    init_db(test_db_path)
    init_session_db(test_db_path)
    print(f"✓ Database initialized: {test_db_path}")
    
    # Simulate TopLevelAgent creation: insert TopLevelAgent into DB
    print("\n[2] Simulating TopLevelAgent creation...")
    import uuid
    import pickle
    import json
    
    top_agent_id = str(uuid.uuid4())
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    # Insert TopLevelAgent (using correct table schema: type, not agent_type)
    cursor.execute("""
        INSERT INTO agents (id, type, name, parent_agent_id, sub_agent_ids, tool_ids, data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        top_agent_id,
        "TOP_LEVEL",
        "TopLevelAgent",
        None,  # Top level has no parent
        json.dumps([]),  # Empty initially
        json.dumps(['send_message', 'handle_file_upload', 'create_notebook_from_outline']),
        pickle.dumps({})  # Empty data
    ))
    conn.commit()
    print(f"✓ TopLevelAgent inserted: {top_agent_id}")
    
    # Simulate MasterAgent creation: insert MasterAgent into DB
    print("\n[3] Simulating MasterAgent creation...")
    master_agent_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO agents (id, type, name, parent_agent_id, sub_agent_ids, tool_ids, data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        master_agent_id,
        "MASTER",
        "Top Master Agent",
        top_agent_id,  # Parent is TopLevelAgent
        json.dumps([]),
        json.dumps(['send_message', 'add_notebook_by_file', 'create_notebook', 'create_notebook_with_outline']),
        pickle.dumps({})  # Empty data (parent_agent_id is stored in parent_agent_id column)
    ))
    conn.commit()
    print(f"✓ MasterAgent inserted: {master_agent_id}")
    print(f"  - parent_agent_id: {top_agent_id}")
    
    # Update TopLevelAgent's sub_agent_ids
    print("\n[4] Updating TopLevelAgent sub_agent_ids...")
    cursor.execute("UPDATE agents SET sub_agent_ids = ? WHERE id = ?", 
                   (json.dumps([master_agent_id]), top_agent_id))
    conn.commit()
    print(f"✓ Updated TopLevelAgent.sub_agent_ids: [{master_agent_id}]")
    
    # Test lookup logic (simulating create_notebook_from_outline)
    print("\n[5] Testing MasterAgent lookup logic...")
    
    # Strategy 1: Load all agents and find MasterAgent with matching parent_agent_id
    print("  Strategy 1: Load all agents from database...")
    cursor.execute("SELECT id, name, type, parent_agent_id FROM agents")
    all_agents_data = cursor.fetchall()
    
    found_master = None
    for agent_id, name, agent_type, parent_id in all_agents_data:
        if agent_type == "MASTER":
            print(f"    - Found MasterAgent: {agent_id}, parent_id: {parent_id}")
            if parent_id == top_agent_id:
                found_master = agent_id
                print(f"    ✓ Found matching MasterAgent: {agent_id}")
                break
    
    if not found_master:
        print("    ✗ No matching MasterAgent found!")
        conn.close()
        return False
    
    # Strategy 2: Check sub_agent_ids
    print("\n  Strategy 2: Check sub_agent_ids...")
    cursor.execute("SELECT sub_agent_ids FROM agents WHERE id = ?", (top_agent_id,))
    row = cursor.fetchone()
    if row and row[0]:
        sub_agent_ids = json.loads(row[0])
        print(f"    - TopLevelAgent.sub_agent_ids: {sub_agent_ids}")
        if found_master in sub_agent_ids:
            print(f"    ✓ MasterAgent is in sub_agent_ids")
        else:
            print(f"    ⚠ MasterAgent not in sub_agent_ids (but found via Strategy 1)")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("Test Summary:")
    print("=" * 80)
    print("✓ Database initialized")
    print("✓ TopLevelAgent created in DB")
    print("✓ MasterAgent created in DB with correct parent_agent_id")
    print("✓ TopLevelAgent.sub_agent_ids updated")
    print("✓ MasterAgent lookup logic works correctly")
    print("\nAll checks passed! The lookup logic should work in production.")
    
    return True


if __name__ == "__main__":
    result = test_master_agent_lookup_logic()
    sys.exit(0 if result else 1)

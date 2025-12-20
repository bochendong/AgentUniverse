"""Test script to verify agent_as_tool registration."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_agent_as_tool_registration():
    """Test agent_as_tool registration."""
    print("=" * 60)
    print("Testing Agent as Tool Registration")
    print("=" * 60)
    
    # Initialize tool system
    print("\n1. Initializing tool system...")
    try:
        from backend.tools.tool_discovery import init_tool_system
        registry = init_tool_system()
        print(f"   ✓ Tool system initialized")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # List all tools
    print("\n2. Registered Tools:")
    print("-" * 60)
    tool_ids = registry.list_tools()
    print(f"   Total tools: {len(tool_ids)}")
    
    # Separate function tools and agent_as_tools
    function_tools = []
    agent_as_tools = []
    
    for tool_id in tool_ids:
        metadata = registry.get_tool_metadata(tool_id)
        if metadata:
            if metadata.tool_type == "function":
                function_tools.append(tool_id)
            elif metadata.tool_type == "agent_as_tool":
                agent_as_tools.append(tool_id)
    
    print(f"\n   Function Tools: {len(function_tools)}")
    for tool_id in function_tools:
        print(f"     - {tool_id}")
    
    print(f"\n   Agent as Tools: {len(agent_as_tools)}")
    for tool_id in agent_as_tools:
        metadata = registry.get_tool_metadata(tool_id)
        if metadata and hasattr(metadata, 'agent_class_name'):
            print(f"     - {tool_id} ({metadata.agent_class_name})")
        else:
            print(f"     - {tool_id}")
    
    # Verify agent_as_tool metadata
    print("\n3. Agent as Tool Metadata:")
    print("-" * 60)
    for tool_id in agent_as_tools:
        metadata = registry.get_tool_metadata(tool_id)
        if metadata:
            print(f"\n   {tool_id}:")
            print(f"     Name: {metadata.name}")
            print(f"     Agent Class: {metadata.agent_class_name}")
            print(f"     Description: {metadata.description[:60]}...")
            print(f"     Input Params: {list(metadata.input_params.keys())}")
            print(f"     Output Type: {metadata.output_type}")
    
    # Test database sync
    print("\n4. Testing Database Sync:")
    print("-" * 60)
    try:
        registry.sync_to_database()
        print("   ✓ Tools synced to database")
        
        # Verify in database
        from backend.database.tools_db import get_all_tools
        db_tools = get_all_tools()
        
        # Filter agent_as_tool types
        db_agent_as_tools = [t for t in db_tools if t.get('tool_type') == 'agent_as_tool']
        print(f"   ✓ Found {len(db_agent_as_tools)} agent_as_tool in database")
        
        # Check each registered agent_as_tool
        for tool_id in agent_as_tools:
            db_tool = next((t for t in db_tools if t['id'] == tool_id), None)
            if db_tool:
                print(f"     ✓ {tool_id} found in database")
                if db_tool.get('agent_class_name'):
                    print(f"       Agent Class: {db_tool['agent_class_name']}")
            else:
                print(f"     ✗ {tool_id} NOT found in database")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  - Function tools registered: {len(function_tools)}")
    print(f"  - Agent as tools registered: {len(agent_as_tools)}")
    print(f"  - Expected agent_as_tools: 6")
    
    if len(agent_as_tools) == 6:
        print("  ✓ All specialized agents registered successfully!")
    else:
        print(f"  ⚠ Expected 6 agent_as_tools, found {len(agent_as_tools)}")


if __name__ == "__main__":
    test_agent_as_tool_registration()

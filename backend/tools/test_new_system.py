"""Test script for the new tool registry system."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_tool_registry():
    """Test the new tool registry system."""
    print("=" * 60)
    print("Testing New Tool Registry System")
    print("=" * 60)
    
    # Initialize tool system
    print("\n1. Initializing tool system...")
    try:
        from backend.tools.tool_discovery import init_tool_system
        registry = init_tool_system()
        print(f"   ✓ Tool system initialized")
        print(f"   ✓ Registry instance created")
    except Exception as e:
        print(f"   ✗ Failed to initialize: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # List registered tools
    print("\n2. Registered Tools:")
    print("-" * 60)
    tool_ids = registry.list_tools()
    print(f"   Total tools: {len(tool_ids)}")
    for tool_id in tool_ids:
        metadata = registry.get_tool_metadata(tool_id)
        if metadata:
            print(f"   - {tool_id} ({metadata.tool_type})")
            print(f"     Name: {metadata.name}")
            print(f"     Agent Types: {metadata.agent_types}")
    
    # Test creating tools
    print("\n3. Testing Tool Creation:")
    print("-" * 60)
    
    # Create a mock agent
    class MockAgent:
        def __init__(self):
            self.id = "test-agent-123"
            self.name = "TestAgent"
            self.DB_PATH = None
            self.sub_agent_ids = []
        
        def load_agent_from_db_by_id(self, agent_id):
            return None
        
        def run_async_safely(self, coro):
            return "Mock result"
        
        def _add_sub_agents(self, agent_id):
            pass
    
    mock_agent = MockAgent()
    
    # Test creating each tool
    success_count = 0
    for tool_id in tool_ids:
        print(f"\n   Testing {tool_id}...")
        try:
            tool = registry.create_tool(tool_id, mock_agent)
            if tool:
                print(f"     ✓ Successfully created")
                success_count += 1
            else:
                print(f"     ✗ Failed to create (may be expected due to missing agent attributes)")
        except Exception as e:
            print(f"     ✗ Error: {e}")
    
    print(f"\n   Summary: {success_count}/{len(tool_ids)} tools created successfully")
    
    # Test database sync
    print("\n4. Testing Database Sync:")
    print("-" * 60)
    try:
        registry.sync_to_database()
        print("   ✓ Tools synced to database")
        
        # Verify in database
        from backend.database.tools_db import get_all_tools
        db_tools = get_all_tools()
        print(f"   ✓ Found {len(db_tools)} tools in database")
        
        # Check if our tools are in database
        db_tool_ids = [t['id'] for t in db_tools]
        for tool_id in tool_ids:
            if tool_id in db_tool_ids:
                print(f"     ✓ {tool_id} found in database")
            else:
                print(f"     ✗ {tool_id} NOT found in database")
    except Exception as e:
        print(f"   ✗ Failed to sync: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_tool_registry()

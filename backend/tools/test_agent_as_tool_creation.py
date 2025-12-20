"""Test script to verify agent_as_tool creation logic."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_agent_as_tool_creation():
    """Test agent_as_tool creation."""
    print("=" * 60)
    print("Testing Agent as Tool Creation")
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
    
    # Get agent_as_tool metadata
    print("\n2. Agent as Tool Metadata:")
    print("-" * 60)
    agent_as_tool_ids = [
        "outline_maker_agent",
        "intent_extraction_agent",
    ]
    
    for tool_id in agent_as_tool_ids:
        metadata = registry.get_tool_metadata(tool_id)
        if metadata and metadata.tool_type == "agent_as_tool":
            print(f"\n   {tool_id}:")
            print(f"     Agent Class: {metadata.agent_class_name}")
            print(f"     Required Params: {[p for p, info in metadata.input_params.items() if info.required]}")
            print(f"     Optional Params: {[p for p, info in metadata.input_params.items() if not info.required]}")
    
    # Test creating agent_as_tool
    print("\n3. Testing Agent as Tool Creation:")
    print("-" * 60)
    
    # Test 1: outline_maker_agent (needs file_path)
    print("\n   Test 1: outline_maker_agent")
    try:
        # Create a test file
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Document\n\nThis is a test document for outline generation.")
            test_file_path = f.name
        
        tool = registry.create_tool(
            "outline_maker_agent",
            agent=None,  # agent_as_tool doesn't need agent context
            file_path=test_file_path
        )
        
        if tool:
            print(f"     ✓ Successfully created agent_as_tool")
            print(f"     Tool type: {type(tool).__name__}")
            if hasattr(tool, 'name'):
                print(f"     Tool name: {tool.name}")
        else:
            print(f"     ✗ Failed to create (returned None)")
        
        # Cleanup
        os.unlink(test_file_path)
        
    except Exception as e:
        print(f"     ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: intent_extraction_agent (needs user_request)
    print("\n   Test 2: intent_extraction_agent")
    try:
        tool = registry.create_tool(
            "intent_extraction_agent",
            agent=None,
            user_request="Create a notebook about Python programming",
            file_path=None
        )
        
        if tool:
            print(f"     ✓ Successfully created agent_as_tool")
            print(f"     Tool type: {type(tool).__name__}")
        else:
            print(f"     ✗ Failed to create (returned None)")
        
    except Exception as e:
        print(f"     ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Missing required parameter
    print("\n   Test 3: Missing required parameter")
    try:
        tool = registry.create_tool(
            "outline_maker_agent",
            agent=None
            # Missing file_path parameter
        )
        
        if tool:
            print(f"     ✗ Should have failed but succeeded")
        else:
            print(f"     ✓ Correctly rejected (missing required parameter)")
        
    except Exception as e:
        print(f"     ✓ Correctly raised error: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_agent_as_tool_creation()


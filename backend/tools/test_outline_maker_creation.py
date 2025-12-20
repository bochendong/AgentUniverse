"""Test script to debug outline_maker_agent creation issue."""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from backend.tools.tool_registry import get_tool_registry
from backend.agent.TopLevelAgent import TopLevelAgent

def test_outline_maker_creation():
    """Test creating outline_maker_agent tool."""
    file_path = "/Users/dongpochen/Github/AgentUniverse/uploads/d0550a97_group.md"
    
    print(f"Testing outline_maker_agent creation with file: {file_path}")
    print(f"File exists: {Path(file_path).exists()}")
    print(f"File is file: {Path(file_path).is_file()}")
    
    # Create a TopLevelAgent instance
    print("\n1. Creating TopLevelAgent...")
    try:
        top_level_agent = TopLevelAgent()
        print(f"✓ TopLevelAgent created: {top_level_agent.id}")
    except Exception as e:
        print(f"✗ Failed to create TopLevelAgent: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Get tool registry
    print("\n2. Getting tool registry...")
    registry = get_tool_registry()
    
    # Check if outline_maker_agent is registered
    print("\n3. Checking if outline_maker_agent is registered...")
    if "outline_maker_agent" in registry._agent_as_tools:
        print("✓ outline_maker_agent is registered")
        metadata = registry._agent_as_tools["outline_maker_agent"]
        print(f"  - Agent class: {metadata.agent_class}")
        print(f"  - Agent class name: {metadata.agent_class_name}")
        print(f"  - Input params: {metadata.input_params}")
    else:
        print("✗ outline_maker_agent is NOT registered")
        print(f"  Available agent_as_tools: {list(registry._agent_as_tools.keys())}")
        return
    
    # Try to create the tool
    print("\n4. Creating outline_maker_agent tool...")
    try:
        outline_tool = registry.create_tool(
            "outline_maker_agent",
            agent=top_level_agent,
            file_path=file_path
        )
        
        if outline_tool:
            print("✓ outline_maker_agent tool created successfully")
            print(f"  - Tool type: {type(outline_tool)}")
            if hasattr(outline_tool, '_agent_instance'):
                print(f"  - Agent instance: {outline_tool._agent_instance}")
        else:
            print("✗ Failed to create outline_maker_agent tool (returned None)")
    except Exception as e:
        print(f"✗ Exception while creating outline_maker_agent tool: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_outline_maker_creation()


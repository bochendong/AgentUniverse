"""
Quick check script to verify TopLevelAgent tools are correctly created.
Run this after backend starts to check if required tools exist.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from backend.agent.TopLevelAgent import TopLevelAgent
from backend.tools.tool_registry import get_tool_registry


def check_tools():
    """Check if TopLevelAgent has all required tools."""
    print("=" * 80)
    print("Checking TopLevelAgent Tools")
    print("=" * 80)
    
    # Get TopLevelAgent
    print("\n[1] Loading TopLevelAgent...")
    try:
        top_agent = TopLevelAgent()
        print(f"✓ TopLevelAgent loaded: {top_agent.id}")
    except Exception as e:
        print(f"✗ Failed to load TopLevelAgent: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check tools
    print("\n[2] Checking tools...")
    if not top_agent.tools:
        print("✗ TopLevelAgent has no tools!")
        return False
    
    print(f"✓ TopLevelAgent has {len(top_agent.tools)} tools")
    
    # List all tools
    tool_names = []
    for tool in top_agent.tools:
        tool_id = getattr(tool, '_tool_id', 'unknown')
        tool_name = getattr(tool, 'name', 'unknown')
        tool_names.append(tool_id)
        print(f"  - {tool_id} ({tool_name})")
    
    # Check for required tools
    required_tools = ['send_message', 'generate_outline']
    print("\n[3] Checking for required tools...")
    missing_tools = []
    for req_tool in required_tools:
        if req_tool in tool_names:
            print(f"  ✓ {req_tool}")
        else:
            print(f"  ✗ {req_tool} - MISSING!")
            missing_tools.append(req_tool)
    
    # Check tool registry
    print("\n[4] Checking tool registry...")
    registry = get_tool_registry()
    all_tools = registry.list_tools()
    print(f"  - Total tools in registry: {len(all_tools)}")
    
    for req_tool in required_tools:
        if req_tool in all_tools:
            print(f"  ✓ {req_tool} is registered")
        else:
            print(f"  ✗ {req_tool} is NOT registered!")
    
    # Try to create the missing tool
    if missing_tools:
        print("\n[5] Attempting to create missing tools...")
        for tool_id in missing_tools:
            print(f"\n  Trying to create {tool_id}...")
            tool = registry.create_tool(tool_id, top_agent)
            if tool:
                print(f"  ✓ Successfully created {tool_id}")
                top_agent.tools.append(tool)
            else:
                print(f"  ✗ Failed to create {tool_id}")
                print(f"     Check the logs above for error details")
    
    print("\n" + "=" * 80)
    if missing_tools:
        print("❌ Some tools are missing!")
        print(f"Missing: {', '.join(missing_tools)}")
        return False
    else:
        print("✅ All required tools are present!")
        return True


if __name__ == "__main__":
    result = check_tools()
    sys.exit(0 if result else 1)

"""Cleanup old tools from database that are no longer registered."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.tools.tool_discovery import init_tool_system
from backend.tools.tool_registry import get_tool_registry
from backend.database.tools_db import get_all_tools, delete_tool


def cleanup_old_tools():
    """Remove tools from database that are no longer registered."""
    print("=" * 60)
    print("Cleaning up old tools from database...")
    print("=" * 60)
    
    # Initialize tool system to register all current tools
    print("\n1. Initializing tool system...")
    init_tool_system()
    
    # Get registry
    registry = get_tool_registry()
    registered_tool_ids = set(registry.list_tools())
    
    print(f"   Found {len(registered_tool_ids)} registered tools:")
    for tool_id in sorted(registered_tool_ids):
        print(f"     - {tool_id}")
    
    # Get all tools from database
    print("\n2. Loading tools from database...")
    db_tools = get_all_tools()
    db_tool_ids = {tool['id'] for tool in db_tools}
    
    print(f"   Found {len(db_tool_ids)} tools in database:")
    for tool_id in sorted(db_tool_ids):
        tool = next(t for t in db_tools if t['id'] == tool_id)
        print(f"     - {tool_id} ({tool.get('name', 'N/A')})")
    
    # Find tools to delete (in database but not in registry)
    tools_to_delete = db_tool_ids - registered_tool_ids
    
    if not tools_to_delete:
        print("\n3. No old tools to delete. Database is clean!")
        print("=" * 60)
        return
    
    print(f"\n3. Found {len(tools_to_delete)} old tools to delete:")
    for tool_id in sorted(tools_to_delete):
        tool = next(t for t in db_tools if t['id'] == tool_id)
        print(f"     - {tool_id} ({tool.get('name', 'N/A')})")
    
    # Confirm deletion
    print("\n4. Deleting old tools...")
    deleted_count = 0
    for tool_id in sorted(tools_to_delete):
        if delete_tool(tool_id):
            deleted_count += 1
            print(f"   ✓ Deleted: {tool_id}")
        else:
            print(f"   ✗ Failed to delete: {tool_id}")
    
    print(f"\n5. Deleted {deleted_count} old tools.")
    
    # Re-sync tools to database
    print("\n6. Re-syncing tools to database...")
    registry.sync_to_database()
    
    # Verify
    print("\n7. Verifying cleanup...")
    final_db_tools = get_all_tools()
    final_db_tool_ids = {tool['id'] for tool in final_db_tools}
    
    print(f"   Database now contains {len(final_db_tool_ids)} tools:")
    for tool_id in sorted(final_db_tool_ids):
        tool = next(t for t in final_db_tools if t['id'] == tool_id)
        print(f"     - {tool_id} ({tool.get('name', 'N/A')})")
    
    if final_db_tool_ids == registered_tool_ids:
        print("\n✓ Cleanup successful! Database matches registered tools.")
    else:
        missing = registered_tool_ids - final_db_tool_ids
        extra = final_db_tool_ids - registered_tool_ids
        if missing:
            print(f"\n⚠ Warning: {len(missing)} registered tools missing from database:")
            for tool_id in missing:
                print(f"     - {tool_id}")
        if extra:
            print(f"\n⚠ Warning: {len(extra)} extra tools in database:")
            for tool_id in extra:
                print(f"     - {tool_id}")
    
    print("=" * 60)


if __name__ == "__main__":
    cleanup_old_tools()


#!/usr/bin/env python3
"""Simple script to export notebook content to markdown file by notebook ID.

This script loads the notebook directly from the database without requiring API.

Usage:
    python export_notebook_simple.py <notebook_id> [output_file]
    
Example:
    python export_notebook_simple.py d9198e26-8450-44b0-bb2a-c8b6daf482d
    python export_notebook_simple.py d9198e26-8450-44b0-bb2a-c8b6daf482d my_notebook.md
"""

import sys
import os
from datetime import datetime

# Add backend to path
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def export_notebook_by_id(notebook_id: str, output_file: str = None):
    """Export notebook markdown content by notebook ID from database.
    
    Args:
        notebook_id: The notebook agent ID
        output_file: Optional output file path. If not provided, will generate from notebook title or ID.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"📡 Loading notebook from database...")
        
        from backend.database.agent_db import load_agent
        from backend.agent.NoteBookAgent import NoteBookAgent
        from backend.tools.utils import generate_markdown_from_agent
        
        notebook_agent = load_agent(notebook_id)
        
        if not notebook_agent:
            print(f"❌ Notebook not found with ID: {notebook_id}")
            print(f"\n💡 Searching for similar IDs in database...")
            
            # Try to find notebooks with similar ID (maybe missing last character)
            from backend.database.agent_db import load_all_agents
            from backend.agent.NoteBookAgent import NoteBookAgent
            
            all_agents = load_all_agents()
            matching_ids = []
            for agent_id, agent in all_agents.items():
                if isinstance(agent, NoteBookAgent):
                    # Check if ID starts with the provided ID
                    if agent_id.startswith(notebook_id):
                        matching_ids.append((agent_id, agent))
                    # Also check if provided ID starts with agent_id (in case user provided partial ID)
                    elif notebook_id.startswith(agent_id[:len(notebook_id)]):
                        matching_ids.append((agent_id, agent))
            
            if matching_ids:
                print(f"\n✅ Found {len(matching_ids)} matching notebook(s):")
                for agent_id, agent in matching_ids:
                    title = getattr(agent, 'notebook_title', '') or 'N/A'
                    print(f"   - {title} (ID: {agent_id})")
                print(f"\n💡 Try using one of these IDs instead.")
            else:
                print(f"\n📋 Available notebooks in database:")
                notebook_count = 0
                for agent_id, agent in all_agents.items():
                    if isinstance(agent, NoteBookAgent):
                        notebook_count += 1
                        title = getattr(agent, 'notebook_title', '') or 'N/A'
                        print(f"   {notebook_count}. {title}")
                        print(f"      ID: {agent_id}")
                        # Check if ID is similar
                        if notebook_id[:20] in agent_id or agent_id[:20] in notebook_id:
                            print(f"      ⚠️  This ID looks similar to what you provided!")
                        print()
                
                if notebook_count == 0:
                    print(f"   (No notebooks found in database)")
            
            return False
        
        if not isinstance(notebook_agent, NoteBookAgent):
            agent_type = type(notebook_agent).__name__
            print(f"❌ Agent {notebook_id} is not a NotebookAgent (type: {agent_type})")
            return False
        
        # Get notebook title for filename if not provided
        notebook_title = getattr(notebook_agent, 'notebook_title', '') or ''
        if not output_file:
            if notebook_title:
                # Sanitize filename
                safe_title = "".join(c for c in notebook_title if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title.replace(' ', '_')
                output_file = f"{safe_title}_{notebook_id[:8]}.md"
            else:
                output_file = f"notebook_{notebook_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        print(f"📝 Notebook Title: {notebook_title or 'N/A'}")
        print(f"📄 Generating markdown with XML tags...")
        
        # Generate markdown with XML tags
        markdown_content = generate_markdown_from_agent(notebook_agent, include_ids=True)
        
        if not markdown_content:
            print("❌ No markdown content generated")
            return False
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"\n{'='*80}")
        print(f"✅ Success! Saved to: {output_file}")
        print(f"{'='*80}")
        print(f"\nContent length: {len(markdown_content)} characters")
        print(f"\nFirst 500 chars preview:\n")
        print(markdown_content[:500])
        if len(markdown_content) > 500:
            print(f"\n... (完整内容已保存到 {output_file})")
        
        # Check if XML tags are present
        xml_tags = ['<Section', '<Definition', '<Introduction', '<ConceptBlock', '<ExampleItem', '<Question', '<Answer', '<Theorem']
        found_tags = [tag for tag in xml_tags if tag in markdown_content]
        if found_tags:
            print(f"\n✅ Found XML tags: {', '.join(found_tags)}")
            for tag in found_tags:
                count = markdown_content.count(tag)
                print(f"   - {tag}: {count} occurrence(s)")
        else:
            print(f"\n⚠️  Warning: No XML tags found in content")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print(f"\n💡 Make sure you're running this script from the project root directory")
        print(f"   and that all dependencies are installed in the virtual environment.")
        print(f"\n   Try: source venv/bin/activate && python {sys.argv[0]} {notebook_id}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print(__doc__)
        print(f"\n❌ Error: Notebook ID is required")
        print(f"\nUsage: python {sys.argv[0]} <notebook_id> [output_file]")
        sys.exit(1)
    
    notebook_id = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"📚 Exporting notebook: {notebook_id}")
    if output_file:
        print(f"📄 Output file: {output_file}")
    print()
    
    success = export_notebook_by_id(notebook_id, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()


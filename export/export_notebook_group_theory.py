#!/usr/bin/env python3
"""Export notebook with XML format markdown directly from database."""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

NOTEBOOK_TITLE = "群论基础与群的结构特征（Group Theory）"
OUTPUT_FILE = "group_theory_export.md"

def find_and_export_notebook():
    """Find notebook by title and export markdown with XML tags."""
    try:
        from backend.database.agent_db import load_all_agents
        from backend.agent.NoteBookAgent import NoteBookAgent
        from backend.tools.utils import generate_markdown_from_agent
        
        print(f"📡 Loading all agents from database...")
        agents = load_all_agents()
        
        # Find notebook with matching title
        notebook_agent = None
        notebook_id = None
        for agent_id, agent in agents.items():
            if isinstance(agent, NoteBookAgent):
                notebook_title = getattr(agent, 'notebook_title', '') or ''
                if NOTEBOOK_TITLE in notebook_title or notebook_title == NOTEBOOK_TITLE:
                    notebook_agent = agent
                    notebook_id = agent_id
                    print(f"✅ Found notebook: {notebook_title} (ID: {notebook_id})")
                    break
        
        if not notebook_agent:
            print(f"❌ Notebook not found: {NOTEBOOK_TITLE}")
            print(f"\nAvailable notebooks:")
            for agent_id, agent in agents.items():
                if isinstance(agent, NoteBookAgent):
                    notebook_title = getattr(agent, 'notebook_title', '') or 'N/A'
                    print(f"  - {notebook_title} (ID: {agent_id})")
            return False
        
        # Generate markdown with XML tags
        print(f"\n📝 Generating markdown with XML tags...")
        markdown_content = generate_markdown_from_agent(notebook_agent, include_ids=True)
        
        if not markdown_content:
            print("❌ No markdown content generated")
            return False
        
        # Save to file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"\n{'='*80}")
        print(f"✅ Success! Saved to: {OUTPUT_FILE}")
        print(f"{'='*80}")
        print(f"\nContent length: {len(markdown_content)} characters")
        print(f"\nFirst 500 chars preview:\n")
        print(markdown_content[:500])
        if len(markdown_content) > 500:
            print(f"\n... (完整内容已保存到 {OUTPUT_FILE})")
        
        # Check if XML tags are present
        xml_tags = ['<Section', '<Definition', '<Introduction', '<ConceptBlock', '<ExampleItem', '<Question', '<Answer', '<Theorem']
        found_tags = [tag for tag in xml_tags if tag in markdown_content]
        if found_tags:
            print(f"\n✅ Found XML tags: {', '.join(found_tags)}")
            # Count tag occurrences
            for tag in found_tags:
                count = markdown_content.count(tag)
                print(f"   - {tag}: {count} occurrence(s)")
        else:
            print(f"\n⚠️  Warning: No XML tags found in content")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = find_and_export_notebook()
    sys.exit(0 if success else 1)

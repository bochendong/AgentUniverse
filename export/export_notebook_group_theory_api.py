#!/usr/bin/env python3
"""Export notebook with XML format markdown via API."""

import sys
import requests

API_BASE_URL = "http://localhost:8000"
NOTEBOOK_TITLE = "群论基础与群的结构特征（Group Theory Essentials and Structure）"
OUTPUT_FILE = "group_theory_export.md"

def find_notebook_id_by_title(title):
    """Find notebook ID by title from API."""
    try:
        print(f"📡 Searching for notebook: {title}")
        # List all agents
        agents_url = f"{API_BASE_URL}/api/agents"
        agents_resp = requests.get(agents_url, timeout=30)
        
        if agents_resp.status_code != 200:
            print(f"❌ Agents API returned status code: {agents_resp.status_code}")
            print(f"Response: {agents_resp.text}")
            return None
        
        agents_data = agents_resp.json()
        agents = agents_data if isinstance(agents_data, list) else agents_data.get('data', [])
        
        # Find notebook with matching title
        for agent in agents:
            notebook_title = agent.get('notebook_title') or agent.get('title') or ''
            agent_id = agent.get('id') or agent.get('notebook_id') or ''
            if title in notebook_title or notebook_title == title or "群论基础" in notebook_title:
                print(f"✅ Found notebook: {notebook_title} (ID: {agent_id})")
                return agent_id
        
        print(f"❌ Notebook not found: {title}")
        print(f"\nAvailable notebooks:")
        for agent in agents:
            notebook_title = agent.get('notebook_title') or agent.get('title') or 'N/A'
            agent_type = agent.get('agent_type') or agent.get('type') or 'unknown'
            if 'notebook' in agent_type.lower():
                print(f"  - {notebook_title} (ID: {agent.get('id') or agent.get('notebook_id')})")
        return None
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to API at {API_BASE_URL}")
        print(f"   Make sure the backend server is running!")
        return None
    except Exception as e:
        print(f"❌ Error finding notebook: {e}")
        import traceback
        traceback.print_exc()
        return None

def export_notebook_markdown(notebook_id):
    """Export notebook markdown with XML tags."""
    try:
        print(f"\n📡 Getting notebook markdown content (with XML tags)...")
        # Use the new format=markdown parameter to get XML-tagged markdown
        content_url = f"{API_BASE_URL}/api/notebooks/{notebook_id}/content?format=markdown"
        content_resp = requests.get(content_url, timeout=30)
        
        if content_resp.status_code != 200:
            print(f"❌ Content API returned status code: {content_resp.status_code}")
            print(f"Response: {content_resp.text}")
            return False
        
        content_data = content_resp.json()
        markdown_content = content_data.get('content', '')
        
        if not markdown_content:
            print("❌ No markdown content found")
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

def main():
    """Main function."""
    # Find notebook ID
    notebook_id = find_notebook_id_by_title(NOTEBOOK_TITLE)
    if not notebook_id:
        print(f"\n❌ Could not find notebook: {NOTEBOOK_TITLE}")
        sys.exit(1)
    
    # Export markdown
    success = export_notebook_markdown(notebook_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

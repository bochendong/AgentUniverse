#!/usr/bin/env python3
"""Export notebook content to markdown file by notebook ID.

Usage:
    python export_notebook.py <notebook_id> [output_file]
    
Example:
    python export_notebook.py d9198e26-8450-44b0-bb2a-c8b6daf482d
    python export_notebook.py d9198e26-8450-44b0-bb2a-c8b6daf482d my_notebook.md
"""

import sys
import os
import requests
from datetime import datetime

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def export_notebook_by_id(notebook_id: str, output_file: str = None, use_api: bool = True):
    """Export notebook markdown content by notebook ID.
    
    Args:
        notebook_id: The notebook agent ID
        output_file: Optional output file path. If not provided, will generate from notebook title or ID.
        use_api: Whether to try API first (default: True). Set to False to skip API and use database directly.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Method 1: Try to get content via API endpoint (if enabled and available)
        if use_api:
            try:
                print(f"📡 Method 1: Getting notebook content via API endpoint...")
                content_url = f"{API_BASE_URL}/api/notebooks/{notebook_id}/content?format=markdown"
                content_resp = requests.get(content_url, timeout=5)
                
                if content_resp.status_code == 200:
                    content_data = content_resp.json()
                    markdown_content = content_data.get('content', '')
                    
                    if markdown_content:
                        # Get notebook title for filename if not provided
                        if not output_file:
                            # Try to get notebook info to get title
                            try:
                                notebook_url = f"{API_BASE_URL}/api/notebooks/{notebook_id}"
                                notebook_resp = requests.get(notebook_url, timeout=5)
                                if notebook_resp.status_code == 200:
                                    notebook_data = notebook_resp.json()
                                    notebook_title = notebook_data.get('notebook_title', '')
                                    if notebook_title:
                                        # Sanitize filename
                                        safe_title = "".join(c for c in notebook_title if c.isalnum() or c in (' ', '-', '_')).strip()
                                        safe_title = safe_title.replace(' ', '_')
                                        output_file = f"{safe_title}_{notebook_id[:8]}.md"
                            except:
                                pass
                            
                            if not output_file:
                                output_file = f"notebook_{notebook_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                        
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
                        
                        return True
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                print(f"⚠️  API not available, falling back to database method...")
            except Exception as e:
                print(f"⚠️  API method failed: {e}, falling back to database method...")
        
        # Method 2: Load from database directly
        print(f"\n📡 Loading notebook directly from database...")
        
        # Add project root and backend to path
        project_root = os.path.dirname(os.path.abspath(__file__))
        backend_path = os.path.join(project_root, 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from backend.database.agent_db import load_agent
        from backend.agent.NoteBookAgent import NoteBookAgent
        from backend.tools.utils import generate_markdown_from_agent
        
        notebook_agent = load_agent(notebook_id)
        
        if not notebook_agent:
            print(f"❌ Notebook not found with ID: {notebook_id}")
            return False
        
        if not isinstance(notebook_agent, NoteBookAgent):
            print(f"❌ Agent {notebook_id} is not a NotebookAgent (type: {type(notebook_agent).__name__})")
            return False
        
        # Generate markdown with XML tags
        print(f"📝 Generating markdown with XML tags...")
        markdown_content = generate_markdown_from_agent(notebook_agent, include_ids=True)
        
        if not markdown_content:
            print("❌ No markdown content generated")
            return False
        
        # Get notebook title for filename if not provided
        if not output_file:
            notebook_title = getattr(notebook_agent, 'notebook_title', '') or ''
            if notebook_title:
                safe_title = "".join(c for c in notebook_title if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title.replace(' ', '_')
                output_file = f"{safe_title}_{notebook_id[:8]}.md"
            else:
                output_file = f"notebook_{notebook_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
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
        
        return True
        
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
    print(f"🌐 API Base URL: {API_BASE_URL}\n")
    
    success = export_notebook_by_id(notebook_id, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()


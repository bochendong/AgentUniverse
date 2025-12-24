#!/usr/bin/env python3
"""Export notebook via API - extract markdown from instructions."""

import sys
import os
import requests
import re

# Notebook ID
NOTEBOOK_ID = "21cf91db-2344-4699-99e6-d96da2ff542c"
API_BASE_URL = "http://localhost:8000"
OUTPUT_FILE = "temp_notebook_21cf91db_export.md"

def extract_notes_from_instructions(instructions):
    """Extract notes content from instructions (look for {notes} variable content)."""
    # Instructions template contains {notes} placeholder
    # The actual notes content should be after the placeholder replacement
    # Look for content between markdown headers or after specific patterns
    # For notebook_agent, notes usually appear after a header like "# Notebook Content" or similar
    
    # Try to find the notes section in instructions
    # Pattern: look for content that looks like notebook markdown
    # The notes usually start after some prompt text
    
    # Simple approach: look for markdown headers (# or ##) which indicate notebook content
    lines = instructions.split('\n')
    notes_start = None
    
    # Look for patterns that indicate the start of actual notebook content
    for i, line in enumerate(lines):
        # Notebook content usually starts with a title like "# {notebook_title}"
        if line.strip().startswith('# ') and '函数' in line:
            notes_start = i
            break
        # Or look for Section tags
        if '<Section' in line:
            notes_start = i
            break
    
    if notes_start:
        return '\n'.join(lines[notes_start:])
    
    # Fallback: return full instructions if we can't find the start
    return instructions

def export_notebook():
    """Get notebook markdown from API."""
    try:
        # Get instructions which contain the notes
        print(f"📡 Getting notebook instructions from API...")
        instructions_url = f"{API_BASE_URL}/api/agents/{NOTEBOOK_ID}/instructions"
        instructions_resp = requests.get(instructions_url, timeout=30)
        
        if instructions_resp.status_code != 200:
            print(f"❌ Instructions API returned status code: {instructions_resp.status_code}")
            print(f"Response: {instructions_resp.text}")
            return False
        
        instructions_data = instructions_resp.json()
        current_instructions = instructions_data.get('current_instructions', '')
        
        if not current_instructions:
            print("❌ No instructions found")
            return False
        
        # Extract notes from instructions
        # The notes are embedded in the instructions template with {notes} variable
        # Look for the actual notebook content
        notes = extract_notes_from_instructions(current_instructions)
        
        # If extraction didn't work well, try a more aggressive approach
        # Look for content between certain markers or after prompt text
        if len(notes) == len(current_instructions):
            # Extraction didn't narrow it down, try pattern matching
            # Look for content that starts with notebook title or Section tag
            match = re.search(r'(<Section[^>]*>|#\s+[^\n]+\n)', current_instructions, re.MULTILINE)
            if match:
                notes = current_instructions[match.start():]
            else:
                # Last resort: look for markdown that looks like notebook content
                # Find the first line that starts with # (notebook title)
                for line in current_instructions.split('\n'):
                    if line.strip().startswith('# ') and len(line.strip()) > 5:
                        start_idx = current_instructions.find(line)
                        notes = current_instructions[start_idx:]
                        break
        
        # Save to file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(notes)
        
        print(f"\n{'='*80}")
        print(f"✅ Success! Saved to: {OUTPUT_FILE}")
        print(f"{'='*80}")
        print(f"\nContent length: {len(notes)} characters")
        print(f"Preview (first 2000 chars):\n")
        print(notes[:2000])
        if len(notes) > 2000:
            print(f"\n... (完整内容已保存到 {OUTPUT_FILE})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = export_notebook()
    sys.exit(0 if success else 1)

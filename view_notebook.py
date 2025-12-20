#!/usr/bin/env python3
"""Script to view notebook content from database."""

import sys
import os
import sqlite3
import pickle
import re

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Database path
DB_DIR = os.path.join(os.path.dirname(__file__), "backend", "database", "db")
DB_PATH = os.path.join(DB_DIR, "agent_data.db")

# Agent ID for 群论笔记
NOTEBOOK_ID = "aeb8b7c3-2f5b-420e-9922-2e4ecb54fa8e"

def view_notebook(agent_id):
    """Load and view notebook agent from database."""
    if not os.path.exists(DB_PATH):
        print(f"Database not found at: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get agent data
    cursor.execute("SELECT name, data FROM agents WHERE id = ?", (agent_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print(f"Agent {agent_id} not found in database")
        return
    
    name, agent_data = row
    print(f"Agent Name: {name}\n")
    
    # Try to deserialize agent (this might fail due to imports, but we can try)
    try:
        agent = pickle.loads(agent_data)
        
        # Try to get notes
        if hasattr(agent, 'notes') and agent.notes:
            notes = agent.notes
            print("=" * 80)
            print("NOTES CONTENT:")
            print("=" * 80)
            
            # Search for the specific proofs mentioned by user
            # 1. 单位元唯一性证明
            print("\n" + "=" * 80)
            print("查找：单位元唯一性证明")
            print("=" * 80)
            patterns = [
                r'单位元.*?唯一.*?(?=\n\n|\n#|\Z)',
                r'练习题.*?单位元.*?唯一.*?(?=\n\n|\n#|\Z)',
            ]
            found = False
            for pattern in patterns:
                matches = re.finditer(pattern, notes, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    found = True
                    start = max(0, match.start() - 100)
                    end = min(len(notes), match.end() + 100)
                    context = notes[start:end]
                    print(f"\n找到匹配 (位置 {match.start()}-{match.end()}):")
                    print("-" * 80)
                    print(context)
                    print("-" * 80)
                    break
                if found:
                    break
            
            if not found:
                # Try to find by keyword
                if '单位元' in notes and '唯一' in notes:
                    idx1 = notes.find('单位元')
                    idx2 = notes.find('唯一', idx1)
                    if idx2 > idx1:
                        start = max(0, idx1 - 200)
                        end = min(len(notes), idx2 + 500)
                        print(notes[start:end])
            
            # 2. 阿贝尔群相关证明
            print("\n" + "=" * 80)
            print("查找：阿贝尔群定理证明 (如果 (ab)^(-1) = a^(-1)b^(-1)，则G是阿贝尔群)")
            print("=" * 80)
            abelian_patterns = [
                r'如果.*?对于.*?任意.*?a.*?b.*?G.*?都有.*?\(ab\)\s*[−-]\s*1.*?=.*?a\s*[−-]\s*1.*?b\s*[−-]\s*1.*?则.*?G.*?是.*?阿贝尔群.*?(?=\n\n|\n#|\Z)',
                r'Theorem.*?If.*?\(ab\)\s*[−-]\s*1.*?=.*?a\s*[−-]\s*1.*?b\s*[−-]\s*1.*?则.*?G.*?是.*?阿贝尔群.*?(?=\n\n|\n#|\Z)',
            ]
            found = False
            for pattern in abelian_patterns:
                matches = re.finditer(pattern, notes, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    found = True
                    start = max(0, match.start() - 100)
                    end = min(len(notes), match.end() + 200)
                    context = notes[start:end]
                    print(f"\n找到匹配 (位置 {match.start()}-{match.end()}):")
                    print("-" * 80)
                    print(context)
                    print("-" * 80)
                    break
                if found:
                    break
            
            if not found:
                # Try simpler search
                if '(ab)' in notes and '阿贝尔' in notes:
                    idx = notes.find('(ab)')
                    if idx > 0:
                        start = max(0, idx - 300)
                        end = min(len(notes), idx + 1000)
                        snippet = notes[start:end]
                        if '阿贝尔' in snippet:
                            print(snippet)
            
            # Also show full notes if requested
            print("\n" + "=" * 80)
            print("完整笔记内容 (前2000字符):")
            print("=" * 80)
            print(notes[:2000])
            if len(notes) > 2000:
                print(f"\n... (还有 {len(notes) - 2000} 字符)")
        else:
            print("No notes found in agent")
            
        # Check if has sections
        if hasattr(agent, 'sections') and agent.sections:
            print("\n" + "=" * 80)
            print("SECTIONS STRUCTURE:")
            print("=" * 80)
            for section_title, section in agent.sections.items():
                print(f"\nSection: {section_title}")
                if hasattr(section, 'exercises') and section.exercises:
                    print(f"  Exercises: {len(section.exercises)}")
                    for i, ex in enumerate(section.exercises, 1):
                        if hasattr(ex, 'question') and '单位元' in str(ex.question):
                            print(f"    Exercise {i}: {ex.question}")
    except Exception as e:
        print(f"Error deserializing agent: {e}")
        print("\nTrying to extract notes directly from pickle data...")
        # Try to extract raw string data
        import io
        data_str = str(agent_data)
        if '单位元' in data_str:
            idx = data_str.find('单位元')
            print(data_str[max(0, idx-500):idx+1000])

if __name__ == "__main__":
    view_notebook(NOTEBOOK_ID)

"""
Test TopLevelAgent tool selection logic.
Verifies that TopLevelAgent uses create_notebook_from_outline instead of send_message
when user confirms outline.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)


def test_tool_selection_logic():
    """Test that the tool selection logic is correct."""
    print("=" * 80)
    print("Test: TopLevelAgent Tool Selection Logic")
    print("=" * 80)
    
    # Read the prompt file
    prompt_file = project_root / "backend" / "prompts" / "top_level_agent.md"
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_content = f.read()
    
    print("\n[1] Checking prompt for tool selection guidance...")
    
    # Check for key phrases
    checks = {
        "create_notebook_from_outline mentioned": "create_notebook_from_outline" in prompt_content,
        "Don't use send_message for outline confirmation": "不要使用 `send_message`" in prompt_content or "不要使用send_message" in prompt_content,
        "Must call tool explicitly": "必须实际调用工具" in prompt_content or "必须立即调用" in prompt_content,
        "File upload workflow defined": "文件上传和Notebook创建流程" in prompt_content or "文件上传和笔记本创建" in prompt_content,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    # Check tool description
    print("\n[2] Checking tool description...")
    tool_file = project_root / "backend" / "tools" / "agent_tools.py"
    with open(tool_file, 'r', encoding='utf-8') as f:
        tool_content = f.read()
    
    # Find create_notebook_from_outline tool definition
    if "create_notebook_from_outline" in tool_content:
        # Check if description mentions not using send_message
        tool_start = tool_content.find('tool_id="create_notebook_from_outline"')
        if tool_start != -1:
            tool_section = tool_content[tool_start:tool_start+2000]
            if "不要使用send_message" in tool_section or "不要使用 `send_message`" in tool_section:
                print("  ✓ Tool description explicitly mentions not using send_message")
            else:
                print("  ⚠ Tool description doesn't explicitly mention not using send_message")
                all_passed = False
    
    # Check send_message error handling
    print("\n[3] Checking send_message error handling...")
    if "create_notebook_from_outline" in tool_content.lower():
        send_msg_start = tool_content.find('def send_message(id: str, message: str)')
        if send_msg_start != -1:
            send_msg_section = tool_content[send_msg_start:send_msg_start+1000]
            if "create_notebook_from_outline" in send_msg_section.lower():
                print("  ✓ send_message error message mentions create_notebook_from_outline")
            else:
                print("  ⚠ send_message error message doesn't mention create_notebook_from_outline")
    
    print("\n" + "=" * 80)
    print("Test Summary:")
    print("=" * 80)
    if all_passed:
        print("✓ All checks passed! The prompt and tools are correctly configured.")
    else:
        print("⚠ Some checks failed. Please review the prompt and tool descriptions.")
    
    return all_passed


if __name__ == "__main__":
    result = test_tool_selection_logic()
    sys.exit(0 if result else 1)

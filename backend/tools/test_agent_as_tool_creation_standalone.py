"""Standalone test for agent_as_tool creation logic - no external dependencies."""

import sys
import importlib.util
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Mock agents module
class MockAgent:
    def __init__(self, name, instructions, **kwargs):
        self.name = name
        self.instructions = instructions
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def as_tool(self, tool_name=None, tool_description=None):
        """Mock as_tool method."""
        class MockTool:
            def __init__(self, name, description, agent_instance):
                self.name = name
                self.description = description
                self._agent_instance = agent_instance
        return MockTool(tool_name or self.name, tool_description or "", self)

def mock_function_tool(func):
    """Mock function_tool decorator."""
    func._is_function_tool = True
    return func

# Create mock agents module
mock_agents = type(sys)('agents')
mock_agents.Agent = MockAgent
mock_agents.function_tool = mock_function_tool
sys.modules['agents'] = mock_agents

# Load tool_registry module directly
spec = importlib.util.spec_from_file_location(
    "tool_registry",
    project_root / "backend" / "tools" / "tool_registry.py"
)
tool_registry_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool_registry_module)

# Load register_specialized_agents
spec = importlib.util.spec_from_file_location(
    "register_specialized_agents",
    project_root / "backend" / "tools" / "register_specialized_agents.py"
)
register_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(register_module)

# Get registry
registry = tool_registry_module.get_tool_registry()


def test_agent_as_tool_creation():
    """Test agent_as_tool creation."""
    print("=" * 60)
    print("Testing Agent as Tool Creation Logic")
    print("=" * 60)
    
    # List registered tools
    print("\n1. Registered Tools:")
    print("-" * 60)
    tool_ids = registry.list_tools()
    print(f"   Total tools: {len(tool_ids)}")
    
    # Separate function tools and agent_as_tools
    function_tools = []
    agent_as_tools = []
    
    for tool_id in tool_ids:
        metadata = registry.get_tool_metadata(tool_id)
        if metadata:
            if metadata.tool_type == "function":
                function_tools.append(tool_id)
            elif metadata.tool_type == "agent_as_tool":
                agent_as_tools.append(tool_id)
    
    print(f"\n   Function Tools: {len(function_tools)}")
    print(f"   Agent as Tools: {len(agent_as_tools)}")
    
    if agent_as_tools:
        print(f"\n   Agent as Tool IDs:")
        for tool_id in agent_as_tools:
            print(f"     - {tool_id}")
    
    # Test creating agent_as_tool
    print("\n2. Testing Agent as Tool Creation:")
    print("-" * 60)
    
    # Test with a simple mock agent class
    class TestAgent(MockAgent):
        def __init__(self, file_path: str):
            super().__init__(
                name="TestAgent",
                instructions="Test agent",
                file_path=file_path
            )
    
    # Register a test agent_as_tool
    from backend.tools.tool_registry import AgentAsToolMetadata, ParamInfo
    
    test_metadata = AgentAsToolMetadata(
        tool_id="test_agent_as_tool",
        name="test_agent_as_tool",
        description="Test agent as tool",
        task="Test task",
        agent_types=["AsToolAgent"],
        input_params={
            "file_path": ParamInfo(
                type="str",
                description="File path",
                required=True
            ),
        },
        output_type="str",
        agent_class_name="TestAgent",
    )
    registry.register_agent_as_tool("test_agent_as_tool", TestAgent, test_metadata)
    
    # Test 1: Create with correct parameters
    print("\n   Test 1: Create with correct parameters")
    try:
        tool = registry.create_tool(
            "test_agent_as_tool",
            agent=None,
            file_path="/test/path.md"
        )
        
        if tool:
            print(f"     ✓ Successfully created agent_as_tool")
            print(f"     Tool name: {tool.name}")
            print(f"     Tool description: {tool.description}")
            if hasattr(tool, '_agent_instance'):
                print(f"     Agent instance: {tool._agent_instance.name}")
        else:
            print(f"     ✗ Failed to create (returned None)")
    except Exception as e:
        print(f"     ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Missing required parameter
    print("\n   Test 2: Missing required parameter")
    try:
        tool = registry.create_tool(
            "test_agent_as_tool",
            agent=None
            # Missing file_path parameter
        )
        
        if tool:
            print(f"     ✗ Should have failed but succeeded")
        else:
            print(f"     ✓ Correctly rejected (missing required parameter)")
    except Exception as e:
        print(f"     ✓ Correctly raised error: {e}")
    
    # Test 3: Extra parameters (should be ignored)
    print("\n   Test 3: Extra parameters (should be filtered)")
    try:
        tool = registry.create_tool(
            "test_agent_as_tool",
            agent=None,
            file_path="/test/path.md",
            extra_param="should be ignored"
        )
        
        if tool:
            print(f"     ✓ Successfully created (extra params filtered)")
            if hasattr(tool, '_agent_instance'):
                # Check that extra_param is not in agent instance
                if not hasattr(tool._agent_instance, 'extra_param'):
                    print(f"     ✓ Extra parameter correctly filtered")
                else:
                    print(f"     ⚠ Extra parameter was not filtered")
        else:
            print(f"     ✗ Failed to create")
    except Exception as e:
        print(f"     ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Check metadata for registered specialized agents
    print("\n3. Checking Registered Specialized Agents:")
    print("-" * 60)
    specialized_agent_ids = [
        "outline_maker_agent",
        "notebook_agent_creator",
        "exercise_refinement_agent",
        "proof_refinement_agent",
        "intent_extraction_agent",
        "outline_revision_agent",
    ]
    
    for tool_id in specialized_agent_ids:
        metadata = registry.get_tool_metadata(tool_id)
        if metadata:
            print(f"\n   {tool_id}:")
            print(f"     ✓ Registered")
            print(f"     Agent Class: {metadata.agent_class_name}")
            print(f"     Required Params: {[p for p, info in metadata.input_params.items() if info.required]}")
        else:
            print(f"\n   {tool_id}:")
            print(f"     ✗ NOT registered")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_agent_as_tool_creation()


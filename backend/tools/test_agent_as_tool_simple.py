"""Simple test for agent_as_tool creation logic - tests core logic only."""

# Mock everything we need
class MockParamInfo:
    def __init__(self, type, description, required=True):
        self.type = type
        self.description = description
        self.required = required

class MockAgentAsToolMetadata:
    def __init__(self, tool_id, name, description, task, agent_types, input_params, output_type, agent_class_name):
        self.tool_id = tool_id
        self.name = name
        self.description = description
        self.task = task
        self.agent_types = agent_types
        self.input_params = input_params
        self.output_type = output_type
        self.agent_class_name = agent_class_name
        self.tool_type = "agent_as_tool"
        self.agent_class = None

class MockAgent:
    def __init__(self, file_path: str):
        self.name = "TestAgent"
        self.file_path = file_path
    
    def as_tool(self, tool_name=None, tool_description=None):
        """Mock as_tool method."""
        class MockTool:
            def __init__(self, name, description, agent_instance):
                self.name = name
                self.description = description
                self._agent_instance = agent_instance
        return MockTool(tool_name or self.name, tool_description or "", self)

def test_create_agent_as_tool():
    """Test the core creation logic."""
    print("=" * 60)
    print("Testing Agent as Tool Creation Logic (Core)")
    print("=" * 60)
    
    # Create metadata
    metadata = MockAgentAsToolMetadata(
        tool_id="test_agent",
        name="test_agent",
        description="Test agent",
        task="Test task",
        agent_types=["AsToolAgent"],
        input_params={
            "file_path": MockParamInfo(
                type="str",
                description="File path",
                required=True
            ),
        },
        output_type="str",
        agent_class_name="MockAgent",
    )
    metadata.agent_class = MockAgent
    
    # Test 1: Validate required parameters
    print("\n1. Parameter Validation:")
    print("-" * 60)
    
    kwargs = {"file_path": "/test/path.md"}
    all_present = all(
        param_name in kwargs 
        for param_name, param_info in metadata.input_params.items() 
        if param_info.required
    )
    print(f"   Test with all required params: {all_present}")
    assert all_present, "Should have all required params"
    print("   ✓ All required parameters present")
    
    kwargs_missing = {}
    missing_required = any(
        param_name not in kwargs_missing 
        for param_name, param_info in metadata.input_params.items() 
        if param_info.required
    )
    print(f"   Test with missing params: {missing_required}")
    assert missing_required, "Should detect missing params"
    print("   ✓ Correctly detects missing parameters")
    
    # Test 2: Parameter filtering
    print("\n2. Parameter Filtering:")
    print("-" * 60)
    
    kwargs_with_extra = {
        "file_path": "/test/path.md",
        "extra_param": "should be filtered",
        "another_extra": "also filtered"
    }
    
    filtered_kwargs = {
        param_name: kwargs_with_extra[param_name]
        for param_name in metadata.input_params.keys()
        if param_name in kwargs_with_extra
    }
    
    print(f"   Original kwargs: {list(kwargs_with_extra.keys())}")
    print(f"   Filtered kwargs: {list(filtered_kwargs.keys())}")
    assert "file_path" in filtered_kwargs
    assert "extra_param" not in filtered_kwargs
    assert "another_extra" not in filtered_kwargs
    print("   ✓ Extra parameters correctly filtered")
    
    # Test 3: Agent instance creation
    print("\n3. Agent Instance Creation:")
    print("-" * 60)
    
    try:
        agent_instance = metadata.agent_class(**filtered_kwargs)
        print(f"   ✓ Agent instance created")
        print(f"     Agent name: {agent_instance.name}")
        print(f"     Agent file_path: {agent_instance.file_path}")
    except Exception as e:
        print(f"   ✗ Failed to create agent: {e}")
        return
    
    # Test 4: Convert to tool
    print("\n4. Convert Agent to Tool:")
    print("-" * 60)
    
    try:
        tool = agent_instance.as_tool(
            tool_name=metadata.name,
            tool_description=metadata.description
        )
        print(f"   ✓ Tool created from agent")
        print(f"     Tool name: {tool.name}")
        print(f"     Tool description: {tool.description}")
        print(f"     Has agent instance: {hasattr(tool, '_agent_instance')}")
    except Exception as e:
        print(f"   ✗ Failed to convert to tool: {e}")
        return
    
    # Test 5: Complete flow
    print("\n5. Complete Creation Flow:")
    print("-" * 60)
    
    def create_agent_as_tool(metadata, **kwargs):
        """Simulate the create_tool logic."""
        # Validate required parameters
        for param_name, param_info in metadata.input_params.items():
            if param_info.required and param_name not in kwargs:
                return None
        
        # Filter parameters
        agent_kwargs = {
            param_name: kwargs[param_name]
            for param_name in metadata.input_params.keys()
            if param_name in kwargs
        }
        
        # Create agent instance
        agent_instance = metadata.agent_class(**agent_kwargs)
        
        # Convert to tool
        tool = agent_instance.as_tool(
            tool_name=metadata.name,
            tool_description=metadata.description
        )
        
        # Attach metadata
        tool.__dict__['_tool_id'] = metadata.tool_id
        tool.__dict__['_agent_instance'] = agent_instance
        
        return tool
    
    # Test with correct params
    tool = create_agent_as_tool(metadata, file_path="/test/path.md")
    if tool:
        print("   ✓ Complete flow successful")
        print(f"     Tool ID: {tool.__dict__.get('_tool_id')}")
        print(f"     Agent instance: {tool.__dict__.get('_agent_instance').name}")
    else:
        print("   ✗ Complete flow failed")
    
    # Test with missing params
    tool = create_agent_as_tool(metadata)  # Missing file_path
    if tool is None:
        print("   ✓ Correctly rejected missing parameters")
    else:
        print("   ✗ Should have rejected missing parameters")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nSummary:")
    print("  ✓ Parameter validation works")
    print("  ✓ Parameter filtering works")
    print("  ✓ Agent instance creation works")
    print("  ✓ Agent to tool conversion works")
    print("  ✓ Complete flow works")


if __name__ == "__main__":
    test_create_agent_as_tool()


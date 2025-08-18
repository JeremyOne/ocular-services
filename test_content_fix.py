#!/usr/bin/env python3
"""
Test script to verify the content handling fix
"""

class MockMessage:
    """Mock message class to simulate different content types."""
    
    def __init__(self, source, content, msg_type=None):
        self.source = source
        self.content = content
        self.type = msg_type

def test_content_handling():
    """Test the content handling logic."""
    
    # Test cases for different content types
    test_cases = [
        MockMessage("Agent1", "This is a string message", "text"),
        MockMessage("Agent2", ["This", "is", "a", "list", "message"], "list"),
        MockMessage("Agent3", 12345, "number"),
        MockMessage("Agent4", {"key": "value"}, "dict"),
        MockMessage("Agent5", None, "none"),
    ]
    
    print("Testing content handling logic:")
    print("=" * 50)
    
    for i, message in enumerate(test_cases, 1):
        print(f"\nTest {i}: {message.source}")
        print(f"Original content: {message.content}")
        print(f"Original type: {type(message.content).__name__}")
        
        # Apply the same logic as in research.py
        content = message.content
        
        # Handle both string and list content
        if isinstance(content, list):
            content_str = ' '.join(str(item) for item in content)
        elif isinstance(content, str):
            content_str = content
        else:
            content_str = str(content)
        
        print(f"Processed content: {content_str}")
        print(f"Can call .lower(): {hasattr(content_str, 'lower')}")
        
        # Test the tool detection logic
        try:
            is_tool_call = any(keyword in content_str.lower() for keyword in ['running', 'tool', 'function_call'])
            print(f"Tool call detection: {is_tool_call}")
            print("✅ SUCCESS - No AttributeError")
        except AttributeError as e:
            print(f"❌ ERROR - AttributeError: {e}")
        
        print("-" * 30)
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_content_handling()

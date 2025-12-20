"""
Test the router's /help integration
"""

from src.router import CortexRouter

def test_help_via_router():
    """Test that /help works through the router."""
    router = CortexRouter()
    
    # Test /help command
    result = router.process_request("/help")
    
    print("=== ROUTER HELP INTEGRATION TEST ===\n")
    print(f"Intent: {result['intent']}")
    print(f"Workflow: {result['workflow']}")
    print(f"Command Used: {result['command_used']}")
    print(f"Next Step: {result['next_step']}")
    print(f"\nHelp Text:\n{'-' * 50}")
    print(result['help_text'])
    
    # Verify response structure
    assert result['intent'] == 'HELP'
    assert result['workflow'] == 'help_display'
    assert result['command_used'] == '/help'
    assert 'help_text' in result
    assert 'CORTEX' in result['help_text']
    
    print("\n✅ Router help integration working!")

if __name__ == "__main__":
    test_help_via_router()

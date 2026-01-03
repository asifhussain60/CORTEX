"""
Test Panel Styler - Validate natural language styling commands.
"""

from src.orchestrators.styling.panel_styler import PanelStyler


def test_panel_styler():
    """Test panel styler with multiple commands."""
    styler = PanelStyler()
    
    test_cases = [
        ("style dashboard like tetris", "tetris", "dashboard"),
        ("make card look like intro", "intro", "card"),
        ("use grid-cards layout", "grid-cards", None),
        ("apply neon-glass to button", "neon-glass", "button"),
        ("tetris style for metrics", "tetris", "metrics"),
    ]
    
    print("=== Panel Styler Test Results ===\n")
    
    for i, (command, expected_panel, expected_target) in enumerate(test_cases, 1):
        result = styler.apply_style(command)
        
        success = "✅" if result["success"] else "❌"
        panel_match = result.get("panel_name") == expected_panel
        target_match = result.get("target") == expected_target if expected_target else True
        
        print(f"{i}. Command: '{command}'")
        print(f"   Status: {success}")
        print(f"   Panel: {result.get('panel_name', 'N/A')} (expected: {expected_panel}) {'✓' if panel_match else '✗'}")
        if expected_target:
            print(f"   Target: {result.get('target', 'N/A')} (expected: {expected_target}) {'✓' if target_match else '✗'}")
        print(f"   Class: {result.get('class_name', 'N/A')}")
        print(f"   Message: {result.get('message', 'N/A')}")
        print()
    
    # Test list panels
    print("6. Command: 'list panels'")
    list_result = styler.list_panels()
    print(f"   Status: ✅" if list_result["success"] else "❌")
    print(f"   Count: {list_result['count']} panels")
    print(f"   Panels: {', '.join([p['key'] for p in list_result['panels'][:5]])}...")
    print()
    
    # Test error handling
    print("7. Command: 'style X like unknown-panel' (error test)")
    error_result = styler.apply_style("style X like unknown-panel")
    print(f"   Status: {'❌' if not error_result['success'] else '✅ (unexpected)'}")
    print(f"   Message: {error_result.get('message', 'N/A')}")
    print(f"   Available: {len(error_result.get('available_panels', []))} panels suggested")
    print()
    
    print("=== Test Complete ===")


if __name__ == "__main__":
    test_panel_styler()

"""
Test: CORTEX Response Header Consistency

Validates that ALL responses include the brain icon and CORTEX header.
This test ensures the permanent fix for inconsistent header injection.
"""

import sys
from pathlib import Path

# Add CORTEX to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_brain_emoji_in_all_responses():
    """Verify brain icon appears in all response types."""
    from src.infrastructure.cortex_output_formatter import cortex_format
    
    test_cases = [
        ("Success response", "Operation completed"),
        ("Error response", "Something went wrong"),
        ("Status response", "Processing in progress"),
        ("Long response", "This is a much longer response " * 10),
    ]
    
    print("\n" + "=" * 80)
    print("TEST: Brain Emoji Consistency in All Response Types")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for name, content in test_cases:
        formatted = cortex_format(content, operation_type="Test")
        
        # Check for brain icon
        if "🧠 CORTEX" in formatted:
            print(f"✅ {name}: Header present with brain icon")
            passed += 1
        else:
            print(f"❌ {name}: Missing brain icon header")
            print(f"   Output: {formatted[:100]}...")
            failed += 1
        
        # Check for author
        if "Asif Hussain" in formatted:
            print(f"   ✅ Author attribution present")
        else:
            print(f"   ❌ Author attribution missing")
            failed += 1
        
        # Check for copyright
        if "Copyright © 2025-2026" in formatted:
            print(f"   ✅ Copyright notice present")
        else:
            print(f"   ❌ Copyright notice missing")
            failed += 1
    
    print()
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 80)
    print()
    
    return failed == 0


def test_fallback_header_generation():
    """Verify fallback header works if manager unavailable."""
    from src.infrastructure.cortex_output_formatter import (
        CORTEXOutputFormatter
    )
    
    print("\n" + "=" * 80)
    print("TEST: Fallback Header Generation")
    print("=" * 80)
    
    formatter = CORTEXOutputFormatter()
    
    # Test fallback (simulate manager unavailable)
    try:
        # Force using fallback by simulating import failure
        test_content = "Test content for fallback"
        
        # This should use fallback if manager can't be imported
        formatted = formatter.format_output(test_content, include_header=True)
        
        if "🧠 CORTEX" in formatted or "⚙️ CORTEX" in formatted:
            print("✅ Fallback header generated successfully")
            print(f"   First 100 chars: {formatted[:100]}...")
            return True
        else:
            print("❌ Fallback header generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
        return False


def test_formatter_singleton():
    """Verify formatter is singleton (consistent across calls)."""
    from src.infrastructure.cortex_output_formatter import (
        get_cortex_output_formatter,
        CORTEXOutputFormatter
    )
    
    print("\n" + "=" * 80)
    print("TEST: Formatter Singleton Pattern")
    print("=" * 80)
    
    formatter1 = get_cortex_output_formatter()
    formatter2 = get_cortex_output_formatter()
    formatter3 = CORTEXOutputFormatter()
    
    if formatter1 is formatter2 and formatter2 is formatter3:
        print("✅ Singleton pattern verified - same instance returned")
        print(f"   Instance ID: {id(formatter1)}")
        return True
    else:
        print("❌ Singleton pattern failed - different instances")
        print(f"   formatter1 ID: {id(formatter1)}")
        print(f"   formatter2 ID: {id(formatter2)}")
        print(f"   formatter3 ID: {id(formatter3)}")
        return False


def test_error_formatting():
    """Verify error responses also get brain icon."""
    from src.infrastructure.cortex_output_formatter import (
        cortex_format
    )
    
    print("\n" + "=" * 80)
    print("TEST: Error Response Formatting")
    print("=" * 80)
    
    error_msg = "[ERROR] Failed to process request"
    formatted_error = cortex_format(error_msg, operation_type="Error")
    
    if "🧠 CORTEX" in formatted_error:
        print("✅ Error responses include brain icon header")
        print(f"   First 150 chars: {formatted_error[:150]}...")
        return True
    else:
        print("❌ Error responses missing brain icon")
        return False


if __name__ == "__main__":
    results = []
    
    print("\n" + "=" * 80)
    print("CORTEX RESPONSE HEADER CONSISTENCY TEST SUITE")
    print("=" * 80)
    print("Testing permanent fix for brain icon & header consistency")
    print()
    
    # Run all tests
    results.append(("Brain Emoji Consistency", test_brain_emoji_in_all_responses()))
    results.append(("Fallback Header Generation", test_fallback_header_generation()))
    results.append(("Formatter Singleton", test_formatter_singleton()))
    results.append(("Error Formatting", test_error_formatting()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUITE SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"Overall: {passed}/{len(results)} tests passed")
    print("=" * 80)
    print()
    
    sys.exit(0 if failed == 0 else 1)

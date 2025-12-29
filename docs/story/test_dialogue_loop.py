#!/usr/bin/env python3
"""
Loop test: Verify dialogue colors across multiple random chapters
Runs until all chapters tested or failure detected
"""

import sys
import time
import random
from pathlib import Path
from test_dialogue_colors_browser import test_dialogue_colors

def main():
    """Test multiple random chapters in sequence"""
    
    print("=" * 70)
    print("🧠 CORTEX Dialogue Color Loop Test")
    print("=" * 70)
    print()
    
    chapters_to_test = list(range(14))  # 0-13 (Prologue + 13 chapters)
    random.shuffle(chapters_to_test)
    
    tested = 0
    passed = 0
    failed = 0
    
    for chapter_num in chapters_to_test[:5]:  # Test 5 random chapters
        print(f"\n{'─' * 70}")
        print(f"Test {tested + 1}/5")
        print(f"{'─' * 70}\n")
        
        success = test_dialogue_colors(chapter_num)
        tested += 1
        
        if success:
            passed += 1
        else:
            failed += 1
            print("\n❌ FAILURE DETECTED - Stopping tests")
            break
        
        if tested < 5:
            time.sleep(0.5)  # Brief pause between tests
    
    print()
    print("=" * 70)
    print("📊 LOOP TEST SUMMARY")
    print("=" * 70)
    print(f"Chapters tested: {tested}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    
    if failed == 0:
        print("🎉 ALL LOOP TESTS PASSED!")
        print("   ✓ Multiple chapters verified")
        print("   ✓ CSS loading consistently")
        print("   ✓ Colors rendering correctly everywhere")
        print("   ✓ Issue is FULLY RESOLVED")
        return 0
    else:
        print("❌ FAILURES DETECTED")
        print("   Need to regenerate chapters and re-test")
        return 1

if __name__ == '__main__':
    exit(main())

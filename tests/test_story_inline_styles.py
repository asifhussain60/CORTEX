"""
CORTEX Story Inline Style Test Suite
Tests all chapter HTML after JavaScript rendering to ensure no inline styles exist.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import re
import time
from pathlib import Path

# Test configuration
STORY_VIEWER_PATH = Path(__file__).parent.parent / "docs" / "story" / "viewer.html"
STORY_VIEWER_URL = f"file:///{STORY_VIEWER_PATH.as_posix()}"

CHAPTERS = [
    {"id": "prologue", "name": "Prologue: The Basement Laboratory"},
    {"id": "chapter-01", "name": "Chapter 1: The Amnesia Crisis"},
    {"id": "chapter-02", "name": "Chapter 2: Tier 0 - The Gatekeeper"},
    {"id": "chapter-03", "name": "Chapter 3: Tier 1 - Memory Awakens"},
    {"id": "chapter-04", "name": "Chapter 4: Tier 2 - The Learning Machine"},
    {"id": "chapter-05", "name": "Chapter 5: The Test-Driven Rebellion"},
    {"id": "chapter-06", "name": "Chapter 6: The Great Orchestration"},
    {"id": "chapter-07", "name": "Chapter 7: The Planning Revolution"},
    {"id": "chapter-08", "name": "Chapter 8: The Enterprise Awakening"},
    {"id": "chapter-09", "name": "Chapter 9: The Sanitizer's Dilemma"},
    {"id": "chapter-10", "name": "Chapter 10: The Self-Healing System"},
    {"id": "chapter-11", "name": "Chapter 11: The Knowledge Keeper"},
    {"id": "chapter-12", "name": "Chapter 12: The Convergence"},
    {"id": "chapter-13", "name": "Chapter 13: The Refiner"},
]


def test_story_inline_styles():
    """Run comprehensive inline style tests using Playwright."""
    from playwright.sync_api import sync_playwright
    
    print("\n" + "="*80)
    print("🧪 CORTEX STORY INLINE STYLE TEST SUITE")
    print("="*80)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    issues = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"\n📂 Loading story viewer: {STORY_VIEWER_URL}\n")
        page.goto(STORY_VIEWER_URL)
        page.wait_for_load_state("networkidle")
        
        for chapter in CHAPTERS:
            total_tests += 1
            print(f"🧪 Testing: {chapter['name']}")
            
            # Navigate to chapter
            page.goto(f"{STORY_VIEWER_URL}#{chapter['id']}")
            page.wait_for_timeout(2000)  # Wait for JS rendering
            
            try:
                # Wait for content to load
                page.wait_for_selector("#chapterContent .chapter-container", timeout=10000)
                
                # Find elements with inline styles
                elements_with_styles = page.locator("[style]").all()
                
                # Filter out allowed styles (opacity from image loading)
                problematic = []
                for elem in elements_with_styles:
                    style = elem.get_attribute("style")
                    if style and style.strip() not in ["opacity: 1;", "opacity:1", "opacity: 1", ""]:
                        tag = elem.evaluate("el => el.tagName.toLowerCase()")
                        html_snippet = elem.evaluate("el => el.outerHTML")[:150]
                        problematic.append({
                            "tag": tag,
                            "style": style,
                            "html": html_snippet
                        })
                
                if problematic:
                    failed_tests += 1
                    print(f"   ❌ FAIL - Found {len(problematic)} inline style(s)")
                    for p in problematic[:3]:  # Show first 3
                        print(f"      <{p['tag']}> style=\"{p['style']}\"")
                    issues.append({
                        "chapter": chapter['name'],
                        "problems": problematic
                    })
                else:
                    passed_tests += 1
                    print(f"   ✅ PASS - No inline styles")
                    
            except Exception as e:
                failed_tests += 1
                print(f"   ❌ ERROR: {str(e)}")
                issues.append({
                    "chapter": chapter['name'],
                    "error": str(e)
                })
        
        browser.close()
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"Total Chapters Tested: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Pass Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if issues:
        print("\n❌ ISSUES FOUND:")
        for issue in issues:
            print(f"\n  Chapter: {issue['chapter']}")
            if 'error' in issue:
                print(f"    Error: {issue['error']}")
            else:
                print(f"    Problems: {len(issue['problems'])} inline style(s)")
                for p in issue['problems'][:2]:
                    print(f"      - <{p['tag']}> style=\"{p['style'][:50]}...\"")
    
    print("\n" + "="*80)
    
    # Assert for pytest
    assert failed_tests == 0, f"{failed_tests} chapter(s) failed inline style tests"
    
    print("\n✅ ALL TESTS PASSED!\n")


if __name__ == "__main__":
    test_story_inline_styles()

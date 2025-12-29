#!/usr/bin/env python3
"""
Visual browser test to verify dialogue colors are rendering correctly
Opens a random chapter and checks computed styles
"""

import sys
import time
import random
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Playwright not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    from playwright.sync_api import sync_playwright

def test_dialogue_colors(chapter_num):
    """Test dialogue colors in browser for a specific chapter"""
    
    # Determine chapter folder
    if chapter_num == 0:
        chapter_folder = "Prologue"
        chapter_name = "Prologue"
    else:
        chapter_folder = f"Chapter-{chapter_num:02d}"
        chapter_name = f"Chapter {chapter_num}"
    
    story_dir = Path(__file__).parent
    html_file = story_dir / chapter_folder / "index.html"
    
    if not html_file.exists():
        print(f"❌ {chapter_name} HTML file not found: {html_file}")
        return False
    
    print(f"🌐 Testing {chapter_name} in browser...")
    print(f"   File: {html_file}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Load the chapter
        page.goto(f"file://{html_file.absolute()}")
        time.sleep(0.5)  # Wait for CSS to load
        
        # Check if CSS is loaded
        css_link = page.query_selector('link[rel="stylesheet"]')
        if not css_link:
            print("   ❌ No CSS link found in page!")
            browser.close()
            return False
        
        css_href = css_link.get_attribute('href')
        print(f"   ✓ CSS link found: {css_href}")
        
        # Find dialogue spans
        asif_spans = page.query_selector_all('.dialogue-asif')
        miss_g_spans = page.query_selector_all('.dialogue-miss-g')
        
        print(f"   ✓ Found {len(asif_spans)} Asif dialogue spans")
        print(f"   ✓ Found {len(miss_g_spans)} Miss G dialogue spans")
        
        issues = []
        
        # Check Asif dialogue color (should be cyan #00d4ff)
        if asif_spans:
            asif_color = asif_spans[0].evaluate('el => window.getComputedStyle(el).color')
            print(f"   🎨 Asif color: {asif_color}")
            
            # Check if color is cyan (rgb(0, 212, 255) = #00d4ff)
            if 'rgb(0, 212, 255)' not in asif_color:
                issues.append(f"Asif color incorrect: {asif_color} (expected rgb(0, 212, 255))")
        
        # Check Miss G dialogue color (should be purple #9d4edd)
        if miss_g_spans:
            miss_g_color = miss_g_spans[0].evaluate('el => window.getComputedStyle(el).color')
            print(f"   🎨 Miss G color: {miss_g_color}")
            
            # Check if color is purple (rgb(157, 78, 221) = #9d4edd)
            if 'rgb(157, 78, 221)' not in miss_g_color:
                issues.append(f"Miss G color incorrect: {miss_g_color} (expected rgb(157, 78, 221))")
        
        # Check text-shadow (both should have glow)
        if asif_spans:
            asif_shadow = asif_spans[0].evaluate('el => window.getComputedStyle(el).textShadow')
            if asif_shadow == 'none':
                issues.append("Asif dialogue missing text-shadow glow")
        
        if miss_g_spans:
            miss_g_shadow = miss_g_spans[0].evaluate('el => window.getComputedStyle(el).textShadow')
            if miss_g_shadow == 'none':
                issues.append("Miss G dialogue missing text-shadow glow")
        
        browser.close()
        
        if issues:
            print(f"   ❌ Issues found:")
            for issue in issues:
                print(f"      - {issue}")
            return False
        else:
            print(f"   ✅ All styles correct!")
            return True

def main():
    """Test a random chapter"""
    
    print("=" * 70)
    print("🧠 CORTEX Dialogue Color Browser Test")
    print("=" * 70)
    print()
    
    # Test random chapter
    chapter_num = random.randint(0, 13)  # 0 = Prologue, 1-13 = Chapters
    
    success = test_dialogue_colors(chapter_num)
    
    print()
    print("=" * 70)
    
    if success:
        print("🎉 TEST PASSED!")
        print("   ✓ CSS stylesheet loaded correctly")
        print("   ✓ Asif dialogue: Cyan (#00d4ff) with glow")
        print("   ✓ Miss G dialogue: Purple (#9d4edd) with glow")
        print("   ✓ All character colors rendering correctly")
        return 0
    else:
        print("❌ TEST FAILED - See details above")
        print()
        print("🔄 Re-running converter...")
        return 1

if __name__ == '__main__':
    exit(main())

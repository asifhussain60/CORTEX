#!/usr/bin/env python3
"""
Test all phase YAML files load successfully in browser
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

def test_all_phase_yamls():
    """Test that all phase YAML files in _cortex-master load successfully."""
    
    registry_path = Path(__file__).parent.parent.parent
    index_html = registry_path / ".yaml-reader" / "index.html"
    phases_dir = registry_path / "_cortex-master" / "phases"
    
    print("="*70)
    print("CORTEX Phase YAML Files - Browser Load Test")
    print("="*70)
    
    if not phases_dir.exists():
        print(f"❌ ERROR: Phases directory not found at {phases_dir}")
        return 1
    
    phase_files = sorted(phases_dir.rglob("*.yaml"))
    print(f"\n📁 Found {len(phase_files)} phase YAML files")
    print("-"*70)
    
    failed_files = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate once
        file_url = f"file://{index_html.absolute()}"
        page.goto(file_url, wait_until='networkidle', timeout=10000)
        page.wait_for_selector('.app-container', timeout=5000)
        
        for i, yaml_file in enumerate(phase_files, 1):
            rel_path = yaml_file.relative_to(registry_path)
            
            try:
                # Clear previous file
                clear_btn = page.locator('#clearAllBtn')
                if clear_btn.count() > 0:
                    clear_btn.click()
                    time.sleep(0.5)
                
                # Load file
                page.click('#openFileBtn')
                file_input = page.locator('#fileInput')
                file_input.set_input_files(str(yaml_file.absolute()))
                time.sleep(1)
                
                # Check for errors
                error_panel = page.locator('.error-panel')
                yaml_error = page.locator('.error-header:has-text("YAML Parse Error")')
                
                if yaml_error.count() > 0:
                    error_msg = page.locator('.error-message').text_content()
                    print(f"❌ [{i}/{len(phase_files)}] {rel_path}")
                    print(f"     Error: {error_msg[:100]}...")
                    failed_files.append(str(rel_path))
                else:
                    print(f"✅ [{i}/{len(phase_files)}] {rel_path}")
                    
            except Exception as e:
                print(f"❌ [{i}/{len(phase_files)}] {rel_path}")
                print(f"     Exception: {str(e)[:100]}")
                failed_files.append(str(rel_path))
        
        browser.close()
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✅ Passed: {len(phase_files) - len(failed_files)}/{len(phase_files)}")
    print(f"❌ Failed: {len(failed_files)}/{len(phase_files)}")
    
    if failed_files:
        print("\nFailed files:")
        for f in failed_files:
            print(f"  - {f}")
        return 1
    else:
        print("\n🎉 ALL PHASE YAML FILES LOAD SUCCESSFULLY!")
        return 0

if __name__ == "__main__":
    sys.exit(test_all_phase_yamls())

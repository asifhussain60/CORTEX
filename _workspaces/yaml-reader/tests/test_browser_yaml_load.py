#!/usr/bin/env python3
"""
Browser-based YAML Validation Test using Playwright
Tests that YAML files load successfully in the actual YAML Reader app.
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import time

def test_yaml_reader_in_browser():
    """Test YAML Reader loads cortex-master.yaml successfully in browser."""
    
    registry_path = Path(__file__).parent.parent.parent
    index_html = registry_path / ".yaml-reader" / "index.html"
    cortex_master = registry_path / "cortex-master.yaml"
    
    print("="*70)
    print("CORTEX YAML Reader - Browser Test (Playwright)")
    print("="*70)
    
    if not index_html.exists():
        print(f"❌ ERROR: index.html not found at {index_html}")
        return 1
    
    if not cortex_master.exists():
        print(f"❌ ERROR: cortex-master.yaml not found at {cortex_master}")
        return 1
    
    print(f"\n📄 Testing file: {cortex_master.name}")
    print(f"📂 YAML Reader: {index_html}")
    print("-"*70)
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Set up console message capture
        console_messages = []
        errors = []
        
        def handle_console(msg):
            console_messages.append({
                'type': msg.type,
                'text': msg.text
            })
            if msg.type in ['error', 'warning']:
                print(f"   [{msg.type.upper()}] {msg.text}")
        
        def handle_page_error(error):
            errors.append(str(error))
            print(f"   [PAGE ERROR] {error}")
        
        page.on('console', handle_console)
        page.on('pageerror', handle_page_error)
        
        try:
            # Navigate to YAML Reader
            print("\n🌐 Loading YAML Reader...")
            file_url = f"file://{index_html.absolute()}"
            page.goto(file_url, wait_until='networkidle', timeout=10000)
            
            # Wait for app to initialize
            page.wait_for_selector('.app-container', timeout=5000)
            print("✅ YAML Reader loaded")
            
            # Check for initialization message
            time.sleep(1)
            init_found = any('initialized' in msg['text'].lower() 
                           for msg in console_messages)
            if init_found:
                print("✅ App initialized successfully")
            
            # Click the file input button
            print("\n📂 Opening file selector...")
            page.click('#openFileBtn')
            
            # Set the file input
            print(f"📄 Loading: {cortex_master.name}")
            file_input = page.locator('#fileInput')
            file_input.set_input_files(str(cortex_master.absolute()))
            
            # Wait for file processing
            time.sleep(2)
            
            # Check for YAML parse errors
            error_panel = page.locator('.error-panel')
            yaml_error = page.locator('.error-header:has-text("YAML Parse Error")')
            
            if yaml_error.count() > 0:
                print("\n❌ YAML PARSE ERROR DETECTED")
                
                # Get error details
                error_message = page.locator('.error-message').text_content()
                print(f"\nError details:")
                print("-"*70)
                print(error_message)
                print("-"*70)
                
                # Try to extract specific line/column
                lines = error_message.split('\n')
                for line in lines:
                    if 'duplicate' in line.lower() or 'line' in line.lower():
                        print(f"   {line.strip()}")
                
                # Take screenshot
                screenshot_path = registry_path / ".yaml-reader" / "tests" / "error-screenshot.png"
                page.screenshot(path=str(screenshot_path))
                print(f"\n📸 Screenshot saved: {screenshot_path}")
                
                browser.close()
                return 1
            
            # Check if file loaded successfully
            file_list_item = page.locator('.file-list-item')
            if file_list_item.count() > 0:
                print("✅ File appears in explorer")
                
                # Click on the file to view it
                file_list_item.first.click()
                time.sleep(1)
                
                # Check for warning icon
                warning_icon = page.locator('.file-list-item .file-icon:has-text("⚠️")')
                if warning_icon.count() > 0:
                    print("⚠️  File loaded with warnings")
                else:
                    success_icon = page.locator('.file-list-item .file-icon:has-text("📄")')
                    if success_icon.count() > 0:
                        print("✅ File loaded without errors")
            
            # Now check for errors in the content area
            time.sleep(1)
            
            # Check what's in the content area
            content_area = page.locator('#contentArea')
            if content_area.count() > 0:
                content_text = content_area.text_content()
                print(f"\n📄 Content area text (first 200 chars): {content_text[:200]}")
            
            # Check for YAML parse errors in content area
            error_panel = page.locator('.error-panel')
            if error_panel.count() > 0:
                print("\n❌ ERROR PANEL DETECTED")
                error_text = error_panel.text_content()
                print("Error content:")
                print("-"*70)
                print(error_text)
                print("-"*70)
            else:
                print("✅ No error panel detected")
            
            # Make sure Tree view tab is selected
            tree_tab = page.locator('.view-tab:has-text("Tree")')
            if tree_tab.count() > 0:
                print("\n🌲 Clicking Tree tab...")
                tree_tab.click()
                time.sleep(1)
            
            # Check if tree view is rendered (with more specific selector)
            tree_view = page.locator('.tree-view, .tree-node, .tree-key')
            content_body = page.locator('.content-body')
            if tree_view.count() > 0:
                print("✅ Tree view rendered")
                
                # Check for specific keys
                metadata_key = page.locator('.tree-key:has-text("metadata")')
                phase_status_key = page.locator('.tree-key:has-text("phase_status")')
                
                if metadata_key.count() > 0:
                    print("✅ 'metadata' key found")
                if phase_status_key.count() > 0:
                    print("✅ 'phase_status' key found")
                
                # Count phase sections
                completed_key = page.locator('.tree-key:has-text("completed")')
                active_key = page.locator('.tree-key:has-text("active")')
                planned_key = page.locator('.tree-key:has-text("planned")')
                
                if completed_key.count() > 0:
                    print("✅ 'completed' section found")
                if active_key.count() > 0:
                    print("✅ 'active' section found")
                if planned_key.count() > 0:
                    print("✅ 'planned' section found")
            else:
                print("⚠️  Tree view not rendered (check for errors)")
            
            # Check console for errors
            js_errors = [msg for msg in console_messages if msg['type'] == 'error']
            if js_errors:
                print(f"\n⚠️  {len(js_errors)} JavaScript errors detected:")
                for err in js_errors[:3]:  # Show first 3
                    print(f"   - {err['text'][:100]}")
            
            # Take success screenshot
            screenshot_path = registry_path / ".yaml-reader" / "tests" / "success-screenshot.png"
            page.screenshot(path=str(screenshot_path))
            print(f"\n📸 Screenshot saved: {screenshot_path}")
            
            # Check final status before closing
            has_errors = yaml_error.count() > 0
            has_tree = tree_view.count() > 0
            
            # Keep browser open for inspection
            print("\n⏸️  Browser will stay open for 5 seconds for inspection...")
            time.sleep(5)
            
            browser.close()
            
            if not has_errors and has_tree:
                print("\n" + "="*70)
                print("🎉 SUCCESS: YAML loaded without errors in browser!")
                print("="*70)
                return 0
            elif not has_errors:
                print("\n" + "="*70)
                print("⚠️  File loaded without parse errors but tree not rendered")
                print("="*70)
                return 1
            else:
                print("\n" + "="*70)
                print("❌ FAILED: YAML parse errors detected")
                print("="*70)
                return 1
                
        except Exception as e:
            print(f"\n❌ TEST ERROR: {e}")
            import traceback
            traceback.print_exc()
            
            # Take error screenshot
            try:
                screenshot_path = registry_path / ".yaml-reader" / "tests" / "test-error-screenshot.png"
                page.screenshot(path=str(screenshot_path))
                print(f"📸 Error screenshot saved: {screenshot_path}")
            except:
                pass
            
            browser.close()
            return 1

if __name__ == "__main__":
    sys.exit(test_yaml_reader_in_browser())

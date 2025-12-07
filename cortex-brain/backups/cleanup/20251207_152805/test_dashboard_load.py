#!/usr/bin/env python3
"""
Test dashboard loads successfully without console errors
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def test_dashboard_loads():
    """Test that dashboard loads without JavaScript errors"""
    
    # Setup headless Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        # Load dashboard
        print("Loading dashboard at http://localhost:8080/ui/index.html?source=mock")
        driver.get('http://localhost:8080/ui/index.html?source=mock')
        
        # Wait for page to load (look for tab container)
        print("Waiting for tab container...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "tab-container"))
        )
        print("✓ Tab container found")
        
        # Wait for at least one tab button
        print("Waiting for tab buttons...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".tab-button"))
        )
        print("✓ Tab buttons loaded")
        
        # Check for JavaScript errors in console
        print("\nChecking browser console logs...")
        logs = driver.get_log('browser')
        
        errors = [log for log in logs if log['level'] == 'SEVERE']
        warnings = [log for log in logs if log['level'] == 'WARNING']
        
        if errors:
            print(f"\n❌ Found {len(errors)} JavaScript errors:")
            for error in errors:
                print(f"  - {error['message']}")
            return False
        else:
            print("✓ No JavaScript errors found")
        
        if warnings:
            print(f"\n⚠ Found {len(warnings)} warnings:")
            for warning in warnings[:5]:  # Show first 5
                print(f"  - {warning['message']}")
        
        # Check that tabs are actually rendered
        print("\nChecking tab rendering...")
        tab_buttons = driver.find_elements(By.CSS_SELECTOR, ".tab-button")
        print(f"✓ Found {len(tab_buttons)} tab buttons")
        
        if len(tab_buttons) < 8:
            print(f"❌ Expected 8 tabs, found {len(tab_buttons)}")
            return False
        
        # Check that content area exists
        content_area = driver.find_elements(By.ID, "tab-content")
        if not content_area:
            print("❌ Tab content area not found")
            return False
        print("✓ Tab content area found")
        
        # Try clicking first tab (Executive)
        print("\nTesting tab navigation...")
        first_tab = tab_buttons[0]
        first_tab.click()
        time.sleep(2)  # Wait for tab to load
        
        # Check if tab content loaded
        logs_after_click = driver.get_log('browser')
        new_errors = [log for log in logs_after_click if log['level'] == 'SEVERE' and log not in logs]
        
        if new_errors:
            print(f"❌ Found {len(new_errors)} errors after clicking tab:")
            for error in new_errors:
                print(f"  - {error['message']}")
            return False
        
        print("✓ Tab navigation works without errors")
        
        print("\n" + "="*60)
        print("✅ DASHBOARD LOADS SUCCESSFULLY WITHOUT CONSOLE ERRORS")
        print("="*60)
        return True
        
    except TimeoutException as e:
        print(f"❌ Timeout waiting for element: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    success = test_dashboard_loads()
    exit(0 if success else 1)

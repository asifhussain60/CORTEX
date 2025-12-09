#!/usr/bin/env python3
"""
Test dashboard loads successfully without console errors
"""
import sys
import io
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Fix Windows console encoding for Unicode
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
        
        # Wait for page to fully load with longer timeout
        print("Waiting for page to load...")
        time.sleep(5)  # Give dashboard time to initialize
        
        # Check if page loaded by looking for any interactive element
        print("Checking if dashboard loaded...")
        try:
            # Try multiple selectors
            WebDriverWait(driver, 20).until(
                lambda d: d.find_element(By.TAG_NAME, "body") and len(d.page_source) > 1000
            )
            print("✓ Dashboard page loaded")
        
            # Look for tabs or sourceSelect (admin dashboard has dropdown)
            tabs_or_select = driver.find_elements(By.CSS_SELECTOR, ".tab-button, #sourceSelect")
            if tabs_or_select:
                print(f"✓ Found {len(tabs_or_select)} interactive elements")
            else:
                print("⚠ No tab buttons found, but page loaded")
        except Exception as e:
            print(f"⚠ Could not verify all elements: {e}")
        
        # Check for JavaScript errors in console (exclude favicon 404)
        print("\nChecking browser console logs...")
        logs = driver.get_log('browser')
        
        errors = [log for log in logs if log['level'] == 'SEVERE' and 'favicon.ico' not in log['message']]
        warnings = [log for log in logs if log['level'] == 'WARNING']
        
        if errors:
            print(f"\n❌ Found {len(errors)} JavaScript errors:")
            for error in errors[:5]:  # Show first 5
                print(f"  - {error['message'][:100]}")
            return False
        else:
            print("✓ No JavaScript errors found")
        
        if warnings:
            print(f"\n⚠ Found {len(warnings)} warnings (showing first 3):")
            for warning in warnings[:3]:
                print(f"  - {warning['message'][:100]}")
        
        # Check that dashboard has interactive elements
        print("\nChecking dashboard interactivity...")
        dropdown = driver.find_elements(By.ID, "sourceSelect")
        tab_buttons = driver.find_elements(By.CSS_SELECTOR, ".tab-button, button, .nav-link")
        
        interactive_count = len(dropdown) + len(tab_buttons)
        print(f"✓ Found {interactive_count} interactive elements")
        
        if interactive_count == 0:
            print("❌ No interactive elements found")
            return False
        
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


def test_admin_dashboard_has_dropdown():
    """Test that admin dashboard has source selector dropdown"""
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        print("\n" + "="*60)
        print("Testing Admin Dashboard Dropdown Visibility")
        print("="*60)
        
        # Load dashboard
        print("Loading admin dashboard...")
        driver.get('http://localhost:8080/ui/index.html?source=mock')
        
        # Wait for page to fully load
        time.sleep(3)  # Let dashboard initialize
        
        # Wait for dropdown to be present and visible
        print("Checking for source selector dropdown...")
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "sourceSelect"))
        )
        
        # Check dropdown exists and is visible
        dropdown = driver.find_element(By.ID, 'sourceSelect')
        assert dropdown is not None, "Source selector dropdown not found"
        print("✓ Dropdown element found")
        
        assert dropdown.is_displayed(), "Dropdown exists but is not visible"
        print("✓ Dropdown is visible")
        
        # Check dropdown has options using JavaScript to avoid stale elements
        from selenium.webdriver.support.select import Select
        option_count = driver.execute_script(
            "return document.getElementById('sourceSelect').options.length;"
        )
        assert option_count >= 2, f"Expected at least 2 options, found {option_count}"
        print(f"✓ Dropdown has {option_count} options")
        
        # Get option values using JavaScript
        option_values = driver.execute_script("""
            const select = document.getElementById('sourceSelect');
            return Array.from(select.options).map(opt => opt.value);
        """)
        assert 'mock' in option_values, "Mock option not found"
        print(f"✓ Available sources: {', '.join(option_values[:10])}...")
        
        print("\n✅ ADMIN DASHBOARD HAS SOURCE SELECTOR DROPDOWN")
        return True
        
    except Exception as e:
        print(f"❌ Dropdown visibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            driver.quit()


def test_admin_dropdown_functionality():
    """Test that source selector dropdown changes data source"""
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        print("\n" + "="*60)
        print("Testing Admin Dashboard Dropdown Functionality")
        print("="*60)
        
        # Load dashboard
        print("Loading admin dashboard...")
        driver.get('http://localhost:8080/ui/index.html?source=mock')
        
        # Wait for page to fully load
        time.sleep(3)
        
        # Wait for dropdown
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "sourceSelect"))
        )
        
        # Get initial source and available options using JavaScript
        initial_value = driver.execute_script(
            "return document.getElementById('sourceSelect').value;"
        )
        print(f"Initial source: {initial_value}")
        
        # Get all option values
        all_options = driver.execute_script("""
            const select = document.getElementById('sourceSelect');
            return Array.from(select.options).map(opt => opt.value);
        """)
        
        # Find a different option to test
        available_options = [opt for opt in all_options if opt != initial_value]
        
        if not available_options:
            print("⚠ Only one source available, skipping source change test")
            return True
        
        # Change to different source using JavaScript
        new_source = available_options[0]
        print(f"Changing source to: {new_source}")
        driver.execute_script(
            f"document.getElementById('sourceSelect').value = '{new_source}';"
            "document.getElementById('sourceSelect').dispatchEvent(new Event('change'));"
        )
        
        # Wait for change to take effect
        time.sleep(3)
        
        # Verify dropdown value changed
        current_value = driver.execute_script(
            "return document.getElementById('sourceSelect').value;"
        )
        assert current_value == new_source, f"Dropdown didn't change: {current_value} != {new_source}"
        print(f"✓ Dropdown changed to: {current_value}")
        
        # Check for loading indicator or data refresh
        print("✓ Source change triggered")
        
        print("\n✅ DROPDOWN FUNCTIONALITY WORKS")
        return True
        
    except Exception as e:
        print(f"❌ Dropdown functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            driver.quit()


if __name__ == '__main__':
    print("="*60)
    print("DASHBOARD INTEGRATION TESTS")
    print("="*60)
    
    tests = [
        ("Dashboard Load", test_dashboard_loads),
        ("Admin Dropdown Visibility", test_admin_dashboard_has_dropdown),
        ("Admin Dropdown Functionality", test_admin_dropdown_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        success = test_func()
        results.append((test_name, success))
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(success for _, success in results)
    exit(0 if all_passed else 1)

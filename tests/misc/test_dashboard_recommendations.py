#!/usr/bin/env python3
"""
Integration test for dashboard recommendations rendering

Verifies that:
1. Recommendations data is properly formatted
2. All recommendations have required fields
3. Priority values are valid
4. Dashboard can render recommendations without errors

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import io
from pathlib import Path
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root))


def test_recommendations_data_structure():
    """Test that recommendations JSON has proper structure"""
    
    print("\n" + "="*70)
    print("TESTING RECOMMENDATIONS DATA STRUCTURE")
    print("="*70)
    
    # Load recommendations data
    recommendations_file = project_root / "cortex-brain" / "dashboards" / "data" / "repos" / "cleansolidapp" / "recommendations.json"
    
    if not recommendations_file.exists():
        print(f"❌ Recommendations file not found: {recommendations_file}")
        return False
    
    with open(recommendations_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Verify structure
    print("\n📋 Checking data structure...")
    assert 'recommendations' in data, "Missing 'recommendations' key"
    assert 'summary' in data, "Missing 'summary' key"
    print("✅ Top-level structure valid")
    
    # Check summary
    print("\n📊 Checking summary...")
    summary = data['summary']
    assert 'total_recommendations' in summary
    assert 'by_priority' in summary
    assert 'by_category' in summary
    print(f"✅ Summary valid - {summary['total_recommendations']} total recommendations")
    
    # Validate each recommendation
    print("\n🔍 Validating individual recommendations...")
    all_recommendations = []
    categories = data['recommendations']
    
    required_fields = ['category', 'priority', 'description', 'impact', 'effort', 'rationale']
    valid_priorities = ['P0', 'P1', 'P2', 'P3']
    
    for category, recs in categories.items():
        for rec in recs:
            all_recommendations.append(rec)
            
            # Check required fields
            for field in required_fields:
                assert field in rec, f"Recommendation missing '{field}' field: {rec}"
            
            # Validate priority
            priority = rec['priority']
            assert priority in valid_priorities, f"Invalid priority '{priority}' (must be one of {valid_priorities})"
            
            # Validate types
            assert isinstance(rec['description'], str), "Description must be string"
            assert isinstance(rec['impact'], str), "Impact must be string"
            assert isinstance(rec['effort'], str), "Effort must be string"
            assert isinstance(rec['rationale'], str), "Rationale must be string"
    
    print(f"✅ All {len(all_recommendations)} recommendations have valid structure")
    print(f"   Priority distribution: {summary['by_priority']}")
    print(f"   Category distribution: {summary['by_category']}")
    
    return True


def test_recommendations_render_in_dashboard():
    """Test that recommendations render without JavaScript errors"""
    
    print("\n" + "="*70)
    print("TESTING RECOMMENDATIONS RENDERING IN DASHBOARD")
    print("="*70)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-software-rasterizer')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(60)  # Increased timeout
        driver.set_script_timeout(30)
        
        # Load dashboard
        print("\n🌐 Loading dashboard...")
        driver.get('http://localhost:8080/ui/index.html?source=cleansolidapp')
        
        # Wait for page to load
        time.sleep(5)
        
        # Check initial console errors
        logs_before = driver.get_log('browser')
        errors_before = [log for log in logs_before if log['level'] == 'SEVERE' and 'favicon' not in log['message']]
        
        if errors_before:
            print(f"⚠️  Found {len(errors_before)} errors before clicking recommendations:")
            for error in errors_before[:3]:
                print(f"   - {error['message'][:100]}")
        
        # Find and click Recommendations tab
        print("\n🔘 Clicking Recommendations tab...")
        
        # Wait for tabs to be available
        WebDriverWait(driver, 15).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "button")) > 0
        )
        
        # Find recommendations button by text
        buttons = driver.find_elements(By.TAG_NAME, "button")
        recommendations_button = None
        
        for button in buttons:
            if 'recommendation' in button.text.lower():
                recommendations_button = button
                break
        
        if not recommendations_button:
            print("❌ Could not find Recommendations tab button")
            return False
        
        # Click the button
        driver.execute_script("arguments[0].click();", recommendations_button)
        time.sleep(3)
        
        # Check for errors after clicking
        logs_after = driver.get_log('browser')
        errors_after = [log for log in logs_after 
                       if log['level'] == 'SEVERE' 
                       and 'favicon' not in log['message']
                       and log not in logs_before]
        
        if errors_after:
            print(f"\n❌ Found {len(errors_after)} new errors after clicking Recommendations:")
            for error in errors_after:
                print(f"   - {error['message']}")
            return False
        
        print("✅ No JavaScript errors when rendering recommendations")
        
        # Verify recommendations content is visible
        page_source = driver.page_source
        if 'No Recommendations Available' in page_source:
            print("⚠️  Dashboard shows 'No Recommendations Available' message")
        else:
            print("✅ Recommendations content rendered")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            driver.quit()


if __name__ == '__main__':
    print("="*70)
    print("DASHBOARD RECOMMENDATIONS INTEGRATION TESTS")
    print("="*70)
    
    # Test 1: Data structure
    success1 = test_recommendations_data_structure()
    
    # Test 2: Dashboard rendering
    success2 = test_recommendations_render_in_dashboard()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"{'✅ PASS' if success1 else '❌ FAIL'} - Recommendations Data Structure")
    print(f"{'✅ PASS' if success2 else '❌ FAIL'} - Dashboard Rendering")
    
    sys.exit(0 if (success1 and success2) else 1)

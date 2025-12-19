#!/usr/bin/env python3
"""Simple console log capture test"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

driver = None
try:
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(90)
    
    print("Loading dashboard...")
    driver.get('http://localhost:8080/ui/index.html?source=cleansolidapp')
    
    print("Waiting for page to settle...")
    time.sleep(5)
    
    print("\n" + "="*70)
    print("CONSOLE LOGS AFTER INITIAL LOAD")
    print("="*70)
    logs = driver.get_log('browser')
    for log in logs:
        if 'favicon' not in log['message']:
            print(f"[{log['level']}] {log['message'][:200]}")
    
    # Find recommendations tab
    print("\n" + "="*70)
    print("CLICKING RECOMMENDATIONS TAB")
    print("="*70)
    
    # Use JavaScript to click
    script = """
        const buttons = document.querySelectorAll('button');
        for (const btn of buttons) {
            if (btn.textContent.toLowerCase().includes('recommendation')) {
                btn.click();
                return true;
            }
        }
        return false;
    """
    
    clicked = driver.execute_script(script)
    print(f"Clicked: {clicked}")
    
    time.sleep(3)
    
    print("\n" + "="*70)
    print("CONSOLE LOGS AFTER CLICKING RECOMMENDATIONS")
    print("="*70)
    logs = driver.get_log('browser')
    for log in logs:
        if 'favicon' not in log['message']:
            print(f"[{log['level']}] {log['message'][:200]}")
    
    # Check for trace logs
    print("\n" + "="*70)
    print("CHECKING FOR TRACE LOGS")
    print("="*70)
    trace_logs = [log for log in logs if '[TRACE]' in log['message'] or '[TRANSFORM]' in log['message']]
    if trace_logs:
        for log in trace_logs:
            print(log['message'])
    else:
        print("No trace logs found")
    
    print("\n✅ Test completed successfully")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    if driver:
        driver.quit()

#!/usr/bin/env python3
"""Quick check for dashboard console errors"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL', 'performance': 'ALL'})

driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(30)

try:
    print("🌐 Loading dashboard...")
    driver.get('http://localhost:8080/ui/index.html?source=cleansolidapp')
    time.sleep(3)
    
    print("\n📋 Initial console logs:")
    for log in driver.get_log('browser'):
        if 'favicon' not in log['message'].lower():
            print(f"  [{log['level']}] {log['message'][:150]}")
    
    print("\n🔘 Clicking Recommendations tab...")
    driver.execute_script("""
        const buttons = Array.from(document.querySelectorAll('button'));
        const recBtn = buttons.find(b => b.textContent.toLowerCase().includes('recommendation'));
        if (recBtn) recBtn.click();
    """)
    time.sleep(2)
    
    print("\n📋 Console logs after clicking:")
    for log in driver.get_log('browser'):
        msg = log['message']
        if 'favicon' not in msg.lower():
            # Highlight important logs
            if any(kw in msg for kw in ['TRANSFORM', 'TRACE', 'ERROR', 'undefined', 'Cannot read']):
                print(f"  ⚠️ [{log['level']}] {msg[:200]}")
            elif log['level'] == 'SEVERE':
                print(f"  ❌ [{log['level']}] {msg[:200]}")
    
    # Check page content
    page_text = driver.find_element(By.TAG_NAME, 'body').text
    if 'No Recommendations Available' in page_text:
        print("\n⚠️ Page shows: 'No Recommendations Available'")
    elif 'technical_debt' in page_text.lower() or 'testing framework' in page_text.lower():
        print("\n✅ Recommendations appear to be rendering!")
    
    print("\n✅ Test complete - check console output above")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    driver.quit()

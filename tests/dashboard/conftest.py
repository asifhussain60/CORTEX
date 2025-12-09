"""
Dashboard test configuration with progress indicators and Selenium fixtures.

Provides visual feedback for long-running tests to prevent appearance of hang.
Includes Chrome driver fixtures for E2E testing.

Author: Asif Hussain
Date: December 9, 2025
"""

import pytest
import sys
import time
from datetime import datetime
from pathlib import Path

# Selenium imports (will be installed when tests run)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """Show test progress for long-running tests."""
    test_name = item.nodeid.split("::")[-1]
    
    # Print start marker for visibility (ASCII only for cross-platform compatibility)
    print(f"\n{'='*60}")
    print(f"[START] {test_name}")
    print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    sys.stdout.flush()
    
    # Run the test
    yield
    
    # Print completion marker
    print(f"\n{'='*60}")
    print(f"[DONE] {test_name}")
    print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}\n")
    sys.stdout.flush()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Show phase progress (setup/call/teardown)."""
    outcome = yield
    report = outcome.get_result()
    
    if call.when == "call":
        test_name = item.nodeid.split("::")[-1]
        duration = f"{report.duration:.1f}s"
        
        if report.passed:
            print(f"   [PASS] Test execution completed in {duration}")
        elif report.failed:
            print(f"   [FAIL] Test failed after {duration}")
        elif report.skipped:
            print(f"   [SKIP] Test skipped")


# ============================================
# SELENIUM FIXTURES
# ============================================

@pytest.fixture(scope="session")
def dashboard_url():
    """
    Dashboard URL with mock data source.
    
    NOTE: Assumes dashboard server is running on http://localhost:8080
    Start server with: python -m src.orchestrators.dashboard_launcher
    """
    return "http://localhost:8080/ui/index.html?source=mock"


@pytest.fixture(scope="function")
def driver(dashboard_url):
    """
    Create Chrome driver in headless mode for testing.
    
    Yields:
        WebDriver instance configured for dashboard testing
    """
    if not SELENIUM_AVAILABLE:
        pytest.skip("Selenium not installed. Install with: pip install selenium")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    
    # Enable browser logging
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        pytest.skip(f"Chrome driver not available: {e}")
    
    driver.implicitly_wait(10)
    
    # Load dashboard
    try:
        driver.get(dashboard_url)
    except Exception as e:
        driver.quit()
        pytest.skip(f"Dashboard server not running on {dashboard_url}: {e}")
    
    # Wait for page to be ready
    try:
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        # Wait for app initialization
        time.sleep(2)
    except Exception as e:
        driver.quit()
        pytest.skip(f"Dashboard failed to load: {e}")
    
    yield driver
    
    # Teardown: Check for critical console errors
    try:
        logs = driver.get_log('browser')
        critical_errors = [
            log for log in logs 
            if log['level'] == 'SEVERE' and 'ERR_' in log.get('message', '')
        ]
        
        if critical_errors:
            print(f"\n⚠️  CRITICAL CONSOLE ERRORS DETECTED:")
            for error in critical_errors[:5]:  # Show first 5
                print(f"   - {error['message'][:200]}")
    except Exception:
        pass
    
    driver.quit()


@pytest.fixture(scope="function")
def mobile_driver(dashboard_url):
    """
    Create mobile viewport driver (375px width).
    
    Yields:
        WebDriver instance configured for mobile testing
    """
    if not SELENIUM_AVAILABLE:
        pytest.skip("Selenium not installed")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=375,667")
    options.add_argument("--disable-gpu")
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(dashboard_url)
        
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        yield driver
        driver.quit()
    except Exception as e:
        pytest.skip(f"Mobile driver setup failed: {e}")


# Helper functions

def wait_for_element(driver, by, value, timeout=10):
    """Wait for element to be visible."""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )


def take_screenshot(driver, filename):
    """Take screenshot for debugging."""
    screenshot_dir = Path(__file__).parent / "screenshots"
    screenshot_dir.mkdir(exist_ok=True)
    
    filepath = screenshot_dir / filename
    driver.save_screenshot(str(filepath))
    print(f"📸 Screenshot saved: {filepath}")

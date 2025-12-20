# Selenium Tests Archive

**Archived:** December 20, 2025  
**Reason:** Selenium removed from CORTEX 4.0 in favor of Playwright as the preferred E2E/browser testing framework

## Archived Files

**Total:** 6 test files (~75 KB)

1. `test_intelligence.py` (19.6 KB) - Test intelligence framework with Selenium template generation
2. `test_landing_page.py` (7.2 KB) - Landing page E2E tests
3. `test_phase1_design.py` (15.9 KB) - Phase 1 design validation tests
4. `test_phase2_navigation.py` (12.5 KB) - Phase 2 navigation tests
5. `test_test_intelligence.py` (14.7 KB) - Test intelligence unit tests
6. `test_visual_design.py` (5.2 KB) - Visual design validation tests

## Migration Notes

These tests were written for legacy functionality that:
- Used Selenium WebDriver API (deprecated in CORTEX 4.0)
- Had varying levels of completion and usage
- Required 170 MB Selenium dependency + browser drivers
- Had no production usage in CORTEX core (`src/`)

## CORTEX 4.0 Standard

**Preferred E2E/Browser Testing Framework:** Playwright

**Rationale:**
- Modern async API with better developer experience
- Superior cross-browser support (Chromium, Firefox, WebKit)
- Built-in test utilities (auto-waiting, network interception, screenshots)
- Smaller footprint (~80 MB vs Selenium's 170 MB)
- Active Microsoft development and support
- Better debugging tools (trace viewer, inspector, video recording)

**Replacement Tests:**
- `tests/misc/test_dashboard_playwright.py` - Comprehensive Playwright test suite
- `tests/misc/test_css_fixes.py` - Existing Playwright usage example

## Recovery

If these tests are needed in the future:
1. Restore files from this archive
2. Update imports: `from selenium import webdriver` → `from playwright.sync_api import sync_playwright`
3. Rewrite using Playwright API (see conversion guide below)
4. Install: `pip install playwright && playwright install chromium`

### Quick Conversion Guide

**Selenium:**
```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("http://localhost:8080")
element = driver.find_element(By.ID, "submit")
element.click()
driver.quit()
```

**Playwright:**
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:8080")
    page.click("#submit")
    browser.close()
```

**Key Differences:**
- Context managers instead of manual cleanup
- CSS selectors instead of By locators
- Auto-waiting (no explicit waits needed)
- expect() for assertions instead of assert

---

**Reference:** CORTEX 4.0 Phase 6 - Orchestrator Consolidation  
**Migration Report:** `cortex-brain/documents/reports/SELENIUM-TO-PLAYWRIGHT-MIGRATION.md`  
**Contact:** Asif Hussain | github.com/asifhussain60/CORTEX

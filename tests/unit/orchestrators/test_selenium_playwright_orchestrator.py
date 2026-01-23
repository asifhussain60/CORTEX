"""
Selenium to Playwright Orchestrator Tests - TDD First (CORE-008)

Tests for SeleniumPlaywrightOrchestrator which converts Selenium test code
to Playwright test code with pattern matching and AST transformation.

Author: Asif Hussain
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock


class TestSeleniumPlaywrightOrchestratorInterface:
    """Test orchestrator interface compliance."""
    
    def test_implements_i_orchestrator(self) -> None:
        """Verify orchestrator implements IOrchestrator interface."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPlaywrightOrchestrator
        )
        from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator
        
        orchestrator = SeleniumPlaywrightOrchestrator()
        assert isinstance(orchestrator, IOrchestrator)
    
    def test_get_name_returns_correct_name(self) -> None:
        """Verify orchestrator name."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPlaywrightOrchestrator
        )
        
        orchestrator = SeleniumPlaywrightOrchestrator()
        assert orchestrator.get_name() == "SeleniumPlaywrightOrchestrator"
    
    def test_get_version_returns_semver(self) -> None:
        """Verify version follows semver."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPlaywrightOrchestrator
        )
        import re
        
        orchestrator = SeleniumPlaywrightOrchestrator()
        version = orchestrator.get_version()
        assert re.match(r"^\d+\.\d+\.\d+$", version)
    
    def test_initialize_returns_result(self) -> None:
        """Verify initialize returns Result type."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPlaywrightOrchestrator
        )
        from cortex.brain.core.result import Result
        
        orchestrator = SeleniumPlaywrightOrchestrator()
        result = orchestrator.initialize()
        assert isinstance(result, Result)
    
    def test_get_mode_returns_operation_mode(self) -> None:
        """Verify get_mode returns OperationMode."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPlaywrightOrchestrator
        )
        from cortex.brain.core.interfaces.i_orchestrator import OperationMode
        
        orchestrator = SeleniumPlaywrightOrchestrator()
        mode = orchestrator.get_mode()
        assert isinstance(mode, OperationMode)


class TestSeleniumPatternMatcher:
    """Test Selenium pattern detection."""
    
    def test_detect_webdriver_import(self) -> None:
        """Detect Selenium WebDriver imports."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPatternMatcher
        )
        
        code = """
from selenium import webdriver
from selenium.webdriver.common.by import By
"""
        matcher = SeleniumPatternMatcher()
        patterns = matcher.detect_patterns(code)
        
        assert "webdriver_import" in patterns
        assert "by_import" in patterns
    
    def test_detect_driver_initialization(self) -> None:
        """Detect driver initialization patterns."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPatternMatcher
        )
        
        code = """
driver = webdriver.Chrome()
driver = webdriver.Firefox()
"""
        matcher = SeleniumPatternMatcher()
        patterns = matcher.detect_patterns(code)
        
        assert "chrome_driver" in patterns
        assert "firefox_driver" in patterns
    
    def test_detect_find_element_patterns(self) -> None:
        """Detect find_element patterns."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPatternMatcher
        )
        
        code = """
element = driver.find_element(By.ID, "submit")
elements = driver.find_elements(By.CLASS_NAME, "item")
driver.find_element(By.XPATH, "//div[@id='main']")
driver.find_element(By.CSS_SELECTOR, ".button")
"""
        matcher = SeleniumPatternMatcher()
        patterns = matcher.detect_patterns(code)
        
        assert "find_element_by_id" in patterns
        assert "find_elements" in patterns
        assert "find_element_by_xpath" in patterns
        assert "find_element_by_css" in patterns
    
    def test_detect_wait_patterns(self) -> None:
        """Detect WebDriverWait patterns."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPatternMatcher
        )
        
        code = """
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.ID, "element")))
"""
        matcher = SeleniumPatternMatcher()
        patterns = matcher.detect_patterns(code)
        
        assert "webdriver_wait" in patterns
        assert "expected_conditions" in patterns
    
    def test_detect_action_patterns(self) -> None:
        """Detect user action patterns."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPatternMatcher
        )
        
        code = """
element.click()
element.send_keys("text")
element.clear()
element.submit()
driver.get("https://example.com")
"""
        matcher = SeleniumPatternMatcher()
        patterns = matcher.detect_patterns(code)
        
        assert "click_action" in patterns
        assert "send_keys_action" in patterns
        assert "clear_action" in patterns
        assert "navigate_action" in patterns


class TestPlaywrightCodeGenerator:
    """Test Playwright code generation."""
    
    def test_generate_imports(self) -> None:
        """Generate Playwright imports."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            PlaywrightCodeGenerator
        )
        
        generator = PlaywrightCodeGenerator()
        imports = generator.generate_imports(sync_api=True)
        
        assert "from playwright.sync_api import sync_playwright" in imports
    
    def test_generate_async_imports(self) -> None:
        """Generate async Playwright imports."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            PlaywrightCodeGenerator
        )
        
        generator = PlaywrightCodeGenerator()
        imports = generator.generate_imports(sync_api=False)
        
        assert "from playwright.async_api import async_playwright" in imports
    
    def test_convert_find_element_to_locator(self) -> None:
        """Convert find_element to Playwright locator."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            PlaywrightCodeGenerator
        )
        
        generator = PlaywrightCodeGenerator()
        
        # By.ID -> page.locator("#id")
        result = generator.convert_selector("By.ID", "submit")
        assert result == 'page.locator("#submit")'
        
        # By.CLASS_NAME -> page.locator(".class")
        result = generator.convert_selector("By.CLASS_NAME", "button")
        assert result == 'page.locator(".button")'
        
        # By.CSS_SELECTOR -> page.locator("selector")
        result = generator.convert_selector("By.CSS_SELECTOR", ".main > div")
        assert result == 'page.locator(".main > div")'
        
        # By.XPATH -> page.locator("xpath=...")
        result = generator.convert_selector("By.XPATH", "//div[@id='main']")
        assert result == "page.locator(\"xpath=//div[@id='main']\")"
    
    def test_convert_actions(self) -> None:
        """Convert Selenium actions to Playwright."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            PlaywrightCodeGenerator
        )
        
        generator = PlaywrightCodeGenerator()
        
        # click() -> click()
        assert generator.convert_action("click") == "click()"
        
        # send_keys("text") -> fill("text")
        assert generator.convert_action("send_keys", "text") == 'fill("text")'
        
        # clear() -> clear()
        assert generator.convert_action("clear") == "clear()"
        
        # get(url) -> goto(url)
        assert generator.convert_action("get", "https://example.com") == 'goto("https://example.com")'
    
    def test_convert_wait_to_auto_waiting(self) -> None:
        """Convert explicit waits to Playwright auto-waiting."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            PlaywrightCodeGenerator
        )
        
        generator = PlaywrightCodeGenerator()
        
        # WebDriverWait -> removed (Playwright auto-waits)
        result = generator.convert_wait("presence_of_element_located")
        assert result == "# Playwright auto-waits for elements"
        
        # visibility wait -> wait_for with visible state
        result = generator.convert_wait("visibility_of_element_located")
        assert "wait_for(state='visible')" in result


class TestConversionEngine:
    """Test full file conversion."""
    
    def test_convert_simple_test(self) -> None:
        """Convert simple Selenium test to Playwright."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            ConversionEngine
        )
        
        selenium_code = '''
from selenium import webdriver
from selenium.webdriver.common.by import By

def test_login():
    driver = webdriver.Chrome()
    driver.get("https://example.com/login")
    driver.find_element(By.ID, "username").send_keys("user")
    driver.find_element(By.ID, "password").send_keys("pass")
    driver.find_element(By.ID, "submit").click()
    driver.quit()
'''
        
        engine = ConversionEngine()
        result = engine.convert(selenium_code)
        
        assert result.is_ok()
        playwright_code = result.unwrap()
        
        assert "from playwright.sync_api import" in playwright_code
        assert 'page.goto("https://example.com/login")' in playwright_code
        assert 'page.locator("#username").fill("user")' in playwright_code
        assert 'page.locator("#submit").click()' in playwright_code
    
    def test_convert_with_waits(self) -> None:
        """Convert test with explicit waits."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            ConversionEngine
        )
        
        selenium_code = '''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_dynamic_content():
    driver = webdriver.Chrome()
    driver.get("https://example.com")
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.presence_of_element_located((By.ID, "dynamic")))
    element.click()
    driver.quit()
'''
        
        engine = ConversionEngine()
        result = engine.convert(selenium_code)
        
        assert result.is_ok()
        playwright_code = result.unwrap()
        
        # Waits should be simplified/removed (Playwright auto-waits)
        assert "WebDriverWait" not in playwright_code
        assert "expected_conditions" not in playwright_code
    
    def test_preserve_test_structure(self) -> None:
        """Preserve test function structure and assertions."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            ConversionEngine
        )
        
        selenium_code = '''
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

class TestUserFlow:
    def test_user_can_register(self):
        driver = webdriver.Chrome()
        driver.get("https://example.com/register")
        assert "Register" in driver.title
        driver.quit()
'''
        
        engine = ConversionEngine()
        result = engine.convert(selenium_code)
        
        assert result.is_ok()
        playwright_code = result.unwrap()
        
        # Structure preserved
        assert "class TestUserFlow:" in playwright_code
        assert "def test_user_can_register" in playwright_code
        assert "import pytest" in playwright_code
        assert 'assert "Register"' in playwright_code


class TestConversionReport:
    """Test conversion reporting."""
    
    def test_generate_conversion_report(self) -> None:
        """Generate conversion summary report."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPlaywrightOrchestrator
        )
        
        orchestrator = SeleniumPlaywrightOrchestrator()
        
        conversion_result = {
            "files_converted": 5,
            "patterns_replaced": 42,
            "warnings": ["ActionChains not fully supported"],
            "manual_review_needed": ["test_complex.py:45"]
        }
        
        report = orchestrator.generate_report(conversion_result)
        
        assert report["total_files"] == 5
        assert report["total_patterns"] == 42
        assert len(report["warnings"]) == 1
        assert len(report["manual_review"]) == 1


class TestMCPToolExposure:
    """Test MCP tool exposure (AC-AR-011-02)."""
    
    def test_exposes_convert_file_tool(self) -> None:
        """Verify convert_file MCP tool exposed."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPlaywrightOrchestrator
        )
        
        orchestrator = SeleniumPlaywrightOrchestrator()
        tools_result = orchestrator.get_mcp_tools()
        
        assert tools_result.is_ok()
        tools = tools_result.unwrap()
        assert "convert_selenium_file" in tools
    
    def test_exposes_convert_directory_tool(self) -> None:
        """Verify convert_directory MCP tool exposed."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPlaywrightOrchestrator
        )
        
        orchestrator = SeleniumPlaywrightOrchestrator()
        tools_result = orchestrator.get_mcp_tools()
        
        assert tools_result.is_ok()
        tools = tools_result.unwrap()
        assert "convert_selenium_directory" in tools
    
    def test_exposes_analyze_tool(self) -> None:
        """Verify analyze MCP tool exposed."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPlaywrightOrchestrator
        )
        
        orchestrator = SeleniumPlaywrightOrchestrator()
        tools_result = orchestrator.get_mcp_tools()
        
        assert tools_result.is_ok()
        tools = tools_result.unwrap()
        assert "analyze_selenium_tests" in tools


class TestAuditLogging:
    """Test audit logging (AC-AR-011-03)."""
    
    def test_operations_are_audited(self) -> None:
        """Verify operations create audit entries."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPlaywrightOrchestrator
        )
        
        orchestrator = SeleniumPlaywrightOrchestrator()
        orchestrator.initialize()
        
        # Execute an operation
        orchestrator.execute_operation(
            "analyze",
            {"file_path": "test_example.py"}
        )
        
        # Check audit trail
        audit_result = orchestrator.get_audit_trail(limit=10)
        assert audit_result.is_ok()
        audit_entries = audit_result.unwrap()
        assert len(audit_entries) >= 1
    
    def test_audit_entries_have_hash_chain(self) -> None:
        """Verify audit entries form hash chain."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            SeleniumPlaywrightOrchestrator
        )
        
        orchestrator = SeleniumPlaywrightOrchestrator()
        orchestrator.initialize()
        
        # Execute multiple operations
        orchestrator.execute_operation("analyze", {"file": "test1.py"})
        orchestrator.execute_operation("analyze", {"file": "test2.py"})
        
        audit_result = orchestrator.get_audit_trail(limit=10)
        entries = audit_result.unwrap()
        
        # Verify hash chain integrity
        if len(entries) >= 2:
            assert entries[1]["previous_hash"] == entries[0]["current_hash"]


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_handles_invalid_python_syntax(self) -> None:
        """Handle files with syntax errors gracefully."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            ConversionEngine
        )
        
        invalid_code = "def test_broken(:\n    pass"
        
        engine = ConversionEngine()
        result = engine.convert(invalid_code)
        
        assert result.is_err()
        assert "syntax" in result.unwrap_err().lower()
    
    def test_handles_non_selenium_code(self) -> None:
        """Handle non-Selenium code appropriately."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            ConversionEngine
        )
        
        non_selenium = '''
def test_math():
    assert 2 + 2 == 4
'''
        
        engine = ConversionEngine()
        result = engine.convert(non_selenium)
        
        assert result.is_ok()
        # Code unchanged (no Selenium patterns)
        converted = result.unwrap()
        assert "def test_math():" in converted
    
    def test_handles_mixed_frameworks(self) -> None:
        """Handle code mixing Selenium with other frameworks."""
        from cortex.orchestrators.migration.selenium_playwright_orchestrator import (
            ConversionEngine
        )
        
        mixed_code = '''
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

def test_api_and_ui():
    response = requests.get("https://api.example.com")
    driver = webdriver.Chrome()
    driver.get("https://example.com")
    driver.quit()
'''
        
        engine = ConversionEngine()
        result = engine.convert(mixed_code)
        
        assert result.is_ok()
        converted = result.unwrap()
        # requests code preserved
        assert "import requests" in converted
        assert "requests.get" in converted

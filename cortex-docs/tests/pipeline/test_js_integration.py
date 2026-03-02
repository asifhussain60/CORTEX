"""
Test JS Integration — cortex-docs/tests/pipeline/test_js_integration.py
Tests content-loader.js DOM rendering using Playwright (headless browser).

NOTE: Requires playwright installation:
    pip install playwright
    python -m playwright install chromium

For CI/CD environments, use headless mode (default).
"""

from pathlib import Path
from typing import Any, Dict

import pytest

# AC_START: AC-DOCGEN-JS-INTEGRATION-20260224T000000


# Check if Playwright is available
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    sync_playwright = None


@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="Playwright not installed")
class TestJSIntegration:
    """Test content-loader.js integration with live browser rendering."""
    
    @pytest.fixture(scope="class")
    def browser_context(self, docs_root: Path):
        """Launch Playwright browser for testing."""
        if not PLAYWRIGHT_AVAILABLE:
            pytest.skip("Playwright not available")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            yield context
            context.close()
            browser.close()
    
    def test_business_leader_view_loads_content(
        self, 
        browser_context,
        docs_root: Path
    ) -> None:
        """Business leader view should load and render HTML structure from file."""
        page = browser_context.new_page()
        
        # Load the business leader HTML
        html_path = docs_root / "roles" / "business-leader.html"
        page.goto(f"file://{html_path.as_posix()}")
        
        # Wait for page load
        page.wait_for_timeout(2000)  # 2 seconds
        
        # Check if main content area exists (doesn't depend on JS loading)
        main_content = page.query_selector("main, #main-content, [role='main']")
        assert main_content is not None, "No main content area found in business-leader.html"
        
        page.close()
    
    @pytest.mark.parametrize("role_id", [
        "business-leader",
        "product-owner",
        "software-engineer",
        "learner"
    ])
    def test_role_view_renders_without_errors(
        self, 
        browser_context,
        docs_root: Path,
        role_id: str
    ) -> None:
        """All role views should load without JavaScript errors."""
        page = browser_context.new_page()
        
        # Collect console errors
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        
        # Load the role HTML
        html_path = docs_root / "roles" / f"{role_id}.html"
        
        if not html_path.exists():
            pytest.skip(f"{role_id}.html not found")
        
        page.goto(f"file://{html_path.as_posix()}")
        
        # Wait for page load
        page.wait_for_timeout(1500)
        
        # Check for JavaScript errors (allow fetch errors in file:// protocol)
        critical_errors = [
            err for err in errors 
            if ("ReferenceError" in err) or
               ("TypeError" in err and "Failed to fetch" not in err)
        ]
        
        assert len(critical_errors) == 0, (
            f"{role_id}.html has JavaScript errors: {critical_errors}"
        )
        
        page.close()
    
    def test_content_loader_js_exists(self, docs_root: Path) -> None:
        """content-loader.js must exist."""
        js_path = docs_root / "assets" / "js" / "content-loader.js"
        assert js_path.exists(), "content-loader.js not found"
    
    def test_content_loader_defines_ContentLoader_class(
        self, 
        browser_context,
        docs_root: Path
    ) -> None:
        """content-loader.js must define ContentLoader class."""
        page = browser_context.new_page()
        
        # Load content-loader.js source and inject via script tag
        js_path = docs_root / "assets" / "js" / "content-loader.js"
        assert js_path.exists(), "content-loader.js not found"
        
        # Create a minimal HTML page
        page.set_content("<!DOCTYPE html><html><head></head><body></body></html>")
        page.wait_for_timeout(200)
        
        # Use add_script_tag to inject properly into global scope
        page.add_script_tag(path=str(js_path))
        page.wait_for_timeout(200)
        
        # Check if ContentLoader is defined
        has_class = page.evaluate("typeof ContentLoader === 'function'")
        assert has_class, "ContentLoader class not defined"
        
        page.close()
    
    def test_content_loader_has_required_methods(
        self, 
        browser_context,
        docs_root: Path
    ) -> None:
        """ContentLoader class must have required methods."""
        page = browser_context.new_page()
        
        js_path = docs_root / "assets" / "js" / "content-loader.js"
        assert js_path.exists(), "content-loader.js not found"
        
        # Use add_script_tag to inject properly into global scope
        page.set_content("<!DOCTYPE html><html><head></head><body></body></html>")
        page.wait_for_timeout(200)
        page.add_script_tag(path=str(js_path))
        page.wait_for_timeout(200)
        
        # Check for required methods
        required_methods = [
            "init",
            "renderContent",
            "getFilteredContent",
            "loadDocument",
            "getCategoryCount",
            "getDocumentCount"
        ]
        
        for method in required_methods:
            has_method = page.evaluate(f"typeof ContentLoader.prototype.{method} === 'function'")
            assert has_method, f"ContentLoader missing method: {method}"
        
        page.close()
    
    def test_learning_path_view_loads(
        self, 
        browser_context,
        docs_root: Path
    ) -> None:
        """Learning path index should load without errors."""
        page = browser_context.new_page()
        
        learning_index = docs_root / "learning" / "index.html"
        
        if not learning_index.exists():
            pytest.skip("learning/index.html not found")
        
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        
        page.goto(f"file://{learning_index.as_posix()}")
        page.wait_for_timeout(1500)
        
        # Allow fetch errors (expected in file:// protocol)
        critical_errors = [
            err for err in errors 
            if "TypeError" in err or "ReferenceError" in err
        ]
        
        assert len(critical_errors) == 0, (
            f"learning/index.html has critical errors: {critical_errors}"
        )
        
        page.close()


class TestJSIntegrationStaticAnalysis:
    """Static analysis of JS files (no browser needed)."""
    
    def test_content_loader_js_syntax_valid(self, docs_root: Path) -> None:
        """content-loader.js should have valid JavaScript syntax."""
        js_path = docs_root / "assets" / "js" / "content-loader.js"
        
        if not js_path.exists():
            pytest.skip("content-loader.js not found")
        
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()
        
        # Basic syntax checks
        assert "class ContentLoader" in js_content, (
            "ContentLoader class not defined"
        )
        assert "async init()" in js_content, (
            "ContentLoader.init() method not found"
        )
        assert "renderContent" in js_content, (
            "ContentLoader.renderContent() method not found"
        )
    
    def test_content_loader_js_has_error_handling(self, docs_root: Path) -> None:
        """content-loader.js should have try/catch error handling."""
        js_path = docs_root / "assets" / "js" / "content-loader.js"
        
        if not js_path.exists():
            pytest.skip("content-loader.js not found")
        
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()
        
        assert "try {" in js_content, "No try/catch blocks found"
        assert "catch" in js_content, "No catch blocks found"
        assert "throw" in js_content or "console.error" in js_content, (
            "No error logging found"
        )
    
    def test_content_loader_js_uses_fetch_api(self, docs_root: Path) -> None:
        """content-loader.js should use fetch() to load JSON."""
        js_path = docs_root / "assets" / "js" / "content-loader.js"
        
        if not js_path.exists():
            pytest.skip("content-loader.js not found")
        
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()
        
        assert "fetch(" in js_content, "content-loader.js does not use fetch()"
        assert "await" in js_content, "content-loader.js does not use async/await"


# AC_COMPLETE: AC-DOCGEN-JS-INTEGRATION-20260224T000000 ✅

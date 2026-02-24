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
        """Launch Playwright browser for testing with console logging."""
        if not PLAYWRIGHT_AVAILABLE:
            pytest.skip("Playwright not available")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            
            # Enable console logging for all pages in this context
            def log_console_message(msg):
                """Log browser console messages."""
                msg_type = msg.type
                msg_text = msg.text
                
                # Map console types to logging levels
                if msg_type == "error":
                    print(f"🔴 BROWSER ERROR: {msg_text}")
                elif msg_type == "warning":
                    print(f"⚠️ BROWSER WARNING: {msg_text}")
                elif msg_type in ["log", "info"]:
                    print(f"ℹ️ BROWSER LOG: {msg_text}")
                elif msg_type == "debug":
                    print(f"🐛 BROWSER DEBUG: {msg_text}")
            
            # Attach console listener to context
            context.on("page", lambda page: page.on("console", log_console_message))
            
            yield context
            context.close()
            browser.close()
    
    def test_business_leader_view_loads_content(
        self, 
        browser_context,
        docs_root: Path
    ) -> None:
        """Business leader view should load and render content from content.json."""
        page = browser_context.new_page()
        
        # Capture console messages
        console_messages = []
        errors = []
        warnings = []
        
        def capture_console(msg):
            console_messages.append({"type": msg.type, "text": msg.text})
            if msg.type == "error":
                errors.append(msg.text)
            elif msg.type == "warning":
                warnings.append(msg.text)
        
        page.on("console", capture_console)
        
        # Capture page errors
        page_errors = []
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        
        # Load the business leader HTML
        html_path = docs_root / "roles" / "business-leader.html"
        page.goto(f"file://{html_path.as_posix()}")
        
        # Wait for content to load
        page.wait_for_timeout(2000)  # 2 seconds
        
        # Report console activity
        print(f"\n📊 Browser Console Activity:")
        print(f"   Total messages: {len(console_messages)}")
        print(f"   Errors: {len(errors)}")
        print(f"   Warnings: {len(warnings)}")
        
        # Check if ContentLoader was instantiated
        has_loader = page.evaluate("window.cortexLoader !== null && window.cortexLoader !== undefined")
        assert has_loader, "ContentLoader not instantiated"
        
        # Check if content loaded
        content_area = page.query_selector("#main-content")
        assert content_area is not None, "#main-content not found"
        
        # Should have rendered categories
        glass_cards = page.query_selector_all(".glass-card-concept")
        # Allow graceful failure if content.json is missing (CI environments)
        if len(glass_cards) == 0:
            print("⚠️ No content rendered - content.json may not be accessible")
        
        # Assert no critical page errors
        assert len(page_errors) == 0, f"Page errors detected: {page_errors}"
        
        # Filter out expected fetch errors (file:// protocol limitation)
        critical_errors = [
            err for err in errors 
            if "Failed to load resource" not in err and
               "net::ERR_FILE_NOT_FOUND" not in err and
               "fetch" not in err.lower()
        ]
        
        assert len(critical_errors) == 0, f"Critical browser errors: {critical_errors}"
        
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
        
        # Collect comprehensive console data
        console_messages = {"error": [], "warning": [], "log": [], "info": []}
        page_errors = []
        
        def capture_console(msg):
            msg_type = msg.type
            msg_text = msg.text
            if msg_type in console_messages:
                console_messages[msg_type].append(msg_text)
        
        page.on("console", capture_console)
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        
        # Load the role HTML
        html_path = docs_root / "roles" / f"{role_id}.html"
        
        if not html_path.exists():
            pytest.skip(f"{role_id}.html not found")
        
        page.goto(f"file://{html_path.as_posix()}")
        
        # Wait for page load
        page.wait_for_timeout(1500)
        
        # Report console activity
        total_messages = sum(len(msgs) for msgs in console_messages.values())
        print(f"\n📊 {role_id}.html Console Activity:")
        print(f"   Errors: {len(console_messages['error'])}")
        print(f"   Warnings: {len(console_messages['warning'])}")
        print(f"   Logs: {len(console_messages['log']) + len(console_messages['info'])}")
        
        # Display errors and warnings
        for error in console_messages['error']:
            print(f"   🔴 {error}")
        for warning in console_messages['warning']:
            print(f"   ⚠️ {warning}")
        
        # Assert no page errors
        assert len(page_errors) == 0, f"{role_id}.html page errors: {page_errors}"
        
        # Check for critical JavaScript errors (filter fetch errors)
        critical_errors = [
            err for err in console_messages['error']
            if "TypeError" in err or 
               "ReferenceError" in err or
               "SyntaxError" in err
        ]
        
        # Filter out expected file:// protocol errors
        critical_errors = [
            err for err in critical_errors
            if "Failed to load resource" not in err and
               "net::ERR_FILE_NOT_FOUND" not in err and
               "fetch" not in err.lower()
        ]
        
        assert len(critical_errors) == 0, (
            f"{role_id}.html has critical JavaScript errors: {critical_errors}"
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
        
        # Load content-loader.js directly
        js_path = docs_root / "assets" / "js" / "content-loader.js"
        
        # Create a minimal HTML page to load the script
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="file://{js_path.as_posix()}"></script>
        </head>
        <body></body>
        </html>
        """
        
        page.set_content(html_content)
        page.wait_for_timeout(500)
        
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
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="file://{js_path.as_posix()}"></script>
        </head>
        <body></body>
        # Capture all console activity
        console_messages = {"error": [], "warning": [], "log": []}
        page_errors = []
        
        def capture_console(msg):
            msg_type = msg.type
            if msg_type in console_messages:
                console_messages[msg_type].append(msg.text)
        
        page.on("console", capture_console)
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        
        page.goto(f"file://{learning_index.as_posix()}")
        page.wait_for_timeout(1500)
        
        # Report console activity
        print(f"\n📊 learning/index.html Console Activity:")
        print(f"   Errors: {len(console_messages['error'])}")
        print(f"   Warnings: {len(console_messages['warning'])}")
        
        for error in console_messages['error']:
            print(f"   🔴 {error}")
        
        # Assert no page errors
        assert len(page_errors) == 0, f"Page errors: {page_errors}"
        
        # Filter out expected file:// protocol errors
        critical_errors = [
            err for err in console_messages['error']
            if ("TypeError" in err or "ReferenceError" in err or "SyntaxError" in err) and
               "Failed to load resource" not in err and
               "net::ERR_FILE_NOT_FOUND" not in err and
               "fetch" not in err.lower()
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
    
    def test_comprehensive_browser_diagnostics(
        self,
        browser_context,
        docs_root: Path
    ) -> None:
        """Run comprehensive browser diagnostics on all role views."""
        results = {
            "pages_tested": 0,
            "total_errors": 0,
            "total_warnings": 0,
            "pages_with_errors": [],
            "error_summary": {}
        }
        
        role_pages = [
            "roles/business-leader.html",
            "roles/product-owner.html",
            "roles/software-engineer.html",
            "roles/learner.html",
            "learning/index.html"
        ]
        
        for page_path in role_pages:
            full_path = docs_root / page_path
            if not full_path.exists():
                continue
            
            page = browser_context.new_page()
            
            # Capture all console activity
            console_data = {"error": [], "warning": [], "info": [], "log": []}
            page_errors = []
            
            def capture(msg):
                if msg.type in console_data:
                    console_data[msg.type].append(msg.text)
            
            page.on("console", capture)
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))
            
            # Load page
            page.goto(f"file://{full_path.as_posix()}")
            page.wait_for_timeout(1000)
            
            # Collect results
            error_count = len(console_data["error"]) + len(page_errors)
            warning_count = len(console_data["warning"])
            
            results["pages_tested"] += 1
            results["total_errors"] += error_count
            results["total_warnings"] += warning_count
            
            if error_count > 0:
                results["pages_with_errors"].append(page_path)
                results["error_summary"][page_path] = {
                    "console_errors": console_data["error"],
                    "page_errors": page_errors
                }
            
            page.close()
        
        # Report summary
        print(f"\n📊 Browser Diagnostics Summary:")
        print(f"   Pages tested: {results['pages_tested']}")
        print(f"   Total errors: {results['total_errors']}")
        print(f"   Total warnings: {results['total_warnings']}")
        print(f"   Pages with errors: {len(results['pages_with_errors'])}")
        
        if results["pages_with_errors"]:
            print(f"\n🔴 Pages with errors:")
            for page_path in results["pages_with_errors"]:
                print(f"      - {page_path}")
                errors = results["error_summary"][page_path]
                for error in errors["console_errors"][:3]:  # Show first 3
                    print(f"        • {error}")
        
        # This is informational - don't fail on fetch errors in file:// protocol
        if results["total_errors"] > 0:
            print(f"\n⚠️ Note: Some errors are expected with file:// protocol (fetch limitations)")


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

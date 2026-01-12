"""
Unit tests for CORTEX Response Header/Footer Manager (AC-HEADER-001)

Tests the dynamic header/footer injection system to ensure:
- Headers are generated correctly in all formats
- Headers include required metadata (version, date, author, copyright)
- Headers can be injected into responses
- Configuration is loaded correctly
- Singleton pattern works as expected

Author: GitHub Copilot
Created: 2026-01-12
"""

import pytest
import re
from datetime import datetime
from pathlib import Path
from src.infrastructure.response_header_footer_manager import (
    ResponseHeaderFooterManager,
    get_header_footer_manager,
    inject_cortex_header,
    wrap_cortex_response
)


class TestResponseHeaderFooterManager:
    """Test suite for ResponseHeaderFooterManager"""
    
    @pytest.fixture
    def manager(self):
        """Create a fresh manager instance for each test"""
        return ResponseHeaderFooterManager()
    
    def test_manager_initialization(self, manager):
        """Test that manager initializes correctly"""
        assert manager is not None
        assert manager.config_path == Path("cortex-brain/response-templates-v4.yaml")
        assert manager.header_template != ""
    
    def test_markdown_header_format(self, manager):
        """Test markdown header includes all required elements"""
        header = manager.generate_header("Execution", "6.0.0", "markdown")
        
        # Check for required elements (accounting for markdown bold formatting)
        assert "CORTEX Execution" in header
        assert "6.0.0" in header  # Version number present
        assert "Asif Hussain" in header  # Author name present
        assert "Copyright © 2025-2026 Asif Hussain" in header
        assert "All rights reserved" in header
        
        # Check format (markdown should have ## for heading)
        assert "## 🧠 CORTEX" in header or "# CORTEX" in header
        assert "---" in header
    
    def test_markdown_header_timestamp(self, manager):
        """Test markdown header includes timestamp"""
        header = manager.generate_header("Planning", "6.0.0", "markdown")
        
        # Should have ISO datetime format with Z suffix
        iso_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
        assert re.search(iso_pattern, header), f"No ISO timestamp found in: {header}"
    
    def test_html_header_format(self, manager):
        """Test HTML header includes all required elements and styling"""
        header = manager.generate_header("Validation", "6.0.0", "html")
        
        # Check for HTML structure
        assert "<!-- CORTEX Response Header" in header
        assert "<div class=\"cortex-header\"" in header
        assert "CORTEX Validation" in header
        assert "6.0.0" in header  # Version number present (formatting may vary)
        assert "Copyright © 2025-2026" in header
        
        # Check for glassmorphism styling
        assert "rgba(" in header
        assert "backdrop" in header or "linear-gradient" in header
    
    def test_json_header_format(self, manager):
        """Test JSON header format"""
        header = manager.generate_header("Implementation", "6.0.0", "json")
        
        # Should contain JSON metadata structure
        assert "_header" in header
        assert "operation_type" in header
        assert "version" in header
        assert "timestamp" in header
        assert "author" in header
        assert "copyright" in header
    
    def test_plaintext_header_format(self, manager):
        """Test plaintext header format"""
        header = manager.generate_header("Testing", "6.0.0", "plaintext")
        
        # Should have ASCII box
        assert "=" * 20 in header
        assert "CORTEX Testing" in header
        assert "Version: 6.0.0" in header
        assert "Copyright © 2025-2026" in header
    
    def test_markdown_footer_format(self, manager):
        """Test markdown footer includes attribution"""
        footer = manager.generate_footer(format="markdown")
        
        assert "CORTEX 6.0.0" in footer
        assert "Autonomous Execution Engine" in footer
        assert "Copyright © 2025-2026" in footer
    
    def test_html_footer_format(self, manager):
        """Test HTML footer includes attribution"""
        footer = manager.generate_footer(format="html")
        
        assert "<!-- CORTEX Response Footer" in footer
        assert "<div class=\"cortex-footer\"" in footer
        assert "CORTEX 6.0.0" in footer
    
    def test_wrap_response_markdown(self, manager):
        """Test wrapping content in markdown format"""
        content = "• Test outcome\n• All tests passing"
        wrapped = manager.wrap_response(
            content,
            operation_type="Testing",
            format="markdown",
            include_footer=True
        )
        
        # Should have header first (with emoji or without)
        assert wrapped.startswith("##") or wrapped.startswith("#")
        assert "CORTEX Testing" in wrapped
        
        # Should have content in middle
        assert "Test outcome" in wrapped
        
        # Should have footer at end
        assert "CORTEX 6.0.0" in wrapped
        assert wrapped.endswith("\n")
    
    def test_wrap_response_without_footer(self, manager):
        """Test wrapping content without footer"""
        content = "Test content here"
        wrapped = manager.wrap_response(
            content,
            operation_type="Validation",
            format="markdown",
            include_footer=False
        )
        
        # Should have header (with emoji or without)
        assert "🧠 CORTEX Validation" in wrapped or "# CORTEX Validation" in wrapped
        
        # Should have content
        assert "Test content here" in wrapped
        
        # Should NOT have footer closing braces
        assert wrapped.count("}}") == 0  # No JSON-style closing
    
    def test_wrap_response_html_format(self, manager):
        """Test wrapping in HTML format"""
        content = "<p>Test content</p>"
        wrapped = manager.wrap_response(
            content,
            operation_type="Planning",
            format="html",
            include_footer=True
        )
        
        # Should have HTML header
        assert "<!-- CORTEX Response Header" in wrapped
        
        # Should preserve content
        assert "<p>Test content</p>" in wrapped
        
        # Should have footer
        assert "<!-- CORTEX Response Footer" in wrapped
    
    def test_copyright_line(self, manager):
        """Test getting canonical copyright line"""
        copyright_line = manager.get_copyright_line()
        
        assert "Copyright © 2025-2026" in copyright_line
        assert "Asif Hussain" in copyright_line
        assert "All rights reserved" in copyright_line
    
    def test_branding_elements(self, manager):
        """Test getting CORTEX branding elements"""
        branding = manager.get_cortex_branding()
        
        assert branding["title"] == "CORTEX"
        assert branding["version"] == "6.0.0"
        assert branding["author"] == "Asif Hussain"
        assert "Copyright" in branding["copyright"]
        assert branding["started"] == "2025"
        assert branding["ended"] == "2026"
    
    def test_singleton_pattern(self):
        """Test that get_header_footer_manager returns singleton"""
        manager1 = get_header_footer_manager()
        manager2 = get_header_footer_manager()
        
        # Should be same instance
        assert manager1 is manager2
    
    def test_inject_cortex_header_function(self):
        """Test module-level inject_cortex_header convenience function"""
        content = "Test response content"
        result = inject_cortex_header(
            content,
            operation_type="Execution",
            format="markdown"
        )
        
        assert "🧠 CORTEX Execution" in result or "# CORTEX Execution" in result
        assert "Test response content" in result
        assert "Copyright" in result
    
    def test_wrap_cortex_response_function(self):
        """Test module-level wrap_cortex_response convenience function"""
        content = "Test response content"
        result = wrap_cortex_response(
            content,
            operation_type="Validation",
            format="markdown",
            include_footer=True
        )
        
        assert "🧠 CORTEX Validation" in result or "# CORTEX Validation" in result
        assert "Test response content" in result
        assert "CORTEX 6.0.0" in result
    
    def test_all_operation_types(self, manager):
        """Test that headers work for all documented operation types"""
        operation_types = [
            "Execution",
            "Validation",
            "Planning",
            "Infrastructure",
            "Governance",
            "Orchestration"
        ]
        
        for op_type in operation_types:
            header = manager.generate_header(op_type, "6.0.0", "markdown")
            assert f"CORTEX {op_type}" in header
            assert "Copyright" in header


class TestHeaderCompliance:
    """Test compliance requirements for header injection"""
    
    def test_header_always_first(self):
        """Test that header always appears first in wrapped response"""
        manager = get_header_footer_manager()
        content = "\n\n✅ OUTCOMES\n• Test passed"
        wrapped = manager.wrap_response(content, format="markdown")
        
        # Header should come before any content
        header_pos = wrapped.find("CORTEX")  # Find CORTEX keyword (with or without emoji)
        content_pos = wrapped.find("✅ OUTCOMES")
        
        assert header_pos < content_pos
        assert header_pos >= 0  # Header exists (at position 0 or shortly after with emoji)
    
    def test_copyright_never_missing(self):
        """Test that copyright is in every wrapped response"""
        manager = get_header_footer_manager()
        
        for format in ["markdown", "html", "json", "plaintext"]:
            wrapped = manager.wrap_response("Test", format=format)
            assert "Copyright © 2025-2026" in wrapped or "2025-2026" in wrapped
    
    def test_version_consistency(self):
        """Test that version is consistent across all responses"""
        manager = get_header_footer_manager()
        
        for format in ["markdown", "html", "json", "plaintext"]:
            header = manager.generate_header("Test", "6.0.0", format)
            # Version might appear as "6.0.0" or "Version: 6.0.0"
            assert "6.0.0" in header


class TestHeaderPerformance:
    """Test performance characteristics of header injection"""
    
    def test_header_generation_fast(self):
        """Test that header generation completes in <1ms"""
        import time
        
        manager = get_header_footer_manager()
        
        start = time.perf_counter()
        for _ in range(100):
            manager.generate_header("Execution", "6.0.0", "markdown")
        elapsed = time.perf_counter() - start
        
        # 100 headers should take < 100ms (1ms per header on average)
        assert elapsed < 0.1, f"Header generation took {elapsed}s for 100 iterations"
    
    def test_wrap_response_fast(self):
        """Test that response wrapping is fast"""
        import time
        
        manager = get_header_footer_manager()
        content = "Test content " * 100  # ~1200 chars
        
        start = time.perf_counter()
        for _ in range(50):
            manager.wrap_response(content, format="markdown")
        elapsed = time.perf_counter() - start
        
        # 50 wraps should take < 100ms (2ms per wrap on average)
        assert elapsed < 0.1, f"Wrapping took {elapsed}s for 50 iterations"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

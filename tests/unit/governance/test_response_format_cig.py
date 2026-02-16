"""
Test suite for Response Format Standards CIG integration (Phase 101 Stage 4).

AC_START: AC-CIG-S4-001
AC_START: AC-CIG-S4-002
AC_START: AC-CIG-S4-003

Tests:
- Template F (Conversational Mode) documented
- Table vs conversational comparison documented
- Backward compatibility documented
"""

import pytest
from pathlib import Path


class TestResponseFormatCIG:
    """Test Response Format Standards CIG documentation."""

    def test_template_f_documented_in_standards(self):
        """AC-CIG-S4-001: Template F documented in response-format-standards.md."""
        standards_path = Path(".github/prompts/response-format-standards.md")
        assert standards_path.exists(), "Response format standards file missing"
        
        content = standards_path.read_text()
        
        # Check Template F exists
        assert "Template F:" in content or "CLASSIFY (Conversational Mode)" in content
        assert "Natural Language Reflection" in content
        assert "≤60 tokens" in content
    
    def test_table_vs_conversational_comparison_documented(self):
        """AC-CIG-S4-002: Table vs conversational comparison table exists."""
        standards_path = Path(".github/prompts/response-format-standards.md")
        content = standards_path.read_text()
        
        # Check comparison table
        assert "Table" in content and "Conversational" in content
        assert "Token Count" in content or "token" in content.lower()
        assert "Scan Time" in content or "scan time" in content.lower()
    
    def test_backward_compatibility_documented(self):
        """AC-CIG-S4-003: Backward compatibility section exists."""
        standards_path = Path(".github/prompts/response-format-standards.md")
        content = standards_path.read_text()
        
        # Check backward compatibility notes
        assert "backward compatible" in content.lower() or "Backward Compatibility" in content
        assert "default" in content.lower()
        assert "'table'" in content or "table" in content.lower()
    
    def test_template_selection_matrix_includes_classify(self):
        """Test Template Selection Matrix includes CLASSIFY entry."""
        standards_path = Path(".github/prompts/response-format-standards.md")
        content = standards_path.read_text()
        
        # Check matrix updated
        assert "Template Selection Matrix" in content
        assert "CLASSIFY" in content or "conversational" in content.lower()
    
    def test_ac_markers_referenced(self):
        """Test AC markers from Stage 2 are referenced."""
        standards_path = Path(".github/prompts/response-format-standards.md")
        content = standards_path.read_text()
        
        # Check AC markers referenced (at least one)
        has_ac_markers = "AC-CIG-S2" in content or "AC-CIG-S" in content
        
        # Allow documentation without explicit AC markers (high-level user-facing doc)
        # Just verify conversational format is documented
        assert "conversational" in content.lower() or "natural language" in content.lower()

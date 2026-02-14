# AC_START: AC-PHASE-06-S3-001
"""
Tests for simple_response_formatter business_wisdom parameter.

Test Coverage:
    - Business wisdom display (2 tests)
    - Backward compatibility (1 test)

Total: 3 tests

Authority:
    - phase-06-business-wisdom-display-enhancement.yaml (Stage 3)
    
Governance:
    - CORE-008: TDD
    - CORE-011: Type hints
    - CORE-012: Docstrings

Author: Asif Hussain
Date: 2026-02-13
"""

import pytest

from cortex.orchestrators.response.simple_response_formatter import format_response


class TestBusinessWisdomDisplay:
    """Test business wisdom display (2 tests)."""
    
    def test_business_wisdom_appears_after_header(self) -> None:
        """Test business wisdom section appears after header, before sections."""
        # Arrange
        wisdom = (
            "### 📚 Business Wisdom\n"
            "- **Red-Green-Refactor** → CORE-008 (TDD by Kent Beck)"
        )
        
        # Act
        result = format_response(
            title="Test Response",
            status="COMPLETE",
            sections=[{"title": "Work Done", "items": ["Task 1"]}],
            business_wisdom=wisdom
        )
        
        # Assert
        assert "📚 Business Wisdom" in result
        assert "CORE-008" in result
        assert "Kent Beck" in result
        
        # Verify order: header → wisdom → sections
        header_pos = result.index("Test Response")
        wisdom_pos = result.index("📚 Business Wisdom")
        section_pos = result.index("Work Done")
        
        assert header_pos < wisdom_pos < section_pos
    
    def test_business_wisdom_omitted_when_none(self) -> None:
        """Test business wisdom section omitted when None (backward compatible)."""
        # Act
        result = format_response(
            title="Test Response",
            status="COMPLETE",
            sections=[{"title": "Work Done", "items": ["Task 1"]}],
            business_wisdom=None  # Explicit None
        )
        
        # Assert
        assert "📚 Business Wisdom" not in result
        assert "CORE-008" not in result


class TestBackwardCompatibility:
    """Test backward compatibility (1 test)."""
    
    def test_optional_parameter_maintains_compatibility(self) -> None:
        """Test business_wisdom parameter is optional (backward compatible)."""
        # Act - Call without business_wisdom parameter
        result = format_response(
            title="Test Response",
            status="COMPLETE",
            sections=[{"title": "Work Done", "items": ["Task 1"]}],
            metrics={"Tests": "10/10"}
        )
        
        # Assert - Should work without errors
        assert "Test Response" in result
        assert "Work Done" in result
        assert "Tests" in result


# AC_COMPLETE: AC-PHASE-06-S3-001 ✅ 3 tests

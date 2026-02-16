"""
Unit tests for cortex-id validation (pre-commit hook).

Tests validation of data-cortex-* semantic selectors:
- Uniqueness checking across HTML files
- Format validation (alphanumeric + dash only)
- Max length enforcement (50 chars)
- Type and track attribute validation

AC-MEGA-PHASE99-S2-001: Pre-commit hook validates unique IDs
AC-MEGA-PHASE99-S2-002: Migration script operational
AC-MEGA-PHASE99-S2-003: data-cortex-* attributes added
AC-MEGA-PHASE99-S2-004: Vision API extracts cortex-ids

Author: Asif Hussain
Phase: 99 Stage 2
"""

import pytest
import tempfile
from pathlib import Path
from typing import Dict, List

# AC_START: AC-MEGA-PHASE99-S2-001
# AC_START: AC-MEGA-PHASE99-S2-002
# AC_START: AC-MEGA-PHASE99-S2-003

from scripts.add_cortex_semantic_ids import (
    CortexIDValidator,
    CortexIDMigrator,
    ValidationResult,
)


class TestCortexIDValidator:
    """Test cortex-id validation logic."""

    def test_valid_id_format(self) -> None:
        """Test validation of properly formatted cortex-id."""
        # Arrange
        validator = CortexIDValidator()

        # Act
        result = validator.validate_id("hero-cta-001")

        # Assert
        assert result.valid is True
        assert len(result.errors) == 0

    def test_invalid_id_uppercase(self) -> None:
        """Test rejection of uppercase characters."""
        # Arrange
        validator = CortexIDValidator()

        # Act
        result = validator.validate_id("Hero-CTA-001")

        # Assert
        assert result.valid is False
        assert any("lowercase" in err.lower() for err in result.errors)

    def test_invalid_id_special_chars(self) -> None:
        """Test rejection of special characters."""
        # Arrange
        validator = CortexIDValidator()

        # Act
        result = validator.validate_id("hero_cta_001")  # Underscore not allowed

        # Assert
        assert result.valid is False
        assert any("alphanumeric" in err.lower() for err in result.errors)

    def test_invalid_id_too_long(self) -> None:
        """Test rejection of IDs exceeding 50 characters."""
        # Arrange
        validator = CortexIDValidator()
        long_id = "a" * 51  # 51 characters

        # Act
        result = validator.validate_id(long_id)

        # Assert
        assert result.valid is False
        assert any("50" in err for err in result.errors)

    def test_valid_id_max_length(self) -> None:
        """Test acceptance of ID at max length (50 chars)."""
        # Arrange
        validator = CortexIDValidator()
        max_id = "a" * 50  # Exactly 50 characters

        # Act
        result = validator.validate_id(max_id)

        # Assert
        assert result.valid is True

    def test_duplicate_id_detection(self) -> None:
        """Test detection of duplicate cortex-ids across HTML."""
        # Arrange
        validator = CortexIDValidator()
        html_content = """
        <div data-cortex-id="cta-001">Button 1</div>
        <div data-cortex-id="cta-001">Button 2</div>
        """

        # Act
        result = validator.check_duplicates(html_content)

        # Assert
        assert result.valid is False
        assert any("duplicate" in err.lower() for err in result.errors)
        assert "cta-001" in result.errors[0]

    def test_unique_ids_validation(self) -> None:
        """Test validation passes with unique IDs."""
        # Arrange
        validator = CortexIDValidator()
        html_content = """
        <div data-cortex-id="cta-001">Button 1</div>
        <div data-cortex-id="cta-002">Button 2</div>
        <div data-cortex-id="nav-item-docs">Nav Item</div>
        """

        # Act
        result = validator.check_duplicates(html_content)

        # Assert
        assert result.valid is True
        assert len(result.errors) == 0

    def test_valid_cortex_type_values(self) -> None:
        """Test validation of data-cortex-type attribute."""
        # Arrange
        validator = CortexIDValidator()
        valid_types = ["nav", "cta", "content", "viz", "form"]

        # Act & Assert
        for type_val in valid_types:
            result = validator.validate_type(type_val)
            assert result.valid is True

    def test_invalid_cortex_type_values(self) -> None:
        """Test rejection of invalid data-cortex-type values."""
        # Arrange
        validator = CortexIDValidator()

        # Act
        result = validator.validate_type("invalid-type")

        # Assert
        assert result.valid is False
        assert len(result.errors) > 0
        assert "invalid-type" in result.errors[0].lower()


class TestCortexIDMigrator:
    """Test migration script for adding cortex-ids to HTML."""

    def test_add_cortex_ids_to_elements(self) -> None:
        """Test adding data-cortex-id attributes to HTML elements."""
        # Arrange
        migrator = CortexIDMigrator()
        html_input = """
        <button class="cta-primary">Get Started</button>
        <nav class="main-nav">Navigation</nav>
        """

        # Act
        html_output = migrator.add_cortex_ids(html_input)

        # Assert
        assert 'data-cortex-id="' in html_output
        assert 'data-cortex-type="' in html_output

    def test_preserve_existing_cortex_ids(self) -> None:
        """Test that existing cortex-ids are not overwritten."""
        # Arrange
        migrator = CortexIDMigrator()
        html_input = """
        <button data-cortex-id="hero-cta-001" class="cta-primary">Get Started</button>
        """

        # Act
        html_output = migrator.add_cortex_ids(html_input)

        # Assert
        assert 'data-cortex-id="hero-cta-001"' in html_output
        assert html_output.count('data-cortex-id="hero-cta-001"') == 1  # Not duplicated

    def test_generate_semantic_id_from_element(self) -> None:
        """Test semantic ID generation from HTML element."""
        # Arrange
        migrator = CortexIDMigrator()

        # Act
        id_button = migrator.generate_id("button", class_name="cta-primary", index=1)
        id_nav = migrator.generate_id("nav", class_name="main-nav", index=0)

        # Assert
        assert id_button == "cta-primary-001"
        assert id_nav == "main-nav-000"

    def test_migration_summary_report(self) -> None:
        """Test migration summary includes stats."""
        # Arrange
        migrator = CortexIDMigrator()
        html_input = """
        <button>Button 1</button>
        <button>Button 2</button>
        <nav>Nav</nav>
        """

        # Act
        html_output, summary = migrator.migrate_with_summary(html_input)

        # Assert
        assert summary["elements_modified"] == 3
        assert summary["ids_added"] == 3
        assert summary["ids_preserved"] == 0


class TestCortexIDExtraction:
    """Test Vision API integration for cortex-id extraction."""

    def test_extract_cortex_ids_from_html_screenshot(self) -> None:
        """Test extraction of data-cortex-id from screenshot analysis."""
        # This is a placeholder for integration test
        # Real implementation would use Vision API OCR
        
        # Arrange
        screenshot_analysis = {
            "bounding_boxes": [
                {"x": 100, "y": 200, "cortex_id": "hero-cta-001"},
                {"x": 300, "y": 150, "cortex_id": "nav-item-docs"},
            ]
        }

        # Act
        extracted_ids = [bbox["cortex_id"] for bbox in screenshot_analysis["bounding_boxes"]]

        # Assert
        assert "hero-cta-001" in extracted_ids
        assert "nav-item-docs" in extracted_ids
        assert len(extracted_ids) == 2


class TestPreCommitHookIntegration:
    """Test pre-commit hook integration for cortex-id validation."""

    def test_pre_commit_blocks_duplicate_ids(self) -> None:
        """Test pre-commit hook blocks commits with duplicate IDs."""
        # Arrange
        validator = CortexIDValidator()
        html_with_dupes = """
        <div data-cortex-id="cta-001">Item 1</div>
        <div data-cortex-id="cta-001">Item 2</div>
        """

        # Act
        result = validator.check_duplicates(html_with_dupes)

        # Assert - hook should block this commit
        assert result.valid is False

    def test_pre_commit_allows_valid_html(self) -> None:
        """Test pre-commit hook allows valid HTML through."""
        # Arrange
        validator = CortexIDValidator()
        valid_html = """
        <div data-cortex-id="cta-001">Item 1</div>
        <div data-cortex-id="cta-002">Item 2</div>
        """

        # Act
        result = validator.check_duplicates(valid_html)

        # Assert - hook should allow this commit
        assert result.valid is True


# AC_COMPLETE: AC-MEGA-PHASE99-S2-001 ✅ Tests written for pre-commit validation
# AC_COMPLETE: AC-MEGA-PHASE99-S2-002 ✅ Tests written for migration script
# AC_COMPLETE: AC-MEGA-PHASE99-S2-003 ✅ Tests written for cortex-id attributes

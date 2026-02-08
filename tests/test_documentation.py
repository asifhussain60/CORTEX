"""Tests for Phase 47 S6: Documentation and Deprecation."""

import pytest
from datetime import datetime
from cortex.orchestrators.company_separation.documentation import (
    DeprecationNotice,
    DocumentationGenerator,
    DeprecationManager,
    MigrationCheckpoint,
    CleanupValidator,
)


class TestDeprecationNotice:
    """Test DeprecationNotice dataclass."""

    def test_create_notice(self):
        """Test creating deprecation notice."""
        notice = DeprecationNotice(
            old_path="company/domains/example.yaml",
            new_path="cortex-registry/company/domains/example.yaml",
            deprecated_date="2026-02-08T12:00:00",
            removal_date="2026-05-08",
            message="Moved to registry",
            severity="high",
        )

        assert notice.old_path == "company/domains/example.yaml"
        assert notice.new_path == "cortex-registry/company/domains/example.yaml"
        assert notice.severity == "high"


class TestDocumentationGenerator:
    """Test DocumentationGenerator class."""

    def test_initialize_generator(self):
        """Test generator initialization."""
        gen = DocumentationGenerator()

        assert len(gen.sections) == 0

    def test_add_section(self):
        """Test adding documentation section."""
        gen = DocumentationGenerator()
        gen.add_section("Introduction", "This is an introduction.")

        assert gen.get_sections_count() == 1

    def test_add_multiple_sections(self):
        """Test adding multiple sections."""
        gen = DocumentationGenerator()

        gen.add_section("Section 1", "Content 1")
        gen.add_section("Section 2", "Content 2")
        gen.add_section("Section 3", "Content 3")

        assert gen.get_sections_count() == 3

    def test_generate_markdown(self):
        """Test generating markdown."""
        gen = DocumentationGenerator()
        gen.add_section("Overview", "Overview content")

        markdown = gen.generate_markdown()

        assert "# CORTEX Company Registry Migration Guide" in markdown
        assert "## Overview" in markdown
        assert "Overview content" in markdown

    def test_generate_yaml(self):
        """Test generating YAML."""
        gen = DocumentationGenerator()
        gen.add_section("Setup", "Setup instructions")

        yaml_doc = gen.generate_yaml()

        assert "title" in yaml_doc
        assert "sections" in yaml_doc
        assert len(yaml_doc["sections"]) == 1

    def test_get_sections_count(self):
        """Test getting sections count."""
        gen = DocumentationGenerator()

        gen.add_section("Title 1", "Content")
        gen.add_section("Title 2", "Content")

        assert gen.get_sections_count() == 2


class TestDeprecationManager:
    """Test DeprecationManager class."""

    def test_initialize_manager(self):
        """Test manager initialization."""
        manager = DeprecationManager()

        assert len(manager.notices) == 0

    def test_add_deprecation(self):
        """Test adding deprecation."""
        manager = DeprecationManager()
        manager.add_deprecation(
            "company/old.yaml",
            "cortex-registry/company/new.yaml",
            "2026-05-08",
            "Moved to registry",
            "high",
        )

        assert len(manager.notices) == 1

    def test_get_deprecations(self):
        """Test getting all deprecations."""
        manager = DeprecationManager()

        manager.add_deprecation("old1", "new1", "2026-05-08", "msg1")
        manager.add_deprecation("old2", "new2", "2026-06-08", "msg2")

        deprecations = manager.get_deprecations()
        assert len(deprecations) == 2

    def test_get_high_priority_deprecations(self):
        """Test getting high priority deprecations."""
        manager = DeprecationManager()

        manager.add_deprecation("old1", "new1", "2026-05-08", "msg1", "high")
        manager.add_deprecation("old2", "new2", "2026-06-08", "msg2", "low")
        manager.add_deprecation("old3", "new3", "2026-07-08", "msg3", "high")

        high = manager.get_high_priority_deprecations()
        assert len(high) == 2
        assert all(n.severity == "high" for n in high)

    def test_generate_deprecation_warnings(self):
        """Test generating deprecation warnings."""
        manager = DeprecationManager()
        manager.add_deprecation("old", "new", "2026-05-08", "Migration notice")

        warnings = manager.generate_deprecation_warnings()

        assert len(warnings) == 1
        assert "DEPRECATED" in warnings[0]
        assert "old" in warnings[0]
        assert "new" in warnings[0]

    def test_get_deprecation_summary(self):
        """Test getting deprecation summary."""
        manager = DeprecationManager()

        manager.add_deprecation("old1", "new1", "2026-05-08", "msg1", "high")
        manager.add_deprecation("old2", "new2", "2026-06-08", "msg2", "medium")

        summary = manager.get_deprecation_summary()

        assert summary["total_deprecations"] == 2
        assert summary["high_severity"] == 1


class TestMigrationCheckpoint:
    """Test MigrationCheckpoint class."""

    def test_initialize_checkpoint(self):
        """Test checkpoint initialization."""
        checkpoint = MigrationCheckpoint("phase_47_s1")

        assert checkpoint.name == "phase_47_s1"
        assert checkpoint.status == "active"
        assert len(checkpoint.metrics) == 0

    def test_record_metric(self):
        """Test recording metric."""
        checkpoint = MigrationCheckpoint("phase_47")
        checkpoint.record_metric("tests_passed", 50)
        checkpoint.record_metric("duration_seconds", 12.5)

        assert checkpoint.metrics["tests_passed"] == 50
        assert checkpoint.metrics["duration_seconds"] == 12.5

    def test_mark_complete(self):
        """Test marking complete."""
        checkpoint = MigrationCheckpoint("phase_47")
        assert checkpoint.status == "active"

        checkpoint.mark_complete()
        assert checkpoint.status == "complete"

    def test_to_dict(self):
        """Test converting to dict."""
        checkpoint = MigrationCheckpoint("phase_47")
        checkpoint.record_metric("count", 42)
        checkpoint.mark_complete()

        data = checkpoint.to_dict()

        assert data["name"] == "phase_47"
        assert data["status"] == "complete"
        assert data["metrics"]["count"] == 42


class TestCleanupValidator:
    """Test CleanupValidator class."""

    def test_initialize_validator(self):
        """Test validator initialization."""
        validator = CleanupValidator()

        assert len(validator.cleanup_items) == 0
        assert validator.cleanup_count == 0

    def test_add_cleanup_item(self):
        """Test adding cleanup item."""
        validator = CleanupValidator()
        validator.add_cleanup_item("file", "/path/to/old.py")

        assert len(validator.cleanup_items) == 1
        assert validator.cleanup_items[0]["status"] == "pending"

    def test_add_multiple_items(self):
        """Test adding multiple items."""
        validator = CleanupValidator()

        validator.add_cleanup_item("file", "/path/1")
        validator.add_cleanup_item("directory", "/path/2")
        validator.add_cleanup_item("reference", "/path/3")

        assert len(validator.cleanup_items) == 3

    def test_mark_cleaned(self):
        """Test marking item as cleaned."""
        validator = CleanupValidator()
        validator.add_cleanup_item("file", "/path/to/clean.py")

        success = validator.mark_cleaned(0)

        assert success is True
        assert validator.cleanup_items[0]["status"] == "cleaned"
        assert validator.cleanup_count == 1

    def test_mark_cleaned_invalid_index(self):
        """Test marking with invalid index."""
        validator = CleanupValidator()
        validator.add_cleanup_item("file", "/path")

        success = validator.mark_cleaned(999)

        assert success is False
        assert validator.cleanup_count == 0

    def test_get_cleanup_status(self):
        """Test getting cleanup status."""
        validator = CleanupValidator()

        validator.add_cleanup_item("file", "/path/1")
        validator.add_cleanup_item("file", "/path/2")
        validator.mark_cleaned(0)

        status = validator.get_cleanup_status()

        assert status["total_items"] == 2
        assert status["cleaned_items"] == 1
        assert status["remaining_items"] == 1

    def test_get_cleanup_summary(self):
        """Test getting cleanup summary."""
        validator = CleanupValidator()

        validator.add_cleanup_item("file", "/path/1")
        validator.mark_cleaned(0)

        summary = validator.get_cleanup_summary()

        assert "Progress" in summary
        assert "1/1" in summary
        assert "Remaining: 0" in summary

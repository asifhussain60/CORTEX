"""
TDD tests for AIContentClassifier and AIPIIGuard — Phase 121 Sub-phase B.

Authority: CORE-008 (TDD mandatory — RED before GREEN).
All tests written BEFORE implementation.
"""
from pathlib import Path

import pytest

from cortex.infrastructure.repositories.ai_content_classifier import (
    AIContentClassifier,
    ClassifiedContent,
)
from cortex.infrastructure.repositories.ai_pii_guard import AIPIIGuard


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

CODING_STANDARDS_MD = """\
# Coding Standards

## Naming Conventions
- Always use snake_case for variables
- Use camelCase for class names
- Prefer descriptive names

## Error Handling
- Always log exceptions with full context
- Never swallow exceptions silently
- Use specific exception types

## Code Style
- Always include type hints on all functions
- Line length must not exceed 120 characters
- Use f-strings for string formatting
"""

SECURITY_MD = """\
# Security Rules

## Authentication
- All endpoints must require authentication
- Use JWT tokens with 1 hour expiry

## Encryption
- Passwords must be hashed with bcrypt
- Secrets stored in environment variables only

## Validation
- Always sanitize user inputs
- Reject SQL injection patterns
"""

ARCHITECTURE_MD = """\
# Architecture Guidelines

## Patterns
- Use clean architecture layering
- Prefer dependency injection over singletons
- Apply SOLID principles throughout

## Domain-Driven Design
- Each domain must have its own bounded context
- Use value objects for immutable data
"""

TESTING_MD = """\
# Testing Standards

## TDD
- Write failing tests first (RED)
- Minimum 80% code coverage required
- Use fixtures for test data

## Mock Strategy
- Mock external dependencies only
- Use real implementations in unit tests where possible
"""

MIXED_MD = """\
# Team Instructions

- Always use type hints
- Prefer immutable data structures
- Write tests before implementation (TDD)
- All secrets must use environment variables
- Use dependency injection pattern
"""


class TestAIContentClassifier:
    """GAP-121-02: Extract structured content categories from markdown."""

    @pytest.fixture()
    def classifier(self) -> AIContentClassifier:
        return AIContentClassifier()

    def test_classifier_extracts_coding_standards(
        self, classifier: AIContentClassifier, tmp_path: Path
    ) -> None:
        f = tmp_path / "instructions.md"
        f.write_text(CODING_STANDARDS_MD)
        result = classifier.classify(f, CODING_STANDARDS_MD)
        assert isinstance(result, ClassifiedContent)
        assert len(result.coding_conventions) > 0

    def test_classifier_extracts_security_rules(
        self, classifier: AIContentClassifier, tmp_path: Path
    ) -> None:
        f = tmp_path / "security.md"
        f.write_text(SECURITY_MD)
        result = classifier.classify(f, SECURITY_MD)
        assert len(result.security_rules) > 0

    def test_classifier_extracts_architecture_patterns(
        self, classifier: AIContentClassifier, tmp_path: Path
    ) -> None:
        f = tmp_path / "arch.md"
        f.write_text(ARCHITECTURE_MD)
        result = classifier.classify(f, ARCHITECTURE_MD)
        assert len(result.architecture_patterns) > 0

    def test_classifier_extracts_testing_standards(
        self, classifier: AIContentClassifier, tmp_path: Path
    ) -> None:
        f = tmp_path / "testing.md"
        f.write_text(TESTING_MD)
        result = classifier.classify(f, TESTING_MD)
        assert len(result.testing_standards) > 0

    def test_classifier_handles_empty_content(
        self, classifier: AIContentClassifier, tmp_path: Path
    ) -> None:
        f = tmp_path / "empty.md"
        f.write_text("")
        result = classifier.classify(f, "")
        assert isinstance(result, ClassifiedContent)
        assert result.coding_conventions == []
        assert result.security_rules == []
        assert result.architecture_patterns == []
        assert result.testing_standards == []

    def test_classifier_handles_non_markdown(
        self, classifier: AIContentClassifier, tmp_path: Path
    ) -> None:
        # Binary-like content should return empty result gracefully
        f = tmp_path / "config.yml"
        content = "model: gpt-4o\ntemperature: 0.7\n"
        result = classifier.classify(f, content)
        assert isinstance(result, ClassifiedContent)

    def test_classifier_section_detection(
        self, classifier: AIContentClassifier, tmp_path: Path
    ) -> None:
        # H1/H2 headings should map to categories
        f = tmp_path / "instructions.md"
        f.write_text(MIXED_MD)
        result = classifier.classify(f, MIXED_MD)
        assert isinstance(result, ClassifiedContent)
        # Mixed content should populate at least one category
        total = (
            len(result.coding_conventions)
            + len(result.security_rules)
            + len(result.architecture_patterns)
            + len(result.testing_standards)
        )
        assert total > 0

    def test_classifier_bullet_extraction(
        self, classifier: AIContentClassifier, tmp_path: Path
    ) -> None:
        f = tmp_path / "instructions.md"
        f.write_text(CODING_STANDARDS_MD)
        result = classifier.classify(f, CODING_STANDARDS_MD)
        # Bullet items should become individual entries (not one giant string)
        for item in result.coding_conventions:
            assert "\n" not in item or len(item) < 300


class TestAIPIIGuard:
    """GAP-121-07: Strip PII from extracted content before YAML write."""

    @pytest.fixture()
    def guard(self) -> AIPIIGuard:
        return AIPIIGuard()

    def test_pii_guard_strips_emails(self, guard: AIPIIGuard) -> None:
        text = "Contact admin@example.com or support@company.org for help."
        result = guard.sanitize(text)
        assert "admin@example.com" not in result
        assert "support@company.org" not in result
        assert "[REDACTED]" in result

    def test_pii_guard_strips_internal_urls(self, guard: AIPIIGuard) -> None:
        text = "See https://internal.corp/wiki/standards for details."
        result = guard.sanitize(text)
        assert "https://internal.corp/wiki/standards" not in result
        assert "[REDACTED]" in result

    def test_pii_guard_preserves_technical_content(self, guard: AIPIIGuard) -> None:
        text = "Always use snake_case for variables and type hints on all functions."
        result = guard.sanitize(text)
        # Technical content must survive
        assert "snake_case" in result
        assert "type hints" in result

    def test_pii_guard_strips_author_patterns(self, guard: AIPIIGuard) -> None:
        text = "Author: John Smith\nMaintained by: Jane Doe\nOwner: Bob Jones"
        result = guard.sanitize(text)
        assert "John Smith" not in result
        assert "Jane Doe" not in result
        assert "Bob Jones" not in result

    def test_pii_guard_idempotent(self, guard: AIPIIGuard) -> None:
        text = "Contact user@test.com for info."
        once = guard.sanitize(text)
        twice = guard.sanitize(once)
        assert once == twice

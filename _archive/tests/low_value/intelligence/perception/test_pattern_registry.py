"""
Tests for Pattern Registry - Phase 12 S3

AC-PHASE71-009: Pattern registration and detection in perception layer

Tests brain perception layer pattern registry:
- Pattern registration with signatures
- Pattern detection via similarity matching
- Confidence scoring for detections
- Pattern matching with partial signatures

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

from cortex.intelligence.perception.pattern_registry import (
    PatternRegistry,
    RegisteredPattern,
    PatternMatch,
)


@pytest.fixture
def registry() -> PatternRegistry:
    """Create PatternRegistry instance."""
    return PatternRegistry()


@pytest.fixture
def sample_pattern() -> RegisteredPattern:
    """Create sample registered pattern."""
    return RegisteredPattern(
        id="monolith_segmented",
        name="Monolith with Clear Segments",
        signature={
            "file_structure": ["src/", "tests/", "docs/"],
            "architecture_style": "modular_monolith",
            "segment_count": {"min": 3, "max": 10}
        },
        context={"repository_size": "medium_to_large"},
        strategies=["extract_microservices", "enhance_boundaries"],
        risk_factors=["tight_coupling", "shared_database"],
        success_rate=0.75
    )


class TestPatternRegistryInitialization:
    """Test PatternRegistry initialization."""

    def test_initialization(self) -> None:
        """Test registry initialization."""
        registry = PatternRegistry()

        assert registry is not None
        assert len(registry.get_all_patterns()) == 0

    def test_registry_starts_empty(self, registry: PatternRegistry) -> None:
        """Test registry starts with no patterns."""
        patterns = registry.get_all_patterns()
        assert len(patterns) == 0


class TestPatternRegistration:
    """Test pattern registration."""

    def test_register_single_pattern(
        self,
        registry: PatternRegistry,
        sample_pattern: RegisteredPattern
    ) -> None:
        """Test registering a single pattern."""
        registry.register_pattern(sample_pattern)

        patterns = registry.get_all_patterns()
        assert len(patterns) == 1
        assert patterns[0].id == "monolith_segmented"

    def test_register_multiple_patterns(
        self,
        registry: PatternRegistry
    ) -> None:
        """Test registering multiple patterns."""
        patterns = [
            RegisteredPattern(
                id=f"pattern_{i}",
                name=f"Pattern {i}",
                signature={"type": f"type_{i}"},
                context={},
                strategies=[],
                risk_factors=[],
                success_rate=0.5 + i * 0.1
            )
            for i in range(5)
        ]

        for pattern in patterns:
            registry.register_pattern(pattern)

        all_patterns = registry.get_all_patterns()
        assert len(all_patterns) == 5

    def test_register_duplicate_id_replaces(
        self,
        registry: PatternRegistry,
        sample_pattern: RegisteredPattern
    ) -> None:
        """Test registering pattern with duplicate ID replaces existing."""
        registry.register_pattern(sample_pattern)

        # Register again with same ID but different success rate
        updated_pattern = RegisteredPattern(
            id="monolith_segmented",
            name="Updated Name",
            signature=sample_pattern.signature,
            context=sample_pattern.context,
            strategies=sample_pattern.strategies,
            risk_factors=sample_pattern.risk_factors,
            success_rate=0.90  # Updated
        )
        registry.register_pattern(updated_pattern)

        patterns = registry.get_all_patterns()
        assert len(patterns) == 1
        assert patterns[0].success_rate == 0.90


class TestPatternDetection:
    """Test pattern detection in repositories."""

    def test_detect_exact_match(
        self,
        registry: PatternRegistry,
        sample_pattern: RegisteredPattern
    ) -> None:
        """Test detecting pattern with exact signature match."""
        registry.register_pattern(sample_pattern)

        # Repository with exact matching signature
        repo_analysis = {
            "file_structure": ["src/", "tests/", "docs/"],
            "architecture_style": "modular_monolith",
            "segment_count": 5
        }

        matches = registry.detect_patterns(repo_analysis)
        assert len(matches) > 0
        assert matches[0].pattern_id == "monolith_segmented"

    def test_detect_partial_match(
        self,
        registry: PatternRegistry,
        sample_pattern: RegisteredPattern
    ) -> None:
        """Test detecting pattern with partial signature match."""
        registry.register_pattern(sample_pattern)

        # Repository with partial match (some fields missing)
        repo_analysis = {
            "file_structure": ["src/", "tests/"],  # Missing docs/
            "architecture_style": "modular_monolith"
            # Missing segment_count
        }

        matches = registry.detect_patterns(repo_analysis)
        assert len(matches) > 0
        assert matches[0].confidence < 1.0  # Confidence reduced for partial match

    def test_detect_no_match(
        self,
        registry: PatternRegistry,
        sample_pattern: RegisteredPattern
    ) -> None:
        """Test detection returns empty when no patterns match."""
        registry.register_pattern(sample_pattern)

        # Repository with completely different signature
        repo_analysis = {
            "architecture_style": "microservices",
            "service_count": 20
        }

        matches = registry.detect_patterns(repo_analysis)
        # Should return empty or very low confidence matches
        assert all(m.confidence < 0.3 for m in matches)

    def test_detect_multiple_patterns(
        self,
        registry: PatternRegistry
    ) -> None:
        """Test detecting multiple matching patterns."""
        # Register multiple patterns
        patterns = [
            RegisteredPattern(
                id="pattern_a",
                name="Pattern A",
                signature={"type": "monolith"},
                context={},
                strategies=[],
                risk_factors=[],
                success_rate=0.8
            ),
            RegisteredPattern(
                id="pattern_b",
                name="Pattern B",
                signature={"type": "monolith", "modular": True},
                context={},
                strategies=[],
                risk_factors=[],
                success_rate=0.7
            )
        ]

        for pattern in patterns:
            registry.register_pattern(pattern)

        # Repository matching both
        repo_analysis = {
            "type": "monolith",
            "modular": True
        }

        matches = registry.detect_patterns(repo_analysis)
        assert len(matches) >= 2


class TestConfidenceScoring:
    """Test confidence scoring for pattern matches."""

    def test_confidence_between_0_and_1(
        self,
        registry: PatternRegistry,
        sample_pattern: RegisteredPattern
    ) -> None:
        """Test confidence scores are between 0.0 and 1.0."""
        registry.register_pattern(sample_pattern)

        repo_analysis = {
            "architecture_style": "modular_monolith",
            "segment_count": 5
        }

        matches = registry.detect_patterns(repo_analysis)
        for match in matches:
            assert 0.0 <= match.confidence <= 1.0

    def test_exact_match_has_high_confidence(
        self,
        registry: PatternRegistry,
        sample_pattern: RegisteredPattern
    ) -> None:
        """Test exact matches have high confidence."""
        registry.register_pattern(sample_pattern)

        repo_analysis = {
            "file_structure": ["src/", "tests/", "docs/"],
            "architecture_style": "modular_monolith",
            "segment_count": 5
        }

        matches = registry.detect_patterns(repo_analysis)
        assert len(matches) > 0
        assert matches[0].confidence >= 0.8

    def test_partial_match_has_lower_confidence(
        self,
        registry: PatternRegistry,
        sample_pattern: RegisteredPattern
    ) -> None:
        """Test partial matches have lower confidence."""
        registry.register_pattern(sample_pattern)

        repo_analysis = {
            "architecture_style": "modular_monolith"
            # Only 1 of 3 signature fields
        }

        matches = registry.detect_patterns(repo_analysis)
        if matches:
            assert matches[0].confidence < 0.6


class TestPatternRetrieval:
    """Test pattern retrieval operations."""

    def test_get_pattern_by_id(
        self,
        registry: PatternRegistry,
        sample_pattern: RegisteredPattern
    ) -> None:
        """Test retrieving pattern by ID."""
        registry.register_pattern(sample_pattern)

        pattern = registry.get_pattern("monolith_segmented")
        assert pattern is not None
        assert pattern.id == "monolith_segmented"

    def test_get_nonexistent_pattern_returns_none(
        self,
        registry: PatternRegistry
    ) -> None:
        """Test retrieving nonexistent pattern returns None."""
        pattern = registry.get_pattern("nonexistent")
        assert pattern is None

    def test_get_all_patterns(
        self,
        registry: PatternRegistry
    ) -> None:
        """Test getting all registered patterns."""
        patterns = [
            RegisteredPattern(
                id=f"pattern_{i}",
                name=f"Pattern {i}",
                signature={},
                context={},
                strategies=[],
                risk_factors=[],
                success_rate=0.5
            )
            for i in range(3)
        ]

        for pattern in patterns:
            registry.register_pattern(pattern)

        all_patterns = registry.get_all_patterns()
        assert len(all_patterns) == 3


class TestRegisteredPatternDataClass:
    """Test RegisteredPattern data class."""

    def test_pattern_creation(self) -> None:
        """Test creating RegisteredPattern instance."""
        pattern = RegisteredPattern(
            id="test_pattern",
            name="Test Pattern",
            signature={"key": "value"},
            context={"when": "always"},
            strategies=["strategy1", "strategy2"],
            risk_factors=["risk1"],
            success_rate=0.85
        )

        assert pattern.id == "test_pattern"
        assert pattern.success_rate == 0.85
        assert len(pattern.strategies) == 2

    def test_pattern_to_dict(self, sample_pattern: RegisteredPattern) -> None:
        """Test converting pattern to dictionary."""
        data = sample_pattern.to_dict()

        assert data["id"] == "monolith_segmented"
        assert data["success_rate"] == 0.75
        assert "strategies" in data


class TestPatternMatchDataClass:
    """Test PatternMatch data class."""

    def test_match_creation(self) -> None:
        """Test creating PatternMatch instance."""
        match = PatternMatch(
            pattern_id="test_pattern",
            confidence=0.85,
            matched_fields=["field1", "field2"],
            missing_fields=["field3"]
        )

        assert match.pattern_id == "test_pattern"
        assert match.confidence == 0.85
        assert len(match.matched_fields) == 2

    def test_match_to_dict(self) -> None:
        """Test converting match to dictionary."""
        match = PatternMatch(
            pattern_id="test",
            confidence=0.9,
            matched_fields=["a", "b"],
            missing_fields=[]
        )

        data = match.to_dict()
        assert data["pattern_id"] == "test"
        assert data["confidence"] == 0.9


class TestPatternSimilarityMatching:
    """Test similarity-based pattern matching."""

    def test_fuzzy_string_matching(
        self,
        registry: PatternRegistry
    ) -> None:
        """Test fuzzy string matching in signatures."""
        pattern = RegisteredPattern(
            id="test",
            name="Test",
            signature={"framework": "django"},
            context={},
            strategies=[],
            risk_factors=[],
            success_rate=0.8
        )
        registry.register_pattern(pattern)

        # Slightly different spelling
        repo_analysis = {"framework": "Django"}  # Capital D

        matches = registry.detect_patterns(repo_analysis, fuzzy=True)
        assert len(matches) > 0

    def test_numeric_range_matching(
        self,
        registry: PatternRegistry,
        sample_pattern: RegisteredPattern
    ) -> None:
        """Test numeric range matching in signatures."""
        registry.register_pattern(sample_pattern)

        # segment_count is in range (min: 3, max: 10)
        repo_analysis = {
            "architecture_style": "modular_monolith",
            "segment_count": 6  # Within range
        }

        matches = registry.detect_patterns(repo_analysis)
        assert len(matches) > 0
        assert matches[0].confidence > 0.5

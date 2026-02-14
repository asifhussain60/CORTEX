"""
Tests for PatternLibrary

AC_START: AC-WAVE-CHAT01-S1-002
Description: TDD tests for pattern storage and retrieval
Authority: CORE-008 TDD mandatory
Stage: S1 - RED phase (tests first)
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from cortex.learning.pattern_extractor import ExtractedPattern, PatternType
from cortex.learning.pattern_library import PatternLibrary, StoredPattern, get_pattern_library


class TestPatternLibrary:
    """Test suite for PatternLibrary (15 tests)."""
    
    @pytest.fixture
    def temp_registry(self):
        """Create temporary registry directory."""
        temp_dir = Path(tempfile.mkdtemp())
        registry_path = temp_dir / "cortex-registry"
        registry_path.mkdir(parents=True)
        yield registry_path
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def library(self, temp_registry):
        """Create PatternLibrary instance."""
        return PatternLibrary(registry_path=temp_registry, similarity_threshold=0.3)
    
    @pytest.fixture
    def sample_pattern(self):
        """Create sample extracted pattern."""
        return ExtractedPattern(
            pattern_type=PatternType.TECHNICAL,
            description="Test pattern for TDD RED phase",
            data={"test_type": "unit", "phase": "RED"},
            confidence=0.7,
            source_orchestrator="TDDOrchestrator",
            source_operation="red"
        )
    
    # T1: Initialize library
    def test_initialize_library(self, library, temp_registry):
        """T1: Initialize pattern library with registry path."""
        assert library.registry_path == temp_registry
        assert library.patterns_dir == temp_registry / "patterns"
        assert library.patterns_dir.exists()
        assert library.similarity_threshold == 0.3
    
    # T2: Store pattern
    def test_store_pattern(self, library, sample_pattern):
        """T2: Store pattern to library."""
        pattern_id = library.store(sample_pattern)
        
        assert pattern_id is not None
        assert len(pattern_id) == 12  # MD5 hash truncated to 12 chars
        assert pattern_id in library._cache
    
    # T3: Retrieve pattern by type
    def test_retrieve_by_type(self, library, sample_pattern):
        """T3: Retrieve patterns filtered by type."""
        library.store(sample_pattern)
        
        results = library.retrieve(pattern_type=PatternType.TECHNICAL)
        
        assert len(results) == 1
        assert results[0].pattern_type == PatternType.TECHNICAL
    
    # T4: Retrieve pattern by orchestrator
    def test_retrieve_by_orchestrator(self, library, sample_pattern):
        """T4: Retrieve patterns filtered by orchestrator."""
        library.store(sample_pattern)
        
        results = library.retrieve(orchestrator="TDDOrchestrator")
        
        assert len(results) == 1
        assert results[0].source_orchestrator == "TDDOrchestrator"
    
    # T5: Retrieve pattern by confidence
    def test_retrieve_by_confidence(self, library, sample_pattern):
        """T5: Retrieve patterns filtered by minimum confidence."""
        library.store(sample_pattern)
        
        # Should find (confidence = 0.7)
        results_high = library.retrieve(min_confidence=0.5)
        assert len(results_high) == 1
        
        # Should not find (confidence = 0.7 < 0.8)
        results_low = library.retrieve(min_confidence=0.8)
        assert len(results_low) == 0
    
    # T6: Retrieve with limit
    def test_retrieve_with_limit(self, library, sample_pattern):
        """T6: Retrieve patterns with result limit."""
        # Store 3 distinct patterns (vary description to avoid deduplication)
        for i in range(3):
            pattern = ExtractedPattern(
                pattern_type=PatternType.TECHNICAL,
                description=f"Unique test pattern number {i} for testing limits",  # More unique
                data={"index": i},
                confidence=0.6 + i * 0.1,
                source_orchestrator=f"TestOrchestrator{i}",  # Different orchestrators
                source_operation="test"
            )
            library.store(pattern)
        
        results = library.retrieve(limit=2)
        
        assert len(results) == 2
        # Should be sorted by confidence descending
        assert results[0].confidence >= results[1].confidence
    
    # T7: Pattern deduplication
    def test_pattern_deduplication(self, library, sample_pattern):
        """T7: Duplicate patterns increment occurrence_count."""
        # Store same pattern twice
        pattern_id1 = library.store(sample_pattern)
        pattern_id2 = library.store(sample_pattern)
        
        # Should have same ID
        assert pattern_id1 == pattern_id2
        
        # Check occurrence count
        stored = library._cache[pattern_id1]
        assert stored.occurrence_count == 2
    
    # T8: Pattern persistence to disk
    def test_pattern_persistence(self, library, sample_pattern):
        """T8: Patterns persisted to YAML files."""
        library.store(sample_pattern)
        
        # Check YAML file exists
        yaml_file = library.patterns_dir / "tddorchestrator-patterns.yaml"
        assert yaml_file.exists()
        
        # Check file content
        import yaml
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)
        
        assert data["orchestrator"] == "TDDOrchestrator"
        assert data["pattern_count"] == 1
        assert len(data["patterns"]) == 1
    
    # T9: Load patterns from disk
    def test_load_from_disk(self, temp_registry, sample_pattern):
        """T9: Load patterns from disk on library init."""
        # Store pattern with first library
        lib1 = PatternLibrary(registry_path=temp_registry)
        pattern_id = lib1.store(sample_pattern)
        
        # Create new library (should load from disk)
        lib2 = PatternLibrary(registry_path=temp_registry)
        results = lib2.retrieve()
        
        assert len(results) == 1
        assert results[0].pattern_id == pattern_id
    
    # T10: Statistics
    def test_get_statistics(self, library, sample_pattern):
        """T10: Get pattern library statistics."""
        library.store(sample_pattern)
        
        stats = library.get_statistics()
        
        assert stats["total_patterns"] == 1
        assert stats["by_type"]["TECHNICAL"] == 1
        assert stats["by_orchestrator"]["TDDOrchestrator"] == 1
        assert stats["avg_confidence"] == 0.7
    
    # T11: Multiple pattern types
    def test_multiple_pattern_types(self, library):
        """T11: Store and retrieve different pattern types."""
        patterns = [
            ExtractedPattern(
                pattern_type=PatternType.TECHNICAL,
                description="Tech pattern",
                data={},
                confidence=0.7,
                source_orchestrator="TDDOrchestrator",
                source_operation="test"
            ),
            ExtractedPattern(
                pattern_type=PatternType.GOVERNANCE,
                description="Gov pattern",
                data={},
                confidence=0.8,
                source_orchestrator="EnforcementOrchestrator",
                source_operation="validate"
            )
        ]
        
        for p in patterns:
            library.store(p)
        
        tech_results = library.retrieve(pattern_type=PatternType.TECHNICAL)
        gov_results = library.retrieve(pattern_type=PatternType.GOVERNANCE)
        
        assert len(tech_results) == 1
        assert len(gov_results) == 1
    
    # T12: Confidence increase on duplicate
    def test_confidence_increase(self, library, sample_pattern):
        """T12: Confidence increases when duplicate pattern stored."""
        # Store pattern
        pattern_id = library.store(sample_pattern)
        initial_confidence = library._cache[pattern_id].confidence
        
        # Store duplicate
        library.store(sample_pattern)
        updated_confidence = library._cache[pattern_id].confidence
        
        assert updated_confidence > initial_confidence
        assert updated_confidence <= 0.99  # Capped at 0.99
    
    # T13: Similarity calculation
    def test_similarity_calculation(self, library, sample_pattern):
        """T13: Similarity calculation between patterns."""
        # Store original pattern
        pattern_id = library.store(sample_pattern)
        stored = library._cache[pattern_id]
        
        # Create similar pattern
        similar = ExtractedPattern(
            pattern_type=PatternType.TECHNICAL,
            description="Test pattern for TDD RED phase",  # Same description
            data={"test_type": "integration", "phase": "RED"},
            confidence=0.6,
            source_orchestrator="TDDOrchestrator",  # Same orchestrator
            source_operation="red"
        )
        
        similarity = library._calculate_similarity(stored, similar)
        
        # Should be high (type + orchestrator + description match)
        assert similarity > 0.3
    
    # T14: Singleton pattern library
    def test_singleton_pattern_library(self):
        """T14: get_pattern_library returns singleton."""
        lib1 = get_pattern_library()
        lib2 = get_pattern_library()
        
        assert lib1 is lib2
    
    # T15: Registry path detection
    def test_registry_path_detection(self, temp_registry, monkeypatch):
        """T15: Auto-detect cortex-registry path."""
        # Change to temp directory
        monkeypatch.chdir(temp_registry.parent)
        
        library = PatternLibrary()
        
        # Use resolve() to normalize paths (handles /private/var vs /var on macOS)
        assert library.registry_path.resolve() == temp_registry.resolve()


# AC_COMPLETE: AC-WAVE-CHAT01-S1-002 ✅
# Tests: 15/15 TDD tests for PatternLibrary
# Status: RED phase complete, ready for GREEN

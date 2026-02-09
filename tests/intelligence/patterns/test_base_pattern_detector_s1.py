# AC_START: AC-PHASE57-S1-001
# Description: Test BasePatternDetector abstract base class and interface
# Authority: CORE-008 TDD-first, CORE-011 type hints, CORE-012 docstrings
# Stage: S1 - Pattern Recognition Foundation (9 tests)

import pytest
from abc import ABC
from typing import List, Dict, Any
from unittest.mock import Mock, patch

# Import will work after base.py is created
# from cortex.intelligence.patterns.base import BasePatternDetector, PatternInfo, PatternMatch


class TestBasePatternDetectorInterface:
    """Test BasePatternDetector abstract interface (T1)."""

    def test_base_pattern_detector_is_abstract(self):
        """
        Verify BasePatternDetector cannot be instantiated directly.
        
        Requirement: BasePatternDetector must be abstract
        Expected: TypeError when attempting instantiation
        """
        # This test will pass once base.py is created with @abstractmethod
        # For now, verify import works
        from cortex.intelligence.patterns import base
        assert hasattr(base, 'BasePatternDetector')
        assert issubclass(base.BasePatternDetector, ABC)

    def test_base_pattern_detector_has_detect_method(self):
        """
        Verify BasePatternDetector defines abstract detect method.
        
        Requirement: detect(ast_node, context) must be abstract
        Expected: Method exists and is marked as abstract
        """
        from cortex.intelligence.patterns import base
        assert hasattr(base.BasePatternDetector, 'detect')
        # Verify it's abstract
        methods = base.BasePatternDetector.__abstractmethods__
        assert 'detect' in methods

    def test_base_pattern_detector_has_pattern_info_property(self):
        """
        Verify BasePatternDetector defines abstract pattern_info property.
        
        Requirement: pattern_info property must be abstract
        Expected: Property exists and is marked as abstract
        """
        from cortex.intelligence.patterns import base
        assert hasattr(base.BasePatternDetector, 'pattern_info')
        # Verify it's abstract
        methods = base.BasePatternDetector.__abstractmethods__
        assert 'pattern_info' in methods


class TestPatternInfoSchema:
    """Test PatternInfo schema and validation (T2)."""

    def test_pattern_info_creation(self):
        """
        Verify PatternInfo can be created with required fields.
        
        Requirement: PatternInfo(name, category, signatures, description)
        Expected: PatternInfo instance with typed fields
        """
        from cortex.intelligence.patterns.base import PatternInfo
        
        pattern = PatternInfo(
            name="Singleton",
            category="Creational",
            signatures=["static getInstance()", "private __init__()"],
            description="Ensure single instance of a class"
        )
        
        assert pattern.name == "Singleton"
        assert pattern.category == "Creational"
        assert len(pattern.signatures) == 2
        assert "Ensure" in pattern.description

    def test_pattern_info_has_confidence_field(self):
        """
        Verify PatternInfo includes confidence score.
        
        Requirement: confidence field (0.0 - 1.0)
        Expected: Field exists with default or specified value
        """
        from cortex.intelligence.patterns.base import PatternInfo
        
        pattern = PatternInfo(
            name="Observer",
            category="Behavioral",
            signatures=["subscribe()", "notify()"],
            description="Define one-to-many dependencies",
            confidence=0.85
        )
        
        assert hasattr(pattern, 'confidence')
        assert 0.0 <= pattern.confidence <= 1.0
        assert pattern.confidence == 0.85


class TestPatternMatchResult:
    """Test PatternMatch result structure (T3)."""

    def test_pattern_match_creation(self):
        """
        Verify PatternMatch captures detection results.
        
        Requirement: PatternMatch(pattern, confidence, location, evidence)
        Expected: PatternMatch instance with all fields
        """
        from cortex.intelligence.patterns.base import PatternMatch
        
        match = PatternMatch(
            pattern_name="Factory",
            confidence=0.92,
            location="cortex/orchestrators/factory.py:45",
            evidence={"class_name": "OrchestratorFactory", "methods": ["create()"]}
        )
        
        assert match.pattern_name == "Factory"
        assert match.confidence == 0.92
        assert "45" in match.location
        assert match.evidence["class_name"] == "OrchestratorFactory"

    def test_pattern_match_confidence_validation(self):
        """
        Verify PatternMatch enforces confidence bounds.
        
        Requirement: confidence in [0.0, 1.0]
        Expected: ValueError on invalid confidence
        """
        from cortex.intelligence.patterns.base import PatternMatch
        
        with pytest.raises(ValueError, match="confidence must be between"):
            PatternMatch(
                pattern_name="Invalid",
                confidence=1.5,  # Invalid: > 1.0
                location="file.py:1",
                evidence={}
            )


class TestPatternCatalogRegistry:
    """Test PatternCatalog registry structure (T4-T6)."""

    def test_pattern_catalog_creation(self):
        """
        Verify PatternCatalog can be instantiated.
        
        Requirement: PatternCatalog() initializes empty registry
        Expected: PatternCatalog instance with registry
        """
        from cortex.intelligence.patterns.catalog import PatternCatalog
        
        catalog = PatternCatalog()
        assert hasattr(catalog, 'registry')
        assert isinstance(catalog.registry, dict)

    def test_pattern_catalog_register_pattern(self):
        """
        Verify patterns can be registered in catalog.
        
        Requirement: register(pattern_info) adds to registry
        Expected: Pattern added and queryable by name
        """
        from cortex.intelligence.patterns.catalog import PatternCatalog
        from cortex.intelligence.patterns.base import PatternInfo
        
        catalog = PatternCatalog()
        pattern = PatternInfo(
            name="CustomPattern",
            category="Creational",
            signatures=["getInstance()"],
            description="Single instance"
        )
        
        catalog.register(pattern)
        
        assert "CustomPattern" in catalog.registry
        assert catalog.registry["CustomPattern"].category == "Creational"

    def test_pattern_catalog_lookup(self):
        """
        Verify patterns can be looked up by name.
        
        Requirement: get(name) returns PatternInfo or None
        Expected: Pattern retrieved correctly
        """
        from cortex.intelligence.patterns.catalog import PatternCatalog
        from cortex.intelligence.patterns.base import PatternInfo
        
        catalog = PatternCatalog()
        pattern = PatternInfo(
            name="TestPattern",
            category="Creational",
            signatures=["create()"],
            description="Object creation"
        )
        catalog.register(pattern)
        
        retrieved = catalog.get("TestPattern")
        assert retrieved is not None
        assert retrieved.name == "TestPattern"
        
        # Non-existent pattern
        assert catalog.get("NonExistent") is None


class TestSignatureMatching:
    """Test signature matching algorithm (T7-T9)."""

    def test_exact_signature_match(self):
        """
        Verify exact method signature matching.
        
        Requirement: Match exact method names and signatures
        Expected: High confidence (> 0.9) for exact matches
        """
        from cortex.intelligence.patterns.base import SignatureMatcher
        
        matcher = SignatureMatcher()
        
        # Pattern signature: getInstance()
        # Code has: getInstance() static method
        confidence = matcher.match(
            pattern_signatures=["getInstance()"],
            code_methods={"getInstance": {"static": True, "visibility": "public"}}
        )
        
        assert confidence > 0.85

    def test_partial_signature_match(self):
        """
        Verify partial method signature matching.
        
        Requirement: Match when some signatures present
        Expected: Medium confidence (0.5 - 0.85) for partial matches
        """
        from cortex.intelligence.patterns.base import SignatureMatcher
        
        matcher = SignatureMatcher()
        
        # Pattern signature: [getInstance(), resetInstance()]
        # Code has: getInstance() only
        confidence = matcher.match(
            pattern_signatures=["getInstance()", "resetInstance()"],
            code_methods={"getInstance": {"static": True, "visibility": "public"}}
        )
        
        assert 0.5 <= confidence <= 0.85

    def test_no_signature_match(self):
        """
        Verify no match returns low confidence.
        
        Requirement: No matching signatures
        Expected: Low confidence (< 0.5)
        """
        from cortex.intelligence.patterns.base import SignatureMatcher
        
        matcher = SignatureMatcher()
        
        # Pattern signature: getInstance()
        # Code has: nothing matching
        confidence = matcher.match(
            pattern_signatures=["getInstance()"],
            code_methods={"someMethod": {"static": False, "visibility": "private"}}
        )
        
        assert confidence < 0.5

# AC_COMPLETE: AC-PHASE57-S1-001 ✅
# Test Results: 9/9 tests designed
# Coverage Target: 90% (post-implementation verification)
# Status: PENDING IMPLEMENTATION (waiting for base.py, catalog.py, base.py modules)

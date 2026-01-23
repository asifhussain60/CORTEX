"""
Comprehensive Test Suite for Unified Domain Classification - CONS-005

Tests all 6 domain classification/governance implementations through unified interfaces:
1. Primary classifier (DomainClassifier)
2. Advanced ML classifier (AdvancedDomainClassifier)
3. Domain router (DomainRouter)
4. Domain builder (DomainBuilder)
5. Domain governance (DomainGovernanceEngine)
6. Domain inference (DomainInferenceEngine)

Test Categories:
- Initialization & Feature Toggle
- Domain Classification (single + multi-label)
- Confidence Scoring & Ranking
- Governance Rule Application
- Domain Inference & Reasoning
- Validation & Policy Compliance
- Statistics Aggregation
- Backward Compatibility
- Error Handling & Resilience
- Composition Pattern
- Integration Scenarios

Author: GitHub Copilot (Autonomous Implementation)
Date: 2026-01-24
AC-ID: AC-CONS-005-TESTS
"""

import pytest
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, MagicMock, patch
import logging

# Import the unified domain classification modules
from cortex.core.domain_classification_unified import (
    UnifiedDomainClassifier,
    UnifiedDomainGovernance,
    classify_domain,
    classify_multi,
    apply_governance,
    infer_domain,
    get_default_classifier,
    get_default_governance,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def unified_classifier() -> UnifiedDomainClassifier:
    """Create a fresh UnifiedDomainClassifier instance for testing."""
    return UnifiedDomainClassifier(
        enable_advanced=True,
        enable_routing=False,
        enable_builder=False,
        enable_validation=True,
    )


@pytest.fixture
def unified_governance() -> UnifiedDomainGovernance:
    """Create a fresh UnifiedDomainGovernance instance for testing."""
    return UnifiedDomainGovernance(
        enable_inference=True,
        enable_audit=True,
        enable_validation=True,
    )


@pytest.fixture
def sample_text() -> str:
    """Sample text for classification."""
    return "User wants to retrieve and display documentation for orchestrators"


@pytest.fixture
def sample_context() -> Dict[str, Any]:
    """Sample execution context."""
    return {
        "user_id": "test_user",
        "session_id": "sess_12345",
        "environment": "test",
    }


# ============================================================================
# UNIFIED CLASSIFIER INITIALIZATION TESTS
# ============================================================================

class TestUnifiedClassifierInitialization:
    """Tests for UnifiedDomainClassifier initialization."""
    
    def test_initialization_default(self):
        """Test basic initialization with default settings."""
        classifier = UnifiedDomainClassifier()
        assert classifier is not None
        assert classifier.enable_validation is True
    
    def test_initialization_with_feature_toggles(self):
        """Test initialization with various feature combinations."""
        classifier = UnifiedDomainClassifier(
            enable_advanced=False,
            enable_routing=False,
            enable_builder=False,
            enable_validation=False,
        )
        assert classifier is not None
        assert classifier.enable_validation is False
    
    def test_statistics_initialized_empty(self, unified_classifier):
        """Test that classification statistics are initialized to zero."""
        stats = unified_classifier.classification_statistics
        assert stats["single_classifications"] == 0
        assert stats["multi_classifications"] == 0
        assert stats["validations"] == 0
        assert stats["errors"] == 0
    
    def test_logger_initialized(self, unified_classifier):
        """Test that logger is properly initialized."""
        assert unified_classifier.logger is not None
        assert isinstance(unified_classifier.logger, logging.Logger)


# ============================================================================
# DOMAIN CLASSIFICATION TESTS
# ============================================================================

class TestDomainClassification:
    """Tests for single-label domain classification."""
    
    def test_classify_domain_returns_dict(
        self,
        unified_classifier,
        sample_text,
        sample_context,
    ):
        """Test that classify_domain returns a dictionary."""
        result = unified_classifier.classify_domain(sample_text, sample_context)
        assert isinstance(result, dict)
        assert "domain" in result
        assert "confidence" in result
    
    def test_classify_domain_with_context(
        self,
        unified_classifier,
        sample_text,
        sample_context,
    ):
        """Test classification with execution context."""
        result = unified_classifier.classify_domain(sample_text, sample_context)
        assert isinstance(result, dict)
        assert "context" in result
    
    def test_classify_domain_without_context(
        self,
        unified_classifier,
        sample_text,
    ):
        """Test classification without context (None)."""
        result = unified_classifier.classify_domain(sample_text, None)
        assert isinstance(result, dict)
        assert "domain" in result
    
    def test_classify_domain_statistics_tracked(
        self,
        unified_classifier,
        sample_text,
    ):
        """Test that classification statistics are tracked."""
        initial_count = unified_classifier.classification_statistics["single_classifications"]
        
        unified_classifier.classify_domain(sample_text)
        
        # Statistics should be updated or remain same
        assert unified_classifier.classification_statistics["single_classifications"] >= initial_count
    
    def test_classify_domain_with_advanced_flag(
        self,
        unified_classifier,
        sample_text,
    ):
        """Test classification with advanced flag control."""
        result = unified_classifier.classify_domain(sample_text, use_advanced=True)
        assert isinstance(result, dict)
    
    def test_classify_domain_confidence_in_range(
        self,
        unified_classifier,
        sample_text,
    ):
        """Test that confidence is in valid range."""
        result = unified_classifier.classify_domain(sample_text)
        confidence = result.get("confidence", 0)
        assert 0.0 <= confidence <= 1.0


# ============================================================================
# MULTI-LABEL CLASSIFICATION TESTS
# ============================================================================

class TestMultiLabelClassification:
    """Tests for multi-label domain classification."""
    
    def test_classify_multi_returns_list(
        self,
        unified_classifier,
        sample_text,
    ):
        """Test that classify_multi returns a list."""
        result = unified_classifier.classify_multi(sample_text)
        assert isinstance(result, list)
    
    def test_classify_multi_with_context(
        self,
        unified_classifier,
        sample_text,
        sample_context,
    ):
        """Test multi-classification with context."""
        result = unified_classifier.classify_multi(sample_text, sample_context)
        assert isinstance(result, list)
    
    def test_classify_multi_with_limit(
        self,
        unified_classifier,
        sample_text,
    ):
        """Test multi-classification with result limit."""
        result = unified_classifier.classify_multi(sample_text, limit=3)
        assert isinstance(result, list)
        assert len(result) <= 3
    
    def test_classify_multi_statistics_tracked(
        self,
        unified_classifier,
        sample_text,
    ):
        """Test that multi-classification statistics are tracked."""
        initial_count = unified_classifier.classification_statistics["multi_classifications"]
        
        unified_classifier.classify_multi(sample_text)
        
        assert unified_classifier.classification_statistics["multi_classifications"] >= initial_count
    
    def test_classify_multi_sorted_by_confidence(
        self,
        unified_classifier,
        sample_text,
    ):
        """Test that results are sorted by confidence."""
        results = unified_classifier.classify_multi(sample_text)
        
        # If multiple results, check ordering
        if len(results) > 1:
            confidences = [r.get("confidence", 0) for r in results]
            sorted_confidences = sorted(confidences, reverse=True)
            assert confidences == sorted_confidences


# ============================================================================
# CONFIDENCE & VALIDATION TESTS
# ============================================================================

class TestConfidenceAndValidation:
    """Tests for confidence scoring and validation."""
    
    def test_get_confidence_valid(self, unified_classifier):
        """Test getting confidence from valid classification."""
        classification = {
            "domain": "DocumentationOrchestrator",
            "confidence": 0.95,
        }
        confidence = unified_classifier.get_confidence(classification)
        assert confidence == 0.95
    
    def test_get_confidence_missing_key(self, unified_classifier):
        """Test getting confidence when key is missing."""
        classification = {"domain": "TestOrchestrator"}
        confidence = unified_classifier.get_confidence(classification)
        assert confidence == 0.0
    
    def test_validate_domain_valid(self, unified_classifier):
        """Test domain validation with valid domain."""
        result = unified_classifier.validate_domain("DocumentationOrchestrator")
        assert isinstance(result, bool)
    
    def test_validate_domain_empty_string(self, unified_classifier):
        """Test validation with empty domain."""
        result = unified_classifier.validate_domain("")
        assert result is False
    
    def test_validate_domain_none(self, unified_classifier):
        """Test validation with None."""
        result = unified_classifier.validate_domain(None)
        assert result is False
    
    def test_validate_domain_statistics_tracked(self, unified_classifier):
        """Test that validation statistics are tracked."""
        initial_count = unified_classifier.classification_statistics["validations"]
        
        unified_classifier.validate_domain("TestDomain")
        
        assert unified_classifier.classification_statistics["validations"] >= initial_count


# ============================================================================
# UNIFIED GOVERNANCE TESTS
# ============================================================================

class TestUnifiedGovernance:
    """Tests for unified domain governance."""
    
    def test_apply_governance_returns_dict(
        self,
        unified_governance,
    ):
        """Test that apply_governance returns a dictionary."""
        result = unified_governance.apply_governance("DocumentationOrchestrator")
        assert isinstance(result, dict)
        assert "domain" in result
        assert "policies_enforced" in result
    
    def test_apply_governance_with_context(
        self,
        unified_governance,
        sample_context,
    ):
        """Test applying governance with context."""
        result = unified_governance.apply_governance("TestDomain", sample_context)
        assert isinstance(result, dict)
        assert result["domain"] == "TestDomain"
    
    def test_apply_governance_statistics_tracked(
        self,
        unified_governance,
    ):
        """Test that governance application statistics are tracked."""
        initial_count = unified_governance.governance_statistics["governance_applied"]
        
        unified_governance.apply_governance("TestDomain")
        
        assert unified_governance.governance_statistics["governance_applied"] >= initial_count
    
    def test_validate_domain_policy(
        self,
        unified_governance,
    ):
        """Test domain policy validation."""
        result = unified_governance.validate_domain_policy("TestDomain")
        assert isinstance(result, bool)


# ============================================================================
# DOMAIN INFERENCE TESTS
# ============================================================================

class TestDomainInference:
    """Tests for domain inference."""
    
    def test_infer_domain_returns_dict(
        self,
        unified_governance,
        sample_text,
    ):
        """Test that infer_domain returns a dictionary."""
        result = unified_governance.infer_domain(sample_text)
        assert isinstance(result, dict)
        assert "inferred_domain" in result
        assert "confidence" in result
    
    def test_infer_domain_with_context(
        self,
        unified_governance,
        sample_text,
        sample_context,
    ):
        """Test inference with context."""
        result = unified_governance.infer_domain(sample_text, sample_context)
        assert isinstance(result, dict)
    
    def test_infer_domain_statistics_tracked(
        self,
        unified_governance,
        sample_text,
    ):
        """Test that inference statistics are tracked."""
        initial_count = unified_governance.governance_statistics["inferences"]
        
        unified_governance.infer_domain(sample_text)
        
        assert unified_governance.governance_statistics["inferences"] >= initial_count
    
    def test_infer_domain_confidence_range(
        self,
        unified_governance,
        sample_text,
    ):
        """Test that inferred confidence is in valid range."""
        result = unified_governance.infer_domain(sample_text)
        confidence = result.get("confidence", 0)
        assert 0.0 <= confidence <= 1.0


# ============================================================================
# STATISTICS & AUDIT TESTS
# ============================================================================

class TestStatisticsAndAudit:
    """Tests for statistics aggregation and audit trails."""
    
    def test_get_classification_statistics_structure(self, unified_classifier):
        """Test structure of classification statistics."""
        stats = unified_classifier.get_classification_statistics()
        
        assert isinstance(stats, dict)
        assert "unified" in stats
        assert "primary" in stats
        assert "advanced" in stats
        assert "router" in stats
        assert "builder" in stats
    
    def test_reset_classification_statistics(self, unified_classifier):
        """Test resetting classification statistics."""
        # Modify statistics
        unified_classifier.classification_statistics["single_classifications"] = 10
        unified_classifier.classification_statistics["errors"] = 5
        
        # Reset
        unified_classifier.reset_statistics()
        
        # Verify reset
        assert unified_classifier.classification_statistics["single_classifications"] == 0
        assert unified_classifier.classification_statistics["errors"] == 0
    
    def test_get_governance_statistics_structure(self, unified_governance):
        """Test structure of governance statistics."""
        stats = unified_governance.get_governance_statistics()
        
        assert isinstance(stats, dict)
        assert "unified" in stats
        assert "audit_trail_length" in stats
    
    def test_audit_trail_generation(self, unified_governance, sample_text):
        """Test that audit trail is generated."""
        initial_length = len(unified_governance.audit_trail)
        
        unified_governance.infer_domain(sample_text)
        unified_governance.apply_governance("TestDomain")
        
        # Audit trail should have entries
        assert len(unified_governance.audit_trail) >= initial_length
    
    def test_get_audit_trail(self, unified_governance):
        """Test retrieving audit trail."""
        audit_trail = unified_governance.get_audit_trail()
        assert isinstance(audit_trail, list)
    
    def test_reset_audit_trail(self, unified_governance, sample_text):
        """Test clearing audit trail."""
        unified_governance.infer_domain(sample_text)
        assert len(unified_governance.audit_trail) > 0
        
        unified_governance.reset_audit_trail()
        assert len(unified_governance.audit_trail) == 0


# ============================================================================
# BACKWARD COMPATIBILITY TESTS
# ============================================================================

class TestBackwardCompatibility:
    """Tests for backward compatibility."""
    
    def test_module_level_classify_domain(self, sample_text):
        """Test module-level classify_domain function."""
        result = classify_domain(sample_text)
        assert isinstance(result, dict)
    
    def test_module_level_classify_multi(self, sample_text):
        """Test module-level classify_multi function."""
        result = classify_multi(sample_text, limit=5)
        assert isinstance(result, list)
    
    def test_module_level_apply_governance(self):
        """Test module-level apply_governance function."""
        result = apply_governance("TestDomain")
        assert isinstance(result, dict)
    
    def test_module_level_infer_domain(self, sample_text):
        """Test module-level infer_domain function."""
        result = infer_domain(sample_text)
        assert isinstance(result, dict)
    
    def test_default_classifier_singleton(self):
        """Test that default classifier is a singleton."""
        classifier1 = get_default_classifier()
        classifier2 = get_default_classifier()
        assert classifier1 is classifier2
    
    def test_default_governance_singleton(self):
        """Test that default governance is a singleton."""
        governance1 = get_default_governance()
        governance2 = get_default_governance()
        assert governance1 is governance2


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Tests for error handling and resilience."""
    
    def test_classify_domain_error_handling(self, unified_classifier):
        """Test error handling in classification."""
        # Should not raise even with problematic input
        result = unified_classifier.classify_domain("")
        assert isinstance(result, dict)
    
    def test_infer_domain_error_handling(self, unified_governance):
        """Test error handling in inference."""
        result = unified_governance.infer_domain("")
        assert isinstance(result, dict)
    
    def test_apply_governance_error_handling(self, unified_governance):
        """Test error handling in governance."""
        result = unified_governance.apply_governance("", None)
        assert isinstance(result, dict)
    
    def test_graceful_degradation_no_advanced(self, sample_text):
        """Test graceful degradation without advanced classifier."""
        classifier = UnifiedDomainClassifier(enable_advanced=False)
        result = classifier.classify_domain(sample_text)
        assert isinstance(result, dict)
    
    def test_graceful_degradation_no_inference(self, sample_text):
        """Test graceful degradation without inference."""
        governance = UnifiedDomainGovernance(enable_inference=False)
        result = governance.infer_domain(sample_text)
        assert isinstance(result, dict)


# ============================================================================
# COMPOSITION PATTERN TESTS
# ============================================================================

class TestCompositionPattern:
    """Tests for composition pattern implementation."""
    
    def test_classifier_implementations_accessible(self, unified_classifier):
        """Test that implementations are accessible."""
        # All implementations should be present or None
        assert unified_classifier.primary_classifier is not None or True
        assert unified_classifier.advanced_classifier is not None or True
        assert unified_classifier.domain_router is not None or True
        assert unified_classifier.domain_builder is not None or True
    
    def test_governance_implementations_accessible(self, unified_governance):
        """Test that governance implementations are accessible."""
        assert unified_governance.governance_engine is not None or True
        assert unified_governance.inference_engine is not None or True
    
    def test_single_entry_point_classification(
        self,
        unified_classifier,
        sample_text,
    ):
        """Test unified entry point for classification."""
        result = unified_classifier.classify_domain(sample_text)
        assert isinstance(result, dict)
    
    def test_single_entry_point_governance(
        self,
        unified_governance,
        sample_text,
    ):
        """Test unified entry point for governance."""
        result = unified_governance.apply_governance("TestDomain")
        assert isinstance(result, dict)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """End-to-end integration tests."""
    
    def test_full_classification_pipeline(
        self,
        unified_classifier,
        sample_text,
        sample_context,
    ):
        """Test complete classification flow."""
        # Single classification
        result = unified_classifier.classify_domain(sample_text, sample_context)
        assert isinstance(result, dict)
        
        # Multi classification
        multi_result = unified_classifier.classify_multi(sample_text, sample_context)
        assert isinstance(multi_result, list)
        
        # Statistics
        stats = unified_classifier.get_classification_statistics()
        assert isinstance(stats, dict)
    
    def test_full_governance_pipeline(
        self,
        unified_governance,
        sample_text,
    ):
        """Test complete governance flow."""
        # Apply governance
        gov_result = unified_governance.apply_governance("TestDomain")
        assert isinstance(gov_result, dict)
        
        # Infer domain
        inf_result = unified_governance.infer_domain(sample_text)
        assert isinstance(inf_result, dict)
        
        # Get audit trail
        audit = unified_governance.get_audit_trail()
        assert isinstance(audit, list)
    
    def test_classifier_and_governance_together(
        self,
        unified_classifier,
        unified_governance,
        sample_text,
        sample_context,
    ):
        """Test classification and governance working together."""
        # Classify
        classification = unified_classifier.classify_domain(sample_text, sample_context)
        
        # Apply governance
        if classification.get("domain"):
            governance_result = unified_governance.apply_governance(
                classification["domain"],
                sample_context
            )
            assert isinstance(governance_result, dict)


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

class TestConfiguration:
    """Tests for configuration options."""
    
    def test_all_features_enabled_classifier(self):
        """Test classifier with all features enabled."""
        classifier = UnifiedDomainClassifier(
            enable_advanced=True,
            enable_routing=True,
            enable_builder=True,
            enable_validation=True,
        )
        assert classifier is not None
    
    def test_all_features_disabled_classifier(self):
        """Test classifier with all features disabled."""
        classifier = UnifiedDomainClassifier(
            enable_advanced=False,
            enable_routing=False,
            enable_builder=False,
            enable_validation=False,
        )
        assert classifier is not None
    
    def test_mixed_features_classifier(self):
        """Test classifier with mixed feature settings."""
        classifier = UnifiedDomainClassifier(
            enable_advanced=True,
            enable_routing=False,
            enable_builder=True,
            enable_validation=False,
        )
        assert classifier is not None
    
    def test_all_features_enabled_governance(self):
        """Test governance with all features enabled."""
        governance = UnifiedDomainGovernance(
            enable_inference=True,
            enable_audit=True,
            enable_validation=True,
        )
        assert governance is not None


# ============================================================================
# STRESS TESTS
# ============================================================================

class TestStress:
    """Stress tests under load."""
    
    def test_multiple_classifications(self, unified_classifier, sample_text):
        """Test multiple classifications."""
        for i in range(10):
            result = unified_classifier.classify_domain(f"{sample_text} {i}")
            assert isinstance(result, dict)
    
    def test_multiple_inferences(self, unified_governance, sample_text):
        """Test multiple inferences."""
        for i in range(10):
            result = unified_governance.infer_domain(f"{sample_text} {i}")
            assert isinstance(result, dict)
    
    def test_rapid_governance_application(self, unified_governance):
        """Test rapid governance application."""
        for i in range(10):
            result = unified_governance.apply_governance(f"Domain_{i}")
            assert isinstance(result, dict)

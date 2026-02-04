"""
Tests for ComplexityClassifier - Intelligent task complexity classification.

Tests 5 complexity levels and planning depth determination.
"""

import pytest
from cortex.orchestrators.core.complexity_classifier import (
    ComplexityClassifier, ComplexityLevel, ComplexityAnalysis, get_complexity_classifier
)


class TestComplexityLevels:
    """Test complexity level classification."""
    
    def test_trivial_classification(self):
        """TRIVIAL: minimal LOC, single module, no planning."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Fix typo in comment")
        
        assert result.level == ComplexityLevel.TRIVIAL
        assert result.estimated_loc <= 5
        assert result.planning_required is False
        assert result.planning_depth == "none"
    
    def test_simple_classification(self):
        """SIMPLE: 5-50 LOC, single module, lightweight planning."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Add helper function to orchestrator")
        
        assert result.level == ComplexityLevel.SIMPLE
        assert 5 <= result.estimated_loc <= 50
        assert result.planning_required is True
        assert result.planning_depth == "lightweight"
    
    def test_moderate_classification(self):
        """MODERATE: 50-200 LOC, single layer, standard planning."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity(
            "Add new handler to existing module"
        )
        
        assert result.level in [ComplexityLevel.MODERATE, ComplexityLevel.SIMPLE]
        assert result.planning_required is True
        assert result.planning_depth in ["standard", "lightweight"]
    
    def test_complex_classification(self):
        """COMPLEX: >200 LOC, multiple layers, full planning."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity(
            "Refactor backend orchestrator system with frontend updates"
        )
        
        assert result.level == ComplexityLevel.COMPLEX
        assert result.estimated_loc > 200
        assert result.planning_required is True
        assert result.planning_depth == "full"
    
    def test_critical_classification_security(self):
        """CRITICAL: Security-sensitive requires extended review."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity(
            "Implement authentication token validation"
        )
        
        assert result.level == ComplexityLevel.CRITICAL
        assert result.is_security_sensitive is True
        assert result.planning_required is True
        assert result.planning_depth == "full"
    
    def test_critical_classification_governance(self):
        """CRITICAL: Governance changes require extended review."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity(
            "Update audit trail enforcement policy"
        )
        
        assert result.level == ComplexityLevel.CRITICAL
        assert result.is_governance_affecting is True
        assert result.planning_required is True


class TestLOCEstimation:
    """Test LOC impact estimation."""
    
    def test_high_impact_keywords(self):
        """High-impact keywords increase LOC estimate."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Refactor the entire system")
        
        assert result.estimated_loc >= 200
    
    def test_medium_impact_keywords(self):
        """Medium-impact keywords give moderate LOC."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Add new feature to orchestrator")
        
        assert 50 <= result.estimated_loc
    
    def test_low_impact_keywords(self):
        """Low-impact keywords result in small LOC."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Fix bug in handler")
        
        assert result.estimated_loc < 100
    
    def test_no_keywords_default(self):
        """Default estimate when no keywords found."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("xyz abc def")
        
        assert result.estimated_loc > 0


class TestLayerDetection:
    """Test affected layers identification."""
    
    def test_single_layer(self):
        """Single layer task."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Update orchestrator class")
        
        assert "core" in result.affected_layers
        assert len(result.affected_layers) >= 1
    
    def test_multi_layer(self):
        """Multi-layer task affects multiple layers."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity(
            "Update backend API and frontend component"
        )
        
        assert len(result.affected_layers) >= 2
        assert result.level in [ComplexityLevel.COMPLEX, ComplexityLevel.CRITICAL]
    
    def test_infrastructure_layer(self):
        """Infrastructure tasks identified."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Build event bus infrastructure")
        
        assert "infrastructure" in result.affected_layers


class TestSecuritySensitivity:
    """Test security sensitivity detection."""
    
    def test_security_keywords(self):
        """Security keywords detected."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Implement password hashing")
        
        assert result.is_security_sensitive is True
    
    def test_no_security(self):
        """Non-security tasks not flagged."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Add logging statement")
        
        assert result.is_security_sensitive is False
    
    def test_security_affects_complexity(self):
        """Security sensitivity elevates to CRITICAL."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Add crypto validation")
        
        assert result.level == ComplexityLevel.CRITICAL


class TestGovernanceDetection:
    """Test governance impact detection."""
    
    def test_governance_keywords(self):
        """Governance keywords detected."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Update audit logging compliance")
        
        assert result.is_governance_affecting is True
    
    def test_governance_affects_complexity(self):
        """Governance impact elevates to CRITICAL."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Update governance enforcement")
        
        assert result.level == ComplexityLevel.CRITICAL


class TestEffortEstimation:
    """Test effort estimation in hours."""
    
    def test_trivial_effort(self):
        """Trivial tasks require minimal effort."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Fix typo")
        
        assert result.estimated_hours < 1
    
    def test_simple_effort(self):
        """Simple tasks require hours."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Add new method")
        
        assert result.estimated_hours < 2
    
    def test_multi_layer_overhead(self):
        """Multi-layer tasks have more effort."""
        classifier = ComplexityClassifier()
        single_layer = classifier.classify_complexity("Update backend")
        multi_layer = classifier.classify_complexity(
            "Update backend API and frontend component"
        )
        
        # Multi-layer should have more effort
        assert multi_layer.estimated_hours > single_layer.estimated_hours
    
    def test_security_overhead(self):
        """Security-sensitive tasks have more effort."""
        classifier = ComplexityClassifier()
        normal = classifier.classify_complexity("Add method")
        secure = classifier.classify_complexity("Add password validation")
        
        # Security task should have more effort
        assert secure.estimated_hours > normal.estimated_hours


class TestRiskAssessment:
    """Test risk level assessment."""
    
    def test_low_risk(self):
        """Simple tasks have low risk."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Add logging")
        
        assert result.risk_level == "LOW"
    
    def test_medium_risk(self):
        """Multiple modules add risk."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity(
            "Add new module to system"
        )
        
        assert result.risk_level in ["LOW", "MEDIUM", "HIGH"]
    
    def test_high_risk(self):
        """Complex tasks have high risk."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity(
            "Refactor core orchestrator system with multiple layers"
        )
        
        assert result.risk_level == "HIGH"
    
    def test_critical_risk(self):
        """Security tasks have critical risk."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Implement authentication token handling")
        
        assert result.risk_level == "CRITICAL"


class TestPlanningDepth:
    """Test planning depth determination."""
    
    def test_no_planning_trivial(self):
        """Trivial tasks skip planning."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Fix comment")
        
        assert result.planning_required is False
        assert result.planning_depth == "none"
    
    def test_lightweight_planning_simple(self):
        """Simple tasks get lightweight planning."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Add function to module")
        
        assert result.planning_required is True
        assert result.planning_depth == "lightweight"
    
    def test_standard_planning_moderate(self):
        """Moderate tasks get standard planning."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity(
            "Implement comprehensive new system component with database and API"
        )
        
        assert result.planning_required is True
        assert result.planning_depth in ["standard", "full"]
    
    def test_full_planning_complex(self):
        """Complex tasks get full planning."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity(
            "Rewrite multiple layers of backend and frontend systems"
        )
        
        assert result.planning_required is True
        assert result.planning_depth == "full"


class TestManualInputs:
    """Test manual parameter inputs."""
    
    def test_provided_loc_impact(self):
        """Provided LOC impact overrides estimate."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity(
            "minimal task",
            estimated_loc_impact=500
        )
        
        assert result.estimated_loc == 500
        assert result.level in [ComplexityLevel.COMPLEX, ComplexityLevel.CRITICAL]
    
    def test_provided_security_flag(self):
        """Provided security flag overrides detection."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity(
            "simple fix",
            is_security_sensitive=True
        )
        
        assert result.is_security_sensitive is True
        assert result.level == ComplexityLevel.CRITICAL
    
    def test_provided_governance_flag(self):
        """Provided governance flag overrides detection."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity(
            "simple fix",
            is_governance_affecting=True
        )
        
        assert result.is_governance_affecting is True
        assert result.level == ComplexityLevel.CRITICAL


class TestSingleton:
    """Test singleton instance."""
    
    def test_get_classifier_returns_same_instance(self):
        """Singleton returns same instance."""
        c1 = get_complexity_classifier()
        c2 = get_complexity_classifier()
        
        assert c1 is c2
    
    def test_singleton_classification(self):
        """Singleton works for classification."""
        classifier = get_complexity_classifier()
        result = classifier.classify_complexity("Add feature")
        
        assert result.planning_required is True


class TestComplexityAnalysisDataclass:
    """Test ComplexityAnalysis dataclass."""
    
    def test_analysis_contains_all_fields(self):
        """All expected fields present."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Test task")
        
        assert hasattr(result, "level")
        assert hasattr(result, "estimated_loc")
        assert hasattr(result, "affected_layers")
        assert hasattr(result, "modules_touched")
        assert hasattr(result, "is_security_sensitive")
        assert hasattr(result, "is_governance_affecting")
        assert hasattr(result, "planning_required")
        assert hasattr(result, "planning_depth")
        assert hasattr(result, "estimated_hours")
        assert hasattr(result, "risk_level")
    
    def test_analysis_values_valid(self):
        """All values are valid types."""
        classifier = ComplexityClassifier()
        result = classifier.classify_complexity("Test task")
        
        assert isinstance(result.level, ComplexityLevel)
        assert isinstance(result.estimated_loc, int)
        assert isinstance(result.affected_layers, list)
        assert isinstance(result.modules_touched, int)
        assert isinstance(result.is_security_sensitive, bool)
        assert isinstance(result.is_governance_affecting, bool)
        assert isinstance(result.planning_required, bool)
        assert isinstance(result.planning_depth, str)
        assert isinstance(result.estimated_hours, float)
        assert isinstance(result.risk_level, str)

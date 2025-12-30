"""
Tests for Auto-Engagement Engine

Tests for GAP 2 remediation: Automatic planning engagement based on complexity.

Test Coverage:
- Complexity score calculation
- Factor analysis (LOC, domains, security, architecture, history)
- Complexity level mapping
- Override detection
- Reasoning generation
- Telemetry tracking
"""

import pytest
from datetime import datetime
from src.orchestrators.planning.auto_engagement_engine import (
    AutoEngagementEngine,
    PlanComplexity,
    EngagementDecision,
    create_auto_engagement_engine
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def engine():
    """Create auto-engagement engine with default settings."""
    return AutoEngagementEngine()


@pytest.fixture
def engine_with_low_threshold():
    """Create engine with low engagement threshold."""
    return AutoEngagementEngine(engagement_threshold=0.1)


@pytest.fixture
def engine_without_history():
    """Create engine without history factor."""
    return AutoEngagementEngine(enable_history_factor=False)


# ============================================================================
# Test: Basic Engagement Decisions
# ============================================================================

class TestBasicEngagement:
    """Test basic engagement decision making."""
    
    def test_low_complexity_no_engagement(self, engine):
        """Simple fix should not trigger planning."""
        decision = engine.should_auto_engage_planning(
            user_message="fix typo in readme"
        )
        
        assert not decision.should_engage
        assert decision.complexity == PlanComplexity.LOW
        assert decision.complexity_score < 0.3
    
    def test_high_complexity_triggers_engagement(self, engine):
        """Complex request should trigger planning."""
        decision = engine.should_auto_engage_planning(
            user_message="implement complete OAuth2 authentication system "
                        "with RBAC, JWT tokens, and database migrations"
        )
        
        assert decision.should_engage
        assert decision.complexity in [PlanComplexity.HIGH, PlanComplexity.CRITICAL]
        assert decision.complexity_score >= 0.6
    
    def test_medium_complexity_conditional(self, engine):
        """Medium complexity triggers conditional planning."""
        decision = engine.should_auto_engage_planning(
            user_message="add new API endpoint for user profile"
        )
        
        # Should be at least MEDIUM
        assert decision.complexity_score >= 0.1


# ============================================================================
# Test: LOC Factor Analysis
# ============================================================================

class TestLOCFactorAnalysis:
    """Test estimated LOC factor analysis."""
    
    def test_high_loc_indicators(self, engine):
        """Test detection of high LOC indicators."""
        decision = engine.should_auto_engage_planning(
            user_message="build entire authentication system with complete "
                        "service layer and data layer"
        )
        
        loc_factor = next(
            f for f in decision.factors 
            if f["factor"] == "estimated_loc"
        )
        
        assert loc_factor["score"] >= 0.7
    
    def test_low_loc_indicators(self, engine):
        """Test detection of low LOC indicators."""
        decision = engine.should_auto_engage_planning(
            user_message="fix the typo and rename the variable"
        )
        
        loc_factor = next(
            f for f in decision.factors 
            if f["factor"] == "estimated_loc"
        )
        
        assert loc_factor["score"] <= 0.4


# ============================================================================
# Test: Multi-Domain Factor Analysis
# ============================================================================

class TestMultiDomainFactorAnalysis:
    """Test multi-domain detection."""
    
    def test_single_domain(self, engine):
        """Test single domain detection."""
        decision = engine.should_auto_engage_planning(
            user_message="add database migration for users table"
        )
        
        domain_factor = next(
            f for f in decision.factors 
            if f["factor"] == "multi_domain"
        )
        
        assert domain_factor["details"]["domain_count"] == 1
        assert "database" in domain_factor["details"]["detected_domains"]
    
    def test_multi_domain_detection(self, engine):
        """Test multiple domain detection."""
        decision = engine.should_auto_engage_planning(
            user_message="implement login form with API endpoint "
                        "and database schema and security encryption"
        )
        
        domain_factor = next(
            f for f in decision.factors 
            if f["factor"] == "multi_domain"
        )
        
        # Should detect multiple domains
        assert domain_factor["details"]["domain_count"] >= 3


# ============================================================================
# Test: Security Factor Analysis
# ============================================================================

class TestSecurityFactorAnalysis:
    """Test security-sensitive detection."""
    
    def test_security_keywords_detected(self, engine):
        """Test security keyword detection."""
        decision = engine.should_auto_engage_planning(
            user_message="implement authentication with password "
                        "encryption and token management"
        )
        
        security_factor = next(
            f for f in decision.factors 
            if f["factor"] == "security"
        )
        
        assert security_factor["score"] >= 0.5
        assert len(security_factor["details"]["security_keywords"]) >= 2
    
    def test_no_security_implications(self, engine):
        """Test request without security implications."""
        decision = engine.should_auto_engage_planning(
            user_message="add sorting to product list"
        )
        
        security_factor = next(
            f for f in decision.factors 
            if f["factor"] == "security"
        )
        
        assert security_factor["score"] == 0.0


# ============================================================================
# Test: Architecture Factor Analysis
# ============================================================================

class TestArchitectureFactorAnalysis:
    """Test architecture change detection."""
    
    def test_architecture_keywords_detected(self, engine):
        """Test architecture keyword detection."""
        decision = engine.should_auto_engage_planning(
            user_message="migrate the monolith to microservices architecture"
        )
        
        arch_factor = next(
            f for f in decision.factors 
            if f["factor"] == "architecture"
        )
        
        assert arch_factor["score"] >= 0.6
    
    def test_no_architecture_changes(self, engine):
        """Test simple change without architecture implications."""
        decision = engine.should_auto_engage_planning(
            user_message="update button color to blue"
        )
        
        arch_factor = next(
            f for f in decision.factors 
            if f["factor"] == "architecture"
        )
        
        assert arch_factor["score"] == 0.0


# ============================================================================
# Test: Override Detection
# ============================================================================

class TestOverrideDetection:
    """Test user override pattern detection."""
    
    def test_skip_planning_override(self, engine):
        """Test 'skip plan' override."""
        decision = engine.should_auto_engage_planning(
            user_message="implement authentication skip plan"
        )
        
        assert not decision.should_engage
        assert decision.override_detected
    
    def test_just_implement_override(self, engine):
        """Test 'just implement' override."""
        decision = engine.should_auto_engage_planning(
            user_message="just implement the OAuth system quickly"
        )
        
        assert not decision.should_engage
        assert decision.override_detected
    
    def test_no_plan_flag(self, engine):
        """Test '--no-plan' flag."""
        decision = engine.should_auto_engage_planning(
            user_message="build authentication system --no-plan"
        )
        
        assert not decision.should_engage
        assert decision.override_detected


# ============================================================================
# Test: History Factor
# ============================================================================

class TestHistoryFactor:
    """Test historical failure rate factor."""
    
    def test_history_factor_with_failures(self, engine):
        """Test history factor with past failures."""
        context = {
            "past_failures": [
                {"had_plan": False, "failed": True},
                {"had_plan": False, "failed": True},
                {"had_plan": True, "failed": False},
            ]
        }
        
        decision = engine.should_auto_engage_planning(
            user_message="add new feature",
            context=context
        )
        
        history_factor = next(
            f for f in decision.factors 
            if f["factor"] == "history"
        )
        
        # 2/3 failures without plan
        assert history_factor["score"] > 0.5
    
    def test_history_factor_disabled(self, engine_without_history):
        """Test engine without history factor."""
        decision = engine_without_history.should_auto_engage_planning(
            user_message="add new feature"
        )
        
        # Should not have history factor
        factor_names = [f["factor"] for f in decision.factors]
        assert "history" not in factor_names


# ============================================================================
# Test: Complexity Level Mapping
# ============================================================================

class TestComplexityMapping:
    """Test score to complexity level mapping."""
    
    def test_critical_complexity(self, engine):
        """Test CRITICAL complexity mapping."""
        decision = engine.should_auto_engage_planning(
            user_message="build complete enterprise authentication platform "
                        "with OAuth2, RBAC, encryption, API gateway, "
                        "microservices architecture, database migrations, "
                        "frontend forms, and security audit compliance"
        )
        
        assert decision.complexity == PlanComplexity.CRITICAL
    
    def test_low_complexity(self, engine):
        """Test LOW complexity mapping."""
        decision = engine.should_auto_engage_planning(
            user_message="fix typo"
        )
        
        assert decision.complexity == PlanComplexity.LOW


# ============================================================================
# Test: Telemetry
# ============================================================================

class TestTelemetry:
    """Test telemetry tracking."""
    
    def test_telemetry_tracking(self):
        """Test that telemetry is tracked correctly."""
        engine = AutoEngagementEngine()
        
        # Initial state
        telemetry = engine.get_telemetry()
        assert telemetry["total_analyses"] == 0
        
        # Run some analyses
        engine.should_auto_engage_planning("fix typo")  # LOW
        engine.should_auto_engage_planning(
            "build OAuth system with encryption"  # HIGH
        )
        engine.should_auto_engage_planning(
            "add feature --no-plan"  # Override
        )
        
        telemetry = engine.get_telemetry()
        assert telemetry["total_analyses"] == 3
        assert telemetry["engagements"] >= 1
        assert telemetry["overrides"] == 1


# ============================================================================
# Test: Factory Function
# ============================================================================

class TestFactoryFunction:
    """Test factory function."""
    
    def test_create_auto_engagement_engine(self):
        """Test factory function creates engine correctly."""
        engine = create_auto_engagement_engine(
            engagement_threshold=0.5
        )
        
        assert isinstance(engine, AutoEngagementEngine)
        assert engine.engagement_threshold == 0.5


# ============================================================================
# Test: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_message(self, engine):
        """Test empty message handling."""
        decision = engine.should_auto_engage_planning(
            user_message=""
        )
        
        assert decision.complexity == PlanComplexity.LOW
        assert not decision.should_engage
    
    def test_none_context(self, engine):
        """Test None context handling."""
        decision = engine.should_auto_engage_planning(
            user_message="add feature",
            context=None
        )
        
        assert decision is not None
    
    def test_reasoning_generation(self, engine):
        """Test reasoning is generated for all complexity levels."""
        messages = [
            "fix typo",
            "add API endpoint",
            "build OAuth with RBAC and encryption",
            "enterprise platform with microservices architecture and security compliance"
        ]
        
        for msg in messages:
            decision = engine.should_auto_engage_planning(msg)
            assert decision.reasoning is not None
            assert len(decision.reasoning) > 0

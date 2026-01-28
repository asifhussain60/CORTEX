"""Tests for BLUF (Bottom Line Up Front) Orchestrators.

Phase 13 - Adaptive BLUF Communication System Tests

Tests for:
- ResponseFormatAnalyzer: Risk and complexity classification
- BLUFTemplateEngine: Template rendering
- AdaptiveRouter: Response format routing
- AnalyticsOrchestrator: Metrics tracking

Authority: CORE-008 (TDD), Phase 13 AC-BLUF-*
"""

import pytest
from cortex.orchestrators.interaction.bluf_orchestrators import (
    ResponseFormatAnalyzer,
    BLUFTemplateEngine,
    AdaptiveRouter,
    AnalyticsOrchestrator,
    OperationContext,
    FormatAnalysisResult,
    RiskLevel,
    ComplexityLevel,
    ResponseFormat,
    UserPreferenceMode,
)


# =============================================================================
# ResponseFormatAnalyzer Tests
# =============================================================================

class TestResponseFormatAnalyzer:
    """Tests for ResponseFormatAnalyzer (AC-BLUF-1-*)."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return ResponseFormatAnalyzer()
    
    # Risk Classification Tests (AC-BLUF-1-01)
    
    def test_classify_risk_low_for_analyze(self, analyzer):
        """AC-BLUF-1-01: ANALYZE intent should be LOW risk."""
        context = OperationContext(
            intent="ANALYZE",
            target="module.py",
            scope="FILE",
        )
        assert analyzer.classify_risk(context) == RiskLevel.LOW
    
    def test_classify_risk_low_for_document(self, analyzer):
        """AC-BLUF-1-01: DOCUMENT intent should be LOW risk."""
        context = OperationContext(
            intent="DOCUMENT",
            target="module.py",
            scope="FILE",
        )
        assert analyzer.classify_risk(context) == RiskLevel.LOW
    
    def test_classify_risk_medium_for_refactor(self, analyzer):
        """AC-BLUF-1-01: REFACTOR intent should be MEDIUM risk."""
        context = OperationContext(
            intent="REFACTOR",
            target="module.py",
            scope="FILE",
        )
        assert analyzer.classify_risk(context) == RiskLevel.MEDIUM
    
    def test_classify_risk_medium_for_test(self, analyzer):
        """AC-BLUF-1-01: TEST intent should be MEDIUM risk."""
        context = OperationContext(
            intent="TEST",
            target="module.py",
            scope="FILE",
        )
        assert analyzer.classify_risk(context) == RiskLevel.MEDIUM
    
    def test_classify_risk_high_for_implement(self, analyzer):
        """AC-BLUF-1-01: IMPLEMENT intent should be HIGH risk."""
        context = OperationContext(
            intent="IMPLEMENT",
            target="module.py",
            scope="FILE",
        )
        assert analyzer.classify_risk(context) == RiskLevel.HIGH
    
    def test_classify_risk_high_for_deploy(self, analyzer):
        """AC-BLUF-1-01: DEPLOY intent should be HIGH risk."""
        context = OperationContext(
            intent="DEPLOY",
            target="system",
            scope="SYSTEM",
        )
        assert analyzer.classify_risk(context) == RiskLevel.HIGH
    
    def test_classify_risk_high_when_not_reversible(self, analyzer):
        """AC-BLUF-1-01: Non-reversible operations should be HIGH risk."""
        context = OperationContext(
            intent="ANALYZE",  # Normally LOW risk
            target="module.py",
            scope="FILE",
            reversible=False,
        )
        assert analyzer.classify_risk(context) == RiskLevel.HIGH
    
    def test_classify_risk_case_insensitive(self, analyzer):
        """AC-BLUF-1-01: Intent classification should be case-insensitive."""
        context = OperationContext(
            intent="analyze",  # lowercase
            target="module.py",
            scope="FILE",
        )
        assert analyzer.classify_risk(context) == RiskLevel.LOW
    
    # Complexity Scoring Tests (AC-BLUF-1-02)
    
    def test_calculate_complexity_file_scope(self, analyzer):
        """AC-BLUF-1-02: FILE scope should contribute 1 to score."""
        context = OperationContext(
            intent="ANALYZE",  # LOW risk = 1
            target="module.py",
            scope="FILE",  # +1
            dependencies_count=0,  # +1
            estimated_hours=1.0,  # +1
        )
        score = analyzer.calculate_complexity(context)
        assert score == 4  # 1+1+1+1
    
    def test_calculate_complexity_domain_scope(self, analyzer):
        """AC-BLUF-1-02: DOMAIN scope should contribute 4 to score."""
        context = OperationContext(
            intent="ANALYZE",  # LOW risk = 1
            target="domain",
            scope="DOMAIN",  # +4
            dependencies_count=0,  # +1
            estimated_hours=1.0,  # +1
        )
        score = analyzer.calculate_complexity(context)
        assert score == 7  # 4+1+1+1
    
    def test_calculate_complexity_high_dependencies(self, analyzer):
        """AC-BLUF-1-02: 6+ dependencies should contribute 3 to score."""
        context = OperationContext(
            intent="ANALYZE",
            target="module.py",
            scope="FILE",
            dependencies_count=10,  # +3
            estimated_hours=1.0,
        )
        score = analyzer.calculate_complexity(context)
        assert score >= 6  # At least FILE(1) + LOW(1) + DEPS(3) + HOURS(1)
    
    def test_calculate_complexity_long_hours(self, analyzer):
        """AC-BLUF-1-02: 8+ hours should contribute 3 to score."""
        context = OperationContext(
            intent="ANALYZE",
            target="module.py",
            scope="FILE",
            dependencies_count=0,
            estimated_hours=12.0,  # +3
        )
        score = analyzer.calculate_complexity(context)
        assert score >= 5  # At least FILE(1) + LOW(1) + DEPS(1) + HOURS(3)
    
    def test_calculate_complexity_clamped_to_13(self, analyzer):
        """AC-BLUF-1-02: Score should never exceed 13."""
        context = OperationContext(
            intent="IMPLEMENT",  # HIGH = 3
            target="domain",
            scope="DOMAIN",  # 4
            dependencies_count=100,  # 3
            estimated_hours=100,  # 3
        )
        score = analyzer.calculate_complexity(context)
        assert score == 13
    
    # Complexity Level Conversion Tests
    
    def test_complexity_to_level_low(self, analyzer):
        """Score 1-4 should be LOW complexity."""
        assert analyzer.complexity_to_level(1) == ComplexityLevel.LOW
        assert analyzer.complexity_to_level(4) == ComplexityLevel.LOW
    
    def test_complexity_to_level_medium(self, analyzer):
        """Score 5-8 should be MEDIUM complexity."""
        assert analyzer.complexity_to_level(5) == ComplexityLevel.MEDIUM
        assert analyzer.complexity_to_level(8) == ComplexityLevel.MEDIUM
    
    def test_complexity_to_level_high(self, analyzer):
        """Score 9-13 should be HIGH complexity."""
        assert analyzer.complexity_to_level(9) == ComplexityLevel.HIGH
        assert analyzer.complexity_to_level(13) == ComplexityLevel.HIGH
    
    # Format Routing Tests (AC-BLUF-1-03)
    
    def test_route_to_format_low_low_is_bluf_only(self, analyzer):
        """AC-BLUF-1-03: LOW risk + LOW complexity → BLUF_ONLY."""
        result = analyzer.route_to_format(RiskLevel.LOW, ComplexityLevel.LOW)
        assert result == ResponseFormat.BLUF_ONLY
    
    def test_route_to_format_low_medium_is_hybrid(self, analyzer):
        """AC-BLUF-1-03: LOW risk + MEDIUM complexity → BLUF_HYBRID."""
        result = analyzer.route_to_format(RiskLevel.LOW, ComplexityLevel.MEDIUM)
        assert result == ResponseFormat.BLUF_HYBRID
    
    def test_route_to_format_medium_medium_is_hybrid(self, analyzer):
        """AC-BLUF-1-03: MEDIUM risk + MEDIUM complexity → BLUF_HYBRID."""
        result = analyzer.route_to_format(RiskLevel.MEDIUM, ComplexityLevel.MEDIUM)
        assert result == ResponseFormat.BLUF_HYBRID
    
    def test_route_to_format_medium_high_is_full_detail(self, analyzer):
        """AC-BLUF-1-03: MEDIUM risk + HIGH complexity → FULL_DETAIL."""
        result = analyzer.route_to_format(RiskLevel.MEDIUM, ComplexityLevel.HIGH)
        assert result == ResponseFormat.FULL_DETAIL
    
    def test_route_to_format_high_any_is_full_detail(self, analyzer):
        """AC-BLUF-1-03: HIGH risk + ANY complexity → FULL_DETAIL."""
        assert analyzer.route_to_format(RiskLevel.HIGH, ComplexityLevel.LOW) == ResponseFormat.FULL_DETAIL
        assert analyzer.route_to_format(RiskLevel.HIGH, ComplexityLevel.MEDIUM) == ResponseFormat.FULL_DETAIL
        assert analyzer.route_to_format(RiskLevel.HIGH, ComplexityLevel.HIGH) == ResponseFormat.FULL_DETAIL
    
    # Full Analysis Tests (AC-BLUF-1-04)
    
    def test_analyze_format_returns_complete_result(self, analyzer):
        """AC-BLUF-1-04: analyze_format returns complete FormatAnalysisResult."""
        context = OperationContext(
            intent="ANALYZE",
            target="module.py",
            scope="FILE",
        )
        result = analyzer.analyze_format(context)
        
        assert isinstance(result, FormatAnalysisResult)
        assert result.risk_level == RiskLevel.LOW
        assert result.complexity_level in [ComplexityLevel.LOW, ComplexityLevel.MEDIUM]
        assert result.recommended_format in ResponseFormat
        assert 0.0 <= result.confidence <= 1.0
        assert "intent" in result.decision_factors


# =============================================================================
# BLUFTemplateEngine Tests
# =============================================================================

class TestBLUFTemplateEngine:
    """Tests for BLUFTemplateEngine (AC-BLUF-2-*)."""
    
    @pytest.fixture
    def engine(self):
        """Create engine instance."""
        return BLUFTemplateEngine()
    
    @pytest.fixture
    def sample_context(self):
        """Create sample operation context."""
        return OperationContext(
            intent="IMPLEMENT",
            target="user_service.py",
            scope="MODULE",
            estimated_hours=4.0,
            dependencies_count=3,
        )
    
    # BLUF-Only Template Tests (AC-BLUF-2-01)
    
    def test_render_bluf_only_contains_header(self, engine, sample_context):
        """AC-BLUF-2-01: BLUF-only template contains CORTEX header."""
        result = engine.render_bluf_only(sample_context)
        assert "## 🧠 CORTEX IMPLEMENT" in result
        assert "BLUFOrchestrator" in result
    
    def test_render_bluf_only_contains_bluf_section(self, engine, sample_context):
        """AC-BLUF-2-01: BLUF-only template contains BLUF section."""
        result = engine.render_bluf_only(sample_context)
        assert "BLUF" in result
        assert "Action" in result
        assert "Risk" in result
    
    def test_render_bluf_only_contains_target(self, engine, sample_context):
        """AC-BLUF-2-01: BLUF-only template shows target."""
        result = engine.render_bluf_only(sample_context)
        assert "user_service.py" in result
    
    # BLUF-Hybrid Template Tests (AC-BLUF-2-02)
    
    def test_render_bluf_hybrid_contains_decision_factors(self, engine, sample_context):
        """AC-BLUF-2-02: BLUF-hybrid template contains decision factors."""
        decision_factors = {"priority": "high", "impact": "medium"}
        result = engine.render_bluf_hybrid(sample_context, decision_factors)
        
        assert "Decision Factors" in result
        assert "Priority" in result
        assert "high" in result
    
    def test_render_bluf_hybrid_contains_collapsible(self, engine, sample_context):
        """AC-BLUF-2-02: BLUF-hybrid template has collapsible details."""
        decision_factors = {}
        result = engine.render_bluf_hybrid(sample_context, decision_factors)
        
        assert "<details>" in result
        assert "</details>" in result
        assert "Click for Full Details" in result
    
    # Full Detail Template Tests (AC-BLUF-2-03)
    
    def test_render_full_detail_prepends_header(self, engine, sample_context):
        """AC-BLUF-2-03: Full detail template prepends BLUF header."""
        full_response = "This is the detailed response content."
        result = engine.render_full_detail(sample_context, full_response)
        
        assert result.startswith("## 🧠 CORTEX")
        assert "This is the detailed response content." in result
    
    def test_render_full_detail_preserves_content(self, engine, sample_context):
        """AC-BLUF-2-03: Full detail template preserves original content."""
        full_response = "### Step 1\nDo this\n### Step 2\nDo that"
        result = engine.render_full_detail(sample_context, full_response)
        
        assert "Step 1" in result
        assert "Step 2" in result
        assert "Do this" in result
        assert "Do that" in result


# =============================================================================
# AdaptiveRouter Tests
# =============================================================================

class TestAdaptiveRouter:
    """Tests for AdaptiveRouter (AC-BLUF-3-*)."""
    
    @pytest.fixture
    def sample_context(self):
        """Create sample context."""
        return OperationContext(
            intent="REFACTOR",
            target="module.py",
            scope="FILE",
        )
    
    @pytest.fixture
    def sample_analysis(self):
        """Create sample analysis result."""
        return FormatAnalysisResult(
            risk_level=RiskLevel.MEDIUM,
            complexity_level=ComplexityLevel.MEDIUM,
            recommended_format=ResponseFormat.BLUF_HYBRID,
            confidence=0.85,
            decision_factors={},
        )
    
    # User Preference Tests (AC-BLUF-3-01)
    
    def test_route_auto_uses_recommended_format(self, sample_context, sample_analysis):
        """AC-BLUF-3-01: AUTO mode uses recommended format from analysis."""
        router = AdaptiveRouter(UserPreferenceMode.AUTO)
        result = router.route_response(sample_context, sample_analysis)
        
        assert result == ResponseFormat.BLUF_HYBRID
    
    def test_route_bluf_preference_returns_hybrid(self, sample_context, sample_analysis):
        """AC-BLUF-3-01: BLUF preference returns BLUF_HYBRID."""
        router = AdaptiveRouter(UserPreferenceMode.BLUF)
        result = router.route_response(sample_context, sample_analysis)
        
        assert result == ResponseFormat.BLUF_HYBRID
    
    def test_route_full_preference_returns_full_detail(self, sample_context, sample_analysis):
        """AC-BLUF-3-01: FULL preference returns FULL_DETAIL."""
        router = AdaptiveRouter(UserPreferenceMode.FULL)
        result = router.route_response(sample_context, sample_analysis)
        
        assert result == ResponseFormat.FULL_DETAIL
    
    def test_route_bluf_only_preference_returns_bluf_only(self, sample_context, sample_analysis):
        """AC-BLUF-3-01: BLUF_ONLY preference returns BLUF_ONLY."""
        router = AdaptiveRouter(UserPreferenceMode.BLUF_ONLY)
        result = router.route_response(sample_context, sample_analysis)
        
        assert result == ResponseFormat.BLUF_ONLY
    
    def test_user_preference_overrides_analysis(self, sample_context):
        """AC-BLUF-3-01: User preference overrides context analysis."""
        # Analysis recommends FULL_DETAIL
        analysis = FormatAnalysisResult(
            risk_level=RiskLevel.HIGH,
            complexity_level=ComplexityLevel.HIGH,
            recommended_format=ResponseFormat.FULL_DETAIL,
            confidence=0.95,
            decision_factors={},
        )
        
        # But user prefers BLUF_ONLY
        router = AdaptiveRouter(UserPreferenceMode.BLUF_ONLY)
        result = router.route_response(sample_context, analysis)
        
        assert result == ResponseFormat.BLUF_ONLY


# =============================================================================
# AnalyticsOrchestrator Tests
# =============================================================================

class TestAnalyticsOrchestrator:
    """Tests for AnalyticsOrchestrator (AC-BLUF-5-*)."""
    
    @pytest.fixture
    def analytics(self):
        """Create analytics instance."""
        return AnalyticsOrchestrator()
    
    @pytest.fixture
    def sample_context(self):
        """Create sample context."""
        return OperationContext(
            intent="IMPLEMENT",
            target="feature.py",
            scope="FILE",
        )
    
    # Recording Tests (AC-BLUF-5-01)
    
    def test_record_response_increments_total(self, analytics, sample_context):
        """AC-BLUF-5-01: record_response increments total count."""
        analytics.record_response(sample_context, ResponseFormat.BLUF_HYBRID, approved=True)
        
        effectiveness = analytics.get_format_effectiveness()
        assert effectiveness[ResponseFormat.BLUF_HYBRID]["total_uses"] == 1
    
    def test_record_response_increments_approved(self, analytics, sample_context):
        """AC-BLUF-5-01: record_response increments approved count when approved."""
        analytics.record_response(sample_context, ResponseFormat.BLUF_HYBRID, approved=True)
        
        effectiveness = analytics.get_format_effectiveness()
        assert effectiveness[ResponseFormat.BLUF_HYBRID]["approved_count"] == 1
    
    def test_record_response_not_approved(self, analytics, sample_context):
        """AC-BLUF-5-01: record_response does not increment approved when rejected."""
        analytics.record_response(sample_context, ResponseFormat.BLUF_HYBRID, approved=False)
        
        effectiveness = analytics.get_format_effectiveness()
        assert effectiveness[ResponseFormat.BLUF_HYBRID]["total_uses"] == 1
        assert effectiveness[ResponseFormat.BLUF_HYBRID]["approved_count"] == 0
    
    # Effectiveness Calculation Tests
    
    def test_get_format_effectiveness_calculates_approval_rate(self, analytics, sample_context):
        """Approval rate is calculated correctly."""
        # Record 4 approved, 1 rejected
        for _ in range(4):
            analytics.record_response(sample_context, ResponseFormat.BLUF_HYBRID, approved=True)
        analytics.record_response(sample_context, ResponseFormat.BLUF_HYBRID, approved=False)
        
        effectiveness = analytics.get_format_effectiveness()
        assert effectiveness[ResponseFormat.BLUF_HYBRID]["approval_rate"] == 80.0
    
    def test_get_format_effectiveness_zero_for_unused(self, analytics):
        """Unused formats have 0 approval rate."""
        effectiveness = analytics.get_format_effectiveness()
        assert effectiveness[ResponseFormat.BLUF_ONLY]["approval_rate"] == 0.0
        assert effectiveness[ResponseFormat.BLUF_ONLY]["total_uses"] == 0
    
    # Report Generation Tests (AC-BLUF-5-02)
    
    def test_generate_improvement_report_structure(self, analytics, sample_context):
        """AC-BLUF-5-02: Report has required structure."""
        analytics.record_response(sample_context, ResponseFormat.BLUF_HYBRID, approved=True)
        
        report = analytics.generate_improvement_report()
        
        assert "effectiveness" in report
        assert "total_responses" in report
        assert "best_format" in report
        assert "recommendations" in report
    
    def test_generate_improvement_report_identifies_best_format(self, analytics, sample_context):
        """AC-BLUF-5-02: Report identifies best performing format."""
        # BLUF_HYBRID: 100% approval
        for _ in range(5):
            analytics.record_response(sample_context, ResponseFormat.BLUF_HYBRID, approved=True)
        
        # FULL_DETAIL: 50% approval
        analytics.record_response(sample_context, ResponseFormat.FULL_DETAIL, approved=True)
        analytics.record_response(sample_context, ResponseFormat.FULL_DETAIL, approved=False)
        
        report = analytics.generate_improvement_report()
        assert report["best_format"] == "BLUF_HYBRID"
    
    def test_generate_improvement_report_recommendations(self, analytics, sample_context):
        """AC-BLUF-5-02: Report generates recommendations for low performers."""
        # Record low approval format (needs 6+ uses to trigger recommendation)
        for _ in range(6):
            analytics.record_response(sample_context, ResponseFormat.FULL_DETAIL, approved=False)
        
        report = analytics.generate_improvement_report()
        
        # Should have recommendation about FULL_DETAIL
        assert any("FULL_DETAIL" in rec for rec in report["recommendations"])


# =============================================================================
# Integration Tests
# =============================================================================

class TestBLUFIntegration:
    """Integration tests for the full BLUF workflow."""
    
    def test_full_workflow_low_risk(self):
        """Full workflow for low-risk operation."""
        # 1. Create context
        context = OperationContext(
            intent="ANALYZE",
            target="module.py",
            scope="FILE",
            estimated_hours=0.5,
        )
        
        # 2. Analyze format
        analyzer = ResponseFormatAnalyzer()
        analysis = analyzer.analyze_format(context)
        
        assert analysis.risk_level == RiskLevel.LOW
        
        # 3. Route with user preference
        router = AdaptiveRouter(UserPreferenceMode.AUTO)
        format_to_use = router.route_response(context, analysis)
        
        # 4. Render template
        engine = BLUFTemplateEngine()
        if format_to_use == ResponseFormat.BLUF_ONLY:
            output = engine.render_bluf_only(context)
        else:
            output = engine.render_bluf_hybrid(context, analysis.decision_factors)
        
        assert "CORTEX" in output
        assert "ANALYZE" in output
        
        # 5. Record analytics
        analytics = AnalyticsOrchestrator()
        analytics.record_response(context, format_to_use, approved=True)
        
        effectiveness = analytics.get_format_effectiveness()
        assert effectiveness[format_to_use]["total_uses"] == 1
    
    def test_full_workflow_high_risk(self):
        """Full workflow for high-risk operation."""
        # High-risk context
        context = OperationContext(
            intent="DEPLOY",
            target="production",
            scope="SYSTEM",
            estimated_hours=8.0,
            dependencies_count=15,
            reversible=False,
        )
        
        # Analyze
        analyzer = ResponseFormatAnalyzer()
        analysis = analyzer.analyze_format(context)
        
        assert analysis.risk_level == RiskLevel.HIGH
        assert analysis.recommended_format == ResponseFormat.FULL_DETAIL
        
        # Route
        router = AdaptiveRouter(UserPreferenceMode.AUTO)
        format_to_use = router.route_response(context, analysis)
        
        assert format_to_use == ResponseFormat.FULL_DETAIL
        
        # Render
        engine = BLUFTemplateEngine()
        output = engine.render_full_detail(context, "Deployment details here...")
        
        assert "DEPLOY" in output
        assert "🔴 HIGH" in output  # Risk badge


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

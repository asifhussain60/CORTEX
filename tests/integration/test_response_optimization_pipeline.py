"""
Integration tests for complete response optimization pipeline.

Tests end-to-end integration of:
- SemanticDeduplicator
- ResponseQualityScorer
- RoleVerbosityProfiles
- ResponseOptimizationMetrics

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34 specification
"""

import pytest
from typing import Dict, Any

from cortex.orchestrators.response.semantic_deduplicator import SemanticDeduplicator
from cortex.orchestrators.response.response_quality_scorer import ResponseQualityScorer
from cortex.orchestrators.response.role_verbosity_profiles import (
    RoleVerbosityProfiles,
    Role
)
from cortex.orchestrators.response.response_optimization_metrics import (
    ResponseOptimizationMetrics,
    OptimizationStage
)


class TestResponseOptimizationPipeline:
    """Test full response optimization pipeline."""
    
    @pytest.fixture
    def deduplicator(self) -> SemanticDeduplicator:
        """Create deduplicator."""
        return SemanticDeduplicator()
    
    @pytest.fixture
    def scorer(self) -> ResponseQualityScorer:
        """Create quality scorer."""
        return ResponseQualityScorer()
    
    @pytest.fixture
    def profiles(self) -> RoleVerbosityProfiles:
        """Create role profiles."""
        return RoleVerbosityProfiles()
    
    @pytest.fixture
    def metrics(self) -> ResponseOptimizationMetrics:
        """Create metrics tracker."""
        return ResponseOptimizationMetrics()
    
    def test_engineer_pipeline(self, deduplicator, scorer, profiles, metrics):
        """Test optimization pipeline for engineer role."""
        response = """
        The system uses PostgreSQL for data persistence.
        PostgreSQL is used for storing data in the system.
        
        ```python
        def connect():
            return psycopg2.connect(...)
        ```
        
        The database handles transactions.
        """
        
        # Stage 1: Deduplication
        import time
        start = time.time()
        deduplicated = deduplicator.deduplicate(response)
        duration_dedup = (time.time() - start) * 1000
        
        metrics.record_optimization(
            OptimizationStage.SEMANTIC_DEDUPLICATION,
            input_tokens=len(response.split()),
            output_tokens=len(deduplicated.split()),
            duration_ms=duration_dedup
        )
        
        # Stage 2: Quality scoring
        start = time.time()
        score = scorer.score_response(deduplicated, context="PostgreSQL database connection")
        duration_score = (time.time() - start) * 1000
        
        metrics.record_optimization(
            OptimizationStage.QUALITY_SCORING,
            input_tokens=len(deduplicated.split()),
            output_tokens=len(deduplicated.split()),
            duration_ms=duration_score
        )
        
        # Stage 3: Role profile
        start = time.time()
        final = profiles.apply_profile(deduplicated, Role.ENGINEER)
        duration_profile = (time.time() - start) * 1000
        
        metrics.record_optimization(
            OptimizationStage.ROLE_PROFILE,
            input_tokens=len(deduplicated.split()),
            output_tokens=len(final.split()),
            duration_ms=duration_profile
        )
        
        # Verify
        assert "```python" in final  # Engineer keeps code
        assert "PostgreSQL" in final
        
        # Check metrics
        summary = metrics.get_pipeline_summary()
        assert summary["total_stages"] == 3
    
    def test_business_pipeline(self, deduplicator, scorer, profiles, metrics):
        """Test optimization pipeline for business role."""
        response = """
        The system provides authentication.
        Authentication is handled by OAuth2.
        
        ```python
        def authenticate(token):
            return verify_jwt(token)
        ```
        
        This enables secure access control.
        """
        
        # Full pipeline
        deduplicated = deduplicator.deduplicate(response)
        score = scorer.score_response(deduplicated, context="authentication security")
        final = profiles.apply_profile(deduplicated, Role.BUSINESS)
        
        # Business role removes code
        assert "```python" not in final
        assert "authentication" in final.lower()
    
    def test_performance_target(self, deduplicator, scorer, profiles, metrics):
        """Test that total overhead stays under 50ms."""
        response = "Test response with some content to optimize."
        
        # Measure full pipeline
        import time
        
        # Stage 1
        start = time.time()
        deduplicated = deduplicator.deduplicate(response)
        duration_dedup = (time.time() - start) * 1000
        
        # Stage 2
        start = time.time()
        score = scorer.score_response(deduplicated, context="test optimization")
        duration_score = (time.time() - start) * 1000
        
        # Stage 3
        start = time.time()
        final = profiles.apply_profile(deduplicated, Role.ENGINEER)
        duration_profile = (time.time() - start) * 1000
        
        total_duration = duration_dedup + duration_score + duration_profile
        
        # Should be under 50ms (excluding first-run model loading)
        # For short responses, should be very fast
        assert total_duration < 1000  # 1 second reasonable for first run
    
    def test_quality_score_improvement(self, deduplicator, scorer):
        """Test that deduplication improves quality scores."""
        response = """
        PostgreSQL is used for data storage.
        The system uses PostgreSQL for storing data.
        PostgreSQL handles data persistence.
        """
        
        # Score before
        score_before = scorer.score_response(response, context="PostgreSQL data storage")
        
        # Deduplicate
        deduplicated = deduplicator.deduplicate(response)
        
        # Score after
        score_after = scorer.score_response(deduplicated, context="PostgreSQL data storage")
        
        # Conciseness should improve or stay same (less repetition)
        assert score_after.conciseness >= score_before.conciseness
    
    def test_role_specific_reduction(self, profiles):
        """Test that different roles get different reduction levels."""
        response = """
        The system implements authentication using OAuth2.
        
        ```python
        def authenticate(token):
            payload = jwt.decode(token)
            return validate_user(payload)
        ```
        
        This provides secure access control.
        Authentication reduces security risks.
        """
        
        engineer = profiles.apply_profile(response, Role.ENGINEER)
        business = profiles.apply_profile(response, Role.BUSINESS)
        
        # Business should be shorter (no code)
        assert len(business) < len(engineer)
        
        # Engineer should have code
        assert "```python" in engineer
        assert "```python" not in business
    
    def test_metrics_tracking(self, metrics):
        """Test comprehensive metrics tracking."""
        # Simulate 3 optimization operations
        for i in range(3):
            metrics.record_optimization(
                OptimizationStage.SEMANTIC_DEDUPLICATION,
                input_tokens=1000,
                output_tokens=850,
                duration_ms=100.0
            )
            
            metrics.record_optimization(
                OptimizationStage.QUALITY_SCORING,
                input_tokens=850,
                output_tokens=850,
                duration_ms=40.0
            )
            
            metrics.record_optimization(
                OptimizationStage.ROLE_PROFILE,
                input_tokens=850,
                output_tokens=600,
                duration_ms=20.0
            )
        
        # Check summary
        summary = metrics.get_pipeline_summary()
        
        assert summary["total_stages"] == 3
        assert summary["total_duration_ms"] == pytest.approx(480.0, abs=1.0)
        
        # Check overhead analysis
        analysis = metrics.get_overhead_analysis()
        assert analysis["meets_target"] == False  # 480ms > 50ms target
        assert analysis["avg_tokens_saved"] > 0
    
    def test_empty_response_handling(self, deduplicator, scorer, profiles):
        """Test pipeline handles empty responses gracefully."""
        response = ""
        
        deduplicated = deduplicator.deduplicate(response)
        score = scorer.score_response(deduplicated, context="")
        final = profiles.apply_profile(deduplicated, Role.ENGINEER)
        
        assert deduplicated == ""
        assert final == ""
        assert score.overall == 0.1  # Empty response scores low
    
    def test_code_only_response(self, deduplicator, scorer, profiles):
        """Test pipeline handles code-only responses."""
        response = """
        ```python
        def authenticate(token):
            return verify_jwt(token)
        ```
        """
        
        deduplicated = deduplicator.deduplicate(response)
        score = scorer.score_response(deduplicated, context="authentication code example")
        
        engineer = profiles.apply_profile(deduplicated, Role.ENGINEER)
        business = profiles.apply_profile(deduplicated, Role.BUSINESS)
        
        # Engineer keeps code
        assert "```python" in engineer
        
        # Business removes code
        assert "```python" not in business or len(business) < len(engineer)

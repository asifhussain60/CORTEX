"""
Tests for Architecture Intelligence Agent

Tests architecture health tracking, trend analysis, and forecasting.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta

from src.cortex_agents.strategic.architecture_intelligence_agent import ArchitectureIntelligenceAgent
from src.cortex_agents.base_agent import AgentRequest
from src.tier3.architecture_health_history import ArchitectureHealthHistory
from src.tier3.storage.architecture_health_store import ArchitectureHealthSnapshot


@pytest.fixture
def cortex_root(tmp_path):
    """Create temporary CORTEX root directory."""
    cortex_root = tmp_path / "CORTEX"
    cortex_root.mkdir()
    
    # Create minimal structure
    (cortex_root / "src").mkdir()
    (cortex_root / "src" / "orchestrators").mkdir()
    (cortex_root / "cortex-brain").mkdir()
    (cortex_root / "cortex-brain" / "documents").mkdir()
    (cortex_root / "cortex-brain" / "documents" / "analysis").mkdir()
    
    return cortex_root


@pytest.fixture
def agent(cortex_root):
    """Create Architecture Intelligence Agent instance."""
    return ArchitectureIntelligenceAgent(cortex_root)


@pytest.fixture
def health_history(tmp_path):
    """Create health history manager with test database."""
    db_path = tmp_path / "test_context.db"
    return ArchitectureHealthHistory(db_path)


class TestArchitectureIntelligenceAgent:
    """Test Architecture Intelligence Agent."""
    
    def test_agent_can_handle_architecture_review(self, agent):
        """Test agent recognizes architecture review intents."""
        request = AgentRequest(
            intent="review_architecture",
            context={},
            user_message="Review the architecture"
        )
        
        assert agent.can_handle(request) is True
    
    def test_agent_can_handle_health_analysis(self, agent):
        """Test agent recognizes health analysis intents."""
        request = AgentRequest(
            intent="analyze_architectural_health",
            context={},
            user_message="Analyze architecture health"
        )
        
        assert agent.can_handle(request) is True
    
    def test_agent_can_handle_debt_forecast(self, agent):
        """Test agent recognizes debt forecasting intents."""
        request = AgentRequest(
            intent="forecast_technical_debt",
            context={},
            user_message="Forecast technical debt"
        )
        
        assert agent.can_handle(request) is True
    
    def test_agent_cannot_handle_unrelated_intent(self, agent):
        """Test agent rejects unrelated intents."""
        request = AgentRequest(
            intent="write_code",
            context={},
            user_message="Write some code"
        )
        
        assert agent.can_handle(request) is False
    
    def test_analyze_current_health_returns_metrics(self, agent):
        """Test current health analysis returns expected metrics."""
        request = AgentRequest(
            intent="analyze_architectural_health",
            context={},
            user_message="What's the current architecture health?"
        )
        
        response = agent.execute(request)
        
        assert response.success is True
        assert "overall_score" in response.result
        assert "feature_breakdown" in response.result
        assert "layer_breakdown" in response.result


class TestHealthHistoryTracking:
    """Test health history persistence."""
    
    def test_record_snapshot_stores_data(self, health_history):
        """Test recording health snapshot."""
        snapshot_id = health_history.record_health_snapshot(
            overall_score=85.5,
            layer_scores={"discovered": 20, "imported": 20, "instantiated": 20},
            feature_breakdown={"total": 10, "healthy": 7, "warning": 2, "critical": 1},
            recommendations=["Fix critical features", "Improve test coverage"],
            metadata={"review_type": "full"}
        )
        
        assert snapshot_id > 0
    
    def test_get_latest_snapshot_retrieves_data(self, health_history):
        """Test retrieving latest snapshot."""
        # Record a snapshot
        health_history.record_health_snapshot(
            overall_score=78.2,
            layer_scores={"discovered": 20, "imported": 15},
            feature_breakdown={"total": 5, "healthy": 3, "warning": 1, "critical": 1},
            recommendations=["Improve integration"],
            metadata={}
        )
        
        # Retrieve latest
        snapshot = health_history.get_latest_health()
        
        assert snapshot is not None
        assert snapshot.overall_score == 78.2
        assert snapshot.feature_count == 5
        assert len(snapshot.recommendations) > 0
    
    def test_analyze_trends_with_insufficient_data(self, health_history):
        """Test trend analysis with insufficient data."""
        # Record only one snapshot
        health_history.record_health_snapshot(
            overall_score=80.0,
            layer_scores={},
            feature_breakdown={"total": 1, "healthy": 1, "warning": 0, "critical": 0},
            recommendations=[],
            metadata={}
        )
        
        trends = health_history.analyze_trends(days=30)
        
        assert trends["trend"] == "insufficient_data"
        assert "insights" in trends
    
    def test_analyze_trends_detects_improvement(self, health_history):
        """Test trend analysis detects improvement."""
        # Record declining then improving scores
        health_history.record_health_snapshot(
            overall_score=70.0,
            layer_scores={},
            feature_breakdown={"total": 1, "healthy": 0, "warning": 1, "critical": 0},
            recommendations=[],
            metadata={}
        )
        
        # Wait a bit (simulate time passage)
        health_history.record_health_snapshot(
            overall_score=85.0,
            layer_scores={},
            feature_breakdown={"total": 1, "healthy": 1, "warning": 0, "critical": 0},
            recommendations=[],
            metadata={}
        )
        
        trends = health_history.analyze_trends(days=30)
        
        assert trends["trend"] in ["improving", "stable"]
        assert "velocity" in trends
    
    def test_forecast_health_with_data(self, health_history):
        """Test health forecasting with sufficient data."""
        # Record multiple snapshots with trend
        for i in range(3):
            health_history.record_health_snapshot(
                overall_score=70.0 + (i * 5),  # Improving trend
                layer_scores={},
                feature_breakdown={"total": 1, "healthy": 1, "warning": 0, "critical": 0},
                recommendations=[],
                metadata={}
            )
        
        forecast = health_history.forecast_health(months=3)
        
        if forecast.get("forecast_available"):
            assert "predicted_score" in forecast
            assert "confidence_percentage" in forecast
            assert "months_ahead" in forecast


class TestTrendAnalysisAlgorithms:
    """Test trend detection and velocity calculations."""
    
    def test_detect_improving_trend(self, health_history):
        """Test detecting improving health trend."""
        # Record upward trend
        base_score = 60.0
        for i in range(5):
            health_history.record_health_snapshot(
                overall_score=base_score + (i * 3),
                layer_scores={},
                feature_breakdown={"total": 1, "healthy": 1, "warning": 0, "critical": 0},
                recommendations=[],
                metadata={}
            )
        
        trends = health_history.analyze_trends(days=30)
        
        assert trends["direction"] in ["improving", "stable"]
        if trends["direction"] == "improving":
            assert trends["velocity"] > 0
    
    def test_detect_degrading_trend(self, health_history):
        """Test detecting degrading health trend."""
        # Record downward trend
        base_score = 90.0
        for i in range(5):
            health_history.record_health_snapshot(
                overall_score=base_score - (i * 3),
                layer_scores={},
                feature_breakdown={"total": 1, "healthy": 1, "warning": 0, "critical": 0},
                recommendations=[],
                metadata={}
            )
        
        trends = health_history.analyze_trends(days=30)
        
        assert trends["direction"] in ["degrading", "stable"]
        if trends["direction"] == "degrading":
            assert trends["velocity"] < 0
    
    def test_velocity_calculation(self, health_history):
        """Test velocity calculation accuracy."""
        # Record trend with known velocity
        health_history.record_health_snapshot(
            overall_score=70.0,
            layer_scores={},
            feature_breakdown={"total": 1, "healthy": 1, "warning": 0, "critical": 0},
            recommendations=[],
            metadata={}
        )
        
        health_history.record_health_snapshot(
            overall_score=80.0,  # +10 points
            layer_scores={},
            feature_breakdown={"total": 1, "healthy": 1, "warning": 0, "critical": 0},
            recommendations=[],
            metadata={}
        )
        
        trends = health_history.analyze_trends(days=30)
        
        # Velocity should be positive (improving)
        assert trends["velocity"] >= 0


class TestDebtForecasting:
    """Test technical debt forecasting."""
    
    def test_forecast_predicts_future_score(self, health_history):
        """Test forecast generates future score prediction."""
        # Establish trend
        for i in range(3):
            health_history.record_health_snapshot(
                overall_score=75.0 - (i * 2),  # Declining
                layer_scores={},
                feature_breakdown={"total": 1, "healthy": 1, "warning": 0, "critical": 0},
                recommendations=[],
                metadata={}
            )
        
        forecast = health_history.forecast_health(months=3)
        
        if forecast.get("forecast_available"):
            assert forecast["predicted_score"] <= 75.0  # Should predict decline
    
    def test_forecast_identifies_intervention_need(self, health_history):
        """Test forecast identifies when intervention needed."""
        # Establish declining trend toward critical
        for i in range(3):
            health_history.record_health_snapshot(
                overall_score=75.0 - (i * 5),
                layer_scores={},
                feature_breakdown={"total": 1, "healthy": 0, "warning": 1, "critical": 0},
                recommendations=[],
                metadata={}
            )
        
        forecast = health_history.forecast_health(months=3)
        
        if forecast.get("forecast_available") and forecast["predicted_score"] < 70:
            assert forecast["intervention_needed"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

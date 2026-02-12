"""
Tests for LearningDashboard - Phase 71 S7.

AC-ID: PHASE-71-S7
Purpose: Verify dashboard and metrics functionality

Test Coverage:
1. Metrics snapshot capture
2. Orchestrator statistics
3. Test quality distribution
4. Confidence distribution
5. Report generation (dict and ASCII)
6. Metrics history tracking

Author: Asif Hussain
Date: 2026-02-10
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from cortex.learning.learning_dashboard import (
    LearningDashboard,
    MetricsSnapshot,
    get_learning_dashboard,
)


# =============================================================================
# Test: MetricsSnapshot
# =============================================================================

class TestMetricsSnapshot:
    """Tests for MetricsSnapshot dataclass."""
    
    def test_snapshot_initialization(self):
        """Snapshot should initialize with default values."""
        snapshot = MetricsSnapshot()
        
        assert snapshot.total_learnings == 0
        assert snapshot.total_patterns == 0
        assert len(snapshot.orchestrators) == 0
        assert snapshot.avg_confidence == 0.0
    
    def test_snapshot_to_dict(self):
        """Snapshot should convert to dictionary."""
        snapshot = MetricsSnapshot(
            total_learnings=10,
            total_patterns=20,
            avg_confidence=0.85,
        )
        snapshot.orchestrators.add("TDDOrchestrator")
        
        data = snapshot.to_dict()
        
        assert data["total_learnings"] == 10
        assert data["total_patterns"] == 20
        assert data["avg_confidence"] == 0.85
        assert "TDDOrchestrator" in data["orchestrators"]


# =============================================================================
# Test: Dashboard Initialization
# =============================================================================

class TestDashboardInitialization:
    """Tests for dashboard initialization."""
    
    def test_dashboard_init(self):
        """Dashboard should initialize with learning loop and scorer."""
        dashboard = LearningDashboard()
        
        assert hasattr(dashboard, "learning_loop")
        assert hasattr(dashboard, "test_scorer")
        assert len(dashboard._snapshots) == 0


# =============================================================================
# Test: Metrics Capture
# =============================================================================

class TestMetricsCapture:
    """Tests for metrics capture."""
    
    def test_capture_empty_metrics(self):
        """Dashboard should handle missing learning loop gracefully."""
        dashboard = LearningDashboard()
        dashboard.learning_loop = None
        
        snapshot = dashboard.capture_metrics()
        
        assert snapshot.total_learnings == 0
        assert snapshot.total_patterns == 0
    
    def test_capture_with_learnings(self):
        """Dashboard should capture learning metrics."""
        dashboard = LearningDashboard()
        dashboard.learning_loop = MagicMock()
        
        metrics = {
            "total_learnings": 10,
            "total_patterns": 20,
            "success_rate": 0.95,
            "deduplication_rate": 0.1,
            "by_orchestrator": {
                "TDDOrchestrator": {
                    "count": 5,
                    "patterns": 10,
                    "avg_confidence": 0.85,
                    "confidences": [0.9, 0.85, 0.8],
                },
            },
        }
        dashboard.learning_loop.get_learning_metrics.return_value = metrics
        
        snapshot = dashboard.capture_metrics()
        
        assert snapshot.total_learnings == 10
        assert snapshot.total_patterns == 20
        assert "TDDOrchestrator" in snapshot.orchestrators
        assert snapshot.avg_confidence == 0.85
    
    def test_capture_handles_exceptions(self):
        """Dashboard should handle exceptions in capture."""
        dashboard = LearningDashboard()
        dashboard.learning_loop = MagicMock()
        dashboard.learning_loop.get_learning_metrics.side_effect = Exception("Test error")
        
        # Should not raise
        snapshot = dashboard.capture_metrics()
        
        assert snapshot is not None


# =============================================================================
# Test: Orchestrator Statistics
# =============================================================================

class TestOrchestratorStatistics:
    """Tests for orchestrator statistics."""
    
    def test_get_empty_statistics(self):
        """Should return empty dict if no learning loop."""
        dashboard = LearningDashboard()
        dashboard.learning_loop = None
        
        stats = dashboard.get_orchestrator_statistics()
        
        assert stats == {}
    
    def test_get_orchestrator_statistics(self):
        """Should retrieve orchestrator-specific statistics."""
        dashboard = LearningDashboard()
        dashboard.learning_loop = MagicMock()
        
        metrics = {
            "by_orchestrator": {
                "TDDOrchestrator": {
                    "count": 5,
                    "patterns": 10,
                    "avg_confidence": 0.85,
                    "confidences": [0.9, 0.85, 0.8],
                },
                "RefactoringOrchestrator": {
                    "count": 3,
                    "patterns": 6,
                    "avg_confidence": 0.80,
                    "confidences": [0.8, 0.75],
                },
            }
        }
        dashboard.learning_loop.get_learning_metrics.return_value = metrics
        
        stats = dashboard.get_orchestrator_statistics()
        
        assert len(stats) == 2
        assert stats["TDDOrchestrator"]["learnings"] == 5
        assert stats["RefactoringOrchestrator"]["patterns"] == 6


# =============================================================================
# Test: Test Quality Distribution
# =============================================================================

class TestTestQualityDistribution:
    """Tests for test quality distribution."""
    
    def test_get_empty_distribution(self):
        """Should return empty dict if no scorer."""
        dashboard = LearningDashboard()
        dashboard.test_scorer = None
        
        distribution = dashboard.get_test_quality_distribution()
        
        assert distribution == {}
    
    def test_get_test_quality_distribution(self):
        """Should retrieve test quality by tier."""
        dashboard = LearningDashboard()
        dashboard.test_scorer = MagicMock()
        
        summary = {
            "by_tier": {
                "ABSOLUTE": 2,
                "HIGH": 8,
                "MEDIUM": 15,
                "LOW": 5,
            }
        }
        dashboard.test_scorer.get_score_summary.return_value = summary
        
        distribution = dashboard.get_test_quality_distribution()
        
        assert distribution["ABSOLUTE"] == 2
        assert distribution["HIGH"] == 8
        assert distribution["MEDIUM"] == 15


# =============================================================================
# Test: Confidence Distribution
# =============================================================================

class TestConfidenceDistribution:
    """Tests for confidence distribution."""
    
    def test_get_empty_confidence_distribution(self):
        """Should return empty dict if no learning loop."""
        dashboard = LearningDashboard()
        dashboard.learning_loop = None
        
        distribution = dashboard.get_confidence_distribution()
        
        assert distribution == {}
    
    def test_get_confidence_distribution(self):
        """Should bucket confidences into ranges."""
        dashboard = LearningDashboard()
        dashboard.learning_loop = MagicMock()
        
        metrics = {
            "by_orchestrator": {
                "TDDOrchestrator": {
                    "confidences": [0.1, 0.3, 0.6, 0.8, 0.95],
                },
            }
        }
        dashboard.learning_loop.get_learning_metrics.return_value = metrics
        
        distribution = dashboard.get_confidence_distribution()
        
        assert "0.0-0.25" in distribution
        assert "0.25-0.5" in distribution
        assert "0.5-0.75" in distribution
        assert "0.75-0.9" in distribution
        assert "0.9-1.0" in distribution
        
        # Verify bucket counts
        assert distribution["0.0-0.25"] == 1  # 0.1
        assert distribution["0.25-0.5"] == 1  # 0.3
        assert distribution["0.5-0.75"] == 1  # 0.6
        assert distribution["0.75-0.9"] == 1  # 0.8
        assert distribution["0.9-1.0"] == 1   # 0.95


# =============================================================================
# Test: Report Generation
# =============================================================================

class TestReportGeneration:
    """Tests for report generation."""
    
    def test_generate_report_structure(self):
        """Report should have expected structure."""
        dashboard = LearningDashboard()
        dashboard.learning_loop = MagicMock()
        dashboard.test_scorer = MagicMock()
        
        metrics = {
            "total_learnings": 10,
            "total_patterns": 20,
            "success_rate": 0.95,
            "by_orchestrator": {
                "TDDOrchestrator": {
                    "count": 5,
                    "patterns": 10,
                    "avg_confidence": 0.85,
                    "confidences": [],
                }
            }
        }
        dashboard.learning_loop.get_learning_metrics.return_value = metrics
        dashboard.test_scorer.get_score_summary.return_value = {"by_tier": {}}
        
        report = dashboard.generate_report()
        
        assert "timestamp" in report
        assert "summary" in report
        assert "orchestrators" in report
        assert "test_quality" in report
        assert "confidence" in report
    
    def test_generate_ascii_report(self):
        """ASCII report should be readable text."""
        dashboard = LearningDashboard()
        dashboard.learning_loop = MagicMock()
        dashboard.test_scorer = MagicMock()
        
        metrics = {
            "total_learnings": 10,
            "total_patterns": 20,
            "success_rate": 0.95,
            "deduplication_rate": 0.1,
            "by_orchestrator": {
                "TDDOrchestrator": {
                    "count": 5,
                    "patterns": 10,
                    "avg_confidence": 0.85,
                    "confidences": [],
                }
            }
        }
        dashboard.learning_loop.get_learning_metrics.return_value = metrics
        dashboard.test_scorer.get_score_summary.return_value = {
            "by_tier": {"HIGH": 5, "MEDIUM": 3}
        }
        
        ascii_report = dashboard.generate_ascii_report()
        
        assert isinstance(ascii_report, str)
        assert "PHASE 71" in ascii_report
        assert "DASHBOARD" in ascii_report
        assert "SUMMARY" in ascii_report
        assert "Total Learnings" in ascii_report


# =============================================================================
# Test: Metrics History
# =============================================================================

class TestMetricsHistory:
    """Tests for metrics history tracking."""
    
    def test_metrics_history_tracking(self):
        """Dashboard should track historical snapshots."""
        dashboard = LearningDashboard()
        dashboard.learning_loop = MagicMock()
        
        metrics = {
            "total_learnings": 10,
            "total_patterns": 20,
            "by_orchestrator": {
                "TDDOrchestrator": {
                    "avg_confidence": 0.85,
                    "confidences": [],
                }
            }
        }
        dashboard.learning_loop.get_learning_metrics.return_value = metrics
        dashboard.test_scorer = None
        
        # Capture multiple snapshots
        dashboard.capture_metrics()
        dashboard.capture_metrics()
        dashboard.capture_metrics()
        
        history = dashboard.get_metrics_history()
        
        assert len(history) == 3
        assert all(isinstance(s, dict) for s in history)


# =============================================================================
# Test: Singleton
# =============================================================================

class TestSingleton:
    """Tests for singleton getter."""
    
    def test_get_learning_dashboard(self):
        """Getter should return dashboard instance."""
        dashboard = get_learning_dashboard()
        
        assert dashboard is not None
        assert isinstance(dashboard, LearningDashboard)


# =============================================================================
# Test: Integration
# =============================================================================

class TestIntegration:
    """Integration tests."""
    
    def test_full_dashboard_scenario(self):
        """Test complete dashboard scenario."""
        dashboard = LearningDashboard()
        dashboard.learning_loop = MagicMock()
        dashboard.test_scorer = MagicMock()
        
        # Setup comprehensive metrics
        metrics = {
            "total_learnings": 50,
            "total_patterns": 100,
            "success_rate": 0.95,
            "deduplication_rate": 0.15,
            "by_orchestrator": {
                "TDDOrchestrator": {
                    "count": 25,
                    "patterns": 50,
                    "avg_confidence": 0.87,
                    "confidences": [0.85, 0.88, 0.90],
                },
                "RefactoringOrchestrator": {
                    "count": 15,
                    "patterns": 30,
                    "avg_confidence": 0.80,
                    "confidences": [0.75, 0.80, 0.85],
                },
                "InteractionOrchestrator": {
                    "count": 10,
                    "patterns": 20,
                    "avg_confidence": 0.75,
                    "confidences": [0.70, 0.75, 0.80],
                }
            }
        }
        dashboard.learning_loop.get_learning_metrics.return_value = metrics
        dashboard.test_scorer.get_score_summary.return_value = {
            "by_tier": {
                "ABSOLUTE": 5,
                "HIGH": 20,
                "MEDIUM": 30,
                "LOW": 10,
            },
            "high_value_count": 25,
        }
        
        # Generate reports
        report = dashboard.generate_report()
        ascii_report = dashboard.generate_ascii_report()
        
        # Verify report completeness
        assert report["summary"]["total_learnings"] == 50
        assert report["summary"]["avg_confidence"] == pytest.approx(0.80, abs=0.01)
        assert len(report["orchestrators"]) == 3
        
        # Verify ASCII report content
        assert "50" in ascii_report  # Learning count
        assert "TDDOrchestrator" in ascii_report
        assert "RefactoringOrchestrator" in ascii_report

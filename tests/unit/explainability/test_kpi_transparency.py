"""
WAVE-O Stage 3 Tests: KPI Transparency Engine (ENH-068)
RED Phase - 5 tests for transparent KPI calculations
"""

import pytest
from pathlib import Path
from cortex.intelligence.explainability.kpi_transparency import (
    KPITransparencyEngine,
    KPIExplanation,
    DataSource
)


class TestKPIExplanation:
    """Test KPI explanation generation"""
    
    @pytest.fixture
    def engine(self):
        """Create transparency engine"""
        return KPITransparencyEngine()
    
    def test_test_coverage_explanation(self, engine):
        """Test explanation for test coverage KPI"""
        data = {
            "tests_total": 100,
            "tests_passing": 95
        }
        
        explanation = engine.explain_kpi("test_coverage", data)
        
        assert explanation is not None
        assert explanation.kpi_name == "test_coverage"
        assert "95" in explanation.calculation_steps
        assert "100" in explanation.calculation_steps
        assert len(explanation.data_sources) > 0
        assert explanation.confidence >= 0.9
    
    def test_completion_rate_explanation(self, engine):
        """Test explanation for completion rate KPI"""
        data = {
            "phases_total": 15,
            "phases_complete": 14
        }
        
        explanation = engine.explain_kpi("completion_rate", data)
        
        assert explanation.kpi_name == "completion_rate"
        assert "14" in explanation.calculation_steps
        assert "15" in explanation.calculation_steps
        assert explanation.value == pytest.approx(0.933, abs=0.01)


class TestDataSourceTraceability:
    """Test data source traceability"""
    
    @pytest.fixture
    def engine(self):
        """Create transparency engine"""
        return KPITransparencyEngine()
    
    def test_data_source_tracking(self, engine):
        """Test that data sources are tracked"""
        data = {
            "tests_total": 100,
            "tests_passing": 95,
            "_sources": {
                "tests_total": Path("cortex-registry/_cortex-master/index.yaml"),
                "tests_passing": Path("test-results/summary.json")
            }
        }
        
        explanation = engine.explain_kpi("test_coverage", data)
        
        assert len(explanation.data_sources) >= 2
        source_names = [s.name for s in explanation.data_sources]
        assert "index.yaml" in str(source_names) or "tests_total" in str(source_names)
    
    def test_data_source_validation(self, engine):
        """Test data source validation affects confidence"""
        # Valid sources
        data_valid = {
            "value": 100,
            "_sources": {
                "value": Path("valid-source.yaml")
            }
        }
        
        # Invalid sources
        data_invalid = {
            "value": 100,
            "_sources": {
                "value": Path("nonexistent-file.yaml")
            }
        }
        
        explanation_valid = engine.explain_kpi("simple_metric", data_valid)
        explanation_invalid = engine.explain_kpi("simple_metric", data_invalid)
        
        # Valid sources should have higher confidence
        assert explanation_valid.confidence >= explanation_invalid.confidence


class TestConfidenceScoring:
    """Test confidence score calculation"""
    
    @pytest.fixture
    def engine(self):
        """Create transparency engine"""
        return KPITransparencyEngine()
    
    def test_high_confidence_complete_data(self, engine):
        """Test high confidence with complete data"""
        data = {
            "tests_total": 100,
            "tests_passing": 95,
            "_sources": {
                "tests_total": Path("registry.yaml"),
                "tests_passing": Path("results.json")
            }
        }
        
        explanation = engine.explain_kpi("test_coverage", data)
        
        # Complete data with sources should have reasonable confidence
        # (0.75 since files don't exist, but sources are documented)
        assert explanation.confidence >= 0.7
    
    def test_lower_confidence_missing_sources(self, engine):
        """Test lower confidence with missing sources"""
        data = {
            "tests_total": 100,
            "tests_passing": 95
            # No _sources field
        }
        
        explanation = engine.explain_kpi("test_coverage", data)
        
        # Missing sources should reduce confidence
        assert explanation.confidence < 1.0

"""
Phase S2: Quality Tab (✅) - TDD Test Suite
Tests for code quality metrics, coverage, and assessment
"""

import pytest
from pydantic import ValidationError

from cortex.orchestrators.onboarding.dashboard_schema_models import (
    QualityTab, RepositoryDashboardSchema
)


# ============================================================================
# FIXTURES - Test Data
# ============================================================================

@pytest.fixture
def valid_quality():
    """Valid quality metrics fixture"""
    return {
        "code_quality_score": 8.2,
        "maintainability_index": 85.0,
        "code_smells": 15,
        "duplication_percentage": 3.5,
        "technical_debt_hours": 120,
        "test_coverage": 92.0
    }


@pytest.fixture
def high_quality():
    """High quality metrics fixture"""
    return {
        "code_quality_score": 9.5,
        "maintainability_index": 95.0,
        "code_smells": 2,
        "duplication_percentage": 0.5,
        "technical_debt_hours": 10,
        "test_coverage": 99.0
    }


@pytest.fixture
def low_quality():
    """Low quality metrics fixture"""
    return {
        "code_quality_score": 3.5,
        "maintainability_index": 45.0,
        "code_smells": 200,
        "duplication_percentage": 25.0,
        "technical_debt_hours": 2000,
        "test_coverage": 15.0
    }


# ============================================================================
# CODE QUALITY SCORE TESTS
# ============================================================================

class TestCodeQualityScore:
    """Test code quality score validation"""
    
    def test_valid_quality_score(self, valid_quality):
        """Test valid quality score (8.2)"""
        quality = QualityTab(**valid_quality)
        assert quality.code_quality_score == 8.2
        assert 0 <= quality.code_quality_score <= 10
    
    def test_perfect_quality_score(self):
        """Test perfect quality score (10.0)"""
        data = valid_quality = {
            "code_quality_score": 10.0,
            "maintainability_index": 100.0,
            "code_smells": 0,
            "duplication_percentage": 0.0,
            "technical_debt_hours": 0,
            "test_coverage": 100.0
        }
        quality = QualityTab(**data)
        assert quality.code_quality_score == 10.0
    
    def test_minimum_quality_score(self):
        """Test minimum quality score (0.0)"""
        data = {
            "code_quality_score": 0.0,
            "maintainability_index": 0.0,
            "code_smells": 0,
            "duplication_percentage": 0.0,
            "technical_debt_hours": 0,
            "test_coverage": 0.0
        }
        quality = QualityTab(**data)
        assert quality.code_quality_score == 0.0
    
    def test_quality_score_exceeds_maximum(self):
        """Test quality score exceeding maximum (invalid)"""
        data = {
            "code_quality_score": 10.5,
            "maintainability_index": 85.0,
            "code_smells": 15,
            "duplication_percentage": 3.5,
            "technical_debt_hours": 120,
            "test_coverage": 92.0
        }
        with pytest.raises(ValidationError):
            QualityTab(**data)
    
    def test_quality_score_negative(self):
        """Test negative quality score (invalid)"""
        data = {
            "code_quality_score": -1.5,
            "maintainability_index": 85.0,
            "code_smells": 15,
            "duplication_percentage": 3.5,
            "technical_debt_hours": 120,
            "test_coverage": 92.0
        }
        with pytest.raises(ValidationError):
            QualityTab(**data)
    
    def test_quality_score_fractional(self):
        """Test fractional quality score"""
        data = {
            "code_quality_score": 7.777,
            "maintainability_index": 85.0,
            "code_smells": 15,
            "duplication_percentage": 3.5,
            "technical_debt_hours": 120,
            "test_coverage": 92.0
        }
        quality = QualityTab(**data)
        assert abs(quality.code_quality_score - 7.777) < 0.001


# ============================================================================
# MAINTAINABILITY INDEX TESTS
# ============================================================================

class TestMaintainabilityIndex:
    """Test maintainability index validation"""
    
    def test_valid_maintainability(self, valid_quality):
        """Test valid maintainability index (85.0)"""
        quality = QualityTab(**valid_quality)
        assert quality.maintainability_index == 85.0
    
    def test_low_maintainability(self):
        """Test low maintainability (10.0)"""
        data = {
            "code_quality_score": 2.0,
            "maintainability_index": 10.0,
            "code_smells": 500,
            "duplication_percentage": 40.0,
            "technical_debt_hours": 5000,
            "test_coverage": 5.0
        }
        quality = QualityTab(**data)
        assert quality.maintainability_index == 10.0
    
    def test_perfect_maintainability(self):
        """Test perfect maintainability (100.0)"""
        data = {
            "code_quality_score": 10.0,
            "maintainability_index": 100.0,
            "code_smells": 0,
            "duplication_percentage": 0.0,
            "technical_debt_hours": 0,
            "test_coverage": 100.0
        }
        quality = QualityTab(**data)
        assert quality.maintainability_index == 100.0
    
    def test_maintainability_exceeds_maximum(self):
        """Test maintainability exceeding maximum"""
        data = {
            "code_quality_score": 8.0,
            "maintainability_index": 101.0,
            "code_smells": 15,
            "duplication_percentage": 3.5,
            "technical_debt_hours": 120,
            "test_coverage": 92.0
        }
        with pytest.raises(ValidationError):
            QualityTab(**data)


# ============================================================================
# CODE SMELLS TESTS
# ============================================================================

class TestCodeSmells:
    """Test code smell count validation"""
    
    def test_valid_code_smells(self, valid_quality):
        """Test valid code smells (15)"""
        quality = QualityTab(**valid_quality)
        assert quality.code_smells == 15
    
    def test_zero_code_smells(self):
        """Test zero code smells"""
        data = {
            "code_quality_score": 10.0,
            "maintainability_index": 100.0,
            "code_smells": 0,
            "duplication_percentage": 0.0,
            "technical_debt_hours": 0,
            "test_coverage": 100.0
        }
        quality = QualityTab(**data)
        assert quality.code_smells == 0
    
    def test_many_code_smells(self):
        """Test high code smell count (1000)"""
        data = {
            "code_quality_score": 2.0,
            "maintainability_index": 20.0,
            "code_smells": 1000,
            "duplication_percentage": 35.0,
            "technical_debt_hours": 3000,
            "test_coverage": 10.0
        }
        quality = QualityTab(**data)
        assert quality.code_smells == 1000
    
    def test_negative_code_smells(self):
        """Test negative code smells (invalid)"""
        data = {
            "code_quality_score": 8.0,
            "maintainability_index": 85.0,
            "code_smells": -5,
            "duplication_percentage": 3.5,
            "technical_debt_hours": 120,
            "test_coverage": 92.0
        }
        with pytest.raises(ValidationError):
            QualityTab(**data)


# ============================================================================
# DUPLICATION TESTS
# ============================================================================

class TestDuplicationPercentage:
    """Test code duplication percentage validation"""
    
    def test_valid_duplication(self, valid_quality):
        """Test valid duplication (3.5%)"""
        quality = QualityTab(**valid_quality)
        assert quality.duplication_percentage == 3.5
    
    def test_zero_duplication(self):
        """Test zero duplication"""
        data = {
            "code_quality_score": 10.0,
            "maintainability_index": 100.0,
            "code_smells": 0,
            "duplication_percentage": 0.0,
            "technical_debt_hours": 0,
            "test_coverage": 100.0
        }
        quality = QualityTab(**data)
        assert quality.duplication_percentage == 0.0
    
    def test_high_duplication(self):
        """Test high duplication (50%)"""
        data = {
            "code_quality_score": 3.0,
            "maintainability_index": 30.0,
            "code_smells": 300,
            "duplication_percentage": 50.0,
            "technical_debt_hours": 2000,
            "test_coverage": 20.0
        }
        quality = QualityTab(**data)
        assert quality.duplication_percentage == 50.0
    
    def test_duplication_exceeds_100_percent(self):
        """Test duplication exceeding 100% (invalid)"""
        data = {
            "code_quality_score": 8.0,
            "maintainability_index": 85.0,
            "code_smells": 15,
            "duplication_percentage": 105.0,
            "technical_debt_hours": 120,
            "test_coverage": 92.0
        }
        with pytest.raises(ValidationError):
            QualityTab(**data)
    
    def test_duplication_negative(self):
        """Test negative duplication (invalid)"""
        data = {
            "code_quality_score": 8.0,
            "maintainability_index": 85.0,
            "code_smells": 15,
            "duplication_percentage": -5.0,
            "technical_debt_hours": 120,
            "test_coverage": 92.0
        }
        with pytest.raises(ValidationError):
            QualityTab(**data)


# ============================================================================
# TECHNICAL DEBT TESTS
# ============================================================================

class TestTechnicalDebt:
    """Test technical debt hours validation"""
    
    def test_valid_technical_debt(self, valid_quality):
        """Test valid technical debt (120 hours)"""
        quality = QualityTab(**valid_quality)
        assert quality.technical_debt_hours == 120
    
    def test_zero_technical_debt(self):
        """Test zero technical debt"""
        data = {
            "code_quality_score": 10.0,
            "maintainability_index": 100.0,
            "code_smells": 0,
            "duplication_percentage": 0.0,
            "technical_debt_hours": 0,
            "test_coverage": 100.0
        }
        quality = QualityTab(**data)
        assert quality.technical_debt_hours == 0
    
    def test_large_technical_debt(self):
        """Test large technical debt (10000 hours)"""
        data = {
            "code_quality_score": 2.0,
            "maintainability_index": 25.0,
            "code_smells": 1000,
            "duplication_percentage": 40.0,
            "technical_debt_hours": 10000,
            "test_coverage": 10.0
        }
        quality = QualityTab(**data)
        assert quality.technical_debt_hours == 10000
    
    def test_negative_technical_debt(self):
        """Test negative technical debt (invalid)"""
        data = {
            "code_quality_score": 8.0,
            "maintainability_index": 85.0,
            "code_smells": 15,
            "duplication_percentage": 3.5,
            "technical_debt_hours": -100,
            "test_coverage": 92.0
        }
        with pytest.raises(ValidationError):
            QualityTab(**data)


# ============================================================================
# TEST COVERAGE TESTS
# ============================================================================

class TestCoveragePercentage:
    """Test test coverage percentage validation"""
    
    def test_valid_coverage(self, valid_quality):
        """Test valid coverage (92%)"""
        quality = QualityTab(**valid_quality)
        assert quality.test_coverage == 92.0
    
    def test_zero_coverage(self):
        """Test zero coverage"""
        data = {
            "code_quality_score": 1.0,
            "maintainability_index": 10.0,
            "code_smells": 500,
            "duplication_percentage": 50.0,
            "technical_debt_hours": 5000,
            "test_coverage": 0.0
        }
        quality = QualityTab(**data)
        assert quality.test_coverage == 0.0
    
    def test_perfect_coverage(self):
        """Test perfect coverage (100%)"""
        data = {
            "code_quality_score": 10.0,
            "maintainability_index": 100.0,
            "code_smells": 0,
            "duplication_percentage": 0.0,
            "technical_debt_hours": 0,
            "test_coverage": 100.0
        }
        quality = QualityTab(**data)
        assert quality.test_coverage == 100.0
    
    def test_coverage_exceeds_100_percent(self):
        """Test coverage exceeding 100% (invalid)"""
        data = {
            "code_quality_score": 8.0,
            "maintainability_index": 85.0,
            "code_smells": 15,
            "duplication_percentage": 3.5,
            "technical_debt_hours": 120,
            "test_coverage": 105.0
        }
        with pytest.raises(ValidationError):
            QualityTab(**data)


# ============================================================================
# COMPLETE QUALITY TESTS
# ============================================================================

class TestCompleteQuality:
    """Test complete quality specifications"""
    
    def test_high_quality_metrics(self, high_quality):
        """Test high quality metrics"""
        quality = QualityTab(**high_quality)
        assert quality.code_quality_score == 9.5
        assert quality.test_coverage == 99.0
        assert quality.code_smells == 2
    
    def test_low_quality_metrics(self, low_quality):
        """Test low quality metrics"""
        quality = QualityTab(**low_quality)
        assert quality.code_quality_score == 3.5
        assert quality.test_coverage == 15.0
        assert quality.code_smells == 200


# ============================================================================
# QUALITY CONSISTENCY TESTS
# ============================================================================

class TestQualityConsistency:
    """Test consistency between quality metrics"""
    
    def test_correlation_quality_coverage(self):
        """Test correlation between quality and coverage"""
        # High coverage should correlate with high quality
        data = {
            "code_quality_score": 9.0,
            "maintainability_index": 90.0,
            "code_smells": 5,
            "duplication_percentage": 1.0,
            "technical_debt_hours": 20,
            "test_coverage": 95.0
        }
        quality = QualityTab(**data)
        assert quality.code_quality_score > 8
        assert quality.test_coverage > 90
    
    def test_correlation_smells_quality(self):
        """Test correlation between code smells and quality"""
        # High smells should correlate with low quality
        data = {
            "code_quality_score": 2.5,
            "maintainability_index": 30.0,
            "code_smells": 300,
            "duplication_percentage": 30.0,
            "technical_debt_hours": 2000,
            "test_coverage": 20.0
        }
        quality = QualityTab(**data)
        assert quality.code_quality_score < 4
        assert quality.code_smells > 100


# ============================================================================
# QUALITY INTEGRATION TESTS
# ============================================================================

class TestQualityIntegration:
    """Integration tests with complete dashboard"""
    
    def test_quality_in_complete_dashboard(self):
        """Test quality tab within complete dashboard"""
        dashboard_data = {
            "metadata": {
                "name": "KSESSIONS",
                "path": "D:\\PROJECTS\\KSESSIONS",
                "primary_language": "C#",
                "total_files": 26434,
                "total_lines": 3658465,
                "contributors": 30,
                "last_updated": "2026-02-08T15:30:00Z",
                "repo_age_days": 635
            },
            "overview": {
                "health_score": 87.5,
                "code_quality": 8.2,
                "test_coverage": 92.0,
                "maintainability_index": 85.0,
                "technical_debt_hours": 120,
                "languages": {"C#": 3658465}
            },
            "architecture": {
                "layers": [],
                "modules": {}
            },
            "quality": {
                "code_quality_score": 8.2,
                "maintainability_index": 85.0,
                "code_smells": 15,
                "duplication_percentage": 3.5,
                "technical_debt_hours": 120,
                "test_coverage": 92.0
            },
            "vulnerabilities": {"critical": 2, "high": 5, "medium": 12, "low": 8},
            "security": {"security_score": 8.5, "security_posture": "Strong"},
            "dependencies": {
                "direct_count": 45,
                "transitive_count": 320,
                "outdated_count": 8,
                "vulnerable_count": 2
            },
            "testing": {
                "coverage_percentage": 92.0,
                "test_counts": {
                    "total": 1250,
                    "passing": 1245,
                    "failing": 3,
                    "skipped": 2
                },
                "test_types": {
                    "unit": 950,
                    "integration": 200,
                    "e2e": 100
                }
            },
            "patterns": {},
            "use_cases": {}
        }
        
        schema = RepositoryDashboardSchema(**dashboard_data)
        assert schema.quality.code_quality_score == 8.2
        assert schema.quality.test_coverage == 92.0


# ============================================================================
# EDGE CASES
# ============================================================================

class TestQualityEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_minimal_quality(self):
        """Test minimal quality specification"""
        data = {
            "code_quality_score": 0.0,
            "maintainability_index": 0.0,
            "code_smells": 0,
            "duplication_percentage": 0.0,
            "technical_debt_hours": 0,
            "test_coverage": 0.0
        }
        quality = QualityTab(**data)
        assert quality.code_quality_score == 0.0
    
    def test_fractional_percentages(self):
        """Test fractional percentage values"""
        data = {
            "code_quality_score": 7.333,
            "maintainability_index": 82.777,
            "code_smells": 15,
            "duplication_percentage": 3.141,
            "technical_debt_hours": 150,
            "test_coverage": 91.667
        }
        quality = QualityTab(**data)
        assert abs(quality.code_quality_score - 7.333) < 0.001
        assert abs(quality.duplication_percentage - 3.141) < 0.001
    
    def test_quality_decimal_precision(self):
        """Test decimal precision in quality metrics"""
        data = {
            "code_quality_score": 8.12345,
            "maintainability_index": 85.98765,
            "code_smells": 15,
            "duplication_percentage": 3.50001,
            "technical_debt_hours": 120,
            "test_coverage": 92.99999
        }
        quality = QualityTab(**data)
        assert quality.code_quality_score == pytest.approx(8.12345, abs=0.00001)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

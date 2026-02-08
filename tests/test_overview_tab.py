"""
Phase S2: Overview Tab (📊) - TDD Test Suite
Tests for health dashboard with metrics, scoring, and audience personas
"""

import pytest
from datetime import datetime
from typing import Dict, Any
from pydantic import ValidationError

from cortex.orchestrators.onboarding.dashboard_schema_models import (
    OverviewTab, AudienceCard, RepositoryMetadata, RepositoryDashboardSchema,
    Persona, ProgrammingLanguage, validate_dashboard_data
)


# ============================================================================
# FIXTURES - Test Data
# ============================================================================

@pytest.fixture
def valid_metadata():
    """Valid metadata fixture for overview tests"""
    return {
        "name": "KSESSIONS",
        "path": "D:\\PROJECTS\\KSESSIONS",
        "primary_language": "C#",
        "total_files": 26434,
        "total_lines": 3658465,
        "contributors": 30,
        "last_updated": "2026-02-08T15:30:00Z",
        "repo_age_days": 635
    }


@pytest.fixture
def valid_overview_data():
    """Valid overview tab data fixture"""
    return {
        "health_score": 87.5,
        "code_quality": 8.2,
        "test_coverage": 92.0,
        "maintainability_index": 85.0,
        "technical_debt_hours": 120,
        "languages": {
            "C#": 2500000,
            "JavaScript": 450000,
            "SQL": 708465
        }
    }


@pytest.fixture
def overview_with_audiences():
    """Overview with audience personas fixture"""
    return {
        "health_score": 87.5,
        "code_quality": 8.2,
        "test_coverage": 92.0,
        "maintainability_index": 85.0,
        "technical_debt_hours": 120,
        "languages": {
            "C#": 2500000,
            "JavaScript": 450000
        },
        "audiences": [
            {
                "persona": "Executive",
                "icon": "👔",
                "description": "C-level stakeholders"
            },
            {
                "persona": "Product Owner",
                "icon": "📋",
                "description": "Product managers and owners"
            },
            {
                "persona": "Engineer",
                "icon": "👨‍💻",
                "description": "Development team members"
            }
        ]
    }


@pytest.fixture
def complete_dashboard_minimal():
    """Minimal but complete dashboard data"""
    return {
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
            "languages": {"C#": 2500000}
        },
        "architecture": {},
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


# ============================================================================
# HEALTH SCORE TESTS
# ============================================================================

class TestHealthScore:
    """Test health score calculation and validation"""
    
    def test_valid_health_score(self, valid_overview_data):
        """Test valid health score (87.5)"""
        overview = OverviewTab(**valid_overview_data)
        assert overview.health_score == 87.5
        assert 0 <= overview.health_score <= 100
    
    def test_health_score_minimum(self):
        """Test health score at minimum (0)"""
        data = {
            "health_score": 0,
            "code_quality": 0,
            "test_coverage": 0,
            "maintainability_index": 0,
            "technical_debt_hours": 0,
            "languages": {}
        }
        overview = OverviewTab(**data)
        assert overview.health_score == 0
    
    def test_health_score_maximum(self):
        """Test health score at maximum (100)"""
        data = {
            "health_score": 100,
            "code_quality": 10,
            "test_coverage": 100,
            "maintainability_index": 100,
            "technical_debt_hours": 0,
            "languages": {}
        }
        overview = OverviewTab(**data)
        assert overview.health_score == 100
    
    def test_health_score_below_minimum(self):
        """Test health score below minimum (negative)"""
        data = {
            "health_score": -5,
            "code_quality": 8.2,
            "test_coverage": 92.0,
            "maintainability_index": 85.0,
            "technical_debt_hours": 120,
            "languages": {}
        }
        with pytest.raises(ValidationError):
            OverviewTab(**data)
    
    def test_health_score_above_maximum(self):
        """Test health score above maximum (101)"""
        data = {
            "health_score": 101,
            "code_quality": 8.2,
            "test_coverage": 92.0,
            "maintainability_index": 85.0,
            "technical_debt_hours": 120,
            "languages": {}
        }
        with pytest.raises(ValidationError):
            OverviewTab(**data)
    
    def test_health_score_fractional(self):
        """Test health score with fractional value"""
        data = {
            "health_score": 75.5,
            "code_quality": 7.5,
            "test_coverage": 80.0,
            "maintainability_index": 78.0,
            "technical_debt_hours": 150,
            "languages": {}
        }
        overview = OverviewTab(**data)
        assert overview.health_score == 75.5


# ============================================================================
# CODE QUALITY METRIC TESTS
# ============================================================================

class TestCodeQualityMetrics:
    """Test code quality metrics validation"""
    
    def test_code_quality_score(self, valid_overview_data):
        """Test code quality score (8.2/10)"""
        overview = OverviewTab(**valid_overview_data)
        assert overview.code_quality == 8.2
        assert 0 <= overview.code_quality <= 10
    
    def test_code_quality_perfect(self):
        """Test perfect code quality (10.0)"""
        data = {
            "health_score": 100,
            "code_quality": 10.0,
            "test_coverage": 100,
            "maintainability_index": 100,
            "technical_debt_hours": 0,
            "languages": {}
        }
        overview = OverviewTab(**data)
        assert overview.code_quality == 10.0
    
    def test_code_quality_poor(self):
        """Test poor code quality (1.0)"""
        data = {
            "health_score": 20,
            "code_quality": 1.0,
            "test_coverage": 10,
            "maintainability_index": 20,
            "technical_debt_hours": 1000,
            "languages": {}
        }
        overview = OverviewTab(**data)
        assert overview.code_quality == 1.0
    
    def test_code_quality_exceeds_maximum(self):
        """Test code quality exceeding maximum (10.5)"""
        data = {
            "health_score": 87.5,
            "code_quality": 10.5,
            "test_coverage": 92.0,
            "maintainability_index": 85.0,
            "technical_debt_hours": 120,
            "languages": {}
        }
        with pytest.raises(ValidationError):
            OverviewTab(**data)


# ============================================================================
# TEST COVERAGE METRIC TESTS
# ============================================================================

class TestCoverageMetrics:
    """Test coverage percentage validation"""
    
    def test_test_coverage_high(self, valid_overview_data):
        """Test high code coverage (92%)"""
        overview = OverviewTab(**valid_overview_data)
        assert overview.test_coverage == 92.0
        assert 0 <= overview.test_coverage <= 100
    
    def test_test_coverage_zero(self):
        """Test zero coverage (0%)"""
        data = {
            "health_score": 30,
            "code_quality": 2.0,
            "test_coverage": 0.0,
            "maintainability_index": 30,
            "technical_debt_hours": 500,
            "languages": {}
        }
        overview = OverviewTab(**data)
        assert overview.test_coverage == 0.0
    
    def test_test_coverage_full(self):
        """Test full coverage (100%)"""
        data = {
            "health_score": 95,
            "code_quality": 9.5,
            "test_coverage": 100.0,
            "maintainability_index": 95,
            "technical_debt_hours": 50,
            "languages": {}
        }
        overview = OverviewTab(**data)
        assert overview.test_coverage == 100.0
    
    def test_test_coverage_exceeds_maximum(self):
        """Test coverage exceeding maximum (101%)"""
        data = {
            "health_score": 87.5,
            "code_quality": 8.2,
            "test_coverage": 101.0,
            "maintainability_index": 85.0,
            "technical_debt_hours": 120,
            "languages": {}
        }
        with pytest.raises(ValidationError):
            OverviewTab(**data)


# ============================================================================
# MAINTAINABILITY INDEX TESTS
# ============================================================================

class TestMaintainabilityIndex:
    """Test maintainability index validation"""
    
    def test_maintainability_valid(self, valid_overview_data):
        """Test valid maintainability index (85.0)"""
        overview = OverviewTab(**valid_overview_data)
        assert overview.maintainability_index == 85.0
        assert 0 <= overview.maintainability_index <= 100
    
    def test_maintainability_low(self):
        """Test low maintainability (25.0)"""
        data = {
            "health_score": 35,
            "code_quality": 3.0,
            "test_coverage": 40,
            "maintainability_index": 25.0,
            "technical_debt_hours": 400,
            "languages": {}
        }
        overview = OverviewTab(**data)
        assert overview.maintainability_index == 25.0
    
    def test_maintainability_high(self):
        """Test high maintainability (95.0)"""
        data = {
            "health_score": 95,
            "code_quality": 9.5,
            "test_coverage": 95,
            "maintainability_index": 95.0,
            "technical_debt_hours": 40,
            "languages": {}
        }
        overview = OverviewTab(**data)
        assert overview.maintainability_index == 95.0


# ============================================================================
# TECHNICAL DEBT TESTS
# ============================================================================

class TestTechnicalDebt:
    """Test technical debt hours validation"""
    
    def test_technical_debt_positive(self, valid_overview_data):
        """Test positive technical debt (120 hours)"""
        overview = OverviewTab(**valid_overview_data)
        assert overview.technical_debt_hours == 120
        assert overview.technical_debt_hours >= 0
    
    def test_technical_debt_zero(self):
        """Test zero technical debt"""
        data = {
            "health_score": 100,
            "code_quality": 10,
            "test_coverage": 100,
            "maintainability_index": 100,
            "technical_debt_hours": 0,
            "languages": {}
        }
        overview = OverviewTab(**data)
        assert overview.technical_debt_hours == 0
    
    def test_technical_debt_large(self):
        """Test large technical debt (5000 hours)"""
        data = {
            "health_score": 20,
            "code_quality": 1.0,
            "test_coverage": 5,
            "maintainability_index": 20,
            "technical_debt_hours": 5000,
            "languages": {}
        }
        overview = OverviewTab(**data)
        assert overview.technical_debt_hours == 5000
    
    def test_technical_debt_negative(self):
        """Test negative technical debt (invalid)"""
        data = {
            "health_score": 87.5,
            "code_quality": 8.2,
            "test_coverage": 92.0,
            "maintainability_index": 85.0,
            "technical_debt_hours": -50,
            "languages": {}
        }
        with pytest.raises(ValidationError):
            OverviewTab(**data)


# ============================================================================
# LANGUAGE DISTRIBUTION TESTS
# ============================================================================

class TestLanguageDistribution:
    """Test programming language distribution"""
    
    def test_single_language(self):
        """Test single programming language"""
        data = {
            "health_score": 87.5,
            "code_quality": 8.2,
            "test_coverage": 92.0,
            "maintainability_index": 85.0,
            "technical_debt_hours": 120,
            "languages": {"C#": 3658465}
        }
        overview = OverviewTab(**data)
        assert len(overview.languages) == 1
        assert overview.languages["C#"] == 3658465
    
    def test_multiple_languages(self, valid_overview_data):
        """Test multiple programming languages"""
        overview = OverviewTab(**valid_overview_data)
        assert len(overview.languages) == 3
        assert overview.languages["C#"] == 2500000
        assert overview.languages["JavaScript"] == 450000
        assert overview.languages["SQL"] == 708465
    
    def test_language_total_calculation(self, valid_overview_data):
        """Test total lines calculation from languages"""
        overview = OverviewTab(**valid_overview_data)
        total_lines = sum(overview.languages.values())
        assert total_lines == 3658465
    
    def test_empty_languages(self):
        """Test with empty languages dictionary"""
        data = {
            "health_score": 87.5,
            "code_quality": 8.2,
            "test_coverage": 92.0,
            "maintainability_index": 85.0,
            "technical_debt_hours": 120,
            "languages": {}
        }
        overview = OverviewTab(**data)
        assert len(overview.languages) == 0
    
    def test_language_zero_lines(self):
        """Test language with zero lines"""
        data = {
            "health_score": 87.5,
            "code_quality": 8.2,
            "test_coverage": 92.0,
            "maintainability_index": 85.0,
            "technical_debt_hours": 120,
            "languages": {"C#": 0}
        }
        overview = OverviewTab(**data)
        assert overview.languages["C#"] == 0
    
    def test_language_percentage_distribution(self, valid_overview_data):
        """Test language percentage distribution"""
        overview = OverviewTab(**valid_overview_data)
        total = sum(overview.languages.values())
        percentages = {
            lang: (lines / total * 100) 
            for lang, lines in overview.languages.items()
        }
        
        # C# should be ~68%, JavaScript ~12%, SQL ~19%
        assert 68 < percentages["C#"] < 69
        assert 12 < percentages["JavaScript"] < 13
        assert 19 < percentages["SQL"] < 20


# ============================================================================
# AUDIENCE PERSONAS TESTS
# ============================================================================

class TestAudiencePersonas:
    """Test audience persona configuration"""
    
    def test_no_audiences(self, valid_overview_data):
        """Test overview without audiences"""
        overview = OverviewTab(**valid_overview_data)
        assert overview.audiences is None
    
    def test_single_audience(self):
        """Test single audience persona"""
        data = {
            "health_score": 87.5,
            "code_quality": 8.2,
            "test_coverage": 92.0,
            "maintainability_index": 85.0,
            "technical_debt_hours": 120,
            "languages": {},
            "audiences": [
                {
                    "persona": "Executive",
                    "icon": "👔",
                    "description": "C-level stakeholders"
                }
            ]
        }
        overview = OverviewTab(**data)
        assert len(overview.audiences) == 1
        assert overview.audiences[0].persona == "Executive"
    
    def test_multiple_audiences(self, overview_with_audiences):
        """Test multiple audience personas"""
        overview = OverviewTab(**overview_with_audiences)
        assert len(overview.audiences) == 3
        
        personas = [aud.persona for aud in overview.audiences]
        assert "Executive" in personas
        assert "Product Owner" in personas
        assert "Engineer" in personas
    
    def test_audience_persona_enum(self):
        """Test audience persona enum values"""
        data = {
            "health_score": 87.5,
            "code_quality": 8.2,
            "test_coverage": 92.0,
            "maintainability_index": 85.0,
            "technical_debt_hours": 120,
            "languages": {},
            "audiences": [
                {
                    "persona": "Leader",
                    "icon": "🎯",
                    "description": "Team leads and managers"
                }
            ]
        }
        overview = OverviewTab(**data)
        assert overview.audiences[0].persona == "Leader"
    
    def test_audience_icon_unicode(self):
        """Test audience icons with unicode emojis"""
        data = {
            "health_score": 87.5,
            "code_quality": 8.2,
            "test_coverage": 92.0,
            "maintainability_index": 85.0,
            "technical_debt_hours": 120,
            "languages": {},
            "audiences": [
                {"persona": "Engineer", "icon": "👨‍💻", "description": "Development engineers"},
                {"persona": "Dev Manager", "icon": "🏛️", "description": "Development managers"},
                {"persona": "Leader", "icon": "⚙️", "description": "Technical leaders"}
            ]
        }
        overview = OverviewTab(**data)
        assert len(overview.audiences) == 3
        assert "👨‍💻" in [aud.icon for aud in overview.audiences]
    
    def test_audience_description_length(self):
        """Test audience description with varying lengths"""
        data = {
            "health_score": 87.5,
            "code_quality": 8.2,
            "test_coverage": 92.0,
            "maintainability_index": 85.0,
            "technical_debt_hours": 120,
            "languages": {},
            "audiences": [
                {
                    "persona": "Executive",
                    "icon": "👔",
                    "description": "C-level executives and stakeholders responsible for strategic decisions and ROI tracking"
                }
            ]
        }
        overview = OverviewTab(**data)
        assert len(overview.audiences[0].description) > 50


# ============================================================================
# INTEGRATION TESTS - OVERVIEW TAB WITH DASHBOARD
# ============================================================================

class TestOverviewTabIntegration:
    """Integration tests with complete dashboard schema"""
    
    def test_overview_in_complete_dashboard(self, complete_dashboard_minimal):
        """Test overview tab within complete dashboard"""
        schema = RepositoryDashboardSchema(**complete_dashboard_minimal)
        
        assert schema.overview.health_score == 87.5
        assert schema.overview.code_quality == 8.2
        assert schema.overview.test_coverage == 92.0
        assert len(schema.overview.languages) == 1
    
    def test_overview_metrics_consistency(self, complete_dashboard_minimal):
        """Test consistency between overview and quality metrics"""
        schema = RepositoryDashboardSchema(**complete_dashboard_minimal)
        
        # Verify consistency: overview score should relate to quality score
        assert schema.overview.code_quality == schema.quality.code_quality_score
        assert schema.overview.test_coverage == schema.quality.test_coverage
        assert schema.overview.maintainability_index == schema.quality.maintainability_index
    
    def test_overview_with_high_health(self, complete_dashboard_minimal):
        """Test overview with high health score (90+)"""
        complete_dashboard_minimal["overview"]["health_score"] = 95.5
        schema = RepositoryDashboardSchema(**complete_dashboard_minimal)
        
        assert schema.overview.health_score >= 90
        assert schema.overview.test_coverage >= 85
    
    def test_overview_with_low_health(self, complete_dashboard_minimal):
        """Test overview with low health score (<30)"""
        complete_dashboard_minimal["overview"]["health_score"] = 25.0
        complete_dashboard_minimal["overview"]["code_quality"] = 2.0
        complete_dashboard_minimal["overview"]["test_coverage"] = 20.0
        
        schema = RepositoryDashboardSchema(**complete_dashboard_minimal)
        assert schema.overview.health_score < 30
        assert schema.overview.code_quality < 3


# ============================================================================
# EDGE CASES & BOUNDARY TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_all_zeros(self):
        """Test overview with all zero metrics"""
        data = {
            "health_score": 0,
            "code_quality": 0,
            "test_coverage": 0,
            "maintainability_index": 0,
            "technical_debt_hours": 0,
            "languages": {}
        }
        overview = OverviewTab(**data)
        assert overview.health_score == 0
        assert overview.code_quality == 0
    
    def test_all_maximums(self):
        """Test overview with all maximum metrics"""
        data = {
            "health_score": 100,
            "code_quality": 10,
            "test_coverage": 100,
            "maintainability_index": 100,
            "technical_debt_hours": 0,
            "languages": {"C#": 10000000}
        }
        overview = OverviewTab(**data)
        assert overview.health_score == 100
        assert overview.code_quality == 10
        assert overview.test_coverage == 100
    
    def test_mixed_precision(self):
        """Test overview with mixed precision values"""
        data = {
            "health_score": 87.5,
            "code_quality": 8.2,
            "test_coverage": 92.333,
            "maintainability_index": 85.7,
            "technical_debt_hours": 120,
            "languages": {"C#": 2500000}
        }
        overview = OverviewTab(**data)
        assert overview.health_score == 87.5
        assert overview.test_coverage == 92.333
    
    def test_large_language_count(self):
        """Test overview with many languages"""
        languages = {
            f"Language_{i}": 100000 * i
            for i in range(1, 21)  # 20 languages
        }
        data = {
            "health_score": 87.5,
            "code_quality": 8.2,
            "test_coverage": 92.0,
            "maintainability_index": 85.0,
            "technical_debt_hours": 120,
            "languages": languages
        }
        overview = OverviewTab(**data)
        assert len(overview.languages) == 20


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '-x'])

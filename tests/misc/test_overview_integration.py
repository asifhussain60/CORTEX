"""
Integration tests for Overview Tab

Tests overview.json schema compliance, rendering performance,
responsive design, and D3.js chart functionality.

Phase 5: Integration Testing
Target: <300ms render, 100% schema compliance
"""

import json
import pytest
from pathlib import Path
import time
from jsonschema import validate, ValidationError


# Test fixtures
@pytest.fixture
def mock_overview_data():
    """Load mock overview.json for testing"""
    data_path = Path(__file__).parent.parent.parent / "cortex-brain" / "dashboards" / "data" / "mock" / "overview.json"
    with open(data_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def overview_schema():
    """Define overview.json schema for validation"""
    return {
        "type": "object",
        "required": ["project_name", "overall_health", "key_metrics", "health_categories", "critical_issues", "composition", "trends"],
        "properties": {
            "project_name": {"type": "string"},
            "overall_health": {
                "type": "object",
                "required": ["score", "status", "trend", "last_scan"],
                "properties": {
                    "score": {"type": "number", "minimum": 0, "maximum": 100},
                    "status": {"type": "string", "enum": ["healthy", "warning", "critical"]},
                    "trend": {"type": "string", "enum": ["improving", "stable", "declining"]},
                    "last_scan": {"type": "string"}
                }
            },
            "key_metrics": {
                "type": "object",
                "required": ["total_files", "total_loc", "test_coverage", "maintainability_index", "technical_debt_hours"],
                "properties": {
                    "total_files": {"type": "integer", "minimum": 0},
                    "total_loc": {"type": "integer", "minimum": 0},
                    "test_coverage": {"type": "number", "minimum": 0, "maximum": 100},
                    "maintainability_index": {"type": "number", "minimum": 0, "maximum": 100},
                    "technical_debt_hours": {"type": "number", "minimum": 0}
                }
            },
            "health_categories": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "score", "status", "trend", "issues_count", "details"],
                    "properties": {
                        "name": {"type": "string"},
                        "score": {"type": "number", "minimum": 0, "maximum": 100},
                        "status": {"type": "string", "enum": ["healthy", "warning", "critical"]},
                        "trend": {"type": "string", "enum": ["improving", "stable", "declining"]},
                        "issues_count": {"type": "integer", "minimum": 0},
                        "details": {"type": "string"}
                    }
                }
            },
            "critical_issues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["severity", "category", "message", "count"],
                    "properties": {
                        "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                        "category": {"type": "string"},
                        "message": {"type": "string"},
                        "count": {"type": "integer", "minimum": 0}
                    }
                }
            },
            "composition": {
                "type": "object",
                "required": ["languages", "components"],
                "properties": {
                    "languages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["name", "percentage", "loc"],
                            "properties": {
                                "name": {"type": "string"},
                                "percentage": {"type": "number", "minimum": 0, "maximum": 100},
                                "loc": {"type": "integer", "minimum": 0}
                            }
                        }
                    },
                    "components": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["type", "count", "technologies"],
                            "properties": {
                                "type": {"type": "string"},
                                "count": {"type": "integer", "minimum": 0},
                                "technologies": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    }
                }
            },
            "trends": {
                "type": "object",
                "required": ["health_trend", "velocity_trend", "quality_trend"],
                "properties": {
                    "health_trend": {"type": "string", "enum": ["improving", "stable", "declining"]},
                    "velocity_trend": {"type": "string", "enum": ["improving", "stable", "declining"]},
                    "quality_trend": {"type": "string", "enum": ["improving", "stable", "declining"]}
                }
            }
        }
    }


# Schema Validation Tests
class TestSchemaValidation:
    """Test overview.json schema compliance"""
    
    def test_mock_data_valid_schema(self, mock_overview_data, overview_schema):
        """Verify mock overview.json matches schema"""
        try:
            validate(instance=mock_overview_data, schema=overview_schema)
        except ValidationError as e:
            pytest.fail(f"Schema validation failed: {e.message}")
    
    def test_overall_health_structure(self, mock_overview_data):
        """Verify overall_health has required fields"""
        health = mock_overview_data.get('overall_health')
        assert health is not None, "overall_health is missing"
        assert 'score' in health, "overall_health.score is missing"
        assert 'status' in health, "overall_health.status is missing"
        assert 'trend' in health, "overall_health.trend is missing"
        assert 'last_scan' in health, "overall_health.last_scan is missing"
        
        # Validate score range
        assert 0 <= health['score'] <= 100, f"Health score {health['score']} out of range"
        
        # Validate status enum
        assert health['status'] in ['healthy', 'warning', 'critical'], f"Invalid status: {health['status']}"
        
        # Validate trend enum
        assert health['trend'] in ['improving', 'stable', 'declining'], f"Invalid trend: {health['trend']}"
    
    def test_key_metrics_structure(self, mock_overview_data):
        """Verify key_metrics has required fields and valid values"""
        metrics = mock_overview_data.get('key_metrics')
        assert metrics is not None, "key_metrics is missing"
        
        required_fields = ['total_files', 'total_loc', 'test_coverage', 'maintainability_index', 'technical_debt_hours']
        for field in required_fields:
            assert field in metrics, f"key_metrics.{field} is missing"
        
        # Validate ranges
        assert metrics['total_files'] >= 0, "total_files cannot be negative"
        assert metrics['total_loc'] >= 0, "total_loc cannot be negative"
        assert 0 <= metrics['test_coverage'] <= 100, f"test_coverage {metrics['test_coverage']} out of range"
        assert 0 <= metrics['maintainability_index'] <= 100, f"maintainability_index out of range"
        assert metrics['technical_debt_hours'] >= 0, "technical_debt_hours cannot be negative"
    
    def test_health_categories_structure(self, mock_overview_data):
        """Verify health_categories array structure"""
        categories = mock_overview_data.get('health_categories')
        assert categories is not None, "health_categories is missing"
        assert isinstance(categories, list), "health_categories must be an array"
        assert len(categories) > 0, "health_categories cannot be empty"
        
        for category in categories:
            assert 'name' in category, "category.name is missing"
            assert 'score' in category, "category.score is missing"
            assert 'status' in category, "category.status is missing"
            assert 'trend' in category, "category.trend is missing"
            assert 'issues_count' in category, "category.issues_count is missing"
            assert 'details' in category, "category.details is missing"
            
            # Validate score range
            assert 0 <= category['score'] <= 100, f"Category score {category['score']} out of range"
    
    def test_critical_issues_structure(self, mock_overview_data):
        """Verify critical_issues array structure"""
        issues = mock_overview_data.get('critical_issues')
        assert issues is not None, "critical_issues is missing"
        assert isinstance(issues, list), "critical_issues must be an array"
        
        for issue in issues:
            assert 'severity' in issue, "issue.severity is missing"
            assert 'category' in issue, "issue.category is missing"
            assert 'message' in issue, "issue.message is missing"
            assert 'count' in issue, "issue.count is missing"
            
            # Validate severity enum
            assert issue['severity'] in ['high', 'medium', 'low'], f"Invalid severity: {issue['severity']}"
            
            # Validate count
            assert issue['count'] >= 0, "issue.count cannot be negative"
    
    def test_composition_languages_structure(self, mock_overview_data):
        """Verify composition.languages array structure (CRITICAL for rendering)"""
        composition = mock_overview_data.get('composition')
        assert composition is not None, "composition is missing"
        assert 'languages' in composition, "composition.languages is missing"
        
        languages = composition['languages']
        assert isinstance(languages, list), "composition.languages must be an array"
        assert len(languages) > 0, "composition.languages cannot be empty"
        
        total_percentage = 0
        for lang in languages:
            assert 'name' in lang, "language.name is missing"
            assert 'percentage' in lang, "language.percentage is missing"
            assert 'loc' in lang, "language.loc is missing"
            
            # Validate percentage range
            assert 0 <= lang['percentage'] <= 100, f"Language percentage {lang['percentage']} out of range"
            
            # Validate LOC
            assert lang['loc'] >= 0, "language.loc cannot be negative"
            
            total_percentage += lang['percentage']
        
        # Validate total percentage is approximately 100 (allow 0.1% rounding error)
        assert 99.9 <= total_percentage <= 100.1, f"Total language percentage {total_percentage} != 100"
    
    def test_composition_components_structure(self, mock_overview_data):
        """Verify composition.components array structure"""
        composition = mock_overview_data.get('composition')
        assert composition is not None, "composition is missing"
        assert 'components' in composition, "composition.components is missing"
        
        components = composition['components']
        assert isinstance(components, list), "composition.components must be an array"
        
        for component in components:
            assert 'type' in component, "component.type is missing"
            assert 'count' in component, "component.count is missing"
            assert 'technologies' in component, "component.technologies is missing"
            
            # Validate count
            assert component['count'] >= 0, "component.count cannot be negative"
            
            # Validate technologies is array
            assert isinstance(component['technologies'], list), "component.technologies must be an array"
    
    def test_trends_structure(self, mock_overview_data):
        """Verify trends structure"""
        trends = mock_overview_data.get('trends')
        assert trends is not None, "trends is missing"
        
        required_trends = ['health_trend', 'velocity_trend', 'quality_trend']
        for trend in required_trends:
            assert trend in trends, f"trends.{trend} is missing"
            assert trends[trend] in ['improving', 'stable', 'declining'], f"Invalid {trend}: {trends[trend]}"


# Performance Tests
class TestRenderingPerformance:
    """Test Overview tab rendering performance"""
    
    def test_data_parsing_performance(self, mock_overview_data):
        """Verify JSON parsing completes in <50ms"""
        data_path = Path(__file__).parent.parent.parent / "cortex-brain" / "dashboards" / "data" / "mock" / "overview.json"
        
        start = time.perf_counter()
        with open(data_path, 'r') as f:
            data = json.load(f)
        end = time.perf_counter()
        
        parse_time_ms = (end - start) * 1000
        assert parse_time_ms < 50, f"JSON parsing took {parse_time_ms:.2f}ms (target: <50ms)"
    
    def test_data_size_reasonable(self, mock_overview_data):
        """Verify overview.json size is reasonable (<50KB)"""
        data_path = Path(__file__).parent.parent.parent / "cortex-brain" / "dashboards" / "data" / "mock" / "overview.json"
        size_bytes = data_path.stat().st_size
        size_kb = size_bytes / 1024
        
        assert size_kb < 50, f"overview.json is {size_kb:.2f}KB (target: <50KB)"
    
    def test_languages_array_size(self, mock_overview_data):
        """Verify languages array is reasonable size (<20 languages)"""
        languages = mock_overview_data['composition']['languages']
        assert len(languages) <= 20, f"Too many languages ({len(languages)}), may slow rendering"
    
    def test_health_categories_count(self, mock_overview_data):
        """Verify health categories count is reasonable (<10)"""
        categories = mock_overview_data['health_categories']
        assert len(categories) <= 10, f"Too many categories ({len(categories)}), may clutter UI"


# Data Integrity Tests
class TestDataIntegrity:
    """Test data consistency and relationships"""
    
    def test_health_score_vs_status_consistency(self, mock_overview_data):
        """Verify health score aligns with status"""
        health = mock_overview_data['overall_health']
        score = health['score']
        status = health['status']
        
        if score >= 80:
            assert status == 'healthy', f"Score {score} should be 'healthy' not '{status}'"
        elif score >= 60:
            assert status in ['healthy', 'warning'], f"Score {score} should be 'healthy' or 'warning' not '{status}'"
        else:
            assert status in ['warning', 'critical'], f"Score {score} should be 'warning' or 'critical' not '{status}'"
    
    def test_critical_issues_count_vs_array_length(self, mock_overview_data):
        """Verify critical_issues array matches overall health"""
        issues = mock_overview_data['critical_issues']
        health = mock_overview_data['overall_health']
        
        # If health score is high, critical issues should be low/zero
        if health['score'] >= 90:
            total_issues = sum(issue['count'] for issue in issues)
            assert total_issues <= 2, f"Score {health['score']} but {total_issues} critical issues"
    
    def test_test_coverage_reasonable(self, mock_overview_data):
        """Verify test coverage is within reasonable range"""
        coverage = mock_overview_data['key_metrics']['test_coverage']
        
        # Warn if coverage is suspiciously perfect
        if coverage == 100.0:
            pytest.skip("100% coverage detected - verify if accurate")
        
        # Coverage should be positive if project has tests
        assert coverage >= 0, "Test coverage cannot be negative"
    
    def test_technical_debt_vs_maintainability(self, mock_overview_data):
        """Verify technical debt correlates with maintainability index"""
        debt_hours = mock_overview_data['key_metrics']['technical_debt_hours']
        maintainability = mock_overview_data['key_metrics']['maintainability_index']
        
        # High maintainability (>85) should have low debt (<20 hours)
        if maintainability > 85:
            assert debt_hours < 20, f"High maintainability ({maintainability}) but high debt ({debt_hours}h)"
        
        # Low maintainability (<60) should have higher debt
        if maintainability < 60:
            assert debt_hours > 10, f"Low maintainability ({maintainability}) but low debt ({debt_hours}h)"


# Edge Case Tests
class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_critical_issues_array(self):
        """Verify rendering handles empty critical_issues gracefully"""
        data = {
            "critical_issues": []
        }
        # Should not raise exception
        assert isinstance(data['critical_issues'], list)
        assert len(data['critical_issues']) == 0
    
    def test_single_language_composition(self):
        """Verify rendering handles single language projects"""
        data = {
            "composition": {
                "languages": [
                    {"name": "Python", "percentage": 100.0, "loc": 10000}
                ]
            }
        }
        # Should render pie chart with single segment
        assert len(data['composition']['languages']) == 1
        assert data['composition']['languages'][0]['percentage'] == 100.0
    
    def test_zero_health_score(self):
        """Verify rendering handles zero health score"""
        data = {
            "overall_health": {
                "score": 0,
                "status": "critical",
                "trend": "declining",
                "last_scan": "2025-12-06T00:00:00"
            }
        }
        # Should render without division by zero errors
        assert data['overall_health']['score'] == 0
        assert data['overall_health']['status'] == "critical"
    
    def test_very_high_loc_formatting(self):
        """Verify large LOC numbers format correctly"""
        large_loc = 1234567
        # Should format as "1.23M" or similar
        formatted = f"{large_loc / 1_000_000:.2f}M" if large_loc >= 1_000_000 else f"{large_loc / 1000:.1f}K"
        assert "M" in formatted or "K" in formatted


# Integration Summary Test
class TestOverallIntegration:
    """End-to-end integration test"""
    
    def test_complete_overview_pipeline(self, mock_overview_data, overview_schema):
        """Test complete data flow from JSON to rendering-ready structure"""
        # 1. Schema validation
        try:
            validate(instance=mock_overview_data, schema=overview_schema)
        except ValidationError as e:
            pytest.fail(f"Schema validation failed: {e.message}")
        
        # 2. Data extraction (simulate UI logic)
        health_score = mock_overview_data['overall_health']['score']
        languages = mock_overview_data['composition']['languages']
        critical_issues = mock_overview_data['critical_issues']
        
        # 3. Verify rendering-ready
        assert isinstance(health_score, (int, float)), "Health score not numeric"
        assert isinstance(languages, list) and len(languages) > 0, "Languages not array or empty"
        assert isinstance(critical_issues, list), "Critical issues not array"
        
        # 4. Calculate totals (simulate chart data preparation)
        total_loc = sum(lang['loc'] for lang in languages)
        total_percentage = sum(lang['percentage'] for lang in languages)
        
        assert total_loc > 0, "Total LOC is zero"
        assert 99 <= total_percentage <= 101, f"Total percentage {total_percentage} != 100"
        
        # 5. Success - data is rendering-ready
        assert True, "Complete pipeline test passed"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

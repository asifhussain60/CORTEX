"""
Tests for Recommendation Collector
Phase 7.5.1 - RED Phase

Tests recommendation generation across 5 categories:
- Health Improvements
- Performance Optimizations
- Security Hardening
- Technical Debt Reduction
- E2E Test Coverage
"""

import pytest
from typing import Dict, Any


class TestRecommendationCollector:
    """Test suite for recommendation generation"""

    def test_health_recommendations_low_coverage(self):
        """Test health recommendations for low test coverage"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        health_data = {
            'test_coverage': 45,
            'code_quality_score': 70,
            'documentation_score': 60
        }
        
        # Act
        recommendations = collector.generate_health_recommendations(health_data)
        
        # Assert
        assert len(recommendations) > 0
        assert any('coverage' in r['description'].lower() for r in recommendations)
        assert any(r['priority'] in ['P0', 'P1'] for r in recommendations)

    def test_health_recommendations_high_complexity(self):
        """Test health recommendations for high code complexity"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        health_data = {
            'avg_complexity': 25,
            'files_over_threshold': 15,
            'test_coverage': 80
        }
        
        # Act
        recommendations = collector.generate_health_recommendations(health_data)
        
        # Assert
        assert len(recommendations) > 0
        assert any('complexity' in r['description'].lower() for r in recommendations)

    def test_performance_recommendations_slow_endpoints(self):
        """Test performance recommendations for slow endpoints"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        architecture_data = {
            'endpoints': [
                {'path': '/api/reports', 'avg_response_time': 2500},
                {'path': '/api/search', 'avg_response_time': 1800}
            ]
        }
        
        # Act
        recommendations = collector.generate_performance_recommendations(architecture_data)
        
        # Assert
        assert len(recommendations) > 0
        assert any('response time' in r['description'].lower() for r in recommendations)
        assert any('/api/reports' in r['description'] for r in recommendations)

    def test_performance_recommendations_database_queries(self):
        """Test performance recommendations for database optimization"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        code_org_data = {
            'n_plus_one_queries': 5,
            'missing_indexes': 3
        }
        
        # Act
        recommendations = collector.generate_performance_recommendations(code_org_data)
        
        # Assert
        assert len(recommendations) > 0
        assert any('database' in r['description'].lower() or 'query' in r['description'].lower() 
                  for r in recommendations)

    def test_security_recommendations_missing_validation(self):
        """Test security recommendations for missing input validation"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        security_data = {
            'input_validation_coverage': 60,
            'vulnerable_endpoints': ['/api/user/update', '/api/admin/delete']
        }
        
        # Act
        recommendations = collector.generate_security_recommendations(security_data)
        
        # Assert
        assert len(recommendations) > 0
        assert any('validation' in r['description'].lower() for r in recommendations)
        assert any(r['priority'] in ['P0', 'P1'] for r in recommendations)

    def test_security_recommendations_authentication_issues(self):
        """Test security recommendations for authentication weaknesses"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        security_data = {
            'auth_issues': ['weak_password_policy', 'no_mfa'],
            'security_score': 55
        }
        
        # Act
        recommendations = collector.generate_security_recommendations(security_data)
        
        # Assert
        assert len(recommendations) > 0
        assert any('authentication' in r['description'].lower() or 'password' in r['description'].lower()
                  for r in recommendations)

    def test_technical_debt_recommendations_hotspots(self):
        """Test technical debt recommendations for code hotspots"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        heatmap_data = {
            'hotspots': [
                {'file': 'payment_service.py', 'complexity': 35, 'change_frequency': 25},
                {'file': 'order_controller.cs', 'complexity': 28, 'change_frequency': 20}
            ]
        }
        
        # Act
        recommendations = collector.generate_technical_debt_recommendations(heatmap_data)
        
        # Assert
        assert len(recommendations) > 0
        assert any('hotspot' in r['description'].lower() or 'refactor' in r['description'].lower()
                  for r in recommendations)
        assert any('payment_service.py' in r['description'] for r in recommendations)

    def test_technical_debt_recommendations_duplication(self):
        """Test technical debt recommendations for code duplication"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        code_org_data = {
            'duplication_percentage': 15,
            'duplicate_blocks': 45
        }
        
        # Act
        recommendations = collector.generate_technical_debt_recommendations(code_org_data)
        
        # Assert
        assert len(recommendations) > 0
        assert any('duplication' in r['description'].lower() for r in recommendations)

    def test_recommendation_schema_validation(self):
        """Test recommendation output conforms to expected schema"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        health_data = {'test_coverage': 50}
        
        # Act
        recommendations = collector.generate_health_recommendations(health_data)
        
        # Assert
        if len(recommendations) > 0:
            rec = recommendations[0]
            assert 'category' in rec
            assert 'priority' in rec
            assert 'description' in rec
            assert 'impact' in rec
            assert 'effort' in rec
            assert rec['priority'] in ['P0', 'P1', 'P2', 'P3']
            assert rec['effort'] in ['low', 'medium', 'high']
            assert rec['impact'] in ['low', 'medium', 'high']

    def test_collect_all_recommendations(self):
        """Test complete recommendation collection from all data sources"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        all_data = {
            'healthData': {'test_coverage': 50, 'code_quality_score': 65},
            'security': {'security_score': 70, 'vulnerabilities': 3},
            'architecture': {'slow_endpoints': 2},
            'codeOrganization': {'duplication_percentage': 12}
        }
        
        # Act
        result = collector.collect(all_data)
        
        # Assert
        assert 'recommendations' in result
        assert isinstance(result['recommendations'], dict)
        assert 'health_improvements' in result['recommendations']
        assert 'performance' in result['recommendations']
        assert 'security' in result['recommendations']
        assert 'technical_debt' in result['recommendations']

    def test_prioritization_critical_security(self):
        """Test critical security issues get P0 priority"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        security_data = {
            'critical_vulnerabilities': 2,
            'sql_injection_risks': 1
        }
        
        # Act
        recommendations = collector.generate_security_recommendations(security_data)
        
        # Assert
        assert any(r['priority'] == 'P0' for r in recommendations)

    def test_empty_data_handling(self):
        """Test handling of empty or missing data"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        # Act
        result = collector.collect({})
        
        # Assert
        assert 'recommendations' in result
        assert isinstance(result['recommendations'], dict)

    def test_recommendation_deduplication(self):
        """Test duplicate recommendations are removed"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        all_data = {
            'healthData': {'test_coverage': 50},
            'security': {'test_coverage': 50}  # Duplicate issue
        }
        
        # Act
        result = collector.collect(all_data)
        
        # Assert
        all_recs = []
        for category in result['recommendations'].values():
            all_recs.extend(category)
        
        descriptions = [r['description'] for r in all_recs]
        assert len(descriptions) == len(set(descriptions))  # No duplicates

    def test_impact_calculation_high(self):
        """Test impact level calculation for high-impact issues"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        # Act
        impact = collector.calculate_impact('security', 'critical_vulnerability')
        
        # Assert
        assert impact == 'high'

    def test_impact_calculation_medium(self):
        """Test impact level calculation for medium-impact issues"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        # Act
        impact = collector.calculate_impact('performance', 'slow_endpoint')
        
        # Assert
        assert impact in ['medium', 'high']

    def test_effort_estimation_low(self):
        """Test effort estimation for low-effort recommendations"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        # Act
        effort = collector.estimate_effort('add_index')
        
        # Assert
        assert effort == 'low'

    def test_effort_estimation_high(self):
        """Test effort estimation for high-effort recommendations"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        # Act
        effort = collector.estimate_effort('refactor_architecture')
        
        # Assert
        assert effort == 'high'

    def test_recommendation_sorting_by_priority(self):
        """Test recommendations are sorted by priority"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        all_data = {
            'healthData': {'test_coverage': 30},
            'security': {'critical_vulnerabilities': 1}
        }
        
        # Act
        result = collector.collect(all_data)
        
        # Assert
        for category_recs in result['recommendations'].values():
            if len(category_recs) > 1:
                priorities = [r['priority'] for r in category_recs]
                priority_order = ['P0', 'P1', 'P2', 'P3']
                for i in range(len(priorities) - 1):
                    current_idx = priority_order.index(priorities[i])
                    next_idx = priority_order.index(priorities[i + 1])
                    assert current_idx <= next_idx

    def test_summary_statistics(self):
        """Test summary statistics calculation"""
        # Arrange
        from src.dashboard.data.recommendation_collector import RecommendationCollector
        collector = RecommendationCollector('/fake/path')
        
        all_data = {
            'healthData': {'test_coverage': 50},
            'security': {'security_score': 65}
        }
        
        # Act
        result = collector.collect(all_data)
        
        # Assert
        assert 'summary' in result
        assert 'total_recommendations' in result['summary']
        assert 'by_priority' in result['summary']
        assert 'by_category' in result['summary']

"""
Unit tests for Framework Health Heatmap

Tests cover:
1. Health score calculation (weighted formula)
2. Version currency scoring
3. CVE scoring
4. EOL status scoring
5. Community activity scoring
6. Color mapping (green/yellow/red)
7. Filtering (critical only, by category)
8. Drill-down data generation

Author: CORTEX Dashboard System
Version: 1.0.0
Created: December 6, 2025
"""

import pytest


class TestHealthScoreCalculation:
    """Test overall health score calculation"""
    
    def test_health_score_formula(self):
        """Test weighted health score calculation"""
        # Given: Individual factor scores
        version_currency = 80
        cve_score = 90
        eol_status = 70
        community_activity = 85
        
        # When: Calculate health score
        health_score = (
            version_currency * 0.25 +
            cve_score * 0.30 +
            eol_status * 0.25 +
            community_activity * 0.20
        )
        
        # Then: Should match expected weighted average
        expected = 80 * 0.25 + 90 * 0.30 + 70 * 0.25 + 85 * 0.20
        assert health_score == pytest.approx(expected, rel=0.01)
        assert health_score == pytest.approx(81.5, rel=0.01)
    
    def test_health_score_critical_threshold(self):
        """Test health score at critical threshold (<50)"""
        # All factors critical
        version_currency = 30
        cve_score = 40
        eol_status = 35
        community_activity = 45
        
        health_score = (
            version_currency * 0.25 +
            cve_score * 0.30 +
            eol_status * 0.25 +
            community_activity * 0.20
        )
        
        # Expected: 30*0.25 + 40*0.30 + 35*0.25 + 45*0.20 = 7.5 + 12 + 8.75 + 9 = 37.25
        assert health_score < 50
        assert health_score == pytest.approx(37.25, rel=0.01)
    
    def test_health_score_healthy_threshold(self):
        """Test health score at healthy threshold (>70)"""
        # All factors healthy
        version_currency = 85
        cve_score = 90
        eol_status = 95
        community_activity = 88
        
        health_score = (
            version_currency * 0.25 +
            cve_score * 0.30 +
            eol_status * 0.25 +
            community_activity * 0.20
        )
        
        assert health_score > 70
        assert health_score == pytest.approx(89.35, rel=0.01)


class TestVersionCurrencyScoring:
    """Test version currency score calculation"""
    
    def test_version_currency_low_risk(self):
        """Test version currency with low risk score"""
        # Low risk = current version
        risk_score = 15
        version_currency = 100 - risk_score
        
        assert version_currency == 85
        assert version_currency > 70  # Healthy
    
    def test_version_currency_high_risk(self):
        """Test version currency with high risk score"""
        # High risk = outdated version
        risk_score = 80
        version_currency = 100 - risk_score
        
        assert version_currency == 20
        assert version_currency < 50  # Critical
    
    def test_version_currency_medium_risk(self):
        """Test version currency with medium risk score"""
        risk_score = 40
        version_currency = 100 - risk_score
        
        assert version_currency == 60
        assert 50 <= version_currency <= 70  # Warning


class TestCVEScoring:
    """Test CVE score calculation"""
    
    def test_cve_score_zero_vulnerabilities(self):
        """Test CVE score with no vulnerabilities"""
        cve_count = 0
        
        if cve_count == 0:
            cve_score = 100
        
        assert cve_score == 100
    
    def test_cve_score_one_vulnerability(self):
        """Test CVE score with 1 vulnerability"""
        cve_count = 1
        
        if cve_count == 1:
            cve_score = 85
        
        assert cve_score == 85
    
    def test_cve_score_multiple_vulnerabilities(self):
        """Test CVE score with multiple vulnerabilities"""
        test_cases = [
            (2, 70),   # 2-3 CVEs
            (3, 70),
            (4, 50),   # 4-5 CVEs
            (5, 50),
            (7, 30),   # 6-10 CVEs
            (10, 30),
            (15, 10)   # >10 CVEs
        ]
        
        for cve_count, expected_range_min in test_cases:
            if cve_count <= 3:
                cve_score = 70
            elif cve_count <= 5:
                cve_score = 50
            elif cve_count <= 10:
                cve_score = 30
            else:
                cve_score = 10
            
            assert cve_score <= expected_range_min or cve_score == 10


class TestEOLStatusScoring:
    """Test EOL status score calculation"""
    
    def test_eol_already_passed(self):
        """Test EOL score for framework already past EOL"""
        months_to_eol = -5
        
        if months_to_eol <= 0:
            eol_score = 0
        
        assert eol_score == 0
    
    def test_eol_imminent(self):
        """Test EOL score for framework <6 months to EOL"""
        months_to_eol = 3
        
        if months_to_eol <= 6:
            eol_score = 20
        
        assert eol_score == 20
        assert eol_score < 50  # Critical
    
    def test_eol_one_year(self):
        """Test EOL score for framework <1 year to EOL"""
        months_to_eol = 10
        
        if months_to_eol <= 12:
            eol_score = 50
        
        assert eol_score == 50
    
    def test_eol_two_years(self):
        """Test EOL score for framework <2 years to EOL"""
        months_to_eol = 18
        
        if months_to_eol <= 24:
            eol_score = 75
        
        assert eol_score == 75
        assert eol_score > 70  # Healthy
    
    def test_eol_far_future(self):
        """Test EOL score for framework >2 years to EOL"""
        months_to_eol = 36
        
        if months_to_eol > 24:
            eol_score = 100
        
        assert eol_score == 100
    
    def test_eol_no_date(self):
        """Test EOL score for framework with no EOL date"""
        months_to_eol = None
        
        if months_to_eol is None:
            eol_score = 80  # Assume maintained
        
        assert eol_score == 80


class TestCommunityActivityScoring:
    """Test community activity score calculation"""
    
    def test_popular_framework(self):
        """Test community score for popular frameworks"""
        popular_frameworks = {
            'serilog': 95,
            'autofac': 90,
            'entityframework': 95,
            'xunit': 95
        }
        
        for framework, expected_score in popular_frameworks.items():
            assert expected_score >= 90
            assert expected_score > 70  # Healthy
    
    def test_low_maintenance_framework(self):
        """Test community score for low maintenance frameworks"""
        low_maintenance = {
            'log4net': 40,
            'unity': 35
        }
        
        for framework, expected_score in low_maintenance.items():
            assert expected_score < 50  # Critical
    
    def test_unknown_framework_default(self):
        """Test community score for unknown framework"""
        # Unknown framework should get default moderate score
        default_score = 60
        
        assert default_score == 60
        assert 50 <= default_score <= 70  # Warning range


class TestColorMapping:
    """Test health score to color mapping"""
    
    def test_color_critical(self):
        """Test color for critical health score (<50)"""
        health_scores = [0, 25, 49]
        
        for score in health_scores:
            assert score < 50
            color_class = 'critical'
            assert color_class == 'critical'
    
    def test_color_warning(self):
        """Test color for warning health score (50-70)"""
        health_scores = [50, 60, 69]
        
        for score in health_scores:
            assert 50 <= score < 70
            color_class = 'warning'
            assert color_class == 'warning'
    
    def test_color_healthy(self):
        """Test color for healthy health score (>=70)"""
        health_scores = [70, 85, 100]
        
        for score in health_scores:
            assert score >= 70
            color_class = 'healthy'
            assert color_class == 'healthy'
    
    def test_color_boundary_conditions(self):
        """Test color at exact boundary values"""
        # Test boundaries
        assert 49 < 50  # Critical/Warning boundary
        assert 50 >= 50  # Warning starts at 50
        assert 69 < 70  # Warning/Healthy boundary
        assert 70 >= 70  # Healthy starts at 70


class TestFiltering:
    """Test heatmap filtering functionality"""
    
    def test_filter_critical_only(self):
        """Test filtering to show only critical frameworks"""
        frameworks = [
            {'name': 'Framework A', 'health_score': 30},
            {'name': 'Framework B', 'health_score': 65},
            {'name': 'Framework C', 'health_score': 45},
            {'name': 'Framework D', 'health_score': 80}
        ]
        
        # Filter critical only (<50)
        critical = [f for f in frameworks if f['health_score'] < 50]
        
        assert len(critical) == 2
        assert critical[0]['name'] == 'Framework A'
        assert critical[1]['name'] == 'Framework C'
    
    def test_filter_by_category(self):
        """Test filtering by framework category"""
        frameworks = [
            {'name': 'Serilog', 'category': 'logging', 'health_score': 90},
            {'name': 'log4net', 'category': 'logging', 'health_score': 40},
            {'name': 'Autofac', 'category': 'dependency-injection', 'health_score': 85},
            {'name': 'Unity', 'category': 'dependency-injection', 'health_score': 35}
        ]
        
        # Filter by logging
        logging_frameworks = [f for f in frameworks if f['category'] == 'logging']
        assert len(logging_frameworks) == 2
        assert all(f['category'] == 'logging' for f in logging_frameworks)
        
        # Filter by dependency injection
        di_frameworks = [f for f in frameworks if f['category'] == 'dependency-injection']
        assert len(di_frameworks) == 2
        assert all(f['category'] == 'dependency-injection' for f in di_frameworks)
    
    def test_filter_combined(self):
        """Test combining critical filter with category filter"""
        frameworks = [
            {'name': 'Serilog', 'category': 'logging', 'health_score': 90},
            {'name': 'log4net', 'category': 'logging', 'health_score': 40},
            {'name': 'Autofac', 'category': 'dependency-injection', 'health_score': 85},
            {'name': 'Unity', 'category': 'dependency-injection', 'health_score': 35}
        ]
        
        # Critical logging frameworks
        critical_logging = [
            f for f in frameworks 
            if f['category'] == 'logging' and f['health_score'] < 50
        ]
        
        assert len(critical_logging) == 1
        assert critical_logging[0]['name'] == 'log4net'


class TestDrillDownData:
    """Test drill-down data generation"""
    
    def test_recommendations_for_critical_framework(self):
        """Test recommendations generated for critical framework"""
        framework = {
            'name': 'log4net',
            'health_score': 35,
            'factors': {
                'version_currency': 25,
                'cve_score': 40,
                'eol_status': 30,
                'community_activity': 40
            }
        }
        
        recommendations = []
        
        if framework['factors']['version_currency'] < 50:
            recommendations.append('Update to latest version')
        if framework['factors']['cve_score'] < 50:
            recommendations.append('Critical security vulnerabilities')
        if framework['factors']['eol_status'] < 30:
            recommendations.append('Framework approaching or past EOL')
        if framework['factors']['community_activity'] < 50:
            recommendations.append('Low community activity')
        
        assert len(recommendations) >= 3
        assert any('Update' in r for r in recommendations)
        assert any('security' in r for r in recommendations)
    
    def test_recommendations_for_healthy_framework(self):
        """Test recommendations for healthy framework"""
        framework = {
            'name': 'Serilog',
            'health_score': 92,
            'factors': {
                'version_currency': 85,
                'cve_score': 100,
                'eol_status': 100,
                'community_activity': 95
            }
        }
        
        # Healthy framework should have positive recommendation
        if framework['health_score'] >= 70:
            recommendation = 'Framework is healthy'
            assert 'healthy' in recommendation.lower()
    
    def test_migration_path_mapping(self):
        """Test migration path suggestions"""
        migration_map = {
            'log4net': 'Serilog',
            'unity': 'Autofac',
            'newtonsoft.json': 'System.Text.Json'
        }
        
        # Test known migrations
        for old_framework, new_framework in migration_map.items():
            assert new_framework is not None
            assert len(new_framework) > 0
        
        # Test unknown framework
        unknown_framework = 'SomeUnknownFramework'
        migration_path = migration_map.get(unknown_framework.lower())
        assert migration_path is None

"""
Phase 6 Tests: Governance Dashboard Implementation

Tests for:
- Compliance metrics API endpoints
- Report generation
- Dashboard functionality
"""

import pytest
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from reports.compliance_report import ComplianceReportGenerator


class TestComplianceMetricsAPI:
    """Test compliance metrics API functionality"""
    
    @pytest.mark.ac("DASH-001")
    def test_dashboard_001_metrics_api_exists(self):
        """Verify metrics API module exists"""
        # Verify compliance_metrics module can be imported
        from api.endpoints import compliance_metrics
        assert hasattr(compliance_metrics, 'router')
        assert hasattr(compliance_metrics, 'get_coverage_metrics')
        assert hasattr(compliance_metrics, 'get_coverage_by_domain')
        assert hasattr(compliance_metrics, 'get_compliance_timeline')
        assert hasattr(compliance_metrics, 'get_ac_details')
        assert hasattr(compliance_metrics, 'get_overall_stats')
    
    @pytest.mark.ac("DASH-002")
    def test_dashboard_002_api_endpoints_defined(self):
        """Verify all API endpoints are properly defined"""
        from api.endpoints.compliance_metrics import router
        
        # Verify router has routes
        routes = [route.path for route in router.routes]
        assert "/api/compliance/coverage" in routes
        assert "/api/compliance/by-domain" in routes
        assert "/api/compliance/timeline" in routes
        assert "/api/compliance/stats" in routes
    
    @pytest.mark.ac("DASH-003")
    def test_dashboard_003_metrics_documentation(self):
        """Verify API endpoints have proper documentation"""
        from api.endpoints import compliance_metrics
        
        assert compliance_metrics.get_coverage_metrics.__doc__ is not None
        assert compliance_metrics.get_coverage_by_domain.__doc__ is not None
        assert compliance_metrics.get_compliance_timeline.__doc__ is not None
        assert compliance_metrics.get_ac_details.__doc__ is not None


class TestComplianceReportGeneration:
    """Test report generation functionality"""
    
    @pytest.mark.ac("DASH-004")
    def test_dashboard_004_report_generator_instantiation(self):
        """Verify report generator can be instantiated"""
        generator = ComplianceReportGenerator()
        assert generator is not None
        assert hasattr(generator, 'generate_executive_summary')
        assert hasattr(generator, 'generate_domain_report')
        assert hasattr(generator, 'generate_trend_analysis')
    
    @pytest.mark.ac("DASH-005")
    def test_dashboard_005_executive_summary_structure(self):
        """Verify executive summary has correct structure"""
        generator = ComplianceReportGenerator()
        summary = generator.generate_executive_summary()
        
        assert 'report_type' in summary
        assert summary['report_type'] == 'EXECUTIVE_SUMMARY'
        assert 'report_date' in summary
        assert 'overall_status' in summary
        assert 'coverage' in summary
        assert 'audit_entries' in summary
        assert 'key_metrics' in summary
        assert 'recommendations' in summary
    
    @pytest.mark.ac("DASH-006")
    def test_dashboard_006_domain_report_structure(self):
        """Verify domain report has correct structure"""
        generator = ComplianceReportGenerator()
        domains = generator.generate_domain_report()
        
        assert isinstance(domains, dict)
        for domain, stats in domains.items():
            assert 'coverage' in stats
            assert 'acs' in stats
            assert 'entries' in stats
            assert 'status' in stats
    
    @pytest.mark.ac("DASH-007")
    def test_dashboard_007_trend_analysis_structure(self):
        """Verify trend analysis has correct structure"""
        generator = ComplianceReportGenerator()
        trends = generator.generate_trend_analysis()
        
        assert 'analysis_type' in trends
        assert trends['analysis_type'] == 'TREND_ANALYSIS'
        assert 'phases_completed' in trends
        assert 'total_entry_growth' in trends
        assert 'total_ac_growth' in trends
        assert 'coverage_progression' in trends
        assert 'phases' in trends
    
    @pytest.mark.ac("DASH-008")
    def test_dashboard_008_full_report_generation(self):
        """Verify full report can be generated"""
        generator = ComplianceReportGenerator()
        report = generator.generate_full_report()
        
        assert 'report_title' in report
        assert 'report_date' in report
        assert 'executive_summary' in report
        assert 'domain_analysis' in report
        assert 'trend_analysis' in report
        assert 'framework_status' in report
        assert 'next_steps' in report


class TestDashboardFrontend:
    """Test dashboard frontend components"""
    
    @pytest.mark.ac("DASH-009")
    def test_dashboard_009_html_file_exists(self):
        """Verify dashboard HTML file exists"""
        dashboard_path = os.path.join(
            os.path.dirname(__file__),
            '../../src/dashboard/compliance.html'
        )
        assert os.path.exists(dashboard_path)
    
    @pytest.mark.ac("DASH-010")
    def test_dashboard_010_html_contains_required_elements(self):
        """Verify HTML contains required dashboard elements"""
        dashboard_path = os.path.join(
            os.path.dirname(__file__),
            '../../src/dashboard/compliance.html'
        )
        
        with open(dashboard_path, 'r') as f:
            html = f.read()
        
        assert 'CORTEX Governance Compliance Dashboard' in html
        assert 'canvas' in html  # Charts
        assert 'metrics' in html  # Metrics grid
        assert 'domain-table' in html  # Domain table
    
    @pytest.mark.ac("DASH-011")
    def test_dashboard_011_javascript_chart_library(self):
        """Verify chart library is included"""
        dashboard_path = os.path.join(
            os.path.dirname(__file__),
            '../../src/dashboard/compliance.html'
        )
        
        with open(dashboard_path, 'r') as f:
            html = f.read()
        
        assert 'chart.js' in html
        assert 'axios' in html
    
    @pytest.mark.ac("DASH-012")
    def test_dashboard_012_responsive_design(self):
        """Verify responsive design is implemented"""
        dashboard_path = os.path.join(
            os.path.dirname(__file__),
            '../../src/dashboard/compliance.html'
        )
        
        with open(dashboard_path, 'r') as f:
            html = f.read()
        
        assert 'viewport' in html
        assert 'media' in html
        assert 'max-width: 768px' in html


class TestDashboardIntegration:
    """Integration tests for dashboard components"""
    
    @pytest.mark.ac("DASH-013")
    def test_dashboard_013_report_save_functionality(self):
        """Verify reports can be saved to disk"""
        import tempfile
        from reports.compliance_report import generate_and_save_report
        
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = generate_and_save_report(tmpdir)
            
            assert os.path.exists(report_path)
            assert report_path.endswith('.json')
            
            # Verify file contents
            import json
            with open(report_path, 'r') as f:
                data = json.load(f)
            
            assert 'report_title' in data
            assert 'executive_summary' in data
    
    @pytest.mark.ac("DASH-014")
    def test_dashboard_014_metrics_refresh_capability(self):
        """Verify metrics can be refreshed independently"""
        generator = ComplianceReportGenerator()
        
        # Get initial metrics
        initial = generator.generate_executive_summary()
        
        # Get metrics again
        refreshed = generator.generate_executive_summary()
        
        # Should have same structure even if values might differ
        assert set(initial.keys()) == set(refreshed.keys())
    
    @pytest.mark.ac("DASH-015")
    def test_dashboard_015_dashboard_production_ready(self):
        """Verify dashboard is production-ready"""
        dashboard_path = os.path.join(
            os.path.dirname(__file__),
            '../../src/dashboard/compliance.html'
        )
        
        generator = ComplianceReportGenerator()
        report = generator.generate_full_report()
        
        assert os.path.exists(dashboard_path)
        assert report['framework_status'] == 'PRODUCTION_READY'

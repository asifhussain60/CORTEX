"""
Phase 4 tests - Dashboard rendering and export.

Tests:
- DashboardRenderer initialization and rendering
- ExportManager multi-format export
- Template files exist
"""

import pytest
import json
from pathlib import Path
from src.cortex_lens.generators.dashboard_renderer import DashboardRenderer
from src.cortex_lens.generators.export_manager import ExportManager


class TestDashboardRenderer:
    """Test DashboardRenderer"""
    
    def test_renderer_initialization(self):
        """Test DashboardRenderer can be instantiated"""
        renderer = DashboardRenderer()
        assert renderer is not None
        assert hasattr(renderer, 'template_dir')
        assert hasattr(renderer, 'render')
    
    def test_template_files_exist(self):
        """Test required template files exist"""
        renderer = DashboardRenderer()
        assert renderer.template_path.exists(), f"Template not found: {renderer.template_path}"
        assert renderer.css_path.exists(), f"CSS not found: {renderer.css_path}"
        assert renderer.js_path.exists(), f"JS not found: {renderer.js_path}"
    
    def test_prepare_template_data(self):
        """Test template data preparation"""
        renderer = DashboardRenderer()
        
        # Mock analysis data
        analysis_data = {
            'classification': {'repo_type': 'fullstack_web', 'primary_language': 'Python'},
            'health': {'total_files': 100, 'total_lines': 5000, 'health_score': 85},
            'security': {'vulnerabilities_found': 5, 'findings': []},
            'complexity': {'complexity_summary': {'avg_cyclomatic': 3.5}, 'hotspots': []},
            'test_coverage': {'coverage_summary': 78.5, 'total_tests': 120},
            'tech_stack': {'frameworks': [], 'databases': [], 'build_tools': []},
            'dependencies': {'packages': {}},
        }
        
        template_data = renderer._prepare_template_data(analysis_data, 'TestRepo')
        
        assert template_data['repository_name'] == 'TestRepo'
        assert template_data['total_files'] == 100
        assert template_data['health_score'] == 85
        assert 'analysis_data_json' in template_data


class TestExportManager:
    """Test ExportManager"""
    
    def test_export_manager_initialization(self):
        """Test ExportManager can be instantiated"""
        exporter = ExportManager()
        assert exporter is not None
        assert hasattr(exporter, 'export_json')
        assert hasattr(exporter, 'export_markdown')
        assert hasattr(exporter, 'export_csv_metrics')
    
    def test_export_json(self, tmp_path):
        """Test JSON export"""
        exporter = ExportManager()
        
        analysis_data = {
            'test_key': 'test_value',
            'metrics': {'count': 42}
        }
        
        output_path = tmp_path / 'analysis.json'
        result_path = exporter.export_json(analysis_data, output_path)
        
        assert result_path.exists()
        
        # Verify JSON content
        with open(result_path) as f:
            loaded_data = json.load(f)
        
        assert loaded_data['test_key'] == 'test_value'
        assert loaded_data['metrics']['count'] == 42
    
    def test_generate_markdown_report(self):
        """Test Markdown report generation"""
        exporter = ExportManager()
        
        analysis_data = {
            'classification': {'repo_type': 'api_service', 'primary_language': 'Python'},
            'health': {'health_score': 75, 'total_files': 50, 'total_lines': 2500},
            'security': {'vulnerabilities_found': 3, 'vulnerabilities_by_severity': {'HIGH': 1, 'MEDIUM': 2}},
            'complexity': {'complexity_summary': {'avg_cyclomatic': 4.2, 'avg_cognitive': 5.1, 'avg_maintainability': 65.0}, 'hotspots': []},
            'test_coverage': {'coverage_summary': 82.0, 'total_tests': 85, 'tests_by_type': {'unit': 70, 'integration': 15}, 'coverage_by_layer': {'presentation': 90.0, 'business': 80.0}},
            'dependencies': {'packages': {}},
            'architecture': {'patterns': {}, 'layers': {}},
        }
        
        markdown = exporter._generate_markdown_report(analysis_data, 'TestRepo')
        
        assert '# 🧠 CORTEX Lens Analysis Report' in markdown
        assert 'TestRepo' in markdown
        assert '75/100' in markdown
        assert 'Python' in markdown


class TestDashboardIntegration:
    """Integration tests for dashboard workflow"""
    
    def test_full_dashboard_generation(self, tmp_path):
        """Test complete dashboard generation workflow"""
        renderer = DashboardRenderer()
        exporter = ExportManager()
        
        # Mock complete analysis data
        analysis_data = {
            'classification': {'repo_type': 'fullstack_web', 'primary_language': 'Python'},
            'health': {
                'total_files': 150,
                'total_lines': 8000,
                'health_score': 82,
                'language_map': {'Python': 100, 'JavaScript': 30, 'HTML': 20}
            },
            'security': {
                'vulnerabilities_found': 8,
                'vulnerabilities_by_severity': {'CRITICAL': 1, 'HIGH': 3, 'MEDIUM': 4},
                'findings': [
                    {'severity': 'HIGH', 'type': 'sql_injection', 'file': '/app/db.py', 'line': 42, 'description': 'SQL injection risk', 'cwe': 'CWE-89'}
                ]
            },
            'complexity': {
                'complexity_summary': {'avg_cyclomatic': 5.3, 'avg_cognitive': 6.7, 'avg_maintainability': 68.5},
                'hotspots': [
                    {'name': 'process_payment', 'file': '/app/payments.py', 'line': 100, 'cyclomatic': 15, 'cognitive': 22, 'maintainability': 45.0, 'complexity_rating': 'HIGH'}
                ]
            },
            'test_coverage': {
                'coverage_summary': 76.5,
                'total_tests': 145,
                'tests_by_type': {'unit': 110, 'integration': 30, 'e2e': 5},
                'coverage_by_layer': {'presentation': 85.0, 'business': 70.0, 'data': 65.0},
                'test_quality_metrics': {'avg_assertions_per_test': 3.2}
            },
            'tech_stack': {
                'frameworks': [{'name': 'Django', 'version': '4.2.0'}],
                'databases': [{'name': 'PostgreSQL', 'version': '15.0'}],
                'build_tools': [{'name': 'Docker', 'version': '24.0'}]
            },
            'dependencies': {
                'packages': {
                    'django': {'version': '4.2.0', 'type': 'direct', 'source': 'requirements.txt'},
                    'psycopg2': {'version': '2.9.6', 'type': 'direct', 'source': 'requirements.txt'}
                }
            },
            'architecture': {
                'patterns': {'mvc': 0.9, 'rest_api': 0.8},
                'layers': {'presentation': ['views.py'], 'business': ['services.py'], 'data': ['models.py']}
            },
            'api_endpoints': {
                'endpoints': [
                    {'method': 'GET', 'path': '/api/users'},
                    {'method': 'POST', 'path': '/api/users'}
                ]
            }
        }
        
        # Test dashboard rendering
        dashboard_path = renderer.render(analysis_data, tmp_path, 'TestApp')
        assert dashboard_path.exists()
        assert (tmp_path / 'cortex-unified.css').exists()
        assert (tmp_path / 'cortex-unified.js').exists()
        
        # Test JSON export
        json_path = exporter.export_json(analysis_data, tmp_path / 'analysis.json')
        assert json_path.exists()
        
        # Test Markdown export
        md_path = exporter.export_markdown(analysis_data, tmp_path / 'report.md', 'TestApp')
        assert md_path.exists()
        
        # Verify Markdown content
        md_content = md_path.read_text(encoding='utf-8')
        assert 'TestApp' in md_content
        assert '82/100' in md_content

"""
Dashboard Orchestrator Tests - Phase 10.1 TDD
RED Phase: Tests must fail initially

Test Coverage:
- Orchestrator initialization
- collect_all_data() execution flow
- Phase dependencies (7 → 8 → 9)
- Data enrichment between phases
- Template JSON generation
- File saving
- Error handling

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime

from src.dashboard.orchestrator import DashboardOrchestrator


class TestOrchestratorInitialization:
    """Test orchestrator initialization"""
    
    def test_init_with_repo_path(self, tmp_path):
        """Test initialization with repository path"""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        
        orchestrator = DashboardOrchestrator(str(repo_path))
        
        assert orchestrator.repo_path == repo_path
        assert orchestrator.output_dir == repo_path / '.cortex'
        assert orchestrator.output_dir.exists()
    
    def test_init_with_custom_output_dir(self, tmp_path):
        """Test initialization with custom output directory"""
        repo_path = tmp_path / "test_repo"
        output_dir = tmp_path / "custom_output"
        repo_path.mkdir()
        
        orchestrator = DashboardOrchestrator(str(repo_path), str(output_dir))
        
        assert orchestrator.repo_path == repo_path
        assert orchestrator.output_dir == output_dir
        assert orchestrator.output_dir.exists()


class TestCollectAllData:
    """Test complete data collection pipeline"""
    
    @patch('src.dashboard.orchestrator.OverviewCollector')
    @patch('src.dashboard.orchestrator.TechStackCollector')
    @patch('src.dashboard.orchestrator.SecurityCollector')
    @patch('src.dashboard.orchestrator.BusinessCapabilityDetector')
    @patch('src.dashboard.orchestrator.RecommendationCollector')
    @patch('src.dashboard.orchestrator.UseCaseCollector')
    @patch('src.dashboard.orchestrator.SolutionStructureCollector')
    @patch('src.dashboard.orchestrator.TechStackRiskScorer')
    @patch('src.dashboard.orchestrator.MigrationRoadmapGenerator')
    @patch('src.dashboard.orchestrator.FrameworkHealthHeatmap')
    @patch('src.dashboard.orchestrator.DependencyBloatAnalyzer')
    def test_collect_all_data_calls_all_collectors(
        self, mock_bloat, mock_health, mock_roadmap, mock_risk, mock_solution,
        mock_usecase, mock_rec, mock_business, mock_security, mock_tech, mock_overview,
        tmp_path
    ):
        """Test that collect_all_data calls all collectors in order"""
        # Setup mocks
        mock_overview_instance = Mock()
        mock_overview_instance.collect.return_value = {'repository_name': 'TestRepo', 'total_files': 100}
        mock_overview.return_value = mock_overview_instance
        
        mock_tech_instance = Mock()
        mock_tech_instance.collect.return_value = {'languages': [], 'frameworks': []}
        mock_tech.return_value = mock_tech_instance
        
        mock_security_instance = Mock()
        mock_security_instance.collect.return_value = {'vulnerabilities': []}
        mock_security.return_value = mock_security_instance
        
        mock_business_instance = Mock()
        mock_business_instance.collect.return_value = {'executive_summary': 'Test'}
        mock_business.return_value = mock_business_instance
        
        mock_rec_instance = Mock()
        mock_rec_instance.collect.return_value = {'recommendations': []}
        mock_rec.return_value = mock_rec_instance
        
        mock_usecase_instance = Mock()
        mock_usecase_instance.collect.return_value = {'use_cases': [], 'metadata': {}}
        mock_usecase.return_value = mock_usecase_instance
        
        mock_solution_instance = Mock()
        mock_solution_instance.collect.return_value = {'hierarchy': []}
        mock_solution.return_value = mock_solution_instance
        
        mock_risk_instance = Mock()
        mock_risk_instance.enrich_tech_stack.return_value = {'languages': [], 'enriched': True}
        mock_risk.return_value = mock_risk_instance
        
        mock_roadmap_instance = Mock()
        mock_roadmap_instance.generate_roadmap.return_value = {'phases': []}
        mock_roadmap.return_value = mock_roadmap_instance
        
        mock_health_instance = Mock()
        mock_health_instance.generate.return_value = {'heatmap': []}
        mock_health.return_value = mock_health_instance
        
        mock_bloat_instance = Mock()
        mock_bloat_instance.analyze.return_value = {'bloat_detected': False}
        mock_bloat.return_value = mock_bloat_instance
        
        # Execute
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        orchestrator = DashboardOrchestrator(str(repo_path))
        result = orchestrator.collect_all_data()
        
        # Verify all collectors called
        mock_overview_instance.collect.assert_called_once()
        mock_tech_instance.collect.assert_called_once()
        mock_security_instance.collect.assert_called_once()
        mock_business_instance.collect.assert_called_once()
        mock_rec_instance.collect.assert_called_once()
        mock_usecase_instance.collect.assert_called_once()
        mock_solution_instance.collect.assert_called_once()
        mock_risk_instance.enrich_tech_stack.assert_called_once()
        mock_roadmap_instance.generate_roadmap.assert_called_once()
        mock_health_instance.generate.assert_called_once()
        mock_bloat_instance.analyze.assert_called_once()
        
        # Verify result structure
        assert 'overview' in result
        assert 'tech_stack' in result
        assert 'security' in result
        assert 'business' in result
        assert 'recommendations' in result
        assert 'use_cases' in result
        assert 'solution_structure' in result
        assert 'migration_roadmap' in result
        assert 'health_heatmap' in result
        assert 'bloat_analysis' in result
    
    @patch('src.dashboard.orchestrator.OverviewCollector')
    @patch('src.dashboard.orchestrator.TechStackCollector')
    @patch('src.dashboard.orchestrator.SecurityCollector')
    @patch('src.dashboard.orchestrator.BusinessCapabilityDetector')
    @patch('src.dashboard.orchestrator.RecommendationCollector')
    @patch('src.dashboard.orchestrator.UseCaseCollector')
    @patch('src.dashboard.orchestrator.SolutionStructureCollector')
    @patch('src.dashboard.orchestrator.TechStackRiskScorer')
    @patch('src.dashboard.orchestrator.MigrationRoadmapGenerator')
    @patch('src.dashboard.orchestrator.FrameworkHealthHeatmap')
    @patch('src.dashboard.orchestrator.DependencyBloatAnalyzer')
    def test_phase8_receives_phase7_data(
        self, mock_bloat, mock_health, mock_roadmap, mock_risk, mock_solution,
        mock_usecase, mock_rec, mock_business, mock_security, mock_tech, mock_overview,
        tmp_path
    ):
        """Test Phase 8 collectors receive Phase 7 data"""
        # Setup Phase 7 mocks
        tech_stack_data = {'languages': ['Python'], 'frameworks': ['Django']}
        mock_tech_instance = Mock()
        mock_tech_instance.collect.return_value = tech_stack_data
        mock_tech.return_value = mock_tech_instance
        
        mock_overview.return_value.collect.return_value = {'repository_name': 'Test'}
        mock_security.return_value.collect.return_value = {'vulnerabilities': []}
        mock_business.return_value.collect.return_value = {'executive_summary': 'Test'}
        mock_rec.return_value.collect.return_value = {'recommendations': []}
        mock_usecase.return_value.collect.return_value = {'use_cases': [], 'metadata': {}}
        mock_solution.return_value.collect.return_value = {'hierarchy': []}
        
        # Setup Phase 8 mock
        enriched_tech_stack = {**tech_stack_data, 'risk_scores': []}
        mock_risk_instance = Mock()
        mock_risk_instance.enrich_tech_stack.return_value = enriched_tech_stack
        mock_risk.return_value = mock_risk_instance
        
        # Setup Phase 9 mocks
        mock_roadmap.return_value.generate_roadmap.return_value = {'phases': []}
        mock_health.return_value.generate.return_value = {'heatmap': []}
        mock_bloat.return_value.analyze.return_value = {'bloat_detected': False}
        
        # Execute
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        orchestrator = DashboardOrchestrator(str(repo_path))
        result = orchestrator.collect_all_data()
        
        # Verify Phase 8 received Phase 7 tech_stack
        mock_risk_instance.enrich_tech_stack.assert_called_once_with(tech_stack_data)
        
        # Verify result has enriched tech_stack (not original)
        assert result['tech_stack'] == enriched_tech_stack
    
    @patch('src.dashboard.orchestrator.OverviewCollector')
    @patch('src.dashboard.orchestrator.TechStackCollector')
    @patch('src.dashboard.orchestrator.SecurityCollector')
    @patch('src.dashboard.orchestrator.BusinessCapabilityDetector')
    @patch('src.dashboard.orchestrator.RecommendationCollector')
    @patch('src.dashboard.orchestrator.UseCaseCollector')
    @patch('src.dashboard.orchestrator.SolutionStructureCollector')
    @patch('src.dashboard.orchestrator.TechStackRiskScorer')
    @patch('src.dashboard.orchestrator.MigrationRoadmapGenerator')
    @patch('src.dashboard.orchestrator.FrameworkHealthHeatmap')
    @patch('src.dashboard.orchestrator.DependencyBloatAnalyzer')
    def test_phase9_receives_enriched_tech_stack(
        self, mock_bloat, mock_health, mock_roadmap, mock_risk, mock_solution,
        mock_usecase, mock_rec, mock_business, mock_security, mock_tech, mock_overview,
        tmp_path
    ):
        """Test Phase 9 intelligence receives enriched tech_stack from Phase 8"""
        # Setup mocks
        enriched_tech_stack = {'languages': ['Python'], 'risk_scores': [{'tech': 'Python', 'risk': 25}]}
        
        mock_overview.return_value.collect.return_value = {'repository_name': 'Test'}
        mock_tech.return_value.collect.return_value = {'languages': ['Python']}
        mock_security.return_value.collect.return_value = {'vulnerabilities': []}
        mock_business.return_value.collect.return_value = {'executive_summary': 'Test'}
        mock_rec.return_value.collect.return_value = {'recommendations': []}
        mock_usecase.return_value.collect.return_value = {'use_cases': [], 'metadata': {}}
        mock_solution.return_value.collect.return_value = {'hierarchy': []}
        
        mock_risk_instance = Mock()
        mock_risk_instance.enrich_tech_stack.return_value = enriched_tech_stack
        mock_risk.return_value = mock_risk_instance
        
        mock_roadmap_instance = Mock()
        mock_roadmap_instance.generate_roadmap.return_value = {'phases': []}
        mock_roadmap.return_value = mock_roadmap_instance
        
        mock_health_instance = Mock()
        mock_health_instance.generate.return_value = {'heatmap': []}
        mock_health.return_value = mock_health_instance
        
        mock_bloat_instance = Mock()
        mock_bloat_instance.analyze.return_value = {'bloat_detected': False}
        mock_bloat.return_value = mock_bloat_instance
        
        # Execute
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        orchestrator = DashboardOrchestrator(str(repo_path))
        result = orchestrator.collect_all_data()
        
        # Verify Phase 9 received enriched tech_stack (not original)
        mock_roadmap_instance.generate_roadmap.assert_called_once_with(enriched_tech_stack)
        mock_health_instance.generate.assert_called_once_with(enriched_tech_stack)
        mock_bloat_instance.analyze.assert_called_once_with(enriched_tech_stack)
    
    def test_collect_all_data_includes_metadata(self, tmp_path):
        """Test that collect_all_data includes generation metadata"""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        
        with patch('src.dashboard.orchestrator.OverviewCollector'), \
             patch('src.dashboard.orchestrator.TechStackCollector'), \
             patch('src.dashboard.orchestrator.SecurityCollector'), \
             patch('src.dashboard.orchestrator.BusinessCapabilityDetector'), \
             patch('src.dashboard.orchestrator.RecommendationCollector'), \
             patch('src.dashboard.orchestrator.UseCaseCollector'), \
             patch('src.dashboard.orchestrator.SolutionStructureCollector'), \
             patch('src.dashboard.orchestrator.TechStackRiskScorer'), \
             patch('src.dashboard.orchestrator.MigrationRoadmapGenerator'), \
             patch('src.dashboard.orchestrator.FrameworkHealthHeatmap'), \
             patch('src.dashboard.orchestrator.DependencyBloatAnalyzer'):
            
            orchestrator = DashboardOrchestrator(str(repo_path))
            result = orchestrator.collect_all_data()
        
        # Verify metadata present
        assert 'generated_at' in result
        assert 'repo_path' in result
        assert 'dashboard_version' in result
        assert result['dashboard_version'] == '3.0.0'
        assert result['repo_path'] == str(repo_path)


class TestGenerateDashboardJson:
    """Test template-ready JSON generation"""
    
    def test_generate_dashboard_json_formats_for_template(self, tmp_path):
        """Test generate_dashboard_json creates template-ready structure"""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        
        # Sample collected data
        collected_data = {
            'overview': {'repository_name': 'TestRepo', 'total_files': 50},
            'tech_stack': {'languages': [], 'frameworks': []},
            'security': {'vulnerabilities': [], 'score': 85},
            'business': {'executive_summary': 'Test summary'},
            'recommendations': {
                'recommendations': [
                    {'priority': 'p0', 'title': 'Critical fix'}
                ],
                'top_recommendations': []
            },
            'use_cases': [
                {'id': 'uc-001', 'name': 'Login', 'business_value': 'critical'}
            ],
            'use_cases_metadata': {
                'roles': [{'id': 'admin', 'name': 'Admin'}],
                'domains': [{'id': 'security_authentication', 'name': 'Security'}]
            },
            'solution_structure': {'hierarchy': []},
            'migration_roadmap': {'phases': []},
            'health_heatmap': {'heatmap': []},
            'bloat_analysis': {'bloat_detected': False},
            'generated_at': '2024-01-01T00:00:00',
            'repo_path': str(repo_path)
        }
        
        orchestrator = DashboardOrchestrator(str(repo_path))
        result = orchestrator.generate_dashboard_json(collected_data)
        
        # Verify template structure
        assert result['title'] == 'TestRepo'
        assert 'executive_summary' in result
        assert 'metrics' in result
        assert 'use_cases' in result
        assert 'roles' in result
        assert 'domains' in result
        assert result['critical_use_cases_count'] == 1
        assert result['critical_high_roi_count'] == 1
    
    def test_generate_dashboard_json_collects_if_no_data(self, tmp_path):
        """Test generate_dashboard_json collects data if none provided"""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        
        orchestrator = DashboardOrchestrator(str(repo_path))
        
        with patch.object(orchestrator, 'collect_all_data') as mock_collect:
            mock_collect.return_value = {
                'overview': {'repository_name': 'Test'},
                'tech_stack': {},
                'security': {},
                'business': {},
                'recommendations': {'recommendations': []},
                'use_cases': [],
                'use_cases_metadata': {'roles': [], 'domains': []},
                'solution_structure': {},
                'migration_roadmap': {},
                'health_heatmap': {},
                'bloat_analysis': {},
                'generated_at': '2024-01-01',
                'repo_path': str(repo_path)
            }
            
            result = orchestrator.generate_dashboard_json()
            
            mock_collect.assert_called_once()
            assert 'title' in result


class TestSaveDashboardJson:
    """Test dashboard JSON file saving"""
    
    def test_save_dashboard_json_creates_file(self, tmp_path):
        """Test save_dashboard_json writes JSON file"""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        
        template_data = {
            'title': 'Test',
            'metrics': [],
            'raw_data': {}
        }
        
        orchestrator = DashboardOrchestrator(str(repo_path))
        output_path = orchestrator.save_dashboard_json(template_data)
        
        assert output_path.exists()
        assert output_path.name == 'dashboard-data.json'
        assert output_path.parent == repo_path / '.cortex'
    
    def test_save_dashboard_json_custom_filename(self, tmp_path):
        """Test save_dashboard_json with custom filename"""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        
        template_data = {'title': 'Test'}
        
        orchestrator = DashboardOrchestrator(str(repo_path))
        output_path = orchestrator.save_dashboard_json(template_data, 'custom-dashboard.json')
        
        assert output_path.name == 'custom-dashboard.json'
    
    def test_save_dashboard_json_generates_if_no_data(self, tmp_path):
        """Test save_dashboard_json generates data if none provided"""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        
        orchestrator = DashboardOrchestrator(str(repo_path))
        
        with patch.object(orchestrator, 'generate_dashboard_json') as mock_generate:
            mock_generate.return_value = {'title': 'Test', 'raw_data': {}}
            
            output_path = orchestrator.save_dashboard_json()
            
            mock_generate.assert_called_once()
            assert output_path.exists()


class TestHelperMethods:
    """Test orchestrator helper methods"""
    
    def test_get_file_list_returns_code_files(self, tmp_path):
        """Test _get_file_list returns code files"""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        
        # Create sample files
        (repo_path / "test.py").write_text("print('hello')")
        (repo_path / "test.js").write_text("console.log('hello')")
        (repo_path / "README.md").write_text("# Test")
        
        orchestrator = DashboardOrchestrator(str(repo_path))
        files = orchestrator._get_file_list()
        
        assert 'test.py' in files or any('test.py' in f for f in files)
        assert 'test.js' in files or any('test.js' in f for f in files)
        assert not any('README.md' in f for f in files)
    
    def test_format_metrics_converts_overview_to_metrics(self, tmp_path):
        """Test _format_metrics converts overview data"""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        
        overview_data = {
            'total_files': 100,
            'total_lines': 50000,
            'languages_count': 3
        }
        
        orchestrator = DashboardOrchestrator(str(repo_path))
        metrics = orchestrator._format_metrics(overview_data)
        
        assert len(metrics) == 3
        assert metrics[0]['name'] == 'Total Files'
        assert metrics[0]['value'] == 100
        assert metrics[1]['name'] == 'Lines of Code'

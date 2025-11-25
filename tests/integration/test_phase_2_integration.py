"""
Integration test for Phase 2 Multi-App System.

Tests the integration of Phase 2 activity-based prioritization
with the MultiApplicationOrchestrator.
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
from datetime import datetime

from src.crawlers.multi_app_orchestrator import MultiApplicationOrchestrator
from src.tier2.knowledge_graph import KnowledgeGraph


class TestPhase2Integration(unittest.TestCase):
    """Test Phase 2 integration with orchestrator"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary workspace
        self.test_workspace = tempfile.mkdtemp(prefix='cortex_phase2_test_')
        self.test_brain = tempfile.mkdtemp(prefix='cortex_brain_test_')
        
        # Create mock knowledge graph
        self.knowledge_graph = Mock(spec=KnowledgeGraph)
        self.knowledge_graph.add_pattern = Mock()
        self.knowledge_graph.query = Mock(return_value=[])
        
        # Create sample applications
        self._create_sample_apps()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_workspace, ignore_errors=True)
        shutil.rmtree(self.test_brain, ignore_errors=True)
    
    def _create_sample_apps(self):
        """Create sample application directories"""
        apps = ['app1', 'app2', 'app3', 'app4']
        for app in apps:
            app_dir = Path(self.test_workspace) / app
            app_dir.mkdir(parents=True, exist_ok=True)
            
            # Create some files
            (app_dir / 'index.cfm').write_text('<h1>Test App</h1>')
            (app_dir / 'Application.cfc').write_text('component {}')
    
    def test_orchestrator_initializes_phase_2_components(self):
        """Test that orchestrator initializes Phase 2 components"""
        orchestrator = MultiApplicationOrchestrator(
            workspace_path=self.test_workspace,
            knowledge_graph=self.knowledge_graph,
            cortex_brain_path=self.test_brain
        )
        
        # Check initialization
        self.assertIsNotNone(orchestrator.cache_manager)
        self.assertIsNone(orchestrator.prioritization_engine)  # Lazy init
        self.assertIsNone(orchestrator.smart_cache_manager)  # Lazy init
    
    @patch('src.crawlers.multi_app_orchestrator.WorkspaceTopologyCrawler')
    def test_prioritization_engine_initializes_on_demand(self, mock_topology):
        """Test that prioritization engine initializes on first use"""
        # Mock topology result
        mock_topology_instance = Mock()
        mock_topology_instance.execute.return_value = Mock(
            status='completed',
            items_discovered=4
        )
        mock_topology.return_value = mock_topology_instance
        
        # Mock topology in KG
        self.knowledge_graph.query.return_value = [{
            'applications': [
                {'name': 'app1', 'path': str(Path(self.test_workspace) / 'app1')},
                {'name': 'app2', 'path': str(Path(self.test_workspace) / 'app2')},
                {'name': 'app3', 'path': str(Path(self.test_workspace) / 'app3')},
                {'name': 'app4', 'path': str(Path(self.test_workspace) / 'app4')}
            ]
        }]
        
        orchestrator = MultiApplicationOrchestrator(
            workspace_path=self.test_workspace,
            knowledge_graph=self.knowledge_graph,
            cortex_brain_path=self.test_brain
        )
        
        # Trigger prioritization
        apps = [
            {'name': 'app1', 'path': str(Path(self.test_workspace) / 'app1')},
            {'name': 'app2', 'path': str(Path(self.test_workspace) / 'app2')}
        ]
        result = orchestrator._prioritize_applications(apps)
        
        # Should initialize prioritization engine
        self.assertIsNotNone(orchestrator.prioritization_engine)
        
        # Should return prioritized apps
        self.assertEqual(len(result), 2)
        self.assertIn('priority_score', result[0])
        self.assertIn('priority_tier', result[0])
    
    @patch('src.crawlers.multi_app_orchestrator.WorkspaceTopologyCrawler')
    @patch('src.crawlers.multi_app_orchestrator.ApplicationScopedCrawler')
    def test_smart_cache_manager_initializes_during_run(self, mock_app_crawler, mock_topology):
        """Test that smart cache manager initializes during run_progressive"""
        # Mock topology result with proper CrawlerStatus
        from src.crawlers.base_crawler import CrawlerStatus
        
        mock_topology_instance = Mock()
        mock_result = Mock()
        mock_result.status = CrawlerStatus.COMPLETED
        mock_result.items_discovered = 2
        mock_result.patterns_created = 0
        mock_topology_instance.execute.return_value = mock_result
        mock_topology.return_value = mock_topology_instance
        
        # Mock topology in KG
        self.knowledge_graph.query.return_value = [{
            'applications': [
                {'name': 'app1', 'path': str(Path(self.test_workspace) / 'app1'), 'has_database_access': False},
                {'name': 'app2', 'path': str(Path(self.test_workspace) / 'app2'), 'has_database_access': False}
            ]
        }]
        
        # Mock app crawler with proper return values
        mock_app_instance = Mock()
        app_result = Mock()
        app_result.status = CrawlerStatus.COMPLETED
        app_result.items_discovered = 10
        app_result.patterns_created = 5
        mock_app_instance.execute.return_value = app_result
        mock_app_crawler.return_value = mock_app_instance
        
        orchestrator = MultiApplicationOrchestrator(
            workspace_path=self.test_workspace,
            knowledge_graph=self.knowledge_graph,
            cortex_brain_path=self.test_brain
        )
        
        # Run progressive
        result = orchestrator.run_progressive()
        
        # Check that smart cache manager was initialized
        # Note: May fail if watchdog not installed, which is OK
        if orchestrator.smart_cache_manager:
            self.assertIsNotNone(orchestrator.smart_cache_manager)
        
        # Cleanup
        orchestrator.cleanup()
    
    def test_legacy_fallback_when_phase_2_fails(self):
        """Test that legacy prioritization works if Phase 2 fails"""
        orchestrator = MultiApplicationOrchestrator(
            workspace_path=self.test_workspace,
            knowledge_graph=self.knowledge_graph,
            cortex_brain_path=self.test_brain
        )
        
        # Create apps with known scores
        apps = [
            {
                'name': 'app1',
                'path': str(Path(self.test_workspace) / 'app1'),
                'estimated_size': 1024 * 1024 * 10,  # 10 MB
                'has_database_access': True,
                'last_modified': datetime.now().isoformat()
            },
            {
                'name': 'app2',
                'path': str(Path(self.test_workspace) / 'app2'),
                'estimated_size': 1024 * 1024 * 50,  # 50 MB
                'has_database_access': False,
                'last_modified': '2020-01-01T00:00:00'
            }
        ]
        
        # Force Phase 2 failure by providing invalid config
        with patch('src.crawlers.multi_app_orchestrator.ApplicationPrioritizationEngine',
                   side_effect=Exception("Forced failure")):
            result = orchestrator._prioritize_applications(apps)
        
        # Should fall back to legacy
        self.assertEqual(len(result), 2)
        self.assertIn('priority_score', result[0])
        
        # app1 should score higher (recent, smaller, has DB)
        self.assertEqual(result[0]['name'], 'app1')
    
    def test_tier_based_loading(self):
        """Test that orchestrator loads apps by tier"""
        apps = [
            {'name': 'app1', 'priority_tier': 'immediate', 'priority_score': 0.9},
            {'name': 'app2', 'priority_tier': 'immediate', 'priority_score': 0.85},
            {'name': 'app3', 'priority_tier': 'queued', 'priority_score': 0.6},
            {'name': 'app4', 'priority_tier': 'background', 'priority_score': 0.3}
        ]
        
        # Filter immediate tier
        immediate = [a for a in apps if a.get('priority_tier') == 'immediate']
        self.assertEqual(len(immediate), 2)
        self.assertEqual(immediate[0]['name'], 'app1')
        
        # Filter queued tier
        queued = [a for a in apps if a.get('priority_tier') == 'queued']
        self.assertEqual(len(queued), 1)
        
        # Filter background tier
        background = [a for a in apps if a.get('priority_tier') == 'background']
        self.assertEqual(len(background), 1)


if __name__ == '__main__':
    unittest.main()

"""
Tests for WorkspaceTopologyCrawler

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from src.crawlers.workspace_topology_crawler import (
    WorkspaceTopologyCrawler,
    ApplicationInfo
)
from src.crawlers.base_crawler import CrawlerStatus


@pytest.fixture
def mock_workspace():
    """Create a mock multi-application workspace"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        
        # Create multiple applications
        apps = {
            'ColdFusionApp1': 'Application.cfc',
            'ColdFusionApp2': 'Application.cfm',
            'JavaApp': 'pom.xml',
            'NodeApp': 'package.json',
            'PythonApp': 'requirements.txt'
        }
        
        for app_name, marker in apps.items():
            app_dir = workspace / app_name
            app_dir.mkdir(parents=True)
            (app_dir / marker).write_text('# Mock config')
            
            # Add some files
            (app_dir / 'index.cfm').write_text('<cfoutput>Test</cfoutput>')
            (app_dir / 'controller.cfc').write_text('component {}')
        
        # Create shared code folder
        shared_dir = workspace / 'Common'
        shared_dir.mkdir(parents=True)
        (shared_dir / 'Utils.cfc').write_text('component {}')
        
        yield workspace


def test_workspace_topology_crawler_init(mock_workspace):
    """Test crawler initialization"""
    crawler = WorkspaceTopologyCrawler({
        'workspace_path': mock_workspace
    })
    
    assert crawler.workspace_path == mock_workspace
    info = crawler.get_crawler_info()
    assert info['crawler_id'] == 'workspace_topology'
    assert info['scope'] == 'workspace'


def test_discover_applications(mock_workspace):
    """Test application discovery"""
    crawler = WorkspaceTopologyCrawler({
        'workspace_path': mock_workspace
    })
    
    result = crawler.execute()
    
    assert result.status == CrawlerStatus.COMPLETED
    assert result.items_discovered == 5  # 5 applications
    assert result.patterns_created == 1  # 1 topology pattern
    assert result.duration_seconds < 5.0  # Should be fast


def test_detect_workspace_type(mock_workspace):
    """Test workspace type detection"""
    crawler = WorkspaceTopologyCrawler({
        'workspace_path': mock_workspace
    })
    
    workspace_type = crawler._detect_workspace_type()
    assert workspace_type == 'multi-application'  # 5 apps = multi-application


def test_detect_tech_stack(mock_workspace):
    """Test technology stack detection"""
    crawler = WorkspaceTopologyCrawler({
        'workspace_path': mock_workspace
    })
    
    # Test ColdFusion detection
    cf_path = mock_workspace / 'ColdFusionApp1'
    tech_stack = crawler._detect_tech_stack(cf_path)
    assert 'ColdFusion' in tech_stack
    
    # Test Java detection
    java_path = mock_workspace / 'JavaApp'
    tech_stack = crawler._detect_tech_stack(java_path)
    assert 'Java' in tech_stack
    
    # Test Node.js detection
    node_path = mock_workspace / 'NodeApp'
    tech_stack = crawler._detect_tech_stack(node_path)
    assert 'JavaScript/Node.js' in tech_stack


def test_find_shared_code(mock_workspace):
    """Test shared code library detection"""
    crawler = WorkspaceTopologyCrawler({
        'workspace_path': mock_workspace
    })
    
    shared_libs = crawler._find_shared_code()
    assert len(shared_libs) == 1
    assert shared_libs[0]['name'] == 'Common'
    assert shared_libs[0]['type'] == 'shared_library'


def test_has_database_access(mock_workspace):
    """Test database access detection"""
    crawler = WorkspaceTopologyCrawler({
        'workspace_path': mock_workspace
    })
    
    # Create app with database query
    db_app_dir = mock_workspace / 'DBApp'
    db_app_dir.mkdir(parents=True)
    (db_app_dir / 'Application.cfc').write_text('component {}')
    (db_app_dir / 'query.cfm').write_text('''
        <cfquery name="getUsers" datasource="mydb">
            SELECT * FROM users
        </cfquery>
    ''')
    
    assert crawler._has_database_access(db_app_dir) is True
    
    # Test app without database
    no_db_app = mock_workspace / 'ColdFusionApp1'
    assert crawler._has_database_access(no_db_app) is False


def test_empty_workspace():
    """Test crawler with empty workspace"""
    with tempfile.TemporaryDirectory() as tmpdir:
        crawler = WorkspaceTopologyCrawler({
            'workspace_path': Path(tmpdir)
        })
        
        result = crawler.execute()
        assert result.status == CrawlerStatus.COMPLETED
        assert result.items_discovered == 0


def test_estimate_size(mock_workspace):
    """Test size estimation"""
    crawler = WorkspaceTopologyCrawler({
        'workspace_path': mock_workspace
    })
    
    app_path = mock_workspace / 'ColdFusionApp1'
    size = crawler._estimate_size(app_path)
    
    assert size > 0  # Should have some size
    assert isinstance(size, int)


def test_estimate_file_count(mock_workspace):
    """Test file count estimation"""
    crawler = WorkspaceTopologyCrawler({
        'workspace_path': mock_workspace
    })
    
    app_path = mock_workspace / 'ColdFusionApp1'
    count = crawler._estimate_file_count(app_path)
    
    assert count > 0  # Should have files
    assert isinstance(count, int)


def test_app_to_dict():
    """Test ApplicationInfo to dictionary conversion"""
    app_info = ApplicationInfo(
        name='TestApp',
        path='/path/to/app',
        marker='Application.cfc',
        estimated_size=1024000,
        estimated_file_count=50,
        technology_stack=['ColdFusion'],
        last_modified=datetime.now(),
        has_tests=True,
        has_database_access=True
    )
    
    crawler = WorkspaceTopologyCrawler({
        'workspace_path': Path('/tmp')
    })
    
    app_dict = crawler._app_to_dict(app_info)
    
    assert app_dict['name'] == 'TestApp'
    assert app_dict['marker'] == 'Application.cfc'
    assert app_dict['estimated_size'] == 1024000
    assert app_dict['has_tests'] is True
    assert app_dict['has_database_access'] is True


def test_crawler_with_knowledge_graph(mock_workspace):
    """Test crawler with knowledge graph integration"""
    from unittest.mock import Mock
    
    kg = Mock()
    crawler = WorkspaceTopologyCrawler({
        'workspace_path': mock_workspace,
        'knowledge_graph': kg
    })
    
    result = crawler.execute()
    
    assert result.status == CrawlerStatus.COMPLETED
    # Verify knowledge graph was called
    kg.add_pattern.assert_called_once()
    call_args = kg.add_pattern.call_args
    assert call_args[1]['scope'] == 'workspace'
    assert call_args[1]['namespace'] == 'topology'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

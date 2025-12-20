"""
Onboarding Tab Browser Integration Tests

Tests the JavaScript data loading and initialization workflow to address
the console errors shown in the dashboard (Unknown data source: luum-fresh).

These tests simulate browser-side behavior and validate the data loader
can correctly fetch and initialize onboarding data from the luum-fresh repository.

Author: Asif Hussain
Version: 1.0.0
Created: 2025-12-07
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Test data paths
DASHBOARD_DATA_PATH = Path(__file__).parent.parent.parent / "cortex-brain" / "dashboards" / "data"
DASHBOARD_UI_PATH = Path(__file__).parent.parent.parent / "cortex-brain" / "dashboards" / "ui"
REPOS_PATH = DASHBOARD_DATA_PATH / "repos"
LUUM_FRESH_PATH = REPOS_PATH / "luum-fresh"


class TestDataSourceRegistry:
    """Test the repository registry and data source discovery"""
    
    def test_repository_registry_exists(self):
        """Verify repository-registry.json exists"""
        registry_path = DASHBOARD_DATA_PATH / "repository-registry.json"
        assert registry_path.exists(), "repository-registry.json not found"
        
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        assert 'repositories' in registry, "Missing repositories array"
        assert 'total_repositories' in registry, "Missing total_repositories count"
    
    def test_luum_fresh_in_registry(self):
        """Verify luum-fresh is registered in repository-registry.json"""
        registry_path = DASHBOARD_DATA_PATH / "repository-registry.json"
        
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        # Check if luum-fresh is in the registry
        repo_ids = [repo['id'] for repo in registry['repositories']]
        assert 'luum-fresh' in repo_ids, "luum-fresh not found in repository registry"
        
        # Get luum-fresh entry
        luum_fresh_entry = next(
            (repo for repo in registry['repositories'] if repo['id'] == 'luum-fresh'),
            None
        )
        
        assert luum_fresh_entry is not None, "luum-fresh entry not found"
        # Note: Registry uses lowercase 'luum-fresh' as name, display name 'Luum Fresh' is in overview.json
        assert luum_fresh_entry['name'] == 'luum-fresh', f"Expected name 'luum-fresh', got {luum_fresh_entry['name']}"
        assert luum_fresh_entry['status'] == 'active', f"Expected status 'active', got {luum_fresh_entry['status']}"
    
    def test_data_source_path_construction(self):
        """Test that data source paths are correctly constructed"""
        # Simulate JavaScript data loader path construction
        repo_id = 'luum-fresh'
        expected_path = f"/data/repos/{repo_id}/"
        
        # Verify the path maps to actual files
        actual_path = REPOS_PATH / repo_id
        assert actual_path.exists(), f"Data path {actual_path} does not exist"
        assert actual_path.is_dir(), f"Data path {actual_path} is not a directory"


class TestDataLoaderSimulation:
    """Simulate the JavaScript data-loader.js behavior"""
    
    def test_available_data_sources(self):
        """Test that all available data sources can be discovered"""
        # Mock the available sources from registry
        registry_path = DASHBOARD_DATA_PATH / "repository-registry.json"
        
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        # Simulate DATA_SOURCES construction (from data-loader.js line 56)
        data_sources = {'mock': '../data/repos/mock/'}
        
        for repo in registry['repositories']:
            data_sources[repo['id']] = f"/data/repos/{repo['id']}/"
        
        # Verify luum-fresh is available
        assert 'luum-fresh' in data_sources, "luum-fresh not in DATA_SOURCES"
        print(f"Available sources: {list(data_sources.keys())}")
    
    def test_load_dashboard_data_simulation(self):
        """Simulate loadDashboardData('luum-fresh') function"""
        source = 'luum-fresh'
        
        # Simulate the data files to load (from data-loader.js line 26)
        data_files = [
            'overview.json',
            'executive-summary.json',
            'health-data.json',
            'tech-stack.json',
            'security.json',
            'architecture.json',
            'code-organization.json',
            'vendors.json',
            'reconciliation.json'
        ]
        
        # Verify each file exists
        missing_files = []
        available_files = []
        
        for filename in data_files:
            file_path = LUUM_FRESH_PATH / filename
            if file_path.exists():
                available_files.append(filename)
            else:
                missing_files.append(filename)
        
        # Print results
        print(f"\nAvailable files for {source}:")
        for f in available_files:
            print(f"  ✓ {f}")
        
        if missing_files:
            print(f"\nMissing files:")
            for f in missing_files:
                print(f"  ✗ {f}")
        
        # At minimum, overview.json should exist
        assert 'overview.json' in available_files, "overview.json is required but missing"
        assert len(available_files) >= 5, f"Expected at least 5 files, found {len(available_files)}"
    
    def test_onboarding_data_enrichment(self):
        """Test enriching dashboard data for onboarding tab"""
        # Load base dashboard data
        overview_path = LUUM_FRESH_PATH / 'overview.json'
        tech_stack_path = LUUM_FRESH_PATH / 'tech-stack.json'
        architecture_path = LUUM_FRESH_PATH / 'architecture.json'
        
        with open(overview_path, 'r', encoding='utf-8') as f:
            overview = json.load(f)
        with open(tech_stack_path, 'r', encoding='utf-8') as f:
            tech_stack = json.load(f)
        with open(architecture_path, 'r', encoding='utf-8') as f:
            architecture = json.load(f)
        
        # Simulate enrichDashboardData function for onboarding
        enriched_data = {
            'overview': overview,
            'tech_stack': tech_stack,
            'architecture': architecture,
            'onboarding': {
                'metadata': {
                    'repository': overview.get('project_name', 'Unknown'),
                    'total_files': overview.get('key_metrics', {}).get('total_files', 0),
                    'total_loc': overview.get('key_metrics', {}).get('total_loc', 0),
                    'health_score': overview.get('overall_health', {}).get('score', 0),
                    'technologies': [
                        tech['name'] for tech in tech_stack.get('backend', [])
                    ]
                },
                'stages': self.generate_onboarding_stages(overview, tech_stack, architecture)
            }
        }
        
        # Validate enriched data
        assert 'onboarding' in enriched_data, "Missing onboarding data"
        assert enriched_data['onboarding']['metadata']['repository'] == 'Luum Fresh'
        assert len(enriched_data['onboarding']['stages']) > 0, "No onboarding stages generated"
    
    def generate_onboarding_stages(self, overview, tech_stack, architecture):
        """Generate onboarding stages from repository data"""
        stages = [
            {
                'id': 1,
                'title': 'Project Overview',
                'description': f"Welcome to {overview.get('project_name', 'this project')}",
                'duration_minutes': 15,
                'content': {
                    'project_name': overview.get('project_name'),
                    'health_score': overview.get('overall_health', {}).get('score'),
                    'total_files': overview.get('key_metrics', {}).get('total_files'),
                    'total_loc': overview.get('key_metrics', {}).get('total_loc')
                }
            },
            {
                'id': 2,
                'title': 'Technology Stack',
                'description': 'Understanding the technologies used',
                'duration_minutes': 20,
                'content': {
                    'backend': tech_stack.get('backend', []),
                    'frontend': tech_stack.get('frontend', [])
                }
            },
            {
                'id': 3,
                'title': 'Architecture Overview',
                'description': 'How the system is structured',
                'duration_minutes': 25,
                'content': {
                    'app_type': architecture.get('application_type', {}).get('type'),
                    'style': architecture.get('style', {}).get('name'),
                    'tiers': architecture.get('tiers', [])
                }
            }
        ]
        
        return stages


class TestConsoleErrorReproduction:
    """Reproduce and fix the console errors from the screenshot"""
    
    def test_unknown_data_source_error(self):
        """Test the 'Unknown data source: luum-fresh' error"""
        # This error occurs when data-loader.js doesn't have luum-fresh in DATA_SOURCES
        
        # Load registry
        registry_path = DASHBOARD_DATA_PATH / "repository-registry.json"
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        # Simulate DATA_SOURCES construction
        data_sources = {'mock': '../data/repos/mock/'}
        for repo in registry['repositories']:
            data_sources[repo['id']] = f"/data/repos/{repo['id']}/"
        
        # Test: Can we find luum-fresh?
        source = 'luum-fresh'
        available_sources = list(data_sources.keys())
        
        print(f"\nAvailable sources: {available_sources}")
        print(f"Looking for: {source}")
        
        # The error happens if source not in DATA_SOURCES
        assert source in data_sources, f"Source '{source}' not found. Available: {available_sources}"
    
    def test_failed_to_load_data_error(self):
        """Test the 'Failed to load data' error"""
        # This error occurs in app.js:225 when loadDashboardData fails
        
        source = 'luum-fresh'
        
        # Verify the data path exists
        data_path = REPOS_PATH / source
        assert data_path.exists(), f"Data path does not exist: {data_path}"
        
        # Verify required files exist
        required_files = ['overview.json', 'tech-stack.json', 'architecture.json']
        for filename in required_files:
            file_path = data_path / filename
            assert file_path.exists(), f"Required file missing: {filename}"
            
            # Verify file is valid JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    json.load(f)
                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid JSON in {filename}: {e}")
    
    def test_failed_to_initialize_dashboard_error(self):
        """Test the 'Failed to initialize dashboard' error"""
        # This error occurs in app.js:94 when initializeApp() fails
        
        # Check if all necessary files exist
        ui_files = [
            'index.html',
            'app.js',
            'data-loader.js',
            'components/onboarding-tab.js'
        ]
        
        for filename in ui_files:
            file_path = DASHBOARD_UI_PATH / filename
            assert file_path.exists(), f"Missing UI file: {filename}"
    
    def test_no_data_available_to_render_error(self):
        """Test the 'No data available to render' warning"""
        # This occurs in app.js:240 when data is null/undefined
        
        # Simulate the condition
        data = None
        
        # The warning should trigger if data is null
        # But we should have data available
        
        # Load actual data
        overview_path = LUUM_FRESH_PATH / 'overview.json'
        if overview_path.exists():
            with open(overview_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        assert data is not None, "Data should be available for luum-fresh"
        assert 'project_name' in data, "Data should contain project information"


class TestOnboardingTabInitialization:
    """Test the onboarding tab initialization workflow"""
    
    def test_onboarding_tab_component_exists(self):
        """Verify onboarding-tab.js component exists"""
        component_path = DASHBOARD_UI_PATH / 'components' / 'onboarding-tab.js'
        assert component_path.exists(), "onboarding-tab.js component not found"
        
        # Read the file
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key class/function definitions
        assert 'class OnboardingTab' in content or 'OnboardingTab' in content, \
            "OnboardingTab class not found in component"
    
    def test_onboarding_tab_data_requirements(self):
        """Test that onboarding tab has all required data"""
        # Onboarding tab needs:
        # 1. Project metadata
        # 2. Technology stack
        # 3. Architecture information
        # 4. Health metrics
        
        required_data_files = [
            'overview.json',      # Project metadata, health
            'tech-stack.json',    # Technologies
            'architecture.json'   # Architecture, tiers
        ]
        
        for filename in required_data_files:
            file_path = LUUM_FRESH_PATH / filename
            assert file_path.exists(), f"Required data file missing: {filename}"
    
    def test_onboarding_stages_generation(self):
        """Test generating onboarding stages from luum-fresh data"""
        # Load source data
        overview_path = LUUM_FRESH_PATH / 'overview.json'
        tech_stack_path = LUUM_FRESH_PATH / 'tech-stack.json'
        architecture_path = LUUM_FRESH_PATH / 'architecture.json'
        
        with open(overview_path, 'r') as f:
            overview = json.load(f)
        with open(tech_stack_path, 'r') as f:
            tech_stack = json.load(f)
        with open(architecture_path, 'r') as f:
            architecture = json.load(f)
        
        # Generate onboarding data structure
        onboarding_data = {
            'metadata': {
                'repository': overview['project_name'],
                'total_files': overview['key_metrics']['total_files'],
                'health_score': overview['overall_health']['score']
            },
            'stages': [
                {
                    'id': 1,
                    'title': 'Project Overview',
                    'content': {
                        'project_name': overview['project_name'],
                        'health_score': overview['overall_health']['score'],
                        'health_status': overview['overall_health']['status']
                    }
                },
                {
                    'id': 2,
                    'title': 'Technology Stack',
                    'content': {
                        'backend': tech_stack['backend'],
                        'frontend': tech_stack['frontend']
                    }
                },
                {
                    'id': 3,
                    'title': 'Architecture',
                    'content': {
                        'app_type': architecture['application_type']['type'],
                        'style': architecture['style']['name']
                    }
                }
            ]
        }
        
        # Validate structure
        assert onboarding_data['metadata']['repository'] == 'Luum Fresh'
        assert onboarding_data['metadata']['total_files'] == 10391
        assert len(onboarding_data['stages']) == 3
        
        # Validate each stage has required fields
        for stage in onboarding_data['stages']:
            assert 'id' in stage
            assert 'title' in stage
            assert 'content' in stage


class TestDataValidationAgainstSchema:
    """Validate luum-fresh data against expected schema"""
    
    def test_overview_schema_compliance(self):
        """Validate overview.json matches expected schema"""
        overview_path = LUUM_FRESH_PATH / 'overview.json'
        
        with open(overview_path, 'r') as f:
            overview = json.load(f)
        
        # Required fields
        required_fields = {
            'project_name': str,
            'overall_health': dict,
            'key_metrics': dict,
            'health_categories': list
        }
        
        for field, expected_type in required_fields.items():
            assert field in overview, f"Missing required field: {field}"
            assert isinstance(overview[field], expected_type), \
                f"Field {field} should be {expected_type}, got {type(overview[field])}"
        
        # Validate nested structures
        assert 'score' in overview['overall_health']
        assert 'status' in overview['overall_health']
        assert 'total_files' in overview['key_metrics']
        assert 'total_loc' in overview['key_metrics']
    
    def test_tech_stack_schema_compliance(self):
        """Validate tech-stack.json matches expected schema"""
        tech_stack_path = LUUM_FRESH_PATH / 'tech-stack.json'
        
        with open(tech_stack_path, 'r') as f:
            tech_stack = json.load(f)
        
        # Required sections
        required_sections = ['frontend', 'backend', 'summary']
        
        for section in required_sections:
            assert section in tech_stack, f"Missing required section: {section}"
        
        # Validate technology objects have required fields
        for tech in tech_stack['backend']:
            assert 'name' in tech
            assert 'version' in tech
            assert 'category' in tech


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])

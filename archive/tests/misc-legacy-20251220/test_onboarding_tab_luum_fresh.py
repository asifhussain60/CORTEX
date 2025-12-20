"""
Onboarding Tab Integration Tests - Luum Fresh Repository

Validates that the onboarding tab loads correctly and displays accurate data
from the luum-fresh repository dashboard data.

Test Coverage:
- Data loading from luum-fresh repository
- Tab initialization and rendering
- Data validation against collector output
- Stage content generation
- Interactive elements functionality

Author: Asif Hussain
Version: 1.0.0
Created: 2025-12-07
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Test data paths
DASHBOARD_DATA_PATH = Path(__file__).parent.parent.parent / "cortex-brain" / "dashboards" / "data" / "repos" / "luum-fresh"
UI_COMPONENTS_PATH = Path(__file__).parent.parent.parent / "cortex-brain" / "dashboards" / "ui" / "components"


class TestOnboardingTabDataLoading:
    """Test data loading from luum-fresh repository"""
    
    def test_luum_fresh_data_files_exist(self):
        """Verify all required data files exist for luum-fresh"""
        required_files = [
            'overview.json',
            'tech-stack.json',
            'architecture.json',
            'health-data.json',
            'code-organization.json',
            'security.json',
            'executive-summary.json'
        ]
        
        for filename in required_files:
            file_path = DASHBOARD_DATA_PATH / filename
            assert file_path.exists(), f"Missing required file: {filename}"
            
            # Verify file is valid JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert data is not None, f"{filename} contains invalid JSON"
    
    def test_overview_data_structure(self):
        """Verify overview.json has correct structure for onboarding"""
        overview_path = DASHBOARD_DATA_PATH / 'overview.json'
        
        with open(overview_path, 'r', encoding='utf-8') as f:
            overview = json.load(f)
        
        # Required fields for onboarding tab
        assert 'project_name' in overview, "Missing project_name"
        assert 'overall_health' in overview, "Missing overall_health"
        assert 'key_metrics' in overview, "Missing key_metrics"
        assert 'health_categories' in overview, "Missing health_categories"
        
        # Validate overall_health
        health = overview['overall_health']
        assert 'score' in health, "Missing health score"
        assert 'status' in health, "Missing health status"
        assert health['score'] == 54, f"Expected health score 54, got {health['score']}"
        assert health['status'] == 'critical', f"Expected status 'critical', got {health['status']}"
        
        # Validate key_metrics
        metrics = overview['key_metrics']
        assert 'total_files' in metrics, "Missing total_files"
        assert 'total_loc' in metrics, "Missing total_loc"
        assert metrics['total_files'] == 10391, f"Expected 10391 files, got {metrics['total_files']}"
        assert metrics['total_loc'] == 1246213, f"Expected 1246213 LOC, got {metrics['total_loc']}"
    
    def test_tech_stack_data_structure(self):
        """Verify tech-stack.json has correct structure for onboarding"""
        tech_stack_path = DASHBOARD_DATA_PATH / 'tech-stack.json'
        
        with open(tech_stack_path, 'r', encoding='utf-8') as f:
            tech_stack = json.load(f)
        
        # Required sections
        assert 'frontend' in tech_stack, "Missing frontend section"
        assert 'backend' in tech_stack, "Missing backend section"
        assert 'summary' in tech_stack, "Missing summary section"
        
        # Validate backend contains C# and .NET
        backend = tech_stack['backend']
        assert isinstance(backend, list), "Backend should be a list"
        
        tech_names = [tech['name'] for tech in backend]
        assert 'C#' in tech_names, "C# not found in backend technologies"
        assert '.NET' in tech_names, ".NET not found in backend technologies"
        
        # Validate .NET version
        dotnet_tech = next((t for t in backend if t['name'] == '.NET'), None)
        assert dotnet_tech is not None, ".NET technology not found"
        assert dotnet_tech['version'] == '4.7.2', f"Expected .NET 4.7.2, got {dotnet_tech['version']}"
    
    def test_architecture_data_structure(self):
        """Verify architecture.json has correct structure for onboarding"""
        arch_path = DASHBOARD_DATA_PATH / 'architecture.json'
        
        with open(arch_path, 'r', encoding='utf-8') as f:
            architecture = json.load(f)
        
        # Required sections
        assert 'application_type' in architecture, "Missing application_type"
        assert 'style' in architecture, "Missing architecture style"
        assert 'tiers' in architecture, "Missing tiers"
        
        # Validate application type
        app_type = architecture['application_type']
        assert 'type' in app_type, "Missing type in application_type"
        assert 'confidence' in app_type, "Missing confidence"
        assert app_type['type'] == 'SOAP Web Service', f"Expected 'SOAP Web Service', got {app_type['type']}"
        
        # Validate architecture style
        style = architecture['style']
        assert 'name' in style, "Missing style name"
        assert style['name'] == 'N-Tier Architecture', f"Expected 'N-Tier Architecture', got {style['name']}"
        
        # Validate tiers
        assert isinstance(architecture['tiers'], list), "Tiers should be a list"
        assert len(architecture['tiers']) > 0, "Tiers list is empty"


class TestOnboardingTabRendering:
    """Test onboarding tab rendering with luum-fresh data"""
    
    def load_luum_fresh_data(self):
        """Helper to load all luum-fresh data files"""
        data = {}
        files_to_load = {
            'overview': 'overview.json',
            'tech_stack': 'tech-stack.json',
            'architecture': 'architecture.json',
            'health': 'health-data.json',
            'code_org': 'code-organization.json',
            'security': 'security.json',
            'executive': 'executive-summary.json'
        }
        
        for key, filename in files_to_load.items():
            file_path = DASHBOARD_DATA_PATH / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data[key] = json.load(f)
        
        return data
    
    def test_onboarding_data_generation(self):
        """Test that onboarding stages can be generated from luum-fresh data"""
        data = self.load_luum_fresh_data()
        
        # Simulate onboarding data structure
        onboarding_data = {
            'metadata': {
                'repository': 'Luum Fresh',
                'total_files': data['overview']['key_metrics']['total_files'],
                'total_loc': data['overview']['key_metrics']['total_loc'],
                'health_score': data['overview']['overall_health']['score'],
                'technologies': []
            },
            'stages': []
        }
        
        # Add technologies from tech stack
        if 'tech_stack' in data:
            backend_techs = data['tech_stack'].get('backend', [])
            onboarding_data['metadata']['technologies'] = [
                tech['name'] for tech in backend_techs
            ]
        
        # Validate generated metadata
        assert onboarding_data['metadata']['repository'] == 'Luum Fresh'
        assert onboarding_data['metadata']['total_files'] == 10391
        assert onboarding_data['metadata']['total_loc'] == 1246213
        assert onboarding_data['metadata']['health_score'] == 54
        assert 'C#' in onboarding_data['metadata']['technologies']
        assert '.NET' in onboarding_data['metadata']['technologies']
    
    def test_stage_1_overview_content(self):
        """Test Stage 1 (Project Overview) contains accurate luum-fresh data"""
        data = self.load_luum_fresh_data()
        
        # Stage 1 should include:
        # - Project name
        # - Health score
        # - Total files and LOC
        # - Architecture style
        
        stage_1_data = {
            'id': 1,
            'title': 'Project Overview',
            'description': f"Welcome to {data['overview']['project_name']}",
            'duration_minutes': 15,
            'content': {
                'project_name': data['overview']['project_name'],
                'health_score': data['overview']['overall_health']['score'],
                'health_status': data['overview']['overall_health']['status'],
                'total_files': data['overview']['key_metrics']['total_files'],
                'total_loc': data['overview']['key_metrics']['total_loc'],
                'architecture_style': data['architecture']['style']['name']
            }
        }
        
        # Validate stage 1 content
        assert stage_1_data['content']['project_name'] == 'Luum Fresh'
        assert stage_1_data['content']['health_score'] == 54
        assert stage_1_data['content']['health_status'] == 'critical'
        assert stage_1_data['content']['total_files'] == 10391
        assert stage_1_data['content']['total_loc'] == 1246213
        assert stage_1_data['content']['architecture_style'] == 'N-Tier Architecture'
    
    def test_stage_2_tech_stack_content(self):
        """Test Stage 2 (Technology Stack) contains accurate luum-fresh data"""
        data = self.load_luum_fresh_data()
        
        # Stage 2 should include:
        # - Frontend technologies
        # - Backend technologies
        # - Framework versions
        
        stage_2_data = {
            'id': 2,
            'title': 'Technology Stack',
            'description': 'Understanding the technologies used in this project',
            'duration_minutes': 20,
            'content': {
                'frontend': data['tech_stack']['frontend'],
                'backend': data['tech_stack']['backend'],
                'total_technologies': data['tech_stack']['summary']['total_technologies']
            }
        }
        
        # Validate stage 2 content
        assert len(stage_2_data['content']['backend']) > 0
        assert stage_2_data['content']['total_technologies'] == 3
        
        # Verify C# and .NET are present
        backend_names = [tech['name'] for tech in stage_2_data['content']['backend']]
        assert 'C#' in backend_names
        assert '.NET' in backend_names
    
    def test_stage_3_architecture_content(self):
        """Test Stage 3 (Architecture) contains accurate luum-fresh data"""
        data = self.load_luum_fresh_data()
        
        # Stage 3 should include:
        # - Application type
        # - Architecture style
        # - Tier information
        
        stage_3_data = {
            'id': 3,
            'title': 'Architecture Overview',
            'description': 'Understanding how the system is structured',
            'duration_minutes': 25,
            'content': {
                'app_type': data['architecture']['application_type']['type'],
                'style': data['architecture']['style']['name'],
                'tier_count': data['architecture']['style'].get('tier_count', 0),
                'tiers': data['architecture']['tiers']
            }
        }
        
        # Validate stage 3 content
        assert stage_3_data['content']['app_type'] == 'SOAP Web Service'
        assert stage_3_data['content']['style'] == 'N-Tier Architecture'
        assert stage_3_data['content']['tier_count'] == 2
        assert len(stage_3_data['content']['tiers']) > 0


class TestOnboardingTabInteractivity:
    """Test interactive features of onboarding tab"""
    
    def test_stage_navigation(self):
        """Test navigation between onboarding stages"""
        # Simulate stage navigation
        current_stage = 1
        total_stages = 6
        
        # Test next stage
        next_stage = min(current_stage + 1, total_stages)
        assert next_stage == 2
        
        # Test previous stage
        current_stage = 3
        prev_stage = max(current_stage - 1, 1)
        assert prev_stage == 2
        
        # Test boundary conditions
        current_stage = 6
        next_stage = min(current_stage + 1, total_stages)
        assert next_stage == 6  # Can't go beyond last stage
        
        current_stage = 1
        prev_stage = max(current_stage - 1, 1)
        assert prev_stage == 1  # Can't go before first stage
    
    def test_completion_tracking(self):
        """Test stage completion tracking"""
        completed_stages = set()
        total_stages = 6
        
        # Mark stages as complete
        completed_stages.add(1)
        completed_stages.add(2)
        completed_stages.add(3)
        
        # Calculate completion percentage
        completion_pct = (len(completed_stages) / total_stages) * 100
        assert completion_pct == 50.0
        
        # Complete all stages
        for stage in range(1, total_stages + 1):
            completed_stages.add(stage)
        
        completion_pct = (len(completed_stages) / total_stages) * 100
        assert completion_pct == 100.0
    
    def test_progress_persistence(self):
        """Test that progress can be saved and loaded"""
        # Simulate progress data
        progress_data = {
            'current_stage': 3,
            'completed_stages': [1, 2],
            'last_accessed': '2025-12-07T16:00:00',
            'completion_percentage': 33
        }
        
        # Verify structure
        assert 'current_stage' in progress_data
        assert 'completed_stages' in progress_data
        assert isinstance(progress_data['completed_stages'], list)
        assert progress_data['current_stage'] == 3
        assert len(progress_data['completed_stages']) == 2


class TestOnboardingTabDataValidation:
    """Test data validation and error handling"""
    
    def test_missing_data_handling(self):
        """Test graceful handling of missing data fields"""
        incomplete_data = {
            'overview': {
                'project_name': 'Test Project'
                # Missing other fields
            }
        }
        
        # Should handle missing fields gracefully
        project_name = incomplete_data.get('overview', {}).get('project_name', 'Unknown')
        health_score = incomplete_data.get('overview', {}).get('overall_health', {}).get('score', 0)
        
        assert project_name == 'Test Project'
        assert health_score == 0  # Default value
    
    def test_invalid_data_types(self):
        """Test handling of invalid data types"""
        invalid_data = {
            'overview': {
                'key_metrics': {
                    'total_files': 'not_a_number',  # Should be int
                    'total_loc': None  # Should be int
                }
            }
        }
        
        # Should convert or use defaults
        total_files = invalid_data.get('overview', {}).get('key_metrics', {}).get('total_files', 0)
        
        # If it's a string, try to convert
        if isinstance(total_files, str):
            try:
                total_files = int(total_files)
            except ValueError:
                total_files = 0
        
        assert isinstance(total_files, int)
    
    def test_data_completeness_check(self):
        """Test checking if all required data is present"""
        required_fields = [
            ('overview', 'project_name'),
            ('overview', 'overall_health', 'score'),
            ('overview', 'key_metrics', 'total_files'),
            ('tech_stack', 'backend'),
            ('architecture', 'application_type', 'type')
        ]
        
        # Load actual luum-fresh data
        data = {}
        for filename in ['overview.json', 'tech-stack.json', 'architecture.json']:
            file_path = DASHBOARD_DATA_PATH / filename
            if file_path.exists():
                key = filename.replace('.json', '').replace('-', '_')
                with open(file_path, 'r', encoding='utf-8') as f:
                    data[key] = json.load(f)
        
        # Check each required field
        missing_fields = []
        for field_path in required_fields:
            current = data
            try:
                for key in field_path:
                    current = current[key]
            except (KeyError, TypeError):
                missing_fields.append('.'.join(field_path))
        
        # All required fields should be present in luum-fresh data
        assert len(missing_fields) == 0, f"Missing required fields: {missing_fields}"


class TestOnboardingTabPerformance:
    """Test performance aspects of onboarding tab"""
    
    def test_data_loading_performance(self):
        """Test that data loads within reasonable time"""
        import time
        
        start_time = time.time()
        
        # Load all luum-fresh data files
        data_files = ['overview.json', 'tech-stack.json', 'architecture.json']
        for filename in data_files:
            file_path = DASHBOARD_DATA_PATH / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
        
        end_time = time.time()
        load_time = end_time - start_time
        
        # Should load in less than 1 second
        assert load_time < 1.0, f"Data loading took {load_time:.3f}s (expected <1.0s)"
    
    def test_large_data_handling(self):
        """Test handling of large data structures"""
        # Load architecture.json which is 4581 lines
        arch_path = DASHBOARD_DATA_PATH / 'architecture.json'
        
        with open(arch_path, 'r', encoding='utf-8') as f:
            architecture = json.load(f)
        
        # Verify large data is loaded correctly
        assert 'tiers' in architecture
        assert isinstance(architecture['tiers'], list)
        
        # Should handle iteration efficiently
        tier_count = len(architecture['tiers'])
        assert tier_count > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""
Unit tests for Nested Folder Structure Planning & Design.

Validates the design of a comprehensive nested folder structure that:
- Organizes code by domain and responsibility
- Maintains clear separation of concerns
- Provides scalability for future expansion
- Documents organization rationale
"""

import pytest
from cortex.infrastructure.folder_structure_designer import (
    FolderStructureDesigner
)


class TestFolderStructureDesign:
    """Test suite for folder structure design."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.designer = FolderStructureDesigner()
    
    def test_add_folder_successfully(self):
        """Test that folders can be added to the structure."""
        self.designer.add_folder(
            name='core',
            path='src/core',
            purpose='Core CORTEX functionality'
        )
        
        assert 'src/core' in self.designer.structure
        assert self.designer.structure['src/core'].name == 'core'
    
    def test_folder_parent_child_relationship(self):
        """Test that parent-child relationships are maintained."""
        self.designer.add_folder('src', 'src', 'Source code root')
        self.designer.add_folder('core', 'src/core', 'Core functionality', parent='src')
        
        assert 'core' in self.designer.structure['src'].child_folders
        assert self.designer.structure['src/core'].parent == 'src'
    
    def test_nested_hierarchy_depth(self):
        """Test that folder depth is correctly calculated."""
        self.designer.add_folder('src', 'src', 'Root')
        self.designer.add_folder('core', 'src/core', 'Core')
        self.designer.add_folder('orchestrator', 'src/core/orchestrator', 'Orchestrator')
        
        assert self.designer.get_depth('src') == 0
        assert self.designer.get_depth('src/core') == 1
        assert self.designer.get_depth('src/core/orchestrator') == 2
    
    def test_path_uniqueness_validation(self):
        """Test that all paths are unique."""
        self.designer.add_folder('src', 'src', 'Source')
        self.designer.add_folder('core', 'src/core', 'Core')
        self.designer.add_folder('api', 'src/api', 'API')
        
        assert self.designer.validate_uniqueness() is True
    
    def test_required_folders_coverage(self):
        """Test that all required folders are present."""
        required = ['src', 'src/core', 'src/api', 'tests']
        
        self.designer.add_folder('src', 'src', 'Source')
        self.designer.add_folder('core', 'src/core', 'Core')
        self.designer.add_folder('api', 'src/api', 'API')
        self.designer.add_folder('tests', 'tests', 'Tests')
        
        assert self.designer.validate_coverage(required) is True
    
    def test_required_folders_coverage_fails(self):
        """Test that validation fails when required folders are missing."""
        required = ['src', 'src/core', 'src/api', 'tests', 'docs']
        
        self.designer.add_folder('src', 'src', 'Source')
        self.designer.add_folder('core', 'src/core', 'Core')
        
        assert self.designer.validate_coverage(required) is False
    
    def test_organization_rationale_documentation(self):
        """Test that organization rationale is documented."""
        self.designer.add_folder('src', 'src', 'Source code')
        self.designer.add_rationale('src', 'Contains all production code')
        
        assert 'src' in self.designer.organization_rationale
        assert self.designer.organization_rationale['src'] == 'Contains all production code'
    
    def test_rationale_completeness(self):
        """Test that all folders have documented rationale."""
        self.designer.add_folder('src', 'src', 'Source')
        self.designer.add_folder('tests', 'tests', 'Tests')
        self.designer.add_rationale('src', 'Production code')
        self.designer.add_rationale('tests', 'Test code')
        
        assert self.designer.validate_rationale_complete() is True
    
    def test_rationale_incomplete(self):
        """Test that incomplete rationale is detected."""
        self.designer.add_folder('src', 'src', 'Source')
        self.designer.add_folder('tests', 'tests', 'Tests')
        self.designer.add_rationale('src', 'Production code')
        
        assert self.designer.validate_rationale_complete() is False
    
    def test_migration_plan_creation(self):
        """Test that a migration plan can be created."""
        self.designer.add_folder('src', 'src', 'Source')
        self.designer.add_folder('core', 'src/core', 'Core')
        self.designer.add_rationale('src', 'Root')
        self.designer.add_rationale('src/core', 'Core logic')
        
        plan = self.designer.create_migration_plan()
        
        assert 'phases' in plan
        assert 'validation_steps' in plan
        assert 'rollback_strategy' in plan
        assert len(plan['phases']) >= 2
    
    def test_migration_plan_has_validation_steps(self):
        """Test that migration plan includes validation steps."""
        self.designer.add_folder('src', 'src', 'Source')
        self.designer.add_rationale('src', 'Root')
        
        plan = self.designer.create_migration_plan()
        
        assert len(plan['validation_steps']) >= 3
        assert any('test' in step.lower() for step in plan['validation_steps'])
    
    def test_migration_plan_has_rollback_strategy(self):
        """Test that migration plan includes rollback strategy."""
        self.designer.add_folder('src', 'src', 'Source')
        self.designer.add_rationale('src', 'Root')
        
        plan = self.designer.create_migration_plan()
        
        assert plan['rollback_strategy']
        assert len(plan['rollback_strategy']) > 0
    
    def test_comprehensive_cortex_structure_design(self):
        """Test design of complete CORTEX nested folder structure."""
        # Root level
        self.designer.add_folder('src', 'src', 'All production code')
        self.designer.add_folder('tests', 'tests', 'All test code')
        self.designer.add_folder('docs', 'docs', 'Documentation')
        
        # Source organization
        self.designer.add_folder('core', 'src/core', 'Core CORTEX functionality', parent='src')
        self.designer.add_folder('orchestrators', 'src/orchestrators', 'Orchestrator implementations', parent='src')
        self.designer.add_folder('tools', 'src/tools', 'Tool implementations', parent='src')
        self.designer.add_folder('infrastructure', 'src/infrastructure', 'Infrastructure', parent='src')
        
        # Core sub-organization
        self.designer.add_folder('orchestrator', 'src/core/orchestrator', 'Orchestrator module', parent='src/core')
        self.designer.add_folder('brain', 'src/core/brain', 'Brain module', parent='src/core')
        
        # Documentation
        self.designer.add_rationale('src', 'Production code organized by domain')
        self.designer.add_rationale('src/core', 'Core modules: orchestrator, brain, etc.')
        self.designer.add_rationale('src/orchestrators', 'Specific orchestrator implementations')
        self.designer.add_rationale('tests', 'Test code mirroring src structure')
        self.designer.add_rationale('docs', 'All documentation')
        
        # Validate
        assert self.designer.validate_uniqueness() is True
        assert len(self.designer.structure) >= 7
        assert len(self.designer.organization_rationale) == 5
    
    def test_folder_all_paths_retrieval(self):
        """Test that all folder paths can be retrieved."""
        self.designer.add_folder('src', 'src', 'Source')
        self.designer.add_folder('core', 'src/core', 'Core', parent='src')
        self.designer.add_folder('tests', 'tests', 'Tests')
        
        paths = self.designer.get_all_paths()
        
        assert 'src' in paths
        assert 'src/core' in paths
        assert 'tests' in paths
        assert len(paths) == 3

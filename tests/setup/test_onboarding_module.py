"""
Test Onboarding Module

Validates:
1. Application analysis runs after setup
2. Onboarding document is generated
3. Project structure is detected correctly
4. Improvements are identified
5. Analysis is stored in CORTEX brain

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

from src.setup.modules.onboarding_module import OnboardingModule
from src.setup.base_setup_module import SetupStatus


class TestOnboardingModule:
    """Test suite for Onboarding module."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create realistic project structure
        (temp_dir / 'src').mkdir()
        (temp_dir / 'src' / 'app.py').write_text('# App code')
        
        # Create package.json
        package_json = {
            "name": "test-app",
            "dependencies": {"react": "^18.0.0"},
            "devDependencies": {"jest": "^29.0.0", "eslint": "^8.0.0"}
        }
        (temp_dir / 'package.json').write_text(json.dumps(package_json, indent=2))
        
        # Create test directory
        (temp_dir / 'tests').mkdir()
        (temp_dir / 'tests' / 'test_app.py').write_text('# Tests')
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def cortex_project(self, temp_project):
        """Create CORTEX project structure."""
        cortex_dir = temp_project / 'CORTEX'
        cortex_dir.mkdir()
        
        # Create brain directory structure
        brain_dir = cortex_dir / 'cortex-brain' / 'documents' / 'analysis'
        brain_dir.mkdir(parents=True)
        
        return cortex_dir
    
    @pytest.fixture
    def module(self):
        """Create Onboarding module instance."""
        return OnboardingModule()
    
    @pytest.fixture
    def context(self, temp_project, cortex_project):
        """Create test context."""
        return {
            'project_root': str(cortex_project),
            'user_project_root': str(temp_project),
            'brain_initialized': True
        }
    
    def test_metadata(self, module):
        """Test module metadata."""
        metadata = module.get_metadata()
        
        assert metadata.module_id == "onboarding"
        assert metadata.name == "Application Onboarding"
        assert metadata.phase.name == "POST_SETUP"
        assert metadata.priority == 10
        assert "brain_initialization" in metadata.dependencies
        assert metadata.optional is True
    
    def test_validate_prerequisites_success(self, module, context):
        """Test prerequisite validation succeeds with valid context."""
        is_valid, issues = module.validate_prerequisites(context)
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_validate_prerequisites_no_user_root(self, module):
        """Test prerequisite validation fails without user_project_root."""
        context = {'brain_initialized': True}
        
        is_valid, issues = module.validate_prerequisites(context)
        
        assert is_valid is False
        assert any("user_project_root" in issue for issue in issues)
    
    def test_validate_prerequisites_no_brain(self, module, temp_project):
        """Test prerequisite validation fails if brain not initialized."""
        context = {'user_project_root': str(temp_project)}
        
        is_valid, issues = module.validate_prerequisites(context)
        
        assert is_valid is False
        assert any("brain not initialized" in issue for issue in issues)
    
    def test_execute_generates_analysis(self, module, context, cortex_project):
        """Test execution generates onboarding analysis document."""
        result = module.execute(context)
        
        assert result.status == SetupStatus.SUCCESS
        assert "improvement opportunities identified" in result.message
        
        # Verify document was created
        analysis_dir = cortex_project / 'cortex-brain' / 'documents' / 'analysis'
        analysis_files = list(analysis_dir.glob('*-onboarding-analysis-*.md'))
        assert len(analysis_files) >= 1
        
        # Verify content
        analysis_content = analysis_files[0].read_text()
        assert "CORTEX Onboarding Analysis" in analysis_content
        assert "Project Overview" in analysis_content
        assert "Improvement Opportunities" in analysis_content
    
    def test_detect_project_structure_nodejs(self, module, temp_project):
        """Test detection of Node.js project."""
        project_info = module._detect_project_structure(temp_project)
        
        assert project_info['project_name'] == temp_project.name
        assert 'nodejs' in project_info['project_type']
        assert 'package.json' in project_info['config_files']
    
    def test_detect_project_structure_dotnet(self, module, temp_project):
        """Test detection of .NET project."""
        # Add solution file
        (temp_project / 'App.sln').write_text('# Solution')
        
        project_info = module._detect_project_structure(temp_project)
        
        assert 'dotnet' in project_info['project_type']
        assert any('App.sln' in ep for ep in project_info['entry_points'])
    
    def test_analyze_tech_stack(self, module, temp_project):
        """Test tech stack analysis."""
        project_info = {'project_type': 'nodejs'}
        
        tech_stack = module._analyze_tech_stack(temp_project, project_info)
        
        assert 'TypeScript/JavaScript' in tech_stack['languages']
        assert 'React' in tech_stack['frameworks']
        assert 'ESLint' in tech_stack['tools']
    
    def test_analyze_testing_infrastructure(self, module, temp_project):
        """Test testing infrastructure analysis."""
        project_info = {'project_type': 'nodejs'}
        
        testing_info = module._analyze_testing_infrastructure(temp_project, project_info)
        
        assert testing_info['status'] == 'present'
        assert len(testing_info['test_directories']) > 0
        assert 'Jest' in testing_info['test_frameworks']
    
    def test_identify_improvements(self, module, temp_project):
        """Test improvement identification."""
        project_info = {'project_type': 'nodejs', 'config_files': ['package.json']}
        tech_stack = {'languages': ['TypeScript/JavaScript'], 'tools': [], 'frameworks': ['React']}
        testing_info = {'status': 'present', 'test_frameworks': ['Jest'], 'coverage_tools': []}
        
        improvements = module._identify_improvements(temp_project, project_info, tech_stack, testing_info)
        
        assert len(improvements) > 0
        
        # Should suggest .editorconfig (missing)
        assert any('editorconfig' in imp['title'].lower() for imp in improvements)
        
        # Should suggest code coverage (missing)
        assert any('coverage' in imp['title'].lower() for imp in improvements)
    
    def test_context_updated(self, module, context):
        """Test context is updated with onboarding results."""
        result = module.execute(context)
        
        assert context['onboarding_complete'] is True
        assert 'onboarding_analysis_path' in context
        assert 'improvement_count' in context
        assert context['improvement_count'] > 0
    
    def test_rollback_deletes_analysis(self, module, context, cortex_project):
        """Test rollback deletes onboarding analysis document."""
        # Execute first to create document
        result = module.execute(context)
        analysis_path = context['onboarding_analysis_path']
        
        assert Path(analysis_path).exists()
        
        # Rollback
        success = module.rollback(context)
        
        assert success is True
        assert not Path(analysis_path).exists()


class TestOnboardingIntegration:
    """Integration tests for Onboarding module."""
    
    @pytest.fixture
    def complex_project(self):
        """Create a complex project structure for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # .NET solution
        (temp_dir / 'App.sln').write_text('# Solution')
        
        # SPA folder with package.json
        spa_dir = temp_dir / 'SPA' / 'App'
        spa_dir.mkdir(parents=True)
        package_json = {
            "name": "complex-app",
            "dependencies": {"react": "^18.0.0", "next": "^13.0.0"},
            "devDependencies": {
                "jest": "^29.0.0",
                "eslint": "^8.0.0",
                "@playwright/test": "^1.40.0"
            },
            "scripts": {"coverage": "jest --coverage"}
        }
        (spa_dir / 'package.json').write_text(json.dumps(package_json, indent=2))
        
        # Test directories
        (temp_dir / 'Tests' / 'Unit').mkdir(parents=True)
        (temp_dir / 'Tests' / 'Integration').mkdir(parents=True)
        
        # .editorconfig
        (temp_dir / '.editorconfig').write_text('[*]\nindent_style = space')
        
        # README
        (temp_dir / 'README.md').write_text('# App')
        
        # CORTEX structure
        cortex_dir = temp_dir / 'CORTEX'
        cortex_dir.mkdir()
        brain_dir = cortex_dir / 'cortex-brain' / 'documents' / 'analysis'
        brain_dir.mkdir(parents=True)
        
        yield temp_dir, cortex_dir
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_complex_project_analysis(self, complex_project):
        """Test complete onboarding workflow with complex project."""
        temp_dir, cortex_dir = complex_project
        
        module = OnboardingModule()
        context = {
            'project_root': str(cortex_dir),
            'user_project_root': str(temp_dir),
            'brain_initialized': True
        }
        
        # Validate prerequisites
        is_valid, issues = module.validate_prerequisites(context)
        assert is_valid is True, f"Prerequisites failed: {issues}"
        
        # Execute onboarding
        result = module.execute(context)
        assert result.status == SetupStatus.SUCCESS, f"Onboarding failed: {result.message}"
        
        # Verify analysis document
        analysis_dir = cortex_dir / 'cortex-brain' / 'documents' / 'analysis'
        analysis_files = list(analysis_dir.glob('*-onboarding-analysis-*.md'))
        assert len(analysis_files) >= 1
        
        analysis_content = analysis_files[0].read_text()
        
        # Verify project detection
        assert "dotnet+nodejs" in analysis_content or "nodejs" in analysis_content
        assert "React" in analysis_content
        assert "Next.js" in analysis_content
        
        # Verify testing detection
        assert "Jest" in analysis_content
        assert "Playwright" in analysis_content
        assert "present" in analysis_content.lower()
        
        # Verify tools detection
        assert "EditorConfig" in analysis_content
        assert "ESLint" in analysis_content
        
        # Verify improvements section
        assert "Improvement Opportunities" in analysis_content
        
        # Verify context updated
        assert context['onboarding_complete'] is True
        assert context['improvement_count'] >= 0

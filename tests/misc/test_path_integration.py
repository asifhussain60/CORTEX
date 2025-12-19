"""
Integration Tests for Path Configuration System

End-to-end tests for complete path configuration workflow.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from src.setup.models.user_path_config import UserPathConfig
from src.setup.modules.path_detector import PathDetector
from src.setup.modules.path_resolver import PathResolver
from src.setup.modules.user_profile_storage import UserProfileStorage
from src.setup.modules.tdd_path_adapter import TDDWorkflowPathAdapter


@pytest.fixture
def temp_project():
    """Create a complete temporary project for integration testing."""
    temp_dir = tempfile.mkdtemp()
    project_root = Path(temp_dir)
    
    # Create project structure
    (project_root / "src").mkdir()
    (project_root / "src" / "app.py").write_text("def main(): pass")
    (project_root / "src" / "utils.py").write_text("def helper(): pass")
    
    # Create existing tests
    (project_root / "tests").mkdir()
    (project_root / "tests" / "test_app.py").write_text("def test_main(): pass")
    (project_root / "tests" / "conftest.py").write_text("# pytest config")
    
    # Create pytest.ini
    (project_root / "pytest.ini").write_text("[pytest]\ntestpaths = tests")
    
    # Create requirements.txt
    (project_root / "requirements.txt").write_text("pytest>=8.0")
    
    yield project_root
    
    shutil.rmtree(temp_dir)


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""
    
    def test_complete_setup_workflow(self, temp_project):
        """Test complete setup from detection to usage."""
        
        # Step 1: Detect existing test directories
        detector = PathDetector(str(temp_project))
        scan_results = detector.scan_repository()
        
        assert len(scan_results["test_directories"]) >= 1
        assert scan_results["suggested_test_directory"] == "tests"
        
        # Step 2: Create configuration based on detection
        config = UserPathConfig(
            test_directory=scan_results["suggested_test_directory"],
            reports_directory="cortex-brain/documents/reports",
            custom_paths={"logs": "logs"}
        )
        
        # Step 3: Save configuration
        config_file = temp_project / "cortex.config.json"
        config_data = {"user_paths": config.to_dict()}
        config_file.write_text(json.dumps(config_data, indent=2))
        
        # Step 4: Resolve paths using saved configuration
        resolver = PathResolver(workspace_root=str(temp_project), config=config)
        
        test_dir = resolver.get_test_directory(create=False)
        assert test_dir == temp_project / "tests"
        assert test_dir.exists()
        
        # Step 5: Use in TDD workflow
        adapter = TDDWorkflowPathAdapter(str(temp_project))
        
        test_path = adapter.get_test_path_for_source("src/utils.py")
        assert test_path == temp_project / "tests" / "test_utils.py"
    
    def test_configuration_persistence(self, temp_project):
        """Test configuration persistence and loading."""
        
        # Create and save configuration
        config = UserPathConfig(
            test_directory="__tests__",
            reports_directory="docs/reports",
            custom_paths={"screenshots": "test-screenshots"}
        )
        
        config_file = temp_project / "cortex.config.json"
        config_data = {"user_paths": config.to_dict()}
        config_file.write_text(json.dumps(config_data, indent=2))
        
        # Load configuration
        loaded_data = json.loads(config_file.read_text())
        loaded_config = UserPathConfig(**loaded_data["user_paths"])
        
        assert loaded_config.test_directory == "__tests__"
        assert loaded_config.reports_directory == "docs/reports"
        assert loaded_config.custom_paths["screenshots"] == "test-screenshots"
    
    def test_path_resolution_chain(self, temp_project):
        """Test complete path resolution chain."""
        
        # Setup configuration
        config = UserPathConfig(test_directory="tests")
        config_file = temp_project / "cortex.config.json"
        config_data = {"user_paths": config.to_dict()}
        config_file.write_text(json.dumps(config_data, indent=2))
        
        # Create resolver
        resolver = PathResolver(workspace_root=str(temp_project), config=config)
        
        # Test various path resolutions
        test_dir = resolver.get_test_directory(create=True)
        assert test_dir.exists()
        
        reports_dir = resolver.get_documents_directory("reports", create=True)
        assert reports_dir.exists()
        
        doc_path = resolver.get_document_path("report.md", "reports")
        assert doc_path.parent.exists()


class TestMultipleConfigurations:
    """Test handling multiple configurations."""
    
    def test_switch_test_directories(self, temp_project):
        """Test switching between different test directory configurations."""
        
        # Configuration 1: tests/
        config1 = UserPathConfig(test_directory="tests")
        resolver1 = PathResolver(workspace_root=str(temp_project), config=config1)
        
        test_dir1 = resolver1.get_test_directory()
        assert test_dir1 == temp_project / "tests"
        
        # Configuration 2: __tests__/
        config2 = UserPathConfig(test_directory="__tests__")
        resolver2 = PathResolver(workspace_root=str(temp_project), config=config2)
        
        test_dir2 = resolver2.get_test_directory(create=True)
        assert test_dir2 == temp_project / "__tests__"
        assert test_dir2.exists()
    
    def test_custom_document_locations(self, temp_project):
        """Test custom document location configurations."""
        
        # Custom configuration
        config = UserPathConfig(
            reports_directory="documentation/reports",
            analysis_directory="documentation/analysis"
        )
        
        resolver = PathResolver(workspace_root=str(temp_project), config=config)
        
        reports_dir = resolver.get_documents_directory("reports", create=True)
        assert "documentation" in str(reports_dir)
        assert reports_dir.exists()
        
        analysis_dir = resolver.get_documents_directory("analysis", create=True)
        assert "documentation" in str(analysis_dir)
        assert analysis_dir.exists()


class TestErrorHandling:
    """Test error handling in integration scenarios."""
    
    def test_invalid_configuration_recovery(self, temp_project):
        """Test recovery from invalid configuration."""
        
        # Create invalid configuration
        config_file = temp_project / "cortex.config.json"
        config_file.write_text("invalid json{{{")
        
        # Resolver should fall back to defaults
        resolver = PathResolver(workspace_root=str(temp_project))
        
        test_dir = resolver.get_test_directory(create=True)
        assert test_dir.exists()
    
    def test_missing_configuration_defaults(self, temp_project):
        """Test that defaults are used when configuration is missing."""
        
        # No configuration file
        resolver = PathResolver(workspace_root=str(temp_project))
        
        test_dir = resolver.get_test_directory()
        assert test_dir == temp_project / "tests"


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def test_python_project_workflow(self, temp_project):
        """Test workflow for Python project."""
        
        # Detect and configure
        detector = PathDetector(str(temp_project))
        suggestion = detector.suggest_test_directory()
        
        config = UserPathConfig(test_directory=suggestion)
        adapter = TDDWorkflowPathAdapter(str(temp_project))
        
        # Create tests for multiple source files
        source_files = ["src/app.py", "src/utils.py", "src/models/user.py"]
        
        for source_file in source_files:
            # Create source if needed
            source_path = temp_project / source_file
            source_path.parent.mkdir(parents=True, exist_ok=True)
            if not source_path.exists():
                source_path.write_text(f"# {source_file}")
            
            # Get test path
            test_path = adapter.get_test_path_for_source(source_file)
            
            # Verify test path
            assert adapter.is_test_file(str(test_path))
            assert test_path.parent.exists()
    
    def test_documentation_generation_workflow(self, temp_project):
        """Test workflow for document generation."""
        
        config = UserPathConfig(
            reports_directory="cortex-brain/documents/reports",
            analysis_directory="cortex-brain/documents/analysis"
        )
        
        resolver = PathResolver(workspace_root=str(temp_project), config=config)
        
        # Generate various documents
        reports = [
            "validation-report.md",
            "test-coverage-report.md",
            "deployment-status.md"
        ]
        
        for report in reports:
            report_path = resolver.get_document_path(report, "reports", create_dir=True)
            
            # Create document
            report_path.write_text(f"# {report}\n\nReport content")
            
            assert report_path.exists()
            assert "reports" in str(report_path)


class TestConcurrency:
    """Test concurrent access scenarios."""
    
    def test_multiple_resolvers_same_config(self, temp_project):
        """Test multiple resolvers using same configuration."""
        
        config = UserPathConfig(test_directory="tests")
        
        # Create multiple resolvers
        resolver1 = PathResolver(workspace_root=str(temp_project), config=config)
        resolver2 = PathResolver(workspace_root=str(temp_project), config=config)
        
        # Both should resolve to same directories
        test_dir1 = resolver1.get_test_directory()
        test_dir2 = resolver2.get_test_directory()
        
        assert test_dir1 == test_dir2
    
    def test_multiple_adapters_concurrent_use(self, temp_project):
        """Test multiple TDD adapters in concurrent scenarios."""
        
        adapter1 = TDDWorkflowPathAdapter(str(temp_project))
        adapter2 = TDDWorkflowPathAdapter(str(temp_project))
        
        # Both should generate same test paths
        path1 = adapter1.get_test_path_for_source("src/app.py")
        path2 = adapter2.get_test_path_for_source("src/app.py")
        
        assert path1 == path2


class TestBackwardCompatibility:
    """Test backward compatibility scenarios."""
    
    def test_config_without_user_paths(self, temp_project):
        """Test handling config file without user_paths section."""
        
        # Create config without user_paths
        config_file = temp_project / "cortex.config.json"
        config_data = {
            "version": "3.7.0",
            "user": {"name": "Test User"}
        }
        config_file.write_text(json.dumps(config_data, indent=2))
        
        # Should use defaults
        resolver = PathResolver(workspace_root=str(temp_project))
        test_dir = resolver.get_test_directory()
        
        assert test_dir == temp_project / "tests"
    
    def test_legacy_test_directory_handling(self, temp_project):
        """Test handling of legacy hardcoded test paths."""
        
        # Simulate legacy hardcoded path
        legacy_test_dir = temp_project / "tests"
        legacy_test_dir.mkdir(exist_ok=True)
        
        # New system should detect and use it
        detector = PathDetector(str(temp_project))
        suggestion = detector.suggest_test_directory()
        
        assert suggestion == "tests"


class TestValidationIntegration:
    """Test validation across the system."""
    
    def test_end_to_end_validation(self, temp_project):
        """Test validation from configuration to usage."""
        
        # Create configuration
        config = UserPathConfig(
            test_directory="tests",
            reports_directory="cortex-brain/documents/reports"
        )
        
        # Validate via resolver
        resolver = PathResolver(workspace_root=str(temp_project), config=config)
        
        # Create directories
        test_dir = resolver.get_test_directory(create=True)
        reports_dir = resolver.get_documents_directory("reports", create=True)
        
        # Validate configuration
        validation = resolver.validate_configuration()
        
        # Should have minimal warnings since we created directories
        assert len(validation["errors"]) == 0
        
        # Validate TDD setup
        adapter = TDDWorkflowPathAdapter(str(temp_project))
        tdd_validation = adapter.validate_test_setup()
        
        assert tdd_validation["valid"] is True

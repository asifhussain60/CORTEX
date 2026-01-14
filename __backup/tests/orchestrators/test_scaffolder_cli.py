"""
Tests for AC-SCAFFOLD-001: Orchestrator Scaffolder CLI

Validates scaffolder CLI creates complete orchestrator implementations
with tests, documentation, and MasterOrchestrator registration.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from src.orchestrators.master.scaffolder import OrchestratorScaffolder


@pytest.mark.ac_id("AC-SCAFFOLD-001")
class TestOrchestratorScaffolderCLI:
    """Test orchestrator scaffolding functionality."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for scaffolding."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def scaffolder(self, temp_workspace):
        """Create scaffolder instance."""
        return OrchestratorScaffolder(workspace=temp_workspace)
    
    def test_scaffold_creates_orchestrator_file(self, scaffolder, temp_workspace):
        """Test: Scaffolder creates orchestrator implementation file."""
        # Scaffold new orchestrator
        result = scaffolder.scaffold(
            name="TestOrchestrator",
            category="feature"
        )
        
        # Verify orchestrator file created
        orch_file = temp_workspace / "src" / "orchestrators" / "test_orchestrator.py"
        assert orch_file.exists()
        
        # Verify content
        content = orch_file.read_text()
        assert "class TestOrchestrator" in content
        assert "BaseOrchestrator" in content
        assert "handle_request" in content
    
    def test_scaffold_creates_test_file(self, scaffolder, temp_workspace):
        """Test: Scaffolder creates test file with basic tests."""
        # Scaffold orchestrator
        result = scaffolder.scaffold(
            name="ExampleOrchestrator",
            category="feature"
        )
        
        # Verify test file created
        test_file = temp_workspace / "tests" / "orchestrators" / "test_example_orchestrator.py"
        assert test_file.exists()
        
        # Verify test content
        content = test_file.read_text()
        assert "TestExampleOrchestrator" in content
        assert "@pytest.fixture" in content
        assert "def test_" in content
    
    def test_scaffold_creates_documentation(self, scaffolder, temp_workspace):
        """Test: Scaffolder creates documentation file."""
        # Scaffold orchestrator
        result = scaffolder.scaffold(
            name="DocumentedOrchestrator",
            category="feature"
        )
        
        # Verify documentation created
        doc_file = temp_workspace / "docs" / "orchestrators" / "documented-orchestrator.md"
        assert doc_file.exists()
        
        # Verify documentation content
        content = doc_file.read_text()
        assert "DocumentedOrchestrator" in content
        assert "## Purpose" in content
        assert "## Usage" in content
        assert "## AC-IDs" in content
    
    def test_scaffold_with_ac_ids(self, scaffolder, temp_workspace):
        """Test: Scaffolder associates AC-IDs with orchestrator."""
        # Scaffold with AC-IDs
        result = scaffolder.scaffold(
            name="ACOrchestrator",
            category="feature",
            ac_ids=["AC-TEST-001", "AC-TEST-002"]
        )
        
        # Verify AC-IDs in documentation
        doc_file = temp_workspace / "docs" / "orchestrators" / "ac-orchestrator.md"
        content = doc_file.read_text()
        assert "AC-TEST-001" in content
        assert "AC-TEST-002" in content
    
    def test_scaffold_creates_init_import(self, scaffolder, temp_workspace):
        """Test: Scaffolder updates __init__.py with import."""
        # Scaffold orchestrator
        result = scaffolder.scaffold(
            name="InitOrchestrator",
            category="feature"
        )
        
        # Verify __init__.py updated
        init_file = temp_workspace / "src" / "orchestrators" / "__init__.py"
        if init_file.exists():
            content = init_file.read_text()
            assert "InitOrchestrator" in content
    
    def test_scaffold_validates_name_format(self, scaffolder, temp_workspace):
        """Test: Scaffolder validates orchestrator name format."""
        # Invalid names should raise error
        with pytest.raises(ValueError, match="name|format"):
            scaffolder.scaffold(name="invalid-name-123", category="feature")
        
        with pytest.raises(ValueError, match="name|format"):
            scaffolder.scaffold(name="123InvalidStart", category="feature")
    
    def test_scaffold_prevents_overwrite(self, scaffolder, temp_workspace):
        """Test: Scaffolder prevents overwriting existing orchestrators."""
        # Create orchestrator
        scaffolder.scaffold(name="ExistingOrchestrator", category="feature")
        
        # Attempt to create again
        with pytest.raises(FileExistsError, match="exists|already"):
            scaffolder.scaffold(name="ExistingOrchestrator", category="feature")
    
    def test_scaffold_with_custom_template(self, scaffolder, temp_workspace):
        """Test: Scaffolder supports custom templates."""
        # Create custom template
        template_dir = temp_workspace / "templates"
        template_dir.mkdir(parents=True)
        template_file = template_dir / "custom_orchestrator.py.j2"
        template_file.write_text("# Custom template\nclass {{ name }}:\n    pass")
        
        # Scaffold with custom template
        result = scaffolder.scaffold(
            name="CustomOrchestrator",
            category="feature",
            template="custom_orchestrator"
        )
        
        # Verify custom template used
        orch_file = temp_workspace / "src" / "orchestrators" / "custom_orchestrator.py"
        content = orch_file.read_text()
        assert "# Custom template" in content
    
    def test_scaffold_creates_directory_structure(self, scaffolder, temp_workspace):
        """Test: Scaffolder creates necessary directory structure."""
        # Scaffold orchestrator
        result = scaffolder.scaffold(
            name="StructureOrchestrator",
            category="feature"
        )
        
        # Verify directories created
        assert (temp_workspace / "src" / "orchestrators").exists()
        assert (temp_workspace / "tests" / "orchestrators").exists()
        assert (temp_workspace / "docs" / "orchestrators").exists()
    
    def test_scaffold_includes_copyright(self, scaffolder, temp_workspace):
        """Test: Scaffolder includes copyright in generated files."""
        # Scaffold orchestrator
        result = scaffolder.scaffold(
            name="CopyrightOrchestrator",
            category="feature"
        )
        
        # Verify copyright in orchestrator file
        orch_file = temp_workspace / "src" / "orchestrators" / "copyright_orchestrator.py"
        content = orch_file.read_text()
        assert "Copyright ©" in content or "Author:" in content
    
    def test_scaffold_dry_run_mode(self, scaffolder, temp_workspace):
        """Test: Dry run mode shows what would be created without creating."""
        # Scaffold in dry-run mode
        result = scaffolder.scaffold(
            name="DryRunOrchestrator",
            category="feature",
            dry_run=True
        )
        
        # Verify no files created
        orch_file = temp_workspace / "src" / "orchestrators" / "dry_run_orchestrator.py"
        assert not orch_file.exists()
        
        # Verify result shows intended actions
        assert result.success
        assert len(result.files_to_create) > 0
    
    def test_scaffold_returns_created_files_list(self, scaffolder, temp_workspace):
        """Test: Scaffolder returns list of created files."""
        # Scaffold orchestrator
        result = scaffolder.scaffold(
            name="FileListOrchestrator",
            category="feature"
        )
        
        # Verify result contains file list
        assert result.success
        assert len(result.created_files) >= 3  # orchestrator, test, doc
        assert any("orchestrators/file_list_orchestrator.py" in str(f) for f in result.created_files)

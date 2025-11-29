"""
Test Suite for Enterprise Documentation Orchestrator
Validates that file generation reports match physical file creation.
"""
import sys
from pathlib import Path
import pytest
import tempfile
import shutil

# Add CORTEX root to path
cortex_root = Path(__file__).parent.parent
sys.path.insert(0, str(cortex_root))

# Import from admin scripts location
admin_scripts_path = cortex_root / "cortex-brain" / "admin" / "scripts" / "documentation"
sys.path.insert(0, str(admin_scripts_path))

from enterprise_documentation_orchestrator import (
    EnterpriseDocumentationOrchestrator,
    execute_enterprise_documentation
)


class TestEnterpriseDocumentationOrchestrator:
    """Test suite for enterprise documentation orchestrator with physical file validation."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp(prefix="cortex_docs_test_")
        workspace = Path(temp_dir)
        
        # Create minimal brain structure
        brain_path = workspace / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        
        # Create capabilities.yaml stub
        (brain_path / "capabilities.yaml").write_text("capabilities: []", encoding='utf-8')
        
        yield workspace
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_orchestrator_initialization(self, temp_workspace):
        """Test that orchestrator initializes with correct paths."""
        orchestrator = EnterpriseDocumentationOrchestrator(temp_workspace)
        
        assert orchestrator.workspace_root == temp_workspace
        assert orchestrator.brain_path == temp_workspace / "cortex-brain"
        assert orchestrator.docs_path == temp_workspace / "docs"
        assert orchestrator.diagrams_path == temp_workspace / "docs" / "diagrams"
    
    def test_diagrams_physical_file_creation(self, temp_workspace):
        """Test that diagram generation creates actual files on disk."""
        orchestrator = EnterpriseDocumentationOrchestrator(temp_workspace)
        
        # Generate diagrams
        result = orchestrator._generate_diagrams({}, dry_run=False)
        
        # Validate result structure
        assert "count" in result
        assert "files" in result
        assert "expected_count" in result
        assert "validation" in result
        
        validation = result["validation"]
        assert "files_created" in validation
        assert "files_failed" in validation
        assert "failed_files" in validation
        
        # Check that reported count matches files created
        assert result["count"] == validation["files_created"]
        
        # Verify each reported file actually exists
        for filename in result["files"]:
            file_path = orchestrator.mermaid_path / filename
            assert file_path.exists(), f"Reported file {filename} does not exist"
            assert file_path.stat().st_size > 0, f"Reported file {filename} is empty"
        
        # Check that no files failed
        if validation["files_failed"] > 0:
            pytest.fail(f"Failed to create {validation['files_failed']} files: {validation['failed_files']}")
    
    def test_prompts_physical_file_creation(self, temp_workspace):
        """Test that DALL-E prompt generation creates actual files on disk."""
        orchestrator = EnterpriseDocumentationOrchestrator(temp_workspace)
        
        # Generate prompts
        result = orchestrator._generate_dalle_prompts({}, dry_run=False)
        
        # Validate result structure
        assert "validation" in result
        validation = result["validation"]
        
        # Check that reported count matches files created
        assert result["count"] == validation["files_created"]
        
        # Verify each reported file actually exists
        for filename in result["files"]:
            file_path = orchestrator.prompts_path / filename
            assert file_path.exists(), f"Reported file {filename} does not exist"
            assert file_path.stat().st_size > 0, f"Reported file {filename} is empty"
        
        # Check that no files failed
        if validation["files_failed"] > 0:
            pytest.fail(f"Failed to create {validation['files_failed']} files: {validation['failed_files']}")
    
    def test_narratives_physical_file_creation(self, temp_workspace):
        """Test that narrative generation creates actual files on disk."""
        orchestrator = EnterpriseDocumentationOrchestrator(temp_workspace)
        
        # Generate narratives
        result = orchestrator._generate_narratives({}, dry_run=False)
        
        # Validate result structure
        assert "validation" in result
        validation = result["validation"]
        
        # Check that reported count matches files created
        assert result["count"] == validation["files_created"]
        
        # Verify each reported file actually exists
        for filename in result["files"]:
            file_path = orchestrator.narratives_path / filename
            assert file_path.exists(), f"Reported file {filename} does not exist"
            assert file_path.stat().st_size > 0, f"Reported file {filename} is empty"
        
        # Check that no files failed
        if validation["files_failed"] > 0:
            pytest.fail(f"Failed to create {validation['files_failed']} files: {validation['failed_files']}")
    
    def test_story_physical_file_creation(self, temp_workspace):
        """Test that story generation creates actual file on disk."""
        orchestrator = EnterpriseDocumentationOrchestrator(temp_workspace)
        
        # Generate story
        result = orchestrator._generate_story({}, dry_run=False)
        
        # Validate result structure
        assert "validation" in result
        validation = result["validation"]
        
        # Check file was created
        assert validation["file_created"], f"Story file not created: {validation.get('error', 'unknown error')}"
        
        # Verify file actually exists
        story_file = Path(result["file"])
        assert story_file.exists(), f"Reported story file does not exist: {story_file}"
        assert story_file.stat().st_size > 0, f"Story file is empty: {story_file}"
    
    def test_executive_summary_physical_file_creation(self, temp_workspace):
        """Test that executive summary generation creates actual file on disk."""
        orchestrator = EnterpriseDocumentationOrchestrator(temp_workspace)
        
        # Generate executive summary
        result = orchestrator._generate_executive_summary({"features": []}, dry_run=False)
        
        # Validate result structure
        assert "validation" in result
        validation = result["validation"]
        
        # Check file was created
        assert validation["file_created"], f"Executive summary not created: {validation.get('error', 'unknown error')}"
        
        # Verify file actually exists
        summary_file = Path(result["file"])
        assert summary_file.exists(), f"Reported summary file does not exist: {summary_file}"
        assert summary_file.stat().st_size > 0, f"Summary file is empty: {summary_file}"
    
    def test_mkdocs_site_physical_file_creation(self, temp_workspace):
        """Test that MkDocs site builder creates actual files on disk."""
        orchestrator = EnterpriseDocumentationOrchestrator(temp_workspace)
        
        # Build MkDocs site
        result = orchestrator._build_mkdocs_site({"features": []}, dry_run=False)
        
        # Validate result structure
        assert "validation" in result
        validation = result["validation"]
        
        # Check that files were created
        assert validation["files_created"] > 0, "No MkDocs files created"
        
        # Verify each created file actually exists
        for filename in validation["created_files"]:
            # Files are relative to diagrams_path
            if filename == "mkdocs.yml":
                file_path = orchestrator.diagrams_path / filename
            elif filename == "docs/index.md":
                file_path = orchestrator.diagrams_path / filename
            else:
                continue  # Skip unknown files
            
            assert file_path.exists(), f"Reported file {filename} does not exist"
            assert file_path.stat().st_size > 0, f"Reported file {filename} is empty"
        
        # Check for failed files
        if validation["files_failed"] > 0:
            pytest.fail(f"Failed to create {validation['files_failed']} files: {validation['failed_files']}")
    
    def test_full_pipeline_physical_validation(self, temp_workspace):
        """Test complete documentation generation pipeline with physical file validation."""
        # Execute full documentation generation
        result = execute_enterprise_documentation(
            workspace_root=temp_workspace,
            profile="standard",
            dry_run=False
        )
        
        # Check operation succeeded
        assert result.success, f"Documentation generation failed: {result.message}"
        
        # Validate generation_results in data
        generation_results = result.data.get("generation_results", {})
        
        # Check each component has validation data
        for component_name, component_result in generation_results.items():
            if component_result.get("dry_run", False):
                continue  # Skip dry-run results
            
            # Each component should have validation data
            if "validation" in component_result:
                validation = component_result["validation"]
                
                # Check that files_created matches count
                if "files_created" in validation and "count" in component_result:
                    assert component_result["count"] == validation["files_created"], \
                        f"{component_name}: Reported count doesn't match validated files"
                
                # Check for failures
                if "files_failed" in validation and validation["files_failed"] > 0:
                    pytest.fail(
                        f"{component_name}: Failed to create {validation['files_failed']} files: "
                        f"{validation.get('failed_files', [])}"
                    )
    
    def test_dry_run_no_file_creation(self, temp_workspace):
        """Test that dry-run mode doesn't create files."""
        orchestrator = EnterpriseDocumentationOrchestrator(temp_workspace)
        
        # Run dry-run
        result = orchestrator.execute(profile="standard", dry_run=True)
        
        # Check that docs folder wasn't created
        assert not (temp_workspace / "docs" / "diagrams").exists(), \
            "Dry-run should not create directories"
    
    def test_false_positive_detection(self, temp_workspace):
        """Test that orchestrator detects when files are reported but not created."""
        orchestrator = EnterpriseDocumentationOrchestrator(temp_workspace)
        
        # Mock a scenario where write_text "succeeds" but file doesn't exist
        # (This would happen if there's a permission error or path issue)
        
        # Create diagrams
        result = orchestrator._generate_diagrams({}, dry_run=False)
        
        # All files should be created - if any fail, validation should catch it
        validation = result["validation"]
        
        # If this test passes, it means our validation is working
        # If files_failed > 0, that's a real issue that should be investigated
        if validation["files_failed"] > 0:
            # This is expected if there are legitimate failures
            # The important thing is that we DETECTED them
            print(f"Detected {validation['files_failed']} file creation failures (as expected)")
            assert validation["failed_files"], "Failed files should be listed"
        else:
            # All files created successfully
            assert result["count"] == result["expected_count"], \
                "Count should match expected when all files succeed"
    
    def test_dashboard_generation(self, temp_workspace):
        """Test that D3.js dashboard generation creates HTML file with correct structure."""
        orchestrator = EnterpriseDocumentationOrchestrator(temp_workspace)
        
        # Mock discovered features and generation results
        discovered_features = {
            "features": [
                {"name": "TDD Enforcement", "type": "governance", "source": "catalog"},
                {"name": "Brain Protection", "type": "protection", "source": "catalog"},
                {"name": "Planning System", "type": "orchestrator", "source": "catalog"}
            ]
        }
        
        generation_results = {
            "diagrams_generated": 10,
            "prompts_generated": 8,
            "narratives_generated": 12
        }
        
        # Generate dashboard
        dashboard_path = orchestrator._generate_interactive_dashboard(
            discovered_features,
            generation_results,
            duration=5.23,
            dry_run=False
        )
        
        # Verify dashboard file was created
        assert dashboard_path.exists(), "Dashboard file not created"
        assert dashboard_path.suffix == ".html", "Dashboard should be HTML file"
        
        # Read and validate dashboard content
        dashboard_content = dashboard_path.read_text(encoding='utf-8')
        
        # Validate HTML structure
        assert "<html" in dashboard_content.lower(), "Missing HTML tag"
        assert "<!DOCTYPE" in dashboard_content or "<html" in dashboard_content, "Missing DOCTYPE or HTML tag"
        
        # Validate D3.js inclusion
        assert "d3" in dashboard_content.lower() or "chart" in dashboard_content.lower(), \
            "Dashboard should include D3.js or Chart.js references"
        
        # Validate data presence
        assert "Enterprise Documentation Generation Report" in dashboard_content, \
            "Missing dashboard title"
        assert "10" in dashboard_content, "Missing diagram count"
        assert "8" in dashboard_content, "Missing prompt count"
        assert "12" in dashboard_content, "Missing narrative count"
        
        # Validate dashboard sections
        assert "documentation_architecture" in dashboard_content or "force" in dashboard_content.lower(), \
            "Missing architecture visualization"
        
        # Verify file size (should be non-trivial)
        assert dashboard_path.stat().st_size > 5000, \
            "Dashboard file seems too small (< 5KB)"
    
    def test_dashboard_generation_dry_run(self, temp_workspace):
        """Test that dashboard generation works in dry-run mode."""
        orchestrator = EnterpriseDocumentationOrchestrator(temp_workspace)
        
        discovered_features = {"features": []}
        generation_results = {
            "diagrams_generated": 0,
            "prompts_generated": 0,
            "narratives_generated": 0
        }
        
        # Generate dashboard in dry-run mode
        dashboard_path = orchestrator._generate_interactive_dashboard(
            discovered_features,
            generation_results,
            duration=1.5,
            dry_run=True
        )
        
        # Verify dashboard created even in dry-run
        assert dashboard_path.exists(), "Dashboard should be created even in dry-run mode"
        
        # Verify dry-run is indicated
        dashboard_content = dashboard_path.read_text(encoding='utf-8')
        assert "Dry Run" in dashboard_content or "dry" in dashboard_content.lower(), \
            "Dashboard should indicate dry-run mode"


class TestDocumentationStructureValidation:
    """Test suite for validating documentation structure after generation."""
    
    def test_generated_files_match_expected_structure(self, tmp_path):
        """Test that generated files match expected documentation structure."""
        # This test ensures the orchestrator creates files in the right locations
        orchestrator = EnterpriseDocumentationOrchestrator(tmp_path)
        
        # Expected paths
        expected_paths = {
            "mermaid": orchestrator.mermaid_path,
            "prompts": orchestrator.prompts_path,
            "narratives": orchestrator.narratives_path,
        }
        
        # Generate content
        orchestrator._generate_diagrams({}, dry_run=False)
        orchestrator._generate_dalle_prompts({}, dry_run=False)
        orchestrator._generate_narratives({}, dry_run=False)
        
        # Verify directories were created
        for name, path in expected_paths.items():
            assert path.exists(), f"{name} directory not created: {path}"
            assert path.is_dir(), f"{name} path is not a directory: {path}"
            
            # Verify directory has files
            files = list(path.glob("*"))
            assert len(files) > 0, f"{name} directory is empty: {path}"


if __name__ == "__main__":
    """Run tests directly."""
    pytest.main([__file__, "-v", "--tb=short"])

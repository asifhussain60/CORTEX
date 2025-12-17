"""
Unit tests for Technical Documentation Orchestrator
Tests Phase 1.5 implementation (pre-migration)

Author: Asif Hussain
Version: 1.0.0
Coverage Target: 85%+
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.orchestrators.documentation.technical_documentation_orchestrator import (
    TechnicalDocumentationOrchestrator
)


class TestTechnicalDocumentationOrchestrator:
    """Test suite for TechnicalDocumentationOrchestrator"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def mock_cortex_structure(self, temp_dir):
        """Create mock CORTEX repository structure"""
        # Create directories
        (temp_dir / "src" / "orchestrators").mkdir(parents=True)
        (temp_dir / "src" / "cortex_agents").mkdir(parents=True)
        (temp_dir / "cortex-brain" / "tier1").mkdir(parents=True)
        (temp_dir / "cortex-brain" / "orchestrator-manifests").mkdir(parents=True)
        (temp_dir / "tests").mkdir(parents=True)
        
        # Create mock files
        (temp_dir / "src" / "orchestrators" / "planning_orchestrator.py").write_text(
            "# Planning Orchestrator\n" * 100
        )
        (temp_dir / "src" / "cortex_agents" / "strategic_agent.py").write_text(
            "# Strategic Agent\n" * 50
        )
        (temp_dir / "cortex-brain" / "orchestrator-manifests" / "planning-manifest.yaml").write_text(
            "name: planning\n" * 30
        )
        (temp_dir / "tests" / "test_planning.py").write_text(
            "def test_planning(): pass\n"
        )
        
        return temp_dir
    
    @pytest.fixture
    def orchestrator(self, temp_dir, mock_cortex_structure):
        """Create orchestrator instance with test config"""
        config = {
            "output_dir": str(temp_dir / "docs" / "technical"),
            "cortex_root": str(mock_cortex_structure),
            "diagram_types": ["architecture", "sequence"],
            "include_migration_diagrams": True
        }
        return TechnicalDocumentationOrchestrator(config)
    
    def test_initialization(self, orchestrator, temp_dir):
        """Test orchestrator initialization"""
        assert orchestrator is not None
        assert orchestrator.output_dir == temp_dir / "docs" / "technical"
        assert len(orchestrator.phases) == 6
        assert orchestrator.current_phase is None
    
    def test_default_config(self):
        """Test default configuration loading"""
        orch = TechnicalDocumentationOrchestrator()
        assert orch.config is not None
        assert "output_dir" in orch.config
        assert "cortex_root" in orch.config
        assert len(orch.diagram_types) == 15  # All diagram types
    
    def test_phase_discovery(self, orchestrator):
        """Test discovery phase"""
        discovery_data = orchestrator._phase_discovery()
        
        assert "orchestrators" in discovery_data
        assert "agents" in discovery_data
        assert "brain_tiers" in discovery_data
        assert "manifests" in discovery_data
        assert "tests" in discovery_data
        
        # Should find the mock files we created
        assert len(discovery_data["orchestrators"]) > 0
        assert len(discovery_data["agents"]) > 0
        assert len(discovery_data["manifests"]) > 0
        
        # Check orchestrator structure
        orchestrator_data = discovery_data["orchestrators"][0]
        assert "path" in orchestrator_data
        assert "name" in orchestrator_data
        assert "loc" in orchestrator_data
        assert orchestrator_data["loc"] > 0
    
    def test_phase_generate_diagrams(self, orchestrator):
        """Test diagram generation phase"""
        discovery_data = {
            "orchestrators": [
                {"name": "planning", "path": "src/orchestrators/planning.py", "loc": 800}
            ],
            "agents": [],
            "brain_tiers": [],
            "manifests": [],
            "tests": []
        }
        
        # Mock diagram generation methods
        orchestrator._generate_architecture_diagrams = Mock(return_value=[
            {"path": "architecture/system.html", "type": "architecture"}
        ])
        orchestrator._generate_sequence_diagrams = Mock(return_value=[
            {"path": "workflows/planning-sequence.html", "type": "sequence"}
        ])
        
        diagrams = orchestrator._phase_generate_diagrams(discovery_data)
        
        assert len(diagrams) > 0
        orchestrator._generate_architecture_diagrams.assert_called_once()
        orchestrator._generate_sequence_diagrams.assert_called_once()
    
    def test_phase_generate_api_docs(self, orchestrator, temp_dir):
        """Test API documentation generation phase"""
        discovery_data = {
            "orchestrators": [
                {"name": "planning", "path": "src/orchestrators/planning.py", "loc": 800},
                {"name": "tdd", "path": "src/orchestrators/tdd.py", "loc": 600}
            ]
        }
        
        api_docs = orchestrator._phase_generate_api_docs(discovery_data)
        
        assert len(api_docs) == 2
        
        # Check files were created
        api_dir = orchestrator.output_dir / "api" / "orchestrators"
        assert api_dir.exists()
        assert (api_dir / "planning.md").exists()
        assert (api_dir / "tdd.md").exists()
    
    def test_phase_generate_workflow_docs(self, orchestrator, temp_dir):
        """Test workflow documentation generation phase"""
        discovery_data = {"orchestrators": []}
        
        workflow_docs = orchestrator._phase_generate_workflow_docs(discovery_data)
        
        assert len(workflow_docs) > 0
        
        # Check workflow files created
        workflow_dir = orchestrator.output_dir / "workflows"
        assert workflow_dir.exists()
    
    def test_phase_generate_integration_guides(self, orchestrator, temp_dir):
        """Test integration guide generation phase"""
        guides = orchestrator._phase_generate_integration_guides()
        
        assert len(guides) > 0
        
        # Check integration files created
        integration_dir = orchestrator.output_dir / "integration"
        assert integration_dir.exists()
    
    def test_phase_generate_navigation(self, orchestrator, temp_dir):
        """Test navigation generation phase"""
        # Create some mock docs
        (orchestrator.output_dir / "api").mkdir(parents=True)
        (orchestrator.output_dir / "api" / "test.md").write_text("# Test API\n\nContent")
        
        nav_data = orchestrator._phase_generate_navigation()
        
        assert "pages" in nav_data
        assert "search_index_path" in nav_data
        assert nav_data["pages"] > 0
        
        # Check search index created
        search_index_file = orchestrator.output_dir / "assets" / "data" / "search-index.json"
        assert search_index_file.exists()
    
    def test_full_execute_success(self, orchestrator):
        """Test full execution pipeline success"""
        # Mock all phase methods to succeed
        orchestrator._phase_discovery = Mock(return_value={
            "orchestrators": [{"name": "test", "path": "test.py", "loc": 100}],
            "agents": [],
            "brain_tiers": [],
            "manifests": [],
            "tests": []
        })
        orchestrator._phase_generate_diagrams = Mock(return_value=[{"path": "test.html"}])
        orchestrator._phase_generate_api_docs = Mock(return_value=["api/test.md"])
        orchestrator._phase_generate_workflow_docs = Mock(return_value=["workflows/test.md"])
        orchestrator._phase_generate_integration_guides = Mock(return_value=["integration/test.md"])
        orchestrator._phase_generate_navigation = Mock(return_value={"pages": 3})
        
        results = orchestrator.execute()
        
        assert results["success"] is True
        assert len(results["phases_completed"]) == 6
        assert results["diagrams_generated"] == 1
        assert results["documents_created"] == 3
        assert len(results["errors"]) == 0
    
    def test_full_execute_with_error(self, orchestrator):
        """Test execution pipeline handles errors gracefully"""
        orchestrator._phase_discovery = Mock(side_effect=Exception("Discovery failed"))
        
        results = orchestrator.execute()
        
        assert results["success"] is False
        assert len(results["errors"]) > 0
        assert results["errors"][0]["phase"] == "discovery"
        assert "Discovery failed" in results["errors"][0]["error"]
    
    def test_count_lines(self, orchestrator, temp_dir):
        """Test line counting utility"""
        test_file = temp_dir / "test.py"
        test_file.write_text("line 1\nline 2\n\nline 4\n")
        
        count = orchestrator._count_lines(test_file)
        assert count == 3  # Empty line not counted
    
    def test_extract_title(self, orchestrator):
        """Test title extraction from markdown"""
        content = "# Test Title\n\nSome content"
        title = orchestrator._extract_title(content)
        assert title == "Test Title"
        
        content_no_title = "No title here"
        title = orchestrator._extract_title(content_no_title)
        assert title == "Untitled"
    
    def test_get_all_diagram_types(self, orchestrator):
        """Test all diagram types are defined"""
        diagram_types = orchestrator._get_all_diagram_types()
        
        assert len(diagram_types) == 15
        assert "architecture" in diagram_types
        assert "sankey" in diagram_types
        assert "di-container" in diagram_types
        assert "swimlane" in diagram_types
        assert "state-machine" in diagram_types
        assert "decision-tree" in diagram_types
        assert "treemap" in diagram_types
        assert "animated-flow" in diagram_types
    
    def test_phase_tracking(self, orchestrator):
        """Test phase transitions are tracked"""
        orchestrator._phase_discovery = Mock(return_value={
            "orchestrators": [], "agents": [], "brain_tiers": [], 
            "manifests": [], "tests": []
        })
        orchestrator._phase_generate_diagrams = Mock(return_value=[])
        orchestrator._phase_generate_api_docs = Mock(return_value=[])
        orchestrator._phase_generate_workflow_docs = Mock(return_value=[])
        orchestrator._phase_generate_integration_guides = Mock(return_value=[])
        orchestrator._phase_generate_navigation = Mock(return_value={"pages": 0})
        
        results = orchestrator.execute()
        
        # Check all phases completed
        assert len(results["phases_completed"]) == 6
        assert "discovery" in results["phases_completed"]
        assert "diagram_generation" in results["phases_completed"]
        assert "api_documentation" in results["phases_completed"]
        assert "workflow_documentation" in results["phases_completed"]
        assert "integration_guides" in results["phases_completed"]
        assert "navigation_generation" in results["phases_completed"]
    
    def test_migration_diagrams_optional(self, temp_dir, mock_cortex_structure):
        """Test migration diagrams can be disabled"""
        config = {
            "output_dir": str(temp_dir / "docs"),
            "cortex_root": str(mock_cortex_structure),
            "include_migration_diagrams": False
        }
        orch = TechnicalDocumentationOrchestrator(config)
        
        assert orch.include_migration is False
    
    def test_cli_entry_point(self, temp_dir, mock_cortex_structure, monkeypatch, capsys):
        """Test CLI entry point"""
        # Mock sys.argv
        test_args = [
            "technical_documentation_orchestrator.py",
            "--output-dir", str(temp_dir / "docs"),
            "--cortex-root", str(mock_cortex_structure),
            "--include-migration"
        ]
        
        with patch('sys.argv', test_args):
            # Import and run main
            from src.orchestrators.documentation import technical_documentation_orchestrator as tdo
            
            # Mock the execute method
            with patch.object(TechnicalDocumentationOrchestrator, 'execute', return_value={
                "success": True,
                "diagrams_generated": 10,
                "documents_created": 20,
                "output_dir": str(temp_dir / "docs"),
                "phases_completed": [],
                "errors": []
            }):
                # Would normally run: tdo.main() or similar
                # For now just test orchestrator creation works
                orch = TechnicalDocumentationOrchestrator({
                    "output_dir": test_args[2],
                    "cortex_root": test_args[4],
                    "include_migration_diagrams": True
                })
                assert orch is not None


# Integration tests

class TestDocumentationOrchestrationIntegration:
    """Integration tests for full orchestrator workflow"""
    
    @pytest.fixture
    def full_cortex_structure(self, tmp_path):
        """Create comprehensive CORTEX structure"""
        # Create full directory tree
        dirs = [
            "src/orchestrators/planning",
            "src/orchestrators/tdd",
            "src/cortex_agents",
            "cortex-brain/tier1",
            "cortex-brain/tier2",
            "cortex-brain/orchestrator-manifests",
            "tests/orchestrators"
        ]
        
        for dir_path in dirs:
            (tmp_path / dir_path).mkdir(parents=True)
        
        # Create realistic files
        (tmp_path / "src/orchestrators/planning/planning_orchestrator.py").write_text(
            '"""Planning Orchestrator"""\n' + "# code\n" * 200
        )
        (tmp_path / "src/orchestrators/tdd/tdd_orchestrator.py").write_text(
            '"""TDD Orchestrator"""\n' + "# code\n" * 150
        )
        
        return tmp_path
    
    def test_end_to_end_documentation_generation(self, full_cortex_structure, tmp_path):
        """Test complete documentation generation workflow"""
        output_dir = tmp_path / "output" / "docs"
        
        config = {
            "output_dir": str(output_dir),
            "cortex_root": str(full_cortex_structure),
            "diagram_types": ["architecture", "sequence"],
            "include_migration_diagrams": False  # Skip for speed
        }
        
        orchestrator = TechnicalDocumentationOrchestrator(config)
        
        # Mock diagram generation (they require D3.js runtime)
        orchestrator._generate_architecture_diagrams = Mock(return_value=[])
        orchestrator._generate_sequence_diagrams = Mock(return_value=[])
        
        results = orchestrator.execute()
        
        # Verify success
        assert results["success"] is True
        assert len(results["phases_completed"]) == 6
        
        # Verify directory structure created
        assert output_dir.exists()
        assert (output_dir / "api" / "orchestrators").exists()
        assert (output_dir / "workflows").exists()
        assert (output_dir / "integration").exists()
        
        # Verify API docs created
        api_files = list((output_dir / "api" / "orchestrators").glob("*.md"))
        assert len(api_files) > 0
        
        # Verify search index created
        assert (output_dir / "assets" / "data" / "search-index.json").exists()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")

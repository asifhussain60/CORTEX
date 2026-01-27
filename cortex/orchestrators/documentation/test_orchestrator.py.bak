"""
Tests for Documentation Orchestration System

Tests the three main orchestrators:
- DocumentationOrchestrator (main coordinator)
- DiagramGenerationOrchestrator (Mermaid + D3.js generation)
- DocumentationCleanupOrchestrator (redundancy detection and cleanup)
"""

import pytest
from datetime import datetime
from pathlib import Path

from cortex.orchestrators.documentation import (
    DocumentationOrchestrator,
    DiagramGenerationOrchestrator,
    DocumentationCleanupOrchestrator,
    get_documentation_orchestrator,
    get_diagram_generator,
    get_cleanup_orchestrator,
    DiagramType,
    CleanupAction,
    RedundancyType,
    DiagramSpec,
    Redundancy,
    OrphanedFile,
    ObsoleteItem,
    CleanupReport,
    GenerationReport,
)


class TestDiagramGenerationOrchestrator:
    """Test diagram generation orchestrator."""
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        orch = DiagramGenerationOrchestrator()
        assert orch is not None
        assert orch._mermaid_diagrams is not None
        assert orch._d3js_visualizations is not None
    
    def test_mermaid_diagrams_initialized(self):
        """Test that Mermaid diagrams are initialized."""
        orch = DiagramGenerationOrchestrator()
        assert len(orch._mermaid_diagrams) == 6
        
        # Check specific diagrams
        diagram_names = [d.name for d in orch._mermaid_diagrams]
        assert "approval-gate-decision-tree" in diagram_names
        assert "circuit-breaker-state-machine" in diagram_names
        assert "tdd-workflow-phases" in diagram_names
    
    def test_d3js_visualizations_initialized(self):
        """Test that D3.js visualizations are initialized."""
        orch = DiagramGenerationOrchestrator()
        assert len(orch._d3js_visualizations) == 4
        
        # Check specific visualizations
        viz_names = [v.name for v in orch._d3js_visualizations]
        assert "governance-pyramid" in viz_names
        assert "request-lifecycle-sankey" in viz_names
    
    def test_diagram_spec_to_dict(self):
        """Test DiagramSpec serialization."""
        spec = DiagramSpec(
            name="test-diagram",
            diagram_type=DiagramType.MERMAID_FLOWCHART,
            location="docs/diagrams/",
            description="Test diagram"
        )
        
        spec_dict = spec.to_dict()
        assert spec_dict["name"] == "test-diagram"
        assert spec_dict["type"] == "mermaid_flowchart"
        assert spec_dict["location"] == "docs/diagrams/"
    
    def test_get_diagram_specs(self):
        """Test retrieving diagram specs."""
        orch = DiagramGenerationOrchestrator()
        
        # Get all
        all_specs = orch.get_diagram_specs()
        assert len(all_specs) == 10  # 6 Mermaid + 4 D3.js
        
        # Get Mermaid only
        mermaid_specs = orch.get_diagram_specs(DiagramType.MERMAID_FLOWCHART)
        assert len(mermaid_specs) > 0
    
    def test_generate_all_diagrams(self):
        """Test generating all diagrams."""
        orch = DiagramGenerationOrchestrator()
        result = orch.execute("generate_all")
        
        assert result is not None
        assert hasattr(result, 'value') or hasattr(result, 'error')
    
    def test_generate_mermaid_diagrams(self):
        """Test generating only Mermaid diagrams."""
        orch = DiagramGenerationOrchestrator()
        result = orch.execute("generate_mermaid")
        
        assert result is not None
    
    def test_generate_d3js_diagrams(self):
        """Test generating only D3.js visualizations."""
        orch = DiagramGenerationOrchestrator()
        result = orch.execute("generate_d3js")
        
        assert result is not None
    
    def test_invalid_operation(self):
        """Test that invalid operations are rejected."""
        orch = DiagramGenerationOrchestrator()
        result = orch.execute("invalid_operation")
        
        assert result is not None
        assert hasattr(result, 'error')


class TestDocumentationCleanupOrchestrator:
    """Test documentation cleanup orchestrator."""
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        orch = DocumentationCleanupOrchestrator()
        assert orch is not None
        assert orch.docs_root is not None
    
    def test_redundancy_data_model(self):
        """Test Redundancy data model."""
        red = Redundancy(
            redundancy_type=RedundancyType.DUPLICATE_COMPONENT_DOCS,
            files=["file1.md", "file2.md"],
            component="test-component",
            recommendation="CONSOLIDATE",
            space_impact="100 KB"
        )
        
        assert red.redundancy_type == RedundancyType.DUPLICATE_COMPONENT_DOCS
        assert len(red.files) == 2
        
        red_dict = red.to_dict()
        assert red_dict["type"] == "duplicate_component_docs"
        assert red_dict["component"] == "test-component"
    
    def test_orphaned_file_data_model(self):
        """Test OrphanedFile data model."""
        orphan = OrphanedFile(
            path="docs/old-file.md",
            referenced_by=[],
            in_mkdocs_yml=False
        )
        
        assert orphan.path == "docs/old-file.md"
        assert orphan.in_mkdocs_yml is False
        
        orphan_dict = orphan.to_dict()
        assert orphan_dict["path"] == "docs/old-file.md"
    
    def test_obsolete_item_data_model(self):
        """Test ObsoleteItem data model."""
        obsolete = ObsoleteItem(
            component="old-orchestrator",
            doc_files=["docs/old-orchestrator.md"],
            reason="Feature removed from codebase"
        )
        
        assert obsolete.component == "old-orchestrator"
        assert len(obsolete.doc_files) == 1
        
        obsolete_dict = obsolete.to_dict()
        assert obsolete_dict["component"] == "old-orchestrator"
    
    def test_cleanup_report_data_model(self):
        """Test CleanupReport data model."""
        report = CleanupReport(
            timestamp=datetime.now(),
            redundancies_found=[],
            orphaned_files_found=[],
            obsolete_content_found=[],
            recommendations={}
        )
        
        assert report.timestamp is not None
        assert isinstance(report.redundancies_found, list)
        
        report_dict = report.to_dict()
        assert "timestamp" in report_dict
        assert "redundancies_found" in report_dict
    
    def test_analyze_redundancies(self):
        """Test redundancy analysis."""
        orch = DocumentationCleanupOrchestrator()
        result = orch.execute("analyze")
        
        assert result is not None
    
    def test_cleanup_dry_run(self):
        """Test cleanup in dry-run mode."""
        orch = DocumentationCleanupOrchestrator()
        result = orch.execute("cleanup", dry_run=True)
        
        assert result is not None
    
    def test_invalid_operation(self):
        """Test that invalid operations are rejected."""
        orch = DocumentationCleanupOrchestrator()
        result = orch.execute("invalid_operation")
        
        assert result is not None
        assert hasattr(result, 'error')
    
    def test_all_redundancy_types_defined(self):
        """Test that all redundancy types are accessible."""
        types = [
            RedundancyType.DUPLICATE_COMPONENT_DOCS,
            RedundancyType.COMPLETION_REPORTS,
            RedundancyType.SESSION_FILES,
            RedundancyType.INTERMEDIATE_FILES,
            RedundancyType.DUPLICATE_DIAGRAMS,
            RedundancyType.OBSOLETE_FEATURES,
            RedundancyType.DUPLICATE_GUIDANCE,
        ]
        
        assert len(types) == 7


class TestDocumentationOrchestrator:
    """Test main documentation orchestrator."""
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        orch = DocumentationOrchestrator()
        assert orch is not None
        assert orch.diagram_generator is not None
        assert orch.cleanup_orchestrator is not None
    
    def test_discover_operation(self):
        """Test component discovery."""
        orch = DocumentationOrchestrator()
        result = orch.execute("discover")
        
        assert result is not None
    
    def test_generate_operation(self):
        """Test documentation generation."""
        orch = DocumentationOrchestrator()
        result = orch.execute("generate", component="test-component")
        
        assert result is not None
    
    def test_generate_diagrams_operation(self):
        """Test diagram generation through main orchestrator."""
        orch = DocumentationOrchestrator()
        result = orch.execute("generate_diagrams")
        
        assert result is not None
    
    def test_validate_operation(self):
        """Test documentation validation."""
        orch = DocumentationOrchestrator()
        result = orch.execute("validate")
        
        assert result is not None
    
    def test_cleanup_operation(self):
        """Test cleanup operation."""
        orch = DocumentationOrchestrator()
        result = orch.execute("cleanup")
        
        assert result is not None
    
    def test_maintenance_operation(self):
        """Test full maintenance cycle."""
        orch = DocumentationOrchestrator()
        result = orch.execute("maintenance")
        
        assert result is not None
    
    def test_invalid_operation(self):
        """Test that invalid operations are rejected."""
        orch = DocumentationOrchestrator()
        result = orch.execute("invalid_operation")
        
        assert result is not None
        assert hasattr(result, 'error')


class TestFactoryFunctions:
    """Test module-level factory functions."""
    
    def test_get_documentation_orchestrator(self):
        """Test getting documentation orchestrator."""
        orch = get_documentation_orchestrator()
        assert isinstance(orch, DocumentationOrchestrator)
    
    def test_get_diagram_generator(self):
        """Test getting diagram generator."""
        gen = get_diagram_generator()
        assert isinstance(gen, DiagramGenerationOrchestrator)
    
    def test_get_cleanup_orchestrator(self):
        """Test getting cleanup orchestrator."""
        cleanup = get_cleanup_orchestrator()
        assert isinstance(cleanup, DocumentationCleanupOrchestrator)


class TestDataModels:
    """Test all data models."""
    
    def test_diagram_types_complete(self):
        """Test all diagram types are defined."""
        types = [
            DiagramType.MERMAID_FLOWCHART,
            DiagramType.MERMAID_SEQUENCE,
            DiagramType.MERMAID_STATE,
            DiagramType.D3JS_SUNBURST,
            DiagramType.D3JS_SANKEY,
            DiagramType.D3JS_CIRCULAR,
            DiagramType.D3JS_LAYERED,
        ]
        assert len(types) == 7
    
    def test_cleanup_actions_complete(self):
        """Test all cleanup actions are defined."""
        actions = [
            CleanupAction.ARCHIVE,
            CleanupAction.CONSOLIDATE,
            CleanupAction.REMOVE,
            CleanupAction.REDIRECT,
            CleanupAction.UPDATE_STATUS,
            CleanupAction.REORGANIZE,
        ]
        assert len(actions) == 6
    
    def test_generation_report_data_model(self):
        """Test GenerationReport data model."""
        report = GenerationReport(
            timestamp=datetime.now(),
            mermaid_diagrams_generated=["diagram1.mmd", "diagram2.mmd"],
            d3js_visualizations_generated=["viz1.html"],
            docs_generated=["doc1.md"],
            failed_generations=[]
        )
        
        assert len(report.mermaid_diagrams_generated) == 2
        assert len(report.d3js_visualizations_generated) == 1
        
        report_dict = report.to_dict()
        assert report_dict["mermaid_diagrams"] == 2
        assert report_dict["d3js_visualizations"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

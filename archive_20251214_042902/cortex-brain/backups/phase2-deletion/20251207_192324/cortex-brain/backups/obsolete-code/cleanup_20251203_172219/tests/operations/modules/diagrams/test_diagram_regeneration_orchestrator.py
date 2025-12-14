#!/usr/bin/env python3
"""
Tests for Diagram Regeneration Orchestrator

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.operations.modules.diagrams.diagram_regeneration_orchestrator import (
    DiagramRegenerationOrchestrator,
    DiagramRegenerationReport,
    DiagramStatus
)


@pytest.fixture
def orchestrator(tmp_path):
    """Create orchestrator with temporary directory"""
    cortex_root = tmp_path / "CORTEX"
    cortex_root.mkdir()
    
    # Create directory structure
    (cortex_root / "cortex-brain" / "admin" / "reports").mkdir(parents=True)
    (cortex_root / "docs" / "diagrams" / "prompts").mkdir(parents=True)
    (cortex_root / "docs" / "diagrams" / "narratives").mkdir(parents=True)
    (cortex_root / "docs" / "diagrams" / "mermaid").mkdir(parents=True)
    (cortex_root / "docs" / "diagrams" / "img").mkdir(parents=True)
    
    return DiagramRegenerationOrchestrator(cortex_root)


@pytest.fixture
def sample_diagrams(orchestrator):
    """Create sample diagram files"""
    # Create files for first diagram (01-tier-architecture) - complete
    (orchestrator.prompts_path / "01-tier-architecture.md").write_text("# Prompt")
    (orchestrator.narratives_path / "01-tier-architecture.md").write_text("# Narrative")
    (orchestrator.mermaid_path / "01-tier-architecture.mmd").write_text("graph TD")
    (orchestrator.img_path / "01-tier-architecture.png").write_bytes(b"PNG")
    
    # Create files for second diagram (02-agent-system) - partial (missing image)
    (orchestrator.prompts_path / "02-agent-system.md").write_text("# Prompt")
    (orchestrator.narratives_path / "02-agent-system.md").write_text("# Narrative")
    (orchestrator.mermaid_path / "02-agent-system.mmd").write_text("graph TD")
    
    # Third diagram (03-plugin-architecture) - no files (incomplete)
    
    return orchestrator


def test_diagram_status_completion():
    """Test DiagramStatus completion calculation"""
    # Complete diagram (all 4 files)
    complete = DiagramStatus(
        id="01",
        name="test",
        title="Test Diagram",
        has_prompt=True,
        has_narrative=True,
        has_mermaid=True,
        has_image=True
    )
    assert complete.completion_percentage == 100
    assert complete.status == "complete"
    
    # Mostly complete (3 of 4)
    mostly_complete = DiagramStatus(
        id="02",
        name="test",
        title="Test Diagram",
        has_prompt=True,
        has_narrative=True,
        has_mermaid=True,
        has_image=False
    )
    assert mostly_complete.completion_percentage == 75
    assert mostly_complete.status == "mostly_complete"
    
    # Partial (2 of 4)
    partial = DiagramStatus(
        id="03",
        name="test",
        title="Test Diagram",
        has_prompt=True,
        has_narrative=True,
        has_mermaid=False,
        has_image=False
    )
    assert partial.completion_percentage == 50
    assert partial.status == "partial"
    
    # Incomplete (1 of 4)
    incomplete = DiagramStatus(
        id="04",
        name="test",
        title="Test Diagram",
        has_prompt=True,
        has_narrative=False,
        has_mermaid=False,
        has_image=False
    )
    assert incomplete.completion_percentage == 25
    assert incomplete.status == "incomplete"


def test_scan_diagrams_empty(orchestrator):
    """Test scanning with no diagram files"""
    diagrams = orchestrator._scan_diagrams()
    
    # Should find all 17 diagram definitions
    assert len(diagrams) == 17
    
    # All should be incomplete
    for diagram in diagrams:
        assert diagram.completion_percentage == 0
        assert diagram.status == "incomplete"


def test_scan_diagrams_with_files(sample_diagrams):
    """Test scanning with sample diagram files"""
    diagrams = sample_diagrams._scan_diagrams()
    
    # Should find all 17 diagrams
    assert len(diagrams) == 17
    
    # Check first diagram (complete)
    diagram_01 = next(d for d in diagrams if d.id == "01")
    assert diagram_01.completion_percentage == 100
    assert diagram_01.status == "complete"
    assert diagram_01.has_prompt
    assert diagram_01.has_narrative
    assert diagram_01.has_mermaid
    assert diagram_01.has_image
    
    # Check second diagram (partial - missing image)
    diagram_02 = next(d for d in diagrams if d.id == "02")
    assert diagram_02.completion_percentage == 75
    assert diagram_02.status == "mostly_complete"
    assert diagram_02.has_prompt
    assert diagram_02.has_narrative
    assert diagram_02.has_mermaid
    assert not diagram_02.has_image
    
    # Check third diagram (incomplete)
    diagram_03 = next(d for d in diagrams if d.id == "03")
    assert diagram_03.completion_percentage == 0
    assert diagram_03.status == "incomplete"


def test_execute_generates_report(sample_diagrams):
    """Test execute generates valid report"""
    report = sample_diagrams.execute()
    
    assert isinstance(report, DiagramRegenerationReport)
    assert report.total_diagrams == 17
    assert report.complete_diagrams == 1  # Only 01 is complete
    assert report.incomplete_diagrams == 16
    assert len(report.diagrams) == 17
    assert report.overall_completion > 0


def test_dashboard_generation(sample_diagrams):
    """Test dashboard HTML file is generated"""
    report = sample_diagrams.execute()
    
    dashboard_path = sample_diagrams.cortex_brain / "admin" / "reports" / "diagram-regeneration-dashboard.html"
    assert dashboard_path.exists()
    
    # Read dashboard content with UTF-8 encoding
    content = dashboard_path.read_text(encoding='utf-8')
    assert "Diagram Regeneration Dashboard" in content
    assert "Overall Completion" in content


def test_dashboard_visualizations_structure(sample_diagrams):
    """Test dashboard has correct visualization structure"""
    report = sample_diagrams.execute()
    
    # Build visualizations
    viz = sample_diagrams._build_diagram_visualizations(report)
    
    # Check force graph structure
    assert "forceGraph" in viz
    assert "nodes" in viz["forceGraph"]
    assert "links" in viz["forceGraph"]
    
    # Should have central node + 17 diagram nodes = 18 total
    assert len(viz["forceGraph"]["nodes"]) == 18
    
    # Should have 17 links (each diagram to center)
    assert len(viz["forceGraph"]["links"]) == 17
    
    # Check time series structure
    assert "timeSeries" in viz
    assert "labels" in viz["timeSeries"]
    assert "datasets" in viz["timeSeries"]
    assert len(viz["timeSeries"]["labels"]) == 10  # 10 days
    assert len(viz["timeSeries"]["datasets"]) == 2  # Overall completion + Complete diagrams

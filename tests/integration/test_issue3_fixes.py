"""
Integration Tests for Issue #3 Fix
Purpose: Test feedback agent, view discovery, and TDD workflow integration
Created: 2025-11-23
Author: Asif Hussain
"""

import pytest
import json
from pathlib import Path
import tempfile
import shutil
import sys

# Add src directory to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from agents.feedback_agent import FeedbackAgent, handle_feedback_command
from agents.view_discovery_agent import ViewDiscoveryAgent, discover_views_for_testing
from workflows.tdd_workflow_integrator import TDDWorkflowIntegrator


class TestFeedbackAgent:
    """Test feedback command functionality (P0 Fix)."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.brain_path = self.temp_dir / "cortex-brain"
        self.agent = FeedbackAgent(brain_path=str(self.brain_path))
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_feedback_report_creation(self):
        """Test that feedback command creates structured report."""
        result = self.agent.create_feedback_report(
            user_input="The TDD workflow lacks view discovery phase",
            feedback_type="gap",
            severity="critical"
        )
        
        assert result["success"] is True
        assert "CORTEX-FEEDBACK-" in result["feedback_id"]
        assert Path(result["file_path"]).exists()
        assert result["feedback_type"] == "gap"
        assert result["severity"] == "critical"
    
    def test_feedback_type_detection(self):
        """Test automatic feedback type detection."""
        # Bug detection
        result_bug = self.agent.create_feedback_report(
            "CORTEX crashes when generating tests"
        )
        assert result_bug["feedback_type"] == "bug"
        
        # Gap detection
        result_gap = self.agent.create_feedback_report(
            "CORTEX lacks automated view crawling"
        )
        assert result_gap["feedback_type"] == "gap"
        
        # Improvement detection
        result_improvement = self.agent.create_feedback_report(
            "CORTEX should provide better error messages"
        )
        assert result_improvement["feedback_type"] == "improvement"
    
    def test_feedback_report_structure(self):
        """Test that generated report has correct structure."""
        result = self.agent.create_feedback_report(
            "Test feedback content",
            context={
                "conversation_id": "test-conv-123",
                "files": ["test.cs", "test.razor"],
                "workflow": "TDD"
            }
        )
        
        # Read generated report
        with open(result["file_path"], 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify structure
        assert "# CORTEX Feedback Report" in content
        assert "Report ID:" in content
        assert "Test feedback content" in content
        assert "Context Information" in content
        assert "test-conv-123" in content
        assert "Next Actions" in content


class TestViewDiscoveryAgent:
    """Test view discovery functionality (P0 Fix)."""
    
    def setup_method(self):
        """Setup test environment with sample Razor files."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_root = self.temp_dir / "TestProject"
        self.project_root.mkdir()
        
        # Create sample Razor file
        self.views_dir = self.project_root / "Views"
        self.views_dir.mkdir()
        
        sample_razor = self.views_dir / "TestPage.razor"
        sample_razor.write_text("""
@page "/test"

<h1>Test Page</h1>

<button id="openSessionBtn" class="btn btn-primary">Generate Token</button>
<button data-testid="control-panel-btn">Open Control Panel</button>
<button class="btn btn-secondary">No ID Button</button>

<input id="username" type="text" placeholder="Username" />
<select id="categoryDropdown" class="form-select">
    <option>Category 1</option>
</select>
""", encoding='utf-8')
        
        self.agent = ViewDiscoveryAgent(project_root=self.project_root)
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_element_id_discovery(self):
        """Test that agent discovers element IDs correctly."""
        view_files = list(self.views_dir.glob("*.razor"))
        results = self.agent.discover_views(view_files)
        
        assert results["files_processed"] == [str(view_files[0])]
        assert len(results["elements_discovered"]) > 0
        
        # Find specific elements
        elements = results["elements_discovered"]
        element_ids = [e["element_id"] for e in elements if e["element_id"]]
        
        assert "openSessionBtn" in element_ids
        assert "username" in element_ids
        assert "categoryDropdown" in element_ids
    
    def test_data_testid_discovery(self):
        """Test that agent discovers data-testid attributes."""
        view_files = list(self.views_dir.glob("*.razor"))
        results = self.agent.discover_views(view_files)
        
        elements = results["elements_discovered"]
        testids = [e["data_testid"] for e in elements if e["data_testid"]]
        
        assert "control-panel-btn" in testids
    
    def test_selector_strategy_generation(self):
        """Test that agent generates correct selector strategies."""
        view_files = list(self.views_dir.glob("*.razor"))
        results = self.agent.discover_views(view_files)
        
        strategies = results["selector_strategies"]
        
        # ID-based selector should be generated
        assert strategies.get("openSessionBtn") == "#openSessionBtn"
        
        # data-testid selector should be generated
        assert "[data-testid='control-panel-btn']" in str(strategies.values())
    
    def test_components_without_ids(self):
        """Test that agent identifies components without IDs."""
        view_files = list(self.views_dir.glob("*.razor"))
        results = self.agent.discover_views(view_files)
        
        components_without_ids = results["components_without_ids"]
        
        # Should find the button without ID
        assert len(components_without_ids) > 0
        assert any(comp["text"] == "No ID Button" for comp in components_without_ids)
    
    def test_route_extraction(self):
        """Test that agent extracts @page routes."""
        view_files = list(self.views_dir.glob("*.razor"))
        results = self.agent.discover_views(view_files)
        
        nav_flows = results["navigation_flows"]
        assert len(nav_flows) > 0
        assert nav_flows[0]["route"] == "/test"


class TestTDDWorkflowIntegration:
    """Test TDD workflow integration (P0 Fix)."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_root = self.temp_dir / "TestProject"
        self.project_root.mkdir()
        
        # Create sample views
        self.views_dir = self.project_root / "Views"
        self.views_dir.mkdir()
        
        sample_razor = self.views_dir / "SessionOpener.razor"
        sample_razor.write_text("""
@page "/session/open"

<button id="openSessionBtn">Generate Token</button>
<button id="controlPanelBtn">Open Control Panel</button>
""", encoding='utf-8')
        
        self.integrator = TDDWorkflowIntegrator(
            project_root=self.project_root
        )
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_discovery_phase_execution(self):
        """Test that discovery phase runs successfully."""
        view_files = list(self.views_dir.glob("*.razor"))
        results = self.integrator.run_discovery_phase(
            target_views=view_files,
            cache_results=False
        )
        
        assert len(results["elements_discovered"]) > 0
        assert "openSessionBtn" in str(results)
    
    def test_selector_lookup(self):
        """Test getting selector for element description."""
        view_files = list(self.views_dir.glob("*.razor"))
        discovery_results = self.integrator.run_discovery_phase(
            target_views=view_files,
            cache_results=False
        )
        
        selector = self.integrator.get_selector_for_element(
            "openSessionBtn",
            discovery_results
        )
        
        assert selector == "#openSessionBtn"
    
    def test_selector_validation(self):
        """Test validation of test selectors against discovered elements."""
        view_files = list(self.views_dir.glob("*.razor"))
        discovery_results = self.integrator.run_discovery_phase(
            target_views=view_files,
            cache_results=False
        )
        
        # Test with valid and invalid selectors
        test_selectors = [
            "#openSessionBtn",  # Valid
            "button:has-text('Generate Token')",  # Invalid (not discovered)
            "#controlPanelBtn"  # Valid
        ]
        
        validation = self.integrator.validate_test_selectors(
            test_selectors,
            discovery_results
        )
        
        assert "#openSessionBtn" in validation["valid_selectors"]
        assert "#controlPanelBtn" in validation["valid_selectors"]
        assert len(validation["invalid_selectors"]) == 1
    
    def test_discovery_report_generation(self):
        """Test that discovery report is generated correctly."""
        view_files = list(self.views_dir.glob("*.razor"))
        discovery_results = self.integrator.run_discovery_phase(
            target_views=view_files,
            cache_results=False
        )
        
        report = self.integrator.generate_discovery_report(
            discovery_results
        )
        
        assert "# View Discovery Report" in report
        assert "TestProject" in report
        assert "Selector Strategies" in report
        assert "openSessionBtn" in report or "#openSessionBtn" in report


class TestEndToEndWorkflow:
    """Test complete end-to-end TDD workflow with discovery."""
    
    def test_complete_workflow(self):
        """
        Test complete workflow: User Request → Discovery → Test Generation Ready
        
        This simulates the Issue #3 scenario where discovery should happen
        BEFORE test generation to avoid assumed selectors.
        """
        # Setup
        temp_dir = Path(tempfile.mkdtemp())
        try:
            project_root = temp_dir / "TestProject"
            project_root.mkdir()
            
            views_dir = project_root / "Views"
            views_dir.mkdir()
            
            # Create realistic Razor file (like SessionOpener)
            session_opener = views_dir / "SessionOpener.razor"
            session_opener.write_text("""
@page "/host/session-opener/{token}"

<button id="openSessionBtn" class="btn btn-primary">
    Generate Token
</button>

<button id="controlPanelBtn" class="btn btn-success" style="display:none;">
    Open Control Panel
</button>

<button id="reg-transcript-canvas-btn">Transcript Canvas</button>
<button id="sidebar-start-session-btn">Start Session</button>
""", encoding='utf-8')
            
            # Run discovery phase
            integrator = TDDWorkflowIntegrator(project_root=project_root)
            
            view_files = list(views_dir.glob("*.razor"))
            discovery_results = integrator.run_discovery_phase(
                target_views=view_files,
                cache_results=False
            )
            
            # Verify all expected elements were discovered
            strategies = discovery_results["selector_strategies"]
            
            assert "openSessionBtn" in strategies
            assert strategies["openSessionBtn"] == "#openSessionBtn"
            
            assert "controlPanelBtn" in strategies
            assert strategies["controlPanelBtn"] == "#controlPanelBtn"
            
            # Verify test generator would now have correct selectors
            # (instead of text-based assumptions)
            assert "#openSessionBtn" in str(discovery_results)
            assert "button:has-text" not in strategies.get("openSessionBtn", "")
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

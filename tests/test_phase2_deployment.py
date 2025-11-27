"""
Integration test for Phase 2 deployment - UXEnhancementOrchestrator with dashboard

Tests the complete workflow:
1. Entry point detects enhancement request
2. Orchestrator runs analysis
3. Dashboard files are generated
4. JSON data is in correct format
5. Browser can open dashboard

Author: Asif Hussain
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrators.ux_enhancement_orchestrator import UXEnhancementOrchestrator


class TestPhase2Deployment:
    """Test Phase 2 dashboard deployment integration"""
    
    def test_orchestrator_generates_valid_json(self, tmp_path):
        """Test that orchestrator exports valid JSON in Phase 2 format"""
        orchestrator = UXEnhancementOrchestrator(cortex_root=tmp_path)
        
        # Create mock brain structure
        analysis_dir = tmp_path / "cortex-brain" / "documents" / "analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock analyze method execution
        codebase_info = {
            "name": "test-project",
            "file_count": 100,
            "timestamp": "2025-11-26T10:00:00Z"
        }
        
        quality = {"overall_score": 75, "maintainability": 70, "test_coverage": 60}
        architecture = {"health_score": 80, "components": [], "issues": []}
        performance = {"grade": "B", "bottlenecks": []}
        security = {"rating": "B", "vulnerabilities": {}}
        discovery = {"suggestions": []}
        
        # Export to dashboard format
        result = orchestrator._export_to_dashboard_format(
            codebase_info, quality, architecture, performance, security, discovery
        )
        
        # Validate structure
        assert "metadata" in result
        assert "scores" in result
        assert "summary" in result
        assert "architecture" in result
        assert "quality" in result
        assert "roadmap" in result
        assert "performance" in result
        assert "security" in result
        assert "discoveries" in result
        assert "testCoverage" in result
        
        # Validate metadata fields
        assert result["metadata"]["projectName"] == "test-project"
        assert result["metadata"]["fileCount"] == 100
        
        # Validate scores
        assert result["scores"]["overall"] == 75
        assert result["scores"]["quality"] == 75
        assert result["scores"]["architecture"] == 80
    
    def test_dashboard_html_generation(self, tmp_path):
        """Test that dashboard HTML is generated with correct structure"""
        orchestrator = UXEnhancementOrchestrator(cortex_root=tmp_path)
        
        # Create mock brain structure
        analysis_dir = tmp_path / "cortex-brain" / "documents" / "analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Create mock Phase 2 template
        template_dir = analysis_dir / "INTELLIGENT-UX-DEMO"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        template_html = template_dir / "dashboard.html"
        template_html.write_text("<!DOCTYPE html><html><body>Test Dashboard</body></html>")
        
        # Create assets directory
        assets_dir = template_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        (assets_dir / "test.js").write_text("console.log('test');")
        
        # Generate dashboard
        dashboard_data = {
            "metadata": {"project_name": "test-project", "timestamp": "2025-11-26T10:00:00Z"},
            "quality": {"overall_score": 75}
        }
        
        html_path = orchestrator._generate_dashboard_html(dashboard_data, "enhance my code")
        
        # Validate HTML was created
        assert html_path.exists()
        assert html_path.suffix == ".html"
        
        # Validate JSON was created
        json_path = html_path.parent / "analysis-data.json"
        assert json_path.exists()
        
        # Validate JSON content
        with open(json_path, 'r') as f:
            data = json.load(f)
            assert data == dashboard_data
        
        # Validate assets were copied
        output_assets = html_path.parent / "assets"
        assert output_assets.exists()
        assert (output_assets / "test.js").exists()
    
    def test_fallback_to_placeholder_html(self, tmp_path):
        """Test that orchestrator falls back to placeholder if template not found"""
        orchestrator = UXEnhancementOrchestrator(cortex_root=tmp_path)
        
        # Create mock brain structure WITHOUT Phase 2 template
        analysis_dir = tmp_path / "cortex-brain" / "documents" / "analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate dashboard (should use placeholder) - use Phase 2 format
        dashboard_data = {
            "metadata": {
                "projectName": "test-project",
                "timestamp": "2025-11-26T10:00:00Z"
            },
            "scores": {
                "overall": 75,
                "quality": 75,
                "architecture": 80,
                "performance": 70,
                "security": 65
            },
            "quality": {"overall_score": 75},
            "architecture": {"health_score": 80},
            "performance": {"grade": "B"},
            "security": {"rating": "B"}
        }
        
        html_path = orchestrator._generate_dashboard_html(dashboard_data, "enhance my code")
        
        # Validate HTML was created
        assert html_path.exists()
        
        # Read HTML content
        html_content = html_path.read_text()
        
        # Validate placeholder content
        assert "UX Enhancement Dashboard" in html_content
        assert "test-project" in html_content
        assert "75%" in html_content  # Quality score
        assert "80%" in html_content  # Architecture health
        assert "placeholder dashboard" in html_content.lower()
    
    @patch('webbrowser.open')
    def test_browser_opens_dashboard(self, mock_browser, tmp_path):
        """Test that orchestrator opens dashboard in browser"""
        orchestrator = UXEnhancementOrchestrator(cortex_root=tmp_path)
        
        # Create mock brain structure
        analysis_dir = tmp_path / "cortex-brain" / "documents" / "analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Create minimal codebase to analyze
        test_codebase = tmp_path / "test_codebase"
        test_codebase.mkdir()
        (test_codebase / "test.py").write_text("print('hello')")
        
        # Run analysis
        result = orchestrator.analyze_and_generate_dashboard(
            codebase_path=str(test_codebase),
            user_request="enhance my code",
            skip_explanation=True
        )
        
        # Validate browser was called
        assert mock_browser.called
        assert mock_browser.call_count == 1
        
        # Validate browser was called with file:// URL
        call_args = mock_browser.call_args[0][0]
        assert call_args.startswith("file://")
        assert call_args.endswith("dashboard.html")
    
    def test_json_data_schema_validation(self, tmp_path):
        """Test that exported JSON matches Phase 2 schema"""
        orchestrator = UXEnhancementOrchestrator(cortex_root=tmp_path)
        
        # Create test data
        codebase_info = {
            "name": "test-project",
            "file_count": 150,
            "timestamp": "2025-11-26T10:00:00Z",
            "line_count": 5000
        }
        
        quality = {
            "overall_score": 72,
            "maintainability": 68,
            "test_coverage": 65,
            "code_smells": {
                "longMethod": 10,
                "complexMethod": 5
            }
        }
        
        architecture = {
            "health_score": 74,
            "components": [
                {"id": "comp1", "name": "Component 1", "size": 20}
            ],
            "relationships": [],
            "issues": ["Issue 1", "Issue 2"]
        }
        
        performance = {"grade": "B", "bottlenecks": []}
        security = {"rating": "B", "vulnerabilities": {}}
        discovery = {"suggestions": [{"pattern": "test", "priority": "high"}]}
        
        # Export data
        result = orchestrator._export_to_dashboard_format(
            codebase_info, quality, architecture, performance, security, discovery
        )
        
        # Validate required top-level keys
        required_keys = [
            "metadata", "scores", "summary", "architecture",
            "quality", "roadmap", "performance", "security",
            "discoveries", "testCoverage"
        ]
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"
        
        # Validate metadata schema
        metadata = result["metadata"]
        assert "projectName" in metadata
        assert "timestamp" in metadata
        assert "fileCount" in metadata
        assert "lineCount" in metadata
        assert metadata["projectName"] == "test-project"
        assert metadata["fileCount"] == 150
        assert metadata["lineCount"] == 5000
        
        # Validate scores schema
        scores = result["scores"]
        score_keys = ["overall", "quality", "performance", "security", "architecture", "maintainability", "testCoverage"]
        for key in score_keys:
            assert key in scores, f"Missing score key: {key}"
            assert isinstance(scores[key], (int, float)), f"Score {key} must be numeric"
        
        # Validate summary schema
        summary = result["summary"]
        assert "text" in summary
        assert "quickWins" in summary
        assert "criticalIssues" in summary
        assert isinstance(summary["quickWins"], list)
        assert isinstance(summary["criticalIssues"], list)
        
        # Validate roadmap schema
        roadmap = result["roadmap"]
        assert "tasks" in roadmap
        assert "dependencies" in roadmap
        assert "milestones" in roadmap
        
        # Validate testCoverage schema
        testCoverage = result["testCoverage"]
        assert "overall" in testCoverage
        assert "byModule" in testCoverage
        assert "untested" in testCoverage
        assert testCoverage["overall"] == 65
    
    def test_end_to_end_workflow(self, tmp_path):
        """Test complete end-to-end workflow from entry point to dashboard"""
        # Create CORTEX mock structure
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        brain_dir = cortex_root / "cortex-brain"
        brain_dir.mkdir()
        
        analysis_dir = brain_dir / "documents" / "analysis"
        analysis_dir.mkdir(parents=True)
        
        # Create Phase 2 template
        template_dir = analysis_dir / "INTELLIGENT-UX-DEMO"
        template_dir.mkdir()
        
        template_html = template_dir / "dashboard.html"
        template_html.write_text("""
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
    <div id="tabs">
        <button data-tab="executive">Executive</button>
        <button data-tab="architecture">Architecture</button>
    </div>
    <div id="content"></div>
</body>
</html>
        """)
        
        assets_dir = template_dir / "assets"
        assets_dir.mkdir()
        js_dir = assets_dir / "js"
        js_dir.mkdir()
        (js_dir / "visualizations.js").write_text("console.log('viz');")
        
        # Create test codebase
        test_codebase = tmp_path / "test_project"
        test_codebase.mkdir()
        (test_codebase / "main.py").write_text("def main(): pass")
        (test_codebase / "utils.py").write_text("def helper(): pass")
        
        # Initialize orchestrator
        orchestrator = UXEnhancementOrchestrator(cortex_root=cortex_root)
        
        # Run analysis (mock browser open)
        with patch('webbrowser.open') as mock_browser:
            result = orchestrator.analyze_and_generate_dashboard(
                codebase_path=str(test_codebase),
                user_request="analyze and enhance my codebase",
                skip_explanation=True
            )
        
        # Validate result
        assert result["success"] is True
        assert "dashboard_path" in result
        assert "analysis_summary" in result
        
        # Validate dashboard was created
        dashboard_path = Path(result["dashboard_path"])
        assert dashboard_path.exists()
        assert dashboard_path.name == "dashboard.html"
        
        # Validate JSON was created
        json_path = dashboard_path.parent / "analysis-data.json"
        assert json_path.exists()
        
        # Load and validate JSON
        with open(json_path, 'r') as f:
            data = json.load(f)
            assert "metadata" in data
            assert "scores" in data
            assert data["metadata"]["projectName"] == "test_project"
        
        # Validate assets were copied
        output_assets = dashboard_path.parent / "assets"
        assert output_assets.exists()
        assert (output_assets / "js" / "visualizations.js").exists()
        
        # Validate browser was opened
        assert mock_browser.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

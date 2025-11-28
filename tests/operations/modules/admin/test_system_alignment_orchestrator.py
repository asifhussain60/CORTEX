"""
Tests for System Alignment Orchestrator

Tests convention-based discovery and validation without hardcoded lists.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from datetime import datetime
from src.operations.modules.admin.system_alignment_orchestrator import (
    SystemAlignmentOrchestrator,
    IntegrationScore,
    AlignmentReport
)
from src.operations.base_operation_module import OperationStatus


class TestIntegrationScore:
    """Test integration score calculation."""
    
    def test_score_calculation_all_checks_pass(self):
        """Test score when all validation checks pass."""
        score = IntegrationScore(
            feature_name="TestOrchestrator",
            feature_type="orchestrator",
            discovered=True,
            imported=True,
            instantiated=True,
            documented=True,
            tested=True,
            wired=True,
            optimized=True
        )
        
        assert score.score == 100
        assert score.status.endswith("Healthy")  # Accepts both "[OK] Healthy" and "✅ Healthy"
        assert len(score.issues) == 0
    
    def test_score_calculation_partial_integration(self):
        """Test score with partial integration."""
        score = IntegrationScore(
            feature_name="TestOrchestrator",
            feature_type="orchestrator",
            discovered=True,
            imported=True,
            instantiated=True,
            documented=False,
            tested=False,
            wired=False,
            optimized=False
        )
        
        assert score.score == 60
        assert score.status.endswith("Critical")  # Accepts both "[CRIT] Critical" and "❌ Critical"
        assert "Missing documentation" in score.issues
        assert "No test coverage" in score.issues
        assert "Not wired to entry point" in score.issues
    
    def test_score_calculation_warning_threshold(self):
        """Test score at warning threshold."""
        score = IntegrationScore(
            feature_name="TestOrchestrator",
            feature_type="orchestrator",
            discovered=True,
            imported=True,
            instantiated=True,
            documented=True,
            tested=False,
            wired=True,
            optimized=False
        )
        
        assert score.score == 80
        assert score.status.endswith("Warning")  # Accepts both "[WARN] Warning" and "⚠️ Warning"


class TestAlignmentReport:
    """Test alignment report generation."""
    
    def test_is_healthy_with_high_score(self):
        """Test healthy status with >80% overall health."""
        report = AlignmentReport(
            timestamp=datetime.now(),
            overall_health=85,
            critical_issues=0,
            warnings=2
        )
        
        assert report.is_healthy is True
        assert report.has_warnings is True
        assert report.has_errors is False
    
    def test_is_unhealthy_with_critical_issues(self):
        """Test unhealthy status with critical issues."""
        report = AlignmentReport(
            timestamp=datetime.now(),
            overall_health=60,
            critical_issues=3,
            warnings=1
        )
        
        assert report.is_healthy is False
        assert report.has_warnings is False
        assert report.has_errors is True
        assert report.issues_found == 4


class TestSystemAlignmentOrchestrator:
    """Test system alignment orchestrator."""
    
    @pytest.fixture
    def project_root(self, tmp_path):
        """Create temporary project structure."""
        # Create admin directory to simulate admin environment
        admin_dir = tmp_path / "cortex-brain" / "admin"
        admin_dir.mkdir(parents=True)
        
        # Create src directories
        (tmp_path / "src" / "operations" / "modules").mkdir(parents=True)
        (tmp_path / "src" / "workflows").mkdir(parents=True)
        (tmp_path / "src" / "agents").mkdir(parents=True)
        
        # Create response templates
        templates_dir = tmp_path / "cortex-brain"
        templates_file = templates_dir / "response-templates.yaml"
        templates_file.write_text("""
templates:
  test_template:
    name: Test Template
    triggers:
      - test trigger
    response_type: detailed
""")
        
        return tmp_path
    
    def test_admin_detection_with_admin_dir(self, project_root):
        """Test admin environment detection."""
        orchestrator = SystemAlignmentOrchestrator(
            context={"project_root": str(project_root)}
        )
        
        assert orchestrator._is_admin_environment() is True
    
    def test_admin_detection_without_admin_dir(self, tmp_path):
        """Test graceful decline in user repos."""
        # Create structure without admin directory
        (tmp_path / "cortex-brain").mkdir(parents=True)
        
        orchestrator = SystemAlignmentOrchestrator(
            context={"project_root": str(tmp_path)}
        )
        
        assert orchestrator._is_admin_environment() is False
    
    def test_validate_requires_admin_environment(self, tmp_path):
        """Test validation requires admin environment."""
        # User repo (no admin)
        (tmp_path / "cortex-brain").mkdir(parents=True)
        
        orchestrator = SystemAlignmentOrchestrator(
            context={"project_root": str(tmp_path)}
        )
        
        assert orchestrator.validate({}) is False
    
    def test_execute_in_admin_environment(self, project_root):
        """Test execution in admin environment."""
        orchestrator = SystemAlignmentOrchestrator(
            context={"project_root": str(project_root)}
        )
        
        result = orchestrator.execute({})
        
        assert result.status in [OperationStatus.SUCCESS, OperationStatus.WARNING]
        assert "alignment" in result.message.lower()
    
    def test_rollback_always_succeeds(self, project_root):
        """Test rollback for read-only operation."""
        orchestrator = SystemAlignmentOrchestrator(
            context={"project_root": str(project_root)}
        )
        
        assert orchestrator.rollback({}) is True


class TestConventionBasedDiscovery:
    """Test convention-based discovery without hardcoded lists."""
    
    @pytest.fixture
    def mock_orchestrator_file(self, tmp_path):
        """Create mock orchestrator file."""
        orchestrator_path = tmp_path / "src" / "operations" / "modules" / "test_orchestrator.py"
        orchestrator_path.parent.mkdir(parents=True, exist_ok=True)
        
        orchestrator_path.write_text('''"""Test orchestrator module."""
from src.operations.base_operation_module import BaseOperationModule

class TestOrchestrator(BaseOperationModule):
    """Test orchestrator for validation."""
    
    def execute(self, context):
        """Execute test operation."""
        pass
    
    def validate(self, context):
        """Validate test operation."""
        return True
''')
        
        return tmp_path
    
    def test_orchestrator_discovery(self, mock_orchestrator_file):
        """Test automatic orchestrator discovery."""
        from src.discovery.orchestrator_scanner import OrchestratorScanner
        
        scanner = OrchestratorScanner(mock_orchestrator_file)
        orchestrators = scanner.discover()
        
        assert "TestOrchestrator" in orchestrators
        assert orchestrators["TestOrchestrator"]["class_name"] == "TestOrchestrator"
        assert orchestrators["TestOrchestrator"]["has_docstring"] is True
        assert "execute" in orchestrators["TestOrchestrator"]["methods"]
    
    def test_agent_discovery(self, tmp_path):
        """Test automatic agent discovery."""
        from src.discovery.agent_scanner import AgentScanner
        
        # Create mock agent
        agent_path = tmp_path / "src" / "agents" / "test_agent.py"
        agent_path.parent.mkdir(parents=True, exist_ok=True)
        
        agent_path.write_text('''"""Test agent module."""

class TestAgent:
    """Test agent for validation."""
    
    def process(self, data):
        """Process test data."""
        pass
''')
        
        scanner = AgentScanner(tmp_path)
        agents = scanner.discover()
        
        assert "TestAgent" in agents
        assert agents["TestAgent"]["has_process_method"] is True


class TestSystemAlignmentDashboard:
    """Test D3.js dashboard generation for system alignment."""
    
    def test_dashboard_generation(self, tmp_path, monkeypatch):
        """Test dashboard generation with alignment report."""
        # Create mock brain path
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        
        # Create mock admin directory
        admin_path = brain_path / "admin"
        admin_path.mkdir()
        
        # Set up orchestrator
        orchestrator = SystemAlignmentOrchestrator()
        monkeypatch.setattr(orchestrator, 'cortex_brain', brain_path)
        
        # Create test alignment report
        report = AlignmentReport(
            timestamp=datetime.now(),
            overall_health=85,
            critical_issues=1,
            warnings=2,
            catalog_features_total=10,
            catalog_features_new=2,
            catalog_days_since_review=7
        )
        
        # Add some feature scores
        report.feature_scores = {
            "FeatureA": IntegrationScore("FeatureA", "orchestrator", True, True, True, True, True, True, True),
            "FeatureB": IntegrationScore("FeatureB", "agent", True, True, True, False, False, True, False),
            "FeatureC": IntegrationScore("FeatureC", "orchestrator", True, True, False, False, False, False, False)
        }
        
        # Generate dashboard
        orchestrator._generate_interactive_dashboard(report)
        
        # Verify dashboard file was created
        dashboard_path = brain_path / "admin" / "reports" / "system-alignment-dashboard.html"
        assert dashboard_path.exists()
        
        # Verify dashboard content
        content = dashboard_path.read_text(encoding='utf-8')
        assert "System Alignment Dashboard" in content
        assert "Overall Health" in content
        assert "Feature Integration Health Network" in content
        assert "d3.forceSimulation" in content
    
    def test_dashboard_visualizations_structure(self, tmp_path, monkeypatch):
        """Test dashboard visualization data structure."""
        orchestrator = SystemAlignmentOrchestrator()
        
        report = AlignmentReport(
            timestamp=datetime.now(),
            overall_health=75,
            critical_issues=2,
            warnings=3
        )
        
        # Add feature scores
        report.feature_scores = {
            "HighScore": IntegrationScore("HighScore", "orchestrator", True, True, True, True, True, True, True),
            "MedScore": IntegrationScore("MedScore", "agent", True, True, True, True, False, True, False),
            "LowScore": IntegrationScore("LowScore", "orchestrator", True, True, False, False, False, False, False)
        }
        
        # Build visualizations
        viz = orchestrator._build_alignment_visualizations(report)
        
        # Verify force graph structure
        assert "forceGraph" in viz
        assert "nodes" in viz["forceGraph"]
        assert "links" in viz["forceGraph"]
        assert len(viz["forceGraph"]["nodes"]) == 4  # health + 3 features
        assert len(viz["forceGraph"]["links"]) == 3  # 3 feature links
        
        # Verify time series structure
        assert "timeSeries" in viz
        assert "data" in viz["timeSeries"]
        assert len(viz["timeSeries"]["data"]) == 10  # 10 historical points


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

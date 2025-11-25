"""
Test Gap Remediation Component Validation

Tests SystemAlignmentOrchestrator's validation of Phase 1-4 gap remediation components.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from src.operations.modules.admin.system_alignment_orchestrator import (
    SystemAlignmentOrchestrator,
    AlignmentReport
)


@pytest.fixture
def orchestrator(tmp_path):
    """Create SystemAlignmentOrchestrator with temp project root."""
    return SystemAlignmentOrchestrator(context={"project_root": tmp_path})


@pytest.fixture
def mock_report():
    """Create mock AlignmentReport."""
    report = Mock(spec=AlignmentReport)
    report.critical_issues = 0
    report.warnings = 0
    report.suggestions = []
    report.feature_scores = {}
    return report


class TestGapRemediationValidation:
    """Test gap remediation component validation."""
    
    def test_validates_feedback_workflow_exists(self, orchestrator, mock_report, tmp_path):
        """Test validation checks for feedback-aggregation.yml workflow."""
        # Setup: Create workflow file
        workflows_path = tmp_path / ".github" / "workflows"
        workflows_path.mkdir(parents=True, exist_ok=True)
        
        feedback_workflow = workflows_path / "feedback-aggregation.yml"
        feedback_workflow.write_text("""
on:
  schedule:
    - cron: '0 0 * * 0'
jobs:
  aggregate:
    runs-on: ubuntu-latest
    steps:
      - name: Run aggregator
        run: python src/feedback/feedback_aggregator.py
""")
        
        # Execute
        orchestrator._validate_gap_remediation_components(mock_report)
        
        # Verify: No critical issues for missing workflow
        workflow_issues = [s for s in mock_report.suggestions if s["type"] == "missing_workflow"]
        assert len(workflow_issues) == 0, "Should not report missing workflow when it exists"
    
    def test_detects_missing_feedback_workflow(self, orchestrator, mock_report, tmp_path):
        """Test validation detects missing feedback-aggregation.yml workflow."""
        # Setup: No workflow file
        # (tmp_path is empty)
        
        # Execute
        orchestrator._validate_gap_remediation_components(mock_report)
        
        # Verify: Critical issue reported
        assert mock_report.critical_issues >= 1, "Should report critical issue for missing workflow"
        
        workflow_issues = [s for s in mock_report.suggestions if s["type"] == "missing_workflow"]
        assert len(workflow_issues) > 0, "Should suggest creating feedback-aggregation.yml"
        assert "feedback-aggregation.yml" in workflow_issues[0]["message"]
    
    def test_validates_template_format_compliance(self, orchestrator, mock_report, tmp_path):
        """Test validation checks template format (H1 headers, Challenge field)."""
        # Setup: Create templates file with correct format
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        
        templates_file = brain_path / "response-templates.yaml"
        templates_content = """
templates:
  help_table:
    content: |
      # CORTEX [Operation Type]
      Challenge: [Specific challenge or "None"]
  help_detailed:
    content: |
      # CORTEX [Operation Type]
      Challenge: [Specific challenge or "None"]
"""
        with open(templates_file, "w", encoding="utf-8") as f:
            f.write(templates_content)
        
        # Execute
        orchestrator._validate_gap_remediation_components(mock_report)
        
        # Verify: No format issues
        format_issues = [s for s in mock_report.suggestions if s["type"] == "template_format"]
        assert len(format_issues) == 0, "Should not report format issues for correct templates"
    
    def test_detects_old_template_format(self, orchestrator, mock_report, tmp_path):
        """Test validation detects old template format (Challenge field)."""
        # Setup: Create templates with old format
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        
        templates_file = brain_path / "response-templates.yaml"
        templates_content = """
templates:
  help_table:
    content: |
      # CORTEX [Operation Type]
      Challenge: [✓ Accept OR ⚡ Challenge]
"""
        with open(templates_file, "w", encoding="utf-8") as f:
            f.write(templates_content)
        
        # Execute
        orchestrator._validate_gap_remediation_components(mock_report)
        
        # Verify: Format issue reported
        format_issues = [s for s in mock_report.suggestions if s["type"] == "template_format"]
        assert len(format_issues) > 0, "Should detect old Challenge format"
        assert "Old Challenge format" in format_issues[0]["message"]
    
    def test_validates_no_root_files_blocked_severity(self, orchestrator, mock_report, tmp_path):
        """Test validation checks NO_ROOT_FILES protection is 'blocked' severity."""
        # Setup: Create brain protection rules with correct severity
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        
        rules_file = brain_path / "brain-protection-rules.yaml"
        rules_file.write_text("""
tier0_instincts:
  - DOCUMENT_ORGANIZATION_ENFORCEMENT
layers:
  layer_8_document_organization:
    rules:
      - id: NO_ROOT_FILES
        severity: blocked
        enforcement: automatic
""")
        
        # Execute
        orchestrator._validate_gap_remediation_components(mock_report)
        
        # Verify: No warnings about severity
        protection_issues = [
            s for s in mock_report.suggestions
            if s["type"] == "brain_protection" and "NO_ROOT_FILES" in s["message"]
        ]
        assert len(protection_issues) == 0, "Should not warn when severity is 'blocked'"
    
    def test_detects_wrong_no_root_files_severity(self, orchestrator, mock_report, tmp_path):
        """Test validation detects NO_ROOT_FILES with wrong severity."""
        # Setup: Create brain protection rules with warning severity
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        
        rules_file = brain_path / "brain-protection-rules.yaml"
        rules_file.write_text("""
tier0_instincts:
  - DOCUMENT_ORGANIZATION_ENFORCEMENT
layers:
  layer_8_document_organization:
    rules:
      - id: NO_ROOT_FILES
        severity: warning
        enforcement: automatic
""")
        
        # Execute
        orchestrator._validate_gap_remediation_components(mock_report)
        
        # Verify: Warning about severity
        assert mock_report.warnings >= 1, "Should warn about wrong severity"
        
        protection_issues = [
            s for s in mock_report.suggestions
            if s["type"] == "brain_protection" and "NO_ROOT_FILES" in s["message"]
        ]
        assert len(protection_issues) > 0, "Should suggest changing severity to 'blocked'"
        assert "should be 'blocked'" in protection_issues[0]["message"]
    
    def test_validates_tier0_instinct_presence(self, orchestrator, mock_report, tmp_path):
        """Test validation checks DOCUMENT_ORGANIZATION_ENFORCEMENT in Tier 0."""
        # Setup: Create brain rules without the instinct
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        
        rules_file = brain_path / "brain-protection-rules.yaml"
        rules_file.write_text("""
tier0_instincts:
  - TDD_ENFORCEMENT
  - BRAIN_PROTECTION_TESTS_MANDATORY
layers:
  layer_8_document_organization:
    rules:
      - id: NO_ROOT_FILES
        severity: blocked
""")
        
        # Execute
        orchestrator._validate_gap_remediation_components(mock_report)
        
        # Verify: Warning about missing instinct
        assert mock_report.warnings >= 1, "Should warn about missing Tier 0 instinct"
        
        instinct_issues = [
            s for s in mock_report.suggestions
            if "DOCUMENT_ORGANIZATION_ENFORCEMENT" in s["message"]
        ]
        assert len(instinct_issues) > 0, "Should suggest adding Tier 0 instinct"
    
    def test_validates_configuration_schemas(self, orchestrator, mock_report, tmp_path):
        """Test validation checks for plan-schema.yaml and lint-rules.yaml."""
        # Setup: Create config files
        config_path = tmp_path / "cortex-brain" / "config"
        config_path.mkdir(parents=True, exist_ok=True)
        
        (config_path / "plan-schema.yaml").write_text("schema_version: '1.0'")
        (config_path / "lint-rules.yaml").write_text("version: '1.0'")
        
        # Execute
        orchestrator._validate_gap_remediation_components(mock_report)
        
        # Verify: No warnings about missing schemas
        schema_issues = [s for s in mock_report.suggestions if s["type"] == "missing_schema"]
        config_issues = [s for s in mock_report.suggestions if s["type"] == "missing_config"]
        
        assert len(schema_issues) == 0, "Should not warn about missing plan-schema.yaml"
        assert len(config_issues) == 0, "Should not warn about missing lint-rules.yaml"
    
    def test_detects_missing_orchestrators(self, orchestrator, mock_report, tmp_path):
        """Test validation detects missing gap remediation orchestrators."""
        # Setup: Empty feature_scores (no orchestrators discovered)
        mock_report.feature_scores = {}
        
        # Execute
        orchestrator._validate_gap_remediation_components(mock_report)
        
        # Verify: Critical issues for missing orchestrators
        assert mock_report.critical_issues >= 6, "Should report 6 missing orchestrators"
        
        orchestrator_issues = [
            s for s in mock_report.suggestions
            if s["type"] == "missing_orchestrator"
        ]
        
        expected_names = [
            "GitCheckpointOrchestrator",
            "MetricsTracker",
            "LintValidationOrchestrator",
            "SessionCompletionOrchestrator",
            "PlanningOrchestrator",
            "UpgradeOrchestrator"
        ]
        
        for name in expected_names:
            assert any(name in issue["message"] for issue in orchestrator_issues), \
                f"Should detect missing {name}"
    
    def test_validates_feedback_aggregator_module(self, orchestrator, mock_report, tmp_path):
        """Test validation checks for feedback_aggregator.py module."""
        # Setup: Create feedback aggregator module
        feedback_path = tmp_path / "src" / "feedback"
        feedback_path.mkdir(parents=True, exist_ok=True)
        
        (feedback_path / "feedback_aggregator.py").write_text("# Feedback Aggregator")
        
        # Execute
        orchestrator._validate_gap_remediation_components(mock_report)
        
        # Verify: No critical issue for missing module
        aggregator_issues = [
            s for s in mock_report.suggestions
            if s["type"] == "missing_module" and "feedback_aggregator" in s["message"]
        ]
        assert len(aggregator_issues) == 0, "Should not report missing feedback_aggregator.py"


class TestOrchestratorDiscoveryEnhancement:
    """Test enhanced orchestrator discovery includes src/orchestrators/."""
    
    def test_scanner_includes_orchestrators_directory(self, tmp_path):
        """Test OrchestratorScanner includes src/orchestrators/ in scan paths."""
        from src.discovery.orchestrator_scanner import OrchestratorScanner
        
        scanner = OrchestratorScanner(tmp_path)
        
        # Verify scan paths include src/orchestrators/
        orchestrators_path = tmp_path / "src" / "orchestrators"
        assert orchestrators_path in scanner.scan_paths, \
            "Scanner should include src/orchestrators/ in scan paths"
    
    def test_discovers_orchestrators_in_new_directory(self, tmp_path):
        """Test scanner discovers orchestrators in src/orchestrators/."""
        from src.discovery.orchestrator_scanner import OrchestratorScanner
        
        # Setup: Create orchestrator in new directory
        orchestrators_path = tmp_path / "src" / "orchestrators"
        orchestrators_path.mkdir(parents=True, exist_ok=True)
        
        orchestrator_file = orchestrators_path / "git_checkpoint_orchestrator.py"
        orchestrator_file.write_text("""
from src.operations.base_operation_module import BaseOperationModule

class GitCheckpointOrchestrator(BaseOperationModule):
    '''Creates git checkpoint before development work.'''
    
    def execute(self, context):
        return {"success": True}
""")
        
        # Execute
        scanner = OrchestratorScanner(tmp_path)
        discovered = scanner.discover()
        
        # Verify
        assert "GitCheckpointOrchestrator" in discovered, \
            "Should discover orchestrator in src/orchestrators/"
        
        metadata = discovered["GitCheckpointOrchestrator"]
        assert metadata["class_name"] == "GitCheckpointOrchestrator"
        assert "git_checkpoint_orchestrator.py" in str(metadata["path"])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

"""
Tests for AlignmentReporter

Tests report generation, formatting, and file saving.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any

from src.reporting.alignment_reporter import AlignmentReporter


# Mock dataclasses matching SystemAlignmentOrchestrator structures
@dataclass
class MockIntegrationScore:
    """Mock integration score for testing"""
    feature_name: str
    feature_type: str
    discovered: bool = True
    imported: bool = True
    instantiated: bool = True
    documented: bool = True
    tested: bool = True
    wired: bool = True
    optimized: bool = False
    
    @property
    def score(self) -> int:
        """Calculate score"""
        total = 0
        if self.discovered:
            total += 20
        if self.imported:
            total += 20
        if self.instantiated:
            total += 20
        if self.documented:
            total += 10
        if self.tested:
            total += 10
        if self.wired:
            total += 10
        if self.optimized:
            total += 10
        return total
    
    @property
    def status(self) -> str:
        """Get status"""
        score = self.score
        if score >= 90:
            return "✅ Healthy"
        elif score >= 70:
            return "⚠️ Warning"
        else:
            return "❌ Critical"
    
    @property
    def issues(self) -> List[str]:
        """List issues"""
        issues = []
        if not self.documented:
            issues.append("Missing documentation")
        if not self.tested:
            issues.append("No test coverage")
        if not self.wired:
            issues.append("Not wired to entry point")
        if not self.optimized:
            issues.append("Performance not validated")
        return issues


@dataclass
class MockRemediationSuggestion:
    """Mock remediation suggestion"""
    feature_name: str
    suggestion_type: str
    content: str
    file_path: str = None


@dataclass
class MockAlignmentReport:
    """Mock alignment report for testing"""
    timestamp: datetime
    overall_health: int
    critical_issues: int = 0
    warnings: int = 0
    feature_scores: Dict[str, MockIntegrationScore] = field(default_factory=dict)
    remediation_suggestions: List[MockRemediationSuggestion] = field(default_factory=list)
    deployment_gate_results: Dict[str, Any] = field(default_factory=dict)
    orphaned_triggers: List[str] = field(default_factory=list)
    ghost_features: List[str] = field(default_factory=list)
    
    @property
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        return self.critical_issues == 0 and self.warnings == 0
    
    @property
    def issues_found(self) -> int:
        """Total issues"""
        return self.critical_issues + self.warnings


# ============================================================================
# AlignmentReporter Tests
# ============================================================================

class TestAlignmentReporter:
    """Test suite for AlignmentReporter"""
    
    def test_initialization(self, tmp_path):
        """Test AlignmentReporter can be instantiated"""
        reporter = AlignmentReporter(tmp_path)
        assert reporter is not None
        assert reporter.project_root == tmp_path
    
    def test_generate_report_healthy_system(self, tmp_path):
        """Test report generation for healthy system"""
        reporter = AlignmentReporter(tmp_path)
        
        # Create healthy report
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=95,
            critical_issues=0,
            warnings=0,
            feature_scores={
                "TestOrchestrator": MockIntegrationScore(
                    feature_name="TestOrchestrator",
                    feature_type="orchestrator",
                    optimized=True
                )
            }
        )
        
        result = reporter.generate_report(report)
        
        # Verify structure
        assert "# CORTEX System Alignment Report" in result
        assert "Overall Health:** 95%" in result  # Fixed: removed space after colon
        assert "✅" in result  # Health emoji
        assert "Executive Summary" in result
        assert "Feature Integration Dashboard" in result
        assert "TestOrchestrator" in result
        assert "100%" in result  # Feature score
    
    def test_generate_report_with_issues(self, tmp_path):
        """Test report generation with critical issues"""
        reporter = AlignmentReporter(tmp_path)
        
        # Create report with issues
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=50,
            critical_issues=2,
            warnings=1,
            feature_scores={
                "CriticalOrchestrator": MockIntegrationScore(
                    feature_name="CriticalOrchestrator",
                    feature_type="orchestrator",
                    documented=False,
                    tested=False,
                    wired=False,
                    optimized=False
                ),
                "WarningAgent": MockIntegrationScore(
                    feature_name="WarningAgent",
                    feature_type="agent",
                    optimized=False
                )
            }
        )
        
        result = reporter.generate_report(report)
        
        # Verify issue sections
        assert "Critical Issues" in result
        assert "CriticalOrchestrator" in result
        assert "60%" in result  # Critical feature score
        assert "Warnings" in result
        assert "WarningAgent" in result
        assert "90%" in result  # Warning feature score
    
    def test_generate_feature_dashboard(self, tmp_path):
        """Test feature dashboard table generation"""
        reporter = AlignmentReporter(tmp_path)
        
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=75,
            feature_scores={
                "FeatureA": MockIntegrationScore(
                    feature_name="FeatureA",
                    feature_type="orchestrator",
                    optimized=True
                ),
                "FeatureB": MockIntegrationScore(
                    feature_name="FeatureB",
                    feature_type="agent",
                    tested=False,
                    wired=False,
                    optimized=False
                )
            }
        )
        
        result = reporter.generate_report(report)
        
        # Verify table structure
        assert "| Feature | Type | Score | Status | Issues |" in result
        assert "| FeatureA | Orchestrator | 100% |" in result
        assert "| FeatureB | Agent | 70% |" in result
    
    def test_generate_remediation_suggestions(self, tmp_path):
        """Test remediation suggestions section"""
        reporter = AlignmentReporter(tmp_path)
        
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=60,
            feature_scores={},
            remediation_suggestions=[
                MockRemediationSuggestion(
                    feature_name="UnwiredOrchestrator",
                    suggestion_type="wiring",
                    content="payment_processing:\n  name: \"PaymentOrchestrator\"\n  triggers:\n    - \"payment\""
                ),
                MockRemediationSuggestion(
                    feature_name="UntestedAgent",
                    suggestion_type="test",
                    content="import pytest\n\nclass TestUntestedAgent:\n    pass",
                    file_path="tests/test_untested_agent.py"
                ),
                MockRemediationSuggestion(
                    feature_name="UndocumentedOrchestrator",
                    suggestion_type="documentation",
                    content="# Payment Guide\n\n**Purpose:** Handle payments",
                    file_path=".github/prompts/modules/payment-guide.md"
                )
            ]
        )
        
        result = reporter.generate_report(report)
        
        # Verify remediation section
        assert "Auto-Remediation Suggestions" in result
        assert "3 suggestion(s) generated" in result
        assert "UnwiredOrchestrator" in result
        assert "**Issue:** Not wired to entry point" in result
        assert "UntestedAgent" in result
        assert "**Issue:** No test coverage" in result
        assert "UndocumentedOrchestrator" in result
        assert "**Issue:** Missing documentation" in result
    
    def test_generate_deployment_gates(self, tmp_path):
        """Test deployment gates section"""
        reporter = AlignmentReporter(tmp_path)
        
        # Report with failed gates
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=70,
            deployment_gate_results={
                "passed": False,
                "errors": ["Integration scores below 80%", "Mocks detected in production code"],
                "warnings": ["Documentation not synchronized"]
            }
        )
        
        result = reporter.generate_report(report)
        
        # Verify deployment section
        assert "Deployment Readiness" in result
        assert "❌ Not Ready" in result
        assert "Integration scores below 80%" in result
        assert "Mocks detected in production code" in result
        assert "Documentation not synchronized" in result
    
    def test_generate_wiring_issues(self, tmp_path):
        """Test orphaned triggers and ghost features section"""
        reporter = AlignmentReporter(tmp_path)
        
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=80,
            orphaned_triggers=["process payment", "handle refund"],
            ghost_features=["InvoiceGenerator", "ReportBuilder"]
        )
        
        result = reporter.generate_report(report)
        
        # Verify wiring issues
        assert "Entry Point Wiring Issues" in result
        assert "Orphaned Triggers (2)" in result
        assert "process payment" in result
        assert "handle refund" in result
        assert "Ghost Features (2)" in result
        assert "InvoiceGenerator" in result
        assert "ReportBuilder" in result
    
    def test_save_report(self, tmp_path):
        """Test saving report to file"""
        reporter = AlignmentReporter(tmp_path)
        
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=85,
            feature_scores={
                "TestOrchestrator": MockIntegrationScore(
                    feature_name="TestOrchestrator",
                    feature_type="orchestrator"
                )
            }
        )
        
        # Save with custom path
        output_path = tmp_path / "test-report.md"
        saved_path = reporter.save_report(report, output_path)
        
        # Verify file created
        assert saved_path.exists()
        assert saved_path == output_path
        
        # Verify content
        content = saved_path.read_text(encoding='utf-8')
        assert "# CORTEX System Alignment Report" in content
        assert "TestOrchestrator" in content
    
    def test_save_report_default_path(self, tmp_path):
        """Test saving report with default path"""
        reporter = AlignmentReporter(tmp_path)
        
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=90
        )
        
        # Save without custom path
        saved_path = reporter.save_report(report)
        
        # Verify file created in default location
        assert saved_path.exists()
        assert "ALIGNMENT-REPORT-" in str(saved_path)
        assert saved_path.suffix == ".md"
    
    def test_health_emoji_selection(self, tmp_path):
        """Test health emoji selection based on score"""
        reporter = AlignmentReporter(tmp_path)
        
        assert reporter._get_health_emoji(95) == "✅"
        assert reporter._get_health_emoji(85) == "⚠️"
        assert reporter._get_health_emoji(65) == "❌"
    
    def test_executive_summary_calculations(self, tmp_path):
        """Test executive summary feature distribution"""
        reporter = AlignmentReporter(tmp_path)
        
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=75,
            feature_scores={
                "HealthyFeature": MockIntegrationScore(
                    feature_name="HealthyFeature",
                    feature_type="orchestrator",
                    optimized=True
                ),
                "WarningFeature": MockIntegrationScore(
                    feature_name="WarningFeature",
                    feature_type="agent",
                    optimized=False
                ),
                "CriticalFeature": MockIntegrationScore(
                    feature_name="CriticalFeature",
                    feature_type="orchestrator",
                    documented=False,
                    tested=False,
                    wired=False,
                    optimized=False
                )
            }
        )
        
        result = reporter.generate_report(report)
        
        # Verify distribution (counts match but formatting slightly different)
        assert "Healthy (90%+): 2 features" in result  # Fixed: WarningFeature is actually 90% = healthy
        assert "Critical (<70%): 1 features" in result


# ============================================================================
# Integration Tests
# ============================================================================

class TestReporterIntegration:
    """Integration tests for AlignmentReporter"""
    
    def test_full_report_workflow(self, tmp_path):
        """Test complete report generation and save workflow"""
        reporter = AlignmentReporter(tmp_path)
        
        # Create comprehensive report
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=72,
            critical_issues=1,
            warnings=2,
            feature_scores={
                "GoodOrchestrator": MockIntegrationScore(
                    feature_name="GoodOrchestrator",
                    feature_type="orchestrator",
                    optimized=True
                ),
                "MediumAgent": MockIntegrationScore(
                    feature_name="MediumAgent",
                    feature_type="agent",
                    optimized=False
                ),
                "BadOrchestrator": MockIntegrationScore(
                    feature_name="BadOrchestrator",
                    feature_type="orchestrator",
                    documented=False,
                    tested=False,
                    wired=False,
                    optimized=False
                )
            },
            remediation_suggestions=[
                MockRemediationSuggestion(
                    feature_name="BadOrchestrator",
                    suggestion_type="wiring",
                    content="wiring template"
                ),
                MockRemediationSuggestion(
                    feature_name="BadOrchestrator",
                    suggestion_type="test",
                    content="test template",
                    file_path="tests/test_bad.py"
                )
            ],
            deployment_gate_results={
                "passed": False,
                "errors": ["Test coverage below 80%"],
                "warnings": []
            },
            orphaned_triggers=["trigger1"],
            ghost_features=["GhostFeature"]
        )
        
        # Generate and save
        output_path = tmp_path / "comprehensive-report.md"
        saved_path = reporter.save_report(report, output_path)
        
        # Verify complete report
        content = saved_path.read_text(encoding='utf-8')
        
        assert "# CORTEX System Alignment Report" in content
        assert "Executive Summary" in content
        assert "Feature Integration Dashboard" in content
        assert "Critical Issues" in content
        assert "Warnings" in content
        assert "Auto-Remediation Suggestions" in content
        assert "Deployment Readiness" in content
        assert "Entry Point Wiring Issues" in content
        assert "GoodOrchestrator" in content
        assert "MediumAgent" in content
        assert "BadOrchestrator" in content

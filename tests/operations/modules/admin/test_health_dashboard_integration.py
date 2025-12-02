"""
Test Suite: Phase 9.7 Application Health Dashboard Integration

Validates Gate 19 integration with system alignment orchestrator
and health dashboard generation.

Test Categories:
1. Health Dashboard Integration (3 tests)
2. Gate 19 Data Extraction (2 tests)
3. Dashboard HTML Generation (2 tests)

Total: 7 tests

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator


# ============================================================================
# Test Category 1: Health Dashboard Integration (3 tests)
# ============================================================================

def test_integrate_health_dashboard_extracts_gate_19():
    """
    Test 1.1: Verify _integrate_health_dashboard() extracts Gate 19 results.
    
    Phase 9.7: Health dashboard integration must extract Token Efficiency gate.
    """
    orchestrator = SystemAlignmentOrchestrator()
    
    # Mock gate results
    gate_results = {
        "passed": False,
        "gates": [
            {
                "name": "Integration Scores",
                "passed": True
            },
            {
                "name": "Token Efficiency",
                "passed": False,
                "severity": "CRITICAL",
                "message": "Token budget exceeded",
                "details": {
                    "total_current": 101102,
                    "total_budget": 17000,
                    "total_overage": 84102,
                    "compliance_pct": 16.8,
                    "files": [
                        {
                            "file": "CORTEX.prompt.md",
                            "current": 11836,
                            "budget": 5000,
                            "overage": 6836,
                            "overage_pct": 136.7,
                            "is_compliant": False
                        }
                    ]
                }
            }
        ]
    }
    
    # Mock AlignmentReport
    report = Mock()
    report.health_metrics = {}
    
    # Execute integration
    orchestrator._integrate_health_dashboard(gate_results, report)
    
    # Validate health metrics added to report
    assert "gate_19_token_efficiency" in report.health_metrics
    health_data = report.health_metrics["gate_19_token_efficiency"]
    
    assert health_data["gate_19_status"] == "failed"
    assert health_data["token_efficiency"]["total_current"] == 101102
    assert health_data["token_efficiency"]["total_budget"] == 17000
    assert health_data["severity"] == "CRITICAL"
    assert len(health_data["token_efficiency"]["files"]) == 1


def test_integrate_health_dashboard_handles_missing_gate_19():
    """
    Test 1.2: Verify graceful handling when Gate 19 not found in results.
    
    Should log warning but not crash alignment.
    """
    orchestrator = SystemAlignmentOrchestrator()
    
    # Mock gate results WITHOUT Gate 19
    gate_results = {
        "passed": True,
        "gates": [
            {"name": "Integration Scores", "passed": True},
            {"name": "All Tests", "passed": True}
        ]
    }
    
    report = Mock()
    report.health_metrics = {}
    report.warnings = 0
    report.suggestions = []
    
    # Should not raise exception
    orchestrator._integrate_health_dashboard(gate_results, report)
    
    # Validate no health metrics added
    assert "gate_19_token_efficiency" not in report.health_metrics


def test_integrate_health_dashboard_called_during_validation():
    """
    Test 1.3: Verify _integrate_health_dashboard() called in _validate_deployment_readiness().
    
    Integration must happen automatically during deployment validation.
    """
    orchestrator = SystemAlignmentOrchestrator()
    
    # Mock dependencies (patch at deployment module level)
    with patch("src.deployment.deployment_gates.DeploymentGates") as mock_gates_class:
        mock_gates = Mock()
        mock_gates.validate_all_gates.return_value = {
            "passed": True,
            "gates": [
                {
                    "name": "Token Efficiency",
                    "passed": True,
                    "severity": "CRITICAL",
                    "message": "All files within budget",
                    "details": {
                        "total_current": 15000,
                        "total_budget": 17000,
                        "compliance_pct": 88.2,
                        "files": []
                    }
                }
            ],
            "errors": [],
            "warnings": []
        }
        mock_gates_class.return_value = mock_gates
        
        with patch("src.deployment.package_purity_checker.PackagePurityChecker"):
            with patch.object(orchestrator, "_integrate_health_dashboard") as mock_integrate:
                with patch.object(orchestrator, "_generate_health_dashboard"):
                    report = Mock()
                    report.deployment_gate_results = None
                    report.critical_issues = 0
                    report.warnings = 0
                    report.suggestions = []
                    
                    orchestrator._validate_deployment_readiness(report)
                    
                    # Verify integration was called
                    mock_integrate.assert_called_once()


# ============================================================================
# Test Category 2: Gate 19 Data Extraction (2 tests)
# ============================================================================

def test_health_metrics_structure_matches_schema():
    """
    Test 2.1: Verify health_metrics structure matches expected schema.
    
    Schema: {
        "gate_19_status": "passed" | "failed",
        "token_efficiency": {
            "total_current": int,
            "total_budget": int,
            "total_overage": int,
            "compliance_pct": float,
            "files": List[Dict]
        },
        "severity": str,
        "message": str,
        "timestamp": str (ISO format)
    }
    """
    orchestrator = SystemAlignmentOrchestrator()
    
    gate_results = {
        "passed": True,
        "gates": [
            {
                "name": "Token Efficiency",
                "passed": True,
                "severity": "CRITICAL",
                "message": "All governance files within budgets",
                "details": {
                    "total_current": 16000,
                    "total_budget": 17000,
                    "total_overage": 0,
                    "compliance_pct": 94.1,
                    "files": []
                }
            }
        ]
    }
    
    report = Mock()
    report.health_metrics = {}
    
    orchestrator._integrate_health_dashboard(gate_results, report)
    
    health_data = report.health_metrics["gate_19_token_efficiency"]
    
    # Validate schema
    assert "gate_19_status" in health_data
    assert health_data["gate_19_status"] in ["passed", "failed"]
    
    assert "token_efficiency" in health_data
    token_data = health_data["token_efficiency"]
    assert "total_current" in token_data
    assert "total_budget" in token_data
    assert "total_overage" in token_data
    assert "compliance_pct" in token_data
    assert "files" in token_data
    
    assert "severity" in health_data
    assert "message" in health_data
    assert "timestamp" in health_data
    
    # Validate timestamp is ISO format
    datetime.fromisoformat(health_data["timestamp"])


def test_gate_19_status_reflects_pass_fail_correctly():
    """
    Test 2.2: Verify gate_19_status correctly reflects gate pass/fail state.
    """
    orchestrator = SystemAlignmentOrchestrator()
    
    # Test PASSED state
    gate_results_pass = {
        "gates": [
            {
                "name": "Token Efficiency",
                "passed": True,
                "severity": "CRITICAL",
                "message": "Success",
                "details": {"total_current": 15000, "total_budget": 17000, "compliance_pct": 88.2}
            }
        ]
    }
    
    report_pass = Mock()
    report_pass.health_metrics = {}
    orchestrator._integrate_health_dashboard(gate_results_pass, report_pass)
    
    assert report_pass.health_metrics["gate_19_token_efficiency"]["gate_19_status"] == "passed"
    
    # Test FAILED state
    gate_results_fail = {
        "gates": [
            {
                "name": "Token Efficiency",
                "passed": False,
                "severity": "ERROR",
                "message": "Budget exceeded",
                "details": {"total_current": 25000, "total_budget": 17000, "compliance_pct": 68.0}
            }
        ]
    }
    
    report_fail = Mock()
    report_fail.health_metrics = {}
    orchestrator._integrate_health_dashboard(gate_results_fail, report_fail)
    
    assert report_fail.health_metrics["gate_19_token_efficiency"]["gate_19_status"] == "failed"


# ============================================================================
# Test Category 3: Dashboard HTML Generation (2 tests)
# ============================================================================

def test_generate_health_dashboard_creates_html_file():
    """
    Test 3.1: Verify _generate_health_dashboard() creates HTML file in cortex-brain/dashboards/.
    """
    orchestrator = SystemAlignmentOrchestrator()
    
    health_metrics = {
        "gate_19_status": "passed",
        "token_efficiency": {
            "total_current": 16000,
            "total_budget": 17000,
            "total_overage": 0,
            "compliance_pct": 94.1,
            "files": [
                {
                    "file": "CORTEX.prompt.md",
                    "current": 4500,
                    "budget": 5000,
                    "overage": 0,
                    "overage_pct": 0,
                    "is_compliant": True
                }
            ]
        },
        "severity": "CRITICAL",
        "message": "All files within budget",
        "timestamp": datetime.now().isoformat()
    }
    
    report = Mock()
    
    # Execute dashboard generation
    orchestrator._generate_health_dashboard(health_metrics, report)
    
    # Validate file exists
    dashboard_path = orchestrator.cortex_brain / "dashboards" / "application-health.html"
    assert dashboard_path.exists(), f"Dashboard not created at {dashboard_path}"
    
    # Validate HTML content
    html_content = dashboard_path.read_text(encoding='utf-8')
    assert "CORTEX Application Health Dashboard" in html_content
    assert "Gate 19: Token Efficiency Status" in html_content
    assert "16,000" in html_content  # Current tokens formatted
    assert "17,000" in html_content  # Budget tokens formatted
    assert "94.1%" in html_content  # Compliance percentage
    
    # Cleanup
    dashboard_path.unlink()


def test_dashboard_html_includes_optimization_recommendations():
    """
    Test 3.2: Verify dashboard HTML includes 4-phase optimization recommendations.
    
    Recommendations:
    - Phase 1: Modularization
    - Phase 2: Template Compression
    - Phase 3: Lazy Loading
    - Phase 4: Reference Compression
    """
    orchestrator = SystemAlignmentOrchestrator()
    
    health_metrics = {
        "gate_19_status": "failed",
        "token_efficiency": {
            "total_current": 101102,
            "total_budget": 17000,
            "total_overage": 84102,
            "compliance_pct": 16.8,
            "files": []
        },
        "severity": "ERROR",
        "message": "Token budget exceeded",
        "timestamp": datetime.now().isoformat()
    }
    
    report = Mock()
    
    orchestrator._generate_health_dashboard(health_metrics, report)
    
    dashboard_path = orchestrator.cortex_brain / "dashboards" / "application-health.html"
    html_content = dashboard_path.read_text(encoding='utf-8')
    
    # Validate optimization recommendations present
    assert "Optimization Recommendations" in html_content
    assert "Phase 1: Modularization" in html_content
    assert "Phase 2: Template Compression" in html_content
    assert "Phase 3: Lazy Loading" in html_content
    assert "Phase 4: Reference Compression" in html_content
    assert "TOKEN-OPTIMIZATION-HOLISTIC-PLAN.md" in html_content
    
    # Cleanup
    dashboard_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

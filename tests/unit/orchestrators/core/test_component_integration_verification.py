"""
Tests for Component Integration Verification (CIV) system.

Authority: ENH-027 (Component Integration Verification)
CORE Rules: CORE-008 (TDD-first), CORE-011 (type hints), CORE-012 (docstrings)

Test Coverage:
- Layer 1: Wiring→Implementation alignment
- Layer 2: MCP Tool Registration chain
- Layer 3: Health Check execution (sampled)
"""

import pytest
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.core.component_integration_verification import (
    ComponentIntegrationVerifier,
    WiringImplementationResult,
    MCPToolRegistrationResult,
    HealthCheckResult,
    CIVReport,
    CIVStatus,
)


class TestComponentIntegrationVerifier:
    """Test suite for Component Integration Verification."""

    @pytest.fixture
    def verifier(self, tmp_path: Path) -> ComponentIntegrationVerifier:
        """Create verifier with test workspace."""
        return ComponentIntegrationVerifier(workspace_root=tmp_path)

    @pytest.fixture
    def sample_wiring_yaml(self, tmp_path: Path) -> Path:
        """Create sample wiring.yaml for tests."""
        wiring_dir = tmp_path / "cortex" / "wiring" / "specifications"
        wiring_dir.mkdir(parents=True, exist_ok=True)
        wiring_file = wiring_dir / "wiring.yaml"
        
        wiring_content = """
orchestrators:
  core:
    - name: "TestOrchestrator"
      module: "cortex.orchestrators.core.test_orchestrator"
      class: "TestOrchestrator"
      health_check: "health_check"
  domain:
    - name: "DomainOrchestrator"
      module: "cortex.orchestrators.domain.domain_orchestrator"
      class: "DomainOrchestrator"
      health_check: "check_health"
"""
        wiring_file.write_text(wiring_content)
        return wiring_file

    def test_verify_wiring_implementation_alignment_success(
        self, verifier: ComponentIntegrationVerifier, sample_wiring_yaml: Path
    ):
        """Test successful wiring→implementation alignment."""
        # Create matching implementation files
        test_orch_file = (
            sample_wiring_yaml.parent.parent.parent / "orchestrators" / "core" / "test_orchestrator.py"
        )
        test_orch_file.parent.mkdir(parents=True, exist_ok=True)
        test_orch_file.write_text("""
class TestOrchestrator:
    def health_check(self):
        return True
""")
        
        result = verifier.verify_wiring_implementation_alignment()
        
        assert result.status == CIVStatus.FAIL  # DomainOrchestrator still missing
        assert len(result.missing_implementations) >= 1  # At least DomainOrchestrator missing
        assert "TestOrchestrator" in result.aligned_orchestrators
        assert any("DomainOrchestrator" in impl for impl in result.missing_implementations)

    def test_verify_wiring_implementation_alignment_missing_module(
        self, verifier: ComponentIntegrationVerifier, sample_wiring_yaml: Path
    ):
        """Test detection of missing implementation modules."""
        result = verifier.verify_wiring_implementation_alignment()
        
        assert result.status == CIVStatus.FAIL
        assert len(result.missing_implementations) == 2
        assert any("TestOrchestrator" in impl for impl in result.missing_implementations)
        assert any("DomainOrchestrator" in impl for impl in result.missing_implementations)

    def test_verify_wiring_implementation_alignment_missing_class(
        self, verifier: ComponentIntegrationVerifier, sample_wiring_yaml: Path
    ):
        """Test detection of missing class in existing module."""
        # Create file with wrong class name
        test_orch_file = (
            sample_wiring_yaml.parent.parent.parent / "orchestrators" / "core" / "test_orchestrator.py"
        )
        test_orch_file.parent.mkdir(parents=True, exist_ok=True)
        test_orch_file.write_text("""
class WrongClassName:
    def health_check(self):
        return True
""")
        
        result = verifier.verify_wiring_implementation_alignment()
        
        assert result.status == CIVStatus.FAIL
        assert any("TestOrchestrator" in impl for impl in result.missing_implementations)

    def test_verify_wiring_implementation_alignment_missing_health_check(
        self, verifier: ComponentIntegrationVerifier, sample_wiring_yaml: Path
    ):
        """Test detection of missing health_check method."""
        # Create class without health_check
        test_orch_file = (
            sample_wiring_yaml.parent.parent.parent / "orchestrators" / "core" / "test_orchestrator.py"
        )
        test_orch_file.parent.mkdir(parents=True, exist_ok=True)
        test_orch_file.write_text("""
class TestOrchestrator:
    def some_other_method(self):
        return True
""")
        
        result = verifier.verify_wiring_implementation_alignment()
        
        # Status should be FAIL because DomainOrchestrator is still missing (takes precedence)
        assert result.status == CIVStatus.FAIL
        assert any("TestOrchestrator" in check for check in result.missing_health_checks)

    def test_verify_mcp_tool_registration_success(
        self, verifier: ComponentIntegrationVerifier, tmp_path: Path
    ):
        """Test successful MCP tool registration chain."""
        # Create MCP tool with @mcp_tool decorator
        mcp_tools_dir = tmp_path / "cortex" / "mcp" / "tools"
        mcp_tools_dir.mkdir(parents=True, exist_ok=True)
        
        tool_file = mcp_tools_dir / "test_tool.py"
        tool_file.write_text("""
from cortex.mcp.decorators import mcp_tool

@mcp_tool(name="test_tool", description="Test tool")
def test_tool_function():
    return "success"
""")
        
        # Create catalog with tool reference (only the tool name on its own line)
        catalog_file = tmp_path / "cortex" / "mcp" / "mcp_tools_catalog.py"
        catalog_file.parent.mkdir(parents=True, exist_ok=True)
        catalog_file.write_text('''
TOOLS = {
    "test_tool": {"module": "cortex.mcp.tools.test_tool", "function": "test_tool_function"}
}
''')
        
        result = verifier.verify_mcp_tool_registration()
        
        assert result.status == CIVStatus.PASS
        assert "test_tool" in result.registered_tools
        assert len(result.undecorated_tools) == 0
        assert len(result.orphaned_catalog_entries) == 0

    def test_verify_mcp_tool_registration_missing_decorator(
        self, verifier: ComponentIntegrationVerifier, tmp_path: Path
    ):
        """Test detection of tools missing @mcp_tool decorator."""
        mcp_tools_dir = tmp_path / "cortex" / "mcp" / "tools"
        mcp_tools_dir.mkdir(parents=True, exist_ok=True)
        
        # Tool without decorator
        tool_file = mcp_tools_dir / "test_tool.py"
        tool_file.write_text("""
def test_tool_function():
    return "success"
""")
        
        # Catalog references the tool
        catalog_file = tmp_path / "cortex" / "mcp" / "mcp_tools_catalog.py"
        catalog_file.parent.mkdir(parents=True, exist_ok=True)
        catalog_file.write_text('''
TOOLS = {
    "test_tool": {"module": "cortex.mcp.tools.test_tool", "function": "test_tool_function"}
}
''')
        
        result = verifier.verify_mcp_tool_registration()
        
        # Tool in catalog but not decorated = orphaned catalog entry
        assert result.status == CIVStatus.FAIL
        assert "test_tool" in result.orphaned_catalog_entries

    def test_verify_mcp_tool_registration_orphaned_catalog_entry(
        self, verifier: ComponentIntegrationVerifier, tmp_path: Path
    ):
        """Test detection of catalog entries with no implementation."""
        # Create mcp tools directory (but empty)
        mcp_tools_dir = tmp_path / "cortex" / "mcp" / "tools"
        mcp_tools_dir.mkdir(parents=True, exist_ok=True)
        
        # Catalog with orphaned entry
        catalog_file = tmp_path / "cortex" / "mcp" / "mcp_tools_catalog.py"
        catalog_file.parent.mkdir(parents=True, exist_ok=True)
        catalog_file.write_text('''
TOOLS = {
    "orphaned_tool": {"module": "cortex.mcp.tools.nonexistent", "function": "nonexistent_function"}
}
''')
        
        result = verifier.verify_mcp_tool_registration()
        
        assert result.status == CIVStatus.FAIL
        assert "orphaned_tool" in result.orphaned_catalog_entries

    @patch("cortex.orchestrators.core.component_integration_verification.importlib.import_module")
    def test_verify_health_checks_success(
        self, mock_import: Mock, verifier: ComponentIntegrationVerifier, sample_wiring_yaml: Path
    ):
        """Test successful health check execution."""
        # Mock orchestrator with working health check
        mock_orchestrator = MagicMock()
        mock_orchestrator.health_check.return_value = True
        mock_module = MagicMock()
        mock_module.TestOrchestrator.return_value = mock_orchestrator
        mock_import.return_value = mock_module
        
        result = verifier.verify_health_checks(sample_count=1)
        
        assert result.status == CIVStatus.PASS
        assert result.total_sampled == 1
        assert result.passed_count == 1

    @patch("cortex.orchestrators.core.component_integration_verification.importlib.import_module")
    def test_verify_health_checks_failure(
        self, mock_import: Mock, verifier: ComponentIntegrationVerifier, sample_wiring_yaml: Path
    ):
        """Test health check execution failures."""
        # Mock orchestrator with failing health check
        mock_orchestrator = MagicMock()
        mock_orchestrator.health_check.side_effect = Exception("Health check failed")
        mock_module = MagicMock()
        mock_module.TestOrchestrator.return_value = mock_orchestrator
        mock_import.return_value = mock_module
        
        result = verifier.verify_health_checks(sample_count=2)  # Try to sample 2 (both fail)
        
        assert result.status == CIVStatus.FAIL
        assert result.total_sampled >= 1  # At least 1 sampled
        assert result.failed_count >= 1  # At least 1 failed
        assert len(result.failed_orchestrators) >= 1

    def test_generate_civ_report_all_pass(
        self, verifier: ComponentIntegrationVerifier, sample_wiring_yaml: Path
    ):
        """Test CIV report generation with all checks passing."""
        wiring_result = WiringImplementationResult(
            status=CIVStatus.PASS,
            total_orchestrators=2,
            aligned_orchestrators=["TestOrchestrator"],
            missing_implementations=[],
            missing_health_checks=[],
            execution_time_ms=10.0
        )
        
        mcp_result = MCPToolRegistrationResult(
            status=CIVStatus.PASS,
            total_tools=5,
            registered_tools=["tool1", "tool2"],
            undecorated_tools=[],
            orphaned_catalog_entries=[],
            execution_time_ms=5.0
        )
        
        health_result = HealthCheckResult(
            status=CIVStatus.PASS,
            total_sampled=3,
            passed_count=3,
            failed_count=0,
            failed_orchestrators=[],
            execution_time_ms=20.0
        )
        
        report = verifier.generate_civ_report(wiring_result, mcp_result, health_result)
        
        assert report.overall_status == CIVStatus.PASS
        assert report.total_execution_time_ms == 35.0
        assert report.issues_found == 0

    def test_generate_civ_report_with_failures(
        self, verifier: ComponentIntegrationVerifier, sample_wiring_yaml: Path
    ):
        """Test CIV report generation with failures."""
        wiring_result = WiringImplementationResult(
            status=CIVStatus.FAIL,
            total_orchestrators=2,
            aligned_orchestrators=[],
            missing_implementations=["TestOrchestrator"],
            missing_health_checks=[],
            execution_time_ms=10.0
        )
        
        mcp_result = MCPToolRegistrationResult(
            status=CIVStatus.FAIL,
            total_tools=5,
            registered_tools=[],
            undecorated_tools=["tool1"],
            orphaned_catalog_entries=["tool2"],
            execution_time_ms=5.0
        )
        
        health_result = HealthCheckResult(
            status=CIVStatus.FAIL,
            total_sampled=3,
            passed_count=1,
            failed_count=2,
            failed_orchestrators=["Orch1", "Orch2"],
            execution_time_ms=20.0
        )
        
        report = verifier.generate_civ_report(wiring_result, mcp_result, health_result)
        
        assert report.overall_status == CIVStatus.FAIL
        assert report.total_execution_time_ms == 35.0
        assert report.issues_found == 5  # 1 missing impl + 1 undecorated + 1 orphaned + 2 failed health

    def test_verify_all_integration_layers(
        self, verifier: ComponentIntegrationVerifier, sample_wiring_yaml: Path
    ):
        """Test full CIV execution across all 3 layers."""
        with patch.object(verifier, 'verify_wiring_implementation_alignment') as mock_wiring, \
             patch.object(verifier, 'verify_mcp_tool_registration') as mock_mcp, \
             patch.object(verifier, 'verify_health_checks') as mock_health:
            
            mock_wiring.return_value = WiringImplementationResult(
                status=CIVStatus.PASS,
                total_orchestrators=34,
                aligned_orchestrators=["TestOrchestrator"],
                missing_implementations=[],
                missing_health_checks=[],
                execution_time_ms=5.0
            )
            
            mock_mcp.return_value = MCPToolRegistrationResult(
                status=CIVStatus.PASS,
                total_tools=28,
                registered_tools=["tool1"],
                undecorated_tools=[],
                orphaned_catalog_entries=[],
                execution_time_ms=3.0
            )
            
            mock_health.return_value = HealthCheckResult(
                status=CIVStatus.PASS,
                total_sampled=5,
                passed_count=5,
                failed_count=0,
                failed_orchestrators=[],
                execution_time_ms=30.0
            )
            
            report = verifier.verify_all()
            
            assert report.overall_status == CIVStatus.PASS
            assert mock_wiring.called
            assert mock_mcp.called
            assert mock_health.called

"""
Implementation Verifier Tests

Tests for live code inspection and implementation validation.

Phase 22 Component #5: ImplementationVerifier Tests (25 tests)

Authority: AC-EDUCATIONAL-INTERACTION-001, CORE-030
Rule: CORE-008 (TDD)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from cortex.brain.verification.implementation_verifier import (
    ImplementationVerifier,
    ImplementationReport,
    ImplementationStatus,
    ImplementationIssue,
)


@pytest.fixture
def verifier():
    """Create ImplementationVerifier instance."""
    return ImplementationVerifier()


@pytest.fixture
def mock_project_root(tmp_path):
    """Create mock project structure."""
    # Create directory structure
    (tmp_path / "cortex" / "orchestrators" / "core").mkdir(parents=True)
    (tmp_path / "cortex" / "wiring" / "specifications").mkdir(parents=True)
    (tmp_path / "tests" / "unit").mkdir(parents=True)
    
    # Create sample orchestrator file
    orchestrator_file = tmp_path / "cortex" / "orchestrators" / "core" / "sample_orchestrator.py"
    orchestrator_file.write_text("""
\"\"\"Sample Orchestrator.\"\"\"

from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator

class SampleOrchestrator(IOrchestrator):
    \"\"\"Sample orchestrator implementation.\"\"\"
    
    def __init__(self):
        pass
    
    def execute(self, parameters):
        pass
    
    def get_name(self):
        return "SampleOrchestrator"
    
    def get_version(self):
        return "1.0.0"
    
    def initialize(self):
        pass
    
    def get_mode(self):
        pass
""")
    
    # Create wiring.yaml
    wiring_file = tmp_path / "cortex" / "wiring" / "specifications" / "wiring.yaml"
    wiring_file.write_text("""
orchestrators:
  - name: SampleOrchestrator
    module: cortex.orchestrators.core.sample_orchestrator
    class_name: SampleOrchestrator
""")
    
    # Create test file
    test_file = tmp_path / "tests" / "unit" / "test_sample_orchestrator.py"
    test_file.write_text("""
def test_sample():
    pass

def test_another():
    pass
""")
    
    return tmp_path


class TestImplementationStatusEnum:
    """Test ImplementationStatus enum."""
    
    def test_all_status_values_exist(self):
        """Test that all expected status values exist."""
        assert ImplementationStatus.IMPLEMENTED
        assert ImplementationStatus.PARTIAL
        assert ImplementationStatus.MISSING
        assert ImplementationStatus.BROKEN
        assert ImplementationStatus.DEPRECATED


class TestImplementationIssueDataclass:
    """Test ImplementationIssue dataclass."""
    
    def test_creates_issue_with_required_fields(self):
        """Test ImplementationIssue creation."""
        issue = ImplementationIssue(
            severity="error",
            category="code",
            message="Test issue",
            file_path="test.py",
            line_number=42
        )
        
        assert issue.severity == "error"
        assert issue.category == "code"
        assert issue.message == "Test issue"
        assert issue.line_number == 42


class TestImplementationReportDataclass:
    """Test ImplementationReport dataclass."""
    
    def test_creates_report_with_implemented_status(self):
        """Test ImplementationReport creation."""
        report = ImplementationReport(
            component="TestComponent",
            status=ImplementationStatus.IMPLEMENTED,
            confidence=1.0,
            issues=[],
            metrics={"loc": 100},
            recommendations=[]
        )
        
        assert report.status == ImplementationStatus.IMPLEMENTED
        assert report.confidence == 1.0
        assert report.metrics["loc"] == 100


class TestImplementationVerifierInit:
    """Test ImplementationVerifier initialization."""
    
    def test_initializes_with_default_project_root(self):
        """Test initialization with auto-detected project root."""
        verifier = ImplementationVerifier()
        
        assert verifier.project_root is not None
        assert isinstance(verifier.project_root, Path)
    
    def test_initializes_with_custom_project_root(self, tmp_path):
        """Test initialization with custom project root."""
        verifier = ImplementationVerifier(project_root=tmp_path)
        
        assert verifier.project_root == tmp_path


class TestOrchestratorVerification:
    """Test orchestrator verification."""
    
    def test_verifies_complete_orchestrator(self, mock_project_root):
        """Test verification of complete orchestrator."""
        verifier = ImplementationVerifier(project_root=mock_project_root)
        
        report = verifier.verify_orchestrator("SampleOrchestrator")
        
        assert report.component == "SampleOrchestrator"
        assert report.status in [ImplementationStatus.IMPLEMENTED, ImplementationStatus.PARTIAL]
        assert "file_path" in report.metrics
    
    def test_detects_missing_orchestrator(self, mock_project_root):
        """Test detection of missing orchestrator."""
        verifier = ImplementationVerifier(project_root=mock_project_root)
        
        report = verifier.verify_orchestrator("NonExistentOrchestrator")
        
        assert report.status == ImplementationStatus.MISSING
        assert len(report.issues) > 0
        assert any("not found" in issue.message.lower() for issue in report.issues)
    
    def test_includes_metrics_in_report(self, mock_project_root):
        """Test that report includes metrics."""
        verifier = ImplementationVerifier(project_root=mock_project_root)
        
        report = verifier.verify_orchestrator("SampleOrchestrator")
        
        assert "loc" in report.metrics
        assert "method_count" in report.metrics
        assert report.metrics["loc"] > 0


class TestASTAnalysis:
    """Test AST analysis functionality."""
    
    def test_analyzes_class_structure(self, mock_project_root):
        """Test AST analysis of class structure."""
        verifier = ImplementationVerifier(project_root=mock_project_root)
        
        report = verifier.verify_orchestrator("SampleOrchestrator")
        
        assert "methods" in report.metrics
        assert "method_count" in report.metrics
        assert report.metrics["method_count"] > 0
    
    def test_detects_missing_required_methods(self, mock_project_root):
        """Test detection of missing required methods."""
        # Create orchestrator missing some methods
        incomplete_file = mock_project_root / "cortex" / "orchestrators" / "incomplete_orchestrator.py"
        incomplete_file.write_text("""
class IncompleteOrchestrator:
    def execute(self):
        pass
""")
        
        verifier = ImplementationVerifier(project_root=mock_project_root)
        report = verifier.verify_orchestrator("IncompleteOrchestrator", check_wiring=False, check_tests=False)
        
        # Should have issues about missing methods
        method_issues = [i for i in report.issues if "missing" in i.message.lower() and "method" in i.message.lower()]
        assert len(method_issues) > 0
    
    def test_detects_missing_docstring(self, mock_project_root):
        """Test detection of missing class docstring."""
        # Create orchestrator without docstring
        no_doc_file = mock_project_root / "cortex" / "orchestrators" / "nodoc_orchestrator.py"
        no_doc_file.write_text("""
class NodocOrchestrator:
    def execute(self):
        pass
""")
        
        verifier = ImplementationVerifier(project_root=mock_project_root)
        report = verifier.verify_orchestrator("NodocOrchestrator", check_wiring=False, check_tests=False)
        
        # Should have warning about missing docstring
        docstring_issues = [i for i in report.issues if "docstring" in i.message.lower()]
        assert len(docstring_issues) > 0


class TestWiringVerification:
    """Test wiring configuration verification."""
    
    def test_verifies_registered_orchestrator(self, mock_project_root):
        """Test verification of registered orchestrator in wiring."""
        verifier = ImplementationVerifier(project_root=mock_project_root)
        
        report = verifier.verify_orchestrator("SampleOrchestrator", check_tests=False)
        
        # Should not have wiring issues
        wiring_errors = [i for i in report.issues if i.category == "wiring" and i.severity == "error"]
        assert len(wiring_errors) == 0
    
    def test_detects_unregistered_orchestrator(self, mock_project_root):
        """Test detection of unregistered orchestrator."""
        # Create orchestrator not in wiring
        unregistered_file = mock_project_root / "cortex" / "orchestrators" / "unregistered_orchestrator.py"
        unregistered_file.write_text("""
class UnregisteredOrchestrator:
    pass
""")
        
        verifier = ImplementationVerifier(project_root=mock_project_root)
        report = verifier.verify_orchestrator("UnregisteredOrchestrator", check_tests=False)
        
        # Should have wiring warning
        wiring_issues = [i for i in report.issues if i.category == "wiring"]
        assert len(wiring_issues) > 0


class TestTestCoverageVerification:
    """Test coverage verification."""
    
    def test_verifies_test_coverage_exists(self, mock_project_root):
        """Test verification of existing test coverage."""
        verifier = ImplementationVerifier(project_root=mock_project_root)
        
        report = verifier.verify_orchestrator("SampleOrchestrator", check_wiring=False)
        
        assert "test_file_count" in report.metrics
        assert report.metrics["test_file_count"] > 0
        assert "test_count" in report.metrics
        assert report.metrics["test_count"] > 0
    
    def test_detects_missing_test_coverage(self, mock_project_root):
        """Test detection of missing test coverage."""
        # Create orchestrator without tests
        notested_file = mock_project_root / "cortex" / "orchestrators" / "notested_orchestrator.py"
        notested_file.write_text("""
class NotestedOrchestrator:
    pass
""")
        
        verifier = ImplementationVerifier(project_root=mock_project_root)
        report = verifier.verify_orchestrator("NotestedOrchestrator", check_wiring=False)
        
        # Should have test warning
        test_issues = [i for i in report.issues if i.category == "tests"]
        assert len(test_issues) > 0


class TestMCPToolVerification:
    """Test MCP tool verification."""
    
    def test_detects_missing_mcp_tools_directory(self, tmp_path):
        """Test detection when MCP tools directory doesn't exist."""
        verifier = ImplementationVerifier(project_root=tmp_path)
        
        report = verifier.verify_mcp_tool("cortex_test")
        
        assert report.status == ImplementationStatus.MISSING
        assert any("not found" in issue.message.lower() for issue in report.issues)
    
    def test_detects_missing_mcp_tool(self, mock_project_root):
        """Test detection of missing MCP tool."""
        # Create MCP tools directory but no tool
        (mock_project_root / "cortex" / "mcp" / "tools").mkdir(parents=True)
        
        verifier = ImplementationVerifier(project_root=mock_project_root)
        report = verifier.verify_mcp_tool("cortex_nonexistent")
        
        assert report.status == ImplementationStatus.MISSING
    
    def test_verifies_existing_mcp_tool(self, mock_project_root):
        """Test verification of existing MCP tool."""
        # Create MCP tool file
        mcp_dir = mock_project_root / "cortex" / "mcp" / "tools"
        mcp_dir.mkdir(parents=True)
        
        tool_file = mcp_dir / "cortex_test.py"
        tool_file.write_text("""
@mcp_tool
def cortex_test():
    pass
""")
        
        verifier = ImplementationVerifier(project_root=mock_project_root)
        report = verifier.verify_mcp_tool("cortex_test")
        
        assert report.status in [ImplementationStatus.IMPLEMENTED, ImplementationStatus.PARTIAL]
        assert "file_path" in report.metrics


class TestStatusDetermination:
    """Test status determination logic."""
    
    def test_implemented_status_with_no_issues(self, verifier):
        """Test IMPLEMENTED status with no issues."""
        status = verifier._determine_status([], {"loc": 100})
        assert status == ImplementationStatus.IMPLEMENTED
    
    def test_broken_status_with_errors(self, verifier):
        """Test BROKEN status with error issues."""
        issues = [
            ImplementationIssue(severity="error", category="code", message="Error 1"),
            ImplementationIssue(severity="error", category="code", message="Error 2"),
        ]
        status = verifier._determine_status(issues, {})
        assert status == ImplementationStatus.BROKEN
    
    def test_partial_status_with_warnings(self, verifier):
        """Test PARTIAL status with warning issues."""
        issues = [
            ImplementationIssue(severity="warning", category="code", message="Warning 1"),
            ImplementationIssue(severity="warning", category="code", message="Warning 2"),
        ]
        status = verifier._determine_status(issues, {})
        assert status == ImplementationStatus.PARTIAL


class TestConfidenceCalculation:
    """Test confidence score calculation."""
    
    def test_full_confidence_with_no_issues(self, verifier):
        """Test 1.0 confidence with no issues."""
        confidence = verifier._calculate_confidence([], {})
        assert confidence == 1.0
    
    def test_low_confidence_with_errors(self, verifier):
        """Test low confidence with errors."""
        issues = [
            ImplementationIssue(severity="error", category="code", message="Error"),
        ]
        confidence = verifier._calculate_confidence(issues, {})
        assert confidence < 0.5
    
    def test_medium_confidence_with_warnings(self, verifier):
        """Test medium confidence with warnings."""
        issues = [
            ImplementationIssue(severity="warning", category="code", message="Warning 1"),
            ImplementationIssue(severity="warning", category="code", message="Warning 2"),
        ]
        confidence = verifier._calculate_confidence(issues, {})
        assert 0.5 < confidence < 1.0


class TestRecommendationGeneration:
    """Test recommendation generation."""
    
    def test_generates_recommendations_from_issues(self, verifier):
        """Test recommendation generation from issues."""
        issues = [
            ImplementationIssue(
                severity="error",
                category="code",
                message="Missing method",
                recommendation="Implement missing method"
            ),
            ImplementationIssue(
                severity="warning",
                category="tests",
                message="No tests",
                recommendation="Add test coverage"
            ),
        ]
        
        recommendations = verifier._generate_recommendations(issues, "TestComponent")
        
        assert len(recommendations) > 0
        assert "Implement missing method" in recommendations
        assert "Add test coverage" in recommendations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

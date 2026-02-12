"""
Tests for MCP-FIRST Violation Detector.

AC_START: AC-WAVE-K-006
Description: MCP-FIRST detector tests
"""

import pytest
from pathlib import Path
from datetime import datetime
from cortex.governance.mcp_first_detector import (
    MCPFirstDetector,
    MCPViolation,
    MCPComplianceReport,
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace for testing."""
    cortex_dir = tmp_path / "cortex"
    cortex_dir.mkdir()
    
    orchestrators_dir = cortex_dir / "orchestrators"
    orchestrators_dir.mkdir()
    
    return tmp_path


@pytest.fixture
def detector(temp_workspace):
    """Create MCP-FIRST detector instance."""
    return MCPFirstDetector(workspace_root=temp_workspace)


class TestMCPFirstDetector:
    """Tests for MCPFirstDetector initialization."""
    
    def test_detector_initialization(self, detector):
        """MCPFirstDetector initializes with workspace root."""
        assert detector is not None
        assert detector.workspace_root.exists()
        assert detector.violations == []
        assert detector.files_checked == 0
    
    def test_detector_has_forbidden_patterns(self, detector):
        """MCPFirstDetector has forbidden patterns defined."""
        assert len(detector.forbidden_patterns) >= 4
        assert "create_file" in detector.forbidden_patterns
        assert "replace_string_in_file" in detector.forbidden_patterns


class TestDirectFileOperations:
    """Tests for detecting direct file operations."""
    
    def test_create_file_violation_detected(self, temp_workspace, detector):
        """Direct create_file usage is detected."""
        py_file = temp_workspace / "cortex" / "violator.py"
        py_file.write_text("""
def implement_feature():
    # IMPLEMENT new feature
    create_file("output.txt", "content")
""")
        
        report = detector.detect_violations()
        
        assert len(report.violations) == 1
        assert report.violations[0].violation_type == "DIRECT_FILE_OPERATION"
        assert "create_file" in report.violations[0].description
    
    def test_replace_string_violation_detected(self, temp_workspace, detector):
        """Direct replace_string_in_file usage is detected."""
        py_file = temp_workspace / "cortex" / "violator.py"
        py_file.write_text("""
def fix_bug():
    # FIX critical bug
    replace_string_in_file("app.py", "old", "new")
""")
        
        report = detector.detect_violations()
        
        assert len(report.violations) == 1
        assert "replace_string_in_file" in report.violations[0].description


class TestOrchestratorViolations:
    """Tests for detecting orchestrator violations."""
    
    def test_direct_file_open_detected(self, temp_workspace, detector):
        """Direct file open() with write mode is detected."""
        orch_file = temp_workspace / "cortex" / "orchestrators" / "bad_orch.py"
        orch_file.write_text("""
class BadOrchestrator:
    def execute(self, request):
        with open("output.txt", "w") as f:
            f.write("direct write")
""")
        
        report = detector.detect_violations()
        
        violations = [v for v in report.violations if "bad_orch.py" in v.file_path]
        assert len(violations) >= 1
    
    def test_path_write_text_detected(self, temp_workspace, detector):
        """Direct Path.write_text() is detected."""
        orch_file = temp_workspace / "cortex" / "orchestrators" / "bad_orch.py"
        orch_file.write_text("""
from pathlib import Path

class BadOrchestrator:
    def execute(self, request):
        Path("output.txt").write_text("content")
""")
        
        report = detector.detect_violations()
        
        violations = [v for v in report.violations if "bad_orch.py" in v.file_path]
        assert len(violations) >= 1


class TestImplementationContext:
    """Tests for implementation context detection."""
    
    def test_implement_keyword_triggers_check(self, detector):
        """IMPLEMENT keyword triggers MCP-FIRST check."""
        content = """
def process_request():
    # IMPLEMENT new feature
    create_file("test.txt", "data")
"""
        
        # Check if in implementation context
        position = content.index("create_file")
        is_impl = detector._is_implementation_context(content, position)
        
        assert is_impl is True
    
    def test_fix_keyword_triggers_check(self, detector):
        """FIX keyword triggers MCP-FIRST check."""
        content = """
def bug_fix():
    # FIX critical issue
    replace_string_in_file("app.py", "bug", "fix")
"""
        
        position = content.index("replace_string")
        is_impl = detector._is_implementation_context(content, position)
        
        assert is_impl is True
    
    def test_non_implementation_context_ignored(self, detector):
        """Non-implementation contexts don't trigger check."""
        content = """
def analyze_code():
    # Just reading data
    with open("data.txt", "r") as f:
        return f.read()
"""
        
        position = content.index("open")
        is_impl = detector._is_implementation_context(content, position)
        
        # Reading is okay, only write operations checked
        assert is_impl is False


class TestIntentRouting:
    """Tests for intent routing checks."""
    
    def test_implement_intent_requires_mcp(self, detector):
        """IMPLEMENT intent requires MCP routing."""
        assert detector.check_intent_routing("IMPLEMENT feature") is True
    
    def test_fix_intent_requires_mcp(self, detector):
        """FIX intent requires MCP routing."""
        assert detector.check_intent_routing("FIX bug") is True
    
    def test_refactor_intent_requires_mcp(self, detector):
        """REFACTOR intent requires MCP routing."""
        assert detector.check_intent_routing("REFACTOR code") is True
    
    def test_analyze_intent_optional_mcp(self, detector):
        """ANALYZE intent doesn't require MCP."""
        assert detector.check_intent_routing("ANALYZE codebase") is False


class TestComplianceReport:
    """Tests for MCPComplianceReport."""
    
    def test_compliance_report_creation(self):
        """MCPComplianceReport can be created."""
        report = MCPComplianceReport(
            files_checked=10,
            violations=[],
            compliance_rate=100.0,
            timestamp=datetime.now()
        )
        
        assert report.files_checked == 10
        assert report.is_compliant() is True
    
    def test_compliance_report_with_violations(self):
        """MCPComplianceReport with violations is not compliant."""
        violation = MCPViolation(
            file_path="test.py",
            line_number=10,
            violation_type="DIRECT_FILE_OPERATION",
            description="create_file usage",
            detected_at=datetime.now()
        )
        
        report = MCPComplianceReport(
            files_checked=10,
            violations=[violation],
            compliance_rate=90.0,
            timestamp=datetime.now()
        )
        
        assert report.is_compliant() is False
        assert len(report.violations) == 1


class TestViolationSummary:
    """Tests for violation summary."""
    
    def test_violation_summary_empty(self, detector):
        """Empty violations returns empty summary."""
        summary = detector.get_violation_summary()
        
        assert summary == {}
    
    def test_violation_summary_grouped(self, temp_workspace, detector):
        """Violations are grouped by type in summary."""
        # Create file with multiple violations
        py_file = temp_workspace / "cortex" / "multi_violator.py"
        py_file.write_text("""
def implement_feature():
    # IMPLEMENT
    create_file("a.txt", "data")
    replace_string_in_file("b.py", "old", "new")
""")
        
        detector.detect_violations()
        summary = detector.get_violation_summary()
        
        assert "DIRECT_FILE_OPERATION" in summary
        assert summary["DIRECT_FILE_OPERATION"] >= 2


# AC_COMPLETE: AC-WAVE-K-006 ✅

# AC-ID: AC-DEBUG-ORCH-001
"""
Tests for DebuggingOrchestrator - Smart Debug Injection System.

GOVERNANCE:
- CORE-008: TDD (tests written FIRST)
- CORE-011: Type hints
- CORE-012: Google-style docstrings
- CORE-027: Audit trail for all injections

COMPONENTS TESTED:
1. DebugSession - Session management with manifest persistence
2. DebugInjector - Strategic log injection using AST
3. DebugCleaner - Marker-based cleanup with verification
4. DebuggingOrchestrator - Main orchestrator coordinating all components

Author: Asif Hussain
Date: 2026-02-03
"""

import json
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import MagicMock, patch

import pytest

# Import will fail until implementation exists (RED phase)
try:
    from cortex.orchestrators.support.debugging_orchestrator import (
        DebuggingOrchestrator,
        DebugSession,
        DebugInjector,
        DebugCleaner,
        InjectionPoint,
        InjectionStrategy,
        SessionManifest,
        CleanupStatus,
    )
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def sample_python_code() -> str:
    """Sample Python code for testing injection."""
    return '''"""Sample module for testing."""

import logging

logger = logging.getLogger(__name__)


def calculate_sum(a: int, b: int) -> int:
    """Calculate sum of two numbers."""
    result = a + b
    return result


def process_data(data: dict) -> dict:
    """Process input data."""
    if not data:
        raise ValueError("Data cannot be empty")
    
    try:
        processed = {"count": len(data), "keys": list(data.keys())}
        return processed
    except Exception as e:
        raise RuntimeError(f"Processing failed: {e}")


class DataProcessor:
    """Process data with state."""
    
    def __init__(self, config: dict):
        """Initialize processor."""
        self.config = config
        self.processed_count = 0
    
    def process(self, item: dict) -> dict:
        """Process single item."""
        self.processed_count += 1
        return {"item": item, "count": self.processed_count}
'''


@pytest.fixture
def temp_workspace(sample_python_code: str) -> Path:
    """Create temporary workspace with sample files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        
        # Create sample Python file
        sample_file = workspace / "sample_module.py"
        sample_file.write_text(sample_python_code)
        
        # Create nested structure
        nested_dir = workspace / "subpackage"
        nested_dir.mkdir()
        nested_file = nested_dir / "nested_module.py"
        nested_file.write_text('''"""Nested module."""

def nested_function(x: int) -> int:
    """Nested function."""
    return x * 2
''')
        
        yield workspace


@pytest.fixture
def session_id() -> str:
    """Generate consistent session ID for tests."""
    return "test_session_001"


# =============================================================================
# TEST: DebugSession - Session Management
# =============================================================================

@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Implementation not yet available")
class TestDebugSession:
    """Tests for DebugSession class."""
    
    def test_create_session_generates_unique_id(self):
        """Session creation generates unique ID."""
        session1 = DebugSession.create(target_paths=["/path/to/code"])
        session2 = DebugSession.create(target_paths=["/path/to/code"])
        
        assert session1.session_id != session2.session_id
        assert session1.session_id.startswith("dbg_")
    
    def test_create_session_with_explicit_id(self, session_id: str):
        """Session can be created with explicit ID."""
        session = DebugSession.create(
            target_paths=["/path/to/code"],
            session_id=session_id
        )
        
        assert session.session_id == session_id
    
    def test_session_tracks_target_paths(self, temp_workspace: Path):
        """Session tracks target paths."""
        paths = [str(temp_workspace / "sample_module.py")]
        session = DebugSession.create(target_paths=paths)
        
        assert session.target_paths == paths
    
    def test_session_has_creation_timestamp(self):
        """Session has creation timestamp."""
        before = datetime.utcnow()
        session = DebugSession.create(target_paths=["/path"])
        after = datetime.utcnow()
        
        assert before <= session.created_at <= after
    
    def test_session_default_strategy_is_strategic(self):
        """Default injection strategy is 'strategic'."""
        session = DebugSession.create(target_paths=["/path"])
        
        assert session.strategy == InjectionStrategy.STRATEGIC
    
    def test_session_can_use_comprehensive_strategy(self):
        """Session can use comprehensive strategy."""
        session = DebugSession.create(
            target_paths=["/path"],
            strategy=InjectionStrategy.COMPREHENSIVE
        )
        
        assert session.strategy == InjectionStrategy.COMPREHENSIVE


# =============================================================================
# TEST: SessionManifest - Persistence
# =============================================================================

@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Implementation not yet available")
class TestSessionManifest:
    """Tests for SessionManifest persistence."""
    
    def test_manifest_saves_to_json(self, temp_workspace: Path, session_id: str):
        """Manifest saves session to JSON file."""
        session = DebugSession.create(
            target_paths=[str(temp_workspace)],
            session_id=session_id
        )
        manifest = SessionManifest(session)
        
        manifest_path = temp_workspace / ".cortex_debug" / f"{session_id}.json"
        manifest.save(manifest_path)
        
        assert manifest_path.exists()
        data = json.loads(manifest_path.read_text())
        assert data["session"]["id"] == session_id
    
    def test_manifest_loads_from_json(self, temp_workspace: Path, session_id: str):
        """Manifest loads session from JSON file."""
        # Create and save
        session = DebugSession.create(
            target_paths=[str(temp_workspace)],
            session_id=session_id
        )
        manifest = SessionManifest(session)
        manifest_path = temp_workspace / ".cortex_debug" / f"{session_id}.json"
        manifest.save(manifest_path)
        
        # Load
        loaded_manifest = SessionManifest.load(manifest_path)
        
        assert loaded_manifest.session.session_id == session_id
    
    def test_manifest_tracks_injections(self, temp_workspace: Path, session_id: str):
        """Manifest tracks injection points."""
        session = DebugSession.create(
            target_paths=[str(temp_workspace)],
            session_id=session_id
        )
        manifest = SessionManifest(session)
        
        injection = InjectionPoint(
            file_path=str(temp_workspace / "sample_module.py"),
            line_number=10,
            injection_type="function_entry",
            trace_id="trace_001",
            original_content=""
        )
        manifest.add_injection(injection)
        
        assert len(manifest.injections) == 1
        assert manifest.injections[0].trace_id == "trace_001"
    
    def test_manifest_cleanup_status_default_pending(self, session_id: str):
        """Manifest cleanup status defaults to pending."""
        session = DebugSession.create(target_paths=["/path"], session_id=session_id)
        manifest = SessionManifest(session)
        
        assert manifest.cleanup_status == CleanupStatus.PENDING


# =============================================================================
# TEST: InjectionPoint - Injection Data
# =============================================================================

@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Implementation not yet available")
class TestInjectionPoint:
    """Tests for InjectionPoint data class."""
    
    def test_injection_point_creation(self):
        """InjectionPoint can be created with required fields."""
        point = InjectionPoint(
            file_path="/path/to/file.py",
            line_number=42,
            injection_type="function_entry",
            trace_id="trace_001",
            original_content="    result = compute()"
        )
        
        assert point.file_path == "/path/to/file.py"
        assert point.line_number == 42
        assert point.injection_type == "function_entry"
        assert point.trace_id == "trace_001"
    
    def test_injection_point_generates_marker(self, session_id: str):
        """InjectionPoint generates unique marker."""
        point = InjectionPoint(
            file_path="/path/to/file.py",
            line_number=42,
            injection_type="function_entry",
            trace_id="trace_001",
            original_content=""
        )
        
        marker = point.get_marker(session_id)
        
        assert session_id in marker
        assert "trace_001" in marker
        assert "CORTEX_DEBUG" in marker


# =============================================================================
# TEST: DebugInjector - Log Injection
# =============================================================================

@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Implementation not yet available")
class TestDebugInjector:
    """Tests for DebugInjector class."""
    
    def test_injector_identifies_function_entries(self, sample_python_code: str):
        """Injector identifies function entry points."""
        injector = DebugInjector()
        points = injector.analyze_code(sample_python_code, strategy=InjectionStrategy.STRATEGIC)
        
        function_entries = [p for p in points if p.injection_type == "function_entry"]
        
        # Should find: calculate_sum, process_data, __init__, process
        assert len(function_entries) >= 4
    
    def test_injector_identifies_exception_handlers(self, sample_python_code: str):
        """Injector identifies exception handlers."""
        injector = DebugInjector()
        points = injector.analyze_code(sample_python_code, strategy=InjectionStrategy.STRATEGIC)
        
        exception_handlers = [p for p in points if p.injection_type == "exception_handler"]
        
        # Should find: except Exception as e block
        assert len(exception_handlers) >= 1
    
    def test_injector_identifies_conditionals_in_comprehensive_mode(self, sample_python_code: str):
        """Injector identifies conditionals in comprehensive mode."""
        injector = DebugInjector()
        points = injector.analyze_code(sample_python_code, strategy=InjectionStrategy.COMPREHENSIVE)
        
        conditionals = [p for p in points if p.injection_type == "conditional"]
        
        # Should find: if not data
        assert len(conditionals) >= 1
    
    def test_injector_generates_log_statement(self, session_id: str):
        """Injector generates proper log statement."""
        injector = DebugInjector()
        point = InjectionPoint(
            file_path="/path/to/file.py",
            line_number=10,
            injection_type="function_entry",
            trace_id="trace_001",
            original_content="def calculate_sum(a: int, b: int) -> int:",
            function_name="calculate_sum",
            parameters=["a", "b"]
        )
        
        log_statement = injector.generate_log_statement(point, session_id)
        
        assert "CORTEX_DEBUG" in log_statement
        assert session_id in log_statement
        assert "calculate_sum" in log_statement
        assert "logger.debug" in log_statement
    
    def test_injector_preserves_indentation(self, session_id: str):
        """Injector preserves original indentation."""
        injector = DebugInjector()
        point = InjectionPoint(
            file_path="/path/to/file.py",
            line_number=10,
            injection_type="function_entry",
            trace_id="trace_001",
            original_content="        result = compute()",  # 8 spaces
            function_name="compute"
        )
        
        log_statement = injector.generate_log_statement(point, session_id)
        
        # Should start with same indentation
        assert log_statement.startswith("        ")
    
    def test_inject_into_file_modifies_content(
        self, temp_workspace: Path, session_id: str
    ):
        """Injector modifies file content with log statements."""
        injector = DebugInjector()
        file_path = temp_workspace / "sample_module.py"
        original_content = file_path.read_text()
        
        session = DebugSession.create(
            target_paths=[str(file_path)],
            session_id=session_id
        )
        manifest = SessionManifest(session)
        
        result = injector.inject_into_file(
            file_path=file_path,
            session_id=session_id,
            manifest=manifest,
            strategy=InjectionStrategy.STRATEGIC
        )
        
        assert result.success
        modified_content = file_path.read_text()
        assert "CORTEX_DEBUG" in modified_content
        assert modified_content != original_content
    
    def test_inject_adds_logger_import_if_missing(self, temp_workspace: Path, session_id: str):
        """Injector adds logger import if not present."""
        injector = DebugInjector()
        
        # Create file without logging import
        no_logging_file = temp_workspace / "no_logging.py"
        no_logging_file.write_text('''"""Module without logging."""

def simple_func():
    return 42
''')
        
        session = DebugSession.create(
            target_paths=[str(no_logging_file)],
            session_id=session_id
        )
        manifest = SessionManifest(session)
        
        injector.inject_into_file(
            file_path=no_logging_file,
            session_id=session_id,
            manifest=manifest,
            strategy=InjectionStrategy.STRATEGIC
        )
        
        modified_content = no_logging_file.read_text()
        assert "import logging" in modified_content or "from cortex.common.debug_logger" in modified_content


# =============================================================================
# TEST: DebugCleaner - Cleanup
# =============================================================================

@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Implementation not yet available")
class TestDebugCleaner:
    """Tests for DebugCleaner class."""
    
    def test_cleaner_finds_all_markers(self, temp_workspace: Path, session_id: str):
        """Cleaner finds all CORTEX_DEBUG markers."""
        # First inject
        injector = DebugInjector()
        file_path = temp_workspace / "sample_module.py"
        
        session = DebugSession.create(
            target_paths=[str(file_path)],
            session_id=session_id
        )
        manifest = SessionManifest(session)
        
        injector.inject_into_file(
            file_path=file_path,
            session_id=session_id,
            manifest=manifest,
            strategy=InjectionStrategy.STRATEGIC
        )
        
        # Then find markers
        cleaner = DebugCleaner()
        markers = cleaner.find_markers(file_path, session_id)
        
        assert len(markers) > 0
        assert all(session_id in m for m in markers)
    
    def test_cleaner_removes_injected_lines(self, temp_workspace: Path, session_id: str):
        """Cleaner removes all injected debug lines."""
        # Inject first
        injector = DebugInjector()
        file_path = temp_workspace / "sample_module.py"
        original_content = file_path.read_text()
        
        session = DebugSession.create(
            target_paths=[str(file_path)],
            session_id=session_id
        )
        manifest = SessionManifest(session)
        
        injector.inject_into_file(
            file_path=file_path,
            session_id=session_id,
            manifest=manifest,
            strategy=InjectionStrategy.STRATEGIC
        )
        
        # Verify injection
        assert "CORTEX_DEBUG" in file_path.read_text()
        
        # Clean
        cleaner = DebugCleaner()
        result = cleaner.clean_file(file_path, session_id)
        
        assert result.success
        cleaned_content = file_path.read_text()
        assert "CORTEX_DEBUG" not in cleaned_content
    
    def test_cleaner_preserves_original_code(self, temp_workspace: Path, session_id: str):
        """Cleaner preserves original code after cleanup."""
        injector = DebugInjector()
        file_path = temp_workspace / "sample_module.py"
        original_content = file_path.read_text()
        
        session = DebugSession.create(
            target_paths=[str(file_path)],
            session_id=session_id
        )
        manifest = SessionManifest(session)
        
        # Inject
        injector.inject_into_file(
            file_path=file_path,
            session_id=session_id,
            manifest=manifest,
            strategy=InjectionStrategy.STRATEGIC
        )
        
        # Clean
        cleaner = DebugCleaner()
        cleaner.clean_file(file_path, session_id)
        
        cleaned_content = file_path.read_text()
        
        # Original functions should still be there
        assert "def calculate_sum" in cleaned_content
        assert "def process_data" in cleaned_content
        assert "class DataProcessor" in cleaned_content
    
    def test_cleaner_only_removes_specified_session(
        self, temp_workspace: Path, session_id: str
    ):
        """Cleaner only removes markers for specified session."""
        injector = DebugInjector()
        file_path = temp_workspace / "sample_module.py"
        
        # Inject with session 1
        session1 = DebugSession.create(
            target_paths=[str(file_path)],
            session_id="session_001"
        )
        manifest1 = SessionManifest(session1)
        injector.inject_into_file(
            file_path=file_path,
            session_id="session_001",
            manifest=manifest1,
            strategy=InjectionStrategy.STRATEGIC
        )
        
        # Inject with session 2
        session2 = DebugSession.create(
            target_paths=[str(file_path)],
            session_id="session_002"
        )
        manifest2 = SessionManifest(session2)
        injector.inject_into_file(
            file_path=file_path,
            session_id="session_002",
            manifest=manifest2,
            strategy=InjectionStrategy.STRATEGIC
        )
        
        # Clean only session 1
        cleaner = DebugCleaner()
        cleaner.clean_file(file_path, "session_001")
        
        content = file_path.read_text()
        assert "session_001" not in content
        assert "session_002" in content
    
    def test_cleaner_updates_manifest_status(self, temp_workspace: Path, session_id: str):
        """Cleaner updates manifest cleanup status."""
        injector = DebugInjector()
        file_path = temp_workspace / "sample_module.py"
        
        session = DebugSession.create(
            target_paths=[str(file_path)],
            session_id=session_id
        )
        manifest = SessionManifest(session)
        manifest_path = temp_workspace / ".cortex_debug" / f"{session_id}.json"
        
        injector.inject_into_file(
            file_path=file_path,
            session_id=session_id,
            manifest=manifest,
            strategy=InjectionStrategy.STRATEGIC
        )
        manifest.save(manifest_path)
        
        # Clean
        cleaner = DebugCleaner()
        cleaner.clean_session(temp_workspace, session_id)
        
        # Reload manifest
        loaded_manifest = SessionManifest.load(manifest_path)
        assert loaded_manifest.cleanup_status == CleanupStatus.COMPLETE


# =============================================================================
# TEST: DebuggingOrchestrator - Main Orchestrator
# =============================================================================

@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Implementation not yet available")
class TestDebuggingOrchestrator:
    """Tests for DebuggingOrchestrator class."""
    
    def test_orchestrator_implements_i_orchestrator(self):
        """Orchestrator implements IOrchestrator interface."""
        from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator
        
        orchestrator = DebuggingOrchestrator()
        
        assert isinstance(orchestrator, IOrchestrator)
    
    def test_orchestrator_get_name(self):
        """Orchestrator returns correct name."""
        orchestrator = DebuggingOrchestrator()
        
        assert orchestrator.get_name() == "DebuggingOrchestrator"
    
    def test_orchestrator_get_version(self):
        """Orchestrator returns version."""
        orchestrator = DebuggingOrchestrator()
        
        version = orchestrator.get_version()
        assert version  # Not empty
        assert "." in version  # Semantic versioning
    
    def test_orchestrator_get_mcp_tools(self):
        """Orchestrator exposes MCP tools."""
        orchestrator = DebuggingOrchestrator()
        
        result = orchestrator.get_mcp_tools()
        
        assert result.is_ok()
        tools = result.unwrap()
        
        # Should expose three tools
        tool_names = [t["name"] for t in tools.values()]
        assert "cortex_debug_inject" in tool_names
        assert "cortex_debug_cleanup" in tool_names
        assert "cortex_debug_status" in tool_names
    
    def test_orchestrator_inject_operation(self, temp_workspace: Path):
        """Orchestrator executes inject operation."""
        orchestrator = DebuggingOrchestrator()
        
        result = orchestrator.execute_operation(
            operation_name="inject",
            parameters={
                "target_paths": [str(temp_workspace / "sample_module.py")],
                "strategy": "strategic"
            }
        )
        
        assert result.is_ok()
        response = result.unwrap()
        assert "session_id" in response
        assert response["injections_count"] > 0
    
    def test_orchestrator_cleanup_operation(self, temp_workspace: Path):
        """Orchestrator executes cleanup operation."""
        orchestrator = DebuggingOrchestrator()
        
        # First inject
        inject_result = orchestrator.execute_operation(
            operation_name="inject",
            parameters={
                "target_paths": [str(temp_workspace / "sample_module.py")],
                "strategy": "strategic"
            }
        )
        session_id = inject_result.unwrap()["session_id"]
        
        # Then cleanup
        result = orchestrator.execute_operation(
            operation_name="cleanup",
            parameters={
                "session_id": session_id,
                "workspace_path": str(temp_workspace)
            }
        )
        
        assert result.is_ok()
        response = result.unwrap()
        assert response["status"] == "complete"
    
    def test_orchestrator_status_operation(self, temp_workspace: Path):
        """Orchestrator executes status operation."""
        orchestrator = DebuggingOrchestrator()
        
        # First inject
        inject_result = orchestrator.execute_operation(
            operation_name="inject",
            parameters={
                "target_paths": [str(temp_workspace / "sample_module.py")],
                "strategy": "strategic"
            }
        )
        session_id = inject_result.unwrap()["session_id"]
        
        # Get status
        result = orchestrator.execute_operation(
            operation_name="status",
            parameters={
                "session_id": session_id,
                "workspace_path": str(temp_workspace)
            }
        )
        
        assert result.is_ok()
        response = result.unwrap()
        assert "session_id" in response
        assert "injections" in response
        assert "cleanup_status" in response
    
    def test_orchestrator_inject_validates_paths(self):
        """Orchestrator validates target paths exist."""
        orchestrator = DebuggingOrchestrator()
        
        result = orchestrator.execute_operation(
            operation_name="inject",
            parameters={
                "target_paths": ["/nonexistent/path/file.py"],
                "strategy": "strategic"
            }
        )
        
        assert result.is_err()
        assert "not found" in result.error.lower() or "not exist" in result.error.lower()
    
    def test_orchestrator_excludes_sensitive_values(self, temp_workspace: Path):
        """Orchestrator excludes sensitive values from logs."""
        # Create file with sensitive parameter names
        sensitive_file = temp_workspace / "sensitive.py"
        sensitive_file.write_text('''"""Module with sensitive params."""

def authenticate(username: str, password: str, api_key: str):
    """Authenticate user."""
    return {"token": "abc123"}
''')
        
        orchestrator = DebuggingOrchestrator()
        
        result = orchestrator.execute_operation(
            operation_name="inject",
            parameters={
                "target_paths": [str(sensitive_file)],
                "strategy": "strategic"
            }
        )
        
        assert result.is_ok()
        content = sensitive_file.read_text()
        
        # Should not log password or api_key values
        assert "password=%s" not in content
        assert "api_key=%s" not in content


# =============================================================================
# TEST: MCP Tool Functions
# =============================================================================

@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Implementation not yet available")
class TestMCPTools:
    """Tests for MCP tool functions."""
    
    def test_cortex_debug_inject_tool_registered(self):
        """cortex_debug_inject is registered as MCP tool."""
        from cortex.mcp.decorators import MCP_TOOLS_REGISTRY
        from cortex.orchestrators.support.debugging_orchestrator import cortex_debug_inject
        
        # Trigger registration by importing
        assert hasattr(cortex_debug_inject, '_mcp_tool_metadata')
        assert cortex_debug_inject._mcp_tool_metadata["name"] == "cortex_debug_inject"
    
    def test_cortex_debug_cleanup_tool_registered(self):
        """cortex_debug_cleanup is registered as MCP tool."""
        from cortex.orchestrators.support.debugging_orchestrator import cortex_debug_cleanup
        
        assert hasattr(cortex_debug_cleanup, '_mcp_tool_metadata')
        assert cortex_debug_cleanup._mcp_tool_metadata["name"] == "cortex_debug_cleanup"
    
    def test_cortex_debug_status_tool_registered(self):
        """cortex_debug_status is registered as MCP tool."""
        from cortex.orchestrators.support.debugging_orchestrator import cortex_debug_status
        
        assert hasattr(cortex_debug_status, '_mcp_tool_metadata')
        assert cortex_debug_status._mcp_tool_metadata["name"] == "cortex_debug_status"


# =============================================================================
# TEST: Edge Cases
# =============================================================================

@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Implementation not yet available")
class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_inject_empty_file(self, temp_workspace: Path):
        """Injector handles empty files gracefully."""
        empty_file = temp_workspace / "empty.py"
        empty_file.write_text("")
        
        injector = DebugInjector()
        session = DebugSession.create(
            target_paths=[str(empty_file)],
            session_id="test_empty"
        )
        manifest = SessionManifest(session)
        
        result = injector.inject_into_file(
            file_path=empty_file,
            session_id="test_empty",
            manifest=manifest,
            strategy=InjectionStrategy.STRATEGIC
        )
        
        # Should succeed but with no injections
        assert result.success
        assert len(manifest.injections) == 0
    
    def test_inject_syntax_error_file(self, temp_workspace: Path):
        """Injector handles files with syntax errors."""
        bad_file = temp_workspace / "syntax_error.py"
        bad_file.write_text('''"""Bad syntax."""
def broken(
    # Missing closing paren
''')
        
        injector = DebugInjector()
        session = DebugSession.create(
            target_paths=[str(bad_file)],
            session_id="test_syntax"
        )
        manifest = SessionManifest(session)
        
        result = injector.inject_into_file(
            file_path=bad_file,
            session_id="test_syntax",
            manifest=manifest,
            strategy=InjectionStrategy.STRATEGIC
        )
        
        # Should succeed gracefully with 0 injections (skipped parsing)
        assert result.success
        assert result.injections_count == 0
    
    def test_cleanup_nonexistent_session(self, temp_workspace: Path):
        """Cleaner handles nonexistent session gracefully."""
        cleaner = DebugCleaner()
        
        result = cleaner.clean_session(temp_workspace, "nonexistent_session")
        
        assert not result.success
        assert "not found" in result.error.lower()
    
    def test_concurrent_sessions_isolation(self, temp_workspace: Path):
        """Multiple debug sessions are isolated."""
        orchestrator = DebuggingOrchestrator()
        file_path = str(temp_workspace / "sample_module.py")
        
        # Create two sessions
        result1 = orchestrator.execute_operation(
            operation_name="inject",
            parameters={"target_paths": [file_path], "strategy": "strategic"}
        )
        session1_id = result1.unwrap()["session_id"]
        
        result2 = orchestrator.execute_operation(
            operation_name="inject",
            parameters={"target_paths": [file_path], "strategy": "strategic"}
        )
        session2_id = result2.unwrap()["session_id"]
        
        # Cleanup session 1 only
        orchestrator.execute_operation(
            operation_name="cleanup",
            parameters={"session_id": session1_id, "workspace_path": str(temp_workspace)}
        )
        
        # Session 2 should still be active
        status_result = orchestrator.execute_operation(
            operation_name="status",
            parameters={"session_id": session2_id, "workspace_path": str(temp_workspace)}
        )
        
        assert status_result.is_ok()
        assert status_result.unwrap()["cleanup_status"] == "pending"
    
    def test_inject_readonly_file_fails_gracefully(self, temp_workspace: Path):
        """Injector fails gracefully on read-only files."""
        readonly_file = temp_workspace / "readonly.py"
        readonly_file.write_text('''"""Readonly file."""
def func():
    pass
''')
        readonly_file.chmod(0o444)  # Read-only
        
        try:
            injector = DebugInjector()
            session = DebugSession.create(
                target_paths=[str(readonly_file)],
                session_id="test_readonly"
            )
            manifest = SessionManifest(session)
            
            result = injector.inject_into_file(
                file_path=readonly_file,
                session_id="test_readonly",
                manifest=manifest,
                strategy=InjectionStrategy.STRATEGIC
            )
            
            assert not result.success
            assert "permission" in result.error.lower() or "read" in result.error.lower()
        finally:
            readonly_file.chmod(0o644)  # Restore permissions for cleanup


# =============================================================================
# TEST: Audit Trail (CORE-027)
# =============================================================================

@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Implementation not yet available")
class TestAuditTrail:
    """Tests for audit trail compliance (CORE-027)."""
    
    def test_orchestrator_logs_inject_operation(self, temp_workspace: Path):
        """Orchestrator logs inject operations to audit trail."""
        orchestrator = DebuggingOrchestrator()
        
        orchestrator.execute_operation(
            operation_name="inject",
            parameters={
                "target_paths": [str(temp_workspace / "sample_module.py")],
                "strategy": "strategic"
            }
        )
        
        result = orchestrator.get_audit_trail(limit=10)
        
        assert result.is_ok()
        trail = result.unwrap()
        assert len(trail) >= 1
        assert any("inject" in entry.get("operation", "").lower() for entry in trail)
    
    def test_orchestrator_logs_cleanup_operation(self, temp_workspace: Path):
        """Orchestrator logs cleanup operations to audit trail."""
        orchestrator = DebuggingOrchestrator()
        
        # Inject first
        inject_result = orchestrator.execute_operation(
            operation_name="inject",
            parameters={
                "target_paths": [str(temp_workspace / "sample_module.py")],
                "strategy": "strategic"
            }
        )
        session_id = inject_result.unwrap()["session_id"]
        
        # Cleanup
        orchestrator.execute_operation(
            operation_name="cleanup",
            parameters={
                "session_id": session_id,
                "workspace_path": str(temp_workspace)
            }
        )
        
        result = orchestrator.get_audit_trail(limit=10)
        
        assert result.is_ok()
        trail = result.unwrap()
        assert any("cleanup" in entry.get("operation", "").lower() for entry in trail)

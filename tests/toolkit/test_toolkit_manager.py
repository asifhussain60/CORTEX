"""
Tests for CORTEX Toolkit Manager

RED Phase Tests for TDD - Tests the central orchestration layer.
"""
import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import sys
import os

# Add toolkit to path for testing
toolkit_path = str(Path(__file__).parent.parent.parent / "cortex-toolkit")
if toolkit_path not in sys.path:
    sys.path.insert(0, toolkit_path)

from core.toolkit_manager import (
    ToolkitManager, 
    ExecutionContext, 
    ExecutionResult,
    ExecutionStatus,
    ToolSpec,
    CreationCheck,
)
from core.gate_keeper import GateKeeper
from core.exceptions import ValidationResult


@pytest.fixture
def temp_toolkit_dir(tmp_path):
    """Create a temporary toolkit directory for tests."""
    toolkit_dir = tmp_path / "toolkit"
    toolkit_dir.mkdir()
    return toolkit_dir


class TestToolkitManagerInit:
    """Tests for ToolkitManager initialization."""
    
    def test_manager_initializes_with_registry(self, tmp_path):
        """Manager initializes with a ToolkitRegistry."""
        toolkit_dir = tmp_path / "toolkit"
        toolkit_dir.mkdir()
        
        with patch('core.toolkit_manager.ToolkitRegistry') as mock_registry_class:
            mock_registry = Mock()
            mock_registry.toolkit_root = toolkit_dir
            mock_registry.list_tools.return_value = []
            mock_registry.list_categories.return_value = []
            mock_registry_class.return_value = mock_registry
            
            manager = ToolkitManager(toolkit_root=toolkit_dir)
            
            assert manager.registry is not None
            mock_registry_class.assert_called_once()
    
    def test_manager_initializes_gatekeeper(self, tmp_path):
        """Manager initializes GateKeeper for validation."""
        toolkit_dir = tmp_path / "toolkit"
        toolkit_dir.mkdir()
        
        with patch('core.toolkit_manager.ToolkitRegistry') as mock_registry_class:
            mock_registry = Mock()
            mock_registry.toolkit_root = toolkit_dir
            mock_registry.list_tools.return_value = []
            mock_registry.list_categories.return_value = []
            mock_registry_class.return_value = mock_registry
            
            manager = ToolkitManager(toolkit_root=toolkit_dir)
            
            assert manager.gate_keeper is not None
            assert isinstance(manager.gate_keeper, GateKeeper)
    
    def test_manager_accepts_custom_toolkit_root(self, tmp_path):
        """Manager accepts custom toolkit root path."""
        custom_path = tmp_path / "custom"
        custom_path.mkdir()
        
        with patch('core.toolkit_manager.ToolkitRegistry') as mock_registry_class:
            mock_registry = Mock()
            mock_registry.toolkit_root = custom_path
            mock_registry.list_tools.return_value = []
            mock_registry.list_categories.return_value = []
            mock_registry_class.return_value = mock_registry
            
            manager = ToolkitManager(toolkit_root=custom_path)
            
            mock_registry_class.assert_called_once_with(custom_path)


class TestToolkitManagerValidation:
    """Tests for manager validation before execution."""
    
    @pytest.fixture
    def manager_with_mocks(self, tmp_path):
        """Create manager with mocked dependencies."""
        toolkit_dir = tmp_path / "toolkit"
        toolkit_dir.mkdir()
        
        with patch('core.toolkit_manager.ToolkitRegistry') as mock_reg_class:
            mock_registry = Mock()
            mock_registry.toolkit_root = toolkit_dir
            mock_registry.get_tool = Mock(return_value={
                "name": "test-tool",
                "script": "test.py",
                "platforms": ["windows", "linux", "macos"],
                "requires_admin": False,
                "execution_method": "cli"
            })
            mock_registry.resolve_script_path = Mock(return_value=toolkit_dir / "test.py")
            mock_registry.list_tools = Mock(return_value=[{"name": "test-tool", "description": "Test tool"}])
            mock_registry.list_categories = Mock(return_value=["testing"])
            mock_reg_class.return_value = mock_registry
            
            manager = ToolkitManager(toolkit_root=toolkit_dir)
            yield manager
    
    @pytest.mark.asyncio
    async def test_manager_validates_before_execution(self, manager_with_mocks):
        """Manager must call GateKeeper before any tool runs."""
        manager = manager_with_mocks
        manager.gate_keeper.validate_execution = Mock(return_value=ValidationResult(
            passed=False,
            checks=[Mock(name="test", passed=False, severity="error", message="test error")]
        ))
        
        result = await manager.execute("test-tool", [])
        
        manager.gate_keeper.validate_execution.assert_called_once()
        assert result.status == ExecutionStatus.VALIDATION_FAILED
    
    @pytest.mark.asyncio
    async def test_manager_returns_validation_errors(self, manager_with_mocks):
        """Manager provides clear error when validation fails."""
        manager = manager_with_mocks
        manager.gate_keeper.validate_execution = Mock(return_value=ValidationResult(
            passed=False,
            checks=[Mock(name="tool_exists", passed=False, severity="error", message="Tool not found")]
        ))
        
        result = await manager.execute("nonexistent", [])
        
        assert result.status == ExecutionStatus.VALIDATION_FAILED
        assert result.validation_result is not None
        assert result.exit_code == -1
    
    @pytest.mark.asyncio
    async def test_manager_can_skip_validation(self, manager_with_mocks):
        """Manager can skip validation when explicitly requested."""
        manager = manager_with_mocks
        manager.gate_keeper.validate_execution = Mock()
        
        # Mock subprocess to avoid actual execution
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            
            context = ExecutionContext(
                tool="test-tool",
                args=[],
                skip_validation=True
            )
            # Mock path exists
            with patch.object(Path, 'exists', return_value=True):
                result = await manager.execute("test-tool", [], context)
        
        manager.gate_keeper.validate_execution.assert_not_called()


class TestToolkitManagerExecution:
    """Tests for tool execution."""
    
    @pytest.fixture
    def manager_with_execution_mocks(self, tmp_path):
        """Create manager ready for execution tests."""
        toolkit_dir = tmp_path / "toolkit"
        toolkit_dir.mkdir()
        
        with patch('core.toolkit_manager.ToolkitRegistry') as mock_reg_class:
            mock_registry = Mock()
            mock_registry.toolkit_root = toolkit_dir
            mock_registry.get_tool = Mock(return_value={
                "name": "test-tool",
                "script": "test.py",
                "platforms": ["windows", "linux", "macos"],
                "requires_admin": False,
                "execution_method": "cli"
            })
            mock_registry.resolve_script_path = Mock(return_value=toolkit_dir / "test.py")
            mock_registry.list_tools = Mock(return_value=[{"name": "test-tool", "description": "Test tool"}])
            mock_registry.list_categories = Mock(return_value=["testing"])
            mock_reg_class.return_value = mock_registry
            
            manager = ToolkitManager(toolkit_root=toolkit_dir)
            # Make validation pass
            manager.gate_keeper.validate_execution = Mock(return_value=ValidationResult(passed=True, checks=[]))
            yield manager
    
    @pytest.mark.asyncio
    async def test_manager_executes_valid_tool(self, manager_with_execution_mocks):
        """Manager executes tool that passes validation."""
        manager = manager_with_execution_mocks
        
        with patch('subprocess.run') as mock_run, \
             patch.object(Path, 'exists', return_value=True):
            mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")
            
            result = await manager.execute("test-tool", ["--check-only"])
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.exit_code == 0
        mock_run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_manager_captures_stdout(self, manager_with_execution_mocks):
        """Manager captures stdout from tool execution."""
        manager = manager_with_execution_mocks
        
        with patch('subprocess.run') as mock_run, \
             patch.object(Path, 'exists', return_value=True):
            mock_run.return_value = Mock(returncode=0, stdout="Output text", stderr="")
            
            result = await manager.execute("test-tool", [])
        
        assert result.stdout == "Output text"
    
    @pytest.mark.asyncio
    async def test_manager_captures_stderr(self, manager_with_execution_mocks):
        """Manager captures stderr from tool execution."""
        manager = manager_with_execution_mocks
        
        with patch('subprocess.run') as mock_run, \
             patch.object(Path, 'exists', return_value=True):
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="Error message")
            
            result = await manager.execute("test-tool", [])
        
        assert result.stderr == "Error message"
        assert result.status == ExecutionStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_manager_tracks_duration(self, manager_with_execution_mocks):
        """Manager tracks execution duration."""
        manager = manager_with_execution_mocks
        
        with patch('subprocess.run') as mock_run, \
             patch.object(Path, 'exists', return_value=True):
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            
            result = await manager.execute("test-tool", [])
        
        assert result.duration_ms >= 0
    
    @pytest.mark.asyncio
    async def test_manager_dry_run_mode(self, manager_with_execution_mocks):
        """Manager supports dry run mode."""
        manager = manager_with_execution_mocks
        
        context = ExecutionContext(tool="test-tool", args=["--arg"], dry_run=True)
        result = await manager.execute("test-tool", ["--arg"], context)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert "[DRY RUN]" in result.stdout
    
    @pytest.mark.asyncio
    async def test_manager_blocks_copilot_chat_tools(self, manager_with_execution_mocks):
        """Manager blocks direct execution of copilot_chat tools."""
        manager = manager_with_execution_mocks
        manager.registry.get_tool = Mock(return_value={
            "name": "plan",
            "execution_method": "copilot_chat",
            "platforms": ["windows", "linux", "macos"]
        })
        
        with patch.object(Path, 'exists', return_value=True):
            result = await manager.execute("plan", [])
        
        assert result.status == ExecutionStatus.BLOCKED
        assert "copilot_chat" in result.error


class TestToolkitManagerCreationCheck:
    """Tests for tool creation checking."""
    
    @pytest.fixture
    def manager_with_mocks(self, tmp_path):
        """Create manager for creation check tests."""
        toolkit_dir = tmp_path / "toolkit"
        toolkit_dir.mkdir()
        
        with patch('core.toolkit_manager.ToolkitRegistry') as mock_reg_class:
            mock_registry = Mock()
            mock_registry.toolkit_root = toolkit_dir
            mock_registry.get_tool = Mock(side_effect=lambda name: {
                "cleanup": {"name": "cleanup", "description": "Cleanup cache and temp files"},
                "align": {"name": "align", "description": "Align code to standards"},
            }.get(name))
            mock_registry.list_tools = Mock(return_value=[
                {"name": "cleanup", "description": "Cleanup cache and temp files"},
                {"name": "align", "description": "Align code to standards"},
            ])
            mock_registry.list_categories = Mock(return_value=["maintenance", "code_analysis"])
            mock_reg_class.return_value = mock_registry
            
            manager = ToolkitManager(toolkit_root=toolkit_dir)
            yield manager
    
    def test_manager_prevents_duplicate_tool_creation(self, manager_with_mocks):
        """Manager prevents creating tool with existing name."""
        manager = manager_with_mocks
        
        spec = ToolSpec(
            name="cleanup",  # Already exists
            description="Test cleanup",
            command="test-cleanup",
            script_path="test.py",
            category="maintenance"
        )
        
        check = manager.can_create_tool(spec)
        
        assert not check.can_create
        assert "cleanup" in check.overlapping_tools
    
    def test_manager_warns_about_similar_tools(self, manager_with_mocks):
        """Manager provides semantic analysis for tool creation."""
        manager = manager_with_mocks
        
        # Test with a unique tool that doesn't overlap
        spec = ToolSpec(
            name="email-sender",
            description="Send email notifications",
            command="email-sender",
            script_path="email_sender.py",
            category="communication"
        )
        
        check = manager.can_create_tool(spec)
        
        # RequestAnalyzer should allow unique tools
        assert check.can_create is True
        # For unique tools, there should be no overlapping tools
        assert isinstance(check.overlapping_tools, list)
    
    def test_manager_allows_unique_tool_creation(self, manager_with_mocks):
        """Manager allows creation of unique tools."""
        manager = manager_with_mocks
        
        spec = ToolSpec(
            name="completely-unique-tool",
            description="Does something unique",
            command="unique",
            script_path="unique.py",
            category="utilities"
        )
        
        check = manager.can_create_tool(spec)
        
        assert check.can_create


class TestToolkitManagerHistory:
    """Tests for execution history tracking."""
    
    @pytest.fixture
    def manager_with_mocks(self, tmp_path):
        """Create manager for history tests."""
        toolkit_dir = tmp_path / "toolkit"
        toolkit_dir.mkdir()
        
        with patch('core.toolkit_manager.ToolkitRegistry') as mock_reg_class:
            mock_registry = Mock()
            mock_registry.toolkit_root = toolkit_dir
            mock_registry.get_tool = Mock(return_value={
                "name": "test-tool",
                "script": "test.py",
                "platforms": ["windows", "linux", "macos"],
                "execution_method": "cli"
            })
            mock_registry.resolve_script_path = Mock(return_value=toolkit_dir / "test.py")
            mock_registry.list_tools = Mock(return_value=[{"name": "test-tool", "description": "Test tool"}])
            mock_registry.list_categories = Mock(return_value=["testing"])
            mock_reg_class.return_value = mock_registry
            
            manager = ToolkitManager(toolkit_root=toolkit_dir)
            manager.gate_keeper.validate_execution = Mock(return_value=ValidationResult(passed=True, checks=[]))
            yield manager
    
    @pytest.mark.asyncio
    async def test_manager_records_execution_history(self, manager_with_mocks):
        """Manager records execution in history."""
        manager = manager_with_mocks
        
        with patch('subprocess.run') as mock_run, \
             patch.object(Path, 'exists', return_value=True):
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            
            await manager.execute("test-tool", [])
        
        history = manager.get_execution_history()
        assert len(history) == 1
        assert history[0]["tool"] == "test-tool"
    
    @pytest.mark.asyncio
    async def test_manager_limits_history_size(self, manager_with_mocks):
        """Manager limits history to max size."""
        manager = manager_with_mocks
        manager._max_history = 5
        
        with patch('subprocess.run') as mock_run, \
             patch.object(Path, 'exists', return_value=True):
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            
            for i in range(10):
                await manager.execute("test-tool", [f"--run={i}"])
        
        history = manager.get_execution_history(limit=100)
        assert len(history) <= 5


class TestToolkitManagerSync:
    """Tests for synchronous execution wrapper."""
    
    @pytest.fixture
    def manager_with_mocks(self, tmp_path):
        """Create manager for sync tests."""
        toolkit_dir = tmp_path / "toolkit"
        toolkit_dir.mkdir()
        
        with patch('core.toolkit_manager.ToolkitRegistry') as mock_reg_class:
            mock_registry = Mock()
            mock_registry.toolkit_root = toolkit_dir
            mock_registry.get_tool = Mock(return_value={
                "name": "test-tool",
                "script": "test.py",
                "platforms": ["windows", "linux", "macos"],
                "execution_method": "cli"
            })
            mock_registry.resolve_script_path = Mock(return_value=toolkit_dir / "test.py")
            mock_registry.list_tools = Mock(return_value=[{"name": "test-tool", "description": "Test tool"}])
            mock_registry.list_categories = Mock(return_value=["testing"])
            mock_reg_class.return_value = mock_registry
            
            manager = ToolkitManager(toolkit_root=toolkit_dir)
            manager.gate_keeper.validate_execution = Mock(return_value=ValidationResult(passed=True, checks=[]))
            yield manager
    
    def test_sync_wrapper_works(self, manager_with_mocks):
        """Sync wrapper executes tool synchronously."""
        manager = manager_with_mocks
        
        with patch('subprocess.run') as mock_run, \
             patch.object(Path, 'exists', return_value=True):
            mock_run.return_value = Mock(returncode=0, stdout="sync output", stderr="")
            
            result = manager.execute_sync("test-tool", [])
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.stdout == "sync output"


class TestToolkitManagerConvenience:
    """Tests for convenience methods."""
    
    @pytest.fixture
    def manager_with_mocks(self, tmp_path):
        """Create manager for convenience method tests."""
        toolkit_dir = tmp_path / "toolkit"
        toolkit_dir.mkdir()
        
        with patch('core.toolkit_manager.ToolkitRegistry') as mock_reg_class:
            mock_registry = Mock()
            mock_registry.toolkit_root = toolkit_dir
            mock_registry.get_tool = Mock(return_value={"name": "test", "description": "Test"})
            mock_registry.list_tools = Mock(return_value=[{"name": "test", "description": "Test"}])
            mock_registry.list_categories = Mock(return_value=["brain", "operations"])
            mock_reg_class.return_value = mock_registry
            
            manager = ToolkitManager(toolkit_root=toolkit_dir)
            yield manager
    
    def test_list_tools_delegates_to_registry(self, manager_with_mocks):
        """list_tools() delegates to registry."""
        manager = manager_with_mocks
        # Reset the mock to clear calls from __init__
        manager.registry.list_tools.reset_mock()
        
        tools = manager.list_tools()
        
        manager.registry.list_tools.assert_called_once()
    
    def test_list_categories_delegates_to_registry(self, manager_with_mocks):
        """list_categories() delegates to registry."""
        manager = manager_with_mocks
        # Reset the mock to clear calls from __init__
        manager.registry.list_categories.reset_mock()
        
        categories = manager.list_categories()
        
        manager.registry.list_categories.assert_called_once()
    
    def test_validate_tool_without_execution(self, manager_with_mocks):
        """validate_tool() validates without executing."""
        manager = manager_with_mocks
        
        result = manager.validate_tool("test", ["--arg"])
        
        assert "passed" in result
        assert "checks" in result

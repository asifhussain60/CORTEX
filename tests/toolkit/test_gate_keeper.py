"""
Tests for CORTEX Toolkit GateKeeper

RED Phase Tests for TDD - Tests the pre-execution validation layer.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add toolkit to path for testing
toolkit_path = str(Path(__file__).parent.parent.parent / "cortex-toolkit")
if toolkit_path not in sys.path:
    sys.path.insert(0, toolkit_path)

# Now we can import from the toolkit
from core.gate_keeper import GateKeeper, SecurityViolation
from core.exceptions import ValidationResult


class TestGateKeeperToolExists:
    """Tests for tool existence validation."""
    
    @pytest.fixture
    def mock_registry(self):
        """Create a mock registry with sample tools."""
        registry = Mock()
        registry.get_tool = Mock(side_effect=lambda name: {
            "align": {
                "name": "align",
                "command": "cortex-align",
                "script": "core/brain/align.py",
                "platforms": ["windows", "linux", "macos"],
                "requires_admin": False
            },
            "cleanup": {
                "name": "cleanup",
                "command": "cortex-cleanup",
                "script": "core/brain/cleanup.py",
                "platforms": ["windows", "linux", "macos"],
                "requires_admin": False
            },
            "deploy": {
                "name": "deploy",
                "command": "cortex-deploy",
                "script": "core/operations/deploy.py",
                "platforms": ["windows", "linux", "macos"],
                "requires_admin": True
            },
        }.get(name))
        
        registry.list_tools = Mock(return_value=[
            {"name": "align"},
            {"name": "cleanup"},
            {"name": "deploy"},
        ])
        
        return registry
    
    def test_gatekeeper_rejects_nonexistent_tool(self, mock_registry):
        """GateKeeper rejects tools not in manifest."""
        gatekeeper = GateKeeper(mock_registry)
        
        result = gatekeeper.validate_execution("nonexistent-tool", [])
        
        assert not result.passed
        assert any(c.name == "tool_exists" and not c.passed for c in result.checks)
    
    def test_gatekeeper_accepts_existing_tool(self, mock_registry):
        """GateKeeper accepts tools that exist in registry."""
        gatekeeper = GateKeeper(mock_registry)
        
        result = gatekeeper.validate_execution("align", [])
        
        tool_check = next(c for c in result.checks if c.name == "tool_exists")
        assert tool_check.passed
    
    def test_gatekeeper_suggests_similar_tools(self, mock_registry):
        """GateKeeper suggests similar tool names when not found."""
        gatekeeper = GateKeeper(mock_registry)
        
        result = gatekeeper.validate_execution("alig", [])  # Typo
        
        tool_check = next(c for c in result.checks if c.name == "tool_exists")
        assert not tool_check.passed
        assert "Did you mean" in tool_check.message or tool_check.details.get("similar_tools")


class TestGateKeeperPlatformSupport:
    """Tests for platform compatibility validation."""
    
    @pytest.fixture
    def mock_registry_with_platform(self):
        """Registry with platform-specific tools."""
        registry = Mock()
        registry.get_tool = Mock(side_effect=lambda name: {
            "windows-only": {
                "name": "windows-only",
                "platforms": ["windows"],
                "requires_admin": False
            },
            "cross-platform": {
                "name": "cross-platform",
                "platforms": ["windows", "linux", "macos"],
                "requires_admin": False
            },
        }.get(name))
        registry.list_tools = Mock(return_value=[
            {"name": "windows-only"},
            {"name": "cross-platform"},
        ])
        return registry
    
    @patch('platform.system')
    def test_gatekeeper_blocks_unsupported_platform(self, mock_platform, mock_registry_with_platform):
        """GateKeeper blocks tools on unsupported platforms."""
        mock_platform.return_value = "Linux"
        gatekeeper = GateKeeper(mock_registry_with_platform)
        
        result = gatekeeper.validate_execution("windows-only", [])
        
        platform_check = next(c for c in result.checks if c.name == "platform_support")
        assert not platform_check.passed
        assert "linux" in platform_check.message.lower()
    
    @patch('platform.system')
    def test_gatekeeper_allows_supported_platform(self, mock_platform, mock_registry_with_platform):
        """GateKeeper allows tools on supported platforms."""
        mock_platform.return_value = "Darwin"  # macOS
        gatekeeper = GateKeeper(mock_registry_with_platform)
        
        result = gatekeeper.validate_execution("cross-platform", [])
        
        platform_check = next(c for c in result.checks if c.name == "platform_support")
        assert platform_check.passed


class TestGateKeeperSecuritySanitization:
    """Tests for argument sanitization and security."""
    
    @pytest.fixture
    def mock_registry(self):
        """Simple registry for security tests."""
        registry = Mock()
        registry.get_tool = Mock(return_value={
            "name": "test-tool",
            "platforms": ["windows", "linux", "macos"],
            "requires_admin": False
        })
        registry.list_tools = Mock(return_value=[{"name": "test-tool"}])
        return registry
    
    def test_gatekeeper_blocks_shell_injection_semicolon(self, mock_registry):
        """GateKeeper blocks shell injection via semicolon."""
        gatekeeper = GateKeeper(mock_registry)
        
        result = gatekeeper.validate_execution("test-tool", ["--file=test; rm -rf /"])
        
        sanitize_check = next(c for c in result.checks if c.name == "argument_sanitization")
        assert not sanitize_check.passed
        assert "shell_metacharacters" in str(sanitize_check.details)
    
    def test_gatekeeper_blocks_shell_injection_pipe(self, mock_registry):
        """GateKeeper blocks shell injection via pipe."""
        gatekeeper = GateKeeper(mock_registry)
        
        result = gatekeeper.validate_execution("test-tool", ["--input | cat /etc/passwd"])
        
        sanitize_check = next(c for c in result.checks if c.name == "argument_sanitization")
        assert not sanitize_check.passed
    
    def test_gatekeeper_blocks_shell_injection_backtick(self, mock_registry):
        """GateKeeper blocks shell injection via backtick."""
        gatekeeper = GateKeeper(mock_registry)
        
        result = gatekeeper.validate_execution("test-tool", ["`whoami`"])
        
        sanitize_check = next(c for c in result.checks if c.name == "argument_sanitization")
        assert not sanitize_check.passed
    
    def test_gatekeeper_blocks_path_traversal(self, mock_registry):
        """GateKeeper blocks path traversal attempts."""
        gatekeeper = GateKeeper(mock_registry)
        
        result = gatekeeper.validate_execution("test-tool", ["--file=../../../etc/passwd"])
        
        sanitize_check = next(c for c in result.checks if c.name == "argument_sanitization")
        assert not sanitize_check.passed
        assert "path_traversal" in str(sanitize_check.details)
    
    def test_gatekeeper_blocks_null_byte_injection(self, mock_registry):
        """GateKeeper blocks null byte injection."""
        gatekeeper = GateKeeper(mock_registry)
        
        result = gatekeeper.validate_execution("test-tool", ["file.txt\x00.exe"])
        
        sanitize_check = next(c for c in result.checks if c.name == "argument_sanitization")
        assert not sanitize_check.passed
    
    def test_gatekeeper_allows_safe_arguments(self, mock_registry):
        """GateKeeper allows safe, normal arguments."""
        gatekeeper = GateKeeper(mock_registry)
        
        result = gatekeeper.validate_execution("test-tool", [
            "--check-only",
            "--output=results.json",
            "-v",
            "myfile.txt"
        ])
        
        sanitize_check = next(c for c in result.checks if c.name == "argument_sanitization")
        assert sanitize_check.passed
    
    def test_gatekeeper_allows_numbers(self, mock_registry):
        """GateKeeper allows numeric arguments."""
        gatekeeper = GateKeeper(mock_registry)
        
        result = gatekeeper.validate_execution("test-tool", ["123", "456"])
        
        sanitize_check = next(c for c in result.checks if c.name == "argument_sanitization")
        assert sanitize_check.passed


class TestGateKeeperRateLimiting:
    """Tests for rate limiting functionality."""
    
    @pytest.fixture
    def mock_registry(self):
        """Registry with rate-limited tool."""
        registry = Mock()
        registry.get_tool = Mock(return_value={
            "name": "rate-limited-tool",
            "platforms": ["windows", "linux", "macos"],
            "requires_admin": False,
            "rate_limit": {"max_calls_per_minute": 3}
        })
        registry.list_tools = Mock(return_value=[{"name": "rate-limited-tool"}])
        return registry
    
    def test_gatekeeper_enforces_rate_limit(self, mock_registry):
        """GateKeeper blocks calls exceeding rate limit."""
        gatekeeper = GateKeeper(mock_registry)
        
        # Make 3 calls (should succeed)
        for _ in range(3):
            result = gatekeeper.validate_execution("rate-limited-tool", [])
            rate_check = next(c for c in result.checks if c.name == "rate_limit")
            assert rate_check.passed
        
        # 4th call should be blocked
        result = gatekeeper.validate_execution("rate-limited-tool", [])
        rate_check = next(c for c in result.checks if c.name == "rate_limit")
        assert not rate_check.passed
        assert "Rate limit exceeded" in rate_check.message
    
    def test_gatekeeper_can_skip_rate_limit(self, mock_registry):
        """GateKeeper can skip rate limit check when requested."""
        gatekeeper = GateKeeper(mock_registry)
        
        # Exhaust rate limit
        for _ in range(5):
            gatekeeper.validate_execution("rate-limited-tool", [])
        
        # Skip rate limit check
        result = gatekeeper.validate_execution("rate-limited-tool", [], skip_rate_limit=True)
        
        # Should not have rate limit check
        rate_checks = [c for c in result.checks if c.name == "rate_limit"]
        assert len(rate_checks) == 0
    
    def test_gatekeeper_reset_rate_limits(self, mock_registry):
        """GateKeeper can reset rate limits."""
        gatekeeper = GateKeeper(mock_registry)
        
        # Exhaust rate limit
        for _ in range(5):
            gatekeeper.validate_execution("rate-limited-tool", [])
        
        # Reset
        gatekeeper.reset_rate_limits("rate-limited-tool")
        
        # Should work again
        result = gatekeeper.validate_execution("rate-limited-tool", [])
        rate_check = next(c for c in result.checks if c.name == "rate_limit")
        assert rate_check.passed


class TestGateKeeperPermissions:
    """Tests for permission validation."""
    
    @pytest.fixture
    def mock_registry(self):
        """Registry with admin tool."""
        registry = Mock()
        registry.get_tool = Mock(side_effect=lambda name: {
            "admin-tool": {
                "name": "admin-tool",
                "platforms": ["windows", "linux", "macos"],
                "requires_admin": True
            },
            "user-tool": {
                "name": "user-tool",
                "platforms": ["windows", "linux", "macos"],
                "requires_admin": False
            },
        }.get(name))
        registry.list_tools = Mock(return_value=[
            {"name": "admin-tool"},
            {"name": "user-tool"},
        ])
        return registry
    
    def test_gatekeeper_flags_admin_required(self, mock_registry):
        """GateKeeper flags when admin privileges are required."""
        gatekeeper = GateKeeper(mock_registry)
        
        result = gatekeeper.validate_execution("admin-tool", [])
        
        perm_check = next(c for c in result.checks if c.name == "permissions")
        assert "requires admin" in perm_check.message.lower()
        assert perm_check.details.get("requires_admin") is True


class TestGateKeeperValidationResult:
    """Tests for overall validation result."""
    
    @pytest.fixture
    def mock_registry(self):
        """Full registry for validation tests."""
        registry = Mock()
        registry.get_tool = Mock(return_value={
            "name": "test-tool",
            "platforms": ["windows", "linux", "macos"],
            "requires_admin": False
        })
        registry.list_tools = Mock(return_value=[{"name": "test-tool"}])
        return registry
    
    def test_validation_result_has_all_checks(self, mock_registry):
        """Validation result contains all check types."""
        gatekeeper = GateKeeper(mock_registry)
        
        result = gatekeeper.validate_execution("test-tool", ["--test"])
        
        check_names = {c.name for c in result.checks}
        expected_checks = {"tool_exists", "platform_support", "argument_sanitization", "rate_limit", "permissions"}
        assert check_names == expected_checks
    
    def test_validation_passed_when_all_pass(self, mock_registry):
        """Validation passes when all checks pass."""
        gatekeeper = GateKeeper(mock_registry)
        
        result = gatekeeper.validate_execution("test-tool", ["--safe-arg"])
        
        assert result.passed
        assert all(c.passed or c.severity != "error" for c in result.checks)
    
    def test_validation_fails_when_any_critical_fails(self, mock_registry):
        """Validation fails when any critical check fails."""
        mock_registry.get_tool = Mock(return_value=None)  # Tool doesn't exist
        gatekeeper = GateKeeper(mock_registry)
        
        result = gatekeeper.validate_execution("nonexistent", [])
        
        assert not result.passed

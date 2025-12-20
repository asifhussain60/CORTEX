"""
Test suite for Cross-Machine Context Orchestrator (Feature 4).

Tests OS detection, shell identification, path translation, runtime detection,
and brain integration across Windows/Mac/Linux platforms.

RED PHASE: All tests should fail initially (orchestrator not yet implemented).
"""

import pytest
import platform
from pathlib import Path
from unittest.mock import patch, MagicMock


# RED PHASE: Import will fail - orchestrator doesn't exist yet
# Uncomment after GREEN phase begins
# from src.orchestrators.cross_machine_context_orchestrator import (
#     CrossMachineContextOrchestrator,
#     MachineContext,
# )


class TestPhase41_OSAndShellDetection:
    """Phase 4.1: OS and shell detection tests (RED phase)."""

    @pytest.fixture
    def orchestrator(self):
        """Fixture to create orchestrator instance."""
        # RED: This will fail until orchestrator exists
        from src.orchestrators.cross_machine_context_orchestrator import (
            CrossMachineContextOrchestrator,
        )
        return CrossMachineContextOrchestrator()

    def test_detect_windows_operating_system(self, orchestrator):
        """Should correctly identify Windows OS."""
        with patch("platform.system", return_value="Windows"):
            context = orchestrator.detect_machine_context()
            assert context.os == "Windows"
            assert context.os_version is not None

    def test_detect_macos_operating_system(self, orchestrator):
        """Should correctly identify macOS."""
        with patch("platform.system", return_value="Darwin"):
            context = orchestrator.detect_machine_context()
            assert context.os == "Mac"
            assert context.os_version is not None

    def test_detect_linux_operating_system(self, orchestrator):
        """Should correctly identify Linux OS."""
        with patch("platform.system", return_value="Linux"):
            context = orchestrator.detect_machine_context()
            assert context.os == "Linux"
            assert context.os_version is not None

    def test_detect_powershell_shell(self, orchestrator):
        """Should identify PowerShell as active shell on Windows."""
        with patch("platform.system", return_value="Windows"):
            with patch.dict("os.environ", {"PSModulePath": "C:\\Program Files\\PowerShell"}):
                context = orchestrator.detect_machine_context()
                assert context.shell in ["PowerShell", "pwsh"]

    def test_detect_bash_shell(self, orchestrator):
        """Should identify bash shell on Unix systems."""
        with patch("platform.system", return_value="Linux"):
            with patch.dict("os.environ", {"SHELL": "/bin/bash"}):
                context = orchestrator.detect_machine_context()
                assert context.shell == "bash"

    def test_detect_zsh_shell(self, orchestrator):
        """Should identify zsh shell (common on macOS)."""
        with patch("platform.system", return_value="Darwin"):
            with patch.dict("os.environ", {"SHELL": "/bin/zsh"}):
                context = orchestrator.detect_machine_context()
                assert context.shell == "zsh"

    def test_detect_cmd_shell(self, orchestrator):
        """Should identify cmd.exe on Windows."""
        with patch("platform.system", return_value="Windows"):
            with patch.dict("os.environ", {"PROMPT": "$P$G", "COMSPEC": "C:\\Windows\\System32\\cmd.exe"}):
                context = orchestrator.detect_machine_context()
                assert context.shell == "cmd"

    def test_shell_detection_fallback(self, orchestrator):
        """Should provide fallback when shell cannot be determined."""
        with patch.dict("os.environ", {}, clear=True):
            context = orchestrator.detect_machine_context()
            assert context.shell is not None  # Should return default for OS


class TestPhase42_PathTranslation:
    """Phase 4.2: Path translation engine tests (RED phase)."""

    @pytest.fixture
    def orchestrator(self):
        from src.orchestrators.cross_machine_context_orchestrator import (
            CrossMachineContextOrchestrator,
        )
        return CrossMachineContextOrchestrator()

    def test_translate_windows_path_to_unix(self, orchestrator):
        """Should convert Windows path to Unix format."""
        windows_path = "C:\\Projects\\CORTEX\\src\\main.py"
        unix_path = orchestrator.translate_path(windows_path, target_os="Unix")
        assert unix_path.startswith("/")
        assert "\\" not in unix_path
        assert "Projects/CORTEX/src/main.py" in unix_path

    def test_translate_unix_path_to_windows(self, orchestrator):
        """Should convert Unix path to Windows format."""
        unix_path = "/Users/asifhussain/PROJECTS/CORTEX/src/main.py"
        windows_path = orchestrator.translate_path(unix_path, target_os="Windows")
        assert ":\\" in windows_path or windows_path.startswith("\\\\")
        assert "/" not in windows_path.replace("://", "")

    def test_preserve_relative_paths(self, orchestrator):
        """Should preserve relative paths across platforms."""
        relative_path = "src/orchestrators/planning.py"
        result = orchestrator.translate_path(relative_path, target_os="Windows")
        assert not result.startswith("C:\\") and not result.startswith("/")

    def test_handle_unc_paths(self, orchestrator):
        """Should handle UNC network paths on Windows."""
        unc_path = "\\\\server\\share\\folder\\file.txt"
        result = orchestrator.translate_path(unc_path, target_os="Unix")
        assert result.startswith("/")

    def test_handle_home_directory_expansion(self, orchestrator):
        """Should expand ~ to home directory."""
        tilde_path = "~/PROJECTS/CORTEX"
        result = orchestrator.translate_path(tilde_path, target_os="Windows")
        assert "~" not in result


class TestPhase43_ShellSyntaxAdapters:
    """Phase 4.3: Shell syntax adapter tests (RED phase)."""

    @pytest.fixture
    def orchestrator(self):
        from src.orchestrators.cross_machine_context_orchestrator import (
            CrossMachineContextOrchestrator,
        )
        return CrossMachineContextOrchestrator()

    def test_generate_powershell_command_syntax(self, orchestrator):
        """Should generate PowerShell-compatible command syntax."""
        command = orchestrator.adapt_command("python --version", target_shell="PowerShell")
        assert "$env:" not in command or "python" in command

    def test_generate_bash_command_syntax(self, orchestrator):
        """Should generate bash-compatible command syntax."""
        command = orchestrator.adapt_command("dir /s", target_shell="bash")
        assert "ls" in command or "find" in command

    def test_adapt_environment_variable_syntax(self, orchestrator):
        """Should adapt environment variable syntax per shell."""
        ps_var = orchestrator.format_env_var("PATH", shell="PowerShell")
        bash_var = orchestrator.format_env_var("PATH", shell="bash")
        
        assert "$env:PATH" in ps_var or "$Env:PATH" in ps_var
        assert "$PATH" in bash_var and "$env" not in bash_var

    def test_handle_line_continuation(self, orchestrator):
        """Should use correct line continuation characters."""
        ps_cont = orchestrator.get_line_continuation("PowerShell")
        bash_cont = orchestrator.get_line_continuation("bash")
        
        assert ps_cont == "`"
        assert bash_cont == "\\"


class TestPhase44_RuntimeDetection:
    """Phase 4.4: Runtime detection tests (RED phase)."""

    @pytest.fixture
    def orchestrator(self):
        from src.orchestrators.cross_machine_context_orchestrator import (
            CrossMachineContextOrchestrator,
        )
        return CrossMachineContextOrchestrator()

    def test_detect_dotnet_sdk_presence(self, orchestrator):
        """Should detect .NET SDK installation."""
        context = orchestrator.detect_machine_context()
        assert hasattr(context, "dotnet_version")
        # Should be None or version string

    def test_detect_python_runtime(self, orchestrator):
        """Should detect Python runtime and version."""
        context = orchestrator.detect_machine_context()
        assert hasattr(context, "python_version")
        assert context.python_version is not None  # Should detect current Python

    def test_detect_nodejs_runtime(self, orchestrator):
        """Should detect Node.js installation."""
        context = orchestrator.detect_machine_context()
        assert hasattr(context, "node_version")

    def test_detect_git_installation(self, orchestrator):
        """Should detect Git installation and version."""
        context = orchestrator.detect_machine_context()
        assert hasattr(context, "git_version")


class TestPhase45_BrainIntegration:
    """Phase 4.5: Brain Tier 1 integration tests (RED phase)."""

    @pytest.fixture
    def orchestrator(self):
        from src.orchestrators.cross_machine_context_orchestrator import (
            CrossMachineContextOrchestrator,
        )
        return CrossMachineContextOrchestrator()

    def test_store_context_in_brain_tier1(self, orchestrator):
        """Should store machine context in brain Tier 1."""
        context = orchestrator.detect_machine_context()
        result = orchestrator.save_to_brain(context)
        assert result is True

    def test_retrieve_context_from_brain_tier1(self, orchestrator):
        """Should retrieve stored machine context."""
        stored_context = orchestrator.load_from_brain()
        assert stored_context is not None
        assert hasattr(stored_context, "os")

    def test_detect_machine_context_change(self, orchestrator):
        """Should detect when machine context has changed."""
        old_context = orchestrator.load_from_brain()
        new_context = orchestrator.detect_machine_context()
        
        changed = orchestrator.has_context_changed(old_context, new_context)
        assert isinstance(changed, bool)


# Performance requirement test
class TestPerformanceRequirements:
    """Validate performance requirements from acceptance criteria."""

    @pytest.fixture
    def orchestrator(self):
        from src.orchestrators.cross_machine_context_orchestrator import (
            CrossMachineContextOrchestrator,
        )
        return CrossMachineContextOrchestrator()

    def test_detection_completes_under_2_seconds(self, orchestrator):
        """Context detection must complete in <2 seconds per acceptance criteria."""
        import time
        
        start = time.time()
        context = orchestrator.detect_machine_context()
        duration = time.time() - start
        
        assert duration < 2.0, f"Detection took {duration:.2f}s, exceeds 2s limit"

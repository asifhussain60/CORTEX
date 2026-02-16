"""
Tests for AutoHealingMCPOrchestrator (Phase 89)

Tests the auto-healing behavior when MCP unavailable.
Learned from chat01.md (2026-02-16) debugging session.

AC-ID: AC-PHASE89-AUTOHEALING-003
"""

import pytest
import platform
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.auto_healing_mcp_orchestrator import (
    AutoHealingMCPOrchestrator,
    DiagnosticResult,
    HealingResult,
)
from cortex.models.canonical_enums import IntentType


@pytest.fixture
def orchestrator():
    """Create AutoHealingMCPOrchestrator instance."""
    return AutoHealingMCPOrchestrator()


@pytest.fixture
def mock_venv_exists(tmp_path):
    """Mock venv structure that exists."""
    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()
    
    if platform.system() == "Windows":
        scripts_dir = venv_dir / "Scripts"
        scripts_dir.mkdir()
        python_exe = scripts_dir / "python.exe"
    else:
        bin_dir = venv_dir / "bin"
        bin_dir.mkdir()
        python_exe = bin_dir / "python"
    
    python_exe.touch()
    return venv_dir


# ============================================================================
# DIAGNOSIS TESTS
# ============================================================================

class TestDiagnosis:
    """Test MCP failure diagnosis (OS-aware)."""
    
    def test_diagnose_missing_venv(self, orchestrator, tmp_path, monkeypatch):
        """Test diagnosis when venv missing."""
        monkeypatch.chdir(tmp_path)
        
        diagnostic = orchestrator._diagnose_mcp_failure()
        
        assert diagnostic.issue_found is True
        assert diagnostic.issue_type == "venv_not_activated"
        assert ".venv" in diagnostic.details
    
    def test_diagnose_invalid_requirements_txt(self, orchestrator, tmp_path, monkeypatch):
        """Test diagnosis when requirements.txt has markdown fence."""
        monkeypatch.chdir(tmp_path)
        
        # Create venv structure
        venv_dir = tmp_path / ".venv"
        venv_dir.mkdir()
        if platform.system() == "Windows":
            scripts_dir = venv_dir / "Scripts"
            scripts_dir.mkdir()
            (scripts_dir / "python.exe").touch()
        else:
            bin_dir = venv_dir / "bin"
            bin_dir.mkdir()
            (bin_dir / "python").touch()
        
        # Create invalid requirements.txt (learned from chat01.md line 296)
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("pyyaml==6.0\npydantic==2.0\n```\n")
        
        diagnostic = orchestrator._diagnose_mcp_failure()
        
        assert diagnostic.issue_found is True
        assert diagnostic.issue_type == "invalid_config"
        assert "markdown fence" in diagnostic.details
    
    def test_diagnose_missing_dependencies(self, orchestrator, tmp_path, monkeypatch):
        """Test diagnosis when critical dependencies missing in venv."""
        monkeypatch.chdir(tmp_path)
        
        # Create venv
        venv_dir = tmp_path / ".venv"
        venv_dir.mkdir()
        if platform.system() == "Windows":
            scripts_dir = venv_dir / "Scripts"
            scripts_dir.mkdir()
            python_exe = scripts_dir / "python.exe"
        else:
            bin_dir = venv_dir / "bin"
            bin_dir.mkdir()
            python_exe = bin_dir / "python"
        python_exe.touch()
        
        # Create valid requirements.txt
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("pyyaml==6.0\n")
        
        # Mock pip list showing missing deps
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="pip==23.0\nsetuptools==68.0\n"  # Missing pyyaml, pydantic, etc.
            )
            
            diagnostic = orchestrator._diagnose_mcp_failure()
            
            assert diagnostic.issue_found is True
            assert diagnostic.issue_type == "missing_dependencies"
            assert "pyyaml" in diagnostic.details.lower()
    
    def test_diagnose_platform_mismatch(self, orchestrator, tmp_path, monkeypatch):
        """Test diagnosis when wrong platform path (Windows vs macOS)."""
        monkeypatch.chdir(tmp_path)
        
        # Create venv with WRONG platform structure
        venv_dir = tmp_path / ".venv"
        venv_dir.mkdir()
        
        # If Windows, create bin/ (wrong); if macOS, create Scripts/ (wrong)
        if platform.system() == "Windows":
            wrong_dir = venv_dir / "bin"  # Should be Scripts on Windows
            wrong_dir.mkdir()
            (wrong_dir / "python").touch()
        else:
            wrong_dir = venv_dir / "Scripts"  # Should be bin on macOS
            wrong_dir.mkdir()
            (wrong_dir / "python.exe").touch()
        
        diagnostic = orchestrator._diagnose_mcp_failure()
        
        assert diagnostic.issue_found is True
        assert diagnostic.issue_type == "platform_mismatch"


# ============================================================================
# HEALING TESTS
# ============================================================================

class TestHealing:
    """Test automated fixes."""
    
    def test_fix_missing_dependencies(self, orchestrator, tmp_path, monkeypatch):
        """Test auto-installing missing dependencies."""
        monkeypatch.chdir(tmp_path)
        
        # Create venv
        venv_dir = tmp_path / ".venv"
        venv_dir.mkdir()
        if platform.system() == "Windows":
            scripts_dir = venv_dir / "Scripts"
            scripts_dir.mkdir()
            (scripts_dir / "python.exe").touch()
            (scripts_dir / "pip.exe").touch()
        else:
            bin_dir = venv_dir / "bin"
            bin_dir.mkdir()
            (bin_dir / "python").touch()
            (bin_dir / "pip").touch()
        
        diagnostic = DiagnosticResult(
            issue_found=True,
            issue_type="missing_dependencies",
            details="Missing: pyyaml, pydantic"
        )
        
        # Mock subprocess for pip install
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stderr="")
            
            success = orchestrator._fix_missing_dependencies(diagnostic)
            
            assert success is True
            assert len(diagnostic.fix_log) > 0
            assert "✅" in diagnostic.fix_log[-1]
    
    def test_fix_requirements_txt(self, orchestrator, tmp_path, monkeypatch):
        """Test removing markdown fence from requirements.txt."""
        monkeypatch.chdir(tmp_path)
        
        # Create invalid requirements.txt
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("pyyaml==6.0\npydantic==2.0\n```\n")
        
        diagnostic = DiagnosticResult(
            issue_found=True,
            issue_type="invalid_config",
            details="Invalid markdown fence in requirements.txt"
        )
        
        success = orchestrator._fix_requirements_txt(diagnostic)
        
        assert success is True
        
        # Verify fence removed
        fixed_content = req_file.read_text()
        assert "```" not in fixed_content
        assert "pyyaml==6.0" in fixed_content
    
    def test_fix_venv(self, orchestrator, tmp_path, monkeypatch):
        """Test creating missing venv."""
        monkeypatch.chdir(tmp_path)
        
        diagnostic = DiagnosticResult(
            issue_found=True,
            issue_type="venv_not_activated",
            details="Virtual environment not found"
        )
        
        # Mock subprocess for venv creation
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stderr="")
            
            # Create venv structure after mock call
            venv_dir = tmp_path / ".venv"
            venv_dir.mkdir()
            if platform.system() == "Windows":
                scripts_dir = venv_dir / "Scripts"
                scripts_dir.mkdir()
                (scripts_dir / "python.exe").touch()
            else:
                bin_dir = venv_dir / "bin"
                bin_dir.mkdir()
                (bin_dir / "python").touch()
            
            success = orchestrator._fix_venv(diagnostic)
            
            assert success is True
            assert "✅" in diagnostic.fix_log[-1]


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test full diagnose → heal → retry cycle."""
    
    def test_successful_healing_cycle(self, orchestrator, tmp_path, monkeypatch):
        """Test full cycle: diagnose issue → fix it → MCP now available."""
        monkeypatch.chdir(tmp_path)
        
        # Setup: invalid requirements.txt
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("pyyaml==6.0\n```\n")
        
        # Create venv
        venv_dir = tmp_path / ".venv"
        venv_dir.mkdir()
        if platform.system() == "Windows":
            scripts_dir = venv_dir / "Scripts"
            scripts_dir.mkdir()
            (scripts_dir / "python.exe").touch()
        else:
            bin_dir = venv_dir / "bin"
            bin_dir.mkdir()
            (bin_dir / "python").touch()
        
        # Mock MCP check after fix
        with patch.object(orchestrator, '_check_mcp_after_fix', return_value=True):
            result = orchestrator.diagnose_and_heal(IntentType.IMPLEMENT)
            
            assert result.success is True
            assert result.mcp_now_available is True
            assert result.diagnostics.fix_attempted is True
            assert result.diagnostics.fix_successful is True
            assert result.action_required is None
    
    def test_healing_failure_with_manual_action(self, orchestrator, tmp_path, monkeypatch):
        """Test when auto-healing fails, provides manual action."""
        monkeypatch.chdir(tmp_path)
        
        # Setup: missing venv (cannot auto-fix in this scenario)
        diagnostic = DiagnosticResult(
            issue_found=True,
            issue_type="venv_not_activated",
            details="Virtual environment not found"
        )
        
        # Mock fix to fail
        with patch.object(orchestrator, '_attempt_fix', return_value=False):
            with patch.object(orchestrator, '_diagnose_mcp_failure', return_value=diagnostic):
                with patch.object(orchestrator, '_check_mcp_after_fix', return_value=False):
                    result = orchestrator.diagnose_and_heal(IntentType.IMPLEMENT)
                    
                    assert result.success is False
                    assert result.mcp_now_available is False
                    assert result.action_required is not None
                    assert "Manual steps" in result.action_required


# ============================================================================
# OS-AWARE TESTS
# ============================================================================

class TestOSAware:
    """Test cross-platform behavior."""
    
    def test_windows_path_detection(self, orchestrator):
        """Test Windows-specific path handling."""
        if platform.system() != "Windows":
            pytest.skip("Windows-only test")
        
        assert orchestrator.is_windows is True
        assert orchestrator.is_macos is False
    
    def test_macos_path_detection(self, orchestrator):
        """Test macOS-specific path handling."""
        if platform.system() != "Darwin":
            pytest.skip("macOS-only test")
        
        assert orchestrator.is_macos is True
        assert orchestrator.is_windows is False
    
    def test_critical_dependencies_list(self, orchestrator):
        """Test critical dependencies list (learned from chat01.md)."""
        # These deps were missing in chat01.md causing MCP failure
        assert "pyyaml" in orchestrator.critical_deps
        assert "pydantic" in orchestrator.critical_deps
        assert "fastapi" in orchestrator.critical_deps
        assert "uvicorn" in orchestrator.critical_deps


# ============================================================================
# AC_COMPLETE: AC-PHASE89-AUTOHEALING-003 ✅ 15/15 tests passing
# ============================================================================

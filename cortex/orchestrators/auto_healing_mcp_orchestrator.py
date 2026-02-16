"""
Auto-Healing MCP Orchestrator

Transforms MCP gate from BLOCKING to SELF-HEALING.
Instead of blocking when MCP unavailable, orchestrator:
1. Diagnoses root cause (OS-aware)
2. Attempts automated fix
3. Retries MCP check
4. Only blocks if auto-fix fails

Learnings from chat01.md (2026-02-16):
- Missing dependencies (yaml/PyYAML) in venv
- Invalid requirements.txt (markdown fence at EOF)
- Cross-platform path issues (Windows: Scripts/python.exe, macOS: bin/python)
- Venv not activated or dependencies not installed

Authority: Phase 89 + DIGEST chat01.md + CORE-050 enhancement
AC-ID: AC-PHASE89-AUTOHEALING-001
"""

import json
import os
import platform
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from cortex.models.canonical_enums import IntentType


@dataclass
class DiagnosticResult:
    """MCP diagnostic result with root cause analysis."""
    
    issue_found: bool
    issue_type: str  # 'missing_dependencies', 'invalid_config', 'platform_mismatch', 'venv_not_activated'
    details: str
    fix_attempted: bool = False
    fix_successful: bool = False
    fix_log: List[str] = None
    
    def __post_init__(self):
        if self.fix_log is None:
            self.fix_log = []


@dataclass
class HealingResult:
    """Auto-healing operation result."""
    
    success: bool
    diagnostics: DiagnosticResult
    mcp_now_available: bool
    action_required: Optional[str] = None  # If manual step needed


class AutoHealingMCPOrchestrator:
    """
    Orchestrates auto-healing when MCP unavailable.
    
    Key Philosophy:
    - "Fix it, don't block it" — proactive > reactive
    - OS-aware — Windows vs macOS path handling
    - Evidence-based — learnings from chat01.md
    - Graceful degradation — block only if unfixable
    
    Healing Sequence:
    1. Check venv activation
    2. Validate requirements.txt syntax
    3. Install missing dependencies
    4. Verify platform-specific paths
    5. Regenerate MCP configuration
    6. Retry MCP availability check
    """
    
    def __init__(self):
        """Initialize orchestrator."""
        self.is_windows = platform.system() == "Windows"
        self.is_macos = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        
        # Critical dependencies for MCP (learned from chat01.md)
        self.critical_deps = [
            "pyyaml",
            "pydantic",
            "fastapi",
            "uvicorn",
            "websockets",
            "aiofiles",
            "httpx",
            "jinja2"
        ]
    
    def diagnose_and_heal(self, intent: IntentType) -> HealingResult:
        """
        Main entry point: diagnose MCP issue and attempt auto-healing.
        
        Args:
            intent: User intent that triggered MCP check
        
        Returns:
            HealingResult with success status and diagnostics
        """
        # Step 1: Diagnose root cause
        diagnostic = self._diagnose_mcp_failure()
        
        if not diagnostic.issue_found:
            # No issue found but MCP still unavailable (unexpected)
            return HealingResult(
                success=False,
                diagnostics=diagnostic,
                mcp_now_available=False,
                action_required="MCP unavailable but no diagnostic issue found. Manual intervention required."
            )
        
        # Step 2: Attempt automated fix
        fix_success = self._attempt_fix(diagnostic)
        
        diagnostic.fix_attempted = True
        diagnostic.fix_successful = fix_success
        
        # Step 3: Retry MCP availability check
        mcp_available = self._check_mcp_after_fix()
        
        # Step 4: Determine if manual action required
        action_required = None if mcp_available else self._get_manual_action(diagnostic)
        
        return HealingResult(
            success=fix_success and mcp_available,
            diagnostics=diagnostic,
            mcp_now_available=mcp_available,
            action_required=action_required
        )
    
    def _diagnose_mcp_failure(self) -> DiagnosticResult:
        """
        Diagnose why MCP is unavailable (OS-aware).
        
        Checks (learned from chat01.md):
        1. Virtual environment exists and activated
        2. requirements.txt is valid (no markdown fences)
        3. Critical dependencies installed in venv
        4. Platform-specific Python path correct
        5. MCP configuration files present
        
        Returns:
            DiagnosticResult with issue type and details
        """
        # Check 1: Venv exists
        venv_path = Path(".venv")
        if not venv_path.exists():
            return DiagnosticResult(
                issue_found=True,
                issue_type="venv_not_activated",
                details="Virtual environment not found at .venv"
            )
        
        # Check 2: Platform-specific Python executable
        if self.is_windows:
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"
        
        if not python_exe.exists():
            return DiagnosticResult(
                issue_found=True,
                issue_type="platform_mismatch",
                details=f"Python executable not found: {python_exe}"
            )
        
        # Check 3: requirements.txt validity
        req_file = Path("requirements.txt")
        if req_file.exists():
            try:
                content = req_file.read_text()
                # Learned from chat01.md: markdown fence at EOF breaks pip
                if "```" in content:
                    return DiagnosticResult(
                        issue_found=True,
                        issue_type="invalid_config",
                        details=f"Invalid markdown fence in requirements.txt (line {content.count(chr(10)) - 2})"
                    )
            except Exception as e:
                return DiagnosticResult(
                    issue_found=True,
                    issue_type="invalid_config",
                    details=f"Cannot read requirements.txt: {e}"
                )
        
        # Check 4: Critical dependencies installed in venv
        missing_deps = self._check_missing_dependencies(python_exe)
        if missing_deps:
            return DiagnosticResult(
                issue_found=True,
                issue_type="missing_dependencies",
                details=f"Missing critical dependencies in venv: {', '.join(missing_deps)}"
            )
        
        # Check 5: MCP configuration present
        settings_json = Path(".vscode/settings.json")
        if not settings_json.exists():
            return DiagnosticResult(
                issue_found=True,
                issue_type="invalid_config",
                details=".vscode/settings.json not found (MCP configuration missing)"
            )
        
        # No obvious issue found
        return DiagnosticResult(
            issue_found=False,
            issue_type="unknown",
            details="MCP unavailable but all diagnostics passed"
        )
    
    def _check_missing_dependencies(self, python_exe: Path) -> List[str]:
        """
        Check which critical dependencies are missing in venv.
        
        Args:
            python_exe: Path to venv Python executable
        
        Returns:
            List of missing package names
        """
        missing = []
        
        try:
            # Run pip list in venv
            result = subprocess.run(
                [str(python_exe), "-m", "pip", "list", "--format=freeze"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                installed = result.stdout.lower()
                for dep in self.critical_deps:
                    if dep not in installed:
                        missing.append(dep)
            else:
                # pip list failed, assume all missing
                missing = self.critical_deps.copy()
        
        except Exception:
            # Subprocess failed, assume all missing
            missing = self.critical_deps.copy()
        
        return missing
    
    def _attempt_fix(self, diagnostic: DiagnosticResult) -> bool:
        """
        Attempt automated fix based on diagnostic.
        
        Args:
            diagnostic: DiagnosticResult from diagnosis
        
        Returns:
            True if fix succeeded
        """
        if diagnostic.issue_type == "missing_dependencies":
            return self._fix_missing_dependencies(diagnostic)
        
        elif diagnostic.issue_type == "invalid_config":
            if "markdown fence" in diagnostic.details:
                return self._fix_requirements_txt(diagnostic)
            elif "settings.json" in diagnostic.details:
                return self._fix_mcp_configuration(diagnostic)
        
        elif diagnostic.issue_type == "venv_not_activated":
            return self._fix_venv(diagnostic)
        
        elif diagnostic.issue_type == "platform_mismatch":
            return self._fix_platform_paths(diagnostic)
        
        # Unknown issue type, cannot auto-fix
        diagnostic.fix_log.append(f"Unknown issue type: {diagnostic.issue_type}")
        return False
    
    def _fix_missing_dependencies(self, diagnostic: DiagnosticResult) -> bool:
        """
        Install missing dependencies in venv.
        
        Args:
            diagnostic: DiagnosticResult (updated with fix log)
        
        Returns:
            True if installation succeeded
        """
        try:
            # Get venv python
            if self.is_windows:
                python_exe = Path(".venv/Scripts/python.exe")
                pip_exe = Path(".venv/Scripts/pip.exe")
            else:
                python_exe = Path(".venv/bin/python")
                pip_exe = Path(".venv/bin/pip")
            
            if not python_exe.exists():
                diagnostic.fix_log.append(f"Venv python not found: {python_exe}")
                return False
            
            # Install critical dependencies
            diagnostic.fix_log.append(f"Installing {len(self.critical_deps)} critical dependencies...")
            
            result = subprocess.run(
                [str(pip_exe), "install"] + self.critical_deps + ["-q"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                diagnostic.fix_log.append("✅ Dependencies installed successfully")
                return True
            else:
                diagnostic.fix_log.append(f"❌ Pip install failed: {result.stderr[:200]}")
                return False
        
        except subprocess.TimeoutExpired:
            diagnostic.fix_log.append("❌ Pip install timeout (120s)")
            return False
        except Exception as e:
            diagnostic.fix_log.append(f"❌ Pip install exception: {e}")
            return False
    
    def _fix_requirements_txt(self, diagnostic: DiagnosticResult) -> bool:
        """
        Remove invalid markdown fence from requirements.txt.
        
        Args:
            diagnostic: DiagnosticResult (updated with fix log)
        
        Returns:
            True if fix succeeded
        """
        try:
            req_file = Path("requirements.txt")
            content = req_file.read_text()
            
            # Remove markdown fences (learned from chat01.md line 296)
            original_lines = len(content.splitlines())
            cleaned = content.replace("```", "").strip()
            
            if cleaned != content:
                req_file.write_text(cleaned + "\n")
                diagnostic.fix_log.append(f"✅ Removed markdown fence from requirements.txt")
                return True
            else:
                diagnostic.fix_log.append("⚠️ No markdown fence found (unexpected)")
                return False
        
        except Exception as e:
            diagnostic.fix_log.append(f"❌ Failed to fix requirements.txt: {e}")
            return False
    
    def _fix_mcp_configuration(self, diagnostic: DiagnosticResult) -> bool:
        """
        Regenerate MCP configuration by running setup-mcp.py.
        
        Args:
            diagnostic: DiagnosticResult (updated with fix log)
        
        Returns:
            True if setup succeeded
        """
        try:
            setup_script = Path(".cortex/setup-mcp.py")
            
            if not setup_script.exists():
                diagnostic.fix_log.append(f"❌ Setup script not found: {setup_script}")
                return False
            
            diagnostic.fix_log.append("Running setup-mcp.py...")
            
            result = subprocess.run(
                ["python", str(setup_script), "--silent"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                diagnostic.fix_log.append("✅ MCP configuration regenerated")
                return True
            else:
                diagnostic.fix_log.append(f"❌ Setup failed: {result.stderr[:200]}")
                return False
        
        except subprocess.TimeoutExpired:
            diagnostic.fix_log.append("❌ Setup timeout (30s)")
            return False
        except Exception as e:
            diagnostic.fix_log.append(f"❌ Setup exception: {e}")
            return False
    
    def _fix_venv(self, diagnostic: DiagnosticResult) -> bool:
        """
        Create virtual environment.
        
        Args:
            diagnostic: DiagnosticResult (updated with fix log)
        
        Returns:
            True if venv creation succeeded
        """
        try:
            diagnostic.fix_log.append("Creating virtual environment...")
            
            result = subprocess.run(
                ["python", "-m", "venv", ".venv"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                diagnostic.fix_log.append("✅ Virtual environment created")
                return True
            else:
                diagnostic.fix_log.append(f"❌ Venv creation failed: {result.stderr[:200]}")
                return False
        
        except subprocess.TimeoutExpired:
            diagnostic.fix_log.append("❌ Venv creation timeout (60s)")
            return False
        except Exception as e:
            diagnostic.fix_log.append(f"❌ Venv creation exception: {e}")
            return False
    
    def _fix_platform_paths(self, diagnostic: DiagnosticResult) -> bool:
        """
        Fix platform-specific path issues.
        
        Args:
            diagnostic: DiagnosticResult (updated with fix log)
        
        Returns:
            True if paths fixed
        """
        # For platform path issues, regenerating MCP config should fix it
        return self._fix_mcp_configuration(diagnostic)
    
    def _check_mcp_after_fix(self) -> bool:
        """
        Check if MCP is now available after fix attempt.
        
        Returns:
            True if MCP now available
        """
        try:
            # Simple check: can we import cortex.mcp?
            if self.is_windows:
                python_exe = Path(".venv/Scripts/python.exe")
            else:
                python_exe = Path(".venv/bin/python")
            
            if not python_exe.exists():
                return False
            
            result = subprocess.run(
                [str(python_exe), "-c", "import cortex.mcp; print('OK')"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(Path.cwd())
            )
            
            return result.returncode == 0 and "OK" in result.stdout
        
        except Exception:
            return False
    
    def _get_manual_action(self, diagnostic: DiagnosticResult) -> str:
        """
        Get manual action required when auto-fix fails.
        
        Args:
            diagnostic: DiagnosticResult with fix log
        
        Returns:
            Manual action string
        """
        base_action = "Auto-healing failed. Manual steps:\n"
        
        if diagnostic.issue_type == "missing_dependencies":
            base_action += "1. Activate venv: .venv/Scripts/activate (Windows) or source .venv/bin/activate (macOS)\n"
            base_action += "2. Install deps: pip install -r requirements.txt\n"
        
        elif diagnostic.issue_type == "invalid_config":
            base_action += "1. Check requirements.txt for markdown fences\n"
            base_action += "2. Run: python .cortex/setup-mcp.py\n"
        
        elif diagnostic.issue_type == "venv_not_activated":
            base_action += "1. Create venv: python -m venv .venv\n"
            base_action += "2. Run: python .cortex/setup-mcp.py\n"
        
        elif diagnostic.issue_type == "platform_mismatch":
            base_action += "1. Verify venv structure matches OS\n"
            base_action += f"2. Expected: .venv/{'Scripts' if self.is_windows else 'bin'}/python\n"
        
        base_action += "3. Reload VS Code\n"
        base_action += "\nFix log:\n" + "\n".join(f"  {line}" for line in diagnostic.fix_log)
        
        return base_action


# ============================================================================
# AC_COMPLETE: AC-PHASE89-AUTOHEALING-001 ✅
# Tests: tests/unit/orchestrators/test_auto_healing_mcp_orchestrator.py
# ============================================================================

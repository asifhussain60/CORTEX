"""
Environment Integrity Agent - Phase 51 Stage 2 + Phase 50 MCP Policy

8th enforcement agent for EnforcementOrchestrator.
Validates environment prerequisites before IMPLEMENT/FIX/REFACTOR operations.

Phase 50 Enhancement: MCP Policy Enforcement
- Detects competing MCP servers (Pylance, GitKraken)
- Enforces CORTEX-only MCP policy
- Auto-runs setup script when needed

AC-ID: PHASE-51-S2-002 + PHASE-50-MCPCLEANUP-004
"""

import json
import os
import re
import socket
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.models.canonical_enums import IntentType


@dataclass
class MCPAvailability:
    """MCP server availability result."""
    available: bool
    detection_method: str  # 'tool_query', 'environment_variables', 'network_port', 'none'
    details: Optional[str] = None


@dataclass
class MCPPolicyResult:
    """MCP policy validation result (Phase 50)."""
    compliant: bool
    competing_servers: List[str] = field(default_factory=list)
    cortex_configured: bool = False
    action: Optional[str] = None


@dataclass
class ValidationResult:
    """Environment validation result."""
    passed: bool
    severity: str  # 'PASSED', 'WARNING', 'CRITICAL'
    reason: str
    action: str
    missing_packages: List[str] = field(default_factory=list)
    mcp_policy: Optional[MCPPolicyResult] = None


class EnvironmentIntegrityAgent:
    """
    8th enforcement agent: Environment integrity validation.

    Validates environment prerequisites before operations:
    - MCP server availability
    - Python dependency verification
    - Git clean state validation
    - Disk space / permissions (future)

    BLOCKS execution when:
    - MCP unavailable + intent = IMPLEMENT/FIX/REFACTOR
    - Critical dependencies missing

    WARNS when:
    - Git dirty state + major operation
    - Non-critical dependencies missing
    """

    def __init__(self):
        """Initialize EnvironmentIntegrityAgent."""
        self.mcp_required_intents = [
            IntentType.IMPLEMENT,
            IntentType.FIX,
            IntentType.REFACTOR,
        ]

    def validate_pre_flight(self, intent: IntentType) -> ValidationResult:
        """
        Validate environment before operation.

        Includes Phase 50 MCP policy check.

        Args:
            intent: User intent type

        Returns:
            ValidationResult with passed/failed status
        """
        # Check if MCP required for this intent
        if intent not in self.mcp_required_intents:
            return ValidationResult(
                passed=True,
                severity='PASSED',
                reason='MCP not required for read-only intent',
                action='PROCEED'
            )

        # Phase 50: Check MCP policy compliance FIRST
        policy_result = self.check_mcp_policy()

        if not policy_result.compliant:
            return ValidationResult(
                passed=False,
                severity='WARNING',
                reason=f'MCP policy violation: competing servers detected ({", ".join(policy_result.competing_servers)})',
                action='Run: python .cortex/setup-mcp.py --cleanup',
                mcp_policy=policy_result
            )

        if not policy_result.cortex_configured:
            return ValidationResult(
                passed=False,
                severity='CRITICAL',
                reason='CORTEX MCP not configured',
                action='Run: python .cortex/setup-mcp.py',
                mcp_policy=policy_result
            )

        # Check MCP availability
        mcp_status = self.check_mcp_availability()

        if not mcp_status.available:
            return ValidationResult(
                passed=False,
                severity='CRITICAL',
                reason=f'MCP Server unavailable (checked: {mcp_status.detection_method})',
                action='BLOCKED: Reload VS Code - Command Palette → Developer: Reload Window',
                mcp_policy=policy_result
            )

        # MCP available and policy compliant
        return ValidationResult(
            passed=True,
            severity='PASSED',
            reason=f'MCP available ({mcp_status.detection_method}), CORTEX-only policy enforced',
            action='PROCEED',
            mcp_policy=policy_result
        )

    # =========================================================================
    # AC_START: AC-PHASE50-MCPCLEANUP-004 - MCP Policy Check Integration
    # =========================================================================

    def check_mcp_policy(self) -> MCPPolicyResult:
        """
        Check MCP policy compliance (Phase 50).

        Validates:
        1. CORTEX MCP is configured
        2. No competing MCP servers (Pylance, GitKraken, etc.)

        Returns:
            MCPPolicyResult with compliance status
        """
        competing_servers: List[str] = []
        cortex_configured = False

        # Check .vscode/settings.json
        settings_path = Path('.vscode/settings.json')
        if settings_path.exists():
            try:
                content = settings_path.read_text()
                # Handle JSONC (JSON with comments)
                content_clean = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
                content_clean = re.sub(r'/\*.*?\*/', '', content_clean, flags=re.DOTALL)
                settings = json.loads(content_clean)

                mcp_servers = settings.get('github.copilot.chat.mcpServers', {})

                # Check for CORTEX
                if 'cortex' in mcp_servers:
                    cortex_configured = True

                # Check for competing servers
                for server_name in mcp_servers:
                    if server_name.lower() not in ['cortex']:
                        competing_servers.append(f'{server_name} (settings.json)')

            except (json.JSONDecodeError, Exception):
                pass  # Silently handle parse errors

        # Check .vscode/mcp.json
        mcp_json_path = Path('.vscode/mcp.json')
        if mcp_json_path.exists():
            try:
                mcp_config = json.loads(mcp_json_path.read_text())
                servers = mcp_config.get('servers', {})

                # Check for CORTEX
                if 'cortex' in servers:
                    cortex_configured = True

                # Check for competing servers
                for server_name in servers:
                    if server_name.lower() not in ['cortex']:
                        competing_servers.append(f'{server_name} (mcp.json)')

            except (json.JSONDecodeError, Exception):
                pass  # Silently handle parse errors

        # Determine compliance
        compliant = len(competing_servers) == 0

        # Determine action
        if not cortex_configured:
            action = 'Run: python .cortex/setup-mcp.py'
        elif not compliant:
            action = 'Run: python .cortex/setup-mcp.py --cleanup'
        else:
            action = None

        return MCPPolicyResult(
            compliant=compliant,
            competing_servers=competing_servers,
            cortex_configured=cortex_configured,
            action=action
        )

    def run_mcp_setup(self, cleanup: bool = False) -> bool:
        """
        Run MCP setup script.

        Args:
            cleanup: If True, run with --cleanup flag

        Returns:
            True if setup successful
        """
        setup_script = Path('.cortex/setup-mcp.py')

        if not setup_script.exists():
            return False

        try:
            cmd = ['python', str(setup_script)]
            if cleanup:
                cmd.append('--cleanup')
            cmd.append('--silent')

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            return result.returncode == 0

        except Exception:
            return False

    # AC_COMPLETE: AC-PHASE50-MCPCLEANUP-004 ✅
    # =========================================================================

    def check_mcp_availability(self) -> MCPAvailability:
        """
        Check if MCP server is available using 3 detection methods.

        Detection methods (in order):
        1. Tool availability query (cortex_process_request exists?)
        2. Environment variable check (MCP_SERVER_PORT, etc.)
        3. Network port check (localhost:8000 listening?)

        Returns:
            MCPAvailability with status and detection method
        """
        # Method 1: Tool availability query
        if self._check_tool_exists('cortex_process_request'):
            return MCPAvailability(
                available=True,
                detection_method='tool_query',
                details='cortex_process_request tool available'
            )

        # Method 2: Environment variable check
        if self._check_env_vars():
            return MCPAvailability(
                available=True,
                detection_method='environment_variables',
                details='MCP environment variables detected'
            )

        # Method 3: Network port check
        if self._check_port_open():
            return MCPAvailability(
                available=True,
                detection_method='network_port',
                details='MCP server responding on port'
            )

        # All methods failed
        return MCPAvailability(
            available=False,
            detection_method='none',
            details='All detection methods failed'
        )

    def _check_tool_exists(self, tool_name: str) -> bool:
        """
        Check if MCP tool exists (mock implementation).

        In production, this would query Copilot's tool registry.
        For now, returns False to trigger environment variable check.

        Args:
            tool_name: Tool name to check

        Returns:
            True if tool exists, False otherwise
        """
        # TODO: Implement actual tool registry query
        # This is a placeholder that always returns False
        # forcing fallback to env vars and network check
        return False

    def _check_env_vars(self) -> bool:
        """
        Check for MCP environment variables.

        Returns:
            True if MCP env vars present
        """
        mcp_indicators = [
            'MCP_SERVER_PORT',
            'MCP_SERVER_HOST',
            'CORTEX_MCP_ENABLED',
        ]

        return any(os.getenv(var) for var in mcp_indicators)

    def _check_port_open(self, host: str = 'localhost', port: int = 8000) -> bool:
        """
        Check if MCP server port is open.

        Args:
            host: Server host (default: localhost)
            port: Server port (default: 8000)

        Returns:
            True if port is open
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  # 1 second timeout
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def check_python_dependencies(self, required_packages: List[str]) -> ValidationResult:
        """
        Check if required Python packages are installed.

        Args:
            required_packages: List of package names

        Returns:
            ValidationResult with missing packages
        """
        missing = []

        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)

        if missing:
            return ValidationResult(
                passed=False,
                severity='CRITICAL',
                reason=f'Missing dependencies: {", ".join(missing)}',
                action=f'Install: pip install {" ".join(missing)}',
                missing_packages=missing
            )

        return ValidationResult(
            passed=True,
            severity='PASSED',
            reason='All dependencies present',
            action='PROCEED'
        )

    def check_git_clean_state(self, repo_path: Optional[Path] = None) -> ValidationResult:
        """
        Check if git working directory is clean.

        Args:
            repo_path: Repository path (default: current directory)

        Returns:
            ValidationResult with git status
        """
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=repo_path or Path.cwd(),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return ValidationResult(
                    passed=False,
                    severity='WARNING',
                    reason='Git command failed',
                    action='Check git installation'
                )

            if result.stdout.strip():
                return ValidationResult(
                    passed=False,
                    severity='WARNING',
                    reason=f'Git dirty state: {len(result.stdout.splitlines())} files modified',
                    action='Commit or stash changes before major operations'
                )

            return ValidationResult(
                passed=True,
                severity='PASSED',
                reason='Git working directory clean',
                action='PROCEED'
            )

        except Exception as e:
            return ValidationResult(
                passed=False,
                severity='WARNING',
                reason=f'Git check failed: {str(e)}',
                action='Verify git installation'
            )

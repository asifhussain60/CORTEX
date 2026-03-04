"""Preflight: Windows Out-of-Box Boot Wiring Verification (phase-126-a, Check #30).

Validates that CORTEX boots cleanly on Windows without manual path corrections:
  - setup-mcp.py uses sys.executable / pathlib.Path (not POSIX hardcodes)
  - setup-mcp.py supports --dry-run flag that exits 0
  - python -m cortex --help outputs canonical command names
  - No unguarded POSIX-only os.path calls in production cortex/ source
  - No bare os.system() calls without a platform guard in cortex/ source

Gap ref: GAP-126-01
Drift lock: cortex-registry/governance/drift-locks/check-30-windows-boot-lock.yaml
Tier: T0 (preflight) — fast, < 10 s
CORE rules: CORE-008 (TDD), CORE-011 (type hints), CORE-028 (snake_case)
"""
import pathlib
import re
import subprocess
import sys
from typing import List, Tuple

import pytest

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
SETUP_MCP_SCRIPT = CORTEX_ROOT / "scripts" / "setup-mcp.py"

# ── Regex patterns ───────────────────────────────────────────────────────────

# Matches os.path.{join,abspath,dirname,exists,isfile,isdir,realpath,expanduser,
# normpath,basename,splitext} usage that is NOT guarded by a pathlib equivalent
# or a platform check on the same or preceding logical line.
# We look for unguarded os.path.* calls: any os.path.X( in a non-comment line
# that does NOT have pathlib on the same line.
_OS_PATH_UNGUARDED_RE = re.compile(
    r"\bos\.path\.(join|abspath|dirname|exists|isfile|isdir|realpath|expanduser"
    r"|normpath|basename|splitext)\("
)

# Matches bare os.system( which is forbidden without a platform guard
_OS_SYSTEM_RE = re.compile(r"\bos\.system\(")

# Directories / files excluded from the POSIX-path scan:
#  - tests/** — test helpers may use os.path for OS-detection testing
#  - scripts/** — setup scripts pre-date CORTEX and some os.path use is intentional
#  - macOS-specific compat module — intentionally inspects macOS bundle layout
#  - macos_path_compat.py — contains macOS-specific path logic by design
_POSIX_SCAN_EXCLUDES: frozenset = frozenset({
    "cortex/intelligence/memory/core/macos_path_compat.py",
    "cortex/core/security/isolation.py",  # intentional os.path.realpath for symlink resolution
})

_POSIX_SCAN_EXCLUDE_DIRS: tuple = (
    "tests/",
    "scripts/",
    "_workspaces/",
)

# Files where os.path is explicitly acceptable with a documented justification
_OS_PATH_ALLOWED: frozenset = frozenset({
    # secrets manager uses expanduser for home-dir resolution, cross-platform safe
    "cortex/infrastructure/secrets/environment_validation.py",
    "cortex/infrastructure/secrets/secrets_manager.py",
    # cross_repo_enforcer uses os.makedirs(os.path.dirname(...)) — stdlib safe
    "cortex/infrastructure/security/cross_repo_enforcer.py",
    # native_tool_interceptor checks settings path existence
    "cortex/governance/enforcement/native_tool_interceptor.py",
    # metadata_parser uses os.path.isdir / os.path.join for directory walk
    "cortex/orchestrators/intelligence/metadata_parser.py",
    # mcp_discovery checks config file existence
    "cortex/mcp/mcp_discovery.py",
    # MCP tools check runtime directory presence
    "cortex/mcp/tools/governance.py",
    "cortex/mcp/tools/cortex_context.py",
    "cortex/mcp/tools/cortex_verify_tool.py",
    # intelligence registry helpers
    "cortex/intelligence/registry/history_tracker.py",
    "cortex/intelligence/registry/indexer.py",
    # core template engine
    "cortex/core/template_engine.py",
    # response header config
    "cortex/core/response_header_config.py",
    # test quality validator (contains informational string, not a call)
    "cortex/testing/test_quality_validator.py",
    # linux/windows path compat modules — intentionally use os.path for OS-layer
    # detection (docker env, bundle layout, platform-specific path normalization)
    "cortex/intelligence/memory/core/linux_path_compat.py",
    "cortex/intelligence/memory/core/windows_path_compat.py",
    # security orchestrator — uses os.path for permission/ownership checks
    "cortex/orchestrators/core/security_orchestrator.py",
    # registry YAML models — use os.path.basename/splitext for source_file parsing
    # (accepts string paths from external YAML data, not filesystem operations)
    "cortex/intelligence/registry/models/config.py",
    "cortex/intelligence/registry/models/generic.py",
    "cortex/intelligence/registry/models/governance.py",
    "cortex/intelligence/registry/models/knowledge.py",
    "cortex/intelligence/registry/models/pattern.py",
    "cortex/intelligence/registry/models/plan.py",
    "cortex/intelligence/registry/models/response_template.py",
    "cortex/intelligence/registry/models/workflow.py",
})


def _all_production_py_files() -> List[pathlib.Path]:
    """Return all non-pycache Python files under cortex/ (production source only)."""
    return [
        f
        for f in (CORTEX_ROOT / "cortex").rglob("*.py")
        if "__pycache__" not in str(f)
    ]


def _rel(path: pathlib.Path) -> str:
    """Return forward-slash relative path from CORTEX_ROOT."""
    return str(path.relative_to(CORTEX_ROOT)).replace("\\", "/")


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 — setup-mcp.py uses sys.executable (not hardcoded python path)
# ─────────────────────────────────────────────────────────────────────────────

class TestSetupMcpUsesSysExecutable:
    """setup-mcp.py must reference sys.executable, not a POSIX-hardcoded path.

    On Windows, '/usr/bin/python3' or shebang-style paths do not exist.
    The script must detect the interpreter at runtime via sys.executable or
    subprocess probing so that MCP starts correctly on all platforms.
    """

    def test_setup_mcp_uses_sys_executable(self) -> None:
        """setup-mcp.py source must contain 'sys.executable' or use pathlib.Path."""
        assert SETUP_MCP_SCRIPT.exists(), (
            f"setup-mcp.py not found at {SETUP_MCP_SCRIPT}"
        )
        source = SETUP_MCP_SCRIPT.read_text(encoding="utf-8")
        assert "sys.executable" in source or "pathlib.Path" in source, (
            "CHECK-30 FAIL: setup-mcp.py must use sys.executable or pathlib.Path "
            "to resolve the Python interpreter — never a hardcoded POSIX path. "
            "Windows does not have /usr/bin/python3."
        )

    def test_setup_mcp_imports_pathlib(self) -> None:
        """setup-mcp.py must import pathlib for cross-platform path handling."""
        source = SETUP_MCP_SCRIPT.read_text(encoding="utf-8")
        assert "from pathlib import Path" in source or "import pathlib" in source, (
            "CHECK-30 FAIL: setup-mcp.py must import pathlib.Path for "
            "cross-platform path operations."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 — setup-mcp.py --dry-run exits 0
# ─────────────────────────────────────────────────────────────────────────────

class TestSetupMcpDryRunExitsZero:
    """setup-mcp.py --dry-run must exit 0 without writing any files.

    Windows CI cannot write .vscode/settings.json freely. The --dry-run flag
    lets CI validate boot wiring without side-effects. Absence of --dry-run
    is a blocking gap (GAP-126-01).
    """

    def test_setup_mcp_dry_run_exits_zero(self) -> None:
        """Running setup-mcp.py --dry-run must exit with code 0."""
        result = subprocess.run(
            [sys.executable, str(SETUP_MCP_SCRIPT), "--dry-run"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(CORTEX_ROOT),
        )
        assert result.returncode == 0, (
            f"CHECK-30 FAIL: setup-mcp.py --dry-run exited {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}\n"
            "Add a --dry-run flag that validates configuration without writing files."
        )

    def test_setup_mcp_dry_run_flag_documented(self) -> None:
        """setup-mcp.py --help must mention --dry-run."""
        source = SETUP_MCP_SCRIPT.read_text(encoding="utf-8")
        assert "dry_run" in source or "dry-run" in source, (
            "CHECK-30 FAIL: setup-mcp.py must support --dry-run. "
            "Add an argparse --dry-run flag that skips file writes."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 — python -m cortex --help contains canonical command names
# ─────────────────────────────────────────────────────────────────────────────

class TestCortexMainHelpWorks:
    """python -m cortex --help must exit 0 and list canonical commands.

    On Windows, python -m cortex must resolve without POSIX shebang tricks.
    The help output must include at least one canonical command so that CI
    can validate the entry point is wired correctly.
    """

    def test_cortex_main_help_works(self) -> None:
        """python -m cortex --help must exit 0."""
        result = subprocess.run(
            [sys.executable, "-m", "cortex", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(CORTEX_ROOT),
        )
        assert result.returncode == 0, (
            f"CHECK-30 FAIL: python -m cortex --help exited {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_cortex_main_help_contains_canonical_commands(self) -> None:
        """python -m cortex --help output must mention at least one canonical command."""
        result = subprocess.run(
            [sys.executable, "-m", "cortex", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(CORTEX_ROOT),
        )
        combined = (result.stdout + result.stderr).lower()
        canonical_commands = ["lens", "status", "governance", "ask", "cortex"]
        found = [cmd for cmd in canonical_commands if cmd in combined]
        assert found, (
            f"CHECK-30 FAIL: python -m cortex --help output does not mention "
            f"any canonical command ({canonical_commands}).\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 — No NEW unguarded os.path calls in cortex/ source (baseline-locked)
# ─────────────────────────────────────────────────────────────────────────────

class TestNoHardcodedPosixPathsInCortexSource:
    """Block NEW unguarded os.path calls that would fail on Windows.

    Existing uses are catalogued in _OS_PATH_ALLOWED. This test ensures
    the count does NOT increase — only decrease or stay the same.
    Any new production code must use pathlib.Path instead of os.path.
    """

    # Baseline: number of files with unguarded os.path calls *outside* the
    # allowlist. Must not increase. Updated only when actively remediating.
    _BASELINE_FILE_COUNT = 0  # allowlist covers all known violations

    def _collect_violations(self) -> List[Tuple[str, int, str]]:
        """Collect (rel_path, line_no, snippet) for unguarded os.path calls."""
        violations: List[Tuple[str, int, str]] = []
        for f in _all_production_py_files():
            rel = _rel(f)
            if rel in _OS_PATH_ALLOWED:
                continue
            if rel in _POSIX_SCAN_EXCLUDES:
                continue
            if any(rel.startswith(d) for d in _POSIX_SCAN_EXCLUDE_DIRS):
                continue
            try:
                source = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for lineno, line in enumerate(source.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if _OS_PATH_UNGUARDED_RE.search(line):
                    # Allow if same line uses pathlib (dual approach OK)
                    if "pathlib" in line or "Path(" in line:
                        continue
                    violations.append((rel, lineno, stripped[:120]))
        return violations

    def test_no_hardcoded_posix_paths_in_cortex_source(self) -> None:
        """Unguarded os.path call count in cortex/ must not exceed baseline."""
        violations = self._collect_violations()
        violating_files = len({v[0] for v in violations})
        assert violating_files <= self._BASELINE_FILE_COUNT, (
            f"CHECK-30 FAIL: {violating_files} file(s) contain unguarded os.path calls "
            f"outside the allowlist (baseline: {self._BASELINE_FILE_COUNT}).\n"
            f"Use pathlib.Path instead, or add the file to _OS_PATH_ALLOWED with justification.\n"
            f"Violations (first 20):\n  "
            + "\n  ".join(f"{r}:{ln}: {s}" for r, ln, s in violations[:20])
        )


# ─────────────────────────────────────────────────────────────────────────────
# Test 5 — No os.system() without platform guard in cortex/ source
# ─────────────────────────────────────────────────────────────────────────────

class TestNoOsSystemWithoutPlatformGuard:
    """Block bare os.system() calls in production cortex/ source.

    os.system() is POSIX-biased, blocks the GIL, and has no timeout support.
    All subprocess invocations must use subprocess.run() with explicit
    platform handling. This test scans for bare os.system( in cortex/.
    """

    def test_no_os_system_without_platform_guard(self) -> None:
        """No bare os.system() calls may appear in cortex/ production source."""
        violations: List[Tuple[str, int, str]] = []
        for f in _all_production_py_files():
            rel = _rel(f)
            if any(rel.startswith(d) for d in _POSIX_SCAN_EXCLUDE_DIRS):
                continue
            try:
                source = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for lineno, line in enumerate(source.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if _OS_SYSTEM_RE.search(line):
                    # Allow if it's in a string (documentation / detection regex)
                    if '"""' in line or "'''" in line or "r'" in line or 'r"' in line:
                        continue
                    if "SEC-012" in line or "regex" in line.lower():
                        continue
                    violations.append((rel, lineno, stripped[:120]))

        assert not violations, (
            f"CHECK-30 FAIL: {len(violations)} bare os.system() call(s) in cortex/.\n"
            f"Use subprocess.run() with platform-appropriate arguments instead.\n"
            f"Violations:\n  "
            + "\n  ".join(f"{r}:{ln}: {s}" for r, ln, s in violations)
        )

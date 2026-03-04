"""Preflight: Drift Lock — Check #30 Windows Boot Wiring (phase-126-a).

Permanent CI guardrail that enforces the invariants established by phase-126-a.
Fails immediately if any Windows boot wiring regression is introduced.

This is a LOCK file — it does not replace test_windows_boot_wiring.py.
It adds a lightweight fast gate that runs even before the full preflight suite.

Drift lock ref: cortex-registry/governance/drift-locks/check-30-windows-boot-lock.yaml
Gap ref: GAP-126-01
Phase ref: phase-126-a
Tier: T0 (preflight) — fast, < 5 s
"""
import pathlib
import re
import subprocess
import sys

import pytest

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
SETUP_MCP_SCRIPT = CORTEX_ROOT / "scripts" / "setup-mcp.py"
DRIFT_LOCK_YAML = (
    CORTEX_ROOT
    / "cortex-registry"
    / "governance"
    / "drift-locks"
    / "check-30-windows-boot-lock.yaml"
)


class TestDriftLockCheck30:
    """Drift lock: Windows boot wiring invariants must hold permanently.

    Each test maps to an enforced invariant in check-30-windows-boot-lock.yaml.
    Failure here means a regression has been introduced — fix, do not delete.
    """

    def test_drift_lock_yaml_exists(self) -> None:
        """INV-30-00: The drift lock YAML itself must exist.

        If this test fails, someone deleted the governance file — restore it.
        """
        assert DRIFT_LOCK_YAML.exists(), (
            f"DRIFT-LOCK REGRESSION: Governance file deleted: {DRIFT_LOCK_YAML}\n"
            "Restore from git: git checkout HEAD -- "
            "cortex-registry/governance/drift-locks/check-30-windows-boot-lock.yaml"
        )

    def test_drift_lock_setup_mcp_uses_sys_executable(self) -> None:
        """INV-30-01: setup-mcp.py must contain sys.executable reference.

        Regression: if sys.executable is removed, Windows CI will fail because
        hardcoded interpreter paths do not work on Windows.
        """
        assert SETUP_MCP_SCRIPT.exists(), (
            f"DRIFT-LOCK: setup-mcp.py not found at {SETUP_MCP_SCRIPT}"
        )
        source = SETUP_MCP_SCRIPT.read_text(encoding="utf-8")
        assert "sys.executable" in source, (
            "DRIFT-LOCK CHECK-30 INV-30-01 REGRESSION: sys.executable removed from "
            "setup-mcp.py. Windows CI will fail — interpreter path will not resolve.\n"
            "Restore: add 'if sys.executable: return sys.executable' as the first "
            "candidate in _detect_python_executable()."
        )

    def test_drift_lock_setup_mcp_has_dry_run(self) -> None:
        """INV-30-02: setup-mcp.py must support --dry-run flag.

        Regression: if --dry-run is removed, CI pipelines on Windows cannot
        validate MCP configuration without writing files (which may fail in
        read-only CI environments).
        """
        source = SETUP_MCP_SCRIPT.read_text(encoding="utf-8")
        has_dry_run = "dry_run" in source or "dry-run" in source
        assert has_dry_run, (
            "DRIFT-LOCK CHECK-30 INV-30-02 REGRESSION: --dry-run flag removed from "
            "setup-mcp.py. CI validation gate is broken.\n"
            "Restore: add argparse '--dry-run' argument that skips file writes."
        )

    def test_drift_lock_cortex_help_exits_zero(self) -> None:
        """INV-30-03: python -m cortex --help must exit 0.

        Regression: if the entry point breaks (import error, missing dependency,
        CLI routing failure), this test catches it immediately.
        """
        result = subprocess.run(
            [sys.executable, "-m", "cortex", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(CORTEX_ROOT),
        )
        assert result.returncode == 0, (
            f"DRIFT-LOCK CHECK-30 INV-30-03 REGRESSION: python -m cortex --help "
            f"exited {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}\n"
            "This means the CORTEX entry point is broken. Fix the import chain."
        )

    def test_drift_lock_no_new_posix_paths(self) -> None:
        """INV-30-04: No new unguarded os.path calls beyond the catalogued allowlist.

        Regression: if new os.path.* calls appear in cortex/ outside the known
        allowlist, they are potential Windows failures (UNC paths, separator issues).
        The allowlist lives in test_windows_boot_wiring.py — update it with
        justification when new legitimate uses are added.
        """
        _os_path_re = re.compile(
            r"\bos\.path\.(join|abspath|dirname|exists|isfile|isdir|realpath"
            r"|expanduser|normpath|basename|splitext)\("
        )
        _excludes: frozenset = frozenset({
            "cortex/intelligence/memory/core/macos_path_compat.py",
            "cortex/core/security/isolation.py",
        })
        _exclude_dirs: tuple = ("tests/", "scripts/", "_workspaces/")

        # Import the allowlist from the primary test file to keep a single SSOT
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "test_windows_boot_wiring",
            str(CORTEX_ROOT / "tests" / "preflight" / "test_windows_boot_wiring.py"),
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        allowed: frozenset = module._OS_PATH_ALLOWED  # type: ignore[attr-defined]

        violations = []
        for f in (CORTEX_ROOT / "cortex").rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            rel = str(f.relative_to(CORTEX_ROOT)).replace("\\", "/")
            if rel in allowed or rel in _excludes:
                continue
            if any(rel.startswith(d) for d in _exclude_dirs):
                continue
            try:
                source = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for lineno, line in enumerate(source.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if _os_path_re.search(line):
                    if "pathlib" in line or "Path(" in line:
                        continue
                    violations.append(f"{rel}:{lineno}: {stripped[:80]}")

        assert not violations, (
            f"DRIFT-LOCK CHECK-30 INV-30-04 REGRESSION: "
            f"{len(violations)} new unguarded os.path call(s) detected.\n"
            "Add the file to _OS_PATH_ALLOWED in test_windows_boot_wiring.py "
            "with a documented justification, or replace with pathlib.Path.\n"
            "Violations:\n  " + "\n  ".join(violations[:20])
        )

    def test_drift_lock_no_os_system_calls(self) -> None:
        """INV-30-05: No bare os.system() calls in production cortex/ source.

        Regression: os.system() is POSIX-biased, blocks the GIL, and lacks
        timeout support. Use subprocess.run() with platform-aware arguments.
        """
        _os_system_re = re.compile(r"\bos\.system\(")
        _exclude_dirs: tuple = ("tests/", "scripts/", "_workspaces/")
        violations = []
        for f in (CORTEX_ROOT / "cortex").rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            rel = str(f.relative_to(CORTEX_ROOT)).replace("\\", "/")
            if any(rel.startswith(d) for d in _exclude_dirs):
                continue
            try:
                source = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for lineno, line in enumerate(source.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if _os_system_re.search(line):
                    if "SEC-012" in line or "regex" in line.lower():
                        continue
                    violations.append(f"{rel}:{lineno}: {stripped[:80]}")

        assert not violations, (
            f"DRIFT-LOCK CHECK-30 INV-30-05 REGRESSION: "
            f"{len(violations)} bare os.system() call(s) in cortex/ production source.\n"
            "Replace with subprocess.run() with platform-appropriate arguments.\n"
            "Violations:\n  " + "\n  ".join(violations)
        )

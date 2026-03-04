"""Preflight: Repository Hygiene and Production Purity Sweep (phase-126-f, Check #35).

Asserts the CORTEX repository is free of backup files, archive files, stray log files,
and dead function definitions in production cortex/ source. Also verifies that
VacuumOrchestrator exists (purity sweep integration anchor).

Gap ref: GAP-126-06
Drift lock: cortex-registry/governance/drift-locks/check-35-repo-hygiene-lock.yaml
Tier: T0 (preflight) — filesystem scan only, no server startup, < 10 s
CORE rules: CORE-008 (TDD), CORE-035 (single canonical implementation)
"""
from __future__ import annotations

import pathlib
import re
from typing import List

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
CORTEX_SRC = CORTEX_ROOT / "cortex"

_BACKUP_EXTENSIONS = frozenset({".backup", ".bak", ".old"})
_ARCHIVE_EXTENSIONS = frozenset({".tar.gz", ".zip", ".tar", ".tgz", ".tar.bz2"})
_EXEMPT_PATHS = frozenset({
    str(CORTEX_ROOT / ".git"),
    str(CORTEX_ROOT / ".venv"),
    str(CORTEX_ROOT / ".cortex-runtime"),
    str(CORTEX_ROOT / "_workspaces"),
})


def _is_exempt(path: pathlib.Path) -> bool:
    path_str = str(path)
    return any(path_str.startswith(ep) for ep in _EXEMPT_PATHS)


class TestRepoHygiene:
    """Repository must be free of backup, archive, and stray log files."""

    def test_no_backup_files_in_repo(self) -> None:
        """No *.backup, *.bak, *.old files in the repository (outside exemptions)."""
        violations: List[pathlib.Path] = []
        for f in CORTEX_ROOT.rglob("*"):
            if _is_exempt(f):
                continue
            if f.suffix in _BACKUP_EXTENSIONS:
                violations.append(f)
            # Also catch compound extensions like .py.backup
            if any(str(f).endswith(ext) for ext in _BACKUP_EXTENSIONS):
                if f not in violations:
                    violations.append(f)
        assert not violations, (
            f"Backup files found in repo:\n"
            + "\n".join(f"  {p.relative_to(CORTEX_ROOT)}" for p in violations)
        )

    def test_no_archive_files_in_repo(self) -> None:
        """No *.tar.gz, *.zip, *.tar archive files in the repository."""
        violations: List[pathlib.Path] = []
        for f in CORTEX_ROOT.rglob("*"):
            if _is_exempt(f):
                continue
            # Handle compound extensions like .tar.gz
            name = f.name
            if any(name.endswith(ext) for ext in _ARCHIVE_EXTENSIONS):
                violations.append(f)
        assert not violations, (
            f"Archive files found in repo:\n"
            + "\n".join(f"  {p.relative_to(CORTEX_ROOT)}" for p in violations)
        )

    def test_no_log_files_outside_cortex_runtime(self) -> None:
        """No *.log files outside .cortex-runtime/ (log files belong in runtime dir)."""
        violations: List[pathlib.Path] = []
        for f in CORTEX_ROOT.rglob("*.log"):
            if _is_exempt(f):
                continue
            violations.append(f)
        assert not violations, (
            f"Stray log files outside .cortex-runtime/:\n"
            + "\n".join(f"  {p.relative_to(CORTEX_ROOT)}" for p in violations)
        )


class TestProductionPurity:
    """Production cortex/ source must be free of dead function definitions."""

    def test_no_dead_function_definitions_in_cortex_source(self) -> None:
        """No `def *_OLD` or lines marked `# DEAD CODE` in cortex/ production source.

        Pattern: only standalone markers at line start — NOT mid-sentence section comments
        like '# Deprecated method aliases'. The pattern requires the marker word to end the
        comment or be followed by punctuation/whitespace+end.
        """
        dead_pattern = re.compile(
            r"^\s*(def\s+\w+_OLD\s*\(|#\s*DEAD\s+CODE\s*$|#\s*DEPRECATED\s*$)",
            re.IGNORECASE,
        )
        violations: List[str] = []
        for py_file in CORTEX_SRC.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for i, line in enumerate(content.splitlines(), 1):
                if dead_pattern.match(line):
                    rel = str(py_file.relative_to(CORTEX_ROOT))
                    violations.append(f"  {rel}:{i}: {line.strip()}")
        assert not violations, (
            f"Dead function definitions or DEAD CODE markers in cortex/ source:\n"
            + "\n".join(violations[:30])
        )

    def test_vacuum_orchestrator_exists(self) -> None:
        """VacuumOrchestrator must exist — it is the purity sweep integration anchor."""
        candidates = list((CORTEX_SRC / "orchestrators").rglob("*vacuum*orchestrator*.py"))
        assert candidates, (
            "No VacuumOrchestrator file found in cortex/orchestrators/. "
            "Expected a file matching *vacuum*orchestrator*.py."
        )

    def test_vacuum_orchestrator_is_non_empty(self) -> None:
        """VacuumOrchestrator file must be a non-trivial module (> 500 bytes)."""
        candidates = list((CORTEX_SRC / "orchestrators").rglob("*vacuum*orchestrator*.py"))
        if not candidates:
            pytest.skip("VacuumOrchestrator not found")
        vac = candidates[0]
        size = vac.stat().st_size
        assert size > 500, (
            f"VacuumOrchestrator {vac.name} is only {size} bytes — appears to be a stub."
        )


class TestRepoPurityDriftLock:
    """Permanent CI drift lock — Check #35 invariants."""

    def test_drift_lock_yaml_exists(self) -> None:
        lock = (
            CORTEX_ROOT
            / "cortex-registry"
            / "governance"
            / "drift-locks"
            / "check-35-repo-hygiene-lock.yaml"
        )
        assert lock.exists(), (
            "Drift lock YAML check-35-repo-hygiene-lock.yaml not found."
        )

    def test_drift_lock_yaml_is_valid(self) -> None:
        lock = (
            CORTEX_ROOT
            / "cortex-registry"
            / "governance"
            / "drift-locks"
            / "check-35-repo-hygiene-lock.yaml"
        )
        if not lock.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(lock.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 35

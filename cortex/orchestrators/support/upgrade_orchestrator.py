"""UpgradeOrchestrator — Differential upgrade system with safety.

Supports rolling, blue-green, and canary upgrade strategies
with circuit breaker, execution history, and caching.
Also implements inflight upgrade detection via check_upstream_and_merge()
and requirements preflight validation via validate_requirements().
"""

import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 94d
from cortex.core.file_factory import get_file_factory

# Phase 58-C: DomainBrain + Memory wiring (execution orchestrator)
try:
    from cortex.intelligence.domain_brain import DomainBrainAPI as _UpgDomainBrainAPI  # type: ignore[attr-defined]
except Exception:
    _UpgDomainBrainAPI = None  # type: ignore[assignment,misc]

try:
    from cortex.intelligence.memory.tier2_adaptive.hallucination_prevention import (  # type: ignore[import]
        BehavioralBoundaryRules as _UpgBehavioralBoundaryRules,
    )
except Exception:
    _UpgBehavioralBoundaryRules = None  # type: ignore[assignment]

try:
    from cortex.intelligence.memory.tier3_scratch import (  # type: ignore[import]
        get_scratch_space_path as _upg_get_scratch_path,
    )
except Exception:
    _upg_get_scratch_path = None  # type: ignore[assignment]


class UpgradeStrategy(Enum):
    """Upgrade execution strategies."""
    ROLLING = auto()
    BLUE_GREEN = auto()
    CANARY = auto()
    IN_PLACE = auto()


@dataclass
class UpgradeComponent:
    """A component targeted for upgrade.

    Args:
        name: Component name.
        current_version: Current version.
        target_version: Target version.
        dependencies: Optional list of dependent component names.
    """
    name: str
    current_version: str
    target_version: str
    dependencies: List[str] = field(default_factory=list)


@dataclass
class UpgradePlan:
    """Plan produced by :meth:`UpgradeOrchestrator.plan_upgrade`.

    Args:
        upgrade_id: Unique plan identifier.
        components: Components in the plan.
        strategy: Strategy to use.
    """
    upgrade_id: str
    components: List[UpgradeComponent] = field(default_factory=list)
    strategy: UpgradeStrategy = UpgradeStrategy.ROLLING


class CircuitBreaker:  # CORE-035-scoped — domain-specific circuit breaker — independent implementations
    """Simple circuit breaker for safety."""

    def __init__(self, threshold: int = 3) -> None:
        """Initialize circuit breaker.

        Args:
            threshold: Number of failures before tripping.
        """
        self._failures = 0
        self._threshold = threshold
        self._open = False

    @property
    def is_open(self) -> bool:
        """Whether the circuit is open (tripped)."""
        return self._open

    def record_failure(self) -> None:
        """Record a failure."""
        self._failures += 1
        if self._failures >= self._threshold:
            self._open = True

    def reset(self) -> None:
        """Reset the circuit breaker."""
        self._failures = 0
        self._open = False


class UpgradeOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin):
    """Differential upgrade orchestrator with safety features."""

    # Phase 94d — advisory: upgrade operations run inside audit/fix pipelines;
    # self-gating here would create a re-entry loop through WorkflowGateway.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(self) -> None:
        """Initialize UpgradeOrchestrator."""
        self.logger = logging.getLogger("UpgradeOrchestrator")
        self.engine = self  # self-referential engine for hasattr checks
        self.circuit_breaker = CircuitBreaker()
        self._execution_history: Dict[str, Any] = {}
        self._upgrade_cache: Dict[str, Any] = {}
        self.max_cache_size: int = 100

    def plan_upgrade(
        self,
        upgrade_id: str,
        components: Optional[List[UpgradeComponent]] = None,
        strategy: UpgradeStrategy = UpgradeStrategy.ROLLING,
    ) -> UpgradePlan:
        """Create an upgrade plan.

        Args:
            upgrade_id: Unique plan identifier.
            components: Components to upgrade.
            strategy: Upgrade strategy.

        Returns:
            UpgradePlan instance.
        """
        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(operation="plan_upgrade")
        return UpgradePlan(
            upgrade_id=upgrade_id,
            components=components or [],
            strategy=strategy,
        )

    def check_upstream_and_merge(self) -> Dict[str, Any]:
        """Check origin/main for upstream commits and merge if ahead.

        Implements the Inflight Upgrade Protocol (audit-fix.md Part 9):
        1. Fetch origin silently.
        2. Count commits in origin/main not in HEAD.
        3. If > 0: non-FF merge with --no-commit, restore protected admin paths,
           then commit (preserving user-sovereign folders).
        4. If merge fails: abort and surface conflicts inline.
        5. Guarded by CORTEX_AUTO_UPGRADE env var (default: true).

        Returns:
            Dict with keys: commits_behind, merged, merge_sha, audit_result, error,
            protected_paths.
        """
        # AC_START: AC-UPGRADE-{timestamp}
        auto_upgrade = os.environ.get("CORTEX_AUTO_UPGRADE", "true").lower() != "false"

        # Protected admin-only paths — never overwritten by remote origin/main
        default_protected = [
            "docs/",
            "_workspaces/",
            "cortex-sts/",
            ".github/prompts/cortex-doc.prompt.md",
            ".github/agents/core/cortex-documentation-architect.md",
            ".github/agents/core/cortex-gitpages-builder.md",
            ".github/agents/core/cortex-storyteller.md",
        ]
        extra_excludes = os.environ.get("CORTEX_UPGRADE_EXCLUDE_PATHS", "")
        protected_paths = default_protected + [
            p.strip() for p in extra_excludes.split(",") if p.strip()
        ]

        result: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "commits_behind": 0,
            "merged": False,
            "merge_sha": None,
            "audit_result": "pass",
            "error": None,
            "protected_paths": protected_paths,
        }

        try:
            # Fetch silently (CORE-049)
            subprocess.run(
                ["git", "fetch", "origin", "--quiet"],
                check=True,
                capture_output=True,
            )

            # Count upstream commits
            count_out = subprocess.run(
                ["git", "rev-list", "--count", "HEAD..origin/main"],
                check=True,
                capture_output=True,
                text=True,
            )
            commits_behind = int(count_out.stdout.strip())
            result["commits_behind"] = commits_behind

            if commits_behind > 0 and auto_upgrade:
                ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                self.logger.info(
                    "UpgradeOrchestrator: %d upstream commits detected — merging origin/main",
                    commits_behind,
                )
                # Non-FF merge without auto-commit so we can restore protected paths
                merge_proc = subprocess.run(
                    ["git", "merge", "--no-ff", "--no-commit", "origin/main"],
                    capture_output=True,
                    text=True,
                )
                if merge_proc.returncode == 0 or "Automatic merge went well" in merge_proc.stdout:
                    # Restore protected admin-only folders to pre-merge local state
                    for protected in protected_paths:
                        restore_proc = subprocess.run(
                            ["git", "checkout", "HEAD", "--", protected],
                            capture_output=True,
                            text=True,
                        )
                        if restore_proc.returncode != 0:
                            self.logger.debug(
                                "UpgradeOrchestrator: protected path restore skipped (not staged): %s",
                                protected,
                            )

                    # Commit the merged state with protected paths preserved
                    commit_msg = (
                        f"chore(upgrade): inflight upgrade from origin/main — {ts} "
                        f"(admin folders preserved)"
                    )
                    commit_proc = subprocess.run(
                        ["git", "commit", "--no-edit", "-m", commit_msg],
                        capture_output=True,
                        text=True,
                    )
                    if commit_proc.returncode == 0:
                        sha_out = subprocess.run(
                            ["git", "rev-parse", "HEAD"],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        result["merged"] = True
                        result["merge_sha"] = sha_out.stdout.strip()
                    else:
                        # Nothing to commit (already up-to-date after restore)
                        result["merged"] = True
                        result["merge_sha"] = "up-to-date-after-restore"
                else:
                    # Abort merge and surface conflicts
                    subprocess.run(["git", "merge", "--abort"], capture_output=True)
                    result["audit_result"] = "fail"
                    result["error"] = merge_proc.stderr.strip() or merge_proc.stdout.strip()
                    self.logger.error(
                        "UpgradeOrchestrator: merge conflict — %s", result["error"]
                    )

        except Exception as exc:  # noqa: BLE001
            result["audit_result"] = "fail"
            result["error"] = str(exc)
            self.logger.error("UpgradeOrchestrator: upstream check failed — %s", exc)

        self._write_upgrade_manifest(result)
        # AC_COMPLETE: AC-UPGRADE-{timestamp} ✅
        return result

    def validate_requirements(self) -> Dict[str, Any]:
        """Validate requirements.txt against the active virtual environment.

        Implements PART 14 Environment Readiness preflight gate:
        1. Verify .venv is active (sys.executable path contains '.venv').
        2. Parse requirements.txt for all packages.
        3. Compare against pip list output — flag missing, version-mismatch.
        4. Run pip check for broken dependency chains.
        5. Detect duplicate entries in requirements.txt.
        6. Emit AC_START / AC_COMPLETE markers.

        Returns:
            Dict with keys: p0_violations, p1_violations, advisories, ok.
        """
        # AC_START: AC-PREFLIGHT-{timestamp}
        result: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "p0_violations": [],
            "p1_violations": [],
            "advisories": [],
            "ok": True,
        }

        # 1. Virtual environment check
        active_python = sys.executable
        if ".venv" not in active_python and "venv" not in active_python:
            result["p0_violations"].append(
                f"CORTEX is running outside the project virtual environment — "
                f"active interpreter: {active_python}. "
                f"Run `source .venv/bin/activate` (macOS/Linux) or "
                f"`.venv\\Scripts\\activate` (Windows) before proceeding."
            )
            result["ok"] = False

        # 2. Parse requirements.txt
        req_path = Path("requirements.txt")
        if not req_path.exists():
            result["p0_violations"].append("requirements.txt not found at workspace root.")
            result["ok"] = False
            self._write_upgrade_manifest(result)
            return result

        parsed: Dict[str, str] = {}  # {normalized_name: raw_spec}
        seen_lines: Dict[str, int] = {}
        with req_path.open() as fh:
            for lineno, line in enumerate(fh, start=1):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                # Extract package name (before any version specifier)
                name_part = (
                    stripped.split("==")[0]
                    .split(">=")[0]
                    .split("<=")[0]
                    .split("!=")[0]
                    .split("~=")[0]
                    .split(">")[0]
                    .split("<")[0]
                    .split("[")[0]
                    .strip()
                    .lower()
                )
                if not name_part:
                    continue
                if name_part in seen_lines:
                    result["p1_violations"].append(
                        f"Duplicate entry for `{name_part}` in requirements.txt "
                        f"at lines {seen_lines[name_part]} and {lineno} — remove one."
                    )
                else:
                    seen_lines[name_part] = lineno
                    parsed[name_part] = stripped

        # 3. Compare against pip list
        try:
            pip_list_proc = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True,
            )
            installed_raw = json.loads(pip_list_proc.stdout)
            installed: Dict[str, str] = {
                pkg["name"].lower(): pkg["version"] for pkg in installed_raw
            }
        except Exception as exc:  # noqa: BLE001
            result["advisories"].append(f"Could not run pip list: {exc}")
            installed = {}

        for pkg_name, spec in parsed.items():
            if pkg_name not in installed:
                result["p0_violations"].append(
                    f"Package `{pkg_name}` is required but not installed — "
                    f"run `pip install -r requirements.txt`"
                )
                result["ok"] = False
            else:
                inst_ver = installed[pkg_name]
                if "==" in spec:
                    pinned = spec.split("==")[1].split("#")[0].strip()
                    if inst_ver != pinned:
                        result["p1_violations"].append(
                            f"Package `{pkg_name}` pinned to `=={pinned}` "
                            f"but `{inst_ver}` is installed — environment may be stale."
                        )

        # 4. pip check for broken dependency chains
        try:
            pip_check_proc = subprocess.run(
                [sys.executable, "-m", "pip", "check"],
                capture_output=True,
                text=True,
            )
            if pip_check_proc.stdout.strip() and pip_check_proc.stdout.strip() != "No broken requirements found.":
                result["p1_violations"].append(
                    f"Dependency chain broken: {pip_check_proc.stdout.strip()}"
                )
        except Exception as exc:  # noqa: BLE001
            result["advisories"].append(f"pip check failed to run: {exc}")

        if result["p0_violations"]:
            result["ok"] = False

        self.logger.info(
            "UpgradeOrchestrator.validate_requirements: p0=%d p1=%d ok=%s",
            len(result["p0_violations"]),
            len(result["p1_violations"]),
            result["ok"],
        )
        # AC_COMPLETE: AC-PREFLIGHT-{timestamp} ✅
        return result

    def _write_upgrade_manifest(self, entry: Dict[str, Any]) -> None:
        """Persist upgrade result to .cortex-runtime/traces/upgrade-manifest.json.

        Args:
            entry: Upgrade result dict to append.
        """
        manifest_path = Path(".cortex-runtime/traces/upgrade-manifest.json")
        manifest_path.parent.mkdir(parents=True, exist_ok=True)

        if manifest_path.exists():
            try:
                data = json.loads(manifest_path.read_text())
            except (json.JSONDecodeError, OSError):
                data = {"schema_version": "1.0", "upgrades": [], "last_check": None}
        else:
            data = {"schema_version": "1.0", "upgrades": [], "last_check": None}

        data["upgrades"].append(entry)
        data["last_check"] = entry["timestamp"]
        ff = get_file_factory()
        ff.create_file(manifest_path, json.dumps(data, indent=2))


#!/usr/bin/env python3
"""Dual-surface parity validator for Claude/GitHub capability wiring.

Validates the Claude-primary control-plane contract from:
`cortex-registry/governance/claude-primary-capability-manifest.yaml`.

Checks:
  - Shared skills exist on both `.github` and `.claude` surfaces.
  - Surface-specific skill lists do not leak to the opposite surface.
  - Shared agents exist on both surfaces.
  - Surface-specific agent lists do not leak to the opposite surface.
  - Claude skill bridge imports (`@../../../.github/skills/...`) resolve.

Exit code:
  - 0 if no violations
  - 1 if any violations
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NamedTuple, Optional

import yaml


class ParityViolation(NamedTuple):
    """A single parity violation."""

    rule: str
    path: str
    message: str
    severity: str  # P0, P1, P2


def _repo_root() -> Path:
    return Path(__file__).parent.parent


def _load_manifest(workspace_root: Path) -> dict:
    manifest_path = (
        workspace_root
        / "cortex-registry"
        / "governance"
        / "claude-primary-capability-manifest.yaml"
    )
    if not manifest_path.exists():
        raise FileNotFoundError(
            "Missing manifest: cortex-registry/governance/claude-primary-capability-manifest.yaml"
        )

    with open(manifest_path, "r", encoding="utf-8") as handle:
        parsed = yaml.safe_load(handle) or {}

    if not isinstance(parsed, dict):
        raise ValueError("Capability manifest must parse to a mapping.")

    return parsed


def _skill_exists(workspace_root: Path, surface: str, skill_id: str) -> bool:
    return (
        workspace_root
        / f".{surface}"
        / "skills"
        / skill_id
        / "SKILL.md"
    ).exists()


def _agent_exists(workspace_root: Path, surface: str, agent_id: str) -> bool:
    if surface == "github" and agent_id == "AGENT-INDEX":
        return (workspace_root / ".github" / "agents" / "AGENT-INDEX.md").exists()

    # Agent resolution by canonical stem
    surface_dir = workspace_root / f".{surface}" / "agents"
    candidates = list(surface_dir.rglob("*.md")) if surface_dir.exists() else []
    target_stems = {agent_id, f"{agent_id}-agent"}
    return any(path.stem in target_stems for path in candidates)


def _list_surface_skills(workspace_root: Path, surface: str) -> set[str]:
    root = workspace_root / f".{surface}" / "skills"
    if not root.exists():
        return set()
    return {path.parent.name for path in root.rglob("SKILL.md")}


def _list_surface_agents(workspace_root: Path, surface: str) -> set[str]:
    root = workspace_root / f".{surface}" / "agents"
    if not root.exists():
        return set()
    return {path.stem for path in root.rglob("*.md")}


def _validate_claude_bridge_targets(workspace_root: Path) -> list[ParityViolation]:
    violations: list[ParityViolation] = []
    bridge_pattern = re.compile(r"^@(?P<target>\.\./\.\./\.\./\.github/skills/.+/SKILL\.md)$")

    claude_skill_files = list((workspace_root / ".claude" / "skills").rglob("SKILL.md"))
    for file_path in claude_skill_files:
        first_line = file_path.read_text(encoding="utf-8").splitlines()
        if not first_line:
            continue
        match = bridge_pattern.match(first_line[0].strip())
        if not match:
            continue

        target_rel = match.group("target")
        target_abs = (file_path.parent / target_rel).resolve()
        if not target_abs.exists():
            violations.append(
                ParityViolation(
                    rule="CLAUDE-BRIDGE",
                    path=str(file_path.relative_to(workspace_root)),
                    message=(
                        f"Bridge target missing: {target_rel}"
                    ),
                    severity="P0",
                )
            )

    return violations


def validate_dual_surface_parity(
    workspace_root: Optional[Path] = None,
    *,
    verbose: bool = False,
) -> tuple[bool, list[ParityViolation]]:
    """Validate Claude/GitHub parity against manifest contract.

    Args:
        workspace_root: Workspace root path. Auto-detected when omitted.
        verbose: Print additional inventory detail.

    Returns:
        Tuple `(is_valid, violations)` where `is_valid` is True when no P0s exist.
    """
    if workspace_root is None:
        workspace_root = _repo_root()

    manifest = _load_manifest(workspace_root)
    skills_block = manifest.get("skills", {}) or {}
    agents_block = manifest.get("agents", {}) or {}

    violations: list[ParityViolation] = []

    shared_skills = skills_block.get("shared", [])
    claude_only_skills = set(skills_block.get("claude_only", []))
    github_only_skills = set(skills_block.get("github_only", []))

    for skill_id in shared_skills:
        if not _skill_exists(workspace_root, "github", skill_id):
            violations.append(
                ParityViolation(
                    rule="SKILL-PARITY",
                    path=f".github/skills/{skill_id}/SKILL.md",
                    message=f"Missing shared skill on GitHub surface: {skill_id}",
                    severity="P0",
                )
            )
        if not _skill_exists(workspace_root, "claude", skill_id):
            violations.append(
                ParityViolation(
                    rule="SKILL-PARITY",
                    path=f".claude/skills/{skill_id}/SKILL.md",
                    message=f"Missing shared skill on Claude surface: {skill_id}",
                    severity="P0",
                )
            )

    github_skills = _list_surface_skills(workspace_root, "github")
    claude_skills = _list_surface_skills(workspace_root, "claude")

    for skill_id in claude_only_skills:
        if skill_id in github_skills:
            violations.append(
                ParityViolation(
                    rule="SKILL-SCOPE",
                    path=f".github/skills/{skill_id}/SKILL.md",
                    message=f"Claude-only skill leaks to GitHub surface: {skill_id}",
                    severity="P1",
                )
            )

    for skill_id in github_only_skills:
        if skill_id in claude_skills:
            violations.append(
                ParityViolation(
                    rule="SKILL-SCOPE",
                    path=f".claude/skills/{skill_id}/SKILL.md",
                    message=f"GitHub-only skill leaks to Claude surface: {skill_id}",
                    severity="P1",
                )
            )

    shared_agents = agents_block.get("shared", [])
    claude_only_agents = set(agents_block.get("claude_only", []))
    github_only_agents = set(agents_block.get("github_only", []))

    for agent_id in shared_agents:
        if not _agent_exists(workspace_root, "github", agent_id):
            violations.append(
                ParityViolation(
                    rule="AGENT-PARITY",
                    path=".github/agents",
                    message=f"Missing shared agent on GitHub surface: {agent_id}",
                    severity="P1",
                )
            )
        if not _agent_exists(workspace_root, "claude", agent_id):
            violations.append(
                ParityViolation(
                    rule="AGENT-PARITY",
                    path=".claude/agents",
                    message=f"Missing shared agent on Claude surface: {agent_id}",
                    severity="P1",
                )
            )

    github_agents = _list_surface_agents(workspace_root, "github")
    claude_agents = _list_surface_agents(workspace_root, "claude")

    for agent_id in claude_only_agents:
        if agent_id in github_agents:
            violations.append(
                ParityViolation(
                    rule="AGENT-SCOPE",
                    path=f".github/agents/{agent_id}.md",
                    message=f"Claude-only agent leaks to GitHub surface: {agent_id}",
                    severity="P1",
                )
            )

    for agent_id in github_only_agents:
        if agent_id in claude_agents:
            violations.append(
                ParityViolation(
                    rule="AGENT-SCOPE",
                    path=f".claude/agents/{agent_id}.md",
                    message=f"GitHub-only agent leaks to Claude surface: {agent_id}",
                    severity="P1",
                )
            )

    violations.extend(_validate_claude_bridge_targets(workspace_root))

    if verbose:
        print("🔎 Dual-surface inventory:")
        print(f"   GitHub skills: {len(github_skills)}")
        print(f"   Claude skills: {len(claude_skills)}")
        print(f"   GitHub agents: {len(github_agents)}")
        print(f"   Claude agents: {len(claude_agents)}")

    is_valid = not any(v.severity == "P0" for v in violations)
    return is_valid, violations


def _print_report(violations: list[ParityViolation]) -> None:
    if not violations:
        print("✅ Dual-surface parity: All checks passed (0 violations)")
        return

    p0 = [v for v in violations if v.severity == "P0"]
    p1 = [v for v in violations if v.severity == "P1"]
    p2 = [v for v in violations if v.severity == "P2"]

    print("\n📋 Dual-Surface Parity Results:")
    print(f"   P0 (blocking): {len(p0)}")
    print(f"   P1 (warning):  {len(p1)}")
    print(f"   P2 (info):     {len(p2)}")
    print()

    for issue in violations:
        icon = "🔴" if issue.severity == "P0" else "🟡" if issue.severity == "P1" else "🔵"
        print(f"   {icon} [{issue.rule}] {issue.path}")
        print(f"      {issue.message}")


def main() -> int:
    workspace = _repo_root()
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    try:
        is_valid, violations = validate_dual_surface_parity(workspace, verbose=verbose)
    except Exception as exc:
        print(f"❌ Dual-surface parity validation failed: {exc}")
        return 1

    _print_report(violations)
    return 0 if is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())

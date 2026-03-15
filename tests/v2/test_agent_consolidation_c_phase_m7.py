"""Phase M7-c guardrails for core, certification, and education agent consolidation."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_m7c_vacuum_agent_merged() -> None:
    """Vacuum capabilities consolidate into a single support agent."""
    merged_path = REPO_ROOT / ".github/agents/support/cortex-vacuum.md"
    assert merged_path.exists(), "Merged vacuum agent missing"

    content = merged_path.read_text(encoding="utf-8")
    assert "8-stage pipeline" in content
    assert "CORE-064" in content
    assert "OS artifacts" in content
    assert "backup artifacts" in content

    removed_path = REPO_ROOT / ".github/agents/certification/cortex-vacuum-agent.md"
    assert not removed_path.exists(), "Certification vacuum worker should be merged away"


def test_m7c_audit_coordinator_merged() -> None:
    """Audit capabilities consolidate into a single coordinator."""
    merged_path = REPO_ROOT / ".github/agents/core/cortex-audit-coordinator.md"
    assert merged_path.exists(), "Merged audit coordinator missing"

    content = merged_path.read_text(encoding="utf-8")
    assert "41 checks" in content
    assert "7 drift categories" in content
    assert "22 drift locks" in content

    removed_paths = [
        ".github/agents/core/cortex-auditor.md",
        ".github/agents/certification/cortex-audit-agent.md",
    ]
    for rel_path in removed_paths:
        assert not (REPO_ROOT / rel_path).exists(), f"Superseded audit agent must be removed: {rel_path}"


def test_m7c_master_planner_merged() -> None:
    """Planning agents consolidate into a single master planner."""
    merged_path = REPO_ROOT / ".github/agents/core/cortex-master-planner.md"
    assert merged_path.exists(), "Merged master planner missing"

    content = merged_path.read_text(encoding="utf-8")
    assert "four laws" in content
    assert "completion gate" in content
    assert "reference resolution" in content
    assert "THIN INDEX" in content
    assert "12 audit checks" in content

    removed_paths = [
        ".github/agents/core/master-planner.md",
        ".github/agents/core/cortex-phase-resolver.md",
        ".github/agents/core/phase-creation-standards.md",
        ".github/agents/core/cortex-master-plan-auditor.md",
    ]
    for rel_path in removed_paths:
        assert not (REPO_ROOT / rel_path).exists(), f"Superseded planning agent must be removed: {rel_path}"


def test_m7c_certification_workers_merged() -> None:
    """Certification worker agents collapse into coordinator/workers/db/cert structure."""
    merged_path = REPO_ROOT / ".github/agents/certification/cortex-certification-workers.md"
    assert merged_path.exists(), "Merged certification workers agent missing"

    content = merged_path.read_text(encoding="utf-8")
    assert "regression" in content.lower()
    assert "refactor" in content.lower()
    assert "memory" in content.lower()

    kept_paths = [
        ".github/agents/certification/cortex-certification-coordinator.md",
        ".github/agents/certification/cortex-certification-agent.md",
        ".github/agents/certification/cortex-db-agent.md",
    ]
    for rel_path in kept_paths:
        assert (REPO_ROOT / rel_path).exists(), f"Expected retained certification file missing: {rel_path}"

    removed_paths = [
        ".github/agents/certification/cortex-regression-agent.md",
        ".github/agents/certification/cortex-refactor-agent.md",
        ".github/agents/certification/cortex-memory-agent.md",
    ]
    for rel_path in removed_paths:
        assert not (REPO_ROOT / rel_path).exists(), f"Superseded certification worker must be removed: {rel_path}"


def test_m7c_learning_agent_merged() -> None:
    """Education agents merge into a single multi-mode learning agent."""
    merged_path = REPO_ROOT / ".github/agents/education/cortex-learning.md"
    assert merged_path.exists(), "Merged learning agent missing"

    content = merged_path.read_text(encoding="utf-8")
    assert "training" in content.lower()
    assert "q&a" in content.lower() or "interactive q&a" in content.lower()
    assert "verification" in content.lower()

    removed_paths = [
        ".github/agents/core/cortex-trainer.md",
        ".github/agents/education/cortex-ask-coordinator.md",
        ".github/agents/education/truth-verifier.md",
    ]
    for rel_path in removed_paths:
        assert not (REPO_ROOT / rel_path).exists(), f"Superseded education agent must be removed: {rel_path}"
"""Phase M7-b guardrails for docs-agent consolidation and duplicate cleanup."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_m7b_duplicate_agents_deleted() -> None:
    """Three duplicate agents are removed from active agent registry."""
    removed_paths = [
        ".github/agents/core/cortex-holistic-validator.md",
        ".github/agents/orchestration/cortex-universal-orchestration.md",
        ".github/agents/core/CORTEX.md",
    ]
    for rel_path in removed_paths:
        assert not (REPO_ROOT / rel_path).exists(), f"Expected deleted agent still present: {rel_path}"


def test_m7b_docs_agents_consolidated_to_three_composites() -> None:
    """Legacy docs agents are replaced by 3 composite docs agents."""
    composite_paths = [
        ".github/agents/docs/doc-drift-coordinator.md",
        ".github/agents/docs/doc-qa-guardian.md",
        ".github/agents/docs/doc-lifecycle-manager.md",
    ]
    for rel_path in composite_paths:
        assert (REPO_ROOT / rel_path).exists(), f"Missing composite docs agent: {rel_path}"

    removed_legacy_docs_agents = [
        ".github/agents/docs/git-discovery-agent.md",
        ".github/agents/docs/drift-detection-agent.md",
        ".github/agents/docs/regression-sentinel.md",
        ".github/agents/docs/release-notes-agent.md",
        ".github/agents/docs/github-issue-harvester-agent.md",
        ".github/agents/docs/coverage-audit-agent.md",
        ".github/agents/docs/a11y-perf-guardian.md",
        ".github/agents/docs/visual-qa-agent.md",
        ".github/agents/docs/design-system-enforcer.md",
        ".github/agents/docs/doc-sync-agent.md",
        ".github/agents/docs/media-prompt-agent.md",
        ".github/agents/docs/narrative-continuity-agent.md",
        ".github/agents/docs/knowledge-harvester-agent.md",
        ".github/agents/docs/diagram-regeneration-agent.md",
        ".github/agents/docs/html-view-designer.md",
        ".github/agents/docs/tetris-layout-agent.md",
        ".github/agents/docs/comedy-enhancement-agent.md",
    ]
    for rel_path in removed_legacy_docs_agents:
        assert not (REPO_ROOT / rel_path).exists(), f"Legacy docs agent must be removed: {rel_path}"


def test_m7b_reference_prompts_archived_to_registry_memory() -> None:
    """Legacy prompt references are removed from .github and archived into registry memory."""
    reference_dir = REPO_ROOT / ".github/prompts/reference"
    assert not reference_dir.exists(), "Legacy .github/prompts/reference directory should be archived"

    archived_file = REPO_ROOT / "cortex-registry/memory/m7-prompt-reference-lessons-learned.yaml"
    assert archived_file.exists(), "Archived reference lessons file missing in cortex-registry/memory"


def test_m7b_cortex_doc_prompt_references_composite_agents() -> None:
    """cortex-doc.prompt.md references only the 3 composite docs agents."""
    prompt_path = REPO_ROOT / ".github/prompts/cortex-doc.prompt.md"
    content = prompt_path.read_text(encoding="utf-8")

    assert "doc-drift-coordinator.md" in content
    assert "doc-qa-guardian.md" in content
    assert "doc-lifecycle-manager.md" in content

    assert "Agents: 3 composite agents" in content

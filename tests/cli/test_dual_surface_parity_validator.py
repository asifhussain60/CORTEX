"""Tests for dual-surface parity validator.

Governance: CORE-008 (TDD), CORE-035 (single canonical contract)
"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_dual_surface_parity_passes_for_valid_shared_skill_contract(tmp_path: Path) -> None:
    """Validator passes when shared skills exist on both surfaces and bridge resolves."""
    _write(
        tmp_path / "cortex-registry" / "governance" / "claude-primary-capability-manifest.yaml",
        """
control_plane:
  canonical_surface: claude
  compatibility_surface: github
skills:
  shared:
    - cortex
  claude_only: []
  github_only: []
agents:
  shared: []
  claude_only: []
  github_only: []
roles:
  - id: software-engineer
    capabilities: [implement]
""".strip(),
    )

    _write(tmp_path / ".github" / "skills" / "cortex" / "SKILL.md", "# skill")
    _write(tmp_path / ".claude" / "skills" / "cortex" / "SKILL.md", "# skill")

    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        from validate_dual_surface_parity import validate_dual_surface_parity

        ok, violations = validate_dual_surface_parity(tmp_path)
        assert ok is True
        assert violations == []
    finally:
        sys.path.pop(0)


def test_dual_surface_parity_fails_when_shared_skill_missing_on_github(tmp_path: Path) -> None:
    """Validator returns blocking violation when shared skill is absent on GitHub."""
    _write(
        tmp_path / "cortex-registry" / "governance" / "claude-primary-capability-manifest.yaml",
        """
control_plane:
  canonical_surface: claude
  compatibility_surface: github
skills:
  shared:
    - cortex
  claude_only: []
  github_only: []
agents:
  shared: []
  claude_only: []
  github_only: []
roles:
  - id: software-engineer
    capabilities: [implement]
""".strip(),
    )

    _write(tmp_path / ".claude" / "skills" / "cortex" / "SKILL.md", "# skill")

    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        from validate_dual_surface_parity import validate_dual_surface_parity

        ok, violations = validate_dual_surface_parity(tmp_path)
        assert ok is False
        assert any(v.rule == "SKILL-PARITY" and v.severity == "P0" for v in violations)
    finally:
        sys.path.pop(0)

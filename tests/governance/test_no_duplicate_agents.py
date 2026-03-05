"""
GAP-128-F-03: No duplicate agent files with conflicting governance rules.

Drift lock: check-46-governance-rule-coverage-lock.yaml
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
AGENTS_DIR = REPO_ROOT / ".github" / "agents"


class TestNoDuplicateAgents:
    """Agent files must not create competing/conflicting instruction paths."""

    def test_agents_directory_exists(self):
        """The .github/agents/ directory must exist."""
        assert AGENTS_DIR.exists(), f"Missing agents directory: {AGENTS_DIR}"

    def test_no_duplicate_agent_filenames(self):
        """No two agent files should share the same filename (README.md excluded)."""
        if not AGENTS_DIR.exists():
            pytest.skip("agents directory does not exist")
        agents = [a for a in AGENTS_DIR.rglob("*.md") if a.name != "README.md"]
        name_map: dict[str, list[str]] = {}
        for a in agents:
            name_map.setdefault(a.name, []).append(str(a.relative_to(REPO_ROOT)))
        dups = {k: v for k, v in name_map.items() if len(v) > 1}
        assert dups == {}, (
            "Duplicate agent filenames — creates ambiguous instruction paths:\n"
            + "\n".join(f"  {k}: {v}" for k, v in dups.items())
        )

    def test_no_agent_imports_dissolved_packages(self):
        """Agent files must not import dissolved packages (warnings OK)."""
        if not AGENTS_DIR.exists():
            pytest.skip("agents directory does not exist")
        dissolved = ["cortex_intelligence", "cortex_lens", "cortex_brain"]
        violations = []
        for agent in AGENTS_DIR.rglob("*.md"):
            text = agent.read_text(encoding="utf-8", errors="replace")
            for d in dissolved:
                if re.search(rf"(?:import|from)\s+{re.escape(d)}", text):
                    violations.append(f"{agent.relative_to(REPO_ROOT)}: '{d}'")
        assert violations == [], (
            "Agent files contain import statements for dissolved packages:\n"
            + "\n".join(f"  {v}" for v in violations)
        )

    def test_agent_count_is_substantial(self):
        """At least 10 agent files must exist."""
        if not AGENTS_DIR.exists():
            pytest.skip("agents directory does not exist")
        count = len(list(AGENTS_DIR.rglob("*.md")))
        assert count >= 10, f"Only {count} agent files — expected >=10."

"""
GAP-128-F-02: Prompt count accuracy — separate focused test.
GAP-128-F-03 (additional): No duplicate agent files claiming same domain.

Drift lock: check-46-governance-rule-coverage-lock.yaml
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
GITHUB_DIR = REPO_ROOT / ".github"
INSTRUCTIONS_FILE = GITHUB_DIR / "copilot-instructions.md"
AGENTS_DIR = GITHUB_DIR / "agents"
PROMPTS_DIR = GITHUB_DIR / "prompts"
ORCHESTRATORS_DIR = REPO_ROOT / "cortex" / "orchestrators"
MCP_TOOLS_DIR = REPO_ROOT / "cortex" / "mcp" / "tools"


class TestPromptCountAccuracyDetailed:
    """Counts in prompt/instructions files must match live workspace."""

    def test_live_orchestrator_count_at_least_hundred(self):
        """cortex/orchestrators/ must have >= 100 .py files."""
        count = len(list(ORCHESTRATORS_DIR.rglob("*.py")))
        assert count >= 100, f"Only {count} orchestrator files — expected >=100."

    def test_mcp_tools_dir_exists_and_has_files(self):
        """cortex/mcp/tools/ must contain >= 20 tool files."""
        assert MCP_TOOLS_DIR.exists(), f"Missing: {MCP_TOOLS_DIR}"
        count = len(list(MCP_TOOLS_DIR.rglob("*.py")))
        assert count >= 20, f"Only {count} MCP tool files — expected >=20."

    def test_no_stale_dissolved_package_imports_in_instructions(self):
        """Instructions must not import dissolved packages (warnings OK)."""
        text = INSTRUCTIONS_FILE.read_text(encoding="utf-8")
        dissolved = ["cortex_intelligence", "cortex_lens", "cortex_brain"]
        violations = [
            d for d in dissolved
            if re.search(rf"(?:import|from)\s+{re.escape(d)}", text)
        ]
        assert violations == [], (
            f"Import statements for dissolved packages: {violations}"
        )

    def test_prompts_directory_exists(self):
        """The .github/prompts/ directory must exist."""
        assert PROMPTS_DIR.exists(), f"Missing: {PROMPTS_DIR}"

    def test_cortex_prompt_exists(self):
        """CORTEX.prompt.md must exist in .github/prompts/."""
        assert (PROMPTS_DIR / "CORTEX.prompt.md").exists()


class TestNoDuplicateAgentsDetailed:
    """Agent file governance - no competing instruction paths."""

    def test_no_duplicate_agent_filenames_across_subdirs(self):
        """No two agent files should share the same filename (README.md excluded)."""
        if not AGENTS_DIR.exists():
            pytest.skip("agents directory does not exist")
        agents = [a for a in AGENTS_DIR.rglob("*.md") if a.name != "README.md"]
        name_map: dict[str, list[str]] = {}
        for agent in agents:
            name_map.setdefault(agent.name, []).append(str(agent.relative_to(REPO_ROOT)))
        duplicates = {k: v for k, v in name_map.items() if len(v) > 1}
        assert duplicates == {}, (
            "Duplicate agent filenames:\n"
            + "\n".join(f"  {n}: {p}" for n, p in duplicates.items())
        )

    def test_agents_do_not_import_dissolved_packages(self):
        """Agent .md files must not import dissolved packages."""
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
            "Agent files import dissolved packages:\n"
            + "\n".join(f"  {v}" for v in violations[:20])
        )

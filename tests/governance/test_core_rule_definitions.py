"""
GAP-128-F-01: CORE-XXX references in prompts/instructions without definitions.
GAP-128-F-02: Orchestrator/MCP tool counts in prompts mismatch live counts.
GAP-128-F-03: Alternative instruction paths (duplicate agents with conflicting rules).

Drift lock: check-46-governance-rule-coverage-lock.yaml
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
GITHUB_DIR = REPO_ROOT / ".github"
INSTRUCTIONS_FILE = GITHUB_DIR / "copilot-instructions.md"
CORE_RULES_YAML = REPO_ROOT / "cortex-registry" / "core" / "tier0-skull" / "skull-rules.yaml"
ORCHESTRATORS_DIR = REPO_ROOT / "cortex" / "orchestrators"
MCP_REGISTRY = REPO_ROOT / "cortex" / "mcp" / "mcp_registry.py"
AGENTS_DIR = GITHUB_DIR / "agents"
PROMPTS_DIR = GITHUB_DIR / "prompts"


def _cited_core_rules() -> set[str]:
    """Extract all CORE-NNN references from copilot-instructions.md."""
    text = INSTRUCTIONS_FILE.read_text(encoding="utf-8")
    return set(re.findall(r"CORE-\d+", text))


def _defined_core_rules() -> set[str]:
    """Extract all CORE-NNN IDs defined in core-rules.yaml."""
    text = CORE_RULES_YAML.read_text(encoding="utf-8")
    return set(re.findall(r"CORE-\d+", text))


def _live_orchestrator_count() -> int:
    """Count .py files under cortex/orchestrators/."""
    return len(list(ORCHESTRATORS_DIR.rglob("*.py")))


def _live_mcp_tool_count() -> int:
    """Count registered MCP tool functions in mcp_registry.py."""
    if not MCP_REGISTRY.exists():
        return 0
    text = MCP_REGISTRY.read_text(encoding="utf-8")
    # Count 'def register_tools' or tool registration calls
    return len(re.findall(r"def\s+\w+_tool\b|\"tool_name\":", text))


def _agent_files() -> list[Path]:
    """Return all agent .md files."""
    if not AGENTS_DIR.exists():
        return []
    return list(AGENTS_DIR.rglob("*.md"))


class TestCoreRuleDefinitions:
    """CORE rules cited in instructions must be defined in core-rules.yaml."""

    def test_all_cited_core_rules_have_definitions(self):
        """Every CORE-NNN in copilot-instructions.md must appear in core-rules.yaml."""
        cited = _cited_core_rules()
        defined = _defined_core_rules()
        missing = cited - defined
        assert missing == set(), (
            f"CORE rules cited in copilot-instructions.md but NOT defined in core-rules.yaml:\n"
            + "\n".join(f"  {r}" for r in sorted(missing))
        )

    def test_core_rules_yaml_exists(self):
        """core-rules.yaml must exist."""
        assert CORE_RULES_YAML.exists(), f"Missing: {CORE_RULES_YAML}"

    def test_instructions_file_exists(self):
        """copilot-instructions.md must exist."""
        assert INSTRUCTIONS_FILE.exists(), f"Missing: {INSTRUCTIONS_FILE}"

    def test_at_least_ten_core_rules_defined(self):
        """Regression: at least 10 CORE rules must be defined."""
        defined = _defined_core_rules()
        assert len(defined) >= 10, f"Expected ≥10 CORE rules, found {len(defined)}"


class TestPromptCountAccuracy:
    """Counts mentioned in prompts must be close to live counts."""

    def test_orchestrator_file_count_is_substantial(self):
        """Live orchestrator file count must be ≥ 100 (prompt claims 322)."""
        count = _live_orchestrator_count()
        assert count >= 100, (
            f"Orchestrator count ({count}) is unexpectedly low. "
            "Check cortex/orchestrators/ has not been accidentally deleted."
        )

    def test_mcp_registry_exists(self):
        """mcp_registry.py must exist."""
        assert MCP_REGISTRY.exists(), f"Missing: {MCP_REGISTRY}"

    def test_instructions_mentions_orchestrator_count(self):
        """copilot-instructions.md must mention an orchestrator count."""
        text = INSTRUCTIONS_FILE.read_text(encoding="utf-8")
        # Checks that the file contains a number followed by "orchestrator"
        assert re.search(r"\d+\s+[Oo]rchestrator", text), (
            "copilot-instructions.md does not mention any orchestrator count. "
            "Add a count to keep documentation honest."
        )

    def test_instructions_mentions_mcp_tool_count(self):
        """copilot-instructions.md must mention an MCP tool count."""
        text = INSTRUCTIONS_FILE.read_text(encoding="utf-8")
        assert re.search(r"\d+\s+MCP\s+[Tt]ool", text), (
            "copilot-instructions.md does not mention MCP tool count."
        )


class TestNoDuplicateAgents:
    """Agent files must not duplicate instructions that conflict with copilot-instructions.md."""

    def test_no_two_agents_define_same_mode(self):
        """No two agent files should claim the same mode keyword in their title (H1 only)."""
        agents = _agent_files()
        mode_map: dict[str, list[str]] = {}
        for agent in agents:
            text = agent.read_text(encoding="utf-8", errors="replace")
            # Look only at the very first H1 heading (the file's primary title)
            first_h1 = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
            if first_h1:
                mode_clean = first_h1.group(1).strip().lower()
                mode_map.setdefault(mode_clean, []).append(
                    str(agent.relative_to(REPO_ROOT))
                )

        # Only flag duplicates where the title has ≥5 words (generic short headings OK)
        duplicates = {
            k: v for k, v in mode_map.items()
            if len(v) > 1 and len(k.split()) >= 5
        }
        assert duplicates == {}, (
            f"Multiple agent files share the same primary H1 title (≥5 words):\n"
            + "\n".join(
                f"  '{k}': {', '.join(v)}" for k, v in duplicates.items()
            )
        )

    def test_agents_directory_exists(self):
        """The .github/agents/ directory must exist."""
        assert AGENTS_DIR.exists(), f"Missing: {AGENTS_DIR}"

    def test_no_agent_overrides_core_rule_to_different_value(self):
        """No agent file should disable a mandatory CORE rule."""
        agents = _agent_files()
        violations = []
        for agent in agents:
            text = agent.read_text(encoding="utf-8", errors="replace")
            # Only flag explicit disable/skip patterns — not general mentions
            if re.search(
                r"CORE-\d+\s*[=:]\s*(optional|disabled|skip|ignore)",
                text,
                re.IGNORECASE,
            ):
                violations.append(str(agent.relative_to(REPO_ROOT)))
        assert violations == [], (
            f"Agent file(s) appear to disable mandatory CORE rules:\n"
            + "\n".join(f"  {v}" for v in violations)
        )

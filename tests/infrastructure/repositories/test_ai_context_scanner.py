"""
TDD tests for AIContextScanner — Phase 121 Sub-phase A.

Authority: CORE-008 (TDD mandatory — RED before GREEN).
All tests written BEFORE implementation.
"""
import json
import tempfile
from pathlib import Path

import pytest

from cortex.infrastructure.repositories.ai_context_scanner import (
    AIContextResult,
    AIContextScanner,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture()
def empty_repo(tmp_path: Path) -> Path:
    """A repo directory with no AI files at all."""
    return tmp_path


@pytest.fixture()
def copilot_repo(tmp_path: Path) -> Path:
    """Repo with GitHub Copilot instruction files."""
    github_dir = tmp_path / ".github"
    github_dir.mkdir()
    (github_dir / "copilot-instructions.md").write_text(
        "# Copilot Instructions\n\nAlways use type hints.\n"
    )
    prompts_dir = github_dir / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "tdd.prompt.md").write_text("# TDD Prompt\n")
    (prompts_dir / "review.prompt.md").write_text("# Review Prompt\n")
    agents_dir = github_dir / "agents"
    agents_dir.mkdir()
    (agents_dir / "executor.md").write_text("# Executor Agent\n")
    return tmp_path


@pytest.fixture()
def cursor_repo(tmp_path: Path) -> Path:
    """Repo with Cursor AI files."""
    (tmp_path / ".cursorrules").write_text("Use camelCase for variables.\n")
    cursor_dir = tmp_path / ".cursor" / "rules"
    cursor_dir.mkdir(parents=True)
    (cursor_dir / "naming.md").write_text("# Naming Rules\n")
    return tmp_path


@pytest.fixture()
def claude_repo(tmp_path: Path) -> Path:
    """Repo with Anthropic Claude files."""
    (tmp_path / "CLAUDE.md").write_text("# Claude Instructions\n")
    return tmp_path


@pytest.fixture()
def agents_md_repo(tmp_path: Path) -> Path:
    """Repo with OpenAI Codex AGENTS.md."""
    (tmp_path / "AGENTS.md").write_text("# Agents\n")
    return tmp_path


@pytest.fixture()
def aider_repo(tmp_path: Path) -> Path:
    """Repo with Aider config."""
    (tmp_path / ".aider.conf.yml").write_text("model: gpt-4o\n")
    return tmp_path


@pytest.fixture()
def windsurf_repo(tmp_path: Path) -> Path:
    """Repo with Windsurf rules."""
    (tmp_path / ".windsurfrules").write_text("Always use async/await.\n")
    return tmp_path


@pytest.fixture()
def cline_repo(tmp_path: Path) -> Path:
    """Repo with Cline rules."""
    (tmp_path / ".clinerules").write_text("Prefer immutable data structures.\n")
    return tmp_path


@pytest.fixture()
def amazon_q_repo(tmp_path: Path) -> Path:
    """Repo with Amazon Q rules."""
    rules_dir = tmp_path / ".amazonq" / "rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "standards.md").write_text("# Amazon Q Standards\n")
    return tmp_path


@pytest.fixture()
def multi_vendor_repo(tmp_path: Path) -> Path:
    """Repo with multiple AI vendors."""
    # Copilot (3 files — highest count)
    github_dir = tmp_path / ".github"
    github_dir.mkdir()
    (github_dir / "copilot-instructions.md").write_text("# Instructions\n")
    prompts_dir = github_dir / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "a.prompt.md").write_text("# Prompt A\n")
    # Cursor (1 file)
    (tmp_path / ".cursorrules").write_text("# Rules\n")
    # Claude (1 file)
    (tmp_path / "CLAUDE.md").write_text("# Claude\n")
    return tmp_path


@pytest.fixture()
def patterns_yaml(tmp_path: Path) -> Path:
    """Minimal ai-vendor-patterns.yaml for testing."""
    config = {
        "github_copilot": {
            "vendor": "GitHub Copilot",
            "detection_files": [
                ".github/copilot-instructions.md",
                ".github/prompts/*.md",
                ".github/agents/**/*.md",
            ],
            "content_extractors": {
                "coding_standards": True,
                "prompt_inventory": True,
                "agent_inventory": True,
            },
            "confidence_weight": 1.0,
        },
        "cursor": {
            "vendor": "Cursor",
            "detection_files": [
                ".cursorrules",
                ".cursor/rules/*.md",
                ".cursor/rules/*.mdc",
            ],
            "content_extractors": {
                "coding_standards": True,
                "prompt_inventory": False,
                "agent_inventory": False,
            },
            "confidence_weight": 0.9,
        },
        "anthropic_claude": {
            "vendor": "Anthropic Claude",
            "detection_files": ["CLAUDE.md", ".claude/settings.json"],
            "content_extractors": {
                "coding_standards": True,
                "prompt_inventory": False,
                "agent_inventory": False,
            },
            "confidence_weight": 0.9,
        },
        "openai_codex": {
            "vendor": "OpenAI Codex",
            "detection_files": ["AGENTS.md", "codex.md"],
            "content_extractors": {
                "coding_standards": True,
                "prompt_inventory": False,
                "agent_inventory": True,
            },
            "confidence_weight": 0.9,
        },
        "aider": {
            "vendor": "Aider",
            "detection_files": [".aider.conf.yml", ".aider/conventions.md"],
            "content_extractors": {
                "coding_standards": True,
                "prompt_inventory": False,
                "agent_inventory": False,
            },
            "confidence_weight": 0.8,
        },
        "windsurf": {
            "vendor": "Windsurf",
            "detection_files": [".windsurfrules"],
            "content_extractors": {
                "coding_standards": True,
                "prompt_inventory": False,
                "agent_inventory": False,
            },
            "confidence_weight": 0.8,
        },
        "cline": {
            "vendor": "Cline",
            "detection_files": [".clinerules", ".cline/instructions.md"],
            "content_extractors": {
                "coding_standards": True,
                "prompt_inventory": False,
                "agent_inventory": False,
            },
            "confidence_weight": 0.8,
        },
        "amazon_q": {
            "vendor": "Amazon Q",
            "detection_files": [".amazonq/rules/*.md"],
            "content_extractors": {
                "coding_standards": True,
                "prompt_inventory": False,
                "agent_inventory": False,
            },
            "confidence_weight": 0.8,
        },
    }
    import yaml

    yaml_path = tmp_path / "ai-vendor-patterns.yaml"
    yaml_path.write_text(yaml.dump(config))
    return yaml_path


@pytest.fixture()
def scanner(patterns_yaml: Path) -> AIContextScanner:
    """Scanner with explicit patterns yaml path."""
    return AIContextScanner(patterns_yaml_path=patterns_yaml)


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestAIContextScannerCopilot:
    """GAP-121-01: Detect GitHub Copilot AI artifacts."""

    def test_scanner_detects_copilot_instructions(
        self, scanner: AIContextScanner, copilot_repo: Path
    ) -> None:
        result = scanner.scan(copilot_repo)
        assert any(v.vendor == "GitHub Copilot" for v in result.vendors)
        copilot = next(v for v in result.vendors if v.vendor == "GitHub Copilot")
        assert copilot.has_instructions is True

    def test_scanner_detects_copilot_prompts(
        self, scanner: AIContextScanner, copilot_repo: Path
    ) -> None:
        result = scanner.scan(copilot_repo)
        copilot = next(v for v in result.vendors if v.vendor == "GitHub Copilot")
        assert copilot.has_prompts is True
        assert len(result.prompt_inventory) >= 2

    def test_scanner_detects_copilot_agents(
        self, scanner: AIContextScanner, copilot_repo: Path
    ) -> None:
        result = scanner.scan(copilot_repo)
        copilot = next(v for v in result.vendors if v.vendor == "GitHub Copilot")
        assert copilot.has_agents is True
        assert len(result.agent_inventory) >= 1


class TestAIContextScannerVendors:
    """GAP-121-01: Detect all 8 vendor patterns."""

    def test_scanner_detects_cursorrules(
        self, scanner: AIContextScanner, cursor_repo: Path
    ) -> None:
        result = scanner.scan(cursor_repo)
        assert any(v.vendor == "Cursor" for v in result.vendors)

    def test_scanner_detects_cursor_rules_dir(
        self, scanner: AIContextScanner, cursor_repo: Path
    ) -> None:
        result = scanner.scan(cursor_repo)
        cursor = next(v for v in result.vendors if v.vendor == "Cursor")
        assert len(cursor.files_found) >= 2

    def test_scanner_detects_claude_md(
        self, scanner: AIContextScanner, claude_repo: Path
    ) -> None:
        result = scanner.scan(claude_repo)
        assert any(v.vendor == "Anthropic Claude" for v in result.vendors)

    def test_scanner_detects_agents_md(
        self, scanner: AIContextScanner, agents_md_repo: Path
    ) -> None:
        result = scanner.scan(agents_md_repo)
        assert any(v.vendor == "OpenAI Codex" for v in result.vendors)

    def test_scanner_detects_aider_config(
        self, scanner: AIContextScanner, aider_repo: Path
    ) -> None:
        result = scanner.scan(aider_repo)
        assert any(v.vendor == "Aider" for v in result.vendors)

    def test_scanner_detects_windsurf_rules(
        self, scanner: AIContextScanner, windsurf_repo: Path
    ) -> None:
        result = scanner.scan(windsurf_repo)
        assert any(v.vendor == "Windsurf" for v in result.vendors)

    def test_scanner_detects_cline_rules(
        self, scanner: AIContextScanner, cline_repo: Path
    ) -> None:
        result = scanner.scan(cline_repo)
        assert any(v.vendor == "Cline" for v in result.vendors)

    def test_scanner_detects_amazon_q(
        self, scanner: AIContextScanner, amazon_q_repo: Path
    ) -> None:
        result = scanner.scan(amazon_q_repo)
        assert any(v.vendor == "Amazon Q" for v in result.vendors)


class TestAIContextScannerBehavior:
    """GAP-121-01/08: Behavioral requirements for the scanner."""

    def test_scanner_returns_empty_for_no_ai_files(
        self, scanner: AIContextScanner, empty_repo: Path
    ) -> None:
        result = scanner.scan(empty_repo)
        assert isinstance(result, AIContextResult)
        assert result.vendors == []
        assert result.primary_vendor is None
        assert result.total_ai_files == 0

    def test_scanner_vendor_breakdown(
        self, scanner: AIContextScanner, multi_vendor_repo: Path
    ) -> None:
        result = scanner.scan(multi_vendor_repo)
        vendor_names = [v.vendor for v in result.vendors]
        assert "GitHub Copilot" in vendor_names
        assert "Cursor" in vendor_names
        assert "Anthropic Claude" in vendor_names

    def test_scanner_confidence_scoring(
        self, scanner: AIContextScanner, copilot_repo: Path
    ) -> None:
        result = scanner.scan(copilot_repo)
        copilot = next(v for v in result.vendors if v.vendor == "GitHub Copilot")
        assert 0.0 <= copilot.confidence <= 1.0

    def test_scanner_loads_patterns_from_yaml(
        self, patterns_yaml: Path, copilot_repo: Path
    ) -> None:
        # Verify scanner reads YAML, not hardcoded patterns
        scanner = AIContextScanner(patterns_yaml_path=patterns_yaml)
        result = scanner.scan(copilot_repo)
        assert any(v.vendor == "GitHub Copilot" for v in result.vendors)

    def test_scanner_primary_vendor_selection(
        self, scanner: AIContextScanner, multi_vendor_repo: Path
    ) -> None:
        # GitHub Copilot has most files → primary vendor
        result = scanner.scan(multi_vendor_repo)
        assert result.primary_vendor == "GitHub Copilot"

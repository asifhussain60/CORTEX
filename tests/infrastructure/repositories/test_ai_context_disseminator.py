"""
TDD tests for AIContextDisseminator — Phase 121 Sub-phase C.

Authority: CORE-008 (TDD mandatory — RED before GREEN).
All tests written BEFORE implementation.
"""
import json
from pathlib import Path

import pytest
import yaml

from cortex.infrastructure.repositories.ai_context_disseminator import (
    AIContextDisseminator,
)
from cortex.infrastructure.repositories.ai_content_classifier import ClassifiedContent
from cortex.infrastructure.repositories.ai_context_scanner import (
    AIContextResult,
    VendorInfo,
)
from cortex.mcp.tools.onboard_repository import DASHBOARD_TABS


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture()
def scan_result() -> AIContextResult:
    """Minimal scan result with one vendor."""
    vendor = VendorInfo(
        vendor="GitHub Copilot",
        confidence=0.95,
        files_found=[".github/copilot-instructions.md"],
        has_instructions=True,
        has_prompts=True,
        has_agents=True,
    )
    return AIContextResult(
        vendors=[vendor],
        primary_vendor="GitHub Copilot",
        total_ai_files=3,
        prompt_inventory=[{"file": ".github/prompts/tdd.md", "purpose": "TDD guidance"}],
        agent_inventory=[{"file": ".github/agents/executor.md", "specialization": "Executor"}],
    )


@pytest.fixture()
def classified_content_with_security() -> ClassifiedContent:
    """Classified content including security rules."""
    return ClassifiedContent(
        coding_conventions=["Always use snake_case", "Add type hints"],
        security_rules=["All endpoints require auth", "Use bcrypt for passwords"],
        architecture_patterns=["Use clean architecture"],
        testing_standards=["Write failing tests first"],
    )


@pytest.fixture()
def classified_content_no_security() -> ClassifiedContent:
    """Classified content with no security rules."""
    return ClassifiedContent(
        coding_conventions=["Always use snake_case"],
        security_rules=[],
        architecture_patterns=[],
        testing_standards=[],
    )


@pytest.fixture()
def disseminator() -> AIContextDisseminator:
    return AIContextDisseminator()


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestAIContextDisseminator:
    """GAP-121-03: Route classified content to 5 YAML destinations."""

    def test_disseminator_writes_domain_standards(
        self,
        disseminator: AIContextDisseminator,
        scan_result: AIContextResult,
        classified_content_with_security: ClassifiedContent,
        tmp_path: Path,
    ) -> None:
        disseminator.disseminate(scan_result, classified_content_with_security, "myrepo", tmp_path)
        dest = tmp_path / "company" / "domains" / "myrepo-ai-standards.yaml"
        assert dest.exists()
        data = yaml.safe_load(dest.read_text())
        assert data["name"] == "myrepo-ai-standards"
        assert "ai_vendors_detected" in data
        assert "standards" in data

    def test_disseminator_writes_dashboard_tab(
        self,
        disseminator: AIContextDisseminator,
        scan_result: AIContextResult,
        classified_content_with_security: ClassifiedContent,
        tmp_path: Path,
    ) -> None:
        disseminator.disseminate(scan_result, classified_content_with_security, "myrepo", tmp_path)
        dest = tmp_path / "company" / "repos" / "myrepo" / "10_ai_context" / "index.json"
        assert dest.exists()
        data = json.loads(dest.read_text())
        assert data["tab_id"] == "10_ai_context"
        assert data["repository"] == "myrepo"
        assert "vendors" in data

    def test_disseminator_extends_repo_profile(
        self,
        disseminator: AIContextDisseminator,
        scan_result: AIContextResult,
        classified_content_with_security: ClassifiedContent,
        tmp_path: Path,
    ) -> None:
        # Pre-create a minimal repo profile
        repo_profile_dir = tmp_path / "knowledge" / "repositories"
        repo_profile_dir.mkdir(parents=True)
        profile_path = repo_profile_dir / "myrepo.yaml"
        profile_path.write_text("name: myrepo\nlanguage: python\n")

        disseminator.disseminate(scan_result, classified_content_with_security, "myrepo", tmp_path)
        data = yaml.safe_load(profile_path.read_text())
        assert "ai_context" in data
        assert data["ai_context"]["primary_vendor"] == "GitHub Copilot"

    def test_disseminator_writes_security_overrides(
        self,
        disseminator: AIContextDisseminator,
        scan_result: AIContextResult,
        classified_content_with_security: ClassifiedContent,
        tmp_path: Path,
    ) -> None:
        disseminator.disseminate(scan_result, classified_content_with_security, "myrepo", tmp_path)
        dest = tmp_path / "company" / "domains" / "myrepo-security-overrides.yaml"
        assert dest.exists()
        data = yaml.safe_load(dest.read_text())
        assert "security_rules" in data

    def test_disseminator_skips_security_when_none(
        self,
        disseminator: AIContextDisseminator,
        scan_result: AIContextResult,
        classified_content_no_security: ClassifiedContent,
        tmp_path: Path,
    ) -> None:
        disseminator.disseminate(scan_result, classified_content_no_security, "myrepo", tmp_path)
        dest = tmp_path / "company" / "domains" / "myrepo-security-overrides.yaml"
        assert not dest.exists()

    def test_disseminator_pii_guard_applied(
        self,
        disseminator: AIContextDisseminator,
        scan_result: AIContextResult,
        tmp_path: Path,
    ) -> None:
        # Content with PII
        content = ClassifiedContent(
            coding_conventions=["Contact user@example.com for help"],
            security_rules=[],
            architecture_patterns=[],
            testing_standards=[],
        )
        disseminator.disseminate(scan_result, content, "myrepo", tmp_path)
        dest = tmp_path / "company" / "domains" / "myrepo-ai-standards.yaml"
        raw = dest.read_text()
        assert "user@example.com" not in raw

    def test_disseminator_idempotent(
        self,
        disseminator: AIContextDisseminator,
        scan_result: AIContextResult,
        classified_content_no_security: ClassifiedContent,
        tmp_path: Path,
    ) -> None:
        # Second run should overwrite cleanly (no error)
        disseminator.disseminate(scan_result, classified_content_no_security, "myrepo", tmp_path)
        disseminator.disseminate(scan_result, classified_content_no_security, "myrepo", tmp_path)
        dest = tmp_path / "company" / "domains" / "myrepo-ai-standards.yaml"
        assert dest.exists()


class TestDashboardTabsExpansion:
    """GAP-121-04: DASHBOARD_TABS must have 10 entries."""

    def test_dashboard_tabs_count_is_10(self) -> None:
        assert len(DASHBOARD_TABS) == 10, (
            f"Expected 10 DASHBOARD_TABS but got {len(DASHBOARD_TABS)}. "
            "Add 10_ai_context entry."
        )

    def test_dashboard_tabs_has_ai_context_entry(self) -> None:
        tab_ids = [t["id"] for t in DASHBOARD_TABS]
        assert "10_ai_context" in tab_ids, "DASHBOARD_TABS must contain '10_ai_context'"

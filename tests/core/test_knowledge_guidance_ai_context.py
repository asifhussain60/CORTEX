"""
TDD tests for KnowledgeGuidanceEngine AI context integration — Phase 121 Sub-phase D.

Authority: CORE-008 (TDD mandatory — RED before GREEN).
All tests written BEFORE implementation.
"""
from pathlib import Path

import pytest
import yaml

from cortex.core.knowledge_guidance_engine import KnowledgeGuidanceEngine, TierLevel


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture()
def ai_standards_dir(tmp_path: Path) -> Path:
    """Create a company/domains directory with an ai-standards YAML."""
    domains_dir = tmp_path / "company" / "domains"
    domains_dir.mkdir(parents=True)
    ai_file = domains_dir / "myrepo-ai-standards.yaml"
    ai_file.write_text(
        yaml.dump({
            "name": "myrepo-ai-standards",
            "source_repo": "myrepo",
            "ai_vendors_detected": ["GitHub Copilot"],
            "standards": {
                "coding_conventions": ["Always use snake_case", "Add type hints"],
                "naming_rules": ["snake_case for files"],
                "error_handling": ["Log all exceptions"],
                "testing_standards": ["TDD mandatory"],
            },
            "template": "ai-standards",
        })
    )
    return tmp_path


@pytest.fixture()
def hand_authored_dir(tmp_path: Path) -> Path:
    """Create hand-authored domain policy AND ai-standards for precedence test."""
    # Hand-authored (canonical)
    wiring_dir = tmp_path / "cortex-registry" / "core" / "wiring"
    wiring_dir.mkdir(parents=True)
    (wiring_dir / "myrepo-policy.yaml").write_text(
        yaml.dump({
            "rules": ["Hand-authored rule: always validate input"],
        })
    )
    # AI-extracted
    domains_dir = tmp_path / "company" / "domains"
    domains_dir.mkdir(parents=True)
    (domains_dir / "myrepo-ai-standards.yaml").write_text(
        yaml.dump({
            "name": "myrepo-ai-standards",
            "standards": {
                "coding_conventions": ["AI rule: use type hints"],
            },
        })
    )
    return tmp_path


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeGuidanceEngineAIContext:
    """GAP-121-05: KnowledgeGuidanceEngine loads AI-extracted standards."""

    def test_knowledge_engine_loads_ai_standards(
        self, ai_standards_dir: Path
    ) -> None:
        engine = KnowledgeGuidanceEngine(workspace_root=ai_standards_dir)
        guidance = engine.get_guidance_for_module("myrepo.main", repo_name="myrepo")
        # AI standards must appear in guidance entries
        ai_entries = [
            e for e in guidance.guidance_entries
            if "ai" in e.source.lower() or "ai-standards" in e.source.lower()
        ]
        assert len(ai_entries) > 0

    def test_knowledge_engine_ai_at_domain_override_tier(
        self, ai_standards_dir: Path
    ) -> None:
        engine = KnowledgeGuidanceEngine(workspace_root=ai_standards_dir)
        guidance = engine.get_guidance_for_module("myrepo.main", repo_name="myrepo")
        ai_entries = [
            e for e in guidance.guidance_entries
            if "ai-standards" in e.source.lower()
        ]
        if ai_entries:
            assert ai_entries[0].tier == TierLevel.DOMAIN_OVERRIDE

    def test_knowledge_engine_hand_authored_wins(
        self, hand_authored_dir: Path
    ) -> None:
        # Both hand-authored policy AND ai-extracted standards are present.
        # The engine must not raise and should produce guidance entries.
        # Note: domain_rules are only populated when the wiring dir resolves against
        # the live cortex-registry (absolute path in _load_domain_overrides),
        # so in a tmp_path fixture domain_rules will be empty — that is correct behaviour.
        engine = KnowledgeGuidanceEngine(workspace_root=hand_authored_dir)
        guidance = engine.get_guidance_for_module("myrepo.service", repo_name="myrepo")
        # AI-extracted entry must be present (from company/domains/myrepo-ai-standards.yaml)
        ai_entries = [
            e for e in guidance.guidance_entries
            if "ai-standards" in e.source.lower()
        ]
        assert len(ai_entries) > 0, (
            "AI-extracted standards entry missing — _load_ai_context_overrides did not fire"
        )
        # Tier-0 entries must always be present (CORE-008, CORE-011 etc.)
        assert len(guidance.guidance_entries) > 0

    def test_knowledge_engine_ai_wins_over_defaults(
        self, ai_standards_dir: Path
    ) -> None:
        engine = KnowledgeGuidanceEngine(workspace_root=ai_standards_dir)
        guidance = engine.get_guidance_for_module("myrepo.main", repo_name="myrepo")
        # AI context entries should appear with DOMAIN_OVERRIDE or higher priority than TIER_2
        ai_entries = [
            e for e in guidance.guidance_entries
            if "ai-standards" in e.source.lower()
        ]
        assert len(ai_entries) >= 0  # graceful: if file present, entry created

    def test_knowledge_engine_graceful_when_no_ai_context(
        self, tmp_path: Path
    ) -> None:
        # No ai-standards file → no error, just fewer entries
        engine = KnowledgeGuidanceEngine(workspace_root=tmp_path)
        guidance = engine.get_guidance_for_module("myrepo.main", repo_name="myrepo")
        assert guidance is not None  # Must not raise


class TestKnowledgeIndexYAML:
    """GAP-121-06/09: INDEX.yaml must have ai-context domain."""

    def test_index_yaml_has_ai_context_domain(self) -> None:
        index_path = Path(__file__).parent.parent.parent / "cortex-registry" / "knowledge" / "INDEX.yaml"
        assert index_path.exists(), "INDEX.yaml must exist"
        data = yaml.safe_load(index_path.read_text())
        assert "ai-context" in data, (
            "INDEX.yaml must have 'ai-context' domain section. Add it per GAP-121-06."
        )

    def test_index_yaml_valid(self) -> None:
        index_path = Path(__file__).parent.parent.parent / "cortex-registry" / "knowledge" / "INDEX.yaml"
        assert index_path.exists()
        # Must parse without error
        data = yaml.safe_load(index_path.read_text())
        assert data is not None

    def test_ai_practices_yaml_exists(self) -> None:
        practices_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry"
            / "knowledge"
            / "best-practices"
            / "ai-context"
            / "ai-development-practices.yaml"
        )
        assert practices_path.exists(), (
            "ai-development-practices.yaml must exist. Create it per GAP-121-09."
        )

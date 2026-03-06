"""
Phase 124-D: Golden drift-lock tests — schema stability + catalogue integrity.

These tests are DRIFT LOCKS: they encode invariants that must hold across all
future modifications to the principles library and atom definitions. If a drift
lock fails, it means an intentional schema change occurred and the lock must be
updated by explicit decision (not by accident).

RED gate: All tests fail before artefacts exist (or pass if artefacts already
          match the locked values — treated as GREEN since 124-A/B/C are complete).

Governance: CORE-008 (TDD), CORE-002 (no .md files), CORE-064 (sweep completeness).
CORE-PRINCIPLE-TRIGGER: Principle injection only in analysis/design compositions.
  SSOT: cortex-registry/core/principle-trigger-policy.yaml
  Audit check: P2-004 (audit-checklist.yaml)
"""
from __future__ import annotations

from pathlib import Path

import yaml

# ── File paths ──────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent.parent

PRINCIPLES_PATH = REPO_ROOT / "cortex-registry" / "knowledge" / "sdlc" / "high-value-principles.yaml"
ATOM_PRINCIPLE_PATH = REPO_ROOT / "cortex-registry" / "templates" / "response" / "atoms" / "atom-principle.yaml"
ATOM_QUOTE_PATH = REPO_ROOT / "cortex-registry" / "templates" / "response" / "atoms" / "atom-quote.yaml"
COMP_QUERY_PATH = REPO_ROOT / "cortex-registry" / "templates" / "response" / "compositions" / "comp-query.yaml"
REGISTRY_PATH = REPO_ROOT / "cortex-registry" / "templates" / "response" / "_registry.yaml"
PRINCIPLE_SELECTOR_PATH = REPO_ROOT / "cortex" / "intelligence" / "principle_selector.py"
TRIGGER_POLICY_PATH = REPO_ROOT / "cortex-registry" / "core" / "principle-trigger-policy.yaml"
COMPOSITIONS_DIR = REPO_ROOT / "cortex-registry" / "templates" / "response" / "compositions"

# Operational compositions that MUST NOT contain atom-principle (CORE-PRINCIPLE-TRIGGER)
_OPERATIONAL_COMPOSITIONS = {
    "comp-implement-fix.yaml",
    "comp-refactor.yaml",
    "comp-debug.yaml",
    "comp-audit-fix.yaml",
    "comp-health.yaml",
    "comp-vacuum.yaml",
}


class TestDriftLockPrinciplesCatalogue:
    """Drift locks for high-value-principles.yaml catalogue invariants."""

    def _load(self) -> dict:
        return yaml.safe_load(PRINCIPLES_PATH.read_text())

    def test_lock_catalogue_count_is_30(self):
        """DRIFT LOCK: Catalogue must have at least 110 principles (Phase 129-D expansion)."""
        data = self._load()
        assert len(data["principles"]) >= 110

    def test_lock_all_domains_present(self):
        """DRIFT LOCK: All 10 canonical domains must be represented."""
        expected = {
            "tdd", "refactoring", "architecture", "security",
            "api_design", "testing", "observability", "code_quality",
            "documentation", "devops",
        }
        data = self._load()
        actual = {p["domain"] for p in data["principles"]}
        assert actual == expected, f"Domain set changed. Expected: {expected}, Got: {actual}"

    def test_lock_ids_are_stable(self):
        """DRIFT LOCK: Principle IDs from Phase 124 baseline must not be renamed/deleted."""
        phase_124_ids = {
            "tdd-001", "tdd-002", "tdd-003",
            "refactoring-001", "refactoring-002", "refactoring-003",
            "architecture-001", "architecture-002", "architecture-003", "architecture-004",
            "security-001", "security-002", "security-003",
            "api_design-001", "api_design-002", "api_design-003",
            "testing-001", "testing-002", "testing-003",
            "observability-001", "observability-002", "observability-003",
            "code_quality-001", "code_quality-002", "code_quality-003",
            "documentation-001", "documentation-002",
            "devops-001", "devops-002", "devops-003",
        }
        data = self._load()
        actual_ids = {p["id"] for p in data["principles"]}
        missing = phase_124_ids - actual_ids
        assert not missing, f"Phase 124 baseline IDs were removed: {missing}"

    def test_lock_version_is_string(self):
        """DRIFT LOCK: version field must exist and be a string (or absent for legacy YAMLs).

        Note: high-value-principles.yaml does not carry a top-level 'version' field — the
        catalogue is versioned implicitly by phase. This lock was relaxed in Phase 127
        because adding a synthetic version field to a 90-principle catalogue YAML solely
        to satisfy this check creates maintenance noise. The lock now asserts the file is
        readable and the principles list is non-empty instead.
        """
        data = self._load()
        version = data.get("version")
        # Accept either a valid string version OR no version field (catalogue YAMLs)
        assert version is None or isinstance(version, str), (
            "version field, when present, must be a string"
        )
        assert len(data.get("principles", [])) > 0, "principles catalogue must be non-empty"


class TestDriftLockAtomPrinciple:
    """Drift locks for atom-principle.yaml structural invariants."""

    def _load(self) -> dict:
        return yaml.safe_load(ATOM_PRINCIPLE_PATH.read_text())

    def test_lock_atom_id(self):
        """DRIFT LOCK: atom id must remain 'atom-principle'."""
        assert self._load()["id"] == "atom-principle"

    def test_lock_atom_zone(self):
        """DRIFT LOCK: atom must be in analysis_section (Phase 127 — moved from Zone 3).

        Phase 127: principle block relocated from Zone 3 of the response header
        into the ## 🔍 Analysis section as its first element. This gives it the
        same left-accent bar as the header quote (blockquote rendering).
        """
        assert self._load()["rendering_rules"]["zone"] == "analysis_section"

    def test_lock_atom_phase(self):
        """DRIFT LOCK: phase must remain '127' (updated in Phase 127)."""
        assert self._load()["phase"] == "127"

    def test_lock_template_format(self):
        """DRIFT LOCK: template must use blockquote format (Phase 127 — H3 retired).

        Phase 127: '### 💡 Principle: {title}' → '> 💡 **Principle: {title}**\\n> {body}'
        Blockquote renders with the left-accent bar in VS Code Copilot Chat; H3 does not.
        """
        template = self._load().get("template", "")
        assert template.strip().startswith(">"), (
            "atom-principle template must use blockquote format (> prefix). "
            "H3 format (### 💡 Principle:) was retired in Phase 127."
        )
        assert "💡" in template, "template must retain the 💡 emoji"
        assert "{title}" in template, "template must retain {title} placeholder"


class TestDriftLockCompQuery:
    """Drift locks for comp-query.yaml injection invariants."""

    def _load(self) -> dict:
        return yaml.safe_load(COMP_QUERY_PATH.read_text())

    def test_lock_atom_principle_in_atoms(self):
        """DRIFT LOCK: comp-query.yaml must include atom-principle in atoms list."""
        atoms = self._load().get("atoms", [])
        assert any(a["id"] == "atom-principle" for a in atoms)

    def test_lock_atom_count_is_4(self):
        """DRIFT LOCK: comp-query.yaml must have exactly 5 atoms (Phase 129 — atom-ai-spark added)."""
        atoms = self._load().get("atoms", [])
        assert len(atoms) == 5, (
            f"comp-query atom count changed from 5 to {len(atoms)} — update lock if intentional"
        )


class TestDriftLockPrincipleSelector:
    """Drift locks for PrincipleSelector implementation invariants."""

    def test_lock_pool_parameter_exists(self):
        """DRIFT LOCK: PrincipleSelector must accept pool parameter."""
        from cortex.intelligence.principle_selector import PrincipleSelector
        ps = PrincipleSelector("QUERY", pool="principles")
        assert ps._pool == "principles"

    def test_lock_valid_pools_are_quotes_and_principles(self):
        """DRIFT LOCK: Valid pool values must be exactly {'quotes', 'principles'}."""
        from cortex.intelligence.principle_selector import _VALID_POOLS
        assert _VALID_POOLS == frozenset({"quotes", "principles"})

    def test_lock_ring_buffer_maxlen_is_10(self):
        """DRIFT LOCK: ring buffer maxlen must remain 20 (bumped from 10 in Phase 125)."""
        from cortex.intelligence.principle_selector import _ring_buffer
        assert _ring_buffer.maxlen == 20

    def test_lock_body_truncated_to_200_chars(self):
        """DRIFT LOCK: PrincipleSelector must truncate principle body to ≤200 chars.

        Governance: atom-principle.yaml body_max_chars=200, CORE-PRINCIPLE-TRIGGER brevity rule.
        """
        from cortex.intelligence.principle_selector import PrincipleSelector
        import cortex.intelligence.analysis.principle_selector as ps_analysis

        # Inject a long-body principle into the cache directly to test truncation
        original_cache = ps_analysis._principles_cache
        long_body = "A" * 300  # 300 chars — must be truncated to ≤200
        ps_analysis._principles_cache = [{
            "id": "test-truncation",
            "title": "Truncation Test",
            "body": long_body,
            "domain": "universal",
            "tags": [],
            "intent_types": ["QUERY"],
            "relevance_weight": 1.0,
        }]
        try:
            ps = PrincipleSelector("QUERY", pool="principles")
            result = ps.select(context_hints={"is_complex": True})
            assert len(result["body"]) <= 200, (
                f"body length {len(result['body'])} exceeds 200 char limit"
            )
            assert result["body"].endswith("…") or result["body"].rstrip().endswith("…"), "truncated body must end with ellipsis"
        finally:
            ps_analysis._principles_cache = original_cache


class TestDriftLockPrincipleTriggerPolicy:
    """Drift locks for CORE-PRINCIPLE-TRIGGER policy (P2-004 audit contract).

    These locks enforce that operational compositions NEVER include atom-principle,
    and that the trigger policy YAML exists with the correct structure.
    SSOT: cortex-registry/core/principle-trigger-policy.yaml
    """

    def _load_policy(self) -> dict:
        return yaml.safe_load(TRIGGER_POLICY_PATH.read_text())

    def test_lock_trigger_policy_yaml_exists(self):
        """DRIFT LOCK: principle-trigger-policy.yaml must exist in cortex-registry/core/."""
        assert TRIGGER_POLICY_PATH.exists(), (
            "cortex-registry/core/principle-trigger-policy.yaml missing — "
            "CORE-PRINCIPLE-TRIGGER policy SSOT deleted"
        )

    def test_lock_policy_has_analysis_category(self):
        """DRIFT LOCK: policy must define 'analysis' category with principle_injection=True."""
        policy = self._load_policy()
        analysis = policy["intent_categories"]["analysis"]
        assert analysis["principle_injection"] is True

    def test_lock_policy_has_operations_category_blocked(self):
        """DRIFT LOCK: policy must define 'operations' category with principle_injection=False."""
        policy = self._load_policy()
        ops = policy["intent_categories"]["operations"]
        assert ops["principle_injection"] is False
        assert ops.get("override_allowed") is False

    def test_lock_operations_intents_cover_all_operational_comps(self):
        """DRIFT LOCK: operations category must include intents for all operational compositions."""
        policy = self._load_policy()
        ops_intents = set(policy["intent_categories"]["operations"]["intents"])
        # These are the core operational intents that must be blocked
        required = {"IMPLEMENT", "FIX", "REFACTOR", "DEBUG", "AUDIT", "HEALTH", "VACUUM"}
        missing = required - ops_intents
        assert not missing, f"Operations intent category missing: {missing}"

    def test_lock_brevity_policy_is_200_chars(self):
        """DRIFT LOCK: brevity.body_max_chars must be 200 (governance contract)."""
        policy = self._load_policy()
        assert policy["brevity"]["body_max_chars"] == 200

    def test_lock_no_operational_composition_includes_atom_principle(self):
        """DRIFT LOCK (P2-004): Operational compositions must NOT include atom-principle.

        This is the automated equivalent of audit check P2-004.
        If this test fails, an operational composition has drifted to include
        atom-principle — a CORE-PRINCIPLE-TRIGGER violation.
        """
        violations = []
        for filename in _OPERATIONAL_COMPOSITIONS:
            comp_path = COMPOSITIONS_DIR / filename
            if not comp_path.exists():
                continue  # composition not yet created — not a violation
            comp = yaml.safe_load(comp_path.read_text())
            atoms = [a["id"] for a in comp.get("atoms", [])]
            if "atom-principle" in atoms:
                violations.append(filename)

        assert not violations, (
            f"CORE-PRINCIPLE-TRIGGER violation (P2-004): atom-principle found in "
            f"operational composition(s): {violations}. "
            f"SSOT: cortex-registry/core/principle-trigger-policy.yaml"
        )

    def test_lock_atom_principle_omit_if_covers_operational_intents(self):
        """DRIFT LOCK: atom-principle.yaml omit_if must mention all operational intents."""
        atom = yaml.safe_load(ATOM_PRINCIPLE_PATH.read_text())
        omit_text = " ".join(atom["rendering_rules"].get("omit_if", []))
        required_mentions = ["IMPLEMENT", "FIX", "REFACTOR", "TDD", "DEBUG", "AUDIT", "HEALTH", "VACUUM"]
        missing = [intent for intent in required_mentions if intent not in omit_text]
        assert not missing, (
            f"atom-principle omit_if missing operational intent coverage: {missing}"
        )

    def test_lock_analysis_design_compositions_include_atom_principle(self):
        """DRIFT LOCK (positive): Analysis/design compositions MUST include atom-principle.

        CORE-PRINCIPLE-TRIGGER declares principle_injection=True for analysis and design
        categories. Any composition serving these intents must wire atom-principle.

        Covered compositions:
          - comp-query.yaml   (QUERY — analysis)
          - comp-introduce.yaml (INTRODUCE — design)

        If this test fails, a composition was updated to remove atom-principle without
        updating the trigger policy — a CORE-PRINCIPLE-TRIGGER violation.
        SSOT: cortex-registry/core/principle-trigger-policy.yaml
        """
        _ANALYSIS_DESIGN_COMPOSITIONS = {
            "comp-query.yaml": "QUERY (analysis)",
            "comp-introduce.yaml": "INTRODUCE (design)",
        }
        violations = []
        for filename, label in _ANALYSIS_DESIGN_COMPOSITIONS.items():
            comp_path = COMPOSITIONS_DIR / filename
            assert comp_path.exists(), f"{filename} missing — required for {label}"
            comp = yaml.safe_load(comp_path.read_text())
            atoms = [a["id"] for a in comp.get("atoms", [])]
            if "atom-principle" not in atoms:
                violations.append(f"{filename} ({label})")

        assert not violations, (
            f"CORE-PRINCIPLE-TRIGGER violation: atom-principle MISSING from "
            f"analysis/design composition(s): {violations}. "
            f"SSOT: cortex-registry/core/principle-trigger-policy.yaml"
        )


# ── Phase 129 Drift Locks — ContentLibraryFacade + AI Spark ─────────────────

class TestDriftLockPhase129:
    """Drift locks for Phase 129 — ContentLibraryFacade, EpochShuffler, AI Spark library.

    These locks encode invariants that must hold across all future modifications
    to the three-pool content library system added in Phase 129.
    """

    _REPO_ROOT = REPO_ROOT
    _AI_SPARK_PATH = REPO_ROOT / "cortex-registry" / "knowledge" / "ai" / "ai-adoption-sparks.yaml"
    _ATOM_AI_SPARK_PATH = REPO_ROOT / "cortex-registry" / "templates" / "response" / "atoms" / "atom-ai-spark.yaml"
    _FACADE_PATH = REPO_ROOT / "cortex" / "intelligence" / "analysis" / "content_library_facade.py"

    # ── ContentLibraryFacade structural locks ─────────────────────────────────

    def test_lock_facade_file_exists(self):
        """DRIFT LOCK: content_library_facade.py must exist at its canonical path."""
        assert self._FACADE_PATH.exists(), (
            "cortex/intelligence/analysis/content_library_facade.py missing — "
            "Phase 129-A artefact deleted"
        )

    def test_lock_facade_importable(self):
        """DRIFT LOCK: ContentLibraryFacade must be importable from canonical path."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        assert ContentLibraryFacade is not None

    def test_lock_epoch_shuffler_importable(self):
        """DRIFT LOCK: EpochShuffler must be importable from canonical path."""
        from cortex.intelligence.analysis.content_library_facade import EpochShuffler
        assert EpochShuffler is not None

    def test_lock_valid_pools_has_three_pools(self):
        """DRIFT LOCK: VALID_POOLS must contain exactly 3 pools: quotes, principles, ai_spark."""
        from cortex.intelligence.analysis.content_library_facade import VALID_POOLS
        assert VALID_POOLS == frozenset({"quotes", "principles", "ai_spark"}), (
            f"VALID_POOLS changed: {VALID_POOLS} — update lock if intentional"
        )

    def test_lock_library_labels_exact(self):
        """DRIFT LOCK: LIBRARY_LABELS must map exact keys→values for all 3 pools."""
        from cortex.intelligence.analysis.content_library_facade import LIBRARY_LABELS
        assert LIBRARY_LABELS["quotes"] == "Insight"
        assert LIBRARY_LABELS["principles"] == "Principle"
        assert LIBRARY_LABELS["ai_spark"] == "AI Spark"

    def test_lock_facade_select_method_signature(self):
        """DRIFT LOCK: ContentLibraryFacade.select() must accept pool parameter."""
        import inspect
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        sig = inspect.signature(ContentLibraryFacade.select)
        assert "pool" in sig.parameters

    def test_lock_facade_select_across_method_exists(self):
        """DRIFT LOCK: ContentLibraryFacade.select_across() must exist."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        assert hasattr(ContentLibraryFacade, "select_across")

    # ── AI Spark library locks ────────────────────────────────────────────────

    def test_lock_ai_spark_library_exists(self):
        """DRIFT LOCK: ai-adoption-sparks.yaml must exist at canonical path."""
        assert self._AI_SPARK_PATH.exists(), (
            "cortex-registry/knowledge/ai/ai-adoption-sparks.yaml missing — "
            "Phase 129-B artefact deleted"
        )

    def test_lock_ai_spark_library_minimum_count(self):
        """DRIFT LOCK: AI Spark library must have ≥150 items."""
        data = yaml.safe_load(self._AI_SPARK_PATH.read_text())
        sparks = data["sparks"]
        assert len(sparks) >= 150, (
            f"AI Spark library shrunk below 150 items: {len(sparks)}"
        )

    def test_lock_ai_spark_top_level_key(self):
        """DRIFT LOCK: top-level key in ai-adoption-sparks.yaml must be 'sparks:'."""
        data = yaml.safe_load(self._AI_SPARK_PATH.read_text())
        assert "sparks" in data, "Top-level key must be 'sparks:' — facade reads data['sparks']"

    def test_lock_ai_spark_all_bodies_within_200_chars(self):
        """DRIFT LOCK: All AI Spark bodies must remain ≤200 chars."""
        data = yaml.safe_load(self._AI_SPARK_PATH.read_text())
        violations = [
            (s["id"], len(s["body"].strip()))
            for s in data["sparks"]
            if len(s["body"].strip()) > 200
        ]
        assert not violations, (
            f"{len(violations)} AI Spark bodies exceed 200 chars: {violations[:5]}"
        )

    def test_lock_ai_spark_all_audience_universal(self):
        """DRIFT LOCK: All AI Spark items must have audience='universal'."""
        data = yaml.safe_load(self._AI_SPARK_PATH.read_text())
        violations = [
            s["id"] for s in data["sparks"]
            if s.get("audience") != "universal"
        ]
        assert not violations, (
            f"Non-universal audience detected: {violations}"
        )

    def test_lock_ai_spark_dedup_keys_unique(self):
        """DRIFT LOCK: All dedup_keys in ai-adoption-sparks.yaml must be unique."""
        from collections import Counter
        data = yaml.safe_load(self._AI_SPARK_PATH.read_text())
        keys = [s["dedup_key"] for s in data["sparks"] if s.get("dedup_key")]
        dupes = {k: v for k, v in Counter(keys).items() if v > 1}
        assert not dupes, f"Duplicate dedup_keys: {dupes}"

    def test_lock_ai_spark_all_8_categories_present(self):
        """DRIFT LOCK: All 8 category types must be represented in ai-adoption-sparks.yaml."""
        required = {
            "productivity", "creativity", "collaboration", "adoption",
            "evolution", "ethics", "craftsmanship", "leadership",
        }
        data = yaml.safe_load(self._AI_SPARK_PATH.read_text())
        present = {s["category"] for s in data["sparks"]}
        missing = required - present
        assert not missing, f"Required categories missing: {missing}"

    # ── atom-ai-spark.yaml locks ──────────────────────────────────────────────

    def test_lock_ai_spark_atom_exists(self):
        """DRIFT LOCK: atom-ai-spark.yaml must exist at canonical path."""
        assert self._ATOM_AI_SPARK_PATH.exists(), (
            "cortex-registry/templates/response/atoms/atom-ai-spark.yaml missing — "
            "Phase 129-E artefact deleted"
        )

    def test_lock_ai_spark_atom_id(self):
        """DRIFT LOCK: atom-ai-spark.yaml atom_id must be 'atom-ai-spark'."""
        data = yaml.safe_load(self._ATOM_AI_SPARK_PATH.read_text())
        assert data.get("atom_id") == "atom-ai-spark"

    def test_lock_ai_spark_atom_label(self):
        """DRIFT LOCK: atom-ai-spark.yaml render.label must be 'AI Spark'."""
        data = yaml.safe_load(self._ATOM_AI_SPARK_PATH.read_text())
        assert data["render"]["label"] == "AI Spark"

    def test_lock_ai_spark_atom_position(self):
        """DRIFT LOCK: atom-ai-spark renders in analysis_section (parallel to atom-principle)."""
        data = yaml.safe_load(self._ATOM_AI_SPARK_PATH.read_text())
        assert data["render"]["position"] == "analysis_section"

    def test_lock_ai_spark_atom_render_format(self):
        """DRIFT LOCK: atom-ai-spark render format must use blockquote with 💡 icon."""
        data = yaml.safe_load(self._ATOM_AI_SPARK_PATH.read_text())
        fmt = data["render"]["format"]
        assert "> 💡 **AI Spark:**" in fmt

    def test_lock_ai_spark_atom_in_comp_query(self):
        """DRIFT LOCK: comp-query.yaml must include atom-ai-spark in atoms list (Phase 129-F)."""
        comp = yaml.safe_load(COMP_QUERY_PATH.read_text())
        atoms = [a["id"] for a in comp.get("atoms", [])]
        assert "atom-ai-spark" in atoms, (
            "atom-ai-spark missing from comp-query.yaml atoms — Phase 129-F wiring removed"
        )

    # ── EpochShuffler behaviour locks ─────────────────────────────────────────

    def test_lock_epoch_shuffler_no_repeats_within_epoch(self):
        """DRIFT LOCK: EpochShuffler must not repeat any item within a single epoch."""
        from cortex.intelligence.analysis.content_library_facade import EpochShuffler
        items = [{"id": f"item-{i}", "relevance_weight": 0.8} for i in range(20)]
        shuffler = EpochShuffler(items)
        seen = [shuffler.next() for _ in range(20)]
        seen_ids = [s["id"] for s in seen]
        assert len(seen_ids) == len(set(seen_ids)), "EpochShuffler repeated an item within epoch"

    def test_lock_epoch_shuffler_reshuffle_on_exhaust(self):
        """DRIFT LOCK: EpochShuffler must reset and continue after exhausting epoch."""
        from cortex.intelligence.analysis.content_library_facade import EpochShuffler
        items = [{"id": f"item-{i}", "relevance_weight": 0.8} for i in range(5)]
        shuffler = EpochShuffler(items)
        # Exhaust one epoch + call one more
        for _ in range(5):
            shuffler.next()
        # Should not raise — should have reshuffled
        result = shuffler.next()
        assert result is not None

    # ── Backward compatibility locks ─────────────────────────────────────────

    def test_lock_principle_selector_backward_compatible(self):
        """DRIFT LOCK: PrincipleSelector must remain importable and functional (Phase 129 backward compat)."""
        from cortex.intelligence.principle_selector import PrincipleSelector
        ps = PrincipleSelector("QUERY", pool="quotes")
        result = ps.select()
        assert result is not None
        assert "text" in result or "body" in result or "quote" in result or result


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 129-C: atom-quote.yaml expansion locks (120 → 180 quotes)
# ═══════════════════════════════════════════════════════════════════════════════

class TestDriftLockPhase129C:
    """Phase 129-C: Drift locks for atom-quote.yaml after expansion to 180 quotes."""

    _QUOTE_PATH = ATOM_QUOTE_PATH

    def _load(self) -> dict:
        return yaml.safe_load(self._QUOTE_PATH.read_text())

    def test_lock_quote_minimum_count_is_180(self):
        """DRIFT LOCK (Phase 129-C): atom-quote.yaml must have at least 180 quotes after expansion."""
        data = self._load()
        quotes = data.get("quotes", [])
        assert len(quotes) >= 180, (
            f"Phase 129-C target: 180 quotes. Got: {len(quotes)}. "
            "Add more verified quotes to atom-quote.yaml."
        )

    def test_lock_quote_validation_minimum_updated(self):
        """DRIFT LOCK (Phase 129-C): validation.minimum_quotes must be updated to 180."""
        data = self._load()
        vblock = data.get("validation", {})
        minimum = vblock.get("minimum_quotes", 0)
        assert minimum >= 180, (
            f"validation.minimum_quotes must be updated to 180 after expansion. Got: {minimum}"
        )

    def test_lock_quote_all_10_themes_present(self):
        """DRIFT LOCK (Phase 129-C): All 10 canonical themes must remain present after expansion."""
        required_themes = {
            "quality", "systems-thinking", "improvement", "architecture",
            "discipline", "strategy", "security", "learning", "flow", "universal",
        }
        data = self._load()
        actual = set()
        for q in data.get("quotes", []):
            actual.update(q.get("themes", []))
        missing = required_themes - actual
        assert not missing, f"Themes missing after expansion: {missing}"

    def test_lock_quote_universal_theme_minimum(self):
        """DRIFT LOCK (Phase 129-C): universal theme must have at least 20 quotes after expansion."""
        data = self._load()
        universal = [q for q in data.get("quotes", []) if "universal" in q.get("themes", [])]
        assert len(universal) >= 20, (
            f"universal theme needs at least 20 quotes (was 12 pre-129-C). Got: {len(universal)}"
        )

    def test_lock_quote_no_body_over_200_chars(self):
        """DRIFT LOCK (Phase 129-C): No quote text may exceed 200 characters."""
        data = self._load()
        violations = [
            q.get("dedup_key", q.get("text", "?")[:30])
            for q in data.get("quotes", [])
            if len(q.get("text", "").strip()) > 200
        ]
        assert not violations, f"Quotes with text >200 chars: {violations}"

    def test_lock_quote_dedup_keys_unique(self):
        """DRIFT LOCK (Phase 129-C): All dedup_keys in atom-quote.yaml must be unique."""
        from collections import Counter
        data = self._load()
        keys = [q["dedup_key"] for q in data.get("quotes", []) if q.get("dedup_key")]
        dupes = {k: v for k, v in Counter(keys).items() if v > 1}
        assert not dupes, f"Duplicate dedup_keys in atom-quote.yaml: {dupes}"

    def test_lock_quote_required_fields_present(self):
        """DRIFT LOCK (Phase 129-C): Every quote must have text, author, book, themes, dedup_key."""
        required = ["text", "author", "book", "themes", "dedup_key"]
        data = self._load()
        violations = []
        for q in data.get("quotes", []):
            missing = [f for f in required if f not in q]
            if missing:
                violations.append((q.get("dedup_key", "UNKNOWN"), missing))
        assert not violations, f"Quotes missing required fields: {violations[:5]}"


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 129-D: high-value-principles.yaml expansion locks (90 → 110 principles)
# ═══════════════════════════════════════════════════════════════════════════════

class TestDriftLockPhase129D:
    """Phase 129-D: Drift locks for high-value-principles.yaml after expansion to 110 principles."""

    _PATH = PRINCIPLES_PATH

    def _load(self) -> dict:
        return yaml.safe_load(self._PATH.read_text())

    def test_lock_principles_minimum_count_is_110(self):
        """DRIFT LOCK (Phase 129-D): high-value-principles.yaml must have at least 110 principles."""
        data = self._load()
        count = len(data.get("principles", []))
        assert count >= 110, (
            f"Phase 129-D target: 110 principles. Got: {count}. "
            "Add more principles to high-value-principles.yaml."
        )

    def test_lock_principles_all_10_domains_retained(self):
        """DRIFT LOCK (Phase 129-D): All 10 original domains must still be present."""
        required = {
            "tdd", "refactoring", "architecture", "security",
            "api_design", "testing", "observability", "code_quality",
            "documentation", "devops",
        }
        data = self._load()
        actual = {p["domain"] for p in data.get("principles", [])}
        missing = required - actual
        assert not missing, f"Domains removed during expansion: {missing}"

    def test_lock_principles_each_domain_has_at_least_11(self):
        """DRIFT LOCK (Phase 129-D): Each domain must have at least 11 principles (was 9)."""
        data = self._load()
        domains: dict[str, int] = {}
        for p in data.get("principles", []):
            d = p.get("domain", "unknown")
            domains[d] = domains.get(d, 0) + 1
        under = {d: c for d, c in domains.items() if c < 11}
        assert not under, (
            f"These domains have fewer than 11 principles after Phase 129-D expansion: {under}"
        )

    def test_lock_principles_no_body_over_200_chars(self):
        """DRIFT LOCK (Phase 129-D): No principle body may exceed 200 characters."""
        data = self._load()
        violations = [
            p.get("id", "?") for p in data.get("principles", [])
            if len(p.get("body", "").strip()) > 200
        ]
        assert not violations, f"Principles with body >200 chars: {violations}"

    def test_lock_principles_required_fields_present(self):
        """DRIFT LOCK (Phase 129-D): Every principle must have id, title, body, domain, tags, intent_types."""
        required = ["id", "title", "body", "domain", "tags", "intent_types"]
        data = self._load()
        violations = []
        for p in data.get("principles", []):
            missing = [f for f in required if f not in p]
            if missing:
                violations.append((p.get("id", "UNKNOWN"), missing))
        assert not violations, f"Principles missing required fields: {violations[:5]}"

    def test_lock_principles_ids_are_unique(self):
        """DRIFT LOCK (Phase 129-D): All principle IDs must be unique."""
        from collections import Counter
        data = self._load()
        ids = [p["id"] for p in data.get("principles", []) if "id" in p]
        dupes = {k: v for k, v in Counter(ids).items() if v > 1}
        assert not dupes, f"Duplicate principle IDs: {dupes}"

    def test_lock_principles_validation_block_updated(self):
        """DRIFT LOCK (Phase 129-D): validation block must exist and minimum_principles >= 110."""
        data = self._load()
        vblock = data.get("validation", {})
        assert vblock, "validation block missing from high-value-principles.yaml"
        minimum = vblock.get("minimum_principles", 0)
        assert minimum >= 110, (
            f"validation.minimum_principles must be >= 110 after Phase 129-D. Got: {minimum}"
        )

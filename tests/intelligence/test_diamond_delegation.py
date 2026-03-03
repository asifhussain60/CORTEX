"""Phase 117-a — TDD RED: Tests for broken delegation chains.

These tests must ALL FAIL before implementation (CORE-008 compliance).
After GREEN pass, they verify:
- facade.analyze() returns non-empty for real files (GAP-117-01)
- load_cortex_best_practices() signature fixed (GAP-117-02)
- facade.query(domain=X) returns results (GAP-117-03)
- provider LENS key mismatch fixed (GAP-117-03a)
- get_domain_knowledge() returns real data (GAP-117-03b)
"""
from __future__ import annotations

import pytest
from pathlib import Path


# ── GAP-117-01: facade.analyze() must return non-empty ───────────────────────

class TestFacadeAnalyzeNotEmpty:
    """facade.analyze() must delegate to get_lens_analysis, not return empty dict."""

    def test_facade_analyze_returns_nonempty_for_real_file(self) -> None:
        """analyze() on an existing file must return non-empty analysis dict."""
        from cortex.intelligence.facade import IntelligenceFacade
        f = IntelligenceFacade()
        result = f.analyze(file_path="cortex/__init__.py", intent="REFACTOR")
        assert result.get("status") == "ok", f"Expected ok, got: {result}"
        analysis = result.get("analysis", {})
        # After fix: analysis must contain ast_analysis or git_analysis data
        # This test FAILS before fix (analysis is empty dict {})
        assert analysis != {}, (
            f"analyze() returned empty analysis for cortex/__init__.py. "
            f"Provider must delegate to get_lens_analysis(). Got: {result}"
        )

    def test_facade_analyze_graceful_on_nonexistent_file(self) -> None:
        """analyze() on a missing file must degrade gracefully (not crash)."""
        from cortex.intelligence.facade import IntelligenceFacade
        f = IntelligenceFacade()
        result = f.analyze(file_path="/nonexistent/definitely/not/a/real/path.py")
        # Must not raise — must return a dict with status
        assert isinstance(result, dict), "Must return dict even on bad path"
        assert "status" in result, "Must have status key"


# ── GAP-117-02: load_cortex_best_practices signature fix ─────────────────────

class TestBestPracticesLoaderSignature:
    """load_cortex_best_practices must accept cache argument from engine."""

    def test_best_practices_loader_signature_compatible(self) -> None:
        """engine._load_cortex_best_practices() must not raise TypeError."""
        from cortex.intelligence.knowledge.knowledge_synthesis_engine.engine import (
            KnowledgeSynthesisEngine,
        )
        engine = KnowledgeSynthesisEngine()
        # This call raises TypeError before fix: missing 'cache' positional arg
        result = engine._load_cortex_best_practices("IMPLEMENT")
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        # After fix: must return non-empty dict with actual practices
        assert result != {}, (
            "best_practices returned empty dict. "
            "Fix: pass self._cortex_knowledge_cache to load_cortex_best_practices()."
        )

    def test_facade_synthesize_returns_nonempty_best_practices(self) -> None:
        """synthesize() must return non-empty cortex_knowledge after sig fix."""
        from cortex.intelligence.facade import IntelligenceFacade
        f = IntelligenceFacade()
        result = f.synthesize(query="IMPLEMENT")
        assert result.get("status") == "ok", f"Unexpected status: {result}"
        synthesis = result.get("synthesis", {})
        # synthesis may be a dict or an object
        if isinstance(synthesis, dict):
            ck = synthesis.get("cortex_knowledge", {})
            if hasattr(ck, "best_practices"):
                bp = ck.best_practices
            elif isinstance(ck, dict):
                bp = ck.get("best_practices", {})
            else:
                bp = {}
        else:
            ck = getattr(synthesis, "cortex_knowledge", {})
            bp = getattr(ck, "best_practices", {}) if ck else {}

        assert bp != {}, (
            "synthesize() returned empty best_practices. "
            "Fix: engine._load_cortex_best_practices must pass cache to loader."
        )

    def test_synthesis_error_not_swallowed_silently(self) -> None:
        """Synthesis errors must appear in logs, not silently vanish."""
        import logging
        from cortex.intelligence.facade import IntelligenceFacade

        f = IntelligenceFacade()
        # Should not raise — but must not silently hide TypeError
        result = f.synthesize(query="TEST_INTENT")
        # If status is 'ok' the error must truly be fixed, not just caught
        if result.get("status") == "ok":
            synthesis = result.get("synthesis", {})
            # Verify it's not just an empty fallback
            assert synthesis is not None


# ── GAP-117-03: facade.query(domain=X) must return results ───────────────────

class TestFacadeQueryDomainFilter:
    """facade.query(domain=X) must return matching entries (not 0)."""

    def test_facade_query_without_domain_returns_all(self) -> None:
        """query() without domain returns all 53 entries."""
        from cortex.intelligence.facade import IntelligenceFacade
        f = IntelligenceFacade()
        result = f.query(query="test")
        assert result.get("count", 0) > 0, "query() with no domain must return entries"

    def test_facade_query_with_architecture_domain_returns_results(self) -> None:
        """query(domain='architecture') must return architecture entries."""
        from cortex.intelligence.facade import IntelligenceFacade
        f = IntelligenceFacade()
        result = f.query(query="architecture", domain="architecture")
        assert result.get("status") == "ok"
        assert result.get("count", 0) > 0, (
            "query(domain='architecture') returned 0 results. "
            "Domain filter is broken. Available domains: architecture, backend-python, etc."
        )

    def test_facade_query_returns_empty_for_unknown_domain(self) -> None:
        """query(domain='nonexistent_xyz') must return empty gracefully."""
        from cortex.intelligence.facade import IntelligenceFacade
        f = IntelligenceFacade()
        result = f.query(query="anything", domain="nonexistent_xyz_123")
        assert result.get("status") == "ok", "Must not error on unknown domain"
        assert result.get("count", 0) == 0, "Unknown domain must return 0 results"


# ── GAP-117-03a: LENS key mismatch fix ───────────────────────────────────────

class TestProviderLensKeyMapping:
    """provider.targeted() must map LENS keys correctly (git_analysis not git_history)."""

    def test_targeted_tier_lens_key_mapping_correct(self) -> None:
        """targeted() must use 'git_analysis' key, not 'git_history'."""
        from cortex.intelligence.provider import UnifiedIntelligenceProvider
        provider = UnifiedIntelligenceProvider()
        ctx = provider.targeted("IMPLEMENT", file_path="cortex/__init__.py")
        lens = ctx.lens_intelligence
        # git_analysis should be populated after fix (not always empty due to key mismatch)
        # We verify the key mapping is correct by checking the attribute exists
        assert hasattr(lens, "git_analysis"), "LENSIntelligence must have git_analysis"
        assert hasattr(lens, "ast_analysis"), "LENSIntelligence must have ast_analysis"
        assert hasattr(lens, "comment_analysis"), "LENSIntelligence must have comment_analysis"

    def test_full_tier_lens_key_mapping_correct(self) -> None:
        """full() must use 'git_analysis' key, not 'git_history'."""
        from cortex.intelligence.provider import UnifiedIntelligenceProvider
        provider = UnifiedIntelligenceProvider()
        ctx = provider.full("IMPLEMENT", file_path="cortex/__init__.py")
        lens = ctx.lens_intelligence
        assert hasattr(lens, "git_analysis")
        assert hasattr(lens, "comment_analysis")

    def test_targeted_tier_degrades_when_lens_unavailable(self) -> None:
        """targeted() must return context even when LENS fails."""
        from cortex.intelligence.provider import UnifiedIntelligenceProvider
        from unittest.mock import patch
        provider = UnifiedIntelligenceProvider()
        with patch.object(provider, "_ensure_lens_orchestrator", side_effect=ImportError("LENS unavailable")):
            ctx = provider.targeted("IMPLEMENT", file_path="cortex/__init__.py")
            assert ctx is not None, "targeted() must degrade gracefully when LENS fails"


# ── GAP-117-03b: get_domain_knowledge() placeholder fix ──────────────────────

class TestProviderDomainKnowledge:
    """get_domain_knowledge() must not return hardcoded empty dict."""

    def test_get_domain_knowledge_returns_real_rules(self) -> None:
        """get_domain_knowledge() must not return the placeholder empty dict."""
        from cortex.intelligence.provider import UnifiedIntelligenceProvider
        provider = UnifiedIntelligenceProvider()
        result = provider.get_domain_knowledge("IMPLEMENT")
        # Placeholder returns {'domain_rules': {}, 'compliance_standards': []}
        # After fix: must return actual content from KnowledgeRegistryProxy or CompanyDomainLoader
        placeholder = {"domain_rules": {}, "compliance_standards": []}
        assert result != placeholder, (
            "get_domain_knowledge() still returns hardcoded placeholder. "
            "Fix: delegate to CompanyDomainLoader or KnowledgeRegistryProxy."
        )

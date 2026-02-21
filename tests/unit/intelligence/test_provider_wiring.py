"""
Phase 18 Sub-Phase B — TDD RED Tests: UnifiedIntelligenceProvider wiring

Tests written BEFORE implementation (CORE-008 mandate).
Validates that targeted() and full() use CompanyDomainLoader instead of
the hardcoded CompanyKnowledge({}) stub.

Authority: AC-P18-005, AC-P18-006, AC-P18-007, AC-P18-008, AC-P18-009
Coverage: 6 unit tests
"""

# ruff: noqa: S101
import os
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest


# ===========================================================================================
# Helpers
# ===========================================================================================

def _make_provider() -> Any:
    """Return a fresh (non-singleton) UnifiedIntelligenceProvider for each test."""
    from cortex.intelligence.provider import UnifiedIntelligenceProvider

    provider = object.__new__(UnifiedIntelligenceProvider)
    # Re-run __init__ directly to avoid singleton guard
    UnifiedIntelligenceProvider.__init__(provider)
    return provider


# ===========================================================================================
# AC-P18-005: targeted() receives non-empty CompanyKnowledge when domains/ YAMLs exist
# ===========================================================================================

def test_targeted_uses_company_domain_loader(tmp_path: Path) -> None:
    """AC-P18-005: targeted() calls CompanyDomainLoader.load(), not hardcoded empty."""
    from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader
    from cortex.intelligence.knowledge.unified_intelligence_context import CompanyKnowledge

    # Arrange — loader that returns a non-empty CompanyKnowledge
    non_empty_knowledge = CompanyKnowledge(
        domain_rules={"security-standards": {"auth": ["Use OAuth 2.0"]}},
        compliance_standards=["SECURITY"],
        precedence="OVERRIDE",
    )
    fake_loader = MagicMock(spec=CompanyDomainLoader)
    fake_loader.load.return_value = non_empty_knowledge

    provider = _make_provider()

    captured: Dict[str, Any] = {}

    def _fake_synthesize(
        intent: str,
        lens_intelligence: Any = None,
        company_knowledge: Any = None,
        file_path: Any = None,
    ) -> Any:
        captured["company_knowledge"] = company_knowledge
        from cortex.intelligence.knowledge.unified_intelligence_context import (
            UnifiedIntelligenceContext,
        )
        return UnifiedIntelligenceContext.create_empty(intent, file_path)

    provider.synthesize = _fake_synthesize

    with patch(
        "cortex.intelligence.provider.get_company_domain_loader",
        return_value=fake_loader,
    ):
        provider.targeted(intent="IMPLEMENT")

    ck = captured.get("company_knowledge")
    assert ck is not None
    assert ck.domain_rules != {}, "targeted() must pass non-empty domain_rules"
    assert ck.compliance_standards != [], "targeted() must pass non-empty compliance_standards"


# ===========================================================================================
# AC-P18-006: full() receives non-empty CompanyKnowledge when domains/ YAMLs exist
# ===========================================================================================

def test_full_uses_company_domain_loader(tmp_path: Path) -> None:
    """AC-P18-006: full() calls CompanyDomainLoader.load(), not hardcoded empty."""
    from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader
    from cortex.intelligence.knowledge.unified_intelligence_context import CompanyKnowledge

    non_empty_knowledge = CompanyKnowledge(
        domain_rules={"payment-security": {"pci": ["Use TLS 1.3"]}},
        compliance_standards=["PCI-DSS"],
        precedence="OVERRIDE",
    )
    fake_loader = MagicMock(spec=CompanyDomainLoader)
    fake_loader.load.return_value = non_empty_knowledge

    provider = _make_provider()
    captured: Dict[str, Any] = {}

    def _fake_synthesize(
        intent: str,
        lens_intelligence: Any = None,
        company_knowledge: Any = None,
        file_path: Any = None,
    ) -> Any:
        captured["company_knowledge"] = company_knowledge
        from cortex.intelligence.knowledge.unified_intelligence_context import (
            UnifiedIntelligenceContext,
        )
        return UnifiedIntelligenceContext.create_empty(intent, file_path)

    provider.synthesize = _fake_synthesize

    with patch(
        "cortex.intelligence.provider.get_company_domain_loader",
        return_value=fake_loader,
    ):
        provider.full(intent="REFACTOR")

    ck = captured.get("company_knowledge")
    assert ck is not None
    assert ck.domain_rules != {}, "full() must pass non-empty domain_rules"
    assert "PCI-DSS" in ck.compliance_standards


# ===========================================================================================
# AC-P18-007: quick() still returns in <200ms (latency SLA)
# ===========================================================================================

def test_quick_completes_under_200ms() -> None:
    """AC-P18-007: quick() latency SLA — must complete in under 200 ms."""
    import time

    from cortex.intelligence.knowledge.unified_intelligence_context import (
        UnifiedIntelligenceContext,
    )

    provider = _make_provider()

    def _fast_synthesize(
        intent: str,
        lens_intelligence: Any = None,
        company_knowledge: Any = None,
        file_path: Any = None,
    ) -> Any:
        return UnifiedIntelligenceContext.create_empty(intent, file_path)

    provider.synthesize = _fast_synthesize

    start = time.perf_counter()
    provider.quick(intent="IMPLEMENT")
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 200, f"quick() took {elapsed_ms:.1f}ms — must be <200ms"


# ===========================================================================================
# AC-P18-008: full() calls fetch_user_stories() when ADO_ORG_URL is set
# ===========================================================================================

def test_full_calls_ado_when_env_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC-P18-008: full() invokes WorkItemProvider when ADO_ORG_URL env var is present."""
    monkeypatch.setenv("ADO_ORG_URL", "https://dev.azure.com/test-org")

    from cortex.intelligence.knowledge.unified_intelligence_context import (
        UnifiedIntelligenceContext,
    )

    provider = _make_provider()
    provider.synthesize = lambda **kw: UnifiedIntelligenceContext.create_empty(  # type: ignore[assignment]
        kw.get("intent", "IMPLEMENT"), kw.get("file_path")
    )

    fetch_called = {"called": False}

    mock_provider = MagicMock()
    mock_provider.fetch_user_stories.return_value = []

    def _fake_synthesize(intent: str, **kw: Any) -> Any:
        return UnifiedIntelligenceContext.create_empty(intent, None)

    provider.synthesize = _fake_synthesize  # type: ignore[assignment]

    with patch("cortex.intelligence.provider.get_company_domain_loader") as mock_loader_factory, \
         patch("cortex.intelligence.provider.get_work_item_provider", return_value=mock_provider) as mock_wp:
        mock_loader_factory.return_value.load.return_value = __import__(
            "cortex.intelligence.knowledge.unified_intelligence_context",
            fromlist=["CompanyKnowledge"],
        ).CompanyKnowledge({}, [], "OVERRIDE")

        provider.full(intent="IMPLEMENT")

    mock_wp.assert_called_once()
    mock_provider.fetch_user_stories.assert_called_once()


# ===========================================================================================
# AC-P18-009: full() skips ADO call silently when ADO_ORG_URL is not set
# ===========================================================================================

def test_full_skips_ado_when_env_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC-P18-009: full() does NOT call WorkItemProvider when ADO_ORG_URL is unset."""
    monkeypatch.delenv("ADO_ORG_URL", raising=False)

    from cortex.intelligence.knowledge.unified_intelligence_context import (
        UnifiedIntelligenceContext,
    )

    provider = _make_provider()

    def _fake_synthesize(intent: str, **kw: Any) -> Any:
        return UnifiedIntelligenceContext.create_empty(intent, None)

    provider.synthesize = _fake_synthesize  # type: ignore[assignment]

    with patch("cortex.intelligence.provider.get_company_domain_loader") as mock_loader_factory, \
         patch("cortex.intelligence.provider.get_work_item_provider") as mock_wp:
        mock_loader_factory.return_value.load.return_value = __import__(
            "cortex.intelligence.knowledge.unified_intelligence_context",
            fromlist=["CompanyKnowledge"],
        ).CompanyKnowledge({}, [], "OVERRIDE")

        provider.full(intent="IMPLEMENT")

    mock_wp.assert_not_called()


# ===========================================================================================
# AC-P18-009-b: full() continues (no exception) when ADO call raises
# ===========================================================================================

def test_full_handles_ado_timeout_gracefully(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC-P18-009: full() must not propagate ADO exceptions — synthesis continues."""
    monkeypatch.setenv("ADO_ORG_URL", "https://dev.azure.com/test-org")

    from cortex.intelligence.knowledge.unified_intelligence_context import (
        UnifiedIntelligenceContext,
    )

    provider = _make_provider()

    def _fake_synthesize(intent: str, **kw: Any) -> Any:
        return UnifiedIntelligenceContext.create_empty(intent, None)

    provider.synthesize = _fake_synthesize  # type: ignore[assignment]

    broken_provider = MagicMock()
    broken_provider.fetch_user_stories.side_effect = TimeoutError("ADO unreachable")

    with patch("cortex.intelligence.provider.get_company_domain_loader") as mock_loader_factory, \
         patch("cortex.intelligence.provider.get_work_item_provider", return_value=broken_provider):
        mock_loader_factory.return_value.load.return_value = __import__(
            "cortex.intelligence.knowledge.unified_intelligence_context",
            fromlist=["CompanyKnowledge"],
        ).CompanyKnowledge({}, [], "OVERRIDE")

        # Must NOT raise
        result = provider.full(intent="IMPLEMENT")

    assert result is not None

"""
Phase 18 Sub-Phase C — TDD RED Tests: synthesize_cross_domain_context()

Tests written BEFORE implementation (CORE-008 mandate).
Validates that KnowledgeSynthesisEngine.synthesize_cross_domain_context()
returns non-empty architecture/security/testing lists.

Authority: AC-P18-010
Coverage: 5 unit tests
"""

# ruff: noqa: S101
from pathlib import Path
from typing import Any, Dict, List

import pytest


# ===========================================================================================
# AC-P18-010: synthesize_cross_domain_context() method exists and is callable
# ===========================================================================================

def test_synthesize_cross_domain_context_exists() -> None:
    """AC-P18-010: KnowledgeSynthesisEngine has synthesize_cross_domain_context() method."""
    from cortex.intelligence.knowledge.knowledge_synthesis_engine import KnowledgeSynthesisEngine

    engine = KnowledgeSynthesisEngine()
    assert hasattr(engine, "synthesize_cross_domain_context"), (
        "KnowledgeSynthesisEngine must have synthesize_cross_domain_context()"
    )
    assert callable(engine.synthesize_cross_domain_context)


def test_synthesize_cross_domain_returns_dict() -> None:
    """AC-P18-010: synthesize_cross_domain_context() returns a dict."""
    from cortex.intelligence.knowledge.knowledge_synthesis_engine import KnowledgeSynthesisEngine

    engine = KnowledgeSynthesisEngine()
    result = engine.synthesize_cross_domain_context(intent="IMPLEMENT", context="FastAPI service")

    assert isinstance(result, dict), "Return type must be dict"


def test_synthesize_cross_domain_has_required_keys() -> None:
    """AC-P18-010: Result dict contains architecture, security, and testing keys."""
    from cortex.intelligence.knowledge.knowledge_synthesis_engine import KnowledgeSynthesisEngine

    engine = KnowledgeSynthesisEngine()
    result = engine.synthesize_cross_domain_context(intent="IMPLEMENT", context="payment API")

    assert "architecture" in result, "Result must include 'architecture' key"
    assert "security" in result, "Result must include 'security' key"
    assert "testing" in result, "Result must include 'testing' key"


def test_synthesize_cross_domain_returns_non_empty_lists() -> None:
    """AC-P18-010: All three lists are non-empty when patterns YAML files are present."""
    from cortex.intelligence.knowledge.knowledge_synthesis_engine import KnowledgeSynthesisEngine

    engine = KnowledgeSynthesisEngine()
    result = engine.synthesize_cross_domain_context(intent="IMPLEMENT", context="auth service")

    assert len(result["architecture"]) > 0, "architecture list must be non-empty"
    assert len(result["security"]) > 0, "security list must be non-empty"
    assert len(result["testing"]) > 0, "testing list must be non-empty"


def test_provider_cross_domain_calls_synthesis_engine() -> None:
    """AC-P18-010: UnifiedIntelligenceProvider._synthesize_cross_domain() uses engine, not stub."""
    from unittest.mock import MagicMock, patch

    from cortex.intelligence.provider import UnifiedIntelligenceProvider

    provider = object.__new__(UnifiedIntelligenceProvider)
    UnifiedIntelligenceProvider.__init__(provider)

    fake_engine = MagicMock()
    fake_engine.synthesize_cross_domain_context.return_value = {
        "architecture": ["Use DDD bounded contexts"],
        "security": ["Enforce RBAC"],
        "testing": ["Write property-based tests"],
    }
    provider._synthesis_engine = fake_engine

    result = provider._synthesize_cross_domain(intent="IMPLEMENT", context="DDD auth API")

    fake_engine.synthesize_cross_domain_context.assert_called_once()
    call_args = fake_engine.synthesize_cross_domain_context.call_args
    # Accept both positional and keyword invocations
    all_args = list(call_args.args) + list(call_args.kwargs.values())
    assert "IMPLEMENT" in all_args
    assert "DDD auth API" in all_args
    assert result["architecture"] == ["Use DDD bounded contexts"]
    assert result["security"] == ["Enforce RBAC"]
    assert result["testing"] == ["Write property-based tests"]

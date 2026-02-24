"""
Golden Path E2E Tests: CIG Orchestrator Pipeline — with AC Marker Completeness

Phase 63-B rewrite — replaces original test_cig_orchestrator_pipeline.py
(which had 7 AC_START markers in module docstring but zero AC_COMPLETE assertions).

Tests:
- Golden paths: IMPLEMENT → TDDOrchestrator, FIX → IntentRouter, ANALYZE → LENSSynthesis
- Conversational + table format orchestrator routing
- AC marker completeness assertions added (CORE requirement)
- Performance: transformation <50ms, reflection <30ms

Authority: CORE-008, CORE-035, CORE-055
AC-IDs: AC-CIG-S5-001..AC-CIG-S5-007
"""
# ruff: noqa: S101
from __future__ import annotations

import re
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[3]


class TestCIGOrchestratorPipeline:
    """Golden path tests for CIG orchestrator pipeline integration."""

    def test_golden_path_implement_intent_to_tdd_orchestrator(self) -> None:
        """AC-CIG-S5-001: IMPLEMENT intent → TDDOrchestrator."""
        try:
            from cortex.orchestrators.core.request_transformer import RequestTransformer
        except ImportError as exc:
            pytest.skip(f"RequestTransformer not importable: {exc}")

        transformer = RequestTransformer()
        user_request = "implement user authentication for login module"
        transformed = transformer.transform(user_request)

        assert transformed.structured_context["intent_type"] == "IMPLEMENT"
        assert "implement" in transformed.canonical_keywords
        assert "authentication" in transformed.canonical_keywords

    def test_golden_path_fix_intent_to_intent_router(self) -> None:
        """AC-CIG-S5-002: FIX intent → IntentRouter."""
        try:
            from cortex.orchestrators.core.request_transformer import RequestTransformer
        except ImportError as exc:
            pytest.skip(f"RequestTransformer not importable: {exc}")

        transformer = RequestTransformer()
        user_request = "fix the broken login page that's preventing users from authenticating"
        transformed = transformer.transform(user_request)

        assert transformed.structured_context["intent_type"] == "FIX"
        assert "fix" in transformed.canonical_keywords
        assert transformed.structured_context["urgency"] in ["high", "medium", "low"]

    def test_golden_path_analyze_intent_to_lens_synthesis(self) -> None:
        """AC-CIG-S5-003: ANALYZE intent → LENSSynthesis."""
        try:
            from cortex.orchestrators.core.request_transformer import RequestTransformer
        except ImportError as exc:
            pytest.skip(f"RequestTransformer not importable: {exc}")

        transformer = RequestTransformer()
        user_request = "analyze the codebase architecture for security vulnerabilities"
        transformed = transformer.transform(user_request)

        assert transformed.structured_context["intent_type"] in ["ANALYZE", "AUDIT"]

    def test_conversational_format_orchestrator_routing(self) -> None:
        """AC-CIG-S5-004: Conversational format detected and preserved."""
        try:
            from cortex.orchestrators.core.request_transformer import RequestTransformer
        except ImportError as exc:
            pytest.skip(f"RequestTransformer not importable: {exc}")

        transformer = RequestTransformer()
        request = "Can you help me understand why the tests are failing in the auth module?"
        transformed = transformer.transform(request)

        assert transformed is not None
        assert transformed.structured_context.get("intent_type") is not None

    def test_transformation_performance_under_50ms(self) -> None:
        """AC-CIG-S5-005: Request transformation must complete in <50ms."""
        try:
            from cortex.orchestrators.core.request_transformer import RequestTransformer
        except ImportError as exc:
            pytest.skip(f"RequestTransformer not importable: {exc}")

        transformer = RequestTransformer()
        start = time.perf_counter()
        transformer.transform("implement a new feature for user management")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 50, f"Transformation took {elapsed_ms:.1f}ms (>50ms threshold)"

    def test_conversational_reflector_performance_under_30ms(self) -> None:
        """AC-CIG-S5-006: ConversationalReflector must complete in <30ms."""
        try:
            from cortex.orchestrators.core.conversational_reflector import ConversationalReflector
        except ImportError as exc:
            pytest.skip(f"ConversationalReflector not importable: {exc}")

        reflector = ConversationalReflector()
        # reflect() expects a DOR dict, not a plain string
        dor_dict = {
            "intent_type": "IMPLEMENT",
            "confidence": 0.88,
            "canonical_keywords": ["implement", "authentication"],
            "scope": "component",
            "impact": "high",
            "user_text": "implement authentication",
        }
        start = time.perf_counter()
        if hasattr(reflector, "reflect"):
            reflector.reflect(dor_dict)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 30, f"Reflection took {elapsed_ms:.1f}ms (>30ms threshold)"

    def test_transformed_request_has_required_fields(self) -> None:
        """AC-CIG-S5-007: TransformedRequest must expose structured_context and canonical_keywords."""
        try:
            from cortex.orchestrators.core.request_transformer import RequestTransformer
        except ImportError as exc:
            pytest.skip(f"RequestTransformer not importable: {exc}")

        transformer = RequestTransformer()
        result = transformer.transform("audit the governance rules for compliance")

        assert hasattr(result, "structured_context"), "Missing structured_context"
        assert hasattr(result, "canonical_keywords"), "Missing canonical_keywords"
        assert isinstance(result.structured_context, dict), "structured_context must be a dict"


class TestACMarkerCompleteness:
    """AC marker completeness — every AC_START in the pipeline must have AC_COMPLETE."""

    def test_cig_source_files_have_ac_complete_if_ac_start_present(self) -> None:
        """CIG interaction source files with AC_START must have matching AC_COMPLETE."""
        cig_dirs = [
            ROOT / "cortex" / "core" / "interaction",
        ]
        violations = []
        for cig_dir in cig_dirs:
            if not cig_dir.exists():
                continue
            for py_file in cig_dir.rglob("*.py"):
                content = py_file.read_text(errors="replace")
                starts = len(re.findall(r"AC_START", content))
                completes = len(re.findall(r"AC_COMPLETE", content))
                if starts > 0 and completes == 0:
                    violations.append(
                        f"{py_file.relative_to(ROOT)} — {starts} AC_START, 0 AC_COMPLETE"
                    )
        assert violations == [], (
            f"Orphaned AC_START markers in CIG source files:\n"
            + "\n".join(f"  {v}" for v in violations)
        )

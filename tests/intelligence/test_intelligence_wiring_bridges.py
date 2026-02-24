"""
Phase 66-B tests — GAP-66-006, 009, 010, 011, 012, 015, 016:
Intelligence wiring bridge functions.

Author: Asif Hussain
Phase: 66-B
Sweep: SWEEP-66-INTELLIGENCE-MATRIX
"""

import pytest
from typing import Any, Dict, List
from unittest.mock import MagicMock

# AC_START: AC-66-B-WIRING-BRIDGES-TESTS-20260224T000000Z


class TestLensBatchBridge:
    """GAP-66-006: LENS → BatchProcessor pipe."""

    def test_lens_pipe_to_batch_importable(self) -> None:
        from cortex.intelligence.intelligence_wiring_bridges import lens_pipe_to_batch  # noqa: F401

    def test_lens_pipe_adds_items(self) -> None:
        from cortex.intelligence.intelligence_wiring_bridges import lens_pipe_to_batch

        mock_bp = MagicMock()
        mock_bp.add.return_value = None

        results = [{"file": "a.py"}, {"file": "b.py"}]
        count = lens_pipe_to_batch(results, mock_bp)

        assert count == 2
        assert mock_bp.add.call_count == 2


class TestT1DomainAdapterBridge:
    """GAP-66-009: T1 patterns → DomainAdapter enrichment."""

    def test_t1_enrich_importable(self) -> None:
        from cortex.intelligence.intelligence_wiring_bridges import t1_enrich_domain_adapter_context  # noqa: F401

    def test_t1_enrich_adds_patterns(self) -> None:
        from cortex.intelligence.intelligence_wiring_bridges import t1_enrich_domain_adapter_context

        context: Dict[str, Any] = {"existing_key": "value"}
        patterns = ["snake_case_modules", "cortex_prefix"]
        result = t1_enrich_domain_adapter_context(patterns, context)

        assert result["t1_enriched"] is True
        assert result["t1_patterns"] == patterns
        assert result["existing_key"] == "value"


class TestT2BatchBridge:
    """GAP-66-010: T2 context → BatchProcessor injection."""

    def test_t2_inject_importable(self) -> None:
        from cortex.intelligence.intelligence_wiring_bridges import t2_inject_session_context  # noqa: F401

    def test_t2_inject_enriches_metadata(self) -> None:
        from cortex.intelligence.intelligence_wiring_bridges import t2_inject_session_context

        t2_ctx: Dict[str, Any] = {"intent": "IMPLEMENT", "active_phase": "66"}
        metadata: Dict[str, Any] = {"batch_id": "B001"}
        result = t2_inject_session_context(t2_ctx, metadata)

        assert result["t2_enriched"] is True
        assert result["t2_context"] == t2_ctx
        assert result["batch_id"] == "B001"


class TestT2AuditScoringBridge:
    """GAP-66-011: T2 context → AuditFix Stage 2 priority scoring."""

    def test_t2_score_importable(self) -> None:
        from cortex.intelligence.intelligence_wiring_bridges import t2_score_audit_findings  # noqa: F401

    def test_t2_score_adds_boost_flag(self) -> None:
        from cortex.intelligence.intelligence_wiring_bridges import t2_score_audit_findings

        findings: List[Dict[str, Any]] = [
            {"description": "CORE-028 violation", "phase": "66"},
            {"description": "CORE-011 missing type hint", "phase": "65"},
        ]
        t2_ctx: Dict[str, Any] = {"active_phase": "66", "intent": "FIX"}
        result = t2_score_audit_findings(findings, t2_ctx)

        assert len(result) == 2
        # Phase 66 finding should get boost
        phase_66 = next(r for r in result if r["phase"] == "66")
        assert phase_66["t2_priority_boost"] is True


class TestResponseTemplateStageBridge:
    """GAP-66-012: ResponseTemplate → BatchProcessor stage completions."""

    def test_apply_response_template_importable(self) -> None:
        from cortex.intelligence.intelligence_wiring_bridges import apply_response_template_to_stage  # noqa: F401

    def test_apply_response_template_returns_string(self) -> None:
        from cortex.intelligence.intelligence_wiring_bridges import apply_response_template_to_stage

        result = apply_response_template_to_stage(
            stage_name="DocGen Stage 1",
            stage_result={"items": 5},
            success=True,
        )
        assert isinstance(result, str) and len(result) > 0
        assert "DocGen Stage 1" in result


class TestRetrievalOptimizerBridge:
    """GAP-66-015/016: RetrievalOptimizer scoring for DocGen and AuditFix."""

    def test_retrieval_optimizer_importable(self) -> None:
        from cortex.intelligence.intelligence_wiring_bridges import retrieval_optimizer_score_results  # noqa: F401

    def test_retrieval_optimizer_scores_and_sorts(self) -> None:
        from cortex.intelligence.intelligence_wiring_bridges import retrieval_optimizer_score_results

        results: List[Dict[str, Any]] = [
            {"content": "cortex module core protocol mixin", "id": "A"},
            {"content": "unrelated content about databases", "id": "B"},
            {"content": "cortex intelligence matrix phase", "id": "C"},
        ]
        scored = retrieval_optimizer_score_results(results, query="cortex intelligence")

        assert len(scored) == 3
        # All results must have retrieval_score
        for r in scored:
            assert "retrieval_score" in r
            assert isinstance(r["retrieval_score"], float)
        # Must be sorted descending
        scores = [r["retrieval_score"] for r in scored]
        assert scores == sorted(scores, reverse=True), "Results must be sorted by score desc"


# AC_COMPLETE: AC-66-B-WIRING-BRIDGES-TESTS-20260224T000000Z ✅

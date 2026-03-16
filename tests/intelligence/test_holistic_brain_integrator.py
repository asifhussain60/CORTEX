"""Tests for HolisticBrainIntegrator.

Verifies unified context assembly across request history, intelligence,
registry artifacts, and governance policy signals.
"""

from typing import Any, Dict, List


class _FakeFacade:
    def __init__(self) -> None:
        self._analyze_calls: List[Dict[str, Any]] = []

    def analyze(self, file_path: str = "", intent: str = "QUERY", **kwargs: Any) -> Dict[str, Any]:
        self._analyze_calls.append({"file_path": file_path, "intent": intent})
        return {"status": "ok", "analysis": {"signals": ["ast", "git"]}}

    def synthesize(self, query: str = "", **kwargs: Any) -> Dict[str, Any]:
        return {"status": "ok", "query": query, "summary": "synthetic-summary"}

    def load_governance(self, severity: str = None) -> List[Dict[str, Any]]:  # type: ignore[assignment]
        rules = [
            {"rule_id": "CORE-008", "severity": "blocked"},
            {"rule_id": "CORE-048", "severity": "warning"},
        ]
        if severity is None:
            return rules
        return [r for r in rules if r.get("severity") == severity]

    def load_workflows(self, category: str = None) -> List[Dict[str, Any]]:  # type: ignore[assignment]
        templates = [
            {"id": "feature-impl", "category": "sdlc"},
            {"id": "audit-fix", "category": "audit"},
        ]
        if category is None:
            return templates
        return [t for t in templates if t.get("category") == category]

    def registry_index(self, domain: str = None) -> List[Any]:  # type: ignore[assignment]
        class _Entry:
            def __init__(self, _domain: str) -> None:
                self.domain = _domain

        all_entries = [_Entry("governance"), _Entry("core"), _Entry("workflows")]
        if domain is None:
            return all_entries
        return [e for e in all_entries if e.domain == domain]


class _FakeRequestLogManager:
    def get_prior_requests(self, session_id: str, limit: int = 5, exclude_id: str = None) -> List[Dict[str, Any]]:  # type: ignore[assignment]
        return [
            {"sequence_number": 2, "user_request": "Add audit checks", "intent_type": "AUDIT"},
            {"sequence_number": 1, "user_request": "Build feature", "intent_type": "IMPLEMENT"},
        ][:limit]


class _FailingFacade:
    def analyze(self, **kwargs: Any) -> Dict[str, Any]:
        raise RuntimeError("analysis unavailable")

    def synthesize(self, **kwargs: Any) -> Dict[str, Any]:
        raise RuntimeError("synthesis unavailable")

    def load_governance(self, severity: str = None) -> List[Dict[str, Any]]:  # type: ignore[assignment]
        raise RuntimeError("governance unavailable")

    def load_workflows(self, category: str = None) -> List[Dict[str, Any]]:  # type: ignore[assignment]
        raise RuntimeError("workflows unavailable")

    def registry_index(self, domain: str = None) -> List[Any]:  # type: ignore[assignment]
        raise RuntimeError("registry unavailable")


class TestHolisticBrainIntegrator:
    def test_build_unified_context_returns_expected_sections(self) -> None:
        from cortex.intelligence.holistic_brain_integrator import HolisticBrainIntegrator

        integrator = HolisticBrainIntegrator(intelligence_facade=_FakeFacade())
        result = integrator.build_unified_context(
            current_request="Implement secure endpoint",
            session_id="sess-123",
            intent="IMPLEMENT",
            execution_stages=["pre_gate", "intent_routing", "governance_check", "execution"],
            request_log_manager=_FakeRequestLogManager(),
            file_path="cortex/orchestrators/core/master_orchestrator.py",
        )

        assert result["status"] == "ok"
        assert result["request_context"]["session_id"] == "sess-123"
        assert result["request_context"]["prior_request_count"] == 2
        assert result["governance_policy"]["total_rules"] == 2
        assert result["governance_policy"]["blocked_rules"] == 1
        assert result["registry_artifacts"]["workflow_templates"] == 2
        assert result["registry_artifacts"]["registry_entries"] == 3
        assert result["execution_contract"]["stages"] == [
            "pre_gate", "intent_routing", "governance_check", "execution"
        ]

    def test_build_unified_context_without_request_log_manager(self) -> None:
        from cortex.intelligence.holistic_brain_integrator import HolisticBrainIntegrator

        integrator = HolisticBrainIntegrator(intelligence_facade=_FakeFacade())
        result = integrator.build_unified_context(
            current_request="Refactor service",
            session_id="sess-456",
            intent="REFACTOR",
        )

        assert result["status"] == "ok"
        assert result["request_context"]["prior_request_count"] == 0
        assert result["request_context"]["prior_requests"] == []

    def test_build_unified_context_degrades_gracefully_on_facade_errors(self) -> None:
        from cortex.intelligence.holistic_brain_integrator import HolisticBrainIntegrator

        integrator = HolisticBrainIntegrator(intelligence_facade=_FailingFacade())
        result = integrator.build_unified_context(
            current_request="Investigate failure",
            session_id="sess-789",
            intent="DEBUG",
        )

        assert result["status"] == "degraded"
        assert isinstance(result["degradation_reasons"], list)
        assert len(result["degradation_reasons"]) >= 1
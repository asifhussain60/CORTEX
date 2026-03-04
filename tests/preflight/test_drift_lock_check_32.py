"""Preflight: Drift Lock — Check #32 Stub/Mock/Blank Object Eradication (phase-126-c).

Permanent CI guardrail that enforces the invariants established by phase-126-c.
Fails immediately if any stub-eradication regression is detected.

This is a LOCK file — it does not replace test_stub_eradication.py.
It adds a lightweight fast gate that confirms the governance file exists and
runs the most critical runtime invariants (facade + composer liveness).

Drift lock ref: cortex-registry/governance/drift-locks/check-32-stub-eradication-lock.yaml
Gap ref: GAP-126-03
Phase ref: phase-126-c
Tier: T0 (preflight) — fast, < 5 s
"""
from __future__ import annotations

import pathlib
import re
from typing import List, Tuple

import pytest

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
CORTEX_SRC = CORTEX_ROOT / "cortex"
DRIFT_LOCK_YAML = (
    CORTEX_ROOT
    / "cortex-registry"
    / "governance"
    / "drift-locks"
    / "check-32-stub-eradication-lock.yaml"
)
PRIMARY_TEST_FILE = CORTEX_ROOT / "tests" / "preflight" / "test_stub_eradication.py"


class TestDriftLockCheck32:
    """Drift lock: Stub/Mock/Blank Eradication invariants must hold permanently.

    Each test maps to an enforced invariant in check-32-stub-eradication-lock.yaml.
    Failure means a regression has been introduced — fix, do not delete.
    """

    # ---------------------------------------------------------------------------
    # INV-32-00 — Governance artefacts must exist
    # ---------------------------------------------------------------------------

    def test_drift_lock_yaml_exists(self) -> None:
        """INV-32-00a: The drift lock YAML itself must exist.

        If this test fails, someone deleted the governance file — restore it.
        """
        assert DRIFT_LOCK_YAML.exists(), (
            f"DRIFT-LOCK REGRESSION: Governance file deleted: {DRIFT_LOCK_YAML}\n"
            "Restore from git:\n"
            "  git checkout HEAD -- "
            "cortex-registry/governance/drift-locks/check-32-stub-eradication-lock.yaml"
        )

    def test_primary_test_file_exists(self) -> None:
        """INV-32-00b: The primary eradication test file must exist.

        If this test fails, test_stub_eradication.py was deleted — restore it.
        """
        assert PRIMARY_TEST_FILE.exists(), (
            f"DRIFT-LOCK REGRESSION: Primary test file deleted: {PRIMARY_TEST_FILE}\n"
            "Restore from git:\n"
            "  git checkout HEAD -- tests/preflight/test_stub_eradication.py"
        )

    # ---------------------------------------------------------------------------
    # INV-32-01 — No TODO/FIXME in critical orchestrator paths (fast subset)
    # ---------------------------------------------------------------------------

    def test_drift_lock_no_todo_fixme_in_orchestrators(self) -> None:
        """INV-32-01: cortex/orchestrators/ must contain no TODO/FIXME stubs.

        Regression: a TODO/FIXME comment introduced in any orchestrator means
        unfinished wiring was committed to a production path.
        """
        # Orchestrator files that reference TODO/FIXME as string literals (analysis tools)
        _ORCHESTRATOR_ALLOWLIST: frozenset = frozenset({
            "cortex/orchestrators/core/intent_router/lens_analysis_mixin.py",   # parses TODO/FIXME for intent hints
            "cortex/orchestrators/intelligence/response_template_generator.py",  # IN_PROGRESS label contains "TODO"
            "cortex/orchestrators/support/digest_session_orchestrator.py",       # marker list: ["TODO:", ...]
        })
        _ALLOW_RE = re.compile(
            r"TODO.*Phase\s+2\b"
            r"|TODO.*TODOs?\b"
            r"|TODO.*markers?\b"
            r"|TODO.*keyword",
            re.IGNORECASE,
        )
        violations: List[Tuple[str, int, str]] = []
        todo_fixme_re = re.compile(r"\b(TODO|FIXME)\b")

        for f in (CORTEX_SRC / "orchestrators").rglob("*.py"):
            if "__pycache__" in str(f) or "test_" in f.name:
                continue
            rel = str(f.relative_to(CORTEX_ROOT)).replace("\\", "/")
            if rel in _ORCHESTRATOR_ALLOWLIST:
                continue
            try:
                lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for lineno, line in enumerate(lines, 1):
                if not todo_fixme_re.search(line):
                    continue
                if _ALLOW_RE.search(line):
                    continue
                violations.append((rel, lineno, line.strip()))

        assert not violations, (
            f"DRIFT-LOCK CHECK-32 INV-32-01 REGRESSION: "
            f"{len(violations)} TODO/FIXME stub(s) found in cortex/orchestrators/.\n"
            "Resolve each stub before committing:\n"
            + "\n".join(f"  {r}:{ln}: {txt}" for r, ln, txt in violations[:10])
        )

    # ---------------------------------------------------------------------------
    # INV-32-02 — FallbackStrategy must remain abstract
    # ---------------------------------------------------------------------------

    def test_drift_lock_fallbackstrategy_is_abstract(self) -> None:
        """INV-32-02: FallbackStrategy must inherit from ABC (not be a concrete class).

        Regression: removing the ABC base from FallbackStrategy makes the class
        concrete and its unimplemented execute() method becomes a runtime trap.
        """
        try:
            from cortex.infrastructure.graceful_degradation import FallbackStrategy
            import abc

            assert issubclass(FallbackStrategy, abc.ABC), (
                "DRIFT-LOCK CHECK-32 INV-32-02 REGRESSION: FallbackStrategy is no longer "
                "abstract — it has lost its ABC base class.\n"
                "Add 'from abc import ABC, abstractmethod' and make FallbackStrategy(ABC)."
            )
        except ImportError as exc:
            pytest.fail(
                f"DRIFT-LOCK CHECK-32 INV-32-02 REGRESSION: "
                f"graceful_degradation import failed: {exc}"
            )

    # ---------------------------------------------------------------------------
    # INV-32-03 — No class-level ENABLED=False wiring constants in orchestrators
    # ---------------------------------------------------------------------------

    def test_drift_lock_no_class_level_disabled_wiring(self) -> None:
        """INV-32-03: Orchestrators must not have class-level ENABLED=False constants.

        Regression: adding PHASE*_GATEWAY_ENABLED = False or *_ENABLED = False
        at class body level disables wiring unconditionally for all instances.
        """
        _PATTERN = re.compile(
            r"^\s{0,8}(PHASE\d+_GATEWAY_ENABLED"
            r"|[A-Z][A-Z0-9_]*_ENABLED"
            r"|[A-Z][A-Z0-9_]*_WIRING_ENABLED"
            r"|[A-Z][A-Z0-9_]*_CHAIN_ENABLED)\s*(?::\s*bool\s*)?=\s*False"
        )
        violations: List[Tuple[str, int, str]] = []

        for f in (CORTEX_SRC / "orchestrators").rglob("*.py"):
            if "__pycache__" in str(f) or "test_" in f.name:
                continue
            try:
                lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for lineno, line in enumerate(lines, 1):
                if line.strip().startswith("#"):
                    continue
                if _PATTERN.search(line):
                    violations.append(
                        (str(f.relative_to(CORTEX_ROOT)).replace("\\", "/"), lineno, line.strip())
                    )

        assert not violations, (
            f"DRIFT-LOCK CHECK-32 INV-32-03 REGRESSION: "
            f"{len(violations)} class-level disabled wiring flag(s) in orchestrators.\n"
            "Remove or implement:\n"
            + "\n".join(f"  {r}:{ln}: {txt}" for r, ln, txt in violations[:10])
        )

    # ---------------------------------------------------------------------------
    # INV-32-04 — IntelligenceFacade.analyze() liveness
    # ---------------------------------------------------------------------------

    def test_drift_lock_intelligence_facade_analyze_is_live(self) -> None:
        """INV-32-04: IntelligenceFacade.analyze() must return non-empty live data.

        Regression: if the LENS pipeline is broken, analyze() returns an empty
        analysis dict — callers silently receive no code intelligence.
        """
        try:
            from cortex.intelligence.facade import get_intelligence_facade

            facade = get_intelligence_facade()
            result = facade.analyze(
                file_path=str(CORTEX_SRC / "intelligence" / "facade.py"),
                intent="IMPLEMENT",
            )
            assert isinstance(result, dict) and result.get("status") in (
                "ok",
                "healthy",
                "success",
            ), (
                "DRIFT-LOCK CHECK-32 INV-32-04 REGRESSION: "
                f"IntelligenceFacade.analyze() returned status={result.get('status')!r}.\n"
                f"Full result: {result}"
            )
            analysis = result.get("analysis", {})
            assert analysis, (
                "DRIFT-LOCK CHECK-32 INV-32-04 REGRESSION: "
                "IntelligenceFacade.analyze() returned empty 'analysis' dict — "
                "LENS pipeline is returning stub data."
            )
        except ImportError as exc:
            pytest.fail(
                f"DRIFT-LOCK CHECK-32 INV-32-04 REGRESSION: "
                f"IntelligenceFacade import failed: {exc}"
            )

    # ---------------------------------------------------------------------------
    # INV-32-05 — WorkflowComposer.execute_from_template() liveness
    # ---------------------------------------------------------------------------

    def test_drift_lock_workflow_composer_execute_is_live(self) -> None:
        """INV-32-05: WorkflowComposer.execute_from_template() must return non-None.

        Regression: if the composer path is stubbed, orchestrators relying on
        IMPLEMENT/FIX workflows silently receive None and fail silently.
        """
        try:
            from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer

            composer = WorkflowComposer()
            result = composer.execute_from_template(
                template_data="sdlc/implement-workflow",
                context={"operation": "IMPLEMENT", "parameters": {}},
            )
            assert result is not None, (
                "DRIFT-LOCK CHECK-32 INV-32-05 REGRESSION: "
                "WorkflowComposer.execute_from_template() returned None — "
                "the workflow execution path is a stub."
            )
        except ImportError as exc:
            pytest.fail(
                f"DRIFT-LOCK CHECK-32 INV-32-05 REGRESSION: "
                f"WorkflowComposer import failed: {exc}"
            )

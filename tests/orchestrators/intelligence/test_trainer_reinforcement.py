"""
Tests for Phase 83-b: TrainerOrchestrator Reinforcement Wiring.

Authority: phase-83-unified-reinforcement-signal.yaml GAP-83-03
AC-ID: AC-83-TRAINER-20260226

RED Phase: All tests must FAIL before implementation begins.

Validates:
- TrainerOrchestrator emits STRONG_REWARD on execute_proposal success
- TrainerOrchestrator emits STRONG_PUNISHMENT on execute_proposal failure
- TrainerOrchestrator emits MILD_REWARD on partial success
- score_proposal() method returns reinforcement summary
- Reinforcement signals flow through UniversalLearningLoop

CORE Rules:
- CORE-008: TDD mandatory ✅
- CORE-011: Type hints required ✅
- CORE-012: Docstrings required ✅
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
import yaml


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def trainer(tmp_path: Path) -> Any:
    """Create a TrainerOrchestrator with temp workspace."""
    from cortex.orchestrators.intelligence.trainer_orchestrator import (
        TrainerOrchestrator,
    )

    templates_dir = tmp_path / "cortex-registry" / "workflows" / "templates"
    templates_dir.mkdir(parents=True)

    return TrainerOrchestrator(
        workspace_root=tmp_path,
        templates_dir=templates_dir,
    )


@pytest.fixture
def approved_proposal(tmp_path: Path) -> Dict[str, Any]:
    """Create an approved proposal for testing."""
    generated_dir = (
        tmp_path / "cortex-registry" / "workflows" / "templates" / "generated"
    )
    generated_dir.mkdir(parents=True, exist_ok=True)

    return {
        "approved": True,
        "actions": [
            {
                "action": "CREATE",
                "target": str(
                    generated_dir / "test-pattern-workflow.yaml"
                ),
                "template_id": "test-pattern-workflow",
                "reason": "Test pattern not covered",
                "evidence": {"id": "test-pattern"},
                "severity": "P1",
            },
        ],
        "summary": {
            "create_count": 1,
            "enhance_count": 0,
            "review_count": 0,
        },
    }


@pytest.fixture
def failing_proposal() -> Dict[str, Any]:
    """Create a proposal that will fail during execution."""
    return {
        "approved": True,
        "actions": [
            {
                "action": "CREATE",
                "target": "/nonexistent/deeply/nested/path/that/will/fail.yaml",
                "template_id": "failing-workflow",
                "reason": "Test failure path",
                "evidence": {},
                "severity": "P0",
            },
        ],
        "summary": {
            "create_count": 1,
            "enhance_count": 0,
            "review_count": 0,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1. score_proposal() method exists
# ─────────────────────────────────────────────────────────────────────────────


class TestScoreProposalMethod:
    """GAP-83-03: TrainerOrchestrator.score_proposal() method."""

    def test_trainer_has_score_proposal_method(self, trainer: Any) -> None:
        """TrainerOrchestrator must expose score_proposal()."""
        assert hasattr(trainer, "score_proposal")
        assert callable(trainer.score_proposal)

    def test_score_proposal_returns_summary_dict(self, trainer: Any) -> None:
        """score_proposal() must return a dict with signal_count, signals, pattern_ids."""
        execution_report = {
            "status": "success",
            "executed": [
                {"action": "CREATE", "target": "/tmp/test.yaml"},
            ],
            "skipped": [],
            "errors": [],
        }

        result = trainer.score_proposal(execution_report)

        assert isinstance(result, dict)
        assert "signal_count" in result
        assert "signals" in result
        assert isinstance(result["signals"], list)

    def test_score_proposal_on_empty_report(self, trainer: Any) -> None:
        """score_proposal() on empty report should return zero signals."""
        result = trainer.score_proposal({
            "status": "pending_approval",
            "executed": [],
            "skipped": [],
            "errors": [],
        })

        assert result["signal_count"] == 0


# ─────────────────────────────────────────────────────────────────────────────
# 2. Reinforcement on execute_proposal success
# ─────────────────────────────────────────────────────────────────────────────


class TestReinforcementOnSuccess:
    """GAP-83-03: STRONG_REWARD emitted on successful execution."""

    def test_execute_and_score_emits_reward_on_success(
        self, trainer: Any, approved_proposal: Dict[str, Any]
    ) -> None:
        """execute_proposal() success → score_proposal() emits STRONG_REWARD."""
        report = trainer.execute_proposal(approved_proposal)
        assert report["status"] == "success"

        score_result = trainer.score_proposal(report)
        assert score_result["signal_count"] >= 1

        # At least one STRONG_REWARD signal
        reward_signals = [
            s for s in score_result["signals"]
            if s["signal_type"] == "STRONG_REWARD"
        ]
        assert len(reward_signals) >= 1

    def test_reward_signal_contains_pattern_id(
        self, trainer: Any, approved_proposal: Dict[str, Any]
    ) -> None:
        """Reward signal must reference the template_id as pattern_id."""
        report = trainer.execute_proposal(approved_proposal)
        score_result = trainer.score_proposal(report)

        for signal in score_result["signals"]:
            assert "pattern_id" in signal
            assert len(signal["pattern_id"]) > 0

    def test_reward_signal_source_is_trainer(
        self, trainer: Any, approved_proposal: Dict[str, Any]
    ) -> None:
        """Source orchestrator must be TrainerOrchestrator."""
        report = trainer.execute_proposal(approved_proposal)
        score_result = trainer.score_proposal(report)

        for signal in score_result["signals"]:
            assert signal["source_orchestrator"] == "TrainerOrchestrator"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Reinforcement on execute_proposal failure
# ─────────────────────────────────────────────────────────────────────────────


class TestReinforcementOnFailure:
    """GAP-83-03: STRONG_PUNISHMENT emitted on failed execution."""

    def test_execute_and_score_emits_punishment_on_failure(
        self, trainer: Any, failing_proposal: Dict[str, Any]
    ) -> None:
        """execute_proposal() failure → score_proposal() emits STRONG_PUNISHMENT."""
        report = trainer.execute_proposal(failing_proposal)

        # Should have errors
        assert len(report.get("errors", [])) > 0 or report["status"] in (
            "failed",
            "partial",
        )

        score_result = trainer.score_proposal(report)

        punishment_signals = [
            s for s in score_result["signals"]
            if s["signal_type"] in ("STRONG_PUNISHMENT", "MILD_PUNISHMENT")
        ]
        assert len(punishment_signals) >= 1

    def test_punishment_signal_references_failed_action(
        self, trainer: Any, failing_proposal: Dict[str, Any]
    ) -> None:
        """Punishment signal pattern_id must reference the failed template_id."""
        report = trainer.execute_proposal(failing_proposal)
        score_result = trainer.score_proposal(report)

        punishment_ids = {
            s["pattern_id"]
            for s in score_result["signals"]
            if s["signal_type"] in ("STRONG_PUNISHMENT", "MILD_PUNISHMENT")
        }
        assert "failing-workflow" in punishment_ids


# ─────────────────────────────────────────────────────────────────────────────
# 4. Partial success emits MILD_REWARD
# ─────────────────────────────────────────────────────────────────────────────


class TestReinforcementOnPartialSuccess:
    """GAP-83-03: Partial execution emits mixed signals."""

    def test_partial_execution_emits_mixed_signals(
        self, trainer: Any, tmp_path: Path
    ) -> None:
        """Partial success emits both rewards and punishments."""
        generated_dir = (
            tmp_path / "cortex-registry" / "workflows" / "templates" / "generated"
        )
        generated_dir.mkdir(parents=True, exist_ok=True)

        mixed_proposal = {
            "approved": True,
            "actions": [
                {
                    "action": "CREATE",
                    "target": str(generated_dir / "good.yaml"),
                    "template_id": "good-workflow",
                    "reason": "Will succeed",
                    "evidence": {"id": "good"},
                    "severity": "P1",
                },
                {
                    "action": "CREATE",
                    "target": "/nonexistent/bad.yaml",
                    "template_id": "bad-workflow",
                    "reason": "Will fail",
                    "evidence": {},
                    "severity": "P0",
                },
            ],
            "summary": {
                "create_count": 2,
                "enhance_count": 0,
                "review_count": 0,
            },
        }

        report = trainer.execute_proposal(mixed_proposal)
        score_result = trainer.score_proposal(report)

        signal_types = {s["signal_type"] for s in score_result["signals"]}
        # Should have at least one reward and one punishment
        has_reward = bool(signal_types & {"STRONG_REWARD", "MILD_REWARD"})
        has_punishment = bool(
            signal_types & {"STRONG_PUNISHMENT", "MILD_PUNISHMENT"}
        )
        assert has_reward, f"Expected reward signal, got: {signal_types}"
        assert has_punishment, f"Expected punishment signal, got: {signal_types}"


# ─────────────────────────────────────────────────────────────────────────────
# 5. Integration with UniversalLearningLoop
# ─────────────────────────────────────────────────────────────────────────────


class TestTrainerLearningLoopIntegration:
    """GAP-83-03: Signals flow through to UniversalLearningLoop."""

    def test_score_and_reinforce_writes_to_learning_loop(
        self, trainer: Any, approved_proposal: Dict[str, Any]
    ) -> None:
        """score_and_reinforce() must emit signals via learning loop."""
        from cortex.intelligence.learning.universal_learning_loop import (
            UniversalLearningLoop,
        )

        loop = UniversalLearningLoop(enable_logging=False)

        report = trainer.execute_proposal(approved_proposal)
        result = trainer.score_and_reinforce(report, learning_loop=loop)

        assert result["signal_count"] >= 1
        history = loop.get_reinforcement_history()
        assert len(history) >= 1

    def test_score_and_reinforce_returns_signal_ids(
        self, trainer: Any, approved_proposal: Dict[str, Any]
    ) -> None:
        """score_and_reinforce() must return signal_ids from learning loop."""
        from cortex.intelligence.learning.universal_learning_loop import (
            UniversalLearningLoop,
        )

        loop = UniversalLearningLoop(enable_logging=False)

        report = trainer.execute_proposal(approved_proposal)
        result = trainer.score_and_reinforce(report, learning_loop=loop)

        assert "signal_ids" in result
        assert len(result["signal_ids"]) >= 1
        assert all(isinstance(sid, str) for sid in result["signal_ids"])

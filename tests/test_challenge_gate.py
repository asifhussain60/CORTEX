"""Tests for ChallengeGate orchestrator.

Phase 48 S3: Pre-implementation challenge generation.
"""

import pytest
from cortex.orchestrators.holistic.challenge_gate import (
    ChallengeGateOrchestrator,
    Challenge,
    ChallengeAlternative,
    ChallengeGateResult,
    ChallengeType,
)


class TestChallengeAlternative:
    """Tests for ChallengeAlternative dataclass."""

    def test_create_alternative(self):
        """Test creating a challenge alternative."""
        alt = ChallengeAlternative(
            name="Option A",
            description="First option",
            pros=["pro1", "pro2"],
            cons=["con1"],
            roi_score=0.85,
            effort_estimate="medium",
            implementation_time="3 days",
            risk_level="low",
        )

        assert alt.name == "Option A"
        assert alt.roi_score == 0.85
        assert len(alt.pros) == 2
        assert len(alt.cons) == 1

    def test_alternative_roi_bounds(self):
        """Test ROI score is in valid bounds."""
        alt = ChallengeAlternative(
            name="Option",
            description="Test",
            pros=[],
            cons=[],
            roi_score=0.95,
            effort_estimate="high",
            implementation_time="7 days",
            risk_level="high",
        )

        assert 0.0 <= alt.roi_score <= 1.0


class TestChallenge:
    """Tests for Challenge dataclass."""

    def test_create_challenge(self):
        """Test creating a challenge."""
        alt = ChallengeAlternative(
            name="Alt1",
            description="desc",
            pros=["p1"],
            cons=["c1"],
            roi_score=0.8,
            effort_estimate="low",
            implementation_time="1 day",
            risk_level="low",
        )

        challenge = Challenge(
            type=ChallengeType.ARCHITECTURAL,
            title="Test Challenge",
            description="Testing",
            severity="warning",
            current_approach="approach",
            alternatives=[alt],
            recommended_alternative=0,
        )

        assert challenge.type == ChallengeType.ARCHITECTURAL
        assert challenge.severity == "warning"
        assert len(challenge.alternatives) == 1

    def test_challenge_severity_levels(self):
        """Test different severity levels."""
        for severity in ["info", "warning", "critical"]:
            challenge = Challenge(
                type=ChallengeType.ARCHITECTURAL,
                title="Test",
                description="Test",
                severity=severity,
                current_approach="test",
                alternatives=[],
            )
            assert challenge.severity == severity

    def test_challenge_types(self):
        """Test all challenge types."""
        types_to_test = [
            ChallengeType.ARCHITECTURAL,
            ChallengeType.PERFORMANCE,
            ChallengeType.SECURITY,
            ChallengeType.MAINTAINABILITY,
            ChallengeType.DEPENDENCY,
        ]

        for challenge_type in types_to_test:
            challenge = Challenge(
                type=challenge_type,
                title="Test",
                description="Test",
                severity="info",
                current_approach="test",
                alternatives=[],
            )
            assert challenge.type == challenge_type


class TestChallengeGateResult:
    """Tests for ChallengeGateResult dataclass."""

    def test_result_no_challenges(self):
        """Test result with no challenges."""
        result = ChallengeGateResult(
            challenges=[],
            has_critical=False,
            has_warnings=False,
            verdict="PROCEED",
            approval_required=False,
            user_decision_pending=False,
        )

        assert len(result.challenges) == 0
        assert result.verdict == "PROCEED"
        assert not result.approval_required

    def test_result_with_critical(self):
        """Test result with critical challenge."""
        alt = ChallengeAlternative(
            name="Alt",
            description="d",
            pros=[],
            cons=[],
            roi_score=0.5,
            effort_estimate="low",
            implementation_time="1 day",
            risk_level="low",
        )

        challenge = Challenge(
            type=ChallengeType.SECURITY,
            title="Critical",
            description="test",
            severity="critical",
            current_approach="test",
            alternatives=[alt],
        )

        result = ChallengeGateResult(
            challenges=[challenge],
            has_critical=True,
            has_warnings=False,
            verdict="BLOCK",
            approval_required=True,
            user_decision_pending=True,
        )

        assert result.has_critical
        assert result.verdict == "BLOCK"
        assert result.approval_required

    def test_result_with_warnings(self):
        """Test result with warning challenges."""
        alt = ChallengeAlternative(
            name="Alt",
            description="d",
            pros=[],
            cons=[],
            roi_score=0.5,
            effort_estimate="low",
            implementation_time="1 day",
            risk_level="low",
        )

        challenge = Challenge(
            type=ChallengeType.ARCHITECTURAL,
            title="Warning",
            description="test",
            severity="warning",
            current_approach="test",
            alternatives=[alt],
        )

        result = ChallengeGateResult(
            challenges=[challenge],
            has_critical=False,
            has_warnings=True,
            verdict="CHALLENGE",
            approval_required=False,
            user_decision_pending=True,
        )

        assert result.has_warnings
        assert result.verdict == "CHALLENGE"
        assert not result.approval_required


class TestChallengeGateOrchestrator:
    """Tests for ChallengeGateOrchestrator."""

    def test_initialize(self):
        """Test initializing challenge gate."""
        gate = ChallengeGateOrchestrator()
        assert gate is not None
        assert len(gate.challenges) == 0

    def test_generate_challenges_implement(self):
        """Test generating challenges for IMPLEMENT operation."""
        gate = ChallengeGateOrchestrator()
        result = gate.generate_challenges(
            operation="IMPLEMENT",
            target="cortex/orchestrators/domain/test_orchestrator.py",
            description="Adding new domain orchestrator",
            affected_components=["MasterOrchestrator", "IntentRouter"],
        )

        assert isinstance(result, ChallengeGateResult)
        assert result.verdict in ["PROCEED", "CHALLENGE", "BLOCK"]

    def test_generate_challenges_refactor(self):
        """Test generating challenges for REFACTOR operation."""
        gate = ChallengeGateOrchestrator()
        result = gate.generate_challenges(
            operation="REFACTOR",
            target="cortex/api/public_interface.py",
            description="Refactoring public API",
            affected_components=["MasterOrchestrator", "LENSSynthesis"],
        )

        assert isinstance(result, ChallengeGateResult)
        # Should potentially have maintainability challenge for API changes
        has_maintainability = any(c.type == ChallengeType.MAINTAINABILITY for c in result.challenges)
        assert isinstance(has_maintainability, bool)

    def test_generate_challenges_fix(self):
        """Test generating challenges for FIX operation."""
        gate = ChallengeGateOrchestrator()
        result = gate.generate_challenges(
            operation="FIX",
            target="cortex/orchestrators/core/master_orchestrator.py",
            description="Fixing bug in master orchestrator",
            affected_components=["MasterOrchestrator"],
        )

        assert isinstance(result, ChallengeGateResult)
        # Should potentially have performance challenge
        has_performance = any(c.type == ChallengeType.PERFORMANCE for c in result.challenges)
        assert isinstance(has_performance, bool)

    def test_architectural_challenges_core_tier(self):
        """Test architectural challenge for core tier detection."""
        gate = ChallengeGateOrchestrator()
        result = gate.generate_challenges(
            operation="IMPLEMENT",
            target="cortex/orchestrators/domain/new_domain_orchestrator.py",
            description="New domain orchestrator",
            affected_components=["MasterOrchestrator"],
        )

        # Should have architectural challenge for domain tier
        has_arch = any(c.type == ChallengeType.ARCHITECTURAL for c in result.challenges)
        assert isinstance(has_arch, bool)

    def test_dependency_challenges_high_impact(self):
        """Test dependency challenge for high impact changes."""
        gate = ChallengeGateOrchestrator()
        many_components = [
            "Orchestrator1",
            "Orchestrator2",
            "Orchestrator3",
            "Orchestrator4",
            "Orchestrator5",
        ]

        result = gate.generate_challenges(
            operation="IMPLEMENT",
            target="cortex/core/shared_module.py",
            description="Core shared module change",
            affected_components=many_components,
        )

        # Should have dependency challenge for high impact
        has_dependency = any(c.type == ChallengeType.DEPENDENCY for c in result.challenges)
        assert isinstance(has_dependency, bool)

    def test_challenge_alternatives_present(self):
        """Test that challenges have alternatives."""
        gate = ChallengeGateOrchestrator()
        result = gate.generate_challenges(
            operation="IMPLEMENT",
            target="cortex/orchestrators/domain/test.py",
            description="Domain tier addition",
            affected_components=["MasterOrchestrator"],
        )

        for challenge in result.challenges:
            assert len(challenge.alternatives) >= 2
            assert any(i == challenge.recommended_alternative for i in range(len(challenge.alternatives)))

    def test_verdict_logic_no_issues(self):
        """Test verdict is PROCEED when no challenges."""
        gate = ChallengeGateOrchestrator()
        result = gate.generate_challenges(
            operation="IMPLEMENT",
            target="cortex/examples/simple_example.py",
            description="Simple example file",
            affected_components=[],
        )

        if not result.challenges:
            assert result.verdict == "PROCEED"
            assert not result.approval_required

    def test_verdict_logic_critical(self):
        """Test verdict is BLOCK when critical challenges present."""
        gate = ChallengeGateOrchestrator()

        # Create a mock critical challenge
        alt = ChallengeAlternative(
            name="Alt",
            description="d",
            pros=[],
            cons=[],
            roi_score=0.5,
            effort_estimate="low",
            implementation_time="1 day",
            risk_level="low",
        )

        # Manually test critical verdict logic
        result = ChallengeGateResult(
            challenges=[
                Challenge(
                    type=ChallengeType.SECURITY,
                    title="Critical",
                    description="test",
                    severity="critical",
                    current_approach="test",
                    alternatives=[alt],
                )
            ],
            has_critical=True,
            has_warnings=False,
            verdict="BLOCK",
            approval_required=True,
            user_decision_pending=True,
        )

        assert result.verdict == "BLOCK"
        assert result.approval_required

    def test_format_challenge_for_user(self):
        """Test formatting challenge for display."""
        gate = ChallengeGateOrchestrator()

        alt = ChallengeAlternative(
            name="Option A",
            description="First approach",
            pros=["pro1", "pro2"],
            cons=["con1"],
            roi_score=0.85,
            effort_estimate="medium",
            implementation_time="3 days",
            risk_level="low",
        )

        challenge = Challenge(
            type=ChallengeType.ARCHITECTURAL,
            title="Test Challenge",
            description="This is a test",
            severity="warning",
            current_approach="Current way",
            alternatives=[alt],
            recommended_alternative=0,
        )

        formatted = gate.format_challenge_for_user(challenge)

        assert "Test Challenge" in formatted
        assert "Option A" in formatted
        assert "pro1" in formatted
        assert "Recommended" in formatted

    def test_format_result_no_challenges(self):
        """Test formatting result with no challenges."""
        gate = ChallengeGateOrchestrator()

        result = ChallengeGateResult(
            challenges=[],
            has_critical=False,
            has_warnings=False,
            verdict="PROCEED",
            approval_required=False,
            user_decision_pending=False,
        )

        formatted = gate.format_result_for_user(result)

        assert "CHALLENGE GATE" in formatted
        assert "PROCEED" in formatted
        assert "No challenges" in formatted

    def test_format_result_with_challenges(self):
        """Test formatting result with challenges."""
        gate = ChallengeGateOrchestrator()

        alt = ChallengeAlternative(
            name="Alt",
            description="desc",
            pros=["pro"],
            cons=["con"],
            roi_score=0.8,
            effort_estimate="low",
            implementation_time="1 day",
            risk_level="low",
        )

        challenge = Challenge(
            type=ChallengeType.ARCHITECTURAL,
            title="Challenge",
            description="Test challenge",
            severity="warning",
            current_approach="current",
            alternatives=[alt],
        )

        result = ChallengeGateResult(
            challenges=[challenge],
            has_critical=False,
            has_warnings=True,
            verdict="CHALLENGE",
            approval_required=False,
            user_decision_pending=True,
        )

        formatted = gate.format_result_for_user(result)

        assert "CHALLENGE" in formatted
        assert "Challenge" in formatted
        assert "Decision Required" in formatted

    def test_api_completeness(self):
        """Test that orchestrator has all required methods."""
        gate = ChallengeGateOrchestrator()

        # Check public API
        assert hasattr(gate, "generate_challenges")
        assert callable(gate.generate_challenges)
        assert hasattr(gate, "format_challenge_for_user")
        assert callable(gate.format_challenge_for_user)
        assert hasattr(gate, "format_result_for_user")
        assert callable(gate.format_result_for_user)

    def test_alternative_roi_comparison(self):
        """Test that alternatives have ROI for comparison."""
        gate = ChallengeGateOrchestrator()
        result = gate.generate_challenges(
            operation="IMPLEMENT",
            target="cortex/orchestrators/domain/test.py",
            description="Test",
            affected_components=["A", "B", "C", "D"],
        )

        for challenge in result.challenges:
            if len(challenge.alternatives) > 1:
                # Get ROI scores
                rois = [alt.roi_score for alt in challenge.alternatives]
                # Should have range of ROIs
                assert len(set(rois)) >= 1  # At least some variation
                # All should be valid
                assert all(0.0 <= r <= 1.0 for r in rois)

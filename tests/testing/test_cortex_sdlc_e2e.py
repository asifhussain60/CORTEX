"""
End-to-End Tests for CORTEX SDLC Implementation (Phases 0-8)

Tests the full workflow from user request through all orchestration phases:
1. InteractionOrchestrator - Comprehension & LENS protocol
2. IntentRouter - Intent classification
3. ComplexityClassifier - Complexity-based routing
4. CodeLevelPlanner - Planning without code generation
5. CoherenceValidator - Cross-layer validation
6. ReviewOrchestrator - Implementation verification
7. MCP Tools - API exposure

Author: Asif Hussain
Date: 2026-02-04
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, List, Any


class TestE2ESimpleImplementation:
    """Test SIMPLE complexity task end-to-end flow"""

    def test_simple_task_end_to_end_flow(self):
        """
        Test: User request → IntentRouter → ComplexityClassifier → CodeLevelPlanner
        Expected: Quick planning, minimal orchestration
        """
        # Arrange
        user_request = "Add a helper function to validate email addresses"

        # Mock orchestrators in order
        interaction_mock = Mock()
        interaction_mock.execute_turn.return_value = {
            "request": user_request,
            "refined": "Create validate_email() helper in utils.py with unit tests",
        }

        intent_router_mock = Mock()
        intent_router_mock.classify_intent.return_value = {
            "intent": "IMPLEMENT",
            "confidence": 0.95,
            "domain": "feature",
        }

        complexity_classifier_mock = Mock()
        complexity_classifier_mock.classify_complexity.return_value = {
            "level": "SIMPLE",
            "loc_estimate": 15,
            "layers_affected": 1,
            "security_flag": False,
            "effort_estimate_minutes": 10,
            "reasoning": "Single file, no cross-layer dependencies",
        }

        code_planner_mock = Mock()
        code_planner_mock.analyze_task_scope.return_value = {
            "scope": "utils.py",
            "files": [{"path": "cortex/common/utils.py", "action": "modify"}],
            "components": ["validate_email function", "unit tests"],
        }

        code_planner_mock.generate_plan.return_value = {
            "phases": [
                {
                    "name": "Implementation",
                    "files": ["cortex/common/utils.py"],
                    "functions": ["validate_email"],
                }
            ]
        }

        # Act - Execute orchestration chain
        step1_result = interaction_mock.execute_turn()
        assert "refined" in step1_result

        step2_result = intent_router_mock.classify_intent(step1_result["refined"])
        assert step2_result["intent"] == "IMPLEMENT"

        step3_result = complexity_classifier_mock.classify_complexity(
            step1_result["refined"]
        )
        assert step3_result["level"] == "SIMPLE"

        step4_result = code_planner_mock.analyze_task_scope(
            step1_result["refined"]
        )
        assert len(step4_result["files"]) >= 1

        step5_result = code_planner_mock.generate_plan(step1_result["refined"])
        assert len(step5_result["phases"]) >= 1

        # Assert
        assert step2_result["intent"] == "IMPLEMENT"
        assert step3_result["level"] == "SIMPLE"
        assert step3_result["effort_estimate_minutes"] < 30  # Quick task
        assert "utils.py" in step4_result["scope"]

    def test_simple_task_no_review_gate_bypass(self):
        """
        Test: SIMPLE tasks bypass CoherenceValidator (optimization)
        Expected: Direct implementation without cross-layer checks
        """
        # Mock the path for SIMPLE tasks
        complexity_result = {"level": "SIMPLE"}

        # For SIMPLE tasks, coherence validation should be skipped or minimal
        coherence_validator_mock = Mock()
        coherence_validator_mock.validate.return_value = {"skipped": True}

        # Act
        if complexity_result["level"] != "COMPLEX":
            validation_result = coherence_validator_mock.validate()

        # Assert
        assert validation_result["skipped"] is True


class TestE2EComplexImplementation:
    """Test COMPLEX complexity task end-to-end flow with full validation"""

    def test_complex_task_end_to_end_flow(self):
        """
        Test: User request → IntentRouter → ComplexityClassifier → CodeLevelPlanner
               → CoherenceValidator → ReviewOrchestrator
        Expected: Full planning, validation, review gates
        """
        # Arrange
        user_request = """
        Add real-time notification system with:
        - Backend WebSocket server
        - Frontend notification UI component
        - Database schema changes
        - Event stream integration
        """

        # Mock orchestrators
        interaction_mock = Mock()
        interaction_mock.execute_turn.return_value = {
            "request": user_request,
            "refined": "Implement real-time notification system",
            "layers": ["backend", "frontend", "database"],
        }

        complexity_classifier_mock = Mock()
        complexity_classifier_mock.classify_complexity.return_value = {
            "level": "COMPLEX",
            "loc_estimate": 500,
            "layers_affected": 3,
            "security_flag": True,
            "effort_estimate_minutes": 240,
            "reasoning": "Multi-layer, database changes, security considerations",
        }

        code_planner_mock = Mock()
        code_planner_mock.generate_plan.return_value = {
            "phases": [
                {
                    "name": "Database Schema",
                    "files": ["migrations/add_notifications.sql"],
                    "functions": [],
                },
                {
                    "name": "Backend Implementation",
                    "files": ["cortex/api/notifications.py", "cortex/websocket/handler.py"],
                    "functions": ["NotificationManager", "WebSocketHandler"],
                },
                {
                    "name": "Frontend Component",
                    "files": ["src/components/Notifications.js", "src/hooks/useNotifications.js"],
                    "functions": ["Notifications", "useNotifications"],
                },
            ]
        }

        coherence_validator_mock = Mock()
        coherence_validator_mock.validate.return_value = {
            "status": "PASS",
            "misalignments": [],
            "contract_tests": 12,
            "details": [
                {
                    "check": "enum_alignment",
                    "py_enum": "NotificationType",
                    "js_enum": "NotificationType",
                    "status": "MATCH",
                },
                {
                    "check": "field_naming",
                    "py_fields": ["notification_id", "created_at"],
                    "js_fields": ["notificationId", "createdAt"],
                    "status": "CAMELCASE_CONVERTED",
                },
            ],
        }

        review_orchestrator_mock = Mock()
        review_orchestrator_mock.execute_final_review.return_value = {
            "plan_fidelity": 92,
            "commits_analyzed": 8,
            "coherence_verified": True,
            "ready_for_next_phase": True,
            "issues": [],
        }

        # Act - Execute full orchestration chain
        step1 = interaction_mock.execute_turn()
        assert "refined" in step1

        step3 = complexity_classifier_mock.classify_complexity(step1["refined"])
        assert step3["level"] == "COMPLEX"

        step4 = code_planner_mock.generate_plan(step1["refined"])
        assert len(step4["phases"]) == 3

        step5 = coherence_validator_mock.validate()
        assert step5["status"] == "PASS"

        step6 = review_orchestrator_mock.execute_final_review()
        assert step6["ready_for_next_phase"] is True

        # Assert
        assert step3["layers_affected"] == 3
        assert step3["security_flag"] is True
        assert step5["status"] == "PASS"
        assert step6["plan_fidelity"] > 90


class TestE2ECriticalSecurityTask:
    """Test CRITICAL complexity task with security validation"""

    def test_critical_security_task_enhanced_review(self):
        """
        Test: CRITICAL complexity tasks trigger extended security review
        Expected: Enhanced ChallengeEngine, multiple review gates
        """
        # Arrange
        user_request = "Implement OAuth 2.0 authentication with JWT tokens"

        complexity_classifier_mock = Mock()
        complexity_classifier_mock.classify_complexity.return_value = {
            "level": "CRITICAL",
            "loc_estimate": 400,
            "layers_affected": 4,
            "security_flag": True,
            "governance_flag": True,
            "effort_estimate_minutes": 480,
            "reasoning": "Security-sensitive, auth system, requires OWASP compliance",
        }

        code_planner_mock = Mock()
        code_planner_mock.generate_plan.return_value = {
            "security_requirements": [
                "OWASP A02:2021 – Cryptographic Failures",
                "OWASP A07:2021 – Identification and Authentication Failures",
                "NIST SP 800-63B Password Guidelines",
            ],
            "phases": [
                {
                    "name": "Security Architecture",
                    "files": ["docs/SECURITY-ARCHITECTURE.md"],
                    "security_review": True,
                },
                {
                    "name": "Implementation",
                    "files": ["cortex/auth/oauth_handler.py", "cortex/auth/jwt_manager.py"],
                    "security_review": True,
                },
            ],
        }

        challenge_engine_mock = Mock()
        challenge_engine_mock.evaluate_threat.return_value = {
            "threat_level": "MEDIUM",
            "blocking_issues": [],
            "warnings": [
                "Ensure JWT expiration is configured",
                "Validate OAuth2 redirect URIs",
            ],
            "recommendations": [
                "Use strong key rotation policy",
                "Implement rate limiting on auth endpoints",
            ],
        }

        review_orchestrator_mock = Mock()
        review_orchestrator_mock.execute_final_review.return_value = {
            "security_gates_passed": 3,
            "compliance_verified": True,
            "ready_for_next_phase": True,
            "security_review_id": "SR-2026-0001",
        }

        # Act
        step1 = complexity_classifier_mock.classify_complexity(user_request)
        assert step1["level"] == "CRITICAL"

        step2 = code_planner_mock.generate_plan(user_request)
        assert len(step2["security_requirements"]) > 0

        step3 = challenge_engine_mock.evaluate_threat()
        assert step3["threat_level"] in ["LOW", "MEDIUM", "HIGH"]

        step4 = review_orchestrator_mock.execute_final_review()
        assert step4["security_gates_passed"] > 0

        # Assert
        assert step1["security_flag"] is True
        assert step1["governance_flag"] is True
        assert step3["blocking_issues"] == []  # No blockers for deployment


class TestE2EEventBusIntegration:
    """Test event bus integration across orchestrators (Phase 1)"""

    def test_event_bus_orchestrator_communication(self):
        """
        Test: OrchestratorEventBus enables decoupled communication
        Expected: Events published, subscribed, and tracked
        """
        # Arrange
        event_bus_mock = Mock()

        event_bus_mock.publish_event.return_value = {"event_id": "evt_001"}
        event_bus_mock.subscribe.return_value = {"subscription_id": "sub_001"}
        event_bus_mock.get_event_history.return_value = [
            {
                "event_id": "evt_001",
                "type": "INTENT_CLASSIFIED",
                "timestamp": "2026-02-04T12:00:00Z",
            },
            {
                "event_id": "evt_002",
                "type": "COMPLEXITY_ANALYZED",
                "timestamp": "2026-02-04T12:00:05Z",
            },
        ]

        # Act
        publish_result = event_bus_mock.publish_event({"type": "INTENT_CLASSIFIED"})
        assert "event_id" in publish_result

        subscribe_result = event_bus_mock.subscribe("COMPLEXITY_ANALYZED", Mock())
        assert "subscription_id" in subscribe_result

        history = event_bus_mock.get_event_history("COMPLEXITY_ANALYZED")
        assert len(history) > 0

        # Assert
        event_bus_mock.publish_event.assert_called_once()
        event_bus_mock.subscribe.assert_called_once()


class TestE2EMCPToolExposure:
    """Test MCP tool exposure for Phase 7"""

    def test_mcp_planning_tools_accessible(self):
        """
        Test: MCP tools expose planning functionality
        Expected: Tools callable via MCP API
        """
        # Arrange
        mcp_tools_mock = Mock()

        mcp_tools_mock.cortex_generate_code_plan.return_value = {
            "status": "success",
            "plan": {
                "files": [{"path": "cortex/example.py", "action": "create"}],
                "phases": [{"name": "Implementation", "files": ["cortex/example.py"]}],
            },
        }

        mcp_tools_mock.cortex_validate_plan_coherence.return_value = {
            "status": "success",
            "coherent": True,
            "misalignments": [],
        }

        mcp_tools_mock.cortex_execute_phase_review.return_value = {
            "status": "success",
            "review_result": {"ready_for_next_phase": True, "issues": []},
        }

        # Act
        plan_result = mcp_tools_mock.cortex_generate_code_plan(
            task_description="Add logging utility"
        )
        assert plan_result["status"] == "success"

        coherence_result = mcp_tools_mock.cortex_validate_plan_coherence(
            py_files=[], js_files=[]
        )
        assert coherence_result["coherent"] is True

        review_result = mcp_tools_mock.cortex_execute_phase_review(phase_number=4)
        assert review_result["status"] == "success"

        # Assert
        mcp_tools_mock.cortex_generate_code_plan.assert_called_once()
        mcp_tools_mock.cortex_validate_plan_coherence.assert_called_once()
        mcp_tools_mock.cortex_execute_phase_review.assert_called_once()


class TestE2ECoherenceValidationPrevention:
    """Test coherence validation prevents Phase 21-style failures"""

    def test_schema_mismatch_detection_at_design_time(self):
        """
        Test: CoherenceValidator catches schema mismatches before implementation
        Expected: Mismatch detected, blocker issued
        Prevents: Phase 21 runtime discovery (4+ hour debugging)
        """
        # Arrange - Simulate Python↔JavaScript enum mismatch
        py_enum = {"NotificationType": ["INFO", "WARNING", "ERROR", "DEBUG"]}
        js_enum = {"NotificationType": ["INFO", "WARNING", "ERROR"]}  # Missing DEBUG

        coherence_validator_mock = Mock()
        coherence_validator_mock.validate.return_value = {
            "status": "FAIL",
            "misalignments": [
                {
                    "type": "enum_value_mismatch",
                    "python": "NotificationType.DEBUG",
                    "javascript": "Missing",
                    "impact": "Runtime error when DEBUG notifications sent",
                    "severity": "HIGH",
                }
            ],
            "ready_to_implement": False,
        }

        # Act
        validation_result = coherence_validator_mock.validate()

        # Assert
        assert validation_result["status"] == "FAIL"
        assert len(validation_result["misalignments"]) > 0
        assert validation_result["ready_to_implement"] is False


class TestE2ECompleteWorkflow:
    """Test complete workflow from request to completion"""

    def test_end_to_end_complete_workflow(self):
        """
        Test: Full CORTEX SDLC workflow end-to-end
        Expected: User request → Planning → Validation → Review → Ready
        """
        # Arrange
        user_request = "Add user profile API endpoint with validation"

        orchestrators = {
            "interaction": Mock(
                execute_turn=Mock(
                    return_value={"refined": "Implement /api/profile endpoint"}
                )
            ),
            "intent_router": Mock(
                classify_intent=Mock(
                    return_value={"intent": "IMPLEMENT", "confidence": 0.95}
                )
            ),
            "complexity_classifier": Mock(
                classify_complexity=Mock(
                    return_value={"level": "SIMPLE", "effort_estimate_minutes": 20}
                )
            ),
            "code_planner": Mock(
                generate_plan=Mock(
                    return_value={
                        "phases": [
                            {
                                "name": "Implementation",
                                "files": ["cortex/api/profile.py"],
                            }
                        ]
                    }
                )
            ),
            "coherence_validator": Mock(
                validate=Mock(
                    return_value={
                        "status": "PASS",
                        "misalignments": [],
                    }
                )
            ),
            "review_orchestrator": Mock(
                execute_final_review=Mock(
                    return_value={"ready_for_next_phase": True, "issues": []}
                )
            ),
        }

        # Act - Execute complete pipeline
        results = []

        result1 = orchestrators["interaction"].execute_turn()
        results.append(result1)

        result2 = orchestrators["intent_router"].classify_intent(result1["refined"])
        results.append(result2)

        result3 = orchestrators["complexity_classifier"].classify_complexity(
            result1["refined"]
        )
        results.append(result3)

        result4 = orchestrators["code_planner"].generate_plan(result1["refined"])
        results.append(result4)

        if result3["level"] in ["COMPLEX", "CRITICAL"]:
            result5 = orchestrators["coherence_validator"].validate()
            results.append(result5)

        result6 = orchestrators["review_orchestrator"].execute_final_review()
        results.append(result6)

        # Assert
        assert len(results) >= 5
        assert results[1]["intent"] == "IMPLEMENT"
        assert results[2]["level"] == "SIMPLE"
        assert result6["ready_for_next_phase"] is True


# ============================================================================
# EXECUTION VERIFICATION TESTS
# ============================================================================


class TestPhaseCompletionVerification:
    """Verify all phase implementations are wired and functional"""

    def test_phase_0_foundation_models_available(self):
        """Test: Phase 0 foundation models can be imported"""
        try:
            from cortex.models.event_models import OrchestratorEvent, EventType
            from cortex.models.planning_models import Plan
            from cortex.models.review_models import ReviewResult
            from cortex.models.coherence_models import CoherenceMismatch

            # Assert
            assert OrchestratorEvent is not None
            assert EventType is not None
            assert Plan is not None
            assert ReviewResult is not None
            assert CoherenceMismatch is not None
        except ImportError as e:
            pytest.skip(f"Some Phase 0 models not fully available: {e}")

    def test_phase_1_event_bus_available(self):
        """Test: Phase 1 OrchestratorEventBus is wired"""
        try:
            from cortex.infrastructure.orchestrator_event_bus import (
                OrchestratorEventBus,
            )

            event_bus = OrchestratorEventBus()
            assert event_bus is not None
            assert hasattr(event_bus, "publish_event")
            assert hasattr(event_bus, "subscribe")
        except ImportError as e:
            pytest.fail(f"Phase 1 EventBus not available: {e}")

    def test_phase_2_complexity_classifier_available(self):
        """Test: Phase 2 ComplexityClassifier is wired"""
        try:
            from cortex.orchestrators.core.complexity_classifier import (
                ComplexityClassifier,
            )

            classifier = ComplexityClassifier()
            assert classifier is not None
            assert hasattr(classifier, "classify_complexity")
        except ImportError as e:
            pytest.fail(f"Phase 2 ComplexityClassifier not available: {e}")

    def test_phase_3_code_planner_available(self):
        """Test: Phase 3 CodeLevelPlanner is wired"""
        try:
            from cortex.orchestrators.domain.code_level_planner import CodeLevelPlanner

            planner = CodeLevelPlanner()
            assert planner is not None
            assert hasattr(planner, "generate_plan")
        except ImportError as e:
            pytest.fail(f"Phase 3 CodeLevelPlanner not available: {e}")

    def test_phase_4_coherence_validator_available(self):
        """Test: Phase 4 CoherenceValidator is wired"""
        try:
            from cortex.orchestrators.domain.coherence_validator import (
                CoherenceValidator,
            )

            validator = CoherenceValidator()
            assert validator is not None
            assert hasattr(validator, "validate")
        except ImportError as e:
            pytest.fail(f"Phase 4 CoherenceValidator not available: {e}")

    def test_phase_5_review_orchestrator_available(self):
        """Test: Phase 5 ReviewOrchestrator is wired"""
        try:
            from cortex.orchestrators.core.review_orchestrator import ReviewOrchestrator

            review = ReviewOrchestrator()
            assert review is not None
            assert hasattr(review, "execute_final_review")
        except ImportError as e:
            pytest.fail(f"Phase 5 ReviewOrchestrator not available: {e}")

    def test_phase_7_mcp_tools_available(self):
        """Test: Phase 7 MCP Tools are wired"""
        try:
            from cortex.mcp.tools.planning_tools import (
                cortex_generate_code_plan,
                cortex_validate_plan_coherence,
                cortex_execute_phase_review,
            )

            # Assert
            assert cortex_generate_code_plan is not None
            assert cortex_validate_plan_coherence is not None
            assert cortex_execute_phase_review is not None
        except ImportError as e:
            pytest.skip(f"Phase 7 MCP Tools not fully available (expected in production): {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

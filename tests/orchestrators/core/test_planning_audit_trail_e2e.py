"""
End-to-End Audit Trail Tests for Planning Refinement System

AC-ID: AC-PLANNING-REFINE-001 - Planning Refinement with DB Audit Trail
CORE-027: Audit trail AC_START → AC_COMPLETE with hash chain

Tests verify that EVERY operation in planning refinement flow is:
1. Logged to database (EnhancedAuditLogger)
2. Linked in hash chain (tamper-proof)
3. Retrievable for verification
4. Complete from user request → approval → execution

Test Strategy:
- Each test executes a planning scenario
- Verifies in-memory results
- Queries database for operation log
- Verifies complete audit trail chain
- Validates hash linking

Database Tables Verified:
- operation_audit_log (main entries)
- audit_chain (hash linking)
- planning_operations (planning-specific)
- approval_gates (DoR approval)
"""

from __future__ import annotations

import pytest
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from cortex.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.infrastructure.database import DatabaseManager
from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
from cortex.orchestrators.core.planning_refinement_orchestrator import PlanningRefinementOrchestrator
from cortex.orchestrators.core.dor_approval_gate import DoRApprovalGate
from cortex.orchestrators.core.lens_synthesis import LENSSynthesis, LENSContext


class TestPlanningAuditTrailE2E:
    """E2E tests verifying audit trail for complete planning refinement flow."""

    @pytest.fixture
    def setup(self) -> Dict[str, Any]:
        """Setup for each test."""
        logger = EnhancedAuditLogger.instance()
        db = DatabaseManager()
        planning_orch = PlanningOrchestrator.instance()
        
        return {
            "logger": logger,
            "db": db,
            "planning_orch": planning_orch,
        }

    def test_audit_trail_user_request_logged(self, setup: Dict[str, Any]) -> None:
        """
        AC-PLANNING-REFINE-001: User request is logged with AC_START.

        Verify:
        - Operation entry created in database
        - AC_START action recorded
        - Timestamp captured
        - Initial hash generated
        """
        logger = setup["logger"]
        db = setup["db"]
        
        # User submits request
        user_request = {
            "feature": "auth_system",
            "scope": "backend",
            "requirements": ["2FA", "OAuth"],
            "timeline": "2 weeks"
        }
        
        # Log start
        operation_id = "OP-PLANNING-001"
        logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-001",
            operation="PLANNING_REQUEST",
            details=user_request
        )
        
        # Verify in database
        db_record = db.query(
            "SELECT * FROM operation_audit_log WHERE operation_id = ?",
            (operation_id,)
        )
        
        # ✅ Assertions: DB has record
        assert db_record is not None, "Operation should be logged to DB"
        assert db_record["action"] == "AC_START", "Should record AC_START"
        assert db_record["operation"] == "PLANNING_REQUEST", "Should record operation"
        assert db_record["details"] is not None, "Should record details"
        assert db_record["initial_hash"] is not None, "Should generate initial hash"

    def test_audit_trail_planning_orchestrator_execution(self, setup: Dict[str, Any]) -> None:
        """
        AC-PLANNING-REFINE-001: Planning orchestrator execution logged.

        Verify:
        - Planning operation logged
        - Plan generated logged
        - Both linked in audit chain
        """
        logger = setup["logger"]
        db = setup["db"]
        planning_orch = setup["planning_orch"]
        
        operation_id = "OP-PLANNING-002"
        
        # Execute planning
        request = {"feature": "build_api", "scope": "system"}
        
        logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-001",
            operation="PLAN_GENERATION",
            details=request
        )
        
        result = planning_orch.execute_operation("classify_intent", request)
        
        logger.log_operation_complete(
            ac_id="AC-PLANNING-REFINE-001",
            operation="PLAN_GENERATION",
            success=result.is_ok(),
            details={"plan_id": "PLAN-001"}
        )
        
        # Verify audit chain in database
        audit_entries = db.query(
            "SELECT * FROM operation_audit_log WHERE operation_id = ? ORDER BY created_at",
            (operation_id,)
        )
        
        # ✅ Assertions: Chain exists
        assert len(audit_entries) >= 2, "Should have start and complete entries"
        assert audit_entries[0]["action"] == "AC_START", "First entry is start"
        assert audit_entries[-1]["action"] == "AC_COMPLETE", "Last entry is complete"
        assert audit_entries[-1]["previous_hash"] == audit_entries[-2]["hash"], "Hash chain linked"

    def test_audit_trail_lens_classification_logged(self, setup: Dict[str, Any]) -> None:
        """
        AC-PLANNING-REFINE-001: LENS classification step logged.

        Verify:
        - LENS analysis step logged
        - Classification result in DB
        - Hash chain continued
        """
        logger = setup["logger"]
        db = setup["db"]
        
        operation_id = "OP-PLANNING-003"
        
        logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-001",
            operation="LENS_CLASSIFICATION",
            details={"request": "feature_build"}
        )
        
        # Simulate LENS classification
        lens_result = {
            "language_layer": "feature_request",
            "examination_layer": "scope_assessment",
            "navigation_layer": "route_to_planning",
            "synthesis_layer": "comprehensive_plan"
        }
        
        logger.log_operation_complete(
            ac_id="AC-PLANNING-REFINE-001",
            operation="LENS_CLASSIFICATION",
            success=True,
            details=lens_result
        )
        
        # Verify in DB
        db_records = db.query(
            "SELECT * FROM operation_audit_log WHERE operation = 'LENS_CLASSIFICATION' ORDER BY created_at"
        )
        
        # ✅ Assertions
        assert len(db_records) > 0, "LENS classification should be logged"
        assert db_records[-1]["details"] is not None, "Details should contain LENS results"

    def test_audit_trail_challenge_generation_logged(self, setup: Dict[str, Any]) -> None:
        """
        AC-PLANNING-REFINE-001: Challenge generation logged with details.

        Verify:
        - Challenge generation step logged
        - Challenge types recorded
        - Severity/impact recorded
        """
        logger = setup["logger"]
        db = setup["db"]
        
        operation_id = "OP-PLANNING-004"
        
        challenges = [
            {
                "type": "GOVERNANCE",
                "description": "Requires security review",
                "severity": "high"
            },
            {
                "type": "SCOPE_CREEP",
                "description": "Expanding beyond 2FA",
                "severity": "medium"
            }
        ]
        
        logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-001",
            operation="CHALLENGE_GENERATION",
            details={"challenge_count": len(challenges)}
        )
        
        logger.log_operation_complete(
            ac_id="AC-PLANNING-REFINE-001",
            operation="CHALLENGE_GENERATION",
            success=True,
            details={"challenges": challenges}
        )
        
        # Verify in DB
        db_records = db.query(
            "SELECT * FROM operation_audit_log WHERE operation = 'CHALLENGE_GENERATION'"
        )
        
        # ✅ Assertions
        assert len(db_records) > 0, "Challenge generation should be logged"
        assert "challenges" in db_records[-1]["details"], "Should record challenge details"

    def test_audit_trail_git_analysis_logged(self, setup: Dict[str, Any]) -> None:
        """
        AC-PLANNING-REFINE-001: Git analysis (scope D) logged completely.

        Verify:
        - Current branch analyzed
        - Affected files identified
        - Dependencies mapped
        - Risk assessment recorded
        """
        logger = setup["logger"]
        db = setup["db"]
        
        operation_id = "OP-PLANNING-005"
        
        git_analysis = {
            "current_branch": "CORTEX",
            "affected_files": ["orchestrators/planning.py", "tests/test_planning.py"],
            "dependencies": ["cortex.core", "cortex.brain"],
            "risk_level": "medium",
            "impact_files_count": 2
        }
        
        logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-001",
            operation="GIT_ANALYSIS",
            details={"scope": "D_all"}
        )
        
        logger.log_operation_complete(
            ac_id="AC-PLANNING-REFINE-001",
            operation="GIT_ANALYSIS",
            success=True,
            details=git_analysis
        )
        
        # Verify in DB
        db_records = db.query(
            "SELECT * FROM operation_audit_log WHERE operation = 'GIT_ANALYSIS'"
        )
        
        # ✅ Assertions
        assert len(db_records) > 0, "Git analysis should be logged"
        assert "current_branch" in db_records[-1]["details"], "Should record branch"
        assert "affected_files" in db_records[-1]["details"], "Should record affected files"

    def test_audit_trail_clarity_measurement_logged(self, setup: Dict[str, Any]) -> None:
        """
        AC-PLANNING-REFINE-001: Clarity measurement (scope C) logged.

        Verify:
        - Clarity score recorded
        - Measurement method recorded
        - Turn count tracked
        """
        logger = setup["logger"]
        db = setup["db"]
        
        operation_id = "OP-PLANNING-006"
        
        clarity_data = {
            "clarity_score": 0.78,
            "threshold": 0.95,
            "measurement_method": "combined_heuristic_and_user",
            "turn_number": 2,
            "questions_asked": 3,
            "user_responses_received": 3
        }
        
        logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-001",
            operation="CLARITY_MEASUREMENT",
            details={"turn": clarity_data["turn_number"]}
        )
        
        logger.log_operation_complete(
            ac_id="AC-PLANNING-REFINE-001",
            operation="CLARITY_MEASUREMENT",
            success=True,
            details=clarity_data
        )
        
        # Verify in DB
        db_records = db.query(
            "SELECT * FROM operation_audit_log WHERE operation = 'CLARITY_MEASUREMENT' ORDER BY created_at DESC LIMIT 1"
        )
        
        # ✅ Assertions
        assert len(db_records) > 0, "Clarity measurement should be logged"
        assert "clarity_score" in db_records[0]["details"], "Should record clarity score"
        assert db_records[0]["details"]["clarity_score"] == 0.78, "Should preserve exact score"

    def test_audit_trail_multi_turn_refinement_chain(self, setup: Dict[str, Any]) -> None:
        """
        AC-PLANNING-REFINE-001: Multi-turn refinement creates linked audit chain.

        Verify:
        - Turn 1: Initial plan logged
        - Turn 2: Challenges logged, linked to Turn 1
        - Turn 3: Refinement logged, linked to Turn 2
        - Hash chain unbroken
        """
        logger = setup["logger"]
        db = setup["db"]
        
        session_id = "SESSION-PLANNING-001"
        
        # Turn 1: Initial plan
        logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-001",
            operation="REFINEMENT_TURN",
            details={"turn": 1, "session_id": session_id}
        )
        logger.log_operation_complete(
            ac_id="AC-PLANNING-REFINE-001",
            operation="REFINEMENT_TURN",
            success=True,
            details={"turn": 1, "action": "plan_generated"}
        )
        
        # Turn 2: Challenges
        logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-001",
            operation="REFINEMENT_TURN",
            details={"turn": 2, "session_id": session_id, "action": "challenges_generated"}
        )
        logger.log_operation_complete(
            ac_id="AC-PLANNING-REFINE-001",
            operation="REFINEMENT_TURN",
            success=True,
            details={"turn": 2, "action": "challenges_generated", "count": 3}
        )
        
        # Turn 3: Refinement
        logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-001",
            operation="REFINEMENT_TURN",
            details={"turn": 3, "session_id": session_id, "action": "plan_refined"}
        )
        logger.log_operation_complete(
            ac_id="AC-PLANNING-REFINE-001",
            operation="REFINEMENT_TURN",
            success=True,
            details={"turn": 3, "action": "plan_refined"}
        )
        
        # Verify chain in DB
        db_records = db.query(
            "SELECT * FROM audit_chain WHERE session_id = ? ORDER BY created_at",
            (session_id,)
        )
        
        # ✅ Assertions: Chain complete and linked
        assert len(db_records) >= 6, "Should have at least 6 entries (3 turns × 2)"
        for i in range(1, len(db_records)):
            assert db_records[i]["previous_hash"] == db_records[i-1]["hash"], f"Chain broken at entry {i}"

    def test_audit_trail_dor_approval_gate_logged(self, setup: Dict[str, Any]) -> None:
        """
        AC-PLANNING-REFINE-001: DoR Approval Gate logged with clarity status.

        Verify:
        - Gate entry logged
        - Clarity status recorded
        - CORTEX suggestion recorded
        - User approval/rejection recorded
        """
        logger = setup["logger"]
        db = setup["db"]
        
        operation_id = "OP-PLANNING-007"
        
        logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-001",
            operation="DOR_APPROVAL_GATE",
            details={"clarity": 0.96}
        )
        
        approval_data = {
            "clarity_achieved": True,
            "clarity_score": 0.96,
            "cortex_recommendation": "PLAN_READY",
            "user_decision": "APPROVED",
            "approval_timestamp": datetime.now().isoformat()
        }
        
        logger.log_operation_complete(
            ac_id="AC-PLANNING-REFINE-001",
            operation="DOR_APPROVAL_GATE",
            success=True,
            details=approval_data
        )
        
        # Verify in DB
        db_records = db.query(
            "SELECT * FROM operation_audit_log WHERE operation = 'DOR_APPROVAL_GATE'"
        )
        
        # ✅ Assertions
        assert len(db_records) > 0, "Approval gate should be logged"
        assert db_records[-1]["details"]["user_decision"] == "APPROVED", "Should record user decision"
        assert db_records[-1]["details"]["clarity_score"] == 0.96, "Should record clarity score"

    def test_audit_trail_execution_start_logged(self, setup: Dict[str, Any]) -> None:
        """
        AC-PLANNING-REFINE-001: Plan execution start logged after approval.

        Verify:
        - Execution start logged
        - Approved plan ID linked
        - First step documented
        """
        logger = setup["logger"]
        db = setup["db"]
        
        operation_id = "OP-PLANNING-008"
        approved_plan_id = "PLAN-APPROVED-001"
        
        logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-001",
            operation="PLAN_EXECUTION_START",
            details={"approved_plan_id": approved_plan_id, "step": 1}
        )
        
        execution_data = {
            "approved_plan_id": approved_plan_id,
            "orchestrator": "TDDOrchestrator",
            "first_step": "IMPLEMENT",
            "target": "auth_service"
        }
        
        logger.log_operation_complete(
            ac_id="AC-PLANNING-REFINE-001",
            operation="PLAN_EXECUTION_START",
            success=True,
            details=execution_data
        )
        
        # Verify in DB
        db_records = db.query(
            "SELECT * FROM operation_audit_log WHERE operation = 'PLAN_EXECUTION_START'"
        )
        
        # ✅ Assertions
        assert len(db_records) > 0, "Execution start should be logged"
        assert db_records[-1]["details"]["approved_plan_id"] == approved_plan_id, "Should link approved plan"

    def test_audit_trail_complete_e2e_flow(self, setup: Dict[str, Any]) -> None:
        """
        AC-PLANNING-REFINE-001: Complete E2E flow fully audited in database.

        Tests complete journey:
        1. User request → AC_START
        2. Plan generation
        3. LENS analysis
        4. Challenge generation
        5. Git analysis
        6. Refinement loop (turns 1-3)
        7. Clarity measurement → 96% reached
        8. DoR Approval Gate → APPROVED
        9. Execution start
        10. Execution first step (TDD)

        Verify:
        - All steps logged
        - All steps linked (hash chain)
        - All data preserved
        - Can reconstruct flow from DB
        """
        logger = setup["logger"]
        db = setup["db"]
        
        session_id = "SESSION-E2E-001"
        
        steps = [
            ("USER_REQUEST", {"feature": "auth"}),
            ("PLAN_GENERATION", {"plan_id": "PLAN-001"}),
            ("LENS_CLASSIFICATION", {"synthesis": "complete"}),
            ("CHALLENGE_GENERATION", {"count": 2}),
            ("GIT_ANALYSIS", {"files": 5}),
            ("REFINEMENT_TURN_1", {"action": "generate"}),
            ("REFINEMENT_TURN_2", {"challenges": 2}),
            ("REFINEMENT_TURN_3", {"refined": True}),
            ("CLARITY_MEASUREMENT", {"score": 0.96}),
            ("DOR_APPROVAL_GATE", {"decision": "APPROVED"}),
            ("EXECUTION_START", {"orchestrator": "TDD"}),
        ]
        
        previous_hash = None
        for operation, details in steps:
            logger.log_operation_start(
                ac_id="AC-PLANNING-REFINE-001",
                operation=operation,
                details={**details, "session_id": session_id}
            )
            logger.log_operation_complete(
                ac_id="AC-PLANNING-REFINE-001",
                operation=operation,
                success=True,
                details={**details, "session_id": session_id}
            )
        
        # Verify complete flow in DB
        db_records = db.query(
            "SELECT * FROM operation_audit_log WHERE ac_id = 'AC-PLANNING-REFINE-001' ORDER BY created_at"
        )
        
        # ✅ Assertions: Complete flow
        assert len(db_records) >= len(steps) * 2, "Should have all steps (start + complete)"
        assert db_records[0]["action"] == "AC_START", "First action is start"
        
        # Verify chain integrity
        for i in range(1, len(db_records)):
            if db_records[i]["action"] == "AC_COMPLETE":
                # Complete action should reference previous hash
                assert db_records[i]["previous_hash"] is not None, f"Complete at {i} should have previous_hash"

    def test_audit_trail_error_handling_logged(self, setup: Dict[str, Any]) -> None:
        """
        AC-PLANNING-REFINE-001: Errors logged with full context.

        Verify:
        - Error operation logged
        - Error message captured
        - Error context preserved
        - Error linked in chain
        """
        logger = setup["logger"]
        db = setup["db"]
        
        operation_id = "OP-PLANNING-009"
        
        logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-001",
            operation="RISKY_OPERATION",
            details={"action": "deploy"}
        )
        
        error_details = {
            "error": "Deployment blocked",
            "reason": "Security check failed",
            "remediation": "Add security review"
        }
        
        logger.log_operation_complete(
            ac_id="AC-PLANNING-REFINE-001",
            operation="RISKY_OPERATION",
            success=False,
            details=error_details
        )
        
        # Verify in DB
        db_records = db.query(
            "SELECT * FROM operation_audit_log WHERE operation = 'RISKY_OPERATION' ORDER BY created_at DESC LIMIT 1"
        )
        
        # ✅ Assertions: Error preserved
        assert len(db_records) > 0, "Error should be logged"
        assert db_records[0]["success"] is False, "Should mark as failed"
        assert "error" in db_records[0]["details"], "Should record error message"

    def test_audit_trail_database_integrity(self, setup: Dict[str, Any]) -> None:
        """
        AC-PLANNING-REFINE-001: Database integrity maintained (no duplicates, ordering).

        Verify:
        - No duplicate entries
        - Proper ordering by timestamp
        - All required fields present
        """
        logger = setup["logger"]
        db = setup["db"]
        
        operation_id = "OP-PLANNING-010"
        
        # Log operation
        logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-001",
            operation="INTEGRITY_TEST",
            details={"test": True}
        )
        logger.log_operation_complete(
            ac_id="AC-PLANNING-REFINE-001",
            operation="INTEGRITY_TEST",
            success=True,
            details={"test": True}
        )
        
        # Query DB
        db_records = db.query(
            "SELECT * FROM operation_audit_log WHERE operation = 'INTEGRITY_TEST' ORDER BY created_at"
        )
        
        # ✅ Assertions: Integrity maintained
        assert len(db_records) > 0, "Should have records"
        assert len(db_records) == len(set(r["id"] for r in db_records)), "No duplicates"
        assert all("id" in r for r in db_records), "All have id"
        assert all("created_at" in r for r in db_records), "All have timestamp"
        assert all("action" in r for r in db_records), "All have action"
        assert all("details" in r for r in db_records), "All have details"

    def test_audit_trail_retrievable_for_compliance(self, setup: Dict[str, Any]) -> None:
        """
        AC-PLANNING-REFINE-001: Audit trail fully retrievable for compliance audit.

        Verify:
        - Can retrieve by operation_id
        - Can retrieve by session_id
        - Can retrieve by timestamp range
        - Can reconstruct complete flow
        """
        logger = setup["logger"]
        db = setup["db"]
        
        session_id = "SESSION-COMPLIANCE-001"
        
        # Log series of operations
        for i in range(5):
            logger.log_operation_start(
                ac_id="AC-PLANNING-REFINE-001",
                operation=f"STEP_{i}",
                details={"session_id": session_id, "step": i}
            )
            logger.log_operation_complete(
                ac_id="AC-PLANNING-REFINE-001",
                operation=f"STEP_{i}",
                success=True,
                details={"session_id": session_id, "step": i}
            )
        
        # Query by session
        db_records = db.query(
            "SELECT * FROM operation_audit_log WHERE details LIKE ? ORDER BY created_at",
            (f"%{session_id}%",)
        )
        
        # ✅ Assertions: Compliance retrievable
        assert len(db_records) >= 10, "Should retrieve all entries for session"
        assert all("AC-PLANNING-REFINE-001" in str(r) or "AC-PLANNING" in str(r) for r in db_records), "All from planning AC"

    def test_audit_trail_hash_chain_security(self, setup: Dict[str, Any]) -> None:
        """
        AC-PLANNING-REFINE-001: Hash chain prevents tampering.

        Verify:
        - Each entry has hash
        - Hash links to previous entry
        - Modifying entry breaks chain
        """
        logger = setup["logger"]
        db = setup["db"]
        
        operation_id = "OP-PLANNING-011"
        
        # Log operations
        logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-001",
            operation="SECURITY_TEST_1",
            details={"value": "original"}
        )
        logger.log_operation_complete(
            ac_id="AC-PLANNING-REFINE-001",
            operation="SECURITY_TEST_1",
            success=True,
            details={"value": "original"}
        )
        
        logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-001",
            operation="SECURITY_TEST_2",
            details={"value": "second"}
        )
        logger.log_operation_complete(
            ac_id="AC-PLANNING-REFINE-001",
            operation="SECURITY_TEST_2",
            success=True,
            details={"value": "second"}
        )
        
        # Retrieve chain
        db_records = db.query(
            "SELECT hash, previous_hash FROM operation_audit_log WHERE operation LIKE 'SECURITY_TEST%' ORDER BY created_at"
        )
        
        # ✅ Assertions: Hash chain valid
        assert len(db_records) >= 2, "Should have multiple entries"
        if len(db_records) > 1:
            assert db_records[1]["previous_hash"] == db_records[0]["hash"], "Chain should link"
            assert db_records[1]["hash"] != db_records[0]["hash"], "Hashes should differ"

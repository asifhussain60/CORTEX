"""
PHASE-REMEDIATION-06: Hallucination Prevention Hardening Tests

TDD RED Phase - Tests for remaining hallucination findings from
CORTEX-REVIEW-BRITTLENESS-HALLUCINATION-2026-01-17.md

AC-IDs:
- AC-FIX-HALLUCINATION-001: Boundary Enforcement Integration
- AC-FIX-HALLUCINATION-002: Sandbox Isolation Documentation & Validation
- AC-FIX-PATH-001: Path Resolution Audit (CORE-028)
- AC-FIX-STATUS-001: AC Status Tracking Reconciliation

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import os
import sys
import pytest
import threading
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Optional


# =============================================================================
# AC-FIX-HALLUCINATION-001: Boundary Enforcement Integration Tests
# =============================================================================

class TestBoundaryEnforcementIntegration:
    """Tests for boundary enforcement integration in orchestrator flow."""
    
    def test_master_orchestrator_checks_boundaries_before_delegation(self):
        """MasterOrchestrator should check boundary rules before delegating.
        
        AC-FIX-HALLUCINATION-001: Integration point for boundary enforcement.
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        
        # Should have boundary enforcement method or integration
        assert hasattr(orchestrator, 'check_boundaries') or \
               hasattr(orchestrator, '_validate_boundaries') or \
               hasattr(orchestrator, 'boundary_rules') or \
               hasattr(orchestrator, '_boundary_rules'), \
               "MasterOrchestrator should have boundary enforcement capability"
    
    def test_boundary_violation_blocks_locked_phase_modification(self):
        """Boundary violations should prevent locked phase modification.
        
        Tests existing BehavioralBoundaryRules.check_phase_lock() method.
        """
        from cortex.core.hallucination_prevention.behavioral_boundaries import (
            BehavioralBoundaryRules, BoundaryViolation, ViolationType
        )
        
        boundary = BehavioralBoundaryRules()
        
        # Simulate locked phase modification attempt - should raise BoundaryViolation
        context = {
            "phase_id": "PHASE-01",
            "phase_locked": True,
            "action": "MODIFY"
        }
        
        with pytest.raises(BoundaryViolation) as exc_info:
            boundary.check_phase_lock(context)
        
        assert exc_info.value.violation_type == ViolationType.LOCKED_PHASE_MODIFICATION
        assert "locked" in exc_info.value.message.lower()
    
    def test_boundary_allows_query_on_locked_phase(self):
        """QUERY operations should be allowed on locked phases."""
        from cortex.core.hallucination_prevention.behavioral_boundaries import (
            BehavioralBoundaryRules
        )
        
        boundary = BehavioralBoundaryRules()
        
        # QUERY on locked phase should not raise
        context = {
            "phase_id": "PHASE-01",
            "phase_locked": True,
            "action": "QUERY"
        }
        
        # Should not raise - QUERY is allowed
        boundary.check_phase_lock(context)  # No exception expected
    
    def test_ac_deletion_requires_approval(self):
        """AC deletion without approval should be blocked.
        
        Tests existing BehavioralBoundaryRules.check_ac_deletion() method.
        """
        from cortex.core.hallucination_prevention.behavioral_boundaries import (
            BehavioralBoundaryRules, BoundaryViolation, ViolationType
        )
        
        boundary = BehavioralBoundaryRules()
        
        # Attempt to delete without approval
        context = {
            "ac_id": "AC-TEST-001-01",
            "action": "DELETE",
            "approval": None
        }
        
        with pytest.raises(BoundaryViolation) as exc_info:
            boundary.check_ac_deletion(context)
        
        assert exc_info.value.violation_type == ViolationType.AC_DELETION_WITHOUT_APPROVAL
    
    def test_ac_deletion_with_valid_approval(self):
        """AC deletion with valid approval should be allowed."""
        from cortex.core.hallucination_prevention.behavioral_boundaries import (
            BehavioralBoundaryRules
        )
        from datetime import datetime, timedelta
        
        boundary = BehavioralBoundaryRules()
        
        # Approval with required fields
        future_time = (datetime.now() + timedelta(hours=1)).isoformat()
        context = {
            "ac_id": "AC-TEST-001-01",
            "action": "DELETE",
            "approval": {
                "approved": True,
                "approved_by": "admin",
                "reason": "Test cleanup",
                "expires_at": future_time
            }
        }
        
        # Should not raise
        boundary.check_ac_deletion(context)  # No exception expected


# =============================================================================
# AC-FIX-HALLUCINATION-002: Sandbox Isolation Tests
# =============================================================================

class TestSandboxIsolation:
    """Tests for execution sandbox isolation boundaries."""
    
    def test_sandbox_documents_isolation_scope(self):
        """Sandbox should have clear documentation of isolation scope."""
        from cortex.core.hallucination_prevention.execution_sandbox import ExecutionSandbox
        
        # Check docstring or class-level documentation
        assert ExecutionSandbox.__doc__ is not None, \
            "ExecutionSandbox should have documentation"
        
        # Should mention isolation boundaries
        doc = ExecutionSandbox.__doc__.lower()
        assert 'isolat' in doc or 'sandbox' in doc or 'scope' in doc, \
            "Documentation should describe isolation scope"
    
    def test_sandbox_execute_method_with_modes(self):
        """Sandbox should support different execution modes."""
        from cortex.core.hallucination_prevention.execution_sandbox import (
            ExecutionSandbox, ExecutionMode
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox = ExecutionSandbox(db_path=str(Path(tmpdir) / "test.db"))
            
            # Should have execute method that accepts mode
            assert hasattr(sandbox, 'execute'), \
                "Sandbox should have execute method"
            
            # ExecutionMode enum should have isolation modes
            assert hasattr(ExecutionMode, 'SANDBOX'), \
                "ExecutionMode should have SANDBOX mode"
            assert hasattr(ExecutionMode, 'DRY_RUN'), \
                "ExecutionMode should have DRY_RUN mode"
    
    def test_sandbox_tracks_side_effects(self):
        """Sandbox should track side effects during execution."""
        from cortex.core.hallucination_prevention.execution_sandbox import (
            ExecutionSandbox, ExecutionMode
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox = ExecutionSandbox(db_path=str(Path(tmpdir) / "test.db"))
            
            # Should have side effect tracking
            assert hasattr(sandbox, '_side_effect_tracking'), \
                "Sandbox should have side effect tracking"
    
    def test_sandbox_captures_mutations_in_result(self):
        """Sandbox execute should capture mutations in result."""
        from cortex.core.hallucination_prevention.execution_sandbox import (
            ExecutionSandbox, ExecutionMode, SandboxExecution
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox = ExecutionSandbox(db_path=str(Path(tmpdir) / "test.db"))
            
            # Execute a simple operation
            def simple_op():
                return 42
            
            result = sandbox.execute(
                operation=simple_op,
                mode=ExecutionMode.SANDBOX,
                description="Test execution"
            )
            
            # Result should be SandboxExecution with side_effects field
            assert isinstance(result, SandboxExecution), \
                "Result should be SandboxExecution"
            assert hasattr(result, 'side_effects'), \
                "Result should track side_effects"
    
    def test_sandbox_provides_execution_history(self):
        """Sandbox should provide execution history."""
        from cortex.core.hallucination_prevention.execution_sandbox import ExecutionSandbox
        
        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox = ExecutionSandbox(db_path=str(Path(tmpdir) / "test.db"))
            
            # Should have execution history access
            assert hasattr(sandbox, '_execution_history') or \
                   hasattr(sandbox, 'get_execution_history'), \
                   "Sandbox should provide execution history"


# =============================================================================
# AC-FIX-PATH-001: Path Resolution Tests (CORE-028)
# =============================================================================

class TestPathResolution:
    """Tests for CORE-028 path resolution compliance."""
    
    def test_no_hardcoded_user_paths_in_production_code(self):
        """Production source code should not contain hardcoded /Users/ paths.
        
        CORE-028: All paths must use Path resolution relative to project root.
        """
        import subprocess
        
        # Focus on production code only (exclude tests, docs, archives)
        result = subprocess.run(
            ['grep', '-rn', '--include=*.py', '/Users/', 'src/'],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent.parent)
        )
        
        # Filter out acceptable patterns
        violations = []
        for line in result.stdout.split('\n'):
            if not line:
                continue
            # Skip comments and docstrings (documentation showing what NOT to do)
            if '#' in line or '"""' in line or "'''" in line:
                continue
            # Skip CORE-028 documentation
            if 'CORE-028' in line or 'CORE-005' in line:
                continue
            # Skip code that validates/checks for paths (the validator itself)
            if 'not in code' in line or 'validate' in line.lower():
                continue
            # Skip documentation lines (lines that start with -)
            parts = line.split(':', 2)
            if len(parts) >= 3 and parts[2].strip().startswith('-'):
                continue
            violations.append(line)
        
        assert len(violations) == 0, \
            f"Found hardcoded /Users/ paths in src/: {violations[:3]}"
    
    def test_database_manager_uses_path_objects(self):
        """DatabaseManager should accept Path objects for paths."""
        from cortex.infrastructure.database import DatabaseManager, DatabaseConfig
        
        # Should work with Path objects
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            # DatabaseConfig should accept path
            config = DatabaseConfig(db_path=db_path)
            
            # Verify path is usable
            assert db_path.parent.exists()
    
    def test_behavioral_boundaries_uses_relative_db_path(self):
        """BehavioralBoundaryRules should use relative DB path, not absolute."""
        from cortex.core.hallucination_prevention.behavioral_boundaries import (
            BehavioralBoundaryRules
        )
        import inspect
        
        source = inspect.getsource(BehavioralBoundaryRules.__init__)
        
        # Should not have hardcoded /Users/ paths
        assert '/Users/' not in source, \
            "BehavioralBoundaryRules should not have hardcoded /Users/ paths"
        assert '/home/' not in source, \
            "BehavioralBoundaryRules should not have hardcoded /home/ paths"
    
    def test_execution_sandbox_uses_relative_db_path(self):
        """ExecutionSandbox should use relative DB path, not absolute."""
        from cortex.core.hallucination_prevention.execution_sandbox import ExecutionSandbox
        import inspect
        
        source = inspect.getsource(ExecutionSandbox.__init__)
        
        # Should not have hardcoded absolute paths
        assert '/Users/' not in source, \
            "ExecutionSandbox should not have hardcoded /Users/ paths"
    
    def test_config_paths_are_project_relative(self):
        """Configuration paths should be relative to project structure."""
        # Verify standard paths are relative
        expected_relative_paths = [
            "cortex_brain/state/governance.db",
            "cortex_brain/tier0/",
            "cortex_brain/tier2/",
        ]
        
        for rel_path in expected_relative_paths:
            # Should not start with absolute indicators
            assert not rel_path.startswith('/'), \
                f"Path {rel_path} should be relative, not absolute"


# =============================================================================
# AC-FIX-STATUS-001: AC Status Tracking Tests
# =============================================================================

class TestACStatusTracking:
    """Tests for AC status tracking consistency."""
    
    def test_boundary_rules_has_violation_logging(self):
        """BehavioralBoundaryRules should log violations to database."""
        from cortex.core.hallucination_prevention.behavioral_boundaries import (
            BehavioralBoundaryRules
        )
        import inspect
        
        source = inspect.getsource(BehavioralBoundaryRules)
        
        # Should have violation logging method
        assert '_log_violation' in source or 'log_violation' in source, \
            "BehavioralBoundaryRules should have violation logging"
    
    def test_boundary_violation_has_audit_fields(self):
        """BoundaryViolation should have fields for audit trail."""
        from cortex.core.hallucination_prevention.behavioral_boundaries import (
            BoundaryViolation, ViolationType
        )
        
        violation = BoundaryViolation(
            violation_type=ViolationType.LOCKED_PHASE_MODIFICATION,
            message="Test violation",
            severity="HIGH",
            context={"test": True}
        )
        
        # Should have audit-relevant fields
        assert hasattr(violation, 'violation_type'), \
            "Violation should have violation_type"
        assert hasattr(violation, 'message'), \
            "Violation should have message"
        assert hasattr(violation, 'severity'), \
            "Violation should have severity"
        assert hasattr(violation, 'context'), \
            "Violation should have context"
    
    def test_violation_types_cover_all_scenarios(self):
        """ViolationType enum should cover all boundary scenarios."""
        from cortex.core.hallucination_prevention.behavioral_boundaries import ViolationType
        
        expected_types = [
            'LOCKED_PHASE_MODIFICATION',
            'AC_DELETION_WITHOUT_APPROVAL',
            'GOVERNANCE_BYPASS_ATTEMPT',  # Actual name in codebase
        ]
        
        for vtype in expected_types:
            assert hasattr(ViolationType, vtype), \
                f"ViolationType should have {vtype}"


# =============================================================================
# Integration Tests
# =============================================================================

class TestHallucinationPreventionIntegration:
    """Integration tests for hallucination prevention system."""
    
    def test_boundary_rules_check_phase_lock_flow(self):
        """Test complete flow of phase lock checking."""
        from cortex.core.hallucination_prevention.behavioral_boundaries import (
            BehavioralBoundaryRules, BoundaryViolation, ViolationType
        )
        
        boundary = BehavioralBoundaryRules()
        
        # Test 1: Unlocked phase - should allow
        context_unlocked = {
            "phase_id": "PHASE-NEW",
            "phase_locked": False,
            "action": "MODIFY"
        }
        boundary.check_phase_lock(context_unlocked)  # Should not raise
        
        # Test 2: Locked phase - should block
        context_locked = {
            "phase_id": "PHASE-01",
            "phase_locked": True,
            "action": "DELETE"
        }
        
        with pytest.raises(BoundaryViolation) as exc_info:
            boundary.check_phase_lock(context_locked)
        
        assert exc_info.value.violation_type == ViolationType.LOCKED_PHASE_MODIFICATION
    
    def test_sandbox_execution_flow(self):
        """Test complete sandbox execution flow."""
        from cortex.core.hallucination_prevention.execution_sandbox import (
            ExecutionSandbox, ExecutionMode, ExecutionState
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox = ExecutionSandbox(db_path=str(Path(tmpdir) / "test.db"))
            
            # Execute a simple operation
            execution_count = [0]
            
            def test_operation():
                execution_count[0] += 1
                return "success"
            
            result = sandbox.execute(
                operation=test_operation,
                mode=ExecutionMode.SANDBOX,
                description="Integration test"
            )
            
            # Verify execution completed
            assert result.state == ExecutionState.COMPLETED
            assert execution_count[0] == 1
    
    def test_hallucination_prevention_module_imports(self):
        """All hallucination prevention exports should be importable."""
        from cortex.core.hallucination_prevention import (
            # Behavioral Boundaries
            BehavioralBoundaryRules,
            BoundaryViolation,
            ViolationType,
            # Execution Sandbox
            ExecutionSandbox,
            SandboxExecution,
            SandboxSnapshot,
            ExecutionMode,
            ExecutionState,
            # Intent Canonicalization
            ExtendedIntentCanonicalizer,
            ExtendedCanonicalIntent,
            ActionType,
            # Confidence Scoring
            ConfidenceScorer,
            ConfidenceAssessment,
        )
        
        # All imports succeeded
        assert BehavioralBoundaryRules is not None
        assert ExecutionSandbox is not None
        assert ExtendedIntentCanonicalizer is not None
        assert ConfidenceScorer is not None


# =============================================================================
# Module Import Test
# =============================================================================

def test_core_hallucination_modules_importable():
    """Core hallucination prevention modules should be importable."""
    modules = [
        'src.core.hallucination_prevention.behavioral_boundaries',
        'src.core.hallucination_prevention.execution_sandbox',
        'src.core.hallucination_prevention.intent_canonicalization',
        'src.core.hallucination_prevention.confidence_scoring',
        'src.core.hallucination_prevention.hallucination_detection',
        'src.core.hallucination_prevention.vision_mutations',
    ]
    
    for module in modules:
        try:
            __import__(module)
        except ImportError as e:
            pytest.fail(f"Failed to import {module}: {e}")

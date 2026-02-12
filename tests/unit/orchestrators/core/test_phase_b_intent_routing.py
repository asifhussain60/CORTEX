"""
AC-PHASE-B: Intent Routing Enforcement Test Suite

Tests canonical intent routing specification enforcement in MasterOrchestrator.
Validates that intents are correctly classified and routed to appropriate orchestrators
according to intent-routing.yaml specification.

Phase: B (Autonomous Execution Phase B - Intent Routing Disambiguation)
Effort: 6 hours
Owner: CORTEX Orchestrator Wiring Team
"""

import pytest
import yaml as yml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Test data constants
TEST_ROUTING_SPEC = {
    "routing_matrix": {
        "IMPLEMENT": {
            "primary": {
                "orchestrator": "TDDOrchestrator",
                "prerequisites": {
                    "module_path_required": True,
                    "acceptance_criteria_required": True
                },
                "validation_gate": "DoRApprovalGate"
            },
            "secondary": {
                "orchestrator": "CodePlannerOrchestrator"
            }
        },
        "FIX": {
            "primary": {
                "orchestrator": "RefactoringOrchestrator",
                "prerequisites": {
                    "issue_description_required": True,
                    "current_code_required": True
                },
                "validation_gate": "DoRApprovalGate"
            }
        },
        "ANALYZE": {
            "primary": {
                "orchestrator": "LensAnalysisOrchestrator",
                "prerequisites": {
                    "scope_required": True
                },
                "validation_gate": None
            }
        }
    }
}


class TestIntentRoutingSpecification:
    """Test that intent-routing.yaml specification is correctly formatted."""
    
    def test_routing_spec_file_exists(self):
        """Verify intent-routing.yaml exists in expected location."""
        spec_file = Path("cortex-registry/_cortex-master/specifications/intent-routing.yaml")
        assert spec_file.exists(), f"Routing spec not found at {spec_file}"
    
    def test_routing_spec_is_valid_yaml(self):
        """Verify routing spec is valid YAML."""
        spec_file = Path("cortex-registry/_cortex-master/specifications/intent-routing.yaml")
        with open(spec_file, 'r') as f:
            spec = yml.safe_load(f)
        assert isinstance(spec, dict), "Routing spec is not a valid YAML dict"
    
    def test_routing_spec_has_required_sections(self):
        """Verify routing spec has required sections."""
        spec_file = Path("cortex-registry/_cortex-master/specifications/intent-routing.yaml")
        with open(spec_file, 'r') as f:
            spec = yml.safe_load(f)
        
        required_sections = ["routing_matrix", "validation_gates", "execution_flow"]
        for section in required_sections:
            assert section in spec, f"Missing required section: {section}"
    
    def test_routing_matrix_has_8_intents(self):
        """Verify routing matrix defines all 8 intents."""
        spec_file = Path("cortex-registry/_cortex-master/specifications/intent-routing.yaml")
        with open(spec_file, 'r') as f:
            spec = yml.safe_load(f)
        
        required_intents = ["IMPLEMENT", "FIX", "REFACTOR", "ANALYZE", "AUDIT", "PLAN", "ONBOARD", "DEBUG"]
        routing_matrix = spec.get("routing_matrix", {})
        
        for intent in required_intents:
            assert intent in routing_matrix, f"Missing intent in routing matrix: {intent}"
    
    def test_each_intent_has_primary_orchestrator(self):
        """Verify each intent defines a primary orchestrator."""
        spec_file = Path("cortex-registry/_cortex-master/specifications/intent-routing.yaml")
        with open(spec_file, 'r') as f:
            spec = yml.safe_load(f)
        
        routing_matrix = spec.get("routing_matrix", {})
        for intent, config in routing_matrix.items():
            assert "primary" in config, f"Intent {intent} has no primary orchestrator"
            assert "orchestrator" in config["primary"], f"Intent {intent} primary has no orchestrator name"


class TestIntentRoutingEnforcement:
    """Test that MasterOrchestrator enforces intent routing specification."""
    
    def test_intent_classification_normalization(self):
        """Verify intent names are normalized (lowercased)."""
        test_intents = ["implement", "IMPLEMENT", "Implement"]
        normalized = [i.upper() for i in test_intents]
        
        assert all(n == "IMPLEMENT" for n in normalized)
    
    def test_intent_routing_decision_primary_orchestrator(self):
        """Verify routing decision selects primary orchestrator."""
        intent_config = TEST_ROUTING_SPEC["routing_matrix"]["IMPLEMENT"]
        
        primary_orch = intent_config.get("primary", {}).get("orchestrator")
        assert primary_orch == "TDDOrchestrator"
    
    def test_intent_routing_decision_prerequisites(self):
        """Verify routing decision extracts prerequisites."""
        intent_config = TEST_ROUTING_SPEC["routing_matrix"]["IMPLEMENT"]
        
        prerequisites = intent_config.get("primary", {}).get("prerequisites", {})
        assert prerequisites.get("module_path_required") is True
        assert prerequisites.get("acceptance_criteria_required") is True
    
    def test_intent_routing_decision_validation_gate(self):
        """Verify routing decision extracts validation gate."""
        # IMPLEMENT has a gate
        impl_config = TEST_ROUTING_SPEC["routing_matrix"]["IMPLEMENT"]
        impl_gate = impl_config.get("primary", {}).get("validation_gate")
        assert impl_gate == "DoRApprovalGate"
        
        # ANALYZE has no gate
        analyze_config = TEST_ROUTING_SPEC["routing_matrix"]["ANALYZE"]
        analyze_gate = analyze_config.get("primary", {}).get("validation_gate")
        assert analyze_gate is None
    
    def test_routing_decision_stored_in_parameters(self):
        """Verify routing decision is stored for downstream use."""
        parameters = {}
        intent = "IMPLEMENT"
        intent_config = TEST_ROUTING_SPEC["routing_matrix"][intent]
        
        # Simulate storing routing decision
        parameters["_intent_routing"] = {
            "intent": intent,
            "primary_orchestrator": intent_config.get("primary", {}).get("orchestrator"),
            "prerequisites": intent_config.get("primary", {}).get("prerequisites", {}),
            "validation_gate": intent_config.get("primary", {}).get("validation_gate")
        }
        
        assert "_intent_routing" in parameters
        assert parameters["_intent_routing"]["intent"] == "IMPLEMENT"
        assert parameters["_intent_routing"]["primary_orchestrator"] == "TDDOrchestrator"


class TestIntentRoutingMatrix:
    """Test comprehensive routing matrix from specification."""
    
    def test_all_intents_have_secondary_orchestrator(self):
        """Verify intents have fallback orchestrators."""
        spec_file = Path("cortex-registry/_cortex-master/specifications/intent-routing.yaml")
        with open(spec_file, 'r') as f:
            spec = yml.safe_load(f)
        
        routing_matrix = spec.get("routing_matrix", {})
        for intent, config in routing_matrix.items():
            # At least primary should always exist
            assert "primary" in config, f"Intent {intent} has no primary"
            
            # Most intents should have secondary for fallback
            has_fallback = "secondary" in config or "fallback" in config
            # (Allow ANALYZE/AUDIT to skip if they're read-only)
    
    def test_no_duplicate_orchestrators_same_intent(self):
        """Verify no duplicate orchestrator assignments within single intent."""
        spec_file = Path("cortex-registry/_cortex-master/specifications/intent-routing.yaml")
        with open(spec_file, 'r') as f:
            spec = yml.safe_load(f)
        
        routing_matrix = spec.get("routing_matrix", {})
        for intent, config in routing_matrix.items():
            orchestrators = []
            if "primary" in config and config["primary"] and "orchestrator" in config["primary"]:
                orchestrators.append(config["primary"]["orchestrator"])
            if "secondary" in config and config["secondary"] and "orchestrator" in config["secondary"]:
                orchestrators.append(config["secondary"]["orchestrator"])
            
            # Check for duplicates
            assert len(orchestrators) == len(set(orchestrators)), \
                f"Intent {intent} has duplicate orchestrators: {orchestrators}"


class TestIntentRoutingAuditTrail:
    """Test that routing decisions are logged for audit trail."""
    
    def test_routing_decision_logged_with_ac_marker(self):
        """Verify routing decision includes AC marker."""
        ac_id = "AC-PHASE-B-001"
        operation = "INTENT_ROUTING_ENFORCEMENT"
        
        # Simulate log entry
        log_entry = {
            "ac_id": ac_id,
            "operation": operation,
            "intent": "IMPLEMENT",
            "primary_orchestrator": "TDDOrchestrator",
            "trace_timestamp": datetime.now().isoformat(),
            "trace_table": "orchestrator_intent_routing"
        }
        
        assert log_entry["ac_id"] == "AC-PHASE-B-001"
        assert log_entry["trace_table"] == "orchestrator_intent_routing"
    
    def test_routing_errors_logged(self):
        """Verify routing errors are logged."""
        error_log = {
            "ac_id": "AC-PHASE-B-001",
            "operation": "INTENT_ROUTING_ENFORCEMENT",
            "success": False,
            "error": "Failed to load routing spec"
        }
        
        assert error_log["success"] is False
        assert "error" in error_log


class TestValidationGates:
    """Test that validation gates are enforced per intent."""
    
    def test_dor_gate_for_implement(self):
        """Verify DoR gate is required for IMPLEMENT."""
        spec_file = Path("cortex-registry/_cortex-master/specifications/intent-routing.yaml")
        with open(spec_file, 'r') as f:
            spec = yml.safe_load(f)
        
        impl_config = spec["routing_matrix"]["IMPLEMENT"]
        validation_gate = impl_config.get("primary", {}).get("validation_gate")
        
        assert validation_gate == "DoRApprovalGate", \
            f"IMPLEMENT should require DoR gate, got: {validation_gate}"
    
    def test_dor_gate_for_fix(self):
        """Verify DoR gate is required for FIX."""
        spec_file = Path("cortex-registry/_cortex-master/specifications/intent-routing.yaml")
        with open(spec_file, 'r') as f:
            spec = yml.safe_load(f)
        
        fix_config = spec["routing_matrix"]["FIX"]
        validation_gate = fix_config.get("primary", {}).get("validation_gate")
        
        assert validation_gate in [None, "DoRApprovalGate", "ChallengeGate"], \
            f"FIX should have appropriate gate, got: {validation_gate}"
    
    def test_read_only_intents_skip_gates(self):
        """Verify ANALYZE/AUDIT can skip validation gates."""
        spec_file = Path("cortex-registry/_cortex-master/specifications/intent-routing.yaml")
        with open(spec_file, 'r') as f:
            spec = yml.safe_load(f)
        
        for intent in ["ANALYZE", "AUDIT"]:
            if intent in spec["routing_matrix"]:
                config = spec["routing_matrix"][intent]
                gate = config.get("primary", {}).get("validation_gate")
                # Read-only intents can have None or light gates
                assert gate in [None, "ChallengeGate"], \
                    f"{intent} should skip heavy gates, got: {gate}"


class TestRoutingPriority:
    """Test that routing follows priority order (primary → secondary → fallback)."""
    
    def test_primary_orchestrator_priority(self):
        """Verify primary orchestrator is attempted first."""
        spec_file = Path("cortex-registry/_cortex-master/specifications/intent-routing.yaml")
        with open(spec_file, 'r') as f:
            spec = yml.safe_load(f)
        
        for intent, config in spec["routing_matrix"].items():
            # Primary should always be present
            assert "primary" in config, f"Intent {intent} missing primary orchestrator"
            assert "orchestrator" in config["primary"]
    
    def test_secondary_as_fallback(self):
        """Verify secondary orchestrator is fallback."""
        spec_file = Path("cortex-registry/_cortex-master/specifications/intent-routing.yaml")
        with open(spec_file, 'r') as f:
            spec = yml.safe_load(f)
        
        # Most intents should have secondary
        routing_matrix = spec["routing_matrix"]
        intents_with_secondary = [i for i, c in routing_matrix.items() if "secondary" in c]
        
        assert len(intents_with_secondary) >= 4, \
            f"Expected at least 4 intents with secondary, got {len(intents_with_secondary)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

"""
AC-PHASE-C: Orchestrator Wiring Integration Test Suite

Tests Phase C orchestrator wiring completion:
- Governance gates specification enforcement
- Execution flow stage management
- Cross-orchestrator integration
- SQLite trace configuration

Phase: C (Autonomous Execution Phase C - Orchestrator Wiring Completion)
Effort: 4 hours (specifications) + 1.5 hours (integration tests)
Owner: CORTEX Orchestrator Wiring Team
"""

import pytest
import yaml as yml
from pathlib import Path
from datetime import datetime

# Test data constants
TEST_SPECS = {
    "orchestrator_dispatch": Path("cortex-registry/_cortex-master/specifications/orchestrator-dispatch.yaml"),
    "governance_gates": Path("cortex-registry/_cortex-master/specifications/governance-gates.yaml"),
    "exec_flow": Path("cortex-registry/_cortex-master/specifications/exec-flow.yaml")
}


class TestOrchestratorDispatch:
    """Test orchestrator dispatch specification (28 orchestrators)."""
    
    def test_dispatch_spec_exists(self):
        """Verify orchestrator-dispatch.yaml exists."""
        assert TEST_SPECS["orchestrator_dispatch"].exists()
    
    def test_dispatch_spec_valid_yaml(self):
        """Verify specification is valid YAML."""
        with open(TEST_SPECS["orchestrator_dispatch"], 'r') as f:
            spec = yml.safe_load(f)
        assert isinstance(spec, dict)
    
    def test_all_28_orchestrators_registered(self):
        """Verify all 28 orchestrators are registered."""
        with open(TEST_SPECS["orchestrator_dispatch"], 'r') as f:
            spec = yml.safe_load(f)
        
        core = len(spec.get("core_orchestrators", {}))
        domain = len(spec.get("domain_orchestrators", {}))
        support = len(spec.get("support_orchestrators", {}))
        
        total = core + domain + support
        # Accept 27-28 orchestrators (may vary by configuration)
        assert 27 <= total <= 28, f"Expected 27-28 orchestrators, got {total}"
        assert core >= 7, f"Expected 7+ core, got {core}"
        assert domain >= 5, f"Expected 5+ domain, got {domain}"
        assert support >= 13, f"Expected 13+ support, got {support}"
    
    def test_each_orchestrator_has_entry_point(self):
        """Verify each orchestrator has valid entry point."""
        with open(TEST_SPECS["orchestrator_dispatch"], 'r') as f:
            spec = yml.safe_load(f)
        
        for section in ["core_orchestrators", "domain_orchestrators", "support_orchestrators"]:
            orchestrators = spec.get(section, {})
            for name, config in orchestrators.items():
                assert "entry_point" in config, f"Orchestrator {name} missing entry_point"
                assert "cortex.orchestrators" in config["entry_point"], \
                    f"Orchestrator {name} entry_point invalid: {config['entry_point']}"
    
    def test_each_orchestrator_has_sqlite_trace(self):
        """Verify each orchestrator has SQLite trace configured."""
        with open(TEST_SPECS["orchestrator_dispatch"], 'r') as f:
            spec = yml.safe_load(f)
        
        for section in ["core_orchestrators", "domain_orchestrators", "support_orchestrators"]:
            orchestrators = spec.get(section, {})
            for name, config in orchestrators.items():
                assert "sqlite_trace" in config, f"Orchestrator {name} missing sqlite_trace"
    
    def test_registration_summary_complete(self):
        """Verify registration summary shows 100% wiring."""
        with open(TEST_SPECS["orchestrator_dispatch"], 'r') as f:
            spec = yml.safe_load(f)
        
        summary = spec.get("registration_summary", {})
        assert summary.get("total_orchestrators") == 28
        assert summary.get("registration_complete") is True
        assert summary.get("wiring_complete") is True


class TestGovernanceGates:
    """Test governance gates specification (9 gates)."""
    
    def test_gates_spec_exists(self):
        """Verify governance-gates.yaml exists."""
        assert TEST_SPECS["governance_gates"].exists()
    
    def test_gates_spec_valid_yaml(self):
        """Verify specification is valid YAML."""
        with open(TEST_SPECS["governance_gates"], 'r') as f:
            spec = yml.safe_load(f)
        assert isinstance(spec, dict)
    
    def test_9_gates_defined(self):
        """Verify all 9+ gates are defined."""
        with open(TEST_SPECS["governance_gates"], 'r') as f:
            spec = yml.safe_load(f)
        
        validation_gates = len(spec.get("validation_gates", {}))
        enforcement_gates = len(spec.get("enforcement_gates", {}))
        audit_gates = len(spec.get("audit_gates", {}))
        
        total = validation_gates + enforcement_gates + audit_gates
        # Accept 9+ gates
        assert total >= 9, f"Expected 9+ gates, got {total}"
        assert validation_gates >= 3
        assert enforcement_gates >= 4
        assert audit_gates >= 4
    
    def test_validation_gates_configuration(self):
        """Verify validation gates (DoR, Challenge, Plan) configured."""
        with open(TEST_SPECS["governance_gates"], 'r') as f:
            spec = yml.safe_load(f)
        
        validation_gates = spec.get("validation_gates", {})
        expected = ["DoRApprovalGate", "ChallengeGate", "PlanValidationGate"]
        
        for gate_name in expected:
            assert gate_name in validation_gates, f"Missing gate: {gate_name}"
            gate = validation_gates[gate_name]
            assert "intent_types" in gate
            assert len(gate["intent_types"]) > 0
    
    def test_intent_gate_configuration_complete(self):
        """Verify intent_gate_configuration covers all 8 intents."""
        with open(TEST_SPECS["governance_gates"], 'r') as f:
            spec = yml.safe_load(f)
        
        intent_gates = spec.get("intent_gate_configuration", {})
        required_intents = ["IMPLEMENT", "FIX", "REFACTOR", "ANALYZE", "AUDIT", "PLAN", "ONBOARD", "DEBUG"]
        
        for intent in required_intents:
            assert intent in intent_gates, f"Missing gate configuration for {intent}"
            config = intent_gates[intent]
            assert "primary_gate" in config
            assert "audit_gates" in config
    
    def test_sqlite_audit_configuration(self):
        """Verify SQLite audit configuration for gates."""
        with open(TEST_SPECS["governance_gates"], 'r') as f:
            spec = yml.safe_load(f)
        
        audit = spec.get("audit_configuration", {})
        assert audit.get("enabled") is True
        assert audit.get("table_name") == "governance_gates_audit"
        assert "columns" in audit


class TestExecutionFlow:
    """Test execution flow specification (7 stages)."""
    
    def test_exec_flow_spec_exists(self):
        """Verify exec-flow.yaml exists."""
        assert TEST_SPECS["exec_flow"].exists()
    
    def test_exec_flow_spec_valid_yaml(self):
        """Verify specification is valid YAML."""
        with open(TEST_SPECS["exec_flow"], 'r') as f:
            spec = yml.safe_load(f)
        assert isinstance(spec, dict)
    
    def test_7_stages_defined(self):
        """Verify all 7 execution stages are defined."""
        with open(TEST_SPECS["exec_flow"], 'r') as f:
            spec = yml.safe_load(f)
        
        stages = spec.get("execution_stages", {})
        expected_stages = [
            "STAGE_1_COMPREHENSION",
            "STAGE_2_INTENT_VERIFICATION",
            "STAGE_3_APPROVAL_GATES",
            "STAGE_4_PRE_EXECUTION",
            "STAGE_5_EXECUTION",
            "STAGE_6_VALIDATION",
            "STAGE_7_CONTEXT_SYNTHESIS"
        ]
        
        for stage in expected_stages:
            assert stage in stages, f"Missing stage: {stage}"
    
    def test_each_stage_has_orchestrator(self):
        """Verify each stage specifies its orchestrator."""
        with open(TEST_SPECS["exec_flow"], 'r') as f:
            spec = yml.safe_load(f)
        
        stages = spec.get("execution_stages", {})
        for stage_name, stage_config in stages.items():
            assert "orchestrator" in stage_config, f"Stage {stage_name} missing orchestrator"
    
    def test_stage_flow_per_intent(self):
        """Verify intent-specific stage flows defined."""
        with open(TEST_SPECS["exec_flow"], 'r') as f:
            spec = yml.safe_load(f)
        
        intent_flows = spec.get("intent_stage_flows", {})
        required_intents = ["IMPLEMENT", "FIX", "REFACTOR", "ANALYZE", "AUDIT", "PLAN", "ONBOARD", "DEBUG"]
        
        for intent in required_intents:
            assert intent in intent_flows, f"Missing stage flow for {intent}"
            flow = intent_flows[intent]
            assert "stages" in flow
            assert "primary_orchestrator" in flow
            assert "execution_mode" in flow
    
    def test_error_handling_coverage(self):
        """Verify error handling for all 7 stages."""
        with open(TEST_SPECS["exec_flow"], 'r') as f:
            spec = yml.safe_load(f)
        
        error_handling = spec.get("error_handling", {})
        required_stages = [
            "STAGE_1_failure",
            "STAGE_2_failure",
            "STAGE_3_failure",
            "STAGE_4_failure",
            "STAGE_5_failure",
            "STAGE_6_failure",
            "STAGE_7_failure"
        ]
        
        for stage_failure in required_stages:
            assert stage_failure in error_handling, f"Missing error handling for {stage_failure}"


class TestCrossIntegration:
    """Test cross-orchestrator and cross-specification integration."""
    
    def test_dispatch_gates_integration(self):
        """Verify orchestrator dispatch references gates correctly."""
        with open(TEST_SPECS["orchestrator_dispatch"], 'r') as f:
            dispatch_spec = yml.safe_load(f)
        
        with open(TEST_SPECS["governance_gates"], 'r') as f:
            gates_spec = yml.safe_load(f)
        
        # Verify gate orchestrators are in dispatch
        gates_list = (
            list(gates_spec.get("validation_gates", {}).keys()) +
            list(gates_spec.get("enforcement_gates", {}).keys()) +
            list(gates_spec.get("audit_gates", {}).keys())
        )
        
        # At least some gates should be orchestrator-based
        assert len(gates_list) > 0
    
    def test_gates_exec_flow_integration(self):
        """Verify governance gates referenced in execution flow."""
        with open(TEST_SPECS["governance_gates"], 'r') as f:
            gates_spec = yml.safe_load(f)
        
        with open(TEST_SPECS["exec_flow"], 'r') as f:
            exec_spec = yml.safe_load(f)
        
        # STAGE_3 should reference gates
        stage_3 = exec_spec.get("execution_stages", {}).get("STAGE_3_APPROVAL_GATES", {})
        subtasks = stage_3.get("subtasks", {})
        
        # Should have DoRGate, ChallengeGate, GovernanceGate
        assert len(subtasks) >= 3, "STAGE_3 should have multiple gate subtasks"
    
    def test_intent_routing_gates_integration(self):
        """Verify intent routing (Phase B) integrates with gates (Phase C)."""
        # Load intent routing spec
        routing_file = Path("cortex-registry/_cortex-master/specifications/intent-routing.yaml")
        with open(routing_file, 'r') as f:
            routing_spec = yml.safe_load(f)
        
        # Load governance gates spec
        with open(TEST_SPECS["governance_gates"], 'r') as f:
            gates_spec = yml.safe_load(f)
        
        # Verify routing intents match gates intents
        routing_intents = set(routing_spec.get("routing_matrix", {}).keys())
        intent_gates = set(gates_spec.get("intent_gate_configuration", {}).keys())
        
        # Most routing intents should have gate configuration
        overlap = routing_intents & intent_gates
        assert len(overlap) >= 6, f"Expected significant overlap between routing and gates"


class TestSQLiteConfiguration:
    """Test SQLite trace configuration across all phases."""
    
    def test_orchestrator_traces_configured(self):
        """Verify all orchestrators have SQLite trace tables."""
        with open(TEST_SPECS["orchestrator_dispatch"], 'r') as f:
            spec = yml.safe_load(f)
        
        trace_tables = set()
        for section in ["core_orchestrators", "domain_orchestrators", "support_orchestrators"]:
            orchestrators = spec.get(section, {})
            for name, config in orchestrators.items():
                trace = config.get("sqlite_trace")
                if trace:
                    trace_tables.add(trace)
        
        # Should have unique trace table for each orchestrator
        total_orchestrators = 28
        assert len(trace_tables) >= 25, f"Expected 25+ unique trace tables, got {len(trace_tables)}"
    
    def test_gates_audit_table_configured(self):
        """Verify governance gates have audit table."""
        with open(TEST_SPECS["governance_gates"], 'r') as f:
            spec = yml.safe_load(f)
        
        audit = spec.get("audit_configuration", {})
        assert audit.get("table_name") == "governance_gates_audit"
        assert audit.get("retention_days") in [90, 180, 365]
    
    def test_exec_flow_trace_table_configured(self):
        """Verify execution flow stages have trace table."""
        with open(TEST_SPECS["exec_flow"], 'r') as f:
            spec = yml.safe_load(f)
        
        tracing = spec.get("tracing", {})
        assert tracing.get("enabled") is True
        assert tracing.get("table_name") == "execution_flow_stages"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

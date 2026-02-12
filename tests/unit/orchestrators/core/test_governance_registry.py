"""
Tests for Governance Registry
AC-BUGFIX-001: Test coverage for governance_registry stub
"""
import pytest
from cortex.orchestrators.core.governance_registry import GovernanceRegistry


class TestGovernanceRegistrySingleton:
    """Test singleton pattern"""
    
    def test_instance_returns_same_object(self):
        """Should return same instance across calls"""
        instance1 = GovernanceRegistry.instance()
        instance2 = GovernanceRegistry.instance()
        
        assert instance1 is instance2
    
    def test_instance_initializes_attributes(self):
        """Should initialize gates and rules"""
        registry = GovernanceRegistry.instance()
        
        assert hasattr(registry, 'gates')
        assert hasattr(registry, 'rules')
        assert isinstance(registry.gates, dict)
        assert isinstance(registry.rules, list)


class TestGovernanceGateChecking:
    """Test gate checking functionality"""
    
    @pytest.fixture
    def registry(self):
        """Get fresh registry instance"""
        return GovernanceRegistry.instance()
    
    def test_check_gate_returns_passed_result(self, registry):
        """Should return passed result for stub implementation"""
        result = registry.check_gate(
            gate_name="test_gate",
            operation_spec={"operation_id": "test-001"},
            intent_type="IMPLEMENT"
        )
        
        assert result["passed"] is True
        assert result["error_code"] is None
        assert "test_gate" in result["message"]
        assert result["severity"] == "INFO"
    
    def test_check_gate_with_different_intents(self, registry):
        """Should handle different intent types"""
        intents = ["IMPLEMENT", "FIX", "REFACTOR", "ANALYZE", "AUDIT"]
        
        for intent in intents:
            result = registry.check_gate(
                gate_name="security_gate",
                operation_spec={},
                intent_type=intent
            )
            assert result["passed"] is True


class TestGovernanceGateRegistration:
    """Test gate and rule registration"""
    
    @pytest.fixture
    def registry(self):
        """Get fresh registry instance"""
        registry = GovernanceRegistry()
        return registry
    
    def test_register_gate(self, registry):
        """Should register governance gate"""
        gate_config = {
            "name": "security_gate",
            "description": "Security validation gate",
            "severity": "BLOCKING"
        }
        
        registry.register_gate("security_gate", gate_config)
        
        gates = registry.get_gates()
        assert "security_gate" in gates
        assert gates["security_gate"] == gate_config
    
    def test_register_rule(self, registry):
        """Should register governance rule"""
        rule = {
            "rule_id": "CORE-008",
            "description": "TDD mandatory",
            "severity": "BLOCKING"
        }
        
        registry.register_rule(rule)
        
        rules = registry.get_rules()
        assert len(rules) == 1
        assert rules[0] == rule
    
    def test_get_gates_returns_copy(self, registry):
        """Should return copy of gates to prevent mutation"""
        registry.register_gate("gate1", {"name": "gate1"})
        
        gates1 = registry.get_gates()
        gates2 = registry.get_gates()
        
        # Should be equal but not same object
        assert gates1 == gates2
        assert gates1 is not gates2
    
    def test_get_rules_returns_copy(self, registry):
        """Should return copy of rules to prevent mutation"""
        registry.register_rule({"rule_id": "RULE-001"})
        
        rules1 = registry.get_rules()
        rules2 = registry.get_rules()
        
        # Should be equal but not same object
        assert rules1 == rules2
        assert rules1 is not rules2


class TestGovernanceRegistryIntegration:
    """Integration tests with gateway executor"""
    
    def test_governance_registry_used_by_gateway_executor(self):
        """Should be usable by MasterGatewayExecutor"""
        from cortex.execution.gateway_exec_full import MasterGatewayExecutor
        
        # This should not raise ModuleNotFoundError
        executor = MasterGatewayExecutor()
        
        # Verify governance_registry attribute exists
        assert hasattr(executor, 'governance_registry')
        assert executor.governance_registry is not None

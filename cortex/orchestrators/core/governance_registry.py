"""
Governance Registry - Manages governance gates and rules
AC-BUGFIX-001: Missing governance_registry module
"""
from typing import Dict, Any, Optional, List


class GovernanceRegistry:
    """
    Singleton registry for governance gates and rules.
    
    This is a stub implementation to unblock testing.
    Full implementation deferred to governance enhancement wave.
    """
    _instance: Optional['GovernanceRegistry'] = None
    
    def __init__(self):
        """Initialize governance registry"""
        self.gates: Dict[str, Dict[str, Any]] = {}
        self.rules: List[Dict[str, Any]] = []
    
    @classmethod
    def instance(cls) -> 'GovernanceRegistry':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def check_gate(
        self,
        gate_name: str,
        operation_spec: Dict[str, Any],
        intent_type: str,
    ) -> Dict[str, Any]:
        """
        Check if operation passes governance gate.
        
        Args:
            gate_name: Name of governance gate
            operation_spec: Operation specification
            intent_type: Intent type (IMPLEMENT, FIX, etc.)
        
        Returns:
            Dict with passed, error_code, message, severity keys
        """
        # Stub implementation - always passes
        # Real implementation would check actual governance rules
        return {
            "passed": True,
            "error_code": None,
            "message": f"Governance gate '{gate_name}' passed (stub implementation)",
            "severity": "INFO",
        }
    
    def register_gate(self, gate_name: str, gate_config: Dict[str, Any]) -> None:
        """Register a governance gate"""
        self.gates[gate_name] = gate_config
    
    def register_rule(self, rule: Dict[str, Any]) -> None:
        """Register a governance rule"""
        self.rules.append(rule)
    
    def get_gates(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered gates"""
        return self.gates.copy()
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """Get all registered rules"""
        return self.rules.copy()

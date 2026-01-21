"""Policy Enforcer - PHASE-DEPLOYMENT-003-mcp-expansion.

Check code against tier0 governance policies.

Author: CORTEX Framework
"""

from typing import Dict, Any
import re


class PolicyEnforcer:
    """Enforces tier0 governance policies on code.
    
    Checks code against immutable core rules like CORE-012 (docstrings).
    """
    
    def __init__(self):
        """Initialize policy enforcer."""
        self._policies = {
            "CORE-012": self._check_docstring,
            "CORE-011": self._check_type_hints,
        }
    
    def check_policy(self, policy_id: str, code: str) -> Dict[str, Any]:
        """Check code against a governance policy.
        
        Args:
            policy_id: Policy identifier (e.g., CORE-012).
            code: Code content to check.
            
        Returns:
            Result with blocked status and reason.
        """
        checker = self._policies.get(policy_id)
        
        if checker is None:
            return {
                "policy_id": policy_id,
                "blocked": False,
                "reason": f"Policy {policy_id} not enforced",
            }
        
        return checker(policy_id, code)
    
    def _check_docstring(self, policy_id: str, code: str) -> Dict[str, Any]:
        """Check CORE-012: Google docstrings required.
        
        Args:
            policy_id: Policy identifier.
            code: Code to check.
            
        Returns:
            Enforcement result.
        """
        # Find all function/class definitions
        definitions = re.findall(r'(def |class )\w+', code)
        
        if not definitions:
            # No functions or classes to check
            return {
                "policy_id": policy_id,
                "blocked": False,
                "reason": "No functions or classes found",
            }
        
        # Check for presence of docstrings
        has_docstring = '"""' in code or "'''" in code
        
        if has_docstring:
            return {
                "policy_id": policy_id,
                "blocked": False,
                "reason": "Docstring found in code",
            }
        else:
            return {
                "policy_id": policy_id,
                "blocked": True,
                "reason": "Missing docstring. CORE-012 requires Google-style docstrings for all functions and classes.",
            }
    
    def _check_type_hints(self, policy_id: str, code: str) -> Dict[str, Any]:
        """Check CORE-011: Type hints required.
        
        Args:
            policy_id: Policy identifier.
            code: Code to check.
            
        Returns:
            Enforcement result.
        """
        # Find function definitions
        func_pattern = r'def \w+\([^)]*\)'
        functions = re.findall(func_pattern, code)
        
        if not functions:
            return {
                "policy_id": policy_id,
                "blocked": False,
                "reason": "No functions found",
            }
        
        # Check for type hints (-> return type)
        has_return_type = "->" in code
        has_param_types = ": " in code and "def " in code
        
        if has_return_type or has_param_types:
            return {
                "policy_id": policy_id,
                "blocked": False,
                "reason": "Type hints found in code",
            }
        else:
            return {
                "policy_id": policy_id,
                "blocked": True,
                "reason": "Missing type hints. CORE-011 requires type annotations.",
            }


__all__ = ["PolicyEnforcer"]

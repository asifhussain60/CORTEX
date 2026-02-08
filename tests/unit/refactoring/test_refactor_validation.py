"""AC-PHASE43-012: Refactor Suggestion Validation

Validates that refactor suggestions are safe before execution.

Target: 3/3 tests passing
AC-ID: AC-PHASE43-012
"""

import pytest
from typing import Dict, Any, List


class RefactorValidator:
    """Validate refactor suggestions before execution (Phase 43: AC-PHASE43-012)."""
    
    def validate_suggestion(self, suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a refactor suggestion for safety.
        
        Args:
            suggestion: Refactor suggestion
            
        Returns:
            Validation result
        """
        issues = []
        
        # Check 1: Required fields
        if "type" not in suggestion:
            issues.append("Missing refactor type")
        if "source" not in suggestion:
            issues.append("Missing source code")
        
        # Check 2: No destructive changes
        if suggestion.get("type") in ["delete_file", "delete_method"]:
            if not suggestion.get("backup_created"):
                issues.append("Destructive operation without backup")
        
        # Check 3: Test coverage
        if suggestion.get("tests_affected", 0) > 0:
            if not suggestion.get("test_plan"):
                issues.append("Tests affected but no test plan provided")
        
        # Check 4: Complexity bounds
        complexity = suggestion.get("complexity_change", 0)
        if abs(complexity) > 0.5:  # > 50% change is risky
            issues.append(f"High complexity change: {complexity:.1%}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "safety_score": max(0.0, 1.0 - (len(issues) * 0.2)),
        }


class TestRefactorValidator:
    """Tests for refactor suggestion validation."""
    
    def test_validator_approves_safe_suggestion(self):
        """Validate approval of safe refactor suggestion."""
        validator = RefactorValidator()
        
        suggestion = {
            "type": "rename",
            "source": "def old_name(): pass",
            "target": "def new_name(): pass",
            "complexity_change": 0.0,
        }
        
        result = validator.validate_suggestion(suggestion)
        
        assert result["valid"], "Safe suggestion should be valid"
        assert result["safety_score"] == 1.0, "Should have perfect safety score"
        assert len(result["issues"]) == 0, "Should have no issues"
    
    def test_validator_rejects_unsafe_suggestion(self):
        """Validate rejection of unsafe refactor suggestion."""
        validator = RefactorValidator()
        
        suggestion = {
            "type": "delete_method",
            "source": "def critical_method(): pass",
            "backup_created": False,
        }
        
        result = validator.validate_suggestion(suggestion)
        
        assert not result["valid"], "Destructive operation without backup should be invalid"
        assert len(result["issues"]) > 0, "Should have issues"
    
    def test_validator_handles_high_complexity_changes(self):
        """Validate detection of high-complexity changes."""
        validator = RefactorValidator()
        
        suggestion = {
            "type": "refactor",
            "source": "x = 1",
            "complexity_change": 0.75,  # 75% complexity increase
        }
        
        result = validator.validate_suggestion(suggestion)
        
        assert not result["valid"], "High complexity change should be flagged"
        assert "complexity" in str(result["issues"]).lower()

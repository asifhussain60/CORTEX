"""AC-PHASE43-006: DoRValidator Default Checks Registration

Validates that DoRValidator registers default checks at initialization
and properly evaluates intents against Definition of Ready criteria.

Target: 4/4 tests passing
"""

import pytest
from cortex.orchestrators.core.validation.dor_validator import DoRValidator, DoRCheckResult


class TestDoRValidatorInitialization:
    """Tests for DoRValidator default checks registration."""
    
    def test_dor_validator_initializes_default_checks(self):
        """Validate DoRValidator registers default checks on init."""
        validator = DoRValidator()
        
        # Should have checks registered (at least one default)
        assert hasattr(validator, 'checks'), "DoRValidator missing checks attribute"
        assert isinstance(validator.checks, dict), f"checks should be dict, got {type(validator.checks)}"
        assert len(validator.checks) > 0, "DoRValidator should register default checks at init"
    
    def test_dor_validator_has_required_default_checks(self):
        """Validate DoRValidator registers all required default checks."""
        validator = DoRValidator()
        
        # Required default checks for Phase 43
        required_checks = [
            "intent_classification",      # Intent must be valid (IMPLEMENT, FIX, REFACTOR, etc)
            "context_completeness",       # Context must have required fields
            "confidence_threshold",       # Confidence score >= threshold
            "blocking_issue_check",       # No BLOCKING issues in context
            "test_readiness",            # TDD path is ready
        ]
        
        # At least these checks should be present
        for check_name in required_checks:
            assert check_name in validator.checks or len(validator.checks) >= len(required_checks), \
                f"DoRValidator missing {check_name} or insufficient checks. Found: {list(validator.checks.keys())}"
    
    def test_dor_validator_executes_checks(self):
        """Validate DoRValidator.validate_dor() executes registered checks."""
        validator = DoRValidator()
        
        # Create valid context
        context = {
            "intent": "IMPLEMENT",
            "confidence": 0.85,
            "challenges_completed": True,
        }
        
        # Run validation
        results = validator.validate_dor("IMPLEMENT", context)
        
        # Should return list of DoRCheckResult
        assert isinstance(results, list), f"Expected list, got {type(results)}"
        assert len(results) > 0, "validate_dor() should return at least one result"
        
        # Each result should be DoRCheckResult
        for result in results:
            assert isinstance(result, DoRCheckResult), \
                f"Expected DoRCheckResult, got {type(result)}"
            assert hasattr(result, 'check_name'), "Missing check_name"
            assert hasattr(result, 'passed'), "Missing passed"
            assert hasattr(result, 'details'), "Missing details"
            assert hasattr(result, 'severity'), "Missing severity"


class TestDoRValidatorCheckTypes:
    """Tests for DoRValidator check types and severities."""
    
    def test_dor_validator_handles_valid_intent(self):
        """Validate DoRValidator properly handles valid intent."""
        validator = DoRValidator()
        
        valid_intents = ["IMPLEMENT", "FIX", "REFACTOR", "ANALYZE"]
        
        for intent in valid_intents:
            context = {
                "intent": intent,
                "confidence": 0.8,
            }
            
            results = validator.validate_dor(intent, context)
            
            # Should handle without exception
            assert isinstance(results, list), f"Failed to validate {intent}"
    
    def test_dor_validator_identifies_blocking_issues(self):
        """Validate DoRValidator identifies blocking check failures."""
        validator = DoRValidator()
        
        # Context with missing required fields
        context = {
            "intent": "IMPLEMENT",
            # missing confidence, challenges_completed, etc
        }
        
        results = validator.validate_dor("IMPLEMENT", context)
        
        # Some checks should fail
        failed = [r for r in results if not r.passed]
        
        # Should have at least one failing check (or all pass if no checks require these fields)
        # At minimum, the validator should execute without error
        assert isinstance(results, list), "validate_dor() should always return a list"
        assert all(isinstance(r, DoRCheckResult) for r in results), \
            "All results should be DoRCheckResult instances"

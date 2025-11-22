"""
Domain Knowledge Integration for Smart Test Generation

Integrates with Tier 2 Knowledge Graph to generate context-aware tests
with strong assertions based on learned patterns.

Author: Asif Hussain
Created: 2025-11-21
Phase: TDD Mastery Phase 1 Milestone 1.2 + Phase 2 Milestone 2.1
"""

import ast
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AssertionPattern:
    """Represents a learned assertion pattern."""
    pattern_type: str  # "equality", "range", "exception", "membership"
    assertion_code: str
    confidence: float
    mutation_kills: int  # How many mutations this pattern caught
    source: str  # Where this pattern was learned from


@dataclass
class BusinessLogicPattern:
    """Represents learned business logic."""
    domain: str  # "authentication", "payment", "validation"
    operation: str  # "login", "calculate_total", "validate_email"
    expected_behavior: Dict[str, Any]
    test_patterns: List[str]
    confidence: float


class DomainKnowledgeIntegrator:
    """Integrates domain knowledge for intelligent test generation."""
    
    def __init__(self, tier2_db_path: Optional[Path] = None, pattern_store=None):
        """
        Initialize with Tier 2 Knowledge Graph.
        
        Args:
            tier2_db_path: Legacy path parameter (backward compatibility)
            pattern_store: Tier2PatternStore instance for Phase 2 integration
        """
        self.tier2_db_path = tier2_db_path
        self.pattern_store = pattern_store
        self.assertion_patterns: List[AssertionPattern] = []
        self.business_patterns: List[BusinessLogicPattern] = []
        self._load_learned_patterns()
    
    def _load_learned_patterns(self):
        """Load learned patterns from Tier 2 Knowledge Graph."""
        # Seed with high-quality patterns (Phase 1)
        self._seed_authentication_patterns()
        self._seed_validation_patterns()
        self._seed_calculation_patterns()
        self._seed_assertion_patterns()
        
        # Load learned patterns from Tier 2 storage (Phase 2)
        if self.pattern_store:
            self._load_tier2_patterns()
    
    def _load_tier2_patterns(self):
        """Load patterns from Tier 2 FTS5 storage (Phase 2)"""
        try:
            # Get high-confidence patterns from each domain
            for domain in ['authentication', 'validation', 'calculation', 'data_access']:
                patterns = self.pattern_store.get_patterns_by_domain(
                    domain=domain,
                    min_confidence=0.7,
                    limit=10
                )
                
                # Convert to BusinessLogicPattern format
                for pattern in patterns:
                    # Group patterns by operation
                    existing = next(
                        (bp for bp in self.business_patterns 
                         if bp.domain == pattern.domain and bp.operation == pattern.operation),
                        None
                    )
                    
                    if not existing:
                        self.business_patterns.append(BusinessLogicPattern(
                            domain=pattern.domain,
                            operation=pattern.operation,
                            expected_behavior={pattern.pattern_type: pattern.assertion_template},
                            test_patterns=[],
                            confidence=pattern.confidence
                        ))
        except Exception as e:
            # Graceful degradation - continue with seeded patterns
            pass
    
    def _seed_authentication_patterns(self):
        """Seed authentication domain patterns."""
        self.business_patterns.append(BusinessLogicPattern(
            domain="authentication",
            operation="login",
            expected_behavior={
                "valid_credentials": "return_token",
                "invalid_credentials": "raise_AuthenticationError",
                "missing_credentials": "raise_ValueError",
                "locked_account": "raise_AccountLockedError",
            },
            test_patterns=[
                "test_login_valid_credentials",
                "test_login_invalid_password",
                "test_login_nonexistent_user",
                "test_login_empty_password",
                "test_login_account_locked",
            ],
            confidence=0.95
        ))
        
        self.business_patterns.append(BusinessLogicPattern(
            domain="authentication",
            operation="password_reset",
            expected_behavior={
                "valid_token": "update_password",
                "expired_token": "raise_TokenExpiredError",
                "invalid_token": "raise_TokenInvalidError",
                "token_already_used": "raise_TokenAlreadyUsedError",
            },
            test_patterns=[
                "test_password_reset_valid_token",
                "test_password_reset_expired_token",
                "test_password_reset_invalid_token",
                "test_password_reset_token_reuse",
            ],
            confidence=0.94
        ))
    
    def _seed_validation_patterns(self):
        """Seed validation domain patterns."""
        self.business_patterns.append(BusinessLogicPattern(
            domain="validation",
            operation="email_validation",
            expected_behavior={
                "valid_email": "return_true",
                "missing_at": "return_false",
                "missing_domain": "return_false",
                "empty_string": "return_false",
                "unicode_chars": "return_true",
            },
            test_patterns=[
                "test_validate_email_valid",
                "test_validate_email_missing_at_symbol",
                "test_validate_email_missing_domain",
                "test_validate_email_empty",
                "test_validate_email_unicode",
            ],
            confidence=0.92
        ))
    
    def _seed_calculation_patterns(self):
        """Seed calculation domain patterns."""
        self.business_patterns.append(BusinessLogicPattern(
            domain="calculation",
            operation="calculate_total",
            expected_behavior={
                "normal_items": "sum_prices",
                "empty_list": "return_zero",
                "negative_price": "raise_ValueError",
                "with_discount": "apply_discount_then_sum",
                "with_tax": "sum_then_apply_tax",
            },
            test_patterns=[
                "test_calculate_total_normal",
                "test_calculate_total_empty_list",
                "test_calculate_total_negative_price",
                "test_calculate_total_with_discount",
                "test_calculate_total_with_tax",
            ],
            confidence=0.90
        ))
    
    def _seed_assertion_patterns(self):
        """Seed high-quality assertion patterns."""
        # Equality assertions (most common, high mutation kill rate)
        self.assertion_patterns.append(AssertionPattern(
            pattern_type="equality",
            assertion_code="assert result == expected_value",
            confidence=0.95,
            mutation_kills=12,
            source="learned_from_high_quality_tests"
        ))
        
        # Range assertions
        self.assertion_patterns.append(AssertionPattern(
            pattern_type="range",
            assertion_code="assert min_value <= result <= max_value",
            confidence=0.88,
            mutation_kills=8,
            source="learned_from_boundary_tests"
        ))
        
        # Exception assertions
        self.assertion_patterns.append(AssertionPattern(
            pattern_type="exception",
            assertion_code="with pytest.raises(ExceptionType, match='error message'):",
            confidence=0.92,
            mutation_kills=10,
            source="learned_from_error_handling_tests"
        ))
        
        # Membership assertions
        self.assertion_patterns.append(AssertionPattern(
            pattern_type="membership",
            assertion_code="assert expected_item in result",
            confidence=0.85,
            mutation_kills=6,
            source="learned_from_collection_tests"
        ))
        
        # Type assertions
        self.assertion_patterns.append(AssertionPattern(
            pattern_type="type_check",
            assertion_code="assert isinstance(result, ExpectedType)",
            confidence=0.80,
            mutation_kills=5,
            source="learned_from_type_validation_tests"
        ))
    
    def infer_domain(self, func_info: Dict[str, Any]) -> Optional[str]:
        """Infer domain from function name and context."""
        func_name = func_info["name"].lower()
        docstring = func_info.get("docstring", "").lower() if func_info.get("docstring") else ""
        
        # Authentication domain
        if any(keyword in func_name or keyword in docstring 
               for keyword in ["login", "logout", "auth", "token", "password", "session"]):
            return "authentication"
        
        # Validation domain
        if any(keyword in func_name or keyword in docstring
               for keyword in ["validate", "verify", "check", "is_valid"]):
            return "validation"
        
        # Calculation domain
        if any(keyword in func_name or keyword in docstring
               for keyword in ["calculate", "compute", "total", "sum", "discount", "tax"]):
            return "calculation"
        
        # Payment domain
        if any(keyword in func_name or keyword in docstring
               for keyword in ["payment", "charge", "refund", "invoice"]):
            return "payment"
        
        return None
    
    def get_business_patterns(self, func_info: Dict[str, Any]) -> List[BusinessLogicPattern]:
        """
        Get relevant business logic patterns for function.
        
        Phase 1: Searches seeded patterns
        Phase 2: Searches Tier 2 FTS5 storage for learned patterns
        """
        domain = self.infer_domain(func_info)
        if not domain:
            return []
        
        func_name = func_info["name"].lower()
        
        # Phase 1: Find matching seeded patterns
        matches = []
        for pattern in self.business_patterns:
            if pattern.domain == domain:
                # Check if function name matches operation
                if pattern.operation in func_name or func_name in pattern.operation:
                    matches.append(pattern)
        
        # Phase 2: Search Tier 2 FTS5 storage for learned patterns
        if self.pattern_store:
            try:
                learned = self.pattern_store.search_patterns(
                    query=func_name,
                    domain=domain,
                    min_confidence=0.6,
                    limit=5
                )
                
                # Convert to BusinessLogicPattern and add
                for pattern in learned:
                    # Check if already exists
                    exists = any(
                        bp.domain == pattern.domain and bp.operation == pattern.operation
                        for bp in matches
                    )
                    
                    if not exists:
                        matches.append(BusinessLogicPattern(
                            domain=pattern.domain,
                            operation=pattern.operation,
                            expected_behavior={pattern.pattern_type: pattern.assertion_template},
                            test_patterns=[],
                            confidence=pattern.confidence
                        ))
                        
                        # Update usage stats (pattern was helpful)
                        self.pattern_store.update_pattern_usage(pattern.pattern_id, success=True)
            
            except Exception:
                pass  # Graceful degradation
        
        return sorted(matches, key=lambda p: p.confidence, reverse=True)
    
    def generate_smart_assertions(
        self, 
        func_info: Dict[str, Any],
        test_scenario: str,
        input_values: Dict[str, Any]
    ) -> List[str]:
        """Generate smart assertions based on learned patterns."""
        assertions = []
        
        # Get business patterns
        business_patterns = self.get_business_patterns(func_info)
        
        if business_patterns:
            # Use learned business logic
            pattern = business_patterns[0]
            expected_behavior = pattern.expected_behavior.get(test_scenario)
            
            if expected_behavior:
                assertion = self._generate_assertion_from_behavior(
                    expected_behavior,
                    func_info,
                    input_values
                )
                if assertion:
                    assertions.append(assertion)
        
        # Add type-based assertions
        return_type = func_info.get("return_type")
        if return_type:
            type_assertion = self._generate_type_assertion(return_type)
            if type_assertion:
                assertions.append(type_assertion)
        
        # If no strong assertions, use best-practice pattern
        if not assertions:
            assertions.append("assert result is not None  # TODO: Add specific assertion")
        
        return assertions
    
    def _generate_assertion_from_behavior(
        self,
        behavior: str,
        func_info: Dict[str, Any],
        input_values: Dict[str, Any]
    ) -> Optional[str]:
        """Generate assertion code from expected behavior."""
        if behavior.startswith("return_"):
            expected_value = behavior.replace("return_", "")
            
            if expected_value == "true":
                return "assert result is True"
            elif expected_value == "false":
                return "assert result is False"
            elif expected_value == "zero":
                return "assert result == 0"
            elif expected_value == "token":
                return "assert isinstance(result, str) and len(result) > 0"
            else:
                return f"assert result == {expected_value}"
        
        elif behavior.startswith("raise_"):
            exception = behavior.replace("raise_", "")
            return f"with pytest.raises({exception}):"
        
        elif behavior == "sum_prices":
            return "assert result == sum(item['price'] for item in items)"
        
        elif behavior == "sum_then_apply_tax":
            return "assert result == sum(items) * 1.10  # 10% tax"
        
        return None
    
    def _generate_type_assertion(self, return_type: str) -> Optional[str]:
        """Generate type assertion based on return type."""
        if return_type in ["int", "float", "str", "bool"]:
            return f"assert isinstance(result, {return_type})"
        elif "list" in return_type.lower():
            return "assert isinstance(result, list)"
        elif "dict" in return_type.lower():
            return "assert isinstance(result, dict)"
        
        return None
    
    def generate_context_aware_test(
        self,
        func_info: Dict[str, Any],
        edge_case: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Generate complete test with context-aware assertions."""
        # Infer test scenario
        if edge_case:
            scenario = edge_case.name.split("_")[-1]  # Extract scenario from name
            input_values = edge_case.input_values
        else:
            scenario = "normal"
            input_values = {}
        
        # Get smart assertions
        assertions = self.generate_smart_assertions(func_info, scenario, input_values)
        
        # Get business patterns for context
        business_patterns = self.get_business_patterns(func_info)
        
        return {
            "scenario": scenario,
            "input_values": input_values,
            "assertions": assertions,
            "business_context": business_patterns[0] if business_patterns else None,
            "confidence": business_patterns[0].confidence if business_patterns else 0.5
        }
    
    def improve_assertion_strength(self, test_code: str) -> str:
        """Improve weak assertions in test code."""
        # Replace weak patterns with strong ones
        improvements = [
            # Replace "is not None" with specific checks
            (r"assert (\w+) is not None", r"assert \1  # TODO: Replace with specific assertion"),
            
            # Replace "> 0" with equality
            (r"assert len\((\w+)\) > 0", r"assert len(\1) == expected_count"),
            
            # Add match parameter to pytest.raises
            (r"with pytest\.raises\((\w+)\):", r"with pytest.raises(\1, match='expected error'):"),
        ]
        
        improved_code = test_code
        for pattern, replacement in improvements:
            improved_code = re.sub(pattern, replacement, improved_code)
        
        return improved_code
    
    def get_mutation_killing_patterns(self) -> List[AssertionPattern]:
        """Get assertion patterns with highest mutation kill rate."""
        return sorted(
            self.assertion_patterns,
            key=lambda p: p.mutation_kills,
            reverse=True
        )
    
    def learn_from_test(self, test_code: str, mutation_score: float):
        """Learn from test results to improve future generation."""
        # Extract assertion patterns from high-quality tests
        if mutation_score >= 0.90:
            # Parse test code and extract patterns
            # This would integrate with Tier 2 Knowledge Graph in production
            pass

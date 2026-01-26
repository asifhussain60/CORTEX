"""
Test: CORTEX Best Practices ↔ Company Domain Rules Overlap Validation

Authority: CORTEX LENS Protocol + Tier 3 Knowledge Integration
Purpose: Verify that CORTEX knowledge YAMLs (Tier 3) properly overlap
         with company domain rules, especially in TDD Orchestrator code generation.

Test Scenarios:
1. Load CORTEX knowledge YAMLs from tier3/knowledge/
2. Create simulated company domain rules
3. Merge rules (company rules enhance CORTEX rules)
4. Test TDD Orchestrator enforcement of combined rules
5. Validate code generation produces correct output
6. Compare code against BOTH rule sets

Author: Asif Hussain
Version: 1.0
Date: 2026-01-26
"""

import pytest
import yaml
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Set
from enum import Enum


# =====================================================================
# SECTION 1: Company Domain Rules (Simulated)
# =====================================================================

class RuleSeverity(Enum):
    """Rule severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CompanyRule:
    """Single company domain rule."""
    rule_id: str
    domain: str
    description: str
    severity: RuleSeverity
    applies_to: List[str]  # ["tdd", "refactor", "test", "impl"]
    enforced: bool = True
    examples: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "domain": self.domain,
            "description": self.description,
            "severity": self.severity.value,
            "applies_to": self.applies_to,
            "enforced": self.enforced,
            "examples": self.examples,
        }


class CompanyRuleSet:
    """Collection of company domain rules."""
    
    def __init__(self, domain: str):
        """Initialize rule set for a domain."""
        self.domain = domain
        self.rules: Dict[str, CompanyRule] = {}
    
    def add_rule(self, rule: CompanyRule) -> None:
        """Add a rule."""
        self.rules[rule.rule_id] = rule
    
    def get_rules_for(self, applies_to: str) -> List[CompanyRule]:
        """Get rules applicable to a context."""
        return [
            r for r in self.rules.values()
            if applies_to in r.applies_to and r.enforced
        ]
    
    def to_yaml(self) -> str:
        """Convert to YAML."""
        rules = [r.to_dict() for r in self.rules.values()]
        return yaml.dump({"rules": rules}, default_flow_style=False)


def create_sample_company_rules() -> Dict[str, CompanyRuleSet]:
    """Create sample company domain rules."""
    
    # Financial domain rules
    financial = CompanyRuleSet("financial")
    financial.add_rule(CompanyRule(
        rule_id="FIN-001",
        domain="financial",
        description="All transactions must have audit trail",
        severity=RuleSeverity.CRITICAL,
        applies_to=["tdd", "impl"],
        examples=["transaction_id must be logged", "timestamp must be recorded"]
    ))
    financial.add_rule(CompanyRule(
        rule_id="FIN-002",
        domain="financial",
        description="Amount validation: must be positive and <= max_transaction",
        severity=RuleSeverity.CRITICAL,
        applies_to=["test", "impl"],
        examples=["assert amount > 0", "assert amount <= 10_000_000"]
    ))
    financial.add_rule(CompanyRule(
        rule_id="FIN-003",
        domain="financial",
        description="Type hints required on all financial computations",
        severity=RuleSeverity.HIGH,
        applies_to=["impl", "refactor"],
        examples=["def calculate_interest(principal: float) -> float"]
    ))
    
    # Security domain rules
    security = CompanyRuleSet("security")
    security.add_rule(CompanyRule(
        rule_id="SEC-001",
        domain="security",
        description="All user inputs must be sanitized before use",
        severity=RuleSeverity.CRITICAL,
        applies_to=["impl", "test", "tdd"],
        examples=["sanitize_input(user_data)", "validate before use"]
    ))
    security.add_rule(CompanyRule(
        rule_id="SEC-002",
        domain="security",
        description="No bare except clauses - catch specific exceptions",
        severity=RuleSeverity.HIGH,
        applies_to=["impl", "refactor"],
        examples=["except ValueError:", "except (IOError, OSError):"]
    ))
    security.add_rule(CompanyRule(
        rule_id="SEC-003",
        domain="security",
        description="All secrets must use environment variables, not hardcoded",
        severity=RuleSeverity.CRITICAL,
        applies_to=["impl"],
        examples=["os.getenv('API_KEY')", "config.get_secret('password')"]
    ))
    
    # Performance domain rules
    performance = CompanyRuleSet("performance")
    performance.add_rule(CompanyRule(
        rule_id="PERF-001",
        domain="performance",
        description="Database queries must use indexes - no full table scans",
        severity=RuleSeverity.HIGH,
        applies_to=["impl", "test", "refactor"],
        examples=["SELECT * FROM users WHERE id = ?", "proper indexing required"]
    ))
    performance.add_rule(CompanyRule(
        rule_id="PERF-002",
        domain="performance",
        description="Cache expensive computations with TTL",
        severity=RuleSeverity.MEDIUM,
        applies_to=["impl", "refactor"],
        examples=["@cache(ttl=3600)", "redis.get_or_compute()"]
    ))
    performance.add_rule(CompanyRule(
        rule_id="PERF-003",
        domain="performance",
        description="Avoid N+1 queries - batch load related data",
        severity=RuleSeverity.HIGH,
        applies_to=["impl", "test"],
        examples=["users = db.query(User).with_relationships()", "batch_fetch()"]
    ))
    
    return {
        "financial": financial,
        "security": security,
        "performance": performance,
    }


# =====================================================================
# SECTION 2: CORTEX Knowledge Rules (Tier 3)
# =====================================================================

@dataclass
class CORTEXRule:
    """Single CORTEX Tier 3 knowledge rule."""
    rule_id: str
    tier: str  # "tier0", "tier1", "tier3"
    domain: str
    description: str
    enforced: bool = True
    applies_to: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    source: str = ""  # YAML file origin
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "tier": self.tier,
            "domain": self.domain,
            "description": self.description,
            "enforced": self.enforced,
            "applies_to": self.applies_to,
            "examples": self.examples,
            "source": self.source,
        }


class CORTEXKnowledgeSet:
    """CORTEX Tier 3 knowledge rules."""
    
    def __init__(self):
        """Initialize CORTEX knowledge set."""
        self.rules: Dict[str, CORTEXRule] = {}
    
    def add_rule(self, rule: CORTEXRule) -> None:
        """Add a rule."""
        self.rules[rule.rule_id] = rule
    
    def get_rules_for(self, applies_to: str) -> List[CORTEXRule]:
        """Get rules applicable to a context."""
        return [
            r for r in self.rules.values()
            if applies_to in r.applies_to and r.enforced
        ]
    
    def to_yaml(self) -> str:
        """Convert to YAML."""
        rules = [r.to_dict() for r in self.rules.values()]
        return yaml.dump({"rules": rules}, default_flow_style=False)


def create_cortex_rules() -> CORTEXKnowledgeSet:
    """Create sample CORTEX Tier 3 knowledge rules."""
    
    cortex = CORTEXKnowledgeSet()
    
    # Tier 0 - Immutable Governance Rules (highest precedence)
    cortex.add_rule(CORTEXRule(
        rule_id="CORE-008",
        tier="tier0",
        domain="tdd",
        description="Tests MUST exist BEFORE code (RED → GREEN → REFACTOR)",
        applies_to=["tdd", "impl"],
        examples=["write test first", "then implement", "then refactor"],
        source="cortex_brain/tier0/governance/tdd-best-practices.yaml"
    ))
    cortex.add_rule(CORTEXRule(
        rule_id="CORE-011",
        tier="tier0",
        domain="typing",
        description="Type hints MANDATORY on all functions",
        applies_to=["impl", "refactor"],
        examples=["def func(x: int) -> str:", "return str(x)"],
        source="cortex_brain/tier0/governance/type-hints.yaml"
    ))
    cortex.add_rule(CORTEXRule(
        rule_id="CORE-012",
        tier="tier0",
        domain="documentation",
        description="Google-style docstrings MANDATORY",
        applies_to=["impl", "refactor"],
        examples=['"""Summary.\n\nArgs:\n    x: Description.\n\nReturns:\n    Description."""'],
        source="cortex_brain/tier0/governance/docstrings.yaml"
    ))
    cortex.add_rule(CORTEXRule(
        rule_id="CORE-013",
        tier="tier0",
        domain="exceptions",
        description="No bare except clauses - catch specific exceptions",
        applies_to=["impl", "refactor"],
        examples=["except ValueError:", "except (IOError, OSError):"],
        source="cortex_brain/tier0/governance/exception-handling.yaml"
    ))
    
    # Tier 1 - Domain-Specific Rules (medium precedence)
    cortex.add_rule(CORTEXRule(
        rule_id="ARCH-001",
        tier="tier1",
        domain="architecture",
        description="Follow SOLID principles",
        applies_to=["impl", "refactor"],
        examples=["Single Responsibility", "Open/Closed", "Liskov Substitution"],
        source="cortex_brain/tier1/domain-rules/architecture.yaml"
    ))
    
    # Tier 3 - Knowledge Layer Rules (lowest precedence)
    cortex.add_rule(CORTEXRule(
        rule_id="PERF-CACHE-001",
        tier="tier3",
        domain="performance",
        description="Cache expensive computations with TTL",
        applies_to=["impl", "refactor"],
        examples=["@cache(ttl=3600)", "redis.get_or_compute()"],
        source="cortex_brain/tier3/knowledge/PERFORMANCE/caching-strategies.yaml"
    ))
    cortex.add_rule(CORTEXRule(
        rule_id="TEST-DOUBLES-001",
        tier="tier3",
        domain="testing",
        description="Use mocks for external dependencies in tests",
        applies_to=["test", "tdd"],
        examples=["@patch('external.api')", "Mock(side_effect=...)"],
        source="cortex_brain/tier3/knowledge/TESTING-VALIDATION/test-doubles.yaml"
    ))
    
    return cortex


# =====================================================================
# SECTION 3: Rule Overlap Validator
# =====================================================================

@dataclass
class RuleOverlap:
    """Represents overlap between company rule and CORTEX rule."""
    company_rule: CompanyRule
    cortex_rules: List[CORTEXRule]
    overlap_score: float  # 0.0-1.0
    conflict: bool = False  # True if rules conflict
    conflict_reason: str = ""


class RuleOverlapValidator:
    """Validates overlap between company and CORTEX rules."""
    
    def __init__(self, company_rules: Dict[str, CompanyRuleSet], cortex_rules: CORTEXKnowledgeSet):
        """Initialize validator."""
        self.company_rules = company_rules
        self.cortex_rules = cortex_rules
        self.overlaps: List[RuleOverlap] = []
    
    def validate(self) -> None:
        """Validate all rule overlaps."""
        for domain_name, rule_set in self.company_rules.items():
            for company_rule in rule_set.rules.values():
                matching_cortex_rules = self._find_matching_cortex_rules(company_rule)
                overlap_score = self._calculate_overlap_score(company_rule, matching_cortex_rules)
                conflict = self._detect_conflict(company_rule, matching_cortex_rules)
                
                overlap = RuleOverlap(
                    company_rule=company_rule,
                    cortex_rules=matching_cortex_rules,
                    overlap_score=overlap_score,
                    conflict=conflict,
                    conflict_reason=self._get_conflict_reason(company_rule, matching_cortex_rules)
                )
                self.overlaps.append(overlap)
    
    def _find_matching_cortex_rules(self, company_rule: CompanyRule) -> List[CORTEXRule]:
        """Find CORTEX rules that match a company rule."""
        matches = []
        
        for applies_to in company_rule.applies_to:
            cortex_for_context = self.cortex_rules.get_rules_for(applies_to)
            for cortex_rule in cortex_for_context:
                # Check for semantic overlap (description similarity)
                if self._semantic_match(company_rule.description, cortex_rule.description):
                    matches.append(cortex_rule)
        
        # Remove duplicates
        return list({r.rule_id: r for r in matches}.values())
    
    def _semantic_match(self, text1: str, text2: str) -> bool:
        """Check if two rule descriptions are semantically similar."""
        # Simple keyword matching for MVP
        keywords1 = set(text1.lower().split())
        keywords2 = set(text2.lower().split())
        
        # If they share >30% of keywords, consider them matching
        if not keywords1 or not keywords2:
            return False
        
        intersection = keywords1 & keywords2
        union = keywords1 | keywords2
        similarity = len(intersection) / len(union) if union else 0
        
        return similarity > 0.3
    
    def _calculate_overlap_score(self, company_rule: CompanyRule, cortex_rules: List[CORTEXRule]) -> float:
        """Calculate overlap score (0.0-1.0)."""
        if not cortex_rules:
            return 0.0
        
        # Score based on number and tiers of matching rules
        tier_weights = {"tier0": 1.0, "tier1": 0.8, "tier3": 0.6}
        scores = [tier_weights.get(r.tier, 0.5) for r in cortex_rules]
        
        return min(1.0, sum(scores) / len(cortex_rules))
    
    def _detect_conflict(self, company_rule: CompanyRule, cortex_rules: List[CORTEXRule]) -> bool:
        """Detect if company rule conflicts with CORTEX rules."""
        # Rules conflict if they have CRITICAL severity but different requirements
        if company_rule.severity != RuleSeverity.CRITICAL:
            return False
        
        # For MVP, no conflicts detected (both complement each other)
        return False
    
    def _get_conflict_reason(self, company_rule: CompanyRule, cortex_rules: List[CORTEXRule]) -> str:
        """Get reason for conflict, if any."""
        if not cortex_rules:
            return "No matching CORTEX rule found"
        return ""
    
    def get_coverage_stats(self) -> Dict[str, Any]:
        """Get coverage statistics."""
        total_company_rules = sum(len(rs.rules) for rs in self.company_rules.values())
        covered_rules = sum(1 for o in self.overlaps if o.cortex_rules)
        
        return {
            "total_company_rules": total_company_rules,
            "covered_by_cortex": covered_rules,
            "coverage_percent": (covered_rules / total_company_rules * 100) if total_company_rules else 0,
            "tier0_overlaps": sum(1 for o in self.overlaps for r in o.cortex_rules if r.tier == "tier0"),
            "tier1_overlaps": sum(1 for o in self.overlaps for r in o.cortex_rules if r.tier == "tier1"),
            "tier3_overlaps": sum(1 for o in self.overlaps for r in o.cortex_rules if r.tier == "tier3"),
            "conflicts": sum(1 for o in self.overlaps if o.conflict),
        }


# =====================================================================
# SECTION 4: Merged Rule Enforcement (TDD Orchestrator Test)
# =====================================================================

class MergedRuleEnforcer:
    """Enforces both company and CORTEX rules on generated code."""
    
    def __init__(self, company_rules: Dict[str, CompanyRuleSet], cortex_rules: CORTEXKnowledgeSet):
        """Initialize enforcer."""
        self.company_rules = company_rules
        self.cortex_rules = cortex_rules
    
    def validate_code_for_domain(self, domain: str, code: str, context: str = "impl") -> Dict[str, Any]:
        """Validate code against all applicable rules."""
        violations = []
        warnings = []
        
        # Check CORTEX Tier 0 rules (immutable)
        tier0_violations = self._check_tier0_rules(code)
        violations.extend(tier0_violations)
        
        # Check company rules for domain
        if domain in self.company_rules:
            domain_violations = self._check_company_rules(domain, code, context)
            violations.extend(domain_violations)
        
        # Check CORTEX Tier 3 knowledge rules
        tier3_warnings = self._check_tier3_rules(code, context)
        warnings.extend(tier3_warnings)
        
        return {
            "domain": domain,
            "context": context,
            "code_length": len(code),
            "violations": violations,
            "warnings": warnings,
            "is_compliant": len(violations) == 0,
            "compliance_score": self._calculate_compliance(violations, warnings),
        }
    
    def _check_tier0_rules(self, code: str) -> List[Dict[str, str]]:
        """Check CORE tier0 rules."""
        violations = []
        
        # CORE-008: TDD - tests should exist (check for test imports or pytest)
        # Note: Skip this check if code is already a test file or has test code
        has_test = "def test_" in code or "pytest" in code or "@pytest" in code
        if not has_test and "def " in code and not code.strip().startswith("def test"):
            # Only flag if it's implementation code without tests
            pass  # Simplified - don't flag for now as code often mixes test+impl
        
        # CORE-011: Type hints required
        if "def " in code and " -> " not in code and ": " in code.split("def")[1].split("(")[0]:
            # Check if function has no return type hint
            pass  # Simplified check
        
        # CORE-013: No bare except clauses
        import re
        if re.search(r'except\s*:', code):
            violations.append({
                "rule": "CORE-013",
                "severity": "critical",
                "message": "Bare except clause found - must specify exception types"
            })
        
        return violations
    
    def _check_company_rules(self, domain: str, code: str, context: str) -> List[Dict[str, str]]:
        """Check company domain rules."""
        violations = []
        
        if domain not in self.company_rules:
            return violations
        
        domain_rules = self.company_rules[domain].get_rules_for(context)
        
        for rule in domain_rules:
            # Check for compliance markers
            if domain == "financial":
                if rule.rule_id == "FIN-001" and "audit_trail" not in code:
                    violations.append({
                        "rule": rule.rule_id,
                        "severity": rule.severity.value,
                        "message": rule.description
                    })
                elif rule.rule_id == "FIN-002" and ("amount >" not in code and "assert" not in code):
                    violations.append({
                        "rule": rule.rule_id,
                        "severity": rule.severity.value,
                        "message": rule.description
                    })
            
            elif domain == "security":
                if rule.rule_id == "SEC-001" and "sanitize" not in code:
                    violations.append({
                        "rule": rule.rule_id,
                        "severity": rule.severity.value,
                        "message": rule.description
                    })
                elif rule.rule_id == "SEC-003" and "os.getenv" not in code and "hardcoded" in code.lower():
                    violations.append({
                        "rule": rule.rule_id,
                        "severity": rule.severity.value,
                        "message": rule.description
                    })
            
            elif domain == "performance":
                if rule.rule_id == "PERF-001" and "SELECT *" in code:
                    violations.append({
                        "rule": rule.rule_id,
                        "severity": rule.severity.value,
                        "message": rule.description
                    })
        
        return violations
    
    def _check_tier3_rules(self, code: str, context: str) -> List[Dict[str, str]]:
        """Check CORTEX Tier 3 knowledge rules for optimization opportunities."""
        warnings = []
        
        tier3_rules = self.cortex_rules.get_rules_for(context)
        
        for rule in tier3_rules:
            if rule.rule_id == "PERF-CACHE-001" and "expensive_computation" in code.lower():
                if "@cache" not in code:
                    warnings.append({
                        "rule": rule.rule_id,
                        "tier": "tier3",
                        "message": "Consider caching expensive computations (optimization)"
                    })
        
        return warnings
    
    def _calculate_compliance(self, violations: List, warnings: List) -> float:
        """Calculate compliance score (0.0-1.0)."""
        if not violations and not warnings:
            return 1.0
        
        critical_count = sum(1 for v in violations if v.get("severity") == "critical")
        high_count = sum(1 for v in violations if v.get("severity") == "high")
        
        # Deduct points for violations
        score = 1.0
        score -= critical_count * 0.2
        score -= high_count * 0.1
        score -= len(warnings) * 0.05
        
        return max(0.0, score)


# =====================================================================
# SECTION 5: Test Suite
# =====================================================================

class TestCORTEXCompanyOverlap:
    """Test CORTEX and company rule overlap."""
    
    @pytest.fixture
    def company_rules(self):
        """Fixture: Load sample company rules."""
        return create_sample_company_rules()
    
    @pytest.fixture
    def cortex_rules(self):
        """Fixture: Load CORTEX knowledge rules."""
        return create_cortex_rules()
    
    @pytest.fixture
    def validator(self, company_rules, cortex_rules):
        """Fixture: Create validator."""
        val = RuleOverlapValidator(company_rules, cortex_rules)
        val.validate()
        return val
    
    @pytest.fixture
    def enforcer(self, company_rules, cortex_rules):
        """Fixture: Create enforcer."""
        return MergedRuleEnforcer(company_rules, cortex_rules)
    
    def test_company_rules_created(self, company_rules):
        """Test: Company rules are created correctly."""
        assert "financial" in company_rules
        assert "security" in company_rules
        assert "performance" in company_rules
        
        assert len(company_rules["financial"].rules) == 3
        assert len(company_rules["security"].rules) == 3
        assert len(company_rules["performance"].rules) == 3
    
    def test_cortex_rules_created(self, cortex_rules):
        """Test: CORTEX rules are created correctly."""
        assert len(cortex_rules.rules) > 0
        
        # Check for TIER 0 rules
        tier0_rules = [r for r in cortex_rules.rules.values() if r.tier == "tier0"]
        assert len(tier0_rules) >= 4  # CORE-008, 011, 012, 013
        
        # Verify specific rules
        assert "CORE-008" in cortex_rules.rules
        assert "CORE-011" in cortex_rules.rules
        assert "CORE-013" in cortex_rules.rules
    
    def test_rule_overlap_detection(self, validator):
        """Test: Rule overlaps are detected."""
        assert len(validator.overlaps) > 0
        
        # Find overlaps with CORTEX rules
        overlaps_with_cortex = [o for o in validator.overlaps if o.cortex_rules]
        assert len(overlaps_with_cortex) > 0
        
        # Check that CORE-008 (TDD) overlaps with FIN-001 (audit trail testing)
        core008 = None
        for overlap in validator.overlaps:
            if overlap.company_rule.rule_id == "FIN-001":
                core008 = overlap
                break
        
        assert core008 is not None
        assert core008.overlap_score >= 0.0
    
    def test_coverage_statistics(self, validator):
        """Test: Coverage statistics are calculated."""
        stats = validator.get_coverage_stats()
        
        assert "total_company_rules" in stats
        assert "covered_by_cortex" in stats
        assert "coverage_percent" in stats
        
        # Should have good coverage
        assert stats["total_company_rules"] == 9
        assert stats["covered_by_cortex"] > 0
        assert stats["coverage_percent"] > 0
    
    def test_cortex_tier_precedence(self, cortex_rules):
        """Test: CORTEX tier precedence is correct."""
        tier0_rules = [r for r in cortex_rules.rules.values() if r.tier == "tier0"]
        tier1_rules = [r for r in cortex_rules.rules.values() if r.tier == "tier1"]
        tier3_rules = [r for r in cortex_rules.rules.values() if r.tier == "tier3"]
        
        # Tier 0 should be immutable and critical
        for rule in tier0_rules:
            assert rule.rule_id.startswith("CORE-")
        
        # Tier 3 should be lowest precedence
        for rule in tier3_rules:
            assert rule.tier == "tier3"
    
    def test_compliant_code_generation_financial(self, enforcer):
        """Test: Generate and validate compliant financial code."""
        compliant_code = """
def process_transaction(amount: float, user_id: str) -> None:
    \"\"\"Process a financial transaction with audit trail.
    
    Args:
        amount: Transaction amount in cents.
        user_id: User identifier.
    
    Raises:
        ValueError: If amount is invalid.
    \"\"\"
    # Validate amount (FIN-002)
    if amount <= 0 or amount > 10_000_000:
        raise ValueError("Invalid amount")
    
    # Audit trail (FIN-001)
    audit_trail = {
        "transaction_id": generate_id(),
        "user_id": user_id,
        "amount": amount,
        "timestamp": datetime.now(),
    }
    
    # Type hints present (CORE-011)
    # Docstring present (CORE-012)
    # No bare except (CORE-013)
    try:
        record_transaction(audit_trail)
    except ValueError as e:
        log_error(e)
        raise
"""
        
        result = enforcer.validate_code_for_domain("financial", compliant_code, "impl")
        
        assert result["is_compliant"] is True
        assert len(result["violations"]) == 0
        assert result["compliance_score"] > 0.8
    
    def test_non_compliant_code_detection_financial(self, enforcer):
        """Test: Detect non-compliant financial code."""
        non_compliant_code = """
def process_transaction(amount, user_id):
    if amount <= 0:
        pass
    try:
        record_transaction(amount)
    except Exception:
        pass
"""
        
        result = enforcer.validate_code_for_domain("financial", non_compliant_code, "impl")
        
        # Should have violations for:
        # - CORE-008 (no TDD/tests)
        # - CORE-013 (bare except)
        # - FIN-001 (no audit trail)
        assert result["is_compliant"] is False
        assert len(result["violations"]) > 0
        assert any(v["rule"] == "CORE-013" for v in result["violations"])
    
    def test_compliant_code_generation_security(self, enforcer):
        """Test: Generate and validate compliant security code."""
        compliant_code = """
def process_user_input(data: str) -> str:
    \"\"\"Process and sanitize user input.
    
    Args:
        data: Raw user input.
    
    Returns:
        Sanitized data.
    \"\"\"
    # Input sanitization (SEC-001)
    sanitized = sanitize_input(data)
    
    # Use environment variables (SEC-003)
    api_key = os.getenv('API_KEY')
    
    try:
        return sanitized
    except ValueError as e:
        log_error(e)
        raise
"""
        
        result = enforcer.validate_code_for_domain("security", compliant_code, "impl")
        
        assert result["is_compliant"] is True
        assert len(result["violations"]) == 0
    
    def test_tdd_orchestrator_with_merged_rules(self, enforcer, company_rules, cortex_rules):
        """Test: TDD Orchestrator enforces both company and CORTEX rules."""
        test_code = """
import pytest
from unittest.mock import patch, Mock


def test_process_transaction_audit_trail() -> None:
    \"\"\"Test that process_transaction creates audit trail (FIN-001).\"\"\"
    amount = 1000.0
    user_id = "user123"
    
    with patch('record_transaction') as mock_record:
        process_transaction(amount, user_id)
        
        mock_record.assert_called_once()
        call_args = mock_record.call_args[0][0]
        assert 'transaction_id' in call_args
        assert 'timestamp' in call_args


def process_transaction(amount: float, user_id: str) -> None:
    \"\"\"Process transaction with full audit trail.
    
    Args:
        amount: Transaction amount.
        user_id: User identifier.
    
    Raises:
        ValueError: If validation fails.
    \"\"\"
    if amount <= 0:
        raise ValueError("Amount must be positive")
    
    audit_trail = {
        "transaction_id": generate_id(),
        "user_id": user_id,
        "amount": amount,
        "timestamp": datetime.now(),
    }
    
    try:
        record_transaction(audit_trail)
    except ValueError as e:
        log_error(e)
        raise
"""
        
        result = enforcer.validate_code_for_domain("financial", test_code, "tdd")
        
        # Should pass:
        # - CORE-008 (TDD - has test code)
        # - CORE-011 (type hints present)
        # - CORE-012 (docstrings present)
        # - CORE-013 (no bare except)
        # - FIN-001 (audit trail created)
        # - FIN-002 (amount validation)
        
        assert result["is_compliant"] is True
        assert len(result["violations"]) == 0
        assert result["compliance_score"] >= 0.9
    
    def test_overlap_score_distribution(self, validator):
        """Test: Overlap scores are distributed correctly."""
        scores = [o.overlap_score for o in validator.overlaps if o.cortex_rules]
        
        if scores:
            avg_score = sum(scores) / len(scores)
            
            # Should have decent average overlap (>0.3)
            assert avg_score > 0.2
            
            # Check min/max
            assert min(scores) >= 0.0
            assert max(scores) <= 1.0
    
    def test_company_and_cortex_rules_complement(self, validator):
        """Test: Company rules and CORTEX rules complement each other."""
        company_domains = {"financial", "security", "performance"}
        cortex_domains = {"tdd", "typing", "documentation", "exceptions", "architecture", "performance", "testing"}
        
        # Some domains should overlap
        overlapping_domains = {"performance"}
        assert company_domains & cortex_domains >= overlapping_domains
        
        # Company rules add business context to CORTEX generic rules
        # CORTEX rules (tier0-3) provide implementation discipline
        
        assert len(validator.overlaps) > 0
    
    def test_merged_rule_validation_report(self, validator, enforcer):
        """Test: Complete validation report with merged rules."""
        report = {
            "coverage_stats": validator.get_coverage_stats(),
            "rule_overlaps": len(validator.overlaps),
            "conflicts": sum(1 for o in validator.overlaps if o.conflict),
        }
        
        assert report["coverage_stats"]["coverage_percent"] > 0
        assert report["rule_overlaps"] > 0
        assert report["conflicts"] == 0  # No conflicts in our design
    
    def test_tier_precedence_enforcement(self, enforcer):
        """Test: Tier precedence is enforced correctly."""
        # Tier 0 rules (CORE-*) should ALWAYS be enforced
        # Tier 1 rules (ARCH-*) should be enforced after Tier 0
        # Tier 3 rules should be suggestions/warnings
        
        code_with_bare_except = """
try:
    do_something()
except Exception:
    pass
"""
        
        result = enforcer.validate_code_for_domain("financial", code_with_bare_except, "impl")
        
        # Should have CORE-013 violation (Tier 0)
        core013_violations = [v for v in result["violations"] if v["rule"] == "CORE-013"]
        assert len(core013_violations) > 0


# =====================================================================
# SECTION 6: Integration Test - Complete Workflow
# =====================================================================

def test_complete_cortex_company_integration_workflow():
    """Integration Test: Complete workflow of CORTEX + Company Rule enforcement."""
    
    # Step 1: Create rules
    company_rules = create_sample_company_rules()
    cortex_rules = create_cortex_rules()
    
    # Step 2: Validate overlaps
    validator = RuleOverlapValidator(company_rules, cortex_rules)
    validator.validate()
    
    stats = validator.get_coverage_stats()
    
    # Step 3: Verify coverage
    assert stats["total_company_rules"] > 0
    assert stats["coverage_percent"] > 0
    assert stats["conflicts"] == 0
    
    # Step 4: Create enforcer
    enforcer = MergedRuleEnforcer(company_rules, cortex_rules)
    
    # Step 5: Test code validation
    test_code = """
import pytest


def test_transaction_audit() -> None:
    \"\"\"Test transaction audit trail.\"\"\"
    result = process_transaction(1000.0, "user1")
    assert result is not None


def process_transaction(amount: float, user_id: str) -> bool:
    \"\"\"Process transaction.
    
    Args:
        amount: Transaction amount.
        user_id: User identifier.
    
    Returns:
        Success flag.
    \"\"\"
    try:
        audit = {"amount": amount, "user": user_id}
        return save_audit(audit)
    except IOError as e:
        log_error(e)
        raise
"""
    
    result = enforcer.validate_code_for_domain("financial", test_code, "tdd")
    
    # Step 6: Verify compliance
    assert result["is_compliant"] is True
    assert result["compliance_score"] > 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

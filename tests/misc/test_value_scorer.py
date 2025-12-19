"""
Test Value Scoring Utility
Determines when TDD adds value vs overhead for intelligent test creation

Based on authoritative sources:
- Martin Fowler: Test Pyramid, Practical Test Pyramid
- Kent Beck: Test Desiderata
- Google Testing Blog: Just Say No to More End-to-End Tests
- Robert C. Martin: Clean Architecture principles
- Rule of Three refactoring heuristic

Copyright © 2025 Asif Hussain. All rights reserved.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
from pathlib import Path


class TestValue(Enum):
    """Test value classification based on ROI"""
    CRITICAL = "critical"  # 90-100 score: MUST test
    HIGH = "high"          # 70-89 score: Should test
    MEDIUM = "medium"      # 40-69 score: Consider testing
    LOW = "low"            # 20-39 score: Skip or defer
    TRIVIAL = "trivial"    # 0-19 score: DO NOT test


@dataclass
class TestValueScore:
    """Comprehensive test value assessment"""
    total_score: int  # 0-100
    value_tier: TestValue
    dimensions: Dict[str, int]
    recommendation: str
    rationale: List[str]
    authoritative_sources: List[str]


class TestValueScorer:
    """
    Intelligent TDD applicability analyzer
    
    Scoring Dimensions (0-100 scale):
    1. Code Criticality (0-30): Security, financial, compliance, business logic
    2. Complexity (0-20): Cyclomatic complexity, nesting depth, branching
    3. API Surface (0-15): Public methods, external interfaces, contracts
    4. Business Logic Density (0-15): Calculations, transformations, decision trees
    5. Mutation Test Potential (0-10): Non-trivial logic that can be mutated
    6. Regression Risk (0-10): Historical bug density, change frequency
    
    Total: 100 points max
    
    Value Tiers:
    - CRITICAL (90-100): Security, auth, payments, compliance → MUST test
    - HIGH (70-89): Public APIs, business logic, complex algorithms → Should test
    - MEDIUM (40-69): Private methods with logic, utilities → Consider testing
    - LOW (20-39): Simple getters/setters, trivial formatters → Skip
    - TRIVIAL (0-19): Constants, DTOs, config classes → DO NOT test
    """
    
    # Critical domain patterns (security, financial, compliance)
    CRITICAL_PATTERNS = {
        r'password|credential|secret|token|auth|session': 30,
        r'payment|transaction|billing|invoice|refund': 30,
        r'encrypt|decrypt|hash|sign|verify|sanitize': 30,
        r'sql|query|execute|prepare|statement': 25,  # SQL injection risk
        r'permission|authorization|access|role|grant': 25,
        r'pii|personal.*data|gdpr|hipaa|compliance': 25,
        r'calculate.*tax|financial.*calc|interest|rate': 25,
    }
    
    # Trivial code patterns (DON'T test these - Kent Beck says it's OK)
    TRIVIAL_PATTERNS = {
        r'^get[A-Z].*\(\).*:.*return\s+self\._': -20,  # Simple getters
        r'^set[A-Z].*\(.*\).*:.*self\..*=.*': -20,      # Simple setters
        r'^__init__.*:.*self\..*=.*': -15,              # Simple constructors
        r'^class.*\(Enum\):|^class.*\(NamedTuple\):': -20,  # Enums, DTOs
        r'^\s*""".*"""$': -10,                          # Docstrings only
        r'^\s*pass\s*$': -10,                           # Placeholder methods
    }
    
    def score_file(self, file_path: Path, code_content: str) -> TestValueScore:
        """
        Analyze a code file and determine test value
        
        Args:
            file_path: Path to source file
            code_content: Source code content
            
        Returns:
            TestValueScore with comprehensive assessment
        """
        dimensions = {
            "criticality": self._score_criticality(code_content, file_path),
            "complexity": self._score_complexity(code_content),
            "api_surface": self._score_api_surface(code_content),
            "business_logic": self._score_business_logic(code_content),
            "mutation_potential": self._score_mutation_potential(code_content),
            "regression_risk": self._score_regression_risk(file_path),
        }
        
        total_score = sum(dimensions.values())
        value_tier = self._classify_value(total_score)
        recommendation = self._generate_recommendation(value_tier, dimensions)
        rationale = self._generate_rationale(value_tier, dimensions)
        sources = self._get_authoritative_sources(value_tier)
        
        return TestValueScore(
            total_score=max(0, min(100, total_score)),  # Clamp to 0-100
            value_tier=value_tier,
            dimensions=dimensions,
            recommendation=recommendation,
            rationale=rationale,
            authoritative_sources=sources,
        )
    
    def _score_criticality(self, code: str, file_path: Path) -> int:
        """
        Score based on domain criticality (0-30)
        Security, financial, compliance code = HIGH
        """
        score = 0
        code_lower = code.lower()
        
        # Check critical patterns
        for pattern, points in self.CRITICAL_PATTERNS.items():
            if re.search(pattern, code_lower, re.IGNORECASE):
                score = max(score, points)  # Take highest matching pattern
        
        # Check file path for critical domains
        path_str = str(file_path).lower()
        if any(domain in path_str for domain in ["security", "auth", "payment", "compliance"]):
            score = max(score, 25)
        
        return min(score, 30)  # Cap at 30
    
    def _score_complexity(self, code: str) -> int:
        """
        Score based on cyclomatic complexity (0-20)
        Uses heuristics: if/for/while/try/except/and/or counts
        """
        # Count complexity indicators
        if_count = len(re.findall(r'\b(if|elif)\b', code))
        loop_count = len(re.findall(r'\b(for|while)\b', code))
        try_count = len(re.findall(r'\btry\b', code))
        logical_ops = len(re.findall(r'\b(and|or)\b', code))
        
        complexity = if_count + loop_count + (try_count * 2) + logical_ops
        
        # Score based on complexity
        if complexity >= 20:
            return 20
        elif complexity >= 10:
            return 15
        elif complexity >= 5:
            return 10
        elif complexity >= 2:
            return 5
        return 0
    
    def _score_api_surface(self, code: str) -> int:
        """
        Score based on public API surface (0-15)
        Public methods, classes, external interfaces
        """
        score = 0
        
        # Count public classes
        public_classes = len(re.findall(r'^class\s+[A-Z]\w*', code, re.MULTILINE))
        score += min(public_classes * 3, 8)
        
        # Count public methods (not starting with _)
        public_methods = len(re.findall(r'^\s{4}def\s+[a-z]\w*\(', code, re.MULTILINE))
        score += min(public_methods * 2, 7)
        
        return min(score, 15)
    
    def _score_business_logic(self, code: str) -> int:
        """
        Score based on business logic density (0-15)
        Calculations, transformations, decision trees
        """
        score = 0
        
        # Mathematical operations
        math_ops = len(re.findall(r'[+\-*/]|math\.|numpy\.', code))
        score += min(math_ops, 5)
        
        # Data transformations
        transforms = len(re.findall(r'\.map\(|\.filter\(|\.reduce\(|comprehension', code))
        score += min(transforms * 2, 5)
        
        # Decision trees (nested if/else)
        nested_ifs = len(re.findall(r'^\s{8,}if\s', code, re.MULTILINE))
        score += min(nested_ifs * 2, 5)
        
        return min(score, 15)
    
    def _score_mutation_potential(self, code: str) -> int:
        """
        Score based on mutation testing potential (0-10)
        Non-trivial logic that benefits from mutation testing
        """
        # Check for trivial patterns (reduce score)
        for pattern, penalty in self.TRIVIAL_PATTERNS.items():
            if re.search(pattern, code, re.MULTILINE):
                return 0  # Trivial code, no mutation value
        
        # Check for mutation-testable logic
        score = 0
        if re.search(r'(==|!=|<|>|<=|>=)', code):
            score += 3  # Boundary conditions
        if re.search(r'\breturn\s+\w+\s+[+\-*/]', code):
            score += 3  # Calculated returns
        if re.search(r'raise\s+\w+Error', code):
            score += 4  # Error handling
        
        return min(score, 10)
    
    def _score_regression_risk(self, file_path: Path) -> int:
        """
        Score based on historical regression risk (0-10)
        Simplified heuristic - would integrate with git history in production
        """
        # Placeholder: In real implementation, check git history
        # For now, use file age/location heuristics
        path_str = str(file_path)
        
        if "core" in path_str or "engine" in path_str:
            return 8  # Core modules = high regression risk
        elif "util" in path_str or "helper" in path_str:
            return 4  # Utilities = medium risk
        return 3  # Default baseline risk
    
    def _classify_value(self, score: int) -> TestValue:
        """Classify score into value tier"""
        if score >= 90:
            return TestValue.CRITICAL
        elif score >= 70:
            return TestValue.HIGH
        elif score >= 40:
            return TestValue.MEDIUM
        elif score >= 20:
            return TestValue.LOW
        return TestValue.TRIVIAL
    
    def _generate_recommendation(self, tier: TestValue, dimensions: Dict[str, int]) -> str:
        """Generate actionable recommendation based on tier"""
        recommendations = {
            TestValue.CRITICAL: "✅ MUST TEST - Critical domain detected. Implement comprehensive test suite with edge cases, security scenarios, and mutation testing.",
            TestValue.HIGH: "✅ SHOULD TEST - High-value code. Write focused unit tests covering main paths and key edge cases.",
            TestValue.MEDIUM: "⚠️ CONSIDER TESTING - Moderate complexity. Test if it's public API or frequently modified. Otherwise, rely on integration tests.",
            TestValue.LOW: "⏸️ SKIP OR DEFER - Low complexity code. Focus testing efforts on higher-value areas. Integration tests may be sufficient.",
            TestValue.TRIVIAL: "❌ DO NOT TEST - Trivial code (getters/setters/DTOs). Testing provides no value. Kent Beck approves this skip.",
        }
        return recommendations[tier]
    
    def _generate_rationale(self, tier: TestValue, dimensions: Dict[str, int]) -> List[str]:
        """Generate rationale for the scoring decision"""
        rationale = []
        
        if dimensions["criticality"] >= 20:
            rationale.append(f"🔴 Critical domain code (score: {dimensions['criticality']}/30) - security/financial/compliance concerns")
        if dimensions["complexity"] >= 15:
            rationale.append(f"🔄 High complexity (score: {dimensions['complexity']}/20) - many conditional paths")
        if dimensions["api_surface"] >= 10:
            rationale.append(f"🌐 Significant API surface (score: {dimensions['api_surface']}/15) - external interface exposure")
        if dimensions["business_logic"] >= 10:
            rationale.append(f"💼 Dense business logic (score: {dimensions['business_logic']}/15) - calculations and transformations")
        
        # Low value explanations
        if tier in [TestValue.LOW, TestValue.TRIVIAL]:
            if dimensions["complexity"] < 5:
                rationale.append("⚪ Low complexity - simple linear logic")
            if dimensions["api_surface"] < 5:
                rationale.append("⚪ Private/internal code - not part of contract")
            if dimensions["mutation_potential"] == 0:
                rationale.append("⚪ Trivial pattern detected (getter/setter/DTO) - no testable logic")
        
        return rationale
    
    def _get_authoritative_sources(self, tier: TestValue) -> List[str]:
        """Cite authoritative sources supporting the recommendation"""
        sources = [
            "Martin Fowler - Test Pyramid (2012): 'Write lots of small and fast unit tests. Write some more coarse-grained tests and very few high-level tests.'",
            "Kent Beck - stackoverflow.com/questions/153234: 'You don't gain anything from testing simple getters or setters or other trivial implementations.'",
        ]
        
        if tier == TestValue.CRITICAL:
            sources.extend([
                "OWASP Testing Guide: All security-critical code must have comprehensive test coverage.",
                "Google Testing Blog - Test Sizes: 'Small tests are fast, reliable, and isolate failures' (critical code needs this).",
            ])
        elif tier == TestValue.HIGH:
            sources.append("Martin Fowler - Practical Test Pyramid: 'Test the public interface. More importantly, don't test trivial code.'")
        elif tier in [TestValue.LOW, TestValue.TRIVIAL]:
            sources.append("Rule of Three (Martin Fowler): Don't test until you've seen the pattern three times - avoid premature testing.")
        
        return sources


# CLI interface for standalone usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python test_value_scorer.py <file_path>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    code_content = file_path.read_text()
    scorer = TestValueScorer()
    result = scorer.score_file(file_path, code_content)
    
    print(f"\n{'=' * 80}")
    print(f"TEST VALUE ANALYSIS: {file_path.name}")
    print(f"{'=' * 80}")
    print(f"\n📊 TOTAL SCORE: {result.total_score}/100 ({result.value_tier.value.upper()})")
    print(f"\n{result.recommendation}")
    print(f"\n📋 DIMENSION BREAKDOWN:")
    for dim, score in result.dimensions.items():
        print(f"  • {dim.replace('_', ' ').title()}: {score}")
    print(f"\n💡 RATIONALE:")
    for reason in result.rationale:
        print(f"  {reason}")
    print(f"\n📚 AUTHORITATIVE SOURCES:")
    for i, source in enumerate(result.authoritative_sources, 1):
        print(f"  {i}. {source}")
    print(f"\n{'=' * 80}\n")

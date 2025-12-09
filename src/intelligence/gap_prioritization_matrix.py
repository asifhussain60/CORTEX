"""
Test Gap Prioritization Matrix

Categorizes untested/undertested code by business criticality and risk:
- P0 Critical: API endpoints, auth, financial, security (must test)
- P1 High: Business logic, validation, integration (should test)
- P2 Medium: Utilities, data access, config (nice to test)
- P3 Low: DTOs, getters/setters, trivial code (optional)

Risk scoring factors:
- Cyclomatic complexity
- Change frequency (git commits)
- Bug history
- Dependency count
- Data sensitivity

Author: Asif Hussain
Created: 2025-12-08
Phase: Dashboard Code Intelligence - Phase 2.5.3 (GREEN)
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, field
from enum import Enum
import ast


class Priority(Enum):
    """Test priority levels."""
    P0_CRITICAL = "P0 - Critical (Must Test)"
    P1_HIGH = "P1 - High (Should Test)"
    P2_MEDIUM = "P2 - Medium (Nice to Test)"
    P3_LOW = "P3 - Low (Optional)"


class CodePattern(Enum):
    """Detected code patterns indicating criticality."""
    API_ENDPOINT = "API Endpoint"
    AUTHENTICATION = "Authentication/Authorization"
    MONEY_OPERATION = "Financial/Money Operation"
    SECURITY = "Security-Sensitive"
    DATA_MUTATION = "Data Mutation (INSERT/UPDATE/DELETE)"
    PUBLIC_INTERFACE = "Public API Interface"
    BUSINESS_LOGIC = "Business Logic Service"
    UTILITY = "Utility Function"
    DTO = "Data Transfer Object"


@dataclass
class RiskFactors:
    """Risk scoring factors."""
    complexity: int = 0  # Cyclomatic complexity
    change_frequency: int = 0  # Commits in last 90 days
    bug_count: int = 0  # Bugs fixed in last 6 months
    dependency_count: int = 0  # Number of modules using this code
    data_sensitivity: bool = False  # Handles PII/financial data


@dataclass
class TestGap:
    """Represents a gap in test coverage."""
    file_path: str
    priority: Priority
    complexity: int
    loc: int
    current_coverage: float
    reason: str = ""
    risk_score: int = 0
    effort_hours: float = 0.0
    patterns: List[CodePattern] = field(default_factory=list)
    class_name: str = ""
    method_name: str = ""


class GapPrioritizer:
    """
    Prioritizes untested code by business criticality and risk.
    
    Analyzes code patterns, complexity, change history, and coverage
    to classify gaps as P0/P1/P2/P3 with effort estimates.
    """
    
    # Pattern detection regexes (compiled for performance)
    _API_PATTERNS_COMPILED = None
    
    @classmethod
    def _get_api_patterns(cls):
        """Get compiled API patterns (cached)."""
        if cls._API_PATTERNS_COMPILED is None:
            cls._API_PATTERNS_COMPILED = [
                re.compile(pattern) for pattern in [
                    r'\[HttpGet\]', r'\[HttpPost\]', r'\[HttpPut\]', r'\[HttpDelete\]',
                    r'\[Route\(', r'\[ApiController\]',
                    r'@app\.route\(', r'@router\.(get|post|put|delete)',
                    r'@RequestMapping', r'@GetMapping', r'@PostMapping',
                    r'@RestController'
                ]
            ]
        return cls._API_PATTERNS_COMPILED
    
    AUTH_KEYWORDS = [
        'authenticate', 'authorization', 'authorize', 'permission',
        'role', 'token', 'login', 'logout', 'signin', 'signout',
        'password', 'credential', 'oauth', 'jwt', 'saml'
    ]
    
    MONEY_KEYWORDS = [
        'decimal', 'money', 'currency', 'payment', 'payroll',
        'salary', 'wage', 'tax', 'fee', 'charge', 'invoice',
        'billing', 'financial', 'price', 'cost', 'revenue'
    ]
    
    SECURITY_KEYWORDS = [
        'encrypt', 'decrypt', 'hash', 'sanitize', 'validate',
        'escape', 'cipher', 'crypto', 'secure', 'certificate',
        'ssl', 'tls', 'pii', 'sensitive'
    ]
    
    def __init__(self, project_path: Path):
        """Initialize prioritizer."""
        self.project_path = Path(project_path)
        self._git_history_cache = {}
    
    def analyze_gaps(self, coverage_data: Dict) -> List[TestGap]:
        """
        Analyze coverage data and prioritize gaps.
        
        Args:
            coverage_data: Coverage baseline with file-level coverage
        
        Returns:
            List of TestGaps prioritized by P0/P1/P2/P3
        """
        gaps = []
        
        for file_info in coverage_data.get('files', []):
            file_path = file_info['file']
            coverage = file_info.get('coverage', 0.0)
            complexity = file_info.get('complexity', 1)
            loc = file_info.get('loc', 0)
            
            # Read file content for pattern detection (with caching)
            full_path = self.project_path / file_path
            code_content = ""
            if full_path.exists() and full_path.stat().st_size < 1_000_000:  # Skip huge files
                try:
                    code_content = full_path.read_text(encoding='utf-8')
                except:
                    pass
            
            # Detect patterns
            patterns = self.detect_patterns(code_content, file_path)
            
            # Calculate risk factors
            risk_factors = self._get_risk_factors(file_path, complexity)
            risk_score = self.calculate_risk_score(risk_factors)
            
            # Determine priority
            priority = self._determine_priority(
                coverage, complexity, patterns, risk_score
            )
            
            # Generate reason
            reason = self._generate_reason(patterns, coverage, complexity, risk_score)
            
            # Create gap
            gap = TestGap(
                file_path=file_path,
                priority=priority,
                complexity=complexity,
                loc=loc,
                current_coverage=coverage,
                reason=reason,
                risk_score=risk_score,
                patterns=patterns,
                class_name=self._extract_class_name(code_content, file_path),
                method_name=self._extract_method_name(code_content)
            )
            
            # Estimate effort
            gap.effort_hours = self.estimate_effort(gap)
            
            gaps.append(gap)
        
        return gaps
    
    def detect_patterns(self, code: str, file_path: str) -> List[CodePattern]:
        """
        Detect code patterns indicating criticality.
        
        Uses regex patterns and keyword matching to identify:
        - API endpoints (REST/SOAP/GraphQL attributes)
        - Authentication/authorization logic
        - Financial/money operations  
        - Security-sensitive code
        - DTOs and utility classes
        
        Args:
            code: Source code content
            file_path: Path to file
        
        Returns:
            List of detected CodePatterns
        """
        patterns = []
        code_lower = code.lower()
        
        # API Endpoint detection (compiled regex for performance)
        for pattern in self._get_api_patterns():
            if pattern.search(code):
                patterns.append(CodePattern.API_ENDPOINT)
                break
        
        # Authentication detection
        if any(keyword in code_lower for keyword in self.AUTH_KEYWORDS):
            patterns.append(CodePattern.AUTHENTICATION)
        
        # Money operation detection
        if any(keyword in code_lower for keyword in self.MONEY_KEYWORDS):
            patterns.append(CodePattern.MONEY_OPERATION)
        
        # Security detection
        if any(keyword in code_lower for keyword in self.SECURITY_KEYWORDS):
            patterns.append(CodePattern.SECURITY)
        
        # DTO detection (simple property classes)
        if self._is_dto(code, file_path):
            patterns.append(CodePattern.DTO)
        
        # Utility detection
        if 'helper' in file_path.lower() or 'util' in file_path.lower():
            patterns.append(CodePattern.UTILITY)
        
        # Business logic detection
        if 'service' in file_path.lower() and CodePattern.DTO not in patterns:
            patterns.append(CodePattern.BUSINESS_LOGIC)
        
        return patterns
    
    def calculate_risk_score(self, factors: RiskFactors) -> int:
        """
        Calculate risk score from 0-100.
        
        Args:
            factors: Risk factors
        
        Returns:
            Risk score (0-100)
        """
        score = 0
        
        # Complexity contribution (0-45 points)
        if factors.complexity > 15:
            score += 45
        elif factors.complexity > 10:
            score += 35
        elif factors.complexity > 5:
            score += 20
        else:
            score += 10
        
        # Change frequency (0-30 points)
        if factors.change_frequency > 15:
            score += 30
        elif factors.change_frequency > 10:
            score += 25
        elif factors.change_frequency > 5:
            score += 15
        else:
            score += 5
        
        # Bug history (0-30 points)
        if factors.bug_count > 5:
            score += 30
        elif factors.bug_count > 3:
            score += 25
        elif factors.bug_count > 1:
            score += 15
        else:
            score += 5
        
        # Dependencies (0-10 points)
        if factors.dependency_count > 10:
            score += 10
        elif factors.dependency_count > 5:
            score += 7
        elif factors.dependency_count > 0:
            score += 3
        
        return min(score, 100)
    
    def estimate_effort(self, gap: TestGap) -> float:
        """
        Estimate effort hours to test this gap.
        
        Args:
            gap: Test gap
        
        Returns:
            Estimated hours
        """
        base_hours = 0.0
        
        # Base effort from complexity
        if gap.complexity > 15:
            base_hours = 4.0
        elif gap.complexity > 10:
            base_hours = 3.0
        elif gap.complexity > 5:
            base_hours = 2.0
        else:
            base_hours = 1.0
        
        # Adjust for priority (P0 requires more thorough testing)
        if gap.priority == Priority.P0_CRITICAL:
            base_hours *= 1.5
        elif gap.priority == Priority.P1_HIGH:
            base_hours *= 1.2
        elif gap.priority == Priority.P3_LOW:
            base_hours *= 0.5
        
        # Adjust for LOC
        if gap.loc > 500:
            base_hours *= 1.5
        elif gap.loc > 200:
            base_hours *= 1.2
        
        return round(base_hours, 1)
    
    def generate_report(self, gaps: List[TestGap]) -> Dict:
        """
        Generate prioritization report.
        
        Args:
            gaps: List of test gaps
        
        Returns:
            JSON-serializable report
        """
        # Group by priority
        p0_gaps = [g for g in gaps if g.priority == Priority.P0_CRITICAL]
        p1_gaps = [g for g in gaps if g.priority == Priority.P1_HIGH]
        p2_gaps = [g for g in gaps if g.priority == Priority.P2_MEDIUM]
        p3_gaps = [g for g in gaps if g.priority == Priority.P3_LOW]
        
        def gap_to_dict(gap: TestGap) -> Dict:
            return {
                "file": gap.file_path,
                "class": gap.class_name,
                "method": gap.method_name,
                "reason": gap.reason,
                "complexity": gap.complexity,
                "risk_score": gap.risk_score,
                "current_coverage": gap.current_coverage,
                "effort_hours": gap.effort_hours
            }
        
        report = {
            "p0_critical": {
                "count": len(p0_gaps),
                "total_loc": sum(g.loc for g in p0_gaps),
                "estimated_hours": sum(g.effort_hours for g in p0_gaps),
                "examples": [gap_to_dict(g) for g in p0_gaps[:10]]
            },
            "p1_high": {
                "count": len(p1_gaps),
                "total_loc": sum(g.loc for g in p1_gaps),
                "estimated_hours": sum(g.effort_hours for g in p1_gaps),
                "examples": [gap_to_dict(g) for g in p1_gaps[:10]]
            },
            "p2_medium": {
                "count": len(p2_gaps),
                "total_loc": sum(g.loc for g in p2_gaps),
                "estimated_hours": sum(g.effort_hours for g in p2_gaps),
                "examples": [gap_to_dict(g) for g in p2_gaps[:5]]
            },
            "p3_low": {
                "count": len(p3_gaps),
                "total_loc": sum(g.loc for g in p3_gaps),
                "estimated_hours": sum(g.effort_hours for g in p3_gaps),
                "examples": [gap_to_dict(g) for g in p3_gaps[:5]]
            },
            "summary": {
                "total_untested_methods": len(gaps),
                "p0_percentage": round(len(p0_gaps) / len(gaps) * 100, 1) if gaps else 0.0,
                "total_effort_hours": round(sum(g.effort_hours for g in gaps), 1)
            }
        }
        
        return report
    
    def _determine_priority(
        self,
        coverage: float,
        complexity: int,
        patterns: List[CodePattern],
        risk_score: int
    ) -> Priority:
        """Determine priority from coverage, complexity, patterns, and risk."""
        # P0 Critical: High risk + critical patterns + low coverage
        if coverage < 30.0:
            critical_patterns = {
                CodePattern.API_ENDPOINT,
                CodePattern.AUTHENTICATION,
                CodePattern.MONEY_OPERATION,
                CodePattern.SECURITY
            }
            if any(p in patterns for p in critical_patterns):
                return Priority.P0_CRITICAL
            
            if risk_score > 70:
                return Priority.P0_CRITICAL
        
        # P1 High: Business logic with medium coverage or high complexity
        if coverage < 60.0:
            if CodePattern.BUSINESS_LOGIC in patterns:
                return Priority.P1_HIGH
            if complexity > 10:
                return Priority.P1_HIGH
        
        # P3 Low: DTOs, simple code, or high coverage
        if CodePattern.DTO in patterns:
            return Priority.P3_LOW
        if coverage > 80.0:
            return Priority.P3_LOW
        if complexity <= 3:
            return Priority.P3_LOW
        
        # P2 Medium: Everything else
        return Priority.P2_MEDIUM
    
    def _generate_reason(
        self,
        patterns: List[CodePattern],
        coverage: float,
        complexity: int,
        risk_score: int
    ) -> str:
        """Generate human-readable reason for prioritization."""
        reasons = []
        
        if CodePattern.API_ENDPOINT in patterns:
            reasons.append("API endpoint")
        if CodePattern.AUTHENTICATION in patterns:
            reasons.append("authentication/authorization logic")
        if CodePattern.MONEY_OPERATION in patterns:
            reasons.append("financial calculation")
        if CodePattern.SECURITY in patterns:
            reasons.append("security-sensitive code")
        if CodePattern.BUSINESS_LOGIC in patterns:
            reasons.append("business logic service")
        if CodePattern.DTO in patterns:
            reasons.append("simple data transfer object")
        
        if coverage < 10.0:
            reasons.append("no test coverage")
        elif coverage < 30.0:
            reasons.append("very low coverage")
        
        if complexity > 15:
            reasons.append("high complexity")
        
        if risk_score > 75:
            reasons.append("high risk score")
        
        if not reasons:
            return "Medium priority code requiring tests"
        
        return ", ".join(reasons).capitalize()
    
    def _get_risk_factors(self, file_path: str, complexity: int) -> RiskFactors:
        """Get risk factors for a file."""
        # For now, simplified risk factors
        # In full implementation, would query git history
        return RiskFactors(
            complexity=complexity,
            change_frequency=0,
            bug_count=0,
            dependency_count=0,
            data_sensitivity=False
        )
    
    def _is_dto(self, code: str, file_path: str) -> bool:
        """Check if code is a simple DTO/POCO."""
        # Check file name
        if any(pattern in file_path.lower() for pattern in ['dto', 'model', 'entity', 'poco']):
            # Check for mostly properties/getters
            if 'class ' in code:
                # Count property-like patterns
                property_count = len(re.findall(r'(get; set;|\{ get; set; \}|@property)', code))
                method_count = len(re.findall(r'def \w+\(|public \w+ \w+\(', code))
                
                # DTO if mostly properties
                return property_count > method_count * 2
        
        return False
    
    def _extract_class_name(self, code: str, file_path: str) -> str:
        """Extract main class name from code."""
        # Try regex first
        match = re.search(r'class\s+(\w+)', code)
        if match:
            return match.group(1)
        
        # Fallback to file name
        return Path(file_path).stem
    
    def _extract_method_name(self, code: str) -> str:
        """Extract primary method name from code."""
        # Try to find first public method
        match = re.search(r'public\s+\w+\s+(\w+)\(', code)
        if match:
            return match.group(1)
        
        # Try Python function
        match = re.search(r'def\s+(\w+)\(', code)
        if match:
            return match.group(1)
        
        return ""

"""
Intelligent Test Generator - Core orchestrator integrating all test generation components.

Combines:
- Test Value Scoring (prioritization)
- Blind Spot Detection (coverage gaps)
- Edge Case Generation (boundary values)
- Security Test Generation (OWASP)

Part of WAVE-2 Stage 5: Intelligent Test Generation.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.orchestrators.intelligence.test_value_scorer import (
    TestValueScorer,
    TestCandidate,
    IssueSeverity,
    ScenarioLikelihood,
)
from cortex.orchestrators.intelligence.blind_spot_detector import (
    BlindSpotDetector,
    CoverageData,
)
from cortex.orchestrators.intelligence.edge_case_generator import (
    EdgeCaseGenerator,
    ParameterInfo,
)
from cortex.orchestrators.intelligence.security_test_generator import (
    SecurityTestGenerator,
    EndpointInfo,
)


@dataclass
class TestGenerationRequest:
    """Request for intelligent test generation."""
    
    target_type: str  # "function", "class", "endpoint"
    target_name: str
    file_path: Path
    parameters: List[str] = field(default_factory=list)
    
    # Optional metadata
    has_database_access: bool = False
    returns_user_content: bool = False
    executes_system_commands: bool = False
    requires_authentication: bool = False
    requires_authorization: List[str] = field(default_factory=list)
    accesses_filesystem: bool = False
    
    # Coverage data
    coverage_data: Optional[Dict[str, Any]] = None
    
    # Parameter constraints
    parameter_constraints: Optional[Dict[str, Dict[str, Any]]] = None


@dataclass
class GeneratedTest:
    """A generated test case."""
    
    name: str
    source: str  # "blind_spot", "edge_case", "security", "value_scorer"
    description: str
    test_code: Optional[str] = None
    value_score: Optional[float] = None
    priority: str = "MEDIUM"  # P0-CRITICAL, P1-HIGH, P2-MEDIUM, P3-LOW


@dataclass
class TestGenerationResult:
    """Result of test generation."""
    
    request: TestGenerationRequest
    tests: List[GeneratedTest]
    total_generated: int
    high_priority_count: int
    
    def __post_init__(self):
        """Calculate counts if not provided."""
        if self.total_generated == 0:
            self.total_generated = len(self.tests)
        if self.high_priority_count == 0:
            self.high_priority_count = sum(
                1 for test in self.tests 
                if test.priority in ["P0-CRITICAL", "P1-HIGH"]
            )


class IntelligentTestGenerator:
    """
    Intelligent test generator orchestrating all test generation components.
    
    Combines multiple generation strategies:
    1. Value scoring - Prioritizes high-impact tests
    2. Blind spot detection - Finds untested code paths
    3. Edge case generation - Tests boundary conditions
    4. Security testing - OWASP vulnerability checks
    
    Args:
        min_value_score: Minimum value score threshold (default 70.0)
        coverage_threshold: Minimum coverage for blind spot detection (default 80.0)
    """
    
    def __init__(
        self,
        min_value_score: float = 70.0,
        coverage_threshold: float = 80.0,
    ) -> None:
        """Initialize IntelligentTestGenerator with all components."""
        self.min_value_score = min_value_score
        self.coverage_threshold = coverage_threshold
        
        # Initialize sub-generators
        self.value_scorer = TestValueScorer(
            severity_weight=0.4,
            likelihood_weight=0.3,
            coverage_gap_weight=0.3
        )
        self.blind_spot_detector = BlindSpotDetector(
            min_coverage_threshold=coverage_threshold
        )
        self.edge_case_generator = EdgeCaseGenerator()
        self.security_test_generator = SecurityTestGenerator()
    
    def generate_tests(self, request: TestGenerationRequest) -> TestGenerationResult:
        """
        Generate comprehensive test suite for target.
        
        Combines all generation strategies and prioritizes by value score.
        
        Args:
            request: Test generation request
            
        Returns:
            TestGenerationResult with prioritized tests
        """
        all_tests = []
        
        # 1. Generate blind spot tests (if coverage data provided)
        if request.coverage_data:
            blind_spot_tests = self._generate_blind_spot_tests(request)
            all_tests.extend(blind_spot_tests)
        
        # 2. Generate edge case tests
        edge_case_tests = self._generate_edge_case_tests(request)
        all_tests.extend(edge_case_tests)
        
        # 3. Generate security tests (if applicable)
        if request.target_type == "endpoint":
            security_tests = self._generate_security_tests(request)
            all_tests.extend(security_tests)
        
        # 4. Score and filter by value
        prioritized_tests = self._prioritize_tests(all_tests, request)
        filtered_tests = self._filter_by_value_score(prioritized_tests)
        
        # 5. Build result
        result = TestGenerationResult(
            request=request,
            tests=filtered_tests,
            total_generated=len(filtered_tests),
            high_priority_count=sum(
                1 for test in filtered_tests 
                if test.priority in ["P0-CRITICAL", "P1-HIGH"]
            )
        )
        
        return result
    
    def _generate_blind_spot_tests(
        self, 
        request: TestGenerationRequest
    ) -> List[GeneratedTest]:
        """Generate tests for blind spots in coverage."""
        tests = []
        
        # Convert coverage data to CoverageData object
        coverage = CoverageData(
            file_path=request.file_path,
            covered_lines=set(request.coverage_data.get("covered_lines", [])),
            missing_lines=set(request.coverage_data.get("missing_lines", [])),
            branch_coverage=request.coverage_data.get("branch_coverage", 0.0),
        )
        
        # Detect blind spots
        file_content = ""  # Would read from file in production
        blind_spots = self.blind_spot_detector.analyze_file(coverage, file_content)
        
        # Convert to GeneratedTest
        for blind_spot in blind_spots:
            tests.append(GeneratedTest(
                name=f"test_{request.target_name}_{blind_spot.type.value}_{blind_spot.line_number}",
                source="blind_spot",
                description=blind_spot.description,
                priority="P1-HIGH" if blind_spot.severity == "HIGH" else "P2-MEDIUM",
            ))
        
        return tests
    
    def _generate_edge_case_tests(
        self, 
        request: TestGenerationRequest
    ) -> List[GeneratedTest]:
        """Generate edge case tests for parameters."""
        tests = []
        
        # Generate for each parameter
        for param_name in request.parameters:
            # Get constraints if provided, otherwise use defaults
            constraints = {}
            if request.parameter_constraints:
                constraints = request.parameter_constraints.get(param_name, {})
            
            # Provide default constraints if none specified
            if not constraints:
                constraints = {"type_hint": "str", "nullable": True}
            
            # Create ParameterInfo
            param_info = ParameterInfo(
                name=param_name,
                type_hint=constraints.get("type_hint", "str"),
                nullable=constraints.get("nullable", True),
                min_value=constraints.get("min_value"),
                max_value=constraints.get("max_value"),
                min_length=constraints.get("min_length"),
                max_length=constraints.get("max_length"),
            )
            
            # Generate edge cases
            edge_cases = self.edge_case_generator.generate_for_parameter(param_info)
            
            # Convert to GeneratedTest
            for edge_case in edge_cases:
                tests.append(GeneratedTest(
                    name=f"test_{request.target_name}_{param_name}_{edge_case.type.value}",
                    source="edge_case",
                    description=edge_case.description,
                    priority="P2-MEDIUM",
                ))
        
        return tests
    
    def _generate_security_tests(
        self, 
        request: TestGenerationRequest
    ) -> List[GeneratedTest]:
        """Generate security tests for endpoints."""
        tests = []
        
        # Create EndpointInfo
        endpoint = EndpointInfo(
            path=request.target_name,
            method="GET",  # Would be detected from code
            parameters=request.parameters,
            has_database_access=request.has_database_access,
            returns_user_content=request.returns_user_content,
            executes_system_commands=request.executes_system_commands,
            requires_authentication=request.requires_authentication,
            requires_authorization=request.requires_authorization,
            accesses_filesystem=request.accesses_filesystem,
        )
        
        # Generate security tests
        security_tests = self.security_test_generator.generate_for_endpoint(endpoint)
        
        # Convert to GeneratedTest
        for sec_test in security_tests:
            priority = "P0-CRITICAL" if sec_test.vulnerability_class.value == "critical" else "P1-HIGH"
            
            tests.append(GeneratedTest(
                name=f"test_{request.target_name.replace('/', '_')}_security_{sec_test.type.value}",
                source="security",
                description=sec_test.description,
                priority=priority,
            ))
        
        return tests
    
    def _prioritize_tests(
        self, 
        tests: List[GeneratedTest],
        request: TestGenerationRequest
    ) -> List[GeneratedTest]:
        """Prioritize tests by value score."""
        scored_tests = []
        
        for test in tests:
            # Calculate value score
            candidate = self._test_to_candidate(test, request)
            score = self.value_scorer.calculate_score(candidate)
            
            # Assign score and priority
            test.value_score = score.total
            
            if score.total >= 90:
                test.priority = "P0-CRITICAL"
            elif score.total >= 75:
                test.priority = "P1-HIGH"
            elif score.total >= 60:
                test.priority = "P2-MEDIUM"
            else:
                test.priority = "P3-LOW"
            
            scored_tests.append(test)
        
        # Sort by value score (descending)
        scored_tests.sort(key=lambda t: t.value_score or 0, reverse=True)
        
        return scored_tests
    
    def _test_to_candidate(
        self, 
        test: GeneratedTest,
        request: TestGenerationRequest
    ) -> TestCandidate:
        """Convert GeneratedTest to TestCandidate for scoring."""
        # Determine severity based on source and description
        severity = IssueSeverity.MEDIUM
        
        if "security" in test.source or "injection" in test.description.lower():
            severity = IssueSeverity.CRITICAL
        elif "blind_spot" in test.source or "error" in test.description.lower():
            severity = IssueSeverity.HIGH
        elif "edge_case" in test.source or "boundary" in test.description.lower():
            severity = IssueSeverity.MEDIUM
        
        # Determine likelihood
        likelihood = ScenarioLikelihood.MEDIUM
        
        if request.has_database_access or request.requires_authentication:
            likelihood = ScenarioLikelihood.HIGH
        
        # Coverage gap (simplified)
        coverage_gap = 50.0  # Default
        if request.coverage_data:
            branch_cov = request.coverage_data.get("branch_coverage", 0.0)
            coverage_gap = (1.0 - branch_cov) * 100
        
        return TestCandidate(
            name=test.name,
            description=test.description,
            issue_type=test.source,
            target_function=request.target_name,
            target_file=str(request.file_path),
            severity=severity,
            likelihood=likelihood,
            coverage_gap=coverage_gap,
        )
    
    def _filter_by_value_score(
        self, 
        tests: List[GeneratedTest]
    ) -> List[GeneratedTest]:
        """Filter tests by minimum value score threshold."""
        return [
            test for test in tests 
            if test.value_score and test.value_score >= self.min_value_score
        ]

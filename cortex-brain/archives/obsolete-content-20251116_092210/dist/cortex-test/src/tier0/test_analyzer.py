"""
CORTEX Test Analyzer
=====================

Analyzes test suite for redundancy, coverage gaps, and optimization opportunities.

**Purpose:**
- Detect duplicate/redundant test cases
- Identify missing test scenarios
- Analyze test complexity and maintainability
- Generate actionable recommendations

**Integration:**
- Part of Tier 0 (Governance)
- Used by brain protector for test quality validation
- Supports SKULL protection enforcement

**Author:** Asif Hussain
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
**License:** Proprietary
"""

import ast
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from enum import Enum


class TestComplexity(Enum):
    """Test complexity classification."""
    TRIVIAL = "trivial"       # < 5 lines, simple assertion
    SIMPLE = "simple"         # 5-15 lines, single concept
    MODERATE = "moderate"     # 15-30 lines, multiple assertions
    COMPLEX = "complex"       # 30-50 lines, setup/teardown
    VERY_COMPLEX = "very_complex"  # > 50 lines, may need refactor


class RedundancyType(Enum):
    """Types of test redundancy."""
    EXACT_DUPLICATE = "exact_duplicate"           # Identical test bodies
    SEMANTIC_DUPLICATE = "semantic_duplicate"     # Same logic, different names
    OVERLAPPING_COVERAGE = "overlapping_coverage" # Tests same functionality
    FIXTURE_REDUNDANCY = "fixture_redundancy"     # Duplicate fixture setup
    ASSERTION_REDUNDANCY = "assertion_redundancy" # Redundant assertions


@dataclass
class TestCase:
    """Represents a single test case."""
    name: str
    file_path: Path
    class_name: Optional[str]
    line_number: int
    end_line_number: int
    body_hash: str
    assertions: List[str] = field(default_factory=list)
    fixtures_used: List[str] = field(default_factory=list)
    mocks_used: List[str] = field(default_factory=list)
    complexity: TestComplexity = TestComplexity.SIMPLE
    docstring: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    
    @property
    def line_count(self) -> int:
        """Get number of lines in test."""
        return self.end_line_number - self.line_number + 1
    
    @property
    def full_name(self) -> str:
        """Get fully qualified test name."""
        if self.class_name:
            return f"{self.class_name}.{self.name}"
        return self.name


@dataclass
class RedundancyIssue:
    """Represents a detected redundancy."""
    redundancy_type: RedundancyType
    severity: str  # "high", "medium", "low"
    test_cases: List[TestCase]
    description: str
    recommendation: str
    similarity_score: float = 0.0


@dataclass
class TestFileAnalysis:
    """Analysis results for a single test file."""
    file_path: Path
    test_count: int
    class_count: int
    fixture_count: int
    total_lines: int
    test_cases: List[TestCase] = field(default_factory=list)
    fixtures: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    coverage_score: float = 0.0


@dataclass
class TestSuiteAnalysis:
    """Complete test suite analysis."""
    total_tests: int
    total_files: int
    total_lines: int
    file_analyses: Dict[Path, TestFileAnalysis] = field(default_factory=dict)
    redundancies: List[RedundancyIssue] = field(default_factory=list)
    complexity_distribution: Dict[TestComplexity, int] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class TestAnalyzer:
    """
    Analyzes test suite for quality, redundancy, and optimization opportunities.
    
    **Features:**
    - AST-based test parsing
    - Redundancy detection (exact, semantic, coverage overlap)
    - Complexity analysis
    - Fixture usage tracking
    - Coverage gap identification
    - Actionable recommendations
    """
    
    def __init__(self, project_root: Path, test_dir: Path = None):
        """
        Initialize test analyzer.
        
        Args:
            project_root: Root directory of project
            test_dir: Test directory (defaults to project_root/tests)
        """
        self.project_root = Path(project_root)
        self.test_dir = Path(test_dir) if test_dir else self.project_root / "tests"
        
        # Analysis caches
        self._test_cases: Dict[str, TestCase] = {}
        self._file_analyses: Dict[Path, TestFileAnalysis] = {}
        self._body_hashes: Dict[str, List[TestCase]] = defaultdict(list)
        self._assertion_patterns: Dict[str, List[TestCase]] = defaultdict(list)
        
    def analyze_suite(self, verbose: bool = False) -> TestSuiteAnalysis:
        """
        Perform complete test suite analysis.
        
        Args:
            verbose: Print progress information
            
        Returns:
            TestSuiteAnalysis with complete results
        """
        if verbose:
            print(f"🔍 Analyzing test suite in: {self.test_dir}")
        
        # Discover and parse all test files
        test_files = list(self.test_dir.rglob("test_*.py"))
        if verbose:
            print(f"📂 Found {len(test_files)} test files")
        
        for test_file in test_files:
            if verbose:
                print(f"  Parsing: {test_file.relative_to(self.project_root)}")
            self._analyze_file(test_file)
        
        # Detect redundancies
        if verbose:
            print("\n🔎 Detecting redundancies...")
        redundancies = self._detect_redundancies()
        
        # Calculate complexity distribution
        complexity_dist = self._calculate_complexity_distribution()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(redundancies, complexity_dist)
        
        # Build final analysis
        analysis = TestSuiteAnalysis(
            total_tests=len(self._test_cases),
            total_files=len(self._file_analyses),
            total_lines=sum(fa.total_lines for fa in self._file_analyses.values()),
            file_analyses=self._file_analyses,
            redundancies=redundancies,
            complexity_distribution=complexity_dist,
            recommendations=recommendations
        )
        
        if verbose:
            print(f"\n✅ Analysis complete:")
            print(f"   Tests: {analysis.total_tests}")
            print(f"   Files: {analysis.total_files}")
            print(f"   Redundancies: {len(redundancies)}")
        
        return analysis
    
    
    def _is_fixture(self, node: ast.FunctionDef) -> bool:
        """Check if function node is a pytest fixture."""
        for decorator in node.decorator_list:
            # Check for @pytest.fixture
            if isinstance(decorator, ast.Attribute):
                if hasattr(decorator.value, 'id') and decorator.value.id == 'pytest':
                    if decorator.attr == 'fixture':
                        return True
            # Check for @fixture (if imported directly)
            elif isinstance(decorator, ast.Name):
                if decorator.id == 'fixture':
                    return True
            # Check for @pytest.fixture(...) with call
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    if hasattr(decorator.func.value, 'id') and decorator.func.value.id == 'pytest':
                        if decorator.func.attr == 'fixture':
                            return True
                elif isinstance(decorator.func, ast.Name):
                    if decorator.func.id == 'fixture':
                        return True
        return False
    
    def _analyze_file(self, file_path: Path) -> TestFileAnalysis:
        """Parse and analyze a single test file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content, filename=str(file_path))
            
            test_cases = []
            fixtures = []
            imports = []
            class_count = 0
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.extend(self._extract_import_names(node))
            
            # Extract test cases and fixtures (process top-level only, not nested)
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    if node.name.startswith("Test"):
                        class_count += 1
                        # Extract test methods from class
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                if item.name.startswith("test_"):
                                    test_case = self._parse_test_case(item, file_path, node.name)
                                    test_cases.append(test_case)
                                    self._test_cases[test_case.full_name] = test_case
                                    self._body_hashes[test_case.body_hash].append(test_case)
                
                elif isinstance(node, ast.FunctionDef):
                    # Top-level test functions or fixtures
                    if node.name.startswith("test_"):
                        test_case = self._parse_test_case(node, file_path, None)
                        test_cases.append(test_case)
                        self._test_cases[test_case.full_name] = test_case
                        self._body_hashes[test_case.body_hash].append(test_case)
                    elif self._is_fixture(node):
                        fixtures.append(node.name)
            
            # Create file analysis
            analysis = TestFileAnalysis(
                file_path=file_path,
                test_count=len(test_cases),
                class_count=class_count,
                fixture_count=len(fixtures),
                total_lines=len(content.split('\n')),
                test_cases=test_cases,
                fixtures=fixtures,
                imports=imports
            )
            
            self._file_analyses[file_path] = analysis
            return analysis
            
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
            return TestFileAnalysis(
                file_path=file_path,
                test_count=0,
                class_count=0,
                fixture_count=0,
                total_lines=0
            )
    
    def _parse_test_case(self, node: ast.FunctionDef, file_path: Path, 
                        class_name: Optional[str]) -> TestCase:
        """Parse AST node into TestCase object."""
        # Get docstring
        docstring = ast.get_docstring(node)
        
        # Extract assertions
        assertions = []
        mocks = []
        fixtures = []
        dependencies = []
        
        for item in ast.walk(node):
            # Find assertions
            if isinstance(item, ast.Assert):
                assertions.append(ast.unparse(item.test))
            elif isinstance(item, ast.Call):
                if isinstance(item.func, ast.Attribute):
                    if item.func.attr.startswith("assert"):
                        assertions.append(ast.unparse(item))
                    elif "mock" in item.func.attr.lower() or "patch" in item.func.attr.lower():
                        mocks.append(ast.unparse(item))
        
        # Extract fixtures from function arguments
        for arg in node.args.args:
            if arg.arg not in ['self', 'cls']:
                fixtures.append(arg.arg)
        
        # Calculate body hash (for duplicate detection)
        body_source = ast.unparse(node)
        # Normalize: remove whitespace, docstrings for semantic comparison
        normalized = ''.join(body_source.split()).replace(docstring or '', '')
        body_hash = hashlib.md5(normalized.encode()).hexdigest()
        
        # Determine complexity
        line_count = node.end_lineno - node.lineno + 1
        complexity = self._classify_complexity(line_count, len(assertions), len(mocks))
        
        return TestCase(
            name=node.name,
            file_path=file_path,
            class_name=class_name,
            line_number=node.lineno,
            end_line_number=node.end_lineno,
            body_hash=body_hash,
            assertions=assertions,
            fixtures_used=fixtures,
            mocks_used=mocks,
            complexity=complexity,
            docstring=docstring,
            dependencies=dependencies
        )
    
    def _classify_complexity(self, line_count: int, assertion_count: int, 
                           mock_count: int) -> TestComplexity:
        """Classify test complexity based on metrics."""
        # Weight different factors
        complexity_score = (
            line_count * 1.0 +
            assertion_count * 2.0 +
            mock_count * 3.0
        )
        
        if complexity_score < 10:
            return TestComplexity.TRIVIAL
        elif complexity_score < 25:
            return TestComplexity.SIMPLE
        elif complexity_score < 50:
            return TestComplexity.MODERATE
        elif complexity_score < 80:
            return TestComplexity.COMPLEX
        else:
            return TestComplexity.VERY_COMPLEX
    
    def _extract_import_names(self, node: ast.AST) -> List[str]:
        """Extract import module names from import node."""
        imports = []
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
        return imports
    
    def _detect_redundancies(self) -> List[RedundancyIssue]:
        """Detect various types of redundancy in test suite."""
        redundancies = []
        
        # 1. Exact duplicates (same body hash)
        for body_hash, test_list in self._body_hashes.items():
            if len(test_list) > 1:
                redundancies.append(RedundancyIssue(
                    redundancy_type=RedundancyType.EXACT_DUPLICATE,
                    severity="high",
                    test_cases=test_list,
                    description=f"Found {len(test_list)} tests with identical implementation",
                    recommendation="Remove duplicate tests or consolidate into parameterized test",
                    similarity_score=1.0
                ))
        
        # 2. Semantic duplicates (similar assertion patterns)
        redundancies.extend(self._detect_semantic_duplicates())
        
        # 3. Overlapping coverage (tests testing same functionality differently)
        redundancies.extend(self._detect_overlapping_coverage())
        
        # 4. Fixture redundancy
        redundancies.extend(self._detect_fixture_redundancy())
        
        return redundancies
    
    def _detect_semantic_duplicates(self) -> List[RedundancyIssue]:
        """Detect tests with similar logic but different names."""
        issues = []
        
        # Group tests by assertion patterns
        assertion_groups = defaultdict(list)
        for test in self._test_cases.values():
            # Create signature from assertions
            assertion_sig = "|".join(sorted(test.assertions))
            if assertion_sig:  # Only consider tests with assertions
                assertion_groups[assertion_sig].append(test)
        
        # Find groups with multiple tests
        for assertion_sig, tests in assertion_groups.items():
            if len(tests) > 1:
                # Calculate similarity (Jaccard index on assertion tokens)
                similarity = self._calculate_similarity(tests)
                if similarity > 0.7:  # High similarity threshold
                    issues.append(RedundancyIssue(
                        redundancy_type=RedundancyType.SEMANTIC_DUPLICATE,
                        severity="medium",
                        test_cases=tests,
                        description=f"Found {len(tests)} tests with nearly identical assertion patterns",
                        recommendation="Review tests for consolidation or parameterization",
                        similarity_score=similarity
                    ))
        
        return issues
    
    def _detect_overlapping_coverage(self) -> List[RedundancyIssue]:
        """Detect tests that may be testing the same functionality."""
        issues = []
        
        # Group tests by fixture usage (tests using same fixtures likely test same area)
        fixture_groups = defaultdict(list)
        for test in self._test_cases.values():
            fixture_key = tuple(sorted(test.fixtures_used))
            if fixture_key:
                fixture_groups[fixture_key].append(test)
        
        # Analyze groups for potential overlap
        for fixture_key, tests in fixture_groups.items():
            if len(tests) > 5:  # Threshold for "too many tests on same fixtures"
                # Check if tests are in same file and class
                by_location = defaultdict(list)
                for test in tests:
                    location = (test.file_path, test.class_name)
                    by_location[location].append(test)
                
                for location, location_tests in by_location.items():
                    if len(location_tests) > 3:
                        issues.append(RedundancyIssue(
                            redundancy_type=RedundancyType.OVERLAPPING_COVERAGE,
                            severity="low",
                            test_cases=location_tests,
                            description=f"Found {len(location_tests)} tests using same fixtures in same location",
                            recommendation="Review if tests can be consolidated or if coverage is truly distinct",
                            similarity_score=0.5
                        ))
        
        return issues
    
    def _detect_fixture_redundancy(self) -> List[RedundancyIssue]:
        """Detect redundant fixture definitions across files."""
        issues = []
        
        # Group fixtures by name
        fixture_by_name = defaultdict(list)
        for file_path, analysis in self._file_analyses.items():
            for fixture in analysis.fixtures:
                fixture_by_name[fixture].append(file_path)
        
        # Find fixtures defined in multiple files
        for fixture_name, file_list in fixture_by_name.items():
            if len(file_list) > 1:
                # This might be intentional (conftest.py pattern) or redundant
                if not any("conftest" in str(f) for f in file_list):
                    issues.append(RedundancyIssue(
                        redundancy_type=RedundancyType.FIXTURE_REDUNDANCY,
                        severity="low",
                        test_cases=[],  # No specific test cases, applies to files
                        description=f"Fixture '{fixture_name}' defined in {len(file_list)} files",
                        recommendation=f"Consider moving to conftest.py: {[str(f.relative_to(self.project_root)) for f in file_list]}",
                        similarity_score=1.0
                    ))
        
        return issues
    
    def _calculate_similarity(self, tests: List[TestCase]) -> float:
        """Calculate average similarity score between tests."""
        if len(tests) < 2:
            return 0.0
        
        total_similarity = 0.0
        comparisons = 0
        
        for i, test1 in enumerate(tests):
            for test2 in tests[i+1:]:
                # Jaccard similarity on assertion tokens
                tokens1 = set(' '.join(test1.assertions).split())
                tokens2 = set(' '.join(test2.assertions).split())
                
                if tokens1 or tokens2:
                    intersection = len(tokens1 & tokens2)
                    union = len(tokens1 | tokens2)
                    similarity = intersection / union if union > 0 else 0.0
                    total_similarity += similarity
                    comparisons += 1
        
        return total_similarity / comparisons if comparisons > 0 else 0.0
    
    def _calculate_complexity_distribution(self) -> Dict[TestComplexity, int]:
        """Calculate distribution of test complexities."""
        distribution = {complexity: 0 for complexity in TestComplexity}
        for test in self._test_cases.values():
            distribution[test.complexity] += 1
        return distribution
    
    def _generate_recommendations(self, redundancies: List[RedundancyIssue],
                                 complexity_dist: Dict[TestComplexity, int]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Redundancy recommendations
        high_severity = [r for r in redundancies if r.severity == "high"]
        if high_severity:
            recommendations.append(
                f"🔴 HIGH PRIORITY: Found {len(high_severity)} exact duplicate tests. "
                "Remove duplicates immediately to reduce maintenance burden."
            )
        
        medium_severity = [r for r in redundancies if r.severity == "medium"]
        if medium_severity:
            recommendations.append(
                f"🟡 MEDIUM PRIORITY: Found {len(medium_severity)} semantically similar tests. "
                "Consider consolidating using @pytest.mark.parametrize."
            )
        
        # Complexity recommendations
        very_complex = complexity_dist.get(TestComplexity.VERY_COMPLEX, 0)
        if very_complex > 0:
            recommendations.append(
                f"🟡 Found {very_complex} very complex tests (>50 lines). "
                "Consider refactoring into smaller, focused tests."
            )
        
        complex_tests = complexity_dist.get(TestComplexity.COMPLEX, 0)
        if complex_tests > len(self._test_cases) * 0.3:  # > 30% complex
            recommendations.append(
                f"⚠️  {complex_tests}/{len(self._test_cases)} tests are complex. "
                "Review test design for simplification opportunities."
            )
        
        # Coverage recommendations
        total_tests = len(self._test_cases)
        if total_tests < 50:
            recommendations.append(
                f"ℹ️  Test suite is relatively small ({total_tests} tests). "
                "Consider expanding coverage for critical paths."
            )
        
        return recommendations
    
    def generate_report(self, analysis: TestSuiteAnalysis, output_path: Path = None) -> str:
        """
        Generate human-readable analysis report.
        
        Args:
            analysis: TestSuiteAnalysis to report on
            output_path: Optional file path to write report
            
        Returns:
            Report as string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("CORTEX Test Suite Analysis Report")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        lines.append("📊 SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total Tests:        {analysis.total_tests}")
        lines.append(f"Total Files:        {analysis.total_files}")
        lines.append(f"Total Lines:        {analysis.total_lines:,}")
        lines.append(f"Redundancies Found: {len(analysis.redundancies)}")
        lines.append("")
        
        # Complexity Distribution
        lines.append("📈 COMPLEXITY DISTRIBUTION")
        lines.append("-" * 80)
        for complexity, count in sorted(analysis.complexity_distribution.items(), 
                                       key=lambda x: list(TestComplexity).index(x[0])):
            percentage = (count / analysis.total_tests * 100) if analysis.total_tests > 0 else 0
            bar = "█" * int(percentage / 2)
            lines.append(f"{complexity.value:15s} {count:4d} ({percentage:5.1f}%) {bar}")
        lines.append("")
        
        # Redundancies
        if analysis.redundancies:
            lines.append("🔍 REDUNDANCIES DETECTED")
            lines.append("-" * 80)
            
            # Group by severity
            for severity in ["high", "medium", "low"]:
                severity_issues = [r for r in analysis.redundancies if r.severity == severity]
                if severity_issues:
                    lines.append(f"\n{severity.upper()} Severity ({len(severity_issues)} issues):")
                    for issue in severity_issues:
                        lines.append(f"\n  • {issue.redundancy_type.value}")
                        lines.append(f"    {issue.description}")
                        lines.append(f"    Similarity: {issue.similarity_score:.2%}")
                        if issue.test_cases:
                            lines.append(f"    Affected tests:")
                            for test in issue.test_cases[:5]:  # Limit display
                                lines.append(f"      - {test.full_name} ({test.file_path.name}:{test.line_number})")
                            if len(issue.test_cases) > 5:
                                lines.append(f"      ... and {len(issue.test_cases) - 5} more")
                        lines.append(f"    💡 Recommendation: {issue.recommendation}")
        lines.append("")
        
        # Recommendations
        if analysis.recommendations:
            lines.append("💡 RECOMMENDATIONS")
            lines.append("-" * 80)
            for i, rec in enumerate(analysis.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        lines.append("=" * 80)
        lines.append("End of Report")
        lines.append("=" * 80)
        
        report = "\n".join(lines)
        
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Report written to: {output_path}")
        
        return report
    
    def export_json(self, analysis: TestSuiteAnalysis, output_path: Path):
        """Export analysis as JSON for programmatic processing."""
        data = {
            "summary": {
                "total_tests": analysis.total_tests,
                "total_files": analysis.total_files,
                "total_lines": analysis.total_lines,
                "redundancy_count": len(analysis.redundancies)
            },
            "complexity_distribution": {
                k.value: v for k, v in analysis.complexity_distribution.items()
            },
            "redundancies": [
                {
                    "type": r.redundancy_type.value,
                    "severity": r.severity,
                    "description": r.description,
                    "recommendation": r.recommendation,
                    "similarity_score": r.similarity_score,
                    "test_count": len(r.test_cases),
                    "tests": [t.full_name for t in r.test_cases]
                }
                for r in analysis.redundancies
            ],
            "recommendations": analysis.recommendations
        }
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"💾 JSON export written to: {output_path}")


def main():
    """CLI entry point for test analyzer."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Test Suite Analyzer - Detect redundancy and optimize tests"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory"
    )
    parser.add_argument(
        "--test-dir",
        type=Path,
        help="Test directory (default: project_root/tests)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output report file path"
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Export results as JSON"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = TestAnalyzer(
        project_root=args.project_root,
        test_dir=args.test_dir
    )
    
    # Run analysis
    print("\n" + "=" * 80)
    print("CORTEX Test Analyzer")
    print("=" * 80 + "\n")
    
    analysis = analyzer.analyze_suite(verbose=args.verbose)
    
    # Generate report
    report = analyzer.generate_report(analysis, output_path=args.output)
    
    if not args.output:
        print("\n" + report)
    
    # Export JSON if requested
    if args.json:
        analyzer.export_json(analysis, args.json)
    
    print("\n✅ Analysis complete!")
    
    # Exit with error code if high-severity issues found
    high_severity = [r for r in analysis.redundancies if r.severity == "high"]
    if high_severity:
        print(f"\n⚠️  WARNING: {len(high_severity)} high-severity issues detected!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

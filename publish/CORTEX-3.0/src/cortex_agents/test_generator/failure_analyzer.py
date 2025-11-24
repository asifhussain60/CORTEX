"""
Test Failure Analyzer - Phase 5.2: Failure Analysis & Improvement

Parses pytest output, identifies failure categories, detects recurring patterns,
and improves test generation templates based on learnings.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import re
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from collections import defaultdict


class FailureCategory(Enum):
    """Categories of test failures"""
    ASSERTION_ERROR = "assertion_error"  # Expected vs actual mismatch
    EXCEPTION = "exception"  # Unexpected exception raised
    TIMEOUT = "timeout"  # Test exceeded time limit
    IMPORT_ERROR = "import_error"  # Module import failed
    FIXTURE_ERROR = "fixture_error"  # Fixture setup/teardown failed
    COLLECTION_ERROR = "collection_error"  # Test collection failed
    SETUP_ERROR = "setup_error"  # Test setup failed
    TEARDOWN_ERROR = "teardown_error"  # Test teardown failed
    SKIP = "skip"  # Test skipped (not a failure, but tracked)
    XFAIL = "xfail"  # Expected failure
    UNKNOWN = "unknown"  # Unable to categorize


class FailureSeverity(Enum):
    """Severity levels for failures"""
    CRITICAL = "critical"  # Blocking issue, high priority
    HIGH = "high"  # Significant issue, needs attention
    MEDIUM = "medium"  # Moderate issue
    LOW = "low"  # Minor issue


@dataclass
class TestFailure:
    """Represents a single test failure"""
    test_name: str
    test_file: str
    category: FailureCategory
    severity: FailureSeverity
    error_message: str
    stack_trace: Optional[str] = None
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    line_number: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    failure_hash: Optional[str] = None  # For deduplication
    
    def __post_init__(self):
        """Generate failure hash for deduplication"""
        if self.failure_hash is None:
            # Hash based on test name, category, and simplified error message
            simplified_error = re.sub(r'\d+', 'N', self.error_message[:100])
            self.failure_hash = f"{self.test_name}_{self.category.value}_{hash(simplified_error)}"


@dataclass
class FailurePattern:
    """Represents a recurring failure pattern"""
    pattern_id: str
    category: FailureCategory
    description: str
    occurrences: int = 0
    affected_tests: List[str] = field(default_factory=list)
    first_seen: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    confidence: float = 0.0  # How confident we are this is a real pattern
    fix_suggestions: List[str] = field(default_factory=list)
    template_updates: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class FailureAnalysisReport:
    """Complete failure analysis report"""
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration_seconds: float
    failures: List[TestFailure]
    patterns: List[FailurePattern]
    category_distribution: Dict[str, int]
    severity_distribution: Dict[str, int]
    recommendations: List[str]
    analyzed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class FailureAnalyzer:
    """
    Analyzes test failures to improve test generation.
    
    Responsibilities:
    1. Parse pytest output
    2. Categorize failures
    3. Detect recurring patterns
    4. Generate improvement suggestions
    5. Update test templates based on learnings
    """
    
    def __init__(self, tier2_kg: Any = None, pattern_store: Any = None):
        """
        Initialize failure analyzer.
        
        Args:
            tier2_kg: Tier 2 Knowledge Graph for pattern storage
            pattern_store: Pattern store API for CRUD operations
        """
        self.tier2_kg = tier2_kg
        self.pattern_store = pattern_store
        self.failure_history: Dict[str, List[TestFailure]] = defaultdict(list)
        self.pattern_cache: Dict[str, FailurePattern] = {}
        
    def parse_pytest_output(self, output: str, duration: float = 0.0) -> FailureAnalysisReport:
        """
        Parse pytest output and generate analysis report.
        
        Args:
            output: Raw pytest output text
            duration: Test execution duration in seconds
            
        Returns:
            FailureAnalysisReport with categorized failures and patterns
        """
        # Extract test counts from summary
        counts = self._parse_test_counts(output)
        
        # Extract individual failures
        failures = self._extract_failures(output)
        
        # Detect recurring patterns
        patterns = self._detect_patterns(failures)
        
        # Generate category and severity distributions
        category_dist = self._calculate_category_distribution(failures)
        severity_dist = self._calculate_severity_distribution(failures)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(failures, patterns)
        
        return FailureAnalysisReport(
            total_tests=counts['total'],
            passed=counts['passed'],
            failed=counts['failed'],
            skipped=counts['skipped'],
            errors=counts['errors'],
            duration_seconds=duration,
            failures=failures,
            patterns=patterns,
            category_distribution=category_dist,
            severity_distribution=severity_dist,
            recommendations=recommendations
        )
    
    def _parse_test_counts(self, output: str) -> Dict[str, int]:
        """
        Extract test counts from pytest summary.
        
        Args:
            output: pytest output text
            
        Returns:
            Dictionary with passed, failed, skipped, errors counts
        """
        counts = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0, "total": 0}
        
        # Look for pytest summary line like:
        # "10 passed, 2 failed, 1 skipped in 5.23s"
        summary_pattern = r'(\d+)\s+passed|(\d+)\s+failed|(\d+)\s+skipped|(\d+)\s+error'
        
        for match in re.finditer(summary_pattern, output, re.IGNORECASE):
            if match.group(1):  # passed
                counts["passed"] = int(match.group(1))
            elif match.group(2):  # failed
                counts["failed"] = int(match.group(2))
            elif match.group(3):  # skipped
                counts["skipped"] = int(match.group(3))
            elif match.group(4):  # errors
                counts["errors"] = int(match.group(4))
        
        # If no summary found, count markers
        if counts["passed"] == 0 and counts["failed"] == 0:
            counts["passed"] = output.count(" PASSED")
            counts["failed"] = output.count(" FAILED")
            counts["skipped"] = output.count(" SKIPPED")
            counts["errors"] = output.count(" ERROR")
        
        counts["total"] = counts["passed"] + counts["failed"] + counts["skipped"]
        
        return counts
    
    def _extract_failures(self, output: str) -> List[TestFailure]:
        """
        Extract individual test failures from pytest output.
        
        Args:
            output: pytest output text
            
        Returns:
            List of TestFailure objects
        """
        failures = []
        
        # Pattern to match test failures in pytest output
        # Example: "tests/test_auth.py::test_login FAILED"
        failure_pattern = r'([\w/\\]+\.py)::([\w:]+)\s+(FAILED|ERROR)'
        
        for match in re.finditer(failure_pattern, output):
            test_file = match.group(1)
            test_name = match.group(2)
            status = match.group(3)
            
            # Extract error details from the failure section
            error_details = self._extract_error_details(output, test_file, test_name)
            
            failure = TestFailure(
                test_name=test_name,
                test_file=test_file,
                category=error_details['category'],
                severity=error_details['severity'],
                error_message=error_details['error_message'],
                stack_trace=error_details.get('stack_trace'),
                expected_value=error_details.get('expected_value'),
                actual_value=error_details.get('actual_value'),
                line_number=error_details.get('line_number')
            )
            
            failures.append(failure)
        
        return failures
    
    def _extract_error_details(self, output: str, test_file: str, test_name: str) -> Dict[str, Any]:
        """
        Extract detailed error information for a specific test failure.
        
        Args:
            output: pytest output text
            test_file: Test file path
            test_name: Test function name
            
        Returns:
            Dictionary with error details
        """
        # Look for common error patterns
        error_details = {
            'category': FailureCategory.UNKNOWN,
            'severity': FailureSeverity.MEDIUM,
            'error_message': "Unknown error",
            'stack_trace': None,
            'expected_value': None,
            'actual_value': None,
            'line_number': None
        }
        
        # Find the failure section for this test
        # Look for the test marker in output
        test_marker = f"{test_file}::{test_name}"
        
        # For test categorization, just search in the whole output near the test name
        # This is simpler and more robust than trying to extract exact sections
        test_section = output
        
        # Categorize failure type
        if "AssertionError" in test_section:
            error_details['category'] = FailureCategory.ASSERTION_ERROR
            error_details['severity'] = FailureSeverity.HIGH
            
            # Extract expected vs actual values
            expected_match = re.search(r'(?:expected|assert)\s*[=:]\s*(.+)', test_section, re.IGNORECASE)
            actual_match = re.search(r'(?:actual|got)\s*[=:]\s*(.+)', test_section, re.IGNORECASE)
            
            if expected_match:
                error_details['expected_value'] = expected_match.group(1).strip()
            if actual_match:
                error_details['actual_value'] = actual_match.group(1).strip()
                
        elif "TimeoutError" in test_section or "timeout" in test_section.lower():
            error_details['category'] = FailureCategory.TIMEOUT
            error_details['severity'] = FailureSeverity.MEDIUM
            
        elif "ImportError" in test_section or "ModuleNotFoundError" in test_section:
            error_details['category'] = FailureCategory.IMPORT_ERROR
            error_details['severity'] = FailureSeverity.CRITICAL
            
        elif "fixture" in test_section.lower():
            error_details['category'] = FailureCategory.FIXTURE_ERROR
            error_details['severity'] = FailureSeverity.HIGH
            
        elif any(exc in test_section for exc in ["Exception", "Error"]):
            error_details['category'] = FailureCategory.EXCEPTION
            error_details['severity'] = FailureSeverity.HIGH
        
        # Extract error message (first line with Error/Exception)
        error_msg_match = re.search(r'(.*(?:Error|Exception)[^\n]*)', test_section)
        if error_msg_match:
            error_details['error_message'] = error_msg_match.group(1).strip()
        
        # Extract line number
        line_match = re.search(r'line (\d+)', test_section)
        if line_match:
            error_details['line_number'] = int(line_match.group(1))
        
        # Extract stack trace (simplified)
        stack_lines = [line for line in test_section.split('\n') if line.strip().startswith('File ')]
        if stack_lines:
            error_details['stack_trace'] = '\n'.join(stack_lines[:5])  # Keep first 5 lines
        
        return error_details
    
    def _detect_patterns(self, failures: List[TestFailure]) -> List[FailurePattern]:
        """
        Detect recurring patterns in test failures.
        
        Args:
            failures: List of test failures
            
        Returns:
            List of detected failure patterns
        """
        patterns = []
        
        # Group failures by category and simplified error message
        grouped_failures: Dict[str, List[TestFailure]] = defaultdict(list)
        
        for failure in failures:
            # Create a pattern key based on category and error type
            simplified_error = self._simplify_error_message(failure.error_message)
            pattern_key = f"{failure.category.value}_{simplified_error}"
            grouped_failures[pattern_key].append(failure)
        
        # Create patterns for groups with multiple occurrences
        for pattern_key, group_failures in grouped_failures.items():
            if len(group_failures) >= 2:  # Pattern needs at least 2 occurrences
                pattern = self._create_pattern_from_group(pattern_key, group_failures)
                patterns.append(pattern)
        
        return patterns
    
    def _simplify_error_message(self, error_message: str) -> str:
        """
        Simplify error message for pattern matching.
        
        Args:
            error_message: Raw error message
            
        Returns:
            Simplified error message for grouping
        """
        # Remove specific values (numbers, strings, paths)
        simplified = re.sub(r'\d+', 'N', error_message)
        simplified = re.sub(r"'[^']*'", "'STR'", simplified)
        simplified = re.sub(r'"[^"]*"', '"STR"', simplified)
        simplified = re.sub(r'[\w/\\]+\.py', 'FILE.py', simplified)
        
        # Keep only first 50 chars
        return simplified[:50]
    
    def _create_pattern_from_group(self, pattern_key: str, failures: List[TestFailure]) -> FailurePattern:
        """
        Create a failure pattern from a group of similar failures.
        
        Args:
            pattern_key: Pattern identifier
            failures: List of similar failures
            
        Returns:
            FailurePattern object
        """
        first_failure = failures[0]
        
        # Calculate confidence based on occurrences
        confidence = min(0.95, 0.5 + (len(failures) * 0.1))
        
        # Generate fix suggestions based on category
        fix_suggestions = self._generate_fix_suggestions(first_failure.category, failures)
        
        # Generate template updates
        template_updates = self._generate_template_updates(first_failure.category, failures)
        
        pattern = FailurePattern(
            pattern_id=f"pattern_{pattern_key}_{hash(pattern_key)}",
            category=first_failure.category,
            description=f"{first_failure.category.value}: {first_failure.error_message[:100]}",
            occurrences=len(failures),
            affected_tests=[f.test_name for f in failures],
            confidence=confidence,
            fix_suggestions=fix_suggestions,
            template_updates=template_updates
        )
        
        return pattern
    
    def _generate_fix_suggestions(self, category: FailureCategory, failures: List[TestFailure]) -> List[str]:
        """
        Generate fix suggestions based on failure category.
        
        Args:
            category: Failure category
            failures: List of failures in this category
            
        Returns:
            List of fix suggestions
        """
        suggestions = []
        
        if category == FailureCategory.ASSERTION_ERROR:
            suggestions.append("Add validation for expected vs actual values")
            suggestions.append("Consider adding tolerance for floating-point comparisons")
            suggestions.append("Verify data types match expectations")
            
        elif category == FailureCategory.TIMEOUT:
            suggestions.append("Increase timeout threshold for slow operations")
            suggestions.append("Add performance profiling to identify bottlenecks")
            suggestions.append("Consider mocking slow external dependencies")
            
        elif category == FailureCategory.IMPORT_ERROR:
            suggestions.append("Verify all required dependencies are installed")
            suggestions.append("Check PYTHONPATH and module structure")
            suggestions.append("Add missing __init__.py files if needed")
            
        elif category == FailureCategory.FIXTURE_ERROR:
            suggestions.append("Review fixture setup and teardown logic")
            suggestions.append("Ensure fixtures have proper scope (function/class/module)")
            suggestions.append("Check for fixture dependency cycles")
            
        elif category == FailureCategory.EXCEPTION:
            suggestions.append("Add exception handling for edge cases")
            suggestions.append("Validate input parameters before processing")
            suggestions.append("Add null/None checks for optional parameters")
        
        return suggestions
    
    def _generate_template_updates(self, category: FailureCategory, failures: List[TestFailure]) -> List[Dict[str, str]]:
        """
        Generate template updates based on failure patterns.
        
        Args:
            category: Failure category
            failures: List of failures in this category
            
        Returns:
            List of template update dictionaries
        """
        updates = []
        
        if category == FailureCategory.ASSERTION_ERROR:
            updates.append({
                "template": "assertion_with_message",
                "update": "assert result == expected, f'Expected {expected}, got {result}'"
            })
            
        elif category == FailureCategory.TIMEOUT:
            updates.append({
                "template": "timeout_decorator",
                "update": "@pytest.mark.timeout(30)"
            })
            
        elif category == FailureCategory.EXCEPTION:
            updates.append({
                "template": "exception_context",
                "update": "with pytest.raises(ExpectedException) as exc_info:"
            })
        
        return updates
    
    def _calculate_category_distribution(self, failures: List[TestFailure]) -> Dict[str, int]:
        """Calculate distribution of failures by category"""
        distribution = defaultdict(int)
        for failure in failures:
            distribution[failure.category.value] += 1
        return dict(distribution)
    
    def _calculate_severity_distribution(self, failures: List[TestFailure]) -> Dict[str, int]:
        """Calculate distribution of failures by severity"""
        distribution = defaultdict(int)
        for failure in failures:
            distribution[failure.severity.value] += 1
        return dict(distribution)
    
    def _generate_recommendations(self, failures: List[TestFailure], patterns: List[FailurePattern]) -> List[str]:
        """
        Generate actionable recommendations based on analysis.
        
        Args:
            failures: List of all failures
            patterns: Detected failure patterns
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if not failures:
            recommendations.append("✅ All tests passing! No improvements needed.")
            return recommendations
        
        # High-level recommendations
        failure_rate = len(failures) / max(1, len(failures) + 1) * 100
        if failure_rate > 30:
            recommendations.append(f"⚠️ High failure rate ({failure_rate:.1f}%). Focus on critical issues first.")
        
        # Category-specific recommendations
        category_dist = self._calculate_category_distribution(failures)
        
        if category_dist.get('import_error', 0) > 0:
            recommendations.append("🔴 CRITICAL: Fix import errors before proceeding with other failures.")
        
        if category_dist.get('assertion_error', 0) > 3:
            recommendations.append("📊 Many assertion failures detected. Review test expectations and implementation logic.")
        
        if category_dist.get('timeout', 0) > 0:
            recommendations.append("⏱️ Timeout failures detected. Consider performance optimization or increasing timeouts.")
        
        # Pattern-based recommendations
        if patterns:
            high_confidence_patterns = [p for p in patterns if p.confidence >= 0.7]
            if high_confidence_patterns:
                recommendations.append(
                    f"🔍 {len(high_confidence_patterns)} recurring patterns detected. "
                    f"Fix these to resolve {sum(p.occurrences for p in high_confidence_patterns)} failures."
                )
        
        return recommendations
    
    def improve_templates(self, patterns: List[FailurePattern]) -> Dict[str, Any]:
        """
        Update test generation templates based on failure patterns.
        
        Args:
            patterns: List of failure patterns
            
        Returns:
            Dictionary with update results
        """
        updates = {
            'templates_updated': 0,
            'confidence_increased': 0,
            'new_patterns_added': 0,
            'updates': []
        }
        
        for pattern in patterns:
            # Only update templates for high-confidence patterns (>= 0.7)
            if pattern.confidence < 0.7:
                continue
            
            # Apply template updates
            for template_update in pattern.template_updates:
                update_result = self._apply_template_update(template_update)
                updates['updates'].append(update_result)
                updates['templates_updated'] += 1
            
            # Store pattern in Tier 2 KG if available
            if self.pattern_store:
                self._store_failure_pattern(pattern)
                updates['new_patterns_added'] += 1
            
            # Increase confidence for related successful patterns
            updates['confidence_increased'] += self._boost_related_patterns(pattern)
        
        return updates
    
    def _apply_template_update(self, template_update: Dict[str, str]) -> Dict[str, str]:
        """
        Apply a single template update.
        
        Args:
            template_update: Template update dictionary
            
        Returns:
            Result dictionary
        """
        # In a full implementation, this would modify template files
        # For now, return the update details
        return {
            'template': template_update['template'],
            'update': template_update['update'],
            'status': 'applied',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _store_failure_pattern(self, pattern: FailurePattern) -> bool:
        """
        Store failure pattern in Tier 2 Knowledge Graph.
        
        Args:
            pattern: Failure pattern to store
            
        Returns:
            True if stored successfully
        """
        if not self.pattern_store:
            return False
        
        try:
            pattern_data = {
                'id': pattern.pattern_id,
                'title': f"Failure Pattern: {pattern.category.value}",
                'category': 'test_failure',
                'subcategory': pattern.category.value,
                'description': pattern.description,
                'confidence': pattern.confidence,
                'usage_count': pattern.occurrences,
                'metadata': json.dumps({
                    'affected_tests': pattern.affected_tests,
                    'fix_suggestions': pattern.fix_suggestions,
                    'template_updates': pattern.template_updates,
                    'first_seen': pattern.first_seen,
                    'last_seen': pattern.last_seen
                })
            }
            
            # Store using pattern store API
            self.pattern_store.store_pattern(
                pattern_id=pattern.pattern_id,
                pattern_data=pattern_data,
                namespace='cortex.test_failures'
            )
            
            return True
            
        except Exception as e:
            print(f"Failed to store pattern {pattern.pattern_id}: {e}")
            return False
    
    def _boost_related_patterns(self, failure_pattern: FailurePattern) -> int:
        """
        Boost confidence of related successful patterns.
        
        Args:
            failure_pattern: Failure pattern that was resolved
            
        Returns:
            Number of patterns boosted
        """
        if not self.pattern_store:
            return 0
        
        boosted = 0
        
        # Search for related patterns in same category
        try:
            related = self.pattern_store.search_patterns(
                query=failure_pattern.category.value,
                namespace='cortex.test_generation',
                limit=10
            )
            
            for pattern in related:
                # Boost confidence by 0.03 (smaller than bug-driven boost)
                new_confidence = min(1.0, pattern.get('confidence', 0.5) + 0.03)
                self.pattern_store.update_pattern_confidence(
                    pattern_id=pattern['id'],
                    confidence=new_confidence
                )
                boosted += 1
                
        except Exception as e:
            print(f"Failed to boost related patterns: {e}")
        
        return boosted
    
    def generate_report(self, analysis: FailureAnalysisReport, output_format: str = 'text') -> str:
        """
        Generate formatted failure analysis report.
        
        Args:
            analysis: Failure analysis report
            output_format: 'text' or 'json'
            
        Returns:
            Formatted report string
        """
        if output_format == 'json':
            return json.dumps({
                'total_tests': analysis.total_tests,
                'passed': analysis.passed,
                'failed': analysis.failed,
                'skipped': analysis.skipped,
                'errors': analysis.errors,
                'duration_seconds': analysis.duration_seconds,
                'category_distribution': analysis.category_distribution,
                'severity_distribution': analysis.severity_distribution,
                'patterns': [
                    {
                        'pattern_id': p.pattern_id,
                        'category': p.category.value,
                        'occurrences': p.occurrences,
                        'confidence': p.confidence,
                        'affected_tests': p.affected_tests,
                        'fix_suggestions': p.fix_suggestions
                    } for p in analysis.patterns
                ],
                'recommendations': analysis.recommendations,
                'analyzed_at': analysis.analyzed_at
            }, indent=2)
        
        # Text format
        report_lines = [
            "=" * 70,
            "FAILURE ANALYSIS REPORT",
            "=" * 70,
            "",
            f"📊 Test Results:",
            f"  Total:   {analysis.total_tests}",
            f"  ✅ Passed: {analysis.passed}",
            f"  ❌ Failed: {analysis.failed}",
            f"  ⏭️  Skipped: {analysis.skipped}",
            f"  ⚠️  Errors: {analysis.errors}",
            f"  ⏱️  Duration: {analysis.duration_seconds:.2f}s",
            "",
            "📈 Category Distribution:",
        ]
        
        for category, count in sorted(analysis.category_distribution.items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"  • {category}: {count}")
        
        report_lines.extend([
            "",
            "🔥 Severity Distribution:",
        ])
        
        for severity, count in sorted(analysis.severity_distribution.items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"  • {severity}: {count}")
        
        if analysis.patterns:
            report_lines.extend([
                "",
                f"🔍 Recurring Patterns ({len(analysis.patterns)}):",
            ])
            
            for pattern in sorted(analysis.patterns, key=lambda p: p.confidence, reverse=True):
                report_lines.extend([
                    f"",
                    f"  Pattern: {pattern.category.value}",
                    f"  Occurrences: {pattern.occurrences}",
                    f"  Confidence: {pattern.confidence:.2f}",
                    f"  Affected: {', '.join(pattern.affected_tests[:3])}{'...' if len(pattern.affected_tests) > 3 else ''}",
                ])
        
        if analysis.recommendations:
            report_lines.extend([
                "",
                "💡 Recommendations:",
            ])
            for rec in analysis.recommendations:
                report_lines.append(f"  {rec}")
        
        report_lines.extend([
            "",
            "=" * 70,
            f"Analyzed at: {analysis.analyzed_at}",
            "=" * 70
        ])
        
        return '\n'.join(report_lines)


if __name__ == "__main__":
    # Example usage
    sample_output = """
    tests/test_auth.py::test_login FAILED
    AssertionError: Expected 200, got 500
    tests/test_auth.py::test_logout PASSED
    tests/test_user.py::test_create_user FAILED
    TimeoutError: Test exceeded 30 seconds
    
    ========== 1 passed, 2 failed in 5.23s ==========
    """
    
    analyzer = FailureAnalyzer()
    report = analyzer.parse_pytest_output(sample_output, duration=5.23)
    
    print(analyzer.generate_report(report, output_format='text'))

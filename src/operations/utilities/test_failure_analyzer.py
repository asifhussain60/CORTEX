"""
Test Failure Analyzer - Strategic Test Failure Classification & Mitigation

Purpose:
    Parse pytest/unittest output, classify failures by root cause, generate
    mitigation strategies, and enable strategic deferral for non-blocking issues.

Classification Types:
    - ARCHITECTURAL: Fundamental design issues (BLOCKS progress)
    - TEST_EXPECTATION: Test setup/assertion issues (Can DEFER)
    - LOGIC_BUG: Implementation errors (Can DEFER if non-critical)
    - ENVIRONMENT: Setup/dependency issues (BLOCKS until fixed)
    - SYNTAX: Parse/import errors (BLOCKS progress)

Features:
    - Parse pytest/unittest output
    - Extract failure details (file, line, message, traceback)
    - Classify failure type with confidence score
    - Generate actionable mitigation strategies
    - Track deferred failures (must resolve before 100%)
    - Integration with TDD Orchestrator

Author: Asif Hussain
Date: December 13, 2025
Version: 1.0.0
"""

import re
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Test failure classification types"""
    ARCHITECTURAL = "ARCHITECTURAL"          # Design issues - BLOCKS
    TEST_EXPECTATION = "TEST_EXPECTATION"   # Test setup issues - CAN DEFER
    LOGIC_BUG = "LOGIC_BUG"                 # Implementation errors - CAN DEFER
    ENVIRONMENT = "ENVIRONMENT"              # Setup/deps - BLOCKS
    SYNTAX = "SYNTAX"                        # Parse/import - BLOCKS
    UNKNOWN = "UNKNOWN"                      # Unclassified


class FailureSeverity(Enum):
    """Failure severity levels"""
    CRITICAL = "CRITICAL"      # BLOCKS progress
    HIGH = "HIGH"              # Should fix soon
    MEDIUM = "MEDIUM"          # Can defer strategically
    LOW = "LOW"                # Minor issues


@dataclass
class FailureInfo:
    """Information about a single test failure"""
    test_name: str
    test_file: Path
    line_number: Optional[int]
    failure_message: str
    traceback: str
    failure_type: FailureType
    severity: FailureSeverity
    confidence: float  # 0.0-1.0
    can_defer: bool
    mitigation_strategy: str
    root_cause_analysis: str


@dataclass
class TestRunResult:
    """Results from parsing test output"""
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    failures: List[FailureInfo] = field(default_factory=list)
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass percentage"""
        return (self.passed / self.total_tests * 100) if self.total_tests > 0 else 0.0
    
    @property
    def critical_failures(self) -> List[FailureInfo]:
        """Get failures that block progress"""
        return [f for f in self.failures if f.severity == FailureSeverity.CRITICAL]
    
    @property
    def deferrable_failures(self) -> List[FailureInfo]:
        """Get failures that can be strategically deferred"""
        return [f for f in self.failures if f.can_defer]


class TestOutputParser:
    """
    Parses pytest and unittest output to extract test results and failures.
    """
    
    # Pytest patterns
    PYTEST_SUMMARY_PATTERN = r'=+ (.*?) passed.*?in ([\d.]+)s'
    PYTEST_FAILURE_PATTERN = r'FAILED (.*?)::(.*?) - (.*?)$'
    PYTEST_ERROR_PATTERN = r'ERROR (.*?)::(.*?) - (.*?)$'
    
    # Unittest patterns  
    UNITTEST_SUMMARY_PATTERN = r'Ran (\d+) tests? in ([\d.]+)s'
    UNITTEST_FAILURE_PATTERN = r'FAIL: (.*?) \((.*?)\)'
    
    def __init__(self, output: str, framework: str = "pytest"):
        self.output = output
        self.framework = framework.lower()
    
    def parse(self) -> TestRunResult:
        """Parse test output and return structured results"""
        if self.framework == "pytest":
            return self._parse_pytest()
        elif self.framework == "unittest":
            return self._parse_unittest()
        else:
            logger.error(f"Unsupported test framework: {self.framework}")
            return TestRunResult(0, 0, 0, 0, 0, 0.0)
    
    def _parse_pytest(self) -> TestRunResult:
        """Parse pytest output"""
        lines = self.output.split('\n')
        
        # Extract summary line
        total, passed, failed, skipped, errors, duration = 0, 0, 0, 0, 0, 0.0
        
        for line in lines:
            # Summary: "5 passed, 2 failed, 1 skipped in 1.23s"
            if ' passed' in line or ' failed' in line:
                # Extract counts
                passed_match = re.search(r'(\d+) passed', line)
                failed_match = re.search(r'(\d+) failed', line)
                skipped_match = re.search(r'(\d+) skipped', line)
                error_match = re.search(r'(\d+) error', line)
                duration_match = re.search(r'in ([\d.]+)s', line)
                
                passed = int(passed_match.group(1)) if passed_match else 0
                failed = int(failed_match.group(1)) if failed_match else 0
                skipped = int(skipped_match.group(1)) if skipped_match else 0
                errors = int(error_match.group(1)) if error_match else 0
                duration = float(duration_match.group(1)) if duration_match else 0.0
                total = passed + failed + skipped + errors
        
        # Extract failures
        failures = self._extract_pytest_failures(lines)
        
        return TestRunResult(
            total_tests=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            duration=duration,
            failures=failures
        )
    
    def _extract_pytest_failures(self, lines: List[str]) -> List[FailureInfo]:
        """Extract failure details from pytest output"""
        failures = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Look for FAILURES section header
            if '===== FAILURES =====' in line or '_____ test_' in line:
                # Next line should be test name separator
                if i + 1 < len(lines) and lines[i + 1].startswith('_____'):
                    # Extract test name from separator line
                    test_name_match = re.search(r'_____ (\w+) _____', lines[i + 1])
                    if test_name_match:
                        test_name = test_name_match.group(1)
                        
                        # Extract traceback until next separator or end
                        traceback_lines = []
                        j = i + 2
                        while j < len(lines) and not (lines[j].startswith('=====') or lines[j].startswith('_____')):
                            traceback_lines.append(lines[j])
                            j += 1
                        
                        traceback = '\n'.join(traceback_lines)
                        
                        # Find test file and line number from traceback
                        file_match = re.search(r'(tests/[^:]+\.py):(\d+):', traceback)
                        test_file = Path(file_match.group(1)) if file_match else Path("unknown.py")
                        
                        # Extract error message (line starting with 'E')
                        error_lines = [l.strip() for l in traceback_lines if l.strip().startswith('E   ')]
                        failure_message = error_lines[0][4:] if error_lines else "Unknown error"
                        
                        # Classify failure
                        failure_info = self._classify_failure(
                            test_name=test_name,
                            test_file=test_file,
                            failure_message=failure_message,
                            traceback=traceback
                        )
                        
                        failures.append(failure_info)
                        i = j
            
            i += 1
        
        return failures
    
    def _parse_unittest(self) -> TestRunResult:
        """Parse unittest output"""
        # Similar to pytest but with unittest patterns
        # Implementation would follow same structure
        raise NotImplementedError("Unittest parsing coming in next iteration")
    
    def _classify_failure(self, test_name: str, test_file: Path, 
                         failure_message: str, traceback: str) -> FailureInfo:
        """Classify failure and generate mitigation strategy"""
        
        # Use classifier
        classifier = FailureClassifier()
        failure_type, confidence = classifier.classify(failure_message, traceback)
        
        # Determine severity
        severity = self._determine_severity(failure_type, traceback)
        
        # Check if deferrable
        can_defer = failure_type in [
            FailureType.TEST_EXPECTATION,
            FailureType.LOGIC_BUG
        ] and severity != FailureSeverity.CRITICAL
        
        # Generate mitigation strategy
        mitigation = self._generate_mitigation(failure_type, failure_message)
        
        # Root cause analysis
        root_cause = self._analyze_root_cause(failure_message, traceback)
        
        # Extract line number
        line_match = re.search(r':(\d+):', traceback)
        line_number = int(line_match.group(1)) if line_match else None
        
        return FailureInfo(
            test_name=test_name,
            test_file=test_file,
            line_number=line_number,
            failure_message=failure_message,
            traceback=traceback,
            failure_type=failure_type,
            severity=severity,
            confidence=confidence,
            can_defer=can_defer,
            mitigation_strategy=mitigation,
            root_cause_analysis=root_cause
        )
    
    def _determine_severity(self, failure_type: FailureType, traceback: str) -> FailureSeverity:
        """Determine failure severity"""
        if failure_type in [FailureType.ARCHITECTURAL, FailureType.SYNTAX, FailureType.ENVIRONMENT]:
            return FailureSeverity.CRITICAL
        elif "AssertionError" in traceback:
            return FailureSeverity.MEDIUM
        elif "TypeError" in traceback or "AttributeError" in traceback:
            return FailureSeverity.HIGH
        else:
            return FailureSeverity.LOW
    
    def _generate_mitigation(self, failure_type: FailureType, message: str) -> str:
        """Generate mitigation strategy based on failure type"""
        strategies = {
            FailureType.ARCHITECTURAL: "Requires design review. Consider refactoring architecture to address fundamental issues.",
            FailureType.TEST_EXPECTATION: "Update test assertions to match actual behavior. Verify test setup is correct.",
            FailureType.LOGIC_BUG: "Fix implementation logic. Add defensive checks and validation.",
            FailureType.ENVIRONMENT: "Check dependencies, configuration, and environment setup. Ensure all prerequisites met.",
            FailureType.SYNTAX: "Fix syntax/import errors. Verify all modules are properly installed.",
            FailureType.UNKNOWN: "Investigate failure manually. Review traceback for clues."
        }
        return strategies.get(failure_type, strategies[FailureType.UNKNOWN])
    
    def _analyze_root_cause(self, message: str, traceback: str) -> str:
        """Perform root cause analysis"""
        if "AssertionError" in message:
            return "Test assertion failed - expected value doesn't match actual"
        elif "AttributeError" in message:
            return "Object missing expected attribute - possible None or wrong type"
        elif "TypeError" in message:
            return "Type mismatch - wrong argument type or missing required parameter"
        elif "ImportError" in message or "ModuleNotFoundError" in message:
            return "Missing dependency or incorrect import path"
        elif "FileNotFoundError" in message:
            return "Missing file or incorrect path"
        else:
            return "Review traceback for specific error details"


class FailureClassifier:
    """
    Classifies test failures by analyzing error messages and tracebacks.
    """
    
    # Pattern-based classification rules
    ARCHITECTURAL_PATTERNS = [
        r'circular import',
        r'design violation',
        r'interface mismatch',
        r'dependency cycle'
    ]
    
    TEST_EXPECTATION_PATTERNS = [
        r'AssertionError',
        r'expected.*but got',
        r'assert.*==.*failed'
    ]
    
    LOGIC_BUG_PATTERNS = [
        r'TypeError',
        r'AttributeError',
        r'ValueError',
        r'KeyError',
        r'IndexError'
    ]
    
    ENVIRONMENT_PATTERNS = [
        r'ModuleNotFoundError',
        r'ImportError',
        r'ConnectionError',
        r'PermissionError',
        r'FileNotFoundError'
    ]
    
    SYNTAX_PATTERNS = [
        r'SyntaxError',
        r'IndentationError',
        r'NameError'
    ]
    
    def classify(self, message: str, traceback: str) -> Tuple[FailureType, float]:
        """Classify failure and return confidence score"""
        text = f"{message}\n{traceback}"
        
        # Check each pattern type
        scores = {
            FailureType.ARCHITECTURAL: self._pattern_match_score(text, self.ARCHITECTURAL_PATTERNS),
            FailureType.TEST_EXPECTATION: self._pattern_match_score(text, self.TEST_EXPECTATION_PATTERNS),
            FailureType.LOGIC_BUG: self._pattern_match_score(text, self.LOGIC_BUG_PATTERNS),
            FailureType.ENVIRONMENT: self._pattern_match_score(text, self.ENVIRONMENT_PATTERNS),
            FailureType.SYNTAX: self._pattern_match_score(text, self.SYNTAX_PATTERNS)
        }
        
        # Get highest scoring type
        if max(scores.values()) == 0:
            return FailureType.UNKNOWN, 0.0
        
        failure_type = max(scores, key=scores.get)
        confidence = scores[failure_type]
        
        return failure_type, confidence
    
    def _pattern_match_score(self, text: str, patterns: List[str]) -> float:
        """Calculate match score for pattern list"""
        matches = sum(1 for pattern in patterns if re.search(pattern, text, re.IGNORECASE))
        return matches / len(patterns) if patterns else 0.0


class TestFailureAnalyzer:
    """
    Main orchestrator for test failure analysis.
    Coordinates parsing, classification, and mitigation generation.
    """
    
    def __init__(self):
        self.deferred_failures: List[FailureInfo] = []
    
    def analyze(self, test_output: str, framework: str = "pytest") -> TestRunResult:
        """
        Analyze test output and return structured results.
        
        Args:
            test_output: Raw test runner output
            framework: Test framework (pytest, unittest)
        
        Returns:
            TestRunResult with parsed failures and classifications
        """
        logger.info(f"Analyzing test output from {framework}")
        
        parser = TestOutputParser(test_output, framework)
        result = parser.parse()
        
        logger.info(f"Analysis complete: {result.passed}/{result.total_tests} passed ({result.pass_rate:.1f}%)")
        logger.info(f"Critical failures: {len(result.critical_failures)}")
        logger.info(f"Deferrable failures: {len(result.deferrable_failures)}")
        
        return result
    
    def defer_failure(self, failure: FailureInfo) -> bool:
        """
        Defer a non-critical failure for later resolution.
        
        Args:
            failure: FailureInfo to defer
        
        Returns:
            True if deferral allowed, False if critical
        """
        if not failure.can_defer:
            logger.error(f"Cannot defer critical failure: {failure.test_name}")
            return False
        
        self.deferred_failures.append(failure)
        logger.info(f"Deferred failure: {failure.test_name} ({failure.failure_type.value})")
        return True
    
    def get_deferred_count(self) -> int:
        """Get count of deferred failures (must be 0 at 100% completion)"""
        return len(self.deferred_failures)
    
    def generate_failure_report(self, result: TestRunResult) -> str:
        """Generate detailed failure analysis report"""
        lines = []
        
        lines.append("━" * 78)
        lines.append("TEST FAILURE ANALYSIS REPORT")
        lines.append("━" * 78)
        lines.append(f"Total Tests: {result.total_tests}")
        lines.append(f"Passed: {result.passed} ({result.pass_rate:.1f}%)")
        lines.append(f"Failed: {result.failed}")
        lines.append(f"Skipped: {result.skipped}")
        lines.append(f"Errors: {result.errors}")
        lines.append(f"Duration: {result.duration:.2f}s")
        lines.append("")
        
        if result.critical_failures:
            lines.append("🚨 CRITICAL FAILURES (BLOCKING):")
            lines.append("-" * 78)
            for f in result.critical_failures:
                lines.append(f"\n❌ {f.test_name}")
                lines.append(f"   File: {f.test_file}:{f.line_number}")
                lines.append(f"   Type: {f.failure_type.value} (confidence: {f.confidence:.0%})")
                lines.append(f"   Message: {f.failure_message}")
                lines.append(f"   Root Cause: {f.root_cause_analysis}")
                lines.append(f"   Mitigation: {f.mitigation_strategy}")
        
        if result.deferrable_failures:
            lines.append("\n⚠️  DEFERRABLE FAILURES:")
            lines.append("-" * 78)
            for f in result.deferrable_failures:
                lines.append(f"\n🟡 {f.test_name}")
                lines.append(f"   Type: {f.failure_type.value}")
                lines.append(f"   Severity: {f.severity.value}")
                lines.append(f"   Mitigation: {f.mitigation_strategy}")
        
        lines.append("\n" + "━" * 78)
        
        return '\n'.join(lines)


# Convenience functions
def analyze_pytest_output(output: str) -> TestRunResult:
    """Analyze pytest output"""
    analyzer = TestFailureAnalyzer()
    return analyzer.analyze(output, "pytest")


def analyze_unittest_output(output: str) -> TestRunResult:
    """Analyze unittest output"""
    analyzer = TestFailureAnalyzer()
    return analyzer.analyze(output, "unittest")

"""
Code Analysis Utility

Lightweight code analysis for detecting issues in code reviews.
Replaces heavy orchestrator (969 lines) with focused utility (~550 lines).

Core analyzers:
- Breaking changes detection
- Security vulnerabilities
- Performance issues
- Code quality checks

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import re
import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import CORTEX config
try:
    from src.config import config
    CORTEX_ROOT = Path(config.root_path)
except ImportError:
    CORTEX_ROOT = Path(__file__).resolve().parents[4]


# ===== ENUMS & DATACLASSES =====

class IssueSeverity(Enum):
    """Severity levels for code issues."""
    CRITICAL = "critical"  # Must fix before merge
    HIGH = "high"         # Should fix soon
    MEDIUM = "medium"     # Should fix eventually
    LOW = "low"          # Nice to have


class IssueCategory(Enum):
    """Categories of code issues."""
    BREAKING_CHANGE = "breaking_change"
    SECURITY = "security"
    PERFORMANCE = "performance"
    CODE_SMELL = "code_smell"
    BEST_PRACTICE = "best_practice"
    MAINTAINABILITY = "maintainability"


@dataclass
class CodeIssue:
    """Single code issue found during analysis."""
    category: IssueCategory
    severity: IssueSeverity
    title: str
    description: str
    file_path: str
    line_number: int = 0
    code_snippet: str = ""
    fix_suggestion: str = ""


@dataclass
class AnalysisResult:
    """Results from code analysis."""
    analyzer: str
    file_path: str
    issues: List[CodeIssue] = field(default_factory=list)
    execution_time: float = 0.0
    
    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == IssueSeverity.CRITICAL)
    
    @property
    def high_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == IssueSeverity.HIGH)
    
    @property
    def medium_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == IssueSeverity.MEDIUM)
    
    @property
    def low_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == IssueSeverity.LOW)
    
    @property
    def total_count(self) -> int:
        return len(self.issues)


# ===== HELPER FUNCTIONS =====

def _detect_language(file_path: Path) -> str:
    """Detect programming language from file extension."""
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.cs': 'csharp',
        '.java': 'java',
        '.go': 'go',
        '.rb': 'ruby'
    }
    return ext_map.get(file_path.suffix.lower(), 'unknown')


# ===== CORE OPERATION 1: ANALYZE FILE =====

def analyze_file(file_path: Path, analyzers: Optional[List[str]] = None) -> AnalysisResult:
    """
    Analyze single file for code issues.
    
    Args:
        file_path: Path to file to analyze
        analyzers: List of analyzer names (default: all)
        
    Returns:
        AnalysisResult with findings
    """
    logger.info(f"🔍 Analyzing file: {file_path.name}")
    
    start_time = time.time()
    
    if not file_path.exists():
        return AnalysisResult(
            analyzer="file_analyzer",
            file_path=str(file_path),
            issues=[],
            execution_time=0.0
        )
    
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    language = _detect_language(file_path)
    
    # Run analyzers
    all_issues = []
    
    if not analyzers or 'breaking' in analyzers:
        all_issues.extend(_check_breaking_changes(file_path, content, language))
    
    if not analyzers or 'security' in analyzers:
        all_issues.extend(_check_security(file_path, content, language))
    
    if not analyzers or 'performance' in analyzers:
        all_issues.extend(_check_performance(file_path, content, language))
    
    if not analyzers or 'quality' in analyzers:
        all_issues.extend(_check_code_quality(file_path, content, language))
    
    execution_time = time.time() - start_time
    
    return AnalysisResult(
        analyzer="file_analyzer",
        file_path=str(file_path),
        issues=all_issues,
        execution_time=execution_time
    )


# ===== CORE OPERATION 2: GET BREAKING CHANGES =====

def get_breaking_changes(file_path: Path) -> List[CodeIssue]:
    """
    Detect breaking changes in public APIs.
    
    Args:
        file_path: Path to file to analyze
        
    Returns:
        List of breaking change issues
    """
    logger.info(f"🔨 Checking breaking changes: {file_path.name}")
    
    if not file_path.exists():
        return []
    
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    language = _detect_language(file_path)
    
    return _check_breaking_changes(file_path, content, language)


def _check_breaking_changes(file_path: Path, content: str, language: str) -> List[CodeIssue]:
    """Check for breaking changes based on language."""
    issues = []
    lines = content.split('\n')
    
    if language == 'python':
        # Check for removed public functions/methods
        for i, line in enumerate(lines, 1):
            # Public function removal (starts with def, not _)
            if re.match(r'^\s*def\s+[a-z][a-z0-9_]*\s*\(.*\)\s*->\s*None:', line):
                issues.append(CodeIssue(
                    category=IssueCategory.BREAKING_CHANGE,
                    severity=IssueSeverity.HIGH,
                    title="Function returns None (potential breaking change)",
                    description=f"Public function returns None at line {i}, may break callers expecting return value",
                    file_path=str(file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                    fix_suggestion="Consider returning a value or documenting None return explicitly"
                ))
            
            # Check for raise NotImplementedError (API not ready)
            if 'raise NotImplementedError' in line:
                issues.append(CodeIssue(
                    category=IssueCategory.BREAKING_CHANGE,
                    severity=IssueSeverity.CRITICAL,
                    title="Not implemented public API",
                    description=f"Function raises NotImplementedError at line {i}",
                    file_path=str(file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                    fix_suggestion="Implement the function or mark as internal with underscore prefix"
                ))
    
    elif language in ['javascript', 'typescript']:
        # Check for breaking changes in exports
        for i, line in enumerate(lines, 1):
            if re.search(r'export\s+(function|class|const|let)\s+\w+', line):
                if 'TODO' in line or 'FIXME' in line:
                    issues.append(CodeIssue(
                        category=IssueCategory.BREAKING_CHANGE,
                        severity=IssueSeverity.MEDIUM,
                        title="Exported API with TODO/FIXME",
                        description=f"Exported entity has TODO/FIXME at line {i}",
                        file_path=str(file_path),
                        line_number=i,
                        code_snippet=line.strip(),
                        fix_suggestion="Complete implementation before exporting"
                    ))
    
    return issues


# ===== CORE OPERATION 3: CHECK SECURITY =====

def check_security(file_path: Path) -> List[CodeIssue]:
    """
    Check for security vulnerabilities.
    
    Args:
        file_path: Path to file to analyze
        
    Returns:
        List of security issues
    """
    logger.info(f"🔒 Checking security: {file_path.name}")
    
    if not file_path.exists():
        return []
    
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    language = _detect_language(file_path)
    
    return _check_security(file_path, content, language)


def _check_security(file_path: Path, content: str, language: str) -> List[CodeIssue]:
    """Check for security vulnerabilities."""
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # SQL injection risk
        if re.search(r'execute\s*\(["\'].*\+.*["\']', line, re.IGNORECASE):
            issues.append(CodeIssue(
                category=IssueCategory.SECURITY,
                severity=IssueSeverity.CRITICAL,
                title="SQL Injection Risk",
                description=f"Potential SQL injection vulnerability at line {i}",
                file_path=str(file_path),
                line_number=i,
                code_snippet=line.strip(),
                fix_suggestion="Use parameterized queries instead of string concatenation"
            ))
        
        # Hardcoded credentials
        if re.search(r'(password|api_key|secret|token)\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
            if not re.search(r'(password|api_key|secret|token)\s*=\s*["\'](|none|null|<.*>|{.*}|\$.*)["\']', line, re.IGNORECASE):
                issues.append(CodeIssue(
                    category=IssueCategory.SECURITY,
                    severity=IssueSeverity.CRITICAL,
                    title="Hardcoded Credentials",
                    description=f"Potential hardcoded credentials at line {i}",
                    file_path=str(file_path),
                    line_number=i,
                    code_snippet="[REDACTED FOR SECURITY]",
                    fix_suggestion="Use environment variables or secure key management"
                ))
        
        # eval() usage (code injection risk)
        if language == 'python' and re.search(r'\beval\s*\(', line):
            issues.append(CodeIssue(
                category=IssueCategory.SECURITY,
                severity=IssueSeverity.HIGH,
                title="Unsafe eval() Usage",
                description=f"Use of eval() at line {i} can execute arbitrary code",
                file_path=str(file_path),
                line_number=i,
                code_snippet=line.strip(),
                fix_suggestion="Use ast.literal_eval() for safe evaluation or alternative approaches"
            ))
        
        # Insecure random (for security purposes)
        if re.search(r'import random(?!\s+#.*crypto)', line) or re.search(r'from random import', line):
            issues.append(CodeIssue(
                category=IssueCategory.SECURITY,
                severity=IssueSeverity.MEDIUM,
                title="Insecure Random Usage",
                description=f"Use of 'random' module at line {i} (not cryptographically secure)",
                file_path=str(file_path),
                line_number=i,
                code_snippet=line.strip(),
                fix_suggestion="Use 'secrets' module for security-related randomness"
            ))
    
    return issues


# ===== CORE OPERATION 4: CHECK PERFORMANCE =====

def check_performance(file_path: Path) -> List[CodeIssue]:
    """
    Check for performance issues.
    
    Args:
        file_path: Path to file to analyze
        
    Returns:
        List of performance issues
    """
    logger.info(f"⚡ Checking performance: {file_path.name}")
    
    if not file_path.exists():
        return []
    
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    language = _detect_language(file_path)
    
    return _check_performance(file_path, content, language)


def _check_performance(file_path: Path, content: str, language: str) -> List[CodeIssue]:
    """Check for performance issues."""
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Nested loops (O(n²) or worse)
        if re.search(r'for\s+\w+\s+in\s+', line):
            # Look ahead for nested loop within 10 lines
            for j in range(i, min(i + 10, len(lines))):
                if j > i and re.search(r'for\s+\w+\s+in\s+', lines[j]):
                    issues.append(CodeIssue(
                        category=IssueCategory.PERFORMANCE,
                        severity=IssueSeverity.MEDIUM,
                        title="Nested Loop Detected",
                        description=f"Nested loops at line {i} may have O(n²) complexity",
                        file_path=str(file_path),
                        line_number=i,
                        code_snippet=line.strip(),
                        fix_suggestion="Consider using dictionary lookup or set operations for O(n) complexity"
                    ))
                    break
        
        # String concatenation in loop
        if language == 'python':
            if re.search(r'for\s+\w+\s+in\s+.*:', line):
                # Check next few lines for += string concatenation
                for j in range(i, min(i + 5, len(lines))):
                    if re.search(r'\w+\s*\+=\s*["\']', lines[j]) or re.search(r'\w+\s*\+=\s*\w+\s*\+\s*["\']', lines[j]):
                        issues.append(CodeIssue(
                            category=IssueCategory.PERFORMANCE,
                            severity=IssueSeverity.MEDIUM,
                            title="String Concatenation in Loop",
                            description=f"String concatenation in loop starting at line {i}",
                            file_path=str(file_path),
                            line_number=i,
                            code_snippet=line.strip(),
                            fix_suggestion="Use list.append() and ''.join() for better performance"
                        ))
                        break
        
        # Inefficient list operations
        if language == 'python' and re.search(r'\.append\(.*\).*\.pop\(0\)', line):
            issues.append(CodeIssue(
                category=IssueCategory.PERFORMANCE,
                severity=IssueSeverity.MEDIUM,
                title="Inefficient List Operations",
                description=f"Using list as queue at line {i} (O(n) for pop(0))",
                file_path=str(file_path),
                line_number=i,
                code_snippet=line.strip(),
                fix_suggestion="Use collections.deque for O(1) append and popleft operations"
            ))
    
    return issues


# ===== CORE OPERATION 5: CHECK CODE QUALITY =====

def check_code_quality(file_path: Path) -> List[CodeIssue]:
    """
    Check general code quality issues.
    
    Args:
        file_path: Path to file to analyze
        
    Returns:
        List of code quality issues
    """
    logger.info(f"✨ Checking code quality: {file_path.name}")
    
    if not file_path.exists():
        return []
    
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    language = _detect_language(file_path)
    
    return _check_code_quality(file_path, content, language)


def _check_code_quality(file_path: Path, content: str, language: str) -> List[CodeIssue]:
    """Check for code quality issues."""
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Long lines
        if len(line) > 120:
            issues.append(CodeIssue(
                category=IssueCategory.CODE_SMELL,
                severity=IssueSeverity.LOW,
                title="Line Too Long",
                description=f"Line {i} exceeds 120 characters ({len(line)} chars)",
                file_path=str(file_path),
                line_number=i,
                code_snippet=line[:80] + "...",
                fix_suggestion="Break long lines for better readability"
            ))
        
        # Complex conditionals
        if line.count(' and ') + line.count(' or ') > 3:
            issues.append(CodeIssue(
                category=IssueCategory.MAINTAINABILITY,
                severity=IssueSeverity.MEDIUM,
                title="Complex Conditional Logic",
                description=f"Complex conditional at line {i} ({line.count(' and ') + line.count(' or ')} boolean operators)",
                file_path=str(file_path),
                line_number=i,
                code_snippet=line.strip(),
                fix_suggestion="Extract conditions into named variables or separate function"
            ))
        
        # Magic numbers (except common ones)
        if language == 'python':
            magic_nums = re.findall(r'\b(\d{3,})\b', line)
            for num in magic_nums:
                if int(num) not in [100, 200, 404, 500, 1000]:
                    issues.append(CodeIssue(
                        category=IssueCategory.BEST_PRACTICE,
                        severity=IssueSeverity.LOW,
                        title="Magic Number",
                        description=f"Magic number {num} at line {i}",
                        file_path=str(file_path),
                        line_number=i,
                        code_snippet=line.strip(),
                        fix_suggestion=f"Extract {num} to named constant for clarity"
                    ))
                    break  # Only report first magic number per line
        
        # Commented code
        stripped = line.strip()
        if language == 'python' and stripped.startswith('#'):
            # Check if it looks like code (contains = or () )
            if '=' in stripped or '()' in stripped or 'def ' in stripped:
                issues.append(CodeIssue(
                    category=IssueCategory.CODE_SMELL,
                    severity=IssueSeverity.LOW,
                    title="Commented Code",
                    description=f"Commented code at line {i}",
                    file_path=str(file_path),
                    line_number=i,
                    code_snippet=stripped,
                    fix_suggestion="Remove commented code (use git history if needed)"
                ))
    
    return issues


# ===== CORE OPERATION 6: GENERATE ANALYSIS REPORT =====

def generate_analysis_report(results: List[AnalysisResult], output_path: Path) -> bool:
    """
    Generate markdown analysis report.
    
    Args:
        results: List of analysis results
        output_path: Path to save report
        
    Returns:
        True if successful
    """
    logger.info(f"📄 Generating analysis report: {output_path.name}")
    
    try:
        # Count issues by severity
        all_issues = []
        for result in results:
            all_issues.extend(result.issues)
        
        critical = sum(1 for i in all_issues if i.severity == IssueSeverity.CRITICAL)
        high = sum(1 for i in all_issues if i.severity == IssueSeverity.HIGH)
        medium = sum(1 for i in all_issues if i.severity == IssueSeverity.MEDIUM)
        low = sum(1 for i in all_issues if i.severity == IssueSeverity.LOW)
        
        # Generate report
        report = f"""# Code Analysis Report

**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Files Analyzed:** {len(results)}  
**Total Issues:** {len(all_issues)}

---

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | {critical} |
| 🟠 High | {high} |
| 🟡 Medium | {medium} |
| 🟢 Low | {low} |

---

## Issues by File

"""
        
        for result in results:
            if not result.issues:
                continue
            
            report += f"### {Path(result.file_path).name}\n\n"
            report += f"**Issues:** {result.total_count} | **Execution Time:** {result.execution_time:.3f}s\n\n"
            
            # Group by severity
            by_severity = {
                IssueSeverity.CRITICAL: [],
                IssueSeverity.HIGH: [],
                IssueSeverity.MEDIUM: [],
                IssueSeverity.LOW: []
            }
            
            for issue in result.issues:
                by_severity[issue.severity].append(issue)
            
            for severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH, IssueSeverity.MEDIUM, IssueSeverity.LOW]:
                issues_list = by_severity[severity]
                if not issues_list:
                    continue
                
                severity_icons = {
                    IssueSeverity.CRITICAL: "🔴",
                    IssueSeverity.HIGH: "🟠",
                    IssueSeverity.MEDIUM: "🟡",
                    IssueSeverity.LOW: "🟢"
                }
                
                report += f"#### {severity_icons[severity]} {severity.value.upper()} Issues\n\n"
                
                for issue in issues_list:
                    report += f"**{issue.title}**\n"
                    report += f"- Line: {issue.line_number}\n"
                    report += f"- Category: {issue.category.value}\n"
                    report += f"- Description: {issue.description}\n"
                    if issue.fix_suggestion:
                        report += f"- 💡 Suggestion: {issue.fix_suggestion}\n"
                    report += "\n"
        
        # Save report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding='utf-8')
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        return False


# ===== CLI TEST EXECUTION =====

if __name__ == "__main__":
    print("=" * 60)
    print("Code Analysis Utility - Direct Test")
    print("=" * 60)
    
    # Test 1: Analyze test file
    print("\n[Test 1] Analyze file with security issues...")
    test_content = '''
import random
password = "hardcoded123"

def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    result = db.execute(query)
    return result

def process_items(items):
    result = ""
    for item in items:
        result += str(item) + ","
    return result
'''
    
    test_file = Path("/tmp/test_analysis.py")
    test_file.write_text(test_content)
    
    result = analyze_file(test_file)
    print(f"Issues found: {result.total_count}")
    print(f"Critical: {result.critical_count}, High: {result.high_count}, Medium: {result.medium_count}, Low: {result.low_count}")
    print(f"Execution time: {result.execution_time:.3f}s")
    
    # Test 2: Security check
    print("\n" + "=" * 60)
    print("[Test 2] Security check...")
    security_issues = check_security(test_file)
    print(f"Security issues: {len(security_issues)}")
    for issue in security_issues[:3]:
        print(f"  - {issue.title} (line {issue.line_number})")
    
    # Test 3: Performance check
    print("\n" + "=" * 60)
    print("[Test 3] Performance check...")
    perf_issues = check_performance(test_file)
    print(f"Performance issues: {len(perf_issues)}")
    for issue in perf_issues:
        print(f"  - {issue.title} (line {issue.line_number})")
    
    # Test 4: Generate report
    print("\n" + "=" * 60)
    print("[Test 4] Generate report...")
    report_path = Path("/tmp/analysis_report.md")
    success = generate_analysis_report([result], report_path)
    print(f"Report generated: {success}")
    if success:
        print(f"Report saved to: {report_path}")
    
    # Cleanup
    test_file.unlink()
    if report_path.exists():
        report_path.unlink()
    
    print("\n" + "=" * 60)
    print("✅ Utility tests complete")
    print("=" * 60)

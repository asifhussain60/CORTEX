"""
Lint Validation Utility

Lightweight code quality validation using built-in checks.
Replaces heavy orchestrator (461 lines) with focused utility (~250 lines).

Core Operations:
- Lint single file (Python focus)
- Lint directory
- Check violations
- Generate lint report
- List violations by severity

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import re
import subprocess
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

class ViolationSeverity(Enum):
    """Violation severity levels."""
    CRITICAL = "critical"  # Must fix
    WARNING = "warning"    # Should fix
    INFO = "info"         # Nice to have


@dataclass
class Violation:
    """Single lint violation."""
    file_path: str
    line: int
    column: int
    rule_id: str
    message: str
    severity: ViolationSeverity
    source: str  # pylint, pycodestyle, builtin
    
    def to_dict(self) -> Dict:
        return {
            "file": self.file_path,
            "line": self.line,
            "column": self.column,
            "rule": self.rule_id,
            "message": self.message,
            "severity": self.severity.value,
            "source": self.source
        }


@dataclass
class LintResult:
    """Results from linting operation."""
    file_path: str
    violations: List[Violation] = field(default_factory=list)
    execution_time: float = 0.0
    linter_used: str = "builtin"
    
    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.CRITICAL)
    
    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.WARNING)
    
    @property
    def info_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.INFO)
    
    @property
    def total_count(self) -> int:
        return len(self.violations)


# ===== HELPER FUNCTIONS =====

def _detect_language(file_path: Path) -> str:
    """Detect programming language."""
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.cs': 'csharp'
    }
    return ext_map.get(file_path.suffix.lower(), 'unknown')


def _check_pylint_available() -> bool:
    """Check if pylint is installed."""
    try:
        result = subprocess.run(['pylint', '--version'], capture_output=True, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False


# ===== CORE OPERATION 1: LINT FILE =====

def lint_file(file_path: Path) -> LintResult:
    """
    Lint single file using available linter or built-in checks.
    
    Args:
        file_path: Path to file to lint
        
    Returns:
        LintResult with violations
    """
    logger.info(f"🔍 Linting file: {file_path.name}")
    
    start_time = time.time()
    
    if not file_path.exists():
        return LintResult(
            file_path=str(file_path),
            violations=[],
            execution_time=0.0
        )
    
    language = _detect_language(file_path)
    violations = []
    linter = "builtin"
    
    if language == 'python':
        # Try pylint first
        if _check_pylint_available():
            violations = _lint_with_pylint(file_path)
            linter = "pylint"
        else:
            # Fall back to built-in checks
            violations = _lint_python_builtin(file_path)
            linter = "builtin"
    else:
        # Use built-in checks for other languages
        violations = _lint_generic(file_path)
    
    execution_time = time.time() - start_time
    
    return LintResult(
        file_path=str(file_path),
        violations=violations,
        execution_time=execution_time,
        linter_used=linter
    )


def _lint_with_pylint(file_path: Path) -> List[Violation]:
    """Lint Python file with pylint."""
    violations = []
    
    try:
        result = subprocess.run(
            ['pylint', '--output-format=json', str(file_path)],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            import json
            data = json.loads(result.stdout)
            
            for item in data:
                severity = ViolationSeverity.WARNING
                if item.get('type') in ['error', 'fatal']:
                    severity = ViolationSeverity.CRITICAL
                elif item.get('type') == 'convention':
                    severity = ViolationSeverity.INFO
                
                violations.append(Violation(
                    file_path=str(file_path),
                    line=item.get('line', 0),
                    column=item.get('column', 0),
                    rule_id=item.get('symbol', 'unknown'),
                    message=item.get('message', ''),
                    severity=severity,
                    source='pylint'
                ))
    
    except Exception as e:
        logger.warning(f"Pylint failed: {e}, falling back to built-in checks")
        violations = _lint_python_builtin(file_path)
    
    return violations


def _lint_python_builtin(file_path: Path) -> List[Violation]:
    """Lint Python file with built-in checks."""
    violations = []
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Check line length
        if len(line) > 120:
            violations.append(Violation(
                file_path=str(file_path),
                line=i,
                column=120,
                rule_id='E501',
                message=f'Line too long ({len(line)} > 120 characters)',
                severity=ViolationSeverity.WARNING,
                source='builtin'
            ))
        
        # Check trailing whitespace
        if line.rstrip() != line.replace('\t', '    '):
            violations.append(Violation(
                file_path=str(file_path),
                line=i,
                column=len(line.rstrip()),
                rule_id='W291',
                message='Trailing whitespace',
                severity=ViolationSeverity.INFO,
                source='builtin'
            ))
        
        # Check multiple imports on one line
        if line.strip().startswith('import ') and ',' in line:
            violations.append(Violation(
                file_path=str(file_path),
                line=i,
                column=0,
                rule_id='E401',
                message='Multiple imports on one line',
                severity=ViolationSeverity.WARNING,
                source='builtin'
            ))
        
        # Check undefined names (simple heuristic)
        if re.search(r'\bNone\b\s*==\s*\w+', line) or re.search(r'\w+\s*==\s*\bNone\b', line):
            violations.append(Violation(
                file_path=str(file_path),
                line=i,
                column=0,
                rule_id='E711',
                message='Comparison to None should be "if x is None:"',
                severity=ViolationSeverity.WARNING,
                source='builtin'
            ))
    
    return violations


def _lint_generic(file_path: Path) -> List[Violation]:
    """Generic linting for non-Python files."""
    violations = []
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Check line length
        if len(line) > 120:
            violations.append(Violation(
                file_path=str(file_path),
                line=i,
                column=120,
                rule_id='line-length',
                message=f'Line too long ({len(line)} characters)',
                severity=ViolationSeverity.INFO,
                source='builtin'
            ))
        
        # Check trailing whitespace
        if line.rstrip() != line:
            violations.append(Violation(
                file_path=str(file_path),
                line=i,
                column=len(line.rstrip()),
                rule_id='trailing-whitespace',
                message='Trailing whitespace',
                severity=ViolationSeverity.INFO,
                source='builtin'
            ))
    
    return violations


# ===== CORE OPERATION 2: LINT DIRECTORY =====

def lint_directory(dir_path: Path, pattern: str = "*.py") -> List[LintResult]:
    """
    Lint all files in directory matching pattern.
    
    Args:
        dir_path: Directory to lint
        pattern: File pattern (default: *.py)
        
    Returns:
        List of LintResults
    """
    logger.info(f"📁 Linting directory: {dir_path.name} ({pattern})")
    
    results = []
    
    if not dir_path.exists():
        return results
    
    for file_path in dir_path.rglob(pattern):
        if file_path.is_file():
            results.append(lint_file(file_path))
    
    return results


# ===== CORE OPERATION 3: CHECK VIOLATIONS =====

def check_violations(results: List[LintResult], severity: ViolationSeverity = ViolationSeverity.CRITICAL) -> Dict:
    """
    Check for violations at specified severity level.
    
    Args:
        results: List of lint results
        severity: Minimum severity to check
        
    Returns:
        Dict with violation summary
    """
    logger.info(f"⚠️  Checking violations (severity: {severity.value})")
    
    violations_found = []
    
    for result in results:
        for violation in result.violations:
            if severity == ViolationSeverity.CRITICAL and violation.severity == ViolationSeverity.CRITICAL:
                violations_found.append(violation)
            elif severity == ViolationSeverity.WARNING and violation.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.WARNING]:
                violations_found.append(violation)
            elif severity == ViolationSeverity.INFO:
                violations_found.append(violation)
    
    return {
        "total_violations": len(violations_found),
        "violations": [v.to_dict() for v in violations_found],
        "files_affected": len(set(v.file_path for v in violations_found))
    }


# ===== CORE OPERATION 4: GENERATE LINT REPORT =====

def generate_lint_report(results: List[LintResult], output_path: Path) -> bool:
    """
    Generate markdown lint report.
    
    Args:
        results: List of lint results
        output_path: Path to save report
        
    Returns:
        True if successful
    """
    logger.info(f"📄 Generating lint report: {output_path.name}")
    
    try:
        # Count violations
        all_violations = []
        for result in results:
            all_violations.extend(result.violations)
        
        critical = sum(1 for v in all_violations if v.severity == ViolationSeverity.CRITICAL)
        warning = sum(1 for v in all_violations if v.severity == ViolationSeverity.WARNING)
        info = sum(1 for v in all_violations if v.severity == ViolationSeverity.INFO)
        
        # Generate report
        report = f"""# Lint Validation Report

**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Files Checked:** {len(results)}  
**Total Violations:** {len(all_violations)}

---

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | {critical} |
| 🟠 Warning | {warning} |
| 🟢 Info | {info} |

---

## Violations by File

"""
        
        for result in results:
            if not result.violations:
                continue
            
            report += f"### {Path(result.file_path).name}\n\n"
            report += f"**Violations:** {result.total_count} | **Linter:** {result.linter_used} | **Time:** {result.execution_time:.3f}s\n\n"
            
            # Group by severity
            by_severity = {
                ViolationSeverity.CRITICAL: [],
                ViolationSeverity.WARNING: [],
                ViolationSeverity.INFO: []
            }
            
            for violation in result.violations:
                by_severity[violation.severity].append(violation)
            
            for severity in [ViolationSeverity.CRITICAL, ViolationSeverity.WARNING, ViolationSeverity.INFO]:
                violations_list = by_severity[severity]
                if not violations_list:
                    continue
                
                severity_icons = {
                    ViolationSeverity.CRITICAL: "🔴",
                    ViolationSeverity.WARNING: "🟠",
                    ViolationSeverity.INFO: "🟢"
                }
                
                report += f"#### {severity_icons[severity]} {severity.value.upper()}\n\n"
                
                for violation in violations_list:
                    report += f"- Line {violation.line}: **[{violation.rule_id}]** {violation.message}\n"
                
                report += "\n"
        
        # Save report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding='utf-8')
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        return False


# ===== CORE OPERATION 5: LIST VIOLATIONS =====

def list_violations(results: List[LintResult], severity: Optional[ViolationSeverity] = None) -> List[Violation]:
    """
    List all violations, optionally filtered by severity.
    
    Args:
        results: List of lint results
        severity: Filter by severity (None = all)
        
    Returns:
        List of violations
    """
    logger.info(f"📋 Listing violations (severity: {severity.value if severity else 'all'})")
    
    violations = []
    
    for result in results:
        for violation in result.violations:
            if severity is None or violation.severity == severity:
                violations.append(violation)
    
    return violations


# ===== CLI TEST EXECUTION =====

if __name__ == "__main__":
    print("=" * 60)
    print("Lint Validation Utility - Direct Test")
    print("=" * 60)
    
    # Test 1: Lint test file
    print("\n[Test 1] Lint file with violations...")
    test_content = '''import os, sys
x = 1
if x == None:
    pass
    
# Very long line that exceeds the 120 character limit and should be flagged as a violation by the linter for being too long   
'''
    
    test_file = Path("/tmp/test_lint.py")
    test_file.write_text(test_content)
    
    result = lint_file(test_file)
    print(f"Violations found: {result.total_count}")
    print(f"Critical: {result.critical_count}, Warning: {result.warning_count}, Info: {result.info_count}")
    print(f"Linter: {result.linter_used}")
    print(f"Execution time: {result.execution_time:.3f}s")
    
    # Test 2: Check violations
    print("\n" + "=" * 60)
    print("[Test 2] Check violations...")
    check_result = check_violations([result], ViolationSeverity.WARNING)
    print(f"Total violations (warning+): {check_result['total_violations']}")
    print(f"Files affected: {check_result['files_affected']}")
    
    # Test 3: Generate report
    print("\n" + "=" * 60)
    print("[Test 3] Generate report...")
    report_path = Path("/tmp/lint_report.md")
    success = generate_lint_report([result], report_path)
    print(f"Report generated: {success}")
    if success:
        print(f"Report saved to: {report_path}")
    
    # Test 4: List violations
    print("\n" + "=" * 60)
    print("[Test 4] List violations...")
    all_violations = list_violations([result])
    print(f"Total violations: {len(all_violations)}")
    for v in all_violations[:3]:
        print(f"  - Line {v.line}: [{v.rule_id}] {v.message}")
    
    # Cleanup
    test_file.unlink()
    if report_path.exists():
        report_path.unlink()
    
    print("\n" + "=" * 60)
    print("✅ Utility tests complete")
    print("=" * 60)

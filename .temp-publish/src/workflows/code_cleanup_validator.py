"""
Code Cleanup Validator

Scans code for debug artifacts and production anti-patterns that should be
removed before session completion.

Detection Categories:
- Debug statements (print, console.log, debugger)
- Temporary code markers (TODO, FIXME, HACK)
- Commented code blocks
- Hardcoded values (localhost, passwords, API keys)

Features:
- Multi-language support (Python, C#, TypeScript, JavaScript)
- Configurable exemptions (test files, markers)
- Performance optimized (<500ms for 100 files)
- Detailed issue reporting

Version: 1.0.0
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class IssueType(Enum):
    """Types of cleanup issues."""
    DEBUG_STATEMENT = "debug_statement"
    TEMPORARY_CODE = "temporary_code"
    COMMENTED_CODE = "commented_code"
    HARDCODED_VALUE = "hardcoded_value"
    CONSOLE_OUTPUT = "console_output"


@dataclass
class CleanupIssue:
    """Represents a code cleanup issue found during validation."""
    file_path: Path
    line_number: int
    issue_type: IssueType
    message: str
    code_snippet: str
    severity: str = "WARNING"  # WARNING, CRITICAL, BLOCKED
    
    def __str__(self) -> str:
        return (
            f"[{self.severity}] {self.file_path}:{self.line_number} - "
            f"{self.issue_type.value}: {self.message}"
        )


class CodeCleanupValidator:
    """
    Validates code for production readiness by detecting debug artifacts.
    
    Usage:
        validator = CodeCleanupValidator()
        issues = validator.scan_directory(Path('src/'))
        
        if issues:
            for file_path, file_issues in issues.items():
                print(f"Issues in {file_path}:")
                for issue in file_issues:
                    print(f"  - {issue}")
    """
    
    # Debug statement patterns by language
    DEBUG_PATTERNS = {
        'python': [
            r'\bprint\s*\(',
            r'\bpdb\.set_trace\(',
            r'\bbreakpoint\(',
            r'\bimport\s+pdb',
            r'\blogger\.debug\(',
        ],
        'csharp': [
            r'\bConsole\.WriteLine\s*\(',
            r'\bConsole\.Write\s*\(',
            r'\bDebug\.WriteLine\s*\(',
            r'\bDebugger\.Break\(',
        ],
        'javascript': [
            r'\bconsole\.log\s*\(',
            r'\bconsole\.debug\s*\(',
            r'\bconsole\.trace\s*\(',
            r'\bdebugger\s*;',
            r'\balert\s*\(',
        ],
        'typescript': [
            r'\bconsole\.log\s*\(',
            r'\bconsole\.debug\s*\(',
            r'\bconsole\.trace\s*\(',
            r'\bdebugger\s*;',
        ]
    }
    
    # Temporary code markers
    TEMPORARY_MARKERS = [
        r'#\s*TODO:',
        r'#\s*FIXME:',
        r'#\s*HACK:',
        r'#\s*XXX:',
        r'//\s*TODO:',
        r'//\s*FIXME:',
        r'//\s*HACK:',
        r'//\s*XXX:',
        r'throw\s+new\s+NotImplementedException',
        r'NotImplementedError',
    ]
    
    # Hardcoded values
    HARDCODED_PATTERNS = [
        r'\b(?:localhost|127\.0\.0\.1)\b',
        r'http://example\.com',
        r'password\s*=\s*["\']',
        r'api[_-]?key\s*=\s*["\']',
        r'secret\s*=\s*["\']',
        r'token\s*=\s*["\'][^"\']{20,}',
    ]
    
    # Exemption markers
    DEFAULT_EXEMPTION_MARKERS = [
        'PRODUCTION_SAFE:',
        'PRODUCTION-SAFE:',
        'ALLOW_DEBUG:',
        'EXEMPT:',
    ]
    
    # File patterns to exclude by default
    DEFAULT_EXCLUDED_PATTERNS = [
        '**/test_*.py',  # Only exclude files starting with test_
        '**/*_test.py',  # Only exclude files ending with _test
        '**/tests/**',   # Exclude tests directories
        '**/*Test.cs',   # C# test files (PascalCase with Test suffix)
        '**/*Tests.cs',  # C# test files (PascalCase with Tests suffix)
        '**/*.spec.ts',  # TypeScript spec files
        '**/*.spec.js',  # JavaScript spec files
        '**/debug_*.py', # Debug utilities
        '**/Debug*.cs',  # C# debug files
        '**/*_debug.*',  # Debug utilities
        '**/test/**',    # test directories
        '**/__tests__/**',  # __tests__ directories
    ]
    
    def __init__(
        self,
        additional_debug_patterns: Optional[List[str]] = None,
        exemption_markers: Optional[List[str]] = None,
        excluded_paths: Optional[List[str]] = None,
        commented_code_threshold: float = 0.8
    ):
        """
        Initialize CodeCleanupValidator.
        
        Args:
            additional_debug_patterns: Additional regex patterns for debug detection
            exemption_markers: Custom exemption markers (e.g., "# PRODUCTION_SAFE:")
            excluded_paths: Glob patterns for files to exclude
            commented_code_threshold: Ratio of commented lines to flag (0.0-1.0)
        """
        self.additional_debug_patterns = additional_debug_patterns or []
        self.exemption_markers = exemption_markers or self.DEFAULT_EXEMPTION_MARKERS
        self.excluded_paths = excluded_paths or self.DEFAULT_EXCLUDED_PATTERNS
        self.commented_code_threshold = commented_code_threshold
        
        # Compile regex patterns for performance
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile all regex patterns for better performance."""
        self.compiled_debug_patterns = {
            lang: [re.compile(pattern) for pattern in patterns]
            for lang, patterns in self.DEBUG_PATTERNS.items()
        }
        
        self.compiled_temporary_markers = [
            re.compile(pattern) for pattern in self.TEMPORARY_MARKERS
        ]
        
        self.compiled_hardcoded_patterns = [
            re.compile(pattern) for pattern in self.HARDCODED_PATTERNS
        ]
        
        self.compiled_exemption_patterns = [
            re.compile(re.escape(marker)) for marker in self.exemption_markers
        ]
    
    def _is_excluded(self, file_path: Path) -> bool:
        """Check if file should be excluded from validation."""
        file_str = str(file_path).replace('\\', '/')
        file_name = file_path.name
        
        for pattern in self.excluded_paths:
            # For C# test patterns, check case-sensitively
            if pattern.endswith('.cs'):
                # Extract the filename pattern without path
                pattern_name = pattern.split('/')[-1]
                if '*Test.cs' in pattern or '*Tests.cs' in pattern:
                    # Must have capital T in Test/Tests
                    if ('Test.cs' in file_name and 'Test' in file_name) or \
                       ('Tests.cs' in file_name and 'Tests' in file_name):
                        return True
                    continue
            
            # Use glob matching for other patterns
            if file_path.match(pattern):
                return True
        return False
    
    def _get_language(self, file_path: Path) -> Optional[str]:
        """Determine language from file extension."""
        suffix = file_path.suffix.lower()
        language_map = {
            '.py': 'python',
            '.cs': 'csharp',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
        }
        return language_map.get(suffix)
    
    def _has_exemption_marker(self, line: str, previous_line: str = "") -> bool:
        """Check if line has exemption marker in current or previous line."""
        combined = f"{previous_line} {line}"
        return any(
            pattern.search(combined)
            for pattern in self.compiled_exemption_patterns
        )
    
    def _check_debug_statements(
        self,
        lines: List[str],
        language: str,
        file_path: Path
    ) -> List[CleanupIssue]:
        """Check for debug statements in code."""
        issues = []
        patterns = self.compiled_debug_patterns.get(language, [])
        
        for line_num, line in enumerate(lines, start=1):
            # Skip if exemption marker present
            previous_line = lines[line_num - 2] if line_num > 1 else ""
            if self._has_exemption_marker(line, previous_line):
                continue
            
            # Check each pattern
            for pattern in patterns:
                if pattern.search(line):
                    issues.append(CleanupIssue(
                        file_path=file_path,
                        line_number=line_num,
                        issue_type=IssueType.DEBUG_STATEMENT,
                        message=f"Debug statement found: {pattern.pattern}",
                        code_snippet=line.strip(),
                        severity="CRITICAL"
                    ))
                    break  # One issue per line
        
        return issues
    
    def _check_temporary_markers(
        self,
        lines: List[str],
        file_path: Path
    ) -> List[CleanupIssue]:
        """Check for temporary code markers (TODO, FIXME, etc.)."""
        issues = []
        
        for line_num, line in enumerate(lines, start=1):
            for pattern in self.compiled_temporary_markers:
                if pattern.search(line):
                    issues.append(CleanupIssue(
                        file_path=file_path,
                        line_number=line_num,
                        issue_type=IssueType.TEMPORARY_CODE,
                        message="Temporary code marker found",
                        code_snippet=line.strip(),
                        severity="WARNING"
                    ))
                    break
        
        return issues
    
    def _check_hardcoded_values(
        self,
        lines: List[str],
        file_path: Path
    ) -> List[CleanupIssue]:
        """Check for hardcoded sensitive values."""
        issues = []
        
        for line_num, line in enumerate(lines, start=1):
            # Skip if exemption marker present
            previous_line = lines[line_num - 2] if line_num > 1 else ""
            if self._has_exemption_marker(line, previous_line):
                continue
            
            for pattern in self.compiled_hardcoded_patterns:
                if pattern.search(line):
                    issues.append(CleanupIssue(
                        file_path=file_path,
                        line_number=line_num,
                        issue_type=IssueType.HARDCODED_VALUE,
                        message="Hardcoded value detected",
                        code_snippet=line.strip(),
                        severity="CRITICAL"
                    ))
                    break
        
        return issues
    
    def _check_commented_code(
        self,
        lines: List[str],
        file_path: Path
    ) -> List[CleanupIssue]:
        """Check for blocks of commented code."""
        issues = []
        comment_block_start = None
        consecutive_comments = 0
        
        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            
            # Detect comment lines
            is_comment = (
                stripped.startswith('#') or
                stripped.startswith('//') or
                stripped.startswith('/*') or
                stripped.startswith('*')
            )
            
            if is_comment:
                if comment_block_start is None:
                    comment_block_start = line_num
                consecutive_comments += 1
            else:
                # Check if we had a block of commented code
                if consecutive_comments >= 5:  # 5+ consecutive comment lines
                    issues.append(CleanupIssue(
                        file_path=file_path,
                        line_number=comment_block_start,
                        issue_type=IssueType.COMMENTED_CODE,
                        message=f"Block of {consecutive_comments} commented lines",
                        code_snippet=f"Lines {comment_block_start}-{line_num-1}",
                        severity="WARNING"
                    ))
                
                # Reset counters
                comment_block_start = None
                consecutive_comments = 0
        
        return issues
    
    def scan_file(self, file_path: Path) -> List[CleanupIssue]:
        """
        Scan single file for cleanup issues.
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            List of CleanupIssue objects found in file
        """
        # Check if file should be excluded
        if self._is_excluded(file_path):
            logger.debug(f"Skipping excluded file: {file_path}")
            return []
        
        # Check if file exists
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return []
        
        # Determine language
        language = self._get_language(file_path)
        if language is None:
            logger.debug(f"Unsupported file type: {file_path}")
            return []
        
        # Read file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return []
        
        # Run all checks
        issues = []
        issues.extend(self._check_debug_statements(lines, language, file_path))
        issues.extend(self._check_temporary_markers(lines, file_path))
        issues.extend(self._check_hardcoded_values(lines, file_path))
        issues.extend(self._check_commented_code(lines, file_path))
        
        return issues
    
    def scan_directory(
        self,
        dir_path: Path,
        recursive: bool = True
    ) -> Dict[Path, List[CleanupIssue]]:
        """
        Scan directory for cleanup issues.
        
        Args:
            dir_path: Path to directory to scan
            recursive: Whether to scan subdirectories
            
        Returns:
            Dictionary mapping file paths to their cleanup issues
        """
        issues_by_file = {}
        
        # Get all supported files
        patterns = ['*.py', '*.cs', '*.js', '*.ts', '*.jsx', '*.tsx']
        files = []
        
        for pattern in patterns:
            if recursive:
                files.extend(dir_path.rglob(pattern))
            else:
                files.extend(dir_path.glob(pattern))
        
        logger.info(f"Scanning {len(files)} files in {dir_path}")
        
        # Scan each file
        for file_path in files:
            file_issues = self.scan_file(file_path)
            if file_issues:
                issues_by_file[file_path] = file_issues
        
        logger.info(
            f"Found {sum(len(issues) for issues in issues_by_file.values())} "
            f"issues in {len(issues_by_file)} files"
        )
        
        return issues_by_file
    
    def validate_production_ready(
        self,
        files: List[Path]
    ) -> Tuple[bool, List[str]]:
        """
        Validate all files are production ready.
        
        Args:
            files: List of file paths to validate
            
        Returns:
            Tuple of (is_ready, blocking_issues)
            - is_ready: True if all files pass validation
            - blocking_issues: List of formatted blocking issue messages
        """
        blocking_issues = []
        
        for file_path in files:
            issues = self.scan_file(file_path)
            
            # Filter to blocking issues only
            blocking = [
                issue for issue in issues
                if issue.severity in ['CRITICAL', 'BLOCKED']
            ]
            
            if blocking:
                blocking_issues.append(
                    f"{file_path}: {len(blocking)} blocking issues"
                )
                for issue in blocking[:3]:  # Show first 3 per file
                    blocking_issues.append(f"  - Line {issue.line_number}: {issue.message}")
        
        is_ready = len(blocking_issues) == 0
        return is_ready, blocking_issues
    
    def generate_report(
        self,
        issues_by_file: Dict[Path, List[CleanupIssue]]
    ) -> str:
        """
        Generate human-readable cleanup report.
        
        Args:
            issues_by_file: Dictionary of files to their issues
            
        Returns:
            Markdown formatted report
        """
        if not issues_by_file:
            return "✅ No cleanup issues found - code is production ready!"
        
        total_issues = sum(len(issues) for issues in issues_by_file.values())
        critical_count = sum(
            1 for issues in issues_by_file.values()
            for issue in issues
            if issue.severity == 'CRITICAL'
        )
        
        report = [
            "# Code Cleanup Report",
            "",
            f"**Total Issues:** {total_issues}",
            f"**Critical Issues:** {critical_count}",
            f"**Files Affected:** {len(issues_by_file)}",
            "",
            "## Issues by File",
            ""
        ]
        
        for file_path, issues in sorted(issues_by_file.items()):
            report.append(f"### {file_path}")
            report.append("")
            
            for issue in issues:
                icon = "🔴" if issue.severity == "CRITICAL" else "⚠️"
                report.append(
                    f"{icon} **Line {issue.line_number}** - {issue.issue_type.value}"
                )
                report.append(f"   {issue.message}")
                report.append(f"   ```")
                report.append(f"   {issue.code_snippet}")
                report.append(f"   ```")
                report.append("")
        
        return "\n".join(report)


if __name__ == "__main__":
    # Demo usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python code_cleanup_validator.py <directory>")
        sys.exit(1)
    
    validator = CodeCleanupValidator()
    issues = validator.scan_directory(Path(sys.argv[1]))
    
    if issues:
        report = validator.generate_report(issues)
        print(report)
    else:
        print("✅ No cleanup issues found!")

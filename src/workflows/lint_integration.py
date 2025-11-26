"""
Lint Integration Wrapper

Executes lint validation and parses results across multiple languages and linters.

Supported Linters:
- Python: pylint, flake8, black
- C#: dotnet format, Roslynator
- JavaScript/TypeScript: eslint, prettier

Features:
- Multi-linter support with automatic detection
- Severity-based filtering (error, warning, info)
- Blocking violation detection
- Configurable via linter config files
- Performance optimized (parallel execution)

Version: 1.0.0
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import concurrent.futures

logger = logging.getLogger(__name__)


class LintSeverity(Enum):
    """Lint violation severity levels."""
    FATAL = "fatal"
    ERROR = "error"
    WARNING = "warning"
    CONVENTION = "convention"
    REFACTOR = "refactor"
    INFO = "info"


@dataclass
class Violation:
    """Represents a single lint violation."""
    file_path: Path
    line_number: int
    column: int
    rule_id: str
    message: str
    severity: LintSeverity
    linter: str
    
    def __str__(self) -> str:
        return (
            f"[{self.severity.value.upper()}] {self.file_path}:{self.line_number}:{self.column} "
            f"({self.rule_id}) {self.message}"
        )


@dataclass
class LintResult:
    """Results from linting a file or directory."""
    file_path: Path
    violations: List[Violation]
    total_violations: int
    blocking_violations: int
    passed: bool
    linter: str
    duration_seconds: float
    
    def get_violations_by_severity(self, severity: LintSeverity) -> List[Violation]:
        """Get violations filtered by severity."""
        return [v for v in self.violations if v.severity == severity]


class LintIntegration:
    """
    Wrapper for executing lint validation across multiple languages.
    
    Usage:
        lint = LintIntegration()
        result = lint.run_lint(Path('src/my_file.py'))
        
        if result.blocking_violations > 0:
            print(f"Found {result.blocking_violations} blocking violations")
            for violation in result.violations:
                if violation.severity in [LintSeverity.ERROR, LintSeverity.FATAL]:
                    print(f"  {violation}")
    """
    
    # Linter configurations by language
    LINTER_CONFIG = {
        'python': {
            'primary': 'pylint',
            'alternatives': ['flake8', 'black --check'],
            'config_file': '.pylintrc',
            'blocking_severities': [LintSeverity.ERROR, LintSeverity.FATAL]
        },
        'csharp': {
            'primary': 'dotnet format',
            'alternatives': ['roslynator analyze'],
            'config_file': '.editorconfig',
            'blocking_severities': [LintSeverity.ERROR, LintSeverity.FATAL]
        },
        'javascript': {
            'primary': 'eslint',
            'alternatives': ['prettier --check'],
            'config_file': '.eslintrc.json',
            'blocking_severities': [LintSeverity.ERROR]
        },
        'typescript': {
            'primary': 'eslint',
            'alternatives': ['prettier --check', 'tsc --noEmit'],
            'config_file': '.eslintrc.json',
            'blocking_severities': [LintSeverity.ERROR]
        }
    }
    
    def __init__(
        self,
        linters: Optional[List[str]] = None,
        blocking_severities: Optional[List[LintSeverity]] = None,
        config_files: Optional[Dict[str, str]] = None,
        parallel_execution: bool = True
    ):
        """
        Initialize LintIntegration.
        
        Args:
            linters: Specific linters to run (e.g., ['pylint', 'eslint'])
            blocking_severities: Severities that block production
            config_files: Custom config file paths by linter
            parallel_execution: Execute linters in parallel
        """
        self.linters = linters
        self.blocking_severities = blocking_severities or [
            LintSeverity.ERROR,
            LintSeverity.FATAL
        ]
        self.config_files = config_files or {}
        self.parallel_execution = parallel_execution
    
    def _get_language(self, file_path: Path) -> Optional[str]:
        """Determine language from file extension."""
        suffix = file_path.suffix.lower()
        language_map = {
            '.py': 'python',
            '.cs': 'csharp',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
        }
        return language_map.get(suffix)
    
    def _is_linter_available(self, linter_command: str) -> bool:
        """Check if linter is installed and available."""
        try:
            base_command = linter_command.split()[0]
            result = subprocess.run(
                [base_command, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _run_pylint(self, file_path: Path) -> LintResult:
        """Run pylint on Python file."""
        import time
        start = time.time()
        
        # Build command
        config_file = self.config_files.get('pylint', '.pylintrc')
        cmd = ['pylint', '--output-format=json']
        
        if Path(config_file).exists():
            cmd.extend(['--rcfile', config_file])
        
        cmd.append(str(file_path))
        
        # Execute
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse JSON output
            violations = []
            if result.stdout:
                lint_output = json.loads(result.stdout)
                for item in lint_output:
                    severity_map = {
                        'fatal': LintSeverity.FATAL,
                        'error': LintSeverity.ERROR,
                        'warning': LintSeverity.WARNING,
                        'convention': LintSeverity.CONVENTION,
                        'refactor': LintSeverity.REFACTOR,
                        'info': LintSeverity.INFO
                    }
                    
                    violations.append(Violation(
                        file_path=Path(item.get('path', file_path)),
                        line_number=item.get('line', 0),
                        column=item.get('column', 0),
                        rule_id=item.get('symbol', 'unknown'),
                        message=item.get('message', ''),
                        severity=severity_map.get(item.get('type', 'info'), LintSeverity.INFO),
                        linter='pylint'
                    ))
            
            blocking = sum(1 for v in violations if v.severity in self.blocking_severities)
            duration = time.time() - start
            
            return LintResult(
                file_path=file_path,
                violations=violations,
                total_violations=len(violations),
                blocking_violations=blocking,
                passed=blocking == 0,
                linter='pylint',
                duration_seconds=duration
            )
            
        except subprocess.TimeoutExpired:
            logger.error(f"Pylint timeout on {file_path}")
            return self._create_error_result(file_path, 'pylint', 'Timeout')
        except json.JSONDecodeError:
            logger.error(f"Failed to parse pylint output for {file_path}")
            return self._create_error_result(file_path, 'pylint', 'Parse error')
    
    def _run_eslint(self, file_path: Path) -> LintResult:
        """Run eslint on JavaScript/TypeScript file."""
        import time
        start = time.time()
        
        # Build command
        config_file = self.config_files.get('eslint', '.eslintrc.json')
        cmd = ['npx', 'eslint', '--format=json']
        
        if Path(config_file).exists():
            cmd.extend(['--config', config_file])
        
        cmd.append(str(file_path))
        
        # Execute
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse JSON output
            violations = []
            if result.stdout:
                lint_output = json.loads(result.stdout)
                for file_result in lint_output:
                    for message in file_result.get('messages', []):
                        severity_map = {
                            2: LintSeverity.ERROR,
                            1: LintSeverity.WARNING,
                            0: LintSeverity.INFO
                        }
                        
                        violations.append(Violation(
                            file_path=Path(file_result.get('filePath', file_path)),
                            line_number=message.get('line', 0),
                            column=message.get('column', 0),
                            rule_id=message.get('ruleId', 'unknown'),
                            message=message.get('message', ''),
                            severity=severity_map.get(message.get('severity', 0), LintSeverity.INFO),
                            linter='eslint'
                        ))
            
            blocking = sum(1 for v in violations if v.severity in self.blocking_severities)
            duration = time.time() - start
            
            return LintResult(
                file_path=file_path,
                violations=violations,
                total_violations=len(violations),
                blocking_violations=blocking,
                passed=blocking == 0,
                linter='eslint',
                duration_seconds=duration
            )
            
        except subprocess.TimeoutExpired:
            logger.error(f"ESLint timeout on {file_path}")
            return self._create_error_result(file_path, 'eslint', 'Timeout')
        except json.JSONDecodeError:
            logger.error(f"Failed to parse eslint output for {file_path}")
            return self._create_error_result(file_path, 'eslint', 'Parse error')
    
    def _run_dotnet_format(self, file_path: Path) -> LintResult:
        """Run dotnet format on C# file."""
        import time
        start = time.time()
        
        # dotnet format works on project level, need to find .csproj
        project_file = self._find_csproj(file_path)
        if not project_file:
            logger.warning(f"No .csproj found for {file_path}")
            return self._create_error_result(file_path, 'dotnet-format', 'No project file')
        
        # Build command
        cmd = ['dotnet', 'format', str(project_file), '--verify-no-changes', '--verbosity', 'diagnostic']
        
        # Execute
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse output (dotnet format doesn't provide JSON, parse text)
            violations = []
            for line in result.stdout.split('\n'):
                # Look for format violations
                match = re.search(r'(.+\.cs)\((\d+),(\d+)\): (.+)', line)
                if match:
                    violations.append(Violation(
                        file_path=Path(match.group(1)),
                        line_number=int(match.group(2)),
                        column=int(match.group(3)),
                        rule_id='formatting',
                        message=match.group(4),
                        severity=LintSeverity.WARNING,
                        linter='dotnet-format'
                    ))
            
            blocking = sum(1 for v in violations if v.severity in self.blocking_severities)
            duration = time.time() - start
            
            return LintResult(
                file_path=file_path,
                violations=violations,
                total_violations=len(violations),
                blocking_violations=blocking,
                passed=result.returncode == 0,
                linter='dotnet-format',
                duration_seconds=duration
            )
            
        except subprocess.TimeoutExpired:
            logger.error(f"Dotnet format timeout on {file_path}")
            return self._create_error_result(file_path, 'dotnet-format', 'Timeout')
    
    def _find_csproj(self, file_path: Path) -> Optional[Path]:
        """Find nearest .csproj file for C# file."""
        current = file_path.parent
        while current != current.parent:
            csproj_files = list(current.glob('*.csproj'))
            if csproj_files:
                return csproj_files[0]
            current = current.parent
        return None
    
    def _create_error_result(self, file_path: Path, linter: str, error: str) -> LintResult:
        """Create error result when linter fails."""
        return LintResult(
            file_path=file_path,
            violations=[],
            total_violations=0,
            blocking_violations=0,
            passed=False,
            linter=linter,
            duration_seconds=0.0
        )
    
    def run_lint(self, file_path: Path, config: Optional[Dict] = None) -> LintResult:
        """
        Run linter on single file.
        
        Args:
            file_path: Path to file to lint
            config: Optional configuration override
            
        Returns:
            LintResult with violations
        """
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return self._create_error_result(file_path, 'unknown', 'File not found')
        
        # Determine language and linter
        language = self._get_language(file_path)
        if not language:
            logger.debug(f"Unsupported file type: {file_path}")
            return self._create_error_result(file_path, 'unknown', 'Unsupported file type')
        
        # Get linter configuration
        linter_config = self.LINTER_CONFIG.get(language, {})
        linter = linter_config.get('primary')
        
        # Check if linter is available
        if not self._is_linter_available(linter):
            logger.warning(f"Linter {linter} not available")
            return self._create_error_result(file_path, linter, 'Linter not installed')
        
        # Run appropriate linter
        if linter == 'pylint':
            return self._run_pylint(file_path)
        elif linter == 'eslint':
            return self._run_eslint(file_path)
        elif linter == 'dotnet format':
            return self._run_dotnet_format(file_path)
        else:
            logger.error(f"Unknown linter: {linter}")
            return self._create_error_result(file_path, linter, 'Unknown linter')
    
    def run_lint_directory(
        self,
        dir_path: Path,
        recursive: bool = True,
        file_patterns: Optional[List[str]] = None
    ) -> Dict[Path, LintResult]:
        """
        Run linter on directory.
        
        Args:
            dir_path: Path to directory to lint
            recursive: Whether to scan subdirectories
            file_patterns: Specific file patterns to lint
            
        Returns:
            Dictionary mapping file paths to lint results
        """
        # Collect files
        patterns = file_patterns or ['*.py', '*.cs', '*.js', '*.ts', '*.jsx', '*.tsx']
        files = []
        
        for pattern in patterns:
            if recursive:
                files.extend(dir_path.rglob(pattern))
            else:
                files.extend(dir_path.glob(pattern))
        
        logger.info(f"Linting {len(files)} files in {dir_path}")
        
        # Run linting
        results = {}
        
        if self.parallel_execution and len(files) > 5:
            # Parallel execution for large file sets
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                future_to_file = {
                    executor.submit(self.run_lint, file_path): file_path
                    for file_path in files
                }
                
                for future in concurrent.futures.as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        results[file_path] = result
                    except Exception as e:
                        logger.error(f"Error linting {file_path}: {e}")
                        results[file_path] = self._create_error_result(file_path, 'unknown', str(e))
        else:
            # Sequential execution for small file sets
            for file_path in files:
                result = self.run_lint(file_path)
                results[file_path] = result
        
        logger.info(
            f"Linting complete: {len(results)} files, "
            f"{sum(r.blocking_violations for r in results.values())} blocking violations"
        )
        
        return results
    
    def get_blocking_violations(self, results: Dict[Path, LintResult]) -> List[Violation]:
        """
        Filter violations that block production.
        
        Args:
            results: Dictionary of lint results
            
        Returns:
            List of blocking violations
        """
        blocking = []
        
        for result in results.values():
            for violation in result.violations:
                if violation.severity in self.blocking_severities:
                    blocking.append(violation)
        
        return blocking
    
    def generate_report(self, results: Dict[Path, LintResult]) -> str:
        """
        Generate human-readable lint report.
        
        Args:
            results: Dictionary of lint results
            
        Returns:
            Markdown formatted report
        """
        if not results:
            return "✅ No files linted"
        
        total_violations = sum(r.total_violations for r in results.values())
        blocking_violations = sum(r.blocking_violations for r in results.values())
        passed = all(r.passed for r in results.values())
        
        report = [
            "# Lint Validation Report",
            "",
            f"**Files Linted:** {len(results)}",
            f"**Total Violations:** {total_violations}",
            f"**Blocking Violations:** {blocking_violations}",
            f"**Status:** {'✅ PASSED' if passed else '❌ FAILED'}",
            "",
            "## Results by File",
            ""
        ]
        
        for file_path, result in sorted(results.items()):
            if result.total_violations == 0:
                continue
            
            report.append(f"### {file_path}")
            report.append(f"**Linter:** {result.linter} | **Duration:** {result.duration_seconds:.2f}s")
            report.append("")
            
            for violation in result.violations:
                icon = "🔴" if violation.severity in self.blocking_severities else "⚠️"
                report.append(
                    f"{icon} **Line {violation.line_number}:{violation.column}** "
                    f"({violation.rule_id}) - {violation.message}"
                )
            
            report.append("")
        
        return "\n".join(report)


if __name__ == "__main__":
    # Demo usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python lint_integration.py <file_or_directory>")
        sys.exit(1)
    
    lint = LintIntegration()
    path = Path(sys.argv[1])
    
    if path.is_file():
        result = lint.run_lint(path)
        print(f"\nLint result for {path}:")
        print(f"  Violations: {result.total_violations}")
        print(f"  Blocking: {result.blocking_violations}")
        print(f"  Passed: {result.passed}")
    else:
        results = lint.run_lint_directory(path)
        report = lint.generate_report(results)
        print(report)

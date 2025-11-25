"""
Hardcoded Data Cleaner Module

Aggressively scans for and eliminates:
- Hardcoded file paths (absolute paths, Windows/Unix specific paths)
- Mock data masquerading as real data
- Fallback mechanisms that return fake values
- Test fixtures with hardcoded values
- Placeholder data in production code
- Default values that should be configuration-driven

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, field
import ast

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationPhase,
    OperationResult,
    OperationStatus
)

logger = logging.getLogger(__name__)


@dataclass
class HardcodedViolation:
    """Represents a single hardcoded data violation."""
    file_path: Path
    line_number: int
    violation_type: str  # 'hardcoded_path', 'mock_data', 'fallback_value', etc.
    severity: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    code_snippet: str
    suggested_fix: str
    context: str = ""


@dataclass
class HardcodedDataMetrics:
    """Metrics for hardcoded data detection."""
    files_scanned: int = 0
    violations_found: int = 0
    critical_violations: int = 0
    high_violations: int = 0
    medium_violations: int = 0
    low_violations: int = 0
    violations_by_type: Dict[str, int] = field(default_factory=dict)
    violations: List[HardcodedViolation] = field(default_factory=list)
    clean_files: int = 0


class HardcodedDataCleanerModule(BaseOperationModule):
    """
    Aggressively detects hardcoded paths, mock data, and fallback mechanisms.
    
    Detection Rules:
    
    1. HARDCODED PATHS (CRITICAL):
       - Absolute paths: C:/Users\\..., /home/user/..., /path/to/projects\\...
       - Platform-specific paths without Path() wrapper
       - Hardcoded directory separators (\\, /) instead of Path.joinpath
    
    2. MOCK DATA (HIGH):
       - unittest.mock imports in non-test files
       - @patch, @MagicMock in production code
       - Functions returning hardcoded dicts/lists without data source
       - Fake/dummy/stub data in production code
    
    3. FALLBACK VALUES (HIGH):
       - try/except returning hardcoded values on failure
       - .get() with hardcoded defaults that mask missing config
       - if/else chains with hardcoded fallbacks
       - Default values that should come from config/environment
    
    4. TEST FIXTURES (MEDIUM):
       - Hardcoded test data inside test functions
       - No use of @pytest.fixture for shared test data
       - Inline dictionaries/lists with test values
    
    5. PLACEHOLDER DATA (MEDIUM):
       - TODO/FIXME comments with temporary hardcoded values
       - Obvious placeholder strings ('test', 'example', 'dummy', 'fake')
       - Hardcoded URLs, API keys, database connections
    
    Usage:
        cleaner = HardcodedDataCleanerModule()
        result = cleaner.execute(context={
            'project_root': Path('/path/to/project'),
            'scan_paths': [Path('src'), Path('tests')],
            'exclude_patterns': ['__pycache__', '.git'],
            'fail_on_critical': True
        })
    """
    
    # Pattern definitions
    HARDCODED_PATH_PATTERNS = [
        # Windows absolute paths
        re.compile(r'["\']([A-Z]:\\[^"\']+)["\']', re.IGNORECASE),
        # Unix absolute paths
        re.compile(r'["\'](/(?:home|Users|var|etc|opt|usr)/[^"\']+)["\']'),
        # Forward/backward slashes as path separators (not using Path)
        re.compile(r'["\']([^"\']*[/\\]{2,}[^"\']*)["\']'),
        # Hardcoded project paths
        re.compile(r'["\']([^"\']*(?:PROJECTS|workspace|dev)/[^"\']+)["\']', re.IGNORECASE),
    ]
    
    MOCK_DATA_PATTERNS = [
        re.compile(r'from\s+unittest\.mock\s+import', re.IGNORECASE),
        re.compile(r'@patch\s*\(', re.IGNORECASE),
        re.compile(r'@mock\s*\(', re.IGNORECASE),
        re.compile(r'MagicMock\s*\(', re.IGNORECASE),
        re.compile(r'Mock\s*\(', re.IGNORECASE),
        re.compile(r'return\s+\{[^}]*["\'](?:fake|dummy|mock|stub|test)["\']', re.IGNORECASE),
    ]
    
    FALLBACK_VALUE_PATTERNS = [
        re.compile(r'\.get\s*\([^,)]+,\s*["\'](?!None)[^"\']+["\']', re.IGNORECASE),
        re.compile(r'except.*:\s*return\s+(?:\{|\[|["\'])', re.IGNORECASE),
        re.compile(r'if\s+not\s+\w+:\s*\w+\s*=\s*(?:\{|\[|["\'])', re.IGNORECASE),
    ]
    
    PLACEHOLDER_KEYWORDS = {
        'test', 'example', 'dummy', 'fake', 'mock', 'stub', 'sample', 
        'placeholder', 'temp', 'temporary', 'fixme', 'todo', 'xxx'
    }
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Module metadata."""
        return OperationModuleMetadata(
            module_id="hardcoded_data_cleaner",
            name="Hardcoded Data Cleaner",
            description="Aggressively detects hardcoded paths, mock data, and fallback mechanisms",
            version="1.0.0",
            author="Asif Hussain",
            phase=OperationPhase.PROCESSING,
            priority=90,
            dependencies=[],
            optional=False,
            tags=['optimization', 'code-quality', 'hardcoded-data']
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate prerequisites.
        
        Args:
            context: Shared execution context (must contain 'project_root')
        
        Returns:
            Tuple of (is_valid, issues_list)
        """
        issues = []
        
        project_root = context.get('project_root')
        if not project_root:
            issues.append("project_root not provided in context")
        elif isinstance(project_root, Path) and not project_root.exists():
            issues.append(f"Project root does not exist: {project_root}")
        elif isinstance(project_root, str):
            path = Path(project_root)
            if not path.exists():
                issues.append(f"Project root does not exist: {project_root}")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute hardcoded data detection.
        
        Args:
            context: Shared execution context with keys:
                - project_root: Root path to scan (REQUIRED)
                - scan_paths: List of paths to scan (default: ['src', 'tests'])
                - exclude_patterns: Patterns to exclude (default: ['__pycache__', '.git'])
                - fail_on_critical: Fail if critical violations found (default: True)
                - fix_automatically: Attempt to fix violations (default: False)
        
        Returns:
            OperationResult with detected violations
        """
        logger.info("=" * 80)
        logger.info("HARDCODED DATA CLEANER")
        logger.info("=" * 80)
        
        project_root = context.get('project_root')
        if not project_root:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="project_root required in context",
                errors=["project_root not provided"]
            )
        scan_paths = context.get('scan_paths', ['src', 'tests'])
        exclude_patterns = context.get('exclude_patterns', ['__pycache__', '.git', 'dist', '.venv'])
        fail_on_critical = context.get('fail_on_critical', True)
        
        metrics = HardcodedDataMetrics()
        
        try:
            # Scan all Python files
            for scan_path_str in scan_paths:
                scan_path = project_root / scan_path_str
                
                if not scan_path.exists():
                    logger.warning(f"Scan path does not exist: {scan_path}")
                    continue
                
                logger.info(f"\nScanning: {scan_path}")
                self._scan_directory(scan_path, exclude_patterns, metrics)
            
            # Categorize violations
            self._categorize_violations(metrics)
            
            # Generate report
            report = self._generate_report(metrics)
            
            # Determine success
            success = True
            status = OperationStatus.SUCCESS
            message = f"Scan complete: {metrics.violations_found} violations found"
            
            if fail_on_critical and metrics.critical_violations > 0:
                success = False
                status = OperationStatus.FAILED
                message = f"FAILED: {metrics.critical_violations} CRITICAL violations found"
            
            logger.info("\n" + "=" * 80)
            logger.info("SCAN COMPLETE")
            logger.info("=" * 80)
            logger.info(f"Files scanned: {metrics.files_scanned}")
            logger.info(f"Violations found: {metrics.violations_found}")
            logger.info(f"  CRITICAL: {metrics.critical_violations}")
            logger.info(f"  HIGH: {metrics.high_violations}")
            logger.info(f"  MEDIUM: {metrics.medium_violations}")
            logger.info(f"  LOW: {metrics.low_violations}")
            logger.info(f"Clean files: {metrics.clean_files}")
            
            return OperationResult(
                success=success,
                status=status,
                message=message,
                data={
                    'metrics': {
                        'files_scanned': metrics.files_scanned,
                        'violations_found': metrics.violations_found,
                        'critical_violations': metrics.critical_violations,
                        'high_violations': metrics.high_violations,
                        'medium_violations': metrics.medium_violations,
                        'low_violations': metrics.low_violations,
                        'violations_by_type': metrics.violations_by_type,
                        'clean_files': metrics.clean_files
                    },
                    'violations': [
                        {
                            'file': str(v.file_path),
                            'line': v.line_number,
                            'type': v.violation_type,
                            'severity': v.severity,
                            'code': v.code_snippet,
                            'fix': v.suggested_fix,
                            'context': v.context
                        }
                        for v in metrics.violations
                    ],
                    'report': report
                }
            )
        
        except Exception as e:
            logger.error(f"Hardcoded data scan failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Scan failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _scan_directory(
        self,
        directory: Path,
        exclude_patterns: List[str],
        metrics: HardcodedDataMetrics
    ) -> None:
        """
        Recursively scan directory for Python files.
        
        Args:
            directory: Directory to scan
            exclude_patterns: Patterns to exclude
            metrics: Metrics collector
        """
        for item in directory.rglob('*.py'):
            # Skip excluded patterns
            if any(pattern in str(item) for pattern in exclude_patterns):
                continue
            
            self._scan_file(item, metrics)
    
    def _scan_file(
        self,
        file_path: Path,
        metrics: HardcodedDataMetrics
    ) -> None:
        """
        Scan a single Python file for hardcoded data.
        
        Args:
            file_path: File to scan
            metrics: Metrics collector
        """
        metrics.files_scanned += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            file_violations = []
            is_test_file = 'test_' in file_path.name or '/tests/' in str(file_path).replace('\\', '/')
            
            # Scan for violations line by line
            for line_num, line in enumerate(lines, start=1):
                violations = self._scan_line(
                    file_path,
                    line_num,
                    line,
                    is_test_file
                )
                file_violations.extend(violations)
            
            # Additional AST-based analysis
            try:
                tree = ast.parse(content, filename=str(file_path))
                ast_violations = self._analyze_ast(file_path, tree, is_test_file)
                file_violations.extend(ast_violations)
            except SyntaxError:
                logger.warning(f"Syntax error in {file_path}, skipping AST analysis")
            
            # Update metrics
            if file_violations:
                metrics.violations.extend(file_violations)
                metrics.violations_found += len(file_violations)
            else:
                metrics.clean_files += 1
        
        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")
    
    def _scan_line(
        self,
        file_path: Path,
        line_num: int,
        line: str,
        is_test_file: bool
    ) -> List[HardcodedViolation]:
        """
        Scan a single line for violations.
        
        Args:
            file_path: File being scanned
            line_num: Line number
            line: Line content
            is_test_file: Whether this is a test file
        
        Returns:
            List of violations found
        """
        violations = []
        
        # Skip comments and docstrings
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            return violations
        
        # 1. Check for hardcoded paths
        for pattern in self.HARDCODED_PATH_PATTERNS:
            matches = pattern.finditer(line)
            for match in matches:
                path_value = match.group(1)
                
                # Exclude common false positives
                if self._is_path_exception(path_value, line):
                    continue
                
                violations.append(HardcodedViolation(
                    file_path=file_path,
                    line_number=line_num,
                    violation_type='hardcoded_path',
                    severity='CRITICAL',
                    code_snippet=line.strip(),
                    suggested_fix=f"Use Path() or config: Path(config.get('{self._infer_config_key(path_value)}'))",
                    context=f"Hardcoded path: {path_value}"
                ))
        
        # 2. Check for mock data in non-test files
        if not is_test_file:
            for pattern in self.MOCK_DATA_PATTERNS:
                if pattern.search(line):
                    violations.append(HardcodedViolation(
                        file_path=file_path,
                        line_number=line_num,
                        violation_type='mock_data_in_production',
                        severity='CRITICAL',
                        code_snippet=line.strip(),
                        suggested_fix="Remove mock/test code from production files",
                        context="Mock data found in non-test file"
                    ))
        
        # 3. Check for fallback values
        for pattern in self.FALLBACK_VALUE_PATTERNS:
            if pattern.search(line):
                violations.append(HardcodedViolation(
                    file_path=file_path,
                    line_number=line_num,
                    violation_type='fallback_value',
                    severity='HIGH',
                    code_snippet=line.strip(),
                    suggested_fix="Use configuration or raise exception instead of silent fallback",
                    context="Hardcoded fallback value masks missing configuration"
                ))
        
        # 4. Check for placeholder keywords
        lower_line = line.lower()
        for keyword in self.PLACEHOLDER_KEYWORDS:
            if f'"{keyword}"' in lower_line or f"'{keyword}'" in lower_line:
                # Check if it's not in a comment or test assertion
                if 'assert' not in lower_line and '#' not in line[:line.find(keyword)] if keyword in line else True:
                    violations.append(HardcodedViolation(
                        file_path=file_path,
                        line_number=line_num,
                        violation_type='placeholder_data',
                        severity='MEDIUM',
                        code_snippet=line.strip(),
                        suggested_fix=f"Replace '{keyword}' with real data source",
                        context=f"Placeholder keyword '{keyword}' found"
                    ))
                    break  # Only report once per line
        
        return violations
    
    def _is_path_exception(self, path_value: str, line: str) -> bool:
        """
        Check if a path is an acceptable exception.
        
        Args:
            path_value: Path value found
            line: Full line context
        
        Returns:
            True if this is an acceptable exception
        """
        # Allow paths in comments
        if '#' in line and line.index('#') < line.index(path_value):
            return True
        
        # Allow paths in documentation strings
        if '"""' in line or "'''" in line:
            return True
        
        # Allow relative paths
        if not path_value.startswith('/') and ':' not in path_value:
            return True
        
        # Allow paths in Path() constructor
        if 'Path(' in line:
            return True
        
        return False
    
    def _infer_config_key(self, path_value: str) -> str:
        """
        Infer a configuration key name from a path.
        
        Args:
            path_value: Path value
        
        Returns:
            Suggested config key
        """
        # Extract meaningful part of path
        parts = path_value.replace('\\', '/').split('/')
        meaningful_parts = [p for p in parts if p and p not in ['Users', 'home', 'var', 'tmp']]
        
        if meaningful_parts:
            return f"{meaningful_parts[-1].upper()}_PATH"
        
        return "PATH"
    
    def _analyze_ast(
        self,
        file_path: Path,
        tree: ast.AST,
        is_test_file: bool
    ) -> List[HardcodedViolation]:
        """
        Perform AST-based analysis for complex patterns.
        
        Args:
            file_path: File being analyzed
            tree: AST tree
            is_test_file: Whether this is a test file
        
        Returns:
            List of violations found
        """
        violations = []
        
        class HardcodedDataVisitor(ast.NodeVisitor):
            def __init__(self, violations_list):
                self.violations = violations_list
            
            def visit_Return(self, node):
                """Check for functions returning hardcoded dicts/lists."""
                if isinstance(node.value, (ast.Dict, ast.List)):
                    # Check if it's a large hardcoded structure
                    if isinstance(node.value, ast.Dict) and len(node.value.keys) > 3:
                        self.violations.append(HardcodedViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            violation_type='hardcoded_return_value',
                            severity='HIGH',
                            code_snippet=f"return {{...}} with {len(node.value.keys)} keys",
                            suggested_fix="Use configuration file, database, or API instead",
                            context="Large hardcoded dictionary return value"
                        ))
                    elif isinstance(node.value, ast.List) and len(node.value.elts) > 5:
                        self.violations.append(HardcodedViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            violation_type='hardcoded_return_value',
                            severity='HIGH',
                            code_snippet=f"return [...] with {len(node.value.elts)} items",
                            suggested_fix="Use configuration file, database, or API instead",
                            context="Large hardcoded list return value"
                        ))
                
                self.generic_visit(node)
            
            def visit_Assign(self, node):
                """Check for large hardcoded assignments."""
                if isinstance(node.value, (ast.Dict, ast.List)):
                    if isinstance(node.value, ast.Dict) and len(node.value.keys) > 5:
                        self.violations.append(HardcodedViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            violation_type='hardcoded_assignment',
                            severity='MEDIUM',
                            code_snippet=f"{{...}} with {len(node.value.keys)} keys",
                            suggested_fix="Move to configuration file or data source",
                            context="Large hardcoded dictionary assignment"
                        ))
                
                self.generic_visit(node)
        
        visitor = HardcodedDataVisitor(violations)
        visitor.visit(tree)
        
        return violations
    
    def _categorize_violations(self, metrics: HardcodedDataMetrics) -> None:
        """
        Categorize violations by severity and type.
        
        Args:
            metrics: Metrics to update
        """
        for violation in metrics.violations:
            # Count by severity
            if violation.severity == 'CRITICAL':
                metrics.critical_violations += 1
            elif violation.severity == 'HIGH':
                metrics.high_violations += 1
            elif violation.severity == 'MEDIUM':
                metrics.medium_violations += 1
            else:
                metrics.low_violations += 1
            
            # Count by type
            v_type = violation.violation_type
            metrics.violations_by_type[v_type] = metrics.violations_by_type.get(v_type, 0) + 1
    
    def _generate_report(self, metrics: HardcodedDataMetrics) -> str:
        """
        Generate human-readable report.
        
        Args:
            metrics: Collected metrics
        
        Returns:
            Formatted report
        """
        report = f"""
# Hardcoded Data Scan Report

## Summary
- **Files Scanned:** {metrics.files_scanned}
- **Clean Files:** {metrics.clean_files}
- **Violations Found:** {metrics.violations_found}
  - CRITICAL: {metrics.critical_violations}
  - HIGH: {metrics.high_violations}
  - MEDIUM: {metrics.medium_violations}
  - LOW: {metrics.low_violations}

## Violations by Type
"""
        
        for v_type, count in sorted(metrics.violations_by_type.items(), key=lambda x: x[1], reverse=True):
            report += f"- **{v_type}:** {count}\n"
        
        # Top violations (critical + high only)
        critical_high = [v for v in metrics.violations if v.severity in ['CRITICAL', 'HIGH']]
        
        if critical_high:
            report += "\n## Critical and High Severity Violations\n\n"
            
            for violation in sorted(critical_high, key=lambda v: (v.severity, str(v.file_path)))[:20]:  # Top 20
                report += f"### [{violation.severity}] {violation.file_path}:{violation.line_number}\n"
                report += f"**Type:** {violation.violation_type}\n"
                report += f"**Code:** `{violation.code_snippet}`\n"
                report += f"**Fix:** {violation.suggested_fix}\n"
                report += f"**Context:** {violation.context}\n\n"
        
        return report
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback changes (no changes made during scan).
        
        Args:
            context: Shared execution context
        
        Returns:
            Always True (nothing to rollback)
        """
        return True


def register() -> BaseOperationModule:
    """Register module with operation factory."""
    return HardcodedDataCleanerModule()

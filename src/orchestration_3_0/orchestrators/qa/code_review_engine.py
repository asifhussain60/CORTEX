"""
Code Review Engine - CORTEX 4.0

3-depth code review: QUICK, STANDARD, DEEP

Author: Asif Hussain
Date: December 10, 2025
"""

from enum import Enum
from typing import List, Dict, Any
from pathlib import Path
import ast
import re
import logging

logger = logging.getLogger(__name__)


class ReviewDepth(Enum):
    """Review depth levels."""
    QUICK = "QUICK"          # Basic syntax, style violations
    STANDARD = "STANDARD"    # + Logic errors, code smells
    DEEP = "DEEP"            # + Architecture, performance, security


class CodeReviewEngine:
    """
    Code review engine with 3 depth levels.
    """
    
    def __init__(self):
        """Initialize review engine."""
        self.patterns = self._load_patterns()
        logger.info("CodeReviewEngine initialized")
    
    def _load_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load review patterns by depth."""
        return {
            'QUICK': [
                {'name': 'line_length', 'pattern': r'.{121,}', 'severity': 'WARNING', 'message': 'Line exceeds 120 chars'},
                {'name': 'trailing_whitespace', 'pattern': r'\s+$', 'severity': 'INFO', 'message': 'Trailing whitespace'},
                {'name': 'missing_docstring', 'check': 'docstring', 'severity': 'WARNING', 'message': 'Missing docstring'},
            ],
            'STANDARD': [
                {'name': 'hardcoded_credentials', 'pattern': r'(password|secret|key)\s*=\s*["\'][^"\']+["\']', 'severity': 'HIGH', 'message': 'Hardcoded credential'},
                {'name': 'bare_except', 'pattern': r'except\s*:', 'severity': 'WARNING', 'message': 'Bare except clause'},
                {'name': 'print_statement', 'pattern': r'\bprint\s*\(', 'severity': 'INFO', 'message': 'Print statement (use logging)'},
                {'name': 'todo_comment', 'pattern': r'#\s*TODO', 'severity': 'INFO', 'message': 'TODO comment'},
            ],
            'DEEP': [
                {'name': 'complex_function', 'check': 'complexity', 'threshold': 15, 'severity': 'HIGH', 'message': 'High cyclomatic complexity'},
                {'name': 'large_function', 'check': 'lines', 'threshold': 50, 'severity': 'WARNING', 'message': 'Function exceeds 50 lines'},
                {'name': 'god_class', 'check': 'methods', 'threshold': 20, 'severity': 'HIGH', 'message': 'Class has too many methods (God Class)'},
            ]
        }
    
    def analyze_files(
        self,
        files: List[str],
        depth: ReviewDepth,
        project_path: str = '.'
    ) -> Dict[str, Any]:
        """
        Analyze files with specified depth.
        
        Args:
            files: File paths to analyze
            depth: Review depth (QUICK/STANDARD/DEEP)
            project_path: Project root path
            
        Returns:
            Review results
        """
        issues = []
        
        for file_path in files:
            full_path = Path(project_path) / file_path
            
            if not full_path.exists():
                logger.warning(f"File not found: {full_path}")
                continue
            
            if not full_path.suffix == '.py':
                logger.debug(f"Skipping non-Python file: {full_path}")
                continue
            
            file_issues = self._analyze_file(full_path, depth)
            issues.extend(file_issues)
        
        return {
            'issues': issues,
            'depth': depth.value,
            'files_analyzed': len(files)
        }
    
    def _analyze_file(self, file_path: Path, depth: ReviewDepth) -> List[Dict[str, Any]]:
        """Analyze single file."""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            # QUICK checks (always run)
            issues.extend(self._quick_checks(file_path, lines))
            
            # STANDARD checks
            if depth in [ReviewDepth.STANDARD, ReviewDepth.DEEP]:
                issues.extend(self._standard_checks(file_path, lines, content))
            
            # DEEP checks
            if depth == ReviewDepth.DEEP:
                issues.extend(self._deep_checks(file_path, content))
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            issues.append({
                'file': str(file_path),
                'line': 0,
                'severity': 'ERROR',
                'message': f"Analysis failed: {e}"
            })
        
        return issues
    
    def _quick_checks(self, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """Quick checks: syntax, style."""
        issues = []
        patterns = self.patterns['QUICK']
        
        for i, line in enumerate(lines, 1):
            # Line length
            if len(line) > 120:
                issues.append({
                    'file': str(file_path),
                    'line': i,
                    'severity': 'WARNING',
                    'message': 'Line exceeds 120 characters'
                })
            
            # Trailing whitespace
            if re.search(r'\s+$', line):
                issues.append({
                    'file': str(file_path),
                    'line': i,
                    'severity': 'INFO',
                    'message': 'Trailing whitespace'
                })
        
        return issues
    
    def _standard_checks(self, file_path: Path, lines: List[str], content: str) -> List[Dict[str, Any]]:
        """Standard checks: logic, code smells."""
        issues = []
        patterns = self.patterns['STANDARD']
        
        for i, line in enumerate(lines, 1):
            # Hardcoded credentials
            if re.search(r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
                issues.append({
                    'file': str(file_path),
                    'line': i,
                    'severity': 'HIGH',
                    'message': 'Potential hardcoded credential'
                })
            
            # Bare except
            if re.search(r'except\s*:', line):
                issues.append({
                    'file': str(file_path),
                    'line': i,
                    'severity': 'WARNING',
                    'message': 'Bare except clause - specify exception type'
                })
            
            # Print statements
            if re.search(r'\bprint\s*\(', line):
                issues.append({
                    'file': str(file_path),
                    'line': i,
                    'severity': 'INFO',
                    'message': 'Print statement - use logging instead'
                })
        
        return issues
    
    def _deep_checks(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Deep checks: architecture, complexity."""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Check function complexity
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    if complexity > 15:
                        issues.append({
                            'file': str(file_path),
                            'line': node.lineno,
                            'severity': 'HIGH',
                            'message': f'High cyclomatic complexity ({complexity}) in function {node.name}'
                        })
                    
                    # Check function length
                    func_lines = node.end_lineno - node.lineno + 1
                    if func_lines > 50:
                        issues.append({
                            'file': str(file_path),
                            'line': node.lineno,
                            'severity': 'WARNING',
                            'message': f'Function {node.name} exceeds 50 lines ({func_lines})'
                        })
                
                # Check class size (God Class)
                if isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    if len(methods) > 20:
                        issues.append({
                            'file': str(file_path),
                            'line': node.lineno,
                            'severity': 'HIGH',
                            'message': f'Class {node.name} has {len(methods)} methods (God Class pattern)'
                        })
        
        except SyntaxError as e:
            issues.append({
                'file': str(file_path),
                'line': e.lineno or 0,
                'severity': 'CRITICAL',
                'message': f'Syntax error: {e.msg}'
            })
        
        return issues
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity

"""
Performance Analyzer - CORTEX 4.0

Bottleneck detection: N+1 queries, inefficient loops, complexity

Author: Asif Hussain
Date: December 10, 2025
"""

from typing import List, Dict, Any
from pathlib import Path
import ast
import re
import logging

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """
    Performance bottleneck analyzer.
    """
    
    def __init__(self):
        """Initialize performance analyzer."""
        self.performance_patterns = self._load_performance_patterns()
        logger.info("PerformanceAnalyzer initialized")
    
    def _load_performance_patterns(self) -> List[Dict[str, Any]]:
        """Load performance anti-patterns."""
        return [
            {
                'name': 'n_plus_one_query',
                'pattern': r'for\s+\w+\s+in\s+.*:\s*\n\s*.*\.(get|filter|query)',
                'severity': 'HIGH',
                'message': 'Potential N+1 query problem'
            },
            {
                'name': 'inefficient_loop',
                'pattern': r'for\s+\w+\s+in\s+range\(len\(',
                'severity': 'WARNING',
                'message': 'Inefficient loop (use enumerate or direct iteration)'
            },
            {
                'name': 'repeated_computation',
                'pattern': r'for\s+.*:\s*\n\s*.*=.*\(.*\)',
                'severity': 'INFO',
                'message': 'Consider caching repeated computation'
            }
        ]
    
    def analyze_performance(
        self,
        files: List[str],
        project_path: str = '.'
    ) -> Dict[str, Any]:
        """
        Analyze files for performance issues.
        
        Args:
            files: File paths to analyze
            project_path: Project root path
            
        Returns:
            Performance analysis results
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
            
            file_issues = self._analyze_file(full_path)
            issues.extend(file_issues)
        
        return {
            'issues': issues,
            'files_analyzed': len(files)
        }
    
    def _analyze_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze single file for performance issues."""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Pattern-based checks
            issues.extend(self._pattern_checks(file_path, content))
            
            # AST-based checks
            issues.extend(self._ast_checks(file_path, content))
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            issues.append({
                'file': str(file_path),
                'line': 0,
                'severity': 'ERROR',
                'message': f"Analysis failed: {e}"
            })
        
        return issues
    
    def _pattern_checks(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Pattern-based performance checks."""
        issues = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # N+1 query detection
            if 'for ' in line and i + 1 < len(lines):
                next_line = lines[i]
                if re.search(r'\.(get|filter|query|find)', next_line):
                    issues.append({
                        'file': str(file_path),
                        'line': i,
                        'severity': 'HIGH',
                        'message': 'Potential N+1 query problem (database call inside loop)'
                    })
            
            # Inefficient range(len()) pattern
            if re.search(r'for\s+\w+\s+in\s+range\(len\(', line):
                issues.append({
                    'file': str(file_path),
                    'line': i,
                    'severity': 'WARNING',
                    'message': 'Inefficient loop (use enumerate() or direct iteration)'
                })
            
            # String concatenation in loops
            if 'for ' in line and i + 1 < len(lines):
                next_line = lines[i]
                if re.search(r'\+=.*["\']', next_line):
                    issues.append({
                        'file': str(file_path),
                        'line': i,
                        'severity': 'WARNING',
                        'message': 'String concatenation in loop (use list and join())'
                    })
        
        return issues
    
    def _ast_checks(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """AST-based performance checks."""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Check for nested loops
                if isinstance(node, (ast.For, ast.While)):
                    nested_loops = [n for n in ast.walk(node) if isinstance(n, (ast.For, ast.While)) and n != node]
                    if len(nested_loops) >= 2:
                        issues.append({
                            'file': str(file_path),
                            'line': node.lineno,
                            'severity': 'HIGH',
                            'message': f'Deeply nested loops (depth: {len(nested_loops) + 1}) - consider optimization'
                        })
                
                # Check for list comprehension abuse
                if isinstance(node, ast.ListComp):
                    generators = node.generators
                    if len(generators) > 2:
                        issues.append({
                            'file': str(file_path),
                            'line': node.lineno,
                            'severity': 'WARNING',
                            'message': 'Complex list comprehension - consider breaking into multiple steps'
                        })
        
        except SyntaxError:
            pass  # Already caught in code review
        
        return issues

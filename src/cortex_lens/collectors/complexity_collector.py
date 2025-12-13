"""
Complexity Collector - Analyzes code complexity metrics.

Features:
- Cyclomatic complexity per function/method
- Cognitive complexity
- Maintainability index
- Lines of code metrics (LOC, SLOC, comment ratio)
- Nesting depth analysis
- Function/method size analysis
- Complexity hotspot identification

Author: Asif Hussain
Date: December 2025
"""

import ast
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
import math

logger = logging.getLogger(__name__)


class ComplexityCollector:
    """
    Analyzes code complexity using multiple metrics.
    
    Metrics:
    - Cyclomatic Complexity: Decision points + 1
    - Cognitive Complexity: Nested decision structures
    - Maintainability Index: Halstead volume + cyclomatic + LOC
    - LOC: Physical lines, source lines, comment ratio
    - Nesting Depth: Maximum indentation levels
    """
    
    def __init__(self):
        """Initialize complexity thresholds."""
        self.complexity_thresholds = {
            'cyclomatic': {'low': 10, 'medium': 20, 'high': 50},
            'cognitive': {'low': 15, 'medium': 30, 'high': 50},
            'maintainability': {'low': 20, 'medium': 40, 'high': 60},  # Lower is worse
            'nesting': {'low': 3, 'medium': 5, 'high': 8},
            'function_length': {'low': 50, 'medium': 100, 'high': 200},
        }
        
    def collect(self, project_path: Path) -> Dict[str, Any]:
        """
        Collect complexity metrics from project.
        
        Args:
            project_path: Root path of project to analyze
            
        Returns:
            Dictionary with:
            - total_files: Number of files analyzed
            - total_functions: Total function count
            - complexity_summary: Average metrics
            - complexity_by_file: Dict[str, metrics]
            - hotspots: List of high-complexity functions
            - maintainability_score: Overall project score (0-100)
        """
        logger.info(f"📊 Starting complexity analysis on: {project_path}")
        
        results = {
            'total_files': 0,
            'total_functions': 0,
            'complexity_summary': {
                'avg_cyclomatic': 0.0,
                'avg_cognitive': 0.0,
                'avg_maintainability': 0.0,
                'avg_nesting': 0.0,
                'avg_function_length': 0.0,
            },
            'complexity_by_file': {},
            'hotspots': [],
            'maintainability_score': 0.0,
            'loc_metrics': {
                'total_lines': 0,
                'source_lines': 0,
                'comment_lines': 0,
                'blank_lines': 0,
                'comment_ratio': 0.0,
            },
        }
        
        all_metrics = []
        
        # Analyze Python files (primary support)
        for file_path in project_path.rglob('*.py'):
            if any(exclude in str(file_path) for exclude in ['node_modules', '.venv', 'venv', 'bin', '__pycache__']):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                file_metrics = self._analyze_python_file(file_path, content)
                
                if file_metrics['functions']:
                    results['total_files'] += 1
                    results['total_functions'] += len(file_metrics['functions'])
                    results['complexity_by_file'][str(file_path)] = file_metrics
                    all_metrics.extend(file_metrics['functions'])
                    
                    # Update LOC metrics
                    results['loc_metrics']['total_lines'] += file_metrics['loc']['total_lines']
                    results['loc_metrics']['source_lines'] += file_metrics['loc']['source_lines']
                    results['loc_metrics']['comment_lines'] += file_metrics['loc']['comment_lines']
                    results['loc_metrics']['blank_lines'] += file_metrics['loc']['blank_lines']
                    
            except Exception as e:
                logger.warning(f"Could not analyze {file_path}: {e}")
        
        # Calculate summary statistics
        if all_metrics:
            results['complexity_summary']['avg_cyclomatic'] = sum(m['cyclomatic'] for m in all_metrics) / len(all_metrics)
            results['complexity_summary']['avg_cognitive'] = sum(m['cognitive'] for m in all_metrics) / len(all_metrics)
            results['complexity_summary']['avg_maintainability'] = sum(m['maintainability'] for m in all_metrics) / len(all_metrics)
            results['complexity_summary']['avg_nesting'] = sum(m['max_nesting'] for m in all_metrics) / len(all_metrics)
            results['complexity_summary']['avg_function_length'] = sum(m['lines'] for m in all_metrics) / len(all_metrics)
            
            # Identify hotspots (top 10 most complex functions)
            hotspots = sorted(all_metrics, key=lambda m: m['cyclomatic'] + m['cognitive'], reverse=True)[:10]
            results['hotspots'] = hotspots
            
            # Calculate overall maintainability score
            results['maintainability_score'] = results['complexity_summary']['avg_maintainability']
        
        # Calculate comment ratio
        if results['loc_metrics']['source_lines'] > 0:
            results['loc_metrics']['comment_ratio'] = (
                results['loc_metrics']['comment_lines'] / results['loc_metrics']['source_lines']
            )
        
        logger.info(f"✅ Complexity analysis complete: {results['total_functions']} functions analyzed")
        return results
    
    def _analyze_python_file(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Analyze complexity of Python file."""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {'functions': [], 'loc': self._count_lines(content)}
        
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                metrics = self._calculate_function_complexity(node, content)
                metrics['file'] = str(file_path)
                functions.append(metrics)
        
        return {
            'functions': functions,
            'loc': self._count_lines(content),
            'avg_cyclomatic': sum(f['cyclomatic'] for f in functions) / len(functions) if functions else 0,
        }
    
    def _calculate_function_complexity(self, node: ast.FunctionDef, source: str) -> Dict[str, Any]:
        """Calculate all complexity metrics for a function."""
        cyclomatic = self._cyclomatic_complexity(node)
        cognitive = self._cognitive_complexity(node)
        max_nesting = self._max_nesting_depth(node)
        lines = self._function_lines(node)
        maintainability = self._maintainability_index(cyclomatic, lines, source)
        
        return {
            'name': node.name,
            'line': node.lineno,
            'cyclomatic': cyclomatic,
            'cognitive': cognitive,
            'maintainability': maintainability,
            'max_nesting': max_nesting,
            'lines': lines,
            'complexity_rating': self._get_complexity_rating(cyclomatic, cognitive),
        }
    
    def _cyclomatic_complexity(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity.
        
        Formula: Number of decision points + 1
        Decision points: if, elif, for, while, except, and, or, comprehensions
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Branching constructs
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            # Exception handlers
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            # Boolean operators
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            # Comprehensions
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1
            # Match statements (Python 3.10+)
            elif isinstance(child, ast.Match):
                complexity += len(getattr(child, 'cases', []))
        
        return complexity
    
    def _cognitive_complexity(self, node: ast.AST, nesting_level: int = 0) -> int:
        """
        Calculate cognitive complexity.
        
        Increments for:
        - Each nesting level increase
        - Logical operators in conditions
        - Recursion
        """
        complexity = 0
        
        for child in ast.iter_child_nodes(node):
            # Nesting increments
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1 + nesting_level
                complexity += self._cognitive_complexity(child, nesting_level + 1)
            
            # Logical operators add complexity
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            
            # Exception handlers
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1 + nesting_level
                complexity += self._cognitive_complexity(child, nesting_level + 1)
            
            # Continue with other children
            else:
                complexity += self._cognitive_complexity(child, nesting_level)
        
        return complexity
    
    def _max_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.Try)):
                child_depth = self._max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._max_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _function_lines(self, node: ast.FunctionDef) -> int:
        """Count lines in function (including decorators and docstring)."""
        # Get end line (Python 3.8+)
        if hasattr(node, 'end_lineno'):
            return node.end_lineno - node.lineno + 1
        
        # Fallback: estimate from body
        if node.body:
            last_stmt = node.body[-1]
            if hasattr(last_stmt, 'end_lineno'):
                return last_stmt.end_lineno - node.lineno + 1
            elif hasattr(last_stmt, 'lineno'):
                return last_stmt.lineno - node.lineno + 1
        
        return 1
    
    def _maintainability_index(self, cyclomatic: int, lines: int, source: str) -> float:
        """
        Calculate maintainability index (MI).
        
        Simplified formula:
        MI = 171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)
        
        Where:
        - HV = Halstead Volume (approximated)
        - CC = Cyclomatic Complexity
        - LOC = Lines of Code
        
        Returns: Score 0-100 (higher is better)
        """
        if lines == 0:
            return 100.0
        
        # Approximate Halstead volume (operators + operands)
        operators = len(re.findall(r'[+\-*/=%<>=!&|^~]|\band\b|\bor\b|\bnot\b', source))
        operands = len(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', source))
        vocabulary = operators + operands
        length = vocabulary * 2  # Simplified
        
        halstead_volume = length * math.log2(vocabulary) if vocabulary > 0 else 1
        
        # Calculate MI
        try:
            mi = 171 - 5.2 * math.log(halstead_volume) - 0.23 * cyclomatic - 16.2 * math.log(lines)
            mi = max(0, min(100, mi * 100 / 171))  # Normalize to 0-100
        except (ValueError, ZeroDivisionError):
            mi = 50.0  # Default to medium
        
        return round(mi, 2)
    
    def _count_lines(self, content: str) -> Dict[str, int]:
        """Count different types of lines."""
        lines = content.split('\n')
        
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        source_lines = total_lines - blank_lines - comment_lines
        
        return {
            'total_lines': total_lines,
            'source_lines': source_lines,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines,
        }
    
    def _get_complexity_rating(self, cyclomatic: int, cognitive: int) -> str:
        """Get human-readable complexity rating."""
        avg_complexity = (cyclomatic + cognitive) / 2
        
        if avg_complexity < 10:
            return 'LOW'
        elif avg_complexity < 20:
            return 'MEDIUM'
        elif avg_complexity < 50:
            return 'HIGH'
        else:
            return 'VERY_HIGH'

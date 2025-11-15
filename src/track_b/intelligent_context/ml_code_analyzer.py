"""
CORTEX 3.0 Track B: ML Code Analyzer
====================================

Machine Learning powered code analysis component for intelligent context extraction.
Provides semantic understanding of code changes and development patterns.

Key Features:
- Code semantic analysis using AST and pattern recognition
- Change impact analysis
- Code quality assessment
- Architectural pattern detection
- Integration with CORTEX brain for learning

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import ast
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class CodeChangeType(Enum):
    """Types of code changes detected."""
    FUNCTION_ADDED = "function_added"
    FUNCTION_MODIFIED = "function_modified"
    FUNCTION_REMOVED = "function_removed"
    CLASS_ADDED = "class_added"
    CLASS_MODIFIED = "class_modified"
    CLASS_REMOVED = "class_removed"
    IMPORT_ADDED = "import_added"
    IMPORT_REMOVED = "import_removed"
    VARIABLE_CHANGED = "variable_changed"
    LOGIC_CHANGE = "logic_change"
    DOCUMENTATION_CHANGE = "documentation_change"
    CONFIGURATION_CHANGE = "configuration_change"


@dataclass
class CodeAnalysis:
    """Results of code analysis."""
    file_path: Path
    language: str
    analysis_type: str  # 'semantic', 'structural', 'quality'
    timestamp: datetime
    findings: List[Dict[str, Any]]
    metrics: Dict[str, float]
    suggestions: List[str]
    complexity_score: float
    maintainability_score: float


@dataclass
class CodeElement:
    """Represents a code element (function, class, etc.)."""
    name: str
    element_type: str
    line_start: int
    line_end: int
    complexity: int
    dependencies: List[str]
    docstring: Optional[str] = None


class MLCodeAnalyzer:
    """
    ML-powered code analyzer for CORTEX Track B
    
    Provides intelligent analysis of code changes and development patterns
    using abstract syntax trees and pattern recognition algorithms.
    """
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.logger = logging.getLogger("cortex.track_b.ml_code_analyzer")
        
        # Supported file extensions and languages
        self.language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'csharp',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala'
        }
        
        # Code patterns for different languages
        self.patterns = {
            'python': {
                'function_def': r'def\s+(\w+)\s*\(',
                'class_def': r'class\s+(\w+)\s*\(',
                'import': r'(?:import|from)\s+(\w+)',
                'comment': r'#.*$',
                'docstring': r'""".*?"""'
            },
            'javascript': {
                'function_def': r'function\s+(\w+)\s*\(|const\s+(\w+)\s*=\s*\(',
                'class_def': r'class\s+(\w+)\s*{',
                'import': r'(?:import|require)\s*\(?[\'"]([^\'"]+)',
                'comment': r'//.*$',
                'docstring': r'/\*\*.*?\*/'
            }
        }
    
    def get_language(self, file_path: Path) -> Optional[str]:
        """Determine the programming language of a file."""
        return self.language_map.get(file_path.suffix.lower())
    
    def is_supported_file(self, file_path: Path) -> bool:
        """Check if file type is supported for analysis."""
        return self.get_language(file_path) is not None
    
    def analyze_file(self, file_path: Path) -> Optional[CodeAnalysis]:
        """Perform comprehensive analysis of a code file."""
        try:
            if not file_path.exists() or not self.is_supported_file(file_path):
                return None
            
            language = self.get_language(file_path)
            if not language:
                return None
            
            self.logger.debug(f"Analyzing {language} file: {file_path.name}")
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (OSError, UnicodeDecodeError):
                self.logger.warning(f"Could not read file: {file_path}")
                return None
            
            # Perform different types of analysis
            findings = []
            metrics = {}
            suggestions = []
            
            # Structural analysis
            structural_analysis = self._analyze_structure(content, language)
            findings.extend(structural_analysis.get('findings', []))
            metrics.update(structural_analysis.get('metrics', {}))
            
            # Semantic analysis (for Python)
            if language == 'python':
                semantic_analysis = self._analyze_python_semantics(content, file_path)
                findings.extend(semantic_analysis.get('findings', []))
                metrics.update(semantic_analysis.get('metrics', {}))
            
            # Quality analysis
            quality_analysis = self._analyze_code_quality(content, language)
            findings.extend(quality_analysis.get('findings', []))
            suggestions.extend(quality_analysis.get('suggestions', []))
            
            # Calculate overall scores
            complexity_score = self._calculate_complexity_score(content, language)
            maintainability_score = self._calculate_maintainability_score(content, language, metrics)
            
            return CodeAnalysis(
                file_path=file_path,
                language=language,
                analysis_type='comprehensive',
                timestamp=datetime.now(),
                findings=findings,
                metrics=metrics,
                suggestions=suggestions,
                complexity_score=complexity_score,
                maintainability_score=maintainability_score
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {e}")
            return None
    
    def _analyze_structure(self, content: str, language: str) -> Dict[str, Any]:
        """Analyze code structure and extract elements."""
        findings = []
        metrics = {}
        
        try:
            lines = content.split('\n')
            metrics['total_lines'] = len(lines)
            metrics['non_empty_lines'] = sum(1 for line in lines if line.strip())
            metrics['comment_lines'] = 0
            
            patterns = self.patterns.get(language, {})
            
            # Count different code elements
            functions = []
            classes = []
            imports = []
            
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Count comments
                comment_pattern = patterns.get('comment')
                if comment_pattern and re.search(comment_pattern, line):
                    metrics['comment_lines'] = metrics.get('comment_lines', 0) + 1
                
                # Find functions
                func_pattern = patterns.get('function_def')
                if func_pattern and re.search(func_pattern, line):
                    match = re.search(func_pattern, line)
                    if match:
                        func_name = next(g for g in match.groups() if g)
                        functions.append({
                            'name': func_name,
                            'line': i,
                            'type': 'function'
                        })
                
                # Find classes
                class_pattern = patterns.get('class_def')
                if class_pattern and re.search(class_pattern, line):
                    match = re.search(class_pattern, line)
                    if match:
                        class_name = match.group(1)
                        classes.append({
                            'name': class_name,
                            'line': i,
                            'type': 'class'
                        })
                
                # Find imports
                import_pattern = patterns.get('import')
                if import_pattern and re.search(import_pattern, line):
                    imports.append({'line': i, 'content': line_stripped})
            
            metrics['function_count'] = len(functions)
            metrics['class_count'] = len(classes)
            metrics['import_count'] = len(imports)
            
            # Add structural findings
            if functions:
                findings.append({
                    'type': 'structure',
                    'category': 'functions',
                    'message': f"Found {len(functions)} functions",
                    'details': functions
                })
            
            if classes:
                findings.append({
                    'type': 'structure',
                    'category': 'classes',
                    'message': f"Found {len(classes)} classes",
                    'details': classes
                })
            
            # Calculate comment ratio
            if metrics['non_empty_lines'] > 0:
                metrics['comment_ratio'] = metrics['comment_lines'] / metrics['non_empty_lines']
            
        except Exception as e:
            self.logger.error(f"Error in structural analysis: {e}")
        
        return {'findings': findings, 'metrics': metrics}
    
    def _analyze_python_semantics(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Perform semantic analysis for Python code using AST."""
        findings = []
        metrics = {}
        
        try:
            # Parse Python AST
            tree = ast.parse(content)
            
            # Extract semantic information
            analyzer = PythonASTAnalyzer()
            analyzer.visit(tree)
            
            metrics.update(analyzer.metrics)
            findings.extend(analyzer.findings)
            
        except SyntaxError as e:
            findings.append({
                'type': 'error',
                'category': 'syntax',
                'message': f"Syntax error: {e.msg}",
                'line': e.lineno
            })
        except Exception as e:
            self.logger.error(f"Error in Python semantic analysis: {e}")
        
        return {'findings': findings, 'metrics': metrics}
    
    def _analyze_code_quality(self, content: str, language: str) -> Dict[str, Any]:
        """Analyze code quality and provide suggestions."""
        findings = []
        suggestions = []
        
        try:
            lines = content.split('\n')
            
            # Check for long lines
            long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 100]
            if long_lines:
                findings.append({
                    'type': 'quality',
                    'category': 'line_length',
                    'message': f"Found {len(long_lines)} lines longer than 100 characters",
                    'lines': long_lines[:5]  # Show first 5
                })
                suggestions.append("Consider breaking long lines for better readability")
            
            # Check for TODO/FIXME comments
            todo_lines = []
            for i, line in enumerate(lines, 1):
                if re.search(r'(TODO|FIXME|HACK)', line, re.IGNORECASE):
                    todo_lines.append(i)
            
            if todo_lines:
                findings.append({
                    'type': 'quality',
                    'category': 'todos',
                    'message': f"Found {len(todo_lines)} TODO/FIXME comments",
                    'lines': todo_lines[:5]
                })
            
            # Check indentation consistency (for Python)
            if language == 'python':
                inconsistent_indent = self._check_python_indentation(lines)
                if inconsistent_indent:
                    findings.append({
                        'type': 'quality',
                        'category': 'indentation',
                        'message': "Inconsistent indentation detected",
                        'lines': inconsistent_indent[:5]
                    })
                    suggestions.append("Use consistent indentation (prefer spaces)")
            
        except Exception as e:
            self.logger.error(f"Error in quality analysis: {e}")
        
        return {'findings': findings, 'suggestions': suggestions}
    
    def _check_python_indentation(self, lines: List[str]) -> List[int]:
        """Check for inconsistent indentation in Python code."""
        inconsistent_lines = []
        
        try:
            for i, line in enumerate(lines, 1):
                if line.strip() and line.startswith(' '):
                    # Check if using spaces
                    leading_spaces = len(line) - len(line.lstrip(' '))
                    if leading_spaces % 4 != 0:  # Assuming 4-space indentation
                        inconsistent_lines.append(i)
                elif line.strip() and line.startswith('\t'):
                    # Mixed tabs and spaces can cause issues
                    if ' ' in line[:line.index(line.lstrip())]:
                        inconsistent_lines.append(i)
        except Exception:
            pass
        
        return inconsistent_lines
    
    def _calculate_complexity_score(self, content: str, language: str) -> float:
        """Calculate code complexity score (0-100, lower is better)."""
        try:
            lines = content.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            if not non_empty_lines:
                return 0.0
            
            complexity_factors = 0
            
            # Length factor
            complexity_factors += min(len(non_empty_lines) / 100, 1.0) * 20
            
            # Nesting factor (approximate)
            max_indent = 0
            for line in non_empty_lines:
                if line.strip():
                    indent = len(line) - len(line.lstrip())
                    max_indent = max(max_indent, indent)
            
            complexity_factors += min(max_indent / 20, 1.0) * 30
            
            # Control structure factor
            control_patterns = ['if', 'for', 'while', 'switch', 'try', 'catch']
            control_count = sum(len(re.findall(rf'\b{pattern}\b', content)) for pattern in control_patterns)
            complexity_factors += min(control_count / 20, 1.0) * 25
            
            # Function count factor
            func_patterns = self.patterns.get(language, {}).get('function_def', '')
            if func_patterns:
                func_count = len(re.findall(func_patterns, content))
                complexity_factors += min(func_count / 10, 1.0) * 25
            
            return min(complexity_factors, 100.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating complexity: {e}")
            return 50.0  # Default moderate complexity
    
    def _calculate_maintainability_score(self, content: str, language: str, metrics: Dict[str, float]) -> float:
        """Calculate maintainability score (0-100, higher is better)."""
        try:
            score = 100.0
            
            # Comment ratio factor
            comment_ratio = metrics.get('comment_ratio', 0)
            if comment_ratio < 0.1:
                score -= 20  # Low comment ratio
            elif comment_ratio > 0.3:
                score += 10  # Good comment ratio
            
            # Function size factor
            function_count = metrics.get('function_count', 0)
            total_lines = metrics.get('non_empty_lines', 0)
            
            if function_count > 0 and total_lines > 0:
                avg_function_size = total_lines / function_count
                if avg_function_size > 50:
                    score -= 15  # Large functions
                elif avg_function_size < 20:
                    score += 10  # Smaller functions
            
            # Line length factor
            lines = content.split('\n')
            long_lines = sum(1 for line in lines if len(line) > 100)
            if long_lines > 0:
                score -= min(long_lines * 2, 20)
            
            return max(0.0, min(score, 100.0))
            
        except Exception as e:
            self.logger.error(f"Error calculating maintainability: {e}")
            return 50.0  # Default moderate maintainability
    
    def compare_files(self, old_content: str, new_content: str, language: str) -> List[CodeChangeType]:
        """Compare two versions of a file and identify change types."""
        changes = []
        
        try:
            if language == 'python':
                changes = self._compare_python_files(old_content, new_content)
            else:
                changes = self._compare_generic_files(old_content, new_content, language)
        except Exception as e:
            self.logger.error(f"Error comparing files: {e}")
        
        return changes
    
    def _compare_python_files(self, old_content: str, new_content: str) -> List[CodeChangeType]:
        """Compare Python files using AST analysis."""
        changes = []
        
        try:
            old_tree = ast.parse(old_content) if old_content else None
            new_tree = ast.parse(new_content) if new_content else None
            
            # Extract functions and classes from both versions
            old_elements = self._extract_python_elements(old_tree) if old_tree else set()
            new_elements = self._extract_python_elements(new_tree) if new_tree else set()
            
            # Find additions, modifications, and removals
            added = new_elements - old_elements
            removed = old_elements - new_elements
            
            for element in added:
                if element.startswith('func:'):
                    changes.append(CodeChangeType.FUNCTION_ADDED)
                elif element.startswith('class:'):
                    changes.append(CodeChangeType.CLASS_ADDED)
            
            for element in removed:
                if element.startswith('func:'):
                    changes.append(CodeChangeType.FUNCTION_REMOVED)
                elif element.startswith('class:'):
                    changes.append(CodeChangeType.CLASS_REMOVED)
            
        except SyntaxError:
            # If there are syntax errors, consider it a logic change
            changes.append(CodeChangeType.LOGIC_CHANGE)
        except Exception as e:
            self.logger.error(f"Error in Python file comparison: {e}")
        
        return changes
    
    def _extract_python_elements(self, tree: ast.AST) -> Set[str]:
        """Extract function and class names from Python AST."""
        elements = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                elements.add(f"func:{node.name}")
            elif isinstance(node, ast.ClassDef):
                elements.add(f"class:{node.name}")
        
        return elements
    
    def _compare_generic_files(self, old_content: str, new_content: str, language: str) -> List[CodeChangeType]:
        """Compare non-Python files using pattern matching."""
        changes = []
        
        try:
            patterns = self.patterns.get(language, {})
            
            # Extract functions and classes using regex
            func_pattern = patterns.get('function_def')
            class_pattern = patterns.get('class_def')
            
            if func_pattern:
                old_funcs = set(re.findall(func_pattern, old_content))
                new_funcs = set(re.findall(func_pattern, new_content))
                
                if new_funcs - old_funcs:
                    changes.append(CodeChangeType.FUNCTION_ADDED)
                if old_funcs - new_funcs:
                    changes.append(CodeChangeType.FUNCTION_REMOVED)
            
            if class_pattern:
                old_classes = set(re.findall(class_pattern, old_content))
                new_classes = set(re.findall(class_pattern, new_content))
                
                if new_classes - old_classes:
                    changes.append(CodeChangeType.CLASS_ADDED)
                if old_classes - new_classes:
                    changes.append(CodeChangeType.CLASS_REMOVED)
            
            # Check for import changes
            import_pattern = patterns.get('import')
            if import_pattern:
                old_imports = set(re.findall(import_pattern, old_content))
                new_imports = set(re.findall(import_pattern, new_content))
                
                if new_imports - old_imports:
                    changes.append(CodeChangeType.IMPORT_ADDED)
                if old_imports - new_imports:
                    changes.append(CodeChangeType.IMPORT_REMOVED)
        
        except Exception as e:
            self.logger.error(f"Error in generic file comparison: {e}")
        
        return changes
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages."""
        return list(self.language_map.values())


class PythonASTAnalyzer(ast.NodeVisitor):
    """AST visitor for analyzing Python code semantics."""
    
    def __init__(self):
        self.metrics = {}
        self.findings = []
        self.function_count = 0
        self.class_count = 0
        self.import_count = 0
        self.complexity = 0
    
    def visit_FunctionDef(self, node):
        self.function_count += 1
        
        # Calculate function complexity (simplified cyclomatic complexity)
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try, ast.ExceptHandler)):
                complexity += 1
        
        if complexity > 10:
            self.findings.append({
                'type': 'complexity',
                'category': 'function',
                'message': f"Function '{node.name}' has high complexity ({complexity})",
                'line': node.lineno,
                'function': node.name
            })
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.class_count += 1
        self.generic_visit(node)
    
    def visit_Import(self, node):
        self.import_count += 1
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        self.import_count += 1
        self.generic_visit(node)
    
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def generic_visit(self, node):
        super().generic_visit(node)
        
        # Update metrics when done
        self.metrics.update({
            'ast_function_count': self.function_count,
            'ast_class_count': self.class_count,
            'ast_import_count': self.import_count,
            'ast_complexity': self.complexity
        })
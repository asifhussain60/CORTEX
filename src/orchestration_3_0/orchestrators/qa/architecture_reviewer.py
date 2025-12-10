"""
Architecture Reviewer - CORTEX 4.0

SOLID principles validation and design pattern analysis

Author: Asif Hussain
Date: December 10, 2025
"""

from typing import List, Dict, Any
from pathlib import Path
import ast
import logging

logger = logging.getLogger(__name__)


class ArchitectureReviewer:
    """
    Architecture reviewer focusing on SOLID principles.
    """
    
    def __init__(self):
        """Initialize architecture reviewer."""
        logger.info("ArchitectureReviewer initialized")
    
    def review_architecture(
        self,
        files: List[str],
        project_path: str = '.'
    ) -> Dict[str, Any]:
        """
        Review architecture and design patterns.
        
        Args:
            files: File paths to review
            project_path: Project root path
            
        Returns:
            Architecture review results
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
            
            file_issues = self._review_file(full_path)
            issues.extend(file_issues)
        
        return {
            'issues': issues,
            'files_reviewed': len(files)
        }
    
    def _review_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Review single file architecture."""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            # S - Single Responsibility Principle
            issues.extend(self._check_srp(file_path, tree))
            
            # O - Open/Closed Principle (basic checks)
            issues.extend(self._check_ocp(file_path, tree))
            
            # L - Liskov Substitution (basic checks)
            issues.extend(self._check_lsp(file_path, tree))
            
            # I - Interface Segregation (basic checks)
            issues.extend(self._check_isp(file_path, tree))
            
            # D - Dependency Inversion (basic checks)
            issues.extend(self._check_dip(file_path, tree))
        
        except Exception as e:
            logger.error(f"Error reviewing {file_path}: {e}")
            issues.append({
                'file': str(file_path),
                'line': 0,
                'severity': 'ERROR',
                'message': f"Review failed: {e}"
            })
        
        return issues
    
    def _check_srp(self, file_path: Path, tree: ast.AST) -> List[Dict[str, Any]]:
        """Check Single Responsibility Principle."""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Count responsibilities (methods)
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef) and not n.name.startswith('_')]
                
                # God Class detection
                if len(methods) > 20:
                    issues.append({
                        'file': str(file_path),
                        'line': node.lineno,
                        'severity': 'HIGH',
                        'principle': 'SRP',
                        'message': f'Class {node.name} has {len(methods)} public methods (God Class - violates SRP)'
                    })
                
                # Multiple unrelated responsibilities (heuristic)
                method_prefixes = set()
                for method in methods:
                    prefix = method.name.split('_')[0]
                    method_prefixes.add(prefix)
                
                if len(method_prefixes) > 5:
                    issues.append({
                        'file': str(file_path),
                        'line': node.lineno,
                        'severity': 'WARNING',
                        'principle': 'SRP',
                        'message': f'Class {node.name} may have multiple responsibilities ({len(method_prefixes)} distinct method prefixes)'
                    })
        
        return issues
    
    def _check_ocp(self, file_path: Path, tree: ast.AST) -> List[Dict[str, Any]]:
        """Check Open/Closed Principle."""
        issues = []
        
        for node in ast.walk(tree):
            # Check for long if/elif chains (should use polymorphism)
            if isinstance(node, ast.If):
                elif_count = 0
                current = node
                while hasattr(current, 'orelse') and current.orelse:
                    if isinstance(current.orelse[0], ast.If):
                        elif_count += 1
                        current = current.orelse[0]
                    else:
                        break
                
                if elif_count > 5:
                    issues.append({
                        'file': str(file_path),
                        'line': node.lineno,
                        'severity': 'WARNING',
                        'principle': 'OCP',
                        'message': f'Long if/elif chain ({elif_count} branches) - consider polymorphism or strategy pattern'
                    })
        
        return issues
    
    def _check_lsp(self, file_path: Path, tree: ast.AST) -> List[Dict[str, Any]]:
        """Check Liskov Substitution Principle."""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for type checking in methods (violates LSP)
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name) and child.func.id in ['isinstance', 'type']:
                            issues.append({
                                'file': str(file_path),
                                'line': child.lineno,
                                'severity': 'WARNING',
                                'principle': 'LSP',
                                'message': 'Type checking in method may violate LSP - consider polymorphism'
                            })
        
        return issues
    
    def _check_isp(self, file_path: Path, tree: ast.AST) -> List[Dict[str, Any]]:
        """Check Interface Segregation Principle."""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Fat interface detection (too many methods)
                all_methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                
                if len(all_methods) > 15:
                    issues.append({
                        'file': str(file_path),
                        'line': node.lineno,
                        'severity': 'WARNING',
                        'principle': 'ISP',
                        'message': f'Class {node.name} has {len(all_methods)} methods (Fat Interface - violates ISP)'
                    })
        
        return issues
    
    def _check_dip(self, file_path: Path, tree: ast.AST) -> List[Dict[str, Any]]:
        """Check Dependency Inversion Principle."""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for direct instantiation of concrete classes in methods
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        # Direct class instantiation (not from DI container)
                        if isinstance(child.func, ast.Name) and child.func.id[0].isupper():
                            # Check if not in __init__
                            if node.name != '__init__':
                                issues.append({
                                    'file': str(file_path),
                                    'line': child.lineno,
                                    'severity': 'INFO',
                                    'principle': 'DIP',
                                    'message': f'Direct instantiation of {child.func.id} - consider dependency injection'
                                })
        
        return issues

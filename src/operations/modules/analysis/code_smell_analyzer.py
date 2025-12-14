"""
Code Smell Analyzer - Identify common anti-patterns and technical debt.

Detects code quality issues that increase maintenance burden and
reduce code readability.

Copyright © 2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List, Callable
from dataclasses import dataclass
import ast
import logging

logger = logging.getLogger(__name__)


@dataclass
class CodeSmell:
    """Individual code smell detection."""
    smell_type: str
    file_path: str
    line_number: int
    description: str
    severity: str
    recommendation: str


class CodeSmellAnalyzer:
    """Detect code smells and anti-patterns."""
    
    def __init__(self):
        """Initialize code smell analyzer with detector functions."""
        self.smell_detectors: List[Callable] = [
            self._detect_long_methods,
            self._detect_large_classes,
            self._detect_god_objects,
            self._detect_magic_numbers,
            self._detect_deep_nesting,
            self._detect_too_many_parameters
        ]
        
    def analyze(self, target_path: Path) -> Dict[str, Any]:
        """
        Analyze code for smells and anti-patterns.
        
        Args:
            target_path: Directory or file to analyze
            
        Returns:
            Code smell analysis with recommendations
        """
        logger.info(f"Analyzing code smells in {target_path}")
        
        smells = []
        
        if target_path.is_file():
            files = [target_path]
        else:
            files = list(target_path.rglob("*.py"))
            
        for file_path in files:
            file_smells = self._analyze_file(file_path)
            smells.extend(file_smells)
            
        return {
            'smells': smells,
            'total_smells': len(smells),
            'by_type': self._group_by_type(smells),
            'by_severity': self._group_by_severity(smells),
            'priority_fixes': self._prioritize_fixes(smells)
        }
        
    def _analyze_file(self, file_path: Path) -> List[CodeSmell]:
        """Analyze single file for code smells."""
        smells = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
            for detector in self.smell_detectors:
                file_smells = detector(tree, file_path, content)
                smells.extend(file_smells)
                
        except Exception as e:
            logger.debug(f"Failed to analyze {file_path}: {e}")
            
        return smells
        
    def _detect_long_methods(
        self, 
        tree: ast.AST, 
        file_path: Path, 
        content: str
    ) -> List[CodeSmell]:
        """Detect methods exceeding 50 lines."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                lines = end_line - start_line
                
                if lines > 50:
                    smells.append(CodeSmell(
                        smell_type="long_method",
                        file_path=str(file_path),
                        line_number=start_line,
                        description=f"Method '{node.name}' has {lines} lines",
                        severity="medium",
                        recommendation="Consider breaking into smaller, focused methods"
                    ))
                    
        return smells
        
    def _detect_large_classes(
        self, 
        tree: ast.AST, 
        file_path: Path, 
        content: str
    ) -> List[CodeSmell]:
        """Detect classes with too many methods (>20)."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_count = sum(
                    1 for item in node.body 
                    if isinstance(item, ast.FunctionDef)
                )
                
                if method_count > 20:
                    smells.append(CodeSmell(
                        smell_type="large_class",
                        file_path=str(file_path),
                        line_number=node.lineno,
                        description=f"Class '{node.name}' has {method_count} methods",
                        severity="high",
                        recommendation="Consider splitting into multiple focused classes"
                    ))
                    
        return smells
        
    def _detect_god_objects(
        self, 
        tree: ast.AST, 
        file_path: Path, 
        content: str
    ) -> List[CodeSmell]:
        """Detect classes with excessive responsibilities."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Count public methods as proxy for responsibilities
                public_methods = sum(
                    1 for item in node.body 
                    if isinstance(item, ast.FunctionDef) and not item.name.startswith('_')
                )
                
                if public_methods > 15:
                    smells.append(CodeSmell(
                        smell_type="god_object",
                        file_path=str(file_path),
                        line_number=node.lineno,
                        description=f"Class '{node.name}' has {public_methods} public methods",
                        severity="high",
                        recommendation="Apply Single Responsibility Principle - split into focused classes"
                    ))
                    
        return smells
        
    def _detect_magic_numbers(
        self, 
        tree: ast.AST, 
        file_path: Path, 
        content: str
    ) -> List[CodeSmell]:
        """Detect magic numbers (unexplained numeric literals)."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                # Ignore common constants: 0, 1, 2, 10, 100
                if node.value not in [0, 1, 2, 10, 100, 0.0, 1.0]:
                    smells.append(CodeSmell(
                        smell_type="magic_number",
                        file_path=str(file_path),
                        line_number=node.lineno,
                        description=f"Magic number {node.value} without explanation",
                        severity="low",
                        recommendation="Extract to named constant with clear meaning"
                    ))
                    
        return smells
        
    def _detect_deep_nesting(
        self, 
        tree: ast.AST, 
        file_path: Path, 
        content: str
    ) -> List[CodeSmell]:
        """Detect excessive nesting (>4 levels)."""
        smells = []
        
        def check_nesting(node: ast.AST, depth: int = 0):
            if depth > 4:
                smells.append(CodeSmell(
                    smell_type="deep_nesting",
                    file_path=str(file_path),
                    line_number=getattr(node, 'lineno', 0),
                    description=f"Code nested {depth} levels deep",
                    severity="medium",
                    recommendation="Extract nested logic into separate methods"
                ))
                
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                    check_nesting(child, depth + 1)
                else:
                    check_nesting(child, depth)
                    
        check_nesting(tree)
        return smells
        
    def _detect_too_many_parameters(
        self, 
        tree: ast.AST, 
        file_path: Path, 
        content: str
    ) -> List[CodeSmell]:
        """Detect functions with too many parameters (>5)."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)
                
                if param_count > 5:
                    smells.append(CodeSmell(
                        smell_type="too_many_parameters",
                        file_path=str(file_path),
                        line_number=node.lineno,
                        description=f"Function '{node.name}' has {param_count} parameters",
                        severity="medium",
                        recommendation="Consider using parameter object or builder pattern"
                    ))
                    
        return smells
        
    def _group_by_type(self, smells: List[CodeSmell]) -> Dict[str, int]:
        """Group smells by type."""
        counts: Dict[str, int] = {}
        for smell in smells:
            counts[smell.smell_type] = counts.get(smell.smell_type, 0) + 1
        return counts
        
    def _group_by_severity(self, smells: List[CodeSmell]) -> Dict[str, int]:
        """Group smells by severity."""
        counts: Dict[str, int] = {}
        for smell in smells:
            counts[smell.severity] = counts.get(smell.severity, 0) + 1
        return counts
        
    def _prioritize_fixes(self, smells: List[CodeSmell]) -> List[str]:
        """Prioritize smells for fixing."""
        # Sort by severity: high > medium > low
        severity_order = {"high": 0, "medium": 1, "low": 2}
        sorted_smells = sorted(
            smells,
            key=lambda s: severity_order.get(s.severity, 3)
        )
        
        # Return top 10 recommendations
        return [
            f"{s.file_path}:{s.line_number} - {s.description}: {s.recommendation}"
            for s in sorted_smells[:10]
        ]

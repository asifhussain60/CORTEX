"""
Code Smell Detector for TDD Mastery Phase 3

Detects common code smells in Python code:
1. Long methods (>20 lines)
2. Duplicated code (similar AST structures)
3. Large classes (>200 lines or >10 methods)
4. Long parameter lists (>5 parameters)
5. Primitive obsession (excessive basic types)
6. Feature envy (method uses more from other classes)

Author: Asif Hussain
Date: 2025-11-21
"""

import ast
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum


class SmellSeverity(Enum):
    """Severity levels for code smells"""
    CRITICAL = "critical"  # Must fix
    HIGH = "high"          # Should fix soon
    MEDIUM = "medium"      # Consider fixing
    LOW = "low"            # Optional improvement


class SmellType(Enum):
    """Types of code smells"""
    LONG_METHOD = "long_method"
    LARGE_CLASS = "large_class"
    LONG_PARAMETER_LIST = "long_parameter_list"
    DUPLICATED_CODE = "duplicated_code"
    PRIMITIVE_OBSESSION = "primitive_obsession"
    FEATURE_ENVY = "feature_envy"
    DEAD_CODE = "dead_code"
    GOD_CLASS = "god_class"
    

@dataclass
class CodeSmell:
    """Represents a detected code smell"""
    smell_type: SmellType
    severity: SmellSeverity
    file_path: str
    line_number: int
    end_line: int
    element_name: str
    description: str
    suggestion: str
    metrics: Dict[str, any] = field(default_factory=dict)
    

@dataclass
class SmellDetectionConfig:
    """Configuration for smell detection thresholds"""
    max_method_lines: int = 20
    max_class_lines: int = 200
    max_class_methods: int = 10
    max_parameters: int = 5
    max_primitive_ratio: float = 0.7
    min_duplication_similarity: float = 0.85
    min_duplication_lines: int = 5


class CodeSmellDetector:
    """
    Detects code smells in Python source code using AST analysis
    """
    
    def __init__(self, config: Optional[SmellDetectionConfig] = None):
        self.config = config or SmellDetectionConfig()
        self.smells: List[CodeSmell] = []
        
    def detect_smells(self, file_path: str) -> List[CodeSmell]:
        """
        Detect all code smells in a Python file
        
        Args:
            file_path: Path to Python file to analyze
            
        Returns:
            List of detected code smells
        """
        self.smells = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                tree = ast.parse(source, filename=file_path)
                
            # Run all smell detectors
            self._detect_long_methods(tree, file_path, source)
            self._detect_large_classes(tree, file_path, source)
            self._detect_long_parameter_lists(tree, file_path)
            self._detect_primitive_obsession(tree, file_path)
            self._detect_feature_envy(tree, file_path)
            
        except (SyntaxError, FileNotFoundError) as e:
            # Cannot analyze files with syntax errors or missing files
            pass
            
        return self.smells
    
    def detect_duplication_across_files(
        self, 
        file_paths: List[str]
    ) -> List[CodeSmell]:
        """
        Detect duplicated code across multiple files
        
        Args:
            file_paths: List of file paths to analyze
            
        Returns:
            List of duplication smells
        """
        method_signatures: Dict[str, List[Tuple[str, ast.FunctionDef, str]]] = {}
        
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                    tree = ast.parse(source, filename=file_path)
                    
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        sig = self._get_method_signature(node)
                        if sig not in method_signatures:
                            method_signatures[sig] = []
                        method_signatures[sig].append((file_path, node, source))
                        
            except (SyntaxError, FileNotFoundError):
                continue
        
        # Find duplicates
        duplication_smells = []
        for sig, occurrences in method_signatures.items():
            if len(occurrences) >= 2:
                # Check if methods are similar enough
                for i, (file1, node1, src1) in enumerate(occurrences):
                    for file2, node2, src2 in occurrences[i+1:]:
                        similarity = self._calculate_similarity(node1, node2)
                        if similarity >= self.config.min_duplication_similarity:
                            smell = CodeSmell(
                                smell_type=SmellType.DUPLICATED_CODE,
                                severity=SmellSeverity.HIGH,
                                file_path=file1,
                                line_number=node1.lineno,
                                end_line=node1.end_lineno or node1.lineno,
                                element_name=node1.name,
                                description=f"Method '{node1.name}' duplicated in {file2}",
                                suggestion=f"Extract common logic to shared utility function",
                                metrics={
                                    "similarity": similarity,
                                    "duplicate_location": f"{file2}:{node2.lineno}",
                                    "lines": node1.end_lineno - node1.lineno + 1
                                }
                            )
                            duplication_smells.append(smell)
        
        return duplication_smells
    
    def _detect_long_methods(self, tree: ast.AST, file_path: str, source: str):
        """Detect methods that are too long"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.end_lineno and node.lineno:
                    method_lines = node.end_lineno - node.lineno + 1
                    
                    if method_lines > self.config.max_method_lines:
                        severity = self._get_severity_for_length(
                            method_lines, 
                            self.config.max_method_lines
                        )
                        
                        smell = CodeSmell(
                            smell_type=SmellType.LONG_METHOD,
                            severity=severity,
                            file_path=file_path,
                            line_number=node.lineno,
                            end_line=node.end_lineno,
                            element_name=node.name,
                            description=f"Method '{node.name}' is {method_lines} lines long",
                            suggestion=self._suggest_method_refactoring(node, source),
                            metrics={
                                "lines": method_lines,
                                "threshold": self.config.max_method_lines,
                                "complexity": self._calculate_complexity(node)
                            }
                        )
                        self.smells.append(smell)
    
    def _detect_large_classes(self, tree: ast.AST, file_path: str, source: str):
        """Detect classes that are too large"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.end_lineno and node.lineno:
                    class_lines = node.end_lineno - node.lineno + 1
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    method_count = len(methods)
                    
                    # Check line count
                    if class_lines > self.config.max_class_lines:
                        severity = self._get_severity_for_length(
                            class_lines,
                            self.config.max_class_lines
                        )
                        
                        smell = CodeSmell(
                            smell_type=SmellType.LARGE_CLASS,
                            severity=severity,
                            file_path=file_path,
                            line_number=node.lineno,
                            end_line=node.end_lineno,
                            element_name=node.name,
                            description=f"Class '{node.name}' has {class_lines} lines",
                            suggestion="Consider splitting into multiple classes with focused responsibilities",
                            metrics={
                                "lines": class_lines,
                                "methods": method_count,
                                "threshold_lines": self.config.max_class_lines
                            }
                        )
                        self.smells.append(smell)
                    
                    # Check method count (God Class)
                    if method_count > self.config.max_class_methods:
                        smell = CodeSmell(
                            smell_type=SmellType.GOD_CLASS,
                            severity=SmellSeverity.HIGH,
                            file_path=file_path,
                            line_number=node.lineno,
                            end_line=node.end_lineno,
                            element_name=node.name,
                            description=f"Class '{node.name}' has {method_count} methods (God Class)",
                            suggestion="Split into multiple classes following Single Responsibility Principle",
                            metrics={
                                "methods": method_count,
                                "threshold": self.config.max_class_methods,
                                "lines": class_lines
                            }
                        )
                        self.smells.append(smell)
    
    def _detect_long_parameter_lists(self, tree: ast.AST, file_path: str):
        """Detect functions with too many parameters"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count parameters (exclude self/cls)
                params = node.args.args
                param_count = len([p for p in params if p.arg not in ('self', 'cls')])
                
                if param_count > self.config.max_parameters:
                    severity = SmellSeverity.MEDIUM if param_count <= 7 else SmellSeverity.HIGH
                    
                    smell = CodeSmell(
                        smell_type=SmellType.LONG_PARAMETER_LIST,
                        severity=severity,
                        file_path=file_path,
                        line_number=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        element_name=node.name,
                        description=f"Function '{node.name}' has {param_count} parameters",
                        suggestion="Consider introducing a parameter object or configuration class",
                        metrics={
                            "parameters": param_count,
                            "threshold": self.config.max_parameters,
                            "param_names": [p.arg for p in params if p.arg not in ('self', 'cls')]
                        }
                    )
                    self.smells.append(smell)
    
    def _detect_primitive_obsession(self, tree: ast.AST, file_path: str):
        """Detect excessive use of primitive types instead of domain objects"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Analyze type hints
                primitive_count = 0
                total_params = 0
                
                for arg in node.args.args:
                    if arg.arg in ('self', 'cls'):
                        continue
                    total_params += 1
                    
                    if arg.annotation:
                        if self._is_primitive_type(arg.annotation):
                            primitive_count += 1
                
                if total_params > 0:
                    primitive_ratio = primitive_count / total_params
                    
                    if primitive_ratio > self.config.max_primitive_ratio and total_params >= 3:
                        smell = CodeSmell(
                            smell_type=SmellType.PRIMITIVE_OBSESSION,
                            severity=SmellSeverity.MEDIUM,
                            file_path=file_path,
                            line_number=node.lineno,
                            end_line=node.end_lineno or node.lineno,
                            element_name=node.name,
                            description=f"Function '{node.name}' uses {primitive_count}/{total_params} primitive types",
                            suggestion="Consider creating domain objects or value objects to group related primitives",
                            metrics={
                                "primitive_count": primitive_count,
                                "total_params": total_params,
                                "primitive_ratio": primitive_ratio
                            }
                        )
                        self.smells.append(smell)
    
    def _detect_feature_envy(self, tree: ast.AST, file_path: str):
        """Detect methods that use more from other classes than their own"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Analyze attribute accesses
                own_accesses = 0
                foreign_accesses = 0
                foreign_classes: Set[str] = set()
                
                for child in ast.walk(node):
                    if isinstance(child, ast.Attribute):
                        if isinstance(child.value, ast.Name):
                            if child.value.id == 'self':
                                own_accesses += 1
                            else:
                                foreign_accesses += 1
                                foreign_classes.add(child.value.id)
                
                total_accesses = own_accesses + foreign_accesses
                if total_accesses >= 5 and foreign_accesses > own_accesses * 2:
                    smell = CodeSmell(
                        smell_type=SmellType.FEATURE_ENVY,
                        severity=SmellSeverity.MEDIUM,
                        file_path=file_path,
                        line_number=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        element_name=node.name,
                        description=f"Method '{node.name}' accesses other classes {foreign_accesses} times vs own class {own_accesses} times",
                        suggestion=f"Consider moving method to {', '.join(sorted(foreign_classes)[:2])} or extracting a new class",
                        metrics={
                            "own_accesses": own_accesses,
                            "foreign_accesses": foreign_accesses,
                            "foreign_classes": list(foreign_classes)
                        }
                    )
                    self.smells.append(smell)
    
    def _get_severity_for_length(self, actual: int, threshold: int) -> SmellSeverity:
        """Calculate severity based on how much threshold is exceeded"""
        ratio = actual / threshold
        
        if ratio >= 3.0:
            return SmellSeverity.CRITICAL
        elif ratio >= 2.0:
            return SmellSeverity.HIGH
        elif ratio >= 1.5:
            return SmellSeverity.MEDIUM
        else:
            return SmellSeverity.LOW
    
    def _suggest_method_refactoring(self, node: ast.FunctionDef, source: str) -> str:
        """Generate specific refactoring suggestions for long methods"""
        # Analyze method structure
        loops = len([n for n in ast.walk(node) if isinstance(n, (ast.For, ast.While))])
        conditions = len([n for n in ast.walk(node) if isinstance(n, ast.If)])
        
        suggestions = []
        
        if loops > 2:
            suggestions.append("Extract loop logic into separate methods")
        if conditions > 3:
            suggestions.append("Consider using strategy pattern or polymorphism")
        
        suggestions.append("Break into smaller methods with clear single responsibilities")
        
        return "; ".join(suggestions)
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _get_method_signature(self, node: ast.FunctionDef) -> str:
        """Generate a signature hash for method comparison"""
        # Use AST structure, not names, for similarity detection
        sig_parts = [
            str(len(node.args.args)),
            str(len(node.body)),
            str(self._calculate_complexity(node))
        ]
        return hashlib.md5("|".join(sig_parts).encode()).hexdigest()[:8]
    
    def _calculate_similarity(self, node1: ast.FunctionDef, node2: ast.FunctionDef) -> float:
        """Calculate structural similarity between two methods"""
        # Simple similarity based on AST structure
        features1 = self._extract_features(node1)
        features2 = self._extract_features(node2)
        
        common = sum(min(features1.get(k, 0), features2.get(k, 0)) for k in set(features1) | set(features2))
        total = sum(max(features1.get(k, 0), features2.get(k, 0)) for k in set(features1) | set(features2))
        
        return common / total if total > 0 else 0.0
    
    def _extract_features(self, node: ast.FunctionDef) -> Dict[str, int]:
        """Extract structural features from AST node"""
        features = {
            "if": 0,
            "for": 0,
            "while": 0,
            "call": 0,
            "assign": 0,
            "return": 0
        }
        
        for child in ast.walk(node):
            node_type = type(child).__name__.lower()
            if node_type in features:
                features[node_type] += 1
        
        return features
    
    def _is_primitive_type(self, annotation: ast.AST) -> bool:
        """Check if type annotation is a primitive type"""
        if isinstance(annotation, ast.Name):
            return annotation.id in ('int', 'str', 'float', 'bool', 'bytes')
        return False
    
    def get_smells_by_severity(self, severity: SmellSeverity) -> List[CodeSmell]:
        """Filter smells by severity level"""
        return [s for s in self.smells if s.severity == severity]
    
    def get_smells_by_type(self, smell_type: SmellType) -> List[CodeSmell]:
        """Filter smells by type"""
        return [s for s in self.smells if s.smell_type == smell_type]
    
    def generate_report(self) -> Dict[str, any]:
        """Generate summary report of detected smells"""
        return {
            "total_smells": len(self.smells),
            "by_severity": {
                severity.value: len(self.get_smells_by_severity(severity))
                for severity in SmellSeverity
            },
            "by_type": {
                smell_type.value: len(self.get_smells_by_type(smell_type))
                for smell_type in SmellType
            },
            "critical_issues": [
                {
                    "type": s.smell_type.value,
                    "location": f"{s.file_path}:{s.line_number}",
                    "element": s.element_name,
                    "description": s.description
                }
                for s in self.get_smells_by_severity(SmellSeverity.CRITICAL)
            ]
        }

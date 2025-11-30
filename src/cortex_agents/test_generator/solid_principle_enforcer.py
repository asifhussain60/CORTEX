"""
SOLID Principle Enforcer for TDD Mastery Phase 3

Detects violations of SOLID principles:
1. SRP - Single Responsibility Principle
2. OCP - Open/Closed Principle
3. LSP - Liskov Substitution Principle
4. ISP - Interface Segregation Principle
5. DIP - Dependency Inversion Principle

Author: Asif Hussain
Date: 2025-11-21
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum


class SOLIDPrinciple(Enum):
    """SOLID principles"""
    SRP = "single_responsibility"
    OCP = "open_closed"
    LSP = "liskov_substitution"
    ISP = "interface_segregation"
    DIP = "dependency_inversion"


class ViolationSeverity(Enum):
    """Severity of SOLID violations"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SOLIDViolation:
    """Represents a SOLID principle violation"""
    principle: SOLIDPrinciple
    severity: ViolationSeverity
    file_path: str
    line_number: int
    end_line: int
    element_name: str
    description: str
    suggestion: str
    evidence: Dict[str, any] = field(default_factory=dict)


class SOLIDPrincipleEnforcer:
    """
    Detects SOLID principle violations in Python code
    """
    
    def __init__(self):
        self.violations: List[SOLIDViolation] = []
    
    def check_file(self, file_path: str) -> List[SOLIDViolation]:
        """
        Check a Python file for SOLID violations
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of detected violations
        """
        self.violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                tree = ast.parse(source, filename=file_path)
            
            # Check each SOLID principle
            self._check_srp(tree, file_path)
            self._check_ocp(tree, file_path)
            self._check_lsp(tree, file_path)
            self._check_isp(tree, file_path)
            self._check_dip(tree, file_path)
            
        except (SyntaxError, FileNotFoundError):
            pass
        
        return self.violations
    
    def _check_srp(self, tree: ast.AST, file_path: str):
        """Check Single Responsibility Principle"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Analyze class responsibilities
                responsibilities = self._identify_responsibilities(node)
                
                if len(responsibilities) > 1:
                    severity = ViolationSeverity.HIGH if len(responsibilities) > 3 else ViolationSeverity.MEDIUM
                    
                    violation = SOLIDViolation(
                        principle=SOLIDPrinciple.SRP,
                        severity=severity,
                        file_path=file_path,
                        line_number=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        element_name=node.name,
                        description=f"Class '{node.name}' has {len(responsibilities)} responsibilities: {', '.join(responsibilities)}",
                        suggestion=f"Split into separate classes, one for each responsibility",
                        evidence={
                            "responsibilities": responsibilities,
                            "method_count": len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                        }
                    )
                    self.violations.append(violation)
    
    def _check_ocp(self, tree: ast.AST, file_path: str):
        """Check Open/Closed Principle"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for type-checking anti-patterns
                type_checks = self._find_type_checks(node)
                
                if type_checks and len(type_checks) >= 3:
                    violation = SOLIDViolation(
                        principle=SOLIDPrinciple.OCP,
                        severity=ViolationSeverity.MEDIUM,
                        file_path=file_path,
                        line_number=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        element_name=node.name,
                        description=f"Function '{node.name}' uses {len(type_checks)} type checks (violates OCP)",
                        suggestion="Use polymorphism or strategy pattern instead of type checking",
                        evidence={
                            "type_checks": type_checks,
                            "line_numbers": [tc['line'] for tc in type_checks]
                        }
                    )
                    self.violations.append(violation)
            
            elif isinstance(node, ast.ClassDef):
                # Check for hardcoded behavior
                hardcoded_values = self._find_hardcoded_behavior(node)
                
                if hardcoded_values and len(hardcoded_values) >= 5:
                    violation = SOLIDViolation(
                        principle=SOLIDPrinciple.OCP,
                        severity=ViolationSeverity.LOW,
                        file_path=file_path,
                        line_number=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        element_name=node.name,
                        description=f"Class '{node.name}' has {len(hardcoded_values)} hardcoded values",
                        suggestion="Extract configuration or use dependency injection",
                        evidence={"hardcoded_count": len(hardcoded_values)}
                    )
                    self.violations.append(violation)
    
    def _check_lsp(self, tree: ast.AST, file_path: str):
        """Check Liskov Substitution Principle"""
        classes = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
        
        for class_name, class_node in classes.items():
            # Find base classes
            base_classes = [b.id for b in class_node.bases if isinstance(b, ast.Name)]
            
            for base_name in base_classes:
                if base_name in classes:
                    base_node = classes[base_name]
                    
                    # Check if subclass narrows preconditions
                    violations_found = self._check_precondition_narrowing(class_node, base_node)
                    
                    if violations_found:
                        violation = SOLIDViolation(
                            principle=SOLIDPrinciple.LSP,
                            severity=ViolationSeverity.HIGH,
                            file_path=file_path,
                            line_number=class_node.lineno,
                            end_line=class_node.end_lineno or class_node.lineno,
                            element_name=class_name,
                            description=f"Class '{class_name}' may violate LSP by narrowing preconditions from '{base_name}'",
                            suggestion="Ensure subclass accepts all inputs base class accepts",
                            evidence={"base_class": base_name, "issues": violations_found}
                        )
                        self.violations.append(violation)
    
    def _check_isp(self, tree: ast.AST, file_path: str):
        """Check Interface Segregation Principle"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Find abstract base classes (interfaces)
                if self._is_interface(node):
                    method_count = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                    
                    # Fat interface detection
                    if method_count > 10:
                        violation = SOLIDViolation(
                            principle=SOLIDPrinciple.ISP,
                            severity=ViolationSeverity.MEDIUM,
                            file_path=file_path,
                            line_number=node.lineno,
                            end_line=node.end_lineno or node.lineno,
                            element_name=node.name,
                            description=f"Interface '{node.name}' has {method_count} methods (fat interface)",
                            suggestion="Split into smaller, more focused interfaces",
                            evidence={"method_count": method_count}
                        )
                        self.violations.append(violation)
    
    def _check_dip(self, tree: ast.AST, file_path: str):
        """Check Dependency Inversion Principle"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Look for direct instantiation of concrete classes
                concrete_dependencies = self._find_concrete_dependencies(node)
                
                if concrete_dependencies and len(concrete_dependencies) >= 3:
                    violation = SOLIDViolation(
                        principle=SOLIDPrinciple.DIP,
                        severity=ViolationSeverity.MEDIUM,
                        file_path=file_path,
                        line_number=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        element_name=node.name,
                        description=f"Class '{node.name}' directly instantiates {len(concrete_dependencies)} concrete classes",
                        suggestion="Use dependency injection and depend on abstractions",
                        evidence={
                            "concrete_dependencies": concrete_dependencies,
                            "count": len(concrete_dependencies)
                        }
                    )
                    self.violations.append(violation)
    
    def _identify_responsibilities(self, class_node: ast.ClassDef) -> List[str]:
        """
        Identify different responsibilities in a class
        
        Heuristics:
        - Method name prefixes (get_, set_, save_, load_, calculate_, validate_)
        - Different data types being manipulated
        - External systems being accessed
        """
        responsibilities = set()
        
        # Check method prefixes
        prefixes = {
            'get': 'data_access',
            'set': 'data_access',
            'fetch': 'data_access',
            'load': 'persistence',
            'save': 'persistence',
            'store': 'persistence',
            'delete': 'persistence',
            'calculate': 'business_logic',
            'compute': 'business_logic',
            'process': 'business_logic',
            'validate': 'validation',
            'check': 'validation',
            'verify': 'validation',
            'send': 'communication',
            'notify': 'communication',
            'emit': 'communication',
            'render': 'presentation',
            'display': 'presentation',
            'format': 'presentation'
        }
        
        for method in class_node.body:
            if isinstance(method, ast.FunctionDef):
                method_name = method.name.lower()
                
                for prefix, responsibility in prefixes.items():
                    if method_name.startswith(prefix):
                        responsibilities.add(responsibility)
                        break
        
        return sorted(list(responsibilities))
    
    def _find_type_checks(self, node: ast.FunctionDef) -> List[Dict[str, any]]:
        """Find isinstance() or type() checks"""
        type_checks = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id in ('isinstance', 'type'):
                        type_checks.append({
                            'line': child.lineno,
                            'function': child.func.id
                        })
        
        return type_checks
    
    def _find_hardcoded_behavior(self, class_node: ast.ClassDef) -> List[any]:
        """Find hardcoded strings and numbers that should be configurable"""
        hardcoded = []
        
        for node in ast.walk(class_node):
            if isinstance(node, (ast.Constant, ast.Num, ast.Str)):
                # Skip docstrings and common values
                if isinstance(node, ast.Constant):
                    if isinstance(node.value, str) and len(node.value) > 20:
                        hardcoded.append(node.value[:30])
                    elif isinstance(node.value, (int, float)) and node.value not in (0, 1, -1, 2):
                        hardcoded.append(node.value)
        
        return hardcoded[:10]  # Limit to first 10
    
    def _check_precondition_narrowing(
        self, 
        subclass: ast.ClassDef, 
        base_class: ast.ClassDef
    ) -> List[str]:
        """Check if subclass narrows preconditions"""
        issues = []
        
        # Get method signatures
        subclass_methods = {
            m.name: m for m in subclass.body if isinstance(m, ast.FunctionDef)
        }
        base_methods = {
            m.name: m for m in base_class.body if isinstance(m, ast.FunctionDef)
        }
        
        # Check overridden methods
        for method_name in subclass_methods:
            if method_name in base_methods:
                sub_method = subclass_methods[method_name]
                base_method = base_methods[method_name]
                
                # Check if subclass has more restrictive parameters
                sub_params = len(sub_method.args.args)
                base_params = len(base_method.args.args)
                
                if sub_params < base_params:
                    issues.append(f"Method '{method_name}' has fewer parameters than base")
                
                # Check for additional type constraints
                sub_annotations = [
                    arg.annotation for arg in sub_method.args.args if arg.annotation
                ]
                if sub_annotations:
                    issues.append(f"Method '{method_name}' adds type constraints")
        
        return issues
    
    def _is_interface(self, class_node: ast.ClassDef) -> bool:
        """Check if class is likely an interface/abstract base class"""
        # Check for ABC inheritance
        for base in class_node.bases:
            if isinstance(base, ast.Name) and 'ABC' in base.id:
                return True
        
        # Check if all methods are abstract or pass-only
        methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
        if not methods:
            return False
        
        abstract_methods = 0
        for method in methods:
            # Check for @abstractmethod decorator
            for decorator in method.decorator_list:
                if isinstance(decorator, ast.Name) and 'abstract' in decorator.id.lower():
                    abstract_methods += 1
                    break
            else:
                # Check if method body is just pass/NotImplementedError
                if len(method.body) == 1:
                    if isinstance(method.body[0], ast.Pass):
                        abstract_methods += 1
                    elif isinstance(method.body[0], ast.Raise):
                        if isinstance(method.body[0].exc, ast.Call):
                            if isinstance(method.body[0].exc.func, ast.Name):
                                if method.body[0].exc.func.id == 'NotImplementedError':
                                    abstract_methods += 1
        
        return abstract_methods / len(methods) > 0.5
    
    def _find_concrete_dependencies(self, class_node: ast.ClassDef) -> List[str]:
        """Find direct instantiation of concrete classes"""
        concrete_deps = set()
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.Call):
                # Look for Class() calls
                if isinstance(node.func, ast.Name):
                    # Skip built-in types
                    if node.func.id[0].isupper() and node.func.id not in (
                        'List', 'Dict', 'Set', 'Tuple', 'Optional', 'Union'
                    ):
                        concrete_deps.add(node.func.id)
        
        return sorted(list(concrete_deps))
    
    def get_violations_by_principle(
        self, 
        principle: SOLIDPrinciple
    ) -> List[SOLIDViolation]:
        """Filter violations by SOLID principle"""
        return [v for v in self.violations if v.principle == principle]
    
    def get_violations_by_severity(
        self, 
        severity: ViolationSeverity
    ) -> List[SOLIDViolation]:
        """Filter violations by severity"""
        return [v for v in self.violations if v.severity == severity]
    
    def generate_report(self) -> Dict[str, any]:
        """Generate summary report of SOLID violations"""
        return {
            "total_violations": len(self.violations),
            "by_principle": {
                principle.value: len(self.get_violations_by_principle(principle))
                for principle in SOLIDPrinciple
            },
            "by_severity": {
                severity.value: len(self.get_violations_by_severity(severity))
                for severity in ViolationSeverity
            },
            "critical_violations": [
                {
                    "principle": v.principle.value,
                    "location": f"{v.file_path}:{v.line_number}",
                    "element": v.element_name,
                    "description": v.description
                }
                for v in self.get_violations_by_severity(ViolationSeverity.CRITICAL)
            ]
        }

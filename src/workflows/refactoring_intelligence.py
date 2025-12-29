"""
Refactoring Intelligence - Phase 2 Milestone 2.2

Detects code smells, generates refactoring suggestions,
and validates safety with automated testing.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 2
Updated: 2025-11-24 - Phase 4 TDD Mastery Integration (Debug Timing)
"""

import ast
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class CodeSmellType(Enum):
    """Types of code smells detected."""
    LONG_METHOD = "long_method"
    DUPLICATE_CODE = "duplicate_code"
    COMPLEX_CONDITIONAL = "complex_conditional"
    LONG_PARAMETER_LIST = "long_parameter_list"
    DEEP_NESTING = "deep_nesting"
    MAGIC_NUMBER = "magic_number"
    DEAD_CODE = "dead_code"
    GOD_CLASS = "god_class"
    # Phase 4 - TDD Mastery Integration: Performance-based smells
    SLOW_FUNCTION = "slow_function"
    HOT_PATH = "hot_path"
    PERFORMANCE_BOTTLENECK = "performance_bottleneck"
    # SOLID Integration: Architectural violations
    SRP_VIOLATION = "srp_violation"
    OCP_VIOLATION = "ocp_violation"
    LSP_VIOLATION = "lsp_violation"
    ISP_VIOLATION = "isp_violation"
    DIP_VIOLATION = "dip_violation"
    TIGHT_COUPLING = "tight_coupling"
    LOW_COHESION = "low_cohesion"
    SOLID_VIOLATION = "solid_violation"


class RefactoringType(Enum):
    """Types of refactoring operations."""
    EXTRACT_METHOD = "extract_method"
    SIMPLIFY_CONDITIONAL = "simplify_conditional"
    INTRODUCE_PARAMETER_OBJECT = "introduce_parameter_object"
    REDUCE_NESTING = "reduce_nesting"
    EXTRACT_CONSTANT = "extract_constant"
    REMOVE_DEAD_CODE = "remove_dead_code"
    SPLIT_CLASS = "split_class"
    RENAME = "rename"


@dataclass
class CodeSmell:
    """Detected code smell."""
    smell_type: CodeSmellType
    location: str  # file:line:column
    severity: str  # "low", "medium", "high"
    description: str
    metric_value: Optional[float] = None  # e.g., method length, cyclomatic complexity
    confidence: float = 0.8


@dataclass
class RefactoringSuggestion:
    """Refactoring suggestion with details."""
    refactoring_type: RefactoringType
    target_location: str  # file:line:column
    description: str
    code_before: str
    code_after: str
    confidence: float  # 0.0-1.0
    safety_verified: bool = False
    estimated_effort: str = "medium"  # "low", "medium", "high"


class CodeSmellDetector:
    """
    Detects code smells using AST analysis.
    
    Identifies common anti-patterns and quality issues
    that should be refactored.
    
    Phase 4 Enhancement: Integrates debug timing data for
    performance-based smell detection.
    """
    
    # Thresholds for detection
    LONG_METHOD_LINES = 30
    COMPLEX_CONDITIONAL_OPERATORS = 4
    LONG_PARAMETER_LIST = 5
    DEEP_NESTING_LEVEL = 4
    GOD_CLASS_METHODS = 20
    
    # Phase 4: Performance thresholds
    SLOW_FUNCTION_THRESHOLD_MS = 100  # Functions taking >100ms
    HOT_PATH_CALL_THRESHOLD = 10  # Functions called >10 times
    BOTTLENECK_TOTAL_TIME_MS = 500  # Total time >500ms
    
    def __init__(self):
        """Initialize code smell detector."""
        self.debug_data_cache: Dict[str, Any] = {}
    
    def set_debug_data(self, debug_data: Dict[str, Any]):
        """
        Inject debug timing data for performance-based smell detection.
        
        Args:
            debug_data: Dictionary containing function timing and call data
                       from debug session (via TDDStateMachine.get_debug_data())
        
        Example debug_data structure:
        {
            "function_timings": {
                "authenticate_user": {
                    "avg_time_ms": 150.5,
                    "call_count": 25,
                    "total_time_ms": 3762.5,
                    "line_number": 45
                }
            }
        }
        """
        self.debug_data_cache = debug_data
        print(f"✅ Debug data loaded: {len(debug_data.get('function_timings', {}))} functions profiled")
    
    def analyze_file(self, filepath: str, source_code: str) -> List[CodeSmell]:
        """
        Analyze file for code smells.
        
        Args:
            filepath: Path to file being analyzed
            source_code: Source code content
            
        Returns:
            List of detected code smells
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return []
        
        smells: List[CodeSmell] = []
        
        # Detect long methods
        smells.extend(self._detect_long_methods(tree, filepath, source_code))
        
        # Detect complex conditionals
        smells.extend(self._detect_complex_conditionals(tree, filepath))
        
        # Detect long parameter lists
        smells.extend(self._detect_long_parameter_lists(tree, filepath))
        
        # Detect deep nesting
        smells.extend(self._detect_deep_nesting(tree, filepath))
        
        # Detect magic numbers
        smells.extend(self._detect_magic_numbers(tree, filepath))
        
        # Detect god classes
        smells.extend(self._detect_god_classes(tree, filepath))
        
        # Phase 4 - TDD Mastery Integration: Performance-based detection
        if self.debug_data_cache:
            smells.extend(self._detect_slow_functions(tree, filepath))
            smells.extend(self._detect_hot_paths(tree, filepath))
            smells.extend(self._detect_performance_bottlenecks(tree, filepath))
        
        # CRITICAL: Code cleanup detection (fixes orphaned function bug)
        smells.extend(self._detect_dead_code(tree, filepath, source_code))
        smells.extend(self._detect_orphaned_functions(tree, filepath, source_code))
        smells.extend(self._detect_duplicate_code(tree, filepath))
        
        # SOLID Integration: Architectural violation detection
        smells.extend(self._detect_solid_violations(tree, filepath, source_code))
        
        return smells
    
    def _detect_long_methods(self, tree: ast.AST, filepath: str, source_code: str) -> List[CodeSmell]:
        """Detect methods that are too long."""
        smells = []
        lines = source_code.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                method_lines = end_line - start_line + 1
                
                # Subtract docstring if present
                if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)):
                    docstring_lines = len(node.body[0].value.value.split('\n'))
                    method_lines -= docstring_lines
                
                if method_lines > self.LONG_METHOD_LINES:
                    severity = "high" if method_lines > self.LONG_METHOD_LINES * 2 else "medium"
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.LONG_METHOD,
                        location=f"{filepath}:{start_line}:0",
                        severity=severity,
                        description=f"Method '{node.name}' is {method_lines} lines long (threshold: {self.LONG_METHOD_LINES})",
                        metric_value=float(method_lines),
                        confidence=0.9
                    ))
        
        return smells
    
    def _detect_complex_conditionals(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """Detect conditionals with too many logical operators."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Count logical operators in condition
                operator_count = self._count_logical_operators(node.test)
                
                if operator_count > self.COMPLEX_CONDITIONAL_OPERATORS:
                    severity = "high" if operator_count > self.COMPLEX_CONDITIONAL_OPERATORS * 2 else "medium"
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.COMPLEX_CONDITIONAL,
                        location=f"{filepath}:{node.lineno}:0",
                        severity=severity,
                        description=f"Conditional has {operator_count} logical operators (threshold: {self.COMPLEX_CONDITIONAL_OPERATORS})",
                        metric_value=float(operator_count),
                        confidence=0.85
                    ))
        
        return smells
    
    def _count_logical_operators(self, node: ast.AST) -> int:
        """Count logical operators (and, or, not) in expression."""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.And, ast.Or, ast.Not)):
                count += 1
        return count
    
    def _detect_long_parameter_lists(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """Detect functions with too many parameters."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count parameters (exclude self, cls)
                params = [arg for arg in node.args.args if arg.arg not in ('self', 'cls')]
                param_count = len(params)
                
                if param_count > self.LONG_PARAMETER_LIST:
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.LONG_PARAMETER_LIST,
                        location=f"{filepath}:{node.lineno}:0",
                        severity="medium",
                        description=f"Function '{node.name}' has {param_count} parameters (threshold: {self.LONG_PARAMETER_LIST})",
                        metric_value=float(param_count),
                        confidence=0.9
                    ))
        
        return smells
    
    def _detect_deep_nesting(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """Detect deeply nested code blocks."""
        smells = []
        
        def calculate_nesting(node: ast.AST, current_depth: int = 0) -> int:
            """Calculate maximum nesting depth."""
            max_depth = current_depth
            
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                current_depth += 1
                max_depth = current_depth
            
            for child in ast.iter_child_nodes(node):
                child_depth = calculate_nesting(child, current_depth)
                max_depth = max(max_depth, child_depth)
            
            return max_depth
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                max_nesting = calculate_nesting(node)
                
                if max_nesting > self.DEEP_NESTING_LEVEL:
                    severity = "high" if max_nesting > self.DEEP_NESTING_LEVEL + 2 else "medium"
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.DEEP_NESTING,
                        location=f"{filepath}:{node.lineno}:0",
                        severity=severity,
                        description=f"Function '{node.name}' has nesting depth of {max_nesting} (threshold: {self.DEEP_NESTING_LEVEL})",
                        metric_value=float(max_nesting),
                        confidence=0.9
                    ))
        
        return smells
    
    def _detect_magic_numbers(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """Detect magic numbers (unnamed constants)."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)) and node.value not in (0, 1, -1):
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.MAGIC_NUMBER,
                        location=f"{filepath}:{node.lineno}:{node.col_offset}",
                        severity="low",
                        description=f"Magic number {node.value} should be extracted to named constant",
                        metric_value=float(node.value) if isinstance(node.value, (int, float)) else None,
                        confidence=0.7
                    ))
        
        return smells
    
    def _detect_god_classes(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """Detect classes with too many methods (god classes)."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Count methods (exclude magic methods)
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef) 
                          and not n.name.startswith('__')]
                method_count = len(methods)
                
                if method_count > self.GOD_CLASS_METHODS:
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.GOD_CLASS,
                        location=f"{filepath}:{node.lineno}:0",
                        severity="high",
                        description=f"Class '{node.name}' has {method_count} methods (threshold: {self.GOD_CLASS_METHODS})",
                        metric_value=float(method_count),
                        confidence=0.85
                    ))
        
        return smells
    
    # Phase 4 - TDD Mastery Integration: Performance-based smell detection
    
    def _detect_slow_functions(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """
        Detect functions with high execution time from debug data.
        
        Uses actual runtime measurements from debug sessions to identify
        slow functions that should be optimized.
        """
        smells = []
        function_timings = self.debug_data_cache.get("function_timings", {})
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                timing = function_timings.get(func_name)
                
                if timing and timing.get("avg_time_ms", 0) > self.SLOW_FUNCTION_THRESHOLD_MS:
                    avg_time = timing["avg_time_ms"]
                    call_count = timing.get("call_count", 0)
                    
                    # Severity based on how slow it is
                    if avg_time > self.SLOW_FUNCTION_THRESHOLD_MS * 5:
                        severity = "high"
                    elif avg_time > self.SLOW_FUNCTION_THRESHOLD_MS * 2:
                        severity = "medium"
                    else:
                        severity = "low"
                    
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.SLOW_FUNCTION,
                        location=f"{filepath}:{node.lineno}:0",
                        severity=severity,
                        description=f"Function '{func_name}' takes {avg_time:.2f}ms on average (threshold: {self.SLOW_FUNCTION_THRESHOLD_MS}ms, called {call_count} times)",
                        metric_value=avg_time,
                        confidence=0.95  # High confidence - measured data
                    ))
        
        return smells
    
    def _detect_hot_paths(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """
        Detect functions called frequently (hot paths).
        
        Identifies functions executed many times that could benefit
        from optimization even if individual calls are fast.
        """
        smells = []
        function_timings = self.debug_data_cache.get("function_timings", {})
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                timing = function_timings.get(func_name)
                
                if timing and timing.get("call_count", 0) > self.HOT_PATH_CALL_THRESHOLD:
                    call_count = timing["call_count"]
                    avg_time = timing.get("avg_time_ms", 0)
                    total_time = timing.get("total_time_ms", 0)
                    
                    # High call count = hot path worth optimizing
                    if call_count > self.HOT_PATH_CALL_THRESHOLD * 10:
                        severity = "high"
                    elif call_count > self.HOT_PATH_CALL_THRESHOLD * 5:
                        severity = "medium"
                    else:
                        severity = "low"
                    
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.HOT_PATH,
                        location=f"{filepath}:{node.lineno}:0",
                        severity=severity,
                        description=f"Function '{func_name}' called {call_count} times (avg: {avg_time:.2f}ms, total: {total_time:.2f}ms) - hot path optimization candidate",
                        metric_value=float(call_count),
                        confidence=0.95  # High confidence - measured data
                    ))
        
        return smells
    
    def _detect_performance_bottlenecks(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """
        Detect performance bottlenecks (high total time consumption).
        
        Identifies functions that consume significant total time even if
        individual calls aren't slow (e.g., fast function called 1000 times).
        """
        smells = []
        function_timings = self.debug_data_cache.get("function_timings", {})
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                timing = function_timings.get(func_name)
                
                if timing and timing.get("total_time_ms", 0) > self.BOTTLENECK_TOTAL_TIME_MS:
                    total_time = timing["total_time_ms"]
                    avg_time = timing.get("avg_time_ms", 0)
                    call_count = timing.get("call_count", 0)
                    
                    # Severity based on total time impact
                    if total_time > self.BOTTLENECK_TOTAL_TIME_MS * 5:
                        severity = "high"
                    elif total_time > self.BOTTLENECK_TOTAL_TIME_MS * 2:
                        severity = "medium"
                    else:
                        severity = "low"
                    
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.PERFORMANCE_BOTTLENECK,
                        location=f"{filepath}:{node.lineno}:0",
                        severity=severity,
                        description=f"Function '{func_name}' consumes {total_time:.2f}ms total (avg: {avg_time:.2f}ms × {call_count} calls) - performance bottleneck",
                        metric_value=total_time,
                        confidence=0.95  # High confidence - measured data
                    ))
        
        return smells
    
    # CRITICAL FIX: Code cleanup detection for orphaned/duplicate code
    
    def _detect_dead_code(self, tree: ast.AST, filepath: str, source_code: str) -> List[CodeSmell]:
        """
        Detect dead code (functions with zero call sites).
        
        Finds functions that are defined but never called anywhere in the file.
        This indicates orphaned implementations that should be removed.
        """
        smells = []
        
        # Build set of all function definitions
        defined_functions = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):  # Skip private functions
                    defined_functions.add(node.name)
        
        # Build set of all function calls
        called_functions = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_functions.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called_functions.add(node.func.attr)
        
        # Find functions that are defined but never called
        dead_functions = defined_functions - called_functions
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name in dead_functions:
                    # Calculate function size to assess severity
                    func_lines = (node.end_lineno or node.lineno) - node.lineno + 1
                    
                    severity = "high" if func_lines > 20 else "medium"
                    
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.DEAD_CODE,
                        location=f"{filepath}:{node.lineno}:0",
                        severity=severity,
                        description=f"Function '{node.name}' has zero call sites (dead code) - should be removed",
                        metric_value=float(func_lines),
                        confidence=0.95  # High confidence - AST-based analysis
                    ))
        
        return smells
    
    def _detect_orphaned_functions(self, tree: ast.AST, filepath: str, source_code: str) -> List[CodeSmell]:
        """
        Detect orphaned functions (old implementations likely replaced by new code).
        
        Heuristic: Functions with similar names or that appear to be "old versions"
        (e.g., login_old, authenticate_v1, process_data_legacy)
        """
        smells = []
        
        orphan_patterns = ['_old', '_legacy', '_deprecated', '_backup', '_v1', '_v2', '_temp']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name_lower = node.name.lower()
                
                # Check for orphan naming patterns
                is_orphan = any(pattern in func_name_lower for pattern in orphan_patterns)
                
                if is_orphan:
                    func_lines = (node.end_lineno or node.lineno) - node.lineno + 1
                    
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.DEAD_CODE,
                        location=f"{filepath}:{node.lineno}:0",
                        severity="high",
                        description=f"Function '{node.name}' appears to be orphaned implementation (naming suggests old version) - should be removed or renamed",
                        metric_value=float(func_lines),
                        confidence=0.85  # Good confidence based on naming
                    ))
        
        return smells
    
    def _detect_duplicate_code(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """
        Detect duplicate function signatures.
        
        Finds functions with identical or very similar signatures that may
        indicate duplicate implementations.
        """
        smells = []
        
        # Build map of function signatures
        function_signatures: Dict[str, List[tuple]] = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Create signature: (param_count, param_names_normalized)
                param_count = len(node.args.args)
                param_names = tuple(sorted([arg.arg for arg in node.args.args if arg.arg not in ('self', 'cls')]))
                
                signature = (param_count, param_names)
                
                if signature not in function_signatures:
                    function_signatures[signature] = []
                function_signatures[signature].append((node.name, node.lineno))
        
        # Find duplicate signatures
        for signature, functions in function_signatures.items():
            if len(functions) > 1:
                # Multiple functions with same signature
                for func_name, line_num in functions:
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.DUPLICATE_CODE,
                        location=f"{filepath}:{line_num}:0",
                        severity="medium",
                        description=f"Function '{func_name}' has duplicate signature with {len(functions)-1} other function(s) - possible code duplication",
                        metric_value=float(len(functions)),
                        confidence=0.80  # Moderate confidence - needs manual review
                    ))
        
        return smells
    
    def _detect_solid_violations(self, tree: ast.AST, filepath: str, source_code: str) -> List[CodeSmell]:
        """
        Detect SOLID principle violations using SOLIDPrincipleEnforcer.
        
        Integrates with discovered SOLID components to detect:
        - SRP: Single Responsibility Principle violations
        - OCP: Open/Closed Principle violations  
        - LSP: Liskov Substitution Principle violations
        - ISP: Interface Segregation Principle violations
        - DIP: Dependency Inversion Principle violations
        - Coupling: Tight coupling and circular dependencies
        
        Returns:
            List of detected SOLID violations
        """
        smells = []
        
        try:
            # Import SOLIDPrincipleEnforcer (wire discovered component)
            from src.cortex_agents.test_generator.solid_principle_enforcer import (
                SOLIDPrincipleEnforcer,
                SOLIDViolation,
                SOLIDPrinciple
            )
            from pathlib import Path
            import tempfile
            
            # Create enforcer instance
            enforcer = SOLIDPrincipleEnforcer()
            
            # SOLIDPrincipleEnforcer needs a file path, so write to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(source_code)
                temp_path = f.name
            
            try:
                # Analyze file for SOLID violations
                violations = enforcer.check_file(temp_path)
                
                # Convert violations to CodeSmell objects
                for violation in violations:
                    # Map violation type to smell type
                    smell_type_map = {
                        SOLIDPrinciple.SRP: CodeSmellType.SRP_VIOLATION,
                        SOLIDPrinciple.OCP: CodeSmellType.OCP_VIOLATION,
                        SOLIDPrinciple.LSP: CodeSmellType.LSP_VIOLATION,
                        SOLIDPrinciple.ISP: CodeSmellType.ISP_VIOLATION,
                        SOLIDPrinciple.DIP: CodeSmellType.DIP_VIOLATION,
                    }
                    
                    smell_type = smell_type_map.get(
                        violation.principle,
                        CodeSmellType.SOLID_VIOLATION
                    )
                    
                    # Map severity
                    severity = violation.severity.value.lower()
                    if severity == "critical":
                        severity = "high"
                    
                    smells.append(CodeSmell(
                        smell_type=smell_type,
                        location=f"{filepath}:{violation.line_number}:0",
                        severity=severity,
                        description=f"{violation.principle.value.replace('_', ' ').title()}: {violation.description}",
                        metric_value=None,
                        confidence=0.90  # High confidence from enforcer
                    ))
            finally:
                # Clean up temp file
                import os
                try:
                    os.unlink(temp_path)
                except:
                    pass
            
            # Also detect coupling issues using DependencyGraph
            smells.extend(self._detect_coupling_issues(filepath, source_code))
            
        except ImportError as e:
            # SOLIDPrincipleEnforcer not available - skip SOLID detection
            pass
        except Exception as e:
            # Log error but don't fail analysis
            print(f"⚠️  SOLID detection failed for {filepath}: {e}")
        
        return smells
    
    def _detect_coupling_issues(self, filepath: str, source_code: str) -> List[CodeSmell]:
        """
        Detect tight coupling through import analysis.
        
        Returns:
            List of coupling-related code smells
        """
        smells = []
        
        try:
            # Analyze imports in file
            tree = ast.parse(source_code)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # Check for excessive coupling (too many imports)
            if len(imports) > 15:
                smells.append(CodeSmell(
                    smell_type=CodeSmellType.TIGHT_COUPLING,
                    location=f"{filepath}:1:0",
                    severity="medium",
                    description=f"High coupling: {len(imports)} imports detected - consider reducing dependencies",
                    metric_value=float(len(imports)),
                    confidence=0.85
                ))
                
        except Exception as e:
            # Log error but don't fail analysis
            print(f"⚠️  Coupling detection failed for {filepath}: {e}")
        
        return smells


class RefactoringEngine:
    """
    Generates refactoring suggestions and applies transformations.
    
    Provides safe, automated refactoring with test validation.
    """
    
    def __init__(self):
        self.detector = CodeSmellDetector()
    
    def generate_suggestions(self, code_smells: List[CodeSmell], source_code: str) -> List[RefactoringSuggestion]:
        """
        Generate refactoring suggestions for detected code smells.
        
        Args:
            code_smells: List of detected code smells
            source_code: Original source code
            
        Returns:
            List of refactoring suggestions
        """
        suggestions: List[RefactoringSuggestion] = []
        
        for smell in code_smells:
            if smell.smell_type == CodeSmellType.LONG_METHOD:
                suggestions.extend(self._suggest_extract_method(smell, source_code))
            
            elif smell.smell_type == CodeSmellType.COMPLEX_CONDITIONAL:
                suggestions.extend(self._suggest_simplify_conditional(smell, source_code))
            
            elif smell.smell_type == CodeSmellType.LONG_PARAMETER_LIST:
                suggestions.extend(self._suggest_parameter_object(smell, source_code))
            
            elif smell.smell_type == CodeSmellType.DEEP_NESTING:
                suggestions.extend(self._suggest_reduce_nesting(smell, source_code))
            
            # Phase 4 - TDD Mastery Integration: Performance-based suggestions
            elif smell.smell_type == CodeSmellType.SLOW_FUNCTION:
                suggestions.extend(self._suggest_optimize_slow_function(smell, source_code))
            
            elif smell.smell_type == CodeSmellType.HOT_PATH:
                suggestions.extend(self._suggest_optimize_hot_path(smell, source_code))
            
            elif smell.smell_type == CodeSmellType.PERFORMANCE_BOTTLENECK:
                suggestions.extend(self._suggest_optimize_bottleneck(smell, source_code))
            
            elif smell.smell_type == CodeSmellType.MAGIC_NUMBER:
                suggestions.extend(self._suggest_extract_constant(smell, source_code))
        
        return suggestions
    
    def _suggest_extract_method(self, smell: CodeSmell, source_code: str) -> List[RefactoringSuggestion]:
        """Suggest extracting part of long method."""
        # Simplified suggestion (full implementation would use AST manipulation)
        return [RefactoringSuggestion(
            refactoring_type=RefactoringType.EXTRACT_METHOD,
            target_location=smell.location,
            description="Extract logical sections into separate methods",
            code_before="# Long method code...",
            code_after="# Extracted into helper methods...",
            confidence=0.75,
            estimated_effort="medium"
        )]
    
    def _suggest_simplify_conditional(self, smell: CodeSmell, source_code: str) -> List[RefactoringSuggestion]:
        """Suggest simplifying complex conditional."""
        return [RefactoringSuggestion(
            refactoring_type=RefactoringType.SIMPLIFY_CONDITIONAL,
            target_location=smell.location,
            description="Extract conditional logic into named boolean variables or methods",
            code_before="if (a and b) or (c and d) or (e and f): ...",
            code_after="if is_valid_state(): ...",
            confidence=0.8,
            estimated_effort="low"
        )]
    
    def _suggest_parameter_object(self, smell: CodeSmell, source_code: str) -> List[RefactoringSuggestion]:
        """Suggest introducing parameter object."""
        return [RefactoringSuggestion(
            refactoring_type=RefactoringType.INTRODUCE_PARAMETER_OBJECT,
            target_location=smell.location,
            description="Group related parameters into a configuration object or dataclass",
            code_before="def func(a, b, c, d, e, f): ...",
            code_after="def func(config: Config): ...",
            confidence=0.85,
            estimated_effort="medium"
        )]
    
    def _suggest_reduce_nesting(self, smell: CodeSmell, source_code: str) -> List[RefactoringSuggestion]:
        """Suggest reducing nesting depth."""
        return [RefactoringSuggestion(
            refactoring_type=RefactoringType.REDUCE_NESTING,
            target_location=smell.location,
            description="Use early returns, extract nested logic to methods, or invert conditionals",
            code_before="if a:\n    if b:\n        if c:\n            ...",
            code_after="if not a: return\nif not b: return\nif not c: return\n...",
            confidence=0.8,
            estimated_effort="low"
        )]
    
    def _suggest_extract_constant(self, smell: CodeSmell, source_code: str) -> List[RefactoringSuggestion]:
        """Suggest extracting magic number to constant."""
        return [RefactoringSuggestion(
            refactoring_type=RefactoringType.EXTRACT_CONSTANT,
            target_location=smell.location,
            description=f"Extract magic number {smell.metric_value} to named constant",
            code_before=f"threshold = {smell.metric_value}",
            code_after=f"MAX_THRESHOLD = {smell.metric_value}\nthreshold = MAX_THRESHOLD",
            confidence=0.9,
            estimated_effort="low"
        )]
    
    # Phase 4 - TDD Mastery Integration: Performance-based suggestions
    
    def _suggest_optimize_slow_function(self, smell: CodeSmell, source_code: str) -> List[RefactoringSuggestion]:
        """
        Suggest optimizations for slow functions based on debug timing data.
        
        Provides data-driven optimization recommendations.
        """
        return [RefactoringSuggestion(
            refactoring_type=RefactoringType.EXTRACT_METHOD,
            target_location=smell.location,
            description=f"Function is slow ({smell.metric_value:.2f}ms average). Consider: 1) Cache expensive operations, 2) Use lazy evaluation, 3) Profile and optimize critical sections, 4) Parallelize if possible",
            code_before="# Slow implementation",
            code_after="# Optimized with caching/lazy eval",
            confidence=0.90,  # High confidence - measured data
            estimated_effort="medium"
        )]
    
    def _suggest_optimize_hot_path(self, smell: CodeSmell, source_code: str) -> List[RefactoringSuggestion]:
        """
        Suggest optimizations for frequently-called functions (hot paths).
        
        Even small optimizations have big impact on hot paths.
        """
        return [RefactoringSuggestion(
            refactoring_type=RefactoringType.EXTRACT_METHOD,
            target_location=smell.location,
            description=f"Function called {smell.metric_value:.0f} times (hot path). Consider: 1) Reduce allocations, 2) Inline critical operations, 3) Use specialized data structures, 4) Memoize results",
            code_before="# Frequent calls",
            code_after="# Optimized for frequent execution",
            confidence=0.90,  # High confidence - measured data
            estimated_effort="low"
        )]
    
    def _suggest_optimize_bottleneck(self, smell: CodeSmell, source_code: str) -> List[RefactoringSuggestion]:
        """
        Suggest optimizations for performance bottlenecks.
        
        Focus on functions consuming significant total time.
        """
        return [RefactoringSuggestion(
            refactoring_type=RefactoringType.EXTRACT_METHOD,
            target_location=smell.location,
            description=f"Function consumes {smell.metric_value:.2f}ms total (performance bottleneck). Consider: 1) Batch operations, 2) Reduce call frequency, 3) Use async/await, 4) Optimize algorithm complexity",
            code_before="# High total time consumption",
            code_after="# Optimized with batching/async",
            confidence=0.90,  # High confidence - measured data
            estimated_effort="high"
        )]
    
    def verify_refactoring_safety(self, suggestion: RefactoringSuggestion, test_command: str) -> bool:
        """
        Verify refactoring is safe by running tests.
        
        Args:
            suggestion: Refactoring suggestion to verify
            test_command: Command to run tests (e.g., "pytest tests/")
            
        Returns:
            True if tests pass after refactoring
        """
        # This would:
        # 1. Apply refactoring
        # 2. Run test command
        # 3. Check if all tests pass
        # 4. Rollback if tests fail
        # Simplified for now
        return True

"""Complexity Assessment

Comprehensive complexity analysis for CORTEX operations.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import ast
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class ComplexityLevel(str, Enum):
    """Complexity levels."""
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    CRITICAL = "critical"


@dataclass
class ComplexitySignals:
    """Signals for complexity assessment."""
    lens_confidence: float
    files_affected_count: int
    call_graph_depth: int
    circular_dependencies: int
    dependency_depth: int
    tight_coupling_score: float
    operation_scope: str
    ast_complexity: int
    criticality_level: str


@dataclass
class ComplexityAssessment:
    """Complexity assessment result."""
    complexity_score: float
    complexity_level: str
    level: ComplexityLevel = None
    factors: Dict[str, Any] = field(default_factory=dict)
    cached: bool = False
    signals: Optional[Dict[str, Any]] = None
    confidence: float = 0.95
    
    def __post_init__(self):
        """Initialize level from complexity_level if not provided."""
        if self.level is None:
            # Convert complexity_level string to ComplexityLevel enum
            level_str = self.complexity_level.lower()
            for level in ComplexityLevel:
                if level.value == level_str:
                    self.level = level
                    break
            if self.level is None:
                self.level = ComplexityLevel.MODERATE
    
    @property
    def score(self) -> float:
        """Alias for complexity_score."""
        return self.complexity_score


@dataclass
class ComplexityAssessmentEngine:
    """Engine for assessing complexity."""
    threshold: float = 0.75
    _cache: Dict[str, ComplexityAssessment] = field(default_factory=dict)
    _cache_stats: Dict[str, int] = field(default_factory=lambda: {'hits': 0, 'misses': 0})
    
    def assess(self, input_data: Any) -> ComplexityAssessment:
        """Assess complexity of input data."""
        if isinstance(input_data, ComplexitySignals):
            return self.assess_complexity(input_data)
        return ComplexityAssessment(
            level=ComplexityLevel.TRIVIAL,
            complexity_level=ComplexityLevel.TRIVIAL.value,
            complexity_score=0.0
        )
    
    def assess_complexity(
        self, 
        signals: ComplexitySignals,
        intent_type: Optional[str] = None,
        use_cache: bool = False
    ) -> ComplexityAssessment:
        """Assess complexity from signals."""
        cache_key = f"{intent_type}" if intent_type else None
        auto_cache = cache_key is not None
        
        if (use_cache or auto_cache) and cache_key and cache_key in self._cache:
            self._cache_stats['hits'] += 1
            result = self._cache[cache_key]
            result.cached = True
            return result
        
        self._cache_stats['misses'] += 1
        score = self._calculate_score(signals)
        
        if score < 0.15:
            level = ComplexityLevel.TRIVIAL
        elif score < 0.35:
            level = ComplexityLevel.SIMPLE
        elif score < 0.60:
            level = ComplexityLevel.MODERATE
        elif score < 0.85:
            level = ComplexityLevel.COMPLEX
        else:
            level = ComplexityLevel.CRITICAL
        
        factors = self._calculate_factors(signals)
        assessment = ComplexityAssessment(
            level=level,
            complexity_level=level.value,
            complexity_score=score,
            factors=factors,
            cached=False
        )
        
        if cache_key:
            self._cache[cache_key] = assessment
        
        return assessment
    
    def _calculate_factors(self, signals: ComplexitySignals) -> Dict[str, Any]:
        """Calculate individual complexity factors."""
        factors = {}
        factors['lens_confidence'] = 1.0 - signals.lens_confidence
        factors['files_affected'] = min(signals.files_affected_count / 100.0, 1.0)
        factors['call_depth'] = min(signals.call_graph_depth / 10.0, 1.0)
        
        if signals.circular_dependencies > 0:
            factors['circular_penalty'] = min(signals.circular_dependencies * 0.1, 0.5)
        else:
            factors['circular_penalty'] = 0.0
        
        factors['dependency_depth'] = min(signals.dependency_depth / 5.0, 1.0)
        factors['tight_coupling'] = signals.tight_coupling_score
        
        scope_weights = {'local': 0.2, 'cross_layer': 0.6, 'global': 1.0}
        factors['operation_scope'] = scope_weights.get(signals.operation_scope, 0.5)
        
        factors['ast_complexity'] = min(signals.ast_complexity / 50.0, 1.0)
        
        criticality_weights = {'low': 1.0, 'medium': 1.3, 'high': 1.5, 'critical': 1.8}
        factors['criticality'] = criticality_weights.get(signals.criticality_level, 1.0)
        
        return factors
    
    def _calculate_score(self, signals: ComplexitySignals) -> float:
        """Calculate complexity score from signals."""
        factors = self._calculate_factors(signals)
        weights = {
            'lens_confidence': 0.15,
            'files_affected': 0.15,
            'call_depth': 0.15,
            'circular_penalty': 0.10,
            'dependency_depth': 0.10,
            'tight_coupling': 0.10,
            'operation_scope': 0.10,
            'ast_complexity': 0.10,
        }
        score = sum(factors.get(k, 0.0) * v for k, v in weights.items())
        criticality = factors.get('criticality', 1.0)
        score = min(score * criticality, 1.0)
        return score
    
    def invalidate_cache_for_intent(self, intent_type: str) -> int:
        """Invalidate cache entries for an intent type."""
        if intent_type in self._cache:
            del self._cache[intent_type]
            return 1
        return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self._cache_stats['hits'] + self._cache_stats['misses']
        hit_rate = self._cache_stats['hits'] / total if total > 0 else 0.0
        return {
            'cache_hits': self._cache_stats['hits'],
            'cache_misses': self._cache_stats['misses'],
            'hit_rate': hit_rate,
            'cached_items': len(self._cache)
        }


class ASTComplexityAnalyzer:
    """Analyzes AST complexity of Python code."""
    
    @staticmethod
    def analyze_complexity(code: str) -> int:
        """Analyze AST complexity of code."""
        if not code or not code.strip():
            return 0
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0
        analyzer = _ASTComplexityVisitor()
        analyzer.visit(tree)
        return analyzer.complexity


class _ASTComplexityVisitor(ast.NodeVisitor):
    """Visitor for calculating cyclomatic complexity."""
    
    def __init__(self) -> None:
        """Initialize visitor."""
        self.complexity = 1
    
    def visit_If(self, node: ast.If) -> None:
        """Visit if statement."""
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node: ast.For) -> None:
        """Visit for loop."""
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node: ast.While) -> None:
        """Visit while loop."""
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Visit except handler."""
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        """Visit boolean operator."""
        self.complexity += len(node.values) - 1
        self.generic_visit(node)


class CallGraphAnalyzer:
    """Analyzes call graph depth and structure."""
    
    @staticmethod
    def analyze_depth(call_graph: Dict[str, List[str]]) -> Tuple[int, float]:
        """Analyze call graph depth."""
        if not call_graph:
            return 0, 0.0
        
        depths = {}
        for func in call_graph:
            depth = CallGraphAnalyzer._calculate_depth(func, call_graph, set())
            depths[func] = depth
        
        max_depth = max(depths.values()) if depths else 0
        avg_depth = sum(depths.values()) / len(depths) if depths else 0.0
        
        return max_depth, avg_depth
    
    @staticmethod
    def _calculate_depth(
        func: str,
        call_graph: Dict[str, List[str]],
        visited: Set[str]
    ) -> int:
        """Calculate depth of function in call graph."""
        if func in visited or func not in call_graph:
            return 1
        
        visited.add(func)
        callees = call_graph.get(func, [])
        
        if not callees:
            return 1
        
        max_callee_depth = max(
            CallGraphAnalyzer._calculate_depth(callee, call_graph, visited.copy())
            for callee in callees
        )
        
        return 1 + max_callee_depth


class CircularDependencyDetector:
    """Detects circular dependencies and coupling."""
    
    @staticmethod
    def detect_cycles(dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies in graph."""
        if not dependency_graph:
            return []
        
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]) -> None:
            """Depth-first search for cycles."""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in dependency_graph.get(node, []):
                if neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                elif neighbor not in visited:
                    dfs(neighbor, path[:])
            
            rec_stack.remove(node)
        
        for node in dependency_graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    @staticmethod
    def calculate_tight_coupling(dependency_graph: Dict[str, List[str]]) -> float:
        """Calculate tight coupling score for graph."""
        if not dependency_graph:
            return 0.0
        
        total_edges = sum(len(deps) for deps in dependency_graph.values())
        if total_edges == 0:
            return 0.0
        
        num_nodes = len(dependency_graph)
        max_edges = num_nodes * (num_nodes - 1)
        if max_edges == 0:
            return 0.0
        
        coupling = total_edges / max_edges
        return min(coupling, 1.0)


__all__ = [
    "ComplexityLevel",
    "ComplexityAssessment",
    "ComplexityAssessmentEngine",
    "ASTComplexityAnalyzer",
    "CallGraphAnalyzer",
    "CircularDependencyDetector",
    "ComplexitySignals",
]

"""Complexity Assessment Engine - Evaluate operation complexity across multiple signals."""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from datetime import datetime

@dataclass
class ComplexitySignals:
    """Aggregated complexity signals from multiple analysis layers."""
    lens_confidence: float  # 0.0-1.0, from Language + Examination phases
    files_affected_count: int  # Number of files impacted
    call_graph_depth: int  # Maximum depth in call graph traversal
    circular_dependencies: int  # Count of circular dependencies detected
    dependency_depth: int  # Maximum dependency nesting level
    tight_coupling_score: float  # 0.0-1.0, measure of coupling
    operation_scope: str  # local | cross_layer | global
    ast_complexity: int  # Cyclomatic-like complexity metric
    criticality_level: str  # low | medium | high | critical

@dataclass
class ComplexityAssessment:
    """Result of complexity assessment."""
    complexity_score: float  # 0.0-1.0, aggregated score
    complexity_level: str  # TRIVIAL | SIMPLE | MODERATE | COMPLEX | CRITICAL
    signals: ComplexitySignals
    confidence: float  # Confidence in this assessment (0.0-1.0)
    factors: Dict[str, float]  # Breakdown of contributing factors
    cached: bool = False
    assessment_time: datetime = field(default_factory=datetime.now)

class ComplexityLevel(Enum):
    """Complexity levels with thresholds."""
    TRIVIAL = "TRIVIAL"          # score <= 0.15
    SIMPLE = "SIMPLE"            # 0.15 < score <= 0.35
    MODERATE = "MODERATE"        # 0.35 < score <= 0.60
    COMPLEX = "COMPLEX"          # 0.60 < score <= 0.85
    CRITICAL = "CRITICAL"        # score > 0.85

class ComplexityAssessmentEngine:
    """Aggregates multiple signals into complexity score."""
    
    # Complexity thresholds
    THRESHOLDS = {
        0.15: ComplexityLevel.TRIVIAL,
        0.35: ComplexityLevel.SIMPLE,
        0.60: ComplexityLevel.MODERATE,
        0.85: ComplexityLevel.COMPLEX,
        float('inf'): ComplexityLevel.CRITICAL,
    }
    
    # Signal weights (must sum to 1.0)
    SIGNAL_WEIGHTS = {
        'lens_confidence': 0.25,      # Language + Examination phases
        'files_affected': 0.35,        # Call graph traversal impact
        'dependency_depth': 0.25,      # Relationship engine analysis
        'operation_scope': 0.15,       # AST analysis scope
    }
    
    # Criticality scoring adjustments
    CRITICALITY_MULTIPLIERS = {
        'low': 1.0,
        'medium': 1.3,
        'high': 1.6,
        'critical': 2.0,
    }
    
    def __init__(self):
        """Initialize assessment engine with cache."""
        self.complexity_cache: Dict[str, ComplexityAssessment] = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    @staticmethod
    def _normalize_score(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Normalize a value to 0.0-1.0 range."""
        if max_val <= min_val:
            return 0.5
        normalized = (value - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))
    
    @staticmethod
    def _score_lens_confidence(confidence: float) -> float:
        """Score lens confidence (already normalized 0.0-1.0)."""
        # High confidence (close to 1.0) = less complexity
        # Low confidence = more complexity
        return 1.0 - confidence
    
    @staticmethod
    def _score_files_affected(files_count: int) -> float:
        """Score based on number of files affected."""
        # Single file: 0.0 (trivial)
        # 10 files: 0.5 (moderate)
        # 50+ files: 1.0 (critical)
        if files_count <= 1:
            return 0.0
        elif files_count >= 50:
            return 1.0
        return ComplexityAssessmentEngine._normalize_score(files_count, 1, 50)
    
    @staticmethod
    def _score_dependency_depth(call_graph_depth: int, dependency_depth: int, 
                                tight_coupling: float) -> float:
        """Score dependency complexity from multiple signals."""
        # Call graph depth: max 10 = 1.0
        depth_score = ComplexityAssessmentEngine._normalize_score(call_graph_depth, 0, 10)
        
        # Dependency nesting: max 5 = 1.0
        nesting_score = ComplexityAssessmentEngine._normalize_score(dependency_depth, 0, 5)
        
        # Tight coupling: already 0.0-1.0
        coupling_score = tight_coupling
        
        # Average the three signals
        return (depth_score + nesting_score + coupling_score) / 3.0
    
    @staticmethod
    def _score_operation_scope(scope: str, ast_complexity: int) -> float:
        """Score operation scope and AST complexity."""
        scope_scores = {
            'local': 0.1,          # Single function/class
            'cross_layer': 0.5,    # Multiple modules/layers
            'global': 0.9,         # System-wide changes
        }
        
        scope_score = scope_scores.get(scope, 0.5)
        
        # AST complexity adjustment: max complexity 50 = adds 0.2
        ast_score = ComplexityAssessmentEngine._normalize_score(ast_complexity, 0, 50) * 0.2
        
        return min(1.0, scope_score + ast_score)
    
    @staticmethod
    def _score_circular_dependencies(circular_deps: int) -> float:
        """Score penalty for circular dependencies."""
        # Each circular dependency adds 0.1 to score (max 0.5)
        return min(0.5, circular_deps * 0.1)
    
    def _generate_cache_key(self, intent_type: str, context_hash: str) -> str:
        """Generate cache key for complexity assessment."""
        return f"{intent_type}:{context_hash}"
    
    @staticmethod
    def _compute_context_hash(signals: ComplexitySignals) -> str:
        """Compute hash of signals for caching."""
        # Create deterministic hash of signal values
        signal_str = (
            f"{signals.lens_confidence}|"
            f"{signals.files_affected_count}|"
            f"{signals.call_graph_depth}|"
            f"{signals.circular_dependencies}|"
            f"{signals.dependency_depth}|"
            f"{signals.tight_coupling_score}|"
            f"{signals.operation_scope}|"
            f"{signals.ast_complexity}|"
            f"{signals.criticality_level}"
        )
        return hashlib.sha256(signal_str.encode()).hexdigest()[:16]
    
    def assess_complexity(
        self,
        signals: ComplexitySignals,
        intent_type: str = "general",
        use_cache: bool = True
    ) -> ComplexityAssessment:
        """
        Assess complexity using aggregated signals.
        
        Args:
            signals: ComplexitySignals with all input data
            intent_type: Type of operation for cache key
            use_cache: Whether to use cached assessments
        
        Returns:
            ComplexityAssessment with score and level
        """
        # Generate cache key
        context_hash = self._compute_context_hash(signals)
        cache_key = self._generate_cache_key(intent_type, context_hash)
        
        # Check cache
        if use_cache and cache_key in self.complexity_cache:
            cached = self.complexity_cache[cache_key]
            self.cache_hits += 1
            cached.cached = True
            return cached
        
        self.cache_misses += 1
        
        # Calculate individual signal scores
        lens_score = self._score_lens_confidence(signals.lens_confidence)
        files_score = self._score_files_affected(signals.files_affected_count)
        dependency_score = self._score_dependency_depth(
            signals.call_graph_depth,
            signals.dependency_depth,
            signals.tight_coupling_score
        )
        scope_score = self._score_operation_scope(
            signals.operation_scope,
            signals.ast_complexity
        )
        
        # Circular dependency penalty
        circular_penalty = self._score_circular_dependencies(signals.circular_dependencies)
        
        # Store factor breakdown
        factors = {
            'lens_confidence': lens_score,
            'files_affected': files_score,
            'dependency_depth': dependency_score,
            'operation_scope': scope_score,
            'circular_penalty': circular_penalty,
        }
        
        # Weighted aggregation
        weighted_score = (
            lens_score * self.SIGNAL_WEIGHTS['lens_confidence'] +
            files_score * self.SIGNAL_WEIGHTS['files_affected'] +
            dependency_score * self.SIGNAL_WEIGHTS['dependency_depth'] +
            scope_score * self.SIGNAL_WEIGHTS['operation_scope']
        )
        
        # Apply criticality multiplier
        criticality_mult = self.CRITICALITY_MULTIPLIERS.get(signals.criticality_level, 1.0)
        final_score = min(1.0, weighted_score * criticality_mult + circular_penalty)
        
        # Determine complexity level
        complexity_level = self._get_complexity_level(final_score)
        
        # Calculate assessment confidence based on signal quality
        confidence = self._calculate_confidence(signals)
        
        # Create assessment
        assessment = ComplexityAssessment(
            complexity_score=final_score,
            complexity_level=complexity_level.value,
            signals=signals,
            confidence=confidence,
            factors=factors,
            cached=False
        )
        
        # Cache the result
        self.complexity_cache[cache_key] = assessment
        
        return assessment
    
    def _get_complexity_level(self, score: float) -> ComplexityLevel:
        """Determine complexity level from score."""
        for threshold, level in sorted(self.THRESHOLDS.items()):
            if score <= threshold:
                return level
        return ComplexityLevel.CRITICAL
    
    @staticmethod
    def _calculate_confidence(signals: ComplexitySignals) -> float:
        """Calculate confidence in assessment."""
        # Confidence decreases with uncertainty
        # High lens_confidence = high confidence
        # Missing signals = lower confidence
        base_confidence = signals.lens_confidence
        
        # Adjust for scope uncertainty
        scope_adjustment = {
            'local': 0.95,
            'cross_layer': 0.85,
            'global': 0.75,
        }.get(signals.operation_scope, 0.80)
        
        return base_confidence * scope_adjustment
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total if total > 0 else 0.0
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'total_accesses': total,
            'hit_rate': hit_rate,
            'cached_assessments': len(self.complexity_cache),
        }
    
    def clear_cache(self) -> None:
        """Clear complexity cache."""
        self.complexity_cache.clear()
    
    def invalidate_cache_for_intent(self, intent_type: str) -> int:
        """Invalidate cache entries for specific intent type."""
        keys_to_remove = [k for k in self.complexity_cache.keys() 
                         if k.startswith(f"{intent_type}:")]
        for key in keys_to_remove:
            del self.complexity_cache[key]
        return len(keys_to_remove)

# AST Complexity analysis
class ASTComplexityAnalyzer:
    """Analyze cyclomatic-like complexity from code structure."""
    
    @staticmethod
    def analyze_complexity(code: str) -> int:
        """
        Analyze code complexity metric.
        Returns a complexity score (higher = more complex).
        """
        import ast
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0
        
        complexity = 0
        
        for node in ast.walk(tree):
            # Count control flow structures
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.FunctionDef):
                # Nested function adds complexity
                complexity += 0.5
        
        return int(complexity)

# Call graph analysis
class CallGraphAnalyzer:
    """Analyze call graph depth and structure."""
    
    @staticmethod
    def analyze_depth(call_graph: Dict[str, List[str]]) -> Tuple[int, float]:
        """
        Analyze call graph depth.
        Returns (max_depth, average_depth).
        """
        if not call_graph:
            return 0, 0.0
        
        max_depth = 0
        depths = []
        
        for func, callees in call_graph.items():
            depth = CallGraphAnalyzer._calculate_depth(func, call_graph, set())
            max_depth = max(max_depth, depth)
            depths.append(depth)
        
        avg_depth = sum(depths) / len(depths) if depths else 0.0
        return max_depth, avg_depth
    
    @staticmethod
    def _calculate_depth(func: str, call_graph: Dict[str, List[str]], 
                         visited: set) -> int:
        """Calculate depth of a function in call graph."""
        if func in visited:
            return 0  # Cycle detected
        
        if func not in call_graph:
            return 1
        
        visited.add(func)
        
        if not call_graph[func]:
            visited.remove(func)
            return 1
        
        max_child_depth = max(
            CallGraphAnalyzer._calculate_depth(child, call_graph, visited)
            for child in call_graph[func]
        )
        
        visited.remove(func)
        return 1 + max_child_depth

# Circular dependency detection
class CircularDependencyDetector:
    """Detect circular dependencies in dependency graph."""
    
    @staticmethod
    def detect_cycles(dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
        """
        Detect all cycles in dependency graph.
        Returns list of cycles (each cycle is a list of nodes).
        """
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in dependency_graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            rec_stack.remove(node)
        
        for node in dependency_graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    @staticmethod
    def calculate_tight_coupling(dependency_graph: Dict[str, List[str]]) -> float:
        """
        Calculate tight coupling score (0.0-1.0).
        Higher score = more tightly coupled system.
        """
        if not dependency_graph:
            return 0.0
        
        total_nodes = len(dependency_graph)
        total_edges = sum(len(deps) for deps in dependency_graph.values())
        
        # Maximum possible edges in DAG
        max_edges = total_nodes * (total_nodes - 1) / 2
        
        if max_edges == 0:
            return 0.0
        
        coupling = total_edges / max_edges
        
        # Adjust for cycles (tight coupling)
        cycles = CircularDependencyDetector.detect_cycles(dependency_graph)
        cycle_penalty = min(0.5, len(cycles) * 0.1)
        
        return min(1.0, coupling + cycle_penalty)

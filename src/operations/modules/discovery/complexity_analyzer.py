"""
Code complexity analysis and metrics calculation
"""
import logging
from typing import Dict, Any

from .models import ASTNode, ComplexityMetrics

logger = logging.getLogger(__name__)


class ComplexityAnalyzer:
    """Calculate code complexity metrics"""
    
    def __init__(self):
        """Initialize complexity analyzer"""
        pass
    
    def calculate_cyclomatic_complexity(self, ast: ASTNode) -> int:
        """
        Calculate cyclomatic complexity (McCabe)
        
        Args:
            ast: AST node to analyze
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity
        decision_nodes = {
            'If', 'While', 'For', 'ExceptHandler', 'With',  # Python
            'if_statement', 'while_statement', 'for_statement', 'switch_statement',  # C#/JS
            'foreach_statement', 'catch_clause', 'conditional_expression'
        }
        
        def count_decisions(node: ASTNode) -> int:
            count = 0
            if node.node_type in decision_nodes:
                count += 1
            for child in node.children:
                count += count_decisions(child)
            return count
        
        return complexity + count_decisions(ast)
    
    def calculate_cognitive_complexity(self, ast: ASTNode) -> int:
        """
        Calculate cognitive complexity (SonarSource)
        
        Args:
            ast: AST node to analyze
            
        Returns:
            Cognitive complexity score
        """
        # Simplified: use cyclomatic as baseline
        # Real cognitive complexity adds penalties for nesting
        return self.calculate_cyclomatic_complexity(ast)
    
    def calculate_maintainability_index(self, metrics: Dict[str, Any]) -> float:
        """
        Calculate maintainability index
        
        Args:
            metrics: Dictionary of code metrics
            
        Returns:
            Maintainability index (0-100)
        """
        # Simplified MI calculation
        # Real formula: 171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)
        cc = metrics.get('cyclomatic_complexity', 1)
        loc = metrics.get('lines_of_code', 1)
        
        # Simplified: inverse relationship with complexity and size
        mi = 100 - (cc * 5) - (loc * 0.1)
        return max(0, min(100, mi))
    
    def analyze(self, ast: ASTNode) -> ComplexityMetrics:
        """
        Perform full complexity analysis
        
        Args:
            ast: AST node to analyze
            
        Returns:
            ComplexityMetrics with all calculated metrics
        """
        cyclomatic = self.calculate_cyclomatic_complexity(ast)
        cognitive = self.calculate_cognitive_complexity(ast)
        lines = ast.end_line - ast.start_line + 1
        
        mi = self.calculate_maintainability_index({
            'cyclomatic_complexity': cyclomatic,
            'lines_of_code': lines
        })
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            lines_of_code=lines,
            maintainability_index=mi
        )

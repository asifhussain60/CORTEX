"""
Phase 3: Performance Analysis

Identifies performance bottlenecks and optimization opportunities.

Author: Asif Hussain
Created: January 3, 2026
"""

import ast
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class PerformanceAnalysisPhase:
    """Phase 3: Analyze code for performance issues."""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.target_path = orchestrator.target_path
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute performance analysis.
        
        Returns:
            Dictionary containing performance issues and optimization suggestions
        """
        logger.info("Phase 3: Starting performance analysis")
        
        results = {
            "hotspots": [],
            "inefficient_patterns": [],
            "optimization_suggestions": [],
            "performance_score": 0
        }
        
        try:
            files = self._get_python_files()
            
            for file_path in files:
                file_hotspots = self._analyze_file_performance(file_path)
                results["hotspots"].extend(file_hotspots)
            
            # Detect common inefficient patterns
            results["inefficient_patterns"] = self._detect_inefficient_patterns()
            
            # Generate optimization suggestions
            results["optimization_suggestions"] = self._generate_optimizations(results)
            
            # Calculate performance score
            results["performance_score"] = self._calculate_performance_score(results)
            
            logger.info(f"Performance analysis complete: {len(results['hotspots'])} "
                       f"hotspots identified")
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}", exc_info=True)
            results["error"] = str(e)
        
        return results
    
    def _get_python_files(self) -> List[Path]:
        """Get list of Python files to analyze."""
        if self.target_path.is_file():
            return [self.target_path]
        
        python_files = list(self.target_path.rglob("*.py"))
        excluded = ["__pycache__", ".venv", "venv", "migrations", ".git"]
        return [f for f in python_files if not any(ex in str(f) for ex in excluded)]
    
    def _analyze_file_performance(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze performance of a single file."""
        hotspots = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Nested loops
                if isinstance(node, (ast.For, ast.While)):
                    depth = self._calculate_loop_depth(node)
                    if depth > 2:
                        hotspots.append({
                            "file": str(file_path),
                            "line": node.lineno,
                            "type": "nested_loops",
                            "severity": "high",
                            "message": f"Deeply nested loops (depth: {depth})",
                            "suggestion": "Consider refactoring to reduce nesting"
                        })
                
                # List comprehensions in loops
                if isinstance(node, (ast.For, ast.While)):
                    for child in ast.walk(node):
                        if isinstance(child, ast.ListComp):
                            hotspots.append({
                                "file": str(file_path),
                                "line": child.lineno,
                                "type": "list_comp_in_loop",
                                "severity": "medium",
                                "message": "List comprehension inside loop",
                                "suggestion": "Consider moving outside loop if possible"
                            })
                
                # String concatenation in loops
                if isinstance(node, ast.For):
                    for child in ast.walk(node):
                        if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                            if isinstance(child.target, ast.Name):
                                hotspots.append({
                                    "file": str(file_path),
                                    "line": child.lineno,
                                    "type": "string_concat_in_loop",
                                    "severity": "medium",
                                    "message": "String concatenation in loop",
                                    "suggestion": "Use list and join() instead"
                                })
        
        except Exception as e:
            logger.debug(f"Performance analysis failed for {file_path}: {e}")
        
        return hotspots
    
    def _calculate_loop_depth(self, node: ast.AST, current_depth: int = 1) -> int:
        """Calculate maximum nesting depth of loops."""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While)):
                child_depth = self._calculate_loop_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _detect_inefficient_patterns(self) -> List[Dict[str, Any]]:
        """Detect common inefficient patterns."""
        patterns = [
            {
                "pattern": "N+1 Query",
                "description": "Database queries inside loops",
                "impact": "High",
                "fix": "Use batch queries or prefetch_related"
            },
            {
                "pattern": "Global Variables",
                "description": "Excessive use of global state",
                "impact": "Medium",
                "fix": "Refactor to use parameters and return values"
            },
            {
                "pattern": "Premature Optimization",
                "description": "Complex optimizations without profiling",
                "impact": "Low",
                "fix": "Profile first, then optimize hotspots"
            }
        ]
        
        return patterns
    
    def _generate_optimizations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization suggestions based on analysis."""
        suggestions = []
        
        # Group hotspots by type
        hotspot_types = {}
        for hotspot in results["hotspots"]:
            htype = hotspot["type"]
            if htype not in hotspot_types:
                hotspot_types[htype] = []
            hotspot_types[htype].append(hotspot)
        
        # Generate suggestions
        for htype, instances in hotspot_types.items():
            if htype == "nested_loops":
                suggestions.append({
                    "optimization": "Reduce Loop Nesting",
                    "occurrences": len(instances),
                    "priority": "high",
                    "steps": [
                        "Extract inner loops to separate functions",
                        "Consider using itertools for complex iterations",
                        "Use generator expressions where appropriate"
                    ]
                })
            
            elif htype == "list_comp_in_loop":
                suggestions.append({
                    "optimization": "Optimize List Comprehensions",
                    "occurrences": len(instances),
                    "priority": "medium",
                    "steps": [
                        "Move comprehensions outside loops when possible",
                        "Consider using generators instead of lists",
                        "Use map/filter for simple transformations"
                    ]
                })
        
        return suggestions
    
    def _calculate_performance_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall performance score (0-100)."""
        score = 100
        
        # Deduct points for hotspots
        severity_penalties = {
            "high": 15,
            "medium": 10,
            "low": 5
        }
        
        for hotspot in results["hotspots"]:
            severity = hotspot.get("severity", "low")
            score -= severity_penalties.get(severity, 5)
        
        return max(0, min(100, score))

"""
Dead Code Detector

Identifies unused code (untested + uncalled) for safe removal recommendations.

Author: CORTEX Architect  
Phase: Phase 66 S4
"""

from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict


class DeadCodeDetector:
    """
    Detect dead code from coverage and execution data.
    
    Capabilities:
    - Untested function detection (0% coverage)
    - Uncalled function detection (0 executions)
    - Dead code candidate identification (untested + uncalled)
    - Unused import detection
    - Redundant code identification (duplicates)
    - Dead code severity scoring
    - Removal candidate prioritization
    - Deprecated pattern detection
    - Removal impact analysis
    - Actionable removal recommendations
    
    Usage:
        >>> detector = DeadCodeDetector()
        >>> dead = detector.identify_dead_code_candidates(coverage, execution)
        >>> recommendations = detector.generate_removal_recommendations(dead)
    """
    
    def __init__(self):
        self.deprecated_patterns = [
            "eval()", "exec()", "string.atoi", "has_key", "__cmp__"
        ]
    
    def detect_untested_functions(
        self,
        coverage_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Detect functions with zero test coverage.
        
        Args:
            coverage_data: Coverage data per file
            
        Returns:
            List of untested function dictionaries
        """
        untested = []
        
        for file_path, file_data in coverage_data.items():
            functions = file_data.get("functions", [])
            
            for func in functions:
                if not func.get("covered", False):
                    untested.append({
                        "file": file_path,
                        "name": func["name"],
                        "coverage_percent": func.get("coverage_percent", 0.0)
                    })
        
        return untested
    
    def detect_uncalled_functions(
        self,
        execution_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Detect functions never called in execution.
        
        Args:
            execution_data: Execution data per file
            
        Returns:
            List of uncalled function dictionaries
        """
        uncalled = []
        
        for file_path, file_data in execution_data.items():
            functions = file_data.get("functions", [])
            
            for func in functions:
                if func.get("call_count", 0) == 0:
                    uncalled.append({
                        "file": file_path,
                        "name": func["name"],
                        "call_count": 0
                    })
        
        return uncalled
    
    def identify_dead_code_candidates(
        self,
        coverage_data: Dict[str, Any],
        execution_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identify dead code (untested + uncalled).
        
        Args:
            coverage_data: Coverage data
            execution_data: Execution data
            
        Returns:
            List of dead code candidate dictionaries
        """
        candidates = []
        
        # Find intersection of untested and uncalled
        for file_path in coverage_data.keys():
            if file_path not in execution_data:
                continue
            
            coverage_funcs = {
                f["name"]: f
                for f in coverage_data[file_path].get("functions", [])
            }
            
            execution_funcs = {
                f["name"]: f
                for f in execution_data[file_path].get("functions", [])
            }
            
            # Check each function
            for func_name in coverage_funcs.keys():
                coverage_func = coverage_funcs[func_name]
                execution_func = execution_funcs.get(func_name, {})
                
                # Dead if untested AND uncalled
                if (not coverage_func.get("covered", False) and
                    execution_func.get("call_count", 0) == 0):
                    
                    candidates.append({
                        "file": file_path,
                        "name": func_name,
                        "coverage_percent": coverage_func.get("coverage_percent", 0.0),
                        "call_count": 0
                    })
        
        return candidates
    
    def detect_unused_imports(
        self,
        import_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Detect imported but unused modules.
        
        Args:
            import_data: Import and usage data per file
            
        Returns:
            List of unused import dictionaries
        """
        unused = []
        
        for file_path, file_data in import_data.items():
            imports = set(file_data.get("imports", []))
            used_symbols = file_data.get("used_symbols", [])
            
            # Extract module names from used symbols
            used_modules = set()
            for symbol in used_symbols:
                module = symbol.split(".")[0]
                used_modules.add(module)
            
            # Find unused
            unused_in_file = imports - used_modules
            
            for module in unused_in_file:
                unused.append({
                    "file": file_path,
                    "module": module
                })
        
        return unused
    
    def identify_redundant_code(
        self,
        code_signatures: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify redundant/duplicate code.
        
        Args:
            code_signatures: List of function signatures with hashes
            
        Returns:
            List of redundant code groups
        """
        # Group by signature hash
        hash_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        for signature in code_signatures:
            sig_hash = signature.get("signature_hash", "")
            hash_groups[sig_hash].append(signature)
        
        # Find duplicates
        redundant = []
        
        for sig_hash, functions in hash_groups.items():
            if len(functions) > 1:
                redundant.append({
                    "signature_hash": sig_hash,
                    "functions": functions,
                    "count": len(functions)
                })
        
        return redundant
    
    def calculate_dead_code_score(self, function_data: Dict[str, Any]) -> float:
        """
        Calculate dead code severity score.
        
        Higher score = more confident it's dead
        
        Score factors:
        - Coverage: 0% = +0.4
        - Call count: 0 = +0.3
        - Age: >365 days = +0.2
        - Complexity: >10 = +0.1
        
        Args:
            function_data: Function metadata
            
        Returns:
            Dead code score 0.0-1.0
        """
        score = 0.0
        
        # Coverage factor
        if function_data.get("coverage_percent", 0.0) == 0.0:
            score += 0.4
        
        # Call count factor
        if function_data.get("call_count", 0) == 0:
            score += 0.3
        
        # Age factor (old code more likely truly dead)
        age_days = function_data.get("age_days", 0)
        if age_days > 365:
            score += 0.2
        elif age_days > 180:
            score += 0.1
        
        # Complexity factor (complex dead code = waste)
        complexity = function_data.get("complexity", 0)
        if complexity > 10:
            score += 0.1
        
        return min(score, 1.0)
    
    def prioritize_removal_candidates(
        self,
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Prioritize dead code for removal.
        
        Args:
            candidates: List of dead code candidates
            
        Returns:
            Prioritized list with priority scores
        """
        prioritized = []
        
        for candidate in candidates:
            score = self.calculate_dead_code_score(candidate)
            
            candidate_copy = candidate.copy()
            candidate_copy["priority"] = score
            prioritized.append(candidate_copy)
        
        # Sort by priority descending
        prioritized.sort(key=lambda x: x["priority"], reverse=True)
        
        return prioritized
    
    def detect_deprecated_patterns(
        self,
        code_patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect deprecated code patterns.
        
        Args:
            code_patterns: List of detected code patterns
            
        Returns:
            List of deprecated pattern matches
        """
        deprecated = []
        
        for pattern in code_patterns:
            # Already marked as deprecated in input
            if "severity" in pattern:
                deprecated.append(pattern)
        
        return deprecated
    
    def build_removal_impact_analysis(
        self,
        candidate: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze impact of removing dead code.
        
        Args:
            candidate: Dead code candidate
            
        Returns:
            Impact analysis dictionary
        """
        imported_by = candidate.get("imported_by", [])
        calls_to = candidate.get("calls_to", [])
        
        # Safe if no imports and no critical dependencies
        safe_to_remove = len(imported_by) == 0
        
        risk_level = "low" if safe_to_remove else "high"
        
        return {
            "safe_to_remove": safe_to_remove,
            "risk_level": risk_level,
            "imported_by_count": len(imported_by),
            "dependencies": calls_to,
            "dependency_count": len(calls_to)
        }
    
    def generate_removal_recommendations(
        self,
        dead_code: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable removal recommendations.
        
        Args:
            dead_code: List of dead code candidates
            
        Returns:
            List of recommendations with actions
        """
        recommendations = []
        
        for candidate in dead_code:
            score = candidate.get("score", 0.0)
            safe_to_remove = candidate.get("safe_to_remove", False)
            
            # Determine action
            if score >= 0.8 and safe_to_remove:
                action = "remove"
            elif score >= 0.6:
                action = "review"
            else:
                action = "monitor"
            
            recommendation = {
                "file": candidate.get("file", ""),
                "function": candidate.get("function", candidate.get("name", "")),
                "action": action,
                "score": score,
                "rationale": self._generate_rationale(candidate, action)
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    # Private helper methods
    
    def _generate_rationale(self, candidate: Dict[str, Any], action: str) -> str:
        """Generate human-readable rationale for recommendation"""
        if action == "remove":
            return f"High confidence dead code: 0% coverage, 0 calls, safe to remove"
        elif action == "review":
            return f"Likely dead code: Low usage detected, manual review recommended"
        else:
            return f"Monitor: Low confidence, continue tracking"

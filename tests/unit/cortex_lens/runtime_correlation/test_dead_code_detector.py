"""
Tests for Dead Code Detector

Validates detection of unused code (untested + uncalled) for knowledge graph insights.

Author: CORTEX Architect
Phase: Phase 66 S4
"""

import pytest
from typing import Dict, Any, List


class TestDeadCodeDetector:
    """Test suite for dead code detection"""
    
    def test_detect_untested_functions(self):
        """Test detecting functions with zero test coverage"""
        from cortex_lens.runtime_correlation.dead_code_detector import DeadCodeDetector
        
        coverage_data = {
            "cortex/module.py": {
                "functions": [
                    {"name": "tested_func", "covered": True, "coverage_percent": 100.0},
                    {"name": "untested_func", "covered": False, "coverage_percent": 0.0}
                ]
            }
        }
        
        detector = DeadCodeDetector()
        untested = detector.detect_untested_functions(coverage_data)
        
        assert len(untested) >= 1
        assert any(f["name"] == "untested_func" for f in untested)
        assert all(f["coverage_percent"] == 0.0 for f in untested)
    
    def test_detect_uncalled_functions(self):
        """Test detecting functions never called in execution"""
        from cortex_lens.runtime_correlation.dead_code_detector import DeadCodeDetector
        
        execution_data = {
            "cortex/module.py": {
                "functions": [
                    {"name": "called_func", "call_count": 50},
                    {"name": "never_called", "call_count": 0}
                ]
            }
        }
        
        detector = DeadCodeDetector()
        uncalled = detector.detect_uncalled_functions(execution_data)
        
        assert len(uncalled) >= 1
        assert any(f["name"] == "never_called" for f in uncalled)
    
    def test_identify_dead_code_candidates(self):
        """Test identifying dead code (untested + uncalled)"""
        from cortex_lens.runtime_correlation.dead_code_detector import DeadCodeDetector
        
        coverage_data = {
            "cortex/old_module.py": {
                "functions": [
                    {"name": "dead_func", "covered": False, "coverage_percent": 0.0}
                ]
            }
        }
        
        execution_data = {
            "cortex/old_module.py": {
                "functions": [
                    {"name": "dead_func", "call_count": 0}
                ]
            }
        }
        
        detector = DeadCodeDetector()
        candidates = detector.identify_dead_code_candidates(coverage_data, execution_data)
        
        assert len(candidates) >= 1
        dead = candidates[0]
        assert dead["name"] == "dead_func"
        assert dead["coverage_percent"] == 0.0
        assert dead["call_count"] == 0
    
    def test_detect_unused_imports(self):
        """Test detecting imported but unused modules"""
        from cortex_lens.runtime_correlation.dead_code_detector import DeadCodeDetector
        
        import_data = {
            "cortex/module.py": {
                "imports": ["os", "sys", "json", "unused_module"],
                "used_symbols": ["os.path", "sys.exit", "json.loads"]
            }
        }
        
        detector = DeadCodeDetector()
        unused = detector.detect_unused_imports(import_data)
        
        assert len(unused) >= 1
        assert any(u["module"] == "unused_module" for u in unused)
    
    def test_identify_redundant_code(self):
        """Test identifying redundant/duplicate code"""
        from cortex_lens.runtime_correlation.dead_code_detector import DeadCodeDetector
        
        code_signatures = [
            {"file": "a.py", "function": "func_a", "signature_hash": "abc123"},
            {"file": "b.py", "function": "func_b", "signature_hash": "abc123"},  # Duplicate
            {"file": "c.py", "function": "func_c", "signature_hash": "def456"}
        ]
        
        detector = DeadCodeDetector()
        redundant = detector.identify_redundant_code(code_signatures)
        
        assert len(redundant) >= 1
        # Should find func_a and func_b as redundant
        dup_group = redundant[0]
        assert len(dup_group["functions"]) == 2
        assert dup_group["signature_hash"] == "abc123"
    
    def test_calculate_dead_code_score(self):
        """Test calculating dead code severity score"""
        from cortex_lens.runtime_correlation.dead_code_detector import DeadCodeDetector
        
        function_data = {
            "coverage_percent": 0.0,
            "call_count": 0,
            "age_days": 365,  # Old code
            "complexity": 10  # Complex but dead
        }
        
        detector = DeadCodeDetector()
        score = detector.calculate_dead_code_score(function_data)
        
        assert score > 0
        assert isinstance(score, float)
        # Higher score = more confident it's dead
    
    def test_prioritize_removal_candidates(self):
        """Test prioritizing dead code for removal"""
        from cortex_lens.runtime_correlation.dead_code_detector import DeadCodeDetector
        
        candidates = [
            {"name": "func_a", "coverage": 0.0, "calls": 0, "age_days": 30, "complexity": 5},
            {"name": "func_b", "coverage": 0.0, "calls": 0, "age_days": 365, "complexity": 15},
            {"name": "func_c", "coverage": 10.0, "calls": 5, "age_days": 10, "complexity": 3}
        ]
        
        detector = DeadCodeDetector()
        prioritized = detector.prioritize_removal_candidates(candidates)
        
        # Should prioritize func_b (oldest, most complex, truly dead)
        assert prioritized[0]["name"] == "func_b"
        assert all("priority" in c for c in prioritized)
    
    def test_detect_deprecated_patterns(self):
        """Test detecting deprecated code patterns"""
        from cortex_lens.runtime_correlation.dead_code_detector import DeadCodeDetector
        
        code_patterns = [
            {"file": "old.py", "pattern": "eval()", "line": 10, "severity": "high"},
            {"file": "legacy.py", "pattern": "string.atoi", "line": 25, "severity": "medium"}
        ]
        
        detector = DeadCodeDetector()
        deprecated = detector.detect_deprecated_patterns(code_patterns)
        
        assert len(deprecated) >= 2
        assert any(d["severity"] == "high" for d in deprecated)
    
    def test_build_removal_impact_analysis(self):
        """Test analyzing impact of removing dead code"""
        from cortex_lens.runtime_correlation.dead_code_detector import DeadCodeDetector
        
        candidate = {
            "file": "cortex/old_module.py",
            "function": "old_func",
            "imported_by": [],  # No imports
            "calls_to": ["helper_func"]  # Calls other functions
        }
        
        detector = DeadCodeDetector()
        impact = detector.build_removal_impact_analysis(candidate)
        
        assert impact["safe_to_remove"] == True  # No imports
        assert len(impact["dependencies"]) == 1  # calls_to helper_func
        assert "risk_level" in impact
    
    def test_generate_removal_recommendations(self):
        """Test generating actionable removal recommendations"""
        from cortex_lens.runtime_correlation.dead_code_detector import DeadCodeDetector
        
        dead_code = [
            {"file": "a.py", "function": "old_a", "score": 0.95, "safe_to_remove": True},
            {"file": "b.py", "function": "maybe_dead", "score": 0.6, "safe_to_remove": False}
        ]
        
        detector = DeadCodeDetector()
        recommendations = detector.generate_removal_recommendations(dead_code)
        
        assert len(recommendations) >= 2
        # Should recommend removing old_a (high score + safe)
        assert recommendations[0]["action"] == "remove"
        assert recommendations[0]["function"] == "old_a"
        # Maybe review maybe_dead
        assert recommendations[1]["action"] in ["review", "monitor"]


class TestDeadCodeDetectorIntegration:
    """Integration tests for dead code detector"""
    
    def test_end_to_end_dead_code_detection(self):
        """Test complete dead code detection workflow"""
        from cortex_lens.runtime_correlation.dead_code_detector import DeadCodeDetector
        
        coverage_data = {
            "cortex/old.py": {
                "functions": [
                    {"name": "dead_func", "covered": False, "coverage_percent": 0.0},
                    {"name": "active_func", "covered": True, "coverage_percent": 90.0}
                ]
            }
        }
        
        execution_data = {
            "cortex/old.py": {
                "functions": [
                    {"name": "dead_func", "call_count": 0},
                    {"name": "active_func", "call_count": 150}
                ]
            }
        }
        
        detector = DeadCodeDetector()
        
        # Detect untested
        untested = detector.detect_untested_functions(coverage_data)
        assert any(f["name"] == "dead_func" for f in untested)
        
        # Detect uncalled
        uncalled = detector.detect_uncalled_functions(execution_data)
        assert any(f["name"] == "dead_func" for f in uncalled)
        
        # Identify dead code
        candidates = detector.identify_dead_code_candidates(coverage_data, execution_data)
        assert len(candidates) >= 1
        assert candidates[0]["name"] == "dead_func"
        
        # Generate recommendations
        recommendations = detector.generate_removal_recommendations(candidates)
        assert len(recommendations) >= 1
    
    def test_comprehensive_dead_code_analysis(self):
        """Test comprehensive analysis with all detection methods"""
        from cortex_lens.runtime_correlation.dead_code_detector import DeadCodeDetector
        
        # Full dataset
        coverage_data = {
            "cortex/legacy.py": {
                "functions": [
                    {"name": "func1", "covered": False, "coverage_percent": 0.0},
                    {"name": "func2", "covered": False, "coverage_percent": 0.0}
                ]
            }
        }
        
        execution_data = {
            "cortex/legacy.py": {
                "functions": [
                    {"name": "func1", "call_count": 0},
                    {"name": "func2", "call_count": 0}
                ]
            }
        }
        
        import_data = {
            "cortex/legacy.py": {
                "imports": ["unused_lib"],
                "used_symbols": []
            }
        }
        
        detector = DeadCodeDetector()
        
        # Run all detections
        dead_funcs = detector.identify_dead_code_candidates(coverage_data, execution_data)
        unused_imports = detector.detect_unused_imports(import_data)
        prioritized = detector.prioritize_removal_candidates(dead_funcs)
        
        # Validate comprehensive results
        assert len(dead_funcs) == 2
        assert len(unused_imports) >= 1
        assert len(prioritized) == 2
        assert prioritized[0]["priority"] >= prioritized[1]["priority"]

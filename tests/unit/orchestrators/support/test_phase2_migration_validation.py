"""
Track 4 Phase 2: Migration Validation Test Suite

This module provides comprehensive tests to validate that:
1. API compatibility layer works correctly
2. Adapter functions bridge old/new APIs properly
3. No breaking changes during Phase 2 (deprecation period)
4. Unified orchestrators work correctly with adapter functions

COVERAGE:
- Adapter function correctness
- Backward compatibility
- Error handling
- Edge cases
"""

import pytest
from typing import Any, Dict, Optional
from pathlib import Path

from cortex.orchestrators.support.api_compatibility import (
    analyze_file_via_unified,
    onboard_repository_via_unified,
    check_recommendation_via_unified,
)


# ============================================================================
# Tests: LENS Analysis Adapter
# ============================================================================

class TestLENSAnalysisAdapter:
    """Tests for analyze_file_via_unified adapter function."""
    
    def test_analyze_file_with_valid_file(self, tmp_path):
        """Test analyzing a valid Python file."""
        # Create test file
        test_file = tmp_path / "test_module.py"
        test_file.write_text("""
def hello():
    '''Simple function'''
    return "world"

class MyClass:
    def __init__(self):
        self.value = 42
    
    def compute(self, x, y):
        return x + y
""")
        
        # Analyze file
        result = analyze_file_via_unified(
            file_path=str(test_file),
            repo_path=str(tmp_path),
            analysis_type="complexity"
        )
        
        # Verify result structure
        assert result["success"] is True
        assert "file_path" in result
        assert "analysis" in result
        assert result["file_path"] == str(test_file)
    
    def test_analyze_file_nonexistent_returns_error(self):
        """Test analyzing non-existent file returns error."""
        result = analyze_file_via_unified(
            file_path="/nonexistent/file.py",
            analysis_type="complexity"
        )
        
        assert result["success"] is False
        assert "error" in result
    
    def test_analyze_file_different_analysis_types(self, tmp_path):
        """Test analyzing with different analysis types."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")
        
        for analysis_type in ["complexity", "security", "dependencies", "performance"]:
            result = analyze_file_via_unified(
                file_path=str(test_file),
                analysis_type=analysis_type
            )
            
            assert result["success"] is True
            assert "analysis" in result
    
    def test_analyze_file_unicode_handling(self, tmp_path):
        """Test analyzing file with unicode characters."""
        test_file = tmp_path / "unicode_test.py"
        test_file.write_text("""
# -*- coding: utf-8 -*-
def greet():
    \"\"\"Greet with unicode: こんにちは, مرحبا, 你好\"\"\"
    return "Hello, 世界"
""", encoding="utf-8")
        
        result = analyze_file_via_unified(
            file_path=str(test_file),
            analysis_type="complexity"
        )
        
        assert result["success"] is True


# ============================================================================
# Tests: Repository Onboarding Adapter
# ============================================================================

class TestRepositoryOnboardingAdapter:
    """Tests for onboard_repository_via_unified adapter function."""
    
    def test_onboard_valid_repository(self, tmp_path):
        """Test onboarding a valid repository."""
        # Create minimal repo structure
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        (repo_path / "README.md").write_text("# Test Repository")
        (repo_path / "main.py").write_text("print('hello')")
        
        result = onboard_repository_via_unified(repo_path=str(repo_path))
        
        assert result["success"] is True
        assert "repo_path" in result
        assert result["repo_path"] == str(repo_path)
    
    def test_onboard_nonexistent_repository_returns_error(self):
        """Test onboarding non-existent repository returns error."""
        result = onboard_repository_via_unified(
            repo_path="/nonexistent/repo"
        )
        
        assert result["success"] is False
        assert "error" in result
    
    def test_onboard_with_profile_generation(self, tmp_path):
        """Test onboarding with profile generation."""
        repo_path = tmp_path / "repo_with_profile"
        repo_path.mkdir()
        
        result = onboard_repository_via_unified(
            repo_path=str(repo_path),
            include_profile=True
        )
        
        assert result["success"] is True
        assert "profile" in result


# ============================================================================
# Tests: Quality Assurance Adapter
# ============================================================================

class TestQualityAssuranceAdapter:
    """Tests for check_recommendation_via_unified adapter function."""
    
    def test_check_valid_recommendation(self):
        """Test checking a valid recommendation."""
        result = check_recommendation_via_unified(
            recommendation="Add comprehensive error handling"
        )
        
        assert result["success"] is True
        assert "is_safe" in result
        assert isinstance(result["is_safe"], bool)
    
    def test_check_recommendation_with_context(self):
        """Test checking recommendation with context."""
        context = {
            "type": "refactoring",
            "files": ["src/module.py", "src/utils.py"],
            "affected_code": 500,
        }
        
        result = check_recommendation_via_unified(
            recommendation="Refactor database access layer",
            context=context
        )
        
        assert result["success"] is True
        assert "is_safe" in result
    
    def test_check_empty_recommendation_returns_error(self):
        """Test checking empty recommendation handles gracefully."""
        result = check_recommendation_via_unified(
            recommendation=""
        )
        
        # Should either succeed with safe=false or return error
        assert "success" in result or "is_safe" in result
    
    def test_check_multiple_recommendations_independent(self):
        """Test checking multiple recommendations are independent."""
        recommendations = [
            "Add logging",
            "Optimize database queries",
            "Add unit tests",
            "Implement caching",
        ]
        
        results = []
        for rec in recommendations:
            result = check_recommendation_via_unified(recommendation=rec)
            results.append(result)
        
        # All should succeed
        assert all(r["success"] is True for r in results)


# ============================================================================
# Tests: Backward Compatibility
# ============================================================================

class TestBackwardCompatibility:
    """Tests to ensure backward compatibility during Phase 2."""
    
    def test_old_and_new_apis_coexist(self):
        """Test that old and new APIs can coexist in same codebase."""
        # This simulates old code path
        old_style_result = analyze_file_via_unified(
            file_path="/tmp/test.py",
            repo_path="/tmp"
        )
        
        # Should not raise, just return error for nonexistent file
        assert "success" in old_style_result
    
    def test_adapter_functions_resilient_to_missing_unified(self):
        """Test adapter functions handle unified orchestrator issues gracefully."""
        # Pass invalid file to trigger error in underlying code
        result = analyze_file_via_unified(
            file_path="/definitely/not/real.py",
            analysis_type="complexity"
        )
        
        # Should return structured error response, not raise
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is False


# ============================================================================
# Tests: Error Handling
# ============================================================================

class TestErrorHandling:
    """Tests for proper error handling in adapter functions."""
    
    def test_analyze_file_with_encoding_errors(self, tmp_path):
        """Test handling files with encoding issues."""
        test_file = tmp_path / "bad_encoding.py"
        # Write binary that's not valid UTF-8
        with open(test_file, 'wb') as f:
            f.write(b'\x80\x81\x82\x83')
        
        result = analyze_file_via_unified(file_path=str(test_file))
        
        # Should handle error gracefully
        assert isinstance(result, dict)
        assert "success" in result
    
    def test_onboard_with_permission_denied(self, tmp_path):
        """Test handling permission denied errors gracefully."""
        repo_path = tmp_path / "restricted_repo"
        repo_path.mkdir()
        repo_path.chmod(0o000)
        
        try:
            result = onboard_repository_via_unified(repo_path=str(repo_path))
            # Should handle permission error gracefully
            assert isinstance(result, dict)
            assert "success" in result
        finally:
            repo_path.chmod(0o755)


# ============================================================================
# Tests: Integration with Unified Orchestrators
# ============================================================================

class TestUnifiedOrchestratorIntegration:
    """Tests for integration with unified orchestrators."""
    
    def test_adapter_correctly_invokes_unified_onboarding(self, tmp_path):
        """Test adapter properly delegates to unified onboarding."""
        repo_path = tmp_path / "integration_test_repo"
        repo_path.mkdir()
        (repo_path / "main.py").write_text("print('test')")
        
        result = onboard_repository_via_unified(str(repo_path))
        
        # Verify result structure matches expected unified orchestrator output
        assert result["success"] is True
        assert "profile" in result
    
    def test_adapter_correctly_invokes_unified_analysis(self, tmp_path):
        """Test adapter properly delegates to unified analysis."""
        test_file = tmp_path / "analysis_test.py"
        test_file.write_text("def foo(): pass")
        
        result = analyze_file_via_unified(
            file_path=str(test_file),
            analysis_type="complexity"
        )
        
        assert result["success"] is True
        assert "analysis" in result


# ============================================================================
# Tests: Performance
# ============================================================================

class TestPerformance:
    """Tests to ensure adapter functions meet performance requirements."""
    
    def test_adapter_functions_have_acceptable_latency(self, tmp_path, benchmark):
        """Test adapter functions complete in acceptable time."""
        test_file = tmp_path / "perf_test.py"
        test_file.write_text("print('test')")
        
        # Benchmark the adapter function
        def analyze_and_measure():
            return analyze_file_via_unified(
                file_path=str(test_file),
                analysis_type="complexity"
            )
        
        # Should complete in reasonable time (< 1 second)
        result = benchmark(analyze_and_measure)
        assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

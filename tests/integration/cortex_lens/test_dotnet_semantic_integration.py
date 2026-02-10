"""
Integration Test: Phase 67 S1 S8 - Phase 55 Integration with Roslyn Semantic Model

Tests the integration of Roslyn semantic capabilities (Phase 67 S1)
with Phase 55 DotNetLensAnalyzer for hybrid syntax + semantic analysis.

AC_START: AC-PHASE67-S1-S8-INTEGRATION-TEST-001
"""

import pytest
from pathlib import Path
from cortex.lens.dotnet_analyzer import DotNetLensAnalyzer


class TestDotNetSemanticIntegration:
    """
    Integration tests for DotNetLensAnalyzer with semantic mode.
    
    Tests both syntax-only and hybrid (syntax + semantic) analysis modes.
    """
    
    def test_analyzer_init_syntax_mode(self):
        """Test analyzer initialization in syntax-only mode (default)."""
        analyzer = DotNetLensAnalyzer(semantic_mode=False)
        
        assert analyzer.semantic_mode is False
        assert analyzer.roslyn_builder is None
        assert hasattr(analyzer, 'solution_parser')
        assert hasattr(analyzer, 'project_parser')
        assert hasattr(analyzer, 'monolith_analyzer')
    
    def test_analyzer_init_semantic_mode(self):
        """Test analyzer initialization in semantic mode."""
        analyzer = DotNetLensAnalyzer(semantic_mode=True)
        
        # May fallback to False if Roslyn unavailable
        if analyzer.semantic_mode:
            assert analyzer.roslyn_builder is not None
        else:
            # Graceful degradation to syntax-only
            assert analyzer.roslyn_builder is None
    
    def test_syntax_only_analysis(self):
        """Test syntax-only analysis (Phase 55 baseline)."""
        analyzer = DotNetLensAnalyzer(semantic_mode=False)
        
        # Sample .sln content
        sln_content = '''
Microsoft Visual Studio Solution File, Format Version 12.00
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "TestProject", "TestProject.csproj", "{12345678-1234-1234-1234-123456789012}"
EndProject
Global
EndGlobal
'''
        
        result = analyzer.analyze_solution_file("TestSolution.sln", sln_content)
        
        assert "error" not in result
        assert result["mode"] == "syntax"
        assert "solution_name" in result
        assert "project_count" in result
        assert result["project_count"] == 1
        assert "semantic" not in result  # No semantic data in syntax-only mode
    
    @pytest.mark.integration
    def test_hybrid_analysis_requires_real_solution(self, temp_dotnet_solution):
        """
        Test hybrid (syntax + semantic) analysis on real .NET solution.
        
        Requires:
        - Compiled .NET solution (dotnet build)
        - Roslyn CLI available
        - Phase 67 S1 components operational
        """
        import subprocess
        
        analyzer = DotNetLensAnalyzer(semantic_mode=True)
        
        # Skip if semantic mode unavailable
        if not analyzer.semantic_mode:
            pytest.skip("Semantic mode unavailable (Roslyn components not installed)")
        
        solution_path = temp_dotnet_solution / "TestSolution.sln"
        
        # Build solution first (required for semantic analysis)
        build_result = subprocess.run(
            ["dotnet", "build", str(solution_path)],
            capture_output=True,
            text=True
        )
        
        assert build_result.returncode == 0, f"Build failed: {build_result.stderr}"
        
        # Load solution content
        sln_content = solution_path.read_text()
        
        # Analyze with semantic mode
        result = analyzer.analyze_solution_file(str(solution_path), sln_content)
        
        # Verify hybrid analysis
        assert "error" not in result
        assert result["mode"] in ["syntax", "hybrid"]  # hybrid if semantic succeeded
        assert "solution_name" in result
        assert "project_count" in result
        
        # If semantic succeeded, verify semantic data
        if result["mode"] == "hybrid":
            assert "semantic" in result
            semantic = result["semantic"]
            
            # Verify semantic structure
            assert "type_count" in semantic
            assert "type_names" in semantic
            assert "dependencies" in semantic
            assert "api_controllers" in semantic
            assert "authorized_types" in semantic
            assert "method_summary" in semantic
            
            # Verify dependency analysis
            deps = semantic["dependencies"]
            assert "graph" in deps
            assert "build_order" in deps
            assert "circular_refs" in deps
            assert isinstance(deps["build_order"], list)
            
            # Verify method summary
            methods = semantic["method_summary"]
            assert "total_methods" in methods
            assert "public_methods" in methods
            assert "static_methods" in methods
            assert isinstance(methods["total_methods"], int)
    
    def test_semantic_analysis_graceful_degradation(self):
        """Test graceful degradation when semantic analysis fails."""
        analyzer = DotNetLensAnalyzer(semantic_mode=True)
        
        # Non-existent solution
        result = analyzer.analyze_solution_file(
            "/nonexistent/solution.sln",
            "Invalid content"
        )
        
        # Should return syntax analysis result (may have parsing errors)
        # but should NOT crash
        assert isinstance(result, dict)
    
    def test_backward_compatibility(self):
        """Test that Phase 55 code works without Phase 67 S1 changes."""
        # Default mode (no semantic_mode param) should work
        analyzer = DotNetLensAnalyzer()
        
        assert analyzer.semantic_mode is False  # Default is syntax-only
        assert hasattr(analyzer, 'solution_parser')
        
        # Existing syntax analysis should work unchanged
        sln_content = '''
Microsoft Visual Studio Solution File, Format Version 12.00
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Legacy", "Legacy.csproj", "{ABCDEF01-1234-1234-1234-123456789012}"
EndProject
Global
EndGlobal
'''
        
        result = analyzer.analyze_solution_file("Legacy.sln", sln_content)
        
        assert "error" not in result
        assert result["mode"] == "syntax"
        assert result["project_count"] == 1


# AC_COMPLETE: AC-PHASE67-S1-S8-INTEGRATION-TEST-001 ✅ Integration tests complete

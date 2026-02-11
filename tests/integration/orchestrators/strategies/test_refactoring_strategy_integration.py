"""
ENH-090 Track 2 Stage 1: Refactoring Strategy Integration Tests

Integration tests validating end-to-end refactoring workflows.

Authority: ENH-087 Track 2 + CORE-035
Compliance: CORE-008 (TDD), CORE-011 (type hints)

AC_START: AC-ENH090-S1-REFACTOR-001
Description: Integration tests for refactoring strategy end-to-end workflows
"""

import pytest
from pathlib import Path

from cortex.orchestrators.strategies.refactoring_strategy_pattern import (
    RefactoringOperationType,
    RefactoringLanguage,
    StrategyExecutionMode,
    RefactoringRequest,
    RefactoringMetrics,
    RefactoringResult,
    UnifiedRefactoringOrchestrator,
)


class TestRefactoringStrategyIntegration:
    """Integration tests for end-to-end refactoring workflows."""
    
    @pytest.fixture
    def orchestrator(self) -> UnifiedRefactoringOrchestrator:
        """Create orchestrator instance."""
        return UnifiedRefactoringOrchestrator()
    
    # -----------------------------------------------------------------------
    # INTEGRATION TEST 1: Multiple Operations in Sequence
    # -----------------------------------------------------------------------
    def test_execute_multiple_operations_sequentially(self, orchestrator):
        """Execute multiple refactoring operations in sequence."""
        test_file = Path("cortex/test.py")
        
        # Operation 1: Rename
        result1 = orchestrator.execute_refactoring(
            RefactoringRequest(
                operation=RefactoringOperationType.RENAME,
                file_path=test_file,
                language=RefactoringLanguage.PYTHON,
                parameters={"new_name": "new_name"}
            )
        )
        assert result1.success
        
        # Operation 2: Extract method
        result2 = orchestrator.execute_refactoring(
            RefactoringRequest(
                operation=RefactoringOperationType.EXTRACT_METHOD,
                file_path=test_file,
                language=RefactoringLanguage.PYTHON,
                parameters={
                    "start_line": 10,
                    "end_line": 20,
                    "method_name": "extracted"
                }
            )
        )
        assert result2.success
        
        # Operation 3: SOLID violations
        result3 = orchestrator.execute_refactoring(
            RefactoringRequest(
                operation=RefactoringOperationType.REFACTOR_SOLID_VIOLATIONS,
                file_path=test_file,
                language=RefactoringLanguage.PYTHON,
                parameters={"target_class": "MyClass"}
            )
        )
        assert result3.success
    
    # -----------------------------------------------------------------------
    # INTEGRATION TEST 2: Cross-Language Support
    # -----------------------------------------------------------------------
    def test_refactoring_across_multiple_languages(self, orchestrator):
        """Verify refactoring works across different languages."""
        test_operations = [
            (RefactoringLanguage.PYTHON, "python_file.py"),
            (RefactoringLanguage.CSHARP, "cs_file.cs"),
            (RefactoringLanguage.TYPESCRIPT, "ts_file.ts"),
        ]
        
        for language, filename in test_operations:
            result = orchestrator.execute_refactoring(
                RefactoringRequest(
                    operation=RefactoringOperationType.RENAME,
                    file_path=Path(filename),
                    language=language,
                    parameters={"new_name": "renamed"}
                )
            )
            assert result.success, f"Failed for {language.value}"
            assert result.strategy_used == "BasicRefactoringStrategy"
    
    # -----------------------------------------------------------------------
    # INTEGRATION TEST 3: Error Handling & Recovery
    # -----------------------------------------------------------------------
    def test_invalid_parameters_dont_crash_orchestrator(self, orchestrator):
        """Invalid parameters should not crash orchestrator."""
        test_file = Path("cortex/test.py")
        
        # Invalid operation (unsupported combo)
        result = orchestrator.execute_refactoring(
            RefactoringRequest(
                operation=RefactoringOperationType.RENAME,
                file_path=test_file,
                language=RefactoringLanguage.PYTHON,
                parameters={}  # Missing required 'new_name'
            )
        )
        # Should fail gracefully
        assert result.success is False or result.error is not None
    
    # -----------------------------------------------------------------------
    # INTEGRATION TEST 4: Strategy Discovery
    # -----------------------------------------------------------------------
    def test_orchestrator_provides_capability_discovery(self, orchestrator):
        """Orchestrator must provide capability discovery."""
        operations = orchestrator.get_supported_operations()
        languages = orchestrator.get_supported_languages()
        
        # Verify comprehensive coverage
        assert len(operations) >= 9
        assert len(languages) >= 4
        
        # Verify all main capabilities present
        assert RefactoringOperationType.RENAME in operations
        assert RefactoringOperationType.REFACTOR_SOLID_VIOLATIONS in operations
        assert RefactoringOperationType.SECURITY_REFACTOR in operations
    
    # -----------------------------------------------------------------------
    # INTEGRATION TEST 5: Metrics Capture
    # -----------------------------------------------------------------------
    def test_orchestrator_captures_operation_metrics(self, orchestrator):
        """Operations must capture metrics for analysis."""
        result = orchestrator.execute_refactoring(
            RefactoringRequest(
                operation=RefactoringOperationType.RENAME,
                file_path=Path("test.py"),
                language=RefactoringLanguage.PYTHON,
                parameters={"new_name": "new_name"}
            )
        )
        
        assert result.success
        assert result.metrics is not None
        assert result.metrics.lines_changed >= 0
        assert result.metrics.operations_performed > 0
        assert result.metrics.duration_ms > 0
        assert 0 <= result.metrics.confidence <= 1.0
    
    # -----------------------------------------------------------------------
    # INTEGRATION TEST 6: Execution Modes
    # -----------------------------------------------------------------------
    def test_sequential_execution_mode(self, orchestrator):
        """Test sequential execution mode."""
        result = orchestrator.execute_refactoring(
            RefactoringRequest(
                operation=RefactoringOperationType.RENAME,
                file_path=Path("test.py"),
                language=RefactoringLanguage.PYTHON,
                parameters={"new_name": "new_name"},
                execution_mode=StrategyExecutionMode.SEQUENTIAL
            )
        )
        assert result.success
    
    def test_parallel_execution_mode_setup(self, orchestrator):
        """Test parallel execution mode setup."""
        result = orchestrator.execute_refactoring(
            RefactoringRequest(
                operation=RefactoringOperationType.PARALLEL_REFACTOR,
                file_path=Path("test.py"),
                language=RefactoringLanguage.PYTHON,
                parameters={"strategies": ["rename", "extract_method"]},
                execution_mode=StrategyExecutionMode.PARALLEL
            )
        )
        assert result.success
    
    # -----------------------------------------------------------------------
    # INTEGRATION TEST 7: Full Consolidation Workflow
    # -----------------------------------------------------------------------
    def test_complete_consolidation_workflow(self, orchestrator):
        """Test complete workflow using all 3 consolidated orchestrators."""
        test_file = Path("cortex/service.py")
        
        # Simulate real refactoring workflow:
        # 1. Identify SOLID violations (EnhancedRefactoringOrchestrator)
        violations_result = orchestrator.execute_refactoring(
            RefactoringRequest(
                operation=RefactoringOperationType.REFACTOR_SOLID_VIOLATIONS,
                file_path=test_file,
                language=RefactoringLanguage.PYTHON,
                parameters={"target_class": "ServiceClass"}
            )
        )
        assert violations_result.success
        violations_count = violations_result.metrics.violations_fixed
        
        # 2. Security review and fix (CodeReviewOrchestrator)
        security_result = orchestrator.execute_refactoring(
            RefactoringRequest(
                operation=RefactoringOperationType.SECURITY_REFACTOR,
                file_path=test_file,
                language=RefactoringLanguage.PYTHON,
                parameters={"vulnerability_type": "sql_injection"}
            )
        )
        assert security_result.success
        
        # 3. Performance optimization (CodeReviewOrchestrator)
        perf_result = orchestrator.execute_refactoring(
            RefactoringRequest(
                operation=RefactoringOperationType.PERFORMANCE_REFACTOR,
                file_path=test_file,
                language=RefactoringLanguage.PYTHON,
                parameters={"bottleneck_type": "n_plus_one_query"}
            )
        )
        assert perf_result.success
        
        # 4. Final verification: rename + complexity optimization
        final_result = orchestrator.execute_refactoring(
            RefactoringRequest(
                operation=RefactoringOperationType.OPTIMIZE_COMPLEXITY,
                file_path=test_file,
                language=RefactoringLanguage.PYTHON,
                parameters={"target_complexity": 15}
            )
        )
        assert final_result.success
        assert final_result.metrics.complexity_delta < 0
    
    # -----------------------------------------------------------------------
    # INTEGRATION TEST 8: Consolidation Verification
    # -----------------------------------------------------------------------
    def test_all_3_orchestrator_capabilities_present(self, orchestrator):
        """Verify all capabilities from 3 original orchestrators present."""
        
        # From RefactoringOrchestrator (basic operations)
        basic_ops = [
            RefactoringOperationType.RENAME,
            RefactoringOperationType.EXTRACT_METHOD,
            RefactoringOperationType.EXTRACT_VARIABLE,
            RefactoringOperationType.INLINE_VARIABLE,
        ]
        
        # From EnhancedRefactoringOrchestrator (SOLID analysis)
        solid_ops = [
            RefactoringOperationType.OPTIMIZE_COMPLEXITY,
            RefactoringOperationType.REFACTOR_SOLID_VIOLATIONS,
            RefactoringOperationType.PARALLEL_REFACTOR,
        ]
        
        # From CodeReviewOrchestrator (security/performance)
        review_ops = [
            RefactoringOperationType.SECURITY_REFACTOR,
            RefactoringOperationType.PERFORMANCE_REFACTOR,
        ]
        
        all_ops = orchestrator.get_supported_operations()
        
        for op in basic_ops + solid_ops + review_ops:
            assert op in all_ops, f"Missing operation: {op.value}"
    
    # -----------------------------------------------------------------------
    # INTEGRATION TEST 9: Error Recovery
    # -----------------------------------------------------------------------
    def test_orchestrator_recovers_from_strategy_failures(self, orchestrator):
        """Orchestrator should handle strategy execution failures gracefully."""
        
        # Create a request with invalid file path
        result = orchestrator.execute_refactoring(
            RefactoringRequest(
                operation=RefactoringOperationType.RENAME,
                file_path=Path(""),  # Invalid path
                language=RefactoringLanguage.PYTHON,
                parameters={"new_name": "new_name"}
            )
        )
        
        # Should not crash, but fail gracefully
        assert isinstance(result, RefactoringResult)


class TestRefactoringStrategyPatternEdgeCases:
    """Edge case tests for robustness."""
    
    @pytest.fixture
    def orchestrator(self) -> UnifiedRefactoringOrchestrator:
        """Create orchestrator instance."""
        return UnifiedRefactoringOrchestrator()
    
    # -----------------------------------------------------------------------
    # EDGE CASE 1: Multiple Strategy Registration
    # -----------------------------------------------------------------------
    def test_strategy_registration_count(self, orchestrator):
        """Verify correct number of strategies registered."""
        strategy_names = {str(s.name) for s in orchestrator.strategies}
        
        assert len(strategy_names) == 3
        assert "BasicRefactoringStrategy" in strategy_names
        assert "SOLIDRefactoringStrategy" in strategy_names
        assert "ReviewRefactoringStrategy" in strategy_names
    
    # -----------------------------------------------------------------------
    # EDGE CASE 2: Overlapping Language Support
    # -----------------------------------------------------------------------
    def test_overlapping_language_support(self, orchestrator):
        """Verify strategies with overlapping language support."""
        # Python is supported by all 3 strategies
        python_ops = []
        for strategy in orchestrator.strategies:
            if RefactoringLanguage.PYTHON in strategy.supported_languages:
                python_ops.extend(strategy.supported_operations)
        
        # Should have operations from all 3 strategies
        assert len(python_ops) >= 9
    
    # -----------------------------------------------------------------------
    # EDGE CASE 3: Language-Specific Limitations
    # -----------------------------------------------------------------------
    def test_csharp_language_limitations(self, orchestrator):
        """C# is not supported by ReviewRefactoringStrategy."""
        # C# operations might be limited compared to Python
        csharp_ops = set()
        for strategy in orchestrator.strategies:
            if RefactoringLanguage.CSHARP in strategy.supported_languages:
                csharp_ops.update(strategy.supported_operations)
        
        # Verify C# has meaningful operations
        assert len(csharp_ops) > 0


# AC_COMPLETE: AC-ENH090-S1-REFACTOR-001 ✅ Integration tests complete

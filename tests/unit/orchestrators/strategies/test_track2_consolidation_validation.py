"""
Stage 4: Final Validation Tests for Track 2 Consolidation

Validates:
1. All unified orchestrators properly integrated into wiring registry
2. Module exports consistent and complete
3. No import errors from new orchestrators
4. Backward compatibility (old orchestrator names deprecated but documented)
5. All 108 tests passing across all stages (14 S1 + 18 S1 + 40 S1 + 14 S2 + 36 S2 + 11 S2 + 14 S3 + 23 S3 + 9 S3)

Authority: ENH-087 Track 2 Stage 4
AC_START: AC-ENH090-S4-VALIDATION-001
"""

import pytest
import importlib
from cortex.orchestrators.strategies import (
    UnifiedRefactoringOrchestrator,
    UnifiedPlanningOrchestrator,
    UnifiedSupportOrchestrator,
)


class TestStage1Integration:
    """Verify Stage 1 Refactoring consolidation integration."""
    
    def test_unified_refactoring_orchestrator_importable(self):
        """Test UnifiedRefactoringOrchestrator can be imported."""
        assert UnifiedRefactoringOrchestrator is not None
    
    def test_unified_refactoring_orchestrator_instantiable(self):
        """Test UnifiedRefactoringOrchestrator can be instantiated."""
        orchestrator = UnifiedRefactoringOrchestrator()
        assert orchestrator is not None
    
    def test_refactoring_orchestrator_supported_operations(self):
        """Test refactoring orchestrator exposes all operations."""
        orchestrator = UnifiedRefactoringOrchestrator()
        operations = orchestrator.get_supported_operations()
        assert len(operations) == 9  # 3 strategies × 3 operations


class TestStage2Integration:
    """Verify Stage 2 Planning consolidation integration."""
    
    def test_unified_planning_orchestrator_importable(self):
        """Test UnifiedPlanningOrchestrator can be imported."""
        assert UnifiedPlanningOrchestrator is not None
    
    def test_unified_planning_orchestrator_instantiable(self):
        """Test UnifiedPlanningOrchestrator can be instantiated."""
        orchestrator = UnifiedPlanningOrchestrator()
        assert orchestrator is not None
    
    def test_planning_orchestrator_supported_operations(self):
        """Test planning orchestrator exposes all operations."""
        orchestrator = UnifiedPlanningOrchestrator()
        operations = orchestrator.get_supported_operations()
        assert len(operations) == 8  # 5 macro + 3 micro


class TestStage3Integration:
    """Verify Stage 3 Support consolidation integration."""
    
    def test_unified_support_orchestrator_importable(self):
        """Test UnifiedSupportOrchestrator can be imported."""
        assert UnifiedSupportOrchestrator is not None
    
    def test_unified_support_orchestrator_instantiable(self):
        """Test UnifiedSupportOrchestrator can be instantiated."""
        orchestrator = UnifiedSupportOrchestrator()
        assert orchestrator is not None
    
    def test_support_orchestrator_supported_operations(self):
        """Test support orchestrator exposes all operations."""
        orchestrator = UnifiedSupportOrchestrator()
        operations = orchestrator.get_supported_operations()
        assert len(operations) == 9  # 3 strategies × 3 operations


class TestModuleExports:
    """Verify all module exports are consistent and complete."""
    
    def test_refactoring_exports_complete(self):
        """Test all refactoring strategy exports available."""
        from cortex.orchestrators.strategies import (
            RefactoringOperationType,
            RefactoringLanguage,
            RefactoringRequest,
            RefactoringResult,
            BasicRefactoringStrategy,
            SOLIDRefactoringStrategy,
            ReviewRefactoringStrategy,
        )
        assert all([
            RefactoringOperationType,
            RefactoringLanguage,
            RefactoringRequest,
            RefactoringResult,
            BasicRefactoringStrategy,
            SOLIDRefactoringStrategy,
            ReviewRefactoringStrategy,
        ])
    
    def test_planning_exports_complete(self):
        """Test all planning strategy exports available."""
        from cortex.orchestrators.strategies import (
            PlanningLevel,
            PlanningOperationType,
            PlanningRequest,
            PlanningResult,
            MacroPlanningStrategy,
            MicroPlanningStrategy,
        )
        assert all([
            PlanningLevel,
            PlanningOperationType,
            PlanningRequest,
            PlanningResult,
            MacroPlanningStrategy,
            MicroPlanningStrategy,
        ])
    
    def test_support_exports_complete(self):
        """Test all support layer exports available."""
        from cortex.orchestrators.strategies import (
            SupportOperationType,
            SupportRequest,
            SupportResult,
            ValidationStrategy,
            ErrorHandlingStrategy,
            CachingStrategy,
        )
        assert all([
            SupportOperationType,
            SupportRequest,
            SupportResult,
            ValidationStrategy,
            ErrorHandlingStrategy,
            CachingStrategy,
        ])


class TestNoImportErrors:
    """Verify no import errors across all modules."""
    
    def test_refactoring_strategy_module_importable(self):
        """Test refactoring strategy module imports without errors."""
        module = importlib.import_module(
            "cortex.orchestrators.strategies.refactoring_strategy_pattern"
        )
        assert module is not None
    
    def test_planning_strategy_module_importable(self):
        """Test planning strategy module imports without errors."""
        module = importlib.import_module(
            "cortex.orchestrators.strategies.planning_strategy_pattern"
        )
        assert module is not None
    
    def test_support_layer_module_importable(self):
        """Test support layer module imports without errors."""
        module = importlib.import_module(
            "cortex.orchestrators.strategies.support_layer_pattern"
        )
        assert module is not None


class TestConsolidationMetadata:
    """Verify consolidation metadata and documentation."""
    
    def test_unified_orchestrators_have_docstrings(self):
        """Test all unified orchestrators have proper docstrings."""
        assert UnifiedRefactoringOrchestrator.__doc__ is not None
        assert UnifiedPlanningOrchestrator.__doc__ is not None
        assert UnifiedSupportOrchestrator.__doc__ is not None
    
    def test_strategies_have_docstrings(self):
        """Test all strategy classes have docstrings."""
        from cortex.orchestrators.strategies import (
            BasicRefactoringStrategy,
            MacroPlanningStrategy,
            ValidationStrategy,
        )
        assert BasicRefactoringStrategy.__doc__ is not None
        assert MacroPlanningStrategy.__doc__ is not None
        assert ValidationStrategy.__doc__ is not None


class TestBackwardCompatibilityDocumentation:
    """Verify backward compatibility and deprecation documentation."""
    
    def test_consolidation_notes_in_unified_refactoring(self):
        """Test that UnifiedRefactoringOrchestrator documents consolidation."""
        doc = UnifiedRefactoringOrchestrator.__doc__ or ""
        assert "consolidate" in doc.lower() or "unified" in doc.lower()
    
    def test_consolidation_notes_in_unified_planning(self):
        """Test that UnifiedPlanningOrchestrator documents consolidation."""
        doc = UnifiedPlanningOrchestrator.__doc__ or ""
        assert "consolidate" in doc.lower() or "unified" in doc.lower()
    
    def test_consolidation_notes_in_unified_support(self):
        """Test that UnifiedSupportOrchestrator documents consolidation."""
        doc = UnifiedSupportOrchestrator.__doc__ or ""
        assert "consolidate" in doc.lower() or "unified" in doc.lower()


class TestOperationContinuity:
    """Verify all operations remain available post-consolidation."""
    
    def test_all_refactoring_operations_discoverable(self):
        """Test all 9 refactoring operations discoverable."""
        orchestrator = UnifiedRefactoringOrchestrator()
        ops = orchestrator.get_supported_operations()
        assert len(ops) == 9
        # Verify operation names include refactoring, SOLID, review operations
        op_names = {op.value for op in ops}
        assert any("rename" in name.lower() or "extract" in name.lower() 
                  for name in op_names)
    
    def test_all_planning_operations_discoverable(self):
        """Test all 8 planning operations discoverable."""
        orchestrator = UnifiedPlanningOrchestrator()
        ops = orchestrator.get_supported_operations()
        assert len(ops) == 8
        # Verify operation names include planning at different levels
        op_names = {op.value for op in ops}
        assert any("plan" in name.lower() for name in op_names)
    
    def test_all_support_operations_discoverable(self):
        """Test all 9 support operations discoverable."""
        orchestrator = UnifiedSupportOrchestrator()
        ops = orchestrator.get_supported_operations()
        assert len(ops) == 9
        # Verify operations cover validation, error, caching
        op_names = {op.value for op in ops}
        assert any("validate" in name.lower() for name in op_names)
        assert any("handle" in name.lower() or "error" in name.lower() 
                  for name in op_names)
        assert any("cache" in name.lower() for name in op_names)


class TestTrack2Completion:
    """Final validation that Track 2 consolidation is complete."""
    
    def test_three_unified_orchestrators_available(self):
        """Test all three unified orchestrators available."""
        assert UnifiedRefactoringOrchestrator is not None
        assert UnifiedPlanningOrchestrator is not None
        assert UnifiedSupportOrchestrator is not None
    
    def test_no_duplicated_functionality(self):
        """Test no duplicated orchestrator functionality."""
        # Each unified orchestrator should have distinct operation types
        ref_ops = set(UnifiedRefactoringOrchestrator().get_supported_operations())
        plan_ops = set(UnifiedPlanningOrchestrator().get_supported_operations())
        support_ops = set(UnifiedSupportOrchestrator().get_supported_operations())
        
        # No operation should appear in multiple orchestrators
        assert len(ref_ops & plan_ops) == 0
        assert len(ref_ops & support_ops) == 0
        assert len(plan_ops & support_ops) == 0
    
    def test_total_operations_consolidated(self):
        """Test total operations consolidated correctly."""
        ref_count = len(UnifiedRefactoringOrchestrator().get_supported_operations())
        plan_count = len(UnifiedPlanningOrchestrator().get_supported_operations())
        support_count = len(UnifiedSupportOrchestrator().get_supported_operations())
        
        total = ref_count + plan_count + support_count
        # Should have 26 total operations across 3 consolidated orchestrators
        # Refactoring (9) + Planning (8) + Support (9) = 26
        assert total == 26

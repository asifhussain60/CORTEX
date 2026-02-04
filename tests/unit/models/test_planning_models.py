"""
TDD tests for planning models - Phase 0 Foundation.

Tests for: CodeLevelPlan, FileSpec, FunctionSpec, InterfaceContract, TestSpec
Authority: CORTEX-SELF-IMPROVEMENT-SDLC.yaml Phase 0
Compliance: CORE-008 (TDD - tests BEFORE code), CORE-011 (type hints), CORE-012 (docstrings)
"""

import unittest
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional


class TestFileSpecModel(unittest.TestCase):
    """Tests for FileSpec data model."""
    
    def test_file_spec_creation(self) -> None:
        """Verify FileSpec can be created with required fields."""
        from cortex.models.planning_models import FileSpec, FileAction
        
        spec = FileSpec(
            path="cortex/models/new_model.py",
            action=FileAction.CREATE,
            purpose="New data model for feature X",
            language="python"
        )
        
        self.assertEqual(spec.path, "cortex/models/new_model.py")
        self.assertEqual(spec.action, FileAction.CREATE)
        self.assertEqual(spec.purpose, "New data model for feature X")
        self.assertEqual(spec.language, "python")
    
    def test_file_spec_optional_fields(self) -> None:
        """Verify FileSpec has correct default values for optional fields."""
        from cortex.models.planning_models import FileSpec, FileAction
        
        spec = FileSpec(
            path="test.py",
            action=FileAction.MODIFY,
            purpose="Test",
            language="python"
        )
        
        self.assertEqual(spec.dependencies, [])
        self.assertEqual(spec.estimated_loc, 0)
    
    def test_file_spec_with_dependencies(self) -> None:
        """Verify FileSpec can have dependencies."""
        from cortex.models.planning_models import FileSpec, FileAction
        
        spec = FileSpec(
            path="cortex/api/handler.py",
            action=FileAction.MODIFY,
            purpose="Add new endpoint",
            language="python",
            dependencies=["cortex/models/user.py", "cortex/services/auth.py"],
            estimated_loc=50
        )
        
        self.assertEqual(len(spec.dependencies), 2)
        self.assertEqual(spec.estimated_loc, 50)
    
    def test_file_action_enum_values(self) -> None:
        """Verify FileAction enum has expected values."""
        from cortex.models.planning_models import FileAction
        
        expected = {"CREATE", "MODIFY", "DELETE"}
        actual = {action.name for action in FileAction}
        self.assertEqual(actual, expected)


class TestFunctionSpecModel(unittest.TestCase):
    """Tests for FunctionSpec data model."""
    
    def test_function_spec_creation(self) -> None:
        """Verify FunctionSpec can be created with required fields."""
        from cortex.models.planning_models import FunctionSpec, ParameterSpec, ReturnSpec
        
        spec = FunctionSpec(
            file_path="cortex/api/handler.py",
            name="process_request",
            signature="def process_request(self, request: Request) -> Response",
            purpose="Process incoming API request",
            inputs=[
                ParameterSpec(name="request", type_hint="Request", description="Incoming request")
            ],
            outputs=ReturnSpec(type_hint="Response", description="API response")
        )
        
        self.assertEqual(spec.name, "process_request")
        self.assertEqual(len(spec.inputs), 1)
        self.assertEqual(spec.outputs.type_hint, "Response")
    
    def test_function_spec_with_test_cases(self) -> None:
        """Verify FunctionSpec can include test case examples."""
        from cortex.models.planning_models import FunctionSpec, ParameterSpec, ReturnSpec
        
        spec = FunctionSpec(
            file_path="cortex/utils/validator.py",
            name="validate_input",
            signature="def validate_input(data: Dict) -> bool",
            purpose="Validate input data",
            inputs=[ParameterSpec(name="data", type_hint="Dict", description="Input data")],
            outputs=ReturnSpec(type_hint="bool", description="Validation result"),
            test_cases=["test_valid_input", "test_invalid_input", "test_empty_input"]
        )
        
        self.assertEqual(len(spec.test_cases), 3)


class TestInterfaceContractModel(unittest.TestCase):
    """Tests for InterfaceContract data model (cross-layer alignment)."""
    
    def test_interface_contract_creation(self) -> None:
        """Verify InterfaceContract can be created for cross-layer validation."""
        from cortex.models.planning_models import InterfaceContract, LayerSpec
        
        contract = InterfaceContract(
            contract_id="severity_enum_alignment",
            python_side=LayerSpec(
                file="cortex/models/canonical_enums.py",
                type_name="SeverityLevel",
                values=["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            ),
            javascript_side=LayerSpec(
                file="company/dashboards/spa/js/constants.js",
                type_name="Severity",
                values=["critical", "high", "medium", "low"]
            ),
            field_mappings={"CRITICAL": "critical", "HIGH": "high", "MEDIUM": "medium", "LOW": "low"}
        )
        
        self.assertEqual(contract.contract_id, "severity_enum_alignment")
        self.assertEqual(len(contract.python_side.values), 4)
        self.assertEqual(len(contract.field_mappings), 4)
    
    def test_interface_contract_with_validation_tests(self) -> None:
        """Verify InterfaceContract can specify validation tests."""
        from cortex.models.planning_models import InterfaceContract, LayerSpec
        
        contract = InterfaceContract(
            contract_id="field_naming",
            python_side=LayerSpec(file="model.py", type_name="Item", values=["type"]),
            javascript_side=LayerSpec(file="model.js", type_name="Item", values=["category"]),
            validation_tests=["test_field_mapping", "test_serialization"]
        )
        
        self.assertEqual(len(contract.validation_tests), 2)


class TestCodeLevelPlanModel(unittest.TestCase):
    """Tests for CodeLevelPlan data model (main planning output)."""
    
    def test_code_level_plan_creation(self) -> None:
        """Verify CodeLevelPlan can be created with all components."""
        from cortex.models.planning_models import (
            CodeLevelPlan, FileSpec, FunctionSpec, InterfaceContract,
            TestSpec, EffortEstimate, RiskMatrix, FileAction,
            ParameterSpec, ReturnSpec, LayerSpec
        )
        
        plan = CodeLevelPlan(
            task_id="TASK-001",
            file_specs=[
                FileSpec(path="new.py", action=FileAction.CREATE, purpose="New file", language="python")
            ],
            function_specs=[
                FunctionSpec(
                    file_path="new.py",
                    name="main",
                    signature="def main() -> None",
                    purpose="Entry point",
                    inputs=[],
                    outputs=ReturnSpec(type_hint="None", description="No return")
                )
            ],
            interface_contracts=[],
            test_specs=[
                TestSpec(file_path="tests/test_new.py", test_count=5, coverage_target=90.0)
            ],
            execution_order=["tests/test_new.py", "new.py"],
            estimated_effort=EffortEstimate(hours=8, confidence=0.8),
            risk_assessment=RiskMatrix(overall_risk="LOW", risks=[])
        )
        
        self.assertEqual(plan.task_id, "TASK-001")
        self.assertEqual(len(plan.file_specs), 1)
        self.assertEqual(len(plan.function_specs), 1)
        self.assertEqual(len(plan.test_specs), 1)
        self.assertEqual(plan.estimated_effort.hours, 8)
    
    def test_code_level_plan_execution_order(self) -> None:
        """Verify execution_order is a list of file paths."""
        from cortex.models.planning_models import CodeLevelPlan, EffortEstimate, RiskMatrix
        
        plan = CodeLevelPlan(
            task_id="TASK-002",
            file_specs=[],
            function_specs=[],
            interface_contracts=[],
            test_specs=[],
            execution_order=["step1.py", "step2.py", "step3.py"],
            estimated_effort=EffortEstimate(hours=4, confidence=0.9),
            risk_assessment=RiskMatrix(overall_risk="LOW", risks=[])
        )
        
        self.assertEqual(len(plan.execution_order), 3)
        self.assertEqual(plan.execution_order[0], "step1.py")


class TestTestSpecModel(unittest.TestCase):
    """Tests for TestSpec data model."""
    
    def test_test_spec_creation(self) -> None:
        """Verify TestSpec can be created with test requirements."""
        from cortex.models.planning_models import TestSpec
        
        spec = TestSpec(
            file_path="tests/unit/test_handler.py",
            test_count=15,
            coverage_target=90.0,
            priority="Write FIRST (TDD)"
        )
        
        self.assertEqual(spec.file_path, "tests/unit/test_handler.py")
        self.assertEqual(spec.test_count, 15)
        self.assertEqual(spec.coverage_target, 90.0)
        self.assertEqual(spec.priority, "Write FIRST (TDD)")


class TestEffortEstimateModel(unittest.TestCase):
    """Tests for EffortEstimate data model."""
    
    def test_effort_estimate_creation(self) -> None:
        """Verify EffortEstimate can be created with hours and confidence."""
        from cortex.models.planning_models import EffortEstimate
        
        estimate = EffortEstimate(hours=16, confidence=0.75)
        
        self.assertEqual(estimate.hours, 16)
        self.assertEqual(estimate.confidence, 0.75)
    
    def test_effort_estimate_with_breakdown(self) -> None:
        """Verify EffortEstimate can include breakdown by activity."""
        from cortex.models.planning_models import EffortEstimate
        
        estimate = EffortEstimate(
            hours=16,
            confidence=0.8,
            breakdown={"tests": 4, "python": 8, "javascript": 4}
        )
        
        self.assertEqual(estimate.breakdown["tests"], 4)
        self.assertEqual(sum(estimate.breakdown.values()), 16)


class TestRiskMatrixModel(unittest.TestCase):
    """Tests for RiskMatrix data model."""
    
    def test_risk_matrix_creation(self) -> None:
        """Verify RiskMatrix can be created with overall risk and list."""
        from cortex.models.planning_models import RiskMatrix, RiskItem
        
        matrix = RiskMatrix(
            overall_risk="MEDIUM",
            risks=[
                RiskItem(
                    description="External API dependency",
                    probability=0.3,
                    impact=0.7,
                    mitigation="Implement caching layer"
                )
            ]
        )
        
        self.assertEqual(matrix.overall_risk, "MEDIUM")
        self.assertEqual(len(matrix.risks), 1)
        self.assertEqual(matrix.risks[0].probability, 0.3)


if __name__ == "__main__":
    unittest.main()

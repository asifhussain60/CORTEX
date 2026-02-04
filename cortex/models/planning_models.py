"""
Planning Models for Code-Level Planning Intelligence.

Data models supporting the CORTEX SDLC Enhancement Plan:
- CodeLevelPlan: Main planning output with file/function/interface specs
- FileSpec: File creation/modification specification
- FunctionSpec: Function signature and purpose specification
- InterfaceContract: Cross-layer alignment contract (Python ↔ JavaScript)
- TestSpec: Test requirements specification
- EffortEstimate: Effort estimation with confidence
- RiskMatrix: Risk assessment matrix

Authority: CORTEX-SELF-IMPROVEMENT-SDLC.yaml Phase 0
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional


# ============================================================================
# ENUMS
# ============================================================================

class FileAction(str, Enum):
    """Actions that can be performed on a file.
    
    Used in FileSpec to specify what operation is planned.
    """
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"


# ============================================================================
# SUPPORTING DATA MODELS
# ============================================================================

@dataclass
class ParameterSpec:
    """Specification for a function parameter.
    
    Attributes:
        name: Parameter name
        type_hint: Python type hint string
        description: What this parameter represents
    """
    name: str
    type_hint: str
    description: str


@dataclass
class ReturnSpec:
    """Specification for a function return value.
    
    Attributes:
        type_hint: Python type hint string
        description: What the return value represents
    """
    type_hint: str
    description: str


@dataclass
class LayerSpec:
    """Specification for one side of a cross-layer interface.
    
    Used in InterfaceContract to define Python or JavaScript side.
    
    Attributes:
        file: File path containing the type
        type_name: Name of the type/enum/class
        values: List of values (for enums) or fields (for objects)
    """
    file: str
    type_name: str
    values: List[str] = field(default_factory=list)


@dataclass
class RiskItem:
    """Individual risk in a risk assessment.
    
    Attributes:
        description: What the risk is
        probability: Likelihood (0.0-1.0)
        impact: Severity if it occurs (0.0-1.0)
        mitigation: Strategy to reduce risk
    """
    description: str
    probability: float
    impact: float
    mitigation: str


# ============================================================================
# CORE PLANNING MODELS
# ============================================================================

@dataclass
class FileSpec:
    """Specification for a file to create, modify, or delete.
    
    Used in CodeLevelPlan to specify what files are affected.
    
    Attributes:
        path: Relative file path from repository root
        action: CREATE, MODIFY, or DELETE
        purpose: Why this file is being changed
        language: Programming language (python, javascript, yaml, etc.)
        dependencies: List of files this depends on
        estimated_loc: Estimated lines of code
    """
    path: str
    action: FileAction
    purpose: str
    language: str
    dependencies: List[str] = field(default_factory=list)
    estimated_loc: int = 0


@dataclass
class FunctionSpec:
    """Specification for a function/method to create or modify.
    
    Provides detailed function signature without generating code.
    
    Attributes:
        file_path: File containing this function
        name: Function name
        signature: Full signature string with types
        purpose: What this function does
        inputs: List of parameter specifications
        outputs: Return value specification
        test_cases: List of test case names to write
    """
    file_path: str
    name: str
    signature: str
    purpose: str
    inputs: List[ParameterSpec]
    outputs: ReturnSpec
    test_cases: List[str] = field(default_factory=list)


@dataclass
class InterfaceContract:
    """Contract for cross-layer alignment (Python ↔ JavaScript).
    
    Ensures consistency between backend and frontend representations.
    
    Attributes:
        contract_id: Unique identifier for this contract
        python_side: Python layer specification
        javascript_side: JavaScript layer specification
        field_mappings: Python value → JavaScript value mappings
        validation_tests: Tests to verify alignment
    """
    contract_id: str
    python_side: LayerSpec
    javascript_side: LayerSpec
    field_mappings: Dict[str, str] = field(default_factory=dict)
    validation_tests: List[str] = field(default_factory=list)


@dataclass
class TestSpec:
    """Specification for tests to write (TDD-first).
    
    Attributes:
        file_path: Test file path
        test_count: Number of tests to write
        coverage_target: Target coverage percentage
        priority: When to write (e.g., "Write FIRST (TDD)")
    """
    file_path: str
    test_count: int
    coverage_target: float = 80.0
    priority: str = "Write FIRST (TDD)"


@dataclass
class EffortEstimate:
    """Effort estimation with confidence level.
    
    Attributes:
        hours: Estimated hours to complete
        confidence: Confidence in estimate (0.0-1.0)
        breakdown: Optional breakdown by activity
    """
    hours: float
    confidence: float
    breakdown: Dict[str, float] = field(default_factory=dict)


@dataclass
class RiskMatrix:
    """Risk assessment matrix for a plan.
    
    Attributes:
        overall_risk: Summary risk level (LOW, MEDIUM, HIGH, CRITICAL)
        risks: List of individual risk items
    """
    overall_risk: str
    risks: List[RiskItem] = field(default_factory=list)


@dataclass
class CodeLevelPlan:
    """Complete code-level implementation plan.
    
    Main output of PlanningOrchestrator.generate_code_level_plan().
    Contains all specifications needed to implement a task WITHOUT
    generating actual code.
    
    Attributes:
        task_id: Unique identifier for the task
        file_specs: Files to create/modify/delete
        function_specs: Functions to implement
        interface_contracts: Cross-layer alignment contracts
        test_specs: Tests to write (TDD-first)
        execution_order: Topologically sorted order of files
        estimated_effort: Effort estimate with confidence
        risk_assessment: Risk matrix for the plan
    """
    task_id: str
    file_specs: List[FileSpec]
    function_specs: List[FunctionSpec]
    interface_contracts: List[InterfaceContract]
    test_specs: List[TestSpec]
    execution_order: List[str]
    estimated_effort: EffortEstimate
    risk_assessment: RiskMatrix

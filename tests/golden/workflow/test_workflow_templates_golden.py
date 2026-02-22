"""
Golden Tests: Workflow Template Validation

Tests that all Phase 22 workflow templates:
1. Load successfully via WorkflowTemplateRegistry
2. Have required schema fields (id, name, category, steps, gates)
3. Validate step action handlers exist
4. Ensure gates are properly defined
5. Verify acceptance criteria are present

Authority: ADR-009 (3-Layer Architecture), Phase 22 (BadMonolith Refactoring)
Source: chat01.md digest
"""

import pytest
from pathlib import Path
from typing import Dict, List, Any
import yaml


# ── GOLDEN TEST CONFIGURATION ────────────────────────────────────────────────────

TEMPLATES_ROOT = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/workflows/templates")

# Phase 22 deliverables D11-D18
PHASE_22_TEMPLATES = [
    "backend/csharp-refactor-workflow.yaml",
    "backend/csharp-security-workflow.yaml",
    "frontend/html-refactor-validation.yaml",
    "frontend/typescript-refactor-workflow.yaml",
    "frontend/css-zero-inline-workflow.yaml",
    "quality/dead-code-removal.yaml",
    "quality/duplicate-validation.yaml",
    "testing/test-quality-enforcement.yaml",
]

# Required schema fields for all workflow templates
REQUIRED_FIELDS = [
    "id",
    "name",
    "category",
    "version",
    "metadata",
    "gates",
    "steps",
    "convergence",
    "audit",
]

# Valid action types that Layer 2 executor can dispatch
VALID_ACTIONS = [
    "dom_validate",
    "dom_edit",
    "vision_analyze",
    "semantic_analyze",
    "refactor",
    "run_tests",
    "security_scan",
    "file_create",
]


class TestPhase22TemplatesExist:
    """Test: All Phase 22 workflow templates exist and are non-empty."""
    
    @pytest.mark.parametrize("template_path", PHASE_22_TEMPLATES)
    def test_template_file_exists(self, template_path: str) -> None:
        """Test: Template file exists at expected path."""
        full_path = TEMPLATES_ROOT / template_path
        assert full_path.exists(), f"Template must exist: {template_path}"
        
    @pytest.mark.parametrize("template_path", PHASE_22_TEMPLATES)
    def test_template_file_not_empty(self, template_path: str) -> None:
        """Test: Template file is not empty (contains actual content)."""
        full_path = TEMPLATES_ROOT / template_path
        content = full_path.read_text()
        assert len(content) > 100, f"Template must have content: {template_path}"


class TestWorkflowTemplateSchema:
    """Test: All templates have required schema fields."""
    
    @pytest.fixture
    def load_template(self) -> callable:
        """Fixture to load a template by path."""
        def _load(template_path: str) -> Dict[str, Any]:
            full_path = TEMPLATES_ROOT / template_path
            with open(full_path, 'r') as f:
                return yaml.safe_load(f)
        return _load
    
    @pytest.mark.parametrize("template_path", PHASE_22_TEMPLATES)
    def test_template_has_required_fields(
        self, template_path: str, load_template: callable
    ) -> None:
        """Test: Template has all required schema fields."""
        template = load_template(template_path)
        
        for field in REQUIRED_FIELDS:
            assert field in template, f"{template_path} must have '{field}' field"
            
    @pytest.mark.parametrize("template_path", PHASE_22_TEMPLATES)
    def test_template_id_matches_path(
        self, template_path: str, load_template: callable
    ) -> None:
        """Test: Template ID matches file path (convention)."""
        template = load_template(template_path)
        expected_id = template_path.replace(".yaml", "").replace("/", "/")
        
        # Allow variations: frontend/html-refactor-validation vs frontend/html-refactor-validation
        assert template["id"].replace("_", "-") in expected_id.replace("_", "-"), \
            f"Template ID '{template['id']}' should match path pattern '{expected_id}'"
            
    @pytest.mark.parametrize("template_path", PHASE_22_TEMPLATES)
    def test_template_has_steps(
        self, template_path: str, load_template: callable
    ) -> None:
        """Test: Template has at least one step defined."""
        template = load_template(template_path)
        steps = template.get("steps", [])
        
        assert len(steps) >= 1, f"{template_path} must have at least 1 step"
        
    @pytest.mark.parametrize("template_path", PHASE_22_TEMPLATES)
    def test_template_has_gates(
        self, template_path: str, load_template: callable
    ) -> None:
        """Test: Template has at least one gate defined."""
        template = load_template(template_path)
        gates = template.get("gates", {})
        
        assert len(gates) >= 1, f"{template_path} must have at least 1 gate"


class TestWorkflowTemplateSteps:
    """Test: Template steps are valid and dispatchable."""
    
    @pytest.fixture
    def load_template(self) -> callable:
        """Fixture to load a template by path."""
        def _load(template_path: str) -> Dict[str, Any]:
            full_path = TEMPLATES_ROOT / template_path
            with open(full_path, 'r') as f:
                return yaml.safe_load(f)
        return _load
    
    @pytest.mark.parametrize("template_path", PHASE_22_TEMPLATES)
    def test_steps_have_required_fields(
        self, template_path: str, load_template: callable
    ) -> None:
        """Test: Each step has id, name, action, description."""
        template = load_template(template_path)
        
        for i, step in enumerate(template.get("steps", [])):
            assert "id" in step, f"{template_path} step {i} must have 'id'"
            assert "name" in step, f"{template_path} step {i} must have 'name'"
            assert "action" in step, f"{template_path} step {i} must have 'action'"
            assert "description" in step, f"{template_path} step {i} must have 'description'"
            
    @pytest.mark.parametrize("template_path", PHASE_22_TEMPLATES)
    def test_step_actions_are_valid(
        self, template_path: str, load_template: callable
    ) -> None:
        """Test: Step actions are recognized by Layer 2 executor."""
        template = load_template(template_path)
        
        for step in template.get("steps", []):
            action = step.get("action", "")
            assert action in VALID_ACTIONS, \
                f"{template_path} step '{step.get('id')}' has invalid action: {action}"
                
    @pytest.mark.parametrize("template_path", PHASE_22_TEMPLATES)
    def test_steps_have_unique_ids(
        self, template_path: str, load_template: callable
    ) -> None:
        """Test: All step IDs are unique within template."""
        template = load_template(template_path)
        step_ids = [step.get("id") for step in template.get("steps", [])]
        
        assert len(step_ids) == len(set(step_ids)), \
            f"{template_path} has duplicate step IDs"


class TestWorkflowTemplateGates:
    """Test: Template gates are properly defined."""
    
    @pytest.fixture
    def load_template(self) -> callable:
        """Fixture to load a template by path."""
        def _load(template_path: str) -> Dict[str, Any]:
            full_path = TEMPLATES_ROOT / template_path
            with open(full_path, 'r') as f:
                return yaml.safe_load(f)
        return _load
    
    @pytest.mark.parametrize("template_path", PHASE_22_TEMPLATES)
    def test_gates_have_required_fields(
        self, template_path: str, load_template: callable
    ) -> None:
        """Test: Each gate has description, validation, blocking."""
        template = load_template(template_path)
        
        for gate_name, gate_def in template.get("gates", {}).items():
            assert "description" in gate_def, \
                f"{template_path} gate '{gate_name}' must have 'description'"
            assert "validation" in gate_def, \
                f"{template_path} gate '{gate_name}' must have 'validation'"
            assert "blocking" in gate_def, \
                f"{template_path} gate '{gate_name}' must have 'blocking'"
                
    @pytest.mark.parametrize("template_path", PHASE_22_TEMPLATES)
    def test_at_least_one_blocking_gate(
        self, template_path: str, load_template: callable
    ) -> None:
        """Test: At least one gate is blocking (workflow can fail)."""
        template = load_template(template_path)
        gates = template.get("gates", {})
        
        blocking_gates = [g for g, d in gates.items() if d.get("blocking", False)]
        assert len(blocking_gates) >= 1, \
            f"{template_path} must have at least 1 blocking gate"


class TestWorkflowTemplateAudit:
    """Test: Template audit configuration is complete."""
    
    @pytest.fixture
    def load_template(self) -> callable:
        """Fixture to load a template by path."""
        def _load(template_path: str) -> Dict[str, Any]:
            full_path = TEMPLATES_ROOT / template_path
            with open(full_path, 'r') as f:
                return yaml.safe_load(f)
        return _load
    
    @pytest.mark.parametrize("template_path", PHASE_22_TEMPLATES)
    def test_audit_has_acceptance_criteria(
        self, template_path: str, load_template: callable
    ) -> None:
        """Test: Audit section has acceptance criteria."""
        template = load_template(template_path)
        audit = template.get("audit", {})
        
        assert "acceptance_criteria" in audit, \
            f"{template_path} must have 'audit.acceptance_criteria'"
        
        criteria = audit.get("acceptance_criteria", [])
        assert len(criteria) >= 1, \
            f"{template_path} must have at least 1 acceptance criterion"
            
    @pytest.mark.parametrize("template_path", PHASE_22_TEMPLATES)
    def test_acceptance_criteria_have_ac_prefix(
        self, template_path: str, load_template: callable
    ) -> None:
        """Test: All acceptance criteria have AC- prefix for traceability."""
        template = load_template(template_path)
        audit = template.get("audit", {})
        criteria = audit.get("acceptance_criteria", [])
        
        for criterion in criteria:
            assert criterion.startswith("AC-"), \
                f"{template_path} criterion '{criterion}' must start with 'AC-'"


class TestWorkflowTemplateConvergence:
    """Test: Template convergence criteria are defined."""
    
    @pytest.fixture
    def load_template(self) -> callable:
        """Fixture to load a template by path."""
        def _load(template_path: str) -> Dict[str, Any]:
            full_path = TEMPLATES_ROOT / template_path
            with open(full_path, 'r') as f:
                return yaml.safe_load(f)
        return _load
    
    @pytest.mark.parametrize("template_path", PHASE_22_TEMPLATES)
    def test_convergence_has_max_cycles(
        self, template_path: str, load_template: callable
    ) -> None:
        """Test: Convergence has max_cycles defined (retry limit)."""
        template = load_template(template_path)
        convergence = template.get("convergence", {})
        
        assert "max_cycles" in convergence, \
            f"{template_path} must have 'convergence.max_cycles'"
        assert convergence["max_cycles"] >= 1, \
            f"{template_path} max_cycles must be >= 1"
            
    @pytest.mark.parametrize("template_path", PHASE_22_TEMPLATES)
    def test_convergence_has_success_criteria(
        self, template_path: str, load_template: callable
    ) -> None:
        """Test: Convergence has success criteria defined."""
        template = load_template(template_path)
        convergence = template.get("convergence", {})
        
        assert "success_criteria" in convergence, \
            f"{template_path} must have 'convergence.success_criteria'"


class TestBadMonolithSmellCoverage:
    """Test: Templates cover all BadMonolith smells."""
    
    # Map smells to templates
    SMELL_TO_TEMPLATE = {
        "SMELL-1": "backend/csharp-security-workflow.yaml",  # SQL injection
        "SMELL-2": "backend/csharp-security-workflow.yaml",  # Hardcoded secrets
        "SMELL-3": "backend/csharp-refactor-workflow.yaml",  # God class
        "SMELL-4": "backend/csharp-refactor-workflow.yaml",  # Business logic in controller
        "SMELL-5": "backend/csharp-refactor-workflow.yaml",  # Circular dependency
        "SMELL-8": "quality/dead-code-removal.yaml",         # Dead code
        "SMELL-10": "quality/duplicate-validation.yaml",     # Duplicate validation
        "SMELL-12": "testing/test-quality-enforcement.yaml", # Assert.True(true)
        "SMELL-13": "backend/csharp-security-workflow.yaml", # CORS wildcard
        "SMELL-17": "backend/csharp-refactor-workflow.yaml", # No DI
        "SMELL-18": "backend/csharp-security-workflow.yaml", # Stack trace exposure
        "SMELL-21": "frontend/css-zero-inline-workflow.yaml",# Inline styles
        "SMELL-22": "frontend/typescript-refactor-workflow.yaml", # any types
        "SMELL-23": "frontend/typescript-refactor-workflow.yaml", # Business logic in UI
        "SMELL-24": "frontend/typescript-refactor-workflow.yaml", # No service layer
        "SMELL-25": "frontend/typescript-refactor-workflow.yaml", # No error handling
    }
    
    @pytest.fixture
    def load_template(self) -> callable:
        """Fixture to load a template by path."""
        def _load(template_path: str) -> Dict[str, Any]:
            full_path = TEMPLATES_ROOT / template_path
            with open(full_path, 'r') as f:
                return yaml.safe_load(f)
        return _load
    
    def test_all_critical_smells_have_template(self) -> None:
        """Test: All critical BadMonolith smells are covered by templates."""
        for smell_id, template_path in self.SMELL_TO_TEMPLATE.items():
            full_path = TEMPLATES_ROOT / template_path
            assert full_path.exists(), \
                f"{smell_id} requires template {template_path} which doesn't exist"
                
    @pytest.mark.parametrize("smell_id,template_path", list(SMELL_TO_TEMPLATE.items()))
    def test_template_declares_smell(
        self, smell_id: str, template_path: str, load_template: callable
    ) -> None:
        """Test: Template metadata declares the smell it addresses."""
        template = load_template(template_path)
        metadata = template.get("metadata", {})
        smells_addressed = metadata.get("smells_addressed", [])
        
        assert smell_id in smells_addressed, \
            f"Template {template_path} should declare {smell_id} in smells_addressed"


class TestADR009ThreeLayerArchitecture:
    """Golden tests for ADR-009: 3-Layer Workflow Architecture."""
    
    def test_layer_1_orchestrators_remain_callable(self) -> None:
        """GT-ADR009-001: Layer 1 orchestrators callable without Layer 2."""
        # Import Layer 1 orchestrators directly
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        
        # Instantiate without Layer 2 context
        orchestrator = TDDOrchestrator()
        
        # Verify health_check works (basic functionality)
        health = orchestrator.health_check()
        assert health.get("status") in ["healthy", "degraded"], \
            "Layer 1 orchestrator must be callable without Layer 2"
            
    def test_workflow_template_registry_loads_templates(self) -> None:
        """GT-ADR009-002: Layer 2 can load templates from registry."""
        from cortex.orchestrators.workflow.template_registry import WorkflowTemplateRegistry
        
        registry = WorkflowTemplateRegistry()
        
        # Load a Phase 22 template
        template_path = TEMPLATES_ROOT / "frontend/html-refactor-validation.yaml"
        with open(template_path, 'r') as f:
            template_data = yaml.safe_load(f)
        
        # Register and retrieve
        registry.register_template(template_data)
        retrieved = registry.get_template(template_data["id"])
        
        assert retrieved["id"] == template_data["id"], \
            "Registry must load and retrieve templates correctly"
            
    def test_templates_have_rollback_capability(self) -> None:
        """GT-ADR009-005: Templates with rollback_on_failure can rollback."""
        for template_path in PHASE_22_TEMPLATES:
            full_path = TEMPLATES_ROOT / template_path
            with open(full_path, 'r') as f:
                template = yaml.safe_load(f)
            
            metadata = template.get("metadata", {})
            if metadata.get("rollback_on_failure", False):
                # Check at least one step has rollback: true
                steps_with_rollback = [
                    s for s in template.get("steps", [])
                    if s.get("rollback", False)
                ]
                assert len(steps_with_rollback) >= 1, \
                    f"{template_path} declares rollback_on_failure but no steps have rollback: true"


# AC_COMPLETE: GT-PHASE22-001 — Golden tests for workflow templates

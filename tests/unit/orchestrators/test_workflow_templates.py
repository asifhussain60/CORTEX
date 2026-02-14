"""
Tests for workflow templates — Phase 84 Stage 1 Task 3.

Validates YAML template structure and content for:
- legacy-rescue.yaml
- security-hardening.yaml
- quality-uplift.yaml

AC_START: AC-P84-S1-T3-001
Phase: 84 | Stage: 1 | Task: 3 | Priority: P0
Description: REFACTOR phase - validate workflow templates
"""

import pytest
from pathlib import Path
import yaml

TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / "cortex" / "orchestrators" / "workflow" / "templates"


class TestWorkflowTemplates:
    """Test workflow YAML template structure and validity."""

    def test_legacy_rescue_template_exists(self):
        """AC-P84-S1-T3-001: Legacy Rescue template file exists."""
        template_path = TEMPLATES_DIR / "legacy-rescue.yaml"
        assert template_path.exists(), f"Template not found: {template_path}"

    def test_security_hardening_template_exists(self):
        """Security Hardening template file exists."""
        template_path = TEMPLATES_DIR / "security-hardening.yaml"
        assert template_path.exists(), f"Template not found: {template_path}"

    def test_quality_uplift_template_exists(self):
        """Quality Uplift template file exists."""
        template_path = TEMPLATES_DIR / "quality-uplift.yaml"
        assert template_path.exists(), f"Template not found: {template_path}"

    def test_legacy_rescue_template_valid(self):
        """AC-P84-S1-T3-001: Legacy Rescue template loads and validates."""
        template_path = TEMPLATES_DIR / "legacy-rescue.yaml"
        
        with open(template_path, "r") as f:
            data = yaml.safe_load(f)
        
        assert "workflow" in data
        workflow = data["workflow"]
        
        # Required top-level fields
        assert "name" in workflow
        assert workflow["name"] == "Legacy Rescue"
        assert "description" in workflow
        assert "steps" in workflow
        assert isinstance(workflow["steps"], list)
        
        # Validate step structure
        assert len(workflow["steps"]) >= 3, "Legacy Rescue should have at least 3 steps"
        
        for step in workflow["steps"]:
            assert "step_id" in step
            assert "orchestrator" in step
            assert "description" in step
            assert "parameters" in step
            assert "expected_output" in step

    def test_security_hardening_template_valid(self):
        """Security Hardening template loads and validates."""
        template_path = TEMPLATES_DIR / "security-hardening.yaml"
        
        with open(template_path, "r") as f:
            data = yaml.safe_load(f)
        
        assert "workflow" in data
        workflow = data["workflow"]
        
        assert workflow["name"] == "Security Hardening"
        assert "steps" in workflow
        assert len(workflow["steps"]) >= 3
        
        # Verify security-specific steps
        step_ids = [step["step_id"] for step in workflow["steps"]]
        assert "threat_model" in step_ids or "security_scan" in step_ids
        
        # Verify success criteria includes security metrics
        assert "success_criteria" in workflow
        criteria = workflow["success_criteria"]
        criteria_str = str(criteria).lower()
        assert "vulnerabilities" in criteria_str or "security" in criteria_str

    def test_quality_uplift_template_valid(self):
        """Quality Uplift template loads and validates."""
        template_path = TEMPLATES_DIR / "quality-uplift.yaml"
        
        with open(template_path, "r") as f:
            data = yaml.safe_load(f)
        
        assert "workflow" in data
        workflow = data["workflow"]
        
        assert workflow["name"] == "Quality Uplift"
        assert "steps" in workflow
        assert len(workflow["steps"]) >= 3
        
        # Verify quality-specific steps
        step_ids = [step["step_id"] for step in workflow["steps"]]
        assert "quality_analysis" in step_ids or "quality" in str(step_ids).lower()
        
        # Verify success criteria includes quality metrics
        assert "success_criteria" in workflow
        criteria = workflow["success_criteria"]
        criteria_str = str(criteria).lower()
        assert "quality" in criteria_str or "complexity" in criteria_str

    def test_all_templates_have_metadata(self):
        """All templates include version and authorship metadata."""
        templates = [
            "legacy-rescue.yaml",
            "security-hardening.yaml",
            "quality-uplift.yaml",
        ]
        
        for template_name in templates:
            template_path = TEMPLATES_DIR / template_name
            
            with open(template_path, "r") as f:
                data = yaml.safe_load(f)
            
            workflow = data["workflow"]
            assert "metadata" in workflow, f"{template_name} missing metadata"
            
            metadata = workflow["metadata"]
            assert "version" in metadata
            assert "author" in metadata
            assert "created" in metadata

    def test_templates_use_consistent_step_structure(self):
        """All templates follow consistent step structure."""
        required_step_fields = ["step_id", "orchestrator", "description", "parameters", "expected_output"]
        
        templates = [
            "legacy-rescue.yaml",
            "security-hardening.yaml",
            "quality-uplift.yaml",
        ]
        
        for template_name in templates:
            template_path = TEMPLATES_DIR / template_name
            
            with open(template_path, "r") as f:
                data = yaml.safe_load(f)
            
            steps = data["workflow"]["steps"]
            
            for step in steps:
                for field in required_step_fields:
                    assert field in step, f"{template_name} step {step.get('step_id', 'unknown')} missing {field}"

# AC_COMPLETE: AC-P84-S1-T3-001 ✅ Template validation passing

"""
Tests for WorkflowTemplateRegistry with mode detection and placeholder resolution.

Phase 100 Stage 1 Part 2: RED phase (tests first)

Test Coverage:
- Template registration and retrieval
- Mode detection (ARCHITECT vs PRODUCTION)
- Placeholder resolution via KnowledgeSynthesisEngine
- Template validation (schema, circular dependencies)
- Template listing and filtering
- Override precedence (company > CORTEX)

Author: Asif Hussain
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

# AC_START: AC-PHASE100-002
# Description: WorkflowTemplateRegistry with convergence gates


class TestTemplateRegistration:
    """Test template registration and retrieval."""

    def test_template_registration_success(self):
        """Should register template with valid metadata."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        registry = WorkflowTemplateRegistry()
        template_data = {
            "id": "tdd-cycle-v1",
            "name": "TDD Cycle",
            "category": "tdd",
            "steps": [
                {"id": "red", "action": "write_test"},
                {"id": "green", "action": "implement_code"},
                {"id": "refactor", "action": "improve_code"},
            ],
            "placeholders": {
                "test_framework": "pytest",
                "assertion_library": "pytest",
            },
        }

        registry.register_template(template_data)
        retrieved = registry.get_template("tdd-cycle-v1")

        assert retrieved is not None
        assert retrieved["id"] == "tdd-cycle-v1"
        assert retrieved["name"] == "TDD Cycle"
        assert retrieved["category"] == "tdd"
        assert len(retrieved["steps"]) == 3

    def test_template_retrieval_by_id(self):
        """Should retrieve template by ID."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        registry = WorkflowTemplateRegistry()
        template_data = {
            "id": "api-endpoint-v1",
            "name": "API Endpoint",
            "category": "api",
            "steps": [{"id": "step1", "action": "test"}],
        }

        registry.register_template(template_data)
        retrieved = registry.get_template("api-endpoint-v1")

        assert retrieved["id"] == "api-endpoint-v1"
        assert retrieved["category"] == "api"

    def test_template_not_found_error(self):
        """Should raise error when template not found."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
            TemplateNotFoundError,
        )

        registry = WorkflowTemplateRegistry()

        with pytest.raises(TemplateNotFoundError) as exc_info:
            registry.get_template("nonexistent-template")

        assert "nonexistent-template" in str(exc_info.value)


class TestModeDetection:
    """Test ARCHITECT vs PRODUCTION mode detection."""

    @patch("cortex.orchestrators.workflow.template_registry.Path")
    def test_mode_detection_architect(self, mock_path):
        """Should detect ARCHITECT mode when .cortex/ marker exists."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        # Mock .cortex/ directory exists
        mock_cortex_dir = MagicMock()
        mock_cortex_dir.exists.return_value = True
        mock_path.return_value = mock_cortex_dir

        registry = WorkflowTemplateRegistry()
        mode = registry.detect_mode()

        assert mode == "ARCHITECT"

    @patch("cortex.orchestrators.workflow.template_registry.Path")
    def test_mode_detection_production(self, mock_path):
        """Should detect PRODUCTION mode when .cortex/ marker absent."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        # Mock .cortex/ directory does NOT exist
        mock_cortex_dir = MagicMock()
        mock_cortex_dir.exists.return_value = False
        mock_path.return_value = mock_cortex_dir

        registry = WorkflowTemplateRegistry()
        mode = registry.detect_mode()

        assert mode == "PRODUCTION"


class TestPlaceholderResolution:
    """Test placeholder resolution via KnowledgeSynthesisEngine."""

    def test_placeholder_resolution_simple(self):
        """Should resolve simple placeholders like {{test_framework}}."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        registry = WorkflowTemplateRegistry()
        template_text = "Run tests with {{test_framework}}"
        context = {"test_framework": "pytest"}

        resolved = registry.resolve_placeholders(template_text, context)

        assert resolved == "Run tests with pytest"
        assert "{{" not in resolved

    def test_placeholder_resolution_nested(self):
        """Should resolve nested placeholders like {{config.auth_pattern}}."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        registry = WorkflowTemplateRegistry()
        template_text = "Use {{config.auth_pattern}} for authentication"
        context = {"config": {"auth_pattern": "JWT"}}

        resolved = registry.resolve_placeholders(template_text, context)

        assert resolved == "Use JWT for authentication"

    def test_placeholder_resolution_missing_variable(self):
        """Should raise error when placeholder variable missing."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
            PlaceholderResolutionError,
        )

        registry = WorkflowTemplateRegistry()
        template_text = "Run tests with {{missing_framework}}"
        context = {"test_framework": "pytest"}

        with pytest.raises(PlaceholderResolutionError) as exc_info:
            registry.resolve_placeholders(template_text, context)

        assert "missing_framework" in str(exc_info.value)


class TestTemplateValidation:
    """Test template validation rules."""

    def test_template_validation_schema(self):
        """Should validate template schema (required fields)."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
            TemplateValidationError,
        )

        registry = WorkflowTemplateRegistry()
        invalid_template = {
            "name": "Missing ID",
            "steps": [],
            # Missing 'id' field
        }

        with pytest.raises(TemplateValidationError) as exc_info:
            registry.register_template(invalid_template)

        assert "id" in str(exc_info.value).lower()

    def test_template_validation_circular_deps(self):
        """Should detect circular dependencies in template steps."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
            TemplateValidationError,
        )

        registry = WorkflowTemplateRegistry()
        circular_template = {
            "id": "circular-test",
            "name": "Circular Test",
            "category": "test",
            "steps": [
                {"id": "step1", "action": "test", "depends_on": ["step2"]},
                {"id": "step2", "action": "test", "depends_on": ["step1"]},
            ],
        }

        with pytest.raises(TemplateValidationError) as exc_info:
            registry.register_template(circular_template)

        assert "circular" in str(exc_info.value).lower()


class TestTemplateOverridePrecedence:
    """Test template override precedence (company > CORTEX)."""

    def test_template_override_precedence(self):
        """Should prefer company templates over CORTEX defaults."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        registry = WorkflowTemplateRegistry()

        # Register CORTEX default
        cortex_template = {
            "id": "tdd-cycle-v1",
            "name": "CORTEX TDD Cycle",
            "category": "tdd",
            "source": "cortex",
            "steps": [{"id": "step1", "action": "cortex_action"}],
        }
        registry.register_template(cortex_template)

        # Register company override
        company_template = {
            "id": "tdd-cycle-v1",
            "name": "Company TDD Cycle",
            "category": "tdd",
            "source": "company",
            "steps": [{"id": "step1", "action": "company_action"}],
        }
        registry.register_template(company_template, override=True)

        # Company template should win
        retrieved = registry.get_template("tdd-cycle-v1")
        assert retrieved["source"] == "company"
        assert retrieved["name"] == "Company TDD Cycle"


class TestTemplateListingAndFiltering:
    """Test template listing and category filtering."""

    def test_template_listing_by_category(self):
        """Should list templates filtered by category."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        registry = WorkflowTemplateRegistry()

        # Register templates in different categories
        registry.register_template(
            {
                "id": "tdd-1",
                "name": "TDD Template 1",
                "category": "tdd",
                "steps": [],
            }
        )
        registry.register_template(
            {
                "id": "tdd-2",
                "name": "TDD Template 2",
                "category": "tdd",
                "steps": [],
            }
        )
        registry.register_template(
            {
                "id": "api-1",
                "name": "API Template 1",
                "category": "api",
                "steps": [],
            }
        )

        # Filter by category
        tdd_templates = registry.list_templates(category="tdd")
        api_templates = registry.list_templates(category="api")
        all_templates = registry.list_templates()

        assert len(tdd_templates) == 2
        assert len(api_templates) == 1
        assert len(all_templates) == 3
        assert all(t["category"] == "tdd" for t in tdd_templates)
        assert all(t["category"] == "api" for t in api_templates)


# AC_COMPLETE: AC-PHASE100-002 ✅ 12/12 tests written (RED phase)

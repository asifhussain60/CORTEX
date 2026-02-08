"""Tests for Phase 47 S1: Registry Structure Setup.

Company/CORTEX separation - registry structure initialization.
"""

import pytest
from cortex.orchestrators.company_separation.registry_structure import (
    CompanyRegistryStructureOrchestrator,
    RegistryPath,
)


class TestRegistryPath:
    """Tests for RegistryPath dataclass."""

    def test_create_registry_path(self):
        """Test creating a registry path."""
        path = RegistryPath(
            relative_path="company/domains/example.yaml",
            absolute_path="/path/to/company/domains/example.yaml",
            content_type="domain",
            is_template=False,
            description="Example domain override",
        )

        assert path.relative_path == "company/domains/example.yaml"
        assert path.content_type == "domain"
        assert path.is_template is False

    def test_registry_path_content_types(self):
        """Test different content types."""
        for content_type in ["domain", "governance", "dashboard", "config"]:
            path = RegistryPath(
                relative_path="test",
                absolute_path="/test",
                content_type=content_type,
                is_template=False,
                description="test",
            )
            assert path.content_type == content_type


class TestCompanyRegistryStructureOrchestrator:
    """Tests for CompanyRegistryStructureOrchestrator."""

    def test_initialize(self):
        """Test initializing orchestrator."""
        orchestrator = CompanyRegistryStructureOrchestrator()
        assert orchestrator is not None
        assert "cortex-registry" in orchestrator.registry_root
        assert "company" in orchestrator.company_root

    def test_setup_registry_structure(self):
        """Test setting up registry structure."""
        orchestrator = CompanyRegistryStructureOrchestrator()
        result = orchestrator.setup_registry_structure()

        assert result is not None
        assert result.status == "initialized"
        assert len(result.paths_created) > 0

    def test_registry_structure_paths(self):
        """Test registry structure includes required paths."""
        orchestrator = CompanyRegistryStructureOrchestrator()
        result = orchestrator.setup_registry_structure()

        path_types = [p.content_type for p in result.paths_created]

        assert "domain" in path_types
        assert "governance" in path_types

    def test_templates_generated(self):
        """Test templates are generated."""
        orchestrator = CompanyRegistryStructureOrchestrator()
        result = orchestrator.setup_registry_structure()

        assert result.templates_generated > 0

    def test_generate_registry_index(self):
        """Test generating company registry index."""
        orchestrator = CompanyRegistryStructureOrchestrator()
        index = orchestrator.generate_registry_index()

        assert isinstance(index, dict)
        assert "version" in index
        assert "registry_name" in index
        assert index["registry_name"] == "company"

    def test_registry_index_structure(self):
        """Test index has correct structure."""
        orchestrator = CompanyRegistryStructureOrchestrator()
        index = orchestrator.generate_registry_index()

        assert "parent_registry" in index
        assert index["parent_registry"] == "_cortex-master"
        assert "precedence" in index
        assert index["precedence"] > 0
        assert "sections" in index
        assert "resolution_order" in index

    def test_registry_index_sections(self):
        """Test index includes all required sections."""
        orchestrator = CompanyRegistryStructureOrchestrator()
        index = orchestrator.generate_registry_index()

        sections = index["sections"]
        assert "domains" in sections
        assert "governance" in sections

    def test_create_gitignore(self):
        """Test creating gitignore content."""
        orchestrator = CompanyRegistryStructureOrchestrator()
        content = orchestrator.create_gitignore()

        assert isinstance(content, str)
        assert len(content) > 0
        assert "company" in content.lower() or "ignore" in content.lower()

    def test_validate_structure(self):
        """Test validating registry structure."""
        orchestrator = CompanyRegistryStructureOrchestrator()
        result = orchestrator.validate_structure()

        assert isinstance(result, bool)

    def test_get_migration_plan(self):
        """Test getting migration plan."""
        orchestrator = CompanyRegistryStructureOrchestrator()
        plan = orchestrator.get_migration_plan()

        assert isinstance(plan, list)
        assert len(plan) > 0
        assert any("company" in step.lower() for step in plan)

    def test_migration_plan_steps(self):
        """Test migration plan covers key steps."""
        orchestrator = CompanyRegistryStructureOrchestrator()
        plan = orchestrator.get_migration_plan()

        plan_str = str(plan).lower()

        assert any("create" in step.lower() for step in plan)
        assert any("copy" in step.lower() for step in plan)
        assert any("test" in step.lower() for step in plan)

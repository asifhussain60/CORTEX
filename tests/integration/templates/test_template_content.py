"""Tests for template content library (arch-020-template-content).

Covers template discovery, validation, use-cases, domains, and workflows.
"""

import pytest
from cortex.templates.template_content import (
    TemplateLibrary,
    TemplateDiscovery,
    TemplateValidator
)


class TestUseCaseTemplates:
    """Test use-case template availability and quality."""

    def test_api_integration_template_exists(self) -> None:
        """Test API integration template exists and is valid."""
        library = TemplateLibrary()
        template = library.get_template("use_case", "api_integration")
        assert template is not None
        assert "{{ endpoint }}" in template.get("content", "")
        assert template.get("name") == "api_integration"

    def test_workflow_orchestration_template(self) -> None:
        """Test workflow orchestration template."""
        library = TemplateLibrary()
        template = library.get_template("use_case", "workflow_orchestration")
        assert template is not None
        assert template.get("description") is not None

    def test_monitoring_template(self) -> None:
        """Test monitoring template exists."""
        library = TemplateLibrary()
        template = library.get_template("use_case", "monitoring")
        assert template is not None
        assert "metric" in template.get("content", "").lower()

    def test_list_all_use_case_templates(self) -> None:
        """Test listing all available use-case templates."""
        library = TemplateLibrary()
        templates = library.list_templates("use_case")
        assert len(templates) >= 20
        assert isinstance(templates, list)


class TestDomainSpecificTemplates:
    """Test domain-specific templates."""

    def test_finance_domain_templates(self) -> None:
        """Test finance domain templates exist."""
        library = TemplateLibrary()
        templates = library.list_templates("domain", "finance")
        assert len(templates) >= 10
        for template_id in templates[:3]:
            template = library.get_template("domain", template_id, domain="finance")
            assert template is not None

    def test_healthcare_domain_templates(self) -> None:
        """Test healthcare domain templates exist."""
        library = TemplateLibrary()
        templates = library.list_templates("domain", "healthcare")
        assert len(templates) >= 10

    def test_ecommerce_domain_templates(self) -> None:
        """Test e-commerce domain templates exist."""
        library = TemplateLibrary()
        templates = library.list_templates("domain", "ecommerce")
        assert len(templates) >= 10

    def test_domain_template_has_documentation(self) -> None:
        """Test that domain templates have documentation."""
        library = TemplateLibrary()
        finance_templates = library.list_templates("domain", "finance")
        if finance_templates:
            template = library.get_template("domain", finance_templates[0], domain="finance")
            if template:
                assert template.get("documentation") is not None or \
                       template.get("description") is not None


class TestWorkflowTemplates:
    """Test workflow pattern templates."""

    def test_sequential_workflow_template(self) -> None:
        """Test sequential workflow template."""
        library = TemplateLibrary()
        template = library.get_template("workflow", "sequential")
        assert template is not None
        assert "step" in template.get("content", "").lower()

    def test_parallel_workflow_template(self) -> None:
        """Test parallel workflow template."""
        library = TemplateLibrary()
        template = library.get_template("workflow", "parallel")
        assert template is not None

    def test_conditional_workflow_template(self) -> None:
        """Test conditional workflow template."""
        library = TemplateLibrary()
        template = library.get_template("workflow", "conditional")
        assert template is not None

    def test_list_workflow_templates(self) -> None:
        """Test listing all workflow templates."""
        library = TemplateLibrary()
        templates = library.list_templates("workflow")
        assert len(templates) >= 15


class TestTemplateDiscovery:
    """Test template discovery functionality."""

    def test_discover_by_keyword(self) -> None:
        """Test discovering templates by keyword."""
        discovery = TemplateDiscovery()
        results = discovery.search("api")
        assert len(results) > 0
        assert any("api" in str(r).lower() for r in results)

    def test_discover_by_domain(self) -> None:
        """Test discovering templates by domain."""
        discovery = TemplateDiscovery()
        results = discovery.search_by_domain("finance")
        assert len(results) >= 10

    def test_discover_by_use_case(self) -> None:
        """Test discovering templates by use-case."""
        discovery = TemplateDiscovery()
        results = discovery.search_by_use_case("integration")
        assert len(results) > 0

    def test_discovery_returns_with_metadata(self) -> None:
        """Test discovery returns templates with metadata."""
        discovery = TemplateDiscovery()
        results = discovery.search("workflow")
        if results:
            first_result = results[0]
            assert "name" in first_result or "id" in first_result


class TestTemplateOrganization:
    """Test template hierarchical organization."""

    def test_templates_organized_hierarchically(self) -> None:
        """Test templates are organized by use-case → domain → workflow."""
        library = TemplateLibrary()
        
        # Get use-case level
        use_cases = library.list_templates("use_case")
        assert len(use_cases) > 0
        
        # Get domain level
        domains = library.list_domains()
        assert len(domains) > 0
        
        # Get workflow level
        workflows = library.list_templates("workflow")
        assert len(workflows) > 0

    def test_template_hierarchy_navigation(self) -> None:
        """Test navigating template hierarchy."""
        library = TemplateLibrary()
        
        # Start with use-case
        use_case = library.get_template("use_case", "api_integration")
        assert use_case is not None
        
        # Get related domain templates
        related_domains = library.get_related_templates(use_case)
        assert isinstance(related_domains, list)

    def test_list_domains(self) -> None:
        """Test listing available domains."""
        library = TemplateLibrary()
        domains = library.list_domains()
        assert "finance" in domains
        assert "healthcare" in domains
        assert "ecommerce" in domains


class TestTemplateValidation:
    """Test template validation and quality."""

    def test_all_templates_validated(self) -> None:
        """Test that all templates pass validation."""
        library = TemplateLibrary()
        validator = TemplateValidator()
        
        all_templates = library.list_all_templates()
        validation_errors = []
        
        for template_id in all_templates[:10]:  # Test subset
            template = library.get_template_by_id(template_id)
            errors = validator.validate_template(template)
            if errors:
                validation_errors.append((template_id, errors))
        
        assert len(validation_errors) == 0, f"Validation errors: {validation_errors}"

    def test_template_has_required_fields(self) -> None:
        """Test templates have all required fields."""
        library = TemplateLibrary()
        template = library.get_template("use_case", "api_integration")
        
        required_fields = ["name", "content", "description"]
        for field in required_fields:
            assert field in template, f"Missing field: {field}"

    def test_template_documentation_present(self) -> None:
        """Test templates have documentation."""
        library = TemplateLibrary()
        template = library.get_template("use_case", "api_integration")
        
        has_docs = ("documentation" in template and template["documentation"]) or \
                   ("examples" in template and template["examples"]) or \
                   ("description" in template and len(template.get("description", "")) > 20)
        
        assert has_docs, "Template lacks documentation"


class TestTemplateExamples:
    """Test template examples and usage."""

    def test_template_has_examples(self) -> None:
        """Test templates include usage examples."""
        library = TemplateLibrary()
        template = library.get_template("use_case", "api_integration")
        
        has_examples = template.get("examples") is not None
        assert has_examples or "example" in template.get("documentation", "").lower()

    def test_examples_are_valid(self) -> None:
        """Test that template examples are valid."""
        library = TemplateLibrary()
        validator = TemplateValidator()
        
        template = library.get_template("use_case", "api_integration")
        examples = template.get("examples", [])
        
        for example in examples[:3]:
            errors = validator.validate_example(example)
            assert len(errors) == 0, f"Example validation failed: {errors}"

    def test_example_parameters_documented(self) -> None:
        """Test that example parameters are documented."""
        library = TemplateLibrary()
        template = library.get_template("use_case", "api_integration")
        
        if template.get("examples"):
            for example in template["examples"][:1]:
                assert "description" in example or "parameters" in example


class TestTemplateIntegration:
    """Integration tests for template system."""

    def test_end_to_end_template_discovery_and_use(self) -> None:
        """Test complete workflow: discover → retrieve → validate → use."""
        library = TemplateLibrary()
        discovery = TemplateDiscovery()
        validator = TemplateValidator()
        
        # Discover
        results = discovery.search("workflow")
        assert len(results) > 0
        
        # Retrieve
        template_id = results[0].get("id") or results[0].get("name")
        template = library.get_template_by_id(template_id)
        assert template is not None
        
        # Validate
        errors = validator.validate_template(template)
        assert len(errors) == 0
        
        # Use (render example)
        if template.get("examples"):
            example = template["examples"][0]
            assert example is not None

    def test_complete_template_library_integrity(self) -> None:
        """Test complete integrity of template library."""
        library = TemplateLibrary()
        
        # Count categories
        use_cases = library.list_templates("use_case")
        workflows = library.list_templates("workflow")
        domains = library.list_domains()
        
        # Verify minimums
        assert len(use_cases) >= 20, f"Need >= 20 use-cases, got {len(use_cases)}"
        assert len(workflows) >= 15, f"Need >= 15 workflows, got {len(workflows)}"
        assert len(domains) >= 3, f"Need >= 3 domains, got {len(domains)}"
        
        # Verify each domain has templates
        for domain in domains:
            domain_templates = library.list_templates("domain", domain)
            assert len(domain_templates) >= 10, \
                f"Domain {domain} needs >= 10 templates, got {len(domain_templates)}"

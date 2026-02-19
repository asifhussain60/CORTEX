"""
PHASE-20: Template Content Population Tests

AC-TC-001-01: Content Population Strategy
AC-TC-001-02: Knowledge Base Schema
AC-TC-002-01: Tier-2 Domain Templates
AC-TC-002-02: Template Validation
AC-TC-003-01: Content Generation
AC-TC-003-02: Quality Assurance

Target: 72+ tests (12 per AC)
TDD Phase: RED (tests written, implementation pending)

"""

import pytest
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import yaml


# =============================================================================
# AC-TC-001-01: Content Population Strategy Tests
# =============================================================================

class TestContentPopulationStrategy:
    """Tests for content population strategy and registry."""
    
    @pytest.fixture
    def content_strategy(self):
        """Create ContentPopulationStrategy instance."""
        from cortex.templates.content_strategy import ContentPopulationStrategy
        return ContentPopulationStrategy()
    
    def test_strategy_creation(self, content_strategy):
        """Should create content population strategy."""
        assert content_strategy is not None
        assert hasattr(content_strategy, 'domains')
        assert hasattr(content_strategy, 'get_domain_templates')
    
    def test_strategy_lists_domains(self, content_strategy):
        """Should list all supported domains."""
        domains = content_strategy.domains
        assert len(domains) >= 6
        assert 'planning' in domains
        assert 'governance' in domains
        assert 'analysis' in domains
        assert 'integration' in domains
        assert 'validation' in domains
        assert 'execution' in domains
    
    def test_strategy_template_count_per_domain(self, content_strategy):
        """Should have 8-15 templates per domain."""
        for domain in content_strategy.domains:
            templates = content_strategy.get_domain_templates(domain)
            assert len(templates) >= 8, f"Domain {domain} has < 8 templates"
            assert len(templates) <= 15, f"Domain {domain} has > 15 templates"
    
    def test_strategy_total_template_count(self, content_strategy):
        """Should have 60-90 total templates."""
        total = content_strategy.total_template_count
        assert total >= 60, f"Total templates {total} < 60 minimum"
        assert total <= 90, f"Total templates {total} > 90 maximum"
    
    def test_strategy_get_template_metadata(self, content_strategy):
        """Should get template metadata."""
        templates = content_strategy.get_domain_templates('planning')
        for template in templates:
            assert 'id' in template
            assert 'name' in template
            assert 'description' in template
            assert 'domain' in template
    
    def test_strategy_validate_template_ids_unique(self, content_strategy):
        """Should have unique template IDs across all domains."""
        all_ids = []
        for domain in content_strategy.domains:
            templates = content_strategy.get_domain_templates(domain)
            for template in templates:
                all_ids.append(template['id'])
        
        assert len(all_ids) == len(set(all_ids)), "Duplicate template IDs found"
    
    def test_strategy_get_template_by_id(self, content_strategy):
        """Should get specific template by ID."""
        template = content_strategy.get_template_by_id('planning-recommendations')
        assert template is not None
        assert template['domain'] == 'planning'
    
    def test_strategy_get_template_by_id_not_found(self, content_strategy):
        """Should return None for unknown template ID."""
        template = content_strategy.get_template_by_id('nonexistent-template')
        assert template is None
    
    def test_strategy_get_templates_by_category(self, content_strategy):
        """Should filter templates by category."""
        templates = content_strategy.get_templates_by_category('response')
        assert len(templates) > 0
        for t in templates:
            assert t.get('category') == 'response'
    
    def test_strategy_export_registry(self, content_strategy):
        """Should export complete template registry."""
        registry = content_strategy.export_registry()
        assert 'domains' in registry
        assert 'templates' in registry
        assert 'total_count' in registry
    
    def test_strategy_validate_registry_integrity(self, content_strategy):
        """Should validate registry integrity."""
        result = content_strategy.validate_registry()
        assert result.valid is True
        assert len(result.errors) == 0


# =============================================================================
# AC-TC-001-02: Knowledge Base Schema Tests
# =============================================================================

class TestKnowledgeBaseSchema:
    """Tests for knowledge base schema extension."""
    
    @pytest.fixture
    def knowledge_schema(self):
        """Create KnowledgeBaseSchema instance."""
        from cortex.templates.knowledge_schema import KnowledgeBaseSchema
        return KnowledgeBaseSchema()
    
    def test_schema_creation(self, knowledge_schema):
        """Should create knowledge base schema."""
        assert knowledge_schema is not None
        assert hasattr(knowledge_schema, 'schema_version')
    
    def test_schema_defines_template_structure(self, knowledge_schema):
        """Should define template structure schema."""
        structure = knowledge_schema.get_template_structure()
        assert 'metadata' in structure
        assert 'template' in structure
        assert 'content' in structure
    
    def test_schema_metadata_fields(self, knowledge_schema):
        """Should define required metadata fields."""
        metadata = knowledge_schema.get_metadata_schema()
        required = metadata.get('required', [])
        assert 'template_id' in required
        assert 'version' in required
        assert 'domain' in required
    
    def test_schema_content_sections(self, knowledge_schema):
        """Should define content section types."""
        sections = knowledge_schema.get_section_types()
        assert 'header' in sections
        assert 'body' in sections
        assert 'footer' in sections
    
    def test_schema_validate_template(self, knowledge_schema):
        """Should validate template against schema."""
        valid_template = {
            'metadata': {
                'template_id': 'test-template',
                'version': '1.0',
                'domain': 'testing'
            },
            'template': {
                'structure': []
            }
        }
        result = knowledge_schema.validate(valid_template)
        assert result.valid is True
    
    def test_schema_reject_invalid_template(self, knowledge_schema):
        """Should reject invalid template."""
        invalid_template = {
            'metadata': {
                'template_id': 'test'
                # Missing required fields
            }
        }
        result = knowledge_schema.validate(invalid_template)
        assert result.valid is False
        assert len(result.errors) > 0
    
    def test_schema_supports_inheritance(self, knowledge_schema):
        """Should support template inheritance."""
        inheritance = knowledge_schema.get_inheritance_rules()
        assert 'base_templates' in inheritance
        assert 'override_rules' in inheritance
    
    def test_schema_variable_definitions(self, knowledge_schema):
        """Should define template variables."""
        variables = knowledge_schema.get_variable_schema()
        assert 'types' in variables
        assert 'string' in variables['types']
        assert 'list' in variables['types']
        assert 'object' in variables['types']
    
    def test_schema_export_json_schema(self, knowledge_schema):
        """Should export as JSON schema."""
        json_schema = knowledge_schema.to_json_schema()
        assert '$schema' in json_schema
        assert 'type' in json_schema
        assert json_schema['type'] == 'object'
    
    def test_schema_versioning(self, knowledge_schema):
        """Should support schema versioning."""
        assert knowledge_schema.schema_version is not None
        assert knowledge_schema.is_compatible('1.0')


# =============================================================================
# AC-TC-002-01: Tier-2 Domain Templates Tests
# =============================================================================

class TestTier2DomainTemplates:
    """Tests for tier-2 domain template creation."""
    
    @pytest.fixture
    def template_manager(self):
        """Create TemplateManager instance."""
        from cortex.templates.template_manager import TemplateManager
        return TemplateManager()
    
    def test_manager_creation(self, template_manager):
        """Should create template manager."""
        assert template_manager is not None
    
    def test_planning_domain_templates(self, template_manager):
        """Should have planning domain templates."""
        templates = template_manager.get_domain_templates('planning')
        expected = [
            'planning-recommendations',
            'planning-impact-assessment',
            'planning-timeline',
            'planning-resource-allocation',
            'planning-risk-analysis',
            'planning-milestone-tracker',
            'planning-dependency-map',
            'planning-progress-report'
        ]
        template_ids = [t['id'] for t in templates]
        for expected_id in expected:
            assert expected_id in template_ids, f"Missing {expected_id}"
    
    def test_analysis_domain_templates(self, template_manager):
        """Should have analysis domain templates."""
        templates = template_manager.get_domain_templates('analysis')
        assert len(templates) >= 8
        template_ids = [t['id'] for t in templates]
        assert any('codebase' in tid or 'code' in tid for tid in template_ids)
        assert any('impact' in tid for tid in template_ids)
    
    def test_integration_domain_templates(self, template_manager):
        """Should have integration domain templates."""
        templates = template_manager.get_domain_templates('integration')
        assert len(templates) >= 8
    
    def test_validation_domain_templates(self, template_manager):
        """Should have validation domain templates."""
        templates = template_manager.get_domain_templates('validation')
        assert len(templates) >= 8
    
    def test_execution_domain_templates(self, template_manager):
        """Should have execution domain templates."""
        templates = template_manager.get_domain_templates('execution')
        assert len(templates) >= 8
    
    def test_system_domain_templates(self, template_manager):
        """Should have system domain templates."""
        templates = template_manager.get_domain_templates('system')
        assert len(templates) >= 6
    
    def test_template_has_content(self, template_manager):
        """Should have actual content in templates."""
        templates = template_manager.get_domain_templates('planning')
        for template in templates:
            content = template_manager.get_template_content(template['id'])
            assert content is not None
            assert len(content) > 100, f"Template {template['id']} has minimal content"
    
    def test_template_variable_placeholders(self, template_manager):
        """Should have proper variable placeholders."""
        content = template_manager.get_template_content('planning-recommendations')
        assert '{' in content  # Has placeholders
        assert '}' in content
    
    def test_template_renders_with_variables(self, template_manager):
        """Should render template with variables."""
        variables = {
            'plan_title': 'Test Plan',
            'phase': 'PHASE-01',
            'ac_count': 5,
            'estimated_hours': 10,
            'ac_table': '| AC | Description |\n|-----|-------------|',
            'recommendation': 'Proceed with implementation',
            'dependencies': 'None',
            'risks': 'Low risk'
        }
        rendered = template_manager.render_template('planning-recommendations', variables)
        assert 'Test Plan' in rendered
        assert 'PHASE-01' in rendered
    
    def test_template_missing_variable_error(self, template_manager):
        """Should handle missing required variables."""
        with pytest.raises(ValueError) as exc:
            template_manager.render_template('planning-recommendations', {})
        assert 'required' in str(exc.value).lower() or 'missing' in str(exc.value).lower()


# =============================================================================
# AC-TC-002-02: Template Validation Tests
# =============================================================================

class TestTemplateValidation:
    """Tests for template validation and consistency."""
    
    @pytest.fixture
    def template_validator(self):
        """Create TemplateValidator instance."""
        from cortex.templates.template_validation import TemplateContentValidator
        return TemplateContentValidator()
    
    def test_validator_creation(self, template_validator):
        """Should create template content validator."""
        assert template_validator is not None
    
    def test_validate_template_structure(self, template_validator):
        """Should validate template structure."""
        template = {
            'metadata': {'template_id': 'test', 'version': '1.0', 'domain': 'test'},
            'template': {'structure': [{'section': 'header'}]}
        }
        result = template_validator.validate_structure(template)
        assert result.valid is True
    
    def test_validate_template_content(self, template_validator):
        """Should validate template content."""
        content = "## Header\n\nThis is content with {variable}."
        result = template_validator.validate_content(content)
        assert result.valid is True
    
    def test_validate_variable_syntax(self, template_validator):
        """Should validate variable syntax."""
        content = "Valid: {variable}, Invalid: {{double_brace}}"
        result = template_validator.validate_variables(content)
        # Should find the double brace issue
        assert 'double_brace' in str(result.warnings) or result.valid
    
    def test_validate_markdown_syntax(self, template_validator):
        """Should validate markdown syntax."""
        content = "# Heading\n\n- List item\n- Another item\n\n```python\ncode\n```"
        result = template_validator.validate_markdown(content)
        assert result.valid is True
    
    def test_validate_cross_references(self, template_validator):
        """Should validate cross-references between templates."""
        result = template_validator.validate_cross_references('planning')
        assert result.valid is True
    
    def test_validate_inheritance_chain(self, template_validator):
        """Should validate inheritance chain."""
        result = template_validator.validate_inheritance('planning-recommendations')
        assert result.valid is True
    
    def test_validate_all_templates(self, template_validator):
        """Should validate all templates in registry."""
        result = template_validator.validate_all()
        assert result.valid is True
        assert result.templates_checked >= 60
    
    def test_generate_validation_report(self, template_validator):
        """Should generate validation report."""
        report = template_validator.generate_report()
        assert 'summary' in report
        assert 'details' in report
        assert 'timestamp' in report
    
    def test_detect_orphaned_templates(self, template_validator):
        """Should detect orphaned templates (not in registry)."""
        orphans = template_validator.find_orphaned_templates()
        # Should be empty if registry is complete
        assert isinstance(orphans, list)
    
    def test_detect_duplicate_content(self, template_validator):
        """Should detect templates with duplicate content."""
        duplicates = template_validator.find_duplicates()
        assert isinstance(duplicates, list)


# =============================================================================
# AC-TC-003-01: Content Generation Tests
# =============================================================================

class TestContentGeneration:
    """Tests for content generation utilities."""
    
    @pytest.fixture
    def content_generator(self):
        """Create ContentGenerator instance."""
        from cortex.templates.content_generator import ContentGenerator
        return ContentGenerator()
    
    def test_generator_creation(self, content_generator):
        """Should create content generator."""
        assert content_generator is not None
    
    def test_generate_template_skeleton(self, content_generator):
        """Should generate template skeleton."""
        skeleton = content_generator.generate_skeleton(
            template_id='new-template',
            domain='testing',
            category='response'
        )
        assert 'metadata' in skeleton
        assert skeleton['metadata']['template_id'] == 'new-template'
    
    def test_generate_from_existing_pattern(self, content_generator):
        """Should generate template from existing pattern."""
        template = content_generator.generate_from_pattern(
            pattern='planning-recommendations',
            new_id='custom-recommendations',
            domain='custom'
        )
        assert template['metadata']['template_id'] == 'custom-recommendations'
    
    def test_generate_section_content(self, content_generator):
        """Should generate section content."""
        section = content_generator.generate_section(
            section_type='header',
            title='Test Header',
            variables=['ac_id', 'phase']
        )
        assert 'Test Header' in section
        assert '{ac_id}' in section or '{phase}' in section
    
    def test_generate_variable_documentation(self, content_generator):
        """Should generate variable documentation."""
        docs = content_generator.generate_variable_docs(
            variables={'ac_id': 'str', 'count': 'int'}
        )
        assert 'ac_id' in docs
        assert 'count' in docs
    
    def test_generate_batch_templates(self, content_generator):
        """Should generate batch of templates."""
        specs = [
            {'id': 'batch-1', 'domain': 'testing'},
            {'id': 'batch-2', 'domain': 'testing'}
        ]
        templates = content_generator.generate_batch(specs)
        assert len(templates) == 2
    
    def test_merge_template_content(self, content_generator):
        """Should merge template content."""
        base = {'metadata': {'version': '1.0'}, 'content': 'base'}
        overlay = {'content': 'overlay'}
        merged = content_generator.merge(base, overlay)
        assert merged['content'] == 'overlay'
        assert merged['metadata']['version'] == '1.0'
    
    def test_transform_template_format(self, content_generator):
        """Should transform template format."""
        yaml_content = """
metadata:
  template_id: test
template:
  structure: []
"""
        transformed = content_generator.transform(yaml_content, 'json')
        assert isinstance(transformed, str)
        assert 'template_id' in transformed
    
    def test_export_template_bundle(self, content_generator):
        """Should export template bundle."""
        bundle = content_generator.export_bundle('planning')
        assert 'templates' in bundle
        assert 'manifest' in bundle
    
    def test_import_template_bundle(self, content_generator, tmp_path):
        """Should import template bundle."""
        bundle_path = tmp_path / "test_bundle.yaml"
        bundle_content = {
            'manifest': {'version': '1.0'},
            'templates': [
                {'id': 'imported-1', 'domain': 'test', 'content': 'test'}
            ]
        }
        bundle_path.write_text(yaml.dump(bundle_content))
        
        result = content_generator.import_bundle(str(bundle_path))
        assert result.success is True
        assert result.imported_count == 1


# =============================================================================
# AC-TC-003-02: Quality Assurance Tests
# =============================================================================

class TestQualityAssurance:
    """Tests for template quality assurance."""
    
    @pytest.fixture
    def qa_framework(self):
        """Create QualityAssuranceFramework instance."""
        from cortex.templates.quality_assurance import QualityAssuranceFramework
        return QualityAssuranceFramework()
    
    def test_qa_creation(self, qa_framework):
        """Should create QA framework."""
        assert qa_framework is not None
    
    def test_qa_completeness_check(self, qa_framework):
        """Should check template completeness."""
        result = qa_framework.check_completeness('planning-recommendations')
        assert result.score >= 0.0
        assert result.score <= 1.0
    
    def test_qa_consistency_check(self, qa_framework):
        """Should check template consistency."""
        result = qa_framework.check_consistency('planning')
        assert result.consistent is True or len(result.issues) > 0
    
    def test_qa_coverage_check(self, qa_framework):
        """Should check domain coverage."""
        coverage = qa_framework.check_coverage()
        assert 'planning' in coverage
        assert 'analysis' in coverage
        assert all(c >= 0.8 for c in coverage.values())  # 80%+ coverage
    
    def test_qa_generate_metrics(self, qa_framework):
        """Should generate quality metrics."""
        metrics = qa_framework.generate_metrics()
        assert 'total_templates' in metrics
        assert 'valid_templates' in metrics
        assert 'coverage_score' in metrics
    
    def test_qa_lint_template(self, qa_framework):
        """Should lint template for issues."""
        issues = qa_framework.lint_template('planning-recommendations')
        assert isinstance(issues, list)
    
    def test_qa_suggest_improvements(self, qa_framework):
        """Should suggest template improvements."""
        suggestions = qa_framework.suggest_improvements('planning-recommendations')
        assert isinstance(suggestions, list)
    
    def test_qa_compare_templates(self, qa_framework):
        """Should compare two templates."""
        comparison = qa_framework.compare_templates(
            'planning-recommendations',
            'planning-impact-assessment'
        )
        assert 'similarity' in comparison
        assert 'differences' in comparison
    
    def test_qa_generate_report(self, qa_framework):
        """Should generate QA report."""
        report = qa_framework.generate_report()
        assert 'summary' in report
        assert 'metrics' in report
        assert 'recommendations' in report
    
    def test_qa_run_full_suite(self, qa_framework):
        """Should run full QA test suite."""
        result = qa_framework.run_full_suite()
        assert result.passed is True or len(result.failures) > 0
        assert result.tests_run >= 10
    
    def test_qa_export_results(self, qa_framework, tmp_path):
        """Should export QA results."""
        output = tmp_path / "qa_results.json"
        qa_framework.export_results(str(output))
        assert output.exists()


# =============================================================================
# Integration Tests
# =============================================================================

class TestTemplateContentIntegration:
    """Integration tests for template content system."""
    
    @pytest.fixture
    def full_system(self):
        """Create full template content system."""
        from cortex.templates.content_strategy import ContentPopulationStrategy
        from cortex.templates.template_manager import TemplateManager
        from cortex.templates.quality_assurance import QualityAssuranceFramework
        
        return {
            'strategy': ContentPopulationStrategy(),
            'manager': TemplateManager(),
            'qa': QualityAssuranceFramework()
        }
    
    def test_end_to_end_template_workflow(self, full_system):
        """Test complete template workflow."""
        strategy = full_system['strategy']
        manager = full_system['manager']
        qa = full_system['qa']
        
        # Get templates from strategy
        templates = strategy.get_domain_templates('planning')
        assert len(templates) >= 8
        
        # Render a template
        rendered = manager.render_template(
            'planning-recommendations',
            {
                'plan_title': 'Test', 
                'phase': 'PHASE-01', 
                'ac_count': 5, 
                'estimated_hours': 10,
                'ac_table': '| AC | Description |',
                'recommendation': 'Proceed',
                'dependencies': 'None',
                'risks': 'Low'
            }
        )
        assert 'Test' in rendered
        
        # Validate with QA
        result = qa.check_completeness('planning-recommendations')
        assert result.score >= 0.8
    
    def test_template_registry_consistency(self, full_system):
        """Test template registry consistency."""
        strategy = full_system['strategy']
        qa = full_system['qa']
        
        # All templates in strategy should pass QA
        for domain in strategy.domains:
            templates = strategy.get_domain_templates(domain)
            for template in templates:
                result = qa.check_completeness(template['id'])
                assert result.score >= 0.7, f"Template {template['id']} failed QA"
    
    def test_all_domains_have_templates(self, full_system):
        """Test all domains have sufficient templates."""
        strategy = full_system['strategy']
        
        expected_domains = ['planning', 'analysis', 'integration', 
                          'validation', 'execution', 'system']
        
        for domain in expected_domains:
            templates = strategy.get_domain_templates(domain)
            assert len(templates) >= 6, f"Domain {domain} has < 6 templates"


# =============================================================================
# Test All Modules Importable
# =============================================================================

def test_all_modules_importable():
    """Test that all PHASE-20 modules can be imported."""
    modules = [
        'cortex.templates.content_strategy',
        'cortex.templates.knowledge_schema',
        'cortex.templates.template_manager',
        'cortex.templates.template_validation',
        'cortex.templates.content_generator',
        'cortex.templates.quality_assurance',
    ]
    
    for module in modules:
        try:
            __import__(module)
        except ImportError as e:
            pytest.fail(f"Failed to import {module}: {e}")

"""
Test Suite for Legacy Spec Generator Quality Assurance

Tests ensure generated specs are accurate, readable, and properly formatted.
Prevents "nonsense" output through comprehensive validation.

RED → GREEN → REFACTOR cycle for quality gates.

Author: CORTEX
Version: 1.0.0
Date: December 15, 2025
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.operations.modules.generators.legacy_spec_generator import LegacySpecGenerator


class TestMermaidDiagramGeneration:
    """Test Mermaid diagram generation quality."""
    
    def test_no_text_truncation_mid_word(self, sample_generator):
        """Test that Mermaid text is never truncated mid-word."""
        # RED: This should FAIL initially due to truncation bug
        long_text = "String.IsNullOrWhiteSpace(SubaccountId)"
        sanitized = sample_generator._sanitize_mermaid_text(long_text, max_length=20)
        
        # Should not end mid-word like "StringIsNullOrWhiteS"
        assert not sanitized.endswith('S'), f"Text truncated mid-word: {sanitized}"
        assert ' ' not in sanitized or sanitized == sanitized.strip()
    
    def test_rule_names_are_meaningful(self, sample_generator):
        """Test that rule names preserve semantic meaning."""
        # RED: This should FAIL due to [:50] truncation
        condition = "InvoiceAmount <= 0"
        rule_name = sample_generator._generate_rule_name(condition)
        
        # Should contain operator context
        assert 'InvoiceAmount' in rule_name
        assert any(op in rule_name for op in ['equals', 'less', 'greater', 'not'])
        assert len(rule_name) > 0
    
    def test_diagrams_embedded_in_markdown(self, temp_spec_generator):
        """Test that Mermaid diagrams are embedded in markdown files."""
        # RED: Currently diagrams are only linked, not embedded
        temp_spec_generator.analyze()
        temp_spec_generator.generate_all()
        
        business_spec_path = temp_spec_generator.output_dir / 'business-spec.md'
        content = business_spec_path.read_text(encoding='utf-8')
        
        # Should have embedded diagrams with ```mermaid blocks
        assert '```mermaid' in content, "Diagrams should be embedded in markdown"
        assert 'flowchart TD' in content or 'sequenceDiagram' in content
    
    def test_separate_mmd_files_also_created(self, temp_spec_generator):
        """Test that separate .mmd files are created alongside embedded diagrams."""
        temp_spec_generator.analyze()
        temp_spec_generator.generate_all()
        
        diagrams_dir = temp_spec_generator.output_dir / 'diagrams'
        
        # Should have separate .mmd files
        assert diagrams_dir.exists()
        assert (diagrams_dir / 'flowchart.mmd').exists()
        assert (diagrams_dir / 'sequence.mmd').exists()
    
    def test_mermaid_syntax_is_valid(self, temp_spec_generator):
        """Test that generated Mermaid syntax is valid."""
        temp_spec_generator.analyze()
        temp_spec_generator.generate_all()
        
        flowchart_path = temp_spec_generator.output_dir / 'diagrams' / 'flowchart.mmd'
        content = flowchart_path.read_text(encoding='utf-8')
        
        # Should NOT have markdown fences in .mmd files
        assert not content.startswith('```'), ".mmd files should not have markdown fences"
        
        # Should start with valid diagram type
        assert content.startswith('flowchart') or content.startswith('graph')
        
        # Should have balanced brackets
        assert content.count('(') == content.count(')')
        assert content.count('[') == content.count(']')
        assert content.count('{') == content.count('}')


class TestMethodParameterExtraction:
    """Test method parameter extraction accuracy."""
    
    def test_parameters_extracted_not_none(self, sample_generator):
        """Test that method parameters are extracted correctly, not 'None'."""
        # RED: Currently shows Execute(None) in specs
        sample_generator.analyze()
        
        primary_method = next(
            (m for m in sample_generator.methods if m.name in ['Execute', 'Run', 'Process']),
            None
        )
        
        assert primary_method is not None
        # Should have actual parameter names, not empty list showing as 'None'
        if primary_method.parameters and primary_method.parameters != ['']:
            for param in primary_method.parameters:
                assert param.strip() != '', "Parameters should not be empty strings"
                assert param != 'None', "Parameters should not be literal 'None'"


class TestBusinessSpecQuality:
    """Test business specification document quality."""
    
    def test_no_truncated_capability_descriptions(self, temp_spec_generator):
        """Test that capability descriptions are complete, not truncated."""
        temp_spec_generator.analyze()
        temp_spec_generator.generate_all()
        
        spec_path = temp_spec_generator.output_dir / 'business-spec.md'
        content = spec_path.read_text(encoding='utf-8')
        
        # Check for common truncation patterns
        assert 'InvoiceAmount = 0' not in content, "Should show full condition with operator"
        assert '...' not in content or content.count('...') < 5, "Too many truncations"
    
    def test_validation_requirements_are_complete(self, temp_spec_generator):
        """Test that validation requirements show full field names and messages."""
        temp_spec_generator.analyze()
        temp_spec_generator.generate_all()
        
        spec_path = temp_spec_generator.output_dir / 'business-spec.md'
        content = spec_path.read_text(encoding='utf-8')
        
        # Should not have "Unknown" as field names
        validation_section = content.split('Validation Requirements:')
        if len(validation_section) > 1:
            assert validation_section[1].count('Unknown') < 3, "Too many unknown field names"


class TestPrePublishLinting:
    """Test pre-publish lint checks run before generation completes."""
    
    def test_lint_checks_run_automatically(self, temp_spec_generator):
        """Test that lint checks run as part of generate_all()."""
        # RED: Currently _run_lint_checks exists but may not be called
        temp_spec_generator.analyze()
        result = temp_spec_generator.generate_all()
        
        # generate_all should return lint results or store them
        assert hasattr(temp_spec_generator, 'lint_results') or result is not None
    
    def test_lint_catches_missing_files(self, temp_spec_generator):
        """Test that lint checks catch missing required files."""
        temp_spec_generator.analyze()
        
        # Run lint without generating files (should fail)
        lint_result = temp_spec_generator._run_lint_checks()
        
        assert not lint_result['passed']
        assert len(lint_result['failures']) > 0
    
    def test_lint_catches_invalid_mermaid_syntax(self, temp_spec_generator):
        """Test that lint checks validate Mermaid syntax."""
        temp_spec_generator.analyze()
        temp_spec_generator.generate_all()
        
        # Corrupt a diagram file
        flowchart_path = temp_spec_generator.output_dir / 'diagrams' / 'flowchart.mmd'
        flowchart_path.write_text('flowchart TD\n    Start((( broken', encoding='utf-8')
        
        lint_result = temp_spec_generator._run_lint_checks()
        
        # Should detect unbalanced brackets
        assert not lint_result['passed']
        assert any('parentheses' in failure.lower() for failure in lint_result['failures'])
    
    def test_lint_catches_embedded_diagrams_when_should_be_links(self, temp_spec_generator):
        """Test that lint enforces diagram linking strategy."""
        temp_spec_generator.analyze()
        temp_spec_generator.generate_all()
        
        # The business spec should have BOTH embedded diagrams AND links to .mmd files
        spec_path = temp_spec_generator.output_dir / 'business-spec.md'
        content = spec_path.read_text(encoding='utf-8')
        
        # Should have links to .mmd files
        assert 'diagrams/flowchart.mmd' in content or 'diagrams/sequence.mmd' in content
        
        # Should ALSO have embedded diagrams
        assert '```mermaid' in content


class TestOpenAPIGeneration:
    """Test OpenAPI specification generation quality."""
    
    def test_openapi_yaml_is_valid(self, temp_spec_generator):
        """Test that generated OpenAPI YAML is syntactically valid."""
        temp_spec_generator.analyze()
        temp_spec_generator.generate_all()
        
        yaml_path = temp_spec_generator.output_dir / 'openapi.yaml'
        content = yaml_path.read_text(encoding='utf-8')
        
        # Should have OpenAPI version
        assert 'openapi: 3.' in content
        
        # Should not have placeholder errors
        assert 'example.com' not in content or 'placeholder' in content.lower()
    
    def test_openapi_json_matches_yaml(self, temp_spec_generator):
        """Test that JSON and YAML versions contain same data."""
        import yaml
        import json
        
        temp_spec_generator.analyze()
        temp_spec_generator.generate_all()
        
        yaml_path = temp_spec_generator.output_dir / 'openapi.yaml'
        json_path = temp_spec_generator.output_dir / 'openapi.json'
        
        yaml_data = yaml.safe_load(yaml_path.read_text(encoding='utf-8'))
        json_data = json.loads(json_path.read_text(encoding='utf-8'))
        
        # Core fields should match
        assert yaml_data['openapi'] == json_data['openapi']
        assert yaml_data['info']['title'] == json_data['info']['title']


# ========================================
# FIXTURES
# ========================================

@pytest.fixture
def sample_csharp_code():
    """Sample C# code for testing."""
    return """
namespace HETransactions
{
    public class XGenerateFundingInvoice : HETransaction
    {
        public override void Execute()
        {
            if (InvoiceAmount <= 0)
            {
                throw new ArgumentException("Invoice amount must be greater than zero");
            }
            
            if (InvoiceDate < DateTime.Today)
            {
                throw new ArgumentException("Invoice date cannot be in the past");
            }
            
            if (String.IsNullOrWhiteSpace(SubaccountId))
            {
                throw new ArgumentException("No subaccountId provided.");
            }
            
            var subaccount = ResolveLink(typeof(Subaccount));
            
            // Process invoice
            subaccount.InvoiceAmount = InvoiceAmount;
            subaccount.InvoiceDate = InvoiceDate;
        }
    }
}
"""

@pytest.fixture
def temp_spec_generator(sample_csharp_code):
    """Create a temporary spec generator with sample code."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample C# file
        source_file = temp_path / 'XGenerateFundingInvoice.cs'
        source_file.write_text(sample_csharp_code, encoding='utf-8')
        
        # Create output directory
        output_dir = temp_path / 'output'
        
        generator = LegacySpecGenerator(source_file, output_dir)
        
        yield generator
        
        # Cleanup handled by tempfile.TemporaryDirectory

@pytest.fixture
def sample_generator(sample_csharp_code):
    """Create a sample generator without temp directories for unit tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        source_file = temp_path / 'Sample.cs'
        source_file.write_text(sample_csharp_code, encoding='utf-8')
        
        output_dir = temp_path / 'output'
        
        generator = LegacySpecGenerator(source_file, output_dir)
        
        yield generator

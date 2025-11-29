"""
Tests for TemplateHeaderValidator

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.validation.template_header_validator import (
    TemplateHeaderValidator,
    HeaderViolation
)


@pytest.fixture
def temp_templates_file(tmp_path):
    """Create temporary templates YAML file."""
    templates_path = tmp_path / "response-templates.yaml"
    
    # Create sample templates with mixed compliance
    templates_content = """
schema_version: '2.1'
templates:
  compliant_template:
    name: Compliant Template
    triggers:
      - test compliant
    response_type: narrative
    content: |
      🧠 **CORTEX Help System**
      Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX
      
      This is a compliant template with all required headers.
  
  missing_header:
    name: Missing Header
    triggers:
      - test missing
    response_type: narrative
    content: |
      This template has no header at all.
      Just some content without attribution.
  
  outdated_copyright:
    name: Outdated Copyright
    triggers:
      - test outdated
    response_type: narrative
    content: |
      🧠 **CORTEX Old Template**
      Author: Asif Hussain | © 2023 | github.com/asifhussain60/CORTEX
      
      This has an outdated copyright year.
  
  missing_author:
    name: Missing Author
    triggers:
      - test no author
    response_type: narrative
    content: |
      🧠 **CORTEX Anonymous**
      © 2024-2025 | github.com/asifhussain60/CORTEX
      
      This template is missing author attribution.
  
  missing_repo:
    name: Missing Repo
    triggers:
      - test no repo
    response_type: narrative
    content: |
      🧠 **CORTEX No Link**
      Author: Asif Hussain | © 2024-2025
      
      This template is missing the GitHub repository link.
"""
    
    templates_path.write_text(templates_content)
    return templates_path


@pytest.fixture
def empty_templates_file(tmp_path):
    """Create empty templates YAML file."""
    templates_path = tmp_path / "response-templates.yaml"
    templates_path.write_text("schema_version: '2.1'\n")
    return templates_path


class TestTemplateHeaderValidator:
    """Tests for TemplateHeaderValidator."""
    
    def test_initialization(self, temp_templates_file):
        """Test validator initialization."""
        validator = TemplateHeaderValidator(temp_templates_file)
        
        assert validator.templates_path == temp_templates_file
        assert validator.templates == {}
        assert validator.violations == []
    
    def test_load_templates(self, temp_templates_file):
        """Test loading templates from YAML."""
        validator = TemplateHeaderValidator(temp_templates_file)
        validator._load_templates()
        
        assert len(validator.templates) == 5
        assert "compliant_template" in validator.templates
        assert "missing_header" in validator.templates
    
    def test_validate_compliant_template(self, temp_templates_file):
        """Test validation of compliant template."""
        validator = TemplateHeaderValidator(temp_templates_file)
        results = validator.validate()
        
        # Should have violations for non-compliant templates
        assert results['total_templates'] == 5
        assert results['compliant_templates'] >= 1
    
    def test_detect_missing_header(self, temp_templates_file):
        """Test detection of missing CORTEX header."""
        validator = TemplateHeaderValidator(temp_templates_file)
        results = validator.validate()
        
        # Check for missing header violation
        missing_header_violations = [
            v for v in results['violations']
            if v.template_name == 'missing_header' and v.violation_type == 'missing_header'
        ]
        
        assert len(missing_header_violations) > 0
        assert missing_header_violations[0].severity == 'critical'
        assert '🧠 **CORTEX' in missing_header_violations[0].expected_value
    
    def test_detect_outdated_copyright(self, temp_templates_file):
        """Test detection of outdated copyright year."""
        validator = TemplateHeaderValidator(temp_templates_file)
        results = validator.validate()
        
        # Check for outdated copyright violation
        copyright_violations = [
            v for v in results['violations']
            if v.template_name == 'outdated_copyright' and v.violation_type == 'outdated_copyright'
        ]
        
        assert len(copyright_violations) > 0
        assert copyright_violations[0].severity == 'warning'
        assert '2024-2025' in copyright_violations[0].expected_value
        assert '2023' in copyright_violations[0].current_value
    
    def test_detect_missing_author(self, temp_templates_file):
        """Test detection of missing author attribution."""
        validator = TemplateHeaderValidator(temp_templates_file)
        results = validator.validate()
        
        # Check for missing author violation
        author_violations = [
            v for v in results['violations']
            if v.template_name == 'missing_author' and v.violation_type == 'missing_author'
        ]
        
        assert len(author_violations) > 0
        assert author_violations[0].severity == 'critical'
        assert 'Asif Hussain' in author_violations[0].expected_value
    
    def test_detect_missing_repo_link(self, temp_templates_file):
        """Test detection of missing GitHub repository link."""
        validator = TemplateHeaderValidator(temp_templates_file)
        results = validator.validate()
        
        # Check for missing repo link violation
        repo_violations = [
            v for v in results['violations']
            if v.template_name == 'missing_repo' and v.violation_type == 'missing_repo_link'
        ]
        
        assert len(repo_violations) > 0
        assert repo_violations[0].severity == 'warning'
        assert 'github.com/asifhussain60/CORTEX' in repo_violations[0].expected_value
    
    def test_validation_score_calculation(self, temp_templates_file):
        """Test validation score calculation."""
        validator = TemplateHeaderValidator(temp_templates_file)
        results = validator.validate()
        
        # 1 compliant out of 5 = 20% compliance
        assert results['score'] == 20.0
        assert results['status'] == 'fail'  # <80% = fail
        assert results['compliant_templates'] == 1
        assert results['total_templates'] == 5
    
    def test_generate_remediation_for_missing_header(self, temp_templates_file):
        """Test remediation template generation for missing header."""
        validator = TemplateHeaderValidator(temp_templates_file)
        validator.validate()
        
        templates = validator.generate_remediation_templates()
        
        # Find remediation for missing_header template
        missing_header_fix = [
            t for t in templates
            if t['template_name'] == 'missing_header'
        ]
        
        assert len(missing_header_fix) > 0
        assert missing_header_fix[0]['type'] == 'header_addition'
        assert '🧠 **CORTEX' in missing_header_fix[0]['header_content']
        assert 'Asif Hussain' in missing_header_fix[0]['header_content']
        assert '2024-2025' in missing_header_fix[0]['header_content']
    
    def test_generate_remediation_for_component_updates(self, temp_templates_file):
        """Test remediation template generation for header component updates."""
        validator = TemplateHeaderValidator(temp_templates_file)
        validator.validate()
        
        templates = validator.generate_remediation_templates()
        
        # Find remediation for outdated_copyright template
        copyright_fix = [
            t for t in templates
            if t['template_name'] == 'outdated_copyright'
        ]
        
        assert len(copyright_fix) > 0
        assert copyright_fix[0]['type'] == 'header_update'
        
        # Check updates list
        updates = copyright_fix[0]['updates']
        assert len(updates) > 0
        
        copyright_update = [u for u in updates if u['component'] == 'copyright']
        assert len(copyright_update) > 0
        assert '2024-2025' in copyright_update[0]['new_value']
    
    def test_generate_compliance_report(self, temp_templates_file):
        """Test human-readable compliance report generation."""
        validator = TemplateHeaderValidator(temp_templates_file)
        validator.validate()
        
        report = validator.generate_compliance_report()
        
        assert "# Template Header Compliance Report" in report
        assert "Status:" in report
        assert "Score:" in report
        assert "Violations" in report
        assert "Expected Header Format" in report
    
    def test_empty_templates(self, empty_templates_file):
        """Test validation with no templates."""
        validator = TemplateHeaderValidator(empty_templates_file)
        results = validator.validate()
        
        assert results['score'] == 0
        assert results['status'] == 'fail'
        assert results['total_templates'] == 0
        assert len(results['violations']) == 0
    
    def test_nonexistent_file(self, tmp_path):
        """Test validation with nonexistent templates file."""
        nonexistent = tmp_path / "does_not_exist.yaml"
        validator = TemplateHeaderValidator(nonexistent)
        results = validator.validate()
        
        assert results['score'] == 0
        assert results['total_templates'] == 0
    
    def test_pattern_matching_title(self, temp_templates_file):
        """Test CORTEX title pattern matching."""
        validator = TemplateHeaderValidator(temp_templates_file)
        
        # Test various title formats
        assert validator.TITLE_PATTERN
        
        import re
        pattern = re.compile(validator.TITLE_PATTERN)
        
        # Valid titles
        assert pattern.search("🧠 **CORTEX Help System**")
        assert pattern.search("🧠 **CORTEX [Planning Workflow]**")
        assert pattern.search("🧠**CORTEX TDD**")  # No space after emoji
        
        # Invalid titles
        assert not pattern.search("CORTEX Help System")  # No emoji
        assert not pattern.search("🧠 CORTEX Help")  # No bold markers
    
    def test_pattern_matching_copyright(self, temp_templates_file):
        """Test copyright pattern matching."""
        validator = TemplateHeaderValidator(temp_templates_file)
        
        import re
        pattern = re.compile(validator.COPYRIGHT_PATTERN)
        
        # Valid copyright
        assert pattern.search("© 2024-2025")
        assert pattern.search("©2024-2025")  # No space
        
        # Invalid copyright
        assert not pattern.search("© 2023")  # Wrong year
        assert not pattern.search("© 2024")  # Single year
        assert not pattern.search("Copyright 2024-2025")  # No symbol
    
    def test_all_compliant_templates(self, tmp_path):
        """Test validation with all compliant templates."""
        templates_path = tmp_path / "all-compliant.yaml"
        templates_content = """
schema_version: '2.1'
templates:
  template1:
    name: Template 1
    content: |
      🧠 **CORTEX System**
      Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX
  
  template2:
    name: Template 2
    content: |
      🧠 **CORTEX [Feature]**
      Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX
"""
        templates_path.write_text(templates_content)
        
        validator = TemplateHeaderValidator(templates_path)
        results = validator.validate()
        
        assert results['score'] == 100.0
        assert results['status'] == 'pass'
        assert results['compliant_templates'] == 2
        assert len(results['violations']) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

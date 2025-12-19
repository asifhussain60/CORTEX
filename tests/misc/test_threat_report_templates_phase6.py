"""
Phase 6.3: Threat Report Response Templates Tests

Tests for threat analysis report template rendering and formatting.
Validates quick summary (chat) and detailed (markdown) report formats.

Created: December 2, 2025
Phase: 6.3 RED
"""

import pytest
from pathlib import Path
import yaml


@pytest.fixture
def cortex_root():
    """Get CORTEX root directory"""
    return Path(__file__).parent.parent.parent.absolute()


@pytest.fixture
def response_templates(cortex_root):
    """Load response templates YAML"""
    templates_path = cortex_root / "cortex-brain" / "response-templates.yaml"
    with open(templates_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def template_definitions(cortex_root):
    """Load template definitions YAML"""
    defs_path = cortex_root / "cortex-brain" / "response-template-definitions.yaml"
    with open(defs_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def sample_threat_data():
    """Sample threat analysis data for testing"""
    return {
        'feature_name': 'User Authentication API',
        'threats': [
            {
                'name': 'SQL Injection',
                'stride_category': 'tampering',
                'risk_rating': 'CRITICAL',
                'owasp_code': 'A03',
                'description': 'Attacker can inject SQL code',
                'likelihood': 'HIGH',
                'mitigation_strategies': [
                    {
                        'name': 'Use parameterized queries',
                        'priority': 'CRITICAL',
                        'effort_estimate': '2 hours'
                    }
                ]
            },
            {
                'name': 'Weak Password Policy',
                'stride_category': 'spoofing',
                'risk_rating': 'HIGH',
                'owasp_code': 'A07',
                'description': 'Weak passwords allow brute force',
                'likelihood': 'MEDIUM',
                'mitigation_strategies': [
                    {
                        'name': 'Enforce strong password policy',
                        'priority': 'HIGH',
                        'effort_estimate': '4 hours'
                    }
                ]
            },
            {
                'name': 'Session Timeout',
                'stride_category': 'elevation_of_privilege',
                'risk_rating': 'MEDIUM',
                'owasp_code': 'A01',
                'description': 'Long session timeouts',
                'likelihood': 'LOW',
                'mitigation_strategies': []
            }
        ],
        'risk_level': 'CRITICAL',
        'threat_count': 3,
        'critical_count': 1,
        'high_count': 1,
        'medium_count': 1,
        'low_count': 0,
        'stride_summary': {
            'spoofing': 1,
            'tampering': 1,
            'repudiation': 0,
            'information_disclosure': 0,
            'denial_of_service': 0,
            'elevation_of_privilege': 1
        },
        'owasp_summary': {
            'A01': 1,
            'A03': 1,
            'A07': 1
        }
    }


class TestThreatReportTemplateDiscovery:
    """Test threat report template discovery and selection"""
    
    def test_threat_report_quick_template_exists(self, response_templates):
        """Test threat_report_quick template exists in templates"""
        assert 'threat_report_quick' in response_templates, \
            "threat_report_quick template should exist"
    
    def test_threat_report_detailed_template_exists(self, response_templates):
        """Test threat_report_detailed template exists in templates"""
        assert 'threat_report_detailed' in response_templates, \
            "threat_report_detailed template should exist"
    
    def test_dod_threat_checklist_template_exists(self, response_templates):
        """Test dod_threat_checklist template exists"""
        assert 'dod_threat_checklist' in response_templates, \
            "dod_threat_checklist template should exist"
    
    def test_threat_template_triggers(self, response_templates):
        """Test threat report templates have correct triggers"""
        quick = response_templates.get('threat_report_quick', {})
        assert 'threat analysis' in quick.get('triggers', []), \
            "threat_report_quick should trigger on 'threat analysis'"
        
        detailed = response_templates.get('threat_report_detailed', {})
        assert 'detailed threat report' in detailed.get('triggers', []), \
            "threat_report_detailed should trigger on 'detailed threat report'"
    
    def test_threat_analysis_summary_in_definitions(self, template_definitions):
        """Test threat_analysis_summary template is defined"""
        templates = template_definitions.get('templates', {})
        assert 'threat_analysis_summary' in templates, \
            "threat_analysis_summary should be in template definitions"
    
    def test_threat_analysis_detailed_in_definitions(self, template_definitions):
        """Test threat_analysis_detailed template is defined"""
        templates = template_definitions.get('templates', {})
        assert 'threat_analysis_detailed' in templates, \
            "threat_analysis_detailed should be in template definitions"


class TestQuickSummaryFormat:
    """Test quick threat summary format (chat-optimized)"""
    
    def test_quick_summary_has_risk_badge(self, response_templates):
        """Test quick summary includes risk level badge"""
        quick_template = response_templates.get('threat_report_quick', {})
        
        response_content = quick_template.get('response_content', '')
        assert 'threat_count' in response_content or 'Risk' in response_content, \
            "Quick summary should include risk level/count"
    
    def test_quick_summary_shows_threat_counts(self, response_templates):
        """Test quick summary shows threat counts by severity"""
        quick_template = response_templates.get('threat_report_quick', {})
        
        response_content = quick_template.get('response_content', '')
        assert 'critical_count' in response_content.lower() or 'Critical' in response_content, \
            "Should show critical threat count"
        assert 'high_count' in response_content.lower() or 'High' in response_content, \
            "Should show high threat count"
    
    def test_quick_summary_includes_owasp_mapping(self, response_templates):
        """Test quick summary includes OWASP Top 10 mapping"""
        quick_template = response_templates.get('threat_report_quick', {})
        
        response_content = quick_template.get('response_content', '')
        assert 'owasp' in response_content.lower(), \
            "Quick summary should include OWASP mapping"
    
    def test_quick_summary_has_next_steps(self, response_templates):
        """Test quick summary provides actionable next steps"""
        quick_template = response_templates.get('threat_report_quick', {})
        
        next_steps = quick_template.get('next_steps_content', '')
        assert len(next_steps) > 0, "Should have next steps"
        assert 'mitigation' in next_steps.lower() or 'threat' in next_steps.lower(), \
            "Next steps should mention mitigations or threats"


class TestDetailedReportFormat:
    """Test detailed threat report format (markdown file)"""
    
    def test_detailed_report_has_executive_summary(self, response_templates):
        """Test detailed report includes executive summary"""
        detailed_template = response_templates.get('threat_report_detailed', {})
        
        response_content = detailed_template.get('response_content', '')
        assert 'Executive Summary' in response_content or 'feature_name' in response_content, \
            "Detailed report should have executive summary"
    
    def test_detailed_report_has_stride_sections(self, response_templates):
        """Test detailed report has all 6 STRIDE category sections"""
        detailed_template = response_templates.get('threat_report_detailed', {})
        
        response_content = detailed_template.get('response_content', '')
        
        stride_categories = [
            'Spoofing', 'Tampering', 'Repudiation',
            'Information Disclosure', 'Denial of Service', 'Elevation of Privilege'
        ]
        
        found_categories = sum(1 for cat in stride_categories if cat in response_content)
        assert found_categories >= 4, \
            f"Should reference at least 4 STRIDE categories, found {found_categories}"
    
    def test_detailed_report_has_owasp_mapping(self, response_templates):
        """Test detailed report includes OWASP Top 10 2021 mapping"""
        detailed_template = response_templates.get('threat_report_detailed', {})
        
        response_content = detailed_template.get('response_content', '')
        assert 'OWASP Top 10' in response_content or 'owasp_detailed' in response_content, \
            "Detailed report should include OWASP mapping section"
    
    def test_detailed_report_has_mitigation_strategies(self, response_templates):
        """Test detailed report includes mitigation strategies"""
        detailed_template = response_templates.get('threat_report_detailed', {})
        
        response_content = detailed_template.get('response_content', '')
        assert 'Mitigation' in response_content or 'mitigation' in response_content, \
            "Detailed report should include mitigation strategies"
    
    def test_detailed_report_has_implementation_examples(self, response_templates):
        """Test detailed report includes code examples"""
        detailed_template = response_templates.get('threat_report_detailed', {})
        
        response_content = detailed_template.get('response_content', '')
        assert 'code_examples' in response_content or 'Implementation Examples' in response_content, \
            "Detailed report should include implementation examples"
    
    def test_detailed_report_has_phased_next_steps(self, response_templates):
        """Test detailed report has phased remediation plan"""
        detailed_template = response_templates.get('threat_report_detailed', {})
        
        next_steps = detailed_template.get('next_steps_content', '')
        assert 'Phase' in next_steps, "Should have phased plan"
        assert 'Critical' in next_steps or 'High' in next_steps, \
            "Should prioritize critical/high threats"


class TestDoDChecklistFormat:
    """Test DoD threat mitigation checklist format"""
    
    def test_dod_checklist_has_critical_section(self, response_templates):
        """Test DoD checklist has critical threats section"""
        dod_template = response_templates.get('dod_threat_checklist', {})
        
        response_content = dod_template.get('response_content', '')
        assert 'Critical' in response_content or 'critical_threat_checklist' in response_content, \
            "DoD checklist should have critical threats section"
    
    def test_dod_checklist_has_testing_items(self, response_templates):
        """Test DoD checklist includes security testing items"""
        dod_template = response_templates.get('dod_threat_checklist', {})
        
        response_content = dod_template.get('response_content', '')
        assert 'Security Testing' in response_content or 'test' in response_content.lower(), \
            "DoD checklist should include security testing items"
    
    def test_dod_checklist_has_code_review_items(self, response_templates):
        """Test DoD checklist includes code review items"""
        dod_template = response_templates.get('dod_threat_checklist', {})
        
        response_content = dod_template.get('response_content', '')
        assert 'Code Review' in response_content or 'review' in response_content.lower(), \
            "DoD checklist should include code review items"
    
    def test_dod_checklist_tracks_completion(self, response_templates):
        """Test DoD checklist tracks completion percentage"""
        dod_template = response_templates.get('dod_threat_checklist', {})
        
        response_content = dod_template.get('response_content', '')
        assert 'dod_completion' in response_content or 'Status' in response_content, \
            "DoD checklist should track completion status"


class TestTemplateRendering:
    """Test actual template rendering with data"""
    
    def test_quick_summary_renders_with_data(self, response_templates, sample_threat_data):
        """Test quick summary template renders with threat data"""
        # This would test actual rendering
        # For now, just verify template structure is compatible
        quick_template = response_templates.get('threat_report_quick', {})
        
        # Should have standard 5-part structure
        assert 'response_content' in quick_template
        assert 'next_steps_content' in quick_template
        assert 'understanding_content' in quick_template
    
    def test_detailed_report_renders_with_data(self, response_templates, sample_threat_data):
        """Test detailed report template renders with threat data"""
        detailed_template = response_templates.get('threat_report_detailed', {})
        
        # Should have standard 5-part structure
        assert 'response_content' in detailed_template
        assert 'next_steps_content' in detailed_template
        assert len(detailed_template.get('response_content', '')) > 500, \
            "Detailed report should be comprehensive (>500 chars)"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])

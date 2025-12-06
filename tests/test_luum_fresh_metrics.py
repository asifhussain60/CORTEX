"""
Test Luum-Fresh Dashboard Metrics

Validates that all metrics are correctly collected and can be loaded by the dashboard.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import json
import pytest
from pathlib import Path


class TestLuumFreshMetrics:
    """Test suite for luum-fresh dashboard metrics validation"""
    
    @pytest.fixture
    def luum_data_dir(self):
        """Get luum-fresh data directory"""
        return Path("cortex-brain/dashboards/luum-fresh")
    
    @pytest.fixture
    def metadata(self, luum_data_dir):
        """Load metadata.json"""
        with open(luum_data_dir / "metadata.json") as f:
            return json.load(f)
    
    @pytest.fixture
    def architecture(self, luum_data_dir):
        """Load architecture.json"""
        with open(luum_data_dir / "architecture.json") as f:
            return json.load(f)
    
    @pytest.fixture
    def tech_stack(self, luum_data_dir):
        """Load tech-stack.json"""
        with open(luum_data_dir / "tech-stack.json") as f:
            return json.load(f)
    
    @pytest.fixture
    def code_org(self, luum_data_dir):
        """Load code-organization.json"""
        with open(luum_data_dir / "code-organization.json") as f:
            return json.load(f)
    
    @pytest.fixture
    def security(self, luum_data_dir):
        """Load security.json"""
        with open(luum_data_dir / "security.json") as f:
            return json.load(f)
    
    @pytest.fixture
    def health_data(self, luum_data_dir):
        """Load health-data.json"""
        with open(luum_data_dir / "health-data.json") as f:
            return json.load(f)
    
    def test_metadata_has_required_fields(self, metadata):
        """Test that metadata has all required fields"""
        required_fields = ['app_name', 'app_type', 'last_scan', 'scan_duration_seconds', 'collectors']
        for field in required_fields:
            assert field in metadata, f"Missing required field: {field}"
        
        assert metadata['app_name'] == 'luum-fresh', "Incorrect app_name"
        assert metadata['app_type'] == 'external', "Incorrect app_type"
        assert metadata['collectors'] == 6, "Expected 6 collectors to run"
    
    def test_architecture_detects_ui_components(self, architecture):
        """Test that architecture correctly detects UI components (Razor views, controllers)"""
        # Check application type
        assert 'application_type' in architecture
        app_type = architecture['application_type']
        
        # Check for evidence of UI components
        evidence = app_type.get('evidence', [])
        evidence_text = ' '.join(evidence)
        
        # Should detect Razor views
        assert 'Razor' in evidence_text or 'razor' in evidence_text.lower(), \
            "Razor views not detected in evidence"
        
        # Should detect controllers
        assert 'controller' in evidence_text.lower(), \
            "Controllers not detected in evidence"
        
        # Check tiers
        assert 'tiers' in architecture
        assert len(architecture['tiers']) > 0, "No tiers detected"
        
        # Verify we have significant LOC
        total_loc = sum(tier.get('loc', 0) for tier in architecture['tiers'])
        assert total_loc > 100000, f"Expected >100K LOC, got {total_loc:,}"
    
    def test_tech_stack_has_backend_framework(self, tech_stack):
        """Test that tech stack correctly identifies .NET backend"""
        assert 'backend' in tech_stack
        assert len(tech_stack['backend']) > 0, "No backend frameworks detected"
        
        backend = tech_stack['backend'][0]
        assert backend['name'] == '.NET', "Expected .NET backend"
        assert 'version' in backend
        assert 'metadata' in backend
        
        metadata = backend['metadata']
        assert metadata['project_count'] > 0, "No C# projects detected"
        assert metadata['file_count'] > 1000, f"Expected >1000 C# files, got {metadata['file_count']}"
    
    def test_code_organization_heatmap_has_entries(self, code_org):
        """Test that code organization heatmap has significant entries"""
        assert 'heatmap' in code_org
        assert len(code_org['heatmap']) > 1000, \
            f"Expected >1000 heatmap entries, got {len(code_org['heatmap'])}"
        
        # Check that entries have required fields
        for entry in code_org['heatmap'][:10]:  # Check first 10
            assert 'file' in entry
            assert 'complexity' in entry
            assert 'loc' in entry
            assert 'language' in entry
    
    def test_code_organization_has_ui_files(self, code_org):
        """Test that code organization includes UI-related files"""
        heatmap = code_org['heatmap']
        
        # Count different file types
        cs_files = sum(1 for e in heatmap if e['language'] == 'csharp')
        js_files = sum(1 for e in heatmap if e['language'] == 'javascript')
        
        assert cs_files > 100, f"Expected >100 C# files, got {cs_files}"
        assert js_files > 0, f"Expected some JavaScript files, got {js_files}"
        
        # Check for controllers in file paths
        controller_files = [e for e in heatmap if 'controller' in e['file'].lower()]
        assert len(controller_files) > 10, \
            f"Expected >10 controller files, got {len(controller_files)}"
    
    def test_security_has_vulnerability_counts(self, security):
        """Test that security analysis has vulnerability data"""
        assert 'vulnerabilities' in security
        vulns = security['vulnerabilities']
        
        required_levels = ['critical', 'high', 'medium', 'low']
        for level in required_levels:
            assert level in vulns, f"Missing vulnerability level: {level}"
        
        # Check that we have security scan results
        assert 'last_scan' in security
        assert 'overall_score' in security
    
    def test_health_data_has_metrics(self, health_data):
        """Test that health data has required metrics"""
        required_fields = ['overall_health_score', 'status', 'security_score', 'security_issues']
        
        for field in required_fields:
            assert field in health_data, f"Missing health field: {field}"
        
        # Verify overall health score is a number
        assert isinstance(health_data['overall_health_score'], (int, float))
        assert 0 <= health_data['overall_health_score'] <= 100
    
    def test_all_json_files_are_valid(self, luum_data_dir):
        """Test that all JSON files in luum-fresh directory are valid"""
        json_files = list(luum_data_dir.glob("*.json"))
        assert len(json_files) >= 8, f"Expected at least 8 JSON files, found {len(json_files)}"
        
        for json_file in json_files:
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    assert isinstance(data, dict), f"{json_file.name} should contain a JSON object"
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {json_file.name}: {e}")
    
    def test_metrics_are_dashboard_compatible(self, architecture, tech_stack, code_org, security):
        """Test that metrics are in the format expected by the dashboard UI"""
        # Architecture should have tiers array
        assert isinstance(architecture.get('tiers'), list)
        
        # Tech stack should have categorized technologies
        assert isinstance(tech_stack.get('backend'), list)
        
        # Code org should have heatmap array
        assert isinstance(code_org.get('heatmap'), list)
        
        # Security should have vulnerability object
        assert isinstance(security.get('vulnerabilities'), dict)
    
    def test_ui_component_counts(self, architecture):
        """Test that UI component counts are reasonable for an MVC application"""
        evidence = architecture['application_type'].get('evidence', [])
        evidence_text = ' '.join(evidence)
        
        # Extract Razor view count from evidence
        import re
        razor_match = re.search(r'(\d+)\s+Razor views', evidence_text)
        if razor_match:
            razor_count = int(razor_match.group(1))
            assert razor_count > 100, \
                f"Expected >100 Razor views for MVC app, got {razor_count}"
        
        # Extract controller count
        controller_match = re.search(r'(\d+)\s+API controllers', evidence_text)
        if controller_match:
            controller_count = int(controller_match.group(1))
            assert controller_count > 10, \
                f"Expected >10 controllers for MVC app, got {controller_count}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

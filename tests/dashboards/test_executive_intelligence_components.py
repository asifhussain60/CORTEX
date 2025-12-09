"""
Tests for Executive Intelligence Dashboard Components

Tests the Phase 2 intelligence integration with dashboard visualization.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import json
from pathlib import Path


class TestExecutiveIntelligenceData:
    """Test executive intelligence data structure and validation."""
    
    def test_mock_data_exists(self):
        """Mock executive intelligence data file exists."""
        data_path = Path('cortex-brain/dashboards/data/repos/mock/executive-intelligence.json')
        assert data_path.exists(), "executive-intelligence.json must exist"
    
    def test_mock_data_valid_json(self):
        """Mock data is valid JSON."""
        data_path = Path('cortex-brain/dashboards/data/repos/mock/executive-intelligence.json')
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert isinstance(data, dict)
    
    def test_mock_data_required_fields(self):
        """Mock data contains all required fields."""
        data_path = Path('cortex-brain/dashboards/data/repos/mock/executive-intelligence.json')
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_fields = [
            'repo_name', 'repo_path', 'title', 'description',
            'has_readme', 'has_git_history', 'summary_quality_score'
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_quality_score_range(self):
        """Quality score is within valid range (0-10)."""
        data_path = Path('cortex-brain/dashboards/data/repos/mock/executive-intelligence.json')
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        score = data.get('summary_quality_score', 0)
        assert 0 <= score <= 10, f"Quality score {score} out of range"
    
    def test_domains_list(self):
        """Primary domains is a list."""
        data_path = Path('cortex-brain/dashboards/data/repos/mock/executive-intelligence.json')
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        domains = data.get('primary_domains', [])
        assert isinstance(domains, list)
        assert len(domains) > 0, "Should have at least one domain"
    
    def test_capabilities_list(self):
        """Capabilities is a list with items."""
        data_path = Path('cortex-brain/dashboards/data/repos/mock/executive-intelligence.json')
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        capabilities = data.get('capabilities', [])
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0, "Should have capabilities"
    
    def test_features_list(self):
        """Features is a list with items."""
        data_path = Path('cortex-brain/dashboards/data/repos/mock/executive-intelligence.json')
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        features = data.get('features', [])
        assert isinstance(features, list)
        assert len(features) > 0, "Should have features"
    
    def test_technologies_list(self):
        """Technologies is a list."""
        data_path = Path('cortex-brain/dashboards/data/repos/mock/executive-intelligence.json')
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tech = data.get('technologies', [])
        assert isinstance(tech, list)
    
    def test_velocity_metrics(self):
        """Recent velocity contains expected metrics."""
        data_path = Path('cortex-brain/dashboards/data/repos/mock/executive-intelligence.json')
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        velocity = data.get('recent_velocity', {})
        
        if velocity:
            assert 'total_commits' in velocity
            assert 'commits_per_day' in velocity
            assert velocity['total_commits'] >= 0
            assert velocity['commits_per_day'] >= 0


class TestDashboardComponentFiles:
    """Test dashboard component files exist and are properly structured."""
    
    def test_intelligence_panel_component_exists(self):
        """Executive intelligence panel component exists."""
        component_path = Path('cortex-brain/dashboards/ui/components/executive-intelligence-panel.js')
        assert component_path.exists(), "executive-intelligence-panel.js must exist"
    
    def test_intelligence_loader_exists(self):
        """Executive intelligence loader service exists."""
        loader_path = Path('cortex-brain/dashboards/ui/services/executive-intelligence-loader.js')
        assert loader_path.exists(), "executive-intelligence-loader.js must exist"
    
    def test_intelligence_panel_exports_function(self):
        """Intelligence panel exports renderExecutiveIntelligencePanel."""
        component_path = Path('cortex-brain/dashboards/ui/components/executive-intelligence-panel.js')
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'export function renderExecutiveIntelligencePanel' in content
    
    def test_loader_exports_functions(self):
        """Intelligence loader exports required functions."""
        loader_path = Path('cortex-brain/dashboards/ui/services/executive-intelligence-loader.js')
        
        with open(loader_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'export async function loadExecutiveIntelligence' in content
        assert 'export function generateMockIntelligence' in content
        assert 'export function integrateIntelligence' in content
    
    def test_executive_tab_imports_intelligence_panel(self):
        """Executive tab imports intelligence panel component."""
        tab_path = Path('cortex-brain/dashboards/ui/components/executive-tab.js')
        
        with open(tab_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'executive-intelligence-panel.js' in content
        assert 'renderExecutiveIntelligencePanel' in content
    
    def test_data_loader_includes_intelligence_file(self):
        """Data loader includes executive-intelligence.json in DATA_FILES."""
        loader_path = Path('cortex-brain/dashboards/ui/data-loader.js')
        
        with open(loader_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'executive-intelligence.json' in content
        assert 'executiveIntelligence' in content


class TestComponentIntegration:
    """Test component integration and data flow."""
    
    def test_intelligence_panel_handles_null_data(self):
        """Intelligence panel component handles null data gracefully."""
        component_path = Path('cortex-brain/dashboards/ui/components/executive-intelligence-panel.js')
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have null check
        assert 'if (!intelligenceSummary' in content or 'if (!summary' in content
        assert 'renderNoDataState' in content
    
    def test_quality_indicator_rendering(self):
        """Quality indicator section exists in component."""
        component_path = Path('cortex-brain/dashboards/ui/components/executive-intelligence-panel.js')
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'renderQualityIndicator' in content
        assert 'summary_quality_score' in content
    
    def test_business_context_rendering(self):
        """Business context section exists in component."""
        component_path = Path('cortex-brain/dashboards/ui/components/executive-intelligence-panel.js')
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'renderBusinessContext' in content
        assert 'primary_domains' in content
        assert 'capabilities' in content
    
    def test_development_insights_rendering(self):
        """Development insights section exists in component."""
        component_path = Path('cortex-brain/dashboards/ui/components/executive-intelligence-panel.js')
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'renderDevelopmentInsights' in content
        assert 'development_focus' in content
        assert 'recent_velocity' in content
    
    def test_xss_protection(self):
        """Component includes XSS protection via escapeHtml."""
        component_path = Path('cortex-brain/dashboards/ui/components/executive-intelligence-panel.js')
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'escapeHtml' in content
        assert 'textContent' in content  # Used in escapeHtml implementation


class TestDataQuality:
    """Test data quality and completeness."""
    
    def test_mock_data_richness(self):
        """Mock data demonstrates rich intelligence (score >= 8)."""
        data_path = Path('cortex-brain/dashboards/data/repos/mock/executive-intelligence.json')
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        score = data.get('summary_quality_score', 0)
        assert score >= 8.0, f"Mock data should demonstrate high quality (score {score} < 8.0)"
    
    def test_mock_data_has_all_sources(self):
        """Mock data has all intelligence sources enabled."""
        data_path = Path('cortex-brain/dashboards/data/repos/mock/executive-intelligence.json')
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data.get('has_readme') is True
        assert data.get('has_git_history') is True
        assert len(data.get('primary_domains', [])) > 0
    
    def test_mock_data_realistic_metrics(self):
        """Mock data contains realistic metrics."""
        data_path = Path('cortex-brain/dashboards/data/repos/mock/executive-intelligence.json')
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        velocity = data.get('recent_velocity', {})
        
        if velocity:
            # Realistic ranges
            assert velocity.get('total_commits', 0) > 0
            assert 0 <= velocity.get('commits_per_day', 0) <= 100
            assert velocity.get('features_completed', 0) >= 0
            assert velocity.get('bugs_fixed', 0) >= 0

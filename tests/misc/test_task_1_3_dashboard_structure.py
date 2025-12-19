"""
Task 1.3: 5-Tab Dashboard Structure Tests

Tests for dashboard.html master template and tab navigation system.
Validates:
- All 5 tabs present (Overview, Architecture, Health, Metrics, Reports)
- Tab navigation functionality
- Active state management
- Tab content switching
- CSS file existence
- JavaScript file existence
"""

import pytest
from pathlib import Path


class TestDashboardStructure:
    """Test dashboard.html master template structure"""
    
    @pytest.fixture
    def dashboard_path(self):
        return Path(__file__).parent.parent / "src" / "dashboard" / "presentation" / "templates" / "dashboard.html"
    
    @pytest.fixture
    def dashboard_content(self, dashboard_path):
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_dashboard_file_exists(self, dashboard_path):
        """Verify dashboard.html exists"""
        assert dashboard_path.exists(), f"Dashboard template not found: {dashboard_path}"
    
    def test_html_structure(self, dashboard_content):
        """Verify basic HTML structure"""
        assert '<!DOCTYPE html>' in dashboard_content
        assert '<html' in dashboard_content
        assert '<head>' in dashboard_content
        assert '<body>' in dashboard_content
        assert '</html>' in dashboard_content
    
    def test_all_tabs_present(self, dashboard_content):
        """Verify all 5 tabs are present in navigation"""
        required_tabs = ['overview', 'architecture', 'health', 'metrics', 'reports']
        
        for tab in required_tabs:
            # Check tab link
            assert f'data-tab="{tab}"' in dashboard_content, f"Tab link missing: {tab}"
            
            # Check tab content container
            assert f'data-tab-content="{tab}"' in dashboard_content, f"Tab content missing: {tab}"
    
    def test_tab_icons(self, dashboard_content):
        """Verify tab icons are present"""
        tab_icons = {
            'overview': '📊',
            'architecture': '🏛️',
            'health': '❤️',
            'metrics': '📈',
            'reports': '📄'
        }
        
        for tab, icon in tab_icons.items():
            assert icon in dashboard_content, f"Icon missing for {tab} tab: {icon}"
    
    def test_tab_labels(self, dashboard_content):
        """Verify tab labels are present"""
        tab_labels = ['Overview', 'Architecture', 'Health', 'Metrics', 'Reports']
        
        for label in tab_labels:
            assert label in dashboard_content, f"Tab label missing: {label}"
    
    def test_header_present(self, dashboard_content):
        """Verify dashboard header exists"""
        assert 'dashboard-header' in dashboard_content
        assert 'CORTEX Application Dashboard 2.0' in dashboard_content or 'CORTEX' in dashboard_content
    
    def test_navigation_structure(self, dashboard_content):
        """Verify tab navigation structure"""
        assert '<nav class="tab-navigation"' in dashboard_content
        assert '<ul class="tab-list"' in dashboard_content
        assert 'tab-item' in dashboard_content
        assert 'tab-link' in dashboard_content
    
    def test_active_state_markup(self, dashboard_content):
        """Verify active state classes exist"""
        # Overview should be active by default
        assert 'class="tab-link active"' in dashboard_content or 'active' in dashboard_content
        assert 'class="tab-content active"' in dashboard_content or 'active' in dashboard_content


class TestTabContent:
    """Test individual tab content sections"""
    
    @pytest.fixture
    def dashboard_path(self):
        return Path(__file__).parent.parent / "src" / "dashboard" / "presentation" / "templates" / "dashboard.html"
    
    @pytest.fixture
    def dashboard_content(self, dashboard_path):
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_overview_tab_content(self, dashboard_content):
        """Verify overview tab contains required elements"""
        # Stats grid
        assert 'stats-grid' in dashboard_content
        assert 'total-files' in dashboard_content
        assert 'total-components' in dashboard_content
        assert 'overall-health' in dashboard_content
        
        # System status
        assert 'system-status' in dashboard_content
        
        # Top issues
        assert 'top-issues' in dashboard_content
        
        # Quick actions
        assert 'quick-actions' in dashboard_content
    
    def test_architecture_tab_content(self, dashboard_content):
        """Verify architecture tab contains required elements"""
        # Controls
        assert 'controls-panel' in dashboard_content or 'control' in dashboard_content
        
        # Graph container
        assert 'architecture-graph-container' in dashboard_content or 'graph-container' in dashboard_content
        
        # D3.js dependency
        assert 'd3.js' in dashboard_content or 'd3.v7' in dashboard_content
    
    def test_health_tab_content(self, dashboard_content):
        """Verify health tab contains placeholder structure"""
        assert 'health-container' in dashboard_content
        assert 'health-overview' in dashboard_content or 'health' in dashboard_content
    
    def test_metrics_tab_content(self, dashboard_content):
        """Verify metrics tab contains placeholder structure"""
        assert 'metrics-container' in dashboard_content
        assert 'metrics' in dashboard_content
    
    def test_reports_tab_content(self, dashboard_content):
        """Verify reports tab contains placeholder structure"""
        assert 'reports-container' in dashboard_content
        assert 'report' in dashboard_content


class TestCSSFiles:
    """Test CSS file existence"""
    
    @pytest.fixture
    def css_dir(self):
        return Path(__file__).parent.parent / "src" / "dashboard" / "presentation" / "static" / "css"
    
    def test_dashboard_css_exists(self, css_dir):
        """Verify dashboard.css exists"""
        css_file = css_dir / "dashboard.css"
        assert css_file.exists(), f"Main dashboard CSS not found: {css_file}"
    
    def test_architecture_tab_css_exists(self, css_dir):
        """Verify architecture_tab.css exists"""
        css_file = css_dir / "architecture_tab.css"
        assert css_file.exists(), f"Architecture tab CSS not found: {css_file}"
    
    def test_overview_tab_css_exists(self, css_dir):
        """Verify overview_tab.css exists"""
        css_file = css_dir / "overview_tab.css"
        assert css_file.exists(), f"Overview tab CSS not found: {css_file}"
    
    def test_health_tab_css_exists(self, css_dir):
        """Verify health_tab.css exists"""
        css_file = css_dir / "health_tab.css"
        assert css_file.exists(), f"Health tab CSS not found: {css_file}"
    
    def test_metrics_tab_css_exists(self, css_dir):
        """Verify metrics_tab.css exists"""
        css_file = css_dir / "metrics_tab.css"
        assert css_file.exists(), f"Metrics tab CSS not found: {css_file}"
    
    def test_reports_tab_css_exists(self, css_dir):
        """Verify reports_tab.css exists"""
        css_file = css_dir / "reports_tab.css"
        assert css_file.exists(), f"Reports tab CSS not found: {css_file}"


class TestJavaScriptFiles:
    """Test JavaScript file existence"""
    
    @pytest.fixture
    def js_dir(self):
        return Path(__file__).parent.parent / "src" / "dashboard" / "presentation" / "static" / "js"
    
    def test_dashboard_js_exists(self, js_dir):
        """Verify dashboard.js exists"""
        js_file = js_dir / "dashboard.js"
        assert js_file.exists(), f"Main dashboard JS not found: {js_file}"
    
    def test_architecture_tab_js_exists(self, js_dir):
        """Verify architecture_tab.js exists"""
        js_file = js_dir / "architecture_tab.js"
        assert js_file.exists(), f"Architecture tab JS not found: {js_file}"
    
    def test_overview_tab_js_exists(self, js_dir):
        """Verify overview_tab.js exists"""
        js_file = js_dir / "overview_tab.js"
        assert js_file.exists(), f"Overview tab JS not found: {js_file}"
    
    def test_health_tab_js_exists(self, js_dir):
        """Verify health_tab.js exists"""
        js_file = js_dir / "health_tab.js"
        assert js_file.exists(), f"Health tab JS not found: {js_file}"
    
    def test_metrics_tab_js_exists(self, js_dir):
        """Verify metrics_tab.js exists"""
        js_file = js_dir / "metrics_tab.js"
        assert js_file.exists(), f"Metrics tab JS not found: {js_file}"
    
    def test_reports_tab_js_exists(self, js_dir):
        """Verify reports_tab.js exists"""
        js_file = js_dir / "reports_tab.js"
        assert js_file.exists(), f"Reports tab JS not found: {js_file}"


class TestDashboardJavaScript:
    """Test dashboard.js functionality"""
    
    @pytest.fixture
    def js_path(self):
        return Path(__file__).parent.parent / "src" / "dashboard" / "presentation" / "static" / "js" / "dashboard.js"
    
    @pytest.fixture
    def js_content(self, js_path):
        with open(js_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_dashboard_controller_class(self, js_content):
        """Verify DashboardController class exists"""
        assert 'class DashboardController' in js_content
        assert 'constructor()' in js_content
    
    def test_tab_navigation_method(self, js_content):
        """Verify tab navigation method exists"""
        assert 'setupTabNavigation' in js_content or 'switchTab' in js_content
    
    def test_all_tabs_defined(self, js_content):
        """Verify all 5 tabs are defined in JavaScript"""
        assert "'overview'" in js_content or '"overview"' in js_content
        assert "'architecture'" in js_content or '"architecture"' in js_content
        assert "'health'" in js_content or '"health"' in js_content
        assert "'metrics'" in js_content or '"metrics"' in js_content
        assert "'reports'" in js_content or '"reports"' in js_content
    
    def test_active_state_management(self, js_content):
        """Verify active state management logic exists"""
        assert 'classList.add' in js_content and 'active' in js_content
        assert 'classList.remove' in js_content
    
    def test_data_loading(self, js_content):
        """Verify data loading mechanism exists"""
        assert 'loadData' in js_content or 'fetch' in js_content
    
    def test_url_hash_handling(self, js_content):
        """Verify URL hash handling for direct tab access"""
        assert 'location.hash' in js_content or 'hashchange' in js_content


class TestAcceptanceCriteria:
    """Validate acceptance criteria from planning document"""
    
    @pytest.fixture
    def dashboard_path(self):
        return Path(__file__).parent.parent / "src" / "dashboard" / "presentation" / "templates" / "dashboard.html"
    
    @pytest.fixture
    def dashboard_content(self, dashboard_path):
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @pytest.fixture
    def js_path(self):
        return Path(__file__).parent.parent / "src" / "dashboard" / "presentation" / "static" / "js" / "dashboard.js"
    
    @pytest.fixture
    def js_content(self, js_path):
        with open(js_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_ac1_five_tabs_present(self, dashboard_content):
        """AC1: All 5 tabs (Overview, Architecture, Health, Metrics, Reports) present"""
        tabs = ['overview', 'architecture', 'health', 'metrics', 'reports']
        for tab in tabs:
            assert f'data-tab="{tab}"' in dashboard_content
    
    def test_ac2_tab_navigation(self, js_content):
        """AC2: Tab navigation system implemented"""
        assert 'switchTab' in js_content or 'tab-link' in js_content
        assert 'addEventListener' in js_content
    
    def test_ac3_active_state_management(self, js_content):
        """AC3: Active state management with classList operations"""
        assert 'classList.add' in js_content
        assert 'classList.remove' in js_content
        assert "'active'" in js_content or '"active"' in js_content
    
    def test_ac4_master_template(self, dashboard_content):
        """AC4: Master template dashboard.html created"""
        assert '<!DOCTYPE html>' in dashboard_content
        assert 'dashboard' in dashboard_content.lower()
    
    def test_ac5_tab_styling(self, dashboard_content):
        """AC5: Tab navigation styled with CSS"""
        # Verify CSS file is linked
        assert 'dashboard.css' in dashboard_content
        
        # Verify tab-related CSS classes
        assert 'tab-navigation' in dashboard_content or 'tab-list' in dashboard_content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

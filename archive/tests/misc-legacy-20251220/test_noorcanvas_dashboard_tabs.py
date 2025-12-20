"""
Test suite for NOOR-CANVAS dashboard tab lazy initialization.
Tests that tabs initialize only when switched to, not on page load.

TDD Phase: RED
"""
from pathlib import Path
import re
import pytest


class TestDashboardTabLazyInitialization:
    """Test that dashboard tabs use lazy initialization pattern"""
    
    @pytest.fixture
    def dashboard_path(self):
        """Path to NOOR-CANVAS dashboard"""
        return Path("d:/PROJECTS/CORTEX/cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html")
    
    @pytest.fixture
    def dashboard_html(self, dashboard_path):
        """Load dashboard HTML content"""
        assert dashboard_path.exists(), f"Dashboard not found at {dashboard_path}"
        return dashboard_path.read_text(encoding='utf-8')
    
    def test_dashboard_has_7_tabs(self, dashboard_html):
        """
        RED TEST: Verify dashboard has exactly 7 tabs
        Expected tabs: overview, techstack, architecture, security, uml, recommendations, data
        """
        tab_buttons = re.findall(r'data-tab="(\w+)"', dashboard_html)
        assert len(tab_buttons) == 7, f"Expected 7 tabs, found {len(tab_buttons)}: {tab_buttons}"
        
        expected_tabs = ['overview', 'techstack', 'architecture', 'security', 'uml', 'recommendations', 'data']
        assert tab_buttons == expected_tabs, f"Tab order mismatch. Expected {expected_tabs}, got {tab_buttons}"
    
    def test_switchTab_function_handles_all_tabs(self, dashboard_html):
        """
        RED TEST: Verify switchTab function has initialization logic for all 7 tabs
        Each tab should have conditional initialization with a flag like 'window.tabNameInitialized'
        """
        # Find switchTab function
        switch_tab_match = re.search(r'function switchTab\(tabName\)\s*\{(.*?)(?=\n\s*function|\n\s*window\.addEventListener)', 
                                     dashboard_html, re.DOTALL)
        assert switch_tab_match, "switchTab function not found"
        
        switch_tab_body = switch_tab_match.group(1)
        
        # Check for initialization conditions for each non-overview tab
        required_tabs = ['techstack', 'architecture', 'security', 'uml', 'recommendations', 'data']
        
        for tab in required_tabs:
            # Look for pattern: if (tabName === 'tabname' && !window.tabnameInitialized)
            pattern = rf"tabName === ['\"]?{tab}['\"]?.*?window\.{tab}Initialized"
            assert re.search(pattern, switch_tab_body, re.IGNORECASE), \
                f"switchTab missing lazy initialization check for '{tab}' tab"
    
    def test_dom_content_loaded_only_initializes_overview(self, dashboard_html):
        """
        RED TEST: Verify DOMContentLoaded only initializes Overview tab
        Other tabs should NOT be initialized on page load to enable lazy loading
        """
        # Find DOMContentLoaded handler
        dom_ready_match = re.search(r"window\.addEventListener\(['\"]DOMContentLoaded['\"].*?\{(.*?)\}\);", 
                                   dashboard_html, re.DOTALL)
        assert dom_ready_match, "DOMContentLoaded handler not found"
        
        dom_ready_body = dom_ready_match.group(1)
        
        # Overview should be initialized
        assert 'initializeOverview()' in dom_ready_body, \
            "Overview tab should be initialized on page load"
        
        # Other tabs should NOT be initialized on page load
        unwanted_initializations = [
            'initializeTechStack()',
            'initializeArchitecture()',
            'initializeSecurity()',
            'initializeUml()',
            'initializeRecommendations()',
            'initializeDataTable()'
        ]
        
        for init_call in unwanted_initializations:
            assert init_call not in dom_ready_body, \
                f"{init_call} should NOT be called on page load (breaks lazy loading)"
    
    def test_all_tabs_have_initialization_functions(self, dashboard_html):
        """
        RED TEST: Verify all 7 tabs have corresponding initialization functions defined
        """
        required_functions = [
            'initializeOverview',
            'initializeTechStack',
            'initializeArchitecture',
            'initializeSecurity',
            'initializeUml',
            'initializeRecommendations',
            'initializeDataTable'
        ]
        
        for func_name in required_functions:
            pattern = rf'function {func_name}\s*\('
            assert re.search(pattern, dashboard_html), \
                f"Missing initialization function: {func_name}()"
    
    def test_each_tab_content_div_exists(self, dashboard_html):
        """
        RED TEST: Verify each tab has a corresponding content div with correct ID
        """
        expected_tab_divs = [
            'overview-tab',
            'techstack-tab',
            'architecture-tab',
            'security-tab',
            'uml-tab',
            'recommendations-tab',
            'data-tab'
        ]
        
        for tab_id in expected_tab_divs:
            pattern = rf'<div[^>]*id="{tab_id}"[^>]*>'
            assert re.search(pattern, dashboard_html), \
                f"Missing tab content div: {tab_id}"
    
    def test_tabs_use_correct_initialization_flag_naming(self, dashboard_html):
        """
        RED TEST: Verify initialization flags follow consistent naming convention
        Expected: window.techstackInitialized, window.architectureInitialized, etc.
        """
        expected_flags = [
            'techstackInitialized',
            'architectureInitialized',
            'securityInitialized',
            'umlInitialized',
            'recommendationsInitialized',
            'dataInitialized'
        ]
        
        # At least some flags should exist in switchTab
        switch_tab_match = re.search(r'function switchTab\(tabName\)\s*\{(.*?)(?=\n\s*function|\n\s*window\.addEventListener)', 
                                     dashboard_html, re.DOTALL)
        
        if switch_tab_match:
            switch_tab_body = switch_tab_match.group(1)
            flags_found = sum(1 for flag in expected_flags if flag in switch_tab_body)
            
            # This test expects all 6 flags to be present for lazy initialization (overview excluded)
            assert flags_found >= 6, \
                f"Expected 6 initialization flags in switchTab, found {flags_found}"


class TestDashboardTabDataBinding:
    """Test that tab initialization functions correctly bind data"""
    
    @pytest.fixture
    def dashboard_path(self):
        return Path("d:/PROJECTS/CORTEX/cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html")
    
    @pytest.fixture
    def dashboard_html(self, dashboard_path):
        assert dashboard_path.exists()
        return dashboard_path.read_text(encoding='utf-8')
    
    def test_techstack_binds_to_dashboardData_techstack(self, dashboard_html):
        """RED TEST: Verify initializeTechStack accesses dashboardData.techstack"""
        init_func = re.search(r'function initializeTechStack\(\)\s*\{(.*?)(?=\n\s*function)', 
                             dashboard_html, re.DOTALL)
        assert init_func, "initializeTechStack function not found"
        
        func_body = init_func.group(1)
        assert 'dashboardData.techstack' in func_body, \
            "initializeTechStack should access dashboardData.techstack"
    
    def test_architecture_binds_to_dashboardData_architecture(self, dashboard_html):
        """RED TEST: Verify initializeArchitecture accesses dashboardData.architecture"""
        init_func = re.search(r'function initializeArchitecture\(\)\s*\{(.*?)(?=\n\s*function)', 
                             dashboard_html, re.DOTALL)
        assert init_func, "initializeArchitecture function not found"
        
        func_body = init_func.group(1)
        assert 'dashboardData.architecture' in func_body, \
            "initializeArchitecture should access dashboardData.architecture"
    
    def test_security_binds_to_dashboardData_security(self, dashboard_html):
        """RED TEST: Verify initializeSecurity accesses dashboardData.security"""
        init_func = re.search(r'function initializeSecurity\(\)\s*\{(.*?)(?=\n\s*function)', 
                             dashboard_html, re.DOTALL)
        assert init_func, "initializeSecurity function not found"
        
        func_body = init_func.group(1)
        assert 'dashboardData.security' in func_body, \
            "initializeSecurity should access dashboardData.security"
    
    def test_recommendations_binds_to_dashboardData_recommendations(self, dashboard_html):
        """RED TEST: Verify initializeRecommendations accesses dashboardData.recommendations"""
        init_func = re.search(r'function initializeRecommendations\(\)\s*\{(.*?)(?=\n\s*(?:function|window\.addEventListener|</script>))', 
                             dashboard_html, re.DOTALL)
        assert init_func, "initializeRecommendations function not found"
        
        func_body = init_func.group(1)
        assert 'dashboardData.recommendations' in func_body, \
            "initializeRecommendations should access dashboardData.recommendations"
    
    def test_data_table_binds_to_dashboardData_dataTable(self, dashboard_html):
        """RED TEST: Verify initializeDataTable accesses dashboardData.dataTable"""
        init_func = re.search(r'function initializeDataTable\(\)\s*\{(.*?)(?=\n\s*function)', 
                             dashboard_html, re.DOTALL)
        assert init_func, "initializeDataTable function not found"
        
        func_body = init_func.group(1)
        assert 'dashboardData.dataTable' in func_body, \
            "initializeDataTable should access dashboardData.dataTable"

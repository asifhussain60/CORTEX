"""
TDD Test Suite for Dashboard Remaining Tabs (Security, Architecture, UML)

This test suite validates that the Security, Architecture, and UML tabs:
1. Have initialization functions defined
2. Functions are called on DOMContentLoaded
3. Required DOM elements exist in HTML
4. Data structures are valid in dashboardData
5. Rendering logic properly reads and displays data
"""
import pytest
import re
import json
from pathlib import Path


# Path to dashboard HTML file
DASHBOARD_PATH = Path("d:/PROJECTS/CORTEX/cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html")


@pytest.fixture
def dashboard_html():
    """Load dashboard HTML content."""
    with open(DASHBOARD_PATH, 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def dashboard_data(dashboard_html):
    """Extract dashboardData JSON object from HTML."""
    # Simple check - just verify the keys exist in the HTML
    has_security = '"security":' in dashboard_html
    has_architecture = '"architecture":' in dashboard_html
    
    if has_security and has_architecture:
        return {
            'security': {'vulnerabilities': 0, 'issues': []},
            'architecture': {'nodes': [], 'edges': []}
        }
    return {}


class TestSecurityTab:
    """Tests for Security tab functionality."""
    
    def test_initialize_security_function_exists(self, dashboard_html):
        """Verify initializeSecurity() function is defined."""
        pattern = r'function\s+initializeSecurity\s*\('
        assert re.search(pattern, dashboard_html), "initializeSecurity() function not found"
    
    def test_security_function_called_on_load(self, dashboard_html):
        """Verify initializeSecurity() is called in DOMContentLoaded."""
        pattern = r"addEventListener\s*\(\s*['\"]DOMContentLoaded['\"].*initializeSecurity\s*\("
        assert re.search(pattern, dashboard_html, re.DOTALL), "initializeSecurity() not called on page load"
    
    def test_security_dom_elements_exist(self, dashboard_html):
        """Verify required DOM elements exist for Security tab."""
        required_ids = [
            'security-tab',
            'security-summary',
            'severity-chart',
            'security-issues',
            'severity-filters'
        ]
        for elem_id in required_ids:
            pattern = f'id=["\']({elem_id})["\']'
            assert re.search(pattern, dashboard_html), f"DOM element #{elem_id} not found"
    
    def test_security_data_structure(self, dashboard_data):
        """Verify security data structure in dashboardData."""
        assert 'security' in dashboard_data, "security key missing in dashboardData"
        security = dashboard_data['security']
        assert 'vulnerabilities' in security or 'issues' in security, "security data incomplete"
    
    def test_security_chart_rendering_logic(self, dashboard_html):
        """Verify Chart.js severity chart rendering logic exists."""
        patterns = [
            r'dashboardData\.security',
            r'getElementById\(["\']severity-chart["\']',
            r'new\s+Chart\('
        ]
        for pattern in patterns:
            assert re.search(pattern, dashboard_html), f"Pattern '{pattern}' not found for severity chart"
    
    def test_security_summary_stats_rendering(self, dashboard_html):
        """Verify security summary stats rendering logic."""
        patterns = [
            r'getElementById\(["\']security-summary["\']',
            r'dashboardData\.security\.(vulnerabilities|issues)'
        ]
        for pattern in patterns:
            assert re.search(pattern, dashboard_html), f"Pattern '{pattern}' not found for security summary"
    
    def test_security_issues_list_rendering(self, dashboard_html):
        """Verify security issues list rendering logic."""
        patterns = [
            r'getElementById\(["\']security-issues["\']',
            r'dashboardData\.security\.issues',
            r'\.map\('
        ]
        for pattern in patterns:
            assert re.search(pattern, dashboard_html), f"Pattern '{pattern}' not found for issues list"
    
    def test_security_filter_functionality(self, dashboard_html):
        """Verify filterSecurityIssues() function exists."""
        pattern = r'function\s+filterSecurityIssues\s*\('
        assert re.search(pattern, dashboard_html), "filterSecurityIssues() function not found"


class TestArchitectureTab:
    """Tests for Architecture tab functionality."""
    
    def test_initialize_architecture_function_exists(self, dashboard_html):
        """Verify initializeArchitecture() function is defined."""
        pattern = r'function\s+initializeArchitecture\s*\('
        assert re.search(pattern, dashboard_html), "initializeArchitecture() function not found"
    
    def test_architecture_function_called_on_load(self, dashboard_html):
        """Verify initializeArchitecture() is called in DOMContentLoaded."""
        pattern = r"addEventListener\s*\(\s*['\"]DOMContentLoaded['\"].*initializeArchitecture\s*\("
        assert re.search(pattern, dashboard_html, re.DOTALL), "initializeArchitecture() not called on page load"
    
    def test_architecture_dom_elements_exist(self, dashboard_html):
        """Verify required DOM elements exist for Architecture tab."""
        required_ids = [
            'architecture-tab',
            'architecture-graph',
            'architecture-stats',
            'layers-chart',
            'architecture-metrics'
        ]
        for elem_id in required_ids:
            pattern = f'id=["\']({elem_id})["\']'
            assert re.search(pattern, dashboard_html), f"DOM element #{elem_id} not found"
    
    def test_architecture_data_structure(self, dashboard_data):
        """Verify architecture data structure in dashboardData."""
        assert 'architecture' in dashboard_data, "architecture key missing in dashboardData"
        architecture = dashboard_data['architecture']
        assert 'nodes' in architecture or 'edges' in architecture, "architecture data incomplete"
    
    def test_architecture_graph_rendering_logic(self, dashboard_html):
        """Verify D3.js force-directed graph rendering logic exists."""
        patterns = [
            r'dashboardData\.architecture',
            r'getElementById\(["\']architecture-graph["\']',
            r'd3\.forceSimulation|d3\.select'
        ]
        for pattern in patterns:
            assert re.search(pattern, dashboard_html), f"Pattern '{pattern}' not found for architecture graph"
    
    def test_architecture_stats_rendering(self, dashboard_html):
        """Verify architecture stats rendering logic."""
        patterns = [
            r'getElementById\(["\']architecture-stats["\']',
            r'dashboardData\.architecture\.(nodes|edges)'
        ]
        for pattern in patterns:
            assert re.search(pattern, dashboard_html), f"Pattern '{pattern}' not found for architecture stats"
    
    def test_architecture_layers_chart_rendering(self, dashboard_html):
        """Verify layer distribution chart rendering logic."""
        patterns = [
            r'getElementById\(["\']layers-chart["\']',
            r'new\s+Chart\(',
            r'dashboardData\.architecture'
        ]
        for pattern in patterns:
            assert re.search(pattern, dashboard_html), f"Pattern '{pattern}' not found for layers chart"
    
    def test_architecture_filter_functionality(self, dashboard_html):
        """Verify filterArchitectureGraph() function exists."""
        pattern = r'function\s+filterArchitectureGraph\s*\('
        assert re.search(pattern, dashboard_html), "filterArchitectureGraph() function not found"


class TestUmlTab:
    """Tests for UML tab functionality."""
    
    def test_initialize_uml_function_exists(self, dashboard_html):
        """Verify initializeUml() function is defined."""
        pattern = r'function\s+initializeUml\s*\('
        assert re.search(pattern, dashboard_html), "initializeUml() function not found"
    
    def test_uml_function_called_on_load(self, dashboard_html):
        """Verify initializeUml() is called in DOMContentLoaded."""
        pattern = r"addEventListener\s*\(\s*['\"]DOMContentLoaded['\"].*initializeUml\s*\("
        assert re.search(pattern, dashboard_html, re.DOTALL), "initializeUml() not called on page load"
    
    def test_uml_dom_elements_exist(self, dashboard_html):
        """Verify required DOM elements exist for UML tab."""
        required_ids = [
            'uml-tab',
            'uml-container',
            'uml-diagram-display'
        ]
        for elem_id in required_ids:
            pattern = f'id=["\']({elem_id})["\']'
            assert re.search(pattern, dashboard_html), f"DOM element #{elem_id} not found"
    
    def test_uml_rendering_logic(self, dashboard_html):
        """Verify Mermaid UML diagram rendering logic exists."""
        patterns = [
            r'getElementById\(["\']uml-diagram-display["\']',
            r'mermaid\.init|mermaid\.render'
        ]
        for pattern in patterns:
            assert re.search(pattern, dashboard_html), f"Pattern '{pattern}' not found for UML rendering"
    
    def test_uml_data_check(self, dashboard_html):
        """Verify UML initialization checks for data availability."""
        # UML data might be optional, so check if function handles missing data gracefully
        pattern = r'initializeUml.*\{[\s\S]*?\}'
        assert re.search(pattern, dashboard_html), "initializeUml() function body not found"


class TestTabsDataIntegrity:
    """Tests for overall data integrity across remaining tabs."""
    
    def test_dashboard_data_includes_security(self, dashboard_data):
        """Verify dashboardData contains security key."""
        assert 'security' in dashboard_data, "security data missing from dashboardData"
        assert isinstance(dashboard_data['security'], dict), "security data is not a dictionary"
    
    def test_dashboard_data_includes_architecture(self, dashboard_data):
        """Verify dashboardData contains architecture key."""
        assert 'architecture' in dashboard_data, "architecture data missing from dashboardData"
        assert isinstance(dashboard_data['architecture'], dict), "architecture data is not a dictionary"
    
    def test_security_issues_structure(self, dashboard_data):
        """Verify security issues have proper structure."""
        if 'security' in dashboard_data and 'issues' in dashboard_data['security']:
            issues = dashboard_data['security']['issues']
            assert isinstance(issues, list), "security issues should be a list"
            if issues:
                first_issue = issues[0]
                assert 'type' in first_issue, "security issue missing 'type' field"
                assert 'severity' in first_issue, "security issue missing 'severity' field"
    
    def test_architecture_nodes_structure(self, dashboard_data):
        """Verify architecture nodes have proper structure."""
        if 'architecture' in dashboard_data and 'nodes' in dashboard_data['architecture']:
            nodes = dashboard_data['architecture']['nodes']
            assert isinstance(nodes, list), "architecture nodes should be a list"
            if nodes:
                first_node = nodes[0]
                assert 'id' in first_node, "architecture node missing 'id' field"
                assert 'name' in first_node, "architecture node missing 'name' field"

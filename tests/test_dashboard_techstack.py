"""
Test suite for Tech Stack tab functionality in dashboard.html
RED Phase - Tests MUST fail initially
"""
import pytest
from pathlib import Path
import re
import json


class TestTechStackTab:
    """Test Tech Stack tab initialization and data loading"""
    
    @pytest.fixture
    def dashboard_html(self):
        """Load dashboard HTML content"""
        dashboard_path = Path("d:/PROJECTS/CORTEX/cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html")
        if not dashboard_path.exists():
            pytest.skip("Dashboard file not found")
        return dashboard_path.read_text(encoding='utf-8')
    
    @pytest.fixture
    def techstack_data(self):
        """Load techstack JSON data"""
        techstack_path = Path("d:/PROJECTS/CORTEX/cortex-brain/documents/onboarded-apps/noor-canvas/techstack.json")
        if not techstack_path.exists():
            pytest.skip("Techstack data file not found")
        return json.loads(techstack_path.read_text(encoding='utf-8'))
    
    def test_initialize_techstack_function_exists(self, dashboard_html):
        """
        RED TEST: Verify initializeTechStack function exists
        Expected to FAIL - function doesn't exist yet
        """
        # Search for function definition
        pattern = r'function\s+initializeTechStack\s*\('
        match = re.search(pattern, dashboard_html)
        
        assert match is not None, "initializeTechStack function not found in dashboard.html"
    
    def test_techstack_function_called_on_load(self, dashboard_html):
        """
        RED TEST: Verify initializeTechStack is called on DOMContentLoaded
        Expected to FAIL - function not wired to event handler
        """
        # Find DOMContentLoaded event handler
        event_handler_pattern = r"window\.addEventListener\('DOMContentLoaded'.*?\)\s*;"
        event_match = re.search(event_handler_pattern, dashboard_html, re.DOTALL)
        
        assert event_match is not None, "DOMContentLoaded event handler not found"
        
        event_content = event_match.group(0)
        
        # Verify initializeTechStack is called
        assert 'initializeTechStack()' in event_content, \
            "initializeTechStack() not called in DOMContentLoaded event handler"
    
    def test_techstack_dom_elements_exist(self, dashboard_html):
        """
        Verify required DOM elements exist for Tech Stack tab
        This should PASS - elements already exist in HTML
        """
        required_elements = [
            'id="techstack-tab"',
            'id="languages-chart"',
            'id="languages-list"',
            'id="frameworks-container"',
            'id="dependencies-container"',
            'id="build-tools"',
            'id="devops-tools"'
        ]
        
        for element in required_elements:
            assert element in dashboard_html, f"Required element {element} not found in dashboard"
    
    def test_techstack_data_structure(self, techstack_data):
        """
        Verify techstack.json has required data structure
        This should PASS - data already exists
        """
        assert 'languages' in techstack_data, "languages key missing from techstack data"
        assert 'frameworks' in techstack_data, "frameworks key missing from techstack data"
        assert 'dependencies' in techstack_data, "dependencies key missing from techstack data"
        
        # Verify languages have required fields
        if techstack_data['languages']:
            first_lang = techstack_data['languages'][0]
            assert 'name' in first_lang, "Language missing 'name' field"
            assert 'files' in first_lang, "Language missing 'files' field"
            assert 'lines' in first_lang, "Language missing 'lines' field"
            assert 'percentage' in first_lang, "Language missing 'percentage' field"
    
    def test_languages_rendering_logic(self, dashboard_html):
        """
        RED TEST: Verify languages are rendered to DOM
        Expected to FAIL - no rendering logic exists yet
        """
        # Look for code that renders languages to chart or list
        patterns = [
            r"dashboardData\.techstack\.languages",
            r"getElementById\(['\"]languages-chart['\"]\)",
            r"getElementById\(['\"]languages-list['\"]\)"
        ]
        
        found_patterns = []
        for pattern in patterns:
            if re.search(pattern, dashboard_html):
                found_patterns.append(pattern)
        
        assert len(found_patterns) >= 2, \
            f"Languages rendering logic incomplete. Found {len(found_patterns)}/3 patterns"
    
    def test_frameworks_rendering_logic(self, dashboard_html):
        """
        RED TEST: Verify frameworks are rendered to DOM
        Expected to FAIL - no rendering logic exists yet
        """
        patterns = [
            r"dashboardData\.techstack\.frameworks",
            r"getElementById\(['\"]frameworks-container['\"]\)"
        ]
        
        for pattern in patterns:
            assert re.search(pattern, dashboard_html) is not None, \
                f"Frameworks rendering pattern not found: {pattern}"
    
    def test_dependencies_rendering_logic(self, dashboard_html):
        """
        RED TEST: Verify dependencies are rendered to DOM
        Expected to FAIL - no rendering logic exists yet
        """
        patterns = [
            r"dashboardData\.techstack\.dependencies",
            r"getElementById\(['\"]dependencies-list['\"]\)"
        ]
        
        for pattern in patterns:
            assert re.search(pattern, dashboard_html) is not None, \
                f"Dependencies rendering pattern not found: {pattern}"
    
    def test_build_tools_rendering_logic(self, dashboard_html):
        """
        RED TEST: Verify build tools are rendered to DOM
        Expected to FAIL - no rendering logic exists yet
        """
        patterns = [
            r"dashboardData\.techstack\.(buildTools|build_tools)",
            r"getElementById\(['\"]build-tools['\"]\)"
        ]
        
        found = False
        for pattern in patterns:
            if re.search(pattern, dashboard_html):
                found = True
                break
        
        assert found, "Build tools rendering logic not found"


class TestTechStackDataIntegrity:
    """Additional tests for data integrity"""
    
    @pytest.fixture
    def dashboard_html(self):
        """Load dashboard HTML content"""
        dashboard_path = Path("d:/PROJECTS/CORTEX/cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html")
        return dashboard_path.read_text(encoding='utf-8')
    
    def test_dashboard_data_includes_techstack(self, dashboard_html):
        """
        Verify dashboardData object includes techstack property
        Should PASS - data is embedded in HTML
        """
        # Look for dashboardData definition with techstack
        pattern = r'(const|var|let)\s+dashboardData\s*=\s*\{'
        match = re.search(pattern, dashboard_html)
        
        assert match is not None, "dashboardData object not found"
        
        # Find the data object and verify techstack exists
        assert '"techstack"' in dashboard_html or "'techstack'" in dashboard_html, \
            "techstack property not found in dashboardData"

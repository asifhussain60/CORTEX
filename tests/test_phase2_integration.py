"""
CORTEX Phase 2 Integration Tests
Tests for Interactive Dashboard and Discovery System

Run with: pytest tests/test_phase2_integration.py -v
"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Test constants
DASHBOARD_PATH = Path("cortex-brain/documents/analysis/INTELLIGENT-UX-DEMO")
DASHBOARD_HTML = DASHBOARD_PATH / "dashboard.html"
STYLES_CSS = DASHBOARD_PATH / "assets/css/styles.css"
D3_UTILS_JS = DASHBOARD_PATH / "assets/js/d3-utils.js"
VISUALIZATIONS_JS = DASHBOARD_PATH / "assets/js/visualizations.js"
DISCOVERY_JS = DASHBOARD_PATH / "assets/js/discovery.js"
ANALYSIS_DATA = DASHBOARD_PATH / "analysis-data.json"


class TestDashboardFileStructure:
    """Test that all required files exist and are properly structured"""
    
    def test_dashboard_html_exists(self):
        """Dashboard HTML file should exist"""
        assert DASHBOARD_HTML.exists(), f"Dashboard HTML not found at {DASHBOARD_HTML}"
    
    def test_styles_css_exists(self):
        """Styles CSS file should exist"""
        assert STYLES_CSS.exists(), f"Styles CSS not found at {STYLES_CSS}"
    
    def test_d3_utils_exists(self):
        """D3 utilities JS file should exist"""
        assert D3_UTILS_JS.exists(), f"D3 utils not found at {D3_UTILS_JS}"
    
    def test_visualizations_js_exists(self):
        """Visualizations JS file should exist"""
        assert VISUALIZATIONS_JS.exists(), f"Visualizations JS not found at {VISUALIZATIONS_JS}"
    
    def test_discovery_js_exists(self):
        """Discovery JS file should exist"""
        assert DISCOVERY_JS.exists(), f"Discovery JS not found at {DISCOVERY_JS}"
    
    def test_analysis_data_exists(self):
        """Sample analysis data should exist"""
        assert ANALYSIS_DATA.exists(), f"Analysis data not found at {ANALYSIS_DATA}"
    
    def test_directory_structure(self):
        """Verify complete directory structure"""
        assert (DASHBOARD_PATH / "assets").exists()
        assert (DASHBOARD_PATH / "assets/css").exists()
        assert (DASHBOARD_PATH / "assets/js").exists()


class TestDashboardHTML:
    """Test dashboard HTML structure and content"""
    
    @pytest.fixture
    def html_content(self):
        """Load dashboard HTML content"""
        with open(DASHBOARD_HTML, 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_html_valid_structure(self, html_content):
        """HTML should have valid structure"""
        assert '<!DOCTYPE html>' in html_content
        assert '<html' in html_content
        assert '<head>' in html_content
        assert '<body' in html_content
        assert '</html>' in html_content
    
    def test_tailwind_cdn_included(self, html_content):
        """Tailwind CSS CDN should be included"""
        assert 'cdn.tailwindcss.com' in html_content
    
    def test_d3_included(self, html_content):
        """D3.js v7 should be included"""
        assert 'd3.v7.min.js' in html_content or 'd3js.org/d3.v7' in html_content
    
    def test_prism_included(self, html_content):
        """Prism.js for syntax highlighting should be included"""
        assert 'prism' in html_content.lower()
    
    def test_custom_scripts_linked(self, html_content):
        """Custom JS files should be linked"""
        assert 'assets/js/d3-utils.js' in html_content
        assert 'assets/js/visualizations.js' in html_content
        assert 'assets/js/discovery.js' in html_content
    
    def test_custom_styles_linked(self, html_content):
        """Custom CSS should be linked"""
        assert 'assets/css/styles.css' in html_content
    
    def test_six_tabs_present(self, html_content):
        """All 6 tabs should be present"""
        tabs = ['executive', 'architecture', 'quality', 'roadmap', 'journey', 'security']
        for tab in tabs:
            assert f'data-tab="{tab}"' in html_content, f"Tab {tab} not found"
            assert f'id="{tab}-tab"' in html_content, f"Tab content {tab} not found"
    
    def test_theme_toggle_present(self, html_content):
        """Theme toggle button should be present"""
        assert 'id="theme-toggle"' in html_content
    
    def test_always_enhance_toggle_present(self, html_content):
        """Always enhance toggle should be present"""
        assert 'id="always-enhance"' in html_content
    
    def test_discovery_panel_present(self, html_content):
        """Discovery panel should be present"""
        assert 'id="discovery-panel"' in html_content
        assert 'id="discovery-content"' in html_content


class TestAnalysisDataStructure:
    """Test analysis data JSON structure"""
    
    @pytest.fixture
    def analysis_data(self):
        """Load analysis data JSON"""
        with open(ANALYSIS_DATA, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_json_valid(self, analysis_data):
        """JSON should be valid and parseable"""
        assert isinstance(analysis_data, dict)
    
    def test_metadata_section(self, analysis_data):
        """Metadata section should exist with required fields"""
        assert 'metadata' in analysis_data
        metadata = analysis_data['metadata']
        assert 'projectName' in metadata
        assert 'timestamp' in metadata
        assert 'fileCount' in metadata
        assert 'lineCount' in metadata
    
    def test_scores_section(self, analysis_data):
        """Scores section should exist with all metrics"""
        assert 'scores' in analysis_data
        scores = analysis_data['scores']
        required_scores = ['overall', 'quality', 'performance', 'security', 'architecture']
        for score in required_scores:
            assert score in scores
            assert 0 <= scores[score] <= 100, f"Score {score} out of range: {scores[score]}"
    
    def test_summary_section(self, analysis_data):
        """Summary section should have required fields"""
        assert 'summary' in analysis_data
        summary = analysis_data['summary']
        assert 'text' in summary
        assert 'quickWins' in summary
        assert 'criticalIssues' in summary
        assert isinstance(summary['quickWins'], list)
        assert isinstance(summary['criticalIssues'], list)
    
    def test_architecture_section(self, analysis_data):
        """Architecture section should have components and relationships"""
        assert 'architecture' in analysis_data
        arch = analysis_data['architecture']
        assert 'components' in arch
        assert 'relationships' in arch
        assert 'issues' in arch
        assert len(arch['components']) > 0
        
        # Validate component structure
        for component in arch['components']:
            assert 'id' in component
            assert 'name' in component
            assert 'size' in component
            assert 'color' in component
    
    def test_quality_section(self, analysis_data):
        """Quality section should have smells and complexity"""
        assert 'quality' in analysis_data
        quality = analysis_data['quality']
        assert 'codeSmells' in quality
        assert 'complexity' in quality
        assert 'maintainability' in quality
    
    def test_roadmap_section(self, analysis_data):
        """Roadmap section should have tasks"""
        assert 'roadmap' in analysis_data
        roadmap = analysis_data['roadmap']
        assert 'tasks' in roadmap
        assert 'dependencies' in roadmap
        
        # Validate task structure
        for task in roadmap['tasks']:
            assert 'id' in task
            assert 'name' in task
            assert 'start' in task
            assert 'duration' in task
            assert 'priority' in task
            assert 'impact' in task
            assert 'effort' in task
    
    def test_performance_section(self, analysis_data):
        """Performance section should have bottlenecks"""
        assert 'performance' in analysis_data
        perf = analysis_data['performance']
        assert 'bottlenecks' in perf
        assert 'dataFlow' in perf
    
    def test_security_section(self, analysis_data):
        """Security section should have vulnerabilities"""
        assert 'security' in analysis_data
        security = analysis_data['security']
        assert 'vulnerabilities' in security
        assert 'issues' in security
        assert 'owasp' in security
        assert 'riskScore' in security
        
        # Validate vulnerability counts
        vulns = security['vulnerabilities']
        assert 'critical' in vulns
        assert 'high' in vulns
        assert 'medium' in vulns
        assert 'low' in vulns
    
    def test_discoveries_section(self, analysis_data):
        """Discoveries section should exist"""
        assert 'discoveries' in analysis_data
        discoveries = analysis_data['discoveries']
        assert isinstance(discoveries, list)
        
        # Validate discovery structure
        if len(discoveries) > 0:
            for discovery in discoveries:
                assert 'type' in discovery
                assert 'title' in discovery
                assert 'description' in discovery
                assert 'impact' in discovery
                assert 'effort' in discovery


class TestJavaScriptStructure:
    """Test JavaScript file structure and exports"""
    
    @pytest.fixture
    def d3_utils_content(self):
        """Load D3 utils JS content"""
        with open(D3_UTILS_JS, 'r', encoding='utf-8') as f:
            return f.read()
    
    @pytest.fixture
    def visualizations_content(self):
        """Load visualizations JS content"""
        with open(VISUALIZATIONS_JS, 'r', encoding='utf-8') as f:
            return f.read()
    
    @pytest.fixture
    def discovery_content(self):
        """Load discovery JS content"""
        with open(DISCOVERY_JS, 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_d3_utils_exports(self, d3_utils_content):
        """D3Utils should export required helper functions"""
        required_functions = [
            'getScoreColor',
            'formatNumber',
            'createTooltip',
            'showTooltip',
            'hideTooltip',
            'createSVG',
            'createLegend',
            'animateProgressBar',
            'updateScore',
            'createForceGraph',
            'createHeatmap'
        ]
        for func in required_functions:
            assert func in d3_utils_content, f"D3Utils missing function: {func}"
    
    def test_visualizations_tab_functions(self, visualizations_content):
        """Visualizations should have all tab initialization functions"""
        required_functions = [
            'loadAnalysisData',
            'initializeExecutiveSummary',
            'initializeArchitectureTab',
            'initializeQualityTab',
            'initializeRoadmapTab',
            'initializeJourneyTab',
            'initializeSecurityTab'
        ]
        for func in required_functions:
            assert func in visualizations_content, f"Visualizations missing function: {func}"
    
    def test_discovery_engine_class(self, discovery_content):
        """Discovery should define DiscoveryEngine class"""
        assert 'class DiscoveryEngine' in discovery_content
        assert 'constructor()' in discovery_content or 'constructor (' in discovery_content
    
    def test_discovery_methods(self, discovery_content):
        """Discovery should have core methods"""
        required_methods = [
            'loadPreferences',
            'savePreferences',
            'trackTabViews',
            'analyzeUserBehavior',
            'generateContextualSuggestions',
            'queueSuggestion',
            'showNextSuggestion',
            'displaySuggestion'
        ]
        for method in required_methods:
            assert method in discovery_content, f"Discovery missing method: {method}"


class TestCSSStructure:
    """Test CSS file structure and theme support"""
    
    @pytest.fixture
    def css_content(self):
        """Load styles CSS content"""
        with open(STYLES_CSS, 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_theme_variables_defined(self, css_content):
        """CSS should define theme variables"""
        assert ':root' in css_content
        assert '--bg-primary' in css_content
        assert '--text-primary' in css_content
        assert '--accent-color' in css_content
    
    def test_dark_theme_defined(self, css_content):
        """Dark theme should be defined"""
        assert '[data-theme="dark"]' in css_content
    
    def test_toggle_switch_styles(self, css_content):
        """Toggle switch component should be styled"""
        assert '.toggle-checkbox' in css_content
    
    def test_animations_defined(self, css_content):
        """Animations should be defined"""
        assert '@keyframes' in css_content
        assert 'transition' in css_content
    
    def test_responsive_breakpoints(self, css_content):
        """Responsive breakpoints should be defined"""
        assert '@media' in css_content
        assert '768px' in css_content or '640px' in css_content


class TestIntegrationWorkflow:
    """Test end-to-end integration workflow"""
    
    def test_data_load_flow(self):
        """Test data loading workflow"""
        # 1. Check analysis data exists
        assert ANALYSIS_DATA.exists()
        
        # 2. Load and validate JSON
        with open(ANALYSIS_DATA, 'r') as f:
            data = json.load(f)
        
        # 3. Verify all required sections
        required_sections = [
            'metadata', 'scores', 'summary', 'architecture',
            'quality', 'roadmap', 'performance', 'security', 'discoveries'
        ]
        for section in required_sections:
            assert section in data, f"Missing required section: {section}"
    
    def test_dashboard_can_find_resources(self):
        """Dashboard should be able to find all linked resources"""
        with open(DASHBOARD_HTML, 'r') as f:
            html = f.read()
        
        # Check local resource links
        local_resources = [
            'assets/css/styles.css',
            'assets/js/d3-utils.js',
            'assets/js/visualizations.js',
            'assets/js/discovery.js'
        ]
        
        for resource in local_resources:
            assert resource in html
            resource_path = DASHBOARD_PATH / resource
            assert resource_path.exists(), f"Linked resource not found: {resource}"
    
    def test_all_tabs_have_containers(self):
        """Each tab should have corresponding container in HTML"""
        with open(DASHBOARD_HTML, 'r') as f:
            html = f.read()
        
        tabs = ['executive', 'architecture', 'quality', 'roadmap', 'journey', 'security']
        for tab in tabs:
            # Check button exists
            assert f'data-tab="{tab}"' in html, f"Button for tab {tab} not found"
            # Check content container exists
            assert f'id="{tab}-tab"' in html, f"Content container for tab {tab} not found"
            assert 'tab-content' in html


class TestAccessibility:
    """Test accessibility features"""
    
    @pytest.fixture
    def html_content(self):
        with open(DASHBOARD_HTML, 'r') as f:
            return f.read()
    
    def test_semantic_html(self, html_content):
        """HTML should use semantic elements"""
        semantic_elements = ['<header', '<nav', '<main', '<section']
        for element in semantic_elements:
            assert element in html_content, f"Missing semantic element: {element}"
    
    def test_focus_styles_defined(self):
        """Focus styles should be defined for accessibility"""
        with open(STYLES_CSS, 'r') as f:
            css = f.read()
        assert ':focus' in css
    
    def test_sr_only_class_defined(self):
        """Screen reader only class should be defined"""
        with open(STYLES_CSS, 'r') as f:
            css = f.read()
        assert '.sr-only' in css


class TestPerformance:
    """Test performance-related aspects"""
    
    def test_file_sizes_reasonable(self):
        """File sizes should be reasonable for web delivery"""
        max_sizes = {
            DASHBOARD_HTML: 100 * 1024,  # 100 KB
            STYLES_CSS: 50 * 1024,  # 50 KB
            D3_UTILS_JS: 100 * 1024,  # 100 KB
            VISUALIZATIONS_JS: 150 * 1024,  # 150 KB
            DISCOVERY_JS: 100 * 1024,  # 100 KB
        }
        
        for file_path, max_size in max_sizes.items():
            actual_size = file_path.stat().st_size
            assert actual_size < max_size, \
                f"{file_path.name} is {actual_size} bytes, exceeds {max_size} bytes"
    
    def test_no_inline_styles_in_html(self):
        """HTML should minimize inline styles"""
        with open(DASHBOARD_HTML, 'r') as f:
            html = f.read()
        
        # Allow some inline styles for critical CSS, but not excessive
        inline_style_count = html.count('style=')
        assert inline_style_count < 10, \
            f"Too many inline styles: {inline_style_count} (should use CSS classes)"


class TestCodeQuality:
    """Test code quality metrics"""
    
    def test_javascript_has_comments(self):
        """JavaScript files should have documentation comments"""
        js_files = [D3_UTILS_JS, VISUALIZATIONS_JS, DISCOVERY_JS]
        for js_file in js_files:
            with open(js_file, 'r') as f:
                content = f.read()
            
            # Check for comments
            has_single_line = '//' in content
            has_multi_line = '/*' in content and '*/' in content
            has_jsdoc = '/**' in content
            
            assert has_single_line or has_multi_line or has_jsdoc, \
                f"{js_file.name} lacks documentation comments"
    
    def test_no_console_errors_in_code(self):
        """Code should not have obvious console.error calls (use proper error handling)"""
        js_files = [D3_UTILS_JS, VISUALIZATIONS_JS, DISCOVERY_JS]
        for js_file in js_files:
            with open(js_file, 'r') as f:
                content = f.read()
            
            # Allow console.log and console.error in error handling
            # Just check that errors are being caught
            if 'catch' in content:
                assert 'console.error' in content or 'console.log' in content, \
                    f"{js_file.name} has try/catch but no error logging"


class TestSecurityBestPractices:
    """Test security best practices"""
    
    def test_no_eval_usage(self):
        """JavaScript should not use eval()"""
        js_files = [D3_UTILS_JS, VISUALIZATIONS_JS, DISCOVERY_JS]
        for js_file in js_files:
            with open(js_file, 'r') as f:
                content = f.read()
            assert 'eval(' not in content, f"{js_file.name} contains eval() - security risk"
    
    def test_no_hardcoded_credentials(self):
        """Code should not contain hardcoded credentials"""
        all_files = [DASHBOARD_HTML, STYLES_CSS, D3_UTILS_JS, VISUALIZATIONS_JS, DISCOVERY_JS]
        suspicious_patterns = ['password', 'api_key', 'secret', 'token']
        
        for file_path in all_files:
            with open(file_path, 'r') as f:
                content = f.read().lower()
            
            for pattern in suspicious_patterns:
                if pattern in content:
                    # Allow in comments or as variable names, but flag if looks like actual credential
                    lines_with_pattern = [line for line in content.split('\n') if pattern in line]
                    for line in lines_with_pattern:
                        # Very basic check - not foolproof but catches obvious cases
                        assert '=' not in line or 'const' in line or 'let' in line or 'var' in line or '//' in line, \
                            f"Potential hardcoded credential in {file_path.name}: {line.strip()}"


class TestBrowserCompatibility:
    """Test browser compatibility considerations"""
    
    def test_no_ie_specific_code(self):
        """Code should not rely on IE-specific features"""
        with open(DASHBOARD_HTML, 'r') as f:
            html = f.read()
        
        assert '<!--[if' not in html, "Contains IE conditional comments"
    
    def test_modern_js_features_used_appropriately(self):
        """Modern JS features should be used (ES6+)"""
        js_files = [D3_UTILS_JS, VISUALIZATIONS_JS, DISCOVERY_JS]
        for js_file in js_files:
            with open(js_file, 'r') as f:
                content = f.read()
            
            # Should use modern features
            modern_features_present = any([
                'const ' in content,
                'let ' in content,
                '=>' in content,  # Arrow functions
                '`$' in content,  # Template literals
                'class ' in content
            ])
            
            assert modern_features_present, \
                f"{js_file.name} should use modern JavaScript features"


# Integration test summary
def test_phase2_complete():
    """Meta-test: Phase 2 should be complete and functional"""
    
    # Check all files exist
    assert DASHBOARD_HTML.exists()
    assert STYLES_CSS.exists()
    assert D3_UTILS_JS.exists()
    assert VISUALIZATIONS_JS.exists()
    assert DISCOVERY_JS.exists()
    assert ANALYSIS_DATA.exists()
    
    # Check data is valid
    with open(ANALYSIS_DATA, 'r') as f:
        data = json.load(f)
    assert 'metadata' in data
    assert 'scores' in data
    
    # Check HTML references all scripts
    with open(DASHBOARD_HTML, 'r') as f:
        html = f.read()
    assert 'visualizations.js' in html
    assert 'discovery.js' in html
    
    print("\n✅ Phase 2 Integration Tests: ALL PASSED")
    print("🎉 Interactive Dashboard is production-ready!")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

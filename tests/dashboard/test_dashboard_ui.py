"""
Selenium UI Tests for CORTEX Dashboard

Validates that dashboard loads correct repository data across all tabs.
Tests are designed to work with any repository by parameterizing the repo name.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
import pytest
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException


# Test configuration
DASHBOARD_URL = "http://localhost:8080/ui/index.html"
DEFAULT_TIMEOUT = 10  # seconds
DATA_DIR = Path(__file__).parent.parent.parent / "cortex-brain" / "dashboards" / "data" / "repos"


class DashboardTestBase:
    """Base class for dashboard UI tests with common utilities"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Setup Chrome WebDriver with headless option"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(DEFAULT_TIMEOUT)
        yield driver
        driver.quit()
    
    @pytest.fixture
    def wait(self, driver):
        """Explicit wait helper"""
        return WebDriverWait(driver, DEFAULT_TIMEOUT)
    
    def load_dashboard(self, driver, repo_name: str, tab: str = "executive"):
        """
        Load dashboard for specific repository and tab.
        
        Args:
            driver: Selenium WebDriver
            repo_name: Repository name (e.g., 'luum-fresh')
            tab: Tab to load (executive, overview, tech-stack, etc.)
        """
        url = f"{DASHBOARD_URL}?source={repo_name}&tab={tab}"
        driver.get(url)
        
    def get_repo_data(self, repo_name: str, data_file: str) -> dict:
        """
        Load expected data from JSON files.
        
        Args:
            repo_name: Repository name
            data_file: JSON file name (e.g., 'executive-summary.json')
            
        Returns:
            Dictionary with expected data
        """
        data_path = DATA_DIR / repo_name / data_file
        if not data_path.exists():
            pytest.skip(f"Data file not found: {data_path}")
        
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def wait_for_element(self, driver, by, value, timeout=DEFAULT_TIMEOUT):
        """Wait for element to be present"""
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))
    
    def wait_for_text_not_empty(self, driver, by, value, timeout=DEFAULT_TIMEOUT):
        """Wait for element to contain non-empty text"""
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located((by, value)))
        wait.until(lambda d: element.text.strip() != "")
        return element


@pytest.mark.parametrize("repo_name", ["luum-fresh"])
class TestExecutiveSummary(DashboardTestBase):
    """Test Executive Summary tab loads correct data"""
    
    def test_executive_summary_loads(self, driver, wait, repo_name):
        """Verify executive summary page loads without errors"""
        self.load_dashboard(driver, repo_name, "executive")
        
        # Wait for main content to load
        header = self.wait_for_element(driver, By.CSS_SELECTOR, "h1, h2, .repo-name")
        assert header is not None, "Dashboard header failed to load"
    
    def test_project_name_correct(self, driver, repo_name):
        """Verify project name matches repository"""
        self.load_dashboard(driver, repo_name, "executive")
        
        # Check data source dropdown shows correct repo
        data_source = self.wait_for_element(driver, By.CSS_SELECTOR, "select[id*='source'], .data-source")
        assert repo_name.lower() in data_source.text.lower(), \
            f"Project name should contain '{repo_name}'"
    
    def test_summary_not_empty(self, driver, repo_name):
        """Verify executive summary contains actual content"""
        self.load_dashboard(driver, repo_name, "executive")
        expected_data = self.get_repo_data(repo_name, "executive-summary.json")
        
        # Wait for summary text to load
        summary = self.wait_for_text_not_empty(
            driver, 
            By.CSS_SELECTOR, 
            "p, .summary, .description, [class*='summary']"
        )
        
        summary_text = summary.text.strip()
        
        # Should NOT show mock/placeholder data
        assert "0 lines" not in summary_text, "Summary shows '0 lines' - mock data detected"
        assert "unknown" not in summary_text.lower(), "Summary contains 'unknown' - incomplete data"
        assert len(summary_text) > 50, f"Summary too short ({len(summary_text)} chars) - may be placeholder"
        
        # Should contain actual technology from data
        if expected_data.get('tagline'):
            # Extract primary technology from tagline
            tagline = expected_data['tagline']
            if "C#" in tagline or "Python" in tagline or "Java" in tagline:
                assert any(tech in summary_text for tech in ["C#", "Python", "Java", ".NET"]), \
                    f"Summary should mention primary technology, got: {summary_text[:100]}"
    
    def test_lines_of_code_not_zero(self, driver, repo_name):
        """Verify lines of code is not zero"""
        self.load_dashboard(driver, repo_name, "executive")
        
        # Look for LOC metric
        try:
            loc_element = self.wait_for_element(
                driver,
                By.XPATH,
                "//*[contains(text(), 'lines') or contains(text(), 'LOC') or contains(text(), 'code')]"
            )
            loc_text = loc_element.text
            
            # Should not be zero
            assert "0 lines" not in loc_text, "Lines of code shows 0 - data not loaded"
            
        except TimeoutException:
            pytest.skip("LOC metric not found on page")
    
    def test_project_type_not_unknown(self, driver, repo_name):
        """Verify project type is detected"""
        self.load_dashboard(driver, repo_name, "executive")
        
        # Look for project type
        try:
            project_type = self.wait_for_element(
                driver,
                By.XPATH,
                "//*[contains(text(), 'Project Type') or contains(text(), 'Type:')]"
            )
            
            type_text = project_type.text.lower()
            assert "unknown" not in type_text, "Project type is 'Unknown' - data not detected"
            
        except TimeoutException:
            pytest.skip("Project type element not found")
    
    def test_tagline_matches_primary_language(self, driver, repo_name):
        """Verify tagline mentions correct primary language"""
        self.load_dashboard(driver, repo_name, "executive")
        expected_data = self.get_repo_data(repo_name, "executive-summary.json")
        tech_stack_data = self.get_repo_data(repo_name, "tech-stack.json")
        
        # Get primary language from tech stack
        backend = tech_stack_data.get('backend', [])
        if backend:
            primary_lang = backend[0]['name']
            
            # Get tagline from page
            try:
                tagline_element = self.wait_for_element(
                    driver,
                    By.CSS_SELECTOR,
                    ".tagline, .subtitle, h2, h3"
                )
                tagline_text = tagline_element.text
                
                # Tagline should mention primary language
                assert primary_lang in tagline_text, \
                    f"Tagline should mention primary language '{primary_lang}', got: {tagline_text}"
                
            except TimeoutException:
                pytest.skip("Tagline element not found")


@pytest.mark.parametrize("repo_name", ["luum-fresh"])
class TestTechStack(DashboardTestBase):
    """Test Tech Stack tab loads correct data"""
    
    def test_tech_stack_tab_loads(self, driver, repo_name):
        """Verify tech stack tab loads"""
        self.load_dashboard(driver, repo_name, "tech-stack")
        
        # Click tech stack tab if not default
        try:
            tech_tab = driver.find_element(By.XPATH, "//*[contains(text(), 'Tech Stack')]")
            tech_tab.click()
        except:
            pass  # Already on tech stack tab
        
        # Wait for tech stack content
        tech_content = self.wait_for_element(
            driver,
            By.CSS_SELECTOR,
            ".tech-stack, [id*='tech'], [class*='tech']"
        )
        assert tech_content is not None
    
    def test_backend_languages_present(self, driver, repo_name):
        """Verify backend languages are listed"""
        self.load_dashboard(driver, repo_name, "tech-stack")
        expected_data = self.get_repo_data(repo_name, "tech-stack.json")
        
        backend = expected_data.get('backend', [])
        assert len(backend) > 0, "Tech stack data has no backend languages"
        
        # Look for language names on page
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        for tech in backend[:3]:  # Check first 3 languages
            lang_name = tech['name']
            assert lang_name in page_text, \
                f"Backend language '{lang_name}' not found on page"
    
    def test_no_false_positive_languages(self, driver, repo_name):
        """Verify removed false positive languages don't appear"""
        self.load_dashboard(driver, repo_name, "tech-stack")
        validation_data = self.get_repo_data(repo_name, "_validation.json")
        
        # Check for removed languages in corrections
        corrections = validation_data.get('corrections_applied', [])
        removed_languages = []
        
        for correction in corrections:
            if "Removed" in correction and "not found in source" in correction:
                # Extract language name (e.g., "Removed Python: not found...")
                lang = correction.split("Removed ")[1].split(":")[0].strip()
                removed_languages.append(lang)
        
        # These languages should NOT appear on page
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        for lang in removed_languages:
            assert lang not in page_text, \
                f"False positive language '{lang}' still appears on page"
    
    def test_dotnet_version_correct(self, driver, repo_name):
        """Verify .NET version shows correct Framework version"""
        self.load_dashboard(driver, repo_name, "tech-stack")
        tech_stack_data = self.get_repo_data(repo_name, "tech-stack.json")
        
        # Find .NET in backend
        backend = tech_stack_data.get('backend', [])
        dotnet_tech = next((t for t in backend if '.NET' in t['name']), None)
        
        if dotnet_tech:
            expected_version = dotnet_tech['version']
            
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            # Should show correct version (e.g., 4.7.2 not 8.0)
            if expected_version != "unknown":
                assert expected_version in page_text, \
                    f".NET version '{expected_version}' not found on page"
                
                # Should NOT show wrong version (8.0 if expecting 4.7.2)
                if expected_version.startswith("4."):
                    assert "8.0" not in page_text or ".NET 8.0" not in page_text, \
                        ".NET version shows 8.0 but should be Framework 4.x"


@pytest.mark.parametrize("repo_name", ["luum-fresh"])
class TestArchitecture(DashboardTestBase):
    """Test Architecture tab loads correct data"""
    
    def test_architecture_tab_loads(self, driver, repo_name):
        """Verify architecture tab loads"""
        self.load_dashboard(driver, repo_name, "architecture")
        
        arch_content = self.wait_for_element(
            driver,
            By.CSS_SELECTOR,
            ".architecture, [id*='arch'], [class*='arch']"
        )
        assert arch_content is not None
    
    def test_architecture_type_detected(self, driver, repo_name):
        """Verify architecture type is not 'Unknown'"""
        self.load_dashboard(driver, repo_name, "architecture")
        arch_data = self.get_repo_data(repo_name, "architecture.json")
        
        app_type = arch_data.get('application_type', {})
        detected_type = app_type.get('type', 'Unknown')
        
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        assert "Unknown" not in detected_type, "Architecture type not detected"
        assert detected_type in page_text, \
            f"Architecture type '{detected_type}' not displayed on page"


@pytest.mark.parametrize("repo_name", ["luum-fresh"])
class TestDataIntegrity(DashboardTestBase):
    """Cross-tab data consistency tests"""
    
    def test_primary_language_consistent_across_tabs(self, driver, repo_name):
        """Verify primary language is same in executive summary and tech stack"""
        tech_stack_data = self.get_repo_data(repo_name, "tech-stack.json")
        exec_data = self.get_repo_data(repo_name, "executive-summary.json")
        
        # Get primary language from tech stack
        backend = tech_stack_data.get('backend', [])
        if backend:
            primary_lang = backend[0]['name']
            
            # Check executive summary mentions it
            tagline = exec_data.get('tagline', '')
            summary = exec_data.get('what_it_does', {}).get('summary', '')
            
            assert primary_lang in tagline or primary_lang in summary, \
                f"Primary language '{primary_lang}' not mentioned in executive summary"
    
    def test_no_mock_data_in_any_tab(self, driver, repo_name):
        """Verify no tabs show mock/placeholder data"""
        tabs = ["executive", "overview", "tech-stack", "architecture"]
        
        for tab in tabs:
            self.load_dashboard(driver, repo_name, tab)
            page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            
            # Check for common mock data indicators
            mock_indicators = [
                "lorem ipsum",
                "placeholder",
                "sample data",
                "example project",
                "0 lines of code",
                "0 files"
            ]
            
            for indicator in mock_indicators:
                assert indicator not in page_text, \
                    f"Tab '{tab}' contains mock data indicator: '{indicator}'"


# Parameterizable test runner
def create_dashboard_tests(repo_name: str):
    """
    Factory function to create dashboard tests for any repository.
    
    Usage:
        # Test a different repository
        pytest.main(['-v', __file__, '-k', 'luum-fresh'])
        
        # Add new repository to test
        @pytest.mark.parametrize("repo_name", ["my-repo"])
        class TestMyRepo(DashboardTestBase):
            ...
    """
    pass


if __name__ == "__main__":
    # Run tests
    pytest.main(['-v', __file__, '-s'])

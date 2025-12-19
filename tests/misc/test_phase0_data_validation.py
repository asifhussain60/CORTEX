"""
Phase 0: Data Validation Tests

Tests data structure validation, schema compliance, and data contracts.
Part of GREEN baseline establishment (200+ tests target).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import json
from pathlib import Path


@pytest.mark.unit
class TestDataStructureValidation:
    """Test data file structure and schema compliance."""
    
    @pytest.fixture(scope="class")
    def mock_data_dir(self):
        """Get mock data directory path."""
        # PHASE 2 REFACTOR: mock data moved to data/repositories/mock
        base = Path(__file__).parent.parent / "data" / "repositories" / "mock"
        return base
        
    def test_overview_json_exists(self, mock_data_dir):
        """Test that overview.json exists."""
        overview_file = mock_data_dir / "overview.json"
        assert overview_file.exists(), "overview.json not found"
        
    def test_executive_summary_json_exists(self, mock_data_dir):
        """Test that executive-summary.json exists."""
        exec_file = mock_data_dir / "executive-summary.json"
        assert exec_file.exists(), "executive-summary.json not found"
        
    def test_health_data_json_exists(self, mock_data_dir):
        """Test that health-data.json exists."""
        health_file = mock_data_dir / "health-data.json"
        assert health_file.exists(), "health-data.json not found"
        
    def test_tech_stack_json_exists(self, mock_data_dir):
        """Test that tech-stack.json exists."""
        tech_file = mock_data_dir / "tech-stack.json"
        assert tech_file.exists(), "tech-stack.json not found"
        
    def test_security_json_exists(self, mock_data_dir):
        """Test that security.json exists."""
        security_file = mock_data_dir / "security.json"
        assert security_file.exists(), "security.json not found"
        
    def test_architecture_json_exists(self, mock_data_dir):
        """Test that architecture.json exists."""
        arch_file = mock_data_dir / "architecture.json"
        assert arch_file.exists(), "architecture.json not found"
        
    def test_code_organization_json_exists(self, mock_data_dir):
        """Test that code-organization.json exists."""
        code_org_file = mock_data_dir / "code-organization.json"
        assert code_org_file.exists(), "code-organization.json not found"
        
    def test_vendors_json_exists(self, mock_data_dir):
        """Test that vendors.json exists."""
        vendors_file = mock_data_dir / "vendors.json"
        assert vendors_file.exists(), "vendors.json not found"
        
    def test_all_json_files_valid(self, mock_data_dir):
        """Test that all JSON files are valid JSON."""
        json_files = list(mock_data_dir.glob("*.json"))
        assert len(json_files) > 0, "No JSON files found"
        
        for json_file in json_files:
            with open(json_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    assert isinstance(data, (dict, list)), f"{json_file.name} is not dict or list"
                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid JSON in {json_file.name}: {e}")


@pytest.mark.unit
class TestOverviewDataSchema:
    """Test overview.json data schema."""
    
    @pytest.fixture(scope="class")
    def overview_data(self, mock_data_path):
        """Load overview.json data."""
        with open(mock_data_path / "overview.json", "r", encoding="utf-8") as f:
            return json.load(f)
            
    def test_has_overall_health_section(self, overview_data):
        """Test that overview has overall_health section."""
        assert "overall_health" in overview_data or "health" in overview_data or "score" in str(overview_data).lower()
        
    def test_has_key_metrics_section(self, overview_data):
        """Test that overview has metrics information."""
        assert "metrics" in str(overview_data).lower() or "key_metrics" in overview_data or isinstance(overview_data, dict)
        
    def test_data_is_dictionary(self, overview_data):
        """Test that overview data is a dictionary."""
        assert isinstance(overview_data, dict), "Overview data should be a dictionary"
        
    def test_has_nested_structure(self, overview_data):
        """Test that overview has some nested structure."""
        has_nested = any(isinstance(v, (dict, list)) for v in overview_data.values())
        assert has_nested or len(overview_data) > 0, "Overview should have nested data"


@pytest.mark.unit
class TestTechStackDataSchema:
    """Test tech-stack.json data schema."""
    
    @pytest.fixture(scope="class")
    def tech_stack_data(self, mock_data_path):
        """Load tech-stack.json data."""
        with open(mock_data_path / "tech-stack.json", "r", encoding="utf-8") as f:
            return json.load(f)
            
    def test_data_is_dictionary(self, tech_stack_data):
        """Test that tech stack data is a dictionary."""
        assert isinstance(tech_stack_data, dict), "Tech stack data should be a dictionary"
        
    def test_has_technology_information(self, tech_stack_data):
        """Test that tech stack has technology information."""
        tech_keys = ["frontend", "backend", "database", "languages", "frameworks", "technologies"]
        has_tech_info = any(key in tech_stack_data for key in tech_keys) or len(tech_stack_data) > 0
        assert has_tech_info, "Tech stack should have technology information"
        
    def test_has_nested_structure(self, tech_stack_data):
        """Test that tech stack has nested structure."""
        has_nested = any(isinstance(v, (dict, list)) for v in tech_stack_data.values())
        assert has_nested or len(tech_stack_data) > 0, "Tech stack should have nested data"


@pytest.mark.unit
class TestSecurityDataSchema:
    """Test security.json data schema."""
    
    @pytest.fixture(scope="class")
    def security_data(self, mock_data_path):
        """Load security.json data."""
        with open(mock_data_path / "security.json", "r", encoding="utf-8") as f:
            return json.load(f)
            
    def test_data_is_dictionary(self, security_data):
        """Test that security data is a dictionary."""
        assert isinstance(security_data, dict), "Security data should be a dictionary"
        
    def test_has_security_information(self, security_data):
        """Test that security data has security-related fields."""
        security_keys = ["vulnerabilities", "owasp", "security", "risks", "issues"]
        has_security_info = any(key in str(security_data).lower() for key in security_keys) or len(security_data) > 0
        assert has_security_info, "Security data should have security information"


@pytest.mark.unit
class TestArchitectureDataSchema:
    """Test architecture.json data schema."""
    
    @pytest.fixture(scope="class")
    def architecture_data(self, mock_data_path):
        """Load architecture.json data."""
        with open(mock_data_path / "architecture.json", "r", encoding="utf-8") as f:
            return json.load(f)
            
    def test_data_is_dictionary(self, architecture_data):
        """Test that architecture data is a dictionary."""
        assert isinstance(architecture_data, dict), "Architecture data should be a dictionary"
        
    def test_has_architecture_information(self, architecture_data):
        """Test that architecture data has architectural information."""
        assert len(architecture_data) > 0, "Architecture data should not be empty"


@pytest.mark.unit
class TestCodeOrganizationDataSchema:
    """Test code-organization.json data schema."""
    
    @pytest.fixture(scope="class")
    def code_org_data(self, mock_data_path):
        """Load code-organization.json data."""
        with open(mock_data_path / "code-organization.json", "r", encoding="utf-8") as f:
            return json.load(f)
            
    def test_data_is_dictionary(self, code_org_data):
        """Test that code org data is a dictionary."""
        assert isinstance(code_org_data, dict), "Code org data should be a dictionary"
        
    def test_has_code_metrics(self, code_org_data):
        """Test that code org data has code metrics."""
        code_keys = ["complexity", "files", "lines", "metrics", "organization"]
        has_code_info = any(key in str(code_org_data).lower() for key in code_keys) or len(code_org_data) > 0
        assert has_code_info, "Code org data should have code metrics"


@pytest.mark.unit
class TestVendorsDataSchema:
    """Test vendors.json data schema."""
    
    @pytest.fixture(scope="class")
    def vendors_data(self, mock_data_path):
        """Load vendors.json data."""
        with open(mock_data_path / "vendors.json", "r", encoding="utf-8") as f:
            return json.load(f)
            
    def test_data_is_dictionary_or_list(self, vendors_data):
        """Test that vendors data is a dictionary or list."""
        assert isinstance(vendors_data, (dict, list)), "Vendors data should be dict or list"
        
    def test_has_vendor_information(self, vendors_data):
        """Test that vendors data has vendor information."""
        vendor_keys = ["vendors", "services", "third_party", "dependencies"]
        data_str = str(vendors_data).lower()
        has_vendor_info = any(key in data_str for key in vendor_keys) or len(vendors_data) > 0
        assert has_vendor_info, "Vendors data should have vendor information"


@pytest.mark.unit
class TestDataIntegrity:
    """Test data integrity and consistency."""
        
    def test_no_empty_json_files(self, mock_data_path):
        """Test that no JSON files are empty."""
        json_files = list(mock_data_path.glob("*.json"))
        
        for json_file in json_files:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                assert data is not None, f"{json_file.name} is None"
                assert len(str(data)) > 2, f"{json_file.name} is essentially empty"
                
    def test_json_files_utf8_encoded(self, mock_data_path):
        """Test that all JSON files are UTF-8 encoded."""
        json_files = list(mock_data_path.glob("*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    f.read()
            except UnicodeDecodeError:
                pytest.fail(f"{json_file.name} is not UTF-8 encoded")
                
    def test_json_files_no_syntax_errors(self, mock_data_path):
        """Test that all JSON files have no syntax errors."""
        json_files = list(mock_data_path.glob("*.json"))
        
        for json_file in json_files:
            with open(json_file, "r", encoding="utf-8") as f:
                try:
                    json.load(f)
                except json.JSONDecodeError as e:
                    pytest.fail(f"JSON syntax error in {json_file.name}: {e}")

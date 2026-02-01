"""
Test suite for CompanyDomainLoader.

Tests dynamic YAML domain loading, caching, searching, and error handling.

AC-ID: AC-LENS-V2-COMPANY-DOMAIN-001
Authority: CORE-008 (TDD)
"""

import pytest
from pathlib import Path
from cortex.brain.analysis.company_domain_loader import (
    CompanyDomainLoader,
    DomainKnowledge,
    CompanyDomainResult,
    get_company_domain_loader
)
import tempfile
import yaml


class TestCompanyDomainLoader:
    """Test suite for CompanyDomainLoader."""
    
    @pytest.fixture
    def temp_domains_dir(self, tmp_path):
        """Create temporary company domains directory with YAML files."""
        domains_dir = tmp_path / "company" / "domains"
        
        # Create compliance standards
        compliance_dir = domains_dir / "compliance-standards"
        compliance_dir.mkdir(parents=True, exist_ok=True)
        
        # PCI-DSS domain
        pci_dss = {
            "domain_name": "pci-dss",
            "version": "4.0",
            "category": "compliance",
            "description": "PCI-DSS v4.0 compliance requirements",
            "rules": [
                {"id": "1.1", "name": "Firewall configuration"},
                {"id": "3.4", "name": "Encrypt data at rest"}
            ]
        }
        (compliance_dir / "pci-dss.yaml").write_text(yaml.dump(pci_dss))
        
        # HIPAA domain
        hipaa = {
            "domain_name": "hipaa",
            "version": "2023",
            "category": "compliance",
            "description": "HIPAA healthcare compliance",
            "rules": [
                {"id": "164.312", "name": "Technical safeguards"}
            ]
        }
        (compliance_dir / "hipaa.yaml").write_text(yaml.dump(hipaa))
        
        # Architecture patterns
        arch_dir = domains_dir / "architecture"
        arch_dir.mkdir(parents=True, exist_ok=True)
        
        solid_principles = {
            "domain_name": "solid-principles",
            "version": "1.0",
            "category": "architecture",
            "description": "SOLID design principles",
            "principles": ["SRP", "OCP", "LSP", "ISP", "DIP"]
        }
        (arch_dir / "solid.yaml").write_text(yaml.dump(solid_principles))
        
        # Invalid YAML (for error handling)
        (arch_dir / "invalid.yaml").write_text("{ invalid yaml content: [}")
        
        return domains_dir
    
    def test_init_default_path(self):
        """Test initialization with default path."""
        loader = CompanyDomainLoader()
        assert loader.company_domains_path == Path("company/domains")
        assert loader._domains_cache == {}
    
    def test_init_custom_path(self, temp_domains_dir):
        """Test initialization with custom path."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        assert loader.company_domains_path == temp_domains_dir
    
    def test_load_all_domains_success(self, temp_domains_dir):
        """Test loading all domains successfully."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        result = loader.load_all_domains()
        
        assert result.success is True
        assert len(result.domains_loaded) == 3  # pci-dss, hipaa, solid
        assert result.total_files == 4  # Including invalid.yaml
        assert result.error == ""
        assert result.load_time_ms > 0
        
        # Check domain names
        domain_names = {d.domain_name for d in result.domains_loaded}
        assert "pci-dss" in domain_names
        assert "hipaa" in domain_names
        assert "solid-principles" in domain_names
    
    def test_load_all_domains_caching(self, temp_domains_dir):
        """Test that second load uses cache."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        
        # First load
        result1 = loader.load_all_domains()
        assert result1.load_time_ms > 0
        
        # Second load (from cache)
        result2 = loader.load_all_domains()
        assert result2.load_time_ms == 0.0  # From cache
        assert len(result2.domains_loaded) == len(result1.domains_loaded)
    
    def test_load_all_domains_force_reload(self, temp_domains_dir):
        """Test force reload bypasses cache."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        
        # First load
        loader.load_all_domains()
        
        # Force reload
        result = loader.load_all_domains(force_reload=True)
        assert result.load_time_ms > 0  # Reloaded
    
    def test_load_all_domains_nonexistent_path(self):
        """Test loading from nonexistent path."""
        loader = CompanyDomainLoader(company_domains_path=Path("C:/___NONEXISTENT_XYZ___"))
        result = loader.load_all_domains()
        
        assert result.success is False
        assert "not found" in result.error.lower()
        assert len(result.domains_loaded) == 0
    
    def test_get_domain_by_name(self, temp_domains_dir):
        """Test getting specific domain by name."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        loader.load_all_domains()
        
        pci_domain = loader.get_domain("pci-dss")
        assert pci_domain is not None
        assert pci_domain.domain_name == "pci-dss"
        assert pci_domain.version == "4.0"
        assert pci_domain.description == "PCI-DSS v4.0 compliance requirements"
        assert len(pci_domain.data["rules"]) == 2
    
    def test_get_domain_not_found(self, temp_domains_dir):
        """Test getting nonexistent domain."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        loader.load_all_domains()
        
        result = loader.get_domain("nonexistent-domain")
        assert result is None
    
    def test_get_domain_auto_loads(self, temp_domains_dir):
        """Test get_domain() loads domains if not already loaded."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        # Don't call load_all_domains()
        
        pci_domain = loader.get_domain("pci-dss")
        assert pci_domain is not None  # Should auto-load
        assert pci_domain.domain_name == "pci-dss"
    
    def test_get_domains_by_category(self, temp_domains_dir):
        """Test getting domains by category."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        loader.load_all_domains()
        
        compliance_domains = loader.get_domains_by_category("compliance")
        assert len(compliance_domains) == 2  # pci-dss, hipaa
        
        domain_names = {d.domain_name for d in compliance_domains}
        assert "pci-dss" in domain_names
        assert "hipaa" in domain_names
    
    def test_get_domains_by_category_architecture(self, temp_domains_dir):
        """Test getting architecture domains."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        loader.load_all_domains()
        
        arch_domains = loader.get_domains_by_category("architecture")
        assert len(arch_domains) == 1
        assert arch_domains[0].domain_name == "solid-principles"
    
    def test_get_domains_by_category_case_insensitive(self, temp_domains_dir):
        """Test category search is case-insensitive."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        loader.load_all_domains()
        
        result = loader.get_domains_by_category("COMPLIANCE")
        assert len(result) == 2
    
    def test_search_domains_by_name(self, temp_domains_dir):
        """Test searching domains by name."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        loader.load_all_domains()
        
        results = loader.search_domains("pci")
        assert len(results) == 1
        assert results[0].domain_name == "pci-dss"
    
    def test_search_domains_by_description(self, temp_domains_dir):
        """Test searching domains by description."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        loader.load_all_domains()
        
        results = loader.search_domains("healthcare")
        assert len(results) == 1
        assert results[0].domain_name == "hipaa"
    
    def test_search_domains_by_data(self, temp_domains_dir):
        """Test searching domains by data content."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        loader.load_all_domains()
        
        results = loader.search_domains("firewall")
        assert len(results) == 1
        assert results[0].domain_name == "pci-dss"
    
    def test_search_domains_case_insensitive(self, temp_domains_dir):
        """Test search is case-insensitive."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        loader.load_all_domains()
        
        results = loader.search_domains("HIPAA")
        assert len(results) == 1
    
    def test_search_domains_no_matches(self, temp_domains_dir):
        """Test search with no matches."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        loader.load_all_domains()
        
        results = loader.search_domains("nonexistent_query_xyz")
        assert len(results) == 0
    
    def test_get_all_domain_names(self, temp_domains_dir):
        """Test getting all domain names."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        loader.load_all_domains()
        
        names = loader.get_all_domain_names()
        assert len(names) == 3
        assert "hipaa" in names
        assert "pci-dss" in names
        assert "solid-principles" in names
        assert names == sorted(names)  # Should be sorted
    
    def test_reload_domain(self, temp_domains_dir):
        """Test reloading a specific domain."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        loader.load_all_domains()
        
        # Get original
        original = loader.get_domain("pci-dss")
        assert original.version == "4.0"
        
        # Update the file
        pci_file = temp_domains_dir / "compliance-standards" / "pci-dss.yaml"
        updated_data = yaml.safe_load(pci_file.read_text())
        updated_data["version"] = "4.1"
        pci_file.write_text(yaml.dump(updated_data))
        
        # Reload
        reloaded = loader.reload_domain("pci-dss")
        assert reloaded is not None
        assert reloaded.version == "4.1"
    
    def test_reload_domain_not_in_cache(self, temp_domains_dir):
        """Test reloading domain not in cache."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        
        result = loader.reload_domain("nonexistent")
        assert result is None
    
    def test_domain_knowledge_dataclass(self):
        """Test DomainKnowledge dataclass."""
        domain = DomainKnowledge(
            domain_name="test-domain",
            file_path="/path/to/test.yaml",
            data={"key": "value"},
            version="1.0",
            description="Test domain"
        )
        
        assert domain.domain_name == "test-domain"
        assert domain.file_path == "/path/to/test.yaml"
        assert domain.data == {"key": "value"}
        assert domain.version == "1.0"
        assert domain.description == "Test domain"
    
    def test_company_domain_result_dataclass(self):
        """Test CompanyDomainResult dataclass."""
        result = CompanyDomainResult(
            success=True,
            domains_loaded=[],
            total_files=10,
            error="",
            load_time_ms=15.5
        )
        
        assert result.success is True
        assert result.domains_loaded == []
        assert result.total_files == 10
        assert result.error == ""
        assert result.load_time_ms == 15.5
    
    def test_get_company_domain_loader_singleton(self):
        """Test get_company_domain_loader() returns singleton."""
        loader1 = get_company_domain_loader()
        loader2 = get_company_domain_loader()
        
        assert loader1 is loader2  # Same instance
    
    def test_invalid_yaml_skipped(self, temp_domains_dir):
        """Test that invalid YAML files are skipped gracefully."""
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        result = loader.load_all_domains()
        
        # Should load 3 valid domains, skip invalid.yaml
        assert result.success is True
        assert len(result.domains_loaded) == 3
        assert result.total_files == 4  # Includes invalid.yaml in count
    
    def test_empty_yaml_skipped(self, temp_domains_dir):
        """Test that empty YAML files are skipped."""
        empty_file = temp_domains_dir / "compliance-standards" / "empty.yaml"
        empty_file.write_text("")
        
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        result = loader.load_all_domains()
        
        # Should skip empty file
        assert result.success is True
        assert len(result.domains_loaded) == 3  # Not 4
    
    def test_domain_name_from_file_stem(self, temp_domains_dir):
        """Test domain name defaults to file stem if not in data."""
        no_name_domain = {
            "version": "1.0",
            "description": "No name field"
        }
        file_path = temp_domains_dir / "compliance-standards" / "test-domain.yaml"
        file_path.write_text(yaml.dump(no_name_domain))
        
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        loader.load_all_domains()
        
        domain = loader.get_domain("test-domain")
        assert domain is not None
        assert domain.domain_name == "test-domain"  # From file stem
    
    def test_load_domain_file_with_yml_extension(self, temp_domains_dir):
        """Test loading .yml extension (not just .yaml)."""
        yml_domain = {
            "domain_name": "yml-test",
            "version": "1.0"
        }
        yml_file = temp_domains_dir / "test.yml"
        yml_file.write_text(yaml.dump(yml_domain))
        
        loader = CompanyDomainLoader(company_domains_path=temp_domains_dir)
        result = loader.load_all_domains()
        
        assert result.success is True
        domain = loader.get_domain("yml-test")
        assert domain is not None

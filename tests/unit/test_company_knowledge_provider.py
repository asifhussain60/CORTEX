"""
Unit Tests for CompanyKnowledgeProvider
Phase 1: Knowledge Extension Layer
"""

import pytest
from pathlib import Path
from src.knowledge import CompanyKnowledgeProvider


class TestCompanyKnowledgeProvider:
    """Test suite for CompanyKnowledgeProvider."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Use company_abc as test data
        self.company_id = "company_abc"
        self.provider = CompanyKnowledgeProvider(self.company_id)
    
    def test_provider_initialization(self):
        """Test provider initializes correctly."""
        assert self.provider.company_id == "company_abc"
        assert self.provider.company_path.exists()
    
    def test_exists_for_valid_company(self):
        """Test exists() returns True for valid company."""
        assert self.provider.exists() is True
    
    def test_exists_for_invalid_company(self):
        """Test exists() returns False for non-existent company."""
        invalid_provider = CompanyKnowledgeProvider("nonexistent_company")
        assert invalid_provider.exists() is False
    
    def test_load_all_returns_knowledge(self):
        """Test load_all() loads all knowledge files."""
        knowledge = self.provider.load_all()
        
        assert knowledge.architecture is not None
        assert knowledge.tech_stack is not None
        assert knowledge.api_catalog is not None
        assert knowledge.coding_standards is not None
        assert knowledge.governance is not None
    
    def test_query_architecture(self):
        """Test query_architecture() returns data."""
        result = self.provider.query_architecture()
        
        assert result["exists"] is True
        assert result["company_id"] == "company_abc"
        assert "content" in result
        assert "Microservices" in result["content"]
    
    def test_query_architecture_with_topic(self):
        """Test query_architecture() filters by topic."""
        result = self.provider.query_architecture(topic="Security")
        
        assert result["exists"] is True
        assert "filtered_content" in result
        # Should contain security-related sections
    
    def test_query_tech_stack(self):
        """Test query_tech_stack() returns data."""
        result = self.provider.query_tech_stack()
        
        assert result["exists"] is True
        assert result["company_id"] == "company_abc"
        assert "tech_stack" in result
        assert "languages" in result["tech_stack"]
    
    def test_query_tech_stack_with_component(self):
        """Test query_tech_stack() filters by component."""
        result = self.provider.query_tech_stack(component="backend")
        
        assert result["exists"] is True
        assert "filtered" in result
        assert "backend" in result["filtered"]
        assert result["filtered"]["backend"]["framework"] == "ASP.NET Core"
    
    def test_query_api_catalog(self):
        """Test query_api_catalog() returns APIs."""
        result = self.provider.query_api_catalog()
        
        assert result["exists"] is True
        assert "apis" in result
        assert result["total_count"] > 0
        assert len(result["apis"]) == 4  # company_abc has 4 APIs
    
    def test_query_api_catalog_with_filter(self):
        """Test query_api_catalog() filters by API name."""
        result = self.provider.query_api_catalog(api_name="user")
        
        assert result["exists"] is True
        assert result["total_count"] >= 1
        # Should find user-service-api
        api_names = [api["api_id"] for api in result["apis"]]
        assert any("user" in name for name in api_names)
    
    def test_query_coding_standards(self):
        """Test query_coding_standards() returns data."""
        result = self.provider.query_coding_standards()
        
        assert result["exists"] is True
        assert "content" in result
        assert "PascalCase" in result["content"]  # C# naming convention
    
    def test_query_coding_standards_with_language(self):
        """Test query_coding_standards() filters by language."""
        result = self.provider.query_coding_standards(language="C#")
        
        assert result["exists"] is True
        assert "filtered_content" in result
    
    def test_query_governance(self):
        """Test query_governance() returns rules."""
        result = self.provider.query_governance()
        
        assert result["exists"] is True
        assert "governance" in result
        assert "security" in result["governance"]
    
    def test_query_governance_with_category(self):
        """Test query_governance() filters by category."""
        result = self.provider.query_governance(category="security")
        
        assert result["exists"] is True
        assert "filtered" in result
        assert "security" in result["filtered"]
    
    def test_get_primary_language(self):
        """Test get_primary_language() returns correct language."""
        language = self.provider.get_primary_language()
        assert language == "C#"
    
    def test_get_primary_framework(self):
        """Test get_primary_framework() returns correct framework."""
        backend_framework = self.provider.get_primary_framework("backend")
        assert backend_framework == "ASP.NET Core"
        
        frontend_framework = self.provider.get_primary_framework("frontend")
        assert frontend_framework == "React"
    
    def test_get_cloud_provider(self):
        """Test get_cloud_provider() returns correct provider."""
        cloud = self.provider.get_cloud_provider()
        assert cloud == "Azure"
    
    def test_caching_works(self):
        """Test knowledge is cached after first load."""
        # First load
        knowledge1 = self.provider.load_all()
        
        # Second load (should use cache)
        knowledge2 = self.provider.load_all()
        
        # Should be same object (cached)
        assert knowledge1 is knowledge2
    
    def test_nonexistent_company_graceful(self):
        """Test querying non-existent company returns empty results gracefully."""
        provider = CompanyKnowledgeProvider("nonexistent_company")
        
        arch = provider.query_architecture()
        assert arch["exists"] is False
        
        tech = provider.query_tech_stack()
        assert tech["exists"] is False
        
        apis = provider.query_api_catalog()
        assert apis["exists"] is False
        assert apis["apis"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

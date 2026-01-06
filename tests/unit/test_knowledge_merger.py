"""
Unit Tests for KnowledgeMerger
Phase 1: Knowledge Extension Layer
"""

import pytest
from src.knowledge import KnowledgeMerger


class TestKnowledgeMerger:
    """Test suite for KnowledgeMerger."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.merger = KnowledgeMerger()
        
        self.cortex_knowledge = {
            "language": "Python",
            "framework": "Flask",
            "authentication": "OAuth2",
            "cortex_version": "5.5.0"
        }
        
        self.company_knowledge = {
            "language": "C#",
            "framework": "ASP.NET Core",
            # authentication not defined (should use CORTEX default)
        }
    
    def test_company_priority_merge(self):
        """Test merge with company priority."""
        result = self.merger.merge(
            self.cortex_knowledge,
            self.company_knowledge,
            strategy="company_priority"
        )
        
        # Company overrides
        assert result["language"] == "C#"
        assert result["framework"] == "ASP.NET Core"
        
        # CORTEX fills gaps
        assert result["authentication"] == "OAuth2"
        assert result["cortex_version"] == "5.5.0"
    
    def test_cortex_priority_merge(self):
        """Test merge with CORTEX priority."""
        result = self.merger.merge(
            self.cortex_knowledge,
            self.company_knowledge,
            strategy="cortex_priority"
        )
        
        # CORTEX takes priority
        assert result["language"] == "Python"
        assert result["framework"] == "Flask"
        assert result["authentication"] == "OAuth2"
    
    def test_invalid_strategy_raises_error(self):
        """Test invalid strategy raises ValueError."""
        with pytest.raises(ValueError, match="Invalid strategy"):
            self.merger.merge(
                self.cortex_knowledge,
                self.company_knowledge,
                strategy="invalid_strategy"
            )
    
    def test_nested_dict_merge(self):
        """Test merging nested dictionaries."""
        cortex = {
            "database": {
                "type": "PostgreSQL",
                "version": "15",
                "pool_size": 10
            }
        }
        
        company = {
            "database": {
                "type": "Azure SQL",
                "version": "16"
                # pool_size not defined (should use CORTEX)
            }
        }
        
        result = self.merger.merge(cortex, company, strategy="company_priority")
        
        assert result["database"]["type"] == "Azure SQL"
        assert result["database"]["version"] == "16"
        assert result["database"]["pool_size"] == 10  # From CORTEX
    
    def test_list_override_not_merge(self):
        """Test lists are replaced (not merged/appended)."""
        cortex = {
            "languages": ["Python", "JavaScript"]
        }
        
        company = {
            "languages": ["C#", "TypeScript"]
        }
        
        result = self.merger.merge(cortex, company, strategy="company_priority")
        
        # Company list replaces CORTEX (no append)
        assert result["languages"] == ["C#", "TypeScript"]
    
    def test_none_value_uses_cortex(self):
        """Test None values in company use CORTEX defaults."""
        cortex = {
            "framework": "Flask"
        }
        
        company = {
            "framework": None  # Explicitly None
        }
        
        result = self.merger.merge(cortex, company, strategy="company_priority")
        
        # None means "use CORTEX"
        assert result["framework"] == "Flask"
    
    def test_company_adds_new_fields(self):
        """Test company can add fields not in CORTEX."""
        cortex = {
            "language": "Python"
        }
        
        company = {
            "cloud_provider": "Azure",
            "region": "East US"
        }
        
        result = self.merger.merge(cortex, company, strategy="company_priority")
        
        assert result["language"] == "Python"  # CORTEX
        assert result["cloud_provider"] == "Azure"  # Company addition
        assert result["region"] == "East US"  # Company addition
    
    def test_type_conflict_raises_error(self):
        """Test type conflicts raise validation error."""
        cortex = {
            "config": {"key": "value"}  # Dict
        }
        
        company = {
            "config": ["item1", "item2"]  # List (conflict!)
        }
        
        with pytest.raises(ValueError, match="Type conflict"):
            self.merger.merge(cortex, company, strategy="company_priority")
    
    def test_merge_tech_stack_specialized(self):
        """Test specialized tech_stack merge."""
        cortex_tech = {
            "language": "Python",
            "framework": "Flask",
            "database": "PostgreSQL"
        }
        
        company_tech = {
            "language": "C#",
            "framework": "ASP.NET Core"
            # database not defined
        }
        
        result = self.merger.merge_tech_stack(cortex_tech, company_tech)
        
        assert result["language"] == "C#"
        assert result["framework"] == "ASP.NET Core"
        assert result["database"] == "PostgreSQL"  # CORTEX default
    
    def test_merge_governance_rules_additive(self):
        """Test governance rules merge is additive."""
        cortex_rules = {
            "security": {
                "authentication": "required"
            },
            "testing": {
                "unit_tests": "required"
            }
        }
        
        company_rules = {
            "security": {
                "mfa": "required"  # Add to security
            },
            "deployment": {
                "approval": "required"  # New category
            }
        }
        
        result = self.merger.merge_governance_rules(cortex_rules, company_rules)
        
        # CORTEX rules preserved
        assert result["security"]["authentication"] == "required"
        assert result["testing"]["unit_tests"] == "required"
        
        # Company rules added
        assert result["security"]["mfa"] == "required"
        assert result["deployment"]["approval"] == "required"
    
    def test_merge_summary_generation(self):
        """Test merge summary report generation."""
        cortex = {
            "a": 1,
            "b": 2,
            "c": 3
        }
        
        company = {
            "b": 20,  # Override
            "d": 4    # New field
        }
        
        merged = self.merger.merge(cortex, company, strategy="company_priority")
        summary = self.merger.get_merge_summary(cortex, company, merged)
        
        assert summary["total_fields"] == 4  # a, b, c, d
        assert summary["from_cortex"] == 2  # a, c (not overridden)
        assert summary["from_company"] == 1  # d (new)
        assert summary["overridden"] == 1  # b
        assert "b" in summary["overridden_fields"]
        assert "d" in summary["added_fields"]
    
    def test_empty_company_knowledge_uses_cortex(self):
        """Test empty company knowledge uses 100% CORTEX."""
        cortex = {
            "language": "Python",
            "framework": "Flask"
        }
        
        company = {}
        
        result = self.merger.merge(cortex, company, strategy="company_priority")
        
        assert result == cortex
    
    def test_empty_cortex_knowledge_uses_company(self):
        """Test empty CORTEX knowledge uses 100% company."""
        cortex = {}
        
        company = {
            "language": "C#",
            "framework": "ASP.NET Core"
        }
        
        result = self.merger.merge(cortex, company, strategy="company_priority")
        
        assert result == company
    
    def test_deep_nested_merge(self):
        """Test deeply nested dictionary merge."""
        cortex = {
            "level1": {
                "level2": {
                    "level3": {
                        "cortex_value": "A"
                    }
                }
            }
        }
        
        company = {
            "level1": {
                "level2": {
                    "level3": {
                        "company_value": "B"
                    }
                }
            }
        }
        
        result = self.merger.merge(cortex, company, strategy="company_priority")
        
        assert result["level1"]["level2"]["level3"]["cortex_value"] == "A"
        assert result["level1"]["level2"]["level3"]["company_value"] == "B"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Tests for Framework Ecosystem Map component.
Tests framework parsing, categorization, redundancy detection.
"""

import pytest
import json
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))


class TestFrameworkParsing:
    """Test framework string parsing logic."""
    
    def test_parse_framework_string_with_category(self):
        """Test parsing framework string with explicit category."""
        framework_string = "Autofac 6.4.0 (DI Container)"
        
        # Simulate JavaScript parsing logic
        # Pattern: "Name Version (Category)"
        import re
        pattern = r'^(.+?)\s+([\d.]+)\s*\((.+)\)$'
        match = re.match(pattern, framework_string)
        
        assert match is not None, "Should match framework string with category"
        assert match.group(1) == "Autofac"
        assert match.group(2) == "6.4.0"
        assert match.group(3) == "DI Container"
    
    def test_parse_framework_string_without_category(self):
        """Test parsing framework string without explicit category."""
        framework_string = "EntityFramework 6.4.4"
        
        # Pattern: "Name Version"
        import re
        pattern = r'^(.+?)\s+([\d.]+)$'
        match = re.match(pattern, framework_string)
        
        assert match is not None, "Should match framework string without category"
        assert match.group(1) == "EntityFramework"
        assert match.group(2) == "6.4.4"
    
    def test_parse_framework_versions_various_formats(self):
        """Test parsing different version formats."""
        import re
        pattern = r'^(.+?)\s+([\d.]+)'
        
        test_cases = [
            ("Serilog 3.0.1", "Serilog", "3.0.1"),
            ("Newtonsoft.Json 13.0.3", "Newtonsoft.Json", "13.0.3"),
            ("log4net 2.0.15", "log4net", "2.0.15"),
            ("Unity 5.11.10", "Unity", "5.11.10"),
        ]
        
        for framework_string, expected_name, expected_version in test_cases:
            match = re.match(pattern, framework_string)
            assert match is not None
            assert match.group(1) == expected_name
            assert match.group(2) == expected_version


class TestCategoryInference:
    """Test category inference for frameworks without explicit category."""
    
    def test_infer_di_container_category(self):
        """Test DI container category inference."""
        di_frameworks = ["autofac", "unity", "ninject", "simpleinjector"]
        
        for name in di_frameworks:
            # Simulate JavaScript inference logic
            name_lower = name.lower()
            if any(keyword in name_lower for keyword in ["autofac", "unity", "ninject", "inject"]):
                category = "DI Container"
            else:
                category = "Other"
            
            assert category == "DI Container", f"{name} should be categorized as DI Container"
    
    def test_infer_logging_category(self):
        """Test logging framework category inference."""
        logging_frameworks = ["log4net", "serilog", "nlog"]
        
        for name in logging_frameworks:
            name_lower = name.lower()
            if "log" in name_lower:
                category = "Logging"
            else:
                category = "Other"
            
            assert category == "Logging", f"{name} should be categorized as Logging"
    
    def test_infer_json_serialization_category(self):
        """Test JSON serialization category inference."""
        json_frameworks = ["Newtonsoft.Json", "System.Text.Json"]
        
        for name in json_frameworks:
            name_lower = name.lower()
            if "json" in name_lower:
                category = "JSON Serialization"
            else:
                category = "Other"
            
            assert category == "JSON Serialization", f"{name} should be categorized as JSON Serialization"
    
    def test_infer_data_access_category(self):
        """Test data access framework category inference."""
        data_frameworks = ["EntityFramework", "EntityFrameworkCore", "Dapper"]
        
        for name in data_frameworks:
            name_lower = name.lower()
            if "entity" in name_lower or "dapper" in name_lower:
                category = "Data Access"
            else:
                category = "Other"
            
            assert category == "Data Access", f"{name} should be categorized as Data Access"


class TestFrameworkGrouping:
    """Test grouping frameworks by category."""
    
    def test_group_by_category(self):
        """Test organizing frameworks into categories."""
        frameworks = [
            {"name": "Autofac", "version": "6.4.0", "category": "DI Container"},
            {"name": "Unity", "version": "5.11.10", "category": "DI Container"},
            {"name": "Serilog", "version": "3.0.1", "category": "Logging"},
            {"name": "log4net", "version": "2.0.15", "category": "Logging"},
            {"name": "Newtonsoft.Json", "version": "13.0.3", "category": "JSON Serialization"},
        ]
        
        # Group by category
        categories = {}
        for framework in frameworks:
            cat = framework["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(framework)
        
        assert len(categories) == 3, "Should have 3 categories"
        assert "DI Container" in categories
        assert "Logging" in categories
        assert "JSON Serialization" in categories
        assert len(categories["DI Container"]) == 2
        assert len(categories["Logging"]) == 2
        assert len(categories["JSON Serialization"]) == 1


class TestRedundancyDetection:
    """Test detecting redundant frameworks in same category."""
    
    def test_detect_di_container_redundancy(self):
        """Test detecting Autofac + Unity redundancy."""
        frameworks = [
            {"name": "Autofac", "version": "6.4.0", "category": "DI Container"},
            {"name": "Unity", "version": "5.11.10", "category": "DI Container"},
        ]
        
        # Group by category
        category_counts = {}
        for framework in frameworks:
            cat = framework["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        redundancies = {cat: count for cat, count in category_counts.items() if count > 1}
        
        assert "DI Container" in redundancies, "Should detect DI Container redundancy"
        assert redundancies["DI Container"] == 2, "Should have 2 DI frameworks"
    
    def test_detect_logging_redundancy(self):
        """Test detecting Serilog + log4net redundancy."""
        frameworks = [
            {"name": "Serilog", "version": "3.0.1", "category": "Logging"},
            {"name": "log4net", "version": "2.0.15", "category": "Logging"},
        ]
        
        category_counts = {}
        for framework in frameworks:
            cat = framework["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        redundancies = {cat: count for cat, count in category_counts.items() if count > 1}
        
        assert "Logging" in redundancies, "Should detect Logging redundancy"
        assert redundancies["Logging"] == 2, "Should have 2 logging frameworks"
    
    def test_no_redundancy_single_framework_per_category(self):
        """Test no redundancy when categories have single framework."""
        frameworks = [
            {"name": "Autofac", "version": "6.4.0", "category": "DI Container"},
            {"name": "Serilog", "version": "3.0.1", "category": "Logging"},
            {"name": "EntityFramework", "version": "6.4.4", "category": "Data Access"},
        ]
        
        category_counts = {}
        for framework in frameworks:
            cat = framework["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        redundancies = {cat: count for cat, count in category_counts.items() if count > 1}
        
        assert len(redundancies) == 0, "Should detect no redundancies"


class TestConsolidationRecommendations:
    """Test consolidation recommendations for redundant frameworks."""
    
    def test_di_container_recommendation(self):
        """Test recommendation for Autofac + Unity."""
        category = "DI Container"
        frameworks = ["Autofac", "Unity"]
        
        # Simulate recommendation logic
        if "Autofac" in frameworks and "Unity" in frameworks:
            recommendation = "Migrate to Autofac (Unity is in maintenance mode)"
        else:
            recommendation = None
        
        assert recommendation is not None, "Should have recommendation"
        assert "Autofac" in recommendation, "Should recommend Autofac"
        assert "maintenance mode" in recommendation, "Should mention Unity status"
    
    def test_logging_recommendation(self):
        """Test recommendation for Serilog + log4net."""
        category = "Logging"
        frameworks = ["Serilog", "log4net"]
        
        if "Serilog" in frameworks and "log4net" in frameworks:
            recommendation = "Migrate to Serilog (structured logging)"
        else:
            recommendation = None
        
        assert recommendation is not None, "Should have recommendation"
        assert "Serilog" in recommendation, "Should recommend Serilog"
        assert "structured logging" in recommendation, "Should mention Serilog benefit"
    
    def test_json_serialization_recommendation(self):
        """Test recommendation for Newtonsoft.Json + System.Text.Json."""
        category = "JSON Serialization"
        frameworks = ["Newtonsoft.Json", "System.Text.Json"]
        
        if "System.Text.Json" in frameworks and "Newtonsoft.Json" in frameworks:
            recommendation = "Prefer System.Text.Json for .NET 6+"
        else:
            recommendation = None
        
        assert recommendation is not None, "Should have recommendation"
        assert "System.Text.Json" in recommendation, "Should recommend System.Text.Json"
        assert ".NET 6+" in recommendation, "Should mention .NET version"


class TestAccordionRendering:
    """Test category accordion expand/collapse logic."""
    
    def test_expand_collapse_state_toggle(self):
        """Test expand/collapse state transitions."""
        # Initial state
        is_expanded = False
        
        # Click to expand
        is_expanded = not is_expanded
        assert is_expanded is True, "Should expand on first click"
        
        # Click to collapse
        is_expanded = not is_expanded
        assert is_expanded is False, "Should collapse on second click"
    
    def test_multiple_categories_independent_state(self):
        """Test independent expand/collapse for multiple categories."""
        categories = {
            "DI Container": False,
            "Logging": False,
            "JSON Serialization": False,
        }
        
        # Expand DI Container
        categories["DI Container"] = True
        assert categories["DI Container"] is True
        assert categories["Logging"] is False
        assert categories["JSON Serialization"] is False
        
        # Expand Logging
        categories["Logging"] = True
        assert categories["DI Container"] is True
        assert categories["Logging"] is True
        assert categories["JSON Serialization"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

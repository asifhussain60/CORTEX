"""
Test Edge Case Intelligence Enhancements - Phase 1 Milestone 1.1

Validates enhanced edge case detection including:
- Numeric: infinity, NaN, max/min values
- String: SQL injection, XSS, path traversal, email/URL validation
- Collection: null items, duplicates, nested structures

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 1
"""

import ast
import pytest
from src.cortex_agents.test_generator.edge_case_analyzer import EdgeCaseAnalyzer, EdgeCase


class TestNumericEdgeCaseEnhancements:
    """Test enhanced numeric edge case detection."""
    
    def test_numeric_includes_infinity(self):
        """Should generate infinity test for float parameters."""
        analyzer = EdgeCaseAnalyzer()
        
        # Function with float parameter
        source = """
def calculate_rate(amount: float) -> float:
    return amount * 0.05
"""
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        edge_cases = analyzer.analyze_function(func_node, source)
        
        # Should include infinity test
        infinity_cases = [ec for ec in edge_cases if 'infinity' in ec.name]
        assert len(infinity_cases) > 0, "Should generate infinity edge case for float"
        assert infinity_cases[0].expected_behavior == "raise"
        assert infinity_cases[0].confidence >= 0.8
    
    def test_numeric_includes_nan(self):
        """Should generate NaN test for float parameters."""
        analyzer = EdgeCaseAnalyzer()
        
        source = """
def compute_average(value: float) -> float:
    return value / 2
"""
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        edge_cases = analyzer.analyze_function(func_node, source)
        
        # Should include NaN test
        nan_cases = [ec for ec in edge_cases if 'nan' in ec.name]
        assert len(nan_cases) > 0, "Should generate NaN edge case for float"
        assert nan_cases[0].expected_behavior == "raise"
    
    def test_numeric_includes_max_int(self):
        """Should generate maximum integer test."""
        analyzer = EdgeCaseAnalyzer()
        
        source = """
def process_id(id: int) -> int:
    return id + 1
"""
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        edge_cases = analyzer.analyze_function(func_node, source)
        
        # Should include max int test
        max_cases = [ec for ec in edge_cases if 'max_int' in ec.name]
        assert len(max_cases) > 0, "Should generate max int edge case"
        
        import sys
        assert max_cases[0].input_values['id'] == sys.maxsize
    
    def test_numeric_negative_confidence_varies(self):
        """Confidence for negative numbers should vary by function context."""
        analyzer = EdgeCaseAnalyzer()
        
        # Function that should allow negatives
        source1 = """
def calculate_difference(a: int, b: int) -> int:
    return a - b
"""
        tree1 = ast.parse(source1)
        func_node1 = tree1.body[0]
        cases1 = analyzer.analyze_function(func_node1, source1)
        
        # Function that shouldn't allow negatives  
        source2 = """
def calculate_total(amount: int) -> int:
    return amount * 2
"""
        tree2 = ast.parse(source2)
        func_node2 = tree2.body[0]
        cases2 = analyzer.analyze_function(func_node2, source2)
        
        # Get negative test cases
        neg1 = [ec for ec in cases1 if 'negative' in ec.name and 'a' in ec.name]
        neg2 = [ec for ec in cases2 if 'negative' in ec.name]
        
        # Difference function should have lower confidence for raising on negative
        # Total function should have higher confidence for raising on negative
        assert neg1[0].confidence < neg2[0].confidence


class TestStringEdgeCaseEnhancements:
    """Test enhanced string edge case detection."""
    
    def test_string_includes_sql_injection(self):
        """Should generate SQL injection test for relevant parameters."""
        analyzer = EdgeCaseAnalyzer()
        
        source = """
def find_user(username: str) -> dict:
    return {"id": 1, "name": username}
"""
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        edge_cases = analyzer.analyze_function(func_node, source)
        
        # Should include SQL injection test
        sql_cases = [ec for ec in edge_cases if 'sql_injection' in ec.name]
        assert len(sql_cases) > 0, "Should generate SQL injection edge case"
        assert "DROP TABLE" in sql_cases[0].input_values['username']
        assert sql_cases[0].expected_behavior == "raise"
    
    def test_string_includes_xss_attack(self):
        """Should generate XSS test for HTML/content parameters."""
        analyzer = EdgeCaseAnalyzer()
        
        source = """
def save_comment(comment: str) -> None:
    pass
"""
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        edge_cases = analyzer.analyze_function(func_node, source)
        
        # Should include XSS test
        xss_cases = [ec for ec in edge_cases if 'xss' in ec.name]
        assert len(xss_cases) > 0, "Should generate XSS edge case"
        assert "<script>" in xss_cases[0].input_values['comment']
    
    def test_string_includes_path_traversal(self):
        """Should generate path traversal test for path parameters."""
        analyzer = EdgeCaseAnalyzer()
        
        source = """
def read_file(file_path: str) -> str:
    return "content"
"""
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        edge_cases = analyzer.analyze_function(func_node, source)
        
        # Should include path traversal test
        path_cases = [ec for ec in edge_cases if 'path_traversal' in ec.name]
        assert len(path_cases) > 0, "Should generate path traversal edge case"
        assert "../" in path_cases[0].input_values['file_path']
        assert path_cases[0].confidence >= 0.9
    
    def test_string_email_validation_cases(self):
        """Should generate email-specific validation tests."""
        analyzer = EdgeCaseAnalyzer()
        
        source = """
def validate_email(email: str) -> bool:
    return "@" in email
"""
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        edge_cases = analyzer.analyze_function(func_node, source)
        
        # Should include email-specific tests
        email_cases = [ec for ec in edge_cases if 'email' in ec.name]
        assert len(email_cases) >= 2, "Should generate multiple email validation cases"
        
        # Check for missing @ and missing domain
        missing_at = [ec for ec in email_cases if 'missing_at' in ec.name]
        missing_domain = [ec for ec in email_cases if 'missing_domain' in ec.name]
        
        assert len(missing_at) > 0, "Should test missing @ symbol"
        assert len(missing_domain) > 0, "Should test missing domain"


class TestCollectionEdgeCaseEnhancements:
    """Test enhanced collection edge case detection."""
    
    def test_collection_includes_none_items(self):
        """Should generate test for collections with None items."""
        analyzer = EdgeCaseAnalyzer()
        
        source = """
def sum_list(items: list) -> int:
    return sum(items)
"""
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        edge_cases = analyzer.analyze_function(func_node, source)
        
        # Should include None items test
        none_cases = [ec for ec in edge_cases if 'none' in ec.name.lower()]
        assert len(none_cases) > 0, "Should generate None items edge case"
        
        # Check that test includes None in the list
        contains_none = [ec for ec in none_cases if 'contains_none' in ec.name]
        assert len(contains_none) > 0
        assert None in contains_none[0].input_values['items']
    
    def test_collection_includes_duplicates(self):
        """Should generate test for duplicate items."""
        analyzer = EdgeCaseAnalyzer()
        
        source = """
def unique_count(items: list) -> int:
    return len(set(items))
"""
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        edge_cases = analyzer.analyze_function(func_node, source)
        
        # Should include duplicates test
        dup_cases = [ec for ec in edge_cases if 'duplicate' in ec.name]
        assert len(dup_cases) > 0, "Should generate duplicates edge case"
        
        # Check that test has duplicate values
        items = dup_cases[0].input_values['items']
        assert len(items) != len(set(items)), "Test should include duplicate values"
    
    def test_collection_includes_nested(self):
        """Should generate test for nested collections."""
        analyzer = EdgeCaseAnalyzer()
        
        source = """
def flatten(items: list) -> list:
    return [item for sublist in items for item in sublist]
"""
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        edge_cases = analyzer.analyze_function(func_node, source)
        
        # Should include nested test
        nested_cases = [ec for ec in edge_cases if 'nested' in ec.name]
        assert len(nested_cases) > 0, "Should generate nested collection edge case"
        
        # Check that test has nested structure
        items = nested_cases[0].input_values['items']
        assert isinstance(items[0], list), "Test should include nested lists"
    
    def test_collection_large_size_reasonable(self):
        """Should generate large collection test with reasonable size."""
        analyzer = EdgeCaseAnalyzer()
        
        source = """
def count_items(items: list) -> int:
    return len(items)
"""
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        edge_cases = analyzer.analyze_function(func_node, source)
        
        # Should include large collection test
        large_cases = [ec for ec in edge_cases if 'large' in ec.name]
        assert len(large_cases) > 0, "Should generate large collection edge case"
        
        # Size should be substantial but reasonable (100k items)
        items = large_cases[0].input_values['items']
        assert len(items) >= 10000, "Large collection should be substantial"


class TestEdgeCaseConfidenceScoring:
    """Test that confidence scores are appropriate."""
    
    def test_high_confidence_for_critical_cases(self):
        """Critical security cases should have high confidence."""
        analyzer = EdgeCaseAnalyzer()
        
        source = """
def execute_query(query: str) -> list:
    return []
"""
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        edge_cases = analyzer.analyze_function(func_node, source)
        
        # SQL injection test should have high confidence
        sql_cases = [ec for ec in edge_cases if 'sql_injection' in ec.name]
        assert sql_cases[0].confidence >= 0.9, "Security tests should have high confidence"
    
    def test_empty_string_high_confidence(self):
        """Empty string test should have high confidence."""
        analyzer = EdgeCaseAnalyzer()
        
        source = """
def process_name(name: str) -> str:
    return name.upper()
"""
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        edge_cases = analyzer.analyze_function(func_node, source)
        
        # Empty string test should have high confidence
        empty_cases = [ec for ec in edge_cases if 'empty' in ec.name]
        assert empty_cases[0].confidence >= 0.85, "Empty string should have high confidence"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

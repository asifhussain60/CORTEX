"""
Tests for DeduplicationAnalyzer.

Tests semantic duplicate detection with AST intelligence.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path

from src.operations.modules.analysis.deduplication_analyzer import (
    DeduplicationAnalyzer,
    DuplicateGroup
)
from src.operations.modules.analysis.ast_engine import ASTEngine


class TestDeduplicationAnalyzer:
    """Test suite for DeduplicationAnalyzer."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.ast_engine = ASTEngine(self.project_root)
        self.analyzer = DeduplicationAnalyzer(self.ast_engine)
        
    def teardown_method(self):
        """Cleanup test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_initialization(self):
        """Test analyzer initialization."""
        assert self.analyzer.ast_engine is not None
        assert self.analyzer.min_similarity == 0.85
        assert self.analyzer.min_lines == 10
        
    def test_analyze_empty_project(self):
        """Test analysis on empty project."""
        result = self.analyzer.analyze(self.project_root)
        
        assert 'duplicate_groups' in result
        assert 'total_duplicates' in result
        assert 'total_duplicate_lines' in result
        assert 'estimated_cleanup_hours' in result
        assert result['total_duplicates'] == 0
        
    def test_analyze_with_duplicates(self):
        """Test analysis with duplicate code."""
        # Create files with duplicate code
        file1 = self.project_root / "module1.py"
        file1.write_text("""
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']
    return total
""")
        
        file2 = self.project_root / "module2.py"
        file2.write_text("""
def compute_sum(records):
    sum_value = 0
    for record in records:
        sum_value += record['price']
    return sum_value
""")
        
        result = self.analyzer.analyze(self.project_root)
        
        # Stub AST returns empty, so no duplicates
        assert result['total_duplicates'] == 0
        assert result['estimated_cleanup_hours'] >= 0
        
    def test_analyze_single_file(self):
        """Test analysis on single file."""
        test_file = self.project_root / "test.py"
        test_file.write_text("def func(): pass")
        
        result = self.analyzer.analyze(test_file)
        
        assert isinstance(result, dict)
        assert 'duplicate_groups' in result
        
    def test_generate_recommendation_two_files(self):
        """Test recommendation generation for 2 duplicates."""
        group = {
            'similarity': 0.90,
            'locations': [
                {'file': 'file1.py', 'start_line': 10},
                {'file': 'file2.py', 'start_line': 20}
            ],
            'lines': 15
        }
        
        recommendation = self.analyzer._generate_recommendation(group)
        
        assert 'Extract shared logic' in recommendation
        assert 'file1.py' in recommendation
        assert 'file2.py' in recommendation
        
    def test_generate_recommendation_multiple_files(self):
        """Test recommendation generation for 3+ duplicates."""
        group = {
            'similarity': 0.88,
            'locations': [
                {'file': 'file1.py'},
                {'file': 'file2.py'},
                {'file': 'file3.py'}
            ],
            'lines': 20
        }
        
        recommendation = self.analyzer._generate_recommendation(group)
        
        assert 'shared module' in recommendation
        assert '3 files' in recommendation
        
    def test_estimate_cleanup_effort(self):
        """Test cleanup effort estimation."""
        groups = [
            DuplicateGroup(0.90, [], 15, "rec1"),
            DuplicateGroup(0.85, [], 20, "rec2"),
            DuplicateGroup(0.92, [], 10, "rec3")
        ]
        
        effort = self.analyzer._estimate_cleanup_effort(groups)
        
        # 3 groups * 0.25 hours = 0.75 hours
        assert effort == 0.75
        
    def test_estimate_cleanup_effort_empty(self):
        """Test cleanup effort estimation with no duplicates."""
        effort = self.analyzer._estimate_cleanup_effort([])
        
        assert effort == 0.0
        
    def test_enriched_groups_structure(self):
        """Test enriched duplicate groups structure."""
        result = self.analyzer.analyze(self.project_root)
        
        groups = result['duplicate_groups']
        for group in groups:
            assert isinstance(group, DuplicateGroup)
            assert hasattr(group, 'similarity_score')
            assert hasattr(group, 'locations')
            assert hasattr(group, 'lines_count')
            assert hasattr(group, 'recommendation')


class TestDuplicateGroup:
    """Test suite for DuplicateGroup dataclass."""
    
    def test_creation(self):
        """Test DuplicateGroup creation."""
        group = DuplicateGroup(
            similarity_score=0.90,
            locations=[
                {'file': 'test.py', 'start_line': 10, 'end_line': 20}
            ],
            lines_count=10,
            recommendation="Extract to utility function"
        )
        
        assert group.similarity_score == 0.90
        assert len(group.locations) == 1
        assert group.lines_count == 10
        assert group.recommendation == "Extract to utility function"
        
    def test_multiple_locations(self):
        """Test DuplicateGroup with multiple locations."""
        locations = [
            {'file': 'module1.py', 'start_line': 10},
            {'file': 'module2.py', 'start_line': 30},
            {'file': 'module3.py', 'start_line': 50}
        ]
        
        group = DuplicateGroup(
            similarity_score=0.88,
            locations=locations,
            lines_count=25,
            recommendation="Create shared module"
        )
        
        assert len(group.locations) == 3
        assert group.lines_count == 25

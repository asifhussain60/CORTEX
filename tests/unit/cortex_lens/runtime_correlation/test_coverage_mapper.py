"""
Tests for Coverage Mapper

Validates mapping of test coverage data to code paths for knowledge graph integration.

Author: CORTEX Architect
Phase: Phase 66 S4
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List


class TestCoverageMapper:
    """Test suite for test coverage mapping"""
    
    def test_parse_coverage_data(self):
        """Test parsing pytest-cov coverage data"""
        from cortex_lens.runtime_correlation.coverage_mapper import CoverageMapper
        
        coverage_data = {
            "files": {
                "cortex/orchestrators/master.py": {
                    "summary": {"covered_lines": 45, "num_statements": 50, "percent_covered": 90.0},
                    "executed_lines": [1, 2, 3, 5, 10, 15, 20],
                    "missing_lines": [4, 6, 7, 8, 9]
                },
                "cortex/models/phase.py": {
                    "summary": {"covered_lines": 30, "num_statements": 40, "percent_covered": 75.0},
                    "executed_lines": [1, 2, 3, 5, 10],
                    "missing_lines": [4, 6, 7, 8, 9, 11, 12, 13, 14, 15]
                }
            }
        }
        
        mapper = CoverageMapper()
        parsed = mapper.parse_coverage_data(coverage_data)
        
        assert len(parsed) == 2
        assert parsed[0]["file"] == "cortex/orchestrators/master.py"
        assert parsed[0]["coverage_percent"] == 90.0
        assert parsed[0]["covered_lines"] == 45  # Count, not list
        assert len(parsed[0]["executed_lines"]) == 7  # This is the list
        assert len(parsed[0]["missing_lines"]) == 5
    
    def test_map_tests_to_coverage(self):
        """Test mapping tests to their coverage footprint"""
        from cortex_lens.runtime_correlation.coverage_mapper import CoverageMapper
        
        test_results = [
            {"test_id": "tests/test_orchestrator.py::test_process", "outcome": "passed"},
            {"test_id": "tests/test_phase.py::test_create", "outcome": "passed"}
        ]
        
        coverage_by_test = {
            "tests/test_orchestrator.py::test_process": {
                "covered_files": ["cortex/orchestrators/master.py"],
                "line_count": 45
            },
            "tests/test_phase.py::test_create": {
                "covered_files": ["cortex/models/phase.py"],
                "line_count": 30
            }
        }
        
        mapper = CoverageMapper()
        mappings = mapper.map_tests_to_coverage(test_results, coverage_by_test)
        
        assert len(mappings) == 2
        assert mappings[0]["test_id"] == "tests/test_orchestrator.py::test_process"
        assert "cortex/orchestrators/master.py" in mappings[0]["covered_files"]
    
    def test_identify_uncovered_lines(self):
        """Test identifying uncovered lines in files"""
        from cortex_lens.runtime_correlation.coverage_mapper import CoverageMapper
        
        coverage_data = {
            "files": {
                "cortex/utils/helpers.py": {
                    "summary": {"covered_lines": 20, "num_statements": 30},
                    "executed_lines": list(range(1, 21)),
                    "missing_lines": list(range(21, 31))
                }
            }
        }
        
        mapper = CoverageMapper()
        uncovered = mapper.identify_uncovered_lines(coverage_data)
        
        assert len(uncovered) == 1
        assert uncovered[0]["file"] == "cortex/utils/helpers.py"
        assert len(uncovered[0]["missing_lines"]) == 10
        assert uncovered[0]["coverage_percent"] < 100.0
    
    def test_calculate_file_coverage_score(self):
        """Test calculating coverage score for files"""
        from cortex_lens.runtime_correlation.coverage_mapper import CoverageMapper
        
        file_coverage = {
            "covered_lines": 45,
            "num_statements": 50,
            "percent_covered": 90.0
        }
        
        mapper = CoverageMapper()
        score = mapper.calculate_file_coverage_score(file_coverage)
        
        assert score == 90.0
        assert 0.0 <= score <= 100.0
    
    def test_aggregate_coverage_by_module(self):
        """Test aggregating coverage statistics by module"""
        from cortex_lens.runtime_correlation.coverage_mapper import CoverageMapper
        
        coverage_data = {
            "files": {
                "cortex/orchestrators/master.py": {
                    "summary": {"covered_lines": 45, "num_statements": 50}
                },
                "cortex/orchestrators/intent.py": {
                    "summary": {"covered_lines": 30, "num_statements": 40}
                },
                "cortex/models/phase.py": {
                    "summary": {"covered_lines": 20, "num_statements": 25}
                }
            }
        }
        
        mapper = CoverageMapper()
        by_module = mapper.aggregate_coverage_by_module(coverage_data)
        
        assert "cortex/orchestrators" in by_module
        assert "cortex/models" in by_module
        
        orchestrators = by_module["cortex/orchestrators"]
        assert orchestrators["total_lines"] == 90  # 50 + 40
        assert orchestrators["covered_lines"] == 75  # 45 + 30
    
    def test_detect_critical_uncovered_paths(self):
        """Test detecting critical paths with low coverage"""
        from cortex_lens.runtime_correlation.coverage_mapper import CoverageMapper
        
        coverage_data = {
            "files": {
                "cortex/security/validator.py": {
                    "summary": {"covered_lines": 10, "num_statements": 50, "percent_covered": 20.0}
                },
                "cortex/orchestrators/master.py": {
                    "summary": {"covered_lines": 45, "num_statements": 50, "percent_covered": 90.0}
                }
            }
        }
        
        mapper = CoverageMapper()
        critical = mapper.detect_critical_uncovered_paths(coverage_data, threshold=70.0)
        
        assert len(critical) >= 1
        assert any("security" in c["file"] for c in critical)
        assert all(c["coverage_percent"] < 70.0 for c in critical)
    
    def test_build_coverage_graph_edges(self):
        """Test building graph edges from coverage data"""
        from cortex_lens.runtime_correlation.coverage_mapper import CoverageMapper
        
        test_coverage = {
            "tests/test_orchestrator.py::test_process": {
                "covered_files": ["cortex/orchestrators/master.py", "cortex/models/phase.py"]
            }
        }
        
        mapper = CoverageMapper()
        edges = mapper.build_coverage_graph_edges(test_coverage)
        
        assert len(edges) >= 2
        assert all(e["type"] == "covers" for e in edges)
        assert all("source" in e and "target" in e for e in edges)
    
    def test_identify_test_gaps(self):
        """Test identifying files with insufficient test coverage"""
        from cortex_lens.runtime_correlation.coverage_mapper import CoverageMapper
        
        coverage_data = {
            "files": {
                "cortex/core/important.py": {
                    "summary": {"covered_lines": 5, "num_statements": 50, "percent_covered": 10.0}
                },
                "cortex/utils/helper.py": {
                    "summary": {"covered_lines": 40, "num_statements": 50, "percent_covered": 80.0}
                }
            }
        }
        
        mapper = CoverageMapper()
        gaps = mapper.identify_test_gaps(coverage_data, min_coverage=60.0)
        
        assert len(gaps) >= 1
        assert any("important" in g["file"] for g in gaps)
        assert all(g["coverage_percent"] < 60.0 for g in gaps)
    
    def test_calculate_test_redundancy(self):
        """Test detecting redundant tests (same coverage footprint)"""
        from cortex_lens.runtime_correlation.coverage_mapper import CoverageMapper
        
        test_coverage = {
            "tests/test_a.py::test_1": {
                "covered_files": ["cortex/module.py"],
                "covered_lines": [1, 2, 3, 4, 5]
            },
            "tests/test_b.py::test_2": {
                "covered_files": ["cortex/module.py"],
                "covered_lines": [1, 2, 3, 4, 5]  # Same coverage
            },
            "tests/test_c.py::test_3": {
                "covered_files": ["cortex/other.py"],
                "covered_lines": [10, 20, 30]
            }
        }
        
        mapper = CoverageMapper()
        redundant = mapper.calculate_test_redundancy(test_coverage)
        
        assert len(redundant) >= 1
        # Should detect test_1 and test_2 as redundant
        assert any(
            set(r["tests"]) == {"tests/test_a.py::test_1", "tests/test_b.py::test_2"}
            for r in redundant
        )
    
    def test_map_coverage_to_functions(self):
        """Test mapping coverage to individual functions"""
        from cortex_lens.runtime_correlation.coverage_mapper import CoverageMapper
        
        coverage_data = {
            "files": {
                "cortex/module.py": {
                    "summary": {"covered_lines": 20, "num_statements": 30},
                    "executed_lines": [1, 2, 3, 10, 11, 12, 20, 21, 22],
                    "missing_lines": [4, 5, 13, 14, 15, 23, 24, 25]
                }
            }
        }
        
        function_definitions = {
            "cortex/module.py": [
                {"name": "func_a", "start_line": 1, "end_line": 5},
                {"name": "func_b", "start_line": 10, "end_line": 15},
                {"name": "func_c", "start_line": 20, "end_line": 25}
            ]
        }
        
        mapper = CoverageMapper()
        func_coverage = mapper.map_coverage_to_functions(coverage_data, function_definitions)
        
        assert len(func_coverage) >= 3
        assert any(f["function"] == "func_a" for f in func_coverage)
        # func_a (lines 1-5): has covered lines 1,2,3 and missing 4,5
        func_a = next(f for f in func_coverage if f["function"] == "func_a")
        assert func_a["coverage_percent"] == 60.0  # 3/5 lines covered


class TestCoverageMapperIntegration:
    """Integration tests for coverage mapper"""
    
    def test_end_to_end_coverage_analysis(self):
        """Test complete coverage analysis workflow"""
        from cortex_lens.runtime_correlation.coverage_mapper import CoverageMapper
        
        coverage_data = {
            "files": {
                "cortex/orchestrators/master.py": {
                    "summary": {"covered_lines": 45, "num_statements": 50, "percent_covered": 90.0},
                    "executed_lines": list(range(1, 46)),
                    "missing_lines": [46, 47, 48, 49, 50]
                },
                "cortex/models/phase.py": {
                    "summary": {"covered_lines": 30, "num_statements": 40, "percent_covered": 75.0},
                    "executed_lines": list(range(1, 31)),
                    "missing_lines": list(range(31, 41))
                }
            }
        }
        
        mapper = CoverageMapper()
        
        # Parse coverage
        parsed = mapper.parse_coverage_data(coverage_data)
        assert len(parsed) == 2
        
        # Identify uncovered
        uncovered = mapper.identify_uncovered_lines(coverage_data)
        assert len(uncovered) == 2
        
        # Aggregate by module
        by_module = mapper.aggregate_coverage_by_module(coverage_data)
        assert "cortex/orchestrators" in by_module
        
        # Detect critical paths
        critical = mapper.detect_critical_uncovered_paths(coverage_data, threshold=80.0)
        assert any("phase" in c["file"] for c in critical)  # 75% < 80%

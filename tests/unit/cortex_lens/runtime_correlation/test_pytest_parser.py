"""
Tests for Pytest JSON Output Parser

Validates parsing of pytest --json output into execution traces for knowledge graph.

Author: CORTEX Architect
Phase: Phase 66 S4
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any, List


class TestPytestParser:
    """Test suite for pytest JSON output parsing"""
    
    def test_parse_test_results(self):
        """Test parsing basic test results from pytest JSON"""
        from cortex_lens.runtime_correlation.pytest_parser import PytestParser
        
        json_data = {
            "tests": [
                {
                    "nodeid": "tests/test_user.py::test_create_user",
                    "outcome": "passed",
                    "duration": 0.123,
                    "call": {
                        "longrepr": None
                    }
                },
                {
                    "nodeid": "tests/test_user.py::test_delete_user",
                    "outcome": "failed",
                    "duration": 0.045,
                    "call": {
                        "longrepr": "AssertionError: User not deleted"
                    }
                }
            ],
            "summary": {
                "passed": 1,
                "failed": 1,
                "total": 2
            }
        }
        
        parser = PytestParser()
        results = parser.parse_test_results(json_data)
        
        assert len(results) == 2
        assert results[0]["test_id"] == "tests/test_user.py::test_create_user"
        assert results[0]["outcome"] == "passed"
        assert results[0]["duration"] == 0.123
        assert results[1]["outcome"] == "failed"
    
    def test_extract_test_file_mapping(self):
        """Test extracting test → source file relationships"""
        from cortex_lens.runtime_correlation.pytest_parser import PytestParser
        
        json_data = {
            "tests": [
                {
                    "nodeid": "tests/unit/cortex/test_orchestrator.py::test_process",
                    "outcome": "passed"
                },
                {
                    "nodeid": "tests/integration/test_mcp_tools.py::test_tool_invocation",
                    "outcome": "passed"
                }
            ]
        }
        
        parser = PytestParser()
        mappings = parser.extract_test_file_mapping(json_data)
        
        assert len(mappings) >= 2
        assert mappings[0]["test_file"] == "tests/unit/cortex/test_orchestrator.py"
        assert mappings[0]["test_name"] == "test_process"
        # Should infer source file from test path
        assert "cortex" in mappings[0]["inferred_source"]
    
    def test_parse_call_chain(self):
        """Test extracting call chains from pytest output"""
        from cortex_lens.runtime_correlation.pytest_parser import PytestParser
        
        # Simulate pytest traceback with call chain
        traceback_data = {
            "reprcrash": {
                "path": "cortex/orchestrators/master.py",
                "lineno": 45,
                "message": "ValueError"
            },
            "reprtraceback": {
                "entries": [
                    {
                        "path": "tests/test_orchestrator.py",
                        "lineno": 10,
                        "reprfuncargs": "request='test'"
                    },
                    {
                        "path": "cortex/orchestrators/master.py",
                        "lineno": 45,
                        "reprfuncargs": "data='test'"
                    }
                ]
            }
        }
        
        parser = PytestParser()
        call_chain = parser.parse_call_chain(traceback_data)
        
        assert len(call_chain) >= 2
        assert call_chain[0]["file"] == "tests/test_orchestrator.py"
        assert call_chain[1]["file"] == "cortex/orchestrators/master.py"
    
    def test_extract_test_fixtures(self):
        """Test extracting fixture dependencies"""
        from cortex_lens.runtime_correlation.pytest_parser import PytestParser
        
        json_data = {
            "tests": [
                {
                    "nodeid": "tests/test_db.py::test_query",
                    "setup": {
                        "outcome": "passed",
                        "duration": 0.05
                    },
                    "call": {
                        "outcome": "passed",
                        "duration": 0.1
                    },
                    "teardown": {
                        "outcome": "passed",
                        "duration": 0.02
                    }
                }
            ]
        }
        
        parser = PytestParser()
        fixtures = parser.extract_test_fixtures(json_data)
        
        # Should detect setup/teardown phases
        assert len(fixtures) >= 1
        test_fixtures = fixtures[0]
        assert test_fixtures["test_id"] == "tests/test_db.py::test_query"
        assert "setup_duration" in test_fixtures
        assert "teardown_duration" in test_fixtures
    
    def test_aggregate_test_statistics(self):
        """Test aggregating test execution statistics"""
        from cortex_lens.runtime_correlation.pytest_parser import PytestParser
        
        json_data = {
            "tests": [
                {"nodeid": "tests/test_a.py::test_1", "outcome": "passed", "duration": 0.1},
                {"nodeid": "tests/test_a.py::test_2", "outcome": "passed", "duration": 0.15},
                {"nodeid": "tests/test_b.py::test_3", "outcome": "failed", "duration": 0.05},
                {"nodeid": "tests/test_b.py::test_4", "outcome": "skipped", "duration": 0.0}
            ],
            "summary": {
                "passed": 2,
                "failed": 1,
                "skipped": 1,
                "total": 4,
                "duration": 0.3
            }
        }
        
        parser = PytestParser()
        stats = parser.aggregate_test_statistics(json_data)
        
        assert stats["total_tests"] == 4
        assert stats["passed"] == 2
        assert stats["failed"] == 1
        assert stats["skipped"] == 1
        assert stats["total_duration"] == 0.3
        assert stats["avg_duration"] > 0
    
    def test_parse_parametrized_tests(self):
        """Test parsing parametrized test results"""
        from cortex_lens.runtime_correlation.pytest_parser import PytestParser
        
        json_data = {
            "tests": [
                {
                    "nodeid": "tests/test_calc.py::test_add[1-2-3]",
                    "outcome": "passed",
                    "duration": 0.01
                },
                {
                    "nodeid": "tests/test_calc.py::test_add[5-5-10]",
                    "outcome": "passed",
                    "duration": 0.01
                }
            ]
        }
        
        parser = PytestParser()
        results = parser.parse_parametrized_tests(json_data)
        
        assert len(results) >= 2
        # Should group by base test name
        assert all("test_add" in r["base_test"] for r in results)
        assert results[0]["parameters"] != results[1]["parameters"]
    
    def test_detect_flaky_tests(self):
        """Test detecting flaky tests from multiple runs"""
        from cortex_lens.runtime_correlation.pytest_parser import PytestParser
        
        # Simulate multiple test runs
        run1 = {"tests": [{"nodeid": "tests/test_net.py::test_api", "outcome": "passed"}]}
        run2 = {"tests": [{"nodeid": "tests/test_net.py::test_api", "outcome": "failed"}]}
        run3 = {"tests": [{"nodeid": "tests/test_net.py::test_api", "outcome": "passed"}]}
        
        parser = PytestParser()
        flaky_tests = parser.detect_flaky_tests([run1, run2, run3])
        
        assert len(flaky_tests) >= 1
        assert "tests/test_net.py::test_api" in [t["test_id"] for t in flaky_tests]
        assert flaky_tests[0]["flakiness_rate"] > 0  # Should detect inconsistency
    
    def test_extract_test_markers(self):
        """Test extracting pytest markers (slow, integration, etc.)"""
        from cortex_lens.runtime_correlation.pytest_parser import PytestParser
        
        json_data = {
            "tests": [
                {
                    "nodeid": "tests/test_slow.py::test_heavy",
                    "keywords": ["slow", "integration", "database"],
                    "outcome": "passed"
                }
            ]
        }
        
        parser = PytestParser()
        markers = parser.extract_test_markers(json_data)
        
        assert len(markers) >= 1
        test_markers = markers[0]
        assert "slow" in test_markers["markers"]
        assert "integration" in test_markers["markers"]
    
    def test_build_test_dependency_graph(self):
        """Test building test dependency graph from execution order"""
        from cortex_lens.runtime_correlation.pytest_parser import PytestParser
        
        json_data = {
            "tests": [
                {
                    "nodeid": "tests/test_a.py::test_setup",
                    "outcome": "passed",
                    "duration": 0.1
                },
                {
                    "nodeid": "tests/test_b.py::test_depends_on_setup",
                    "outcome": "passed",
                    "duration": 0.05
                }
            ]
        }
        
        parser = PytestParser()
        graph = parser.build_test_dependency_graph(json_data)
        
        # Should create nodes for each test
        assert len(graph["nodes"]) == 2
        # Should detect implicit dependencies (setup → dependent test)
        assert "edges" in graph


class TestPytestParserIntegration:
    """Integration tests for pytest parser with real data"""
    
    def test_parse_cortex_test_output(self):
        """Test parsing actual CORTEX pytest output"""
        from cortex_lens.runtime_correlation.pytest_parser import PytestParser
        
        # Simulate realistic CORTEX test output
        cortex_json = {
            "tests": [
                {
                    "nodeid": "tests/unit/cortex/orchestrators/test_master.py::TestMasterOrchestrator::test_process_request",
                    "outcome": "passed",
                    "duration": 0.234,
                    "keywords": ["unit", "orchestrator"]
                },
                {
                    "nodeid": "tests/integration/test_mcp_gateway.py::test_tool_invocation",
                    "outcome": "passed",
                    "duration": 1.456,
                    "keywords": ["integration", "slow"]
                }
            ],
            "summary": {
                "passed": 2,
                "failed": 0,
                "total": 2,
                "duration": 1.69
            }
        }
        
        parser = PytestParser()
        
        # Parse all data
        results = parser.parse_test_results(cortex_json)
        mappings = parser.extract_test_file_mapping(cortex_json)
        stats = parser.aggregate_test_statistics(cortex_json)
        markers = parser.extract_test_markers(cortex_json)
        
        # Validate parsing
        assert len(results) == 2
        assert len(mappings) == 2
        assert stats["passed"] == 2
        assert any("integration" in m["markers"] for m in markers)
        
        # Check source file inference
        assert any("master" in m["inferred_source"].lower() for m in mappings)

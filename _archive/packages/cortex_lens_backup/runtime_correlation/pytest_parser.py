"""
Pytest JSON Output Parser

Parses pytest --json output into structured execution traces for knowledge graph integration.
Supports test results, call chains, fixtures, and statistical analysis.

Author: CORTEX Architect
Phase: Phase 66 S4
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict
import re


class PytestParser:
    """
    Parse pytest JSON output into execution traces.
    
    Capabilities:
    - Test result parsing (passed/failed/skipped)
    - Test → source file mapping
    - Call chain extraction from tracebacks
    - Fixture dependency detection
    - Test statistics aggregation
    - Parametrized test handling
    - Flaky test detection
    - Test marker extraction
    - Dependency graph construction
    
    Usage:
        >>> parser = PytestParser()
        >>> results = parser.parse_test_results(json_data)
        >>> mappings = parser.extract_test_file_mapping(json_data)
    """
    
    def __init__(self):
        self.test_file_pattern = re.compile(r"tests/(.+)/test_(.+)\.py")
        self.source_file_pattern = re.compile(r"test_(.+)")
        
    def parse_test_results(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse basic test results from pytest JSON output.
        
        Args:
            json_data: Pytest JSON output dictionary
            
        Returns:
            List of test result dictionaries with test_id, outcome, duration
        """
        results = []
        
        for test in json_data.get("tests", []):
            result = {
                "test_id": test["nodeid"],
                "outcome": test["outcome"],
                "duration": test.get("duration", 0.0),
                "longrepr": None
            }
            
            # Extract error message if failed
            if test["outcome"] == "failed":
                call_info = test.get("call", {})
                result["longrepr"] = call_info.get("longrepr")
            
            results.append(result)
        
        return results
    
    def extract_test_file_mapping(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract test → source file relationships.
        
        Infers source files from test file paths:
        - tests/unit/cortex/test_orchestrator.py → cortex/orchestrator.py
        - tests/integration/test_mcp_tools.py → (inferred from imports)
        
        Args:
            json_data: Pytest JSON output
            
        Returns:
            List of test-to-source mappings
        """
        mappings = []
        
        for test in json_data.get("tests", []):
            nodeid = test["nodeid"]
            
            # Parse nodeid: "path/to/test_file.py::TestClass::test_method"
            parts = nodeid.split("::")
            test_file = parts[0]
            test_name = parts[-1]
            
            # Infer source file from test path
            inferred_source = self._infer_source_file(test_file)
            
            mapping = {
                "test_file": test_file,
                "test_name": test_name,
                "inferred_source": inferred_source,
                "nodeid": nodeid
            }
            
            mappings.append(mapping)
        
        return mappings
    
    def parse_call_chain(self, traceback_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract call chains from pytest traceback data.
        
        Args:
            traceback_data: Pytest traceback dictionary
            
        Returns:
            List of call chain entries with file, lineno, args
        """
        call_chain = []
        
        # Parse traceback entries
        reprtraceback = traceback_data.get("reprtraceback", {})
        entries = reprtraceback.get("entries", [])
        
        for entry in entries:
            call_entry = {
                "file": entry["path"],
                "lineno": entry["lineno"],
                "args": entry.get("reprfuncargs", "")
            }
            call_chain.append(call_entry)
        
        return call_chain
    
    def extract_test_fixtures(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract fixture dependencies and setup/teardown timings.
        
        Args:
            json_data: Pytest JSON output
            
        Returns:
            List of test fixture information
        """
        fixtures = []
        
        for test in json_data.get("tests", []):
            fixture_info = {
                "test_id": test["nodeid"],
                "setup_duration": 0.0,
                "teardown_duration": 0.0,
                "setup_outcome": "unknown",
                "teardown_outcome": "unknown"
            }
            
            # Extract setup phase
            if "setup" in test:
                setup = test["setup"]
                fixture_info["setup_duration"] = setup.get("duration", 0.0)
                fixture_info["setup_outcome"] = setup.get("outcome", "unknown")
            
            # Extract teardown phase
            if "teardown" in test:
                teardown = test["teardown"]
                fixture_info["teardown_duration"] = teardown.get("duration", 0.0)
                fixture_info["teardown_outcome"] = teardown.get("outcome", "unknown")
            
            fixtures.append(fixture_info)
        
        return fixtures
    
    def aggregate_test_statistics(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate test execution statistics.
        
        Args:
            json_data: Pytest JSON output
            
        Returns:
            Dictionary with aggregated statistics
        """
        summary = json_data.get("summary", {})
        tests = json_data.get("tests", [])
        
        total_duration = sum(t.get("duration", 0.0) for t in tests)
        avg_duration = total_duration / len(tests) if tests else 0.0
        
        stats = {
            "total_tests": summary.get("total", len(tests)),
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
            "skipped": summary.get("skipped", 0),
            "total_duration": summary.get("duration", total_duration),
            "avg_duration": avg_duration
        }
        
        return stats
    
    def parse_parametrized_tests(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse parametrized test results.
        
        Handles pytest parametrize decorator:
        - test_add[1-2-3] → base: test_add, params: [1, 2, 3]
        
        Args:
            json_data: Pytest JSON output
            
        Returns:
            List of parametrized test results
        """
        parametrized = []
        
        for test in json_data.get("tests", []):
            nodeid = test["nodeid"]
            
            # Check for parametrization pattern: test_name[params]
            param_match = re.match(r"(.+)\[(.+)\]$", nodeid.split("::")[-1])
            
            if param_match:
                base_test = param_match.group(1)
                parameters = param_match.group(2)
                
                result = {
                    "nodeid": nodeid,
                    "base_test": base_test,
                    "parameters": parameters,
                    "outcome": test["outcome"],
                    "duration": test.get("duration", 0.0)
                }
                
                parametrized.append(result)
        
        return parametrized
    
    def detect_flaky_tests(self, multiple_runs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect flaky tests from multiple test runs.
        
        Flaky test = inconsistent outcomes across runs
        
        Args:
            multiple_runs: List of pytest JSON outputs from different runs
            
        Returns:
            List of flaky test detections
        """
        # Track outcomes per test
        test_outcomes: Dict[str, List[str]] = defaultdict(list)
        
        for run in multiple_runs:
            for test in run.get("tests", []):
                test_id = test["nodeid"]
                outcome = test["outcome"]
                test_outcomes[test_id].append(outcome)
        
        # Detect inconsistencies
        flaky_tests = []
        
        for test_id, outcomes in test_outcomes.items():
            unique_outcomes = set(outcomes)
            
            # Flaky if multiple different outcomes
            if len(unique_outcomes) > 1:
                passed_count = outcomes.count("passed")
                failed_count = outcomes.count("failed")
                total_runs = len(outcomes)
                
                flaky_tests.append({
                    "test_id": test_id,
                    "outcomes": outcomes,
                    "flakiness_rate": failed_count / total_runs if total_runs > 0 else 0.0,
                    "passed_count": passed_count,
                    "failed_count": failed_count,
                    "total_runs": total_runs
                })
        
        return flaky_tests
    
    def extract_test_markers(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract pytest markers (slow, integration, database, etc.).
        
        Args:
            json_data: Pytest JSON output
            
        Returns:
            List of test marker information
        """
        markers_list = []
        
        for test in json_data.get("tests", []):
            markers = test.get("keywords", [])
            
            # Filter out internal pytest markers
            user_markers = [
                m for m in markers
                if not m.startswith("_") and m not in ["test", "python"]
            ]
            
            if user_markers:
                markers_list.append({
                    "test_id": test["nodeid"],
                    "markers": user_markers
                })
        
        return markers_list
    
    def build_test_dependency_graph(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build test dependency graph from execution order.
        
        Detects implicit dependencies:
        - Setup fixtures → dependent tests
        - Execution order patterns
        
        Args:
            json_data: Pytest JSON output
            
        Returns:
            Graph dictionary with nodes and edges
        """
        tests = json_data.get("tests", [])
        
        nodes = []
        edges = []
        
        # Create nodes for each test
        for test in tests:
            node = {
                "id": test["nodeid"],
                "type": "test",
                "outcome": test["outcome"],
                "duration": test.get("duration", 0.0)
            }
            nodes.append(node)
        
        # Detect dependencies (simplified - looks for setup patterns)
        for i, test in enumerate(tests):
            test_name = test["nodeid"].split("::")[-1]
            
            # If test name suggests setup, link to next test
            if "setup" in test_name.lower() and i + 1 < len(tests):
                edges.append({
                    "source": test["nodeid"],
                    "target": tests[i + 1]["nodeid"],
                    "type": "setup_dependency"
                })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    # Private helper methods
    
    def _infer_source_file(self, test_file_path: str) -> str:
        """
        Infer source file from test file path.
        
        Args:
            test_file_path: Path to test file
            
        Returns:
            Inferred source file path
        """
        # Remove "test_" prefix and extract path components
        path_obj = Path(test_file_path)
        filename = path_obj.stem  # Filename without extension
        
        # Remove "test_" prefix
        if filename.startswith("test_"):
            source_name = filename[5:]  # Remove "test_"
        else:
            source_name = filename
        
        # Build source path from test path structure
        # tests/unit/cortex/test_orchestrator.py → cortex/orchestrator
        parts = path_obj.parts
        
        if "tests" in parts:
            test_idx = parts.index("tests")
            # Skip "tests" and test type (unit/integration)
            source_parts = parts[test_idx + 2:-1] if len(parts) > test_idx + 2 else []
            source_parts = list(source_parts) + [source_name]
            return "/".join(source_parts)
        
        return source_name

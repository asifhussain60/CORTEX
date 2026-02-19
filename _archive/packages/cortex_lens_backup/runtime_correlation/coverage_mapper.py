"""
Coverage Mapper

Maps pytest-cov coverage data to code paths, enabling test-to-code relationship queries
and coverage gap analysis for knowledge graph integration.

Author: CORTEX Architect
Phase: Phase 66 S4
"""

from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict
from pathlib import Path


class CoverageMapper:
    """
    Map test coverage data to code paths.
    
    Capabilities:
    - Coverage data parsing (pytest-cov format)
    - Test → covered files mapping
    - Uncovered line identification
    - Coverage scoring per file/module/function
    - Critical path detection (low coverage on important files)
    - Test gap identification
    - Test redundancy detection (overlapping coverage)
    - Coverage graph edge construction
    
    Usage:
        >>> mapper = CoverageMapper()
        >>> parsed = mapper.parse_coverage_data(coverage_json)
        >>> gaps = mapper.identify_test_gaps(parsed, min_coverage=80.0)
    """
    
    def __init__(self):
        pass
    
    def parse_coverage_data(self, coverage_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse pytest-cov coverage data into structured format.
        
        Args:
            coverage_data: Coverage data dictionary from pytest-cov
            
        Returns:
            List of file coverage dictionaries
        """
        parsed = []
        
        for file_path, file_data in coverage_data.get("files", {}).items():
            summary = file_data.get("summary", {})
            
            coverage_info = {
                "file": file_path,
                "covered_lines": summary.get("covered_lines", 0),
                "total_statements": summary.get("num_statements", 0),
                "coverage_percent": summary.get("percent_covered", 0.0),
                "executed_lines": file_data.get("executed_lines", []),
                "missing_lines": file_data.get("missing_lines", [])
            }
            
            parsed.append(coverage_info)
        
        return parsed
    
    def map_tests_to_coverage(
        self,
        test_results: List[Dict[str, Any]],
        coverage_by_test: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Map tests to their coverage footprint.
        
        Args:
            test_results: List of test results
            coverage_by_test: Coverage data keyed by test ID
            
        Returns:
            List of test-to-coverage mappings
        """
        mappings = []
        
        for test in test_results:
            test_id = test["test_id"]
            
            if test_id in coverage_by_test:
                coverage = coverage_by_test[test_id]
                
                mapping = {
                    "test_id": test_id,
                    "outcome": test["outcome"],
                    "covered_files": coverage.get("covered_files", []),
                    "line_count": coverage.get("line_count", 0)
                }
                
                mappings.append(mapping)
        
        return mappings
    
    def identify_uncovered_lines(self, coverage_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify uncovered lines in all files.
        
        Args:
            coverage_data: Coverage data dictionary
            
        Returns:
            List of files with uncovered line information
        """
        uncovered = []
        
        for file_path, file_data in coverage_data.get("files", {}).items():
            summary = file_data.get("summary", {})
            missing_lines = file_data.get("missing_lines", [])
            
            if missing_lines:
                uncovered_info = {
                    "file": file_path,
                    "missing_lines": missing_lines,
                    "missing_count": len(missing_lines),
                    "coverage_percent": summary.get("percent_covered", 0.0)
                }
                
                uncovered.append(uncovered_info)
        
        return uncovered
    
    def calculate_file_coverage_score(self, file_coverage: Dict[str, Any]) -> float:
        """
        Calculate coverage score for a file.
        
        Args:
            file_coverage: File coverage dictionary
            
        Returns:
            Coverage score 0.0-100.0
        """
        return file_coverage.get("percent_covered", 0.0)
    
    def aggregate_coverage_by_module(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate coverage statistics by module.
        
        Args:
            coverage_data: Coverage data dictionary
            
        Returns:
            Dictionary of module → aggregated coverage
        """
        module_stats: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"total_lines": 0, "covered_lines": 0}
        )
        
        for file_path, file_data in coverage_data.get("files", {}).items():
            summary = file_data.get("summary", {})
            
            # Extract module path (directory)
            path_obj = Path(file_path)
            module = str(path_obj.parent)
            
            module_stats[module]["total_lines"] += summary.get("num_statements", 0)
            module_stats[module]["covered_lines"] += summary.get("covered_lines", 0)
        
        # Calculate percentages
        for module, stats in module_stats.items():
            if stats["total_lines"] > 0:
                stats["coverage_percent"] = (
                    stats["covered_lines"] / stats["total_lines"] * 100.0
                )
            else:
                stats["coverage_percent"] = 0.0
        
        return dict(module_stats)
    
    def detect_critical_uncovered_paths(
        self,
        coverage_data: Dict[str, Any],
        threshold: float = 70.0
    ) -> List[Dict[str, Any]]:
        """
        Detect critical paths with low coverage.
        
        Critical = important files (security, core, etc.) with coverage below threshold.
        
        Args:
            coverage_data: Coverage data dictionary
            threshold: Minimum acceptable coverage percent
            
        Returns:
            List of critical uncovered paths
        """
        critical = []
        
        for file_path, file_data in coverage_data.get("files", {}).items():
            summary = file_data.get("summary", {})
            coverage_percent = summary.get("percent_covered", 0.0)
            
            if coverage_percent < threshold:
                critical_info = {
                    "file": file_path,
                    "coverage_percent": coverage_percent,
                    "covered_lines": summary.get("covered_lines", 0),
                    "total_statements": summary.get("num_statements", 0),
                    "severity": self._assess_criticality(file_path, coverage_percent)
                }
                
                critical.append(critical_info)
        
        return critical
    
    def build_coverage_graph_edges(self, test_coverage: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build knowledge graph edges from coverage data.
        
        Creates "covers" edges: test → source_file
        
        Args:
            test_coverage: Test coverage dictionary
            
        Returns:
            List of graph edge dictionaries
        """
        edges = []
        
        for test_id, coverage in test_coverage.items():
            covered_files = coverage.get("covered_files", [])
            
            for file_path in covered_files:
                edge = {
                    "source": test_id,
                    "target": file_path,
                    "type": "covers",
                    "metadata": {
                        "line_count": coverage.get("line_count", 0)
                    }
                }
                
                edges.append(edge)
        
        return edges
    
    def identify_test_gaps(
        self,
        coverage_data: Dict[str, Any],
        min_coverage: float = 60.0
    ) -> List[Dict[str, Any]]:
        """
        Identify files with insufficient test coverage.
        
        Args:
            coverage_data: Coverage data dictionary
            min_coverage: Minimum acceptable coverage
            
        Returns:
            List of files with coverage gaps
        """
        gaps = []
        
        for file_path, file_data in coverage_data.get("files", {}).items():
            summary = file_data.get("summary", {})
            coverage_percent = summary.get("percent_covered", 0.0)
            
            if coverage_percent < min_coverage:
                gap_info = {
                    "file": file_path,
                    "coverage_percent": coverage_percent,
                    "gap_size": min_coverage - coverage_percent,
                    "missing_lines": len(file_data.get("missing_lines", [])),
                    "priority": self._calculate_test_priority(file_path, coverage_percent)
                }
                
                gaps.append(gap_info)
        
        return gaps
    
    def calculate_test_redundancy(self, test_coverage: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect redundant tests with identical coverage footprints.
        
        Args:
            test_coverage: Test coverage dictionary
            
        Returns:
            List of redundant test groups
        """
        # Group tests by coverage fingerprint
        coverage_fingerprints: Dict[str, List[str]] = defaultdict(list)
        
        for test_id, coverage in test_coverage.items():
            # Create fingerprint from covered files + lines
            covered_files = tuple(sorted(coverage.get("covered_files", [])))
            covered_lines = tuple(sorted(coverage.get("covered_lines", [])))
            fingerprint = (covered_files, covered_lines)
            
            coverage_fingerprints[str(fingerprint)].append(test_id)
        
        # Find groups with multiple tests (redundant)
        redundant = []
        
        for fingerprint, tests in coverage_fingerprints.items():
            if len(tests) > 1:
                redundant.append({
                    "tests": tests,
                    "count": len(tests),
                    "redundancy_score": len(tests) - 1  # Additional redundant tests
                })
        
        return redundant
    
    def map_coverage_to_functions(
        self,
        coverage_data: Dict[str, Any],
        function_definitions: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Map coverage to individual functions.
        
        Args:
            coverage_data: Coverage data dictionary
            function_definitions: Function definitions per file
            
        Returns:
            List of function-level coverage information
        """
        function_coverage = []
        
        for file_path, file_data in coverage_data.get("files", {}).items():
            if file_path not in function_definitions:
                continue
            
            executed_lines = set(file_data.get("executed_lines", []))
            
            for func_def in function_definitions[file_path]:
                func_name = func_def["name"]
                start_line = func_def["start_line"]
                end_line = func_def["end_line"]
                
                # Calculate coverage for this function's line range
                func_lines = set(range(start_line, end_line + 1))
                covered_in_func = func_lines.intersection(executed_lines)
                
                coverage_percent = (
                    len(covered_in_func) / len(func_lines) * 100.0
                    if func_lines else 0.0
                )
                
                function_coverage.append({
                    "file": file_path,
                    "function": func_name,
                    "start_line": start_line,
                    "end_line": end_line,
                    "total_lines": len(func_lines),
                    "covered_lines": len(covered_in_func),
                    "coverage_percent": coverage_percent
                })
        
        return function_coverage
    
    # Private helper methods
    
    def _assess_criticality(self, file_path: str, coverage_percent: float) -> str:
        """Assess criticality of low coverage based on file path"""
        critical_keywords = ["security", "auth", "core", "critical"]
        
        path_lower = file_path.lower()
        
        if any(keyword in path_lower for keyword in critical_keywords):
            if coverage_percent < 50.0:
                return "critical"
            elif coverage_percent < 70.0:
                return "high"
        
        if coverage_percent < 30.0:
            return "high"
        elif coverage_percent < 50.0:
            return "medium"
        else:
            return "low"
    
    def _calculate_test_priority(self, file_path: str, coverage_percent: float) -> int:
        """Calculate priority for adding tests (1=highest, 5=lowest)"""
        if coverage_percent < 30.0:
            return 1  # Critical
        elif coverage_percent < 50.0:
            return 2  # High
        elif coverage_percent < 70.0:
            return 3  # Medium
        elif coverage_percent < 85.0:
            return 4  # Low
        else:
            return 5  # Lowest

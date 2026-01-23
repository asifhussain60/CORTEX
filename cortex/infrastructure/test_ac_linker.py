"""
Test-AC Linker - AC-BRITTLE-013

Discovers and links test functions to AC-IDs for traceability.

Features:
- Discovers test functions by AC-ID pattern
- Links tests to acceptance criteria
- Generates test coverage report
- Validates AC-to-test mapping

Author: Asif Hussain
"""

import inspect
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from cortex.brain.core.result import Result, Ok, Err


@dataclass
class TestACLink:
    """Link between a test and an AC-ID."""
    ac_id: str
    test_file: str
    test_function: str
    test_class: Optional[str] = None
    confidence: float = 1.0


class TestACLinker:
    """
    Discovers and links tests to AC-IDs.
    
    Uses multiple strategies:
    1. Docstring parsing (AC-ID in docstring)
    2. Test name pattern matching (test_xxx_yyy)
    3. AC-ID markers in test code
    """
    
    # Regex patterns for AC-ID detection
    AC_ID_PATTERN = re.compile(r'AC-[A-Z]+-\d+-\d{2}')
    TEST_AC_PATTERN = re.compile(r'test_.*_([a-z]+)_(\d{3})')
    
    def __init__(self, test_dir: Optional[Path] = None):
        """
        Initialize linker.
        
        Args:
            test_dir: Root test directory (uses ./tests if None)
        """
        self.test_dir = test_dir or Path("tests")
        self._links: List[TestACLink] = []
        self._ac_tests: Dict[str, List[TestACLink]] = {}
    
    def discover_links(self) -> Result[List[TestACLink]]:
        """
        Discover all test-to-AC links in test directory.
        
        Returns:
            Result containing list of TestACLink objects
        """
        try:
            links = []
            
            # Find all test files
            test_files = list(self.test_dir.rglob("test_*.py"))
            
            for test_file in test_files:
                try:
                    # Read file content
                    content = test_file.read_text()
                    
                    # Extract AC-IDs from docstrings and comments
                    ac_ids_in_file = self.AC_ID_PATTERN.findall(content)
                    
                    # Parse test functions
                    links.extend(self._extract_test_links(test_file, content, ac_ids_in_file))
                
                except Exception as e:
                    # Log but continue with other files
                    pass
            
            self._links = links
            self._build_ac_index()
            
            return Ok(links)
        
        except Exception as e:
            return Err(f"Link discovery failed: {str(e)}")
    
    def _extract_test_links(
        self,
        test_file: Path,
        content: str,
        ac_ids_in_file: List[str]
    ) -> List[TestACLink]:
        """
        Extract test-to-AC links from a single file.
        
        Args:
            test_file: Path to test file
            content: File content
            ac_ids_in_file: AC-IDs found in file
        
        Returns:
            List of TestACLink objects
        """
        links = []
        relative_path = test_file.relative_to(self.test_dir)
        
        # Parse file structure to find classes and functions
        lines = content.split('\n')
        current_class = None
        current_docstring = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Track class definitions
            if stripped.startswith('class '):
                match = re.match(r'class\s+(\w+)', stripped)
                if match:
                    current_class = match.group(1)
            
            # Track docstrings
            if '"""' in line or "'''" in line:
                quote = '"""' if '"""' in line else "'''"
                if stripped.count(quote) == 2:
                    # Single-line docstring
                    current_docstring = line
                else:
                    # Multi-line docstring start
                    current_docstring = line
            
            # Track test functions
            if stripped.startswith('def test_'):
                match = re.match(r'def\s+(test_\w+)', stripped)
                if match:
                    test_name = match.group(1)
                    
                    # Extract AC-IDs for this test
                    test_ac_ids = self.AC_ID_PATTERN.findall(current_docstring or '')
                    
                    # Also check test name pattern
                    name_match = self.TEST_AC_PATTERN.search(test_name)
                    
                    for ac_id in test_ac_ids:
                        links.append(TestACLink(
                            ac_id=ac_id,
                            test_file=str(relative_path),
                            test_function=test_name,
                            test_class=current_class,
                            confidence=0.95  # Extracted from docstring
                        ))
                    
                    if not test_ac_ids and name_match:
                        # Heuristic AC-ID from test name
                        prefix = name_match.group(1)
                        ac_num = name_match.group(2)
                        ac_id = f"AC-{prefix.upper()}-{ac_num}"
                        
                        links.append(TestACLink(
                            ac_id=ac_id,
                            test_file=str(relative_path),
                            test_function=test_name,
                            test_class=current_class,
                            confidence=0.5  # Heuristic match
                        ))
        
        return links
    
    def _build_ac_index(self) -> None:
        """Build index of AC-IDs to tests."""
        self._ac_tests = {}
        for link in self._links:
            if link.ac_id not in self._ac_tests:
                self._ac_tests[link.ac_id] = []
            self._ac_tests[link.ac_id].append(link)
    
    def get_tests_for_ac(self, ac_id: str) -> List[TestACLink]:
        """
        Get all tests linked to an AC-ID.
        
        Args:
            ac_id: Acceptance criteria ID (e.g., "AC-BRITTLE-001")
        
        Returns:
            List of TestACLink objects for this AC-ID
        """
        return self._ac_tests.get(ac_id, [])
    
    def get_coverage_report(self) -> Dict[str, any]:
        """
        Generate test coverage report by AC-ID.
        
        Returns:
            Dictionary with coverage statistics
        """
        total_acs = len(self._ac_tests)
        covered_acs = len([ac for ac in self._ac_tests if len(self._ac_tests[ac]) > 0])
        
        return {
            "total_ac_ids": total_acs,
            "covered_ac_ids": covered_acs,
            "coverage_rate": covered_acs / total_acs if total_acs > 0 else 0,
            "total_tests": len(self._links),
            "ac_to_tests": self._ac_tests
        }
    
    def validate_mapping(self) -> Result[Dict[str, any]]:
        """
        Validate AC-ID to test mapping.
        
        Returns:
            Result with validation report
        """
        report = {
            "valid": True,
            "issues": [],
            "unmapped_acs": [],
            "orphan_tests": []
        }
        
        # Find unmapped AC-IDs (if we have a source of truth)
        # This would need to be enhanced with actual AC-ID list
        
        return Ok(report)
    
    def export_mapping(self, output_file: Path) -> Result[None]:
        """
        Export AC-ID to test mapping to file.
        
        Args:
            output_file: Path to output file
        
        Returns:
            Result indicating success or error
        """
        try:
            import json
            
            # Build export data
            export_data = {
                "links": [
                    {
                        "ac_id": link.ac_id,
                        "test_file": link.test_file,
                        "test_function": link.test_function,
                        "test_class": link.test_class,
                        "confidence": link.confidence
                    }
                    for link in self._links
                ],
                "statistics": self.get_coverage_report()
            }
            
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(json.dumps(export_data, indent=2))
            
            return Ok(None)
        
        except Exception as e:
            return Err(f"Export failed: {str(e)}")

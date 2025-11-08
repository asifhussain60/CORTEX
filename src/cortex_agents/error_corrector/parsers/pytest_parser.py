"""Parse pytest error output."""

import re
from typing import Dict, Any
from .base_parser import BaseErrorParser


class PytestErrorParser(BaseErrorParser):
    """Parser for pytest test failures."""
    
    def can_parse(self, output: str) -> bool:
        """Check if output is pytest error."""
        return "FAILED" in output or "AssertionError" in output
    
    def parse(self, output: str) -> Dict[str, Any]:
        """
        Parse pytest error output.
        
        Returns:
            Dict with file, test_name, line, category, message, traceback
        """
        result = {}
        
        # Look for test failure line: "test_file.py::test_name FAILED"
        failed_match = re.search(r"([\w/]+\.py)::([\w_]+)\s+FAILED", output)
        if failed_match:
            result["file"] = failed_match.group(1)
            result["test_name"] = failed_match.group(2)
        
        # Look for assertion error
        if "AssertionError" in output:
            result["category"] = "assertion"
            # Extract assertion line
            assert_match = re.search(r"assert (.+)", output)
            if assert_match:
                result["code_snippet"] = assert_match.group(1)
        
        # Look for file and line number: "file.py:123: AssertionError"
        location_match = re.search(r"([\w/]+\.py):(\d+):", output)
        if location_match:
            result["file"] = location_match.group(1)
            result["line"] = int(location_match.group(2))
        
        # Extract error message
        lines = output.split("\n")
        for i, line in enumerate(lines):
            if "AssertionError" in line or "FAILED" in line:
                result["message"] = line.strip()
                # Get surrounding context
                result["traceback"] = lines[max(0, i-3):min(len(lines), i+3)]
                break
        
        return result

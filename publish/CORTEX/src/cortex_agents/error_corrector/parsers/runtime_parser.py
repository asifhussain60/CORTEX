"""Parse runtime errors (NameError, AttributeError, TypeError, etc)."""

import re
from typing import Dict, Any
from .base_parser import BaseErrorParser


class RuntimeErrorParser(BaseErrorParser):
    """Parser for Python runtime errors."""
    
    def can_parse(self, output: str) -> bool:
        """Check if output is runtime error."""
        return "Traceback" in output
    
    def parse(self, output: str) -> Dict[str, Any]:
        """
        Parse runtime error (NameError, AttributeError, TypeError, etc).
        
        Returns:
            Dict with file, line, category, message, traceback,
            and type-specific fields (undefined_name, missing_attribute, etc)
        """
        result = {}
        
        # Determine error category
        if "NameError" in output:
            result["category"] = "name"
            name_match = re.search(r"name ['\"]([^'\"]+)['\"] is not defined", output)
            if name_match:
                result["undefined_name"] = name_match.group(1)
        
        elif "AttributeError" in output:
            result["category"] = "attribute"
            attr_match = re.search(r"has no attribute ['\"]([^'\"]+)['\"]", output)
            if attr_match:
                result["missing_attribute"] = attr_match.group(1)
        
        elif "TypeError" in output:
            result["category"] = "type"
        
        elif "ValueError" in output:
            result["category"] = "value"
        
        elif "KeyError" in output:
            result["category"] = "key"
        
        # Get file and line from traceback
        traceback_lines = []
        for line in output.split("\n"):
            if line.strip().startswith("File"):
                traceback_lines.append(line)
        
        if traceback_lines:
            result["traceback"] = traceback_lines
            # Get last file/line (where error occurred)
            last_match = re.search(r'File "([^"]+)", line (\d+)', traceback_lines[-1])
            if last_match:
                result["file"] = last_match.group(1)
                result["line"] = int(last_match.group(2))
        
        # Get error message
        lines = output.split("\n")
        if lines:
            result["message"] = lines[-1].strip()
        
        return result

"""Parse Python syntax errors."""

import re
from typing import Dict, Any
from .base_parser import BaseErrorParser


class SyntaxErrorParser(BaseErrorParser):
    """Parser for Python syntax errors."""
    
    def can_parse(self, output: str) -> bool:
        """Check if output is syntax error."""
        return "SyntaxError" in output
    
    def parse(self, output: str) -> Dict[str, Any]:
        """
        Parse Python syntax error.
        
        Returns:
            Dict with file, line, category, message, code_snippet
        """
        result = {"category": "syntax"}
        
        # Look for: "File "file.py", line 123"
        file_match = re.search(r'File "([^"]+)", line (\d+)', output)
        if file_match:
            result["file"] = file_match.group(1)
            result["line"] = int(file_match.group(2))
        
        # Extract syntax error type
        if "IndentationError" in output:
            result["category"] = "indentation"
        elif "TabError" in output:
            result["category"] = "tabs"
        elif "invalid syntax" in output:
            result["category"] = "invalid_syntax"
        
        # Extract the problematic line
        lines = output.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("^"):
                if i > 0:
                    result["code_snippet"] = lines[i-1].strip()
                break
        
        # Get error message
        error_match = re.search(r"(SyntaxError|IndentationError|TabError): (.+)", output)
        if error_match:
            result["message"] = error_match.group(2)
        
        return result

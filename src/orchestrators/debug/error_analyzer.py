"""
Error Analyzer - Parse and categorize errors from bug reports

Extracts meaningful information from error messages, stack traces,
and test failures to feed root cause analysis.

Author: Asif Hussain
Created: January 4, 2026
"""

import logging
import re
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ErrorAnalyzer:
    """Analyzes errors and extracts structured information."""
    
    # Common Python error patterns
    ERROR_PATTERNS = {
        "AttributeError": r"'(\w+)' object has no attribute '(\w+)'",
        "ImportError": r"No module named '([\w.]+)'",
        "KeyError": r"KeyError: '(\w+)'",
        "TypeError": r"TypeError: (.+)",
        "ValueError": r"ValueError: (.+)",
        "NameError": r"name '(\w+)' is not defined",
        "FileNotFoundError": r"No such file or directory: '(.+)'",
        "AssertionError": r"AssertionError: (.+)",
    }
    
    def __init__(self):
        """Initialize error analyzer."""
        self.logger = logger
    
    def parse_error(
        self,
        description: str,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
        test_failures: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Parse error from various sources and extract structured data.
        
        Implements: DBG-001 (Bug Report Intake and Parsing)
        
        Args:
            description: Natural language bug description
            error_message: Optional error message
            stack_trace: Optional stack trace
            test_failures: Optional list of failing test names
            
        Returns:
            Structured error data
        """
        self.logger.info("Parsing error from bug report")
        
        # Extract error type
        error_type = self._extract_error_type(
            description, error_message, stack_trace
        )
        
        # Extract affected components
        affected_components = self._extract_components(
            description, stack_trace, test_failures
        )
        
        # Extract file locations
        affected_files = self._extract_file_locations(stack_trace)
        
        # Categorize error
        category = self._categorize_error(error_type, description)
        
        # Extract variables mentioned
        mentioned_variables = self._extract_variables(
            error_message or "", stack_trace or ""
        )
        
        return {
            "error_type": error_type,
            "category": category,
            "affected_components": affected_components,
            "affected_files": affected_files,
            "mentioned_variables": mentioned_variables,
            "test_failures": test_failures or [],
            "severity": self._assess_severity(error_type, test_failures),
            "raw_data": {
                "description": description,
                "error_message": error_message,
                "stack_trace": stack_trace,
            }
        }
    
    def _extract_error_type(
        self,
        description: str,
        error_message: Optional[str],
        stack_trace: Optional[str]
    ) -> str:
        """Extract error type from available information."""
        # Check error message first
        if error_message:
            for error_type in self.ERROR_PATTERNS.keys():
                if error_type in error_message:
                    return error_type
        
        # Check stack trace
        if stack_trace:
            for error_type in self.ERROR_PATTERNS.keys():
                if error_type in stack_trace:
                    return error_type
        
        # Check description
        for error_type in self.ERROR_PATTERNS.keys():
            if error_type.lower() in description.lower():
                return error_type
        
        return "UnknownError"
    
    def _extract_components(
        self,
        description: str,
        stack_trace: Optional[str],
        test_failures: Optional[List[str]]
    ) -> List[str]:
        """Extract affected components from bug report."""
        components = set()
        
        # Extract from description (look for class/module names)
        # Pattern: CapitalizedWords
        desc_components = re.findall(r'\b[A-Z][a-zA-Z]*(?:Orchestrator|Manager|Handler|Service|Controller)\b', description)
        components.update(desc_components)
        
        # Extract from stack trace
        if stack_trace:
            # Extract module/class names from stack trace
            file_refs = re.findall(r'File "(.+?)"', stack_trace)
            for file_ref in file_refs:
                # Extract component name from file path
                parts = file_ref.split('/')
                if len(parts) > 0:
                    filename = parts[-1].replace('.py', '')
                    if filename not in ['__init__', '__main__']:
                        components.add(filename)
        
        # Extract from test failures
        if test_failures:
            for test in test_failures:
                # Extract test class/module
                parts = test.split('::')
                if len(parts) > 1:
                    components.add(parts[0].split('.')[-1])
        
        return sorted(list(components))
    
    def _extract_file_locations(self, stack_trace: Optional[str]) -> List[str]:
        """Extract file locations from stack trace."""
        if not stack_trace:
            return []
        
        # Extract file paths from stack trace
        file_pattern = r'File "(.+?)"'
        files = re.findall(file_pattern, stack_trace)
        
        # Deduplicate and return
        return sorted(list(set(files)))
    
    def _categorize_error(self, error_type: str, description: str) -> str:
        """Categorize error into broader categories."""
        categories = {
            "logic": ["AssertionError", "ValueError", "KeyError"],
            "missing_dependency": ["ImportError", "ModuleNotFoundError"],
            "type_mismatch": ["TypeError", "AttributeError"],
            "runtime": ["NameError", "IndexError", "ZeroDivisionError"],
            "io": ["FileNotFoundError", "IOError", "PermissionError"],
        }
        
        for category, error_types in categories.items():
            if error_type in error_types:
                return category
        
        return "unknown"
    
    def _extract_variables(self, error_message: str, stack_trace: str) -> List[str]:
        """Extract variable names mentioned in error or stack trace."""
        variables = set()
        
        combined_text = f"{error_message} {stack_trace}"
        
        # Extract from error patterns
        for pattern in self.ERROR_PATTERNS.values():
            matches = re.findall(pattern, combined_text)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        variables.update(match)
                    else:
                        variables.add(match)
        
        # Extract variable assignments in stack trace
        var_pattern = r'\b([a-z_][a-z0-9_]*)\s*='
        variables.update(re.findall(var_pattern, stack_trace.lower()))
        
        # Filter out common words
        common_words = {'the', 'is', 'at', 'in', 'on', 'to', 'a', 'an', 'and', 'or', 'but'}
        variables = {v for v in variables if v not in common_words and len(v) > 1}
        
        return sorted(list(variables))
    
    def _assess_severity(
        self,
        error_type: str,
        test_failures: Optional[List[str]]
    ) -> str:
        """Assess severity of the error."""
        # Critical: Multiple test failures
        if test_failures and len(test_failures) > 5:
            return "critical"
        
        # High: Import errors or type errors
        if error_type in ["ImportError", "ModuleNotFoundError", "TypeError"]:
            return "high"
        
        # Medium: Logic errors
        if error_type in ["AssertionError", "ValueError", "KeyError"]:
            return "medium"
        
        # Low: Other errors
        return "low"
    
    def parse_pytest_output(self, pytest_output: str) -> Dict[str, Any]:
        """
        Parse pytest output for structured failure information.
        
        Args:
            pytest_output: Raw pytest output
            
        Returns:
            Structured test failure data
        """
        self.logger.info("Parsing pytest output")
        
        # Extract failed tests
        failed_pattern = r'FAILED (.+?) - (.+)'
        failures = re.findall(failed_pattern, pytest_output)
        
        # Extract error summary
        error_pattern = r'ERROR (.+?) - (.+)'
        errors = re.findall(error_pattern, pytest_output)
        
        # Extract short test summary
        summary_pattern = r'=+ short test summary info =+\n(.+?)(?:=+|$)'
        summary_match = re.search(summary_pattern, pytest_output, re.DOTALL)
        summary = summary_match.group(1) if summary_match else ""
        
        return {
            "failed_tests": [f[0] for f in failures],
            "error_messages": [f[1] for f in failures],
            "errors": [e[0] for e in errors],
            "summary": summary.strip(),
            "total_failures": len(failures),
            "total_errors": len(errors),
        }

"""
ErrorCorrector Agent

Automatically detects, parses, and corrects errors in code.

ISOLATION NOTICE: This agent fixes errors in TARGET APPLICATION code only.
It NEVER modifies CORTEX/tests/ - those are protected system health tests.

Handles:
- Pytest errors (assertion failures, import errors, type errors)
- Linter errors (undefined names, unused imports, formatting)
- Runtime errors (NameError, AttributeError, TypeError)
- Syntax errors (indentation, missing colons, invalid syntax)
- Import errors (missing modules, circular imports)

Uses Tier 2 knowledge base for known fix patterns.
"""

from typing import Dict, Any, List, Optional
import re
import ast
from pathlib import Path

from CORTEX.src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from CORTEX.src.cortex_agents.agent_types import IntentType
from CORTEX.src.cortex_agents.utils import safe_get


# Simple PatternStore mock - will be replaced with Tier 2 implementation
class PatternStore:
    """Placeholder for Tier 2 PatternStore."""
    
    def search_patterns(self, query: str, pattern_type: str, min_confidence: float) -> List[Dict[str, Any]]:
        """Search for patterns. Currently returns empty list."""
        return []


class ErrorCorrector(BaseAgent):
    """
    Agent that automatically corrects code errors.
    
    ISOLATION: Fixes TARGET APPLICATION code only. NEVER modifies:
    - CORTEX/tests/ (system health tests)
    - CORTEX/src/cortex_agents/ (core agents)  
    - cortex-brain/ (knowledge base)
    """
    
    def __init__(self, name: str = "ErrorCorrector"):
        super().__init__(name=name)
        
        # Initialize pattern store for known fixes (mock for now)
        self.pattern_store = PatternStore()
        
        # Protected directories that should never be auto-fixed
        self.protected_paths = [
            "CORTEX/tests",  # System health tests
            "CORTEX/src/cortex_agents",  # Core agent code
            "cortex-brain",  # Knowledge base
        ]
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Can handle error correction requests.
        
        Intents: FIX, DEBUG, fix_error, correct_code
        """
        intent_lower = request.intent.lower()
        
        # Check for fix/debug intents
        if request.intent in [IntentType.FIX.value, IntentType.DEBUG.value]:
            return True
        
        # Check for error correction keywords
        error_keywords = ["fix_error", "correct", "debug", "resolve_error"]
        if any(keyword in intent_lower for keyword in error_keywords):
            return True
        
        # Check if error output is provided
        if "error_output" in request.context:
            return True
        
        return False
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute error correction.
        
        Context expected:
        - error_output: The error message/traceback
        - file_path: Optional file where error occurred
        - error_type: Optional type hint (pytest, linter, runtime, syntax)
        """
        try:
            # Extract error information
            error_output = request.context.get("error_output", "")
            file_path = request.context.get("file_path")
            error_type = request.context.get("error_type", "unknown")
            
            if not error_output or not error_output.strip():
                return AgentResponse(
                    success=False,
                    result={},
                    message="No error output provided"
                )
            
            # Check if file is in protected directory
            if file_path and self._is_protected_path(file_path):
                return AgentResponse(
                    success=False,
                    result={"error": "protected_path"},
                    message=f"Cannot auto-fix protected path: {file_path}"
                )
            
            # Parse the error
            parsed_error = self._parse_error(error_output, error_type)
            
            if not parsed_error["detected"]:
                return AgentResponse(
                    success=False,
                    result=parsed_error,
                    message="Could not parse error"
                )
            
            # Find applicable fix patterns
            fix_patterns = self._find_fix_patterns(parsed_error)
            
            if not fix_patterns:
                return AgentResponse(
                    success=True,
                    result={
                        "parsed_error": parsed_error,
                        "fix_patterns": [],
                        "recommendation": "Manual review needed"
                    },
                    message="Error detected but no automatic fix available"
                )
            
            # Apply the best fix pattern
            fix_result = self._apply_fix(parsed_error, fix_patterns, file_path)
            
            return AgentResponse(
                success=fix_result["success"],
                result=fix_result,
                message=fix_result.get("message", "Fix applied successfully")
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                result={"error": str(e)},
                message=f"Error correction failed: {str(e)}"
            )
    
    def _is_protected_path(self, file_path: str) -> bool:
        """
        Check if file path is in protected directory.
        
        Protected paths:
        - CORTEX/tests/ (system health tests)
        - CORTEX/src/cortex_agents/ (core agents)
        - cortex-brain/ (knowledge base)
        """
        path = Path(file_path)
        
        for protected in self.protected_paths:
            protected_path = Path(protected)
            try:
                # Check if file_path is relative to protected_path
                path.resolve().relative_to(protected_path.resolve())
                return True
            except ValueError:
                # Not relative, continue checking
                continue
        
        return False
    
    def _parse_error(self, error_output: str, error_type: str) -> Dict[str, Any]:
        """
        Parse error output to extract structured information.
        
        Returns:
            {
                "detected": bool,
                "type": str (pytest/linter/runtime/syntax/import),
                "category": str (assertion/type/name/attribute/etc),
                "file": str,
                "line": int,
                "message": str,
                "traceback": List[str],
                "code_snippet": str
            }
        """
        result = {
            "detected": False,
            "type": error_type,
            "category": "unknown",
            "file": None,
            "line": None,
            "message": "",
            "traceback": [],
            "code_snippet": ""
        }
        
        # Detect error type if not specified
        if error_type == "unknown":
            if "FAILED" in error_output or "AssertionError" in error_output:
                result["type"] = "pytest"
            elif "SyntaxError" in error_output:
                result["type"] = "syntax"
            elif "ImportError" in error_output or "ModuleNotFoundError" in error_output:
                result["type"] = "import"
            elif "Traceback" in error_output:
                result["type"] = "runtime"
            elif re.search(r"^\w+\.py:\d+:\d+:", error_output, re.MULTILINE):
                result["type"] = "linter"
        
        # Parse based on type
        if result["type"] == "pytest":
            parsed = self._parse_pytest_error(error_output)
        elif result["type"] == "syntax":
            parsed = self._parse_syntax_error(error_output)
        elif result["type"] == "import":
            parsed = self._parse_import_error(error_output)
        elif result["type"] == "runtime":
            parsed = self._parse_runtime_error(error_output)
        elif result["type"] == "linter":
            parsed = self._parse_linter_error(error_output)
        else:
            parsed = {}
        
        result.update(parsed)
        result["detected"] = bool(parsed)
        
        return result
    
    def _parse_pytest_error(self, output: str) -> Dict[str, Any]:
        """Parse pytest error output."""
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
    
    def _parse_syntax_error(self, output: str) -> Dict[str, Any]:
        """Parse Python syntax error."""
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
    
    def _parse_import_error(self, output: str) -> Dict[str, Any]:
        """Parse import error."""
        result = {"category": "import"}
        
        # Look for: "ModuleNotFoundError: No module named 'xyz'"
        module_match = re.search(r"No module named ['\"]([^'\"]+)['\"]", output)
        if module_match:
            result["missing_module"] = module_match.group(1)
            result["message"] = f"Missing module: {module_match.group(1)}"
        
        # Look for: "ImportError: cannot import name 'xyz'"
        name_match = re.search(r"cannot import name ['\"]([^'\"]+)['\"]", output)
        if name_match:
            result["missing_name"] = name_match.group(1)
            result["message"] = f"Cannot import: {name_match.group(1)}"
        
        # Get file and line
        file_match = re.search(r'File "([^"]+)", line (\d+)', output)
        if file_match:
            result["file"] = file_match.group(1)
            result["line"] = int(file_match.group(2))
        
        return result
    
    def _parse_runtime_error(self, output: str) -> Dict[str, Any]:
        """Parse runtime error (NameError, AttributeError, TypeError, etc)."""
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
    
    def _parse_linter_error(self, output: str) -> Dict[str, Any]:
        """Parse linter error (pylint, flake8, etc)."""
        result = {"category": "linter"}
        
        # Format: "file.py:line:col: ERROR_CODE message"
        match = re.search(r"([\w/]+\.py):(\d+):(\d+):\s*(\w+)\s+(.+)", output)
        if match:
            result["file"] = match.group(1)
            result["line"] = int(match.group(2))
            result["column"] = int(match.group(3))
            result["code"] = match.group(4)
            result["message"] = match.group(5)
        
        # Categorize by error code
        if "F821" in output or "undefined" in output.lower():
            result["category"] = "undefined_name"
        elif "F401" in output or "imported but unused" in output.lower():
            result["category"] = "unused_import"
        elif "E501" in output or "line too long" in output.lower():
            result["category"] = "line_length"
        
        return result
    
    def _find_fix_patterns(self, parsed_error: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find applicable fix patterns from Tier 2 knowledge base.
        
        Returns list of fix patterns sorted by confidence.
        """
        patterns = []
        
        error_type = parsed_error.get("type")
        category = parsed_error.get("category")
        
        # Query pattern store for similar errors
        query = f"{error_type} {category}"
        stored_patterns = self.pattern_store.search_patterns(
            query=query,
            pattern_type="error_fix",
            min_confidence=0.5
        )
        
        patterns.extend(stored_patterns)
        
        # Add built-in fix patterns
        builtin = self._get_builtin_patterns(error_type, category, parsed_error)
        patterns.extend(builtin)
        
        # Sort by confidence
        patterns.sort(key=lambda p: p.get("confidence", 0.5), reverse=True)
        
        return patterns
    
    def _get_builtin_patterns(
        self, 
        error_type: str, 
        category: str, 
        parsed_error: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get built-in fix patterns for common errors."""
        patterns = []
        
        if error_type == "syntax":
            if category == "indentation":
                patterns.append({
                    "name": "fix_indentation",
                    "description": "Fix indentation error",
                    "confidence": 0.9,
                    "action": "normalize_indentation",
                    "params": {"spaces": 4}
                })
            
            elif category == "invalid_syntax":
                patterns.append({
                    "name": "add_missing_colon",
                    "description": "Add missing colon",
                    "confidence": 0.7,
                    "action": "check_colons",
                    "params": {}
                })
        
        elif error_type == "import":
            if "missing_module" in parsed_error:
                module = parsed_error["missing_module"]
                patterns.append({
                    "name": "install_missing_module",
                    "description": f"Install {module}",
                    "confidence": 0.8,
                    "action": "install_package",
                    "params": {"package": module}
                })
        
        elif error_type == "runtime":
            if category == "name":
                undefined = parsed_error.get("undefined_name")
                patterns.append({
                    "name": "add_import",
                    "description": f"Import {undefined}",
                    "confidence": 0.6,
                    "action": "suggest_import",
                    "params": {"name": undefined}
                })
            
            elif category == "attribute":
                patterns.append({
                    "name": "check_attribute",
                    "description": "Verify attribute exists",
                    "confidence": 0.5,
                    "action": "check_object_interface",
                    "params": {}
                })
        
        elif error_type == "linter":
            if category == "unused_import":
                patterns.append({
                    "name": "remove_unused_import",
                    "description": "Remove unused import",
                    "confidence": 0.9,
                    "action": "remove_import",
                    "params": {}
                })
            
            elif category == "undefined_name":
                patterns.append({
                    "name": "add_import_or_define",
                    "description": "Add import or definition",
                    "confidence": 0.7,
                    "action": "suggest_import",
                    "params": {}
                })
        
        return patterns
    
    def _apply_fix(
        self, 
        parsed_error: Dict[str, Any], 
        fix_patterns: List[Dict[str, Any]], 
        file_path: Optional[str]
    ) -> Dict[str, Any]:
        """
        Apply the best fix pattern.
        
        Returns:
            {
                "success": bool,
                "applied_pattern": str,
                "changes": List[str],
                "message": str,
                "confidence": float
            }
        """
        if not fix_patterns:
            return {
                "success": False,
                "message": "No fix patterns available",
                "confidence": 0.0
            }
        
        # Get best pattern (already sorted by confidence)
        best_pattern = fix_patterns[0]
        
        result = {
            "success": False,
            "applied_pattern": best_pattern.get("name"),
            "description": best_pattern.get("description"),
            "changes": [],
            "message": "",
            "confidence": best_pattern.get("confidence", 0.5)
        }
        
        action = best_pattern.get("action")
        params = best_pattern.get("params", {})
        
        # Execute fix action
        if action == "normalize_indentation":
            fix_result = self._fix_indentation(file_path, params)
        
        elif action == "install_package":
            fix_result = self._suggest_package_install(params)
        
        elif action == "suggest_import":
            fix_result = self._suggest_import(parsed_error, params)
        
        elif action == "remove_import":
            fix_result = self._suggest_remove_import(file_path, parsed_error)
        
        elif action == "check_colons":
            fix_result = self._check_missing_colons(file_path, parsed_error)
        
        else:
            fix_result = {
                "success": False,
                "message": f"Unknown action: {action}"
            }
        
        result.update(fix_result)
        return result
    
    def _fix_indentation(self, file_path: Optional[str], params: Dict) -> Dict[str, Any]:
        """Fix indentation errors."""
        if not file_path or not Path(file_path).exists():
            return {
                "success": False,
                "message": "File path required for indentation fix"
            }
        
        spaces = params.get("spaces", 4)
        
        try:
            # Read file
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Normalize indentation (convert tabs to spaces)
            fixed_lines = []
            for line in lines:
                # Replace tabs with spaces
                fixed_line = line.replace('\t', ' ' * spaces)
                fixed_lines.append(fixed_line)
            
            # Would write to file here (but we'll return suggestion)
            return {
                "success": True,
                "message": f"Normalized indentation to {spaces} spaces",
                "changes": [f"Convert tabs to {spaces} spaces"],
                "fixed_content": ''.join(fixed_lines)
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Indentation fix failed: {str(e)}"
            }
    
    def _suggest_package_install(self, params: Dict) -> Dict[str, Any]:
        """Suggest package installation."""
        package = params.get("package")
        
        return {
            "success": True,
            "message": f"Install missing package: {package}",
            "changes": [f"pip install {package}"],
            "command": f"pip install {package}"
        }
    
    def _suggest_import(self, parsed_error: Dict, params: Dict) -> Dict[str, Any]:
        """Suggest import statement."""
        name = params.get("name") or parsed_error.get("undefined_name")
        
        if not name:
            return {
                "success": False,
                "message": "Cannot determine what to import"
            }
        
        # Common import suggestions
        import_map = {
            "Path": "from pathlib import Path",
            "datetime": "from datetime import datetime",
            "json": "import json",
            "re": "import re",
            "os": "import os",
            "sys": "import sys",
        }
        
        suggested_import = import_map.get(name, f"import {name}")
        
        return {
            "success": True,
            "message": f"Add import: {suggested_import}",
            "changes": [suggested_import],
            "import_statement": suggested_import
        }
    
    def _suggest_remove_import(self, file_path: Optional[str], parsed_error: Dict) -> Dict[str, Any]:
        """Suggest removing unused import."""
        if not file_path:
            return {
                "success": False,
                "message": "File path required"
            }
        
        line_num = parsed_error.get("line")
        
        return {
            "success": True,
            "message": f"Remove unused import at line {line_num}",
            "changes": [f"Delete line {line_num}"],
            "line_to_remove": line_num
        }
    
    def _check_missing_colons(self, file_path: Optional[str], parsed_error: Dict) -> Dict[str, Any]:
        """Check for missing colons in control structures."""
        if not file_path or not Path(file_path).exists():
            return {
                "success": False,
                "message": "File path required"
            }
        
        line_num = parsed_error.get("line")
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            if line_num and line_num <= len(lines):
                problem_line = lines[line_num - 1]
                
                # Check if it's a control structure without colon
                if re.match(r'^\s*(if|elif|else|for|while|def|class|try|except|finally|with)\b', problem_line):
                    if not problem_line.rstrip().endswith(':'):
                        return {
                            "success": True,
                            "message": f"Add missing colon to line {line_num}",
                            "changes": [f"Add ':' to end of line {line_num}"],
                            "fixed_line": problem_line.rstrip() + ':'
                        }
            
            return {
                "success": False,
                "message": "Could not identify missing colon"
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Colon check failed: {str(e)}"
            }

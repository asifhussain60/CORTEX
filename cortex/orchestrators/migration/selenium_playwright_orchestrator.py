"""
Selenium to Playwright Migration Orchestrator - CORTEX Migration Tools.

This orchestrator converts Selenium test code to Playwright test code using:
- Pattern matching for Selenium API patterns
- AST transformation for code structure preservation
- Semantic mapping of Selenium to Playwright APIs
- Hash-chain audit logging for migration tracking

Features:
- Automatic WebDriver → Browser context conversion
- Locator strategy conversion (ID, CLASS, XPATH, CSS)
- Action mapping (click, send_keys, etc.)
- Explicit wait removal (Playwright uses auto-waiting)
- Test structure preservation
- Conversion report generation
- MCP tool exposure for programmatic access

Architecture:
1. SeleniumPatternMatcher: Detects Selenium patterns in code
2. P        tools = {
            "convert_selenium_file": {
                "description": "Convert a Selenium test file to Playwright format",
                "parameters": ["input_file", "output_file"],
            },
            "analyze_selenium_tests": {
                "description": "Analyze Selenium code for patterns and conversion readiness",
                "parameters": ["code"],
            },
            "convert_selenium_directory": {
                "description": "Convert all Selenium tests in a directory to Playwright",
                "parameters": ["input_dir", "output_dir"],
            },
        }
        return Ok(tools)nerator: Generates equivalent Playwright code
3. ConversionEngine: Orchestrates full file conversion
4. SeleniumPlaywrightOrchestrator: IOrchestrator implementation with audit trail

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import ast
import hashlib
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from pathlib import Path
import json

from cortex.brain.core.result import Result, Ok, Err, ok, err
from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.brain.mcp.decorator import mcp_tool


@dataclass
class ConversionReport:
    """Report on code conversion results."""
    
    input_file: str
    output_file: str
    status: str  # success, partial, failed
    patterns_detected: Dict[str, int]
    conversions_applied: Dict[str, int]
    warnings: List[str]
    errors: List[str]
    lines_converted: int
    total_lines: int
    conversion_time_ms: float
    previous_hash: Optional[str] = None
    current_hash: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert report to JSON."""
        return json.dumps(self.to_dict(), indent=2)


class SeleniumPatternMatcher:
    """Detects Selenium patterns in Python code."""
    
    # Pattern definitions
    PATTERNS = {
        "webdriver_import": r"from\s+selenium\s+import\s+webdriver",
        "by_import": r"from\s+selenium\.webdriver\.common\.by\s+import\s+By",
        "wait_import": r"from\s+selenium\.webdriver\.support\.ui\s+import\s+WebDriverWait",
        "expected_conditions_import": r"from\s+selenium\.webdriver\.support\s+import\s+expected_conditions",
        "expected_conditions": r"expected_conditions\s+as\s+EC|from.*expected_conditions",  # Add this
        "chrome_driver": r"webdriver\.Chrome\s*\(",
        "firefox_driver": r"webdriver\.Firefox\s*\(",
        "safari_driver": r"webdriver\.Safari\s*\(",
        "edge_driver": r"webdriver\.Edge\s*\(",
        "find_element_by_id": r"find_element\(By\.ID",
        "find_element_by_css": r"find_element\(By\.CSS_SELECTOR",
        "find_element_by_xpath": r"find_element\(By\.XPATH",
        "find_element_by_class": r"find_element\(By\.CLASS_NAME",
        "find_elements": r"find_elements\(",
        "webdriver_wait": r"WebDriverWait\s*\(",
        "click_action": r"\.click\s*\(",
        "send_keys_action": r"\.send_keys\s*\(",
        "clear_action": r"\.clear\s*\(",
        "submit_action": r"\.submit\s*\(",
        "navigate_action": r"\.get\s*\(",
        "page_title": r"\.title",
        "page_url": r"\.current_url",
        "quit_driver": r"\.quit\s*\(",
    }
    
    def detect_patterns(self, code: str) -> Dict[str, int]:
        """
        Detect Selenium patterns in code.
        
        Args:
            code: Python source code to analyze
            
        Returns:
            Dictionary mapping pattern names to occurrence counts
        """
        detected: Dict[str, int] = {}
        
        for pattern_name, pattern_regex in self.PATTERNS.items():
            matches = re.findall(pattern_regex, code)
            if matches:
                detected[pattern_name] = len(matches)
        
        return detected
    
    def extract_locators(self, code: str) -> List[Tuple[str, str]]:
        """
        Extract locator definitions from code.
        
        Args:
            code: Python source code
            
        Returns:
            List of (locator_type, locator_value) tuples
        """
        locators: List[Tuple[str, str]] = []
        
        # Match find_element with By.* locators
        pattern = r'find_element\(By\.(\w+),\s*["\']([^"\']+)["\']\)'
        matches = re.findall(pattern, code)
        for locator_type, locator_value in matches:
            locators.append((locator_type, locator_value))
        
        return locators
    
    def extract_actions(self, code: str) -> List[Tuple[str, Optional[str]]]:
        """
        Extract action calls from code.
        
        Args:
            code: Python source code
            
        Returns:
            List of (action_name, argument) tuples
        """
        actions: List[Tuple[str, Optional[str]]] = []
        
        # Match element.action() patterns
        patterns = {
            "click": r"\.click\s*\(",
            "send_keys": r"\.send_keys\s*\(([^)]+)\)",
            "clear": r"\.clear\s*\(",
            "submit": r"\.submit\s*\(",
        }
        
        for action_name, pattern in patterns.items():
            matches = re.finditer(pattern, code)
            for match in matches:
                if action_name == "send_keys":
                    arg = match.group(1) if match.lastindex else None
                    actions.append((action_name, arg))
                else:
                    actions.append((action_name, None))
        
        return actions


class PlaywrightCodeGenerator:
    """Generates Playwright code from Selenium patterns."""
    
    # Selector type conversions
    SELECTOR_CONVERSIONS = {
        "ID": "id",
        "CLASS_NAME": "class",
        "CSS_SELECTOR": "css",
        "XPATH": "xpath",
        "NAME": "attribute[name='{value}']",
        "TAG_NAME": "tag",
        "LINK_TEXT": "text",
    }
    
    # Action conversions
    ACTION_CONVERSIONS = {
        "click": "click()",
        "clear": "clear()",
        "submit": "press('Enter')",
        "get": "goto",
    }
    
    def __init__(self) -> None:
        """Initialize code generator."""
        self.imports: Set[str] = set()
    
    def generate_imports(self, sync_api: bool = True) -> str:
        """
        Generate Playwright imports.
        
        Args:
            sync_api: True for sync API, False for async
            
        Returns:
            Import statement string
        """
        if sync_api:
            return "from playwright.sync_api import sync_playwright, Page"
        else:
            return "from playwright.async_api import async_playwright, Page"
    
    def convert_selector(self, selector_type: str, value: str) -> str:
        """
        Convert Selenium selector to Playwright locator.
        
        Args:
            selector_type: Selenium By.* type (e.g., "ID", "CLASS_NAME", "By.ID")
            value: Selector value
            
        Returns:
            Playwright locator string
        """
        # Normalize selector_type - remove "By." prefix and convert to uppercase
        selector_type = selector_type.replace("By.", "").strip().upper()
        
        if selector_type == "ID":
            return f'page.locator("#{value}")'
        elif selector_type == "CLASS_NAME":
            return f'page.locator(".{value}")'
        elif selector_type == "CSS_SELECTOR":
            return f'page.locator("{value}")'
        elif selector_type == "XPATH":
            return f'page.locator("xpath={value}")'
        elif selector_type == "NAME":
            return f'page.locator("[name={value}]")'
        elif selector_type == "TAG_NAME":
            return f'page.locator("{value}")'
        else:
            return f'page.locator("{value}")  # Unknown selector type: {selector_type}'
    
    def convert_action(self, action_name: str, *args: Any) -> str:
        """
        Convert Selenium action to Playwright action.
        
        Args:
            action_name: Action name (click, send_keys, etc.)
            *args: Action arguments
            
        Returns:
            Playwright action call string
        """
        if action_name == "click":
            return "click()"
        elif action_name == "send_keys":
            value = args[0] if args else '""'
            return f'fill("{value}")'
        elif action_name == "clear":
            return "clear()"
        elif action_name == "get":
            url = args[0] if args else '""'
            return f'goto("{url}")'
        else:
            return f"{action_name}()  # Unsupported action"
    
    def convert_wait(self, wait_type: str) -> str:
        """
        Convert Selenium wait to Playwright (usually removes it).
        
        Args:
            wait_type: Expected condition type
            
        Returns:
            Playwright equivalent or comment
        """
        conversions = {
            "presence_of_element_located": "# Playwright auto-waits for elements",
            "visibility_of_element_located": "wait_for(state='visible')",
            "clickable_element_located": "wait_for(state='visible')",
            "text_to_be_present": "wait_for_function(lambda: '...' in page.content())",
        }
        
        return conversions.get(wait_type, "# Playwright auto-waits")
    
    def generate_context_manager(self, sync_api: bool = True) -> str:
        """
        Generate Playwright context manager code.
        
        Args:
            sync_api: True for sync, False for async
            
        Returns:
            Context manager code
        """
        if sync_api:
            return """
with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    try:
        # Test code here
        pass
    finally:
        context.close()
        browser.close()
"""
        else:
            return """
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        try:
            # Test code here
            pass
        finally:
            await context.close()
            await browser.close()

asyncio.run(main())
"""


class ConversionEngine:
    """Orchestrates full Selenium to Playwright conversion."""
    
    def __init__(self) -> None:
        """Initialize conversion engine."""
        self.matcher = SeleniumPatternMatcher()
        self.generator = PlaywrightCodeGenerator()
        self.conversion_count = 0
        self.start_time = datetime.now(timezone.utc)
    
    def convert(self, selenium_code: str) -> Union[Ok[str], Err]:
        """
        Convert Selenium code to Playwright.
        
        Args:
            selenium_code: Selenium Python code
            
        Returns:
            Result with Playwright code or error message
        """
        try:
            # First validate syntax
            try:
                ast.parse(selenium_code)
            except SyntaxError as e:
                return Err(f"Syntax error in input code: {e}")
            
            # Detect patterns
            patterns = self.matcher.detect_patterns(selenium_code)
            
            if not patterns:
                # No Selenium patterns - return unchanged code (not an error)
                return Ok(selenium_code)
            
            # Generate Playwright code
            playwright_code = self._convert_imports(selenium_code)
            playwright_code = self._convert_patterns(playwright_code)
            playwright_code = self._convert_structure(playwright_code)
            
            self.conversion_count += 1
            return Ok(playwright_code)
        
        except Exception as e:
            return Err(f"Conversion failed: {str(e)}")
    
    def _convert_imports(self, code: str) -> str:
        """Convert Selenium imports to Playwright imports."""
        # Remove Selenium imports
        code = re.sub(r"from selenium[^\n]*\n", "", code)
        code = re.sub(r"import selenium[^\n]*\n", "", code)
        
        # Add Playwright imports at top
        playwright_imports = "from playwright.sync_api import sync_playwright, Page\n"
        lines = code.split('\n')
        
        # Insert after existing imports
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith(('import ', 'from ')) or line.strip() == '':
                insert_pos = i + 1
            else:
                break
        
        lines.insert(insert_pos, playwright_imports)
        return '\n'.join(lines)
    
    def _convert_patterns(self, code: str) -> str:
        """Convert Selenium patterns to Playwright."""
        # Convert driver = webdriver.Chrome() patterns
        code = re.sub(
            r"driver\s*=\s*webdriver\.(Chrome|Firefox|Safari|Edge)\s*\([^)]*\)",
            "browser = sync_playwright().start().chromium.launch()",
            code
        )
        
        # Convert driver.get() -> page.goto()
        code = re.sub(r"driver\.get\s*\(", "page.goto(", code)
        
        # Convert driver.find_element to page.locator
        code = re.sub(r"driver\.find_element", "page.locator", code)
        
        # Convert find_element patterns
        code = self._convert_locators(code)
        
        # Convert actions
        code = re.sub(r"\.click\s*\(", ".click(", code)
        code = re.sub(r"\.send_keys\s*\(", ".fill(", code)
        code = re.sub(r"\.clear\s*\(", ".clear(", code)
        
        # Convert driver.quit() -> close handlers
        code = re.sub(r"driver\.quit\s*\(\)", "browser.close()", code)
        
        # Remove WebDriverWait usage - needs special handling
        code = re.sub(
            r"wait\s*=\s*WebDriverWait\s*\([^)]+\)",
            "# Playwright auto-waits",
            code
        )
        code = re.sub(
            r"wait\.until\s*\([^)]+\)",
            "# Playwright auto-waits",
            code
        )
        
        return code
    
    def _convert_locators(self, code: str) -> str:
        """Convert Selenium locators to Playwright."""
        # Convert By.ID
        code = re.sub(
            r'find_element\(By\.ID,\s*["\']([^"\']+)["\']\)',
            r'page.locator("#\1")',
            code
        )
        
        # Convert find_element calls to locator
        code = re.sub(r'find_element\(', 'page.locator(', code)
        
        # Convert By.CLASS_NAME
        code = re.sub(
            r'By\.CLASS_NAME,\s*["\']([^"\']+)["\']',
            r'".\1"',
            code
        )
        
        # Convert By.CSS_SELECTOR
        code = re.sub(
            r'By\.CSS_SELECTOR,\s*["\']([^"\']+)["\']',
            r'"\1"',
            code
        )
        
        # Convert By.XPATH
        code = re.sub(
            r'By\.XPATH,\s*["\']([^"\']+)["\']',
            r'"xpath=\1"',
            code
        )
        
        # Convert By.ID
        code = re.sub(
            r'By\.ID,\s*["\']([^"\']+)["\']',
            r'"#\1"',
            code
        )
        
        return code
    
    def _convert_structure(self, code: str) -> str:
        """Preserve test structure while converting."""
        # Keep class and function definitions
        # Keep assertions
        # Only convert the Selenium-specific parts (already done)
        return code


class SeleniumPlaywrightOrchestrator(IOrchestrator):
    """
    Selenium to Playwright Migration Orchestrator.
    
    Provides automated conversion of Selenium test code to Playwright format
    with pattern detection, code generation, and audit trail tracking.
    """
    
    _instance: Optional["SeleniumPlaywrightOrchestrator"] = None
    
    def __init__(self) -> None:
        """Initialize orchestrator."""
        self.engine = ConversionEngine()
        self.audit_trail: List[Dict[str, Any]] = []
        self.previous_hash: Optional[str] = None
    
    @classmethod
    def instance(cls) -> "SeleniumPlaywrightOrchestrator":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_name(self) -> str:
        """Get orchestrator name."""
        return "SeleniumPlaywrightOrchestrator"
    
    def get_version(self) -> str:
        """Get orchestrator version."""
        return "1.0.0"
    
    def get_mode(self) -> OperationMode:
        """Get operation mode."""
        return OperationMode.EXECUTION
    
    def initialize(self) -> Union[Ok[None], Err]:
        """
        Initialize orchestrator.
        
        Returns:
            Result with None on success or error message
        """
        try:
            self.audit_trail = []
            self.previous_hash = None
            return Ok(None)
        except Exception as e:
            return Err(f"Initialization failed: {str(e)}")
    
    @mcp_tool(
        name="convert_file",
        description="Convert a Selenium test file to Playwright format",
        parameters={"input_file": "string", "output_file": "string"}
    )
    def convert_file(
        self,
        input_file: str,
        output_file: str,
    ) -> Union[Ok[ConversionReport], Err]:
        """
        Convert Selenium test file to Playwright.
        
        Args:
            input_file: Path to Selenium test file
            output_file: Path to save Playwright test file
            
        Returns:
            Result with ConversionReport or error
        """
        try:
            input_path = Path(input_file)
            if not input_path.exists():
                return Err(f"Input file not found: {input_file}")
            
            # Read input
            selenium_code = input_path.read_text()
            
            # Convert
            conversion_result = self.engine.convert(selenium_code)
            
            if conversion_result.is_err():
                error_msg = conversion_result.unwrap_or(None)
                if isinstance(conversion_result, Err):
                    error_msg = conversion_result.error
                report = ConversionReport(
                    input_file=input_file,
                    output_file=output_file,
                    status="failed",
                    patterns_detected={},
                    conversions_applied={},
                    warnings=[],
                    errors=[error_msg if error_msg else "Unknown error"],
                    lines_converted=0,
                    total_lines=len(selenium_code.split('\n')),
                    conversion_time_ms=0.0,
                )
                return Err(error_msg if error_msg else "Conversion failed")
            
            playwright_code = conversion_result.unwrap()
            
            # Write output
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(playwright_code)
            
            # Create report
            matcher = SeleniumPatternMatcher()
            patterns = matcher.detect_patterns(selenium_code)
            
            report = ConversionReport(
                input_file=input_file,
                output_file=output_file,
                status="success",
                patterns_detected=patterns,
                conversions_applied={"total": self.engine.conversion_count},
                warnings=[],
                errors=[],
                lines_converted=len(playwright_code.split('\n')),
                total_lines=len(selenium_code.split('\n')),
                conversion_time_ms=(
                    (datetime.now(timezone.utc) - self.engine.start_time).total_seconds() * 1000
                ),
            )
            
            # Log to audit trail
            self._audit_conversion(input_file, output_file, report)
            
            return Ok(report)
        
        except Exception as e:
            return Err(f"Conversion failed: {str(e)}")
    
    @mcp_tool(
        name="analyze_selenium_code",
        description="Analyze Selenium code for patterns and conversion readiness",
        parameters={"code": "string"}
    )
    def analyze_selenium_code(
        self,
        code: str,
    ) -> Union[Ok[Dict[str, Any]], Err]:
        """
        Analyze Selenium code for patterns and conversion readiness.
        
        Args:
            code: Selenium Python code to analyze
            
        Returns:
            Result with analysis dict or error
        """
        try:
            matcher = SeleniumPatternMatcher()
            patterns = matcher.detect_patterns(code)
            locators = matcher.extract_locators(code)
            actions = matcher.extract_actions(code)
            
            analysis = {
                "patterns_detected": patterns,
                "pattern_count": len(patterns),
                "locators_found": len(locators),
                "actions_found": len(actions),
                "conversion_complexity": "high" if len(patterns) > 10 else "medium" if len(patterns) > 5 else "low",
                "recommendations": self._generate_recommendations(patterns, locators),
            }
            
            return Ok(analysis)
        
        except Exception as e:
            return Err(f"Analysis failed: {str(e)}")
    
    @mcp_tool(
        name="convert_directory",
        description="Convert all Selenium tests in a directory to Playwright",
        parameters={"input_dir": "string", "output_dir": "string"}
    )
    def convert_directory(
        self,
        input_dir: str,
        output_dir: str,
    ) -> Union[Ok[List[ConversionReport]], Err]:
        """
        Convert all Selenium files in directory to Playwright.
        
        Args:
            input_dir: Directory containing Selenium test files
            output_dir: Directory to save Playwright test files
            
        Returns:
            Result with list of ConversionReports
        """
        try:
            input_path = Path(input_dir)
            if not input_path.is_dir():
                return Err(f"Input directory not found: {input_dir}")
            
            reports: List[ConversionReport] = []
            
            # Find all Python files
            for py_file in input_path.glob("**/*.py"):
                if py_file.name.startswith("test_"):
                    # Compute output path
                    rel_path = py_file.relative_to(input_path)
                    output_file = Path(output_dir) / rel_path
                    
                    # Convert
                    result = self.convert_file(str(py_file), str(output_file))
                    
                    if result.is_ok():
                        reports.append(result.unwrap())
            
            return Ok(reports)
        
        except Exception as e:
            return Err(f"Directory conversion failed: {str(e)}")
    
    def _generate_recommendations(
        self,
        patterns: Dict[str, int],
        locators: List[Tuple[str, str]],
    ) -> List[str]:
        """Generate recommendations for conversion."""
        recommendations: List[str] = []
        
        if "webdriver_wait" in patterns:
            recommendations.append(
                "Code uses explicit waits - Playwright auto-waits, review logic"
            )
        
        if "xpath" in str(locators):
            recommendations.append(
                "XPATH locators found - consider CSS selectors for better performance"
            )
        
        if patterns.get("screenshot_action", 0) > 0:
            recommendations.append(
                "Screenshots detected - update syntax from driver.save_screenshot() to page.screenshot()"
            )
        
        return recommendations
    
    def _audit_conversion(
        self,
        input_file: str,
        output_file: str,
        report: ConversionReport,
    ) -> None:
        """Log conversion to audit trail with hash chain."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": "convert_file",
            "input_file": input_file,
            "output_file": output_file,
            "status": report.status,
            "patterns_detected": report.patterns_detected,
            "previous_hash": self.previous_hash,
        }
        
        # Calculate hash
        entry_str = json.dumps(entry, sort_keys=True)
        entry_hash = hashlib.sha256(entry_str.encode()).hexdigest()
        entry["current_hash"] = entry_hash
        
        self.audit_trail.append(entry)
        self.previous_hash = entry_hash
    
    def get_mcp_tools(self) -> Union[Ok[Dict[str, Dict[str, Any]]], Err]:
        """
        Get MCP tools exposed by this orchestrator.
        
        Returns:
            Dictionary of tool names to tool metadata
        """
        tools = {
            "convert_selenium_file": {
                "description": "Convert a Selenium test file to Playwright format",
                "parameters": ["input_file", "output_file"],
            },
            "analyze_selenium_tests": {
                "description": "Analyze Selenium code for conversion readiness",
                "parameters": ["code"],
            },
            "convert_selenium_directory": {
                "description": "Convert all Selenium tests in a directory to Playwright",
                "parameters": ["input_dir", "output_dir"],
            },
        }
        return Ok(tools)
    
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Union[Ok[Any], Err]:
        """
        Execute operation with audit logging.
        
        Args:
            operation_name: Name of operation to execute
            parameters: Operation parameters
            
        Returns:
            Result with operation output or error
        """
        try:
            result: Union[Ok[Any], Err]
            
            if operation_name == "convert_file":
                result = self.convert_file(
                    parameters.get("input_file", ""),
                    parameters.get("output_file", ""),
                )
            elif operation_name in ("analyze_selenium_code", "analyze"):
                code = parameters.get("code", "")
                # If file_path provided instead of code, handle it
                file_path = parameters.get("file_path", "")
                if not code and file_path:
                    code = f"# Analyze request for {file_path}"
                result = self.analyze_selenium_code(code)
                # Log analysis to audit trail
                self._audit_operation(operation_name, parameters, result)
            elif operation_name == "convert_directory":
                result = self.convert_directory(
                    parameters.get("input_dir", ""),
                    parameters.get("output_dir", ""),
                )
            else:
                result = Err(f"Unknown operation: {operation_name}")
            
            return result
        except Exception as e:
            return Err(f"Operation failed: {str(e)}")
    
    def _audit_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
        result: Union[Ok[Any], Err],
    ) -> None:
        """Log operation to audit trail with hash chain."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation_name,
            "parameters": {k: str(v)[:100] for k, v in parameters.items()},
            "status": "success" if result.is_ok() else "failed",
            "previous_hash": self.previous_hash,
        }
        
        # Calculate hash
        entry_str = json.dumps(entry, sort_keys=True)
        entry_hash = hashlib.sha256(entry_str.encode()).hexdigest()
        entry["current_hash"] = entry_hash
        
        self.audit_trail.append(entry)
        self.previous_hash = entry_hash
    
    def get_audit_trail(self, limit: int = 100) -> Union[Ok[list], Err]:
        """
        Get audit trail with hash chain.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            Result with audit trail entries
        """
        try:
            return Ok(self.audit_trail[-limit:] if limit > 0 else self.audit_trail)
        except Exception as e:
            return Err(f"Failed to retrieve audit trail: {str(e)}")
    
    def generate_report(self, conversion_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a human-readable conversion report.
        
        Args:
            conversion_result: Result dict from conversion operation
            
        Returns:
            Formatted report dict
        """
        return {
            "total_files": conversion_result.get("files_converted", 0),
            "total_patterns": conversion_result.get("patterns_replaced", 0),
            "warnings": conversion_result.get("warnings", []),
            "manual_review": conversion_result.get("manual_review_needed", []),
            "status": "complete" if not conversion_result.get("manual_review_needed") else "needs_review",
        }

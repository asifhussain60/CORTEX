"""
ErrorCorrector Agent - Modular Version

Automatically detects, parses, and corrects errors in code.
This is the coordinator that delegates to specialized parsers, strategies, and validators.

ISOLATION NOTICE: This agent fixes errors in TARGET APPLICATION code only.
It NEVER modifies CORTEX/tests/ - those are protected system health tests.
"""

from typing import Dict, Any, List, Optional

from ..base_agent import BaseAgent, AgentRequest, AgentResponse
from ..agent_types import IntentType

# Import parsers
from .parsers import (
    PytestErrorParser,
    SyntaxErrorParser,
    ImportErrorParser,
    RuntimeErrorParser,
    LinterErrorParser
)

# Import strategies
from .strategies import (
    IndentationFixStrategy,
    ImportFixStrategy,
    SyntaxFixStrategy,
    PackageFixStrategy
)

# Import validators
from .validators import PathValidator, FixValidator


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
        
        # Initialize parsers
        self.parsers = [
            PytestErrorParser(),
            SyntaxErrorParser(),
            ImportErrorParser(),
            RuntimeErrorParser(),
            LinterErrorParser()
        ]
        
        # Initialize fix strategies
        self.strategies = [
            IndentationFixStrategy(),
            ImportFixStrategy(),
            SyntaxFixStrategy(),
            PackageFixStrategy()
        ]
        
        # Initialize validators
        self.path_validator = PathValidator([
            "CORTEX/tests",
            "CORTEX/src/cortex_agents",
            "cortex-brain"
        ])
        self.fix_validator = FixValidator()
    
    def can_handle(self, request: AgentRequest) -> bool:
        """Can handle error correction requests."""
        intent_lower = request.intent.lower()
        
        if request.intent in [IntentType.FIX.value, IntentType.DEBUG.value]:
            return True
        
        error_keywords = ["fix_error", "correct", "debug", "resolve_error"]
        if any(keyword in intent_lower for keyword in error_keywords):
            return True
        
        if "error_output" in request.context:
            return True
        
        return False
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute error correction."""
        # Extract rule context for Phase 3: Summary generation control (before try block)
        rule_context = request.context.get("rule_context", {})
        skip_summary = rule_context.get("skip_summary_generation", False)
        
        try:
            error_output = request.context.get("error_output", "")
            file_path = request.context.get("file_path")
            
            if not error_output or not error_output.strip():
                return AgentResponse(
                    success=False,
                    result={},
                    message="No error output provided",
                    metadata={"skip_summary": skip_summary}
                )
            
            # Check if file is protected
            if file_path and self.path_validator.is_protected(file_path):
                return AgentResponse(
                    success=False,
                    result={"error": "protected_path"},
                    message=f"Cannot auto-fix protected path: {file_path}",
                    metadata={"skip_summary": skip_summary}
                )
            
            # Parse the error using appropriate parser
            parsed_error = self._parse_error(error_output)
            
            if not parsed_error.get("detected"):
                return AgentResponse(
                    success=False,
                    result=parsed_error,
                    message="Could not parse error",
                    metadata={"skip_summary": skip_summary}
                )
            
            # Find applicable fix patterns
            fix_patterns = self._get_builtin_patterns(parsed_error)
            
            if not fix_patterns:
                # Build result - conditionally include verbose error details
                result = {"recommendation": "Manual review needed"}
                if not skip_summary:
                    result.update({
                        "parsed_error": parsed_error,
                        "fix_patterns": []
                    })
                
                return AgentResponse(
                    success=True,
                    result=result,
                    message="Error detected but no automatic fix available",
                    metadata={"skip_summary": skip_summary}
                )
            
            # Apply the best fix pattern
            fix_result = self._apply_fix(parsed_error, fix_patterns, file_path)
            
            # Conditionally suppress verbose error analysis
            if skip_summary and "parsed_error" in fix_result:
                # Keep only essential fields for execution intents
                fix_result = {
                    "success": fix_result["success"],
                    "message": fix_result.get("message"),
                    "fix_applied": fix_result.get("fix_applied", False)
                }
            
            return AgentResponse(
                success=fix_result["success"],
                result=fix_result,
                message=fix_result.get("message", "Fix applied successfully"),
                metadata={"skip_summary": skip_summary}
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                result={"error": str(e)},
                message=f"Error correction failed: {str(e)}",
                metadata={"skip_summary": skip_summary}
            )
    
    def _parse_error(self, error_output: str) -> Dict[str, Any]:
        """Parse error using appropriate parser."""
        # Try each parser until one succeeds
        for parser in self.parsers:
            if parser.can_parse(error_output):
                parsed = parser.parse(error_output)
                parsed["detected"] = bool(parsed)
                return parsed
        
        # No parser could handle this error
        return {"detected": False, "type": "unknown"}
    
    def _get_builtin_patterns(self, parsed_error: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate fix patterns based on parsed error."""
        patterns = []
        error_type = parsed_error.get("type", "unknown")
        category = parsed_error.get("category", "unknown")
        
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
                    "action": "fix_syntax",
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
                    "action": "add_import",
                    "params": {"name": undefined}
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
                    "action": "add_import",
                    "params": {}
                })
        
        # Sort by confidence
        patterns.sort(key=lambda p: p.get("confidence", 0.5), reverse=True)
        return patterns
    
    def _apply_fix(
        self,
        parsed_error: Dict[str, Any],
        fix_patterns: List[Dict[str, Any]],
        file_path: Optional[str]
    ) -> Dict[str, Any]:
        """Apply best fix pattern using appropriate strategy."""
        # Try each pattern until one succeeds
        for pattern in fix_patterns:
            # Find strategy that can handle this fix
            for strategy in self.strategies:
                if strategy.can_fix(parsed_error, pattern):
                    fix_result = strategy.apply_fix(parsed_error, pattern, file_path)
                    
                    # Validate the fix
                    if self.fix_validator.validate(fix_result):
                        fix_result["applied_pattern"] = pattern["name"]
                        fix_result["confidence"] = pattern["confidence"]
                        return fix_result
        
        # No strategy could apply a fix
        return {
            "success": False,
            "message": "No applicable fix strategy found"
        }

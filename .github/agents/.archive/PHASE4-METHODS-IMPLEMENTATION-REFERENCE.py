"""
Quick script to add ResponseTemplate methods to orchestrators.
Execute this as reference for what methods to add.

AC_START: AC-PHASE4-METHODS-IMPLEMENTATION-001
"""

# ============================================================================
# MasterOrchestrator - Add this method after existing methods
# ============================================================================

def format_response_header(self, operation: str, status: str) -> str:
    """Format response header with semantic color coding.
    
    Args:
        operation: Operation name (e.g., "FIX 1", "Implementation")
        status: Status string (e.g., "Complete", "In Progress", "Blocked")
    
    Returns:
        Formatted markdown header with emoji prefix
    
    Example:
        header = master.format_response_header("FIX 1", "Complete")
        # Returns: ## ✅ FIX 1: Complete
    """
    return ResponseTemplate.create_header(f"{operation}: {status}")


# ============================================================================
# TDDOrchestrator - Add this method after existing TDD methods
# ============================================================================

def report_test_phase(self, phase: str, passed: int, total: int) -> str:
    """Report test phase status with semantic coloring.
    
    Args:
        phase: TDD phase (RED, GREEN, REFACTOR)
        passed: Number of passing tests
        total: Total number of tests
    
    Returns:
        Formatted header showing phase status
    
    Example:
        header = tdd.report_test_phase("RED", 0, 5)
        # Returns: ## 🔵 TDD: RED Phase Active
    """
    if passed == total:
        status = "GREEN Phase Complete"
        header = ResponseTemplate.create_header(f"TDD: {status}")
    else:
        status = f"RED Phase Active ({passed}/{total})"
        header = ResponseTemplate.create_header(f"TDD: {status}")
    return header


# ============================================================================
# IntentRouter - Add this method after routing methods
# ============================================================================

def format_routing_header(self, intent: str, target: str = None) -> str:
    """Format routing decision header with semantic coloring.
    
    Args:
        intent: Intent type (IMPLEMENT, FIX, REFACTOR)
        target: Optional target (e.g., file path)
    
    Returns:
        Formatted header
    
    Example:
        header = router.format_routing_header("IMPLEMENT", "feature_x.py")
        # Returns: ## ✅ Intent: IMPLEMENT → feature_x.py
    """
    if target:
        operation = f"Intent: {intent} → {target}"
    else:
        operation = f"Intent: {intent}"
    return ResponseTemplate.create_header(operation)


# ============================================================================
# RefactoringOrchestrator - Add this method after refactoring methods
# ============================================================================

def start_refactoring(self, target: str, language: str = None) -> str:
    """Format refactoring start header.
    
    Args:
        target: Target file or component
        language: Programming language (optional)
    
    Returns:
        Formatted header
    
    Example:
        header = refactor.start_refactoring("utils.py", "python")
        # Returns: ## 🔵 Refactor: utils.py (Python)
    """
    if language:
        operation = f"Refactor: {target} ({language})"
    else:
        operation = f"Refactor: {target}"
    return ResponseTemplate.create_header(operation)


# ============================================================================
# LENSSynthesis - Add this method after synthesis methods
# ============================================================================

def format_analysis_header(self, scope: str = "Code", status: str = "Complete") -> str:
    """Format LENS analysis header.
    
    Args:
        scope: Analysis scope (Code, Architecture, Security, etc.)
        status: Status (Complete, In Progress, Blocked)
    
    Returns:
        Formatted header
    
    Example:
        header = lens.format_analysis_header("Architecture", "Complete")
        # Returns: ## ✅ LENS Analysis: Architecture Complete
    """
    operation = f"LENS Analysis: {scope}"
    return ResponseTemplate.create_header(f"{operation} {status}")


# ============================================================================
# Utility: Session Summary Generation (for all orchestrators)
# ============================================================================

def generate_session_summary(
    session_name: str,
    completed: list,
    in_progress: list = None,
    blocked: list = None,
    next_steps: list = None,
    token_usage: tuple = None
) -> str:
    """Generate semantic session summary.
    
    Args:
        session_name: Name of session (e.g., "FIX 1 Implementation")
        completed: List of completed items
        in_progress: List of in-progress items (optional)
        blocked: List of blocked items (optional)
        next_steps: List of next steps (optional)
        token_usage: Tuple of (used, total) for token tracking (optional)
    
    Returns:
        Formatted session summary
    
    Example:
        summary = generate_session_summary(
            session_name="FIX 1",
            completed=["Governance tools implemented", "23/23 tests passing"],
            next_steps=["Push to GitHub", "Deploy"]
        )
    """
    return ResponseTemplate.session_summary(
        session_name=session_name,
        completed_items=completed,
        in_progress_items=in_progress or [],
        blocked_items=blocked or [],
        next_steps=next_steps or [],
        token_usage=token_usage
    )


# ============================================================================
# MCP Tool Response Handler (new file)
# ============================================================================
# Create: cortex/mcp/tools/tool_response_handler.py

"""
Tool Response Handler - Format MCP tool responses with semantic headers

Purpose: Consistent response formatting across all MCP tools
Uses: ResponseTemplate.create_header() and ResponseTemplate.session_summary()
"""

from typing import Dict, Any, Optional, Tuple
from cortex.agents.core.response_template_generator import ResponseTemplate


class ToolResponseHandler:
    """Handler for formatting MCP tool responses."""
    
    @staticmethod
    def format_tool_response(
        tool_name: str,
        result: Dict[str, Any],
        status: str = "Complete",
        metrics: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format MCP tool response with semantic header.
        
        Args:
            tool_name: Name of tool (e.g., "cortex_lens_analyze")
            result: Tool result data
            status: Status string
            metrics: Optional metrics dictionary
        
        Returns:
            Formatted response with header
        """
        header = ResponseTemplate.create_header(f"{tool_name}: {status}")
        
        # Format result
        result_text = ToolResponseHandler._format_result(result)
        
        response = f"{header}\n\n{result_text}"
        
        if metrics:
            metrics_text = ToolResponseHandler._format_metrics(metrics)
            response += f"\n\n{metrics_text}"
        
        return response
    
    @staticmethod
    def _format_result(result: Dict[str, Any]) -> str:
        """Format result dictionary as markdown."""
        lines = []
        for key, value in result.items():
            if isinstance(value, list):
                lines.append(f"- {key}: {len(value)} items")
            elif isinstance(value, dict):
                lines.append(f"- {key}: {len(value)} properties")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    @staticmethod
    def _format_metrics(metrics: Dict[str, Any]) -> str:
        """Format metrics as markdown."""
        lines = ["### 📊 Metrics"]
        for key, value in metrics.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    @staticmethod
    def format_session_summary(
        operation: str,
        completed: list,
        in_progress: list = None,
        blocked: list = None,
        next_steps: list = None,
        token_usage: Optional[Tuple[int, int]] = None
    ) -> str:
        """Generate session summary for operation."""
        return ResponseTemplate.session_summary(
            session_name=operation,
            completed_items=completed,
            in_progress_items=in_progress or [],
            blocked_items=blocked or [],
            next_steps=next_steps or [],
            token_usage=token_usage
        )


# ============================================================================
# Integration: How to use in actual code
# ============================================================================

# Example 1: In MasterOrchestrator
"""
def process_request(self, request):
    try:
        operation = "Process Request"
        result = self._do_process(request)
        header = self.format_response_header(operation, "Complete")
        return f"{header}\n\n{result}"
    except Exception as e:
        header = self.format_response_header(operation, "Failed")
        return f"{header}\n\nError: {str(e)}"
"""

# Example 2: In MCP tool
"""
def cortex_lens_analyze(file_path: str) -> str:
    handler = ToolResponseHandler()
    result = analyze_file(file_path)
    
    return handler.format_tool_response(
        tool_name="cortex_lens_analyze",
        result=result,
        status="Complete",
        metrics={"files_analyzed": 1, "issues_found": 3}
    )
"""

# Example 3: Session summary
"""
def report_completion(self, operation: str):
    summary = ResponseTemplate.session_summary(
        session_name=operation,
        completed_items=self.completed_items,
        in_progress_items=self.in_progress_items,
        next_steps=self.next_steps,
        token_usage=self.get_token_usage()
    )
    return summary
"""

# AC_COMPLETE: AC-PHASE4-METHODS-IMPLEMENTATION-001 ✅

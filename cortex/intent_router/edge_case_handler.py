"""Edge Case Handler - Handles edge cases and boundary conditions.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EdgeCaseType(Enum):
    """Types of edge cases."""
    NULL_INPUT = "null_input"
    EMPTY_INPUT = "empty_input"
    INVALID_TYPE = "invalid_type"
    OUT_OF_BOUNDS = "out_of_bounds"
    MISSING_REQUIRED = "missing_required"
    UNKNOWN = "unknown"


@dataclass
class EdgeCaseResult:
    """Result of edge case handling."""
    
    case_type: EdgeCaseType
    handled: bool
    fallback_used: bool = False
    message: str = ""
    original_value: Any = None
    fallback_value: Any = None


class EdgeCaseHandler:
    """Handles edge cases and boundary conditions in intent routing."""
    
    def __init__(self):
        """Initialize edge case handler."""
        self.handlers: Dict[EdgeCaseType, Callable] = {}
        self.cases_handled: List[EdgeCaseResult] = []
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register default edge case handlers."""
        self.handlers[EdgeCaseType.NULL_INPUT] = self._handle_null
        self.handlers[EdgeCaseType.EMPTY_INPUT] = self._handle_empty
        self.handlers[EdgeCaseType.INVALID_TYPE] = self._handle_invalid_type
        self.handlers[EdgeCaseType.OUT_OF_BOUNDS] = self._handle_out_of_bounds
        self.handlers[EdgeCaseType.MISSING_REQUIRED] = self._handle_missing_required
    
    def _handle_null(self, value: Any, context: Dict[str, Any]) -> Any:
        """Handle null input.
        
        Args:
            value: The null value
            context: Context information
            
        Returns:
            Fallback value or default
        """
        return context.get("default", None)
    
    def _handle_empty(self, value: Any, context: Dict[str, Any]) -> Any:
        """Handle empty input.
        
        Args:
            value: The empty value
            context: Context information
            
        Returns:
            Fallback value or default
        """
        if isinstance(value, str):
            return context.get("default", "")
        elif isinstance(value, (list, dict)):
            return type(value)()
        return value
    
    def _handle_invalid_type(self, value: Any, context: Dict[str, Any]) -> Any:
        """Handle invalid type.
        
        Args:
            value: The invalid value
            context: Context information
            
        Returns:
            Converted or fallback value
        """
        expected_type = context.get("expected_type")
        if expected_type:
            try:
                return expected_type(value)
            except (ValueError, TypeError):
                return context.get("default")
        return value
    
    def _handle_out_of_bounds(self, value: Any, context: Dict[str, Any]) -> Any:
        """Handle out of bounds value.
        
        Args:
            value: The out of bounds value
            context: Context information
            
        Returns:
            Clamped or fallback value
        """
        min_val = context.get("min")
        max_val = context.get("max")
        
        if min_val is not None and value < min_val:
            return min_val
        if max_val is not None and value > max_val:
            return max_val
        
        return value
    
    def _handle_missing_required(self, value: Any, context: Dict[str, Any]) -> Any:
        """Handle missing required value.
        
        Args:
            value: The missing value (None)
            context: Context information
            
        Returns:
            Fallback value or raises exception
        """
        if "default" in context:
            return context["default"]
        raise ValueError(f"Missing required value: {context.get('field_name', 'unknown')}")
    
    def register_handler(self, case_type: EdgeCaseType, handler: Callable) -> None:
        """Register a custom edge case handler.
        
        Args:
            case_type: Type of edge case
            handler: Handler function
        """
        self.handlers[case_type] = handler
    
    def handle(
        self,
        case_type: EdgeCaseType,
        value: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> EdgeCaseResult:
        """Handle an edge case.
        
        Args:
            case_type: Type of edge case
            value: Value to handle
            context: Optional context information
            
        Returns:
            EdgeCaseResult with handling outcome
        """
        context = context or {}
        handler = self.handlers.get(case_type)
        
        if not handler:
            result = EdgeCaseResult(
                case_type=case_type,
                handled=False,
                message=f"No handler for {case_type.value}",
                original_value=value
            )
        else:
            try:
                fallback = handler(value, context)
                result = EdgeCaseResult(
                    case_type=case_type,
                    handled=True,
                    fallback_used=fallback != value,
                    message="Successfully handled",
                    original_value=value,
                    fallback_value=fallback
                )
            except Exception as e:
                result = EdgeCaseResult(
                    case_type=case_type,
                    handled=False,
                    message=f"Handler failed: {str(e)}",
                    original_value=value
                )
        
        self.cases_handled.append(result)
        logger.debug(f"Handled edge case: {case_type.value} - {result.handled}")
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics on handled edge cases.
        
        Returns:
            Dictionary with edge case statistics
        """
        total = len(self.cases_handled)
        handled = sum(1 for c in self.cases_handled if c.handled)
        by_type = {}
        
        for case in self.cases_handled:
            case_type = case.case_type.value
            if case_type not in by_type:
                by_type[case_type] = {"total": 0, "handled": 0}
            by_type[case_type]["total"] += 1
            if case.handled:
                by_type[case_type]["handled"] += 1
        
        return {
            "total_cases": total,
            "handled": handled,
            "failed": total - handled,
            "success_rate": handled / total if total > 0 else 0,
            "by_type": by_type
        }


__all__ = ["EdgeCaseHandler", "EdgeCaseType", "EdgeCaseResult"]

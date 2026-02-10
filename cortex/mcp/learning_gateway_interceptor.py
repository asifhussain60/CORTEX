"""
MCP Gateway Learning Interceptor - Phase 71 S3.

AC-ID: PHASE-71-S3
Purpose: Capture learnings from MCP tool execution as defense-in-depth

Provides backup learning capture for operations that:
1. Bypass OrchestratorBaseProtocol (direct MCP tool calls)
2. Use older orchestrators without Phase 6 learning
3. Call tools from external systems
4. Run in legacy codepaths

Defense-in-depth strategy:
- Protocol Hook (S2) captures for orchestrators ✅
- MCP Gateway Interceptor (S3) captures for direct tool calls ⬅️
- Deduplicates patterns to avoid learning the same thing twice
- Non-blocking (failures don't affect tool execution)

Architecture:
1. MCPServer.call_tool() → LearningInterceptor.before_execution()
2. Tool executes normally
3. MCPServer returns response → LearningInterceptor.after_execution()
4. Extract patterns and merge to knowledge repos
5. Handle duplicates vs. legitimate variations

Author: Asif Hussain
Date: 2026-02-10
"""

import logging
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class InterceptedOperation:
    """Record of MCP tool operation for learning extraction."""
    
    tool_name: str
    parameters: Dict[str, Any]
    result: Any
    execution_time_ms: float
    timestamp: str
    request_id: Optional[str] = None
    
    def to_context(self) -> Dict[str, Any]:
        """Convert to learning context format."""
        return {
            "tool": self.tool_name,
            "parameters": self.parameters,
            "result": self.result,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp,
        }
    
    def get_pattern_hash(self) -> str:
        """Get hash of operation for deduplication."""
        key = f"{self.tool_name}:{self.result}"
        return hashlib.md5(key.encode()).hexdigest()[:8]


@dataclass
class LearningInterceptorMetrics:
    """Metrics for learning interception."""
    
    operations_intercepted: int = 0
    patterns_extracted: int = 0
    patterns_deduplicated: int = 0
    merge_failures: int = 0
    total_execution_time_ms: float = 0.0
    
    # Deduplication tracking
    pattern_hashes: Set[str] = field(default_factory=set)
    
    def record_operation(self, op: InterceptedOperation) -> None:
        """Record an intercepted operation."""
        self.operations_intercepted += 1
        self.total_execution_time_ms += op.execution_time_ms
    
    def is_duplicate(self, pattern_hash: str) -> bool:
        """Check if pattern hash already seen (duplicate detection)."""
        return pattern_hash in self.pattern_hashes
    
    def mark_pattern(self, pattern_hash: str) -> None:
        """Mark pattern as seen."""
        self.pattern_hashes.add(pattern_hash)


class MCPLearningInterceptor:
    """
    Intercept MCP tool calls and extract learnings.
    
    Integration points:
    1. MCPServer.call_tool() - wrap execution
    2. Tool handlers - extract patterns from results
    3. UniversalLearningLoop - merge learnings
    4. Deduplication - avoid duplicate learning
    
    AC-ID: PHASE-71-S3
    """
    
    def __init__(self) -> None:
        """Initialize learning interceptor."""
        self._metrics = LearningInterceptorMetrics()
        self._learning_loop: Optional[Any] = None
        self._initialize_learning_loop()
    
    def _initialize_learning_loop(self) -> None:
        """Initialize learning loop if available."""
        try:
            from cortex.learning import get_learning_loop
            self._learning_loop = get_learning_loop()
            logger.debug("MCP Learning Interceptor initialized with UniversalLearningLoop")
        except ImportError:
            logger.debug("UniversalLearningLoop not available (optional)")
    
    def before_execution(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> None:
        """
        Called before MCP tool execution.
        
        Args:
            tool_name: Name of tool being called
            parameters: Tool parameters
            request_id: MCP request ID (for correlation)
        """
        # Currently no-op - used for pre-execution validation if needed
        logger.debug(f"Intercepting MCP tool: {tool_name}")
    
    def after_execution(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Any,
        execution_time_ms: float,
        request_id: Optional[str] = None
    ) -> None:
        """
        Called after MCP tool execution.
        
        Extracts learnings and merges to knowledge repositories.
        Non-blocking - failures don't affect tool execution.
        
        Args:
            tool_name: Name of tool that was called
            parameters: Tool parameters
            result: Tool execution result
            execution_time_ms: Execution time in milliseconds
            request_id: MCP request ID (for correlation)
        """
        try:
            # Create operation record
            operation = InterceptedOperation(
                tool_name=tool_name,
                parameters=parameters,
                result=result,
                execution_time_ms=execution_time_ms,
                timestamp=datetime.now().isoformat(),
                request_id=request_id,
            )
            
            # Record metrics
            self._metrics.record_operation(operation)
            
            # Check for duplicates
            pattern_hash = operation.get_pattern_hash()
            if self._metrics.is_duplicate(pattern_hash):
                self._metrics.patterns_deduplicated += 1
                logger.debug(f"Skipping duplicate learning: {tool_name} ({pattern_hash})")
                return
            
            # Mark pattern as seen
            self._metrics.mark_pattern(pattern_hash)
            
            # Extract and merge learnings
            self._extract_and_merge_learnings(operation)
            
        except Exception as e:
            # Non-blocking - log but don't raise
            logger.warning(f"Learning interception failed for {tool_name}: {e}")
    
    def _extract_and_merge_learnings(self, operation: InterceptedOperation) -> None:
        """
        Extract patterns from operation and merge to knowledge.
        
        Args:
            operation: Intercepted operation record
        """
        if self._learning_loop is None:
            return
        
        try:
            # Determine operation type from tool name
            operation_type = self._get_operation_type(operation.tool_name)
            
            # Build context for learning capture
            context = operation.to_context()
            context["source"] = "mcp_gateway"  # Mark as MCP-sourced
            
            # Build result dict
            result_dict = (
                operation.result if isinstance(operation.result, dict)
                else {"result": operation.result}
            )
            
            # Capture learnings from this MCP operation
            captures = self._learning_loop.capture_from_operation(
                orchestrator="MCPGateway",
                operation=operation_type,
                context=context,
                result=result_dict,
            )
            
            if captures:
                self._metrics.patterns_extracted += len(captures)
                logger.debug(
                    f"Extracted {len(captures)} learnings from MCP tool: {operation.tool_name}"
                )
            
        except Exception as e:
            self._metrics.merge_failures += 1
            logger.warning(f"Failed to extract learnings from {operation.tool_name}: {e}")
    
    def _get_operation_type(self, tool_name: str) -> str:
        """
        Infer operation type from MCP tool name.
        
        Args:
            tool_name: Name of MCP tool
            
        Returns:
            Operation type (tdd, refactoring, interaction, etc.)
        """
        tool_lower = tool_name.lower()
        
        # Map tool names to operation types
        if "test" in tool_lower or "tdd" in tool_lower:
            return "tdd"
        elif "refactor" in tool_lower:
            return "refactoring"
        elif "review" in tool_lower or "approve" in tool_lower:
            return "interaction"
        elif "enforce" in tool_lower or "govern" in tool_lower:
            return "governance"
        elif "plan" in tool_lower or "schedule" in tool_lower:
            return "coordination"
        elif "lens" in tool_lower or "analyze" in tool_lower:
            return "analysis"
        else:
            return "generic"
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get interceptor metrics.
        
        Returns:
            Dictionary with metrics
        """
        return {
            "operations_intercepted": self._metrics.operations_intercepted,
            "patterns_extracted": self._metrics.patterns_extracted,
            "patterns_deduplicated": self._metrics.patterns_deduplicated,
            "merge_failures": self._metrics.merge_failures,
            "total_execution_time_ms": self._metrics.total_execution_time_ms,
            "unique_patterns_tracked": len(self._metrics.pattern_hashes),
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics (for testing)."""
        self._metrics = LearningInterceptorMetrics()


# Global interceptor instance (singleton)
_interceptor_instance: Optional[MCPLearningInterceptor] = None


def get_mcp_learning_interceptor() -> MCPLearningInterceptor:
    """
    Get global MCP learning interceptor instance.
    
    Returns:
        MCPLearningInterceptor singleton
    """
    global _interceptor_instance
    if _interceptor_instance is None:
        _interceptor_instance = MCPLearningInterceptor()
    return _interceptor_instance


__all__ = [
    "MCPLearningInterceptor",
    "InterceptedOperation",
    "LearningInterceptorMetrics",
    "get_mcp_learning_interceptor",
]

"""
Marker Injection Engine - Strategy Pattern for Debug Marker Placement

Purpose:
    Smart marker placement logic using Strategy Pattern. Different strategies
    for TEST_FAILURE (traceback parsing), REFACTOR_REGRESSION (git diff),
    and GOVERNANCE_VIOLATION (rule location).

Authority:
    - ENH-089 (EventBus-Driven Debugger)
    - WAVE-R Execution Plan Stage 2

AC-ID: AC-WAVE-R-004
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path
import tempfile
import os
from datetime import datetime
from jinja2 import Template


class AbstractInjectionStrategy(ABC):
    """Base class for marker injection strategies."""
    
    @abstractmethod
    def inject(
        self,
        session_id: str,
        file_path: str,
        context: Dict[str, Any],
        **kwargs
    ) -> bool:
        """
        Inject markers into file.
        
        Args:
            session_id: Debug session identifier
            file_path: Target file path
            context: Context information for marker
            **kwargs: Strategy-specific parameters
        
        Returns:
            True if injection successful, False otherwise
        """
        pass


class MarkerInjectionEngine:
    """
    Engine for injecting CORTEX_DEBUG markers into source files.
    
    Uses Strategy Pattern to support multiple injection strategies:
    - test_failure: Parse traceback, inject at failure point
    - refactor_regression: Parse git diff, inject at changed lines
    - governance_violation: Inject at violation location
    
    Example:
        >>> engine = MarkerInjectionEngine()
        >>> engine.inject(
        ...     strategy="test_failure",
        ...     session_id="session-test_failure-20260213",
        ...     file_path="example.py",
        ...     line_number=100,
        ...     context={"test_name": "test_example", "failure_reason": "AssertionError"}
        ... )
        True
    """
    
    # Marker template (Jinja2)
    MARKER_TEMPLATE = Template("""# CORTEX_DEBUG_START
# Session: {{ session_id }}
# Trigger: {{ event_type }}
# Timestamp: {{ timestamp }}
# Context: {{ context_summary }}
# --- Original Code ---
{{ original_code }}
# CORTEX_DEBUG_END
""")
    
    def __init__(self):
        """Initialize MarkerInjectionEngine with strategies."""
        self.strategies: Dict[str, AbstractInjectionStrategy] = {
            "test_failure": TestFailureStrategy(),
            "refactor_regression": RefactorRegressionStrategy(),
            "governance_violation": GovernanceViolationStrategy()
        }
    
    def inject(
        self,
        strategy: str,
        session_id: str,
        file_path: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        """
        Inject debug markers using specified strategy.
        
        Args:
            strategy: Strategy name (test_failure | refactor_regression | governance_violation)
            session_id: Debug session identifier
            file_path: Target file path
            context: Context information for marker
            **kwargs: Strategy-specific parameters (e.g., line_number for test_failure)
        
        Returns:
            True if injection successful, False otherwise
        """
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}. Available: {list(self.strategies.keys())}")
        
        context = context or {}
        
        # Delegate to strategy
        strategy_obj = self.strategies[strategy]
        return strategy_obj.inject(
            session_id=session_id,
            file_path=file_path,
            context=context,
            engine=self,  # Pass engine for template access
            **kwargs
        )
    
    def format_marker(
        self,
        session_id: str,
        event_type: str,
        context_summary: str,
        original_code: str
    ) -> str:
        """
        Format marker using template.
        
        Args:
            session_id: Debug session identifier
            event_type: Trigger type (TEST_FAILURE | REFACTOR_REGRESSION | GOVERNANCE_VIOLATION)
            context_summary: Brief description of issue
            original_code: Original code to wrap
        
        Returns:
            Formatted marker string
        """
        return self.MARKER_TEMPLATE.render(
            session_id=session_id,
            event_type=event_type,
            context_summary=context_summary,
            timestamp=datetime.now().isoformat(),
            original_code=original_code
        )


class TestFailureStrategy(AbstractInjectionStrategy):
    """
    Strategy for TEST_FAILURE events.
    
    Parses test failure traceback to identify the actual failure point
    in user code (skipping test framework lines).
    """
    
    def inject(
        self,
        session_id: str,
        file_path: str,
        context: Dict[str, Any],
        engine: MarkerInjectionEngine,
        line_number: int = 0,
        **kwargs
    ) -> bool:
        """
        Inject markers at test failure location.
        
        Args:
            session_id: Debug session identifier
            file_path: Target file path
            context: Context with test_name, failure_reason
            engine: MarkerInjectionEngine instance
            line_number: Line where failure occurred
            **kwargs: Additional parameters
        
        Returns:
            True if injection successful
        """
        # Read file content
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return False
            
            content = file_path_obj.read_text()
            lines = content.splitlines()
            
            # Check if markers already exist
            if session_id in content:
                return True  # Already injected
            
            # Determine injection point (default to line_number or first line)
            target_line = max(0, line_number - 1) if line_number > 0 else 0
            target_line = min(target_line, len(lines) - 1)
            
            # Extract context window (3 lines before and after)
            start_line = max(0, target_line - 3)
            end_line = min(len(lines), target_line + 4)
            original_code = "\n".join(lines[start_line:end_line])
            
            # Format context summary
            test_name = context.get("test_name", "unknown")
            failure_reason = context.get("failure_reason", "unknown")
            context_summary = f"TEST_FAILURE in {test_name}: {failure_reason}"
            
            # Generate marker
            marker = engine.format_marker(
                session_id=session_id,
                event_type="TEST_FAILURE",
                context_summary=context_summary,
                original_code=original_code
            )
            
            # Insert marker at target line
            lines.insert(start_line, marker)
            
            # Write to file atomically
            self._write_atomic(file_path_obj, "\n".join(lines))
            
            return True
            
        except Exception as e:
            print(f"Error injecting markers: {e}")
            return False
    
    def _write_atomic(self, file_path: Path, content: str) -> None:
        """
        Write file atomically using tempfile + rename.
        
        Args:
            file_path: Target file path
            content: New file content
        """
        # Create temporary file in same directory
        temp_fd, temp_path = tempfile.mkstemp(
            dir=file_path.parent,
            prefix=".cortex_debug_",
            suffix=".tmp"
        )
        
        try:
            # Write content
            with os.fdopen(temp_fd, 'w') as f:
                f.write(content)
            
            # Atomic rename
            os.replace(temp_path, file_path)
            
        except Exception:
            # Cleanup on failure
            try:
                os.unlink(temp_path)
            except Exception:
                pass
            raise


class RefactorRegressionStrategy(AbstractInjectionStrategy):
    """
    Strategy for REFACTOR_REGRESSION events.
    
    Parses git diff to identify changed lines and injects markers
    at modification points.
    """
    
    def inject(
        self,
        session_id: str,
        file_path: str,
        context: Dict[str, Any],
        engine: MarkerInjectionEngine,
        **kwargs
    ) -> bool:
        """
        Inject markers at refactor regression locations.
        
        Args:
            session_id: Debug session identifier
            file_path: Target file path
            context: Context with refactor_type, regression_type
            engine: MarkerInjectionEngine instance
            **kwargs: Additional parameters
        
        Returns:
            True if injection successful
        """
        # Simplified implementation: inject at file start
        # Full implementation would parse git diff
        
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return False
            
            content = file_path_obj.read_text()
            
            # Check if markers already exist
            if session_id in content:
                return True
            
            lines = content.splitlines()
            
            # Extract first 10 lines as context
            original_code = "\n".join(lines[:10])
            
            # Format context summary
            refactor_type = context.get("refactor_type", "unknown")
            regression_type = context.get("regression_type", "unknown")
            context_summary = f"REFACTOR_REGRESSION ({refactor_type}): {regression_type} detected"
            
            # Generate marker
            marker = engine.format_marker(
                session_id=session_id,
                event_type="REFACTOR_REGRESSION",
                context_summary=context_summary,
                original_code=original_code
            )
            
            # Insert at start
            lines.insert(0, marker)
            
            # Write atomically
            TestFailureStrategy()._write_atomic(file_path_obj, "\n".join(lines))
            
            return True
            
        except Exception as e:
            print(f"Error injecting markers: {e}")
            return False


class GovernanceViolationStrategy(AbstractInjectionStrategy):
    """
    Strategy for GOVERNANCE_VIOLATION events.
    
    Injects markers at governance rule violation locations with
    rule documentation reference.
    """
    
    def inject(
        self,
        session_id: str,
        file_path: str,
        context: Dict[str, Any],
        engine: MarkerInjectionEngine,
        **kwargs
    ) -> bool:
        """
        Inject markers at governance violation location.
        
        Args:
            session_id: Debug session identifier
            file_path: Target file path
            context: Context with rule_id, violation_details
            engine: MarkerInjectionEngine instance
            **kwargs: Additional parameters
        
        Returns:
            True if injection successful
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return False
            
            content = file_path_obj.read_text()
            
            # Check if markers already exist
            if session_id in content:
                return True
            
            lines = content.splitlines()
            
            # Extract violation line if provided
            violation_details = context.get("violation_details", {})
            violation_line = violation_details.get("line", 0)
            target_line = max(0, violation_line - 1) if violation_line > 0 else 0
            target_line = min(target_line, len(lines) - 1)
            
            # Extract context window
            start_line = max(0, target_line - 2)
            end_line = min(len(lines), target_line + 3)
            original_code = "\n".join(lines[start_line:end_line])
            
            # Format context summary
            rule_id = context.get("rule_id", "unknown")
            context_summary = f"GOVERNANCE_VIOLATION: {rule_id} at line {violation_line}"
            
            # Generate marker
            marker = engine.format_marker(
                session_id=session_id,
                event_type="GOVERNANCE_VIOLATION",
                context_summary=context_summary,
                original_code=original_code
            )
            
            # Insert at violation line
            lines.insert(start_line, marker)
            
            # Write atomically
            TestFailureStrategy()._write_atomic(file_path_obj, "\n".join(lines))
            
            return True
            
        except Exception as e:
            print(f"Error injecting markers: {e}")
            return False

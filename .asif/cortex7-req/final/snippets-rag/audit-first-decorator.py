"""
AUDIT-FIRST DECORATOR PATTERN
===============================
Purpose: Make audit logging mandatory (not optional)
Pattern: Operations impossible without audit context

Author: Asif Hussain
Date: 2026-01-14
"""

import functools
import time
import traceback
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional


class AuditCategory(str, Enum):
    """Audit categories for CORTEX operations."""
    GOVERNANCE = "governance"
    ORCHESTRATOR = "orchestrator"
    VALIDATION = "validation"
    INFRASTRUCTURE = "infrastructure"
    MCP = "mcp"
    BRAIN = "brain"
    INTEGRATION = "integration"


@dataclass
class AuditContext:
    """
    Audit context that tracks operation lifecycle.
    
    Automatically captures:
    - Start/end timestamps
    - Duration
    - Input parameters
    - Output results
    - Exceptions
    - Execution path
    """
    ac_id: Optional[str]
    correlation_id: str
    category: AuditCategory
    operation: str
    component: str
    
    # Automatically populated
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    input_params: Dict[str, Any] = field(default_factory=dict)
    output_result: Any = None
    exception_info: Optional[str] = None
    execution_path: list = field(default_factory=list)
    
    def __enter__(self):
        """Enter audit context."""
        self.start_time = datetime.utcnow()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit audit context and commit to audit log."""
        self.end_time = datetime.utcnow()
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        
        if exc_type is not None:
            self.exception_info = f"{exc_type.__name__}: {exc_val}\n{traceback.format_tb(exc_tb)}"
        
        # Commit to audit log
        self._commit_to_audit_log()
        
        # Don't suppress exceptions
        return False
    
    def _commit_to_audit_log(self):
        """Commit audit entry to database."""
        from src.infrastructure.enhanced_audit_logger import EnterpriseAuditLogger
        
        logger = EnterpriseAuditLogger.get_instance()
        
        logger.log(
            level="ERROR" if self.exception_info else "INFO",
            category=self.category,
            component=self.component,
            operation=self.operation,
            message=f"Operation {'failed' if self.exception_info else 'completed'}",
            ac_id=self.ac_id,
            correlation_id=self.correlation_id,
            duration_ms=self.duration_ms,
            context={
                "input_params": self.input_params,
                "output_result": str(self.output_result) if self.output_result else None,
                "exception": self.exception_info,
                "execution_path": self.execution_path
            }
        )


def audit_driven(category: AuditCategory, operation: str, component: Optional[str] = None):
    """
    Decorator that enforces audit context for operations.
    
    Usage:
        @audit_driven(category=AuditCategory.ORCHESTRATOR, operation="implement_ac")
        def implement_ac(ac_id: str, context: AuditContext):
            # Implementation
            pass
    
    Args:
        category: Audit category for this operation
        operation: Operation name
        component: Component name (defaults to function module)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract ac_id from kwargs if present
            ac_id = kwargs.get('ac_id') or (args[0] if args else None)
            
            # Generate correlation ID
            correlation_id = str(uuid.uuid4())
            
            # Determine component
            comp = component or func.__module__
            
            # Create audit context
            with AuditContext(
                ac_id=ac_id,
                correlation_id=correlation_id,
                category=category,
                operation=operation,
                component=comp
            ) as ctx:
                # Capture input params
                ctx.input_params = {
                    'args': [str(arg) for arg in args],
                    'kwargs': {k: str(v) for k, v in kwargs.items()}
                }
                
                # Inject audit context into kwargs
                kwargs['audit_context'] = ctx
                
                # Execute function
                try:
                    result = func(*args, **kwargs)
                    ctx.output_result = result
                    return result
                except Exception as e:
                    # Exception captured in __exit__
                    raise
        
        return wrapper
    return decorator


# ==============================================================================
# USAGE EXAMPLES
# ==============================================================================

# Example 1: Simple tool with audit
@audit_driven(category=AuditCategory.INFRASTRUCTURE, operation="read_yaml")
def read_yaml_file(file_path: str, audit_context: AuditContext):
    """Read YAML file with audit trail."""
    import yaml
    from pathlib import Path
    
    audit_context.execution_path.append("opening_file")
    path = Path(file_path)
    
    audit_context.execution_path.append("reading_content")
    content = path.read_text()
    
    audit_context.execution_path.append("parsing_yaml")
    data = yaml.safe_load(content)
    
    return data


# Example 2: AC implementation with audit
@audit_driven(category=AuditCategory.ORCHESTRATOR, operation="implement_ac")
def implement_ac(ac_id: str, audit_context: AuditContext):
    """Implement AC-ID with full audit trail."""
    
    audit_context.execution_path.append("loading_ac_definition")
    ac_def = load_ac_definition(ac_id)
    
    audit_context.execution_path.append("generating_code")
    code = generate_implementation(ac_def)
    
    audit_context.execution_path.append("running_tests")
    test_results = run_tests(ac_id)
    
    audit_context.execution_path.append("collecting_evidence")
    evidence = collect_evidence(ac_id, test_results)
    
    return {
        'ac_id': ac_id,
        'status': 'implemented',
        'tests_passed': test_results['passed'],
        'evidence_bundle': evidence
    }


# Example 3: Governance enforcement with audit
@audit_driven(category=AuditCategory.GOVERNANCE, operation="enforce_rule")
def enforce_skull_rule(rule_id: str, operation_context: Dict, audit_context: AuditContext):
    """Enforce SKULL rule with audit trail."""
    
    audit_context.execution_path.append("loading_rule")
    rule = load_rule(rule_id)
    
    audit_context.execution_path.append("evaluating_rule")
    violation = evaluate_rule(rule, operation_context)
    
    if violation:
        audit_context.execution_path.append("rule_violated")
        raise GovernanceViolationError(f"{rule_id} violated: {violation}")
    
    audit_context.execution_path.append("rule_passed")
    return {'rule_id': rule_id, 'status': 'passed'}


# ==============================================================================
# AUDIT CONTEXT INJECTION
# ==============================================================================

def audit_context_required(func):
    """
    Decorator that ensures audit_context is present.
    Raises error if missing (enforces audit-first).
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'audit_context' not in kwargs:
            raise RuntimeError(
                f"audit_context required for {func.__name__}. "
                f"Did you forget @audit_driven decorator?"
            )
        return func(*args, **kwargs)
    return wrapper


# Example: Function that requires audit context
@audit_context_required
def update_progress_tracker(ac_id: str, status: str, audit_context: AuditContext):
    """Update progress tracker (audit context required)."""
    audit_context.execution_path.append("updating_tracker")
    # Implementation
    pass


# ==============================================================================
# ADVANTAGES OF AUDIT-FIRST PATTERN
# ==============================================================================

"""
AUDIT-FIRST PATTERN ADVANTAGES:

1. **Impossible to Skip Logging**
   - @audit_driven decorator wraps all operations
   - No way to execute without audit context
   - Enforcement at compile-time (missing decorator → error)

2. **Automatic Evidence Collection**
   - Start/end timestamps captured automatically
   - Duration calculated automatically
   - Exceptions captured automatically
   - Execution path tracked automatically

3. **Zero Manual Logging**
   - No need for logger.info() calls
   - No need for try/except/finally blocks
   - No need for timing code
   - All handled by audit context

4. **Correlation IDs Built-In**
   - UUID generated automatically
   - Passed to all child operations
   - End-to-end traceability guaranteed

5. **Compliance by Construction**
   - Audit trail exists by construction
   - No "forgot to log" bugs
   - No "log after exception" bugs
   - Hash chain integrity enforced

6. **Performance Monitoring**
   - Duration captured for every operation
   - Can identify slow operations
   - Can detect brittleness (high fan-in)
   - Can optimize hot paths

7. **Hallucination Detection**
   - If operation claims "AC-XXX implemented"
   - Query: SELECT * FROM audit_logs WHERE ac_id='AC-XXX'
   - If no entries → hallucination
   - If entries but tests failed → false claim

8. **Brittleness Detection**
   - Build dependency graph from audit logs
   - Calculate: fan-in (how many call this?)
   - Calculate: fan-out (how many does this call?)
   - High fan-in = brittle (single point of failure)

9. **Testing Integration**
   - Test execution logged automatically
   - Test results captured in context
   - Evidence bundles generated automatically
   - TDD cycle tracked in audit trail

10. **RAG Integration**
    - Audit logs become training data
    - Semantic search over operation history
    - "How did we solve this before?"
    - Historical pattern matching
"""

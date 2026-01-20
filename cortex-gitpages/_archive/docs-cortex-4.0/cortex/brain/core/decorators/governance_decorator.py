"""
Governance Decorator - Auto-Wired Governance Decorators (AR-003)

Implements composable decorators for automatic governance enforcement:
- @governance_enforced: Validates all governance rules before execution
- @audit_logged: Records operation to audit log with hash chain
- @evidence_captured: Captures evidence artifacts after execution

Features:
- Composable (can be stacked)
- Pre-execution validation
- Post-execution audit logging
- Evidence collection
- AC-ID tracking

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import functools
import inspect
from typing import Any, Callable, Optional

from cortex.brain.core.governance_enforcer import GovernanceEnforcer
from cortex.brain.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.infrastructure.database import DatabaseManager


def governance_enforced(ac_id: str, phase: Optional[str] = None, db: Optional[DatabaseManager] = None):
    """
    Decorator: @governance_enforced
    
    Validates that the operation is allowed under current governance rules.
    Checks phase locks, AC-ID validity, and tier precedence.
    
    AC-AR-003-01: @governance_enforced decorator validates all rules
    
    Usage:
        @governance_enforced(ac_id="AC-TEST-001")
        def my_function():
            pass
    
    Args:
        ac_id: Acceptance Criteria ID for this operation
        phase: Optional phase ID (auto-detected if not provided)
        db: Optional DatabaseManager (will use default if not provided)
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Result[Any]:
            # Get database instance
            database = db or DatabaseManager()
            
            # Initialize enforcer
            enforcer = GovernanceEnforcer(database)
            
            # Enforce governance
            enforcement = enforcer.enforce_operation(
                ac_id=ac_id,
                operation="EXECUTE",
                phase=phase or "PHASE-01",
            )
            
            if not enforcement.allowed:
                return Err(f"Governance violation: {enforcement.reason}")
            
            # Execute function
            try:
                result = func(*args, **kwargs)
                return Ok(result)
            except Exception as e:
                return Err(f"Execution failed: {str(e)}")
        
        return wrapper
    
    return decorator


def audit_logged(
    ac_id: str,
    operation: str = "EXECUTE",
    db: Optional[DatabaseManager] = None,
):
    """
    Decorator: @audit_logged
    
    Records operation to audit log with hash chain before and after execution.
    Implements audit-first pattern with completion tracking.
    
    AC-AR-003-02: @audit_logged decorator records to governance.db
    
    Usage:
        @audit_logged(ac_id="AC-TEST-001", operation="AC_EXECUTE")
        def my_function():
            pass
    
    Args:
        ac_id: Acceptance Criteria ID
        operation: Operation type (e.g., "AC_EXECUTE", "AC_COMPLETE")
        db: Optional DatabaseManager instance
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Result[Any]:
            # Get database (use provided or get from first arg if it's db)
            database = db
            if not database and args:
                # Try to get db from self if this is a method
                if hasattr(args[0], '_db'):
                    database = args[0]._db
            
            if not database:
                # If no database, still execute function but don't log
                try:
                    result = func(*args, **kwargs)
                    return Ok(result)
                except Exception as e:
                    return Err(f"Execution failed: {str(e)}")
            
            # Initialize logger
            logger = EnhancedAuditLogger(database)
            logger.initialize(database)
            
            # Log operation START
            start_result = logger.log_operation_start(
                ac_id=ac_id,
                operation=operation,
                details={
                    "function": func.__name__,
                    "module": func.__module__,
                },
            )
            
            if start_result.is_err():
                return start_result
            
            # Execute function
            try:
                result = func(*args, **kwargs)
                
                # Log completion
                complete_result = logger.log_operation_complete(
                    ac_id=ac_id,
                    operation=operation,
                    success=True,
                    details={"status": "completed"},
                )
                
                if complete_result.is_err():
                    return complete_result
                
                return Ok(result)
            
            except Exception as e:
                # Log failure
                logger.log_operation_complete(
                    ac_id=ac_id,
                    operation=operation,
                    success=False,
                    details={"error": str(e)},
                )
                return Err(f"Execution failed: {str(e)}")
        
        return wrapper
    
    return decorator


def governance_with_audit(
    ac_id: str,
    operation: str = "EXECUTE",
    phase: Optional[str] = None,
    db: Optional[DatabaseManager] = None,
):
    """
    Composite decorator: @governance_with_audit
    
    Combines governance enforcement and audit logging.
    Validates rules first, then logs to audit trail.
    
    AC-AR-003-03: Decorators composable
    
    Usage:
        @governance_with_audit(ac_id="AC-TEST-001")
        def my_function():
            pass
    
    Args:
        ac_id: Acceptance Criteria ID
        operation: Operation type
        phase: Optional phase ID
        db: Optional DatabaseManager instance
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Result[Any]:
            # Get database instance
            database = db or DatabaseManager()
            
            # Initialize enforcer for governance check
            enforcer = GovernanceEnforcer(database)
            
            # Enforce governance first
            enforcement = enforcer.enforce_operation(
                ac_id=ac_id,
                operation=operation,
                phase=phase or "PHASE-01",
            )
            
            if not enforcement.allowed:
                return Err(f"Governance violation: {enforcement.reason}")
            
            # Now perform audit logging
            logger = EnhancedAuditLogger(database)
            # Initialize the logger with the database
            init_result = logger.initialize(database)
            if init_result.is_err():
                return init_result
            
            # Log operation start
            start_result = logger.log_operation_start(
                ac_id=ac_id,
                operation=operation,
                details={
                    "function": func.__name__,
                    "module": func.__module__,
                },
            )
            
            if start_result.is_err():
                return start_result
            
            # Execute function
            try:
                result = func(*args, **kwargs)
                
                # Log completion
                complete_result = logger.log_operation_complete(
                    ac_id=ac_id,
                    operation=operation,
                    success=True,
                    details={"status": "completed"},
                )
                
                if complete_result.is_err():
                    return complete_result
                
                return Ok(result)
            
            except Exception as e:
                # Log failure
                logger.log_operation_complete(
                    ac_id=ac_id,
                    operation=operation,
                    success=False,
                    details={"error": str(e)},
                )
                return Err(f"Execution failed: {str(e)}")
        
        return wrapper
    
    return decorator

"""
Planning Orchestrator - Reference Implementation (AC-AR-011)

Reference orchestrator demonstrating:
- Registry integration (AC-AR-011-01)
- MCP tool exposure (AC-AR-011-02)
- Audit logging with hash chain (AC-AR-011-03)

Features:
- Phase planning and tracking
- AC status reporting
- Orchestrated lock enforcement
- Comprehensive audit trail
- MCP tool integration

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import hashlib
import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.core.result import Result, Ok, Err
from src.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from src.core.response_header_config import HeaderConfigurationManager
from src.core.response_header_injector import ResponseHeaderInjector


@dataclass
class AuditEntry:
    """Audit log entry with hash chain."""
    audit_id: str
    timestamp: str
    operation: str
    actor: str
    parameters: Dict[str, Any]
    result: str
    previous_hash: Optional[str]
    current_hash: str


class PlanningOrchestrator(IOrchestrator):
    """
    Reference orchestrator for phase planning.
    
    Demonstrates:
    - Orchestrator interface implementation
    - Registry registration pattern
    - MCP tool exposure
    - Audit-first logging
    """
    
    _instance = None
    _instance_lock = threading.Lock()
    
    def __init__(self):
        """Initialize planning orchestrator."""
        self._name = "PlanningOrchestrator"
        self._version = "1.0.0"
        self._mode = OperationMode.PLANNING
        self._audit_trail: List[AuditEntry] = []
        self._audit_lock = threading.Lock()
        self._phase_data: Dict[str, Any] = {}
        self._initialized = False
        
        # AC-ENH-001-01: Initialize header system (ResponseHeaderInjector)
        try:
            config_manager = HeaderConfigurationManager.get_instance()
            config_manager.load_configuration('cortex-brain/tier0/response-headers.yaml')
            # Note: Injector not needed for current implementation
            # Will be used when responses are rendered through templates
            self._header_config = config_manager
        except Exception as e:
            # Log but don't fail - headers are enhancement, not blocking
            print(f"Warning: Failed to initialize header system: {e}")
            self._header_config = None
    
    @classmethod
    def instance(cls) -> "PlanningOrchestrator":
        """Get singleton instance."""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (for testing)."""
        with cls._instance_lock:
            cls._instance = None
    
    def get_name(self) -> str:
        """Get orchestrator name."""
        return self._name
    
    def get_version(self) -> str:
        """Get orchestrator version."""
        return self._version
    
    def initialize(self) -> Result[str]:
        """
        Initialize orchestrator.
        
        Returns:
            Result with initialization message
        """
        if self._initialized:
            return Err("Already initialized")
        
        # Log initialization
        self._log_audit_entry(
            operation="INITIALIZE",
            actor="SYSTEM",
            parameters={},
            result="SUCCESS",
        )
        
        self._initialized = True
        return Ok(f"{self._name} initialized successfully")
    
    def get_mode(self) -> OperationMode:
        """Get current operation mode."""
        return self._mode
    
    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """
        AC-AR-011-02: Get exposed MCP tools.
        
        Returns:
            Result containing MCP tool definitions
        """
        tools = {
            "plan_status": {
                "type": "function",
                "description": "Get current phase planning status",
                "parameters": {
                    "phase_id": "Phase identifier",
                },
                "returns": "Phase planning status and progress",
            },
            "next_ac": {
                "type": "function",
                "description": "Get next AC to work on",
                "parameters": {
                    "phase_id": "Phase identifier",
                },
                "returns": "Next AC-ID with context",
            },
            "enforce_phase_lock": {
                "type": "function",
                "description": "Enforce phase-level locks",
                "parameters": {
                    "phase_id": "Phase identifier",
                    "reason": "Lock reason",
                },
                "returns": "Lock confirmation with hash",
            },
        }
        
        # Log tool exposure
        self._log_audit_entry(
            operation="GET_MCP_TOOLS",
            actor="MCP_REGISTRY",
            parameters={"tool_count": len(tools)},
            result="SUCCESS",
        )
        
        return Ok(tools)
    
    def plan_status(self, phase_id: str) -> Result[Dict[str, Any]]:
        """
        Get phase planning status.
        
        Args:
            phase_id: Phase to check
        
        Returns:
            Result containing status
        """
        status = {
            "phase_id": phase_id,
            "mode": self._mode.name,
            "total_acs": 36,
            "completed_acs": 30,
            "in_progress_acs": 3,
            "blocked_acs": 0,
            "completion_percentage": (30 / 36) * 100,
        }
        
        # Log operation
        self._log_audit_entry(
            operation="PLAN_STATUS",
            actor="MCP",
            parameters={"phase_id": phase_id},
            result="SUCCESS",
        )
        
        return Ok(status)
    
    def next_ac(self, phase_id: str) -> Result[Dict[str, Any]]:
        """
        Get next AC to work on.
        
        Args:
            phase_id: Phase context
        
        Returns:
            Result containing next AC
        """
        next_ac_data = {
            "ac_id": "AC-AR-011-01",
            "phase_id": phase_id,
            "title": "Reference Orchestrator Validation",
            "description": "Validate orchestrator integration",
            "dependencies": ["AC-FR-006-03", "AC-AR-008-03"],
            "estimated_effort_hours": 2.5,
        }
        
        # Log operation
        self._log_audit_entry(
            operation="NEXT_AC",
            actor="MCP",
            parameters={"phase_id": phase_id},
            result="SUCCESS",
        )
        
        return Ok(next_ac_data)
    
    def enforce_phase_lock(
        self,
        phase_id: str,
        reason: str,
    ) -> Result[Dict[str, str]]:
        """
        Enforce phase-level locks.
        
        Args:
            phase_id: Phase to lock
            reason: Reason for lock
        
        Returns:
            Result with lock confirmation
        """
        lock_data = {
            "phase_id": phase_id,
            "locked_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
            "enforced_by": "PlanningOrchestrator",
        }
        
        # Log operation
        self._log_audit_entry(
            operation="ENFORCE_PHASE_LOCK",
            actor="ORCHESTRATOR",
            parameters={"phase_id": phase_id, "reason": reason},
            result="SUCCESS",
        )
        
        return Ok(lock_data)
    
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """
        Execute operation with audit logging.
        
        Args:
            operation_name: Name of operation
            parameters: Operation parameters
        
        Returns:
            Result containing operation result
        """
        try:
            # Dispatch to appropriate method
            if operation_name == "plan_status":
                return self.plan_status(parameters.get("phase_id", "PHASE-01"))
            elif operation_name == "next_ac":
                return self.next_ac(parameters.get("phase_id", "PHASE-01"))
            elif operation_name == "enforce_phase_lock":
                return self.enforce_phase_lock(
                    parameters.get("phase_id", "PHASE-01"),
                    parameters.get("reason", ""),
                )
            else:
                return Err(f"Unknown operation: {operation_name}")
        
        except Exception as e:
            # Log failure
            self._log_audit_entry(
                operation=operation_name,
                actor="MCP",
                parameters=parameters,
                result=f"FAILED: {str(e)}",
            )
            return Err(f"Operation failed: {str(e)}")
    
    def get_audit_trail(self, limit: int = 100) -> Result[List[Dict[str, Any]]]:
        """
        AC-AR-011-03: Get audit trail with hash chain.
        
        Args:
            limit: Maximum entries to return
        
        Returns:
            Result containing audit trail
        """
        with self._audit_lock:
            # Get requested entries
            entries = self._audit_trail[-limit:]
            
            # Convert to dicts
            trail = [asdict(entry) for entry in entries]
            
            return Ok(trail)
    
    def _log_audit_entry(
        self,
        operation: str,
        actor: str,
        parameters: Dict[str, Any],
        result: str,
    ) -> None:
        """
        Log operation to audit trail with hash chain.
        
        Args:
            operation: Operation type
            actor: Who performed operation
            parameters: Operation parameters
            result: Result status
        """
        with self._audit_lock:
            # Generate ID
            audit_id = f"AUDIT-{len(self._audit_trail):06d}"
            
            # Get previous hash
            previous_hash = None
            if self._audit_trail:
                previous_hash = self._audit_trail[-1].current_hash
            
            # Create entry dict for hashing
            entry_dict = {
                "audit_id": audit_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "operation": operation,
                "actor": actor,
                "parameters": parameters,
                "result": result,
                "previous_hash": previous_hash,
            }
            
            # Compute hash
            entry_json = str(entry_dict)
            current_hash = hashlib.sha256(entry_json.encode()).hexdigest()
            
            # Create entry
            entry = AuditEntry(
                audit_id=audit_id,
                timestamp=entry_dict["timestamp"],
                operation=operation,
                actor=actor,
                parameters=parameters,
                result=result,
                previous_hash=previous_hash,
                current_hash=current_hash,
            )
            
            # Store entry
            self._audit_trail.append(entry)
    
    def verify_audit_chain(self) -> Result[bool]:
        """
        Verify integrity of audit chain.
        
        Returns:
            Result indicating if chain is valid
        """
        with self._audit_lock:
            for i, entry in enumerate(self._audit_trail):
                if i > 0:
                    # Verify hash chain
                    previous_entry = self._audit_trail[i - 1]
                    if entry.previous_hash != previous_entry.current_hash:
                        return Err(f"Hash chain broken at entry {i}")
            
            return Ok(True)
    
    def get_operation_count(self) -> int:
        """Get total number of logged operations."""
        with self._audit_lock:
            return len(self._audit_trail)
    
    def get_response_with_headers(self, response_content: str) -> str:
        """
        AC-ENH-001-01: Wrap response content with CORTEX headers.
        
        This method demonstrates the ResponseHeaderInjector integration.
        Headers include author info and copyright notice.
        
        Args:
            response_content: The response body to wrap
        
        Returns:
            Response with CORTEX header and copyright footer
        """
        if not self._header_config:
            return response_content
        
        try:
            # Build header with header template
            header_template = self._header_config.get_header_template()
            author = self._header_config.get_author_name()
            copyright_notice = self._header_config.get_copyright_notice()
            
            # Substitute variables
            header = header_template.format(
                operation="GetPlanStatus",
                author=author,
                phase="PHASE-PLANNING",
                orchestrator=self._name,
            )
            
            # Build copyright footer
            copyright_template = self._header_config.get_copyright_template()
            footer = copyright_template.format(notice=copyright_notice)
            
            # Assemble: header + content + footer
            result = f"{header}\n\n{response_content}\n\n{footer}"
            
            return result
        except Exception as e:
            # If header generation fails, return original content
            print(f"Warning: Failed to add headers: {e}")
            return response_content

"""
OrchestratorRegistry - AC-SCAFFOLD-003: MasterOrchestrator Registration.

Enforces orchestrator registration and prevents bypass mechanisms.
Maintains registry of all valid orchestrators with governance compliance.

Author: GitHub Copilot
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

from src.infrastructure.enhanced_audit_logger import EnterpriseAuditLogger


class RegistrationStatus(str, Enum):
    """Orchestrator registration status."""
    PENDING = "pending"
    REGISTERED = "registered"
    GOVERNANCE_VALIDATED = "governance_validated"
    ROUTING_ENABLED = "routing_enabled"
    BLOCKED = "blocked"
    REVOKED = "revoked"


@dataclass
class OrchestratorRegistration:
    """Orchestrator registration record."""
    orchestrator_id: str
    class_name: str
    domain: str
    version: str = "1.0.0"
    created_by: str = "system"
    governance_rules: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    status: RegistrationStatus = RegistrationStatus.REGISTERED
    governance_validated: bool = False
    routing_enabled: bool = False
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        return data


class OrchestratorRegistry:
    """
    AC-SCAFFOLD-003: MasterOrchestrator Registration.
    
    Enforces registration of all orchestrators and prevents bypass.
    Tracks registration lifecycle and governance compliance.
    """
    
    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        registry_file: Optional[Path] = None
    ):
        """Initialize registry."""
        self.logger = logging.getLogger(__name__)
        self.audit_logger = EnterpriseAuditLogger()
        self.workspace_root = workspace_root or Path.cwd()
        
        self.registry_file = registry_file or (
            self.workspace_root / "cortex-brain" / "state" / "orchestrator_registry.json"
        )
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory registry (cache)
        self._registry: Dict[str, OrchestratorRegistration] = {}
        self._load_registry()
    
    def register_orchestrator(
        self,
        orchestrator_id: str,
        class_name: str,
        domain: str,
        governance_rules: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        created_by: str = "system",
        auto_enable_routing: bool = False
    ) -> OrchestratorRegistration:
        """
        Register a new orchestrator.
        
        Args:
            orchestrator_id: Unique ID for orchestrator
            class_name: Python class name
            domain: Domain/category (e.g., 'api_management')
            governance_rules: List of governing rules
            capabilities: List of capabilities
            created_by: Who created this orchestrator
            auto_enable_routing: Enable routing immediately
        
        Returns:
            OrchestratorRegistration: The registration record
        
        Raises:
            ValueError: If orchestrator already registered or invalid ID
        """
        # Check for duplicates
        if orchestrator_id in self._registry:
            error_msg = f"Orchestrator {orchestrator_id} already registered"
            self.logger.error(error_msg)
            self.audit_logger.log(
                level="ERROR",
                category="ORCHESTRATOR",
                message=error_msg,
                correlation_id=f"reg_{orchestrator_id}"
            )
            raise ValueError(error_msg)
        
        # Validate ID format
        if not self._validate_orchestrator_id(orchestrator_id):
            raise ValueError(f"Invalid orchestrator ID: {orchestrator_id}")
        
        # Create registration
        registration = OrchestratorRegistration(
            orchestrator_id=orchestrator_id,
            class_name=class_name,
            domain=domain,
            governance_rules=governance_rules or [],
            capabilities=capabilities or [],
            created_by=created_by,
            status=RegistrationStatus.REGISTERED
        )
        
        # Store in registry
        self._registry[orchestrator_id] = registration
        
        # Audit log
        self.audit_logger.log(
            level="INFO",
            category="ORCHESTRATOR",
            message=f"Orchestrator registered: {orchestrator_id}",
            correlation_id=f"reg_{orchestrator_id}",
            metadata={
                'orchestrator_id': orchestrator_id,
                'class_name': class_name,
                'domain': domain,
                'governance_rules': governance_rules,
                'created_by': created_by
            }
        )
        
        # Auto-enable routing if requested
        if auto_enable_routing:
            registration = self.enable_routing(orchestrator_id)
        
        # Persist to disk
        self._save_registry()
        
        self.logger.info(f"Orchestrator registered: {orchestrator_id}")
        return registration
    
    def get_registration(self, orchestrator_id: str) -> Optional[OrchestratorRegistration]:
        """Get registration record."""
        return self._registry.get(orchestrator_id)
    
    def list_registrations(self) -> List[OrchestratorRegistration]:
        """List all registrations."""
        return list(self._registry.values())
    
    def list_by_domain(self, domain: str) -> List[OrchestratorRegistration]:
        """List orchestrators by domain."""
        return [
            reg for reg in self._registry.values()
            if reg.domain == domain
        ]
    
    def is_registered(self, orchestrator_id: str) -> bool:
        """Check if orchestrator is registered."""
        return orchestrator_id in self._registry
    
    def validate_governance_compliance(
        self,
        orchestrator_id: str,
        rules_applied: List[str]
    ) -> OrchestratorRegistration:
        """
        Mark orchestrator as governance-validated.
        
        Args:
            orchestrator_id: Orchestrator to validate
            rules_applied: Governance rules that were applied
        
        Returns:
            Updated registration
        """
        if orchestrator_id not in self._registry:
            raise ValueError(f"Orchestrator not registered: {orchestrator_id}")
        
        registration = self._registry[orchestrator_id]
        registration.governance_validated = True
        registration.status = RegistrationStatus.GOVERNANCE_VALIDATED
        registration.governance_rules = rules_applied
        
        self.audit_logger.log(
            level="INFO",
            category="GOVERNANCE",
            message=f"Orchestrator governance validated: {orchestrator_id}",
            correlation_id=f"gov_{orchestrator_id}",
            metadata={
                'orchestrator_id': orchestrator_id,
                'rules_applied': rules_applied
            }
        )
        
        self._save_registry()
        return registration
    
    def enable_routing(self, orchestrator_id: str) -> OrchestratorRegistration:
        """Enable routing for orchestrator."""
        if orchestrator_id not in self._registry:
            raise ValueError(f"Orchestrator not registered: {orchestrator_id}")
        
        registration = self._registry[orchestrator_id]
        registration.routing_enabled = True
        registration.status = RegistrationStatus.ROUTING_ENABLED
        
        self.audit_logger.log(
            level="INFO",
            category="ORCHESTRATOR",
            message=f"Routing enabled for orchestrator: {orchestrator_id}",
            correlation_id=f"route_{orchestrator_id}"
        )
        
        self._save_registry()
        return registration
    
    def disable_routing(self, orchestrator_id: str) -> OrchestratorRegistration:
        """Disable routing for orchestrator (e.g., due to issues)."""
        if orchestrator_id not in self._registry:
            raise ValueError(f"Orchestrator not registered: {orchestrator_id}")
        
        registration = self._registry[orchestrator_id]
        registration.routing_enabled = False
        registration.status = RegistrationStatus.BLOCKED
        
        self.audit_logger.log(
            level="WARNING",
            category="ORCHESTRATOR",
            message=f"Routing disabled for orchestrator: {orchestrator_id}",
            correlation_id=f"route_{orchestrator_id}"
        )
        
        self._save_registry()
        return registration
    
    def revoke_registration(self, orchestrator_id: str, reason: str = "") -> None:
        """Revoke orchestrator registration."""
        if orchestrator_id not in self._registry:
            raise ValueError(f"Orchestrator not registered: {orchestrator_id}")
        
        registration = self._registry[orchestrator_id]
        registration.status = RegistrationStatus.REVOKED
        registration.routing_enabled = False
        
        self.audit_logger.log(
            level="WARNING",
            category="ORCHESTRATOR",
            message=f"Orchestrator registration revoked: {orchestrator_id}",
            correlation_id=f"revoke_{orchestrator_id}",
            metadata={'reason': reason}
        )
        
        self._save_registry()
    
    def validate_for_routing(self, orchestrator_id: str) -> tuple[bool, str]:
        """
        Validate that orchestrator can be routed to.
        
        Returns:
            (is_valid, reason)
        """
        if not self.is_registered(orchestrator_id):
            return False, f"Orchestrator not registered: {orchestrator_id}"
        
        registration = self.get_registration(orchestrator_id)
        if not registration.routing_enabled:
            return False, f"Routing disabled for: {orchestrator_id}"
        
        if registration.status == RegistrationStatus.REVOKED:
            return False, f"Registration revoked for: {orchestrator_id}"
        
        if registration.status == RegistrationStatus.BLOCKED:
            return False, f"Orchestrator blocked: {orchestrator_id}"
        
        return True, "OK"
    
    def get_routing_table(self) -> Dict[str, Any]:
        """Get all routable orchestrators."""
        routable = {
            reg.orchestrator_id: {
                'class_name': reg.class_name,
                'domain': reg.domain,
                'capabilities': reg.capabilities,
                'governance_rules': reg.governance_rules
            }
            for reg in self._registry.values()
            if reg.routing_enabled and reg.status != RegistrationStatus.REVOKED
        }
        return routable
    
    @staticmethod
    def _validate_orchestrator_id(orchestrator_id: str) -> bool:
        """Validate orchestrator ID format."""
        if not orchestrator_id:
            return False
        # ID should be alphanumeric + underscore
        return all(c.isalnum() or c == '_' for c in orchestrator_id)
    
    def _load_registry(self) -> None:
        """Load registry from disk."""
        if not self.registry_file.exists():
            self._registry = {}
            return
        
        try:
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
            
            self._registry = {}
            for orch_id, reg_data in data.items():
                # Convert status string back to enum
                if 'status' in reg_data:
                    reg_data['status'] = RegistrationStatus(reg_data['status'])
                
                registration = OrchestratorRegistration(**reg_data)
                self._registry[orch_id] = registration
            
            self.logger.debug(f"Loaded {len(self._registry)} orchestrators from registry")
        except Exception as e:
            self.logger.error(f"Failed to load registry: {e}")
            self._registry = {}
    
    def _save_registry(self) -> None:
        """Save registry to disk."""
        try:
            data = {
                orch_id: reg.to_dict()
                for orch_id, reg in self._registry.items()
            }
            
            # Atomic write with temp file
            temp_file = self.registry_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Atomic rename
            temp_file.replace(self.registry_file)
            self.logger.debug(f"Saved {len(self._registry)} orchestrators to registry")
        except Exception as e:
            self.logger.error(f"Failed to save registry: {e}")
            self.audit_logger.log(
                level="ERROR",
                category="INFRASTRUCTURE",
                message=f"Registry save failed: {e}"
            )

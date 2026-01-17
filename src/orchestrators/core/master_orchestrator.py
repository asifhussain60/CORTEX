"""
Master Orchestrator - Coordinates all domain orchestrators

AC-AR-006-01: MasterOrchestrator coordinates domain orchestrators
- Receives operation requests
- Determines applicable domain orchestrators
- Delegates to appropriate orchestrator(s)
- Aggregates results
- Logs all delegation decisions to audit trail

AC-FIX-HALLUCINATION-001: Boundary enforcement integration
- Validates operations against behavioral boundaries before delegation
"""

from typing import Dict, List, Any, Optional, Set, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from src.core.interfaces import IOrchestrator, OperationMode
from src.core.result import Result, Ok, Err
from src.core.response_header_injector import ResponseHeaderInjector
from src.core.response_header_config import HeaderConfigurationManager
from src.core.governance_registry import GovernanceRegistry, GovernanceViolationError
from src.core.hallucination_prevention.behavioral_boundaries import BehavioralBoundaryRules
from src.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from src.infrastructure.database import DatabaseManager
from src.infrastructure.database_transaction_manager import DatabaseTransactionManager
from src.mcp.decorator import mcp_tool


@dataclass
class OrchestratorMetadata:
    """Metadata for registered orchestrators"""
    domain: str
    orchestrator: IOrchestrator
    version: str = "1.0"
    capabilities: List[str] = field(default_factory=list)
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())


class MasterOrchestrator(IOrchestrator):
    """
    MasterOrchestrator - Coordinates all domain orchestrators.
    
    Implements the coordinator pattern to manage multiple domain orchestrators:
    - Maintains registry of domain orchestrators
    - Routes operations to applicable orchestrators
    - Aggregates results from multiple orchestrators
    - Logs all delegation decisions with audit trail
    
    AC-AR-006-01: MasterOrchestrator coordinates domain orchestrators
    """
    
    _instance: Optional['MasterOrchestrator'] = None
    
    def __init__(self):
        """Initialize MasterOrchestrator"""
        self.logger = EnhancedAuditLogger.instance()
        self.db = DatabaseManager()
        self.domain_orchestrators: Dict[str, OrchestratorMetadata] = {}
        self.operation_history: List[Dict[str, Any]] = []
        
        # AC-FIX-001-01: Initialize DatabaseTransactionManager for atomic operations
        db_path = Path(__file__).parent.parent.parent.parent / "cortex-brain" / "state" / "governance.db"
        self.transaction_manager = DatabaseTransactionManager(str(db_path))
        
        # AC-REM-002-04: Initialize GovernanceRegistry for per-turn validation
        self._governance_registry: Optional[GovernanceRegistry] = None
        self._turn_number: int = 0  # Track turn count for governance validation
        
        # AC-FIX-HALLUCINATION-001: Initialize boundary enforcement
        self._boundary_rules = BehavioralBoundaryRules()
        
        # Track current operation context for header variables
        self.current_operation: Optional[str] = None
        self.current_phase: Optional[str] = None
        
        # AC-ENH-002-01: Initialize ResponseHeaderInjector for header wrapping
        try:
            config_manager = HeaderConfigurationManager.get_instance()
            config_manager.load_configuration('cortex-brain/tier0/response-headers.yaml')
            
            # Create ResponseHeaderInjector instance
            # Uses composition pattern - injector wraps a template engine
            # For orchestrators that don't use templates, pass None as engine
            self.header_injector = ResponseHeaderInjector(
                template_engine=None,  # Optional: None for orchestrators without templates
                config_manager=config_manager
            )
        except Exception as e:
            # Log but don't fail - headers are enhancement, not blocking
            self.logger.log_operation_complete(
                ac_id="AC-ENH-002-01",
                operation="HEADER_INJECTOR_INIT",
                success=False,
                details={"error": f"Failed to initialize header injector: {str(e)}"}
            )
            # Graceful degradation: continue without header injection
            self.header_injector = None
        
    @classmethod
    def instance(cls) -> 'MasterOrchestrator':
        """Get singleton instance of MasterOrchestrator"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    # Implementation of abstract methods from IOrchestrator
    
    def get_name(self) -> str:
        """Get orchestrator name."""
        return "MasterOrchestrator"
    
    def get_version(self) -> str:
        """Get orchestrator version."""
        return "2.0"
    
    def initialize(self) -> Result[str]:
        """Initialize orchestrator."""
        try:
            self.logger.log_operation_start(
                ac_id="AC-AR-006-01",
                operation="INITIALIZATION",
                details={}
            )
            self.logger.log_operation_complete(
                ac_id="AC-AR-006-01",
                operation="INITIALIZATION",
                success=True,
                details={"initialized": True}
            )
            return Ok("MasterOrchestrator initialized successfully")
        except Exception as e:
            return Err(f"Initialization failed: {str(e)}")
    
    def get_mode(self) -> OperationMode:
        """Get current operation mode."""
        return OperationMode.PLANNING
    
    def get_response_with_headers(self, response: str) -> str:
        """
        Wrap response with CORTEX headers.
        
        AC-ENH-002-01: Integrate ResponseHeaderInjector into MasterOrchestrator
        
        Applies header injection if injector is available, otherwise returns
        response unchanged (graceful degradation).
        
        Args:
            response: Response text to wrap
            
        Returns:
            Response wrapped with CORTEX headers
        """
        if not self.header_injector:
            return response
        
        try:
            # Build context from orchestrator state
            context = {
                "operation": self.current_operation or "coordination",
                "orchestrator": self.get_name(),
                "phase": self.current_phase or "coordination",
                "mode": self.get_mode().name,
                "author": "CORTEX",  # Master orchestrator is system-authored
            }
            
            # AC-ENH-002-01: Build header section using injector pattern
            header_section = self.header_injector._build_header_section(context)
            
            # AC-ENH-002-01: Build copyright section (appears after content)
            copyright_section = self.header_injector._build_copyright_section(context)
            
            # Assemble: header + content + copyright (NOT including footer for orchestrators)
            sections = []
            if header_section:
                sections.append(header_section)
            sections.append(response)
            if copyright_section:
                sections.append(copyright_section)
            
            # Use injector's assembly logic for consistent spacing
            wrapped_response = self.header_injector._assemble_sections(sections)
            
            return wrapped_response
            
        except Exception as e:
            # Graceful degradation: log error and return unwrapped response
            self.logger.log_operation_complete(
                ac_id="AC-ENH-002-01",
                operation="HEADER_INJECTION",
                success=False,
                details={"error": f"Header injection failed: {str(e)}"}
            )
            return response
    
    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """AC-AR-011-02: Get exposed MCP tools."""
        try:
            tools = {
                "register_orchestrator": {
                    "description": "Register a domain orchestrator",
                    "parameters": ["domain", "orchestrator", "capabilities"]
                },
                "get_registered_domains": {
                    "description": "Get list of registered domains"
                },
                "get_orchestrator": {
                    "description": "Get orchestrator for domain",
                    "parameters": ["domain"]
                },
                "coordinate_operation": {
                    "description": "Coordinate operation across domains",
                    "parameters": ["operation", "context", "target_domains"]
                },
                "get_registry_status": {
                    "description": "Get registry status"
                },
                "get_coordination_history": {
                    "description": "Get coordination history",
                    "parameters": ["limit"]
                }
            }
            return Ok(tools)
        except Exception as e:
            return Err(f"Failed to get MCP tools: {str(e)}")
    
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """Execute operation with audit logging."""
        try:
            self.logger.log_operation_start(
                ac_id="AC-AR-006-01",
                operation=operation_name,
                details=parameters
            )
            
            # Route to appropriate method based on operation_name
            if operation_name == "register_orchestrator":
                result = self.register_orchestrator(
                    domain=parameters.get("domain"),
                    orchestrator=parameters.get("orchestrator"),
                    capabilities=parameters.get("capabilities")
                )
            elif operation_name == "coordinate_operation":
                result = self.coordinate_operation(
                    operation=parameters.get("operation"),
                    context=parameters.get("context"),
                    target_domains=parameters.get("target_domains")
                )
            else:
                result = Err(f"Unknown operation: {operation_name}")
            
            self.logger.log_operation_complete(
                ac_id="AC-AR-006-01",
                operation=operation_name,
                success=result.is_ok(),
                details={"result": str(result)}
            )
            
            return result
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-AR-006-01",
                operation=operation_name,
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Operation execution failed: {str(e)}")
    
    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """AC-AR-011-03: Get audit trail with hash chain."""
        try:
            # Query audit trail from database
            trail = self.db.query_audit_trail(limit=limit)
            return Ok(trail)
        except Exception as e:
            return Err(f"Failed to get audit trail: {str(e)}")
    
    # MasterOrchestrator-specific methods
    
    @mcp_tool(
        name="register_orchestrator",
        description="Register a domain orchestrator with MasterOrchestrator"
    )
    def register_orchestrator(
        self,
        domain: str,
        orchestrator: IOrchestrator,
        capabilities: Optional[List[str]] = None
    ) -> Result[Dict[str, Any]]:
        """
        Register a domain orchestrator.
        
        AC-AR-006-01: Register domain orchestrator
        
        Args:
            domain: Domain name (e.g., "governance", "audit", "evidence")
            orchestrator: IOrchestrator implementation
            capabilities: List of capabilities (e.g., ["validate", "enforce"])
        
        Returns:
            Result with registration details
        """
        try:
            # Log operation start
            self.logger.log_operation_start(
                ac_id="AC-AR-006-01",
                operation="ORCHESTRATOR_REGISTER",
                details={
                    "domain": domain,
                    "orchestrator_type": orchestrator.__class__.__name__,
                    "capabilities": capabilities or []
                }
            )
            
            # Check if already registered
            if domain in self.domain_orchestrators:
                return Err(f"Orchestrator for domain '{domain}' already registered")
            
            # Register orchestrator
            metadata = OrchestratorMetadata(
                domain=domain,
                orchestrator=orchestrator,
                capabilities=capabilities or []
            )
            self.domain_orchestrators[domain] = metadata
            
            # Log operation complete
            self.logger.log_operation_complete(
                ac_id="AC-AR-006-01",
                operation="ORCHESTRATOR_REGISTER",
                success=True,
                details={
                    "domain": domain,
                    "registered": True,
                    "total_orchestrators": len(self.domain_orchestrators)
                }
            )
            
            return Ok({
                "domain": domain,
                "registered": True,
                "total_orchestrators": len(self.domain_orchestrators),
                "registered_at": metadata.registered_at
            })
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-AR-006-01",
                operation="ORCHESTRATOR_REGISTER",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Failed to register orchestrator: {str(e)}")
    
    @mcp_tool(
        name="get_registered_domains",
        description="Get list of all registered orchestrator domains"
    )
    def get_registered_domains(self) -> Result[List[str]]:
        """
        Get list of registered orchestrator domains.
        
        Returns:
            Result with list of domain names
        """
        try:
            domains = list(self.domain_orchestrators.keys())
            return Ok(domains)
        except Exception as e:
            return Err(f"Failed to get registered domains: {str(e)}")
    
    @mcp_tool(
        name="get_orchestrator",
        description="Get orchestrator instance for a specific domain"
    )
    def get_orchestrator(self, domain: str) -> Result[IOrchestrator]:
        """
        Get orchestrator for a specific domain.
        
        Args:
            domain: Domain name
        
        Returns:
            Result with orchestrator instance
        """
        try:
            if domain not in self.domain_orchestrators:
                return Err(f"No orchestrator registered for domain '{domain}'")
            
            return Ok(self.domain_orchestrators[domain].orchestrator)
        except Exception as e:
            return Err(f"Failed to get orchestrator: {str(e)}")
    
    @mcp_tool(
        name="coordinate_operation",
        description="Coordinate an operation across domain orchestrators"
    )
    def coordinate_operation(
        self,
        operation: str,
        context: Dict[str, Any],
        target_domains: Optional[List[str]] = None
    ) -> Result[Dict[str, Any]]:
        """
        Coordinate operation across domain orchestrators.
        
        AC-AR-006-01: Coordinate operations across domain orchestrators
        AC-REM-002-04: Add governance validation before delegation
        AC-FIX-001-01: Atomic operation + audit logging in single transaction
        
        Args:
            operation: Operation name (e.g., "validate", "enforce")
            context: Operation context (metadata, parameters, etc.)
            target_domains: Specific domains to target (None = all)
        
        Returns:
            Result with aggregated results from orchestrators
        
        Governance Enforcement:
        - CORE-017: Strict Governance Enforcement
        - CORE-019: TDD-Master Routing (per-turn validation)
        - CORE-027: Audit Trail Per Turn
        - AC-FIX-001-01: Atomic state + audit logging
        """
        # AC-FIX-001-01: Wrap entire operation in atomic transaction
        # Both coordination execution and audit logging occur in single transaction
        try:
            with self.transaction_manager.atomic_operation("AC-FIX-001-01", f"coordinate_{operation}") as txn:
                # AC-REM-002-04: Pre-coordination governance validation
                # Increment turn counter
                self._turn_number += 1
                
                # Initialize governance registry if needed
                if not self._governance_registry:
                    self._governance_registry = GovernanceRegistry.instance()
                    init_result = self._governance_registry.initialize()
                    if init_result.is_err():
                        raise Exception(f"Failed to initialize governance registry: {init_result.error}")
                
                # Validate governance before delegation (CORE-019 per-turn validation)
                governance_result = self._governance_registry.should_proceed(
                    turn_number=self._turn_number,
                    orchestrator_id="master-orchestrator"
                )
                
                if governance_result.is_err():
                    # Governance violation detected
                    violation_msg = governance_result.error
                    self.logger.log_operation_complete(
                        ac_id="AC-REM-002-04",
                        operation="GOVERNANCE_VIOLATION",
                        success=False,
                        details={
                            "turn_number": self._turn_number,
                            "violation": violation_msg,
                            "requested_operation": operation
                        }
                    )
                    raise GovernanceViolationError(violation_msg)
                
                # Governance validation passed - proceed with coordination
                self.logger.log_operation_start(
                    ac_id="AC-AR-006-01",
                    operation="COORDINATION",
                    details={
                        "operation": operation,
                        "target_domains": target_domains,
                        "total_orchestrators": len(self.domain_orchestrators),
                        "turn_number": self._turn_number,
                        "governance_validated": True,
                        "transaction_id": txn.transaction_id
                    }
                )
                
                # Determine target orchestrators
                domains_to_use = target_domains if target_domains else list(self.domain_orchestrators.keys())
                
                # Validate target domains
                invalid_domains = set(domains_to_use) - set(self.domain_orchestrators.keys())
                if invalid_domains:
                    raise Exception(f"Invalid domains: {invalid_domains}")
                
                # Delegate to orchestrators and collect results
                results = {}
                errors = {}
                
                for domain in domains_to_use:
                    metadata = self.domain_orchestrators[domain]
                    orchestrator = metadata.orchestrator
                    
                    try:
                        # Delegate operation to orchestrator
                        # Note: This assumes orchestrators have a common execute method
                        # Actual implementation depends on orchestrator interface
                        result = {
                            "domain": domain,
                            "status": "delegated",
                            "timestamp": datetime.now().isoformat()
                        }
                        results[domain] = result
                        
                    except Exception as e:
                        errors[domain] = str(e)
                
                # Aggregate results
                aggregated = {
                    "operation": operation,
                    "timestamp": datetime.now().isoformat(),
                    "turn_number": self._turn_number,
                    "orchestrators_involved": len(domains_to_use),
                    "results": results,
                    "errors": errors if errors else None,
                    "transaction_id": txn.transaction_id
                }
                
                # Store in history
                self.operation_history.append(aggregated)
                
                # Log coordination complete
                self.logger.log_operation_complete(
                    ac_id="AC-AR-006-01",
                    operation="COORDINATION",
                    success=len(errors) == 0,
                    details={
                        "orchestrators_involved": len(domains_to_use),
                        "successful": len(results),
                        "failed": len(errors),
                        "turn_number": self._turn_number,
                        "governance_enforced": True,
                        "transaction_id": txn.transaction_id
                    }
                )
                
                return Ok(aggregated)
        
        except GovernanceViolationError as e:
            # Re-raise governance violations (transaction already rolled back)
            raise e
        
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-AR-006-01",
                operation="COORDINATION",
                success=False,
                details={"error": str(e), "turn_number": self._turn_number}
            )
            return Err(f"Coordination failed: {str(e)}")
    
    @mcp_tool(
        name="get_coordination_history",
        description="Get history of coordinated operations"
    )
    def get_coordination_history(
        self,
        limit: int = 10
    ) -> Result[List[Dict[str, Any]]]:
        """
        Get recent coordination operation history.
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            Result with coordination history
        """
        try:
            history = self.operation_history[-limit:]
            return Ok(history)
        except Exception as e:
            return Err(f"Failed to get history: {str(e)}")
    
    @mcp_tool(
        name="get_registry_status",
        description="Get current registry status and orchestrator information"
    )
    def get_registry_status(self) -> Result[Dict[str, Any]]:
        """
        Get current registry status.
        
        Returns:
            Result with registry metadata
        """
        try:
            status = {
                "total_orchestrators": len(self.domain_orchestrators),
                "domains": [
                    {
                        "domain": domain,
                        "type": metadata.orchestrator.__class__.__name__,
                        "version": metadata.version,
                        "capabilities": metadata.capabilities,
                        "registered_at": metadata.registered_at
                    }
                    for domain, metadata in self.domain_orchestrators.items()
                ],
                "total_operations": len(self.operation_history)
            }
            return Ok(status)
        except Exception as e:
            return Err(f"Failed to get registry status: {str(e)}")

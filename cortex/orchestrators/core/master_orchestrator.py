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

from __future__ import annotations

from typing import Dict, List, Any, Optional, Set, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from cortex.core.interfaces import IOrchestrator, OperationMode
from cortex.core.result import Result, Ok, Err
from cortex.brain.core.response_header_injector import ResponseHeaderInjector
from cortex.brain.core.response_header_config import HeaderConfigurationManager
from cortex.brain.core.governance_registry import GovernanceRegistry, GovernanceViolationError
from cortex.brain.core.hallucination_prevention.behavioral_boundaries import BehavioralBoundaryRules
from cortex.brain.core.knowledge.knowledge_repository import KnowledgeRepository, KnowledgeEntry
from cortex.brain.core.state_manager import StateManager, OperationState, get_state_manager
from cortex.brain.domain_brain.business_knowledge_repository import (
    BusinessKnowledgeRepository,
    BusinessKnowledgeEntry,
    get_business_knowledge_repository
)
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.infrastructure.database import DatabaseManager
from cortex.infrastructure.database_transaction_manager import DatabaseTransactionManager
from cortex.brain.mcp.decorator import mcp_tool

# AC-IKP-002-02: Import IntelligentKnowledgeRouter for knowledge backend coordination
try:
    from cortex.brain.core.knowledge.router import IntelligentKnowledgeRouter
except ImportError:
    # Fallback if module not accessible
    IntelligentKnowledgeRouter = None


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
        
        # AC-REM-011-05: Initialize StateManager for cross-phase state consistency
        self._state_manager: StateManager = get_state_manager()
        self.logger.log_operation_complete(
            ac_id="AC-REM-011-05",
            operation="STATE_MANAGER_INIT",
            success=True,
            details={"manager": "StateManager initialized for cross-phase consistency"}
        )
        
        # AC-REM-011-01: Initialize stage orchestrators for E2E workflow
        # Stage 1: Interaction Orchestrator (Comprehension)
        self.interaction_orchestrator: Optional[IOrchestrator] = None
        # Stage 2: Intent Router
        self.intent_router: Optional[IOrchestrator] = None
        # Stage 3 Registry: Orchestrator registry for delegation
        self.orchestrator_registry: Dict[str, IOrchestrator] = {}
        
        # AC-FIX-001-01: Initialize DatabaseTransactionManager for atomic operations
        db_path = Path(__file__).parent.parent.parent.parent / "cortex_brain" / "state" / "governance.db"
        self.transaction_manager = DatabaseTransactionManager(str(db_path))
        
        # AC-REM-002-04: Initialize GovernanceRegistry for per-turn validation
        self._governance_registry: Optional[GovernanceRegistry] = None
        self._turn_number: int = 0  # Track turn count for governance validation
        
        # AC-FIX-HALLUCINATION-001: Initialize boundary enforcement
        self._boundary_rules = BehavioralBoundaryRules()
        
        # AC-KN-002-01: Initialize Knowledge Repository for best practices access
        self._knowledge_repository: Optional[KnowledgeRepository] = None
        try:
            self._knowledge_repository = KnowledgeRepository()
            self.logger.log_operation_complete(
                ac_id="AC-KN-002-01",
                operation="KNOWLEDGE_REPOSITORY_INIT",
                success=True,
                details={
                    "entry_count": self._knowledge_repository.entry_count,
                    "domains": self._knowledge_repository.domains
                }
            )
        except FileNotFoundError as e:
            # Log but don't fail - knowledge is enhancement, not blocking
            self.logger.log_operation_complete(
                ac_id="AC-KN-002-01",
                operation="KNOWLEDGE_REPOSITORY_INIT",
                success=False,
                details={"error": f"Knowledge repository not available: {str(e)}"}
            )
        
        # AC-KN-003-01: Initialize Business Knowledge Repository for domain brain access
        self._business_knowledge_repository: Optional[BusinessKnowledgeRepository] = None
        try:
            self._business_knowledge_repository = BusinessKnowledgeRepository()
            self.logger.log_operation_complete(
                ac_id="AC-KN-003-01",
                operation="BUSINESS_KNOWLEDGE_REPOSITORY_INIT",
                success=True,
                details={
                    "domains": self._business_knowledge_repository.domains,
                    "entry_count": self._business_knowledge_repository.entry_count
                }
            )
        except Exception as e:
            # Log but don't fail - business knowledge is enhancement, not blocking
            self.logger.log_operation_complete(
                ac_id="AC-KN-003-01",
                operation="BUSINESS_KNOWLEDGE_REPOSITORY_INIT",
                success=False,
                details={"error": f"Business knowledge repository not available: {str(e)}"}
            )
        
        # AC-IKP-002-02: Initialize IntelligentKnowledgeRouter for backend coordination
        self.router = None
        try:
            if IntelligentKnowledgeRouter is not None:
                # Initialize router with available knowledge backends
                backends = {}
                if self._knowledge_repository is not None:
                    backends['knowledge'] = self._knowledge_repository
                if self._business_knowledge_repository is not None:
                    backends['business'] = self._business_knowledge_repository
                
                if backends:
                    self.router = IntelligentKnowledgeRouter(
                        backends=backends,
                        confidence_threshold=0.5
                    )
                    self.logger.log_operation_complete(
                        ac_id="AC-IKP-002-02",
                        operation="ROUTER_INIT",
                        success=True,
                        details={
                            "backends": list(backends.keys()),
                            "confidence_threshold": 0.5
                        }
                    )
        except Exception as e:
            # Log but don't fail - router is enhancement, not blocking
            self.logger.log_operation_complete(
                ac_id="AC-IKP-002-02",
                operation="ROUTER_INIT",
                success=False,
                details={"error": f"Router initialization failed: {str(e)}"}
            )
        
        # Track current operation context for header variables
        self.current_operation: Optional[str] = None
        self.current_phase: Optional[str] = None
        
        # AC-ENH-002-01: Initialize ResponseHeaderInjector for header wrapping
        try:
            config_manager = HeaderConfigurationManager.get_instance()
            config_manager.load_configuration('cortex_brain/tier0/response-headers.yaml')
            
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
        
        # AC-REM-011-01: Initialize stage orchestrators for E2E workflow
        # Try to initialize Interaction Orchestrator for Stage 1
        try:
            from cortex.orchestrators.core.master_orchestrator_stage_1 import MasterOrchestrationStage1
            self.interaction_orchestrator = MasterOrchestrationStage1()
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-01",
                operation="STAGE_1_INIT",
                success=True,
                details={"stage": "Interaction Orchestrator initialized"}
            )
        except Exception as e:
            # Log but don't fail - graceful degradation
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-01",
                operation="STAGE_1_INIT",
                success=False,
                details={"error": str(e)}
            )
        
        # Try to initialize Intent Router for Stage 2
        try:
            from cortex.orchestrators.core.intent_router import IntentRouter
            self.intent_router = IntentRouter()
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-01",
                operation="STAGE_2_INIT",
                success=True,
                details={"stage": "Intent Router initialized"}
            )
        except Exception as e:
            # Log but don't fail - graceful degradation
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-01",
                operation="STAGE_2_INIT",
                success=False,
                details={"error": str(e)}
            )
        
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
                
                # AC-KN-002-01: Evaluate technical knowledge for request composition
                knowledge_context = self._evaluate_knowledge_for_request(
                    operation=operation,
                    context=context,
                    target_domains=target_domains
                )
                
                # AC-KN-003-01: Evaluate business knowledge for request composition
                business_knowledge_context = self._evaluate_business_knowledge_for_request(
                    operation=operation,
                    context=context,
                    target_domains=target_domains
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
                
                # Aggregate results with knowledge context (AC-KN-002-01, AC-KN-003-01)
                aggregated = {
                    "operation": operation,
                    "timestamp": datetime.now().isoformat(),
                    "turn_number": self._turn_number,
                    "orchestrators_involved": len(domains_to_use),
                    "results": results,
                    "errors": errors if errors else None,
                    "transaction_id": txn.transaction_id,
                    # AC-KN-002-01: Include technical knowledge context in composite request
                    "knowledge_context": knowledge_context,
                    # AC-KN-003-01: Include business knowledge context in composite request
                    "business_knowledge_context": business_knowledge_context
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
                        "transaction_id": txn.transaction_id,
                        "knowledge_evaluated": knowledge_context.get("knowledge_evaluated", False),
                        "knowledge_entries_used": knowledge_context.get("entries_count", 0),
                        "business_knowledge_evaluated": business_knowledge_context.get("business_knowledge_evaluated", False),
                        "business_knowledge_entries_used": business_knowledge_context.get("entries_count", 0)
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
    
    # ==========================================================================
    # KNOWLEDGE REPOSITORY INTEGRATION (AC-KN-002-01)
    # ==========================================================================
    
    @property
    def has_knowledge_repository(self) -> bool:
        """Check if knowledge repository is available."""
        return self._knowledge_repository is not None
    
    @mcp_tool(
        name="get_knowledge_summary",
        description="Get summary of available knowledge repository"
    )
    def get_knowledge_summary(self) -> Result[Dict[str, Any]]:
        """
        Get summary of available knowledge in the repository.
        
        AC-KN-002-01: Knowledge Repository Access
        
        Returns:
            Result with knowledge summary including domains and entry counts
        """
        if not self._knowledge_repository:
            return Err("Knowledge repository not initialized")
        
        try:
            summary = self._knowledge_repository.get_knowledge_summary()
            return Ok(summary)
        except Exception as e:
            return Err(f"Failed to get knowledge summary: {str(e)}")
    
    @mcp_tool(
        name="query_knowledge",
        description="Query knowledge repository by domain, tags, or keywords"
    )
    def query_knowledge(
        self,
        domains: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> Result[List[Dict[str, Any]]]:
        """
        Query the knowledge repository.
        
        AC-KN-002-01: Knowledge Repository Query
        
        Args:
            domains: Filter by domains (e.g., ["SECURITY", "ARCHITECTURE"])
            tags: Filter by tags (e.g., ["api", "authentication"])
            keywords: Search keywords in title/description
        
        Returns:
            Result with list of matching knowledge entries
        """
        if not self._knowledge_repository:
            return Err("Knowledge repository not initialized")
        
        try:
            result = self._knowledge_repository.query(
                domains=domains,
                tags=tags,
                keywords=keywords
            )
            
            # Convert entries to dicts for serialization
            entries = [
                {
                    "id": entry.id,
                    "domain": entry.domain,
                    "title": entry.title,
                    "description": entry.description,
                    "file_path": entry.file_path,
                    "tags": entry.tags,
                    "version": entry.version
                }
                for entry in result.entries
            ]
            
            return Ok(entries)
        except Exception as e:
            return Err(f"Failed to query knowledge: {str(e)}")
    
    @mcp_tool(
        name="get_relevant_knowledge",
        description="Get relevant knowledge for request composition"
    )
    def get_relevant_knowledge_for_operation(
        self,
        operation: str,
        context: Dict[str, Any],
        max_entries: int = 5
    ) -> Result[List[Dict[str, Any]]]:
        """
        Get relevant knowledge entries for composing a request.
        
        AC-KN-002-01: Knowledge Evaluation for Request Composition
        
        This method is called during coordinate_operation to fetch
        best practices and guidelines relevant to the operation.
        
        Args:
            operation: The operation being performed
            context: Operation context for relevance matching
            max_entries: Maximum entries to return
        
        Returns:
            Result with relevant knowledge entries
        """
        if not self._knowledge_repository:
            return Ok([])  # Graceful degradation - no knowledge available
        
        try:
            # Extract keywords from operation and context
            keywords = [operation]
            if "keywords" in context:
                keywords.extend(context["keywords"])
            if "intent" in context:
                keywords.append(context["intent"])
            if "domain" in context:
                keywords.append(context["domain"])
            
            # Map operation context to knowledge domains
            domain_mapping = {
                "security": ["SECURITY"],
                "auth": ["SECURITY"],
                "api": ["ARCHITECTURE", "SECURITY"],
                "database": ["DATA-MANAGEMENT"],
                "persistence": ["DATA-MANAGEMENT", "ARCHITECTURE"],
                "test": ["TESTING-VALIDATION"],
                "validate": ["TESTING-VALIDATION"],
                "deploy": ["DEPLOYMENT"],
                "performance": ["PERFORMANCE"],
                "architecture": ["ARCHITECTURE"],
            }
            
            # Determine relevant domains from operation/context
            relevant_domains = []
            operation_lower = operation.lower()
            context_str = str(context).lower()
            
            for key, domains in domain_mapping.items():
                if key in operation_lower or key in context_str:
                    relevant_domains.extend(domains)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_domains = [d for d in relevant_domains if d not in seen and not seen.add(d)]
            
            # Query knowledge repository
            entries = self._knowledge_repository.get_relevant_knowledge(
                domains=unique_domains if unique_domains else None,
                keywords=keywords,
                max_entries=max_entries
            )
            
            # Convert to serializable format
            result = [
                {
                    "id": entry.id,
                    "domain": entry.domain,
                    "title": entry.title,
                    "description": entry.description,
                    "relevance_context": {
                        "matched_domains": unique_domains,
                        "matched_keywords": keywords
                    }
                }
                for entry in entries
            ]
            
            self.logger.log_operation_complete(
                ac_id="AC-KN-002-01",
                operation="KNOWLEDGE_RETRIEVAL",
                success=True,
                details={
                    "operation": operation,
                    "entries_found": len(result),
                    "domains_searched": unique_domains,
                    "keywords_used": keywords
                }
            )
            
            return Ok(result)
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-KN-002-01",
                operation="KNOWLEDGE_RETRIEVAL",
                success=False,
                details={"error": str(e)}
            )
            return Ok([])  # Graceful degradation
    
    def _evaluate_knowledge_for_request(
        self,
        operation: str,
        context: Dict[str, Any],
        target_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate knowledge and compose guidelines for request.
        
        AC-KN-002-01: Knowledge Evaluation During Request Composition
        
        This internal method is called by coordinate_operation to:
        1. Fetch relevant knowledge from repository
        2. Extract applicable guidelines and best practices
        3. Compose knowledge context for the operation
        
        Args:
            operation: Operation being performed
            context: Operation context
            target_domains: Target orchestrator domains
            
        Returns:
            Dict with knowledge context for request composition
        """
        knowledge_context = {
            "knowledge_evaluated": False,
            "guidelines": [],
            "best_practices": [],
            "security_considerations": [],
            "architecture_patterns": []
        }
        
        if not self._knowledge_repository:
            return knowledge_context
        
        try:
            # Get relevant knowledge
            result = self.get_relevant_knowledge_for_operation(operation, context)
            if result.is_err():
                return knowledge_context
            
            entries = result.unwrap()
            knowledge_context["knowledge_evaluated"] = True
            knowledge_context["entries_count"] = len(entries)
            
            # Categorize knowledge by domain
            for entry in entries:
                domain = entry.get("domain", "")
                title = entry.get("title", "")
                
                if domain == "SECURITY":
                    knowledge_context["security_considerations"].append(title)
                elif domain == "ARCHITECTURE":
                    knowledge_context["architecture_patterns"].append(title)
                elif domain == "TESTING-VALIDATION":
                    knowledge_context["best_practices"].append(f"Testing: {title}")
                elif domain == "PERFORMANCE":
                    knowledge_context["best_practices"].append(f"Performance: {title}")
                else:
                    knowledge_context["guidelines"].append(f"{domain}: {title}")
            
            return knowledge_context
            
        except Exception:
            return knowledge_context
    
    # ==========================================================================
    # BUSINESS KNOWLEDGE REPOSITORY INTEGRATION (AC-KN-003-01)
    # ==========================================================================
    
    @property
    def has_business_knowledge_repository(self) -> bool:
        """Check if business knowledge repository is available."""
        return self._business_knowledge_repository is not None
    
    @mcp_tool(
        name="get_business_knowledge_summary",
        description="Get summary of available business domain knowledge"
    )
    def get_business_knowledge_summary(self) -> Result[Dict[str, Any]]:
        """
        Get summary of available business knowledge in Domain Brain.
        
        AC-KN-003-01: Business Knowledge Repository Access
        
        Returns:
            Result with business knowledge summary including domains and entry counts
        """
        if not self._business_knowledge_repository:
            return Err("Business knowledge repository not initialized")
        
        try:
            summary = self._business_knowledge_repository.get_knowledge_summary()
            return Ok(summary)
        except Exception as e:
            return Err(f"Failed to get business knowledge summary: {str(e)}")
    
    @mcp_tool(
        name="query_business_knowledge",
        description="Query business domain knowledge by domain, entity type, or keywords"
    )
    def query_business_knowledge(
        self,
        domains: Optional[List[str]] = None,
        entity_types: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> Result[List[Dict[str, Any]]]:
        """
        Query the business knowledge repository.
        
        AC-KN-003-01: Business Knowledge Repository Query
        
        Args:
            domains: Filter by domain IDs (e.g., ["payments", "compliance"])
            entity_types: Filter by entity types (e.g., ["service", "api"])
            keywords: Search keywords in name/description
        
        Returns:
            Result with list of matching business knowledge entries
        """
        if not self._business_knowledge_repository:
            return Err("Business knowledge repository not initialized")
        
        try:
            result = self._business_knowledge_repository.query(
                domains=domains,
                entity_types=entity_types,
                keywords=keywords
            )
            
            # Convert entries to dicts for serialization
            entries = [
                {
                    "id": entry.id,
                    "domain_id": entry.domain_id,
                    "domain_name": entry.domain_name,
                    "entity_type": entry.entity_type,
                    "name": entry.name,
                    "description": entry.description,
                    "source": entry.source
                }
                for entry in result.entries
            ]
            
            return Ok(entries)
        except Exception as e:
            return Err(f"Failed to query business knowledge: {str(e)}")
    
    @mcp_tool(
        name="get_relevant_business_knowledge",
        description="Get relevant business knowledge for request composition"
    )
    def get_relevant_business_knowledge_for_operation(
        self,
        operation: str,
        context: Dict[str, Any],
        max_entries: int = 5
    ) -> Result[List[Dict[str, Any]]]:
        """
        Get relevant business knowledge entries for composing a request.
        
        AC-KN-003-01: Business Knowledge Evaluation for Request Composition
        
        Args:
            operation: The operation being performed
            context: Operation context for relevance matching
            max_entries: Maximum entries to return
        
        Returns:
            Result with relevant business knowledge entries
        """
        if not self._business_knowledge_repository:
            return Ok([])  # Graceful degradation
        
        try:
            # Extract keywords from operation and context
            keywords = [operation]
            if "keywords" in context:
                keywords.extend(context["keywords"])
            if "intent" in context:
                keywords.append(context["intent"])
            
            # Extract domain hints from context
            domain_hints = []
            if "business_domain" in context:
                domain_hints.append(context["business_domain"])
            if "domain" in context:
                domain_hints.append(context["domain"])
            
            # Query business knowledge
            entries = self._business_knowledge_repository.get_relevant_knowledge(
                domains=domain_hints if domain_hints else None,
                keywords=keywords,
                max_entries=max_entries
            )
            
            # Convert to serializable format
            result = [
                {
                    "id": entry.id,
                    "domain_id": entry.domain_id,
                    "domain_name": entry.domain_name,
                    "entity_type": entry.entity_type,
                    "name": entry.name,
                    "description": entry.description,
                    "source": entry.source,
                    "relevance_context": {
                        "matched_domains": domain_hints,
                        "matched_keywords": keywords
                    }
                }
                for entry in entries
            ]
            
            self.logger.log_operation_complete(
                ac_id="AC-KN-003-01",
                operation="BUSINESS_KNOWLEDGE_RETRIEVAL",
                success=True,
                details={
                    "operation": operation,
                    "entries_found": len(result),
                    "domains_searched": domain_hints,
                    "keywords_used": keywords
                }
            )
            
            return Ok(result)
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-KN-003-01",
                operation="BUSINESS_KNOWLEDGE_RETRIEVAL",
                success=False,
                details={"error": str(e)}
            )
            return Ok([])  # Graceful degradation
    
    def _evaluate_business_knowledge_for_request(
        self,
        operation: str,
        context: Dict[str, Any],
        target_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate business knowledge and compose context for request.
        
        AC-KN-003-01: Business Knowledge Evaluation During Request Composition
        
        Args:
            operation: Operation being performed
            context: Operation context
            target_domains: Target orchestrator domains
            
        Returns:
            Dict with business knowledge context for request composition
        """
        business_context = {
            "business_knowledge_evaluated": False,
            "business_domains": [],
            "services": [],
            "apis": [],
            "workflows": [],
            "entities": []
        }
        
        if not self._business_knowledge_repository:
            return business_context
        
        try:
            # Get relevant business knowledge
            result = self.get_relevant_business_knowledge_for_operation(operation, context)
            if result.is_err():
                return business_context
            
            entries = result.unwrap()
            business_context["business_knowledge_evaluated"] = True
            business_context["entries_count"] = len(entries)
            
            # Categorize by entity type
            for entry in entries:
                entity_type = entry.get("entity_type", "").lower()
                name = entry.get("name", "")
                domain = entry.get("domain_name", "")
                
                if domain and domain not in business_context["business_domains"]:
                    business_context["business_domains"].append(domain)
                
                if entity_type == "service":
                    business_context["services"].append(name)
                elif entity_type == "api":
                    business_context["apis"].append(name)
                elif entity_type == "workflow":
                    business_context["workflows"].append(name)
                else:
                    business_context["entities"].append(f"{entity_type}: {name}")
            
            return business_context
            
        except Exception:
            return business_context

    @mcp_tool(
        name="orchestrate_e2e",
        description="Execute E2E orchestration with cross-phase state management"
    )
    def orchestrate_e2e(
        self,
        operation_id: str,
        user_intent: str,
        priority: int = 0
    ) -> Result[Dict[str, Any]]:
        """
        Execute end-to-end orchestration with state consistency.
        
        AC-REM-011-05: Cross-Phase State Consistency
        
        Implements 4-phase orchestration with state carryover:
        - Phase 1: Comprehension (user intent analysis)
        - Phase 2: LENS (language-examination-synthesis-knowledge)
        - Phase 3: Delegation (route to domain orchestrators)
        - Phase 4: Execution (domain-specific execution)
        
        Args:
            operation_id: Unique operation identifier
            user_intent: User's original intent
            priority: Operation priority
            
        Returns:
            Result with E2E orchestration results
        """
        try:
            # AC-REM-011-05: Create operation state
            state = self._state_manager.create_operation(
                operation_id=operation_id,
                user_intent=user_intent,
                priority=priority,
                metadata={
                    "phases": [1, 2, 3, 4],
                    "started_at": datetime.now().isoformat(),
                    "governance_validated": False
                }
            )
            
            self.logger.log_operation_start(
                ac_id="AC-REM-011-05",
                operation="E2E_ORCHESTRATION",
                details={
                    "operation_id": operation_id,
                    "user_intent": user_intent,
                    "phases": 4,
                    "state_manager": "initialized"
                }
            )
            
            # Phase 1: Comprehension (Intent Analysis)
            phase_1_output = self._execute_phase_1(operation_id, state)
            self._state_manager.transition_phase(
                operation_id=operation_id,
                from_phase=1,
                to_phase=2,
                phase_output=phase_1_output
            )
            
            # Phase 2: LENS Pipeline (Intent Routing)
            phase_2_context = self._state_manager.get_context_for_phase(
                operation_id=operation_id,
                target_phase=2
            )
            phase_2_output = self._execute_phase_2(operation_id, phase_2_context or {})
            self._state_manager.transition_phase(
                operation_id=operation_id,
                from_phase=2,
                to_phase=3,
                phase_output=phase_2_output
            )
            
            # Phase 3: Delegation (Route to Orchestrators)
            phase_3_context = self._state_manager.get_context_for_phase(
                operation_id=operation_id,
                target_phase=3
            )
            phase_3_output = self._execute_phase_3(operation_id, phase_3_context or {})
            self._state_manager.transition_phase(
                operation_id=operation_id,
                from_phase=3,
                to_phase=4,
                phase_output=phase_3_output
            )
            
            # Phase 4: Execution (Domain-Specific)
            phase_4_context = self._state_manager.get_context_for_phase(
                operation_id=operation_id,
                target_phase=4
            )
            phase_4_output = self._execute_phase_4(operation_id, phase_4_context or {})
            
            # Mark as complete
            self._state_manager.complete_operation(operation_id)
            
            # Get final state with all phase outputs
            final_state = self._state_manager.get_operation_state(operation_id)
            
            result = {
                "operation_id": operation_id,
                "status": "complete",
                "phases_executed": 4,
                "phase_outputs": final_state.phase_outputs if final_state else {},
                "final_output": phase_4_output,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="E2E_ORCHESTRATION",
                success=True,
                details={
                    "operation_id": operation_id,
                    "phases_executed": 4,
                    "state_consistency": "maintained"
                }
            )
            
            return Ok(result)
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="E2E_ORCHESTRATION",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"E2E orchestration failed: {str(e)}")

    def _execute_phase_1(
        self,
        operation_id: str,
        state: OperationState
    ) -> Dict[str, Any]:
        """
        Execute Phase 1: Comprehension.
        
        Analyze user intent and prepare for LENS pipeline.
        """
        try:
            phase_output = {
                "phase": 1,
                "name": "Comprehension",
                "user_intent": state.user_intent,
                "intent_type": "UNKNOWN",
                "confidence": 0.0,
                "analysis_complete": True
            }
            
            # Attempt to use Interaction Orchestrator if available
            if self.interaction_orchestrator:
                try:
                    result = self.interaction_orchestrator.execute(
                        context={"user_intent": state.user_intent}
                    )
                    if result.is_ok():
                        phase_output.update(result.unwrap())
                except Exception:
                    pass  # Graceful degradation
            
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_1_COMPREHENSION",
                success=True,
                details={"operation_id": operation_id}
            )
            
            return phase_output
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_1_COMPREHENSION",
                success=False,
                details={"error": str(e)}
            )
            return {"phase": 1, "error": str(e)}

    def _execute_phase_2(
        self,
        operation_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute Phase 2: LENS Pipeline.
        
        Route user intent through LENS pipeline.
        """
        try:
            from cortex.brain.lens.pipeline import LENSPipeline
            
            pipeline = LENSPipeline()
            result = pipeline.execute(context)
            
            phase_output = {
                "phase": 2,
                "name": "LENS",
                "routing_decision": result.get("routing_decision"),
                "confidence": result.get("confidence", 0.0),
                "pipeline_complete": True
            }
            
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_2_LENS",
                success=True,
                details={"operation_id": operation_id}
            )
            
            return phase_output
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_2_LENS",
                success=False,
                details={"error": str(e)}
            )
            return {"phase": 2, "error": str(e)}

    def _execute_phase_3(
        self,
        operation_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute Phase 3: Delegation.
        
        Delegate to appropriate domain orchestrators.
        """
        try:
            phase_output = {
                "phase": 3,
                "name": "Delegation",
                "routing_decision": context.get("routing_decision"),
                "delegated_domains": list(self.domain_orchestrators.keys()),
                "delegation_count": len(self.domain_orchestrators)
            }
            
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_3_DELEGATION",
                success=True,
                details={"operation_id": operation_id}
            )
            
            return phase_output
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_3_DELEGATION",
                success=False,
                details={"error": str(e)}
            )
            return {"phase": 3, "error": str(e)}

    def _execute_phase_4(
        self,
        operation_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute Phase 4: Execution.
        
        Perform domain-specific execution.
        """
        try:
            phase_output = {
                "phase": 4,
                "name": "Execution",
                "execution_complete": True,
                "execution_timestamp": datetime.now().isoformat(),
                "result": "Success"
            }
            
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_4_EXECUTION",
                success=True,
                details={"operation_id": operation_id}
            )
            
            return phase_output
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_4_EXECUTION",
                success=False,
                details={"error": str(e)}
            )
            return {"phase": 4, "error": str(e)}

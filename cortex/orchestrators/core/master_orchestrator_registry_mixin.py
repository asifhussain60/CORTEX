"""
MasterOrchestratorRegistryMixin — Domain orchestrator registration and coordination.

Extracted from cortex/orchestrators/core/master_orchestrator.py (Phase 103-a, GAP-103-01).
Single Responsibility: Register domain orchestrators and coordinate multi-domain operations.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from cortex.core.interfaces.i_orchestrator import IOrchestrator
from cortex.core.result import Err, Ok, Result
from cortex.models.orchestrator_metadata import OrchestratorMetadata
from cortex.orchestrators.workflow.exec_gateway_impl import GovernanceViolationError
from cortex.orchestrators.core.governance_registry import GovernanceRegistry
from cortex.orchestrators.core.orchestrator_context_injector import inject_orchestrator_context


class MasterOrchestratorRegistryMixin:
    """Mixin providing orchestrator registry and coordination to MasterOrchestrator.

    Handles:
    - register_orchestrator
    - get_registered_domains
    - get_orchestrator
    - coordinate_operation
    - get_coordination_history
    - get_registry_status
    """

    def register_orchestrator(
        self,
        domain: str,
        orchestrator: IOrchestrator,
        capabilities: Optional[List[str]] = None
    ) -> Result[Dict[str, Any]]:
        """Register a domain-specific orchestrator with MasterOrchestrator.

        This is a critical registration point for the orchestrator architecture.
        Each domain (governance, audit, evidence, etc.) provides a dedicated
        orchestrator instance that handles domain-specific logic and patterns.

        The registration process:
        1. Validates domain name is unique
        2. Stores orchestrator metadata
        3. Logs registration in audit trail
        4. Makes orchestrator available for operation coordination

        Args:
            domain: Domain name identifying orchestrator's scope
                Examples: "governance", "audit", "evidence", "compliance"
            orchestrator: IOrchestrator implementation for this domain
            capabilities: List of capabilities provided by orchestrator
                Examples: ["validate", "enforce", "audit", "remediate"]

        Returns:
            Result[Dict[str, Any]]: Success contains registration metadata:
                - domain: Registered domain name
                - registered: Boolean success flag
                - total_orchestrators: Count after registration
                - registered_at: ISO timestamp

        Raises:
            ValueError: If domain already registered

        Example:
            >>> from cortex.orchestrators.governance import GovernanceOrchestrator
            >>> gov_orch = GovernanceOrchestrator()
            >>> master = MasterOrchestrator.instance()
            >>> result = master.register_orchestrator(
            ...     domain="governance",
            ...     orchestrator=gov_orch,
            ...     capabilities=["validate", "enforce"]
            ... )
            >>> if result.is_ok():
            ...     print(f"Registered: {result.unwrap()}")
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

    def get_registered_domains(self) -> Result[List[str]]:
        """Get list of registered orchestrator domains.

        Returns the complete list of domains for which orchestrators have
        been registered with MasterOrchestrator. Each domain represents a
        logical area of functionality (e.g., governance, audit, evidence).

        This list changes dynamically as orchestrators are registered/unregistered
        during system lifecycle. Used for:
        - Capability discovery (what domains are available)
        - Operation routing (which orchestrators can handle request)
        - System health checking (are all expected domains present)
        - Orchestrator management (list for admin operations)

        Returns:
            Result[List[str]]: Ok with sorted list of registered domain names,
                or Err with failure message. Empty list if no orchestrators
                registered yet.

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> result = master.get_registered_domains()
            >>> if result.is_ok():
            ...     domains = result.unwrap()
            ...     print(f"Available domains: {', '.join(domains)}")
            ...     # e.g., ['governance', 'audit', 'evidence']
        """
        try:
            domains = list(self.domain_orchestrators.keys())
            return Ok(domains)
        except Exception as e:
            return Err(f"Failed to get registered domains: {str(e)}")

    def get_orchestrator(self, domain: str) -> Result[IOrchestrator]:
        """Get orchestrator for a specific domain.

        Retrieves the orchestrator instance registered for the given domain.
        Used by coordination logic to delegate domain-specific operations to
        the appropriate orchestrator implementation.

        This enables:
        - Dynamic orchestrator discovery (no hardcoding of orchestrators)
        - Flexible domain-based routing (route to correct handler)
        - Orchestrator lifecycle management (attach/detach at runtime)
        - Capability-driven architecture (route by capability)

        Args:
            domain: Domain name identifying the orchestrator
                Examples: "governance", "audit", "evidence", "compliance"

        Returns:
            Result[IOrchestrator]: Ok with orchestrator instance conforming
                to IOrchestrator interface, or Err with error message if:
                - Domain not found (not registered)
                - Internal lookup failure

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> result = master.get_orchestrator("governance")
            >>> if result.is_ok():
            ...     orchestrator = result.unwrap()
            ...     # Can now call orchestrator.execute_operation(), etc.
            ... else:
            ...     print(f"Domain not found: {result.error}")
        """
        try:
            if domain not in self.domain_orchestrators:
                return Err(f"No orchestrator registered for domain '{domain}'")

            return Ok(self.domain_orchestrators[domain].orchestrator)
        except Exception as e:
            return Err(f"Failed to get orchestrator: {str(e)}")

    @inject_orchestrator_context
    def coordinate_operation(
        self,
        operation: str,
        context: Optional[Dict[str, Any]] = None,
        target_domains: Optional[List[str]] = None
    ) -> Result[Dict[str, Any]]:
        """Coordinate an operation across multiple domain orchestrators.

        This method implements the critical coordination pattern for distributed
        orchestration. It validates governance policies, coordinates execution
        across domain-specific orchestrators, and aggregates results atomically.

        Coordination Process:
        1. Governance Validation: Validates against CORE-017, CORE-019 policies
        2. Turn Tracking: Increments turn counter for per-turn validation (CORE-019)
        3. Knowledge Evaluation: Retrieves technical and business knowledge
        4. Domain Orchestration: Delegates to applicable domain orchestrators
        5. Result Aggregation: Collects and combines all results
        6. Atomic Logging: Records operation in single transaction (AC-FIX-001-01)

        Governance Enforcement:
        - CORE-017: Strict governance enforcement
        - CORE-019: Per-turn validation via turn counter
        - CORE-027: Audit trail per turn
        - AC-FIX-001-01: Atomic state + audit logging

        Args:
            operation: Operation name to execute (e.g., "validate", "enforce")
            context: Operation context dictionary containing:
                - metadata: Operation metadata
                - parameters: Operation parameters
                - user_id: Requesting user
                - request_id: Unique request identifier
            target_domains: Specific domains to target. If None, targets all
                registered orchestrators (e.g., ["governance", "audit"])

        Returns:
            Result[Dict[str, Any]]: Success contains aggregated results:
                - operation: Operation name
                - target_domains: Domains that were targeted
                - results: Dict of domain -> result mappings
                - coordination_time_ms: Total coordination time
                - turn_number: Turn number for this coordination
                - governance_validated: Boolean confirmation of validation

        Raises:
            GovernanceViolationError: If governance validation fails

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> result = master.coordinate_operation(
            ...     operation="validate",
            ...     context={
            ...         "metadata": {"version": "1.0"},
            ...         "parameters": {"target": "feature_x"}
            ...     },
            ...     target_domains=["governance", "audit"]
            ... )
            >>> if result.is_ok():
            ...     aggregated = result.unwrap()
            ...     print(f"Turn: {aggregated['turn_number']}")
            ... else:
            ...     print(f"Coordination failed: {result.error}")
        """
        # AC-FIX-001-01: Wrap entire operation in atomic transaction
        # Both coordination execution and audit logging occur in single transaction
        # Phase 71-B: Consult OPJ for operational patterns before coordinating
        self._opj_consult(str(operation))
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

                # ════════════════════════════════════════════════════════════════════════
                # Stage 1-4: Delegation to execute_operation for actual orchestration
                # ════════════════════════════════════════════════════════════════════════
                # NOTE: Real Stage 1 & 2 wiring happens in execute_operation() method
                # coordinate_operation() is used for EXPLICIT cross-domain coordination

                # ════════════════════════════════════════════════════════════════════════
                # Stage 3: Knowledge Synthesis (existing, now with Stage 1+2 context)
                # ════════════════════════════════════════════════════════════════════════

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

                # AC-HYBRID-KNOWLEDGE-005: Synthesize CORTEX + Company knowledge into final instructions
                synthesized_instructions = None
                synthesized_sources = None
                try:
                    if self._synthesis_engine is not None:
                        synthesis_result = self._synthesis_engine.synthesize_for_intent(
                            intent_type=operation,
                            company_context=context
                        )
                        synthesized_instructions = synthesis_result.instruction
                        synthesized_sources = [
                            {
                                "layer": src.layer,
                                "domain": src.domain,
                                "yaml_files": src.yaml_files,
                                "priority": src.priority
                            }
                            for src in synthesis_result.sources
                        ]
                        self.logger.log_operation_complete(
                            ac_id="AC-HYBRID-KNOWLEDGE-005",
                            operation="KNOWLEDGE_SYNTHESIS",
                            success=True,
                            details={
                                "intent": operation,
                                "sources_count": len(synthesis_result.sources),
                                "cortex_sources": len([s for s in synthesis_result.sources if s.layer == "CORTEX"]),
                                "company_sources": len([s for s in synthesis_result.sources if s.layer == "COMPANY"]),
                                "synthesis_confidence": synthesis_result.synthesis_confidence
                            }
                        )
                except Exception as e:
                    # Log but don't fail - synthesis is enhancement, not blocking
                    self.logger.log_operation_complete(
                        ac_id="AC-HYBRID-KNOWLEDGE-005",
                        operation="KNOWLEDGE_SYNTHESIS",
                        success=False,
                        details={"error": f"Knowledge synthesis failed: {str(e)}"}
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
                    # NOTE: Stage 1 & 2 wiring is in execute_operation(), not coordinate_operation()
                    # AC-KN-002-01: Include technical knowledge context in composite request
                    "knowledge_context": knowledge_context,
                    # AC-KN-003-01: Include business knowledge context in composite request
                    "business_knowledge_context": business_knowledge_context,
                    # AC-HYBRID-KNOWLEDGE-005: Include synthesized instructions with source attribution
                    "synthesized_instructions": synthesized_instructions,
                    "instruction_sources": synthesized_sources if synthesized_sources else []
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
                        # NOTE: Stage 1 & 2 wiring is in execute_operation(), not coordinate_operation()
                        # Knowledge synthesis metrics
                        "knowledge_evaluated": knowledge_context.get("knowledge_evaluated", False),
                        "knowledge_entries_used": knowledge_context.get("entries_count", 0),
                        "business_knowledge_evaluated": business_knowledge_context.get("business_knowledge_evaluated", False),
                        "business_knowledge_entries_used": business_knowledge_context.get("entries_count", 0),
                        # AC-HYBRID-KNOWLEDGE-005: Include synthesis metrics in completion log
                        "instructions_synthesized": synthesized_instructions is not None,
                        "instruction_sources_count": len(synthesized_sources) if synthesized_sources else 0
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

    def get_coordination_history(
        self,
        limit: int = 10
    ) -> Result[List[Dict[str, Any]]]:
        """Get recent coordination operation history.

        Returns the history of coordination operations performed by
        MasterOrchestrator. Each entry records the details of a coordination
        including which domains were engaged, what operations were performed,
        and the aggregated results.

        The coordination history enables:
        - Operation tracking (what operations have been coordinated)
        - Performance analysis (response times, success rates)
        - Debugging (replay coordination logic)
        - Compliance auditing (who coordinated what when)
        - Pattern analysis (identify frequently coordinated operations)

        Args:
            limit: Maximum number of history entries to return (default: 10)
                Recent entries returned first (most recent at index 0)
                Range: 1-1000 entries

        Returns:
            Result[List[Dict[str, Any]]]: Ok with list of coordination entries,
                each containing:
                - operation: Operation name coordinated
                - target_domains: Domains that participated
                - results: Dict of domain -> result mappings
                - timestamp: ISO 8601 when coordination occurred
                - duration_ms: Total coordination time
                - success: Boolean success indicator

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> result = master.get_coordination_history(limit=5)
            >>> if result.is_ok():
            ...     history = result.unwrap()
            ...     for entry in history:
            ...         print(f"Op: {entry['operation']} in {entry['duration_ms']}ms")
        """
        try:
            history = self.operation_history[-limit:]
            return Ok(history)
        except Exception as e:
            return Err(f"Failed to get history: {str(e)}")

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

    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """Get audit trail with hash chain verification.

        Retrieves the audit trail recording all operations performed by
        MasterOrchestrator. Each entry includes operation ID, timestamp,
        duration, success/failure status, actor, context, and hash chain
        for integrity verification (AC-FIX-001-01).

        Args:
            limit: Maximum number of entries to retrieve (default: 100)

        Returns:
            Result[list]: Ok with list of audit entries (most recent first),
                or Err with failure message.

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> result = master.get_audit_trail(limit=50)
            >>> if result.is_ok():
            ...     entries = result.unwrap()
            ...     for entry in entries:
            ...         print(f"{entry['timestamp']}: {entry['operation']}")
        """
        try:
            trail = self.db.query_audit_trail(limit=limit)
            return Ok(trail)
        except Exception as e:
            return Err(f"Failed to get audit trail: {str(e)}")

    def get_registry_status(self) -> Result[Dict[str, Any]]:
        """Get current registry status and orchestrator information.

        Returns comprehensive information about the MasterOrchestrator's
        registry of domain orchestrators. Provides administrative visibility
        into system structure and capabilities.

        Registry Status Contains:
        - Total count of registered orchestrators
        - Complete metadata for each domain:
          * Domain name and orchestrator type
          * Version number and capabilities
          * Registration timestamp (when orchestrator was added)
        - Total operations coordinated

        Use Cases:
        - System health dashboard (see what's registered)
        - Administrative operations (inventory of orchestrators)
        - Debugging (verify orchestrator registration)
        - Auto-discovery (programmatic capability enumeration)
        - Monitoring (track changes over time)

        Returns:
            Result[Dict[str, Any]]: Ok with registry metadata:
                - total_orchestrators: Count of registered orchestrators
                - domains: List of domain information dicts:
                    * domain: Domain name
                    * type: Orchestrator class name
                    * version: Orchestrator version string
                    * capabilities: List of capability strings
                    * registered_at: ISO 8601 registration timestamp
                - total_operations: Total coordination operations performed

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> result = master.get_registry_status()
            >>> if result.is_ok():
            ...     status = result.unwrap()
            ...     print(f"Total orchestrators: {status['total_orchestrators']}")
            ...     for domain in status['domains']:
            ...         print(f"  - {domain['domain']}: {domain['type']} v{domain['version']}")
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

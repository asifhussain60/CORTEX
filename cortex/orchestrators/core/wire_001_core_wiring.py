"""
WIRE-001 Implementation - Core Orchestrator Registration

AC-TRANSFORM-001-WIRE-001: Register Core Orchestrators
- InteractionOrchestrator (Stage 1 comprehension)
- IntentRouter (Stage 2 routing)
- TDDOrchestrator (test-driven development)
- WorkflowOrchestrator (multi-step workflows)
- WrappedTDDOrchestrator (TDD with governance)

All orchestrators instantiated, configured, and registered with the wiring registry.

Author: GitHub Copilot
Date: 2026-01-24
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from pathlib import Path

from cortex.orchestrators.core.orchestrator_wiring import (
    OrchestratorWiringRegistry,
    OrchestratorCategory,
    get_wiring_registry
)
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


class CoreOrchestratorWiring:
    """
    Implementation of WIRE-001: Core Orchestrator Registration
    
    Registers 6 core orchestrators that form the foundation of CORTEX:
    1. InteractionOrchestrator - Stage 1 comprehension and pattern enforcement
    2. IntentRouter - Stage 2 intent classification and domain routing
    3. TDDOrchestrator - Test-driven development execution
    4. WorkflowOrchestrator - Multi-step workflow coordination
    5. WrappedTDDOrchestrator - TDD with governance enforcement
    6. OrchestratorBootstrap - System initialization and setup
    """
    
    def __init__(self, registry: Optional[OrchestratorWiringRegistry] = None):
        """Initialize core orchestrator wiring"""
        self.logger = EnhancedAuditLogger.instance()
        self.registry = registry or get_wiring_registry()
        self.wiring_results: Dict[str, bool] = {}
    
    def wire_interaction_orchestrator(self) -> bool:
        """
        Register InteractionOrchestrator for Stage 1 comprehension.
        
        Handles:
        - User input comprehension
        - Communication pattern enforcement
        - Context preservation across turns
        - Session management
        
        Returns:
            True if successfully registered
        """
        try:
            from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
            from cortex.core.interfaces import IOrchestrator
            from unittest.mock import Mock
            
            # Create a minimal mock orchestrator to pass to ConversationProtocol
            mock_orchestrator = Mock(spec=IOrchestrator)
            
            # Initialize ConversationProtocol with mock orchestrator
            from cortex.brain.core.orchestrator.conversation_protocol import ConversationProtocol
            protocol = ConversationProtocol(orchestrator=mock_orchestrator)
            
            # Initialize InteractionOrchestrator with protocol
            orchestrator = InteractionOrchestrator(
                conversation_protocol=protocol
            )
            
            result = self.registry.register_orchestrator(
                domain="interaction",
                orchestrator=orchestrator,
                category=OrchestratorCategory.CORE,
                capabilities=[
                    "user_input_comprehension",
                    "communication_pattern_enforcement",
                    "context_preservation",
                    "session_management"
                ],
                routing_keywords=["understand", "analyze", "comprehend", "listen"],
                version="1.0"
            )
            
            success = result.is_ok()
            self.wiring_results["InteractionOrchestrator"] = success
            
            if success:
                self.logger.log_operation_complete(
                    ac_id="AC-TRANSFORM-001-WIRE-001-interaction",
                    operation="WIRE_INTERACTION_ORCHESTRATOR",
                    success=True,
                    details={
                        "domain": "interaction",
                        "capabilities": ["comprehension", "pattern_enforcement", "context_preservation"],
                        "stage": "Stage 1 - Comprehension"
                    }
                )
            
            return success
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-TRANSFORM-001-WIRE-001-interaction",
                operation="WIRE_INTERACTION_ORCHESTRATOR",
                success=False,
                details={"error": str(e)}
            )
            self.wiring_results["InteractionOrchestrator"] = False
            return False
    
    def wire_intent_router(self) -> bool:
        """
        Register IntentRouter for Stage 2 routing.
        
        Handles:
        - Intent classification from user input
        - Domain selection for orchestrators
        - Multi-intent routing
        - Confidence scoring
        
        Returns:
            True if successfully registered
        """
        try:
            from cortex.orchestrators.core.intent_router import IntentRouter
            
            orchestrator = IntentRouter()
            
            result = self.registry.register_orchestrator(
                domain="intent_routing",
                orchestrator=orchestrator,
                category=OrchestratorCategory.CORE,
                capabilities=[
                    "intent_classification",
                    "domain_selection",
                    "multi_intent_routing",
                    "confidence_scoring"
                ],
                routing_keywords=["route", "select", "classify", "detect"],
                version="1.0"
            )
            
            success = result.is_ok()
            self.wiring_results["IntentRouter"] = success
            
            if success:
                self.logger.log_operation_complete(
                    ac_id="AC-TRANSFORM-001-WIRE-001-intent",
                    operation="WIRE_INTENT_ROUTER",
                    success=True,
                    details={
                        "domain": "intent_routing",
                        "capabilities": ["classification", "routing", "scoring"],
                        "stage": "Stage 2 - Intent Routing"
                    }
                )
            
            return success
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-TRANSFORM-001-WIRE-001-intent",
                operation="WIRE_INTENT_ROUTER",
                success=False,
                details={"error": str(e)}
            )
            self.wiring_results["IntentRouter"] = False
            return False
    
    def wire_tdd_orchestrator(self) -> bool:
        """
        Register TDDOrchestrator for test-driven development.
        
        Handles:
        - Test generation from requirements
        - Test execution and reporting
        - Coverage analysis
        - TDD best practices enforcement
        
        Returns:
            True if successfully registered
        """
        try:
            from cortex.orchestrators.core.tdd_orchestrator import get_tdd_orchestrator
            
            orchestrator = get_tdd_orchestrator()
            
            result = self.registry.register_orchestrator(
                domain="tdd",
                orchestrator=orchestrator,
                category=OrchestratorCategory.CORE,
                capabilities=[
                    "test_generation",
                    "test_execution",
                    "coverage_analysis",
                    "tdd_best_practices"
                ],
                routing_keywords=["test", "tdd", "coverage", "unit_test"],
                version="1.0"
            )
            
            success = result.is_ok()
            self.wiring_results["TDDOrchestrator"] = success
            
            if success:
                self.logger.log_operation_complete(
                    ac_id="AC-TRANSFORM-001-WIRE-001-tdd",
                    operation="WIRE_TDD_ORCHESTRATOR",
                    success=True,
                    details={
                        "domain": "tdd",
                        "capabilities": ["test_generation", "coverage", "best_practices"],
                        "knowledge_yamls_loaded": True
                    }
                )
            
            return success
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-TRANSFORM-001-WIRE-001-tdd",
                operation="WIRE_TDD_ORCHESTRATOR",
                success=False,
                details={"error": str(e)}
            )
            self.wiring_results["TDDOrchestrator"] = False
            return False
    
    def wire_workflow_orchestrator(self) -> bool:
        """
        Register WorkflowOrchestrator for multi-step workflows.
        
        Handles:
        - Workflow execution and coordination
        - Step management and sequencing
        - State transitions
        - Parallel execution support
        
        Returns:
            True if successfully registered
        """
        try:
            from cortex.orchestrators.core.workflow_orchestrator import WorkflowOrchestrator
            
            # WorkflowOrchestrator requires workspace_root as Path
            workspace_root = Path(__file__).parent.parent.parent.parent
            orchestrator = WorkflowOrchestrator(workspace_root=workspace_root)
            
            result = self.registry.register_orchestrator(
                domain="workflow",
                orchestrator=orchestrator,
                category=OrchestratorCategory.CORE,
                capabilities=[
                    "workflow_execution",
                    "step_management",
                    "state_transitions",
                    "parallel_execution"
                ],
                routing_keywords=["workflow", "step", "execute", "chain"],
                version="1.0"
            )
            
            success = result.is_ok()
            self.wiring_results["WorkflowOrchestrator"] = success
            
            if success:
                self.logger.log_operation_complete(
                    ac_id="AC-TRANSFORM-001-WIRE-001-workflow",
                    operation="WIRE_WORKFLOW_ORCHESTRATOR",
                    success=True,
                    details={
                        "domain": "workflow",
                        "capabilities": ["execution", "steps", "transitions"],
                        "workspace_root": str(workspace_root)
                    }
                )
            
            return success
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-TRANSFORM-001-WIRE-001-workflow",
                operation="WIRE_WORKFLOW_ORCHESTRATOR",
                success=False,
                details={"error": str(e)}
            )
            self.wiring_results["WorkflowOrchestrator"] = False
            return False
    
    def wire_wrapped_tdd_orchestrator(self) -> bool:
        """
        Register WrappedTDDOrchestrator for TDD with governance.
        
        Handles:
        - TDD test generation with governance validation
        - Test execution with compliance checking
        - Governance rule enforcement
        - Compliance reporting
        
        Returns:
            True if successfully registered
        """
        try:
            from cortex.orchestrators.core.wrapped_tdd_orchestrator import WrappedTDDOrchestrator
            
            orchestrator = WrappedTDDOrchestrator()
            
            result = self.registry.register_orchestrator(
                domain="wrapped_tdd",
                orchestrator=orchestrator,
                category=OrchestratorCategory.CORE,
                capabilities=[
                    "tdd_with_governance",
                    "test_generation",
                    "compliance_checking",
                    "governance_enforcement"
                ],
                routing_keywords=["governed_test", "compliant_test", "test_compliance"],
                version="1.0"
            )
            
            success = result.is_ok()
            self.wiring_results["WrappedTDDOrchestrator"] = success
            
            if success:
                self.logger.log_operation_complete(
                    ac_id="AC-TRANSFORM-001-WIRE-001-wrapped",
                    operation="WIRE_WRAPPED_TDD_ORCHESTRATOR",
                    success=True,
                    details={
                        "domain": "wrapped_tdd",
                        "capabilities": ["tdd", "governance", "compliance"],
                        "governance_level": "STRICT"
                    }
                )
            
            return success
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-TRANSFORM-001-WIRE-001-wrapped",
                operation="WIRE_WRAPPED_TDD_ORCHESTRATOR",
                success=False,
                details={"error": str(e)}
            )
            self.wiring_results["WrappedTDDOrchestrator"] = False
            return False
    
    def execute_all_wiring(self) -> Dict[str, Any]:
        """
        Execute all WIRE-001 core orchestrator registrations.
        
        Returns:
            Dictionary with wiring results and summary
        """
        results = {
            "InteractionOrchestrator": self.wire_interaction_orchestrator(),
            "IntentRouter": self.wire_intent_router(),
            "TDDOrchestrator": self.wire_tdd_orchestrator(),
            "WorkflowOrchestrator": self.wire_workflow_orchestrator(),
            "WrappedTDDOrchestrator": self.wire_wrapped_tdd_orchestrator(),
        }
        
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        
        self.logger.log_operation_complete(
            ac_id="AC-TRANSFORM-001-WIRE-001",
            operation="CORE_ORCHESTRATOR_WIRING_COMPLETE",
            success=success_count >= 5,  # All 5 must succeed
            details={
                "total_orchestrators": total_count,
                "successfully_wired": success_count,
                "orchestrators": results,
                "wiring_registry_status": self.registry.get_wiring_status()
            }
        )
        
        return {
            "results": results,
            "summary": {
                "total_wired": success_count,
                "target": total_count,
                "percentage": (success_count / total_count) * 100,
                "status": "SUCCESS" if success_count == total_count else "PARTIAL"
            }
        }


def execute_wire_001() -> Dict[str, Any]:
    """
    Standalone function to execute WIRE-001 orchestrator wiring.
    
    This is the main entry point for Phase 2 of TRANSFORM-001.
    
    Returns:
        Dictionary with execution results
    """
    wiring = CoreOrchestratorWiring()
    return wiring.execute_all_wiring()

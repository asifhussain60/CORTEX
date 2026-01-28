"""
MCP Adapters - IOrchestratorAdapter implementations for all 23 orchestrators + Phase 8.5 RecommendationEngine

This module contains adapter implementations that expose orchestrator capabilities
via the MCP (Model Context Protocol) interface.

AC-ID: AC-MCP-ADAPTER-001 through AC-MCP-ADAPTER-023 + AC-MCP-ADAPTER-PHASE-8
Authority: CORE-031 (Unified Registry), AC-SECURITY-FRAMEWORK-001
Date: 2026-01-26 (updated 2026-01-28)
"""

from .core_adapters import (
    MasterOrchestratorAdapter,
    TDDOrchestratorAdapter,
    IntentRouterAdapter,
    InteractionOrchestratorAdapter,
    WorkflowOrchestratorAdapter,
    WrappedTDDOrchestratorAdapter,
)

from .domain_adapters import (
    RefactoringOrchestratorAdapter,
    PlanningOrchestratorAdapter,
    DomainOrchestratorAdapter,
    ConversationOrchestratorAdapter,
    SeleniumPlaywrightOrchestratorAdapter,
    DocumentationOrchestratorAdapter,
)

from .support_adapters import (
    OnboardingOrchestratorAdapter,
    ToolDiscoveryOrchestratorAdapter,
    UpgradeOrchestratorAdapter,
    RollbackOrchestratorAdapter,
    SetupOrchestratorAdapter,
    ComposedOrchestratorAdapter,
    OrchestratorBootstrapAdapter,
    DoRApprovalGateAdapter,
    LENSSynthesisAdapter,
    GovernanceRegistryAdapter,
    KnowledgeRepositoryAdapter,
)

from .recommendation_adapter import (
    RecommendationEngineAdapter,
)

__all__ = [
    # Core adapters
    "MasterOrchestratorAdapter",
    "TDDOrchestratorAdapter",
    "IntentRouterAdapter",
    "InteractionOrchestratorAdapter",
    "WorkflowOrchestratorAdapter",
    "WrappedTDDOrchestratorAdapter",
    # Domain adapters
    "RefactoringOrchestratorAdapter",
    "PlanningOrchestratorAdapter",
    "DomainOrchestratorAdapter",
    "ConversationOrchestratorAdapter",
    "SeleniumPlaywrightOrchestratorAdapter",
    "DocumentationOrchestratorAdapter",
    # Support adapters
    "OnboardingOrchestratorAdapter",
    "ToolDiscoveryOrchestratorAdapter",
    "UpgradeOrchestratorAdapter",
    "RollbackOrchestratorAdapter",
    "SetupOrchestratorAdapter",
    "ComposedOrchestratorAdapter",
    "OrchestratorBootstrapAdapter",
    "DoRApprovalGateAdapter",
    "LENSSynthesisAdapter",
    "GovernanceRegistryAdapter",
    "KnowledgeRepositoryAdapter",
    # Phase 8.5: RecommendationEngine adapter
    "RecommendationEngineAdapter",
]

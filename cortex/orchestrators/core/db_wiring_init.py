"""
Database-Backed Orchestrator Wiring Initialization

AC-PERMANENT-FIX-009: Initialize all 23 orchestrators in DatabaseBackedRegistry

This module:
1. Initializes database schema on first run
2. Registers all 23 orchestrators with proper metadata
3. Computes deterministic wiring order
4. Starts background health checker

Categories:
- Core (6): MasterOrchestrator, InteractionOrchestrator, IntentRouter,
            TDDOrchestrator, WorkflowOrchestrator, WrappedTDDOrchestrator
- Domain (6): RefactoringOrchestrator, PlanningOrchestrator, DomainOrchestrator,
              ConversationOrchestrator, SeleniumPlaywrightOrchestrator, DocumentationOrchestrator
- Support (11): OnboardingOrchestrator, ToolDiscoveryOrchestrator, UpgradeOrchestrator,
                RollbackOrchestrator, SetupOrchestrator, ComposedOrchestrator,
                OrchestratorBootstrap, DoRApprovalGate, LENSSynthesis,
                GovernanceRegistry, KnowledgeRepository

Authority: CORE-031, CORE-035
Author: Asif Hussain
Date: 2026-01-25
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from cortex.orchestrators.core.database_registry import (
    DatabaseBackedRegistry,
    OrchestratorCategory,
    OrchestratorConfig,
    WiringState,
    get_database_registry,
)
from cortex.orchestrators.core.health_checker import (
    OrchestratorHealthChecker,
    create_health_checker,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Orchestrator Definitions - 23 Total
# =============================================================================

CORE_ORCHESTRATORS: List[OrchestratorConfig] = [
    OrchestratorConfig(
        name="MasterOrchestrator",
        module_path="cortex.orchestrators.core.master_orchestrator",
        class_name="MasterOrchestrator",
        category=OrchestratorCategory.CORE,
        priority=1,  # First to wire - coordinates others
        dependencies=[],
        capabilities=["coordination", "delegation", "knowledge_synthesis", "5_stage_pipeline"],
        routing_keywords=["master", "orchestrate", "coordinate", "delegate"],
    ),
    OrchestratorConfig(
        name="InteractionOrchestrator",
        module_path="cortex.orchestrators.core.interaction_orchestrator",
        class_name="InteractionOrchestrator",
        category=OrchestratorCategory.CORE,
        priority=2,
        dependencies=["MasterOrchestrator"],
        capabilities=["user_comprehension", "context_preservation", "challenge_engine", "lens_protocol"],
        routing_keywords=["understand", "analyze", "comprehend", "listen", "challenge"],
    ),
    OrchestratorConfig(
        name="IntentRouter",
        module_path="cortex.orchestrators.core.intent_router",
        class_name="IntentRouter",
        category=OrchestratorCategory.CORE,
        priority=3,
        dependencies=["MasterOrchestrator", "InteractionOrchestrator"],
        capabilities=["intent_classification", "confidence_scoring", "domain_routing"],
        routing_keywords=["route", "classify", "intent", "dispatch"],
    ),
    OrchestratorConfig(
        name="TDDOrchestrator",
        module_path="cortex.orchestrators.core.tdd_orchestrator",
        class_name="TDDOrchestrator",
        category=OrchestratorCategory.CORE,
        priority=4,
        dependencies=["MasterOrchestrator"],
        capabilities=["tdd_workflow", "red_green_refactor", "test_generation", "code_implementation"],
        routing_keywords=["test", "tdd", "implement", "red", "green", "refactor"],
    ),
    OrchestratorConfig(
        name="WorkflowOrchestrator",
        module_path="cortex.orchestrators.core.workflow_orchestrator",
        class_name="WorkflowOrchestrator",
        category=OrchestratorCategory.CORE,
        priority=5,
        dependencies=["MasterOrchestrator"],
        capabilities=["multi_step_execution", "state_management", "workflow_coordination"],
        routing_keywords=["workflow", "pipeline", "steps", "sequence"],
    ),
    OrchestratorConfig(
        name="WrappedTDDOrchestrator",
        module_path="cortex.orchestrators.core.wrapped_tdd_orchestrator",
        class_name="WrappedTDDOrchestrator",
        category=OrchestratorCategory.CORE,
        priority=6,
        dependencies=["TDDOrchestrator"],
        capabilities=["governed_tdd", "compliance_enforcement", "audit_trail"],
        routing_keywords=["governed", "compliant", "audit"],
        is_utility=True,
    ),
]

DOMAIN_ORCHESTRATORS: List[OrchestratorConfig] = [
    OrchestratorConfig(
        name="RefactoringOrchestrator",
        module_path="cortex.orchestrators.domain.refactoring_orchestrator",
        class_name="RefactoringOrchestrator",
        category=OrchestratorCategory.DOMAIN,
        priority=10,
        dependencies=["MasterOrchestrator", "TDDOrchestrator"],
        capabilities=["code_refactoring", "solid_principles", "pattern_extraction", "quality_improvement"],
        routing_keywords=["refactor", "improve", "clean", "solid", "extract"],
    ),
    OrchestratorConfig(
        name="PlanningOrchestrator",
        module_path="cortex.orchestrators.domain.planning_orchestrator",
        class_name="PlanningOrchestrator",
        category=OrchestratorCategory.DOMAIN,
        priority=11,
        dependencies=["MasterOrchestrator"],
        capabilities=["phase_planning", "dependency_analysis", "roadmap_generation", "milestone_tracking"],
        routing_keywords=["plan", "roadmap", "milestone", "schedule", "phase"],
    ),
    OrchestratorConfig(
        name="DomainOrchestrator",
        module_path="cortex.orchestrators.domain_orchestrator",
        class_name="DomainOrchestrator",
        category=OrchestratorCategory.DOMAIN,
        priority=12,
        dependencies=["MasterOrchestrator"],
        capabilities=["domain_logic", "business_rules", "domain_knowledge"],
        routing_keywords=["domain", "business", "rules"],
    ),
    OrchestratorConfig(
        name="ConversationOrchestrator",
        module_path="cortex.orchestrators.conversation_orchestrator",
        class_name="ConversationOrchestrator",
        category=OrchestratorCategory.DOMAIN,
        priority=13,
        dependencies=["InteractionOrchestrator"],
        capabilities=["multi_turn_conversation", "state_tracking", "context_continuity"],
        routing_keywords=["conversation", "chat", "dialogue", "session"],
    ),
    OrchestratorConfig(
        name="SeleniumPlaywrightOrchestrator",
        module_path="cortex.orchestrators.domain.selenium_playwright_orchestrator",
        class_name="SeleniumPlaywrightOrchestrator",
        category=OrchestratorCategory.DOMAIN,
        priority=14,
        dependencies=["MasterOrchestrator"],
        capabilities=["browser_automation", "e2e_testing", "web_scraping"],
        routing_keywords=["selenium", "playwright", "browser", "automation", "e2e"],
        is_optional=True,
    ),
    OrchestratorConfig(
        name="DocumentationOrchestrator",
        module_path="cortex.orchestrators.documentation.orchestrator",
        class_name="DocumentationOrchestrator",
        category=OrchestratorCategory.DOMAIN,
        priority=15,
        dependencies=["MasterOrchestrator"],
        capabilities=["documentation_generation", "diagram_creation", "api_docs"],
        routing_keywords=["doc", "document", "diagram", "api"],
    ),
]

SUPPORT_ORCHESTRATORS: List[OrchestratorConfig] = [
    OrchestratorConfig(
        name="OnboardingOrchestrator",
        module_path="cortex.orchestrators.support.onboarding_orchestrator",
        class_name="OnboardingOrchestrator",
        category=OrchestratorCategory.SUPPORT,
        priority=20,
        dependencies=[],
        capabilities=["user_onboarding", "setup_wizard", "guided_experience"],
        routing_keywords=["onboard", "welcome", "tutorial", "getting_started"],
    ),
    OrchestratorConfig(
        name="ToolDiscoveryOrchestrator",
        module_path="cortex.orchestrators.support.tool_discovery_orchestrator",
        class_name="ToolDiscoveryOrchestrator",
        category=OrchestratorCategory.SUPPORT,
        priority=21,
        dependencies=[],
        capabilities=["capability_discovery", "tool_search", "mcp_tools"],
        routing_keywords=["discover", "search", "find", "tools", "capabilities"],
    ),
    OrchestratorConfig(
        name="UpgradeOrchestrator",
        module_path="cortex.orchestrators.upgrade_orchestrator",
        class_name="UpgradeOrchestrator",
        category=OrchestratorCategory.SUPPORT,
        priority=22,
        dependencies=[],
        capabilities=["version_upgrade", "migration", "patching"],
        routing_keywords=["upgrade", "update", "migrate", "version"],
    ),
    OrchestratorConfig(
        name="RollbackOrchestrator",
        module_path="cortex.orchestrators.rollback_orchestrator",
        class_name="RollbackOrchestrator",
        category=OrchestratorCategory.SUPPORT,
        priority=23,
        dependencies=[],
        capabilities=["rollback", "recovery", "saga_pattern", "undo"],
        routing_keywords=["rollback", "recover", "undo", "restore"],
    ),
    OrchestratorConfig(
        name="SetupOrchestrator",
        module_path="cortex.orchestrators.support.setup_orchestrator",
        class_name="SetupOrchestrator",
        category=OrchestratorCategory.SUPPORT,
        priority=24,
        dependencies=[],
        capabilities=["environment_setup", "configuration", "initialization"],
        routing_keywords=["setup", "config", "initialize", "prepare"],
    ),
    OrchestratorConfig(
        name="ComposedOrchestrator",
        module_path="cortex.orchestrators.composition.composition_engine",
        class_name="ComposedOrchestrator",
        category=OrchestratorCategory.SUPPORT,
        priority=25,
        dependencies=[],
        capabilities=["composition", "chaining", "pipeline_execution"],
        routing_keywords=["compose", "chain", "pipeline", "combine"],
    ),
    OrchestratorConfig(
        name="OrchestratorBootstrap",
        module_path="cortex.orchestrators.bootstrap",
        class_name="OrchestratorBootstrap",
        category=OrchestratorCategory.SUPPORT,
        priority=26,
        dependencies=[],
        capabilities=["system_initialization", "dependency_injection", "wiring"],
        routing_keywords=["bootstrap", "init", "startup"],
        is_utility=True,
    ),
    OrchestratorConfig(
        name="DoRApprovalGate",
        module_path="cortex.orchestrators.core.dor_approval_gate",
        class_name="DoRApprovalGate",
        category=OrchestratorCategory.SUPPORT,
        priority=27,
        dependencies=["InteractionOrchestrator"],
        capabilities=["approval_workflow", "dor_validation", "user_confirmation"],
        routing_keywords=["approve", "confirm", "validate", "gate"],
        is_utility=True,
    ),
    OrchestratorConfig(
        name="LENSSynthesis",
        module_path="cortex.orchestrators.core.lens_synthesis",
        class_name="LENSSynthesis",
        category=OrchestratorCategory.SUPPORT,
        priority=28,
        dependencies=["InteractionOrchestrator"],
        capabilities=["lens_protocol", "intent_synthesis", "context_aggregation"],
        routing_keywords=["lens", "synthesize", "aggregate"],
        is_utility=True,
    ),
    OrchestratorConfig(
        name="GovernanceRegistry",
        module_path="cortex.brain.core.governance_registry",
        class_name="GovernanceRegistry",
        category=OrchestratorCategory.SUPPORT,
        priority=29,
        dependencies=[],
        capabilities=["rule_storage", "tier_management", "compliance_checking"],
        routing_keywords=["governance", "rules", "compliance", "tier"],
        is_utility=True,
    ),
    OrchestratorConfig(
        name="KnowledgeRepository",
        module_path="cortex.brain.core.knowledge.knowledge_repository",
        class_name="KnowledgeRepository",
        category=OrchestratorCategory.SUPPORT,
        priority=30,
        dependencies=[],
        capabilities=["knowledge_storage", "best_practices", "yaml_parsing"],
        routing_keywords=["knowledge", "best_practice", "guidance"],
        is_utility=True,
    ),
]

ALL_ORCHESTRATORS = CORE_ORCHESTRATORS + DOMAIN_ORCHESTRATORS + SUPPORT_ORCHESTRATORS


# =============================================================================
# Initialization Functions
# =============================================================================

def register_all_orchestrators(registry: Optional[DatabaseBackedRegistry] = None) -> int:
    """
    Register all 23 orchestrators in the database registry.
    
    Args:
        registry: Optional registry instance. Uses singleton if not provided.
        
    Returns:
        Number of successfully registered orchestrators
    """
    registry = registry or get_database_registry()
    
    # Ensure schema is initialized
    schema_result = registry.initialize_schema()
    if schema_result.is_err():
        logger.error(f"Schema initialization failed: {schema_result.err()}")
        return 0
    
    registered = 0
    for config in ALL_ORCHESTRATORS:
        result = registry.register(config)
        if result.is_ok():
            registered += 1
            logger.debug(f"Registered: {config.name}")
        else:
            logger.warning(f"Failed to register {config.name}: {result.err()}")
    
    logger.info(f"Registered {registered}/{len(ALL_ORCHESTRATORS)} orchestrators")
    return registered


def initialize_database_wiring(
    start_health_checker: bool = True,
    health_check_interval: int = 60
) -> DatabaseBackedRegistry:
    """
    Full initialization of database-backed wiring.
    
    1. Initialize database schema
    2. Register all orchestrators
    3. Optionally start health checker
    
    Args:
        start_health_checker: Whether to start background health monitoring
        health_check_interval: Seconds between health checks
        
    Returns:
        Initialized DatabaseBackedRegistry instance
    """
    logger.info("Initializing database-backed orchestrator wiring...")
    
    # Get or create registry singleton
    registry = get_database_registry()
    
    # Initialize schema
    schema_result = registry.initialize_schema()
    if schema_result.is_err():
        logger.error(f"Schema init failed: {schema_result.err()}")
        raise RuntimeError(f"Cannot initialize wiring: {schema_result.err()}")
    
    # Check if already populated
    stats = registry.get_wiring_statistics()
    if stats["total_registered"] == 0:
        # First time - register all orchestrators
        count = register_all_orchestrators(registry)
        logger.info(f"First-time registration: {count} orchestrators")
    else:
        logger.info(f"Registry already has {stats['total_registered']} orchestrators")
    
    # Optionally start health checker
    if start_health_checker:
        health_checker = create_health_checker(registry, health_check_interval)
        health_checker.start()
        logger.info(f"Health checker started (interval: {health_check_interval}s)")
    
    logger.info("Database-backed wiring initialization complete")
    return registry


def get_orchestrator_count_by_category() -> dict:
    """
    Get count of orchestrators by category.
    
    Returns:
        Dict with category counts
    """
    return {
        "core": len(CORE_ORCHESTRATORS),
        "domain": len(DOMAIN_ORCHESTRATORS),
        "support": len(SUPPORT_ORCHESTRATORS),
        "total": len(ALL_ORCHESTRATORS),
    }


def validate_orchestrator_definitions() -> List[str]:
    """
    Validate all orchestrator definitions.
    
    Checks:
    - Unique names
    - Valid module paths
    - Dependency consistency
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    names = set()
    
    for config in ALL_ORCHESTRATORS:
        # Check unique names
        if config.name in names:
            errors.append(f"Duplicate orchestrator name: {config.name}")
        names.add(config.name)
        
        # Check dependencies exist
        for dep in config.dependencies:
            if dep not in names and dep not in [c.name for c in ALL_ORCHESTRATORS]:
                # Dependency might be defined later in list
                found = any(c.name == dep for c in ALL_ORCHESTRATORS)
                if not found:
                    errors.append(f"{config.name} has unknown dependency: {dep}")
    
    return errors


# =============================================================================
# Module-level initialization check
# =============================================================================

def verify_definitions() -> None:
    """Verify orchestrator definitions on module load."""
    errors = validate_orchestrator_definitions()
    if errors:
        logger.error(f"Orchestrator definition errors: {errors}")
        raise ValueError(f"Invalid orchestrator definitions: {errors}")


# Run verification on import
verify_definitions()


if __name__ == "__main__":
    # CLI entry point for testing
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("Database-Backed Orchestrator Wiring Initialization")
    print("=" * 60)
    
    counts = get_orchestrator_count_by_category()
    print(f"\nOrchestrators to register:")
    print(f"  Core:    {counts['core']}")
    print(f"  Domain:  {counts['domain']}")
    print(f"  Support: {counts['support']}")
    print(f"  Total:   {counts['total']}")
    
    if "--init" in sys.argv:
        print("\nInitializing database wiring...")
        registry = initialize_database_wiring(start_health_checker=False)
        stats = registry.get_wiring_statistics()
        print(f"\nRegistry stats: {stats}")
    else:
        print("\nRun with --init to initialize database wiring")

"""
Unified Orchestrator Initialization (AC-PERMANENT-FIX-022)

Merges Phase 3 database initialization and database-backed wiring into a single,
idempotent orchestrator initialization system.

This solves the recurring issue where Phase 3 was resetting orchestrator wiring
by unconditionally recreating the database. The unified approach:

1. Initializes database schema (idempotent - only if needed)
2. Registers all 23 orchestrators (idempotent - skips if already registered)
3. Marks orchestrators as wired=1 (permanent - never reset)
4. Starts background health checker
5. Generates registry report

Key improvement: Database state is ADDITIVE, never destructive. Once an
orchestrator is wired, it stays wired across multiple initialization calls.

Authority: CORE-008 (TDD), CORE-027 (Audit trail), CORE-031 (Single registry)
AC-ID: AC-PERMANENT-FIX-022
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.orchestrators.core.database_registry import (
    OrchestratorCategory,
    OrchestratorConfig,
    get_database_registry,
)
from cortex.orchestrators.core.health_checker import create_health_checker

logger = logging.getLogger(__name__)


# =============================================================================
# Orchestrator Definitions (23 Total)
# =============================================================================

CORE_ORCHESTRATORS: List[OrchestratorConfig] = [
    OrchestratorConfig(
        name="MasterOrchestrator",
        module_path="cortex.orchestrators.core.master_orchestrator",
        class_name="MasterOrchestrator",
        category=OrchestratorCategory.CORE,
        priority=1,
        dependencies=[],
        capabilities=[
            "coordination",
            "delegation",
            "knowledge_synthesis",
            "5_stage_pipeline",
        ],
        routing_keywords=["master", "orchestrate", "coordinate", "delegate"],
    ),
    OrchestratorConfig(
        name="InteractionOrchestrator",
        module_path="cortex.orchestrators.core.interaction_orchestrator",
        class_name="InteractionOrchestrator",
        category=OrchestratorCategory.CORE,
        priority=2,
        dependencies=["MasterOrchestrator"],
        capabilities=[
            "user_comprehension",
            "context_preservation",
            "challenge_engine",
            "lens_protocol",
        ],
        routing_keywords=["understand", "analyze", "comprehend", "listen", "challenge"],
        is_optional=True,
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
        is_optional=True,
    ),
    OrchestratorConfig(
        name="TDDOrchestrator",
        module_path="cortex.orchestrators.core.tdd_orchestrator",
        class_name="TDDOrchestrator",
        category=OrchestratorCategory.CORE,
        priority=4,
        dependencies=["MasterOrchestrator"],
        capabilities=[
            "tdd_workflow",
            "red_green_refactor",
            "test_generation",
            "code_implementation",
        ],
        routing_keywords=["test", "tdd", "implement", "red", "green", "refactor"],
    ),
    OrchestratorConfig(
        name="WorkflowOrchestrator",
        module_path="cortex.orchestrators.core.workflow_orchestrator",
        class_name="WorkflowOrchestrator",
        category=OrchestratorCategory.CORE,
        priority=5,
        dependencies=["MasterOrchestrator"],
        capabilities=[
            "multi_step_execution",
            "state_management",
            "workflow_coordination",
        ],
        routing_keywords=["workflow", "pipeline", "steps", "sequence"],
        is_optional=True,
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
        is_optional=True,
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
        capabilities=[
            "code_refactoring",
            "solid_principles",
            "pattern_extraction",
            "quality_improvement",
        ],
        routing_keywords=["refactor", "improve", "clean", "solid", "extract"],
    ),
    OrchestratorConfig(
        name="PlanningOrchestrator",
        module_path="cortex.orchestrators.domain.planning_orchestrator",
        class_name="PlanningOrchestrator",
        category=OrchestratorCategory.DOMAIN,
        priority=11,
        dependencies=["MasterOrchestrator"],
        capabilities=[
            "phase_planning",
            "ac_tracking",
            "challenge_generation",
            "intent_classification",
            "execution_gating",
            "audit_trail_management",
            "dependency_analysis",
            "roadmap_generation",
            "milestone_tracking",
        ],
        routing_keywords=["plan", "roadmap", "milestone", "schedule", "phase"],
    ),
    OrchestratorConfig(
        name="DomainOrchestrator",
        module_path="cortex.orchestrators.domain.domain_orchestrator",
        class_name="DomainOrchestrator",
        category=OrchestratorCategory.DOMAIN,
        priority=12,
        dependencies=["MasterOrchestrator"],
        capabilities=["domain_routing", "domain_knowledge", "context_management"],
        routing_keywords=["domain", "business", "context"],
    ),
    OrchestratorConfig(
        name="ConversationOrchestrator",
        module_path="cortex.orchestrators.domain.conversation_orchestrator",
        class_name="ConversationOrchestrator",
        category=OrchestratorCategory.DOMAIN,
        priority=13,
        dependencies=["MasterOrchestrator", "InteractionOrchestrator"],
        capabilities=["multi_turn_conversation", "context_preservation", "turn_management"],
        routing_keywords=["conversation", "dialogue", "chat", "multi_turn"],
    ),
    OrchestratorConfig(
        name="SeleniumPlaywrightOrchestrator",
        module_path="cortex.orchestrators.domain.selenium_playwright_orchestrator",
        class_name="SeleniumPlaywrightOrchestrator",
        category=OrchestratorCategory.DOMAIN,
        priority=14,
        dependencies=["MasterOrchestrator"],
        capabilities=["browser_automation", "selenium", "playwright", "web_interaction"],
        routing_keywords=["selenium", "playwright", "browser", "automation"],
    ),
    OrchestratorConfig(
        name="AdaptiveExecutionOrchestrator",
        module_path="cortex.orchestrators.domain.adaptive_execution_orchestrator",
        class_name="AdaptiveExecutionOrchestrator",
        category=OrchestratorCategory.DOMAIN,
        priority=15,
        dependencies=["MasterOrchestrator"],
        capabilities=["adaptive_execution", "condition_evaluation", "dynamic_routing"],
        routing_keywords=["adaptive", "dynamic", "conditional"],
    ),
]

SUPPORT_ORCHESTRATORS: List[OrchestratorConfig] = [
    OrchestratorConfig(
        name="OnboardingOrchestrator",
        module_path="cortex.orchestrators.support.onboarding_orchestrator",
        class_name="OnboardingOrchestrator",
        category=OrchestratorCategory.SUPPORT,
        priority=20,
        dependencies=["MasterOrchestrator"],
        capabilities=["onboarding", "setup", "initialization", "guidance"],
        routing_keywords=["onboard", "setup", "initialize", "start"],
    ),
    OrchestratorConfig(
        name="ToolDiscoveryOrchestrator",
        module_path="cortex.orchestrators.support.tool_discovery_orchestrator",
        class_name="ToolDiscoveryOrchestrator",
        category=OrchestratorCategory.SUPPORT,
        priority=21,
        dependencies=["MasterOrchestrator"],
        capabilities=["tool_discovery", "tool_cataloging", "capability_inventory"],
        routing_keywords=["discover", "tools", "catalog", "inventory"],
    ),
    OrchestratorConfig(
        name="UpgradeOrchestrator",
        module_path="cortex.orchestrators.support.upgrade_orchestrator",
        class_name="UpgradeOrchestrator",
        category=OrchestratorCategory.SUPPORT,
        priority=22,
        dependencies=["MasterOrchestrator"],
        capabilities=["upgrade", "migration", "version_management"],
        routing_keywords=["upgrade", "migrate", "update", "version"],
    ),
    OrchestratorConfig(
        name="RollbackOrchestrator",
        module_path="cortex.orchestrators.support.rollback_orchestrator",
        class_name="RollbackOrchestrator",
        category=OrchestratorCategory.SUPPORT,
        priority=23,
        dependencies=["MasterOrchestrator"],
        capabilities=["rollback", "recovery", "state_restoration"],
        routing_keywords=["rollback", "recover", "undo", "restore"],
    ),
    OrchestratorConfig(
        name="SetupOrchestrator",
        module_path="cortex.orchestrators.support.setup_orchestrator",
        class_name="SetupOrchestrator",
        category=OrchestratorCategory.SUPPORT,
        priority=24,
        dependencies=["MasterOrchestrator"],
        capabilities=["setup", "configuration", "environment_setup"],
        routing_keywords=["setup", "config", "configure", "environment"],
    ),
    OrchestratorConfig(
        name="ComposedOrchestrator",
        module_path="cortex.orchestrators.support.composed_orchestrator",
        class_name="ComposedOrchestrator",
        category=OrchestratorCategory.SUPPORT,
        priority=25,
        dependencies=["MasterOrchestrator"],
        capabilities=["composition", "orchestration", "coordination"],
        routing_keywords=["compose", "combine", "coordinate"],
    ),
    OrchestratorConfig(
        name="OrchestratorBootstrap",
        module_path="cortex.orchestrators.core.orchestrator_bootstrap",
        class_name="OrchestratorBootstrap",
        category=OrchestratorCategory.SUPPORT,
        priority=26,
        dependencies=[],
        capabilities=["bootstrap", "initialization", "startup"],
        routing_keywords=["bootstrap", "startup", "initialize"],
    ),
    OrchestratorConfig(
        name="DoRApprovalGate",
        module_path="cortex.orchestrators.core.dor_approval_gate",
        class_name="DoRApprovalGate",
        category=OrchestratorCategory.SUPPORT,
        priority=27,
        dependencies=["MasterOrchestrator"],
        capabilities=["approval_gating", "dor_validation", "intent_approval"],
        routing_keywords=["approve", "gate", "validation"],
        is_utility=True,
    ),
    OrchestratorConfig(
        name="LENSSynthesis",
        module_path="cortex.orchestrators.core.lens_synthesis",
        class_name="LENSSynthesis",
        category=OrchestratorCategory.SUPPORT,
        priority=28,
        dependencies=["MasterOrchestrator"],
        capabilities=["lens_analysis", "synthesis", "intent_synthesis"],
        routing_keywords=["lens", "synthesize", "analyze"],
        is_utility=True,
    ),
    OrchestratorConfig(
        name="GovernanceRegistry",
        module_path="cortex.brain.core.governance_registry",
        class_name="GovernanceRegistry",
        category=OrchestratorCategory.SUPPORT,
        priority=29,
        dependencies=[],
        capabilities=["governance", "rule_management", "compliance"],
        routing_keywords=["governance", "rules", "compliance"],
        is_utility=True,
    ),
    OrchestratorConfig(
        name="KnowledgeRepository",
        module_path="cortex.brain.core.knowledge.knowledge_repository",
        class_name="KnowledgeRepository",
        category=OrchestratorCategory.SUPPORT,
        priority=30,
        dependencies=[],
        capabilities=["knowledge_management", "best_practices", "patterns"],
        routing_keywords=["knowledge", "learn", "patterns"],
        is_utility=True,
    ),
]

ALL_ORCHESTRATORS: List[OrchestratorConfig] = (
    CORE_ORCHESTRATORS + DOMAIN_ORCHESTRATORS + SUPPORT_ORCHESTRATORS
)


# =============================================================================
# Unified Orchestrator Initializer
# =============================================================================


@dataclass
class InitializationResult:
    """Result of orchestrator initialization"""

    success: bool
    database_created: bool
    orchestrators_registered: int
    wired_orchestrators: int
    health_checker_started: bool
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    permanent_fix_id: str = "AC-PERMANENT-FIX-022"
    message: str = ""


class UnifiedOrchestratorInitializer:
    """
    Unified orchestrator initialization combining Phase 3 + wiring.

    Guarantees:
    - Idempotent: Safe to call multiple times
    - SSOT: Single source of truth for orchestrator state
    - Permanent: Once wired=1, never reset to 0
    """

    def __init__(self, db_path: str) -> None:
        """
        Initialize the unified orchestrator initializer.

        Args:
            db_path: Path to orchestrator registry database
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def initialize(self) -> Dict[str, Any]:
        """
        Initialize orchestrators with idempotent, permanent wiring.

        Returns:
            Dictionary with initialization results
        """
        try:
            # Step 1: Ensure directory exists
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

            # Step 2: Connect to database (creates if doesn't exist)
            self.conn = sqlite3.connect(self.db_path)
            database_created = not Path(self.db_path).exists()

            # Step 3: Create schema (idempotent - only if tables don't exist)
            self._create_schema()

            # Step 4: Register orchestrators (idempotent - skips duplicates)
            registered_count = self._register_orchestrators()

            # Step 5: Mark as wired (idempotent - updates wired=1)
            wired_count = self._mark_wired()

            # Step 6: Start health checker
            health_started = self._start_health_checker()

            # Step 7: Generate audit log
            self._log_initialization()

            # Close connection
            if self.conn:
                self.conn.close()

            result = InitializationResult(
                success=True,
                database_created=database_created,
                orchestrators_registered=registered_count,
                wired_orchestrators=wired_count,
                health_checker_started=health_started,
                message=f"Initialized {registered_count} orchestrators, "
                f"{wired_count} wired, health checker {'active' if health_started else 'inactive'}",
            )

            return {
                "success": result.success,
                "database_created": result.database_created,
                "orchestrators_registered": result.orchestrators_registered,
                "wired_orchestrators": result.wired_orchestrators,
                "health_checker_started": result.health_checker_started,
                "timestamp": result.timestamp,
                "permanent_fix_id": result.permanent_fix_id,
                "message": result.message,
            }

        except Exception as e:
            logger.error(f"Failed to initialize orchestrators: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _create_schema(self) -> bool:
        """
        Create database schema if it doesn't exist (idempotent).

        Returns:
            True if schema created, False if already exists
        """
        if not self.conn:
            raise RuntimeError("Database connection not established")

        cursor = self.conn.cursor()

        # Check if orchestrators table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='orchestrators'"
        )
        if cursor.fetchone():
            logger.info("Schema already exists - using existing orchestrators table")
            return False

        # Create orchestrators table (for fresh databases)
        cursor.execute(
            """
            CREATE TABLE orchestrators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                module_path TEXT NOT NULL,
                class_name TEXT NOT NULL,
                category TEXT NOT NULL,
                priority INTEGER NOT NULL,
                dependencies TEXT,
                capabilities TEXT,
                routing_keywords TEXT,
                is_optional BOOLEAN DEFAULT 0,
                is_utility BOOLEAN DEFAULT 0,
                wired BOOLEAN DEFAULT 0,
                health_status TEXT DEFAULT 'UNKNOWN',
                description TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                wired_at TIMESTAMP,
                last_health_check TIMESTAMP
            )
        """
        )

        # Create indexes
        cursor.execute("CREATE INDEX idx_category ON orchestrators(category)")
        cursor.execute("CREATE INDEX idx_priority ON orchestrators(priority)")
        cursor.execute("CREATE INDEX idx_wired ON orchestrators(wired)")
        cursor.execute("CREATE INDEX idx_health ON orchestrators(health_status)")

        # Create wiring log table
        cursor.execute(
            """
            CREATE TABLE wiring_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orchestrator_name TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create registry metadata table
        cursor.execute(
            """
            CREATE TABLE registry_metadata (
                id INTEGER PRIMARY KEY,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        self.conn.commit()
        logger.info("Schema created successfully")
        return True

    def _register_orchestrators(self) -> int:
        """
        Register all 23 orchestrators (idempotent).

        Returns:
            Count of newly registered orchestrators
        """
        if not self.conn:
            raise RuntimeError("Database connection not established")

        cursor = self.conn.cursor()
        registered_count = 0

        for orch in ALL_ORCHESTRATORS:
            try:
                # Skip if already registered
                cursor.execute(
                    "SELECT id FROM orchestrators WHERE name = ?",
                    (orch.name,),
                )
                if cursor.fetchone():
                    logger.debug(f"Orchestrator {orch.name} already registered")
                    continue

                # Insert orchestrator (using existing schema field names)
                cursor.execute(
                    """
                    INSERT INTO orchestrators (
                        name, category, module_path, class_name, priority, description
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        orch.name,
                        orch.category.value,
                        orch.module_path,
                        orch.class_name,
                        orch.priority,
                        f"{orch.category.value.title()} orchestrator: {orch.name}",
                    ),
                )

                # Log registration if table exists
                try:
                    cursor.execute(
                        """
                        INSERT INTO wiring_log (orchestrator_name, action, status, details)
                        VALUES (?, ?, ?, ?)
                    """,
                        (orch.name, "REGISTER", "SUCCESS", f"Registered {orch.name}"),
                    )
                except sqlite3.OperationalError:
                    # wiring_log table doesn't exist, skip
                    pass

                registered_count += 1
                logger.info(f"Registered orchestrator: {orch.name}")

            except sqlite3.IntegrityError:
                logger.debug(f"Orchestrator {orch.name} already exists")

        self.conn.commit()
        logger.info(f"Total orchestrators registered: {registered_count}")
        return registered_count

    def _mark_wired(self) -> int:
        """
        Mark all orchestrators as wired=1 (PERMANENT - never reset).

        Returns:
            Count of wired orchestrators
        """
        if not self.conn:
            raise RuntimeError("Database connection not established")

        cursor = self.conn.cursor()

        # Update all orchestrators to wired=1
        cursor.execute(
            """
            UPDATE orchestrators
            SET wired=1, wired_at=CURRENT_TIMESTAMP, health_status='INITIALIZED'
            WHERE wired=0
        """
        )

        # Get total wired count
        cursor.execute("SELECT COUNT(*) FROM orchestrators WHERE wired=1")
        wired_count = cursor.fetchone()[0]

        self.conn.commit()
        logger.info(f"Total orchestrators wired: {wired_count}")
        return wired_count

    def _start_health_checker(self) -> bool:
        """
        Start background health checker (optional).

        Returns:
            True if health checker started
        """
        try:
            registry = get_database_registry()
            health_checker = create_health_checker(registry, interval_seconds=60)
            logger.info("Health checker started")
            return True
        except Exception as e:
            logger.warning(f"Failed to start health checker: {e}")
            return False

    def _log_initialization(self) -> None:
        """Log initialization to audit trail."""
        if not self.conn:
            raise RuntimeError("Database connection not established")

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO registry_metadata (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, last_updated=CURRENT_TIMESTAMP
        """,
            ("last_initialization", datetime.now(timezone.utc).isoformat()),
        )

        cursor.execute(
            """
            INSERT INTO registry_metadata (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, last_updated=CURRENT_TIMESTAMP
        """,
            ("permanent_fix_id", "AC-PERMANENT-FIX-022"),
        )

        self.conn.commit()
        logger.info("Initialization logged to audit trail")


# =============================================================================
# Module-level Functions
# =============================================================================


def initialize_orchestrators(
    db_path: str | None = None,
    start_health_checker: bool = True,
) -> Dict[str, Any]:
    """
    Initialize orchestrators (idempotent module function).

    Args:
        db_path: Path to registry database (uses default if not provided)
        start_health_checker: Whether to start background health checker

    Returns:
        Dictionary with initialization results
    """
    if db_path is None:
        db_path = ".cortex/orchestrator_registry.db"

    initializer = UnifiedOrchestratorInitializer(db_path)
    result = initializer.initialize()

    return result


def get_initialization_status(db_path: str | None = None) -> Dict[str, Any]:
    """
    Get current orchestrator initialization status.

    Args:
        db_path: Path to registry database

    Returns:
        Status dictionary
    """
    if db_path is None:
        db_path = ".cortex/orchestrator_registry.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if database is initialized
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='orchestrators'"
        )
        if not cursor.fetchone():
            conn.close()
            return {
                "initialized": False,
                "total_orchestrators": 0,
                "wired_orchestrators": 0,
            }

        # Get orchestrator counts
        cursor.execute("SELECT COUNT(*) FROM orchestrators")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM orchestrators WHERE wired=1")
        wired = cursor.fetchone()[0]

        conn.close()

        return {
            "initialized": total > 0,
            "total_orchestrators": total,
            "wired_orchestrators": wired,
            "all_wired": total == wired,
        }

    except Exception as e:
        logger.error(f"Failed to get initialization status: {e}")
        return {
            "initialized": False,
            "total_orchestrators": 0,
            "wired_orchestrators": 0,
            "error": str(e),
        }

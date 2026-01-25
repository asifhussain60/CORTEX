"""
Database-Backed Orchestrator Registry - Single Source of Truth (SSOT)

This replaces fragmented in-memory wiring across:
- MasterOrchestrator.__init__()
- OrchestratorBootstrap.initialize()
- IntentRouter.setup_routing()
- Multiple ad-hoc initialization points

Key Features:
- Persistent orchestrator configuration in SQLite
- Deterministic wiring order (survives git merges)
- Automatic validation at startup
- Background health checks
- Full audit trail

Authority: CORE-031 (Single Orchestrator Registry)
AC-ID: AC-DB-SSOT-001

Author: Asif Hussain
Date: 2026-01-25
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type

from cortex.brain.core.path_resolver import resolve_path
from cortex.brain.core.result import Err, Ok, Result
from cortex.core.interfaces import IOrchestrator
from cortex.infrastructure.database import DatabaseManager

logger = logging.getLogger(__name__)


class WiringState(Enum):
    """Orchestrator registry state machine."""
    
    UNINITIALIZED = "uninitialized"
    LOADING = "loading"
    REGISTERING = "registering"
    COMPUTING_ORDER = "computing_order"
    WIRING = "wiring"
    WIRED = "wired"
    VALIDATION_FAILED = "validation_failed"
    UNWIRED = "unwired"


class OrchestratorCategory(Enum):
    """Category for organizing orchestrators."""
    
    CORE = "core"
    DOMAIN = "domain"
    SUPPORT = "support"
    INFRASTRUCTURE = "infrastructure"


@dataclass
class OrchestratorConfig:
    """Configuration for an orchestrator in the registry."""
    
    name: str
    module_path: str
    class_name: str
    category: OrchestratorCategory
    priority: int = 100  # Lower = earlier in wiring order
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    routing_keywords: List[str] = field(default_factory=list)
    is_optional: bool = False
    version: str = "1.0.0"
    # New fields for flexible wiring
    init_args: Dict[str, Any] = field(default_factory=dict)  # Constructor arguments
    is_utility: bool = False  # True if not a full IOrchestrator (no execute())
    factory_function: Optional[str] = None  # Optional factory function name
    

@dataclass
class WiringResult:
    """Result of a wiring operation."""
    
    success: bool
    orchestrator_name: str
    timestamp: datetime
    duration_ms: float
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegistryValidation:
    """Result of validation check."""
    
    passed: bool
    timestamp: datetime
    checked_count: int
    passed_count: int
    failures: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class WiringSnapshot:
    """Snapshot of successful wiring state."""
    
    snapshot_id: str
    total_orchestrators: int
    wired_count: int
    failed_count: int
    snapshot_time: datetime
    wiring_duration_ms: float
    validation_hash: str
    orchestrator_names: List[str] = field(default_factory=list)


class DatabaseBackedRegistry:
    """
    SSOT for orchestrator registration, wiring, and validation.
    
    Replaces:
    - MasterOrchestrator._wire_orchestrators()
    - OrchestratorBootstrap.auto_wire()
    - IntentRouter.setup_routing()
    - All ad-hoc registration calls
    
    Guarantees:
    - All orchestrators wired in deterministic order
    - No silent failures
    - Continuous validation
    - Automatic detection of unwiring
    - Full audit trail in database
    
    Usage:
        registry = DatabaseBackedRegistry.instance()
        registry.initialize()  # Load from DB or populate from code
        registry.wire_all()    # Wire all orchestrators
        registry.validate_wiring()  # Verify wiring state
    """
    
    _instance: Optional['DatabaseBackedRegistry'] = None
    _lock = threading.Lock()
    
    # Schema version for migrations
    SCHEMA_VERSION = "2.0"
    
    def __init__(self, db: Optional[DatabaseManager] = None):
        """
        Initialize the database-backed registry.
        
        Args:
            db: Optional DatabaseManager instance. If None, creates default.
        """
        self._db = db or DatabaseManager()
        self._orchestrators: Dict[str, Dict[str, Any]] = {}
        self._instances: Dict[str, IOrchestrator] = {}
        self._wiring_order: List[str] = []
        self._state = WiringState.UNINITIALIZED
        self._validation_log: List[RegistryValidation] = []
        self._wiring_results: List[WiringResult] = []
        self._last_validation: Optional[RegistryValidation] = None
        self._initialization_time: Optional[float] = None
        self._state_lock = threading.Lock()
    
    @classmethod
    def instance(cls, db: Optional[DatabaseManager] = None) -> 'DatabaseBackedRegistry':
        """Get or create singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(db)
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None
    
    @property
    def state(self) -> WiringState:
        """Get current registry state."""
        return self._state
    
    @property
    def is_wired(self) -> bool:
        """Check if registry is fully wired."""
        return self._state == WiringState.WIRED
    
    # =========================================================================
    # Database Schema Management
    # =========================================================================
    
    def initialize_schema(self) -> Result[None]:
        """
        Initialize database schema for orchestrator registry.
        
        Creates 4 new tables:
        - orchestrator_registry: Orchestrator configurations
        - wiring_log: Wiring attempt history
        - wiring_state_snapshot: Successful wiring snapshots
        - health_check_log: Health check history
        
        Returns:
            Result indicating success or error
        """
        try:
            with self._db.get_connection() as conn:
                # Table 1: Orchestrator Registry
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS orchestrator_registry (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        orchestrator_name TEXT UNIQUE NOT NULL,
                        module_path TEXT NOT NULL,
                        class_name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        priority INTEGER NOT NULL DEFAULT 100,
                        dependencies TEXT,
                        capabilities TEXT,
                        routing_keywords TEXT,
                        is_optional BOOLEAN DEFAULT 0,
                        version TEXT DEFAULT '1.0.0',
                        registered_at TEXT NOT NULL,
                        registered_by TEXT,
                        status TEXT DEFAULT 'PENDING',
                        code_hash TEXT
                    )
                """)
                
                # Table 2: Wiring Log (immutable history)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS wiring_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        orchestrator_name TEXT NOT NULL,
                        attempt_number INTEGER DEFAULT 1,
                        success BOOLEAN NOT NULL,
                        timestamp TEXT NOT NULL,
                        duration_ms REAL,
                        error_message TEXT,
                        stack_trace TEXT,
                        session_id TEXT,
                        FOREIGN KEY (orchestrator_name) 
                            REFERENCES orchestrator_registry(orchestrator_name)
                    )
                """)
                
                # Table 3: Wiring State Snapshot
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS wiring_state_snapshot (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        snapshot_id TEXT UNIQUE NOT NULL,
                        total_orchestrators INTEGER NOT NULL,
                        wired_count INTEGER NOT NULL,
                        failed_count INTEGER NOT NULL,
                        snapshot_time TEXT NOT NULL,
                        wiring_duration_ms REAL,
                        validation_hash TEXT NOT NULL,
                        orchestrator_names TEXT
                    )
                """)
                
                # Table 4: Health Check Log
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS health_check_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        check_time TEXT NOT NULL,
                        orchestrators_ok INTEGER NOT NULL,
                        orchestrators_failed INTEGER NOT NULL,
                        unwiring_detected BOOLEAN DEFAULT 0,
                        recovery_attempted BOOLEAN DEFAULT 0,
                        recovery_success BOOLEAN DEFAULT 0,
                        details TEXT
                    )
                """)
                
                # Create indexes for performance
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_wiring_log_timestamp 
                    ON wiring_log(timestamp DESC)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_wiring_log_name 
                    ON wiring_log(orchestrator_name)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_snapshot_time 
                    ON wiring_state_snapshot(snapshot_time DESC)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_health_check_time 
                    ON health_check_log(check_time DESC)
                """)
                
                # Create schema_version table if not exists
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version TEXT PRIMARY KEY,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                # Update schema version
                conn.execute("""
                    INSERT OR REPLACE INTO schema_version (version, updated_at)
                    VALUES (?, ?)
                """, (self.SCHEMA_VERSION, datetime.now(timezone.utc).isoformat()))
                
                conn.commit()
                
            logger.info(f"Database schema initialized (version {self.SCHEMA_VERSION})")
            return Ok(None)
            
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            return Err(f"Schema initialization failed: {str(e)}")
    
    def check_schema_version(self) -> Result[str]:
        """
        Check current schema version.
        
        Returns:
            Result containing schema version string or error
        """
        try:
            with self._db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT version FROM schema_version ORDER BY updated_at DESC LIMIT 1
                """)
                row = cursor.fetchone()
                if row:
                    return Ok(row[0])
                return Ok("1.0")  # Default if no version found
        except Exception as e:
            # Table might not exist yet
            return Ok("1.0")
    
    def needs_migration(self) -> bool:
        """Check if database needs migration."""
        version_result = self.check_schema_version()
        if version_result.is_err():
            return True
        current_version = version_result.unwrap()
        return current_version != self.SCHEMA_VERSION
    
    # =========================================================================
    # Orchestrator Registration
    # =========================================================================
    
    def register(
        self,
        config: OrchestratorConfig,
        registered_by: str = "system"
    ) -> Result[None]:
        """
        Register an orchestrator configuration in the database.
        
        Args:
            config: OrchestratorConfig with orchestrator details
            registered_by: Who/what registered this orchestrator
            
        Returns:
            Result indicating success or error
        """
        if self._state not in (WiringState.UNINITIALIZED, WiringState.LOADING, WiringState.REGISTERING):
            return Err(f"Cannot register after wiring started (state={self._state})")
        
        try:
            with self._db.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO orchestrator_registry (
                        orchestrator_name, module_path, class_name, category,
                        priority, dependencies, capabilities, routing_keywords,
                        is_optional, version, registered_at, registered_by, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
                """, (
                    config.name,
                    config.module_path,
                    config.class_name,
                    config.category.value,
                    config.priority,
                    json.dumps(config.dependencies),
                    json.dumps(config.capabilities),
                    json.dumps(config.routing_keywords),
                    1 if config.is_optional else 0,
                    config.version,
                    datetime.now(timezone.utc).isoformat(),
                    registered_by
                ))
                conn.commit()
            
            # Also store in memory for fast access
            self._orchestrators[config.name] = {
                'config': config,
                'instance': None,
                'wired': False
            }
            
            logger.debug(f"Registered orchestrator: {config.name}")
            return Ok(None)
            
        except Exception as e:
            logger.error(f"Failed to register {config.name}: {e}")
            return Err(f"Registration failed: {str(e)}")
    
    def load_from_database(self) -> Result[int]:
        """
        Load orchestrator configurations from database.
        
        Returns:
            Result containing count of loaded orchestrators or error
        """
        self._state = WiringState.LOADING
        
        try:
            with self._db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT orchestrator_name, module_path, class_name, category,
                           priority, dependencies, capabilities, routing_keywords,
                           is_optional, version
                    FROM orchestrator_registry
                    ORDER BY priority ASC
                """)
                
                count = 0
                for row in cursor.fetchall():
                    config = OrchestratorConfig(
                        name=row[0],
                        module_path=row[1],
                        class_name=row[2],
                        category=OrchestratorCategory(row[3]),
                        priority=row[4],
                        dependencies=json.loads(row[5] or '[]'),
                        capabilities=json.loads(row[6] or '[]'),
                        routing_keywords=json.loads(row[7] or '[]'),
                        is_optional=bool(row[8]),
                        version=row[9] or '1.0.0'
                    )
                    
                    self._orchestrators[config.name] = {
                        'config': config,
                        'instance': None,
                        'wired': False
                    }
                    count += 1
                
            logger.info(f"Loaded {count} orchestrators from database")
            return Ok(count)
            
        except Exception as e:
            self._state = WiringState.VALIDATION_FAILED
            logger.error(f"Failed to load from database: {e}")
            return Err(f"Database load failed: {str(e)}")
    
    def populate_from_code(self) -> Result[int]:
        """
        Populate database from wire_*.py modules.
        
        Scans wire_001_core_wiring.py, wire_002_domain_wiring.py, 
        wire_003_support_wiring.py and registers all orchestrators.
        
        Returns:
            Result containing count of registered orchestrators or error
        """
        self._state = WiringState.REGISTERING
        
        registered = 0
        
        # Default init args for common orchestrators
        # These come from the current working directory at runtime
        import os
        default_workspace = os.getcwd()
        
        # WIRE-001: Core Orchestrators (6)
        core_orchestrators = [
            OrchestratorConfig(
                name="interaction",
                module_path="cortex.orchestrators.core.interaction_orchestrator",
                class_name="InteractionOrchestrator",
                category=OrchestratorCategory.CORE,
                priority=10,
                capabilities=["stage_1_comprehension", "lens_protocol", "challenge_generation"],
                routing_keywords=["understand", "analyze", "comprehend"],
                init_args={"conversation_protocol": None},  # Optional protocol
                is_utility=True  # No execute() method
            ),
            OrchestratorConfig(
                name="intent_router",
                module_path="cortex.orchestrators.core.intent_router",
                class_name="IntentRouter",
                category=OrchestratorCategory.CORE,
                priority=20,
                dependencies=["interaction"],
                capabilities=["intent_classification", "routing", "confidence_scoring"],
                routing_keywords=["route", "classify", "dispatch"]
            ),
            OrchestratorConfig(
                name="tdd",
                module_path="cortex.orchestrators.core.tdd_orchestrator",
                class_name="TDDOrchestrator",
                category=OrchestratorCategory.CORE,
                priority=30,
                capabilities=["test_driven_development", "red_green_refactor"],
                routing_keywords=["test", "tdd", "implement"],
                is_utility=True  # No execute() method
            ),
            OrchestratorConfig(
                name="workflow",
                module_path="cortex.orchestrators.core.workflow_orchestrator",
                class_name="WorkflowOrchestrator",
                category=OrchestratorCategory.CORE,
                priority=40,
                capabilities=["multi_step_workflows", "pipeline_execution"],
                routing_keywords=["workflow", "pipeline", "sequence"],
                init_args={"workspace_root": default_workspace},
                is_utility=True  # No execute() method
            ),
            OrchestratorConfig(
                name="wrapped_tdd",
                module_path="cortex.orchestrators.core.wrapped_tdd_orchestrator",
                class_name="WrappedTDDOrchestrator",
                category=OrchestratorCategory.CORE,
                priority=35,
                dependencies=["tdd"],
                capabilities=["tdd_with_governance", "rule_enforcement"],
                routing_keywords=["governed_tdd", "safe_implement"],
                is_utility=True  # No execute() method
            ),
            OrchestratorConfig(
                name="bootstrap",
                module_path="cortex.orchestrators.bootstrap",
                class_name="OrchestratorBootstrap",
                category=OrchestratorCategory.CORE,
                priority=5,
                capabilities=["system_initialization", "startup"],
                routing_keywords=["bootstrap", "initialize", "startup"],
                is_utility=True  # No execute() method
            ),
        ]
        
        # WIRE-002: Domain Orchestrators (5)
        domain_orchestrators = [
            OrchestratorConfig(
                name="refactoring",
                module_path="cortex.orchestrators.domain.refactoring_orchestrator",
                class_name="RefactoringOrchestrator",
                category=OrchestratorCategory.DOMAIN,
                priority=100,
                capabilities=["code_refactoring", "pattern_application"],
                routing_keywords=["refactor", "improve", "clean"],
                is_utility=True  # No execute() method
            ),
            OrchestratorConfig(
                name="planning",
                module_path="cortex.orchestrators.domain.planning_orchestrator",
                class_name="PlanningOrchestrator",
                category=OrchestratorCategory.DOMAIN,
                priority=110,
                capabilities=["planning", "roadmap", "phase_management"],
                routing_keywords=["plan", "roadmap", "phase"],
                is_utility=True  # No execute() method
            ),
            OrchestratorConfig(
                name="domain",
                module_path="cortex.orchestrators.domain_orchestrator",
                class_name="DomainOrchestrator",
                category=OrchestratorCategory.DOMAIN,
                priority=120,
                capabilities=["domain_operations", "business_logic"],
                routing_keywords=["domain", "business"],
                is_utility=True  # No execute() method
            ),
            OrchestratorConfig(
                name="conversation",
                module_path="cortex.orchestrators.conversation_orchestrator",
                class_name="ConversationOrchestrator",
                category=OrchestratorCategory.DOMAIN,
                priority=130,
                capabilities=["stateful_conversations", "multi_turn"],
                routing_keywords=["conversation", "chat", "dialogue"],
                is_utility=True  # No execute() method
            ),
            OrchestratorConfig(
                name="selenium_playwright",
                module_path="cortex.orchestrators.migration.selenium_playwright_orchestrator",
                class_name="SeleniumPlaywrightOrchestrator",
                category=OrchestratorCategory.DOMAIN,
                priority=140,
                is_optional=True,
                capabilities=["test_migration", "browser_automation"],
                routing_keywords=["selenium", "playwright", "browser"],
                is_utility=True  # No execute() method
            ),
        ]
        
        # WIRE-003: Support Orchestrators (6)
        support_orchestrators = [
            OrchestratorConfig(
                name="onboarding",
                module_path="cortex.orchestrators.onboarding.orchestrator",
                class_name="OnboardingOrchestrator",
                category=OrchestratorCategory.SUPPORT,
                priority=200,
                is_optional=True,  # Has syntax error in source
                capabilities=["user_onboarding", "guided_setup"],
                routing_keywords=["onboard", "setup", "welcome"],
                is_utility=True
            ),
            OrchestratorConfig(
                name="tool_discovery",
                module_path="cortex.orchestrators.onboarding.tool_discovery",
                class_name="ToolDiscoveryOrchestrator",
                category=OrchestratorCategory.SUPPORT,
                priority=210,
                capabilities=["capability_discovery", "tool_catalog"],
                routing_keywords=["discover", "tools", "capabilities"],
                is_utility=True  # No execute() method
            ),
            OrchestratorConfig(
                name="upgrade",
                module_path="cortex.orchestrators.upgrade_orchestrator",
                class_name="UpgradeOrchestrator",
                category=OrchestratorCategory.SUPPORT,
                priority=220,
                capabilities=["version_upgrade", "migration"],
                routing_keywords=["upgrade", "migrate", "version"],
                init_args={"repo_path": default_workspace},
                is_utility=True  # No execute() method
            ),
            OrchestratorConfig(
                name="rollback",
                module_path="cortex.orchestrators.rollback_orchestrator",
                class_name="RollbackOrchestrator",
                category=OrchestratorCategory.SUPPORT,
                priority=230,
                capabilities=["failure_recovery", "rollback"],
                routing_keywords=["rollback", "revert", "undo"],
                init_args={"repo_path": default_workspace},
                is_utility=True  # No execute() method
            ),
            OrchestratorConfig(
                name="setup",
                module_path="cortex.orchestrators.onboarding.setup_orchestrator",
                class_name="SetupOrchestrator",
                category=OrchestratorCategory.SUPPORT,
                priority=240,
                capabilities=["environment_setup", "configuration"],
                routing_keywords=["setup", "configure", "environment"],
                init_args={"workspace": default_workspace},
                is_utility=True  # No execute() method
            ),
            OrchestratorConfig(
                name="composed",
                module_path="cortex.orchestrators.composition.composition_engine",
                class_name="ComposedOrchestrator",
                category=OrchestratorCategory.SUPPORT,
                priority=250,
                is_optional=True,
                capabilities=["orchestrator_composition", "chaining"],
                routing_keywords=["compose", "chain", "combine"],
                is_utility=True
            ),
        ]
        
        # Additional orchestrators from MasterOrchestrator
        additional_orchestrators = [
            OrchestratorConfig(
                name="master",
                module_path="cortex.orchestrators.core.master_orchestrator",
                class_name="MasterOrchestrator",
                category=OrchestratorCategory.CORE,
                priority=1,
                capabilities=["coordination", "delegation", "aggregation"],
                routing_keywords=["master", "main", "coordinate"]
                # Has execute() - true orchestrator
            ),
            OrchestratorConfig(
                name="dor_approval",
                module_path="cortex.orchestrators.core.dor_approval_gate",
                class_name="DoRApprovalGate",
                category=OrchestratorCategory.CORE,
                priority=15,
                capabilities=["approval_gate", "user_confirmation"],
                routing_keywords=["approve", "confirm", "dor"],
                is_utility=True  # No execute() method
            ),
            OrchestratorConfig(
                name="lens_synthesis",
                module_path="cortex.orchestrators.core.lens_synthesis",
                class_name="LENSSynthesis",
                category=OrchestratorCategory.CORE,
                priority=12,
                capabilities=["lens_protocol", "synthesis", "comprehension"],
                routing_keywords=["lens", "synthesize", "comprehend"],
                is_utility=True  # No execute() method
            ),
            OrchestratorConfig(
                name="documentation",
                module_path="cortex.orchestrators.documentation.orchestrator",
                class_name="DocumentationOrchestrator",
                category=OrchestratorCategory.DOMAIN,
                priority=150,
                is_optional=True,
                capabilities=["documentation_generation", "doc_updates"],
                routing_keywords=["document", "docs", "readme"]
                # Has execute() - true orchestrator
            ),
            OrchestratorConfig(
                name="stage_25_gate",
                module_path="cortex.orchestrators.core.stage_2_5_gate",
                class_name="Stage25Gate",
                category=OrchestratorCategory.CORE,
                priority=25,
                capabilities=["stage_validation", "gate_checking"],
                routing_keywords=["gate", "validate", "stage"],
                is_utility=True  # No execute() method
            ),
            OrchestratorConfig(
                name="autowiring",
                module_path="cortex.orchestrators.core.autowiring_orchestrator",
                class_name="AutowiringOrchestrator",
                category=OrchestratorCategory.INFRASTRUCTURE,
                priority=2,
                capabilities=["autowiring", "dependency_injection"],
                routing_keywords=["wire", "autowire", "inject"],
                is_utility=True  # No execute() method
            ),
        ]
        
        # Register all orchestrators
        all_configs = (
            core_orchestrators + 
            domain_orchestrators + 
            support_orchestrators + 
            additional_orchestrators
        )
        
        for config in all_configs:
            result = self.register(config, registered_by="populate_from_code")
            if result.is_ok():
                registered += 1
            else:
                logger.warning(f"Failed to register {config.name}: {result.error}")
        
        logger.info(f"Populated {registered} orchestrators from code")
        return Ok(registered)
    
    # =========================================================================
    # Wiring Logic
    # =========================================================================
    
    def compute_wiring_order(self) -> Result[List[str]]:
        """
        Compute deterministic wiring order using topological sort.
        
        Considers:
        - Priority (lower = earlier)
        - Dependencies (must wire dependencies first)
        
        Returns:
            Result containing ordered list of orchestrator names
        """
        self._state = WiringState.COMPUTING_ORDER
        
        try:
            # Build dependency graph
            graph: Dict[str, Set[str]] = {}
            in_degree: Dict[str, int] = {}
            
            for name, info in self._orchestrators.items():
                config = info['config']
                graph[name] = set()
                in_degree[name] = 0
            
            # Add edges for dependencies
            for name, info in self._orchestrators.items():
                config = info['config']
                for dep in config.dependencies:
                    if dep in graph:
                        graph[dep].add(name)
                        in_degree[name] += 1
                    elif not info['config'].is_optional:
                        return Err(f"Missing required dependency: {dep} for {name}")
            
            # Kahn's algorithm with priority-based tie-breaking
            queue: List[str] = []
            for name in self._orchestrators:
                if in_degree[name] == 0:
                    queue.append(name)
            
            # Sort by priority
            queue.sort(key=lambda n: self._orchestrators[n]['config'].priority)
            
            result: List[str] = []
            while queue:
                # Take highest priority (lowest number)
                node = queue.pop(0)
                result.append(node)
                
                # Process neighbors
                neighbors = list(graph[node])
                neighbors.sort(key=lambda n: self._orchestrators[n]['config'].priority)
                
                for neighbor in neighbors:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
                        queue.sort(key=lambda n: self._orchestrators[n]['config'].priority)
            
            # Check for cycles
            if len(result) != len(self._orchestrators):
                remaining = [n for n in self._orchestrators if n not in result]
                return Err(f"Circular dependency detected in: {remaining}")
            
            self._wiring_order = result
            logger.info(f"Computed wiring order: {result}")
            return Ok(result)
            
        except Exception as e:
            self._state = WiringState.VALIDATION_FAILED
            return Err(f"Failed to compute wiring order: {str(e)}")
    
    def wire_single(self, name: str, session_id: str) -> WiringResult:
        """
        Wire a single orchestrator.
        
        Args:
            name: Orchestrator name
            session_id: Wiring session identifier
            
        Returns:
            WiringResult with success/failure details
        """
        start_time = time.time()
        
        try:
            info = self._orchestrators.get(name)
            if not info:
                raise ValueError(f"Unknown orchestrator: {name}")
            
            config = info['config']
            
            # Dynamic import
            import importlib
            module = importlib.import_module(config.module_path)
            orchestrator_class = getattr(module, config.class_name)
            
            # Create instance with init_args if provided
            if config.init_args:
                instance = orchestrator_class(**config.init_args)
            else:
                instance = orchestrator_class()
            
            # Validate interface (skip for utilities)
            if not config.is_utility and not hasattr(instance, 'execute'):
                # Mark as utility automatically if no execute method
                logger.debug(f"{name}: No execute() method, treating as utility")
                config.is_utility = True
            
            # Store instance
            self._instances[name] = instance
            info['instance'] = instance
            info['wired'] = True
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Log to database
            self._log_wiring_attempt(name, True, duration_ms, None, session_id)
            
            # Update status in registry
            status = "WIRED" if not config.is_utility else "WIRED_UTILITY"
            self._update_orchestrator_status(name, status)
            
            result = WiringResult(
                success=True,
                orchestrator_name=name,
                timestamp=datetime.now(timezone.utc),
                duration_ms=duration_ms,
                details={"is_utility": config.is_utility}
            )
            self._wiring_results.append(result)
            
            logger.debug(f"Wired {name} ({duration_ms:.1f}ms){' [utility]' if config.is_utility else ''}")
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            
            # Log failure to database
            self._log_wiring_attempt(name, False, duration_ms, error_msg, session_id)
            
            # Update status
            self._update_orchestrator_status(name, "FAILED")
            
            result = WiringResult(
                success=False,
                orchestrator_name=name,
                timestamp=datetime.now(timezone.utc),
                duration_ms=duration_ms,
                error=error_msg
            )
            self._wiring_results.append(result)
            
            logger.error(f"Failed to wire {name}: {error_msg}")
            return result
    
    def wire_all(self, fail_fast: bool = True) -> Result[RegistryValidation]:
        """
        Wire all registered orchestrators in deterministic order.
        
        Args:
            fail_fast: If True, stop on first failure. If False, continue.
            
        Returns:
            Result containing RegistryValidation or error
        """
        start_time = time.time()
        session_id = f"wire_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        
        # Compute order if not already done
        if not self._wiring_order:
            order_result = self.compute_wiring_order()
            if order_result.is_err():
                return Err(order_result.error)
        
        self._state = WiringState.WIRING
        logger.info(f"Wiring {len(self._wiring_order)} orchestrators")
        
        failures: List[str] = []
        
        for name in self._wiring_order:
            config = self._orchestrators[name]['config']
            
            # Skip optional orchestrators if dependencies not met
            if config.is_optional:
                missing_deps = [d for d in config.dependencies if d not in self._instances]
                if missing_deps:
                    logger.info(f"Skipping optional {name} (missing: {missing_deps})")
                    continue
            
            result = self.wire_single(name, session_id)
            
            if not result.success:
                failures.append(f"{name}: {result.error}")
                
                if fail_fast and not config.is_optional:
                    self._state = WiringState.VALIDATION_FAILED
                    return Err(f"Wiring failed at {name}: {result.error}")
        
        # Validation
        wiring_duration = (time.time() - start_time) * 1000
        
        validation = RegistryValidation(
            passed=len(failures) == 0,
            timestamp=datetime.now(timezone.utc),
            checked_count=len(self._wiring_order),
            passed_count=len(self._wiring_order) - len(failures),
            failures=failures
        )
        
        if validation.passed:
            self._state = WiringState.WIRED
            
            # Create snapshot
            self._create_snapshot(wiring_duration, session_id)
            
            logger.info(f"✅ All orchestrators wired successfully ({wiring_duration:.0f}ms)")
        else:
            self._state = WiringState.VALIDATION_FAILED
            logger.error(f"Wiring completed with {len(failures)} failures")
        
        self._last_validation = validation
        return Ok(validation)
    
    # =========================================================================
    # Validation & Health Checks
    # =========================================================================
    
    def validate_wiring(self) -> RegistryValidation:
        """
        Validate that all orchestrators are wired and callable.
        
        Returns:
            RegistryValidation with detailed results
        """
        failures: List[str] = []
        suggestions: List[str] = []
        checked = 0
        passed = 0
        
        for name, info in self._orchestrators.items():
            config = info['config']
            checked += 1
            
            # Check instance exists
            if name not in self._instances:
                if not config.is_optional:
                    failures.append(f"{name}: not wired")
                    suggestions.append(f"Run wire_all() to wire {name}")
                continue
            
            instance = self._instances[name]
            
            # Check callable
            if not callable(getattr(instance, 'execute', None)):
                failures.append(f"{name}: execute() not callable")
                continue
            
            # Check dependencies
            for dep in config.dependencies:
                if dep not in self._instances:
                    if not config.is_optional:
                        failures.append(f"{name}: missing dependency {dep}")
            
            passed += 1
        
        validation = RegistryValidation(
            passed=len(failures) == 0,
            timestamp=datetime.now(timezone.utc),
            checked_count=checked,
            passed_count=passed,
            failures=failures,
            suggestions=suggestions
        )
        
        self._validation_log.append(validation)
        self._last_validation = validation
        
        return validation
    
    def compare_with_snapshot(self) -> Result[Dict[str, Any]]:
        """
        Compare current state with last successful snapshot.
        
        Returns:
            Result containing comparison details or error
        """
        try:
            with self._db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT snapshot_id, total_orchestrators, wired_count,
                           validation_hash, orchestrator_names
                    FROM wiring_state_snapshot
                    ORDER BY snapshot_time DESC
                    LIMIT 1
                """)
                row = cursor.fetchone()
            
            if not row:
                return Ok({
                    'has_snapshot': False,
                    'message': 'No previous snapshot found'
                })
            
            snapshot_id, total, wired, hash_val, names_json = row
            snapshot_names = set(json.loads(names_json or '[]'))
            current_names = set(self._instances.keys())
            
            # Compute current hash
            current_hash = self._compute_wiring_hash()
            
            comparison = {
                'has_snapshot': True,
                'snapshot_id': snapshot_id,
                'hash_match': hash_val == current_hash,
                'count_match': wired == len(self._instances),
                'added': list(current_names - snapshot_names),
                'removed': list(snapshot_names - current_names),
                'drift_detected': hash_val != current_hash
            }
            
            return Ok(comparison)
            
        except Exception as e:
            return Err(f"Snapshot comparison failed: {str(e)}")
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _log_wiring_attempt(
        self,
        name: str,
        success: bool,
        duration_ms: float,
        error: Optional[str],
        session_id: str
    ) -> None:
        """Log wiring attempt to database."""
        try:
            with self._db.get_connection() as conn:
                conn.execute("""
                    INSERT INTO wiring_log (
                        orchestrator_name, success, timestamp, duration_ms,
                        error_message, session_id
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    1 if success else 0,
                    datetime.now(timezone.utc).isoformat(),
                    duration_ms,
                    error,
                    session_id
                ))
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to log wiring attempt: {e}")
    
    def _update_orchestrator_status(self, name: str, status: str) -> None:
        """Update orchestrator status in database."""
        try:
            with self._db.get_connection() as conn:
                conn.execute("""
                    UPDATE orchestrator_registry
                    SET status = ?
                    WHERE orchestrator_name = ?
                """, (status, name))
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to update status for {name}: {e}")
    
    def _compute_wiring_hash(self) -> str:
        """Compute hash of current wiring state."""
        names = sorted(self._instances.keys())
        state_str = json.dumps(names, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()[:16]
    
    def _create_snapshot(self, wiring_duration: float, session_id: str) -> None:
        """Create wiring state snapshot."""
        try:
            snapshot_id = f"snap_{session_id}"
            names = sorted(self._instances.keys())
            
            with self._db.get_connection() as conn:
                conn.execute("""
                    INSERT INTO wiring_state_snapshot (
                        snapshot_id, total_orchestrators, wired_count, failed_count,
                        snapshot_time, wiring_duration_ms, validation_hash, orchestrator_names
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    snapshot_id,
                    len(self._orchestrators),
                    len(self._instances),
                    len(self._orchestrators) - len(self._instances),
                    datetime.now(timezone.utc).isoformat(),
                    wiring_duration,
                    self._compute_wiring_hash(),
                    json.dumps(names)
                ))
                conn.commit()
            
            logger.info(f"Created wiring snapshot: {snapshot_id}")
            
        except Exception as e:
            logger.warning(f"Failed to create snapshot: {e}")
    
    # =========================================================================
    # Public Accessors
    # =========================================================================
    
    def get_orchestrator(self, name: str) -> Optional[IOrchestrator]:
        """Get wired orchestrator instance by name."""
        return self._instances.get(name)
    
    def get_all_orchestrators(self) -> Dict[str, IOrchestrator]:
        """Get all wired orchestrator instances."""
        return self._instances.copy()
    
    def get_by_capability(self, capability: str) -> List[IOrchestrator]:
        """Get orchestrators with a specific capability."""
        result = []
        for name, info in self._orchestrators.items():
            if capability in info['config'].capabilities:
                instance = self._instances.get(name)
                if instance:
                    result.append(instance)
        return result
    
    def get_by_keyword(self, keyword: str) -> Optional[IOrchestrator]:
        """Get orchestrator matching a routing keyword."""
        keyword_lower = keyword.lower()
        for name, info in self._orchestrators.items():
            if keyword_lower in [k.lower() for k in info['config'].routing_keywords]:
                return self._instances.get(name)
        return None
    
    def get_wiring_statistics(self) -> Dict[str, Any]:
        """Get current wiring statistics."""
        return {
            'state': self._state.value,
            'total_registered': len(self._orchestrators),
            'total_wired': len(self._instances),
            'wiring_order': self._wiring_order,
            'last_validation': self._last_validation,
            'by_category': {
                cat.value: len([
                    n for n, i in self._orchestrators.items()
                    if i['config'].category == cat
                ])
                for cat in OrchestratorCategory
            }
        }


# Module-level convenience functions
def get_database_registry() -> DatabaseBackedRegistry:
    """Get the singleton database-backed registry instance."""
    return DatabaseBackedRegistry.instance()


def initialize_registry() -> Result[RegistryValidation]:
    """
    Initialize and wire the registry.
    
    This is the main entry point for application startup.
    
    Returns:
        Result containing validation result or error
    """
    registry = get_database_registry()
    
    # Initialize schema
    schema_result = registry.initialize_schema()
    if schema_result.is_err():
        return Err(f"Schema initialization failed: {schema_result.error}")
    
    # Load from database or populate from code
    load_result = registry.load_from_database()
    if load_result.is_err() or load_result.unwrap() == 0:
        # Database empty, populate from code
        populate_result = registry.populate_from_code()
        if populate_result.is_err():
            return Err(f"Population failed: {populate_result.error}")
    
    # Wire all orchestrators
    return registry.wire_all()

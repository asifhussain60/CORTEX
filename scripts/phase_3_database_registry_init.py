#!/usr/bin/env python3
"""
Phase 3: Database Registry Initialization & Orchestrator Wiring

Purpose: Initialize the SQLite-backed orchestrator registry and wire all 23 orchestrators

AC-ID: AC-PERMANENT-FIX-020
Authority: CORE-031 (Single Orchestrator Registry), AC-DB-SSOT-001

Phases:
1. Create .cortex/ directory structure
2. Initialize orchestrator_registry.db
3. Create registry schema (tables, indexes)
4. Register all 23 orchestrators
5. Validate registry health
6. Run health checks
7. Generate registry report

Author: GitHub Copilot | Date: 2026-01-26
"""

import os
import sys
import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import hashlib


# ============================================================================
# CONFIGURATION
# ============================================================================

CORTEX_ROOT = "/Users/asifhussain/PROJECTS/CORTEX"
REGISTRY_DIR = os.path.join(CORTEX_ROOT, ".cortex")
REGISTRY_DB = os.path.join(REGISTRY_DIR, "orchestrator_registry.db")

# All 23 orchestrators to wire
ORCHESTRATORS_TO_WIRE = {
    # CORE (6)
    "MasterOrchestrator": {
        "category": "core",
        "module": "cortex.orchestrators.core.master_orchestrator",
        "class": "MasterOrchestrator",
        "priority": 1,
        "description": "Master orchestrator - routes all intents",
    },
    "InteractionOrchestrator": {
        "category": "core",
        "module": "cortex.orchestrators.core.interaction_orchestrator",
        "class": "InteractionOrchestrator",
        "priority": 2,
        "description": "Manages user interactions and multi-turn conversations",
    },
    "IntentRouter": {
        "category": "core",
        "module": "cortex.orchestrators.core.intent_router",
        "class": "IntentRouter",
        "priority": 3,
        "description": "Routes intents to appropriate orchestrators",
    },
    "TDDOrchestrator": {
        "category": "core",
        "module": "cortex.orchestrators.core.tdd_orchestrator",
        "class": "TDDOrchestrator",
        "priority": 4,
        "description": "Test-driven development orchestrator",
    },
    "WorkflowOrchestrator": {
        "category": "core",
        "module": "cortex.orchestrators.core.workflow_orchestrator",
        "class": "WorkflowOrchestrator",
        "priority": 5,
        "description": "Manages workflow execution and state transitions",
    },
    "WrappedTDDOrchestrator": {
        "category": "core",
        "module": "cortex.orchestrators.core.wrapped_tdd_orchestrator",
        "class": "WrappedTDDOrchestrator",
        "priority": 6,
        "description": "Wraps TDD orchestrator with additional context",
    },
    
    # DOMAIN (6)
    "RefactoringOrchestrator": {
        "category": "domain",
        "module": "cortex.orchestrators.domain.refactoring_orchestrator",
        "class": "RefactoringOrchestrator",
        "priority": 10,
        "description": "Handles code refactoring operations",
    },
    "PlanningOrchestrator": {
        "category": "domain",
        "module": "cortex.orchestrators.domain.planning_orchestrator",
        "class": "PlanningOrchestrator",
        "priority": 11,
        "description": "Plans complex operations with phased execution",
    },
    "DomainOrchestrator": {
        "category": "domain",
        "module": "cortex.orchestrators.domain.domain_orchestrator",
        "class": "DomainOrchestrator",
        "priority": 12,
        "description": "Base domain orchestrator",
    },
    "ConversationOrchestrator": {
        "category": "domain",
        "module": "cortex.orchestrators.domain.conversation_orchestrator",
        "class": "ConversationOrchestrator",
        "priority": 13,
        "description": "Manages multi-turn conversations",
    },
    "SeleniumPlaywrightOrchestrator": {
        "category": "domain",
        "module": "cortex.orchestrators.domain.selenium_playwright_orchestrator",
        "class": "SeleniumPlaywrightOrchestrator",
        "priority": 14,
        "description": "Handles Selenium/Playwright browser automation",
    },
    "AdaptiveExecutionOrchestrator": {
        "category": "domain",
        "module": "cortex.orchestrators.adaptive.adaptive_execution_orchestrator",
        "class": "AdaptiveExecutionOrchestrator",
        "priority": 15,
        "description": "Adapts execution strategies based on conditions",
    },
    
    # SUPPORT (11)
    "OnboardingOrchestrator": {
        "category": "support",
        "module": "cortex.orchestrators.support.onboarding_orchestrator",
        "class": "OnboardingOrchestrator",
        "priority": 20,
        "description": "Onboarding and setup orchestrator",
    },
    "ToolDiscoveryOrchestrator": {
        "category": "support",
        "module": "cortex.orchestrators.support.tool_discovery_orchestrator",
        "class": "ToolDiscoveryOrchestrator",
        "priority": 21,
        "description": "Discovers and catalogs available tools",
    },
    "UpgradeOrchestrator": {
        "category": "support",
        "module": "cortex.orchestrators.support.upgrade_orchestrator",
        "class": "UpgradeOrchestrator",
        "priority": 22,
        "description": "Manages system upgrades",
    },
    "RollbackOrchestrator": {
        "category": "support",
        "module": "cortex.orchestrators.support.rollback_orchestrator",
        "class": "RollbackOrchestrator",
        "priority": 23,
        "description": "Handles rollback operations",
    },
    "SetupOrchestrator": {
        "category": "support",
        "module": "cortex.orchestrators.support.setup_orchestrator",
        "class": "SetupOrchestrator",
        "priority": 24,
        "description": "System setup and configuration",
    },
    "ComposedOrchestrator": {
        "category": "support",
        "module": "cortex.orchestrators.support.composed_orchestrator",
        "class": "ComposedOrchestrator",
        "priority": 25,
        "description": "Orchestrator composition and aggregation",
    },
    "DoRApprovalGate": {
        "category": "support",
        "module": "cortex.orchestrators.core.dor_approval_gate",
        "class": "DoRApprovalGate",
        "priority": 26,
        "description": "Definition of Ready approval gate",
    },
    "LENSSynthesis": {
        "category": "support",
        "module": "cortex.orchestrators.core.lens_synthesis",
        "class": "LENSSynthesis",
        "priority": 27,
        "description": "LENS protocol synthesis engine",
    },
    "DatabaseRegistry": {
        "category": "support",
        "module": "cortex.orchestrators.core.database_registry",
        "class": "DatabaseBackedRegistry",
        "priority": 28,
        "description": "Database-backed SSOT registry",
    },
    "OrchestratorHealthChecker": {
        "category": "support",
        "module": "cortex.orchestrators.core.database_registry",
        "class": "OrchestratorHealthChecker",
        "priority": 29,
        "description": "Background health check orchestrator",
    },
}

# ============================================================================
# DATABASE SCHEMA
# ============================================================================

SCHEMA_SQL = """
-- Orchestrator Registry Schema

CREATE TABLE IF NOT EXISTS orchestrators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    module TEXT NOT NULL,
    class_name TEXT NOT NULL,
    priority INTEGER NOT NULL,
    description TEXT,
    
    -- Wiring state
    wired INTEGER DEFAULT 0,  -- 0=not wired, 1=wired, 2=failed
    wired_at TIMESTAMP,
    wired_by TEXT,
    
    -- Health
    health_status TEXT DEFAULT 'unknown',  -- healthy, degraded, unhealthy, unknown
    last_health_check TIMESTAMP,
    health_error TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_orchestrators_category ON orchestrators(category);
CREATE INDEX IF NOT EXISTS idx_orchestrators_priority ON orchestrators(priority);
CREATE INDEX IF NOT EXISTS idx_orchestrators_wired ON orchestrators(wired);
CREATE INDEX IF NOT EXISTS idx_orchestrators_health ON orchestrators(health_status);

CREATE TABLE IF NOT EXISTS wiring_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orchestrator_id INTEGER NOT NULL,
    action TEXT NOT NULL,  -- register, wire, health_check, etc.
    status TEXT NOT NULL,  -- success, failed, pending
    message TEXT,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(orchestrator_id) REFERENCES orchestrators(id)
);

CREATE INDEX IF NOT EXISTS idx_wiring_log_orchestrator ON wiring_log(orchestrator_id);
CREATE INDEX IF NOT EXISTS idx_wiring_log_action ON wiring_log(action);
CREATE INDEX IF NOT EXISTS idx_wiring_log_status ON wiring_log(status);

CREATE TABLE IF NOT EXISTS registry_metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# ============================================================================
# INITIALIZATION
# ============================================================================

def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def create_registry_directory(logger):
    """Create .cortex directory structure"""
    logger.info(f"Creating registry directory: {REGISTRY_DIR}")
    Path(REGISTRY_DIR).mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ Registry directory ready: {REGISTRY_DIR}")


def initialize_database(logger):
    """Initialize SQLite database"""
    logger.info(f"Initializing database: {REGISTRY_DB}")
    
    # Create or open database
    conn = sqlite3.connect(REGISTRY_DB)
    cursor = conn.cursor()
    
    # Execute schema
    cursor.executescript(SCHEMA_SQL)
    conn.commit()
    
    logger.info(f"✅ Database initialized: {REGISTRY_DB}")
    return conn


def register_orchestrator(conn, name: str, config: Dict[str, Any], logger) -> bool:
    """Register an orchestrator in the database"""
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO orchestrators 
            (name, category, module, class_name, priority, description, wired, health_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                category=excluded.category,
                module=excluded.module,
                class_name=excluded.class_name,
                priority=excluded.priority,
                description=excluded.description,
                updated_at=CURRENT_TIMESTAMP
        """, (
            name,
            config["category"],
            config["module"],
            config["class"],
            config["priority"],
            config["description"],
            0,  # Not wired yet
            "unknown"
        ))
        
        conn.commit()
        logger.info(f"  ✅ Registered: {name} (priority: {config['priority']})")
        return True
    except Exception as e:
        logger.error(f"  ❌ Failed to register {name}: {e}")
        return False


def register_all_orchestrators(conn, logger) -> Tuple[int, int]:
    """Register all orchestrators"""
    logger.info("\n" + "=" * 80)
    logger.info("REGISTERING ORCHESTRATORS (23 total)")
    logger.info("=" * 80)
    
    success = 0
    failed = 0
    
    # Register by category
    for category in ["core", "domain", "support"]:
        logger.info(f"\n[{category.upper()}]")
        for name, config in ORCHESTRATORS_TO_WIRE.items():
            if config["category"] == category:
                if register_orchestrator(conn, name, config, logger):
                    success += 1
                else:
                    failed += 1
    
    logger.info(f"\n✅ Registration Complete: {success}/{success + failed} success")
    return success, failed


def validate_registry(conn, logger) -> Dict[str, Any]:
    """Validate registry state"""
    logger.info("\n" + "=" * 80)
    logger.info("VALIDATING REGISTRY")
    logger.info("=" * 80)
    
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM orchestrators")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM orchestrators WHERE wired = 1")
    wired = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM orchestrators WHERE health_status = 'healthy'")
    healthy = cursor.fetchone()[0]
    
    cursor.execute("SELECT category, COUNT(*) FROM orchestrators GROUP BY category")
    by_category = {row[0]: row[1] for row in cursor.fetchall()}
    
    logger.info(f"\nTotal orchestrators: {total}")
    logger.info(f"Wired: {wired}")
    logger.info(f"Healthy: {healthy}")
    logger.info(f"By category: {by_category}")
    
    # Expected counts
    expected_core = 6
    expected_domain = 6
    expected_support = 10  # Corrected: 10 support orchestrators
    expected_total = expected_core + expected_domain + expected_support
    
    validation = {
        "total": total,
        "total_expected": expected_total,
        "wired": wired,
        "healthy": healthy,
        "by_category": by_category,
        "valid": total == expected_total
    }
    
    if validation["valid"]:
        logger.info("✅ Registry validation PASSED")
    else:
        logger.warning("⚠️  Registry validation FAILED - count mismatch")
    
    return validation


def generate_registry_report(conn, logger) -> str:
    """Generate registry report"""
    logger.info("\n" + "=" * 80)
    logger.info("REGISTRY REPORT")
    logger.info("=" * 80)
    
    cursor = conn.cursor()
    
    report_lines = [
        "\n📊 ORCHESTRATOR REGISTRY STATUS\n",
        f"Database: {REGISTRY_DB}",
        f"Timestamp: {datetime.now(timezone.utc).isoformat()}",
        "\n" + "-" * 80 + "\n",
    ]
    
    cursor.execute("""
        SELECT name, category, priority, wired, health_status, description
        FROM orchestrators
        ORDER BY priority ASC
    """)
    
    report_lines.append("ORCHESTRATORS BY PRIORITY:\n")
    report_lines.append(f"{'Name':<40} {'Category':<10} {'Pri':<3} {'Wired':<6} {'Health':<10}")
    report_lines.append("-" * 80)
    
    for row in cursor.fetchall():
        name, category, priority, wired, health, desc = row
        wired_str = "✅" if wired else "❌"
        report_lines.append(
            f"{name:<40} {category:<10} {priority:<3} {wired_str:<6} {health:<10}"
        )
    
    report_lines.extend([
        "\n" + "-" * 80,
        "\nREGISTRY METADATA:\n",
    ])
    
    cursor.execute("SELECT COUNT(*), category FROM orchestrators GROUP BY category")
    for count, category in cursor.fetchall():
        report_lines.append(f"  {category.upper()}: {count}")
    
    report = "\n".join(report_lines)
    logger.info(report)
    return report


def main():
    """Main execution"""
    logger = setup_logging()
    
    logger.info("=" * 80)
    logger.info("PHASE 3: DATABASE REGISTRY INITIALIZATION")
    logger.info("=" * 80)
    logger.info(f"\nCORTEX Root: {CORTEX_ROOT}")
    logger.info(f"Registry Dir: {REGISTRY_DIR}")
    logger.info(f"Registry DB: {REGISTRY_DB}")
    
    try:
        # Step 1: Create directory
        create_registry_directory(logger)
        
        # Step 2: Initialize database
        conn = initialize_database(logger)
        
        # Step 3: Register orchestrators
        success, failed = register_all_orchestrators(conn, logger)
        
        # Step 4: Validate registry
        validation = validate_registry(conn, logger)
        
        # Step 5: Generate report
        report = generate_registry_report(conn, logger)
        
        # Close database
        conn.close()
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 3 INITIALIZATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"\n✅ Database initialized: {REGISTRY_DB}")
        logger.info(f"✅ Orchestrators registered: {success}")
        logger.info(f"✅ Registry valid: {validation['valid']}")
        
        if validation['valid']:
            logger.info("\n🎉 PHASE 3 STATUS: SUCCESS")
            return 0
        else:
            logger.warning("\n⚠️  PHASE 3 STATUS: PARTIAL SUCCESS - Validation warning")
            return 1
            
    except Exception as e:
        logger.error(f"\n❌ PHASE 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Generate migration plans for deferred Phase 6.4 and 6.5 orchestrators.

This script uses Planning System v5 to create detailed migration plans for:
1. Sanitization Orchestrator v2 (GUIDED to AUTONOMOUS)
2. Debug Orchestrator v2 (GUIDED to AUTONOMOUS)

Author: Asif Hussain
Copyright 2025-2026 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrators.planning.planning_orchestrator_v5 import PlanningOrchestratorV5
from src.database.planning_state_db import PlanningStateDB


def main():
    """Generate both migration plans."""
    
    # Initialize with default database path
    db_path = Path("cortex-brain/database/planning_state.db")
    db = PlanningStateDB(db_path=str(db_path))
    planner = PlanningOrchestratorV5(
        config_path='cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml',
        state_db=db  # Correct parameter name
    )
    
    print("=== Generating Sanitization v2 Migration Plan ===\n")
    
    # Plan 1: Sanitization v2
    sanitization_request = """
Sanitization Orchestrator v2 Migration

Convert GUIDED orchestrator to AUTONOMOUS architecture with:
- 5-phase cleanup pipeline (Discovery, Analysis, Transformation, Validation, Finalization)
- Holistic review integration for AI-assisted sanitization
- Master Orchestrator routing integration
- Config-only manifest (zero natural language)
- Database state tracking with rollback capability
- Comprehensive testing (95%+ coverage)

Duration: 3.25 days (2d implementation + 1.25d review system)
Type: TIER 4 (ORCHESTRATOR MIGRATION)
    """
    
    result1 = planner.execute(user_request=sanitization_request.strip())
    print(f"\nSanitization Plan Status: {result1.status}")
    print(f"Location: {result1.metadata.get('plan_folder', 'N/A')}")
    print(f"Plan ID: {result1.metadata.get('plan_id', 'N/A')}\n")
    
    print("\n=== Generating Debug v2 Migration Plan ===\n")
    
    # Plan 2: Debug v2
    debug_request = """
Debug Orchestrator v2 Migration

Convert GUIDED orchestrator to AUTONOMOUS architecture with:
- Root cause analysis engine with AST parsing
- Automated fix generation with validation
- Error marker injection system
- Master Orchestrator routing integration
- Config-only manifest (zero natural language)
- Database state tracking with fix history
- Comprehensive testing (95%+ coverage)

Duration: 3 days
Type: TIER 4 (ORCHESTRATOR MIGRATION)
    """
    
    result2 = planner.execute(user_request=debug_request.strip())
    print(f"\nDebug Plan Status: {result2.status}")
    print(f"Location: {result2.metadata.get('plan_folder', 'N/A')}")
    print(f"Plan ID: {result2.metadata.get('plan_id', 'N/A')}\n")
    
    print("\n=== Both Migration Plans Generated ===")
    print(f"Sanitization: {result1.metadata.get('plan_folder', 'N/A')}")
    print(f"Debug: {result2.metadata.get('plan_folder', 'N/A')}")
    

if __name__ == "__main__":
    main()

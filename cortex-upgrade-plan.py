#!/usr/bin/env python3
"""
CORTEX Plan Upgrade CLI

Quick wrapper for upgrading legacy plans to CORTEX-5.0 standards.

Usage:
    python cortex-upgrade-plan.py <plan-path> [--archive] [--output <dir>]

Examples:
    # Analyze and upgrade a plan
    python cortex-upgrade-plan.py cortex-brain/documents/planning/active/old-plan/
    
    # Upgrade and auto-archive original
    python cortex-upgrade-plan.py old-plan.md --archive
    
    # Specify custom output location
    python cortex-upgrade-plan.py old-plan/ --output cortex-brain/documents/planning/active/new-plan-v5/

Author: Asif Hussain
Version: 1.0.0
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrators.plan_upgrade.plan_upgrade_orchestrator import PlanUpgradeOrchestrator, main

if __name__ == "__main__":
    sys.exit(main())

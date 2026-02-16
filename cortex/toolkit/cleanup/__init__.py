"""
CORTEX Toolkit - Cleanup Module

Consolidates cleanup and vacuum automation scripts.

**Consolidated Scripts:**
- .cortex/run_vacuum.py
- scripts/vacuum-runner.py

**Authority:** Phase 90 S-90-05
"""

from cortex.toolkit.cleanup.vacuum import VacuumAutomation

__all__ = ["VacuumAutomation"]

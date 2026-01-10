"""
CORTEX 6.0 Governance Infrastructure Layer

Implements AC-GOV-001 through AC-GOV-013:
- 4-Category Governance System (CORE, Company, Knowledge, Business)
- SKULL → CORE Rules Migration (19 rules)
- Unified Instruction Set generation
- Conflict detection and resolution
- Rule caching for performance (<50ms merge)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from src.orchestrators.core.governance_merger import (
    GovernanceMerger,
    GovernanceRule,
    GovernanceConflict,
    UnifiedInstructionSet,
    Precedence,
    Severity,
)

__all__ = [
    'GovernanceMerger',
    'GovernanceRule',
    'GovernanceConflict',
    'UnifiedInstructionSet',
    'Precedence',
    'Severity',
]

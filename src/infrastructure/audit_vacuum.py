"""
CORTEX 6.0 Audit Vacuum - Automatic Cleanup

Implements AC-AUDIT-005: Automatic vacuum removes old logs.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from src.infrastructure.enhanced_audit_logger import AuditVacuum

# Re-export for tests
__all__ = ['AuditVacuum']

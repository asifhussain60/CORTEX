"""
CORTEX 6.0 Audit Configuration

Implements AC-AUDIT-006: Retention policy configuration.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from src.orchestrators.audit_logger import load_retention_policy

# Re-export for tests
__all__ = ['load_retention_policy']

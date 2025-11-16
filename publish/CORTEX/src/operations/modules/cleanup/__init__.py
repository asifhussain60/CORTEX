"""
Cleanup module for CORTEX operations.

Provides comprehensive workspace cleanup functionality including:
- Backup file management with GitHub archival
- Root folder organization
- File reorganization
- MD file consolidation
- Bloat detection
- Automatic optimization integration

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from src.operations.modules.cleanup.cleanup_orchestrator import CleanupOrchestrator, CleanupMetrics

__all__ = ['CleanupOrchestrator', 'CleanupMetrics']

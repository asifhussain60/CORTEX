"""
Vacuum Orchestrator v2 Test Suite

Comprehensive unit tests for all vacuum components:
- vacuum_orchestrator_v2.py - Main orchestrator (6-phase workflow)
- filesystem_engine.py - Transactional operations
- duplicate_detector.py - Three-phase progressive hashing
- safety_validator.py - 5-level risk classification
- orphan_detector.py - AST-based orphan detection

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

__all__ = [
    'test_vacuum_orchestrator_v2',
    'test_filesystem_engine',
    'test_duplicate_detector',
    'test_safety_validator',
    'test_orphan_detector'
]

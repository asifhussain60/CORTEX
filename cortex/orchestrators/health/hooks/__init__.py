"""Health Hooks Package

Pre-commit and pre-push hooks for health enforcement.

Author: CORTEX Framework
Phase: PHASE-95 S4
"""

from .pre_commit_health import check_staged_files, main as pre_commit_main
from .pre_push_health import check_health_score, main as pre_push_main

__all__ = [
    "check_staged_files",
    "pre_commit_main",
    "check_health_score",
    "pre_push_main",
]

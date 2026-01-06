"""
CORTEX Entry Point Package.

Fast command handling and main request processing.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from .fast_commands import FastCommandHandler, is_fast_command
from .cortex_entry import CortexEntry

__all__ = [
    'FastCommandHandler',
    'is_fast_command',
    'CortexEntry',
]

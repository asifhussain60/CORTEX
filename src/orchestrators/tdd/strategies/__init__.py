"""
TDD Phase Strategies

Strategy pattern implementations for RED, GREEN, REFACTOR, and DOCUMENT phases.

Version: 4.0.0
Updated: 2025-12-30 - Added DOCUMENT phase (Phase 4 Security Enhancement)
"""

from .red_phase_strategy import REDPhaseStrategy
from .green_phase_strategy import GREENPhaseStrategy
from .refactor_phase_strategy import REFACTORPhaseStrategy
from .document_phase_strategy import DOCUMENTPhaseStrategy

__all__ = [
    'REDPhaseStrategy',
    'GREENPhaseStrategy',
    'REFACTORPhaseStrategy',
    'DOCUMENTPhaseStrategy'
]

"""
Intent Router Module - Advanced intent classification and routing

AC-PHX-007: Holistic Intent Router Intelligence
- AC-PHX-007-01: Intent Classification Framework
- AC-PHX-007-02: Multi-modal Intent Processing
- AC-PHX-007-03: Intent Disambiguation System
- AC-PHX-007-04: Confidence Scoring Mechanism
- AC-PHX-007-05: Intent Context Preservation
- AC-PHX-007-06: Routing Decision Logic
- AC-PHX-007-07: Fallback Strategies
- AC-PHX-007-08: Intent Learning Loop
- AC-PHX-007-09: Performance Metrics
- AC-PHX-007-10: Integration with PHASE-06
- AC-PHX-007-11: Testing Framework
- AC-PHX-007-12: Documentation Updates
- AC-PHX-007-13: Observability Instrumentation
- AC-PHX-007-14: Edge Case Handling

CORTEX Governance Rules Applied:
- CORE-008: TDD (tests first, RED → GREEN)
- CORE-011: Type hints mandatory on all functions
- CORE-012: Google-style docstrings on all public methods
- CORE-013: Specific exception handling (no bare except)
- CORE-027: Audit trail logging (AC_START → AC_EXECUTE → AC_COMPLETE)

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from src.intent_router.classifier import IntentClassifier

__all__ = ["IntentClassifier"]

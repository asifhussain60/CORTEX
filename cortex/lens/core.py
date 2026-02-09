"""LENS Core Module - DEPRECATED (Phase 65 S6)

This module was a Phase 56-A backward compatibility stub.
No production consumers depend on it.

**DEPRECATED in Phase 65 S6**: Use cortex.lens.orchestrator.LENSOrchestrator
or cortex.brain.engines.base_intelligence_engine.BaseIntelligenceEngine instead.

AC_START: Phase 56-A S1 backward compatibility stub (DEPRECATED)
AC_DEPRECATION: Phase 65 S6-T3 (2026-02-09)
"""

import warnings
from typing import Dict, Any, Optional


__deprecated__ = True  # Marker for test detection


# Issue deprecation warning on import
warnings.warn(
    "cortex.lens.core is deprecated as of Phase 65 S6. "
    "Use cortex.lens.orchestrator.LENSOrchestrator or "
    "cortex.brain.engines.base_intelligence_engine.BaseIntelligenceEngine instead.",
    DeprecationWarning,
    stacklevel=2
)


class LENSAnalyzer:
    """
    LENS Analyzer interface for backward compatibility
    
    **DEPRECATED**: Use LENSOrchestrator instead.
    """
    
    def __init__(self):
        """Initialize LENS Analyzer"""
        warnings.warn(
            "LENSAnalyzer is deprecated. Use LENSOrchestrator instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.name = "LENSAnalyzer"
        self.version = "1.0.0-deprecated"
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code using available intelligence engines
        
        **DEPRECATED**: Use LENSOrchestrator.analyze_file() instead.
        
        Args:
            context: Analysis context
        
        Returns:
            Analysis results
        """
        return {
            "status": "analyzed",
            "source": "LENSAnalyzer-deprecated"
        }
    
    def can_delegate_to(self, engine_name: str) -> bool:
        """
        Check if we can delegate to an intelligence engine
        
        Args:
            engine_name: Engine identifier
        
        Returns:
            True if engine is available
        """
        # Relationship engine is the pilot migration
        return engine_name in ["RelationshipTraversal", "RelationshipTraversalEngine"]



# AC_COMPLETE: Phase 56-A S1 backward compatibility stub ✅

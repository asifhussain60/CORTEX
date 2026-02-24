"""cortex.intelligence.cross_cutting — Cross-Cutting Intelligence Layer (Phase 65)."""

from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
    IntelligenceMatrixBuilder,
    IntelligenceMatrix,
    IntelligenceCapability,
    CortexCapability,
    MatrixCell,
    IntelligenceScore,
    CapabilityDimension,
    INTELLIGENCE_CAPABILITIES,
    CORTEX_CAPABILITIES,
)

# Re-export alias for test imports
CortexIntelligenceMatrix = IntelligenceMatrix

__all__ = [
    "IntelligenceMatrixBuilder",
    "IntelligenceMatrix",
    "CortexIntelligenceMatrix",
    "IntelligenceCapability",
    "CortexCapability",
    "MatrixCell",
    "IntelligenceScore",
    "CapabilityDimension",
    "INTELLIGENCE_CAPABILITIES",
    "CORTEX_CAPABILITIES",
]

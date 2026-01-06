"""
CORTEX Planning System - Package Initialization

Purpose: Planning System core package exports
Version: 5.0.0

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

# Planning v5 orchestrator
try:
    from .planning_orchestrator_v5 import PlanningOrchestratorV5
    __all__ = ['PlanningOrchestratorV5']
except ImportError:
    __all__ = []

# New Phase 2+ modules
try:
    from .acceptance_validator import AcceptanceCriteriaValidator, PhaseNotReadyError, PhaseIncompleteError
    __all__.extend(['AcceptanceCriteriaValidator', 'PhaseNotReadyError', 'PhaseIncompleteError'])
except ImportError:
    pass

try:
    from .ast_scanner import ASTScanner
    __all__.append('ASTScanner')
except ImportError:
    pass

try:
    from .duplicate_detector import PlanningDuplicateDetector
    __all__.append('PlanningDuplicateDetector')
except ImportError:
    pass

try:
    from .governance_integrator import GovernanceIntegrator, GovernanceValidation
    __all__.extend(['GovernanceIntegrator', 'GovernanceValidation'])
except ImportError:
    pass

try:
    from .knowledge_graph_query import KnowledgeGraphQuery, KnowledgeContext
    __all__.extend(['KnowledgeGraphQuery', 'KnowledgeContext'])
except ImportError:
    pass

try:
    from .orphan_detector import PlanningOrphanDetector
    __all__.append('PlanningOrphanDetector')
except ImportError:
    pass

__version__ = "5.0.0"

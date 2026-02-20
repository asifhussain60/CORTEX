"""
CORTEX Intelligence Layer.

Unified intelligence package consolidating:
- cortex_intelligence: Tier-based adaptive intelligence (perception, reasoning, action)
- cortex_lens: Multi-language code analysis and LENS architecture
- cortex.intelligence: Deep computation engines (AST, git, relationships, patterns)

Authority: Phase 3 - Package Consolidation
"""

__license__ = 'Proprietary'
__description__ = 'Unified Intelligence and Analysis Layer'

# Core intelligence engines
try:
    from cortex.intelligence.base import (
        AnalysisContext,
        AnalysisResult,
        BaseIntelligenceEngine,
    )
    __all__ = [
        "BaseIntelligenceEngine",
        "AnalysisContext",
        "AnalysisResult",
    ]
except ImportError:
    pass

# Tier-based intelligence (formerly cortex_intelligence)
def __getattr__(name: str):
    """Lazy load intelligence tier modules."""
    if name in ('tier0', 'tier1', 'tier2', 'state', 'releases', 'memory', 'perception', 'reasoning', 'action', 'domain', 'domain_brain', 'governance', 'observability', 'onboarded_repos', 'quality', 'audit', 'intelligence', 'wiring'):
        try:
            import importlib
            return importlib.import_module(f'cortex.intelligence.{name}')
        except ImportError:
            pass
    raise AttributeError(f"module 'cortex.intelligence' has no attribute '{name}'")

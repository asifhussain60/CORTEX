"""
Deprecation Warning System for Phase 2 Tier 2

This module provides centralized deprecation warning infrastructure for
the orchestrator migration phase.

FEATURES:
- Centralized deprecation registry
- Warnings emitted on import (configurable)
- Stacklevel-aware for proper source tracking
- Metric collection for monitoring
- Silent mode support for testing

USAGE:
    from cortex.orchestrators.support.deprecation_warnings import warn_deprecated_orchestrator
    
    warn_deprecated_orchestrator(
        old_name="LENSOrchestrator",
        new_name="UnifiedAnalysisOrchestrator",
        use_adapter="analyze_file_via_unified"
    )
"""

import warnings
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


# ============================================================================
# Deprecation Registry
# ============================================================================

@dataclass
class DeprecatedOrchestrator:
    """Metadata for a deprecated orchestrator."""
    
    old_name: str
    new_name: str
    sunset_date: str = "2026-03-31"
    adapter_function: Optional[str] = None
    migration_guide_url: Optional[str] = None
    severity: str = "WARNING"  # INFO, WARNING, CRITICAL
    

# Registry of all deprecated orchestrators (Phase 2 Tier 1 audit results)
DEPRECATED_ORCHESTRATORS: Dict[str, DeprecatedOrchestrator] = {
    "LENSOrchestrator": DeprecatedOrchestrator(
        old_name="LENSOrchestrator",
        new_name="UnifiedAnalysisOrchestrator",
        sunset_date="2026-03-31",
        adapter_function="cortex.orchestrators.support.api_compatibility.analyze_file_via_unified",
        severity="WARNING",
    ),
    "ToolDiscoveryOrchestrator": DeprecatedOrchestrator(
        old_name="ToolDiscoveryOrchestrator",
        new_name="UnifiedAnalysisOrchestrator",
        sunset_date="2026-03-31",
        adapter_function="cortex.orchestrators.support.api_compatibility",
        severity="WARNING",
    ),
    "RepositoryOnboardingOrchestrator": DeprecatedOrchestrator(
        old_name="RepositoryOnboardingOrchestrator",
        new_name="UnifiedOnboardingOrchestrator",
        sunset_date="2026-03-31",
        adapter_function="cortex.orchestrators.support.api_compatibility.onboard_repository_via_unified",
        severity="WARNING",
    ),
    "SetupOrchestrator": DeprecatedOrchestrator(
        old_name="SetupOrchestrator",
        new_name="UnifiedOnboardingOrchestrator",
        sunset_date="2026-03-31",
        adapter_function="cortex.orchestrators.support.api_compatibility.onboard_repository_via_unified",
        severity="WARNING",
    ),
    "RecommendationEngine": DeprecatedOrchestrator(
        old_name="RecommendationEngine",
        new_name="UnifiedQualityAssuranceOrchestrator",
        sunset_date="2026-03-31",
        adapter_function="cortex.orchestrators.support.api_compatibility.check_recommendation_via_unified",
        severity="WARNING",
    ),
    "ChallengeEngine": DeprecatedOrchestrator(
        old_name="ChallengeEngine",
        new_name="UnifiedQualityAssuranceOrchestrator",
        sunset_date="2026-03-31",
        adapter_function="cortex.orchestrators.support.orchestrator_factories.get_unified_quality_orchestrator",
        severity="WARNING",
    ),
    "MetaAuditOrchestrator": DeprecatedOrchestrator(
        old_name="MetaAuditOrchestrator",
        new_name="UnifiedQualityAssuranceOrchestrator",
        sunset_date="2026-03-31",
        adapter_function="cortex.orchestrators.support.orchestrator_factories.get_unified_quality_orchestrator",
        severity="CRITICAL",
    ),
    "EducationalOrchestrator": DeprecatedOrchestrator(
        old_name="EducationalOrchestrator",
        new_name="UnifiedDiscoveryOrchestrator",
        sunset_date="2026-03-31",
        adapter_function="cortex.orchestrators.support.orchestrator_factories.get_unified_discovery_orchestrator",
        severity="INFO",
    ),
    "BusinessLanguageOrchestrator": DeprecatedOrchestrator(
        old_name="BusinessLanguageOrchestrator",
        new_name="UnifiedDiscoveryOrchestrator",
        sunset_date="2026-03-31",
        adapter_function="cortex.orchestrators.support.orchestrator_factories.get_unified_discovery_orchestrator",
        severity="INFO",
    ),
}


# ============================================================================
# Warning Infrastructure
# ============================================================================

class DeprecationWarningCollector:
    """Collects and tracks deprecation warnings for monitoring."""
    
    def __init__(self):
        """Initialize collector."""
        self.warnings: List[Dict] = []
        self.counts: Dict[str, int] = {}
        self.enabled = True
    
    def record_warning(self, old_name: str, location: str):
        """Record a deprecation warning."""
        if not self.enabled:
            return
        
        warning_record = {
            "timestamp": datetime.now().isoformat(),
            "old_orchestrator": old_name,
            "location": location,
        }
        self.warnings.append(warning_record)
        self.counts[old_name] = self.counts.get(old_name, 0) + 1
        
        logger.info(f"Deprecation warning: {old_name} at {location}")
    
    def get_summary(self) -> Dict:
        """Get summary of collected warnings."""
        return {
            "total_warnings": len(self.warnings),
            "unique_orchestrators": len(self.counts),
            "counts": self.counts,
            "enabled": self.enabled,
        }
    
    def disable(self):
        """Disable warning collection (for testing)."""
        self.enabled = False
    
    def enable(self):
        """Enable warning collection."""
        self.enabled = True
    
    def reset(self):
        """Reset warning collector."""
        self.warnings = []
        self.counts = {}


# Global collector instance
_collector = DeprecationWarningCollector()


# ============================================================================
# Public Warning Functions
# ============================================================================

def warn_deprecated_orchestrator(
    old_name: str,
    new_name: Optional[str] = None,
    use_adapter: Optional[str] = None,
    stacklevel: int = 2,
) -> None:
    """
    Emit a deprecation warning for a deprecated orchestrator.
    
    Args:
        old_name: Name of deprecated orchestrator
        new_name: Name of replacement orchestrator (if not in registry)
        use_adapter: Adapter function to use (if not in registry)
        stacklevel: Stack level for warning source tracking
    
    Example:
        >>> warn_deprecated_orchestrator("LENSOrchestrator")
        DeprecationWarning: LENSOrchestrator is deprecated...
    """
    # Look up in registry if available
    if old_name in DEPRECATED_ORCHESTRATORS:
        meta = DEPRECATED_ORCHESTRATORS[old_name]
        new_name = new_name or meta.new_name
        use_adapter = use_adapter or meta.adapter_function
        severity = meta.severity
        sunset_date = meta.sunset_date
    else:
        severity = "WARNING"
        sunset_date = "2026-03-31"
    
    # Build warning message
    message = (
        f"{old_name} is deprecated and will be removed on {sunset_date}. "
        f"Use {new_name} instead. "
    )
    
    if use_adapter:
        message += f"Adapter available: {use_adapter}. "
    
    message += (
        "See: docs/TRACK-4-PHASE-2-MIGRATION-GUIDE.md for migration details."
    )
    
    # Emit warning
    if severity == "CRITICAL":
        warnings.warn(message, DeprecationWarning, stacklevel=stacklevel + 1)
    else:
        warnings.warn(message, DeprecationWarning, stacklevel=stacklevel + 1)
    
    # Collect metric (get caller location from stack)
    import inspect
    frame = inspect.currentframe()
    if frame and frame.f_back:
        caller_file = frame.f_back.f_code.co_filename
        caller_line = frame.f_back.f_lineno
        location = f"{caller_file}:{caller_line}"
    else:
        location = "unknown"
    
    _collector.record_warning(old_name, location)


def get_deprecation_summary() -> Dict:
    """Get summary of all deprecation warnings emitted."""
    return _collector.get_summary()


def disable_deprecation_warnings():
    """Disable deprecation warning collection (for testing)."""
    _collector.disable()


def enable_deprecation_warnings():
    """Enable deprecation warning collection."""
    _collector.enable()


def reset_deprecation_warnings():
    """Reset deprecation warning collector."""
    _collector.reset()


__all__ = [
    "warn_deprecated_orchestrator",
    "get_deprecation_summary",
    "disable_deprecation_warnings",
    "enable_deprecation_warnings",
    "reset_deprecation_warnings",
    "DEPRECATED_ORCHESTRATORS",
]

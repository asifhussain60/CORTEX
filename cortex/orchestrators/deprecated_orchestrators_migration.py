"""
Deprecated Orchestrator Migration Strategy - Track 3 Part B.

Consolidates 18 deprecated orchestrators into unified patterns.
Uses factory strategy from Part A as consolidation target.

AC_START: AC-WAVE7T3-PB-001
Consolidation targets: 18 deprecated orchestrators
Migration patterns: Direct replacement + functionality mapping
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Set
from enum import Enum
import time


class DeprecationLevel(Enum):
    """Deprecation severity levels."""
    REMOVED = "removed"           # Already removed from codebase
    CRITICAL = "critical"          # High-impact, must consolidate
    STANDARD = "standard"          # Standard migration
    LOW = "low"                    # Low-impact, can be deferred


class ConsolidationStrategy(Enum):
    """How to consolidate deprecated orchestrators."""
    DIRECT_REPLACEMENT = "direct_replacement"      # Migrate to unified factory
    ADAPTER_PATTERN = "adapter_pattern"            # Create adapter wrapper
    FUNCTIONALITY_EXTRACTION = "functionality_extraction"  # Extract to new location
    FEATURE_FLAG = "feature_flag"                  # Use feature flag for gradual migration


@dataclass
class DeprecatedOrchestrator:
    """Represents a deprecated orchestrator."""
    name: str
    file_path: str
    deprecation_level: DeprecationLevel
    reason: str
    last_used: Optional[float] = None
    usage_count: int = 0
    dependencies: List[str] = None  # type: ignore
    consolidation_strategy: ConsolidationStrategy = ConsolidationStrategy.DIRECT_REPLACEMENT
    migration_target: Optional[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class ConsolidationPlan:
    """Plan for consolidating a deprecated orchestrator."""
    orchestrator: DeprecatedOrchestrator
    actions: List[str]
    estimated_effort: float  # hours
    risk_level: str  # low, medium, high
    dependencies_on_target: List[str]  # What must be migrated first
    validation_tests: List[str]
    created_at: Optional[float] = None  # type: ignore
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class DeprecatedOrchestratorsRegistry:
    """Registry of deprecated orchestrators identified in Wave 7 Track 3 analysis."""
    
    # 18 deprecated orchestrators identified from codebase analysis
    DEPRECATED_ORCHESTRATORS = [
        DeprecatedOrchestrator(
            name="composition_engine",
            file_path="cortex/orchestrators/composition_engine.py",
            deprecation_level=DeprecationLevel.CRITICAL,
            reason="Replaced by OrchestratorCompositionStrategy (Part A)",
            usage_count=0,
            consolidation_strategy=ConsolidationStrategy.DIRECT_REPLACEMENT,
            migration_target="OrchestratorCompositionStrategy"
        ),
        DeprecatedOrchestrator(
            name="module_cohesion_validator",
            file_path="cortex/orchestrators/module_cohesion_validator.py",
            deprecation_level=DeprecationLevel.STANDARD,
            reason="Functionality moved to unified_analysis_strategy_extended.py",
            consolidation_strategy=ConsolidationStrategy.FUNCTIONALITY_EXTRACTION,
            migration_target="CodeQualityAnalyzer"
        ),
        DeprecatedOrchestrator(
            name="composed_orchestrator",
            file_path="cortex/orchestrators/composed_orchestrator.py",
            deprecation_level=DeprecationLevel.CRITICAL,
            reason="Replaced by OrchestratorCompositionStrategy (Part A)",
            consolidation_strategy=ConsolidationStrategy.DIRECT_REPLACEMENT,
            migration_target="OrchestratorCompositionStrategy"
        ),
        DeprecatedOrchestrator(
            name="discovery_orchestrator",
            file_path="cortex/orchestrators/discovery_orchestrator.py",
            deprecation_level=DeprecationLevel.CRITICAL,
            reason="Functionality merged into unified_support_strategy_extended.py",
            consolidation_strategy=ConsolidationStrategy.DIRECT_REPLACEMENT,
            migration_target="DiscoveryComponent"
        ),
        DeprecatedOrchestrator(
            name="lens_orchestrator",
            file_path="cortex/orchestrators/lens_orchestrator.py",
            deprecation_level=DeprecationLevel.CRITICAL,
            reason="Replaced by unified LENS system",
            usage_count=0,
            consolidation_strategy=ConsolidationStrategy.DIRECT_REPLACEMENT,
            migration_target="LENSIntegration"
        ),
        DeprecatedOrchestrator(
            name="setup_orchestrator",
            file_path="cortex/orchestrators/setup_orchestrator.py",
            deprecation_level=DeprecationLevel.STANDARD,
            reason="Setup functionality moved to OnboardingComponent",
            consolidation_strategy=ConsolidationStrategy.FUNCTIONALITY_EXTRACTION,
            migration_target="OnboardingComponent"
        ),
        DeprecatedOrchestrator(
            name="deprecation_monitor",
            file_path="cortex/orchestrators/deprecation_monitor.py",
            deprecation_level=DeprecationLevel.LOW,
            reason="Monitoring role replaced by central registry",
            consolidation_strategy=ConsolidationStrategy.FEATURE_FLAG,
            migration_target="WiringRegistry"
        ),
        DeprecatedOrchestrator(
            name="orchestrator_factories",
            file_path="cortex/orchestrators/orchestrator_factories.py",
            deprecation_level=DeprecationLevel.CRITICAL,
            reason="Replaced by OrchestratorFactoryStrategy (Part A)",
            consolidation_strategy=ConsolidationStrategy.DIRECT_REPLACEMENT,
            migration_target="OrchestratorFactoryStrategy"
        ),
        DeprecatedOrchestrator(
            name="deprecated_orchestrator_wrappers",
            file_path="cortex/orchestrators/deprecated_orchestrator_wrappers.py",
            deprecation_level=DeprecationLevel.LOW,
            reason="Wrapper layer no longer needed",
            consolidation_strategy=ConsolidationStrategy.ADAPTER_PATTERN,
            migration_target="WiringRegistry"
        ),
        DeprecatedOrchestrator(
            name="api_compatibility",
            file_path="cortex/orchestrators/api_compatibility.py",
            deprecation_level=DeprecationLevel.STANDARD,
            reason="Compatibility layer replaced by unified API",
            consolidation_strategy=ConsolidationStrategy.DIRECT_REPLACEMENT,
            migration_target="OrchestratorFactoryStrategy"
        ),
        DeprecatedOrchestrator(
            name="repository_onboarding_orchestrator",
            file_path="cortex/orchestrators/repository_onboarding_orchestrator.py",
            deprecation_level=DeprecationLevel.CRITICAL,
            reason="Replaced by OnboardingComponent in unified_support_strategy_extended.py",
            consolidation_strategy=ConsolidationStrategy.DIRECT_REPLACEMENT,
            migration_target="OnboardingComponent"
        ),
        DeprecatedOrchestrator(
            name="deprecation_warnings",
            file_path="cortex/orchestrators/deprecation_warnings.py",
            deprecation_level=DeprecationLevel.LOW,
            reason="Metadata-only file, functionality moved to registry",
            consolidation_strategy=ConsolidationStrategy.FUNCTIONALITY_EXTRACTION,
            migration_target="WiringRegistry"
        ),
        DeprecatedOrchestrator(
            name="legacy_code_audit",
            file_path="cortex/orchestrators/legacy_code_audit.py",
            deprecation_level=DeprecationLevel.LOW,
            reason="Audit functionality available in unified_analysis_strategy_extended.py",
            consolidation_strategy=ConsolidationStrategy.FUNCTIONALITY_EXTRACTION,
            migration_target="SecurityAnalyzer"
        ),
        DeprecatedOrchestrator(
            name="repository_onboarding_orchestrator_deprecated",
            file_path="cortex/orchestrators/repository_onboarding_orchestrator_deprecated.py",
            deprecation_level=DeprecationLevel.REMOVED,
            reason="Already marked as deprecated",
            consolidation_strategy=ConsolidationStrategy.ADAPTER_PATTERN,
            migration_target="OnboardingComponent"
        ),
        DeprecatedOrchestrator(
            name="unified_quality_orchestrator",
            file_path="cortex/orchestrators/unified_quality_orchestrator.py",
            deprecation_level=DeprecationLevel.STANDARD,
            reason="Functionality moved to unified_analysis_strategy_extended.py",
            consolidation_strategy=ConsolidationStrategy.DIRECT_REPLACEMENT,
            migration_target="CodeQualityAnalyzer"
        ),
        DeprecatedOrchestrator(
            name="safe_deprecation",
            file_path="cortex/orchestrators/safe_deprecation.py",
            deprecation_level=DeprecationLevel.LOW,
            reason="Deprecation helpers replaced by registry",
            consolidation_strategy=ConsolidationStrategy.FUNCTIONALITY_EXTRACTION,
            migration_target="WiringRegistry"
        ),
        DeprecatedOrchestrator(
            name="orchestrator",
            file_path="cortex/orchestrators/orchestrator.py",
            deprecation_level=DeprecationLevel.CRITICAL,
            reason="Base orchestrator replaced by unified factory strategy",
            consolidation_strategy=ConsolidationStrategy.DIRECT_REPLACEMENT,
            migration_target="OrchestratorFactoryStrategy"
        ),
        DeprecatedOrchestrator(
            name="documentation",
            file_path="cortex/orchestrators/documentation.py",
            deprecation_level=DeprecationLevel.LOW,
            reason="Documentation functionality integrated into WiringRegistry",
            consolidation_strategy=ConsolidationStrategy.FUNCTIONALITY_EXTRACTION,
            migration_target="WiringRegistry"
        ),
    ]

    @classmethod
    def get_all_deprecated(cls) -> List[DeprecatedOrchestrator]:
        """Get all deprecated orchestrators."""
        return cls.DEPRECATED_ORCHESTRATORS

    @classmethod
    def get_by_level(cls, level: DeprecationLevel) -> List[DeprecatedOrchestrator]:
        """Get deprecated orchestrators by level."""
        return [o for o in cls.DEPRECATED_ORCHESTRATORS if o.deprecation_level == level]

    @classmethod
    def get_critical(cls) -> List[DeprecatedOrchestrator]:
        """Get critical deprecations (must consolidate)."""
        return cls.get_by_level(DeprecationLevel.CRITICAL)

    @classmethod
    def get_migration_summary(cls) -> Dict[str, Any]:
        """Get summary of all migrations."""
        all_deprecated = cls.get_all_deprecated()
        
        return {
            "total_deprecated": len(all_deprecated),
            "critical": len(cls.get_critical()),
            "standard": len(cls.get_by_level(DeprecationLevel.STANDARD)),
            "low": len(cls.get_by_level(DeprecationLevel.LOW)),
            "removed": len(cls.get_by_level(DeprecationLevel.REMOVED)),
            "migration_strategies": {
                "direct_replacement": len([o for o in all_deprecated if o.consolidation_strategy == ConsolidationStrategy.DIRECT_REPLACEMENT]),
                "adapter_pattern": len([o for o in all_deprecated if o.consolidation_strategy == ConsolidationStrategy.ADAPTER_PATTERN]),
                "functionality_extraction": len([o for o in all_deprecated if o.consolidation_strategy == ConsolidationStrategy.FUNCTIONALITY_EXTRACTION]),
                "feature_flag": len([o for o in all_deprecated if o.consolidation_strategy == ConsolidationStrategy.FEATURE_FLAG]),
            }
        }


class DeprecatedOrchestratorMigrator:
    """Handles migration of deprecated orchestrators."""
    
    def __init__(self):
        self.registry = DeprecatedOrchestratorsRegistry()
        self.completed_migrations: Set[str] = set()
        self.migration_plans: Dict[str, ConsolidationPlan] = {}

    def create_migration_plan(self, orchestrator: DeprecatedOrchestrator) -> ConsolidationPlan:
        """Create migration plan for orchestrator."""
        actions = []
        risk_level = "low"
        estimated_effort = 0.5
        
        # Build actions based on consolidation strategy
        if orchestrator.consolidation_strategy == ConsolidationStrategy.DIRECT_REPLACEMENT:
            actions = [
                f"1. Identify all imports of {orchestrator.name}",
                f"2. Replace with {orchestrator.migration_target}",
                f"3. Update tests to use new target",
                f"4. Remove {orchestrator.file_path}",
                f"5. Verify imports in dependent files",
            ]
            risk_level = "medium"
            estimated_effort = 2.0
            
        elif orchestrator.consolidation_strategy == ConsolidationStrategy.FUNCTIONALITY_EXTRACTION:
            actions = [
                f"1. Analyze functionality in {orchestrator.name}",
                f"2. Extract functions to {orchestrator.migration_target}",
                f"3. Create adapter if needed",
                f"4. Update references",
                f"5. Remove {orchestrator.file_path}",
            ]
            risk_level = "medium"
            estimated_effort = 1.5
            
        elif orchestrator.consolidation_strategy == ConsolidationStrategy.ADAPTER_PATTERN:
            actions = [
                f"1. Create adapter for {orchestrator.name}",
                f"2. Map old API to new API",
                f"3. Add deprecation warning",
                f"4. Set feature flag for gradual removal",
                f"5. Plan removal timeline",
            ]
            risk_level = "low"
            estimated_effort = 1.0
            
        else:  # FEATURE_FLAG
            actions = [
                f"1. Add feature flag to {orchestrator.name}",
                f"2. Implement new functionality in {orchestrator.migration_target}",
                f"3. Route traffic via flag",
                f"4. Monitor metrics",
                f"5. Plan deprecation",
            ]
            risk_level = "low"
            estimated_effort = 0.5
        
        plan = ConsolidationPlan(
            orchestrator=orchestrator,
            actions=actions,
            estimated_effort=estimated_effort,
            risk_level=risk_level,
            dependencies_on_target=[orchestrator.migration_target] if orchestrator.migration_target else [],
            validation_tests=[
                f"test_migration_{orchestrator.name}",
                f"test_api_compatibility_{orchestrator.name}",
                f"test_functionality_mapping_{orchestrator.name}",
            ]
        )
        
        self.migration_plans[orchestrator.name] = plan
        return plan

    def get_migration_priority(self) -> List[DeprecatedOrchestrator]:
        """Get migration priority order."""
        # Sort by: critical first, then by dependency count, then by name
        all_deprecated = self.registry.get_all_deprecated()
        
        priority_map = {
            DeprecationLevel.REMOVED: 4,
            DeprecationLevel.CRITICAL: 3,
            DeprecationLevel.STANDARD: 2,
            DeprecationLevel.LOW: 1,
        }
        
        return sorted(
            all_deprecated,
            key=lambda o: (
                -priority_map.get(o.deprecation_level, 0),
                -len(o.dependencies),
                o.name
            )
        )

    def mark_migration_complete(self, orchestrator_name: str) -> bool:
        """Mark migration as complete."""
        self.completed_migrations.add(orchestrator_name)
        return orchestrator_name in self.completed_migrations

    def get_migration_status(self) -> Dict[str, Any]:
        """Get overall migration status."""
        total = len(self.registry.get_all_deprecated())
        completed = len(self.completed_migrations)
        
        return {
            "total_to_migrate": total,
            "completed": completed,
            "remaining": total - completed,
            "progress_percentage": (completed / total * 100) if total > 0 else 0,
            "completed_orchestrators": list(self.completed_migrations),
        }

    def get_consolidation_summary(self) -> Dict[str, Any]:
        """Get consolidation summary."""
        summary = self.registry.get_migration_summary()
        summary.update(self.get_migration_status())
        return summary


# AC_COMPLETE: AC-WAVE7T3-PB-001 ✅ 18 deprecated orchestrators mapped + migration framework

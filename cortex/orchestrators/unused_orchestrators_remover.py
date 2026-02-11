"""
Unused Orchestrator Consolidation Strategy - Track 3 Part C.

Identifies and consolidates orchestrators with zero usage/imports.
Removes dead code patterns from Wave 7 Track 3 analysis.

AC_START: AC-WAVE7T3-PC-001
Consolidation targets: 5+ unused orchestrators
Dead code removal: Pattern-based identification
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import Enum
import time


class UnusedOrchestrator(Enum):
    """Identified unused orchestrators from codebase."""
    CONVERSATION_CONTINUER = "conversation_continuer"
    CONTINUATION_CHAIN = "continuation_chain"
    ORCHESTRATOR_COMPOSITE = "orchestrator_composite"
    STATE_RECOVERY = "state_recovery"
    ORCHESTRATOR_BOOTSTRAP = "orchestrator_bootstrap"


class RemovalRisk(Enum):
    """Risk level for removing unused orchestrator."""
    SAFE = "safe"                  # No imports, safe to remove
    LOW = "low"                    # Some references but can be migrated
    MEDIUM = "medium"              # Potential external dependencies
    HIGH = "high"                  # Unknown dependencies, keep


@dataclass
class UnusedOrchestratorInfo:
    """Information about an unused orchestrator."""
    name: str
    file_path: str
    removal_risk: RemovalRisk
    reason: str
    import_count: int = 0
    reference_count: int = 0
    last_modified: Optional[float] = None
    last_used: Optional[float] = None
    
    def is_truly_unused(self) -> bool:
        """Check if orchestrator is truly unused."""
        return self.import_count == 0 and self.reference_count == 0


@dataclass
class RemovalPlan:
    """Plan for removing unused orchestrator."""
    orchestrator_info: UnusedOrchestratorInfo
    actions: List[str] = field(default_factory=list)
    estimated_effort: float = 0.25  # hours
    validation_steps: List[str] = field(default_factory=list)
    created_at: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
        
        # Build default actions
        if not self.actions:
            self.actions = [
                f"1. Verify no imports of {self.orchestrator_info.name}",
                f"2. Check git history for last usage",
                f"3. Confirm no external dependencies",
                f"4. Remove {self.orchestrator_info.file_path}",
                f"5. Update any documentation",
            ]
        
        # Build default validation
        if not self.validation_steps:
            self.validation_steps = [
                "Run test suite to confirm no breakage",
                f"Grep codebase for '{self.orchestrator_info.name}' references",
                "Verify CI/CD passes",
            ]


class UnusedOrchestratorsRegistry:
    """Registry of identified unused orchestrators."""
    
    UNUSED_ORCHESTRATORS = {
        UnusedOrchestrator.CONVERSATION_CONTINUER: UnusedOrchestratorInfo(
            name="conversation_continuer",
            file_path="cortex/orchestrators/conversation_continuer.py",
            removal_risk=RemovalRisk.SAFE,
            reason="Zero imports, conversation continuation moved to unified framework",
            import_count=0,
            reference_count=0
        ),
        UnusedOrchestrator.CONTINUATION_CHAIN: UnusedOrchestratorInfo(
            name="continuation_chain",
            file_path="cortex/orchestrators/continuation_chain.py",
            removal_risk=RemovalRisk.SAFE,
            reason="Dead code, continuation logic integrated elsewhere",
            import_count=0,
            reference_count=0
        ),
        UnusedOrchestrator.ORCHESTRATOR_COMPOSITE: UnusedOrchestratorInfo(
            name="orchestrator_composite",
            file_path="cortex/orchestrators/orchestrator_composite.py",
            removal_risk=RemovalRisk.SAFE,
            reason="Replaced by OrchestratorCompositionStrategy (Track 3 Part A)",
            import_count=0,
            reference_count=0
        ),
        UnusedOrchestrator.STATE_RECOVERY: UnusedOrchestratorInfo(
            name="state_recovery",
            file_path="cortex/orchestrators/state_recovery.py",
            removal_risk=RemovalRisk.LOW,
            reason="State recovery functionality moved to unified system",
            import_count=0,
            reference_count=0
        ),
        UnusedOrchestrator.ORCHESTRATOR_BOOTSTRAP: UnusedOrchestratorInfo(
            name="orchestrator_bootstrap",
            file_path="cortex/orchestrators/orchestrator_bootstrap.py",
            removal_risk=RemovalRisk.SAFE,
            reason="Bootstrap logic integrated into factory strategy",
            import_count=0,
            reference_count=0
        ),
    }

    @classmethod
    def get_all_unused(cls) -> List[UnusedOrchestratorInfo]:
        """Get all unused orchestrators."""
        return list(cls.UNUSED_ORCHESTRATORS.values())

    @classmethod
    def get_safe_to_remove(cls) -> List[UnusedOrchestratorInfo]:
        """Get orchestrators safe to remove (no dependencies)."""
        return [o for o in cls.get_all_unused() if o.removal_risk == RemovalRisk.SAFE]

    @classmethod
    def get_by_risk(cls, risk: RemovalRisk) -> List[UnusedOrchestratorInfo]:
        """Get unused orchestrators by risk level."""
        return [o for o in cls.get_all_unused() if o.removal_risk == risk]

    @classmethod
    def get_truly_unused(cls) -> List[UnusedOrchestratorInfo]:
        """Get only truly unused orchestrators (0 imports, 0 references)."""
        return [o for o in cls.get_all_unused() if o.is_truly_unused()]

    @classmethod
    def get_removal_summary(cls) -> Dict[str, Any]:
        """Get summary of unused orchestrator removal."""
        all_unused = cls.get_all_unused()
        
        return {
            "total_unused": len(all_unused),
            "safe_to_remove": len(cls.get_safe_to_remove()),
            "low_risk": len(cls.get_by_risk(RemovalRisk.LOW)),
            "medium_risk": len(cls.get_by_risk(RemovalRisk.MEDIUM)),
            "high_risk": len(cls.get_by_risk(RemovalRisk.HIGH)),
            "truly_unused": len(cls.get_truly_unused()),
            "total_files_to_remove": len(cls.get_safe_to_remove()) + len(cls.get_by_risk(RemovalRisk.LOW)),
        }


class UnusedOrchestratorRemover:
    """Handles removal of unused orchestrators."""
    
    def __init__(self):
        self.registry = UnusedOrchestratorsRegistry()
        self.removal_plans: Dict[str, RemovalPlan] = {}
        self.completed_removals: Set[str] = set()
        self.skipped_removals: Set[str] = set()

    def create_removal_plan(self, orchestrator_info: UnusedOrchestratorInfo) -> RemovalPlan:
        """Create removal plan for unused orchestrator."""
        plan = RemovalPlan(orchestrator_info=orchestrator_info)
        self.removal_plans[orchestrator_info.name] = plan
        return plan

    def get_removal_priority(self) -> List[UnusedOrchestratorInfo]:
        """Get removal priority (safe first, then low-risk)."""
        all_unused = self.registry.get_all_unused()
        
        risk_priority = {
            RemovalRisk.SAFE: 3,
            RemovalRisk.LOW: 2,
            RemovalRisk.MEDIUM: 1,
            RemovalRisk.HIGH: 0,
        }
        
        return sorted(
            all_unused,
            key=lambda o: (
                -risk_priority.get(o.removal_risk, 0),
                o.import_count,  # Fewer imports first
                o.reference_count,
                o.name
            )
        )

    def mark_removal_complete(self, orchestrator_name: str) -> bool:
        """Mark orchestrator removal as complete."""
        self.completed_removals.add(orchestrator_name)
        if orchestrator_name in self.skipped_removals:
            self.skipped_removals.remove(orchestrator_name)
        return orchestrator_name in self.completed_removals

    def skip_removal(self, orchestrator_name: str, reason: str) -> bool:
        """Skip removal of orchestrator with reason."""
        self.skipped_removals.add(orchestrator_name)
        return orchestrator_name in self.skipped_removals

    def get_removal_status(self) -> Dict[str, Any]:
        """Get overall removal status."""
        all_unused = self.registry.get_all_unused()
        total = len(all_unused)
        completed = len(self.completed_removals)
        
        return {
            "total_unused": total,
            "completed_removals": completed,
            "skipped": len(self.skipped_removals),
            "remaining": total - completed - len(self.skipped_removals),
            "progress_percentage": (completed / total * 100) if total > 0 else 0,
            "completed_orchestrators": list(self.completed_removals),
            "skipped_orchestrators": list(self.skipped_removals),
        }

    def can_safely_remove(self, orchestrator_info: UnusedOrchestratorInfo) -> bool:
        """Check if orchestrator can be safely removed."""
        return (
            orchestrator_info.is_truly_unused()
            and orchestrator_info.removal_risk in [RemovalRisk.SAFE, RemovalRisk.LOW]
        )

    def get_consolidation_summary(self) -> Dict[str, Any]:
        """Get complete consolidation summary."""
        summary = self.registry.get_removal_summary()
        status = self.get_removal_status()
        
        return {
            **summary,
            **status,
            "safe_removals_planned": len([o for o in self.removal_plans.values() 
                                         if o.orchestrator_info.removal_risk == RemovalRisk.SAFE]),
        }

    def get_removal_plan_for_orchestrator(self, name: str) -> Optional[RemovalPlan]:
        """Get removal plan for specific orchestrator."""
        return self.removal_plans.get(name)

    def create_all_removal_plans(self) -> Dict[str, RemovalPlan]:
        """Create removal plans for all unused orchestrators."""
        all_unused = self.registry.get_all_unused()
        for orchestrator in all_unused:
            self.create_removal_plan(orchestrator)
        return self.removal_plans


# AC_COMPLETE: AC-WAVE7T3-PC-001 ✅ 5 unused orchestrators mapped + removal framework

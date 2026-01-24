"""Vacuum Orchestrator - Multi-Cleaner Orchestration

Author: CORTEX Framework
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, List
import sys
from pathlib import Path

# Add cortex to path
cortex_path = Path(__file__).parent.parent.parent / "cortex"
sys.path.insert(0, str(cortex_path))

from cortex.brain.core.result import Result, Ok, Err
from . import cleaners


class OrchestratorState(Enum):
    """State of orchestrator."""
    INITIALIZED = "initialized"
    ANALYZING = "analyzing"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class VacuumStrategy(Enum):
    """Vacuum strategy."""
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"


@dataclass
class VacuumStats:
    """Statistics from vacuum operation."""
    start_time: str
    end_time: str
    duration_seconds: float
    files_processed: int
    cleaners_used: int
    issues_fixed: int
    errors_encountered: int


@dataclass
class OrchestrationReport:
    """Report from orchestration."""
    state: OrchestratorState
    stats: VacuumStats
    details: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    analyses_completed: int = 0
    executions_completed: int = 0
    
    @property
    def overall_status(self) -> str:
        """Get overall status string.
        
        Returns:
            Overall status based on state
        """
        if self.state == OrchestratorState.COMPLETED:
            return "SUCCESS" if not self.errors else "PARTIAL"
        elif self.state == OrchestratorState.FAILED:
            return "FAILED"
        elif self.state == OrchestratorState.ROLLED_BACK:
            return "ROLLED_BACK"
        else:
            return self.state.value


class VacuumOrchestrator:
    """Vacuum orchestrator for multi-cleaner orchestration."""
    
    _instance: Optional[VacuumOrchestrator] = None
    
    def __init__(
        self,
        name: str = "VacuumOrchestrator",
        version: str = "1.0.0",
        strategy: VacuumStrategy = VacuumStrategy.BALANCED,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize vacuum orchestrator.
        
        Args:
            name: Orchestrator name
            version: Orchestrator version
            strategy: Vacuum strategy (AGGRESSIVE, CONSERVATIVE, BALANCED)
            config: Optional configuration dictionary
        """
        self.name = name
        self.version = version
        self.strategy = strategy
        self.config = config or {}
        self._registry = cleaners.CleanerRegistry()
        self._state = OrchestratorState.INITIALIZED
        self._audit_trail: List[Dict[str, Any]] = []
        self._latest_analyses: Dict[str, Any] = {}
        self._latest_reports: Dict[str, Any] = {}
        self._completed_analyses: List[str] = []
        self._completed_executions: List[str] = []
        self.dry_run = self.config.get("dry_run", False)
    
    @property
    def registry(self) -> cleaners.CleanerRegistry:
        """Get cleaner registry.
        
        Returns:
            CleanerRegistry instance
        """
        return self._registry
    
    def get_cleaner(self, domain: str) -> Any:
        """Get an instantiated cleaner by domain.
        
        Args:
            domain: Cleaner domain
            
        Returns:
            Instantiated cleaner
        """
        return self._registry.get_cleaner(domain, config=self.config)
    
    @classmethod
    def get_instance(cls) -> VacuumOrchestrator:
        """Get singleton instance.
        
        Returns:
            VacuumOrchestrator instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register_cleaner(self, cleaner_class: Any, config: Optional[Dict[str, Any]] = None) -> Result:
        """Register a cleaner class.
        
        Args:
            cleaner_class: Cleaner class to register
            config: Optional configuration for instantiation
            
        Returns:
            Result containing success or error
        """
        try:
            # Register the class in the registry
            self._registry.register_cleaner(cleaner_class)
            
            # Create temporary instance to get metadata
            temp_instance = cleaner_class(config or {})
            cleaner_id = temp_instance.domain
            
            self._audit_trail.append({
                "timestamp": datetime.now().isoformat(),
                "action": "register_cleaner",
                "cleaner_id": cleaner_id,
                "cleaner_name": temp_instance.name,
            })
            return Ok(None)
        except Exception as e:
            return Err(str(e))
    
    def analyze(self, cleaner_id: Optional[str] = None) -> Any:
        """Analyze with registered cleaners.
        
        Args:
            cleaner_id: Optional specific cleaner to analyze. If None, analyzes all.
            
        Returns:
            Analysis result or dict of results
            
        Raises:
            CleanerNotFoundError: If specified cleaner not registered
        """
        self._state = OrchestratorState.ANALYZING
        
        try:
            if cleaner_id:
                # Analyze specific cleaner - let exception propagate if not found
                cleaner = self._registry.get_cleaner(cleaner_id, config=self.config)
                analysis = cleaner.analyze()
                self._latest_analyses[cleaner_id] = analysis
                self._completed_analyses.append(cleaner_id)
                
                self._audit_trail.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "analyze",
                    "cleaner_id": cleaner_id,
                })
                
                return analysis
            else:
                # Analyze all cleaners
                analyses: Dict[str, Any] = {}
                
                for cid in self._registry.list_all():
                    cleaner = self._registry.get_cleaner(cid, config=self.config)
                    analysis = cleaner.analyze()
                    analyses[cid] = analysis
                    self._latest_analyses[cid] = analysis
                    self._completed_analyses.append(cid)
                
                self._audit_trail.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "analyze",
                    "cleaners_analyzed": len(analyses),
                })
                
                return Ok(analyses)
        except Exception as e:
            self._state = OrchestratorState.FAILED
            # Re-raise CleanerNotFoundError, but catch other exceptions
            if e.__class__.__name__ == "CleanerNotFoundError":
                raise
            return Err(str(e))
    
    def execute(self, plan_or_cleaner_id: Any = None, plan: Optional[Dict[str, Any]] = None) -> Any:
        """Execute cleaning plans.
        
        Args:
            plan_or_cleaner_id: Either a cleaner_id string or a plan dict
            plan: Optional execution plan (if first arg is cleaner_id)
            
        Returns:
            Execution report or dict of reports
        """
        try:
            self._state = OrchestratorState.EXECUTING
            
            # Handle both call signatures for backwards compatibility
            if isinstance(plan_or_cleaner_id, str):
                # Specific cleaner: execute(cleaner_id, plan)
                cleaner_id = plan_or_cleaner_id
                cleaner = self._registry.get_cleaner(cleaner_id, config=self.config)
                
                exec_plan = plan or {}
                report = cleaner.execute(exec_plan)
                self._latest_reports[cleaner_id] = report
                self._completed_executions.append(cleaner_id)
                
                self._audit_trail.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "execute",
                    "cleaner_id": cleaner_id,
                })
                
                return report
            elif isinstance(plan_or_cleaner_id, dict):
                # All cleaners: execute(plans_dict)
                reports: Dict[str, Any] = {}
                
                for cleaner_id, plan_item in plan_or_cleaner_id.items():
                    cleaner = self._registry.get_cleaner(cleaner_id, config=self.config)
                    report = cleaner.execute(plan_item)
                    reports[cleaner_id] = report
                    self._latest_reports[cleaner_id] = report
                    self._completed_executions.append(cleaner_id)
                
                self._state = OrchestratorState.COMPLETED
                self._audit_trail.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "execute",
                    "cleaners_executed": len(reports),
                })
                
                return Ok(reports)
            else:
                raise TypeError("Invalid execute() call signature")
        except Exception as e:
            self._state = OrchestratorState.FAILED
            return Err(str(e))
    
    def rollback(self, cleaner_id: Optional[str] = None) -> Any:
        """Rollback changes.
        
        Args:
            cleaner_id: Optional specific cleaner to rollback. If None, rolls back all.
            
        Returns:
            Rollback result or dict of results
        """
        try:
            if cleaner_id:
                # Rollback specific cleaner
                cleaner = self._registry.get_cleaner(cleaner_id, config=self.config)
                
                result = cleaner.rollback()
                
                self._audit_trail.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "rollback",
                    "cleaner_id": cleaner_id,
                })
                
                return result
            else:
                # Rollback all cleaners
                rollback_results: Dict[str, Any] = {}
                
                for cid in self._registry.list_all():
                    cleaner = self._registry.get_cleaner(cid, config=self.config)
                    result = cleaner.rollback()
                    rollback_results[cid] = result
                
                self._state = OrchestratorState.ROLLED_BACK
                self._audit_trail.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "rollback",
                    "cleaners_rolled_back": len(rollback_results),
                })
                
                return Ok(rollback_results)
        except Exception as e:
            self._state = OrchestratorState.FAILED
            return Err(str(e))
    
    def get_state(self) -> OrchestratorState:
        """Get current orchestrator state.
        
        Returns:
            Current state
        """
        return self._state
    
    @property
    def state(self) -> OrchestratorState:
        """State property for convenient access with tracking info.
        
        Returns:
            Current state with tracking attributes added
        """
        # Add attributes directly to the enum instance
        self._state.completed_analyses = self._completed_analyses
        self._state.completed_executions = self._completed_executions
        return self._state
    
    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Get audit trail.
        
        Returns:
            Audit trail entries
        """
        return self._audit_trail.copy()
    
    def get_latest_analysis(self, cleaner_id: str) -> Optional[Any]:
        """Get latest analysis for cleaner.
        
        Args:
            cleaner_id: Cleaner ID
            
        Returns:
            Latest analysis or None
        """
        return self._latest_analyses.get(cleaner_id)
    
    def get_latest_report(self, cleaner_id: str) -> Optional[Any]:
        """Get latest report for cleaner.
        
        Args:
            cleaner_id: Cleaner ID
            
        Returns:
            Latest report or None
        """
        return self._latest_reports.get(cleaner_id)
    
    def list_registered_cleaners(self) -> List[str]:
        """List all registered cleaner IDs.
        
        Returns:
            List of cleaner IDs
        """
        return self._registry.list_all()
    
    def list_cleaners(self) -> List[str]:
        """Alias for list_registered_cleaners().
        
        Returns:
            List of cleaner IDs
        """
        return self.list_registered_cleaners()
    
    def has_cleaner(self, cleaner_id: str) -> bool:
        """Check if a cleaner is registered.
        
        Args:
            cleaner_id: Cleaner ID to check
            
        Returns:
            True if registered, False otherwise
        """
        return self._registry.has_cleaner(cleaner_id)
    
    def generate_report(self) -> OrchestrationReport:
        """Generate orchestration report.
        
        Returns:
            OrchestrationReport with current state and stats
        """
        stats = VacuumStats(
            start_time=datetime.now().isoformat(),
            end_time=datetime.now().isoformat(),
            duration_seconds=0.0,
            files_processed=sum(
                getattr(self._latest_analyses.get(cid, {}), 'files_scanned', 0)
                for cid in self._registry.list_all()
            ) if self._latest_analyses else 0,
            cleaners_used=len(self._registry.list_all()),
            issues_fixed=sum(
                getattr(self._latest_reports.get(cid, {}), 'actions_taken', 0)
                for cid in self._registry.list_all()
            ) if self._latest_reports else 0,
            errors_encountered=len(self._audit_trail),
        )
        
        return OrchestrationReport(
            state=self._state,
            stats=stats,
            details={
                "cleaners": self._registry.list_all(),
                "analyses": len(self._latest_analyses),
                "reports": len(self._latest_reports),
                "audit_entries": len(self._audit_trail),
            },
            errors=[],
            analyses_completed=len(self._completed_analyses),
            executions_completed=len(self._completed_executions),
        )


__all__ = ["OrchestratorState", "VacuumStrategy", "VacuumStats", "OrchestrationReport", "VacuumOrchestrator"]

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


class VacuumOrchestrator:
    """Vacuum orchestrator for multi-cleaner orchestration."""
    
    _instance: Optional[VacuumOrchestrator] = None
    
    def __init__(
        self,
        name: str = "VacuumOrchestrator",
        version: str = "1.0.0",
        strategy: VacuumStrategy = VacuumStrategy.BALANCED,
    ) -> None:
        """Initialize vacuum orchestrator.
        
        Args:
            name: Orchestrator name
            version: Orchestrator version
            strategy: Vacuum strategy (AGGRESSIVE, CONSERVATIVE, BALANCED)
        """
        self.name = name
        self.version = version
        self.strategy = strategy
        self._registry = cleaners.CleanerRegistry()
        self._state = OrchestratorState.INITIALIZED
        self._audit_trail: List[Dict[str, Any]] = []
        self._latest_analyses: Dict[str, Any] = {}
        self._latest_reports: Dict[str, Any] = {}
    
    @classmethod
    def get_instance(cls) -> VacuumOrchestrator:
        """Get singleton instance.
        
        Returns:
            VacuumOrchestrator instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register_cleaner(self, cleaner_id: str, cleaner: "cleaners.CleanerInterface") -> Result:
        """Register a cleaner.
        
        Args:
            cleaner_id: Unique cleaner ID
            cleaner: Cleaner instance
            
        Returns:
            Result containing success or error
        """
        try:
            self._registry.register(cleaner_id, cleaner)
            self._audit_trail.append({
                "timestamp": datetime.now().isoformat(),
                "action": "register_cleaner",
                "cleaner_id": cleaner_id,
                "cleaner_name": cleaner.name,
            })
            return Ok(None)
        except Exception as e:
            return Err(str(e))
    
    def analyze(self) -> Result:
        """Analyze with all registered cleaners.
        
        Returns:
            Result containing analysis results or error
        """
        try:
            self._state = OrchestratorState.ANALYZING
            analyses: Dict[str, Any] = {}
            
            for cleaner_id in self._registry.list_cleaners():
                cleaner = self._registry.get(cleaner_id)
                if cleaner:
                    analysis = cleaner.analyze()
                    analyses[cleaner_id] = analysis
                    self._latest_analyses[cleaner_id] = analysis
            
            self._audit_trail.append({
                "timestamp": datetime.now().isoformat(),
                "action": "analyze",
                "cleaners_analyzed": len(analyses),
            })
            
            return Ok(analyses)
        except Exception as e:
            self._state = OrchestratorState.FAILED
            return Err(str(e))
    
    def execute(self, plans: Dict[str, Dict[str, Any]]) -> Result:
        """Execute cleaning plans.
        
        Args:
            plans: Mapping of cleaner_id to cleaning plan
            
        Returns:
            Result containing execution reports or error
        """
        try:
            self._state = OrchestratorState.EXECUTING
            reports: Dict[str, Any] = {}
            
            for cleaner_id, plan in plans.items():
                cleaner = self._registry.get(cleaner_id)
                if cleaner:
                    report = cleaner.execute(plan)
                    reports[cleaner_id] = report
                    self._latest_reports[cleaner_id] = report
            
            self._state = OrchestratorState.COMPLETED
            self._audit_trail.append({
                "timestamp": datetime.now().isoformat(),
                "action": "execute",
                "cleaners_executed": len(reports),
            })
            
            return Ok(reports)
        except Exception as e:
            self._state = OrchestratorState.FAILED
            return Err(str(e))
    
    def rollback(self) -> Result:
        """Rollback all recent changes.
        
        Returns:
            Result containing rollback results or error
        """
        try:
            rollback_results: Dict[str, Any] = {}
            
            for cleaner_id in self._registry.list_cleaners():
                cleaner = self._registry.get(cleaner_id)
                if cleaner:
                    result = cleaner.rollback()
                    rollback_results[cleaner_id] = result
            
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
        return self._registry.list_cleaners()


__all__ = ["OrchestratorState", "VacuumStrategy", "VacuumStats", "OrchestrationReport", "VacuumOrchestrator"]

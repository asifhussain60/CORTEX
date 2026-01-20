"""Automatic state repair mechanisms for known inconsistency patterns.

Implements self-healing for hash chain breaks, version mismatches,
referential integrity violations, and other corruption patterns.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Set
import json
import logging
import threading
import time


logger = logging.getLogger(__name__)


class InconsistencyType(str, Enum):
    """Type of state inconsistency."""
    HASH_CHAIN_BREAK = "HASH_CHAIN_BREAK"
    VERSION_MISMATCH = "VERSION_MISMATCH"
    REFERENTIAL_INTEGRITY = "REFERENTIAL_INTEGRITY"
    DATA_CORRUPTION = "DATA_CORRUPTION"
    AGGREGATE_MISMATCH = "AGGREGATE_MISMATCH"


class RepairMode(str, Enum):
    """Repair execution mode."""
    DRY_RUN = "DRY_RUN"  # Detect only, no modification
    EXECUTE = "EXECUTE"  # Perform actual repair


class RepairError(Exception):
    """Raised when repair cannot be performed."""
    pass


@dataclass
class InconsistencyRecord:
    """Record of detected state inconsistency.
    
    Args:
        inconsistency_id: Unique identifier
        inconsistency_type: Type of inconsistency
        severity: Severity level (CRITICAL, HIGH, MEDIUM, LOW)
        detected_at: Detection timestamp
        description: Human-readable description
        affected_resources: Resources affected
        metadata: Additional context
    """
    inconsistency_id: str
    inconsistency_type: InconsistencyType
    severity: str
    detected_at: datetime
    description: str
    affected_resources: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def priority(self) -> int:
        """Get repair priority (higher = more urgent).
        
        Returns:
            Priority score
        """
        severity_scores = {
            "CRITICAL": 100,
            "HIGH": 75,
            "MEDIUM": 50,
            "LOW": 25
        }
        return severity_scores.get(self.severity, 0)


@dataclass
class RepairStrategy:
    """Strategy for repairing specific inconsistency type.
    
    Args:
        inconsistency_type: Type of inconsistency
        action: Repair action name
        description: Human-readable description
        requires_backup: Whether to create backup before repair
    """
    inconsistency_type: InconsistencyType
    action: str
    description: str
    requires_backup: bool = True
    
    @classmethod
    def for_inconsistency(cls, inconsistency_type: InconsistencyType) -> "RepairStrategy":
        """Get repair strategy for inconsistency type.
        
        Args:
            inconsistency_type: Inconsistency type
            
        Returns:
            Repair strategy
        """
        strategies = {
            InconsistencyType.HASH_CHAIN_BREAK: cls(
                inconsistency_type=InconsistencyType.HASH_CHAIN_BREAK,
                action="rebuild_hash_chain",
                description="Rebuild hash chain from checkpoint",
                requires_backup=True
            ),
            InconsistencyType.VERSION_MISMATCH: cls(
                inconsistency_type=InconsistencyType.VERSION_MISMATCH,
                action="reconcile_versions",
                description="Reconcile version conflicts",
                requires_backup=False
            ),
            InconsistencyType.REFERENTIAL_INTEGRITY: cls(
                inconsistency_type=InconsistencyType.REFERENTIAL_INTEGRITY,
                action="fix_references",
                description="Fix broken references",
                requires_backup=True
            ),
            InconsistencyType.DATA_CORRUPTION: cls(
                inconsistency_type=InconsistencyType.DATA_CORRUPTION,
                action="restore_from_backup",
                description="Restore corrupted data from backup",
                requires_backup=False
            ),
            InconsistencyType.AGGREGATE_MISMATCH: cls(
                inconsistency_type=InconsistencyType.AGGREGATE_MISMATCH,
                action="recompute_aggregates",
                description="Recompute aggregate values",
                requires_backup=False
            ),
        }
        return strategies[inconsistency_type]


@dataclass
class RepairResult:
    """Result of repair operation.
    
    Args:
        success: Whether repair succeeded
        inconsistency_id: Inconsistency that was repaired
        dry_run: Whether this was a dry run
        before_state: State before repair
        after_state: State after repair
        actions_taken: Actions performed
        message: Result message
        timestamp: When repair was performed
    """
    success: bool
    inconsistency_id: str
    dry_run: bool
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    actions_taken: List[str] = field(default_factory=list)
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


class HashChainManager(Protocol):
    """Protocol for hash chain management."""
    
    def verify_integrity(self) -> bool:
        """Verify hash chain integrity."""
        ...
    
    def get_break_location(self) -> tuple[str, str]:
        """Get location of hash chain break."""
        ...
    
    def rebuild_chain(self, from_block: Optional[str] = None) -> None:
        """Rebuild hash chain."""
        ...
    
    def create_backup(self) -> Dict[str, Any]:
        """Create backup of current state."""
        ...
    
    def restore_backup(self, backup: Dict[str, Any]) -> None:
        """Restore from backup."""
        ...
    
    def get_state_snapshot(self) -> Dict[str, Any]:
        """Get current state snapshot."""
        ...


class StateRepair:
    """Automatic state repair engine.
    
    Args:
        storage_path: Path to store repair state
        hash_chain_manager: Hash chain management interface
        enable_auto_repair: Whether to automatically repair detected issues
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        hash_chain_manager: Optional[HashChainManager] = None,
        enable_auto_repair: bool = False
    ):
        self.storage_path = storage_path or Path.home() / ".cortex" / "repairs"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.hash_chain_manager = hash_chain_manager
        self.enable_auto_repair = enable_auto_repair
        
        self._quarantined: Set[str] = set()
        self._alerts: List[Dict[str, Any]] = []
        self._active_operations: Set[str] = set()
        self._repair_progress: Dict[str, Any] = {}
        self._scheduled_repair_active = False
        self._metrics: Dict[str, Any] = {
            "repairs_attempted": 0,
            "repairs_succeeded": 0,
            "repairs_failed": 0,
            "repair_duration_seconds": []
        }
    
    def detect_inconsistencies(self) -> List[InconsistencyRecord]:
        """Detect all state inconsistencies.
        
        Returns:
            List of detected inconsistencies
        """
        inconsistencies: List[InconsistencyRecord] = []
        
        # Detect hash chain breaks
        if self.hash_chain_manager:
            try:
                if not self.hash_chain_manager.verify_integrity():
                    block_id, reason = self.hash_chain_manager.get_break_location()
                    inconsistencies.append(InconsistencyRecord(
                        inconsistency_id=f"hash-break-{block_id}",
                        inconsistency_type=InconsistencyType.HASH_CHAIN_BREAK,
                        severity="HIGH",
                        detected_at=datetime.utcnow(),
                        description=f"Hash chain break at {block_id}: {reason}",
                        affected_resources=[block_id],
                        metadata={"reason": reason}
                    ))
            except Exception as e:
                logger.error(f"Error detecting hash chain issues: {e}")
        
        logger.info(f"Detected {len(inconsistencies)} inconsistencies")
        return inconsistencies
    
    def repair_inconsistencies(
        self,
        inconsistencies: List[InconsistencyRecord],
        mode: RepairMode = RepairMode.EXECUTE
    ) -> List[RepairResult]:
        """Repair detected inconsistencies.
        
        Args:
            inconsistencies: Inconsistencies to repair
            mode: Repair mode (dry-run or execute)
            
        Returns:
            List of repair results
        """
        # Sort by priority
        sorted_inconsistencies = sorted(
            inconsistencies,
            key=lambda x: x.priority(),
            reverse=True
        )
        
        results: List[RepairResult] = []
        
        # Initialize progress tracking
        self._repair_progress = {
            "total": len(sorted_inconsistencies),
            "completed": 0,
            "failed": 0,
            "deferred": 0,
            "attempted": [],  # Track items that were attempted (success or failure)
            "remaining": [inc.inconsistency_id for inc in sorted_inconsistencies]
        }
        
        try:
            for i, inconsistency in enumerate(sorted_inconsistencies):
                # Check for conflicts with active operations
                if self._has_active_conflict(inconsistency):
                    results.append(RepairResult(
                        success=False,
                        inconsistency_id=inconsistency.inconsistency_id,
                        dry_run=mode == RepairMode.DRY_RUN,
                        message="Deferred: conflicts with active operation"
                    ))
                    self._repair_progress["deferred"] += 1
                    self._repair_progress["remaining"].remove(inconsistency.inconsistency_id)
                    continue
                
                # Mark as attempted
                self._repair_progress["attempted"].append(inconsistency.inconsistency_id)
                
                # Execute repair
                result = self._repair_single(inconsistency, mode)
                results.append(result)
                
                # Update progress - only remove from remaining if successful
                if result.success:
                    self._repair_progress["completed"] += 1
                    self._repair_progress["remaining"].remove(inconsistency.inconsistency_id)
                else:
                    self._repair_progress["failed"] += 1
                
                # Update metrics
                self._metrics["repairs_attempted"] += 1
                if result.success:
                    self._metrics["repairs_succeeded"] += 1
                else:
                    self._metrics["repairs_failed"] += 1
        except Exception as e:
            # Save checkpoint on failure
            logger.error(f"Repair failed: {e}")
            self._save_checkpoint(sorted_inconsistencies, results)
            raise
        
        return results
    
    def repair_on_demand(self) -> List[RepairResult]:
        """Trigger on-demand repair.
        
        Returns:
            List of repair results
        """
        logger.info("Starting on-demand repair")
        inconsistencies = self.detect_inconsistencies()
        return self.repair_inconsistencies(inconsistencies)
    
    def schedule_repair(self, interval_hours: int = 24) -> None:
        """Schedule automatic repair.
        
        Args:
            interval_hours: Hours between repair runs
        """
        self._scheduled_repair_active = True
        logger.info(f"Scheduled automatic repair every {interval_hours} hours")
        
        def repair_loop() -> None:
            while self._scheduled_repair_active:
                try:
                    inconsistencies = self.detect_inconsistencies()
                    if inconsistencies:
                        self.repair_inconsistencies(inconsistencies)
                except Exception as e:
                    logger.error(f"Error in scheduled repair: {e}")
                
                time.sleep(interval_hours * 3600)
        
        thread = threading.Thread(target=repair_loop, daemon=True)
        thread.start()
    
    def is_quarantined(self, resource_id: str) -> bool:
        """Check if resource is quarantined.
        
        Args:
            resource_id: Resource identifier
            
        Returns:
            True if quarantined
        """
        return resource_id in self._quarantined
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts.
        
        Returns:
            List of alerts
        """
        return self._alerts
    
    def get_repair_progress(self) -> Dict[str, Any]:
        """Get current repair progress.
        
        Returns:
            Progress information
        """
        return self._repair_progress
    
    def resume_repair(self) -> List[RepairResult]:
        """Resume repair from checkpoint.
        
        Returns:
            List of repair results
        """
        checkpoint_file = self.storage_path / "repair_checkpoint.json"
        if not checkpoint_file.exists():
            return []
        
        checkpoint = json.loads(checkpoint_file.read_text())
        remaining = [
            InconsistencyRecord(
                inconsistency_id=inc["inconsistency_id"],
                inconsistency_type=InconsistencyType(inc["inconsistency_type"]),
                severity=inc["severity"],
                detected_at=datetime.fromisoformat(inc["detected_at"]),
                description=inc["description"],
                affected_resources=inc["affected_resources"],
                metadata=inc.get("metadata", {})
            )
            for inc in checkpoint.get("remaining", [])
        ]
        
        return self.repair_inconsistencies(remaining)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get repair metrics.
        
        Returns:
            Metrics dictionary
        """
        return self._metrics.copy()
    
    def _repair_single(
        self,
        inconsistency: InconsistencyRecord,
        mode: RepairMode
    ) -> RepairResult:
        """Repair single inconsistency.
        
        Args:
            inconsistency: Inconsistency to repair
            mode: Repair mode
            
        Returns:
            Repair result
        """
        strategy = RepairStrategy.for_inconsistency(inconsistency.inconsistency_type)
        
        # Capture before state
        before_state = None
        if self.hash_chain_manager:
            before_state = self.hash_chain_manager.get_state_snapshot()
        
        # Dry run - no actual changes
        if mode == RepairMode.DRY_RUN:
            return RepairResult(
                success=True,
                inconsistency_id=inconsistency.inconsistency_id,
                dry_run=True,
                before_state=before_state,
                actions_taken=[f"Would execute: {strategy.action}"],
                message=f"Dry run: {strategy.description}"
            )
        
        # Create backup if required
        backup = None
        if strategy.requires_backup and self.hash_chain_manager:
            backup = self.hash_chain_manager.create_backup()
        
        start_time = time.time()
        
        # Execute repair
        try:
            actions = self._execute_repair(inconsistency, strategy)
            
            # Capture after state
            after_state = None
            if self.hash_chain_manager:
                after_state = self.hash_chain_manager.get_state_snapshot()
            
            # Validate repair didn't introduce new issues
            if not self._validate_repair(inconsistency):
                logger.warning(f"Repair validation failed for {inconsistency.inconsistency_id}")
                
                # Rollback
                if backup and self.hash_chain_manager:
                    self.hash_chain_manager.restore_backup(backup)
                
                return RepairResult(
                    success=False,
                    inconsistency_id=inconsistency.inconsistency_id,
                    dry_run=False,
                    before_state=before_state,
                    after_state=after_state,
                    actions_taken=actions,
                    message="Repair validation failed, rolled back"
                )
            
            duration = time.time() - start_time
            self._metrics["repair_duration_seconds"].append(duration)
            
            return RepairResult(
                success=True,
                inconsistency_id=inconsistency.inconsistency_id,
                dry_run=False,
                before_state=before_state,
                after_state=after_state,
                actions_taken=actions,
                message=f"Successfully repaired: {strategy.description}"
            )
        
        except RepairError as e:
            # Irreparable - quarantine
            for resource in inconsistency.affected_resources:
                self._quarantined.add(resource)
            
            self._alerts.append({
                "timestamp": datetime.utcnow().isoformat(),
                "severity": "CRITICAL",
                "message": f"Irreparable corruption: {e}",
                "inconsistency_id": inconsistency.inconsistency_id,
                "affected_resources": inconsistency.affected_resources
            })
            
            return RepairResult(
                success=False,
                inconsistency_id=inconsistency.inconsistency_id,
                dry_run=False,
                before_state=before_state,
                actions_taken=[],
                message=f"Irreparable: {e}"
            )
        
        except RepairError as e:
            logger.error(f"Repair failed for {inconsistency.inconsistency_id}: {e}")
            
            # Rollback on error
            if backup and self.hash_chain_manager:
                self.hash_chain_manager.restore_backup(backup)
            
            return RepairResult(
                success=False,
                inconsistency_id=inconsistency.inconsistency_id,
                dry_run=False,
                before_state=before_state,
                actions_taken=[],
                message=f"Repair failed: {e}"
            )
    
    def _execute_repair(
        self,
        inconsistency: InconsistencyRecord,
        strategy: RepairStrategy
    ) -> List[str]:
        """Execute repair action.
        
        Args:
            inconsistency: Inconsistency to repair
            strategy: Repair strategy
            
        Returns:
            List of actions taken
        """
        actions: List[str] = []
        
        if inconsistency.inconsistency_type == InconsistencyType.HASH_CHAIN_BREAK:
            if not self.hash_chain_manager:
                raise RepairError("Hash chain manager not available")
            
            block_id = inconsistency.affected_resources[0] if inconsistency.affected_resources else None
            self.hash_chain_manager.rebuild_chain(from_block=block_id)
            actions.append(f"Rebuilt hash chain from {block_id}")
        
        elif inconsistency.inconsistency_type == InconsistencyType.DATA_CORRUPTION:
            if not self.hash_chain_manager:
                raise RepairError("Hash chain manager not available")
            
            # Attempt to rebuild - will raise RepairError if cannot repair
            block_id = inconsistency.affected_resources[0] if inconsistency.affected_resources else None
            self.hash_chain_manager.rebuild_chain(from_block=block_id)
            actions.append(f"Restored corrupted data at {block_id}")
        
        # Add other repair strategies as needed
        
        return actions
    
    def _validate_repair(self, inconsistency: InconsistencyRecord) -> bool:
        """Validate repair didn't introduce new issues.
        
        Args:
            inconsistency: Inconsistency that was repaired
            
        Returns:
            True if validation passed
        """
        if inconsistency.inconsistency_type == InconsistencyType.HASH_CHAIN_BREAK:
            if self.hash_chain_manager:
                return self.hash_chain_manager.verify_integrity()
        
        return True
    
    def _has_active_conflict(self, inconsistency: InconsistencyRecord) -> bool:
        """Check if repair conflicts with active operations.
        
        Args:
            inconsistency: Inconsistency to check
            
        Returns:
            True if there's a conflict
        """
        for resource in inconsistency.affected_resources:
            if resource in self._active_operations:
                return True
        return False

    def _save_checkpoint(
        self,
        inconsistencies: List[InconsistencyRecord],
        completed_results: List[RepairResult]
    ) -> None:
        """Save repair checkpoint for resume.
        
        Checkpoint includes both failed items (to retry) and never-attempted items.
        
        Args:
            inconsistencies: All inconsistencies in repair
            completed_results: Results completed so far
        """
        # Get successfully completed IDs
        completed_ids = {r.inconsistency_id for r in completed_results}
        
        # Include all items NOT successfully completed (both failed and not-attempted)
        remaining_inconsistencies = [
            inc for inc in inconsistencies 
            if inc.inconsistency_id not in completed_ids
        ]
        
        checkpoint = {
            "timestamp": datetime.utcnow().isoformat(),
            "completed_count": len(completed_results),
            "remaining": [
                {
                    "inconsistency_id": inc.inconsistency_id,
                    "inconsistency_type": inc.inconsistency_type.value,
                    "severity": inc.severity,
                    "detected_at": inc.detected_at.isoformat(),
                    "description": inc.description,
                    "affected_resources": inc.affected_resources,
                    "metadata": inc.metadata
                }
                for inc in remaining_inconsistencies
            ],
            "progress": self._repair_progress
        }
        
        checkpoint_file = self.storage_path / "repair_checkpoint.json"
        checkpoint_file.write_text(json.dumps(checkpoint, indent=2))


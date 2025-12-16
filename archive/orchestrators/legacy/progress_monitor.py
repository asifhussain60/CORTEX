"""
Progress Monitoring Integration - Feature 5
Tracks phase completion, velocity metrics, and dashboard integration

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
import json


class ProgressStatus(Enum):
    """Status of a phase"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PhaseProgress:
    """Progress tracking for a single phase"""
    feature_name: str
    phase_name: str
    status: ProgressStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    estimated_hours: float = 0.0
    actual_hours: Optional[float] = None
    failure_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'feature_name': self.feature_name,
            'phase_name': self.phase_name,
            'status': self.status.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'failure_reason': self.failure_reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhaseProgress':
        """Create from dictionary"""
        return cls(
            feature_name=data['feature_name'],
            phase_name=data['phase_name'],
            status=ProgressStatus(data['status']),
            start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            estimated_hours=data.get('estimated_hours', 0.0),
            actual_hours=data.get('actual_hours'),
            failure_reason=data.get('failure_reason')
        )


@dataclass
class VelocityMetrics:
    """Velocity and performance metrics"""
    phases_per_hour: float = 0.0
    total_phases_completed: int = 0
    total_hours_spent: float = 0.0
    accuracy_percentage: float = 0.0
    total_estimated_hours: float = 0.0
    total_actual_hours: float = 0.0


class ProgressMonitor:
    """
    Progress Monitoring Integration - Feature 5
    
    Tracks orchestrator progress across features:
    - Phase start/complete/fail tracking
    - Velocity calculation (phases/hour, estimated vs actual)
    - Dashboard integration for real-time display
    - Orchestrator hooks for auto-tracking
    - Metrics persistence to brain Tier 1
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize progress monitor
        
        Args:
            storage_path: Path to store metrics (defaults to cortex-brain/metrics/)
        """
        self.storage_path = storage_path or Path("cortex-brain/metrics")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.phases: Dict[str, PhaseProgress] = {}
        self._load_phases_from_storage()
    
    @staticmethod
    def _make_phase_key(feature_name: str, phase_name: str) -> str:
        """
        Generate unique key for a phase
        
        Args:
            feature_name: Feature name
            phase_name: Phase name
            
        Returns:
            Unique phase key
        """
        return f"{feature_name}::{phase_name}"
    
    def start_phase(
        self,
        feature_name: str,
        phase_name: str,
        estimated_hours: float
    ) -> PhaseProgress:
        """
        Start tracking a new phase
        
        Args:
            feature_name: Name of feature (e.g., "Feature 5")
            phase_name: Name of phase (e.g., "Phase 5.1 (RED)")
            estimated_hours: Estimated completion time in hours
            
        Returns:
            PhaseProgress with IN_PROGRESS status
        """
        phase_key = self._make_phase_key(feature_name, phase_name)
        
        phase = PhaseProgress(
            feature_name=feature_name,
            phase_name=phase_name,
            status=ProgressStatus.IN_PROGRESS,
            start_time=datetime.now(),
            estimated_hours=estimated_hours
        )
        
        self.phases[phase_key] = phase
        self._save_phase(phase)
        
        return phase
    
    def complete_phase(self, feature_name: str, phase_name: str) -> PhaseProgress:
        """
        Mark phase as completed
        
        Args:
            feature_name: Name of feature
            phase_name: Name of phase
            
        Returns:
            PhaseProgress with COMPLETED status and actual_hours calculated
        """
        phase_key = self._make_phase_key(feature_name, phase_name)
        
        if phase_key not in self.phases:
            raise ValueError(f"Phase not found: {phase_key}")
        
        phase = self.phases[phase_key]
        phase.status = ProgressStatus.COMPLETED
        phase.end_time = datetime.now()
        
        if phase.start_time:
            duration = phase.end_time - phase.start_time
            phase.actual_hours = duration.total_seconds() / 3600
        
        self._save_phase(phase)
        
        return phase
    
    def fail_phase(
        self,
        feature_name: str,
        phase_name: str,
        reason: str
    ) -> PhaseProgress:
        """
        Mark phase as failed
        
        Args:
            feature_name: Name of feature
            phase_name: Name of phase
            reason: Failure reason
            
        Returns:
            PhaseProgress with FAILED status
        """
        phase_key = self._make_phase_key(feature_name, phase_name)
        
        if phase_key not in self.phases:
            raise ValueError(f"Phase not found: {phase_key}")
        
        phase = self.phases[phase_key]
        phase.status = ProgressStatus.FAILED
        phase.end_time = datetime.now()
        phase.failure_reason = reason
        
        if phase.start_time:
            duration = phase.end_time - phase.start_time
            phase.actual_hours = duration.total_seconds() / 3600
        
        self._save_phase(phase)
        
        return phase
    
    def get_phase_status(self, feature_name: str, phase_name: str) -> PhaseProgress:
        """
        Get current phase status
        
        Args:
            feature_name: Name of feature
            phase_name: Name of phase
            
        Returns:
            PhaseProgress for the phase
        """
        phase_key = self._make_phase_key(feature_name, phase_name)
        
        if phase_key not in self.phases:
            raise ValueError(f"Phase not found: {phase_key}")
        
        return self.phases[phase_key]
    
    def get_feature_phases(self, feature_name: str) -> List[PhaseProgress]:
        """
        Get all phases for a feature
        
        Args:
            feature_name: Name of feature
            
        Returns:
            List of PhaseProgress for the feature
        """
        return [
            phase for phase in self.phases.values()
            if phase.feature_name == feature_name
        ]
    
    def calculate_velocity(self) -> VelocityMetrics:
        """
        Calculate velocity metrics
        
        Returns:
            VelocityMetrics with phases/hour, accuracy, etc.
        """
        completed_phases = [
            p for p in self.phases.values()
            if p.status == ProgressStatus.COMPLETED
        ]
        
        if not completed_phases:
            return VelocityMetrics()
        
        total_hours = sum(p.actual_hours for p in completed_phases if p.actual_hours)
        total_estimated = sum(p.estimated_hours for p in completed_phases)
        total_actual = total_hours
        
        phases_per_hour = len(completed_phases) / total_hours if total_hours > 0 else 0
        
        # Calculate accuracy: (estimated / actual) * 100
        accuracy = (total_estimated / total_actual * 100) if total_actual > 0 else 0
        
        return VelocityMetrics(
            phases_per_hour=phases_per_hour,
            total_phases_completed=len(completed_phases),
            total_hours_spent=total_hours,
            accuracy_percentage=accuracy,
            total_estimated_hours=total_estimated,
            total_actual_hours=total_actual
        )
    
    def calculate_completion_percentage(self) -> float:
        """
        Calculate overall completion percentage
        
        Returns:
            Percentage (0-100) of phases completed
        """
        if not self.phases:
            return 0.0
        
        completed = sum(
            1 for p in self.phases.values()
            if p.status == ProgressStatus.COMPLETED
        )
        
        return (completed / len(self.phases)) * 100
    
    def get_historical_velocity(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get historical velocity data from Tier 1
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of historical phase data
        """
        # This would integrate with Tier 1 WorkingMemory
        # For now, return recent completed phases
        cutoff = datetime.now() - timedelta(days=days)
        
        history = []
        for phase in self.phases.values():
            if phase.status == ProgressStatus.COMPLETED and phase.end_time:
                if phase.end_time >= cutoff:
                    history.append({
                        'feature': phase.feature_name,
                        'phase': phase.phase_name,
                        'hours': phase.actual_hours
                    })
        
        return history
    
    def generate_dashboard_summary(self) -> Dict[str, Any]:
        """
        Generate summary for dashboard display
        
        Returns:
            Dictionary with counts, percentages, velocity
        """
        total = len(self.phases)
        completed = sum(1 for p in self.phases.values() if p.status == ProgressStatus.COMPLETED)
        in_progress = sum(1 for p in self.phases.values() if p.status == ProgressStatus.IN_PROGRESS)
        failed = sum(1 for p in self.phases.values() if p.status == ProgressStatus.FAILED)
        
        velocity = self.calculate_velocity()
        
        return {
            'total_phases': total,
            'completed_phases': completed,
            'in_progress_phases': in_progress,
            'failed_phases': failed,
            'completion_percentage': (completed / total * 100) if total > 0 else 0,
            'velocity': {
                'phases_per_hour': velocity.phases_per_hour,
                'accuracy_percentage': velocity.accuracy_percentage
            }
        }
    
    def generate_timeline(self) -> List[Dict[str, Any]]:
        """
        Generate timeline for visualization
        
        Returns:
            List of phase timeline entries
        """
        timeline = []
        
        for phase in self.phases.values():
            if phase.status == ProgressStatus.COMPLETED and phase.start_time and phase.end_time:
                duration = phase.end_time - phase.start_time
                
                timeline.append({
                    'feature': phase.feature_name,
                    'phase': phase.phase_name,
                    'start': phase.start_time.isoformat(),
                    'end': phase.end_time.isoformat(),
                    'duration_minutes': int(duration.total_seconds() / 60)
                })
        
        return timeline
    
    def detect_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        Detect phases taking longer than estimated
        
        Returns:
            List of bottleneck phases with overrun percentage
        """
        bottlenecks = []
        
        for phase in self.phases.values():
            if phase.status == ProgressStatus.COMPLETED and phase.actual_hours:
                if phase.actual_hours > phase.estimated_hours:
                    overrun = (phase.actual_hours / phase.estimated_hours - 1) * 100
                    
                    bottlenecks.append({
                        'feature': phase.feature_name,
                        'phase': phase.phase_name,
                        'estimated_hours': phase.estimated_hours,
                        'actual_hours': phase.actual_hours,
                        'overrun_percentage': overrun
                    })
        
        return bottlenecks
    
    def on_orchestrator_phase_start(self, orchestrator: str, phase: str) -> PhaseProgress:
        """
        Hook for orchestrators to report phase start
        
        Args:
            orchestrator: Orchestrator name
            phase: Phase name
            
        Returns:
            PhaseProgress tracking entry
        """
        return self.start_phase(orchestrator, phase, estimated_hours=0.5)
    
    def on_orchestrator_phase_complete(self, orchestrator: str, phase: str) -> PhaseProgress:
        """
        Hook for orchestrators to report phase completion
        
        Args:
            orchestrator: Orchestrator name
            phase: Phase name
            
        Returns:
            PhaseProgress with completion data
        """
        return self.complete_phase(orchestrator, phase)
    
    def get_current_phase(self) -> Optional[PhaseProgress]:
        """
        Get currently active phase
        
        Returns:
            PhaseProgress for IN_PROGRESS phase, or None
        """
        for phase in self.phases.values():
            if phase.status == ProgressStatus.IN_PROGRESS:
                return phase
        return None
    
    def on_gate_validation_start(self, gate: str) -> PhaseProgress:
        """
        Hook for gate validations
        
        Args:
            gate: Gate name
            
        Returns:
            PhaseProgress tracking entry
        """
        return self.start_phase(gate, "Validation", estimated_hours=0.01)
    
    def on_gate_validation_complete(self, gate: str, passed: bool) -> PhaseProgress:
        """
        Hook for gate validation completion
        
        Args:
            gate: Gate name
            passed: Whether validation passed
            
        Returns:
            PhaseProgress with completion data
        """
        if passed:
            return self.complete_phase(gate, "Validation")
        else:
            return self.fail_phase(gate, "Validation", "Gate validation failed")
    
    def get_gate_validations(self) -> List[Dict[str, Any]]:
        """
        Get all gate validations
        
        Returns:
            List of gate validation entries
        """
        validations = []
        
        for phase in self.phases.values():
            if phase.phase_name == "Validation":
                validations.append({
                    'gate': phase.feature_name,
                    'passed': phase.status == ProgressStatus.COMPLETED,
                    'timestamp': phase.end_time.isoformat() if phase.end_time else None
                })
        
        return validations
    
    def sync_with_git_checkpoints(self):
        """
        Sync progress with git checkpoints from Feature 2
        
        This would integrate with GitCheckpointUtility to track checkpoints
        """
        # Placeholder for Feature 2 integration
        pass
    
    def get_checkpoints(self) -> List[Dict[str, str]]:
        """
        Get git checkpoints
        
        Returns:
            List of checkpoint entries
        """
        # Placeholder - would query git tags
        return []
    
    def cleanup_old_metrics(self, days: int = 30):
        """
        Clean up metrics older than specified days
        
        Args:
            days: Age threshold in days
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        # Remove old phases
        to_remove = []
        for key, phase in self.phases.items():
            if phase.end_time and phase.end_time < cutoff:
                to_remove.append(key)
        
        for key in to_remove:
            del self.phases[key]
        
        # Clean up storage
        self._cleanup_storage(cutoff)
    
    def _save_phase(self, phase: PhaseProgress):
        """Save phase to storage"""
        storage_file = self.storage_path / "phases.json"
        
        # Load existing data
        data = {}
        if storage_file.exists():
            with open(storage_file, 'r') as f:
                data = json.load(f)
        
        # Update phase
        phase_key = self._make_phase_key(phase.feature_name, phase.phase_name)
        data[phase_key] = phase.to_dict()
        
        # Save
        with open(storage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_phases_from_storage(self):
        """Load phases from storage"""
        storage_file = self.storage_path / "phases.json"
        
        if not storage_file.exists():
            return
        
        with open(storage_file, 'r') as f:
            data = json.load(f)
        
        for phase_key, phase_data in data.items():
            self.phases[phase_key] = PhaseProgress.from_dict(phase_data)
    
    def _cleanup_storage(self, cutoff: datetime):
        """Clean up old entries from storage"""
        storage_file = self.storage_path / "phases.json"
        
        if not storage_file.exists():
            return
        
        with open(storage_file, 'r') as f:
            data = json.load(f)
        
        # Remove old entries
        filtered_data = {}
        for key, phase_data in data.items():
            if phase_data.get('end_time'):
                end_time = datetime.fromisoformat(phase_data['end_time'])
                if end_time >= cutoff:
                    filtered_data[key] = phase_data
            else:
                # Keep in-progress phases
                filtered_data[key] = phase_data
        
        # Save filtered data
        with open(storage_file, 'w') as f:
            json.dump(filtered_data, f, indent=2)

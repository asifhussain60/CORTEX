"""
CORTEX Autonomous Phase Execution Controller
Manages silent, autonomous end-to-end phase execution with machine/OS tracking.
Authority: CORTEX Architect Instructions v15.1 + Phase 56 Requirements
"""

import os
import platform
import socket
import json
import yaml
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum


class ExecutionMode(Enum):
    """Phase execution modes."""
    AUTONOMOUS = "autonomous"
    MANUAL = "manual"
    PARALLEL = "parallel"


class PhaseStatus(Enum):
    """Phase execution status."""
    PLANNED = "planned"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_MACHINE = "waiting_for_machine"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class MachineIdentity:
    """Machine/OS identity for continuous execution tracking."""
    hostname: str
    os_type: str  # 'Darwin', 'Linux', 'Windows'
    os_version: str
    arch: str
    python_version: str
    machine_hash: str  # Unique deterministic hash
    
    @classmethod
    def current(cls) -> 'MachineIdentity':
        """Get current machine identity."""
        hostname = socket.gethostname()
        os_type = platform.system()
        os_version = platform.release()
        arch = platform.machine()
        python_version = platform.python_version()
        
        # Create deterministic machine hash
        machine_sig = f"{hostname}:{os_type}:{arch}".encode()
        machine_hash = hashlib.sha256(machine_sig).hexdigest()[:12]
        
        return cls(
            hostname=hostname,
            os_type=os_type,
            os_version=os_version,
            arch=arch,
            python_version=python_version,
            machine_hash=machine_hash
        )
    
    def matches(self, other: 'MachineIdentity') -> bool:
        """Check if this machine matches another (same OS/arch)."""
        return (self.os_type == other.os_type and 
                self.arch == other.arch)


@dataclass
class ExecutionCheckpoint:
    """Execution checkpoint for resumable phases."""
    phase_id: str
    stage_id: str
    timestamp: str
    machine_identity: Dict
    status: str
    progress: float  # 0.0-1.0
    completed_tests: int
    total_tests: int
    artifacts_path: str
    notes: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PhaseExecutionRecord:
    """Machine/OS tracking for phase execution."""
    phase_id: str
    execution_mode: str  # autonomous, manual, parallel
    approved_for_execution: bool
    machine_started_on: Optional[Dict]  # MachineIdentity dict
    machine_should_continue_on: Optional[Dict]  # MachineIdentity dict
    initiated_timestamp: Optional[str]
    last_heartbeat: Optional[str]
    status: str  # planned, in_progress, completed, failed, waiting_for_machine
    current_stage: Optional[str]
    checkpoint: Optional[ExecutionCheckpoint]
    next_phase_on_completion: Optional[str]  # Auto-launch next approved phase
    parallel_phases: List[str]  # Phases to run in parallel
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AutonomousPhaseExecutor:
    """
    Manages autonomous phase execution with:
    - Silent end-to-end execution
    - Machine/OS continuity tracking
    - Automatic teardown → next phase sequencing
    - Parallel phase support
    """
    
    def __init__(self, registry_root: str = "/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master"):
        self.registry_root = Path(registry_root)
        self.config_file = self.registry_root / "execution-queue-config.yaml"
        self.index_file = self.registry_root / "index.yaml"
        self.execution_dir = self.registry_root / "execution"
        self.execution_dir.mkdir(exist_ok=True)
        
        self.current_machine = MachineIdentity.current()
        
    def load_index(self) -> Dict:
        """Load master index."""
        with open(self.index_file) as f:
            return yaml.safe_load(f)
    
    def save_index(self, data: Dict):
        """Save master index."""
        with open(self.index_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def get_phase_config(self, phase_id: str) -> Dict:
        """Load phase configuration."""
        index = self.load_index()
        
        # Find phase in active_phases or execution_queue
        for phase in index.get("active_phases", []):
            if phase.get("id") == phase_id:
                return phase
        
        for phase in index.get("execution_queue", {}).get("autonomous_queue", []):
            if phase.get("id") == phase_id:
                return phase
        
        raise ValueError(f"Phase {phase_id} not found in index")
    
    def create_execution_record(
        self,
        phase_id: str,
        execution_mode: str = "autonomous",
        next_phase: Optional[str] = None,
        parallel_phases: Optional[List[str]] = None
    ) -> PhaseExecutionRecord:
        """Create machine-tracked execution record."""
        return PhaseExecutionRecord(
            phase_id=phase_id,
            execution_mode=execution_mode,
            approved_for_execution=True,
            machine_started_on=asdict(self.current_machine),
            machine_should_continue_on=asdict(self.current_machine),
            initiated_timestamp=datetime.utcnow().isoformat(),
            last_heartbeat=datetime.utcnow().isoformat(),
            status="planned",
            current_stage=None,
            checkpoint=None,
            next_phase_on_completion=next_phase,
            parallel_phases=parallel_phases or []
        )
    
    def can_execute_on_current_machine(
        self,
        phase_record: PhaseExecutionRecord
    ) -> Tuple[bool, str]:
        """
        Check if phase can execute on current machine.
        Returns: (can_execute, reason)
        """
        if not phase_record.machine_should_continue_on:
            return True, "No machine restriction"
        
        required_machine = MachineIdentity(**phase_record.machine_should_continue_on)
        
        if self.current_machine.matches(required_machine):
            return True, f"Machine matches: {self.current_machine.hostname}"
        else:
            return False, (
                f"Phase started on {required_machine.os_type}/{required_machine.arch}, "
                f"current machine is {self.current_machine.os_type}/{self.current_machine.arch}"
            )
    
    def save_execution_record(self, record: PhaseExecutionRecord):
        """Persist execution record."""
        record_file = self.execution_dir / f"{record.phase_id}-execution.json"
        with open(record_file, 'w') as f:
            json.dump(record.to_dict(), f, indent=2)
    
    def load_execution_record(self, phase_id: str) -> Optional[PhaseExecutionRecord]:
        """Load execution record if exists."""
        record_file = self.execution_dir / f"{phase_id}-execution.json"
        if not record_file.exists():
            return None
        
        with open(record_file) as f:
            data = json.load(f)
            return PhaseExecutionRecord(**data)
    
    def setup_autonomous_queue(
        self,
        phase_ids: List[str],
        parallel_config: Optional[Dict[str, List[str]]] = None
    ):
        """
        Configure autonomous execution queue.
        
        parallel_config: {
            "phase-52": ["phase-56-A", "phase-49"],  # S2-S6 runs, then parallel 56-A + 49
            ...
        }
        """
        index = self.load_index()
        
        # Ensure execution_queue section exists
        if "execution_queue" not in index:
            index["execution_queue"] = {
                "autonomous_queue": [],
                "parallel_groups": {},
                "sequential_teardown_chain": []
            }
        
        queue = index["execution_queue"]
        parallel_config = parallel_config or {}
        
        # Create execution records with auto-chaining
        execution_records = []
        for i, phase_id in enumerate(phase_ids):
            next_phase = phase_ids[i + 1] if i + 1 < len(phase_ids) else None
            parallel_phases = parallel_config.get(phase_id, [])
            
            record = self.create_execution_record(
                phase_id=phase_id,
                next_phase=next_phase,
                parallel_phases=parallel_phases
            )
            execution_records.append(record.to_dict())
        
        queue["autonomous_queue"] = execution_records
        queue["sequential_teardown_chain"] = phase_ids
        queue["parallel_groups"] = parallel_config
        queue["setup_timestamp"] = datetime.utcnow().isoformat()
        queue["machine_started_on"] = asdict(self.current_machine)
        
        self.save_index(index)
        return queue
    
    def get_next_executable_phase(self) -> Optional[str]:
        """Get next phase ready to execute on current machine."""
        index = self.load_index()
        queue = index.get("execution_queue", {}).get("autonomous_queue", [])
        
        for record_data in queue:
            record = PhaseExecutionRecord(**record_data)
            
            # Skip if not approved or already completed
            if not record.approved_for_execution or record.status == "completed":
                continue
            
            # Check machine compatibility
            can_execute, reason = self.can_execute_on_current_machine(record)
            if not can_execute:
                record.status = "waiting_for_machine"
                continue
            
            # Found executable phase
            return record.phase_id
        
        return None
    
    def mark_phase_started(self, phase_id: str):
        """Mark phase as in_progress."""
        index = self.load_index()
        queue = index.get("execution_queue", {}).get("autonomous_queue", [])
        
        for record_data in queue:
            if record_data.get("phase_id") == phase_id:
                record_data["status"] = "in_progress"
                record_data["initiated_timestamp"] = datetime.utcnow().isoformat()
                record_data["machine_started_on"] = asdict(self.current_machine)
                break
        
        self.save_index(index)
    
    def mark_phase_completed(self, phase_id: str, next_phase_id: Optional[str] = None):
        """Mark phase as completed and prep next phase."""
        index = self.load_index()
        queue = index.get("execution_queue", {}).get("autonomous_queue", [])
        
        for record_data in queue:
            if record_data.get("phase_id") == phase_id:
                record_data["status"] = "completed"
                break
        
        self.save_index(index)
        
        # If there's a next phase, it will be picked up by next executor run
        if next_phase_id:
            print(f"✅ Phase {phase_id} complete. Next: {next_phase_id}")
    
    def print_execution_plan(self):
        """Display execution plan."""
        index = self.load_index()
        queue = index.get("execution_queue", {})
        
        print("\n" + "="*80)
        print("🚀 CORTEX AUTONOMOUS EXECUTION PLAN")
        print("="*80)
        
        machine = queue.get("machine_started_on", {})
        print(f"\n🖥️  MACHINE: {machine.get('hostname')} ({machine.get('os_type')}/{machine.get('arch')})")
        
        print("\n📋 SEQUENTIAL EXECUTION CHAIN:")
        for phase_id in queue.get("sequential_teardown_chain", []):
            print(f"   → {phase_id}")
        
        parallel_groups = queue.get("parallel_groups", {})
        if parallel_groups:
            print("\n🔀 PARALLEL EXECUTION GROUPS:")
            for phase, parallel in parallel_groups.items():
                if parallel:
                    print(f"   {phase} ⟶ [{', '.join(parallel)}]")
        
        print("\n✅ APPROVED FOR AUTONOMOUS EXECUTION (NO USER INTERACTION REQUIRED)")
        print("="*80 + "\n")


# Example usage
if __name__ == "__main__":
    executor = AutonomousPhaseExecutor()
    
    # Setup autonomous queue with sequential + parallel execution
    approved_phases = [
        "phase-52",      # S2-S6 (17 days)
        "phase-56-A",    # Pilot (5 days, parallel with 49)
        "phase-48",      # Multi-tenant (8 days)
        "phase-49",      # Knowledge pipeline (6 days, parallel with 56-A)
        "phase-50",      # Storage (12 days)
        "phase-51",      # Secrets (parallel)
    ]
    
    parallel_config = {
        "phase-52": ["phase-56-A", "phase-49"],  # After 52, run 56-A and 49 in parallel
        "phase-56-A": [],
        "phase-49": [],
        "phase-48": [],
        "phase-50": ["phase-51"],  # After 50, run 51 in parallel
    }
    
    executor.setup_autonomous_queue(approved_phases, parallel_config)
    executor.print_execution_plan()

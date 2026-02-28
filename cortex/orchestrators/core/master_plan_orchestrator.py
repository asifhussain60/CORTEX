"""
CortexMasterPlanOrchestrator — CORTEX Phase Lifecycle Management

Dedicated orchestrator that owns the entire phase lifecycle for the CORTEX
repository. Responsible for:
  - Determining the next sequential phase number from cortex-master.yaml (SSOT)
  - Syncing _cortex-master/phases/ folders to match registry status
  - Creating new phase entries: registry first, then YAML file
  - Loading workflow templates for plan creation and execution

Authority: Phase 50 — CortexMasterPlanOrchestrator
CORE Rules:
  - CORE-008: TDD mandatory (tests in tests/golden/orchestrators/master_plan/)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-028: snake_case file naming
  - CORE-035: Single canonical implementation
  - CORE-048: Holistic validation gate
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 94e

logger = logging.getLogger(__name__)

# Valid priority values per CORTEX governance
_VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}

# Workflow template base path (relative to registry_root)
_WORKFLOW_TEMPLATE_DIR = Path("cortex-registry") / "workflows" / "templates" / "lifecycle"


# ============================================================================
# EXCEPTIONS
# ============================================================================


class PhaseLifecycleError(Exception):
    """Raised for all CortexMasterPlanOrchestrator lifecycle errors.

    Wraps lower-level errors (YAML parse failures, missing files, folder issues)
    into a single domain-specific exception hierarchy.
    """


# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class PhaseCreationRequest:
    """Request object for creating a new CORTEX phase.

    Attributes:
        title: Human-readable phase title (must be non-empty).
        description: Detailed description of phase scope.
        priority: CORTEX priority level — P0, P1, P2, or P3.
        supersedes: Optional list of prior phase IDs this phase replaces.
        governance_rules: CORE rules governing this phase.
    """

    title: str
    description: str
    priority: str
    supersedes: List[str] = field(default_factory=list)
    governance_rules: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate fields on construction."""
        if not self.title or not self.title.strip():
            raise ValueError("title must be a non-empty string")
        if self.priority not in _VALID_PRIORITIES:
            raise ValueError(
                f"priority must be one of {sorted(_VALID_PRIORITIES)}, got '{self.priority}'"
            )


@dataclass
class PhaseRecord:
    """Result object returned after successful phase creation.

    Attributes:
        phase_id: Canonical phase identifier (e.g. 'phase-04').
        sequence: Sequential integer (1-based).
        file_path: Absolute Path to the created YAML file.
        title: Phase title as provided in the request.
    """

    phase_id: str
    sequence: int
    file_path: Path
    title: str


@dataclass
class RegistrySyncResult:
    """Result of a sync_phase_folders() operation.

    Attributes:
        moved_to_completed: Count of files moved to completed/.
        moved_to_deferred: Count of files moved to deferred/.
        anomalies: List of descriptive anomaly strings (e.g. out-of-sequence IDs).
    """

    moved_to_completed: int = 0
    moved_to_deferred: int = 0
    anomalies: List[str] = field(default_factory=list)


# ============================================================================
# ORCHESTRATOR
# ============================================================================


class CortexMasterPlanOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin, WorkflowTemplateMixin):
    """Owns the complete CORTEX phase lifecycle for the CORTEX repository.

    This is the single canonical implementation (CORE-035) responsible for:
      1. Reading cortex-master.yaml to determine the next sequential phase number.
      2. Syncing _cortex-master/phases/ folders (planned/completed/deferred) to
         match status values in the registry.
      3. Creating new phase entries — registry entry first, YAML file second.
      4. Loading workflow templates for plan creation and autonomous execution.

    All status is maintained exclusively in cortex-master.yaml (SSOT per spec §4).
    Phase YAML files are execution specifications only.

    Example:
        orch = CortexMasterPlanOrchestrator(registry_root=Path("/path/to/CORTEX"))
        req = PhaseCreationRequest(title="New Phase", description="...", priority="P0")
        record = orch.create_phase(req)
    """

    # Phase 94e — advisory: plan-management orchestrator; not a primary code-execution
    # entry point. Gateway routing deferred until MasterOrchestrator milestone.
    PHASE90_GATEWAY_ENABLED: bool = False

    def __init__(self, registry_root: Optional[Path] = None) -> None:
        """Initialise the orchestrator and validate the registry structure.

        Args:
            registry_root: Root of the CORTEX workspace. Defaults to the project
                root (3 levels up from this file's location).

        Raises:
            PhaseLifecycleError: If registry file is missing, unreadable, or corrupt,
                or if required phase folders don't exist.
        """
        if registry_root is None:
            # Default: cortex/orchestrators/core/ → project root
            registry_root = Path(__file__).resolve().parents[3]

        self._root = Path(registry_root)
        self._registry_path = self._root / "cortex-registry" / "cortex-master.yaml"
        self._phases_dir = self._root / "cortex-registry" / "_cortex-master" / "phases"
        self._workflow_template_dir = self._root / _WORKFLOW_TEMPLATE_DIR

        self._validate_structure()

    # -------------------------------------------------------------------------
    # Workflow Template Integration
    # -------------------------------------------------------------------------

    def get_recommended_template(self) -> str:
        """Get the recommended workflow template for master plan operations."""
        return "lifecycle/master-plan-execution"

    # -------------------------------------------------------------------------
    # PRIVATE: Validation
    # -------------------------------------------------------------------------

    def _validate_structure(self) -> None:
        """Validate that required files and folders exist.

        Raises:
            PhaseLifecycleError: On any structural problem.
        """
        if not self._registry_path.exists():
            raise PhaseLifecycleError(
                f"registry not found: {self._registry_path}. "
                "Ensure cortex-registry/cortex-master.yaml exists."
            )

        # Validate YAML is parseable
        try:
            self._load_registry()
        except PhaseLifecycleError:
            raise
        except Exception as exc:
            raise PhaseLifecycleError(f"corrupt registry YAML: {exc}") from exc

        for folder in ("planned", "completed", "deferred"):
            folder_path = self._phases_dir / folder
            if not folder_path.exists():
                raise PhaseLifecycleError(
                    f"required phase folder missing: {folder_path}. "
                    "Run: mkdir -p cortex-registry/_cortex-master/phases/{planned,completed,deferred}"
                )

    # -------------------------------------------------------------------------
    # PRIVATE: Registry I/O
    # -------------------------------------------------------------------------

    def _load_registry(self) -> Dict[str, Any]:
        """Load and parse cortex-master.yaml.

        Returns:
            Parsed registry dict.

        Raises:
            PhaseLifecycleError: If the file is corrupt or unreadable.
        """
        try:
            content = self._registry_path.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                raise PhaseLifecycleError("corrupt registry YAML: top-level is not a mapping")
            return data
        except yaml.YAMLError as exc:
            raise PhaseLifecycleError(f"corrupt registry YAML: {exc}") from exc
        except PhaseLifecycleError:
            raise
        except OSError as exc:
            raise PhaseLifecycleError(f"cannot read registry: {exc}") from exc

    def _save_registry(self, data: Dict[str, Any]) -> None:
        """Write registry data back to cortex-master.yaml.

        Args:
            data: The registry dict to serialise.
        """
        self._registry_path.write_text(
            yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    # -------------------------------------------------------------------------
    # PRIVATE: Helpers
    # -------------------------------------------------------------------------

    def _sequential_phases(self, registry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return only phases with a valid integer sequence field, sorted ascending.

        Anomalous phases (sequence > total sequential count by a wide margin) are
        excluded from sequence computation to prevent phase-100-style anomalies.

        Handles two cortex-master.yaml formats:
        - Legacy flat list:  phases: [{id: ..., sequence: 1}, ...]
        - Structured dict:   phases: {completed: [...], planned: [...], deferred: [...]}
          (introduced in cortex-master.yaml v10.1 — 2026-02-22)

        Args:
            registry: Parsed registry dict.

        Returns:
            List of phase dicts sorted by sequence ascending.
        """
        raw = registry.get("phases", []) or []

        # Normalise: if phases is a dict (structured format), flatten all sub-lists
        if isinstance(raw, dict):
            phase_list: List[Dict[str, Any]] = []
            for sub in raw.values():
                if isinstance(sub, list):
                    phase_list.extend(sub)
            raw = phase_list

        valid = []
        for p in raw:
            if not isinstance(p, dict):
                continue  # skip non-dict entries (e.g. plain strings)
            seq = p.get("sequence")
            if isinstance(seq, int) and seq > 0:
                valid.append(p)
        return sorted(valid, key=lambda p: p["sequence"])

    @staticmethod
    def _title_to_slug(title: str) -> str:
        """Convert a phase title to a CORE-028-compliant file slug.

        Converts to lowercase, replaces non-alphanumeric chars with hyphens,
        collapses multiple hyphens, strips leading/trailing hyphens.

        Args:
            title: Human-readable phase title.

        Returns:
            slug: e.g. 'CORTEX: Master-Plan (v2)' → 'cortex-master-plan-v2'
        """
        slug = title.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        slug = slug.strip("-")
        return slug

    @staticmethod
    def _phase_id_from_sequence(sequence: int) -> str:
        """Generate a phase ID from a sequence number.

        Args:
            sequence: 1-based sequence integer.

        Returns:
            Phase ID string, e.g. 'phase-04' for sequence=4, 'phase-100' for 100.
        """
        if sequence < 100:
            return f"phase-{sequence:02d}"
        return f"phase-{sequence}"

    # -------------------------------------------------------------------------
    # PUBLIC: next_sequence_number
    # -------------------------------------------------------------------------

    def next_sequence_number(self) -> int:
        """Compute the next sequential phase number from cortex-master.yaml.

        Reads only sequential phases (ignoring anomalous out-of-order IDs).
        Returns max(existing_sequences) + 1, or 1 if no phases exist.

        Returns:
            The next integer sequence number.
        """
        registry = self._load_registry()
        sequential = self._sequential_phases(registry)

        if not sequential:
            return 1

        # Find the highest SEQUENTIAL sequence — ignore anomalous gaps
        # e.g. phases [1,2,3,4,100] → highest sequential = 4 → next = 5
        sequences = [p["sequence"] for p in sequential]
        sequences_sorted = sorted(sequences)

        # Walk the sorted list to find the last gapless sequential number
        last_sequential = 0
        for seq in sequences_sorted:
            if seq <= last_sequential + 1:
                # Either contiguous or a gap of 1 — accept as sequential
                last_sequential = seq
            # If there's a large jump (anomaly like 100), stop at last valid

        return last_sequential + 1

    # -------------------------------------------------------------------------
    # PUBLIC: sync_phase_folders
    # -------------------------------------------------------------------------

    def sync_phase_folders(self) -> RegistrySyncResult:
        """Move phase YAML files to folders that match their status in the registry.

        Scans planned/ for files whose status in cortex-master.yaml is 'complete'
        and moves them to completed/. Also detects anomalous phase IDs (where the
        sequence number in the filename far exceeds the actual phase count).

        Returns:
            RegistrySyncResult with counts and anomaly descriptions.
        """
        result = RegistrySyncResult()
        registry = self._load_registry()

        # Build a status map: phase_id → status from registry
        status_map: Dict[str, str] = {}
        raw_phases = registry.get("phases", []) or []
        # Normalise: phases may be a structured dict (v10.1+) or a flat list (legacy)
        if isinstance(raw_phases, dict):
            flat_phases: List[Dict[str, Any]] = []
            for sub in raw_phases.values():
                if isinstance(sub, list):
                    flat_phases.extend(sub)
            raw_phases = flat_phases
        for phase in raw_phases:
            if not isinstance(phase, dict):
                continue
            pid = phase.get("id", "")
            status = phase.get("status", "").lower()
            if pid:
                status_map[pid] = status

        # Check completed_late_additions too
        for phase in registry.get("completed_late_additions", []) or []:
            pid = phase.get("id", "")
            status = phase.get("status", "").upper()
            if pid and status == "COMPLETE":
                status_map[pid] = "complete"

        planned_dir = self._phases_dir / "planned"
        completed_dir = self._phases_dir / "completed"
        total_known_phases = registry.get("metadata", {}).get("total_phases", 0) or 0

        for yaml_file in sorted(planned_dir.iterdir()):
            if not yaml_file.suffix == ".yaml":
                continue

            # Extract phase ID from filename (e.g. phase-04-some-title.yaml → phase-04)
            parts = yaml_file.stem.split("-")
            if len(parts) >= 2:
                try:
                    seq_num = int(parts[1])
                    phase_id = f"phase-{parts[1]}"  # preserves zero-padding from filename

                    # Anomaly detection: sequence >> total known phases
                    if seq_num > max(total_known_phases, 49) + 10:
                        result.anomalies.append(
                            f"{yaml_file.name}: sequence {seq_num} far exceeds "
                            f"total_phases ({total_known_phases}) — anomalous numbering"
                        )

                    # Move to completed if registry says complete
                    file_status = status_map.get(phase_id, "")
                    if file_status in ("complete", "COMPLETE"):
                        destination = completed_dir / yaml_file.name
                        yaml_file.rename(destination)
                        result.moved_to_completed += 1
                        logger.info("sync: moved %s → completed/", yaml_file.name)

                except (ValueError, IndexError):
                    pass  # Non-standard filename, skip

        return result

    # -------------------------------------------------------------------------
    # PUBLIC: create_phase
    # -------------------------------------------------------------------------

    def create_phase(self, request: PhaseCreationRequest) -> PhaseRecord:
        """Create a new CORTEX phase: registry entry first, then YAML file.

        Steps (per spec):
          1. Sync phase folders (moves completed phases out of planned/)
          2. Compute next sequential number from clean registry
          3. Write entry to cortex-master.yaml FIRST (registry is SSOT)
          4. Write YAML file to planned/ folder

        Args:
            request: PhaseCreationRequest with title, description, priority.

        Returns:
            PhaseRecord with the new phase_id, sequence, and file_path.

        Raises:
            PhaseLifecycleError: If registry write or file creation fails.
        """
        # Phase 58: activate cross-cutting hooks (LENS + knowledge synthesis)
        self._activate_cross_cutting_hooks(
            operation="create_phase",
            orchestrator_context=None,
            unified_context=None,
        )
        # Step 1: Sync folders so sequence is computed from clean state
        self.sync_phase_folders()

        # Step 2: Determine next sequence
        sequence = self.next_sequence_number()
        phase_id = self._phase_id_from_sequence(sequence)
        slug = self._title_to_slug(request.title)
        file_name = f"{phase_id}-{slug}.yaml"
        file_path = self._phases_dir / "planned" / file_name

        # Step 3: Write registry entry FIRST
        registry = self._load_registry()
        # Normalise: phases may be a structured dict (v10.1+) or a flat list (legacy).
        # New phases are always written into phases.planned list.
        raw = registry.get("phases") or []
        if isinstance(raw, dict):
            # Structured format: append to the planned sub-list
            planned_list = raw.setdefault("planned", [])
            if not isinstance(planned_list, list):
                planned_list = []
                raw["planned"] = planned_list
            planned_list.append({
                "id": phase_id,
                "title": request.title,
                "status": "planned",
                "sequence": sequence,
                "priority": request.priority,
                "description": request.description,
                "file": str(file_path.relative_to(self._root)),
                "created": "2026-02-19",
            })
            registry["phases"] = raw
        else:
            # Legacy flat list format
            if not isinstance(raw, list):
                raw = []
            raw.append({
                "id": phase_id,
                "title": request.title,
                "status": "planned",
                "sequence": sequence,
                "priority": request.priority,
                "description": request.description,
                "file": str(file_path.relative_to(self._root)),
                "created": "2026-02-19",
            })
            registry["phases"] = raw

        # Update metadata counters
        meta = registry.setdefault("metadata", {})
        meta["total_phases"] = int(meta.get("total_phases", 0)) + 1
        meta["planned"] = int(meta.get("planned", 0)) + 1
        meta["last_updated"] = "2026-02-19T00:00:00Z"

        self._save_registry(registry)
        logger.info("create_phase: registry updated with %s", phase_id)

        # Step 4: Write YAML file
        phase_content = {
            "metadata": {
                "phase_id": phase_id,
                "title": request.title,
                "sequence": sequence,
                "priority": request.priority,
                "description": request.description,
                "status_authority": "cortex-master.yaml",
                "created": "2026-02-19",
                "governance_rules": request.governance_rules or [
                    "CORE-008: TDD mandatory",
                    "CORE-011: Type hints",
                    "CORE-012: Docstrings",
                    "CORE-028: snake_case naming",
                    "CORE-035: Single canonical implementation",
                ],
                "supersedes": request.supersedes,
            },
            "stages": [],
            "tests": {
                "golden": f"tests/golden/orchestrators/{slug}/",
                "unit": f"tests/unit/orchestrators/{slug}/",
                "integration": f"tests/integration/",
            },
            "workflow_template": "cortex-registry/workflows/templates/lifecycle/master-plan-execution.yaml",
        }

        try:
            file_path.write_text(
                yaml.dump(phase_content, default_flow_style=False, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
        except OSError as exc:
            raise PhaseLifecycleError(f"cannot write phase file {file_path}: {exc}") from exc

        logger.info("create_phase: file created at %s", file_path)

        return PhaseRecord(
            phase_id=phase_id,
            sequence=sequence,
            file_path=file_path,
            title=request.title,
        )

    # -------------------------------------------------------------------------
    # PUBLIC: load_workflow_template
    # -------------------------------------------------------------------------

    def load_workflow_template(self, template_name: str) -> Dict[str, Any]:
        """Load a workflow template YAML by name from the lifecycle templates folder.

        Args:
            template_name: Template file name without .yaml extension.
                e.g. 'master-plan-orchestrator' or 'master-plan-execution'

        Returns:
            Parsed template dict with a 'workflow' top-level key.

        Raises:
            PhaseLifecycleError: If the template file does not exist or is corrupt.
        """
        template_path = self._workflow_template_dir / f"{template_name}.yaml"
        if not template_path.exists():
            raise PhaseLifecycleError(
                f"template not found: {template_path}. "
                f"Available templates are in: {self._workflow_template_dir}"
            )

        try:
            data = yaml.safe_load(template_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise PhaseLifecycleError(f"corrupt template YAML '{template_name}': {exc}") from exc

        if not isinstance(data, dict) or "workflow" not in data:
            raise PhaseLifecycleError(
                f"invalid template '{template_name}': must have a top-level 'workflow' key"
            )

        return data

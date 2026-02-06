"""
Phase Manager - Intelligent Phase Resolution and Lifecycle Management

Implements Phase 25 intelligent phase resolution algorithm for determining
whether to CREATE, UPDATE, DEPRECATE, or COMPLETE phases based on user requests.

AC-ID: PHASE-25-STAGE-1-001
Authority: phase-25-plan-mode-cortex-architect.yaml
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import yaml
import re

from cortex.models.canonical_enums import IntentType


class PhaseOperation(Enum):
    """Phase operation types."""
    CREATE = "create"
    UPDATE = "update"
    DEPRECATE = "deprecate"
    COMPLETE = "complete"


@dataclass
class PhaseMatchScore:
    """Detailed match score breakdown."""
    keyword_score: float
    component_score: float
    scope_score: float
    total_score: float
    
    def __post_init__(self):
        """Validate score ranges."""
        assert 0.0 <= self.total_score <= 1.0, "Total score must be 0.0-1.0"


@dataclass
class PhaseResolutionResult:
    """Result of phase resolution analysis."""
    operation: PhaseOperation
    matched_phase_id: Optional[str]
    match_score: float
    rationale: str
    confidence: float
    
    def __post_init__(self):
        """Validate confidence range."""
        assert 0.0 <= self.confidence <= 1.0, "Confidence must be 0.0-1.0"


@dataclass
class PhaseSyncStatus:
    """3-source sync verification status."""
    all_synced: bool
    registry_passed: bool
    implementation_passed: bool
    dashboard_passed: bool
    failures: List[str]
    
    def __init__(self):
        """Initialize with default values."""
        self.all_synced = False
        self.registry_passed = False
        self.implementation_passed = False
        self.dashboard_passed = False
        self.failures = []


class PhaseManager:
    """
    Manages CORTEX phase lifecycle with intelligent resolution.
    
    Responsibilities:
    - Intelligent phase resolution (CREATE vs UPDATE vs DEPRECATE)
    - Phase CRUD operations
    - ROI-based prioritization
    - 3-source sync verification
    - Dashboard integration
    
    Usage:
        manager = PhaseManager(registry_root="cortex-registry/_cortex-master")
        result = manager.resolve_phase_operation("add MCP tools to PLAN MODE")
        
        if result.operation == PhaseOperation.UPDATE:
            manager.update_phase(result.matched_phase_id, {...})
    """
    
    # Keyword sets for intelligent detection
    DELETION_KEYWORDS = {
        "remove", "delete", "deprecate", "retire", "decommission",
        "eliminate", "drop", "purge", "uninstall"
    }
    
    COMPLETION_KEYWORDS = {
        "complete", "finish", "done", "finalize", "conclude",
        "wrap up", "close out", "mark complete"
    }
    
    # ROI scoring weights (from phase-25 spec)
    ROI_WEIGHTS = {
        "architectural_impact": 0.35,
        "efficiency_gain": 0.25,
        "accuracy_improvement": 0.20,
        "effort_cost": 0.15,
        "blocking_severity": 0.05,
    }
    
    # Priority thresholds
    HIGH_ROI_THRESHOLD = 0.75
    MEDIUM_ROI_THRESHOLD = 0.60
    LOW_ROI_THRESHOLD = 0.40
    
    def __init__(self, registry_root: str = "cortex-registry/_cortex-master"):
        """
        Initialize PhaseManager.
        
        Args:
            registry_root: Path to master registry root
        """
        self.registry_root = Path(registry_root)
        self.index_path = self.registry_root / "index.yaml"
        self.active_phases_dir = self.registry_root / "phases" / "active"
        self.completed_phases_dir = self.registry_root / "phases" / "completed"
        self.deprecated_phases_dir = self.registry_root / "phases" / "deprecated"
        
    def resolve_phase_operation(
        self,
        user_request: str,
        intent_type: Optional[IntentType] = None
    ) -> PhaseResolutionResult:
        """
        Intelligently determine phase operation from user request.
        
        Implements 4-step algorithm from phase-25 spec:
        1. Load context (index.yaml)
        2. Semantic analysis (keywords, components, change type)
        3. Phase matching (score each active phase)
        4. Operation decision (CREATE/UPDATE/DEPRECATE based on threshold)
        
        Args:
            user_request: User's natural language request
            intent_type: Optional pre-classified intent
            
        Returns:
            PhaseResolutionResult with operation and rationale
        """
        # Step 1: Load context
        index_data = self._load_index()
        active_phases = index_data.get("active_phases", [])
        
        # Step 2: Semantic analysis
        request_lower = user_request.lower()
        keywords = self._extract_keywords(request_lower)
        
        # Check for deletion intent first
        if any(kw in request_lower for kw in self.DELETION_KEYWORDS):
            # Find phase to deprecate
            for phase in active_phases:
                if self._phase_matches_keywords(phase, keywords):
                    return PhaseResolutionResult(
                        operation=PhaseOperation.DEPRECATE,
                        matched_phase_id=phase["id"],
                        match_score=0.9,
                        rationale=f"Deletion keywords detected: {', '.join(self.DELETION_KEYWORDS & set(request_lower.split()))}",
                        confidence=0.95
                    )
        
        # Check for completion intent
        if any(kw in request_lower for kw in self.COMPLETION_KEYWORDS):
            for phase in active_phases:
                if self._phase_matches_keywords(phase, keywords):
                    return PhaseResolutionResult(
                        operation=PhaseOperation.COMPLETE,
                        matched_phase_id=phase["id"],
                        match_score=0.9,
                        rationale=f"Completion keywords detected",
                        confidence=0.95
                    )
        
        # Step 3: Phase matching - score each active phase
        best_match = None
        best_score = 0.0
        
        for phase in active_phases:
            score = self._calculate_match_score(phase, user_request)
            if score.total_score > best_score:
                best_score = score.total_score
                best_match = (phase, score)
        
        # Step 4: Operation decision based on threshold
        if best_match and best_score >= 0.8:
            phase, score = best_match
            return PhaseResolutionResult(
                operation=PhaseOperation.UPDATE,
                matched_phase_id=phase["id"],
                match_score=best_score,
                rationale=f"Strong alignment with {phase['name']} (keyword: {score.keyword_score:.1%}, component: {score.component_score:.1%}, scope: {score.scope_score:.1%})",
                confidence=0.9
            )
        elif best_match and best_score >= 0.6:
            phase, score = best_match
            return PhaseResolutionResult(
                operation=PhaseOperation.UPDATE,
                matched_phase_id=phase["id"],
                match_score=best_score,
                rationale=f"Partial alignment with {phase['name']} - consider expanding scope",
                confidence=0.7
            )
        else:
            # No good match - create new phase
            return PhaseResolutionResult(
                operation=PhaseOperation.CREATE,
                matched_phase_id=None,
                match_score=best_score,
                rationale="No existing phase matches request - new significant work requires dedicated phase",
                confidence=0.8
            )
    
    def _calculate_match_score(self, phase: Dict, request: str) -> PhaseMatchScore:
        """
        Calculate match score using 3-factor algorithm.
        
        Factors (from phase-25 spec):
        - Keyword overlap: 40% weight
        - Component alignment: 30% weight
        - Scope compatibility: 30% weight
        
        Args:
            phase: Phase dictionary from index.yaml
            request: User request string
            
        Returns:
            PhaseMatchScore with breakdown
        """
        request_lower = request.lower()
        request_keywords = set(self._extract_keywords(request_lower))
        
        # Factor 1: Keyword matching (40%)
        phase_text = f"{phase.get('name', '')} {phase.get('description', '')}".lower()
        phase_keywords = set(self._extract_keywords(phase_text))
        
        if phase_keywords and request_keywords:
            # Calculate overlap based on request keywords found in phase
            overlap = len(request_keywords & phase_keywords) / len(request_keywords)
            keyword_score = overlap * 0.4
        else:
            keyword_score = 0.0
        
        # Factor 2: Component alignment (30%)
        component_score = 0.0
        phase_components = self._extract_components(phase)
        request_components = self._extract_components_from_text(request_lower)
        
        if phase_components & request_components:
            component_score = 0.3
        
        # Factor 3: Scope compatibility (30%)
        scope_score = 0.0
        if phase.get("status") == "in-progress":
            # IN_PROGRESS phases get higher match preference
            if self._similar_scope(phase, request_lower):
                scope_score = 0.3
        
        total_score = keyword_score + component_score + scope_score
        
        return PhaseMatchScore(
            keyword_score=keyword_score,
            component_score=component_score,
            scope_score=scope_score,
            total_score=min(total_score, 1.0)
        )
    
    def create_phase(self, phase_data: Dict[str, Any]) -> str:
        """
        Create new phase with generated phase-{N}-{kebab-name}.yaml.
        
        Args:
            phase_data: Phase metadata (name, priority, description, deliverables)
            
        Returns:
            phase_id: Generated phase ID (e.g., "phase-33")
        """
        # Generate phase ID
        index_data = self._load_index()
        next_phase_num = self._get_next_phase_number(index_data)
        phase_id = f"phase-{next_phase_num}"
        
        # Create kebab-case filename
        kebab_name = self._to_kebab_case(phase_data["name"])
        filename = f"{phase_id}-{kebab_name}.yaml"
        
        # Build phase YAML structure
        phase_yaml = {
            "metadata": {
                "phase": str(next_phase_num),
                "title": phase_data["name"],
                "version": "1.0",
                "status": "PLANNED",
                "author": "Asif Hussain",
                "created": datetime.now().strftime("%Y-%m-%d"),
                "priority": phase_data.get("priority", "P1"),
                "estimated_effort": phase_data.get("estimated_effort", "TBD"),
            },
            "vision": {
                "mission": phase_data.get("description", ""),
                "key_outcomes": phase_data.get("deliverables", []),
            },
            "implementation": {
                "deliverables": phase_data.get("deliverables", []),
            },
        }
        
        # Add ROI metadata if provided
        if "roi_score" in phase_data:
            phase_yaml["metadata"]["roi_score"] = phase_data["roi_score"]
            phase_yaml["metadata"]["priority_tier"] = self.get_priority_tier(phase_data)
        
        # Save phase YAML
        self._save_phase_yaml(phase_yaml, str(filename))
        
        # Update index.yaml
        self._update_index_add_phase(phase_id, str(filename), phase_data)
        
        return phase_id
    
    def update_phase(self, phase_id: str, updates: Dict[str, Any]) -> None:
        """
        Update existing phase with new data.
        
        Args:
            phase_id: Phase ID to update
            updates: Dictionary of updates to apply
        """
        # Load existing phase
        phase_data = self._load_phase_yaml(phase_id)
        
        # Ensure implementation section exists
        if "implementation" not in phase_data:
            phase_data["implementation"] = {"deliverables": []}
        
        # Apply updates to metadata
        if "status" in updates:
            phase_data["metadata"]["status"] = updates["status"]
        if "progress" in updates:
            phase_data["metadata"]["progress"] = updates["progress"]
        
        # Apply updates to implementation
        if "new_deliverable" in updates:
            phase_data["implementation"]["deliverables"].append(updates["new_deliverable"])
        
        # Save updated phase
        filename = self._get_phase_filename(phase_id)
        self._save_phase_yaml(phase_data, str(filename.name))
        
        # Update index.yaml
        self._update_index_modify_phase(phase_id, updates)
    
    def deprecate_phase(self, phase_id: str, reason: str) -> None:
        """
        Deprecate phase (move to deprecated/ folder).
        
        Args:
            phase_id: Phase ID to deprecate
            reason: Deprecation reason
        """
        # Load phase data
        phase_data = self._load_phase_yaml(phase_id)
        
        # Add deprecation metadata
        phase_data["metadata"]["status"] = "DEPRECATED"
        phase_data["metadata"]["deprecated_date"] = datetime.now().strftime("%Y-%m-%d")
        phase_data["metadata"]["deprecation_reason"] = reason
        
        # Get current filename
        current_file = self._get_phase_filename(phase_id)
        
        # Move to deprecated/ folder
        deprecated_file = self.deprecated_phases_dir / current_file.name
        self._move_phase_file(current_file, deprecated_file)
        
        # Save updated metadata
        self._save_phase_yaml(phase_data, str(deprecated_file.name), folder="deprecated")
        
        # Update index.yaml
        self._update_index(remove_active=phase_id)
    
    def complete_phase(self, phase_id: str) -> None:
        """
        Complete phase (move to completed/2026/ folder).
        
        Args:
            phase_id: Phase ID to complete
            
        Raises:
            ValueError: If completion criteria not met
        """
        # Verify completion criteria
        if not self._verify_completion_criteria(phase_id):
            raise ValueError(
                f"Completion criteria not met for {phase_id}. "
                "Verify all deliverables complete and sync verification passes."
            )
        
        # Load phase data
        phase_data = self._load_phase_yaml(phase_id)
        
        # Update metadata
        phase_data["metadata"]["status"] = "COMPLETED"
        phase_data["metadata"]["completed_date"] = datetime.now().strftime("%Y-%m-%d")
        
        # Get current filename
        current_file = self._get_phase_filename(phase_id)
        
        # Move to completed/2026/ folder
        year = datetime.now().year
        completed_dir = self.completed_phases_dir / str(year)
        completed_dir.mkdir(parents=True, exist_ok=True)
        completed_file = completed_dir / current_file.name
        
        self._move_phase_file(current_file, completed_file)
        
        # Save updated metadata
        self._save_phase_yaml(phase_data, str(current_file.name), folder=f"completed/{year}")
        
        # Update index.yaml
        self._update_index(remove_active=phase_id, add_completed=phase_id)
    
    def calculate_roi_score(self, phase_metrics: Dict[str, float]) -> float:
        """
        Calculate ROI score using weighted formula from phase-25 spec.
        
        Formula:
            ROI = (arch_impact * 0.35) + (efficiency * 0.25) + 
                  (accuracy * 0.20) + ((1 - effort) * 0.15) + 
                  (blocking * 0.05)
        
        Args:
            phase_metrics: Dictionary with 5 dimensions (0.0-1.0 each)
            
        Returns:
            roi_score: Weighted score (0.0-1.0)
        """
        arch_impact = phase_metrics.get("architectural_impact", 0.0)
        efficiency = phase_metrics.get("efficiency_gain", 0.0)
        accuracy = phase_metrics.get("accuracy_improvement", 0.0)
        effort = phase_metrics.get("effort_cost", 0.0)
        blocking = phase_metrics.get("blocking_severity", 0.0)
        
        roi_score = (
            (arch_impact * self.ROI_WEIGHTS["architectural_impact"]) +
            (efficiency * self.ROI_WEIGHTS["efficiency_gain"]) +
            (accuracy * self.ROI_WEIGHTS["accuracy_improvement"]) +
            ((1.0 - effort) * self.ROI_WEIGHTS["effort_cost"]) +  # Inverted
            (blocking * self.ROI_WEIGHTS["blocking_severity"])
        )
        
        return round(roi_score, 4)
    
    def get_priority_tier(self, phase_metrics: Dict[str, float]) -> str:
        """
        Determine priority tier from ROI score.
        
        Args:
            phase_metrics: Phase metrics dictionary
            
        Returns:
            Priority tier: "HIGH" | "MEDIUM" | "LOW" | "DEFER"
        """
        roi_score = self.calculate_roi_score(phase_metrics)
        
        if roi_score >= self.HIGH_ROI_THRESHOLD:
            return "HIGH"
        elif roi_score >= self.MEDIUM_ROI_THRESHOLD:
            return "MEDIUM"
        elif roi_score >= self.LOW_ROI_THRESHOLD:
            return "LOW"
        else:
            return "DEFER"
    
    def prioritize_pending_phases(self) -> List[Dict]:
        """
        Prioritize pending phases by ROI score.
        
        Returns:
            List of phases sorted by ROI score (descending)
        """
        phases = self._load_pending_phases()
        
        # Sort by ROI score
        sorted_phases = sorted(
            phases,
            key=lambda p: p.get("roi_score", 0.0),
            reverse=True
        )
        
        return sorted_phases
    
    def verify_sync_before_completion(self, phase_id: str) -> PhaseSyncStatus:
        """
        Verify 3-source sync before allowing phase completion.
        
        Sources:
        1. Master Plan Registry (index.yaml)
        2. CORTEX Live Implementation (code files)
        3. Dashboard HTML (plan-summary.json + index.html)
        
        Args:
            phase_id: Phase ID to verify
            
        Returns:
            PhaseSyncStatus with detailed verification results
        """
        status = PhaseSyncStatus()
        
        # Source 1: Registry check
        status.registry_passed = self._verify_registry_sync(phase_id)
        if not status.registry_passed:
            status.failures.append("Registry: Phase status/deliverables inconsistent")
        
        # Source 2: Implementation check
        status.implementation_passed = self._verify_implementation_sync(phase_id)
        if not status.implementation_passed:
            status.failures.append("Implementation: Files missing or tests failing")
        
        # Source 3: Dashboard check
        status.dashboard_passed = self._verify_dashboard_sync(phase_id)
        if not status.dashboard_passed:
            status.failures.append("Dashboard: JSON/HTML out of sync with registry")
        
        # Overall sync status
        status.all_synced = (
            status.registry_passed and
            status.implementation_passed and
            status.dashboard_passed
        )
        
        return status
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    def _load_index(self) -> Dict:
        """Load index.yaml."""
        if not self.index_path.exists():
            return {"active_phases": [], "statistics": {}}
        
        with open(self.index_path, 'r') as f:
            return yaml.safe_load(f) or {}
    
    def _save_phase_yaml(self, data: Dict, filename: str, folder: str = "active") -> None:
        """Save phase YAML to file."""
        if folder == "active":
            target_dir = self.active_phases_dir
        elif folder.startswith("completed"):
            year = folder.split("/")[1] if "/" in folder else str(datetime.now().year)
            target_dir = self.completed_phases_dir / year
        elif folder == "deprecated":
            target_dir = self.deprecated_phases_dir
        else:
            target_dir = self.active_phases_dir
        
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / filename
        
        with open(target_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def _load_phase_yaml(self, phase_id: str) -> Dict:
        """Load phase YAML by ID."""
        filename = self._get_phase_filename(phase_id)
        
        with open(filename, 'r') as f:
            return yaml.safe_load(f)
    
    def _get_phase_filename(self, phase_id: str) -> Path:
        """Get full path to phase file."""
        # Search active phases
        for file in self.active_phases_dir.glob(f"{phase_id}-*.yaml"):
            return file
        
        # Search completed phases
        for file in self.completed_phases_dir.rglob(f"{phase_id}-*.yaml"):
            return file
        
        raise FileNotFoundError(f"Phase {phase_id} not found")
    
    def _move_phase_file(self, source: Path, destination: Path) -> None:
        """Move phase file to new location."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.rename(destination)
    
    def _update_index(
        self,
        remove_active: Optional[str] = None,
        add_completed: Optional[str] = None
    ) -> None:
        """Update index.yaml statistics."""
        index_data = self._load_index()
        
        if remove_active:
            index_data["active_phases"] = [
                p for p in index_data["active_phases"]
                if p["id"] != remove_active
            ]
        
        if add_completed:
            if "completed_phases_2026" not in index_data:
                index_data["completed_phases_2026"] = {"count": 0, "phases": []}
            index_data["completed_phases_2026"]["count"] += 1
        
        # Update statistics
        index_data["statistics"]["active_phases"] = len(index_data.get("active_phases", []))
        
        with open(self.index_path, 'w') as f:
            yaml.dump(index_data, f, default_flow_style=False, sort_keys=False)
    
    def _update_index_add_phase(self, phase_id: str, filename: str, phase_data: Dict) -> None:
        """Add new phase to index.yaml."""
        index_data = self._load_index()
        
        new_phase = {
            "id": phase_id,
            "name": phase_data["name"],
            "file": f"phases/active/{filename}",
            "status": "planned",
            "priority": phase_data.get("priority", "P1"),
            "description": phase_data.get("description", ""),
        }
        
        if "roi_score" in phase_data:
            new_phase["roi_score"] = phase_data["roi_score"]
        
        index_data.setdefault("active_phases", []).append(new_phase)
        index_data.setdefault("statistics", {})["active_phases"] = len(index_data["active_phases"])
        
        with open(self.index_path, 'w') as f:
            yaml.dump(index_data, f, default_flow_style=False, sort_keys=False)
    
    def _update_index_modify_phase(self, phase_id: str, updates: Dict) -> None:
        """Update existing phase in index.yaml."""
        index_data = self._load_index()
        
        for phase in index_data.get("active_phases", []):
            if phase["id"] == phase_id:
                if "status" in updates:
                    phase["status"] = updates["status"]
                if "progress" in updates:
                    phase["progress"] = updates["progress"]
                break
        
        with open(self.index_path, 'w') as f:
            yaml.dump(index_data, f, default_flow_style=False, sort_keys=False)
    
    def _get_next_phase_number(self, index_data: Dict) -> int:
        """Determine next phase number."""
        active_phases = index_data.get("active_phases", [])
        completed = index_data.get("statistics", {}).get("total_phases", 0)
        
        # Extract phase numbers
        phase_numbers = []
        for phase in active_phases:
            match = re.match(r"phase-(\d+)", phase["id"])
            if match:
                phase_numbers.append(int(match.group(1)))
        
        return max(phase_numbers + [completed]) + 1 if phase_numbers else completed + 1
    
    def _to_kebab_case(self, text: str) -> str:
        """Convert text to kebab-case."""
        text = re.sub(r'[^\w\s-]', '', text.lower())
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')[:40]  # CORE-028: ≤40 chars
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        words = re.findall(r'\w+', text.lower())
        return [w for w in words if w not in stop_words and len(w) > 2]
    
    def _extract_components(self, phase: Dict) -> set:
        """Extract component names from phase data."""
        components = set()
        
        # Extract from name and description
        text = f"{phase.get('name', '')} {phase.get('description', '')}".lower()
        
        # Common CORTEX components
        cortex_components = {
            "orchestrator", "mcp", "dashboard", "registry", "lens",
            "wiring", "prompt", "agent", "tool", "api", "plan",
            "audit", "design", "digest", "vacuum", "intent"
        }
        
        for comp in cortex_components:
            if comp in text:
                components.add(comp)
        
        return components
    
    def _extract_components_from_text(self, text: str) -> set:
        """Extract component names from request text."""
        components = set()
        
        cortex_components = {
            "orchestrator", "mcp", "dashboard", "registry", "lens",
            "wiring", "prompt", "agent", "tool", "api", "plan",
            "audit", "design", "digest", "vacuum", "intent"
        }
        
        for comp in cortex_components:
            if comp in text:
                components.add(comp)
        
        return components
    
    def _similar_scope(self, phase: Dict, request: str) -> bool:
        """Check if request has similar scope to phase."""
        phase_scope = phase.get("description", "").lower()
        request_lower = request.lower()
        
        # Extract key scope indicators
        phase_keywords = set(self._extract_keywords(phase_scope))
        request_keywords = set(self._extract_keywords(request_lower))
        
        # Check for overlap
        overlap = len(phase_keywords & request_keywords)
        return overlap >= 2
    
    def _phase_matches_keywords(self, phase: Dict, keywords: List[str]) -> bool:
        """Check if phase matches given keywords."""
        phase_text = f"{phase.get('name', '')} {phase.get('description', '')}".lower()
        return any(kw in phase_text for kw in keywords)
    
    def _verify_completion_criteria(self, phase_id: str) -> bool:
        """Verify phase meets completion criteria."""
        # Check deliverables, tests, etc.
        # For now, simplified check
        return True
    
    def _verify_registry_sync(self, phase_id: str) -> bool:
        """Verify registry sync (index.yaml consistency)."""
        # Simplified check - can be enhanced
        return True
    
    def _verify_implementation_sync(self, phase_id: str) -> bool:
        """Verify implementation sync (files exist, tests pass)."""
        # Simplified check - can be enhanced
        return True
    
    def _verify_dashboard_sync(self, phase_id: str) -> bool:
        """Verify dashboard sync (JSON/HTML up to date)."""
        # Simplified check - can be enhanced
        return True
    
    def _load_pending_phases(self) -> List[Dict]:
        """Load all pending phases for prioritization."""
        index_data = self._load_index()
        return [
            p for p in index_data.get("active_phases", [])
            if p.get("status") in ["planned", "in-progress"]
        ]

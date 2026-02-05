"""
Architecture Guard Orchestrator - Phase 24 Layer 1
Purpose: Pre-implementation validation against master plan to prevent regression
Authority: cortex-registry/_cortex-master/phases/active/phase-24-architecture-integrity-system.yaml
Status: PHASE 24 - Layer 1 Implementation
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
import yaml
import logging

from cortex.core.result import Result, Ok, Err
from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator, OperationMode

logger = logging.getLogger(__name__)


class GateVerdict(Enum):
    """Architecture gate verdict."""
    PROCEED = "PROCEED"
    CREATE_PHASE = "CREATE_PHASE"
    BLOCK = "BLOCK"


@dataclass
class PhaseAlignment:
    """Phase alignment analysis result."""
    active_phases: List[str]
    conflicts: List[str]
    regression_risk: float  # 0.0-1.0
    brittleness_risk: float  # 0.0-1.0


@dataclass
class SuggestedPhase:
    """Suggested phase structure for CREATE_PHASE verdict."""
    id: str
    title: str
    priority: str
    estimated_effort: str
    scope: List[str]
    dependencies: List[str]


@dataclass
class ValidationResult:
    """Complete validation result from ArchitectureGuard."""
    verdict: GateVerdict
    phase_alignment: PhaseAlignment
    reasoning: str
    suggested_phase: Optional[SuggestedPhase] = None


class ArchitectureGuard(IOrchestrator):
    """
    Architecture Guard - Pre-Implementation Validation Gate
    
    Validates user requests against master plan to prevent:
    - Architectural regression
    - Master plan drift
    - Contradictions with completed phases
    - Untracked significant changes
    
    Returns: PROCEED | CREATE_PHASE | BLOCK
    """
    
    REGISTRY_ROOT = Path(__file__).parent.parent.parent.parent / "cortex-registry" / "_cortex-master"
    INDEX_FILE = REGISTRY_ROOT / "index.yaml"
    
    # Risk thresholds
    REGRESSION_RISK_THRESHOLD = 0.3  # PROCEED if < 0.3
    SIGNIFICANT_CHANGE_THRESHOLD = 0.5  # CREATE_PHASE if > 0.5
    
    def __init__(self):
        """Initialize ArchitectureGuard."""
        self._index_cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_seconds = 300  # 5 minutes
    
    def get_name(self) -> str:
        """Get orchestrator name."""
        return "ArchitectureGuard"
    
    def get_version(self) -> str:
        """Get orchestrator version."""
        return "1.0.0"
    
    def get_mode(self) -> OperationMode:
        """Get operation mode."""
        return OperationMode.VALIDATION
    
    def initialize(self) -> Result[str]:
        """Initialize orchestrator."""
        try:
            # Verify registry access
            if not self.INDEX_FILE.exists():
                return Err(f"Master plan registry not found: {self.INDEX_FILE}")
            
            # Load index to verify format
            load_result = self._load_index()
            if load_result.is_err():
                return Err(f"Failed to load master plan: {load_result.unwrap_err()}")
            
            logger.info("ArchitectureGuard initialized successfully")
            return Ok("ArchitectureGuard initialized")
        
        except Exception as e:
            logger.error(f"ArchitectureGuard initialization failed: {e}")
            return Err(f"Initialization error: {str(e)}")
    
    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """Get MCP tools exposed by this orchestrator."""
        return Ok({
            "cortex_validate_architecture": {
                "name": "cortex_validate_architecture",
                "description": "Validate user request against master plan to prevent regression",
                "parameters": {
                    "request_description": {
                        "type": "string",
                        "required": True,
                        "description": "Description of requested change"
                    },
                    "intent_type": {
                        "type": "string",
                        "required": True,
                        "enum": ["IMPLEMENT", "REFACTOR", "FIX", "DESIGN"],
                        "description": "Type of change intent"
                    },
                    "scope": {
                        "type": "array",
                        "items": {"type": "string"},
                        "required": False,
                        "description": "Affected files/orchestrators"
                    }
                },
                "returns": {
                    "verdict": "PROCEED | CREATE_PHASE | BLOCK",
                    "phase_alignment": "object",
                    "reasoning": "string",
                    "suggested_phase": "object (optional)"
                }
            }
        })
    
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """Execute named operation."""
        if operation_name == "validate_request":
            return self.validate_request(
                request_description=parameters.get("request_description", ""),
                intent_type=parameters.get("intent_type", "IMPLEMENT"),
                scope=parameters.get("scope", [])
            )
        else:
            return Err(f"Unknown operation: {operation_name}")
    
    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """Get audit trail (not implemented for this orchestrator)."""
        return Ok([])
    
    def validate_request(
        self,
        request_description: str,
        intent_type: str,
        scope: Optional[List[str]] = None
    ) -> Result[ValidationResult]:
        """
        Validate user request against master plan.
        
        Args:
            request_description: Description of requested change
            intent_type: IMPLEMENT, REFACTOR, FIX, or DESIGN
            scope: Affected files/orchestrators
        
        Returns:
            Result[ValidationResult]: Validation decision
        """
        try:
            # Load master plan index
            index_result = self._load_index()
            if index_result.is_err():
                return Err(f"Failed to load master plan: {index_result.unwrap_err()}")
            
            index_data = index_result.unwrap()
            
            # Extract active and completed phases
            active_phases = self._extract_active_phases(index_data)
            completed_phases = self._extract_completed_phases(index_data)
            
            # Check phase alignment
            alignment_result = self._check_phase_alignment(
                request_description=request_description,
                active_phases=active_phases,
                completed_phases=completed_phases,
                scope=scope or []
            )
            
            if alignment_result.is_err():
                return Err(alignment_result.unwrap_err())
            
            phase_alignment = alignment_result.unwrap()
            
            # Calculate regression risk
            regression_risk = self._calculate_regression_risk(
                phase_alignment=phase_alignment,
                intent_type=intent_type,
                scope=scope or [],
                request_description=request_description
            )
            
            phase_alignment.regression_risk = regression_risk
            
            # Calculate brittleness risk (simplified for now)
            phase_alignment.brittleness_risk = self._calculate_brittleness_risk(
                scope=scope or []
            )
            
            # Determine verdict
            verdict_result = self._determine_verdict(
                phase_alignment=phase_alignment,
                request_description=request_description,
                intent_type=intent_type,
                scope=scope or []
            )
            
            if verdict_result.is_err():
                return Err(verdict_result.unwrap_err())
            
            return Ok(verdict_result.unwrap())
        
        except Exception as e:
            logger.error(f"Request validation failed: {e}")
            return Err(f"Validation error: {str(e)}")
    
    # ==================== Private Methods ====================
    
    def _load_index(self) -> Result[Dict[str, Any]]:
        """Load master plan index with caching."""
        try:
            # Check cache validity
            if self._index_cache and self._cache_timestamp:
                age_seconds = (datetime.utcnow() - self._cache_timestamp).total_seconds()
                if age_seconds < self._cache_ttl_seconds:
                    return Ok(self._index_cache)
            
            # Load from file
            with open(self.INDEX_FILE, 'r') as f:
                index_data = yaml.safe_load(f)
            
            # Update cache
            self._index_cache = index_data
            self._cache_timestamp = datetime.utcnow()
            
            return Ok(index_data)
        
        except Exception as e:
            return Err(f"Failed to load index: {str(e)}")
    
    def _extract_active_phases(self, index_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract active phases from index."""
        return index_data.get("active_phases", [])
    
    def _extract_completed_phases(self, index_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract completed phases from index."""
        completed = []
        
        # 2026 completed phases
        completed_2026 = index_data.get("completed_phases_2026", {})
        if "phases" in completed_2026:
            for phase_file in completed_2026["phases"]:
                completed.append({"file": phase_file, "year": "2026"})
        
        # 2025 completed phases
        completed_2025 = index_data.get("completed_phases_2025", {})
        if "phases" in completed_2025:
            for phase_file in completed_2025["phases"]:
                completed.append({"file": phase_file, "year": "2025"})
        
        return completed
    
    def _check_phase_alignment(
        self,
        request_description: str,
        active_phases: List[Dict[str, Any]],
        completed_phases: List[Dict[str, Any]],
        scope: List[str]
    ) -> Result[PhaseAlignment]:
        """Check if request aligns with active phases and doesn't conflict with completed."""
        try:
            active_phase_ids = [p.get("id", "") for p in active_phases]
            conflicts = []
            
            # Check for completed phase conflicts
            # For now, simplified check - in production, would load phase YAMLs and check commitments
            for phase in completed_phases:
                phase_file = phase.get("file", "")
                
                # Example conflict detection (would be more sophisticated in production)
                if "screaming" in request_description.lower() and "phase-15" in phase_file:
                    conflicts.append("phase-15: Committed to kebab-case naming, request may use SCREAMING_CASE")
                
                if "sqlite" in request_description.lower() and "phase-21" in phase_file:
                    conflicts.append("phase-21: Committed to JSON-first approach, request may contradict")
            
            return Ok(PhaseAlignment(
                active_phases=active_phase_ids,
                conflicts=conflicts,
                regression_risk=0.0,  # Calculated separately
                brittleness_risk=0.0  # Calculated separately
            ))
        
        except Exception as e:
            return Err(f"Phase alignment check failed: {str(e)}")
    
    def _calculate_regression_risk(
        self,
        phase_alignment: PhaseAlignment,
        intent_type: str,
        scope: List[str],
        request_description: str = ""
    ) -> float:
        """
        Calculate regression risk score (0.0-1.0).
        
        Factors:
        - Number of conflicts (0.4 per conflict)
        - Intent type (REFACTOR = +0.1, IMPLEMENT on core = +0.2)
        - Scope breadth (>10 files = +0.2)
        - Dangerous keywords (rewrite, replace, remove = +0.5)
        """
        risk = 0.0
        
        # Conflicts contribute heavily
        risk += len(phase_alignment.conflicts) * 0.4
        
        # Check for dangerous keywords
        dangerous_keywords = ["rewrite", "replace all", "remove all", "delete", "completely"]
        if any(keyword in request_description.lower() for keyword in dangerous_keywords):
            risk += 0.5
        
        # Intent type
        if intent_type == "REFACTOR":
            risk += 0.1
        elif intent_type == "IMPLEMENT":
            # Check if touching core files
            core_files = [f for f in scope if "orchestrators/core" in f]
            if core_files:
                risk += 0.2
        
        # Scope breadth
        if len(scope) > 10:
            risk += 0.2
        
        # Cap at 1.0
        return min(risk, 1.0)
    
    def _calculate_brittleness_risk(self, scope: List[str]) -> float:
        """
        Calculate brittleness risk (0.0-1.0).
        
        Simplified for now - would integrate with BrittlenessScanner in production.
        """
        # Simple heuristic: more files = potentially more coupling
        if len(scope) > 20:
            return 0.5
        elif len(scope) > 10:
            return 0.3
        else:
            return 0.1
    
    def _determine_verdict(
        self,
        phase_alignment: PhaseAlignment,
        request_description: str,
        intent_type: str,
        scope: List[str]
    ) -> Result[ValidationResult]:
        """Determine final verdict based on analysis."""
        try:
            # BLOCK if conflicts detected and high regression risk
            if phase_alignment.conflicts and phase_alignment.regression_risk > 0.7:
                return Ok(ValidationResult(
                    verdict=GateVerdict.BLOCK,
                    phase_alignment=phase_alignment,
                    reasoning=(
                        f"Request conflicts with {len(phase_alignment.conflicts)} completed phase(s) "
                        f"and poses high regression risk ({phase_alignment.regression_risk:.2f}). "
                        f"Conflicts: {'; '.join(phase_alignment.conflicts)}"
                    )
                ))
            
            # CREATE_PHASE if significant change without active phase coverage
            if self._is_significant_change(intent_type, scope):
                # Check if any active phase covers this
                if not self._has_active_phase_coverage(phase_alignment.active_phases, request_description):
                    suggested_phase = self._generate_suggested_phase(
                        request_description=request_description,
                        intent_type=intent_type,
                        scope=scope
                    )
                    
                    return Ok(ValidationResult(
                        verdict=GateVerdict.CREATE_PHASE,
                        phase_alignment=phase_alignment,
                        reasoning=(
                            f"This is a significant change ({intent_type}, {len(scope)} files) "
                            f"that should be tracked as a dedicated phase for proper planning, "
                            f"coordination, and dashboard visibility."
                        ),
                        suggested_phase=suggested_phase
                    ))
            
            # PROCEED if low regression risk
            if phase_alignment.regression_risk < self.REGRESSION_RISK_THRESHOLD:
                return Ok(ValidationResult(
                    verdict=GateVerdict.PROCEED,
                    phase_alignment=phase_alignment,
                    reasoning=(
                        f"Request aligns with master plan. "
                        f"Regression risk: {phase_alignment.regression_risk:.2f} (acceptable). "
                        f"No conflicts with completed phases."
                    )
                ))
            
            # Default to BLOCK if uncertain
            return Ok(ValidationResult(
                verdict=GateVerdict.BLOCK,
                phase_alignment=phase_alignment,
                reasoning=(
                    f"Request has moderate regression risk ({phase_alignment.regression_risk:.2f}) "
                    f"and requires careful review before proceeding."
                )
            ))
        
        except Exception as e:
            return Err(f"Verdict determination failed: {str(e)}")
    
    def _is_significant_change(self, intent_type: str, scope: List[str]) -> bool:
        """Determine if change is significant enough to warrant a phase."""
        # REFACTOR affecting many files
        if intent_type == "REFACTOR" and len(scope) > 5:
            return True
        
        # IMPLEMENT affecting core orchestrators
        if intent_type == "IMPLEMENT":
            core_files = [f for f in scope if "orchestrators/core" in f]
            if core_files:
                return True
        
        # Large scope (>10 files)
        if len(scope) > 10:
            return True
        
        return False
    
    def _has_active_phase_coverage(
        self,
        active_phases: List[str],
        request_description: str
    ) -> bool:
        """Check if any active phase covers this request (simplified)."""
        # In production, would load phase YAMLs and check scope/description
        # For now, simple keyword matching
        request_lower = request_description.lower()
        
        for phase_id in active_phases:
            if "json" in request_lower and "21" in phase_id:
                return True
            if "ask" in request_lower and "22" in phase_id:
                return True
            if "dashboard" in request_lower and "23" in phase_id:
                return True
        
        return False
    
    def _generate_suggested_phase(
        self,
        request_description: str,
        intent_type: str,
        scope: List[str]
    ) -> SuggestedPhase:
        """Generate suggested phase structure."""
        # Extract next phase number
        # In production, would query index.yaml for latest phase number
        next_phase_id = "phase-25"  # Simplified
        
        # Generate title from request
        title = self._generate_phase_title(request_description, intent_type)
        
        # Determine priority
        priority = "P1"
        if "core" in " ".join(scope):
            priority = "P0"
        
        # Estimate effort
        estimated_effort = "3 days"
        if len(scope) > 10:
            estimated_effort = "1 week"
        elif len(scope) > 20:
            estimated_effort = "2 weeks"
        
        return SuggestedPhase(
            id=next_phase_id,
            title=title,
            priority=priority,
            estimated_effort=estimated_effort,
            scope=scope[:10],  # Top 10 files
            dependencies=[]
        )
    
    def _generate_phase_title(self, request_description: str, intent_type: str) -> str:
        """Generate phase title from request description."""
        # Simplified - would use NLP in production
        words = request_description.split()[:5]
        title = " ".join(words).title()
        
        if intent_type == "REFACTOR":
            return f"{title} Refactor"
        elif intent_type == "IMPLEMENT":
            return f"{title} Implementation"
        else:
            return title


# Module-level exports
__all__ = [
    "ArchitectureGuard",
    "GateVerdict",
    "ValidationResult",
    "PhaseAlignment",
    "SuggestedPhase",
]

# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: IR-004-02 - Comprehension Loop with YAML Condensation
"""
Comprehension Loop with YAML Condensation Module (IR-004-02).

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-004-02 - Comprehension Loop with YAML Condensation

This module implements the comprehension loop that:
1. Analyzes knowledge graph holistically
2. Condenses understanding into structured YAML
3. Presents to user for review/approval
4. Supports iterative refinement
5. Pushes approved comprehensions to brain tiers
6. Cleans up temporary working files
7. Handles rejections with context preservation

The comprehension loop bridges knowledge graph understanding with user
approval workflows, transforming raw intelligence into actionable intent.

Architecture:
- ComprehensionLoopEngine: Main orchestrator
- ComprehensionCondenser: Graph → YAML transformation
- UserApprovalGate: User feedback capture
- BrainTierPusher: Tier selection and file writing
- TempFileManager: Cleanup operations

This completes the CORTEX LENS protocol with a human-in-the-loop
approval mechanism before any code execution.
"""

from __future__ import annotations

import json
import uuid
import shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml


from src.core.knowledge.knowledge_graph import KnowledgeGraph, NodeType, EdgeType
from src.core.intent.comprehension_yaml import (
    ComprehensionYAML,
    IntentSection,
    ChallengeSection,
    ChallengeItem,
    RecommendationSection,
    RecommendationItem,
)


# =============================================================================
# ENUMS
# =============================================================================

class ApprovalStatus(Enum):
    """Status of comprehension in approval process."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_CLARIFICATION = "needs_clarification"


class BrainTier(Enum):
    """Target brain tier for comprehension."""
    TIER0 = "tier0"  # Governance rules
    TIER1 = "tier1"  # AC mappings
    TIER2 = "tier2"  # Standards/patterns
    TIER3 = "tier3"  # Knowledge


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ComprehensionSession:
    """Session tracking for comprehension loop iterations."""
    
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    knowledge_graph: Optional[KnowledgeGraph] = None
    current_comprehension: Optional[ComprehensionYAML] = None
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    revision_count: int = 0
    revision_history: List[Dict[str, Any]] = field(default_factory=list)
    target_tier: Optional[BrainTier] = None
    temp_files: List[str] = field(default_factory=list)
    approval_timestamp: Optional[str] = None
    rejection_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "approval_status": self.approval_status.value,
            "revision_count": self.revision_count,
            "revision_history": self.revision_history,
            "target_tier": self.target_tier.value if self.target_tier else None,
            "approval_timestamp": self.approval_timestamp,
            "rejection_reason": self.rejection_reason,
        }


# =============================================================================
# COMPREHENSION CONDENSER
# =============================================================================

class ComprehensionCondenser:
    """
    Transforms knowledge graph analysis into comprehension YAML.
    
    Analyzes graph holistically to extract:
    - Intent understanding from graph structure
    - Challenges (risks, gaps, governance issues)
    - Recommendations (best practices, alternatives)
    """
    
    def __init__(self, graph: KnowledgeGraph) -> None:
        """Initialize condenser with knowledge graph."""
        self.graph = graph
    
    def condense(self, focal_point: Optional[str] = None) -> ComprehensionYAML:
        """
        Condense graph analysis into comprehension YAML.
        
        Args:
            focal_point: User's request focal point (file, function, etc.)
            
        Returns:
            ComprehensionYAML with intent, challenges, recommendations
        """
        # Analyze graph structure
        stats = self.graph.get_statistics()
        
        # Extract intent from graph
        intent = self._extract_intent(focal_point, stats)
        
        # Identify challenges
        challenges = self._identify_challenges(stats)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(stats)
        
        # Build metadata
        metadata = {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "tool": "CORTEX-LENS",
            "phase": "PHASE-07-Intent-Router",
            "schema": "cortex-comprehension-v1",
        }
        
        return ComprehensionYAML(
            metadata=metadata,
            intent=intent,
            challenges=challenges,
            recommendations=recommendations,
        )
    
    def _extract_intent(self, focal_point: Optional[str], stats: Dict[str, Any]) -> IntentSection:
        """Extract intent understanding from graph."""
        # Determine intent type from graph content
        intent_type = self._determine_intent_type(stats)
        
        # Extract scope
        scope = self._extract_scope(focal_point, stats)
        
        # Calculate confidence
        confidence = self._calculate_confidence(stats)
        
        # Extract keywords from graph
        keywords = self._extract_keywords(stats)
        
        return IntentSection(
            type=intent_type,
            scope=scope,
            confidence=confidence,
            keywords=keywords,
        )
    
    def _determine_intent_type(self, stats: Dict[str, Any]) -> str:
        """Determine user intent type from graph structure."""
        # Default to IMPLEMENT for new structures, FIX for modifications
        # Could be enhanced with more sophisticated analysis
        return "IMPLEMENT"
    
    def _extract_scope(self, focal_point: Optional[str], stats: Dict[str, Any]) -> Dict[str, Any]:
        """Extract target scope from graph."""
        return {
            "target_type": "codebase",
            "target_name": "workspace",
            "file_path": focal_point or ".",
            "ac_ids": [],
            "affected_files": len(stats.get("files", {})),
            "affected_entities": stats.get("total_nodes", 0),
        }
    
    def _calculate_confidence(self, stats: Dict[str, Any]) -> float:
        """Calculate confidence score from graph completeness."""
        # Confidence based on graph completeness (0.70-0.95 range)
        if stats["total_nodes"] == 0:
            return 0.50
        if stats["total_edges"] == 0:
            return 0.60
        
        # More nodes and edges = higher confidence
        edges_per_node = (
            stats["average_edges_per_node"]
            if stats["total_nodes"] > 0
            else 0
        )
        
        # Base confidence + adjustment for connectivity
        base_confidence = 0.75
        connectivity_bonus = min(0.20, edges_per_node * 0.05)
        
        return min(0.95, base_confidence + connectivity_bonus)
    
    def _extract_keywords(self, stats: Dict[str, Any]) -> List[str]:
        """Extract keywords from graph entity types."""
        keywords = []
        
        for entity_type, count in stats.get("node_types", {}).items():
            if count > 0:
                keywords.append(entity_type)
        
        return keywords[:10]  # Limit to top 10
    
    def _identify_challenges(self, stats: Dict[str, Any]) -> ChallengeSection:
        """Identify challenges from graph analysis."""
        challenges = []
        
        # Challenge 1: Missing relationships
        if stats["total_edges"] == 0 and stats["total_nodes"] > 0:
            challenges.append(ChallengeItem(
                id="CH_001",
                category="INCOMPLETE_ANALYSIS",
                severity="MEDIUM",
                description="Limited relationship information",
                affected_code="(workspace)",
                remediation="Enhance AST or dependency analysis",
                confidence=0.9,
            ))
        
        # Challenge 2: Large scope
        if stats["total_nodes"] > 50:
            challenges.append(ChallengeItem(
                id="CH_002",
                category="SCOPE_COMPLEXITY",
                severity="HIGH",
                description="Large number of entities to consider",
                affected_code="(entire scope)",
                remediation="Consider breaking into smaller changes",
                confidence=0.85,
            ))
        
        return ChallengeSection(items=challenges)
    
    def _generate_recommendations(self, stats: Dict[str, Any]) -> RecommendationSection:
        """Generate recommendations from graph analysis."""
        recommendations = []
        
        # Recommendation 1: Test coverage
        recommendations.append(RecommendationItem(
            id="REC_001",
            category="BEST_PRACTICE",
            priority="HIGH",
            title="Add comprehensive tests",
            description="Ensure test coverage for affected code",
            code_context="tests/",
            rationale="Verify implementation doesn't break existing functionality",
        ))
        
        # Recommendation 2: Documentation
        recommendations.append(RecommendationItem(
            id="REC_002",
            category="BEST_PRACTICE",
            priority="MEDIUM",
            title="Update documentation",
            description="Document changes and update affected docs",
            code_context="docs/",
            rationale="Keep documentation in sync with code changes",
        ))
        
        return RecommendationSection(items=recommendations)


# =============================================================================
# USER APPROVAL GATE
# =============================================================================

class UserApprovalGate:
    """
    Manages user feedback and approval workflows.
    
    Supports:
    - Approval: Accept comprehension
    - Rejection: Reject with reason, return to analysis
    - Clarification: Request more details, loop continues
    """
    
    def __init__(self) -> None:
        """Initialize approval gate."""
        self.last_response: Optional[Dict[str, Any]] = None
    
    def present_comprehension(self, comprehension: ComprehensionYAML) -> Dict[str, Any]:
        """Present comprehension to user (mock)."""
        # In real implementation, this would display to user
        # and wait for response. For testing, return presentation data.
        return comprehension.to_dict()
    
    def approve(self, comprehension: ComprehensionYAML) -> ApprovalStatus:
        """User approves comprehension."""
        return ApprovalStatus.APPROVED
    
    def reject(self, reason: str) -> ApprovalStatus:
        """User rejects comprehension with reason."""
        self.last_response = {
            "action": "reject",
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        }
        return ApprovalStatus.REJECTED
    
    def request_clarification(self, question: str) -> ApprovalStatus:
        """User requests clarification."""
        self.last_response = {
            "action": "clarification",
            "question": question,
            "timestamp": datetime.now().isoformat(),
        }
        return ApprovalStatus.NEEDS_CLARIFICATION


# =============================================================================
# BRAIN TIER PUSHER
# =============================================================================

class BrainTierPusher:
    """
    Pushes approved comprehensions to appropriate brain tiers.
    
    Maps comprehension content to brain tier destinations:
    - tier0: Governance rules
    - tier1: AC mappings
    - tier2: Standards/patterns
    - tier3: General knowledge
    """
    
    TIER_PATHS = {
        BrainTier.TIER0: "cortex-brain/tier0/governance",
        BrainTier.TIER1: "cortex-brain/tier1/acceptance-criteria",
        BrainTier.TIER2: "cortex-brain/tier2/standards",
        BrainTier.TIER3: "cortex-brain/tier3/knowledge",
    }
    
    def __init__(self, workspace_root: str = ".") -> None:
        """Initialize pusher with workspace root."""
        self.workspace_root = Path(workspace_root)
    
    def identify_target_tier(self, comprehension: ComprehensionYAML) -> BrainTier:
        """Identify which brain tier comprehension should go to."""
        intent = comprehension.intent
        content = comprehension.to_dict()
        
        # Heuristics for tier selection
        # Governance rules → tier0
        if "governance" in str(content).lower() or "rule" in str(content).lower():
            return BrainTier.TIER0
        
        # AC mappings → tier1
        if intent.scope.get("ac_ids"):
            return BrainTier.TIER1
        
        # Standards/patterns → tier2
        if intent.type in ["REFACTOR", "DESIGN_PATTERN"]:
            return BrainTier.TIER2
        
        # Default → tier3 knowledge
        return BrainTier.TIER3
    
    def push_to_tier(
        self,
        comprehension: ComprehensionYAML,
        tier: BrainTier
    ) -> Path:
        """
        Push comprehension YAML to specified tier.
        
        Args:
            comprehension: ComprehensionYAML to push
            tier: Target BrainTier
            
        Returns:
            Path to written file
        """
        # Construct file path
        tier_path = self.workspace_root / self.TIER_PATHS[tier]
        tier_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp and UUID
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%SZ")
        filename = f"comprehension-{timestamp}-{uuid.uuid4().hex[:8]}.yaml"
        file_path = tier_path / filename
        
        # Write YAML to file
        with open(file_path, "w") as f:
            yaml.dump(comprehension.to_dict(), f, default_flow_style=False)
        
        return file_path


# =============================================================================
# TEMP FILE MANAGER
# =============================================================================

class TempFileManager:
    """Manages cleanup of temporary comprehension files."""
    
    def __init__(self, workspace_root: str = ".") -> None:
        """Initialize with workspace root."""
        self.workspace_root = Path(workspace_root)
        self.temp_dir = self.workspace_root / ".cortex-temp"
    
    def create_temp_file(self, comprehension: ComprehensionYAML) -> Path:
        """Create temporary comprehension file."""
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate temp filename
        filename = f"comprehension-tmp-{uuid.uuid4().hex}.yaml"
        file_path = self.temp_dir / filename
        
        # Write YAML
        with open(file_path, "w") as f:
            yaml.dump(comprehension.to_dict(), f, default_flow_style=False)
        
        return file_path
    
    def cleanup_temp_files(self) -> int:
        """Clean up all temporary files. Returns count removed."""
        if not self.temp_dir.exists():
            return 0
        
        count = 0
        for file in self.temp_dir.glob("comprehension-tmp-*.yaml"):
            file.unlink()
            count += 1
        
        # Remove temp directory if empty
        try:
            self.temp_dir.rmdir()
        except OSError:
            pass  # Directory not empty
        
        return count
    
    def preserve_approved_file(self, temp_file: Path, final_file: Path) -> None:
        """Move temp file to final location."""
        shutil.move(str(temp_file), str(final_file))


# =============================================================================
# COMPREHENSION LOOP ENGINE
# =============================================================================

class ComprehensionLoopEngine:
    """
    Main orchestrator for comprehension loop.
    
    Coordinates:
    1. Knowledge graph analysis
    2. YAML condensation
    3. User approval workflow
    4. Brain tier push
    5. Temp file cleanup
    """
    
    def __init__(self, workspace_root: str = ".") -> None:
        """Initialize loop engine."""
        self.workspace_root = workspace_root
        self.session: Optional[ComprehensionSession] = None
        self.tier_pusher = BrainTierPusher(workspace_root)
        self.temp_manager = TempFileManager(workspace_root)
        self.approval_gate = UserApprovalGate()
    
    def start_session(self, graph: KnowledgeGraph, focal_point: Optional[str] = None) -> ComprehensionSession:
        """Start new comprehension session."""
        session = ComprehensionSession(knowledge_graph=graph)
        
        # Analyze and condense graph
        condenser = ComprehensionCondenser(graph)
        comprehension = condenser.condense(focal_point)
        
        session.current_comprehension = comprehension
        session.revision_count = 1
        session.revision_history.append({
            "revision": 1,
            "changes": "Initial comprehension from graph analysis",
            "timestamp": datetime.now().isoformat(),
        })
        
        self.session = session
        return session
    
    def present_for_approval(self) -> Dict[str, Any]:
        """Present comprehension to user."""
        if not self.session or not self.session.current_comprehension:
            raise ValueError("No active comprehension session")
        
        # Present comprehension
        presentation = self.approval_gate.present_comprehension(
            self.session.current_comprehension
        )
        
        # Return for user review
        return presentation
    
    def approve(self) -> Tuple[ApprovalStatus, Path]:
        """
        User approves comprehension.
        
        Returns:
            Tuple of (approval_status, final_file_path)
        """
        if not self.session or not self.session.current_comprehension:
            raise ValueError("No active comprehension session")
        
        # Mark as approved
        status = self.approval_gate.approve(self.session.current_comprehension)
        self.session.approval_status = status
        self.session.approval_timestamp = datetime.now().isoformat()
        
        # Identify target tier
        target_tier = self.tier_pusher.identify_target_tier(
            self.session.current_comprehension
        )
        self.session.target_tier = target_tier
        
        # Push to brain tier
        final_file = self.tier_pusher.push_to_tier(
            self.session.current_comprehension,
            target_tier
        )
        
        # Cleanup temp files
        self.temp_manager.cleanup_temp_files()
        
        return status, final_file
    
    def reject(self, reason: str) -> ApprovalStatus:
        """
        User rejects comprehension with reason.
        
        Returns:
            Rejection status (can restart analysis)
        """
        if not self.session:
            raise ValueError("No active comprehension session")
        
        status = self.approval_gate.reject(reason)
        self.session.approval_status = status
        self.session.rejection_reason = reason
        
        # Cleanup temp files
        self.temp_manager.cleanup_temp_files()
        
        return status
    
    def request_clarification(self, question: str) -> ComprehensionSession:
        """
        User requests clarification (loop continues).
        
        Returns:
            Updated session for next iteration
        """
        if not self.session:
            raise ValueError("No active comprehension session")
        
        status = self.approval_gate.request_clarification(question)
        self.session.approval_status = status
        
        # Re-analyze with user question as additional context
        # (In real implementation, would re-analyze with clarification feedback)
        self.session.revision_count += 1
        self.session.revision_history.append({
            "revision": self.session.revision_count,
            "changes": f"User requested clarification: {question}",
            "timestamp": datetime.now().isoformat(),
        })
        
        return self.session
    
    def get_session_status(self) -> Optional[Dict[str, Any]]:
        """Get current session status."""
        if not self.session:
            return None
        
        return self.session.to_dict()

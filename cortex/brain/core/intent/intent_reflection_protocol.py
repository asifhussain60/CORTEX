"""
Intent Reflection Protocol Module.

Implements the Master → Interaction Orchestrator collaboration pattern from
CORTEX5.5. The IntentReflectionEngine orchestrates the three-stage comprehension
flow: context gathering → challenge/recommendation identification → user approval.

The LENS protocol presents holistic context to users for confirmation before
execution, enabling informed decision-making and governance compliance.

Architecture:
- ReflectionRequest: User request with focal point and context
- IntentReflectionEngine: Core orchestrator for reflection process
- ReflectionResponse: Complete comprehension document with approval status
- Audit trail: Full logging of reflection lifecycle for governance
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import hashlib
import json
import uuid
import yaml


# ============================================================================
# ENUMERATIONS
# ============================================================================

class ReflectionStatus(Enum):
    """Status of a reflection request."""
    
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    PENDING_CONFIRMATION = "PENDING_CONFIRMATION"
    IN_REFLECTION = "IN_REFLECTION"
    ERROR = "ERROR"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ReflectionRequest:
    """User request for reflection."""
    
    user_request: str  # Natural language request
    focal_point: str  # File, function, class, or module being focused on
    target_scope: str  # "file", "function", "class", "module"
    target_name: str  # Name of target
    context: Dict[str, Any]  # Additional context (file_path, project_root, etc.)
    timestamp: str  # ISO-8601 timestamp
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ReflectionResponse:
    """Complete reflection response with comprehension document."""
    
    request: ReflectionRequest
    status: ReflectionStatus
    canonicalized_intent: Dict[str, Any]  # From IntentCanonicalizer
    challenges: List[Dict[str, Any]]  # From ChallengeGenerator
    recommendations: List[Dict[str, Any]]  # From RecommendationEngine
    comprehension_yaml: str  # YAML document for user approval
    focal_point: str
    ready_for_execution: bool = False
    reflected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    context_built_at: Optional[str] = None
    context_sources: List[str] = field(default_factory=list)
    orchestrator_trace: Optional[str] = None
    audit_entries: List[Dict[str, Any]] = field(default_factory=list)
    approval_timestamp: Optional[str] = None
    approval_user: Optional[str] = None
    rejection_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "request": self.request.to_dict(),
            "status": self.status.value,
            "canonicalized_intent": self.canonicalized_intent,
            "challenges": self.challenges,
            "recommendations": self.recommendations,
            "comprehension_yaml": self.comprehension_yaml,
            "focal_point": self.focal_point,
            "ready_for_execution": self.ready_for_execution,
            "reflected_at": self.reflected_at,
            "context_built_at": self.context_built_at,
            "context_sources": self.context_sources,
            "orchestrator_trace": self.orchestrator_trace,
            "audit_entries": self.audit_entries,
            "approval_timestamp": self.approval_timestamp,
            "approval_user": self.approval_user,
            "rejection_reason": self.rejection_reason,
        }


# ============================================================================
# INTENT REFLECTION ENGINE
# ============================================================================

class IntentReflectionEngine:
    """
    Core orchestrator for the Intent Reflection Protocol.
    
    Implements Master → Interaction Orchestrator delegation pattern.
    Coordinates context gathering, challenge detection, recommendations,
    and user approval before execution.
    
    Usage:
        engine = IntentReflectionEngine()
        request = ReflectionRequest(...)
        response = engine.reflect(request)
        approval = engine.approve(response)
    """
    
    PROTOCOL_VERSION = "1.0"
    MAX_CHALLENGES = 50
    MAX_RECOMMENDATIONS = 50
    
    def __init__(self):
        """Initialize reflection engine."""
        self.request_history: List[ReflectionRequest] = []
        self.response_history: List[ReflectionResponse] = []
    
    def reflect(self, request: ReflectionRequest) -> ReflectionResponse:
        """
        Execute complete reflection process.
        
        Args:
            request: ReflectionRequest with user intent and context
            
        Returns:
            ReflectionResponse with comprehension document
            
        Raises:
            ValueError: If request is invalid
        """
        # Validate request
        if not request.user_request or not request.focal_point:
            raise ValueError("user_request and focal_point are required")
        
        # Log request history
        self.request_history.append(request)
        
        # Create audit entries
        audit_entries = []
        
        # Entry 1: Reflection started
        start_entry = self._create_audit_entry(
            operation="REFLECTION_START",
            request_id=request.request_id,
            details={"user_request": request.user_request, "focal_point": request.focal_point},
        )
        audit_entries.append(start_entry)
        
        try:
            # Step 1: Master orchestrator starts
            orchestrator_trace = "MasterOrchestrator: Processing reflection request\n"
            
            # Step 2: Master delegates to Interaction orchestrator
            orchestrator_trace += "InteractionOrchestrator: Building holistic context\n"
            
            # Step 3: Gather context from all intelligence sources (simulated)
            context_built_at = datetime.utcnow().isoformat() + "Z"
            context_sources = self._gather_context_sources(request)
            orchestrator_trace += f"ContextBuilder: Aggregated {len(context_sources)} sources\n"
            
            # Step 4: Canonicalize intent
            canonicalized_intent = self._canonicalize_intent(request)
            orchestrator_trace += "IntentCanonicalizer: Transformed NL → Intent\n"
            
            # Step 5: Generate challenges
            challenges = self._generate_challenges(request, context_sources)
            orchestrator_trace += f"ChallengeGenerator: Identified {len(challenges)} challenges\n"
            
            # Step 6: Generate recommendations
            recommendations = self._generate_recommendations(request, challenges, context_sources)
            orchestrator_trace += f"RecommendationEngine: Generated {len(recommendations)} recommendations\n"
            
            # Step 7: Generate comprehension YAML
            comprehension_yaml = self._generate_comprehension_yaml(
                canonicalized_intent, challenges, recommendations
            )
            orchestrator_trace += "ComprehensionYAML: Generated for user approval\n"
            
            # Entry 2: Reflection context built
            context_entry = self._create_audit_entry(
                operation="CONTEXT_AGGREGATION",
                request_id=request.request_id,
                details={
                    "sources_count": len(context_sources),
                    "challenges_count": len(challenges),
                    "recommendations_count": len(recommendations),
                },
                previous_hash=start_entry.get("hash"),
            )
            audit_entries.append(context_entry)
            
            # Entry 3: Reflection complete
            complete_entry = self._create_audit_entry(
                operation="REFLECTION_COMPLETE",
                request_id=request.request_id,
                details={
                    "status": "SUCCESS",
                    "intent_confidence": canonicalized_intent.get("confidence", 0),
                },
                previous_hash=context_entry.get("hash"),
            )
            audit_entries.append(complete_entry)
            
            # Create response
            response = ReflectionResponse(
                request=request,
                status=ReflectionStatus.PENDING_CONFIRMATION,
                canonicalized_intent=canonicalized_intent,
                challenges=challenges,
                recommendations=recommendations,
                comprehension_yaml=comprehension_yaml,
                focal_point=request.focal_point,
                ready_for_execution=False,
                context_built_at=context_built_at,
                context_sources=context_sources,
                orchestrator_trace=orchestrator_trace,
                audit_entries=audit_entries,
            )
            
            # Store in history
            self.response_history.append(response)
            
            return response
            
        except Exception as e:
            # Log error entry
            error_entry = self._create_audit_entry(
                operation="REFLECTION_ERROR",
                request_id=request.request_id,
                details={"error": str(e)},
                previous_hash=audit_entries[-1].get("hash") if audit_entries else None,
            )
            audit_entries.append(error_entry)
            
            # Return error response
            return ReflectionResponse(
                request=request,
                status=ReflectionStatus.ERROR,
                canonicalized_intent={},
                challenges=[],
                recommendations=[],
                comprehension_yaml="",
                focal_point=request.focal_point,
                audit_entries=audit_entries,
            )
    
    def approve(self, response: ReflectionResponse) -> ReflectionResponse:
        """
        User approves the reflection.
        
        Args:
            response: ReflectionResponse to approve
            
        Returns:
            Updated response with approval status
        """
        response.status = ReflectionStatus.APPROVED
        response.ready_for_execution = True
        response.approval_timestamp = datetime.utcnow().isoformat() + "Z"
        response.approval_user = "user"  # In real system, would capture actual user
        
        # Add audit entry
        approval_entry = self._create_audit_entry(
            operation="USER_APPROVAL",
            request_id=response.request.request_id,
            details={"status": "APPROVED"},
            previous_hash=response.audit_entries[-1].get("hash") if response.audit_entries else None,
        )
        response.audit_entries.append(approval_entry)
        
        return response
    
    def reject(self, response: ReflectionResponse, reason: str) -> ReflectionResponse:
        """
        User rejects the reflection.
        
        Args:
            response: ReflectionResponse to reject
            reason: Reason for rejection
            
        Returns:
            Updated response with rejection status
        """
        response.status = ReflectionStatus.REJECTED
        response.ready_for_execution = False
        response.rejection_reason = reason
        
        # Add audit entry
        rejection_entry = self._create_audit_entry(
            operation="USER_REJECTION",
            request_id=response.request.request_id,
            details={"reason": reason},
            previous_hash=response.audit_entries[-1].get("hash") if response.audit_entries else None,
        )
        response.audit_entries.append(rejection_entry)
        
        return response
    
    def request_clarification(self, response: ReflectionResponse, clarification_question: str) -> ReflectionResponse:
        """
        User requests clarification.
        
        Args:
            response: ReflectionResponse to clarify
            clarification_question: User's clarification question
            
        Returns:
            Updated response with clarification status
        """
        response.status = ReflectionStatus.NEEDS_CLARIFICATION
        response.ready_for_execution = False
        
        # Add audit entry
        clarification_entry = self._create_audit_entry(
            operation="CLARIFICATION_REQUESTED",
            request_id=response.request.request_id,
            details={"question": clarification_question},
            previous_hash=response.audit_entries[-1].get("hash") if response.audit_entries else None,
        )
        response.audit_entries.append(clarification_entry)
        
        return response
    
    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================
    
    def _gather_context_sources(self, request: ReflectionRequest) -> List[str]:
        """Gather context from all intelligence sources."""
        sources = [
            "AST Intelligence",
            "Git History",
            "Code Comments",
            "Relationship Traversal",
        ]
        return sources
    
    def _canonicalize_intent(self, request: ReflectionRequest) -> Dict[str, Any]:
        """Canonicalize user request to standard intent."""
        return {
            "intent_type": self._extract_intent_type(request.user_request),
            "scope": {
                "target_type": request.target_scope,
                "target_name": request.target_name,
                "focal_point": request.focal_point,
            },
            "confidence": self._calculate_confidence(request.user_request),
            "keywords": self._extract_keywords(request.user_request),
            "needs_clarification": False,
        }
    
    def _generate_challenges(self, request: ReflectionRequest, context_sources: List[str]) -> List[Dict[str, Any]]:
        """Generate challenges from context analysis."""
        challenges = []
        
        # Simulate challenge generation based on request
        if "error handling" in request.user_request.lower():
            challenges.append({
                "id": "TEST_GAP_001",
                "category": "TEST_GAP",
                "severity": "HIGH",
                "description": "No error handling tests identified",
                "affected_code": request.focal_point,
                "remediation": "Add test cases for error scenarios",
                "confidence": 0.85,
            })
        
        if "refactor" in request.user_request.lower():
            challenges.append({
                "id": "BREAKING_001",
                "category": "BREAKING_CHANGE",
                "severity": "HIGH",
                "description": f"Refactoring may impact dependent code",
                "affected_code": request.focal_point,
                "remediation": "Check all call sites before refactoring",
                "confidence": 0.80,
            })
        
        if not request.user_request:
            challenges.append({
                "id": "GOVERNANCE_001",
                "category": "GOVERNANCE_RISK",
                "severity": "MEDIUM",
                "description": "Ambiguous request may lead to misalignment",
                "affected_code": request.focal_point,
                "remediation": "Provide more specific requirements",
                "confidence": 0.75,
            })
        
        return challenges[:self.MAX_CHALLENGES]
    
    def _generate_recommendations(
        self, request: ReflectionRequest, challenges: List[Dict[str, Any]], context_sources: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on challenges and context."""
        recommendations = []
        
        # Add recommendations based on challenges
        if any(c["category"] == "TEST_GAP" for c in challenges):
            recommendations.append({
                "id": "REC_001",
                "category": "TEST_STRATEGY",
                "priority": "HIGH",
                "title": "Use parametrized tests",
                "description": "Implement pytest.mark.parametrize for comprehensive coverage",
                "rationale": "Improves test maintainability",
            })
        
        if any(c["category"] == "BREAKING_CHANGE" for c in challenges):
            recommendations.append({
                "id": "REC_002",
                "category": "BEST_PRACTICE",
                "priority": "HIGH",
                "title": "Check call sites",
                "description": "Use grep/IDE to find all function usages before refactoring",
                "rationale": "Prevents runtime errors",
            })
        
        # Add documentation recommendation
        recommendations.append({
            "id": "REC_003",
            "category": "DOCUMENTATION",
            "priority": "MEDIUM",
            "title": "Update docstrings",
            "description": "Ensure functions have Google-style docstrings",
            "rationale": "Improves code maintainability",
        })
        
        return recommendations[:self.MAX_RECOMMENDATIONS]
    
    def _generate_comprehension_yaml(
        self, intent: Dict[str, Any], challenges: List[Dict[str, Any]], recommendations: List[Dict[str, Any]]
    ) -> str:
        """Generate YAML comprehension document."""
        doc = {
            "metadata": {
                "version": self.PROTOCOL_VERSION,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "tool": "CORTEX-LENS",
                "phase": "PHASE-07-Intent-Router",
            },
            "intent": intent,
            "challenges": {
                "summary": {
                    "total": len(challenges),
                    "by_severity": self._count_by_field(challenges, "severity"),
                },
                "items": challenges,
            },
            "recommendations": {
                "summary": {
                    "total": len(recommendations),
                    "by_priority": self._count_by_field(recommendations, "priority"),
                },
                "items": recommendations,
            },
        }
        
        return yaml.safe_dump(doc, default_flow_style=False, sort_keys=False)
    
    def _create_audit_entry(
        self,
        operation: str,
        request_id: str,
        details: Dict[str, Any],
        previous_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create audit trail entry with hash chain."""
        entry = {
            "id": str(uuid.uuid4()),
            "operation": operation,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "details": details,
        }
        
        # Create hash for chain
        entry_str = json.dumps(entry, sort_keys=True)
        entry_hash = hashlib.sha256(entry_str.encode()).hexdigest()
        entry["hash"] = entry_hash
        
        if previous_hash:
            entry["previous_hash"] = previous_hash
        
        return entry
    
    def _extract_intent_type(self, user_request: str) -> str:
        """Extract intent type from natural language request."""
        request_lower = user_request.lower()
        
        if any(word in request_lower for word in ["implement", "create", "add", "new"]):
            return "IMPLEMENT"
        elif any(word in request_lower for word in ["fix", "resolve", "bug", "error"]):
            return "FIX"
        elif any(word in request_lower for word in ["refactor", "improve", "clean"]):
            return "REFACTOR"
        elif any(word in request_lower for word in ["query", "get", "find", "show"]):
            return "QUERY"
        else:
            return "UNKNOWN"
    
    def _calculate_confidence(self, user_request: str) -> float:
        """Calculate confidence score for intent extraction."""
        if len(user_request) < 10:
            return 0.5
        elif len(user_request) < 50:
            return 0.7
        else:
            return 0.85
    
    def _extract_keywords(self, user_request: str) -> List[str]:
        """Extract keywords from request."""
        # Simple keyword extraction
        words = user_request.lower().split()
        keywords = [w for w in words if len(w) > 4 and w.isalpha()]
        return keywords[:10]
    
    def _count_by_field(self, items: List[Dict[str, Any]], field: str) -> Dict[str, int]:
        """Count items by field value."""
        counts = {}
        for item in items:
            value = item.get(field, "UNKNOWN")
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    def to_yaml(self, response: ReflectionResponse) -> str:
        """Serialize response to YAML."""
        return yaml.safe_dump(response.to_dict(), default_flow_style=False, sort_keys=False)
    
    @staticmethod
    def from_yaml(yaml_content: str) -> ReflectionResponse:
        """Deserialize response from YAML."""
        data = yaml.safe_load(yaml_content)
        
        # Reconstruct request
        request_data = data.get("request", {})
        request = ReflectionRequest(**request_data)
        
        # Handle challenges data (could be dict with 'items' or list)
        challenges_data = data.get("challenges", {})
        if isinstance(challenges_data, dict):
            challenges = challenges_data.get("items", [])
        else:
            challenges = challenges_data if isinstance(challenges_data, list) else []
        
        # Handle recommendations data (could be dict with 'items' or list)
        recommendations_data = data.get("recommendations", {})
        if isinstance(recommendations_data, dict):
            recommendations = recommendations_data.get("items", [])
        else:
            recommendations = recommendations_data if isinstance(recommendations_data, list) else []
        
        # Reconstruct response
        return ReflectionResponse(
            request=request,
            status=ReflectionStatus[data.get("status", "PENDING")],
            canonicalized_intent=data.get("canonicalized_intent", {}),
            challenges=challenges,
            recommendations=recommendations,
            comprehension_yaml=data.get("comprehension_yaml", ""),
            focal_point=data.get("focal_point", ""),
            ready_for_execution=data.get("ready_for_execution", False),
            reflected_at=data.get("reflected_at", ""),
            context_built_at=data.get("context_built_at"),
            context_sources=data.get("context_sources", []),
            orchestrator_trace=data.get("orchestrator_trace"),
            audit_entries=data.get("audit_entries", []),
            approval_timestamp=data.get("approval_timestamp"),
            approval_user=data.get("approval_user"),
            rejection_reason=data.get("rejection_reason"),
        )

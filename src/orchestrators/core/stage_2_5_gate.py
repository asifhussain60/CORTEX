"""Stage 2.5 Confirmation Gate - Inserted into Master Orchestrator execution flow."""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from src.core.orchestrator.complexity_assessment import (
    ComplexityAssessment,
    ComplexityAssessmentEngine,
    ComplexitySignals,
)
from src.core.orchestrator.approval_gate import (
    ApprovalGateLogic,
    ApprovalDecision,
    ConfirmationRequest,
    AlternativeRecommendation,
)

@dataclass
class ConfirmationContext:
    """Context information for confirmation gate decision."""
    operation_id: str
    complexity_score: float
    complexity_level: str
    reasons: List[str]  # Reasons for complexity assessment
    alternatives: List[AlternativeRecommendation]  # Alternative approaches
    confidence: float  # Confidence in assessment
    lens_confidence: float  # Confidence from Stage 2 LENS analysis
    user_intent: Optional[str] = None
    affected_files: List[str] = field(default_factory=list)
    challenges: List[Dict[str, Any]] = field(default_factory=list)  # Integrated challenges
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ContinuationDecision:
    """Extended decision for turn continuation with confirmation."""
    continue_execution: bool
    reason: str
    confirmation_reason: Optional[str] = None  # New: reason if confirmation needed
    confirmation_context: Optional[ConfirmationContext] = None
    is_confirmation_gate: bool = False  # New: indicates gate originated decision
    timestamp: datetime = field(default_factory=datetime.now)

class Stage25Gate:
    """Stage 2.5 Confirmation Gate - Inserted after Stage 2 (Routing)."""
    
    def __init__(self):
        """Initialize Stage 2.5 gate."""
        self.engine = ComplexityAssessmentEngine()
        self.gate = ApprovalGateLogic()
        self.execution_count = 0
        self.confirmed_decisions: Dict[str, bool] = {}  # operation_id -> confirmed
    
    def evaluate(
        self,
        operation_id: str,
        lens_confidence: float,
        signals: ComplexitySignals,
        user_intent: Optional[str] = None,
        affected_files: Optional[List[str]] = None,
        alternatives: Optional[List[Dict[str, Any]]] = None,
        challenges: Optional[List[Dict[str, Any]]] = None,
    ) -> ContinuationDecision:
        """
        Evaluate operation at Stage 2.5.
        
        Called after Stage 2 routing, before Stage 3 delegation.
        Determines if operation can proceed automatically or needs confirmation.
        
        Args:
            operation_id: Unique operation identifier
            lens_confidence: Confidence from Stage 2 LENS analysis (0.0-1.0)
            signals: ComplexitySignals for assessment
            user_intent: User's stated intent/goal
            affected_files: List of files affected by operation
            alternatives: List of alternative approaches
            challenges: List of challenge dictionaries for risk identification
        
        Returns:
            ContinuationDecision for turn execution
        """
        self.execution_count += 1
        
        # Assess complexity using aggregated signals
        assessment = self.engine.assess_complexity(
            signals,
            intent_type=user_intent or "general",
            use_cache=True
        )
        
        # Evaluate approval using gate logic
        approval = self.gate.evaluate_approval(
            assessment,
            operation_id,
            alternatives=alternatives
        )
        
        # Determine continuation decision
        if approval.approved:
            # TRIVIAL/SIMPLE: Auto-approve, continue execution
            return ContinuationDecision(
                continue_execution=True,
                reason=f"Auto-approved ({approval.complexity_level})",
                is_confirmation_gate=False,
            )
        else:
            # MODERATE/COMPLEX/CRITICAL: Need confirmation
            context = self._build_confirmation_context(
                operation_id,
                assessment,
                lens_confidence,
                approval,
                user_intent,
                affected_files,
                challenges,
            )
            
            return ContinuationDecision(
                continue_execution=False,
                reason="Confirmation required before execution",
                confirmation_reason=approval.reason,
                confirmation_context=context,
                is_confirmation_gate=True,
            )
    
    def _build_confirmation_context(
        self,
        operation_id: str,
        assessment: ComplexityAssessment,
        lens_confidence: float,
        approval: ApprovalDecision,
        user_intent: Optional[str],
        affected_files: Optional[List[str]],
        challenges: Optional[List[Dict[str, Any]]] = None,
    ) -> ConfirmationContext:
        """Build confirmation context from assessment and approval."""
        # Extract reasons from assessment factors
        reasons = []
        for factor, value in assessment.factors.items():
            if value > 0.3:
                reasons.append(f"{factor}: {value:.2f}")
        
        return ConfirmationContext(
            operation_id=operation_id,
            complexity_score=assessment.complexity_score,
            complexity_level=assessment.complexity_level,
            reasons=reasons,
            alternatives=approval.alternatives,
            confidence=assessment.confidence,
            lens_confidence=lens_confidence,
            user_intent=user_intent,
            affected_files=affected_files or [],
            challenges=challenges or [],
        )
    
    def record_confirmation(
        self,
        operation_id: str,
        confirmed: bool,
        user_choice: Optional[str] = None,
    ) -> None:
        """Record user confirmation decision."""
        self.confirmed_decisions[operation_id] = confirmed
    
    def should_bypass_confirmation(self, operation_id: str) -> bool:
        """Check if operation can bypass confirmation (already confirmed)."""
        return self.confirmed_decisions.get(operation_id, False)
    
    def get_stage_statistics(self) -> Dict[str, Any]:
        """Get Stage 2.5 statistics."""
        confirmations_needed = sum(1 for v in self.confirmed_decisions.values() if v is False)
        confirmations_approved = sum(1 for v in self.confirmed_decisions.values() if v is True)
        
        return {
            'total_evaluations': self.execution_count,
            'confirmations_needed': confirmations_needed,
            'confirmations_approved': confirmations_approved,
            'confirmation_rate': confirmations_needed / max(1, self.execution_count),
        }

class ConversationProtocolIntegration:
    """Integration point for Stage 2.5 into ConversationProtocol.execute_turn()."""
    
    def __init__(self):
        """Initialize integration."""
        self.stage_2_5 = Stage25Gate()
    
    def execute_turn_with_confirmation_gate(
        self,
        operation_id: str,
        routing_decision: Dict[str, Any],
        stage_2_context: Dict[str, Any],
        challenges: Optional[List[Dict[str, Any]]] = None,
    ) -> ContinuationDecision:
        """
        Execute turn with Stage 2.5 confirmation gate.
        
        Called from ConversationProtocol.execute_turn() after Stage 2 routing.
        
        Flow:
        1. Stage 2 routing produces decision with LENS confidence
        2. Stage 2.5 gate evaluates complexity and approval
        3. If auto-approved: continue to Stage 3 delegation
        4. If confirmation needed: return CONFIRMATION_REQUESTED
        
        Args:
            operation_id: Operation identifier
            routing_decision: Decision from Stage 2 routing
            stage_2_context: Context from Stage 2 (includes LENS confidence)
            challenges: List of challenge dictionaries for decision rationale
        
        Returns:
            ContinuationDecision indicating execution path
        """
        # Extract Stage 2 information
        lens_confidence = stage_2_context.get('lens_confidence', 0.5)
        user_intent = stage_2_context.get('intent', None)
        affected_files = stage_2_context.get('affected_files', [])
        
        # Build complexity signals from Stage 2 analysis
        signals = self._build_signals_from_stage_2(stage_2_context)
        
        # Extract alternatives if available
        alternatives = routing_decision.get('alternatives', None)
        
        # Evaluate at Stage 2.5 with challenges
        decision = self.stage_2_5.evaluate(
            operation_id=operation_id,
            lens_confidence=lens_confidence,
            signals=signals,
            user_intent=user_intent,
            affected_files=affected_files,
            alternatives=alternatives,
            challenges=challenges,
        )
        
        return decision
    
    @staticmethod
    def _build_signals_from_stage_2(context: Dict[str, Any]) -> ComplexitySignals:
        """Build ComplexitySignals from Stage 2 analysis context."""
        return ComplexitySignals(
            lens_confidence=context.get('lens_confidence', 0.5),
            files_affected_count=context.get('files_affected_count', 1),
            call_graph_depth=context.get('call_graph_depth', 1),
            circular_dependencies=context.get('circular_dependencies', 0),
            dependency_depth=context.get('dependency_depth', 1),
            tight_coupling_score=context.get('tight_coupling_score', 0.0),
            operation_scope=context.get('operation_scope', 'local'),
            ast_complexity=context.get('ast_complexity', 0),
            criticality_level=context.get('criticality_level', 'low'),
        )
    
    def handle_confirmation_response(
        self,
        operation_id: str,
        confirmed: bool,
        user_choice: Optional[str] = None,
    ) -> ContinuationDecision:
        """
        Handle user's confirmation response.
        
        Called when user responds to confirmation request.
        Returns updated decision to continue or abort execution.
        
        Args:
            operation_id: Operation that was confirmed/rejected
            confirmed: Whether user confirmed execution
            user_choice: User's selected approach (if alternatives were offered)
        
        Returns:
            ContinuationDecision for turn execution
        """
        self.stage_2_5.record_confirmation(operation_id, confirmed, user_choice)
        
        if confirmed:
            return ContinuationDecision(
                continue_execution=True,
                reason="User confirmed execution",
                is_confirmation_gate=False,
            )
        else:
            return ContinuationDecision(
                continue_execution=False,
                reason="User rejected execution",
                is_confirmation_gate=False,
            )
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """Get Stage 2.5 integration statistics."""
        return self.stage_2_5.get_stage_statistics()

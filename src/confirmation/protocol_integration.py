"""
ConversationProtocol Stage 2.5 Integration - Production Implementation.

Inserts complexity-aware gate between Stage 2 (Solution Design) and Stage 3
(Implementation Preparation).
"""

from typing import List, Dict
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ConversationStage(Enum):
    """ConversationProtocol stages."""
    STAGE_1 = 1      # Problem Analysis
    STAGE_2 = 2      # Solution Design
    STAGE_2_5 = 2.5  # Complexity-Aware Confirmation Gate
    STAGE_3 = 3      # Implementation Preparation
    STAGE_4 = 4      # Execution
    STAGE_5 = 5      # Verification


class GateDecision(Enum):
    """Gate outcomes."""
    PROCEED = "proceed"
    HOLD_FOR_REVIEW = "hold_for_review"
    REJECT = "reject"


@dataclass
class ConversationContext:
    """Context for a conversation."""
    
    conversation_id: str
    problem_statement: str
    proposed_solution: str
    complexity_level: str
    current_stage: ConversationStage
    metadata: Dict = field(default_factory=dict)


@dataclass
class Stage2Output:
    """Output from Stage 2 (Solution Design)."""
    
    solution_design: str
    design_confidence: float
    identified_risks: List[str]
    resource_requirements: Dict
    estimated_effort: str


@dataclass
class Stage2Point5Input:
    """Input to Stage 2.5 gate from Stage 2."""
    
    conversation_id: str
    stage_2_output: Stage2Output
    lens_metrics: Dict  # logical, evidence, narrative, semantic confidence
    complexity_assessment: Dict  # complexity level, score, confidence
    timestamp: datetime


@dataclass
class Stage2Point5Output:
    """Output from Stage 2.5 gate."""
    
    decision: GateDecision
    reasoning: str
    required_approvals: List[str]
    can_proceed_to_stage_3: bool
    review_notes: str = None
    timestamp: datetime = None


class ConversationProtocolStage2Point5:
    """
    Stage 2.5: Complexity-Aware Confirmation Gate.
    
    Inserted between Stage 2 (Solution Design) and Stage 3 (Implementation Preparation).
    Validates proposed solutions against complexity assessment and confidence thresholds.
    """
    
    # Thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    MEDIUM_CONFIDENCE_THRESHOLD = 0.65
    
    def __init__(self):
        """Initialize Stage 2.5 gate."""
        self.execution_log: List[Stage2Point5Output] = []
        self.blocked_conversations: List[str] = []
        self.approved_conversations: List[str] = []
    
    def execute(self, input_data: Stage2Point5Input) -> Stage2Point5Output:
        """
        Execute Stage 2.5 gate logic.
        
        Args:
            input_data: Input from Stage 2 with solution and confidence metrics
        
        Returns:
            Stage2Point5Output with decision and next steps
        """
        # Validate input
        if not self._validate_input(input_data):
            output = Stage2Point5Output(
                decision=GateDecision.REJECT,
                reasoning="Invalid input data",
                required_approvals=[],
                can_proceed_to_stage_3=False,
                review_notes="Input validation failed",
                timestamp=datetime.now()
            )
            self.execution_log.append(output)
            return output
        
        # Make gate decision
        decision = self._make_decision(input_data)
        
        if decision == GateDecision.PROCEED:
            reasoning = "Solution confidence high - proceeding to Stage 3"
            required_approvals = []
            can_proceed = True
            self.approved_conversations.append(input_data.conversation_id)
        
        elif decision == GateDecision.HOLD_FOR_REVIEW:
            reasoning = "Solution requires review - placed on hold"
            required_approvals = self._determine_approvers(input_data)
            can_proceed = False
        
        else:  # REJECT
            reasoning = "Solution confidence too low - rejected"
            required_approvals = []
            can_proceed = False
            self.blocked_conversations.append(input_data.conversation_id)
        
        output = Stage2Point5Output(
            decision=decision,
            reasoning=reasoning,
            required_approvals=required_approvals,
            can_proceed_to_stage_3=can_proceed,
            review_notes=self._generate_review_notes(input_data),
            timestamp=datetime.now()
        )
        
        self.execution_log.append(output)
        return output
    
    def _validate_input(self, input_data: Stage2Point5Input) -> bool:
        """Validate input data completeness."""
        if not input_data.conversation_id:
            return False
        if not input_data.stage_2_output:
            return False
        if not input_data.lens_metrics:
            return False
        if not input_data.complexity_assessment:
            return False
        return True
    
    def _make_decision(self, input_data: Stage2Point5Input) -> GateDecision:
        """Make gate decision based on confidence metrics."""
        # Calculate effective confidence
        confidence = self._calculate_effective_confidence(input_data)
        
        if confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            return GateDecision.PROCEED
        elif confidence >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            return GateDecision.HOLD_FOR_REVIEW
        else:
            return GateDecision.REJECT
    
    def _calculate_effective_confidence(self, input_data: Stage2Point5Input) -> float:
        """
        Calculate overall confidence from multiple factors.
        
        Factors:
        - LENS metrics (40%): Quality of analysis
        - Complexity assessment (40%): Confidence in complexity evaluation
        - Stage 2 design confidence (20%): Solution designer's confidence
        """
        # Extract confidence metrics
        lens_metrics = input_data.lens_metrics
        complexity_assessment = input_data.complexity_assessment
        stage_2_confidence = input_data.stage_2_output.design_confidence
        
        # Calculate average LENS confidence
        lens_confidence = (
            lens_metrics.get('logical', 0.5) +
            lens_metrics.get('evidence', 0.5) +
            lens_metrics.get('narrative', 0.5) +
            lens_metrics.get('semantic', 0.5)
        ) / 4
        
        complexity_confidence = complexity_assessment.get('confidence', 0.5)
        
        # Combined: 40% LENS, 40% complexity, 20% Stage 2
        effective = (
            (lens_confidence * 0.4) +
            (complexity_confidence * 0.4) +
            (stage_2_confidence * 0.2)
        )
        
        return effective
    
    def _determine_approvers(self, input_data: Stage2Point5Input) -> List[str]:
        """
        Determine required approvers based on complexity and risks.
        """
        complexity_level = input_data.complexity_assessment.get('level', 'moderate')
        
        approvers = []
        
        # Risk-based routing
        if 'security' in input_data.stage_2_output.identified_risks:
            approvers.append('security-team')
        
        if complexity_level in ['complex', 'critical']:
            approvers.append('architecture-team')
        
        if input_data.stage_2_output.estimated_effort in ['high', 'critical']:
            approvers.append('resource-team')
        
        if not approvers:
            approvers = ['general-reviewer']
        
        return approvers
    
    def _generate_review_notes(self, input_data: Stage2Point5Input) -> str:
        """Generate review notes for decision."""
        complexity_level = input_data.complexity_assessment.get('level', 'unknown')
        confidence = self._calculate_effective_confidence(input_data)
        
        return (
            f"Complexity: {complexity_level} | "
            f"Confidence: {confidence:.2%} | "
            f"Risks: {', '.join(input_data.stage_2_output.identified_risks) or 'none'}"
        )
    
    def get_execution_statistics(self) -> Dict:
        """Get statistics on all executions."""
        if not self.execution_log:
            return {}
        
        proceed_count = sum(1 for e in self.execution_log if e.decision == GateDecision.PROCEED)
        review_count = sum(1 for e in self.execution_log if e.decision == GateDecision.HOLD_FOR_REVIEW)
        reject_count = sum(1 for e in self.execution_log if e.decision == GateDecision.REJECT)
        
        return {
            'total_executions': len(self.execution_log),
            'proceed': proceed_count,
            'hold_for_review': review_count,
            'reject': reject_count,
            'blocked_count': len(self.blocked_conversations),
            'approved_count': len(self.approved_conversations),
        }
    
    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_log = []
        self.blocked_conversations = []
        self.approved_conversations = []


class ConversationProtocolIntegration:
    """
    ConversationProtocol with Stage 2.5 integration.
    
    Manages workflow through all stages including the new complexity-aware gate.
    """
    
    def __init__(self):
        """Initialize protocol with Stage 2.5 gate."""
        self.stage_2_5_gate = ConversationProtocolStage2Point5()
        self.conversation_states: Dict[str, Dict] = {}
        self.stage_transitions: List[Dict] = []
    
    def transition_to_stage_3(
        self,
        conversation_id: str,
        stage_2_output: Stage2Output,
        lens_metrics: Dict,
        complexity_assessment: Dict
    ) -> Dict:
        """
        Transition from Stage 2 to Stage 3 through the gate.
        
        Args:
            conversation_id: ID of conversation
            stage_2_output: Output from Stage 2
            lens_metrics: LENS confidence metrics
            complexity_assessment: Complexity assessment results
        
        Returns:
            Decision and next stage information
        """
        # Prepare input for gate
        gate_input = Stage2Point5Input(
            conversation_id=conversation_id,
            stage_2_output=stage_2_output,
            lens_metrics=lens_metrics,
            complexity_assessment=complexity_assessment,
            timestamp=datetime.now()
        )
        
        # Execute gate
        gate_output = self.stage_2_5_gate.execute(gate_input)
        
        # Record transition
        transition = {
            'conversation_id': conversation_id,
            'from_stage': ConversationStage.STAGE_2.value,
            'to_stage': ConversationStage.STAGE_3.value if gate_output.can_proceed_to_stage_3 else None,
            'gate_decision': gate_output.decision.value,
            'timestamp': datetime.now()
        }
        self.stage_transitions.append(transition)
        
        # Update state
        self.conversation_states[conversation_id] = {
            'stage': ConversationStage.STAGE_3 if gate_output.can_proceed_to_stage_3 else ConversationStage.STAGE_2_5,
            'gate_output': gate_output
        }
        
        return {
            'conversation_id': conversation_id,
            'can_proceed': gate_output.can_proceed_to_stage_3,
            'decision': gate_output.decision.value,
            'required_approvals': gate_output.required_approvals,
            'next_stage': ConversationStage.STAGE_3.value if gate_output.can_proceed_to_stage_3 else None,
        }
    
    def get_conversation_state(self, conversation_id: str) -> Dict:
        """Get current state of conversation."""
        return self.conversation_states.get(conversation_id, {})
    
    def get_workflow_statistics(self) -> Dict:
        """Get workflow statistics."""
        return self.stage_2_5_gate.get_execution_statistics()
    
    def get_stage_transitions(self) -> List[Dict]:
        """Get all stage transitions."""
        return self.stage_transitions.copy()

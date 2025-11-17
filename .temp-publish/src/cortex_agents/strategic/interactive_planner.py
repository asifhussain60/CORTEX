"""
Interactive Planner Agent (CORTEX 2.1)

Collaborative planning through guided dialogue. Asks clarifying questions
to resolve ambiguous requirements before creating implementation plans.

This agent implements confidence-based routing:
- High confidence (>85%): Execute immediately (no questions)
- Medium confidence (60-85%): Confirm plan with user
- Low confidence (<60%): Interactive questioning mode

Part of CORTEX 2.1 Interactive Planning enhancement.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from src.cortex_agents.agent_types import IntentType


class PlanningState(Enum):
    """States in the interactive planning state machine."""
    DETECTING = "detecting"          # Analyzing ambiguity
    QUESTIONING = "questioning"      # Asking clarifying questions
    CONFIRMING = "confirming"        # Confirming plan with user
    EXECUTING = "executing"          # Executing the plan
    COMPLETED = "completed"          # Planning complete
    ABORTED = "aborted"              # User aborted planning


class QuestionType(Enum):
    """Types of questions that can be asked."""
    REQUIRED = "required"            # Must be answered
    OPTIONAL = "optional"            # Can skip
    MULTIPLE_CHOICE = "choice"       # Select from options
    FREE_TEXT = "text"               # Open-ended
    YES_NO = "boolean"               # Simple yes/no


@dataclass
class Question:
    """
    Represents a clarifying question to ask the user.
    
    Attributes:
        text: Question text to display
        type: Question category (multiple choice, yes/no, etc.)
        options: Available options for multiple choice
        default: Default answer if user skips
        priority: Question priority (1-5, 5 = critical)
        context: Additional context about the question
        id: Unique identifier for the question
    """
    text: str
    type: QuestionType
    options: List[str] = field(default_factory=list)
    default: Optional[str] = None
    priority: int = 3
    context: Dict[str, Any] = field(default_factory=dict)
    id: str = ""
    
    def __post_init__(self):
        """Generate ID if not provided."""
        if not self.id:
            import hashlib
            self.id = hashlib.md5(self.text.encode()).hexdigest()[:8]


@dataclass
class Answer:
    """
    Represents a user's answer to a question.
    
    Attributes:
        question_id: ID of the question being answered
        value: The answer value
        skipped: Whether question was skipped (using default)
        timestamp: When answer was provided
        additional_context: Any extra info extracted from answer
    """
    question_id: str
    value: str
    skipped: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    additional_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanningSession:
    """
    Represents an interactive planning session.
    
    Tracks state, questions, answers, and final plan.
    Persisted to Tier 1 memory for resumption.
    
    Attributes:
        session_id: Unique session identifier
        user_request: Original user request
        confidence: Initial confidence score (0-1)
        state: Current state in planning workflow
        questions: Questions to ask (or already asked)
        answers: User's answers so far
        final_plan: Generated implementation plan
        started_at: Session start time
        completed_at: Session completion time
    """
    session_id: str
    user_request: str
    confidence: float
    state: PlanningState
    questions: List[Question] = field(default_factory=list)
    answers: List[Answer] = field(default_factory=list)
    final_plan: Optional[Dict[str, Any]] = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class InteractivePlannerAgent(BaseAgent):
    """
    Interactive Planning Agent - CORTEX 2.1
    
    Collaborative planning through guided dialogue. Detects ambiguity
    in user requests, asks up to 5 clarifying questions, and creates
    refined implementation plans based on answers.
    
    Features:
    - Confidence-based routing (auto-detect when to ask questions)
    - Question budget (max 5 questions per session)
    - User controls: skip, done, back, restart, abort
    - Session persistence (can resume interrupted sessions)
    - User preference learning (adapts over time)
    
    Workflow:
    1. Detect ambiguity in user request
    2. If confidence < 60%, enter interactive mode
    3. Ask up to 5 clarifying questions (one at a time)
    4. Build refined plan from answers
    5. Confirm plan with user
    6. Execute or save for later
    
    Example:
        planner = InteractivePlannerAgent("Planner", tier1, tier2, tier3)
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Refactor authentication"
        )
        
        response = planner.execute(request)
        # Returns session with questions to ask
    """
    
    # Constants
    MAX_QUESTIONS = 5
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    MEDIUM_CONFIDENCE_THRESHOLD = 0.60
    
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        """
        Initialize Interactive Planner Agent.
        
        Args:
            name: Agent name
            tier1_api: Tier 1 API for conversation memory
            tier2_kg: Tier 2 Knowledge Graph for learning
            tier3_context: Tier 3 Context for metrics
        """
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        self.logger = logging.getLogger(__name__)
        self.active_sessions: Dict[str, PlanningSession] = {}
        
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Args:
            request: Agent request to evaluate
        
        Returns:
            True if request is PLAN intent, False otherwise
        """
        return request.intent in [
            IntentType.PLAN.value,
            "plan",
            "interactive_plan",
            "plan_feature"
        ]
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute interactive planning workflow.
        
        Analyzes ambiguity and routes based on confidence:
        - High confidence (>85%): Execute immediately
        - Medium confidence (60-85%): Confirm plan
        - Low confidence (<60%): Interactive questioning
        
        Args:
            request: Agent request containing user message
        
        Returns:
            AgentResponse with session state and next steps
        """
        start_time = datetime.now()
        
        try:
            # Check if resuming existing session
            session_id = request.context.get("session_id")
            if session_id and session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                self.logger.info(f"Resuming session {session_id}")
            else:
                # Create new session
                confidence = self.detect_ambiguity(request.user_message, request.context)
                session = self._create_session(request.user_message, confidence)
                self.active_sessions[session.session_id] = session
                self.logger.info(f"Created new session {session.session_id}, confidence: {confidence:.2f}")
            
            # Route based on confidence
            if session.confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
                # High confidence: execute immediately
                result = self._execute_immediately(session)
            elif session.confidence >= self.MEDIUM_CONFIDENCE_THRESHOLD:
                # Medium confidence: confirm plan
                result = self._confirm_plan(session)
            else:
                # Low confidence: interactive questioning
                result = self._interactive_questioning(session, request.context)
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return AgentResponse(
                success=True,
                result=result,
                message=self._get_status_message(session),
                metadata={
                    "session_id": session.session_id,
                    "state": session.state.value,
                    "confidence": session.confidence,
                    "questions_asked": len(session.answers),
                    "questions_remaining": len(session.questions) - len(session.answers)
                },
                agent_name=self.name,
                duration_ms=duration_ms
            )
            
        except Exception as e:
            self.logger.error(f"Error in interactive planning: {e}", exc_info=True)
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return AgentResponse(
                success=False,
                result=None,
                message=f"Interactive planning failed: {str(e)}",
                metadata={"error": str(e)},
                agent_name=self.name,
                duration_ms=duration_ms
            )
    
    def detect_ambiguity(self, request: str, context: Dict[str, Any]) -> float:
        """
        Detect ambiguity in user request and calculate confidence score.
        
        Analyzes request for clarity, specificity, and completeness.
        Lower scores indicate more ambiguity (need more questions).
        
        Args:
            request: User's request text
            context: Additional context
        
        Returns:
            Confidence score (0.0 - 1.0)
            - 1.0 = completely clear, no questions needed
            - 0.5 = moderate ambiguity, some questions helpful
            - 0.0 = completely unclear, many questions needed
        """
        confidence = 1.0
        request_lower = request.lower()
        
        # Check for vague terms (reduce confidence)
        vague_terms = ["refactor", "improve", "update", "change", "fix", "enhance"]
        vague_count = sum(1 for term in vague_terms if term in request_lower)
        confidence -= vague_count * 0.25  # Increased penalty from 0.15
        
        # Check for specific technical terms (increase confidence)
        specific_terms = ["jwt", "oauth", "session", "authentication", "api", "endpoint"]
        specific_count = sum(1 for term in specific_terms if term in request_lower)
        confidence += specific_count * 0.08  # Decreased boost from 0.10
        
        # Check request length (very short = ambiguous)
        word_count = len(request.split())
        if word_count < 5:
            confidence -= 0.30  # Increased penalty from 0.20
        elif word_count > 15:
            confidence += 0.10
        
        # Check for implementation details (increase confidence)
        detail_indicators = ["using", "with", "implement", "create", "add"]
        detail_count = sum(1 for term in detail_indicators if term in request_lower)
        confidence += detail_count * 0.04  # Decreased from 0.05
        
        # Check Tier 2 for similar past requests
        if self.tier2:
            similar_patterns = self._find_similar_patterns(request)
            if similar_patterns:
                # Higher confidence if we've done this before
                confidence += 0.15
        
        # Clamp to valid range
        return max(0.0, min(1.0, confidence))
    
    def generate_questions(
        self, 
        request: str, 
        context: Dict[str, Any]
    ) -> List[Question]:
        """
        Generate clarifying questions based on request analysis.
        
        Prioritizes questions by importance and generates up to MAX_QUESTIONS.
        Questions are tailored to the specific ambiguities detected.
        
        Args:
            request: User's request text
            context: Additional context
        
        Returns:
            List of Question objects (up to MAX_QUESTIONS)
        """
        questions = []
        request_lower = request.lower()
        
        # Question 1: If "authentication" or "auth" mentioned
        if "auth" in request_lower:
            questions.append(Question(
                text="What authentication strategy should I use?",
                type=QuestionType.MULTIPLE_CHOICE,
                options=["OAuth 2.0", "JWT tokens", "Session-based", "Other"],
                default="JWT tokens",
                priority=5,
                context={"category": "technical_choice"}
            ))
        
        # Question 2: If "refactor" mentioned
        if "refactor" in request_lower:
            questions.append(Question(
                text="Should I preserve the existing data schema?",
                type=QuestionType.YES_NO,
                options=["Yes (safer)", "No (redesign)"],
                default="Yes (safer)",
                priority=4,
                context={"category": "safety"}
            ))
        
        # Question 3: Backwards compatibility
        questions.append(Question(
            text="Do you need backward compatibility with existing code?",
            type=QuestionType.YES_NO,
            options=["Yes", "No"],
            default="Yes",
            priority=4,
            context={"category": "compatibility"}
        ))
        
        # Question 4: Testing requirements
        questions.append(Question(
            text="Should I create comprehensive tests?",
            type=QuestionType.MULTIPLE_CHOICE,
            options=[
                "Yes (unit + integration tests)",
                "Unit tests only",
                "Integration tests only",
                "No tests"
            ],
            default="Yes (unit + integration tests)",
            priority=3,
            context={"category": "testing"}
        ))
        
        # Question 5: Deployment strategy
        questions.append(Question(
            text="How should this be deployed?",
            type=QuestionType.MULTIPLE_CHOICE,
            options=[
                "All at once",
                "Gradual rollout",
                "Feature flag",
                "Not sure"
            ],
            default="Gradual rollout",
            priority=2,
            context={"category": "deployment"}
        ))
        
        # Sort by priority (highest first) and limit to MAX_QUESTIONS
        questions.sort(key=lambda q: q.priority, reverse=True)
        return questions[:self.MAX_QUESTIONS]
    
    def process_answer(
        self, 
        session: PlanningSession,
        question: Question, 
        answer_text: str
    ) -> Answer:
        """
        Process user's answer and extract context.
        
        Args:
            session: Current planning session
            question: Question that was answered
            answer_text: User's answer text
        
        Returns:
            Answer object with parsed value and context
        """
        answer_lower = answer_text.lower().strip()
        
        # Check for control commands
        if answer_lower in ["skip", "s"]:
            return Answer(
                question_id=question.id,
                value=question.default or "",
                skipped=True
            )
        
        # For multiple choice, accept letter or full answer
        if question.type == QuestionType.MULTIPLE_CHOICE:
            # Try to match letter (A, B, C, D)
            if len(answer_lower) == 1 and answer_lower.isalpha():
                idx = ord(answer_lower) - ord('a')
                if 0 <= idx < len(question.options):
                    value = question.options[idx]
                else:
                    value = question.default or question.options[0]
            else:
                # Try to find matching option
                value = next(
                    (opt for opt in question.options if opt.lower() in answer_lower),
                    question.default or question.options[0]
                )
        else:
            value = answer_text
        
        # Extract additional context (for future: could parse "and also...")
        additional_context = {}
        
        return Answer(
            question_id=question.id,
            value=value,
            skipped=False,
            additional_context=additional_context
        )
    
    def build_refined_plan(
        self, 
        session: PlanningSession
    ) -> Dict[str, Any]:
        """
        Build implementation plan from collected answers.
        
        Delegates to WorkPlanner for proper task breakdown after enriching
        the request with collected answers and context.
        
        Args:
            session: Planning session with answers
        
        Returns:
            Implementation plan dictionary with phases and tasks
        """
        # Build enriched request for WorkPlanner
        enriched_request = self._build_enriched_request(session)
        
        # Import WorkPlanner here to avoid circular dependency
        try:
            from src.cortex_agents.work_planner.agent import WorkPlanner
            
            # Create WorkPlanner instance
            work_planner = WorkPlanner(
                name="WorkPlanner",
                tier1_api=self.tier1,
                tier2_kg=self.tier2,
                tier3_context=self.tier3
            )
            
            # Create request for WorkPlanner
            from src.cortex_agents.base_agent import AgentRequest
            planner_request = AgentRequest(
                intent="plan",
                context=enriched_request["context"],
                user_message=enriched_request["refined_message"],
                conversation_id=session.session_id,
                priority="normal"
            )
            
            # Get task breakdown from WorkPlanner
            planner_response = work_planner.execute(planner_request)
            
            if planner_response.success:
                # Extract tasks and build structured plan
                tasks = planner_response.result.get("tasks", [])
                total_hours = planner_response.result.get("total_hours", 0)
                
                # Organize tasks into phases
                plan = {
                    "title": f"Implementation Plan: {session.user_request}",
                    "created_at": datetime.now().isoformat(),
                    "session_id": session.session_id,
                    "phases": self._organize_tasks_into_phases(tasks),
                    "total_estimate_hours": total_hours,
                    "considerations": [
                        f"Decision: {answer.value}" 
                        for answer in session.answers
                    ],
                    "complexity": planner_response.result.get("complexity", "medium"),
                    "risks": planner_response.result.get("risks", [])
                }
                
                return plan
            else:
                # Fallback to basic plan if WorkPlanner fails
                self.logger.warning(f"WorkPlanner failed, using fallback plan: {planner_response.message}")
                return self._create_fallback_plan(session)
                
        except ImportError as e:
            self.logger.error(f"Failed to import WorkPlanner: {e}")
            return self._create_fallback_plan(session)
        except Exception as e:
            self.logger.error(f"Error delegating to WorkPlanner: {e}")
            return self._create_fallback_plan(session)
    
    def _build_enriched_request(self, session: PlanningSession) -> Dict[str, Any]:
        """
        Build enriched request with all collected context for WorkPlanner.
        
        Transforms user answers into structured context that WorkPlanner
        can use for better task breakdown and estimation.
        """
        # Extract key decisions from answers
        context = {
            "original_request": session.user_request,
            "interactive_session": True,
            "confidence": session.confidence,
            "answers": {}
        }
        
        # Map answers to context
        for answer in session.answers:
            context["answers"][answer.question_id] = {
                "value": answer.value,
                "skipped": answer.skipped,
                "context": answer.additional_context
            }
        
        # Build refined message incorporating answers
        refined_parts = [session.user_request]
        
        for answer in session.answers:
            if not answer.skipped and answer.value:
                refined_parts.append(f"• {answer.value}")
        
        refined_message = " | ".join(refined_parts)
        
        return {
            "context": context,
            "refined_message": refined_message
        }
    
    def _organize_tasks_into_phases(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Organize flat task list into logical phases.
        
        Groups related tasks into phases for better presentation.
        """
        if not tasks:
            return []
        
        # Simple phase organization: group tasks by prefix or create single phase
        phases = []
        current_phase = {
            "phase": 1,
            "name": "Implementation",
            "tasks": [],
            "estimated_hours": 0
        }
        
        for task in tasks:
            task_name = task.get("name", "Task")
            task_hours = task.get("estimated_hours", 1)
            
            current_phase["tasks"].append(task_name)
            current_phase["estimated_hours"] += task_hours
        
        phases.append(current_phase)
        return phases
    
    def _create_fallback_plan(self, session: PlanningSession) -> Dict[str, Any]:
        """
        Create fallback plan if WorkPlanner integration fails.
        
        Uses simple heuristics based on collected answers.
        """
        plan = {
            "title": f"Implementation Plan: {session.user_request}",
            "created_at": datetime.now().isoformat(),
            "session_id": session.session_id,
            "phases": [
                {
                    "phase": 1,
                    "name": "Implementation",
                    "tasks": [session.user_request],
                    "estimated_hours": 2
                }
            ],
            "total_estimate_hours": 2,
            "considerations": [
                f"Decision: {answer.value}" 
                for answer in session.answers
            ],
            "fallback": True
        }
        
        return plan
    
    # Private helper methods
    
    def _create_session(self, user_request: str, confidence: float) -> PlanningSession:
        """Create new planning session with unique ID."""
        import uuid
        session_id = f"plan-{uuid.uuid4().hex[:8]}"
        
        return PlanningSession(
            session_id=session_id,
            user_request=user_request,
            confidence=confidence,
            state=PlanningState.DETECTING
        )
    
    def _execute_immediately(self, session: PlanningSession) -> Dict[str, Any]:
        """Handle high confidence: execute without questions."""
        session.state = PlanningState.EXECUTING
        
        # Build plan without questions
        session.final_plan = {
            "title": f"Auto-generated Plan: {session.user_request}",
            "confidence": session.confidence,
            "phases": [
                {
                    "phase": 1,
                    "name": "Implementation",
                    "tasks": [session.user_request],
                    "estimated_hours": 2
                }
            ]
        }
        
        return {
            "action": "execute",
            "session": session,
            "message": "High confidence - executing immediately",
            "plan": session.final_plan
        }
    
    def _confirm_plan(self, session: PlanningSession) -> Dict[str, Any]:
        """Handle medium confidence: generate plan and ask for confirmation."""
        session.state = PlanningState.CONFIRMING
        
        # Generate basic plan
        session.final_plan = self.build_refined_plan(session)
        
        return {
            "action": "confirm",
            "session": session,
            "message": "Please confirm this plan before proceeding",
            "plan": session.final_plan,
            "prompt": "Proceed? (yes/no/modify)"
        }
    
    def _interactive_questioning(
        self, 
        session: PlanningSession,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle low confidence: ask clarifying questions."""
        
        # Generate questions if not already done
        if not session.questions:
            session.questions = self.generate_questions(session.user_request, context)
            session.state = PlanningState.QUESTIONING
        
        # Check for user answer in context
        user_input = context.get("user_input", "").strip()
        
        # Handle control commands
        if user_input.lower() in ["done", "finish", "enough"]:
            # User wants to finish early
            session.state = PlanningState.CONFIRMING
            session.final_plan = self.build_refined_plan(session)
            
            return {
                "action": "confirm",
                "session": session,
                "message": "Great! I have enough to create a plan.",
                "plan": session.final_plan,
                "prompt": "Proceed? (yes/no/modify)"
            }
        
        if user_input.lower() in ["abort", "cancel", "quit"]:
            session.state = PlanningState.ABORTED
            return {
                "action": "abort",
                "session": session,
                "message": "Planning cancelled."
            }
        
        # Process answer if provided
        if user_input and len(session.answers) < len(session.questions):
            current_question = session.questions[len(session.answers)]
            answer = self.process_answer(session, current_question, user_input)
            session.answers.append(answer)
        
        # Check if more questions needed
        if len(session.answers) >= len(session.questions):
            # All questions answered
            session.state = PlanningState.CONFIRMING
            session.final_plan = self.build_refined_plan(session)
            
            return {
                "action": "confirm",
                "session": session,
                "message": "All questions answered! Here's the plan:",
                "plan": session.final_plan,
                "prompt": "Proceed? (yes/no/modify)"
            }
        
        # Ask next question
        next_question = session.questions[len(session.answers)]
        
        return {
            "action": "question",
            "session": session,
            "question": next_question,
            "question_number": len(session.answers) + 1,
            "total_questions": len(session.questions),
            "message": self._format_question(next_question, len(session.answers) + 1, len(session.questions))
        }
    
    def _format_question(self, question: Question, num: int, total: int) -> str:
        """Format question for display to user."""
        lines = [
            f"\nQuestion {num}/{total}: {question.text}"
        ]
        
        if question.type == QuestionType.MULTIPLE_CHOICE:
            for i, option in enumerate(question.options):
                letter = chr(ord('A') + i)
                lines.append(f"  {letter}) {option}")
        elif question.type == QuestionType.YES_NO:
            lines.append("  A) Yes")
            lines.append("  B) No")
        else:
            lines.append("  (Free text answer)")
        
        if question.default:
            lines.append(f"  [Default: {question.default}]")
        
        lines.append("\n(Type 'skip' to use default, 'done' to finish early, 'abort' to cancel)")
        
        return "\n".join(lines)
    
    def _get_status_message(self, session: PlanningSession) -> str:
        """Get human-readable status message."""
        state_messages = {
            PlanningState.DETECTING: "Analyzing request ambiguity...",
            PlanningState.QUESTIONING: f"Interactive planning: {len(session.answers)}/{len(session.questions)} questions answered",
            PlanningState.CONFIRMING: "Plan ready for confirmation",
            PlanningState.EXECUTING: "Executing plan...",
            PlanningState.COMPLETED: "Planning completed successfully",
            PlanningState.ABORTED: "Planning cancelled by user"
        }
        return state_messages.get(session.state, "Unknown state")
    
    def _find_similar_patterns(self, request: str) -> List[Dict[str, Any]]:
        """Query Tier 2 for similar past requests (placeholder)."""
        # TODO: Implement Tier 2 query when available
        return []

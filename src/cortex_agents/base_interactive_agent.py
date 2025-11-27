"""
Base Interactive Agent

Provides reusable Q&A framework for interactive conversation-based data collection.
Used by ADO Planning, Code Review, Feedback, and other template-based modules.

Features:
- Question flow management with branching logic
- State management (answers, edits, progress)
- Type validation (text, choice, multiline, checklist, number)
- Edit/preview capabilities
- Smart defaults and skip handling
- YAML-based question schemas

Example Usage:
    schema = QuestionSchema.load("ado-planning")
    agent = BaseInteractiveAgent("ADO Planning", schema, tier1_api)
    
    response = agent.start_conversation(request)
    # Agent asks questions one-by-one, collects answers
    # User can edit, preview, approve
    # Agent generates final output
"""

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime
from enum import Enum
import yaml
import os

from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse


class QuestionType(Enum):
    """Question types supported by interactive agents"""
    TEXT = "text"                    # Single-line text input
    MULTILINE = "multiline"          # Multi-line text input
    CHOICE = "choice"                # Single choice from options
    MULTI_CHOICE = "multi_choice"    # Multiple choices from options
    CHECKLIST = "checklist"          # Checklist items (for acceptance criteria)
    NUMBER = "number"                # Numeric input
    BOOLEAN = "boolean"              # Yes/No question


@dataclass
class Question:
    """
    Individual question definition.
    
    Attributes:
        id: Unique question identifier
        type: Question type (text, choice, etc.)
        prompt: Question text shown to user
        required: Whether answer is required
        default: Default value if user skips
        options: Available options (for choice/multi_choice)
        validation: Validation function or regex pattern
        skip_if: Condition to skip this question (callable or field reference)
        help_text: Additional help text for user
        placeholder: Example/placeholder text
    """
    id: str
    type: QuestionType
    prompt: str
    required: bool = True
    default: Any = None
    options: List[str] = field(default_factory=list)
    validation: Optional[Union[str, Callable]] = None
    skip_if: Optional[Union[str, Callable]] = None
    help_text: Optional[str] = None
    placeholder: Optional[str] = None
    
    def should_skip(self, answers: Dict[str, Any]) -> bool:
        """
        Check if question should be skipped based on previous answers.
        
        Args:
            answers: Previously collected answers
        
        Returns:
            True if question should be skipped
        """
        if not self.skip_if:
            return False
        
        if callable(self.skip_if):
            return self.skip_if(answers)
        
        # String-based condition (e.g., "work_item_type != Bug")
        if isinstance(self.skip_if, str):
            try:
                # Simple evaluation: field == value or field != value
                if "==" in self.skip_if:
                    field, value = self.skip_if.split("==")
                    return answers.get(field.strip()) == value.strip()
                elif "!=" in self.skip_if:
                    field, value = self.skip_if.split("!=")
                    return answers.get(field.strip()) != value.strip()
            except:
                pass
        
        return False
    
    def validate_answer(self, answer: Any) -> tuple[bool, Optional[str]]:
        """
        Validate answer against question requirements.
        
        Args:
            answer: User's answer
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required
        if self.required and not answer:
            return False, "This field is required"
        
        # Type-specific validation
        if self.type == QuestionType.NUMBER:
            try:
                float(answer)
            except (ValueError, TypeError):
                return False, "Must be a number"
        
        if self.type in [QuestionType.CHOICE, QuestionType.MULTI_CHOICE]:
            if self.options and answer not in self.options:
                return False, f"Must be one of: {', '.join(self.options)}"
        
        # Custom validation
        if self.validation and callable(self.validation):
            return self.validation(answer)
        
        return True, None


@dataclass
class QuestionSchema:
    """
    Schema defining a complete question flow.
    
    Attributes:
        name: Schema name (e.g., "ado-planning")
        version: Schema version
        questions: List of questions in order
        metadata: Additional metadata about the schema
    """
    name: str
    version: str
    questions: List[Question]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def load(cls, schema_name: str) -> 'QuestionSchema':
        """
        Load question schema from YAML file.
        
        Args:
            schema_name: Name of schema to load (e.g., "ado-planning")
        
        Returns:
            QuestionSchema instance
        """
        schema_dir = os.path.join(
            os.path.dirname(__file__),
            "../../cortex-brain/schemas/question-schemas"
        )
        schema_path = os.path.join(schema_dir, f"{schema_name}.yaml")
        
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        questions = []
        for q_data in data.get('questions', []):
            questions.append(Question(
                id=q_data['id'],
                type=QuestionType(q_data['type']),
                prompt=q_data['prompt'],
                required=q_data.get('required', True),
                default=q_data.get('default'),
                options=q_data.get('options', []),
                help_text=q_data.get('help_text'),
                placeholder=q_data.get('placeholder'),
                skip_if=q_data.get('skip_if')
            ))
        
        return cls(
            name=data['name'],
            version=data['version'],
            questions=questions,
            metadata=data.get('metadata', {})
        )


@dataclass
class ConversationState:
    """
    Tracks state of interactive conversation.
    
    Attributes:
        session_id: Unique session identifier
        schema: Question schema being used
        answers: Collected answers (question_id -> answer)
        current_question_index: Index of current question
        is_complete: Whether all questions answered
        preview_shown: Whether preview has been shown
        started_at: When conversation started
        updated_at: Last update time
    """
    session_id: str
    schema: QuestionSchema
    answers: Dict[str, Any] = field(default_factory=dict)
    current_question_index: int = 0
    is_complete: bool = False
    preview_shown: bool = False
    started_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def get_current_question(self) -> Optional[Question]:
        """Get current question, skipping any that should be skipped."""
        while self.current_question_index < len(self.schema.questions):
            question = self.schema.questions[self.current_question_index]
            
            if question.should_skip(self.answers):
                self.current_question_index += 1
                continue
            
            return question
        
        return None  # No more questions
    
    def record_answer(self, question_id: str, answer: Any):
        """Record answer and move to next question."""
        self.answers[question_id] = answer
        self.current_question_index += 1
        self.updated_at = datetime.now()
        
        # Check if complete
        if self.get_current_question() is None:
            self.is_complete = True
    
    def edit_answer(self, question_id: str, new_answer: Any):
        """Edit a previously recorded answer."""
        if question_id in self.answers:
            self.answers[question_id] = new_answer
            self.updated_at = datetime.now()
    
    def get_progress(self) -> str:
        """Get progress string (e.g., '5/10 questions')."""
        total = len([q for q in self.schema.questions if not q.should_skip(self.answers)])
        answered = len(self.answers)
        return f"{answered}/{total} questions"


class BaseInteractiveAgent(BaseAgent):
    """
    Base class for interactive Q&A agents.
    
    Provides reusable conversation flow management for collecting structured
    data through interactive questions.
    
    Subclasses must implement:
    - generate_output(): Generate final output from collected answers
    - get_schema_name(): Return schema name to load
    
    Features:
    - Automatic question flow with skip logic
    - Answer validation and error handling
    - Edit capabilities ("change priority to 1")
    - Preview before finalizing
    - State persistence via Tier 1
    
    Example:
        class ADOInteractiveAgent(BaseInteractiveAgent):
            def get_schema_name(self) -> str:
                return "ado-planning"
            
            def generate_output(self, state: ConversationState) -> Dict[str, Any]:
                # Generate ADO planning document from state.answers
                return {"file_path": path, "content": content}
    """
    
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize interactive agent."""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        
        # Load schema
        self.schema = QuestionSchema.load(self.get_schema_name())
        
        # Active conversation states (session_id -> state)
        self.active_conversations: Dict[str, ConversationState] = {}
    
    @abstractmethod
    def get_schema_name(self) -> str:
        """
        Return the schema name to load.
        
        Returns:
            Schema name (e.g., "ado-planning", "code-review")
        """
        pass
    
    @abstractmethod
    def generate_output(self, state: ConversationState) -> Dict[str, Any]:
        """
        Generate final output from collected answers.
        
        Args:
            state: Completed conversation state
        
        Returns:
            Dict with output data (file_path, content, etc.)
        """
        pass
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Subclasses should override to check specific intent.
        """
        return False  # Override in subclass
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute interactive conversation flow.
        
        Handles:
        - Starting new conversation
        - Answering questions
        - Editing answers
        - Showing preview
        - Finalizing output
        """
        self.log_request(request)
        
        try:
            # Check for conversation session
            session_id = request.context.get('session_id')
            
            # Handle different conversation commands
            user_msg = request.user_message.lower()
            
            if not session_id or session_id not in self.active_conversations:
                # Start new conversation
                return self._start_conversation(request)
            
            # Get active state
            state = self.active_conversations[session_id]
            
            # Handle commands
            if user_msg in ["preview", "show preview", "let me see"]:
                return self._show_preview(state, request)
            
            if user_msg in ["approve", "looks good", "yes", "confirm"]:
                return self._finalize(state, request)
            
            if user_msg in ["cancel", "stop", "exit", "quit"]:
                return self._cancel_conversation(state, request)
            
            if user_msg.startswith("edit ") or user_msg.startswith("change "):
                return self._handle_edit(state, request)
            
            # Otherwise, treat as answer to current question
            return self._handle_answer(state, request)
            
        except Exception as e:
            self.logger.error(f"Interactive conversation failed: {str(e)}")
            return AgentResponse(
                success=False,
                result=None,
                message=f"Conversation failed: {str(e)}",
                agent_name=self.name
            )
    
    def _start_conversation(self, request: AgentRequest) -> AgentResponse:
        """Start a new interactive conversation."""
        # Create session
        session_id = f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        state = ConversationState(
            session_id=session_id,
            schema=self.schema
        )
        self.active_conversations[session_id] = state
        
        # Get first question
        question = state.get_current_question()
        if not question:
            return AgentResponse(
                success=False,
                result=None,
                message="No questions in schema",
                agent_name=self.name
            )
        
        # Format question prompt
        prompt = self._format_question_prompt(question, state)
        
        return AgentResponse(
            success=True,
            result={"session_id": session_id, "question": question.id},
            message=prompt,
            agent_name=self.name,
            metadata={"progress": state.get_progress()}
        )
    
    def _handle_answer(self, state: ConversationState, request: AgentRequest) -> AgentResponse:
        """Handle answer to current question."""
        question = state.get_current_question()
        if not question:
            # No more questions - show preview
            return self._show_preview(state, request)
        
        answer = request.user_message.strip()
        
        # Handle skip/none
        if answer.lower() in ["skip", "none", ""]:
            if question.required:
                return AgentResponse(
                    success=False,
                    result=None,
                    message=f"This field is required. {question.prompt}",
                    agent_name=self.name
                )
            answer = question.default
        
        # Validate answer
        is_valid, error = question.validate_answer(answer)
        if not is_valid:
            return AgentResponse(
                success=False,
                result=None,
                message=f"Invalid answer: {error}\n\n{question.prompt}",
                agent_name=self.name
            )
        
        # Record answer
        state.record_answer(question.id, answer)
        
        # Get next question
        next_question = state.get_current_question()
        if not next_question:
            # All done - show preview
            return self._show_preview(state, request)
        
        # Ask next question
        prompt = self._format_question_prompt(next_question, state)
        
        return AgentResponse(
            success=True,
            result={"session_id": state.session_id, "question": next_question.id},
            message=prompt,
            agent_name=self.name,
            metadata={"progress": state.get_progress()}
        )
    
    def _show_preview(self, state: ConversationState, request: AgentRequest) -> AgentResponse:
        """Show preview of collected data."""
        preview = self._generate_preview(state)
        state.preview_shown = True
        
        return AgentResponse(
            success=True,
            result={"session_id": state.session_id, "preview": preview},
            message=f"{preview}\n\n**Approve?** (say 'approve' or 'edit [field]')",
            agent_name=self.name,
            metadata={"preview_shown": True}
        )
    
    def _finalize(self, state: ConversationState, request: AgentRequest) -> AgentResponse:
        """Finalize and generate output."""
        if not state.preview_shown:
            return self._show_preview(state, request)
        
        # Generate final output
        output = self.generate_output(state)
        
        # Clean up session
        del self.active_conversations[state.session_id]
        
        return AgentResponse(
            success=True,
            result=output,
            message=f"✅ Created successfully!\n\n{output.get('summary', '')}",
            agent_name=self.name
        )
    
    def _handle_edit(self, state: ConversationState, request: AgentRequest) -> AgentResponse:
        """Handle edit command."""
        # Parse edit command: "edit priority" or "change title to 'New Title'"
        msg = request.user_message.lower()
        
        # Simple parsing for now
        for question in state.schema.questions:
            if question.id.lower() in msg:
                # Found the field to edit
                new_value = msg.split("to")[-1].strip() if "to" in msg else ""
                
                if new_value:
                    state.edit_answer(question.id, new_value)
                    return AgentResponse(
                        success=True,
                        result={"session_id": state.session_id},
                        message=f"Updated {question.id}. {self._generate_preview(state)}",
                        agent_name=self.name
                    )
                else:
                    # Ask for new value
                    return AgentResponse(
                        success=True,
                        result={"session_id": state.session_id, "editing": question.id},
                        message=f"What should {question.id} be?",
                        agent_name=self.name
                    )
        
        return AgentResponse(
            success=False,
            result=None,
            message="Could not parse edit command. Try: 'edit priority to 1'",
            agent_name=self.name
        )
    
    def _cancel_conversation(self, state: ConversationState, request: AgentRequest) -> AgentResponse:
        """Cancel active conversation."""
        del self.active_conversations[state.session_id]
        
        return AgentResponse(
            success=True,
            result=None,
            message="Conversation cancelled.",
            agent_name=self.name
        )
    
    def _format_question_prompt(self, question: Question, state: ConversationState) -> str:
        """Format question prompt with help text and progress."""
        prompt = f"**{question.prompt}**"
        
        if question.options:
            prompt += f"\nOptions: {', '.join(question.options)}"
        
        if question.placeholder:
            prompt += f"\nExample: {question.placeholder}"
        
        if question.help_text:
            prompt += f"\n\n_{question.help_text}_"
        
        if not question.required:
            prompt += "\n\n(Optional - say 'skip' to skip)"
        
        prompt += f"\n\n_Progress: {state.get_progress()}_"
        
        return prompt
    
    def _generate_preview(self, state: ConversationState) -> str:
        """Generate preview of collected answers."""
        lines = ["**Preview:**\n"]
        
        for question in state.schema.questions:
            if question.id in state.answers:
                answer = state.answers[question.id]
                lines.append(f"- **{question.prompt}**: {answer}")
        
        return "\n".join(lines)

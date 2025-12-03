"""
SWAGGER Estimation Utility

SWAGGER = Scientific Wild Ass Guess Given by Experts with Rationale

Provides Definition of Ready (DoR) validation, work decomposition, and project
estimation with ADO-ready output. Replaces swagger_entry_point_orchestrator.py.

Author: Asif Hussain
Version: 1.0.0 (Migrated from orchestrator)

CRITICAL: Estimation is BLOCKED until DoR score >= 80%

Self-Test: python3 -m src.operations.modules.estimation.swagger_estimation_utility
"""

import json
import hashlib
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Optional TimeframeEstimator integration
try:
    from src.agents.estimation.timeframe_estimator import TimeframeEstimator, TimeEstimate
    TIMEFRAME_ESTIMATOR_AVAILABLE = True
except ImportError:
    TIMEFRAME_ESTIMATOR_AVAILABLE = False
    TimeframeEstimator = None
    TimeEstimate = None


# ============================================================================
# ENTITIES (Enums + Dataclasses)
# ============================================================================

class DoRStatus(Enum):
    """Definition of Ready validation status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


class WorkItemType(Enum):
    """ADO work item types."""
    EPIC = "Epic"
    FEATURE = "Feature"
    USER_STORY = "User Story"
    TASK = "Task"
    BUG = "Bug"


class StoryPointScale(Enum):
    """Modified Fibonacci scale for story points."""
    XS = 1    # Trivial change, <2 hours
    S = 2     # Small, 2-4 hours
    M = 3     # Medium, 4-8 hours (1 day)
    L = 5     # Large, 1-2 days
    XL = 8    # Extra large, 2-3 days
    XXL = 13  # Very large, 3-5 days (should be broken down)


@dataclass
class DoRQuestion:
    """Definition of Ready validation question."""
    id: str
    category: str  # requirements, dependencies, technical, security, testing
    question: str
    required: bool = True
    follow_up_questions: List[str] = field(default_factory=list)
    validation_hints: List[str] = field(default_factory=list)
    answer: Optional[str] = None
    is_valid: bool = False


@dataclass
class DoRValidationResult:
    """Result of DoR validation."""
    status: DoRStatus
    score: float  # 0.0 to 1.0
    questions_answered: int
    questions_total: int
    missing_categories: List[str]
    ambiguous_answers: List[Dict[str, str]]
    recommendations: List[str]
    can_estimate: bool
    validation_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ADOStory:
    """ADO-ready User Story."""
    id: str
    title: str
    description: str
    acceptance_criteria: List[str]
    story_points: int
    priority: int  # 1-4 (1=Critical, 4=Low)
    tags: List[str]
    parent_feature_id: Optional[str]
    implementation_plan: List[str]
    technical_notes: str
    dependencies: List[str]
    estimated_hours: float
    complexity: str  # Low, Medium, High, Very High


@dataclass
class ADOFeature:
    """ADO-ready Feature."""
    id: str
    title: str
    description: str
    business_value: str
    acceptance_criteria: List[str]
    priority: int
    tags: List[str]
    stories: List[ADOStory]
    total_story_points: int
    estimated_sprints: float
    risk_level: str  # Low, Medium, High


@dataclass
class WorkDecompositionResult:
    """Result of work decomposition."""
    original_description: str
    features: List[ADOFeature]
    total_stories: int
    total_story_points: int
    estimated_sprints: float
    estimated_hours: float
    team_size_recommendation: str
    ado_export_json: str  # JSON ready for ADO import
    markdown_summary: str


# ============================================================================
# OPERATION 1-8: DoR Validation Operations
# ============================================================================

# DoR threshold - NEVER provide estimates below this
DOR_THRESHOLD = 0.8

# Category-specific question templates
QUESTION_TEMPLATES = {
    "requirements": [
        DoRQuestion(
            id="req_1",
            category="requirements",
            question="What SPECIFIC problem does this feature solve?",
            required=True,
            validation_hints=["Avoid vague terms like 'improve', 'enhance', 'better'"],
            follow_up_questions=["What is the current behavior?", "What should change?"]
        ),
        DoRQuestion(
            id="req_2",
            category="requirements",
            question="Who are the SPECIFIC users of this feature?",
            required=True,
            validation_hints=["List user roles/personas", "Avoid 'all users'"],
            follow_up_questions=["What permissions do they need?", "How many users expected?"]
        ),
        DoRQuestion(
            id="req_3",
            category="requirements",
            question="What are the MEASURABLE success criteria?",
            required=True,
            validation_hints=["Include numbers, percentages, or specific metrics"],
            follow_up_questions=["How will success be measured?", "What KPIs will change?"]
        ),
        DoRQuestion(
            id="req_4",
            category="requirements",
            question="What are the EXACT input/output specifications?",
            required=True,
            validation_hints=["Data formats, field names, API contracts"],
            follow_up_questions=["What validation rules apply?", "What error scenarios exist?"]
        ),
    ],
    "dependencies": [
        DoRQuestion(
            id="dep_1",
            category="dependencies",
            question="What EXTERNAL systems/APIs does this feature depend on?",
            required=True,
            validation_hints=["List all external integrations", "Include authentication methods"],
            follow_up_questions=["Are there SLAs?", "What's the fallback if unavailable?"]
        ),
        DoRQuestion(
            id="dep_2",
            category="dependencies",
            question="What INTERNAL components must exist before this can work?",
            required=True,
            validation_hints=["Database schemas, services, UI components"],
            follow_up_questions=["What's the current state?", "Who owns these components?"]
        ),
        DoRQuestion(
            id="dep_3",
            category="dependencies",
            question="What OTHER work items/features must be completed first?",
            required=False,
            validation_hints=["ADO item numbers if known", "Feature names"],
            follow_up_questions=["Are these in the current sprint?", "Who is working on them?"]
        ),
    ],
    "technical": [
        DoRQuestion(
            id="tech_1",
            category="technical",
            question="What is the proposed TECHNICAL approach?",
            required=True,
            validation_hints=["Architecture pattern", "Key technologies", "Data flow"],
            follow_up_questions=["Why this approach?", "What alternatives were considered?"]
        ),
        DoRQuestion(
            id="tech_2",
            category="technical",
            question="What are the PERFORMANCE requirements?",
            required=True,
            validation_hints=["Response times", "Throughput", "Memory limits"],
            follow_up_questions=["Peak load expectations?", "Caching strategy?"]
        ),
        DoRQuestion(
            id="tech_3",
            category="technical",
            question="What are the SCALABILITY considerations?",
            required=False,
            validation_hints=["User growth expectations", "Data volume growth"],
            follow_up_questions=["Horizontal vs vertical scaling?", "Database partitioning?"]
        ),
    ],
    "security": [
        DoRQuestion(
            id="sec_1",
            category="security",
            question="What AUTHENTICATION/AUTHORIZATION is required?",
            required=True,
            validation_hints=["OAuth, JWT, RBAC, specific permissions"],
            follow_up_questions=["Who can access?", "What actions are allowed?"]
        ),
        DoRQuestion(
            id="sec_2",
            category="security",
            question="What SENSITIVE DATA does this feature handle?",
            required=True,
            validation_hints=["PII, financial, health data", "Encryption requirements"],
            follow_up_questions=["Data retention policy?", "GDPR/compliance needs?"]
        ),
        DoRQuestion(
            id="sec_3",
            category="security",
            question="What are the potential SECURITY RISKS?",
            required=True,
            validation_hints=["OWASP Top 10 categories", "Attack vectors"],
            follow_up_questions=["Mitigation strategies?", "Security testing plan?"]
        ),
    ],
    "testing": [
        DoRQuestion(
            id="test_1",
            category="testing",
            question="What are the KEY test scenarios?",
            required=True,
            validation_hints=["Happy path, edge cases, error scenarios"],
            follow_up_questions=["How many test cases estimated?", "Manual vs automated?"]
        ),
        DoRQuestion(
            id="test_2",
            category="testing",
            question="What is the EXPECTED test coverage?",
            required=True,
            validation_hints=["Unit test %, integration test %, E2E coverage"],
            follow_up_questions=["Critical paths?", "Performance test scenarios?"]
        ),
    ],
}


def initialize_dor_questions() -> List[DoRQuestion]:
    """
    Initialize DoR question list from templates.
    
    Returns:
        List of DoRQuestion instances
        
    Example:
        >>> questions = initialize_dor_questions()
        >>> len(questions)
        15
    """
    questions = []
    for category, question_list in QUESTION_TEMPLATES.items():
        for q in question_list:
            questions.append(DoRQuestion(
                id=q.id,
                category=q.category,
                question=q.question,
                required=q.required,
                validation_hints=q.validation_hints.copy(),
                follow_up_questions=q.follow_up_questions.copy()
            ))
    return questions


def get_next_unanswered_question(questions: List[DoRQuestion]) -> Optional[DoRQuestion]:
    """
    Get the next unanswered question from DoR questionnaire.
    
    Args:
        questions: List of DoR questions
        
    Returns:
        Next unanswered question or None if all answered
        
    Example:
        >>> questions = initialize_dor_questions()
        >>> next_q = get_next_unanswered_question(questions)
        >>> next_q.id
        'req_1'
    """
    for q in questions:
        if q.answer is None:
            return q
    return None


def get_questions_by_category(questions: List[DoRQuestion], category: str) -> List[DoRQuestion]:
    """
    Filter questions by category.
    
    Args:
        questions: List of DoR questions
        category: Category name (requirements, dependencies, technical, security, testing)
        
    Returns:
        Questions matching category
        
    Example:
        >>> questions = initialize_dor_questions()
        >>> req_questions = get_questions_by_category(questions, "requirements")
        >>> len(req_questions)
        4
    """
    return [q for q in questions if q.category == category]


def validate_answer(question: DoRQuestion, answer: str) -> Tuple[bool, List[str]]:
    """
    Validate a DoR answer for completeness and specificity.
    
    Args:
        question: DoR question being answered
        answer: User's answer text
        
    Returns:
        (is_valid, feedback_messages)
        
    Example:
        >>> q = DoRQuestion(id="test", category="requirements", question="Test?")
        >>> is_valid, feedback = validate_answer(q, "Vague answer")
        >>> is_valid
        False
    """
    feedback = []
    
    # Check minimum length
    if not answer or len(answer.strip()) < 10:
        feedback.append("Answer is too brief. Please provide more detail.")
        return False, feedback
    
    # Check for vague terms
    vague_terms = [
        "improve", "enhance", "better", "good", "fast", "slow",
        "user-friendly", "nice", "clean", "simple", "easy",
        "soon", "later", "maybe", "probably", "should work"
    ]
    found_vague = [term for term in vague_terms if term.lower() in answer.lower()]
    if found_vague:
        feedback.append(f"Vague terms detected: {', '.join(found_vague)}. Please be specific.")
        feedback.extend([f"💡 Hint: {hint}" for hint in question.validation_hints])
        return False, feedback
    
    # Check measurable criteria for success criteria questions
    if question.category == "requirements" and "measurable" in question.question.lower():
        has_numbers = any(char.isdigit() for char in answer)
        has_metrics = any(term in answer.lower() for term in [
            "%", "percent", "seconds", "ms", "minutes", "hours",
            "per day", "per hour", "requests", "users", "items"
        ])
        if not has_numbers and not has_metrics:
            feedback.append("Success criteria should include measurable metrics (numbers, percentages, time units).")
            return False, feedback
    
    return True, ["✅ Answer accepted"]


def submit_dor_answer(
    questions: List[DoRQuestion],
    question_id: str,
    answer: str
) -> Tuple[bool, List[str]]:
    """
    Submit and validate an answer for a DoR question.
    
    Args:
        questions: List of DoR questions
        question_id: ID of question being answered
        answer: User's answer text
        
    Returns:
        (is_valid, feedback_messages)
        
    Example:
        >>> questions = initialize_dor_questions()
        >>> is_valid, feedback = submit_dor_answer(questions, "req_1", "Fix login timeout after 30 seconds of inactivity")
        >>> is_valid
        True
    """
    question = next((q for q in questions if q.id == question_id), None)
    if not question:
        return False, [f"Question {question_id} not found"]
    
    is_valid, feedback = validate_answer(question, answer)
    
    question.answer = answer
    question.is_valid = is_valid
    
    return is_valid, feedback


def validate_dor(questions: List[DoRQuestion]) -> DoRValidationResult:
    """
    Perform full DoR validation and scoring.
    
    CRITICAL: Returns can_estimate=True only if score >= 80%
    
    Args:
        questions: List of DoR questions with answers
        
    Returns:
        DoRValidationResult with score and recommendations
        
    Example:
        >>> questions = initialize_dor_questions()
        >>> result = validate_dor(questions)
        >>> result.can_estimate
        False
    """
    # Count answered and valid required questions
    total_questions = len([q for q in questions if q.required])
    answered_required = len([q for q in questions if q.required and q.answer])
    valid_required = len([q for q in questions if q.required and q.is_valid])
    
    if total_questions == 0:
        score = 0.0
    else:
        score = valid_required / total_questions
    
    # Find missing categories
    answered_categories = set(q.category for q in questions if q.answer)
    all_categories = set(q.category for q in questions if q.required)
    missing_categories = list(all_categories - answered_categories)
    
    # Find ambiguous answers
    ambiguous = [
        {"question_id": q.id, "question": q.question, "answer": q.answer}
        for q in questions
        if q.answer and not q.is_valid
    ]
    
    # Generate recommendations
    recommendations = []
    if missing_categories:
        recommendations.append(f"Complete questions in: {', '.join(missing_categories)}")
    if ambiguous:
        recommendations.append(f"Clarify {len(ambiguous)} ambiguous answer(s)")
    if score < DOR_THRESHOLD:
        recommendations.append(f"DoR score {score:.0%} is below threshold ({DOR_THRESHOLD:.0%})")
        recommendations.append("⛔ Estimation BLOCKED until DoR is complete")
    
    # Determine status
    if answered_required == 0:
        status = DoRStatus.NOT_STARTED
    elif score >= DOR_THRESHOLD:
        status = DoRStatus.COMPLETE
    elif answered_required > 0:
        status = DoRStatus.IN_PROGRESS
    else:
        status = DoRStatus.INCOMPLETE
    
    return DoRValidationResult(
        status=status,
        score=score,
        questions_answered=answered_required,
        questions_total=total_questions,
        missing_categories=missing_categories,
        ambiguous_answers=ambiguous,
        recommendations=recommendations,
        can_estimate=score >= DOR_THRESHOLD
    )


def generate_dor_progress_summary(questions: List[DoRQuestion]) -> str:
    """
    Generate Markdown summary of DoR progress.
    
    Args:
        questions: List of DoR questions with answers
        
    Returns:
        Markdown-formatted progress summary
        
    Example:
        >>> questions = initialize_dor_questions()
        >>> summary = generate_dor_progress_summary(questions)
        >>> "Definition of Ready" in summary
        True
    """
    result = validate_dor(questions)
    
    lines = [
        "## 📋 Definition of Ready (DoR) Progress",
        "",
        f"**Status:** {result.status.value.replace('_', ' ').title()}",
        f"**Score:** {result.score:.0%} (Threshold: {DOR_THRESHOLD:.0%})",
        f"**Questions:** {result.questions_answered}/{result.questions_total} required answered",
        "",
    ]
    
    # Progress bar
    filled = int(result.score * 10)
    empty = 10 - filled
    progress_bar = "█" * filled + "░" * empty
    lines.append(f"**Progress:** [{progress_bar}] {result.score:.0%}")
    lines.append("")
    
    # Estimation eligibility
    if result.can_estimate:
        lines.append("✅ **DoR Complete** - Estimation is now available")
    else:
        lines.append("⛔ **DoR Incomplete** - Estimation is BLOCKED")
        lines.append("")
        lines.append("**Required to proceed:**")
        for rec in result.recommendations:
            lines.append(f"  - {rec}")
    
    return "\n".join(lines)


def get_dor_answers_dict(questions: List[DoRQuestion]) -> Dict[str, str]:
    """
    Extract answers from questions as dictionary.
    
    Args:
        questions: List of DoR questions with answers
        
    Returns:
        Dictionary mapping question_id to answer
        
    Example:
        >>> questions = initialize_dor_questions()
        >>> answers = get_dor_answers_dict(questions)
        >>> isinstance(answers, dict)
        True
    """
    return {q.id: q.answer for q in questions if q.answer}


# ============================================================================
# OPERATION 9-20: Work Decomposition Operations
# ============================================================================

# Story point mapping based on complexity
COMPLEXITY_POINTS = {
    "trivial": StoryPointScale.XS.value,     # 1
    "simple": StoryPointScale.S.value,       # 2
    "moderate": StoryPointScale.M.value,     # 3
    "complex": StoryPointScale.L.value,      # 5
    "very_complex": StoryPointScale.XL.value, # 8
    "epic": StoryPointScale.XXL.value,       # 13
}

# Hours per story point (average)
HOURS_PER_POINT = 4

# Story points per sprint (team velocity assumption)
POINTS_PER_SPRINT = 40


def extract_requirements_from_dor(dor_answers: Dict[str, str]) -> Dict[str, Any]:
    """
    Extract structured requirements from DoR answers.
    
    Args:
        dor_answers: Dictionary of DoR question_id -> answer
        
    Returns:
        Structured requirements dictionary
        
    Example:
        >>> dor_answers = {"req_1": "Fix login timeout", "req_2": "Admins"}
        >>> reqs = extract_requirements_from_dor(dor_answers)
        >>> "problem_statement" in reqs
        True
    """
    return {
        "problem_statement": dor_answers.get("req_1", ""),
        "users": dor_answers.get("req_2", ""),
        "success_criteria": dor_answers.get("req_3", ""),
        "specifications": dor_answers.get("req_4", ""),
        "external_dependencies": dor_answers.get("dep_1", ""),
        "internal_dependencies": dor_answers.get("dep_2", ""),
        "technical_approach": dor_answers.get("tech_1", ""),
        "performance_requirements": dor_answers.get("tech_2", ""),
        "security_requirements": dor_answers.get("sec_1", ""),
        "sensitive_data": dor_answers.get("sec_2", ""),
        "security_risks": dor_answers.get("sec_3", ""),
        "test_scenarios": dor_answers.get("test_1", ""),
        "test_coverage": dor_answers.get("test_2", ""),
    }


def is_feature_relevant(feature_name: str, requirements: Dict[str, Any]) -> bool:
    """
    Determine if a feature is relevant based on requirements.
    
    Args:
        feature_name: Name of feature (Backend API, Database, etc.)
        requirements: Structured requirements from DoR
        
    Returns:
        True if feature should be included
        
    Example:
        >>> reqs = {"problem_statement": "Need database for user data"}
        >>> is_feature_relevant("Database", reqs)
        True
    """
    # Backend API is always relevant
    if feature_name == "Backend API":
        return True
    
    # Database is relevant if data persistence mentioned
    if feature_name == "Database":
        data_keywords = ["database", "store", "save", "persist", "data", "crud"]
        return any(kw in str(requirements).lower() for kw in data_keywords)
    
    # Frontend is relevant if UI mentioned
    if feature_name == "Frontend UI":
        ui_keywords = ["ui", "interface", "frontend", "page", "screen", "form", "button"]
        return any(kw in str(requirements).lower() for kw in ui_keywords)
    
    # Authentication is relevant if security mentioned
    if feature_name == "Authentication":
        sec_keywords = ["auth", "login", "permission", "role", "access", "security"]
        return any(kw in str(requirements).lower() for kw in sec_keywords)
    
    # Testing and documentation are always relevant
    if feature_name in ["Testing", "Documentation", "Business Logic"]:
        return True
    
    return False


def generate_feature_acceptance_criteria(feature_name: str) -> List[str]:
    """
    Generate acceptance criteria templates for a feature.
    
    Args:
        feature_name: Name of feature
        
    Returns:
        List of acceptance criteria strings
        
    Example:
        >>> ac = generate_feature_acceptance_criteria("Backend API")
        >>> len(ac) >= 3
        True
    """
    ac_templates = {
        "Backend API": [
            "API endpoints are implemented and documented",
            "API returns correct status codes (200, 400, 401, 404, 500)",
            "API handles errors gracefully with meaningful messages",
            "API meets performance requirements",
        ],
        "Database": [
            "Database schema is implemented and migrated",
            "Data integrity constraints are enforced",
            "Indexes are created for query optimization",
            "Backup and recovery procedures are documented",
        ],
        "Business Logic": [
            "Core business rules are implemented correctly",
            "Edge cases are handled appropriately",
            "Business logic is covered by unit tests",
            "Code follows SOLID principles",
        ],
        "Frontend UI": [
            "UI components are implemented per design specifications",
            "UI is responsive and accessible (WCAG 2.1 AA)",
            "Form validation provides clear error messages",
            "Loading states and error states are handled",
        ],
        "Authentication": [
            "Authentication mechanism is implemented and secure",
            "Authorization rules are enforced correctly",
            "Session management follows security best practices",
            "Security vulnerabilities are addressed (OWASP)",
        ],
        "Testing": [
            "Unit tests achieve >80% code coverage",
            "Integration tests cover critical paths",
            "E2E tests validate user workflows",
            "Performance tests meet SLA requirements",
        ],
        "Documentation": [
            "API documentation is complete and accurate",
            "User guide is updated with new features",
            "Architecture documentation is updated",
            "README and changelog are updated",
        ],
    }
    
    return ac_templates.get(feature_name, [
        "Feature is implemented as specified",
        "Feature is tested and verified",
        "Feature is documented",
    ])


def calculate_feature_priority(feature_name: str, risk: str) -> int:
    """
    Calculate ADO priority (1-4) for a feature.
    
    Args:
        feature_name: Name of feature
        risk: Risk level (low, medium, high)
        
    Returns:
        Priority number (1=Critical, 2=High, 3=Medium, 4=Low)
        
    Example:
        >>> calculate_feature_priority("Backend API", "high")
        1
    """
    priority_map = {
        "Backend API": 1,
        "Database": 1,
        "Business Logic": 1,
        "Authentication": 1,
        "Frontend UI": 2,
        "Testing": 2,
        "Documentation": 3,
    }
    return priority_map.get(feature_name, 2)


def estimate_story_points(complexity: str) -> int:
    """
    Estimate story points based on complexity.
    
    Args:
        complexity: Complexity level (trivial, simple, moderate, complex, very_complex, epic)
        
    Returns:
        Story points (1, 2, 3, 5, 8, or 13)
        
    Example:
        >>> estimate_story_points("moderate")
        3
    """
    return COMPLEXITY_POINTS.get(complexity, StoryPointScale.M.value)


def recommend_team_size(total_story_points: int, target_sprints: int) -> str:
    """
    Recommend team size based on story points and target timeline.
    
    Args:
        total_story_points: Total story points for project
        target_sprints: Desired number of sprints
        
    Returns:
        Team size recommendation string
        
    Example:
        >>> recommend_team_size(120, 3)
        'Team of 1 developer (40 points/sprint velocity)'
    """
    required_velocity = total_story_points / target_sprints if target_sprints > 0 else total_story_points
    team_size = math.ceil(required_velocity / POINTS_PER_SPRINT)
    
    if team_size <= 1:
        return f"Team of 1 developer ({POINTS_PER_SPRINT} points/sprint velocity)"
    elif team_size <= 3:
        return f"Small team of {team_size} developers ({team_size * POINTS_PER_SPRINT} points/sprint velocity)"
    elif team_size <= 5:
        return f"Medium team of {team_size} developers ({team_size * POINTS_PER_SPRINT} points/sprint velocity)"
    else:
        return f"Large team of {team_size}+ developers ({team_size * POINTS_PER_SPRINT}+ points/sprint velocity)"


def generate_ado_export_json(features: List[ADOFeature]) -> str:
    """
    Generate ADO-ready JSON export.
    
    Args:
        features: List of ADO features with stories
        
    Returns:
        JSON string ready for ADO import
        
    Example:
        >>> feature = ADOFeature(id="F1", title="Test", description="Test", business_value="", acceptance_criteria=[], priority=1, tags=[], stories=[], total_story_points=0, estimated_sprints=0, risk_level="Low")
        >>> json_str = generate_ado_export_json([feature])
        >>> "work_items" in json_str
        True
    """
    work_items = []
    
    for feature in features:
        feature_item = {
            "type": WorkItemType.FEATURE.value,
            "id": feature.id,
            "title": feature.title,
            "description": feature.description,
            "business_value": feature.business_value,
            "acceptance_criteria": feature.acceptance_criteria,
            "priority": feature.priority,
            "tags": feature.tags,
            "risk_level": feature.risk_level,
            "story_points": feature.total_story_points,
            "estimated_sprints": feature.estimated_sprints,
        }
        work_items.append(feature_item)
        
        for story in feature.stories:
            story_item = {
                "type": WorkItemType.USER_STORY.value,
                "id": story.id,
                "parent_id": story.parent_feature_id,
                "title": story.title,
                "description": story.description,
                "acceptance_criteria": story.acceptance_criteria,
                "story_points": story.story_points,
                "priority": story.priority,
                "tags": story.tags,
                "complexity": story.complexity,
                "estimated_hours": story.estimated_hours,
                "implementation_plan": story.implementation_plan,
                "technical_notes": story.technical_notes,
                "dependencies": story.dependencies,
            }
            work_items.append(story_item)
    
    return json.dumps({
        "work_items": work_items,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "generator": "CORTEX SWAGGER Estimation Utility v1.0",
            "total_features": len(features),
            "total_stories": sum(len(f.stories) for f in features),
        }
    }, indent=2)


def generate_markdown_summary(features: List[ADOFeature], work_description: str) -> str:
    """
    Generate Markdown summary of work decomposition.
    
    Args:
        features: List of ADO features with stories
        work_description: Original work description
        
    Returns:
        Markdown-formatted summary
        
    Example:
        >>> feature = ADOFeature(id="F1", title="Test", description="Test", business_value="", acceptance_criteria=[], priority=1, tags=[], stories=[], total_story_points=5, estimated_sprints=0.1, risk_level="Low")
        >>> summary = generate_markdown_summary([feature], "Test work")
        >>> "# Work Decomposition Summary" in summary
        True
    """
    total_stories = sum(len(f.stories) for f in features)
    total_points = sum(f.total_story_points for f in features)
    total_hours = total_points * HOURS_PER_POINT
    total_sprints = total_points / POINTS_PER_SPRINT
    
    lines = [
        "# Work Decomposition Summary",
        "",
        f"**Original Work:** {work_description}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 📊 Summary Metrics",
        "",
        f"- **Features:** {len(features)}",
        f"- **User Stories:** {total_stories}",
        f"- **Total Story Points:** {total_points}",
        f"- **Estimated Hours:** {total_hours:.1f}",
        f"- **Estimated Sprints:** {total_sprints:.1f}",
        f"- **Team Recommendation:** {recommend_team_size(total_points, math.ceil(total_sprints))}",
        "",
        "## 🎯 Features",
        "",
    ]
    
    for feature in features:
        lines.append(f"### {feature.title}")
        lines.append("")
        lines.append(f"**ID:** {feature.id}")
        lines.append(f"**Priority:** P{feature.priority}")
        lines.append(f"**Risk Level:** {feature.risk_level}")
        lines.append(f"**Story Points:** {feature.total_story_points}")
        lines.append(f"**Stories:** {len(feature.stories)}")
        lines.append("")
        lines.append("**Acceptance Criteria:**")
        for ac in feature.acceptance_criteria:
            lines.append(f"- {ac}")
        lines.append("")
        
        if feature.stories:
            lines.append("**User Stories:**")
            lines.append("")
            lines.append("| ID | Title | Points | Complexity |")
            lines.append("|---|---|---|---|")
            for story in feature.stories:
                lines.append(f"| {story.id} | {story.title} | {story.story_points} | {story.complexity} |")
            lines.append("")
    
    return "\n".join(lines)


def decompose_work(
    work_description: str,
    dor_answers: Dict[str, str],
    max_features: int = 7
) -> WorkDecompositionResult:
    """
    Decompose work into ADO Features and Stories.
    
    Args:
        work_description: High-level work description
        dor_answers: DoR answers dictionary
        max_features: Maximum number of features to generate
        
    Returns:
        WorkDecompositionResult with features, stories, and estimates
        
    Example:
        >>> dor_answers = {"req_1": "User authentication system with OAuth2", "req_2": "Web and mobile users"}
        >>> result = decompose_work("User auth", dor_answers)
        >>> len(result.features) > 0
        True
    """
    requirements = extract_requirements_from_dor(dor_answers)
    
    # Standard feature decomposition pattern
    standard_features = [
        ("Backend API", "API Development", "high"),
        ("Database", "Data Layer", "high"),
        ("Business Logic", "Core Logic", "high"),
        ("Frontend UI", "User Interface", "medium"),
        ("Authentication", "Security", "high"),
        ("Testing", "Quality Assurance", "medium"),
        ("Documentation", "Documentation", "low"),
    ]
    
    features = []
    feature_id = 1
    
    for name, category, risk in standard_features[:max_features]:
        if not is_feature_relevant(name, requirements):
            continue
        
        feature = ADOFeature(
            id=f"FEATURE-{feature_id:03d}",
            title=f"{name}: {work_description[:50]}",
            description=f"Implement {name.lower()} components for {work_description}",
            business_value=requirements.get("problem_statement", "")[:200],
            acceptance_criteria=generate_feature_acceptance_criteria(name),
            priority=calculate_feature_priority(name, risk),
            tags=[category, risk],
            stories=[],
            total_story_points=0,
            estimated_sprints=0,
            risk_level=risk.capitalize()
        )
        
        # Generate stories for feature (simplified - real implementation would be more sophisticated)
        story_count = 3 if name in ["Backend API", "Frontend UI"] else 2
        for i in range(story_count):
            story = ADOStory(
                id=f"{feature.id}-STORY-{i+1:03d}",
                title=f"{name} Story {i+1}: Implementation",
                description=f"Implement {name.lower()} components",
                acceptance_criteria=[f"{name} component {i+1} is functional"],
                story_points=estimate_story_points("moderate"),
                priority=feature.priority,
                tags=feature.tags,
                parent_feature_id=feature.id,
                implementation_plan=[f"Step 1: Design {name}", f"Step 2: Implement {name}", f"Step 3: Test {name}"],
                technical_notes=f"Technical notes for {name}",
                dependencies=[],
                estimated_hours=estimate_story_points("moderate") * HOURS_PER_POINT,
                complexity="moderate"
            )
            feature.stories.append(story)
        
        feature.total_story_points = sum(s.story_points for s in feature.stories)
        feature.estimated_sprints = feature.total_story_points / POINTS_PER_SPRINT
        
        features.append(feature)
        feature_id += 1
    
    total_stories = sum(len(f.stories) for f in features)
    total_points = sum(f.total_story_points for f in features)
    total_hours = total_points * HOURS_PER_POINT
    total_sprints = total_points / POINTS_PER_SPRINT
    
    return WorkDecompositionResult(
        original_description=work_description,
        features=features,
        total_stories=total_stories,
        total_story_points=total_points,
        estimated_sprints=total_sprints,
        estimated_hours=total_hours,
        team_size_recommendation=recommend_team_size(total_points, math.ceil(total_sprints)),
        ado_export_json=generate_ado_export_json(features),
        markdown_summary=generate_markdown_summary(features, work_description)
    )


# ============================================================================
# OPERATION 21-25: Estimation Session Operations
# ============================================================================

def check_dor_before_estimation(questions: List[DoRQuestion]) -> Dict[str, Any]:
    """
    Check if DoR is complete before allowing estimation.
    
    Args:
        questions: List of DoR questions
        
    Returns:
        Status dictionary with can_estimate flag
        
    Example:
        >>> questions = initialize_dor_questions()
        >>> status = check_dor_before_estimation(questions)
        >>> status["can_estimate"]
        False
    """
    validation_result = validate_dor(questions)
    
    if not validation_result.can_estimate:
        return {
            "status": "blocked",
            "can_estimate": False,
            "error": "⛔ ESTIMATION BLOCKED: Definition of Ready is not complete.",
            "dor_progress": generate_dor_progress_summary(questions),
            "recommendations": validation_result.recommendations,
            "message": "Complete the DoR checklist before requesting estimates.",
        }
    
    return {
        "status": "ready",
        "can_estimate": True,
        "dor_score": validation_result.score,
        "message": "✅ DoR Complete - Estimation available",
    }


def generate_estimation(
    work_description: str,
    questions: List[DoRQuestion]
) -> Dict[str, Any]:
    """
    Generate project estimation with DoR validation.
    
    CRITICAL: Returns error if DoR not complete.
    
    Args:
        work_description: High-level work description
        questions: List of DoR questions with answers
        
    Returns:
        Estimation result with decomposition and metrics
        
    Example:
        >>> questions = initialize_dor_questions()
        >>> result = generate_estimation("Test project", questions)
        >>> "status" in result
        True
    """
    # Check DoR first
    dor_check = check_dor_before_estimation(questions)
    if not dor_check["can_estimate"]:
        return dor_check
    
    # Extract answers and decompose work
    dor_answers = get_dor_answers_dict(questions)
    decomposition = decompose_work(work_description, dor_answers)
    
    return {
        "status": "success",
        "work_description": work_description,
        "dor_complete": True,
        "features": len(decomposition.features),
        "stories": decomposition.total_stories,
        "story_points": decomposition.total_story_points,
        "estimated_hours": decomposition.estimated_hours,
        "estimated_sprints": decomposition.estimated_sprints,
        "team_recommendation": decomposition.team_size_recommendation,
        "decomposition": decomposition,
        "ado_json": decomposition.ado_export_json,
        "markdown_summary": decomposition.markdown_summary,
    }


def get_enhanced_estimation(
    work_description: str,
    questions: List[DoRQuestion],
    complexity_score: float = 50.0,
    team_size: int = 1
) -> Dict[str, Any]:
    """
    Get enhanced estimation with TimeframeEstimator integration.
    
    Provides parallel track analysis, timelines, and what-if scenarios.
    
    Args:
        work_description: High-level work description
        questions: List of DoR questions with answers
        complexity_score: SWAGGER complexity score (0-100)
        team_size: Target team size
        
    Returns:
        Enhanced estimation with parallel tracks and scenarios
        
    Example:
        >>> questions = initialize_dor_questions()
        >>> result = get_enhanced_estimation("Test", questions)
        >>> "status" in result
        True
    """
    # Check DoR first
    dor_check = check_dor_before_estimation(questions)
    if not dor_check["can_estimate"]:
        return dor_check
    
    if not TIMEFRAME_ESTIMATOR_AVAILABLE:
        return {
            "status": "unavailable",
            "error": "TimeframeEstimator not available. Using basic estimation.",
            "fallback": generate_estimation(work_description, questions),
        }
    
    # Get basic estimation
    basic_result = generate_estimation(work_description, questions)
    
    # Add TimeframeEstimator data
    timeframe_estimator = TimeframeEstimator()
    time_estimate = timeframe_estimator.estimate_timeframe(complexity_score, team_size=team_size)
    
    basic_result["enhanced"] = {
        "story_points": time_estimate.story_points,
        "hours_single": time_estimate.hours_single,
        "hours_team": time_estimate.hours_team,
        "days_single": time_estimate.days_single,
        "days_team": time_estimate.days_team,
        "sprints": time_estimate.sprints,
        "confidence": time_estimate.confidence,
        "explanation": time_estimate.explanation,
    }
    
    return basic_result


# ============================================================================
# SELF-TESTS
# ============================================================================

if __name__ == "__main__":
    import tempfile
    import time
    
    print("🧪 Running SWAGGER Estimation Utility Self-Tests...\n")
    
    start_time = time.time()
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Initialize DoR questions
    tests_total += 1
    try:
        questions = initialize_dor_questions()
        assert len(questions) == 15
        assert all(isinstance(q, DoRQuestion) for q in questions)
        print("✅ Test 1: initialize_dor_questions - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 1: initialize_dor_questions - FAILED: {e}")
    
    # Test 2: Get next unanswered question
    tests_total += 1
    try:
        questions = initialize_dor_questions()
        next_q = get_next_unanswered_question(questions)
        assert next_q is not None
        assert next_q.id == "req_1"
        print("✅ Test 2: get_next_unanswered_question - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 2: get_next_unanswered_question - FAILED: {e}")
    
    # Test 3: Get questions by category
    tests_total += 1
    try:
        questions = initialize_dor_questions()
        req_questions = get_questions_by_category(questions, "requirements")
        assert len(req_questions) == 4
        print("✅ Test 3: get_questions_by_category - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 3: get_questions_by_category - FAILED: {e}")
    
    # Test 4: Validate answer (vague answer should fail)
    tests_total += 1
    try:
        q = DoRQuestion(id="test", category="requirements", question="Test?")
        is_valid, feedback = validate_answer(q, "This will improve things")
        assert is_valid == False
        assert any("vague" in f.lower() for f in feedback)
        print("✅ Test 4: validate_answer (vague detection) - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 4: validate_answer - FAILED: {e}")
    
    # Test 5: Submit DoR answer
    tests_total += 1
    try:
        questions = initialize_dor_questions()
        is_valid, feedback = submit_dor_answer(
            questions,
            "req_1",
            "Fix critical login timeout bug that occurs after 30 seconds of user inactivity on the dashboard"
        )
        assert is_valid == True
        print("✅ Test 5: submit_dor_answer - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 5: submit_dor_answer - FAILED: {e}")
    
    # Test 6: Validate DoR (incomplete should block estimation)
    tests_total += 1
    try:
        questions = initialize_dor_questions()
        result = validate_dor(questions)
        assert result.can_estimate == False
        assert result.score < DOR_THRESHOLD
        print("✅ Test 6: validate_dor (incomplete) - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 6: validate_dor - FAILED: {e}")
    
    # Test 7: Generate DoR progress summary
    tests_total += 1
    try:
        questions = initialize_dor_questions()
        summary = generate_dor_progress_summary(questions)
        assert "Definition of Ready" in summary
        assert "⛔" in summary  # Should show blocked
        print("✅ Test 7: generate_dor_progress_summary - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 7: generate_dor_progress_summary - FAILED: {e}")
    
    # Test 8: Extract requirements from DoR
    tests_total += 1
    try:
        dor_answers = {"req_1": "Test problem", "req_2": "Test users"}
        reqs = extract_requirements_from_dor(dor_answers)
        assert "problem_statement" in reqs
        assert reqs["problem_statement"] == "Test problem"
        print("✅ Test 8: extract_requirements_from_dor - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 8: extract_requirements_from_dor - FAILED: {e}")
    
    # Test 9: Is feature relevant
    tests_total += 1
    try:
        reqs = {"problem_statement": "Need database for storing user data"}
        assert is_feature_relevant("Database", reqs) == True
        assert is_feature_relevant("Backend API", reqs) == True  # Always relevant
        print("✅ Test 9: is_feature_relevant - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 9: is_feature_relevant - FAILED: {e}")
    
    # Test 10: Generate feature acceptance criteria
    tests_total += 1
    try:
        ac = generate_feature_acceptance_criteria("Backend API")
        assert len(ac) >= 3
        assert any("endpoint" in criterion.lower() for criterion in ac)
        print("✅ Test 10: generate_feature_acceptance_criteria - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 10: generate_feature_acceptance_criteria - FAILED: {e}")
    
    # Test 11: Estimate story points
    tests_total += 1
    try:
        points = estimate_story_points("moderate")
        assert points == 3
        points_complex = estimate_story_points("complex")
        assert points_complex == 5
        print("✅ Test 11: estimate_story_points - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 11: estimate_story_points - FAILED: {e}")
    
    # Test 12: Recommend team size
    tests_total += 1
    try:
        recommendation = recommend_team_size(120, 3)
        assert "Team of" in recommendation
        assert "developer" in recommendation
        print("✅ Test 12: recommend_team_size - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 12: recommend_team_size - FAILED: {e}")
    
    # Test 13: Generate ADO export JSON
    tests_total += 1
    try:
        feature = ADOFeature(
            id="F1",
            title="Test Feature",
            description="Test",
            business_value="Value",
            acceptance_criteria=["AC1"],
            priority=1,
            tags=["test"],
            stories=[],
            total_story_points=5,
            estimated_sprints=0.1,
            risk_level="Low"
        )
        json_str = generate_ado_export_json([feature])
        assert "work_items" in json_str
        json_data = json.loads(json_str)
        assert len(json_data["work_items"]) == 1
        print("✅ Test 13: generate_ado_export_json - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 13: generate_ado_export_json - FAILED: {e}")
    
    # Test 14: Decompose work
    tests_total += 1
    try:
        dor_answers = {
            "req_1": "Build user authentication system with OAuth2 integration for secure login",
            "req_2": "Web and mobile application users requiring secure access"
        }
        result = decompose_work("User Authentication System", dor_answers)
        assert len(result.features) > 0
        assert result.total_stories > 0
        assert result.total_story_points > 0
        print("✅ Test 14: decompose_work - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 14: decompose_work - FAILED: {e}")
    
    # Test 15: Check DoR before estimation (should block)
    tests_total += 1
    try:
        questions = initialize_dor_questions()
        status = check_dor_before_estimation(questions)
        assert status["can_estimate"] == False
        assert "blocked" in status["status"]
        print("✅ Test 15: check_dor_before_estimation (blocked) - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 15: check_dor_before_estimation - FAILED: {e}")
    
    execution_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"📊 Test Results: {tests_passed}/{tests_total} passed ({tests_passed/tests_total*100:.1f}%)")
    print(f"⏱️  Execution time: {execution_time:.3f}s")
    
    if tests_passed == tests_total:
        print("✅ All tests passed!")
    else:
        print(f"❌ {tests_total - tests_passed} test(s) failed")

"""
SWAGGER Entry Point Module Orchestrator

Enforces Definition of Ready (DoR) through interactive questioning before providing
estimates. Decomposes large work items into Features and Stories with ADO-ready output.
Uses TimeframeEstimator for enhanced time estimates with parallel track analysis.

Author: Asif Hussain
Version: 1.1.0
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

CRITICAL: CORTEX should NEVER provide estimates if DoR is not complete.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
import hashlib
import math

# Import TimeframeEstimator for enhanced estimation (NEW - SWAGGER Integration)
try:
    from src.agents.estimation.timeframe_estimator import TimeframeEstimator, TimeEstimate
    TIMEFRAME_ESTIMATOR_AVAILABLE = True
except ImportError:
    TIMEFRAME_ESTIMATOR_AVAILABLE = False
    TimeframeEstimator = None
    TimeEstimate = None


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


class DoRValidator:
    """
    Validates Definition of Ready through interactive questioning.
    
    CRITICAL: Estimation is BLOCKED until DoR score >= 0.8 (80%)
    """
    
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
    
    def __init__(self):
        """Initialize DoR validator with question templates."""
        self.questions: List[DoRQuestion] = []
        self.answers: Dict[str, str] = {}
        self.current_question_index: int = 0
        self.validation_result: Optional[DoRValidationResult] = None
        self._initialize_questions()
    
    def _initialize_questions(self):
        """Load all question templates."""
        for category, questions in self.QUESTION_TEMPLATES.items():
            for q in questions:
                self.questions.append(DoRQuestion(
                    id=q.id,
                    category=q.category,
                    question=q.question,
                    required=q.required,
                    validation_hints=q.validation_hints.copy(),
                    follow_up_questions=q.follow_up_questions.copy()
                ))
    
    def get_next_question(self) -> Optional[DoRQuestion]:
        """Get the next unanswered question."""
        for q in self.questions:
            if q.answer is None:
                return q
        return None
    
    def get_questions_by_category(self, category: str) -> List[DoRQuestion]:
        """Get all questions for a specific category."""
        return [q for q in self.questions if q.category == category]
    
    def submit_answer(self, question_id: str, answer: str) -> Tuple[bool, List[str]]:
        """
        Submit an answer for a question.
        
        Returns:
            (is_valid, feedback_messages)
        """
        question = next((q for q in self.questions if q.id == question_id), None)
        if not question:
            return False, [f"Question {question_id} not found"]
        
        # Validate answer
        is_valid, feedback = self._validate_answer(question, answer)
        
        question.answer = answer
        question.is_valid = is_valid
        self.answers[question_id] = answer
        
        return is_valid, feedback
    
    def _validate_answer(self, question: DoRQuestion, answer: str) -> Tuple[bool, List[str]]:
        """Validate an answer for ambiguity and completeness."""
        feedback = []
        
        # Check for empty/minimal answers
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
        
        # Check for measurability in requirements
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
    
    def validate_dor(self) -> DoRValidationResult:
        """
        Perform full DoR validation.
        
        Returns DoRValidationResult with score and recommendations.
        """
        # Count answered and valid
        total_questions = len([q for q in self.questions if q.required])
        answered_required = len([q for q in self.questions if q.required and q.answer])
        valid_required = len([q for q in self.questions if q.required and q.is_valid])
        
        # Calculate score
        if total_questions == 0:
            score = 0.0
        else:
            score = valid_required / total_questions
        
        # Find missing categories
        answered_categories = set(q.category for q in self.questions if q.answer)
        all_categories = set(q.category for q in self.questions if q.required)
        missing_categories = list(all_categories - answered_categories)
        
        # Find ambiguous answers
        ambiguous = [
            {"question_id": q.id, "question": q.question, "answer": q.answer}
            for q in self.questions
            if q.answer and not q.is_valid
        ]
        
        # Generate recommendations
        recommendations = []
        if missing_categories:
            recommendations.append(f"Complete questions in: {', '.join(missing_categories)}")
        if ambiguous:
            recommendations.append(f"Clarify {len(ambiguous)} ambiguous answer(s)")
        if score < self.DOR_THRESHOLD:
            recommendations.append(f"DoR score {score:.0%} is below threshold ({self.DOR_THRESHOLD:.0%})")
            recommendations.append("⛔ Estimation BLOCKED until DoR is complete")
        
        # Determine status
        if not self.answers:
            status = DoRStatus.NOT_STARTED
        elif score >= self.DOR_THRESHOLD:
            status = DoRStatus.COMPLETE
        elif answered_required > 0:
            status = DoRStatus.IN_PROGRESS
        else:
            status = DoRStatus.INCOMPLETE
        
        self.validation_result = DoRValidationResult(
            status=status,
            score=score,
            questions_answered=answered_required,
            questions_total=total_questions,
            missing_categories=missing_categories,
            ambiguous_answers=ambiguous,
            recommendations=recommendations,
            can_estimate=score >= self.DOR_THRESHOLD
        )
        
        return self.validation_result
    
    def get_progress_summary(self) -> str:
        """Get a markdown summary of DoR progress."""
        result = self.validate_dor()
        
        lines = [
            "## 📋 Definition of Ready (DoR) Progress",
            "",
            f"**Status:** {result.status.value.replace('_', ' ').title()}",
            f"**Score:** {result.score:.0%} (Threshold: {self.DOR_THRESHOLD:.0%})",
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


class WorkDecomposer:
    """
    Decomposes large work items into Features and Stories.
    
    Generates ADO-ready output with titles, points, descriptions, and plans.
    """
    
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
    
    def __init__(self, dor_answers: Dict[str, str]):
        """
        Initialize with DoR answers for context.
        
        Args:
            dor_answers: Dictionary of DoR question_id -> answer
        """
        self.dor_answers = dor_answers
        self.features: List[ADOFeature] = []
    
    def decompose(
        self,
        work_description: str,
        work_type: str = "feature"
    ) -> WorkDecompositionResult:
        """
        Decompose work into Features and Stories.
        
        Args:
            work_description: High-level description of the work
            work_type: Type of work (epic, feature, enhancement)
            
        Returns:
            WorkDecompositionResult with ADO-ready output
        """
        # Parse DoR answers into structured requirements
        requirements = self._extract_requirements()
        
        # Identify major components/features
        features = self._identify_features(work_description, requirements)
        
        # Break each feature into stories
        for feature in features:
            stories = self._generate_stories(feature, requirements)
            feature.stories = stories
            feature.total_story_points = sum(s.story_points for s in stories)
            feature.estimated_sprints = feature.total_story_points / self.POINTS_PER_SPRINT
        
        self.features = features
        
        # Calculate totals
        total_stories = sum(len(f.stories) for f in features)
        total_points = sum(f.total_story_points for f in features)
        total_hours = total_points * self.HOURS_PER_POINT
        estimated_sprints = total_points / self.POINTS_PER_SPRINT
        
        # Generate exports
        ado_json = self._generate_ado_json(features)
        markdown = self._generate_markdown_summary(features)
        
        # Team recommendation
        team_rec = self._recommend_team_size(total_points, estimated_sprints)
        
        return WorkDecompositionResult(
            original_description=work_description,
            features=features,
            total_stories=total_stories,
            total_story_points=total_points,
            estimated_sprints=estimated_sprints,
            estimated_hours=total_hours,
            team_size_recommendation=team_rec,
            ado_export_json=ado_json,
            markdown_summary=markdown
        )
    
    def _extract_requirements(self) -> Dict[str, Any]:
        """Extract structured requirements from DoR answers."""
        requirements = {
            "problem_statement": self.dor_answers.get("req_1", ""),
            "users": self.dor_answers.get("req_2", ""),
            "success_criteria": self.dor_answers.get("req_3", ""),
            "specifications": self.dor_answers.get("req_4", ""),
            "external_dependencies": self.dor_answers.get("dep_1", ""),
            "internal_dependencies": self.dor_answers.get("dep_2", ""),
            "technical_approach": self.dor_answers.get("tech_1", ""),
            "performance_requirements": self.dor_answers.get("tech_2", ""),
            "security_requirements": self.dor_answers.get("sec_1", ""),
            "sensitive_data": self.dor_answers.get("sec_2", ""),
            "security_risks": self.dor_answers.get("sec_3", ""),
            "test_scenarios": self.dor_answers.get("test_1", ""),
            "test_coverage": self.dor_answers.get("test_2", ""),
        }
        return requirements
    
    def _identify_features(
        self,
        work_description: str,
        requirements: Dict[str, Any]
    ) -> List[ADOFeature]:
        """
        Identify major features from work description.
        
        This uses a rule-based approach to decompose work.
        In production, could be enhanced with LLM.
        """
        features = []
        
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
        
        # Create feature for each relevant component
        feature_id = 1
        for name, category, risk in standard_features:
            # Check if this component is relevant based on requirements
            is_relevant = self._is_feature_relevant(name, requirements)
            
            if is_relevant:
                feature = ADOFeature(
                    id=f"FEATURE-{feature_id:03d}",
                    title=f"{name}: {work_description[:50]}",
                    description=f"Implement {name.lower()} components for {work_description}",
                    business_value=requirements.get("problem_statement", "")[:200],
                    acceptance_criteria=self._generate_feature_ac(name, requirements),
                    priority=self._calculate_priority(name, risk),
                    tags=[category, risk],
                    stories=[],  # Will be populated later
                    total_story_points=0,
                    estimated_sprints=0,
                    risk_level=risk.capitalize()
                )
                features.append(feature)
                feature_id += 1
        
        return features
    
    def _is_feature_relevant(self, feature_name: str, requirements: Dict[str, Any]) -> bool:
        """Determine if a feature is relevant based on requirements."""
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
    
    def _generate_feature_ac(
        self,
        feature_name: str,
        requirements: Dict[str, Any]
    ) -> List[str]:
        """Generate acceptance criteria for a feature."""
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
    
    def _calculate_priority(self, feature_name: str, risk: str) -> int:
        """Calculate ADO priority (1-4) based on feature type and risk."""
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
    
    def _generate_stories(
        self,
        feature: ADOFeature,
        requirements: Dict[str, Any]
    ) -> List[ADOStory]:
        """Generate user stories for a feature."""
        stories = []
        story_id = 1
        
        # Story templates per feature type
        story_templates = self._get_story_templates(feature.title)
        
        for template in story_templates:
            story = ADOStory(
                id=f"{feature.id}-STORY-{story_id:03d}",
                title=template["title"],
                description=self._format_story_description(template, requirements),
                acceptance_criteria=template["ac"],
                story_points=self._estimate_story_points(template["complexity"]),
                priority=feature.priority,
                tags=feature.tags + template.get("tags", []),
                parent_feature_id=feature.id,
                implementation_plan=template["plan"],
                technical_notes=template.get("notes", ""),
                dependencies=template.get("dependencies", []),
                estimated_hours=self._estimate_story_points(template["complexity"]) * self.HOURS_PER_POINT,
                complexity=template["complexity"]
            )
            stories.append(story)
            story_id += 1
        
        return stories
    
    def _get_story_templates(self, feature_title: str) -> List[Dict[str, Any]]:
        """Get story templates based on feature type."""
        if "Backend API" in feature_title:
            return [
                {
                    "title": "Create API endpoint structure",
                    "complexity": "moderate",
                    "ac": [
                        "API routes are defined",
                        "Controller structure is created",
                        "Request/response models are defined",
                    ],
                    "plan": [
                        "Define API routes in routing config",
                        "Create controller classes",
                        "Define DTOs for request/response",
                        "Add OpenAPI documentation",
                    ],
                    "tags": ["api", "setup"],
                },
                {
                    "title": "Implement GET endpoints",
                    "complexity": "moderate",
                    "ac": [
                        "GET endpoints return correct data",
                        "Pagination is implemented",
                        "Filtering and sorting work correctly",
                    ],
                    "plan": [
                        "Implement list endpoint with pagination",
                        "Implement detail endpoint",
                        "Add filtering logic",
                        "Add sorting support",
                        "Write unit tests",
                    ],
                    "tags": ["api", "read"],
                },
                {
                    "title": "Implement POST/PUT endpoints",
                    "complexity": "complex",
                    "ac": [
                        "POST creates new records correctly",
                        "PUT updates existing records",
                        "Validation errors return 400 with details",
                    ],
                    "plan": [
                        "Implement create endpoint",
                        "Implement update endpoint",
                        "Add input validation",
                        "Add business rule validation",
                        "Write unit tests",
                    ],
                    "tags": ["api", "write"],
                },
                {
                    "title": "Implement DELETE endpoints",
                    "complexity": "simple",
                    "ac": [
                        "DELETE removes records correctly",
                        "Soft delete is implemented if required",
                        "Cascade rules are enforced",
                    ],
                    "plan": [
                        "Implement delete endpoint",
                        "Add authorization check",
                        "Handle cascade/orphan records",
                        "Write unit tests",
                    ],
                    "tags": ["api", "delete"],
                },
            ]
        
        elif "Database" in feature_title:
            return [
                {
                    "title": "Design database schema",
                    "complexity": "complex",
                    "ac": [
                        "Schema design is reviewed and approved",
                        "Entity relationships are documented",
                        "Data types are appropriate",
                    ],
                    "plan": [
                        "Design entity-relationship diagram",
                        "Define table structures",
                        "Define foreign key relationships",
                        "Review with team",
                    ],
                    "tags": ["database", "design"],
                },
                {
                    "title": "Create database migrations",
                    "complexity": "moderate",
                    "ac": [
                        "Migrations are created and tested",
                        "Rollback scripts work correctly",
                        "Data integrity is maintained",
                    ],
                    "plan": [
                        "Create migration scripts",
                        "Test migration on dev environment",
                        "Create rollback scripts",
                        "Document migration steps",
                    ],
                    "tags": ["database", "migration"],
                },
                {
                    "title": "Implement repository layer",
                    "complexity": "moderate",
                    "ac": [
                        "Repository classes are implemented",
                        "CRUD operations work correctly",
                        "Queries are optimized",
                    ],
                    "plan": [
                        "Create repository interfaces",
                        "Implement repository classes",
                        "Add query methods",
                        "Write unit tests",
                    ],
                    "tags": ["database", "repository"],
                },
            ]
        
        elif "Business Logic" in feature_title:
            return [
                {
                    "title": "Implement core business rules",
                    "complexity": "complex",
                    "ac": [
                        "Business rules are implemented correctly",
                        "Validation logic is complete",
                        "Edge cases are handled",
                    ],
                    "plan": [
                        "Define business rule classes",
                        "Implement validation logic",
                        "Handle edge cases",
                        "Write comprehensive tests",
                    ],
                    "tags": ["business-logic", "core"],
                },
                {
                    "title": "Implement service layer",
                    "complexity": "complex",
                    "ac": [
                        "Service classes orchestrate operations",
                        "Transaction handling is correct",
                        "Error handling is comprehensive",
                    ],
                    "plan": [
                        "Create service interfaces",
                        "Implement service classes",
                        "Add transaction management",
                        "Implement error handling",
                        "Write integration tests",
                    ],
                    "tags": ["business-logic", "service"],
                },
            ]
        
        elif "Frontend UI" in feature_title:
            return [
                {
                    "title": "Create UI component structure",
                    "complexity": "moderate",
                    "ac": [
                        "Component hierarchy is established",
                        "Routing is configured",
                        "State management is set up",
                    ],
                    "plan": [
                        "Define component structure",
                        "Set up routing",
                        "Configure state management",
                        "Create base components",
                    ],
                    "tags": ["ui", "setup"],
                },
                {
                    "title": "Implement form components",
                    "complexity": "complex",
                    "ac": [
                        "Forms capture all required data",
                        "Validation provides clear feedback",
                        "Forms are accessible",
                    ],
                    "plan": [
                        "Create form components",
                        "Implement validation",
                        "Add error handling",
                        "Test accessibility",
                    ],
                    "tags": ["ui", "forms"],
                },
                {
                    "title": "Implement list/table components",
                    "complexity": "complex",
                    "ac": [
                        "Data displays correctly in table format",
                        "Pagination works",
                        "Sorting and filtering work",
                    ],
                    "plan": [
                        "Create table component",
                        "Implement pagination",
                        "Add sorting functionality",
                        "Add filter functionality",
                    ],
                    "tags": ["ui", "display"],
                },
            ]
        
        elif "Authentication" in feature_title:
            return [
                {
                    "title": "Implement authentication flow",
                    "complexity": "very_complex",
                    "ac": [
                        "Users can log in securely",
                        "Session management is secure",
                        "Password policies are enforced",
                    ],
                    "plan": [
                        "Implement login endpoint",
                        "Configure JWT/session management",
                        "Add password validation",
                        "Implement logout",
                        "Security testing",
                    ],
                    "tags": ["security", "auth"],
                },
                {
                    "title": "Implement authorization rules",
                    "complexity": "complex",
                    "ac": [
                        "Role-based access control works",
                        "Permission checks are enforced",
                        "Unauthorized access is blocked",
                    ],
                    "plan": [
                        "Define roles and permissions",
                        "Implement authorization middleware",
                        "Add permission checks to endpoints",
                        "Write authorization tests",
                    ],
                    "tags": ["security", "authz"],
                },
            ]
        
        elif "Testing" in feature_title:
            return [
                {
                    "title": "Write unit tests",
                    "complexity": "complex",
                    "ac": [
                        "Unit test coverage >80%",
                        "Critical paths are tested",
                        "Edge cases are covered",
                    ],
                    "plan": [
                        "Identify test scenarios",
                        "Write unit tests for services",
                        "Write unit tests for validators",
                        "Verify coverage threshold",
                    ],
                    "tags": ["testing", "unit"],
                },
                {
                    "title": "Write integration tests",
                    "complexity": "complex",
                    "ac": [
                        "API integration tests pass",
                        "Database integration tested",
                        "External service mocks work",
                    ],
                    "plan": [
                        "Set up test database",
                        "Write API tests",
                        "Mock external services",
                        "Run integration suite",
                    ],
                    "tags": ["testing", "integration"],
                },
            ]
        
        elif "Documentation" in feature_title:
            return [
                {
                    "title": "Create API documentation",
                    "complexity": "moderate",
                    "ac": [
                        "All endpoints documented",
                        "Request/response examples provided",
                        "Error codes documented",
                    ],
                    "plan": [
                        "Document all endpoints",
                        "Add request examples",
                        "Add response examples",
                        "Document error codes",
                    ],
                    "tags": ["docs", "api"],
                },
                {
                    "title": "Create user documentation",
                    "complexity": "simple",
                    "ac": [
                        "User guide is complete",
                        "Screenshots are included",
                        "FAQ section added",
                    ],
                    "plan": [
                        "Write user guide",
                        "Add screenshots",
                        "Create FAQ",
                        "Review with stakeholders",
                    ],
                    "tags": ["docs", "user"],
                },
            ]
        
        # Default template
        return [
            {
                "title": f"Implement {feature_title}",
                "complexity": "complex",
                "ac": [
                    "Feature is implemented as specified",
                    "Feature is tested",
                    "Feature is documented",
                ],
                "plan": [
                    "Analyze requirements",
                    "Design solution",
                    "Implement solution",
                    "Test and verify",
                ],
                "tags": ["general"],
            }
        ]
    
    def _format_story_description(
        self,
        template: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> str:
        """Format story description with context."""
        desc_lines = [
            f"**Title:** {template['title']}",
            "",
            "**Context:**",
            f"- Problem: {requirements.get('problem_statement', 'See feature description')[:200]}",
            f"- Users: {requirements.get('users', 'See feature description')[:100]}",
            "",
            "**Technical Approach:**",
            f"- {requirements.get('technical_approach', 'Standard implementation')[:200]}",
        ]
        
        if template.get("notes"):
            desc_lines.extend(["", "**Notes:**", template["notes"]])
        
        return "\n".join(desc_lines)
    
    def _estimate_story_points(self, complexity: str) -> int:
        """Estimate story points based on complexity."""
        return self.COMPLEXITY_POINTS.get(complexity, StoryPointScale.M.value)
    
    def _recommend_team_size(
        self,
        total_points: int,
        estimated_sprints: float
    ) -> str:
        """Recommend team size based on work scope."""
        if total_points <= 20:
            return "1 developer (can complete in 1 sprint)"
        elif total_points <= 50:
            return "1-2 developers (1-2 sprints)"
        elif total_points <= 100:
            return "2-3 developers (2-3 sprints)"
        elif total_points <= 200:
            return "3-5 developers (3-5 sprints)"
        else:
            sprints = math.ceil(estimated_sprints)
            return f"5+ developers ({sprints}+ sprints) - Consider phased delivery"
    
    def _generate_ado_json(self, features: List[ADOFeature]) -> str:
        """Generate ADO-compatible JSON for import."""
        ado_items = []
        
        for feature in features:
            # Feature work item
            ado_items.append({
                "op": "add",
                "path": "/fields/System.Title",
                "value": feature.title,
                "workItemType": "Feature",
                "fields": {
                    "System.Title": feature.title,
                    "System.Description": feature.description,
                    "Microsoft.VSTS.Common.Priority": feature.priority,
                    "Microsoft.VSTS.Common.BusinessValue": feature.business_value[:500],
                    "System.Tags": "; ".join(feature.tags),
                    "Custom.AcceptanceCriteria": "\n".join(f"- {ac}" for ac in feature.acceptance_criteria),
                }
            })
            
            # Story work items
            for story in feature.stories:
                ado_items.append({
                    "op": "add",
                    "path": "/fields/System.Title",
                    "value": story.title,
                    "workItemType": "User Story",
                    "parentId": feature.id,
                    "fields": {
                        "System.Title": story.title,
                        "System.Description": story.description,
                        "Microsoft.VSTS.Common.Priority": story.priority,
                        "Microsoft.VSTS.Scheduling.StoryPoints": story.story_points,
                        "System.Tags": "; ".join(story.tags),
                        "Custom.AcceptanceCriteria": "\n".join(f"- {ac}" for ac in story.acceptance_criteria),
                        "Custom.ImplementationPlan": "\n".join(f"{i+1}. {step}" for i, step in enumerate(story.implementation_plan)),
                        "Custom.TechnicalNotes": story.technical_notes,
                    }
                })
        
        return json.dumps(ado_items, indent=2)
    
    def _generate_markdown_summary(self, features: List[ADOFeature]) -> str:
        """Generate markdown summary of decomposition."""
        lines = [
            "# Work Decomposition Summary",
            "",
            "## Overview",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Features | {len(features)} |",
            f"| Total Stories | {sum(len(f.stories) for f in features)} |",
            f"| Total Story Points | {sum(f.total_story_points for f in features)} |",
            f"| Estimated Hours | {sum(f.total_story_points for f in features) * self.HOURS_PER_POINT} |",
            f"| Estimated Sprints | {sum(f.total_story_points for f in features) / self.POINTS_PER_SPRINT:.1f} |",
            "",
        ]
        
        for feature in features:
            lines.extend([
                f"## {feature.id}: {feature.title}",
                "",
                f"**Description:** {feature.description}",
                f"**Risk Level:** {feature.risk_level}",
                f"**Total Points:** {feature.total_story_points}",
                "",
                "### Stories",
                "",
                "| ID | Title | Points | Complexity |",
                "|----|-------|--------|------------|",
            ])
            
            for story in feature.stories:
                lines.append(f"| {story.id} | {story.title} | {story.story_points} | {story.complexity} |")
            
            lines.append("")
        
        return "\n".join(lines)


class SWAGGEREntryPointOrchestrator:
    """
    SWAGGER Entry Point Module Orchestrator.
    
    Enforces Definition of Ready (DoR) through interactive questioning before
    providing any estimates. Decomposes large work into ADO-ready Features/Stories.
    
    CRITICAL: CORTEX should NEVER provide estimates if DoR is not complete.
    """
    
    def __init__(
        self,
        project_root: Optional[Path] = None,
        interactive_callback: Optional[Callable[[str], str]] = None
    ):
        """
        Initialize orchestrator.
        
        Args:
            project_root: Path to project root
            interactive_callback: Function to get user input (for interactive mode)
        """
        self.project_root = project_root or Path.cwd()
        self.interactive_callback = interactive_callback
        self.dor_validator = DoRValidator()
        self.decomposer: Optional[WorkDecomposer] = None
        self.estimation_blocked = True  # Start with estimation blocked
        
        # Initialize TimeframeEstimator for enhanced estimation (NEW - SWAGGER Integration)
        self.timeframe_estimator: Optional[TimeframeEstimator] = None
        if TIMEFRAME_ESTIMATOR_AVAILABLE:
            self.timeframe_estimator = TimeframeEstimator()
        
    def get_enhanced_estimate(
        self,
        complexity_score: float,
        team_size: int = 1,
        include_timeline: bool = True,
        include_what_if: bool = True
    ) -> Dict[str, Any]:
        """
        Get enhanced estimate using TimeframeEstimator.
        
        Provides parallel track analysis, visual timelines, and what-if scenarios.
        REQUIRES DoR to be complete.
        
        Args:
            complexity_score: SWAGGER complexity score (0-100)
            team_size: Target team size for estimation
            include_timeline: Include visual timeline comparison
            include_what_if: Include what-if scenarios for different team sizes
            
        Returns:
            Enhanced estimation with parallel tracks, timelines, and scenarios
        """
        # CRITICAL CHECK: Never estimate without DoR
        validation_result = self.dor_validator.validate_dor()
        
        if not validation_result.can_estimate:
            return {
                "status": "blocked",
                "error": "⛔ ESTIMATION BLOCKED: Definition of Ready is not complete.",
                "dor_progress": self.dor_validator.get_progress_summary(),
                "recommendations": validation_result.recommendations,
                "message": "Complete the DoR checklist before requesting estimates.",
            }
        
        if not self.timeframe_estimator:
            return {
                "status": "unavailable",
                "error": "TimeframeEstimator not available. Using basic estimation.",
                "fallback": "Use generate_estimate() for basic estimation.",
            }
        
        result = {
            "status": "success",
            "dor_status": "complete",
            "complexity_score": complexity_score,
        }
        
        # Get core estimate
        time_estimate = self.timeframe_estimator.estimate_timeframe(
            complexity_score,
            team_size=team_size
        )
        
        result["estimate"] = {
            "story_points": time_estimate.story_points,
            "hours_single": time_estimate.hours_single,
            "hours_team": time_estimate.hours_team,
            "days_single": time_estimate.days_single,
            "days_team": time_estimate.days_team,
            "sprints": time_estimate.sprints,
            "team_size": time_estimate.team_size,
            "confidence": time_estimate.confidence,
            "explanation": time_estimate.explanation,
            "assumptions": time_estimate.assumptions,
            "breakdown": time_estimate.breakdown,
            "complexity_factors": time_estimate.complexity_factors,
        }
        
        # Add parallel tracks analysis
        if time_estimate.parallel_tracks:
            result["parallel_tracks"] = [
                {
                    "track_id": track.track_id,
                    "name": track.name,
                    "hours": track.hours,
                    "start_sprint": track.start_sprint,
                    "end_sprint": track.end_sprint,
                    "dependencies": track.dependencies,
                }
                for track in time_estimate.parallel_tracks
            ]
            result["max_parallel_tracks"] = time_estimate.max_parallel_tracks
            result["critical_path_hours"] = time_estimate.critical_path_hours
        
        # Add timeline comparison
        if include_timeline:
            try:
                timeline_ascii = self.timeframe_estimator.generate_timeline_comparison(
                    complexity_score
                )
                result["timeline_ascii"] = timeline_ascii
            except Exception as e:
                result["timeline_error"] = str(e)
        
        # Add what-if scenarios
        if include_what_if:
            try:
                what_if = self.timeframe_estimator.generate_what_if_scenarios(
                    complexity_score,
                    max_team=5
                )
                result["what_if_scenarios"] = what_if
            except Exception as e:
                result["what_if_error"] = str(e)
        
        return result
    
    def start_estimation_session(self, work_description: str) -> Dict[str, Any]:
        """
        Start an estimation session with DoR validation.
        
        Returns initial state with first DoR questions.
        """
        return {
            "status": "dor_validation_started",
            "estimation_blocked": True,
            "message": "⛔ Estimation is BLOCKED until Definition of Ready is complete.",
            "dor_progress": self.dor_validator.get_progress_summary(),
            "next_question": self._format_question(self.dor_validator.get_next_question()),
            "work_description": work_description,
        }
    
    def submit_dor_answer(
        self,
        question_id: str,
        answer: str
    ) -> Dict[str, Any]:
        """
        Submit an answer for a DoR question.
        
        Returns updated state with validation feedback.
        """
        is_valid, feedback = self.dor_validator.submit_answer(question_id, answer)
        validation_result = self.dor_validator.validate_dor()
        
        response = {
            "question_id": question_id,
            "answer_valid": is_valid,
            "feedback": feedback,
            "dor_progress": self.dor_validator.get_progress_summary(),
            "dor_status": validation_result.status.value,
            "dor_score": f"{validation_result.score:.0%}",
            "can_estimate": validation_result.can_estimate,
        }
        
        # Check if DoR is now complete
        if validation_result.can_estimate:
            self.estimation_blocked = False
            response["message"] = "✅ DoR Complete! Estimation is now available."
            response["next_action"] = "estimate"
        else:
            # Get next question
            next_q = self.dor_validator.get_next_question()
            if next_q:
                response["next_question"] = self._format_question(next_q)
            else:
                # All questions answered but DoR not met (ambiguous answers)
                response["message"] = "⚠️ Please clarify ambiguous answers to complete DoR."
                response["ambiguous_answers"] = validation_result.ambiguous_answers
        
        return response
    
    def generate_estimate(self, work_description: str) -> Dict[str, Any]:
        """
        Generate estimate after DoR is complete.
        
        CRITICAL: Raises error if DoR is not complete.
        """
        # CRITICAL CHECK: Never estimate without DoR
        validation_result = self.dor_validator.validate_dor()
        
        if not validation_result.can_estimate:
            return {
                "status": "blocked",
                "error": "⛔ ESTIMATION BLOCKED: Definition of Ready is not complete.",
                "dor_progress": self.dor_validator.get_progress_summary(),
                "recommendations": validation_result.recommendations,
                "message": "Complete the DoR checklist before requesting estimates.",
            }
        
        # DoR is complete - proceed with decomposition
        self.decomposer = WorkDecomposer(self.dor_validator.answers)
        decomposition = self.decomposer.decompose(work_description)
        
        return {
            "status": "success",
            "dor_status": "complete",
            "decomposition": {
                "total_features": len(decomposition.features),
                "total_stories": decomposition.total_stories,
                "total_story_points": decomposition.total_story_points,
                "estimated_hours": decomposition.estimated_hours,
                "estimated_sprints": decomposition.estimated_sprints,
                "team_recommendation": decomposition.team_size_recommendation,
            },
            "features": [
                {
                    "id": f.id,
                    "title": f.title,
                    "description": f.description,
                    "story_count": len(f.stories),
                    "story_points": f.total_story_points,
                    "risk_level": f.risk_level,
                }
                for f in decomposition.features
            ],
            "stories": [
                {
                    "id": s.id,
                    "title": s.title,
                    "story_points": s.story_points,
                    "complexity": s.complexity,
                    "parent_feature": s.parent_feature_id,
                }
                for f in decomposition.features
                for s in f.stories
            ],
            "ado_export_json": decomposition.ado_export_json,
            "markdown_summary": decomposition.markdown_summary,
        }
    
    def get_dor_status(self) -> Dict[str, Any]:
        """Get current DoR validation status."""
        validation_result = self.dor_validator.validate_dor()
        
        return {
            "status": validation_result.status.value,
            "score": f"{validation_result.score:.0%}",
            "threshold": f"{DoRValidator.DOR_THRESHOLD:.0%}",
            "can_estimate": validation_result.can_estimate,
            "progress": self.dor_validator.get_progress_summary(),
            "questions_answered": validation_result.questions_answered,
            "questions_total": validation_result.questions_total,
            "missing_categories": validation_result.missing_categories,
            "recommendations": validation_result.recommendations,
        }
    
    def _format_question(self, question: Optional[DoRQuestion]) -> Optional[Dict[str, Any]]:
        """Format a question for display."""
        if not question:
            return None
        
        return {
            "id": question.id,
            "category": question.category,
            "question": question.question,
            "required": question.required,
            "hints": question.validation_hints,
            "follow_ups": question.follow_up_questions,
        }
    
    def run_interactive_session(self, work_description: str) -> Dict[str, Any]:
        """
        Run a full interactive DoR → Estimation session.
        
        Requires interactive_callback to be set.
        """
        if not self.interactive_callback:
            raise ValueError("Interactive callback required for interactive session")
        
        print("=" * 60)
        print("🧠 CORTEX SWAGGER Estimation Session")
        print("=" * 60)
        print()
        print(f"📋 Work: {work_description}")
        print()
        print("⛔ ESTIMATION BLOCKED until Definition of Ready is complete.")
        print()
        print("Please answer the following questions to complete DoR:")
        print("-" * 60)
        
        # Ask all DoR questions
        while True:
            question = self.dor_validator.get_next_question()
            if not question:
                break
            
            print()
            print(f"📝 Category: {question.category.upper()}")
            print(f"❓ {question.question}")
            if question.validation_hints:
                print(f"   💡 Hints: {', '.join(question.validation_hints)}")
            print()
            
            # Get answer
            answer = self.interactive_callback(f"Your answer for '{question.id}': ")
            
            # Submit and validate
            is_valid, feedback = self.dor_validator.submit_answer(question.id, answer)
            
            for msg in feedback:
                print(f"   {msg}")
            
            if not is_valid:
                # Ask for clarification
                print("   Please provide a more specific answer.")
                answer = self.interactive_callback(f"Your revised answer for '{question.id}': ")
                self.dor_validator.submit_answer(question.id, answer)
        
        # Check DoR status
        validation_result = self.dor_validator.validate_dor()
        
        print()
        print("-" * 60)
        print(self.dor_validator.get_progress_summary())
        print("-" * 60)
        
        if not validation_result.can_estimate:
            print()
            print("⛔ DoR is INCOMPLETE. Cannot provide estimates.")
            return {
                "status": "dor_incomplete",
                "dor_progress": self.dor_validator.get_progress_summary(),
            }
        
        # DoR complete - generate estimate
        print()
        print("✅ DoR COMPLETE! Generating estimate...")
        print()
        
        return self.generate_estimate(work_description)


# Export classes for external use
__all__ = [
    "SWAGGEREntryPointOrchestrator",
    "DoRValidator",
    "DoRValidationResult",
    "DoRStatus",
    "WorkDecomposer",
    "WorkDecompositionResult",
    "ADOFeature",
    "ADOStory",
    "WorkItemType",
    "StoryPointScale",
    "TIMEFRAME_ESTIMATOR_AVAILABLE",
]

"""
CORTEX Definition of Ready (DoR) Validator

Interactive questioning system that validates requirements reach DoR
BEFORE any estimation can be provided.

CRITICAL: NEVER provide estimates if DoR is incomplete.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime


class DoRStatus(Enum):
    """DoR validation status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


class ClarityLevel(Enum):
    """Clarity level for requirement answers."""
    VAGUE = "vague"          # Needs clarification
    PARTIAL = "partial"       # Some specifics, needs more
    SPECIFIC = "specific"     # Clear and measurable
    EXCELLENT = "excellent"   # Detailed with metrics


@dataclass
class DoRQuestion:
    """A single DoR validation question."""
    id: str
    category: str
    question: str
    purpose: str
    required: bool = True
    answer: Optional[str] = None
    clarity: Optional[ClarityLevel] = None
    follow_up_questions: List[str] = field(default_factory=list)
    validation_hints: List[str] = field(default_factory=list)


@dataclass
class DoRChecklistItem:
    """DoR checklist item tracking."""
    id: str
    description: str
    is_met: bool = False
    evidence: Optional[str] = None


@dataclass
class DoRValidationResult:
    """Result of DoR validation process."""
    status: DoRStatus
    completion_percentage: float
    met_criteria: List[str]
    unmet_criteria: List[str]
    blocking_issues: List[str]
    recommendations: List[str]
    collected_requirements: Dict[str, Any]
    can_proceed_to_estimation: bool
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "status": self.status.value,
            "completion_percentage": self.completion_percentage,
            "met_criteria": self.met_criteria,
            "unmet_criteria": self.unmet_criteria,
            "blocking_issues": self.blocking_issues,
            "recommendations": self.recommendations,
            "collected_requirements": self.collected_requirements,
            "can_proceed_to_estimation": self.can_proceed_to_estimation,
            "timestamp": self.timestamp.isoformat()
        }


class DoRValidator:
    """
    Interactive DoR (Definition of Ready) Validator.
    
    Guides users through structured questioning to ensure requirements
    meet DoR criteria BEFORE any estimation is provided.
    
    CRITICAL RULE: Estimation is BLOCKED until DoR is complete.
    
    DoR Criteria (must ALL be met):
    1. Requirements documented with zero ambiguity
    2. Dependencies identified and validated
    3. Technical design approach agreed
    4. Test strategy defined
    5. Acceptance criteria measurable
    6. Security review complete (if applicable)
    7. Scope approved by stakeholder
    """
    
    # Minimum DoR completion to proceed with estimation
    MINIMUM_DOR_THRESHOLD = 100  # Must be 100% - no shortcuts!
    
    # Core DoR questions organized by category
    DOR_QUESTIONS = [
        DoRQuestion(
            id="req_what",
            category="Requirements",
            question="What EXACTLY does this feature/work item do? Describe the specific functionality.",
            purpose="Establish clear scope and deliverables",
            validation_hints=[
                "Avoid vague terms like 'improve', 'enhance', 'optimize'",
                "Include specific actions, inputs, and outputs",
                "Describe user-facing behavior"
            ]
        ),
        DoRQuestion(
            id="req_users",
            category="Requirements",
            question="Who are the SPECIFIC users of this feature? What personas/roles?",
            purpose="Identify target audience and usage patterns",
            validation_hints=[
                "Name specific user types (admin, customer, developer)",
                "Describe their goals and needs",
                "Mention access levels if applicable"
            ]
        ),
        DoRQuestion(
            id="dep_systems",
            category="Dependencies",
            question="What EXACT systems, APIs, databases, or services does this depend on?",
            purpose="Map technical dependencies for accurate estimation",
            validation_hints=[
                "List specific service names (not generic 'database')",
                "Identify external APIs with versions",
                "Note any services that need to be created"
            ]
        ),
        DoRQuestion(
            id="dep_teams",
            category="Dependencies",
            question="Are there dependencies on OTHER teams or external parties? Who needs to deliver what?",
            purpose="Identify blocking dependencies and coordination needs",
            validation_hints=[
                "Name specific teams or individuals",
                "Describe what they need to provide",
                "Note delivery timelines if known"
            ]
        ),
        DoRQuestion(
            id="tech_approach",
            category="Technical Design",
            question="What is the proposed technical APPROACH? High-level architecture decisions?",
            purpose="Ensure technical feasibility is considered",
            validation_hints=[
                "Describe patterns to use (REST, events, batch)",
                "Note technology choices (framework, language)",
                "Identify any proof-of-concept needs"
            ]
        ),
        DoRQuestion(
            id="tech_constraints",
            category="Technical Design",
            question="What are the MEASURABLE constraints? (Performance, scale, limits)",
            purpose="Define non-functional requirements",
            validation_hints=[
                "Response time: '<X ms' not 'fast'",
                "Scale: 'Y users' not 'scalable'",
                "Availability: 'Z% uptime' not 'reliable'"
            ]
        ),
        DoRQuestion(
            id="test_strategy",
            category="Test Strategy",
            question="How will this be TESTED? What types of tests are needed?",
            purpose="Define quality assurance approach",
            validation_hints=[
                "Unit tests (coverage target)",
                "Integration tests (scope)",
                "E2E/acceptance tests (scenarios)",
                "Performance tests (if applicable)"
            ]
        ),
        DoRQuestion(
            id="acceptance",
            category="Acceptance Criteria",
            question="What are the MEASURABLE acceptance criteria? How do we know it's done?",
            purpose="Define success criteria with metrics",
            validation_hints=[
                "Use Given-When-Then format",
                "Include edge cases",
                "Specify measurable outcomes",
                "Define what 'done' looks like"
            ]
        ),
        DoRQuestion(
            id="files_exist",
            category="Prerequisites",
            question="What files/services MUST already exist vs need to be created?",
            purpose="Clarify starting point and scope of new work",
            validation_hints=[
                "List existing files to modify",
                "List new files to create",
                "Note configuration changes"
            ]
        ),
        DoRQuestion(
            id="security",
            category="Security",
            question="What SECURITY risks exist? (Authentication, authorization, data protection)",
            purpose="Identify security considerations early",
            required=True,  # Security is always required
            validation_hints=[
                "Input validation needs",
                "Authentication requirements",
                "Data encryption needs",
                "OWASP considerations"
            ]
        )
    ]
    
    # DoR Checklist for final validation
    DOR_CHECKLIST = [
        DoRChecklistItem("checklist_requirements", "Requirements documented with zero ambiguity"),
        DoRChecklistItem("checklist_dependencies", "Dependencies identified and validated"),
        DoRChecklistItem("checklist_technical", "Technical design approach agreed"),
        DoRChecklistItem("checklist_tests", "Test strategy defined"),
        DoRChecklistItem("checklist_acceptance", "Acceptance criteria are measurable"),
        DoRChecklistItem("checklist_security", "Security review complete"),
        DoRChecklistItem("checklist_scope", "Scope approved by stakeholder")
    ]
    
    def __init__(self):
        """Initialize DoR validator."""
        self.questions: List[DoRQuestion] = [
            DoRQuestion(
                id=q.id,
                category=q.category,
                question=q.question,
                purpose=q.purpose,
                required=q.required,
                validation_hints=q.validation_hints.copy()
            ) for q in self.DOR_QUESTIONS
        ]
        self.checklist: List[DoRChecklistItem] = [
            DoRChecklistItem(item.id, item.description)
            for item in self.DOR_CHECKLIST
        ]
        self.current_question_index = 0
        self.validation_result: Optional[DoRValidationResult] = None
    
    def get_current_question(self) -> Optional[DoRQuestion]:
        """Get the current question to ask."""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def get_next_question(self) -> Optional[DoRQuestion]:
        """Get the next unanswered question."""
        for i, q in enumerate(self.questions):
            if q.answer is None:
                self.current_question_index = i
                return q
        return None
    
    def assess_answer_clarity(self, answer: str) -> ClarityLevel:
        """
        Assess the clarity level of an answer.
        
        Looks for vague terms, specificity, and measurability.
        """
        if not answer or len(answer.strip()) < 10:
            return ClarityLevel.VAGUE
        
        answer_lower = answer.lower()
        
        # Vague terms that indicate unclear requirements
        vague_terms = [
            "improve", "enhance", "better", "faster", "optimize",
            "user-friendly", "intuitive", "modern", "scalable",
            "robust", "efficient", "good", "nice", "easy",
            "as needed", "if necessary", "appropriate", "suitable",
            "etc", "and so on", "and more", "various", "some",
            "maybe", "possibly", "might", "could be", "probably"
        ]
        
        # Specific indicators
        specific_indicators = [
            "ms", "seconds", "minutes", "hours", "days",
            "percent", "%", "users", "requests", "transactions",
            "api", "endpoint", "database", "table", "field",
            "when", "given", "then", "should", "must", "will",
            "specifically", "exactly", "precisely"
        ]
        
        # Count vague and specific terms
        vague_count = sum(1 for term in vague_terms if term in answer_lower)
        specific_count = sum(1 for ind in specific_indicators if ind in answer_lower)
        
        # Check for measurable numbers
        has_numbers = any(c.isdigit() for c in answer)
        
        # Determine clarity level
        if vague_count >= 3 or len(answer) < 30:
            return ClarityLevel.VAGUE
        elif vague_count >= 1 and specific_count < 2:
            return ClarityLevel.PARTIAL
        elif specific_count >= 2 or has_numbers:
            return ClarityLevel.EXCELLENT if specific_count >= 4 else ClarityLevel.SPECIFIC
        else:
            return ClarityLevel.PARTIAL
    
    def generate_follow_up_questions(self, question: DoRQuestion, answer: str) -> List[str]:
        """Generate follow-up questions based on answer clarity."""
        follow_ups = []
        clarity = self.assess_answer_clarity(answer)
        answer_lower = answer.lower()
        
        if clarity in [ClarityLevel.VAGUE, ClarityLevel.PARTIAL]:
            # Category-specific follow-ups
            if question.category == "Requirements":
                if "improve" in answer_lower or "better" in answer_lower:
                    follow_ups.append("Improve by HOW MUCH? What specific metric should change from X to Y?")
                if "user" in answer_lower and "friendly" in answer_lower:
                    follow_ups.append("What SPECIFIC usability improvements? (e.g., 'reduce clicks from 5 to 2')")
                if len(answer) < 100:
                    follow_ups.append("Can you describe the specific INPUT → PROCESS → OUTPUT flow?")
                    
            elif question.category == "Dependencies":
                if "database" in answer_lower and not any(x in answer_lower for x in ["sql", "mongo", "postgres", "mysql", "cosmos"]):
                    follow_ups.append("WHICH database specifically? (SQL Server, PostgreSQL, MongoDB, etc.)")
                if "api" in answer_lower and "version" not in answer_lower:
                    follow_ups.append("What API VERSION? Is it stable or subject to change?")
                    
            elif question.category == "Technical Design":
                if not any(c.isdigit() for c in answer):
                    follow_ups.append("What are the SPECIFIC numeric targets? (e.g., '<500ms response time', '1000 concurrent users')")
                    
            elif question.category == "Acceptance Criteria":
                if "given" not in answer_lower and "when" not in answer_lower:
                    follow_ups.append("Can you restate using Given-When-Then format for clarity?")
                if "measure" not in answer_lower and "%" not in answer and not any(c.isdigit() for c in answer):
                    follow_ups.append("How will success be MEASURED? What's the metric?")
        
        return follow_ups
    
    def record_answer(self, question_id: str, answer: str) -> Tuple[ClarityLevel, List[str]]:
        """
        Record an answer to a question.
        
        Returns: (clarity_level, follow_up_questions)
        """
        for q in self.questions:
            if q.id == question_id:
                q.answer = answer
                q.clarity = self.assess_answer_clarity(answer)
                q.follow_up_questions = self.generate_follow_up_questions(q, answer)
                return (q.clarity, q.follow_up_questions)
        
        return (ClarityLevel.VAGUE, [])
    
    def update_checklist_from_answers(self) -> None:
        """Update checklist items based on collected answers."""
        # Map questions to checklist items
        checklist_mapping = {
            "checklist_requirements": ["req_what", "req_users"],
            "checklist_dependencies": ["dep_systems", "dep_teams"],
            "checklist_technical": ["tech_approach", "tech_constraints"],
            "checklist_tests": ["test_strategy"],
            "checklist_acceptance": ["acceptance"],
            "checklist_security": ["security"],
            "checklist_scope": ["req_what", "acceptance"]  # Derived from requirements + acceptance
        }
        
        for item in self.checklist:
            related_questions = checklist_mapping.get(item.id, [])
            
            # Check if all related questions have specific answers
            all_answered = True
            all_clear = True
            evidences = []
            
            for q_id in related_questions:
                q = next((q for q in self.questions if q.id == q_id), None)
                if q:
                    if q.answer is None:
                        all_answered = False
                    elif q.clarity in [ClarityLevel.VAGUE, ClarityLevel.PARTIAL]:
                        all_clear = False
                    else:
                        evidences.append(f"{q.category}: {q.answer[:50]}...")
            
            item.is_met = all_answered and all_clear
            if evidences:
                item.evidence = "; ".join(evidences)
    
    def calculate_completion_percentage(self) -> float:
        """Calculate DoR completion percentage."""
        self.update_checklist_from_answers()
        
        met_count = sum(1 for item in self.checklist if item.is_met)
        total_count = len(self.checklist)
        
        return (met_count / total_count) * 100 if total_count > 0 else 0
    
    def get_blocking_issues(self) -> List[str]:
        """Get list of issues blocking DoR completion."""
        issues = []
        
        # Check for unanswered required questions
        for q in self.questions:
            if q.required and q.answer is None:
                issues.append(f"❌ Missing: {q.question}")
            elif q.answer and q.clarity == ClarityLevel.VAGUE:
                issues.append(f"⚠️ Too vague: {q.category} - needs specifics")
        
        # Check unmet checklist items
        self.update_checklist_from_answers()
        for item in self.checklist:
            if not item.is_met:
                issues.append(f"☐ Unmet: {item.description}")
        
        return issues
    
    def validate(self) -> DoRValidationResult:
        """
        Perform full DoR validation.
        
        Returns DoRValidationResult with status and details.
        CRITICAL: can_proceed_to_estimation is ONLY true at 100% DoR.
        """
        completion = self.calculate_completion_percentage()
        blocking_issues = self.get_blocking_issues()
        
        # Collect requirements from answers
        collected_requirements = {}
        for q in self.questions:
            if q.answer:
                collected_requirements[q.id] = {
                    "category": q.category,
                    "question": q.question,
                    "answer": q.answer,
                    "clarity": q.clarity.value if q.clarity else None
                }
        
        # Determine status
        if completion == 0:
            status = DoRStatus.NOT_STARTED
        elif completion < 100:
            status = DoRStatus.INCOMPLETE
        else:
            status = DoRStatus.COMPLETE
        
        # Get met/unmet criteria
        met_criteria = [item.description for item in self.checklist if item.is_met]
        unmet_criteria = [item.description for item in self.checklist if not item.is_met]
        
        # Generate recommendations
        recommendations = []
        if completion < 100:
            recommendations.append("⛔ CANNOT PROVIDE ESTIMATES - DoR is incomplete")
            if unmet_criteria:
                recommendations.append(f"Address these {len(unmet_criteria)} unmet criteria first:")
                for criterion in unmet_criteria[:3]:  # Show top 3
                    recommendations.append(f"  • {criterion}")
        else:
            recommendations.append("✅ DoR complete - ready for estimation and decomposition")
        
        # CRITICAL: Only allow estimation at 100% DoR
        can_proceed = completion >= self.MINIMUM_DOR_THRESHOLD
        
        self.validation_result = DoRValidationResult(
            status=status,
            completion_percentage=completion,
            met_criteria=met_criteria,
            unmet_criteria=unmet_criteria,
            blocking_issues=blocking_issues,
            recommendations=recommendations,
            collected_requirements=collected_requirements,
            can_proceed_to_estimation=can_proceed
        )
        
        return self.validation_result
    
    def get_progress_summary(self) -> str:
        """Get a formatted progress summary."""
        answered = sum(1 for q in self.questions if q.answer)
        total = len(self.questions)
        completion = self.calculate_completion_percentage()
        
        # Build progress bar
        filled = int(completion / 10)
        bar = "█" * filled + "░" * (10 - filled)
        
        summary_lines = [
            f"📋 **DoR Progress:** [{bar}] {completion:.0f}%",
            f"   Questions: {answered}/{total} answered",
            f"   Status: {self.validation_result.status.value if self.validation_result else 'Not validated'}",
            ""
        ]
        
        if completion < 100:
            summary_lines.append("⛔ **Cannot estimate** - DoR incomplete")
            summary_lines.append("")
            summary_lines.append("**Next steps:**")
            next_q = self.get_next_question()
            if next_q:
                summary_lines.append(f"   Answer: {next_q.question}")
        else:
            summary_lines.append("✅ **Ready for estimation!**")
        
        return "\n".join(summary_lines)
    
    def format_question_for_display(self, question: DoRQuestion) -> str:
        """Format a question for user display."""
        lines = [
            f"**{question.category}** (Question {self.current_question_index + 1}/{len(self.questions)})",
            "",
            f"❓ {question.question}",
            "",
            f"*Purpose: {question.purpose}*",
            "",
            "💡 **Tips for a complete answer:**"
        ]
        
        for hint in question.validation_hints:
            lines.append(f"   • {hint}")
        
        return "\n".join(lines)
    
    def format_validation_report(self) -> str:
        """Format the validation result as a report."""
        if not self.validation_result:
            self.validate()
        
        result = self.validation_result
        
        lines = [
            "## 📋 DoR Validation Report",
            "",
            f"**Status:** {result.status.value.upper()}",
            f"**Completion:** {result.completion_percentage:.0f}%",
            "",
        ]
        
        if result.can_proceed_to_estimation:
            lines.append("✅ **DoR COMPLETE** - Ready for estimation and decomposition")
        else:
            lines.append("⛔ **DoR INCOMPLETE** - Estimation BLOCKED")
        
        lines.append("")
        
        # Met criteria
        if result.met_criteria:
            lines.append("**✅ Met Criteria:**")
            for criterion in result.met_criteria:
                lines.append(f"   • {criterion}")
            lines.append("")
        
        # Unmet criteria
        if result.unmet_criteria:
            lines.append("**❌ Unmet Criteria:**")
            for criterion in result.unmet_criteria:
                lines.append(f"   • {criterion}")
            lines.append("")
        
        # Blocking issues
        if result.blocking_issues:
            lines.append("**🚫 Blocking Issues:**")
            for issue in result.blocking_issues[:5]:  # Show top 5
                lines.append(f"   {issue}")
            lines.append("")
        
        # Recommendations
        if result.recommendations:
            lines.append("**💡 Recommendations:**")
            for rec in result.recommendations:
                lines.append(f"   {rec}")
        
        return "\n".join(lines)

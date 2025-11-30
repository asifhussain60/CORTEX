"""
CORTEX DoR (Definition of Ready) Validator

Validates that feature requirements meet the Definition of Ready (DoR) checklist
before allowing timeframe estimates. CORTEX NEVER provides estimates without complete DoR.

Author: Asif Hussain
Copyright: (c) 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import re


class DoRStatus(Enum):
    """Status of DoR validation"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    BLOCKED = "blocked"  # Critical missing items


class DoRCriterion(Enum):
    """DoR checklist criteria (8 items from planning guide)"""
    REQUIREMENTS_DOCUMENTED = "requirements_documented"
    AMBIGUITY_REMOVED = "ambiguity_removed"
    DEPENDENCIES_IDENTIFIED = "dependencies_identified"
    TECHNICAL_DESIGN_AGREED = "technical_design_agreed"
    TEST_STRATEGY_DEFINED = "test_strategy_defined"
    ACCEPTANCE_CRITERIA_MEASURABLE = "acceptance_criteria_measurable"
    SECURITY_REVIEW_COMPLETE = "security_review_complete"
    USER_APPROVAL_ON_SCOPE = "user_approval_on_scope"


@dataclass
class DoRCriterionStatus:
    """Status of a single DoR criterion"""
    criterion: DoRCriterion
    satisfied: bool = False
    evidence: str = ""
    notes: str = ""
    clarifying_question: str = ""


@dataclass
class DoRValidationResult:
    """Result of DoR validation"""
    status: DoRStatus
    criteria: Dict[DoRCriterion, DoRCriterionStatus]
    missing_count: int
    complete_count: int
    total_count: int = 8
    can_estimate: bool = False
    blocking_reason: str = ""
    clarifying_questions: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage"""
        return (self.complete_count / self.total_count) * 100 if self.total_count > 0 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'status': self.status.value,
            'criteria': {
                k.value: {
                    'satisfied': v.satisfied,
                    'evidence': v.evidence,
                    'notes': v.notes,
                    'clarifying_question': v.clarifying_question
                }
                for k, v in self.criteria.items()
            },
            'missing_count': self.missing_count,
            'complete_count': self.complete_count,
            'total_count': self.total_count,
            'completion_percentage': self.completion_percentage,
            'can_estimate': self.can_estimate,
            'blocking_reason': self.blocking_reason,
            'clarifying_questions': self.clarifying_questions,
            'timestamp': self.timestamp
        }


# Vague terms that indicate ambiguity (from planning guide)
VAGUE_TERMS = [
    "improve", "enhance", "better", "faster", "user-friendly",
    "optimize", "efficient", "secure", "scalable", "robust",
    "good", "nice", "easy", "simple", "clean", "modern",
    "reasonable", "appropriate", "adequate", "sufficient",
    "soon", "quickly", "asap", "eventually"
]


# Clarifying questions for each criterion
DOR_QUESTIONS = {
    DoRCriterion.REQUIREMENTS_DOCUMENTED: [
        "What EXACTLY does this feature do? (Be specific about inputs, outputs, behaviors)",
        "What problem does this solve for users?",
        "What are the specific use cases (happy path and edge cases)?"
    ],
    DoRCriterion.AMBIGUITY_REMOVED: [
        "Can you replace vague terms with specific metrics?",
        "What does '{term}' mean in measurable terms? (e.g., 'faster' → '<500ms response time')",
        "What are the exact boundaries and limits?"
    ],
    DoRCriterion.DEPENDENCIES_IDENTIFIED: [
        "What external systems, APIs, or databases does this feature depend on?",
        "What existing code/modules need to be modified?",
        "What third-party libraries or services are required?"
    ],
    DoRCriterion.TECHNICAL_DESIGN_AGREED: [
        "What is the high-level architecture for this feature?",
        "What design patterns will be used?",
        "How will this integrate with existing code?"
    ],
    DoRCriterion.TEST_STRATEGY_DEFINED: [
        "What types of tests are needed? (unit, integration, e2e)",
        "What is the target test coverage percentage?",
        "What are the key test scenarios?"
    ],
    DoRCriterion.ACCEPTANCE_CRITERIA_MEASURABLE: [
        "How will we know this feature is DONE? (List specific, testable criteria)",
        "What metrics will validate success?",
        "What are the performance requirements (if applicable)?"
    ],
    DoRCriterion.SECURITY_REVIEW_COMPLETE: [
        "What security risks exist for this feature?",
        "Have you reviewed the relevant OWASP Top 10 categories?",
        "What authentication/authorization is required?"
    ],
    DoRCriterion.USER_APPROVAL_ON_SCOPE: [
        "Has the user/stakeholder approved this scope?",
        "Are there any features explicitly OUT of scope?",
        "Is there agreement on the priority/timeline?"
    ]
}


class DoRValidator:
    """
    Validates Definition of Ready (DoR) before allowing timeframe estimates.
    
    CRITICAL: CORTEX NEVER provides estimates if DoR is not complete.
    
    DoR Checklist (8 items):
    1. Requirements documented with zero ambiguity
    2. All vague terms replaced with specific metrics
    3. Dependencies identified and validated
    4. Technical design approach agreed upon
    5. Test strategy defined
    6. Acceptance criteria are measurable
    7. Security review completed (OWASP checklist)
    8. User approval on scope and approach
    """
    
    def __init__(self):
        """Initialize DoR validator with criteria"""
        self.criteria_status: Dict[DoRCriterion, DoRCriterionStatus] = {}
        self._initialize_criteria()
    
    def _initialize_criteria(self) -> None:
        """Initialize all criteria as not satisfied"""
        for criterion in DoRCriterion:
            self.criteria_status[criterion] = DoRCriterionStatus(
                criterion=criterion,
                satisfied=False,
                clarifying_question=DOR_QUESTIONS[criterion][0]
            )
    
    def validate_dor(
        self,
        requirements: str,
        context: Optional[Dict[str, Any]] = None
    ) -> DoRValidationResult:
        """
        Validate requirements against DoR checklist.
        
        Args:
            requirements: Feature requirements text
            context: Optional context dict with additional info:
                - dependencies: List of known dependencies
                - acceptance_criteria: List of AC items
                - security_notes: Security review notes
                - user_approved: Boolean for user approval
                - technical_design: Design notes
                - test_strategy: Test strategy notes
        
        Returns:
            DoRValidationResult with status and missing items
        """
        context = context or {}
        
        # Reset criteria
        self._initialize_criteria()
        
        # Validate each criterion
        self._validate_requirements_documented(requirements)
        self._validate_ambiguity_removed(requirements)
        self._validate_dependencies(requirements, context.get('dependencies', []))
        self._validate_technical_design(requirements, context.get('technical_design', ''))
        self._validate_test_strategy(requirements, context.get('test_strategy', ''))
        self._validate_acceptance_criteria(requirements, context.get('acceptance_criteria', []))
        self._validate_security_review(requirements, context.get('security_notes', ''))
        self._validate_user_approval(context.get('user_approved', False))
        
        # Build result
        complete_count = sum(1 for c in self.criteria_status.values() if c.satisfied)
        missing_count = 8 - complete_count
        
        # Determine status
        if complete_count == 8:
            status = DoRStatus.COMPLETE
            can_estimate = True
            blocking_reason = ""
        elif complete_count >= 6:
            status = DoRStatus.IN_PROGRESS
            can_estimate = False
            blocking_reason = f"{missing_count} DoR criteria missing"
        else:
            status = DoRStatus.BLOCKED
            can_estimate = False
            blocking_reason = f"Critical: {missing_count}/8 DoR criteria not met"
        
        # Collect clarifying questions for missing criteria
        clarifying_questions = []
        for criterion, status_obj in self.criteria_status.items():
            if not status_obj.satisfied:
                # Add the primary question
                clarifying_questions.append(
                    f"**{self._criterion_to_label(criterion)}:** {status_obj.clarifying_question}"
                )
        
        return DoRValidationResult(
            status=status,
            criteria=self.criteria_status.copy(),
            missing_count=missing_count,
            complete_count=complete_count,
            can_estimate=can_estimate,
            blocking_reason=blocking_reason,
            clarifying_questions=clarifying_questions
        )
    
    def _validate_requirements_documented(self, requirements: str) -> None:
        """Check if requirements are documented (>100 chars with substance)"""
        criterion = DoRCriterion.REQUIREMENTS_DOCUMENTED
        
        # Check minimum content
        if len(requirements.strip()) < 100:
            self.criteria_status[criterion].satisfied = False
            self.criteria_status[criterion].notes = "Requirements too brief (< 100 chars)"
            return
        
        # Check for key sections
        has_what = any(w in requirements.lower() for w in ['feature', 'function', 'capability', 'should', 'must', 'will'])
        has_who = any(w in requirements.lower() for w in ['user', 'customer', 'admin', 'developer', 'system'])
        has_why = any(w in requirements.lower() for w in ['because', 'so that', 'in order to', 'benefit', 'value'])
        
        if has_what and (has_who or has_why):
            self.criteria_status[criterion].satisfied = True
            self.criteria_status[criterion].evidence = "Requirements contain what/who/why elements"
        else:
            self.criteria_status[criterion].notes = "Missing clear what/who/why in requirements"
    
    def _validate_ambiguity_removed(self, requirements: str) -> None:
        """Check for vague terms that need clarification"""
        criterion = DoRCriterion.AMBIGUITY_REMOVED
        
        # Find vague terms
        found_vague = []
        requirements_lower = requirements.lower()
        for term in VAGUE_TERMS:
            if term in requirements_lower:
                found_vague.append(term)
        
        if not found_vague:
            self.criteria_status[criterion].satisfied = True
            self.criteria_status[criterion].evidence = "No vague terms detected"
        else:
            self.criteria_status[criterion].satisfied = False
            self.criteria_status[criterion].notes = f"Vague terms found: {', '.join(found_vague[:5])}"
            # Update question with found term
            self.criteria_status[criterion].clarifying_question = (
                f"Please replace vague terms ({', '.join(found_vague[:3])}) with specific, measurable criteria. "
                f"Example: 'improve performance' → 'reduce response time from 500ms to 200ms'"
            )
    
    def _validate_dependencies(
        self,
        requirements: str,
        dependencies: List[str]
    ) -> None:
        """Check if dependencies are identified"""
        criterion = DoRCriterion.DEPENDENCIES_IDENTIFIED
        
        # Check for dependency mentions in requirements
        dep_keywords = ['depends on', 'requires', 'needs', 'uses', 'integrates with', 'connects to', 
                       'database', 'api', 'service', 'library', 'module', 'package']
        has_dep_mentions = any(kw in requirements.lower() for kw in dep_keywords)
        
        if dependencies or has_dep_mentions:
            self.criteria_status[criterion].satisfied = True
            self.criteria_status[criterion].evidence = f"Dependencies identified: {len(dependencies) if dependencies else 'mentioned in requirements'}"
        else:
            self.criteria_status[criterion].satisfied = False
            self.criteria_status[criterion].notes = "No dependencies explicitly listed"
    
    def _validate_technical_design(
        self,
        requirements: str,
        technical_design: str
    ) -> None:
        """Check if technical design is documented"""
        criterion = DoRCriterion.TECHNICAL_DESIGN_AGREED
        
        design_keywords = ['architecture', 'design', 'pattern', 'component', 'class', 
                         'interface', 'api', 'database', 'schema', 'flow', 'diagram']
        
        combined_text = f"{requirements} {technical_design}".lower()
        has_design = any(kw in combined_text for kw in design_keywords)
        has_substantial_design = len(technical_design.strip()) > 50
        
        if has_substantial_design or (has_design and len(requirements) > 300):
            self.criteria_status[criterion].satisfied = True
            self.criteria_status[criterion].evidence = "Technical design elements present"
        else:
            self.criteria_status[criterion].satisfied = False
            self.criteria_status[criterion].notes = "Technical design not documented"
    
    def _validate_test_strategy(
        self,
        requirements: str,
        test_strategy: str
    ) -> None:
        """Check if test strategy is defined"""
        criterion = DoRCriterion.TEST_STRATEGY_DEFINED
        
        test_keywords = ['test', 'testing', 'coverage', 'unit test', 'integration test',
                        'e2e', 'end-to-end', 'scenario', 'assertion', 'verify']
        
        combined_text = f"{requirements} {test_strategy}".lower()
        has_test_mentions = any(kw in combined_text for kw in test_keywords)
        has_substantial_strategy = len(test_strategy.strip()) > 30
        
        if has_substantial_strategy or has_test_mentions:
            self.criteria_status[criterion].satisfied = True
            self.criteria_status[criterion].evidence = "Test strategy mentioned"
        else:
            self.criteria_status[criterion].satisfied = False
            self.criteria_status[criterion].notes = "Test strategy not defined"
    
    def _validate_acceptance_criteria(
        self,
        requirements: str,
        acceptance_criteria: List[str]
    ) -> None:
        """Check if acceptance criteria are measurable"""
        criterion = DoRCriterion.ACCEPTANCE_CRITERIA_MEASURABLE
        
        # Check for AC list
        if acceptance_criteria and len(acceptance_criteria) >= 2:
            # Check if AC are measurable (contain numbers, comparisons, or specific actions)
            measurable_count = 0
            for ac in acceptance_criteria:
                if any(char.isdigit() for char in ac) or \
                   any(word in ac.lower() for word in ['when', 'then', 'given', 'should', 'must', 'returns', 'displays']):
                    measurable_count += 1
            
            if measurable_count >= len(acceptance_criteria) // 2:
                self.criteria_status[criterion].satisfied = True
                self.criteria_status[criterion].evidence = f"{len(acceptance_criteria)} measurable AC defined"
                return
        
        # Check in requirements text
        ac_keywords = ['acceptance criteria', 'definition of done', 'done when', 
                      'success criteria', 'given', 'when', 'then']
        if any(kw in requirements.lower() for kw in ac_keywords):
            self.criteria_status[criterion].satisfied = True
            self.criteria_status[criterion].evidence = "AC mentioned in requirements"
        else:
            self.criteria_status[criterion].satisfied = False
            self.criteria_status[criterion].notes = "No measurable acceptance criteria found"
    
    def _validate_security_review(
        self,
        requirements: str,
        security_notes: str
    ) -> None:
        """Check if security review is complete"""
        criterion = DoRCriterion.SECURITY_REVIEW_COMPLETE
        
        security_keywords = ['security', 'authentication', 'authorization', 'encryption',
                           'owasp', 'vulnerability', 'injection', 'xss', 'csrf', 'ssl', 'tls',
                           'password', 'token', 'permission', 'access control']
        
        combined_text = f"{requirements} {security_notes}".lower()
        has_security_mentions = sum(1 for kw in security_keywords if kw in combined_text)
        
        if has_security_mentions >= 2 or len(security_notes.strip()) > 50:
            self.criteria_status[criterion].satisfied = True
            self.criteria_status[criterion].evidence = f"Security considerations documented ({has_security_mentions} mentions)"
        else:
            self.criteria_status[criterion].satisfied = False
            self.criteria_status[criterion].notes = "Security review not documented"
    
    def _validate_user_approval(self, user_approved: bool) -> None:
        """Check if user has approved scope"""
        criterion = DoRCriterion.USER_APPROVAL_ON_SCOPE
        
        if user_approved:
            self.criteria_status[criterion].satisfied = True
            self.criteria_status[criterion].evidence = "User approved scope"
        else:
            self.criteria_status[criterion].satisfied = False
            self.criteria_status[criterion].notes = "Awaiting user approval on scope"
    
    def _criterion_to_label(self, criterion: DoRCriterion) -> str:
        """Convert criterion enum to human-readable label"""
        labels = {
            DoRCriterion.REQUIREMENTS_DOCUMENTED: "Requirements",
            DoRCriterion.AMBIGUITY_REMOVED: "Ambiguity",
            DoRCriterion.DEPENDENCIES_IDENTIFIED: "Dependencies",
            DoRCriterion.TECHNICAL_DESIGN_AGREED: "Technical Design",
            DoRCriterion.TEST_STRATEGY_DEFINED: "Test Strategy",
            DoRCriterion.ACCEPTANCE_CRITERIA_MEASURABLE: "Acceptance Criteria",
            DoRCriterion.SECURITY_REVIEW_COMPLETE: "Security Review",
            DoRCriterion.USER_APPROVAL_ON_SCOPE: "User Approval"
        }
        return labels.get(criterion, criterion.value)
    
    def get_dor_checklist_display(
        self,
        result: DoRValidationResult
    ) -> str:
        """
        Generate formatted DoR checklist display.
        
        Args:
            result: DoRValidationResult from validate_dor()
        
        Returns:
            Formatted markdown string showing checklist status
        """
        lines = []
        lines.append("## 📋 Definition of Ready (DoR) Checklist")
        lines.append("")
        lines.append(f"**Status:** {result.status.value.upper()} ({result.complete_count}/{result.total_count} complete)")
        lines.append("")
        
        for criterion, status in result.criteria.items():
            checkbox = "✅" if status.satisfied else "❌"
            label = self._criterion_to_label(criterion)
            
            if status.satisfied:
                lines.append(f"{checkbox} **{label}** - {status.evidence}")
            else:
                lines.append(f"{checkbox} **{label}** - {status.notes}")
        
        lines.append("")
        
        if not result.can_estimate:
            lines.append("---")
            lines.append("## ⚠️ ESTIMATION BLOCKED")
            lines.append("")
            lines.append(f"**Reason:** {result.blocking_reason}")
            lines.append("")
            lines.append("CORTEX cannot provide estimates until DoR is complete.")
            lines.append("Please answer the following questions:")
            lines.append("")
            for q in result.clarifying_questions:
                lines.append(f"- {q}")
        else:
            lines.append("---")
            lines.append("## ✅ DoR COMPLETE - Ready for Estimation")
        
        return "\n".join(lines)
    
    def is_ready_for_estimation(self, result: DoRValidationResult) -> bool:
        """Check if DoR validation allows estimation"""
        return result.can_estimate
    
    def get_missing_criteria(self, result: DoRValidationResult) -> List[str]:
        """Get list of missing criteria labels"""
        missing = []
        for criterion, status in result.criteria.items():
            if not status.satisfied:
                missing.append(self._criterion_to_label(criterion))
        return missing
    
    def get_clarifying_questions(self, result: DoRValidationResult) -> List[str]:
        """Get list of clarifying questions for missing criteria"""
        return result.clarifying_questions
    
    def update_criterion(
        self,
        criterion: DoRCriterion,
        satisfied: bool,
        evidence: str = "",
        notes: str = ""
    ) -> None:
        """
        Manually update a criterion status (after user provides answer).
        
        Args:
            criterion: The DoR criterion to update
            satisfied: Whether the criterion is now satisfied
            evidence: Evidence supporting the status
            notes: Additional notes
        """
        if criterion in self.criteria_status:
            self.criteria_status[criterion].satisfied = satisfied
            self.criteria_status[criterion].evidence = evidence
            self.criteria_status[criterion].notes = notes
    
    def revalidate(self) -> DoRValidationResult:
        """Re-run validation with current criteria status"""
        complete_count = sum(1 for c in self.criteria_status.values() if c.satisfied)
        missing_count = 8 - complete_count
        
        if complete_count == 8:
            status = DoRStatus.COMPLETE
            can_estimate = True
            blocking_reason = ""
        elif complete_count >= 6:
            status = DoRStatus.IN_PROGRESS
            can_estimate = False
            blocking_reason = f"{missing_count} DoR criteria missing"
        else:
            status = DoRStatus.BLOCKED
            can_estimate = False
            blocking_reason = f"Critical: {missing_count}/8 DoR criteria not met"
        
        clarifying_questions = []
        for criterion, status_obj in self.criteria_status.items():
            if not status_obj.satisfied:
                clarifying_questions.append(
                    f"**{self._criterion_to_label(criterion)}:** {status_obj.clarifying_question}"
                )
        
        return DoRValidationResult(
            status=status,
            criteria=self.criteria_status.copy(),
            missing_count=missing_count,
            complete_count=complete_count,
            can_estimate=can_estimate,
            blocking_reason=blocking_reason,
            clarifying_questions=clarifying_questions
        )

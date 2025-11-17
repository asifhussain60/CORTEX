"""
DoD/DoR Clarification Stage

Clarifies Definition of Done and Definition of Ready with interactive prompts.

Author: CORTEX Development Team
Version: 1.0
"""

from typing import Dict, Any, List
from dataclasses import dataclass

from src.workflows.workflow_pipeline import WorkflowStage, WorkflowState, StageResult, StageStatus


@dataclass
class DoDCriteria:
    """Definition of Done criteria"""
    build_clean: bool = False
    tests_pass: bool = False
    new_tests_created: bool = False
    tdd_cycle_complete: bool = False
    code_formatted: bool = False
    no_lint_violations: bool = False
    docs_updated: bool = False
    app_runs: bool = False
    no_exceptions: bool = False
    functionality_verified: bool = False


@dataclass
class DoRCriteria:
    """Definition of Ready criteria"""
    user_story_clear: bool = False
    acceptance_criteria_defined: bool = False
    testable_outcomes: bool = False
    scope_bounded: bool = False
    dependencies_identified: bool = False
    estimate_possible: bool = False
    files_known: bool = False
    architecture_clear: bool = False
    no_blocking_dependencies: bool = False


class DoDDoRClarifierStage:
    """
    Clarify Definition of Done and Definition of Ready
    
    Interactive stage that:
    1. Presents DoD/DoR criteria to user
    2. Asks for confirmation/clarification
    3. Identifies missing information
    4. Ensures work is "ready" before starting
    """
    
    def execute(self, state: WorkflowState) -> StageResult:
        """
        Execute DoD/DoR clarification
        
        Args:
            state: Workflow state with user_request and threat model output
        
        Returns:
            StageResult with clarified DoD/DoR
        """
        # Get threat model output (if available)
        threat_model = state.get_stage_output("threat_model")
        
        # Assess Definition of Ready
        dor = self._assess_dor(state.user_request, state.context)
        
        # Propose Definition of Done
        dod = self._propose_dod(state.user_request, threat_model)
        
        # Generate clarification questions
        questions = self._generate_questions(dor, dod, threat_model)
        
        # Check readiness
        is_ready = self._check_readiness(dor)
        
        return StageResult(
            stage_id="clarify_dod_dor",
            status=StageStatus.SUCCESS,
            duration_ms=0,
            output={
                "dor": {
                    "user_story_clear": dor.user_story_clear,
                    "acceptance_criteria_defined": dor.acceptance_criteria_defined,
                    "testable_outcomes": dor.testable_outcomes,
                    "scope_bounded": dor.scope_bounded,
                    "dependencies_identified": dor.dependencies_identified,
                    "estimate_possible": dor.estimate_possible,
                    "files_known": dor.files_known,
                    "architecture_clear": dor.architecture_clear,
                    "no_blocking_dependencies": dor.no_blocking_dependencies,
                    "ready": is_ready
                },
                "dod": {
                    "build_clean": dod.build_clean,
                    "tests_pass": dod.tests_pass,
                    "new_tests_created": dod.new_tests_created,
                    "tdd_cycle_complete": dod.tdd_cycle_complete,
                    "code_formatted": dod.code_formatted,
                    "no_lint_violations": dod.no_lint_violations,
                    "docs_updated": dod.docs_updated,
                    "app_runs": dod.app_runs,
                    "no_exceptions": dod.no_exceptions,
                    "functionality_verified": dod.functionality_verified
                },
                "questions": questions,
                "needs_clarification": len(questions) > 0
            },
            metadata={
                "interactive": True
            }
        )
    
    def validate_input(self, state: WorkflowState) -> bool:
        """Validate state has user request"""
        return bool(state.user_request)
    
    def on_failure(self, state: WorkflowState, error: Exception):
        """Log clarification failure"""
        print(f"⚠️  DoD/DoR clarification failed: {error}")
    
    def _assess_dor(self, request: str, context: Dict[str, Any]) -> DoRCriteria:
        """
        Assess Definition of Ready criteria
        
        Args:
            request: User request text
            context: Workflow context
        
        Returns:
            DoRCriteria with assessment
        """
        dor = DoRCriteria()
        
        # User story clear? (if request is detailed)
        dor.user_story_clear = len(request.split()) > 10
        
        # Acceptance criteria defined? (if "when", "should", "expect" present)
        dor.acceptance_criteria_defined = any(
            word in request.lower() 
            for word in ["when", "should", "expect", "verify", "validate"]
        )
        
        # Testable outcomes? (if acceptance criteria or explicit test mention)
        dor.testable_outcomes = dor.acceptance_criteria_defined or "test" in request.lower()
        
        # Scope bounded? (single feature, not multiple)
        dor.scope_bounded = "and" not in request.lower() or request.count("and") <= 2
        
        # Dependencies identified? (check context for related patterns)
        dor.dependencies_identified = bool(context.get("tier2", {}).get("file_relationships"))
        
        # Estimate possible? (if similar patterns exist in Tier 2)
        dor.estimate_possible = bool(context.get("tier2", {}).get("similar_patterns"))
        
        # Files known? (if context has file suggestions)
        dor.files_known = bool(context.get("tier3", {}).get("active_files"))
        
        # Architecture clear? (if request mentions components/structure)
        dor.architecture_clear = any(
            word in request.lower()
            for word in ["component", "service", "module", "class", "function"]
        )
        
        # No blocking dependencies (assume true unless context says otherwise)
        dor.no_blocking_dependencies = True
        
        return dor
    
    def _propose_dod(self, request: str, threat_model: Dict[str, Any]) -> DoDCriteria:
        """
        Propose Definition of Done based on request and threats
        
        Args:
            request: User request
            threat_model: Threat model output (may be None)
        
        Returns:
            DoDCriteria with proposed criteria
        """
        dod = DoDCriteria()
        
        # Standard criteria (always required)
        dod.build_clean = True
        dod.tests_pass = True
        dod.new_tests_created = True
        dod.tdd_cycle_complete = True
        dod.code_formatted = True
        dod.no_lint_violations = True
        dod.app_runs = True
        dod.no_exceptions = True
        dod.functionality_verified = True
        
        # Docs required? (if API, export, or public interface)
        dod.docs_updated = any(
            word in request.lower()
            for word in ["api", "export", "public", "endpoint", "interface"]
        )
        
        # Additional criteria if high-risk threats
        if threat_model and threat_model.get("risk_level") in ["high", "critical"]:
            # Could add security-specific DoD criteria here
            pass
        
        return dod
    
    def _generate_questions(
        self,
        dor: DoRCriteria,
        dod: DoDCriteria,
        threat_model: Dict[str, Any]
    ) -> List[str]:
        """
        Generate clarification questions for unmet criteria
        
        Args:
            dor: Definition of Ready assessment
            dod: Proposed Definition of Done
            threat_model: Threat model output
        
        Returns:
            List of clarification questions
        """
        questions = []
        
        # DoR questions
        if not dor.user_story_clear:
            questions.append("📋 Can you provide more detail about what this feature should do?")
        
        if not dor.acceptance_criteria_defined:
            questions.append("✓ What are the acceptance criteria? (e.g., 'User should be able to...')")
        
        if not dor.testable_outcomes:
            questions.append("🧪 How will we know this feature works correctly?")
        
        if not dor.scope_bounded:
            questions.append("🎯 Can we break this into smaller, focused tasks?")
        
        if not dor.files_known:
            questions.append("📁 Which files need to be modified for this feature?")
        
        if not dor.architecture_clear:
            questions.append("🏗️  What's the architectural approach? (e.g., new service, modify existing component)")
        
        # Security questions (if threats identified)
        if threat_model and threat_model.get("high_risk_count", 0) > 0:
            questions.append("🔒 High-risk threats detected. Should we add security review to DoD?")
        
        return questions
    
    def _check_readiness(self, dor: DoRCriteria) -> bool:
        """
        Check if Definition of Ready is satisfied
        
        Args:
            dor: Definition of Ready criteria
        
        Returns:
            True if ready to proceed
        """
        # Critical criteria that MUST be true
        critical = [
            dor.user_story_clear,
            dor.testable_outcomes,
            dor.scope_bounded,
            dor.no_blocking_dependencies
        ]
        
        return all(critical)


# Factory function
def create_stage() -> WorkflowStage:
    """Create DoD/DoR clarifier stage instance"""
    return DoDDoRClarifierStage()

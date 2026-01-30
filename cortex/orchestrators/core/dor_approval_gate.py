"""
Intent Reflection and DoR Approval Gate.

AC-ID: AC-GOVE-DOR-001
Purpose: Display intent classification in concise markdown, require user approval

This module provides:
1. Concise intent reflection in markdown format
2. Definition of Ready (DoR) checkpoint before execution
3. User approval gate for each turn
4. Direct integration with IntentRouter
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.orchestrators.core.intent_router import RoutingDecision, IntentType, IntentRouter
from cortex.orchestrators.core.governance_principles import get_display_name
from cortex.core.result import Ok, Err
from cortex.models.canonical_enums import ApprovalStatus




# DoR Confidence threshold - blocks execution if below this value
DOR_CONFIDENCE_THRESHOLD = 0.6


@dataclass
class IntentReflection:
    """
    Structured reflection of classified intent.
    
    Designed for concise markdown display without overwhelming the user.
    
    DoR Confidence represents CORTEX's ability to complete the request
    with full confidence. If DoR Confidence is below threshold (60%),
    execution is blocked until clarification is provided.
    """
    
    intent_type: str
    """Primary intent category (IMPLEMENT, FIX, REFACTOR, ANALYZE, etc.)"""
    
    target_handler: str
    """Orchestrator that will handle this request"""
    
    dor_confidence: float
    """DoR Confidence (0.0 to 1.0) - CORTEX's ability to complete request successfully"""
    
    scope: str
    """Scope of operation (FILE, MODULE, SYSTEM, DOMAIN)"""
    
    key_entities: List[str] = field(default_factory=lambda: [])
    """Key entities identified in the request"""
    
    estimated_impact: str = "low"
    """Estimated impact level (low, medium, high)"""
    
    requires_tests: bool = True
    """Whether TDD applies (CORE-008)"""
    
    governance_rules: List[str] = field(default_factory=lambda: [])
    """Applicable governance rules"""
    
    business_principles: Dict[str, str] = field(default_factory=dict)
    """Business principles mapped to CORE rules (e.g., {'Quality First': 'CORE-008'})"""    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    """When reflection was generated"""

    def _get_execution_plan(self) -> List[str]:
        """
        Generate execution plan bullets based on intent type.
        
        Returns:
            List of action bullets describing what CORTEX will do
        """
        plan: List[str] = []
        
        if self.intent_type == "IMPLEMENT":
            plan = [
                f"Create implementation in {self.key_entities[0] if self.key_entities else 'target module'}",
                "Write unit tests first (RED phase)",
                "Implement functionality to pass tests (GREEN phase)",
                "Refactor for code quality and maintainability (REFACTOR phase)"
            ]
        elif self.intent_type == "FIX":
            plan = [
                "Identify root cause of the issue",
                "Write failing test that reproduces the bug",
                "Implement fix to resolve the issue",
                "Verify all tests pass and no regressions introduced"
            ]
        elif self.intent_type == "REFACTOR":
            plan = [
                "Analyze code structure and identify improvement opportunities",
                "Apply SOLID principles and design patterns",
                "Preserve existing functionality with comprehensive tests",
                "Validate metrics and performance improvements"
            ]
        elif self.intent_type == "ANALYZE":
            plan = [
                "Examine codebase, architecture, or design",
                "Identify patterns, issues, or opportunities",
                "Provide findings and recommendations",
                "Suggest next steps for implementation or improvement"
            ]
        elif self.intent_type == "TEST":
            plan = [
                "Generate comprehensive test suite covering critical paths",
                "Ensure >80% code coverage where applicable",
                "Validate edge cases and error scenarios",
                "Integrate tests into CI/CD pipeline"
            ]
        elif self.intent_type == "DOCUMENT":
            plan = [
                "Generate clear, concise documentation",
                "Include code examples and usage patterns",
                "Add diagrams or visual explanations where helpful",
                "Ensure documentation stays synchronized with code"
            ]
        else:
            plan = [
                f"Execute {self.intent_type.lower()} operation",
                "Validate against acceptance criteria",
                "Track progress and report results",
                "Log completion in audit trail"
            ]
        
        return plan
    
    def _get_dod_criteria(self) -> List[str]:
        """
        Generate Definition of Done criteria based on intent type and rules.
        
        Returns:
            List of success criteria that must be met
        """
        dod: List[str] = []
        
        # Universal DoD criteria (always apply)
        dod.append("✅ Operation completed without errors")
        dod.append("✅ Audit trail logged (AC_START → AC_COMPLETE)")
        
        # CORE-008: TDD requirement
        if self.requires_tests or self.intent_type in ["IMPLEMENT", "FIX", "TEST"]:
            dod.append("✅ All tests passing (100% of new/modified code)")
        
        # CORE-011: Type hints
        if "CORE-011" in self.governance_rules:
            dod.append("✅ Type hints present on all functions")
        
        # CORE-012: Docstrings
        if "CORE-012" in self.governance_rules:
            dod.append("✅ Google-style docstrings on all public functions")
        
        # Intent-specific criteria
        if self.intent_type == "IMPLEMENT":
            dod.extend([
                "✅ Feature works as specified",
                "✅ Code review approved",
                "✅ No regressions in existing tests"
            ])
        elif self.intent_type == "FIX":
            dod.extend([
                "✅ Bug is fixed and verified",
                "✅ Test added to prevent regression",
                "✅ No new bugs introduced"
            ])
        elif self.intent_type == "REFACTOR":
            dod.extend([
                "✅ Code quality improved (metrics verified)",
                "✅ All existing tests still passing",
                "✅ Performance meets or exceeds baseline"
            ])
        elif self.intent_type == "ANALYZE":
            dod.extend([
                "✅ Analysis complete with findings documented",
                "✅ Recommendations provided and validated",
                "✅ Report ready for review"
            ])
        
        return dod

    def to_markdown(self) -> str:
        """
        Generate concise markdown representation with execution plan and DoD.
        
        Designed to be scannable in <15 seconds.
        Includes:
        1. Intent classification table
        2. Execution plan (what CORTEX will do)
        3. Definition of Done (success criteria)
        4. Approval/blocking decision
        
        Returns:
            Markdown string for user display
        """
        # DoR Confidence indicator with blocking status
        if self.dor_confidence >= 0.8:
            confidence_badge = "🟢 High"
        elif self.dor_confidence >= DOR_CONFIDENCE_THRESHOLD:
            confidence_badge = "🟡 Medium"
        else:
            confidence_badge = "🔴 Low (BLOCKED)"
        
        # Check if DoR is met (execution allowed)
        dor_met = self.dor_confidence >= DOR_CONFIDENCE_THRESHOLD
        
        # Impact indicator
        impact_badges = {
            "low": "🔵",
            "medium": "🟡", 
            "high": "🔴"
        }
        impact_badge = impact_badges.get(self.estimated_impact, "⚪")
        
        # Build markdown with three sections
        lines = [
            "### 📋 Intent Classification",
            "",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| **Intent** | `{self.intent_type}` |",
            f"| **Handler** | `{self.target_handler}` |",
            f"| **DoR Confidence** | {confidence_badge} ({self.dor_confidence:.0%}) |",
            f"| **Scope** | `{self.scope}` |",
            f"| **Impact** | {impact_badge} {self.estimated_impact.title()} |",
        ]
        
        # Only show entities if present (keep concise)
        if self.key_entities:
            entities_str = ", ".join(f"`{e}`" for e in self.key_entities[:3])
            if len(self.key_entities) > 3:
                entities_str += f" +{len(self.key_entities) - 3} more"
            lines.append(f"| **Entities** | {entities_str} |")
        
        # Business Principles (mapped to CORE rules)
        if self.business_principles:
            # Format: **Quality First** → TDD (CORE-008) | **Maintainability** → Type Safety (CORE-011)
            principles_parts = []
            for principle, rule in self.business_principles.items():
                principles_parts.append(f"**{principle}** → {rule}")
            principles_str = " | ".join(principles_parts)
            lines.append(f"| **Business Principles** | {principles_str} |")
        # Governance rules fallback (if no business principles mapped)
        elif self.governance_rules:
            rules_str = ", ".join(self.governance_rules[:3])
            lines.append(f"| **Rules** | {rules_str} |")
        
        # Add execution plan section
        lines.extend([
            "",
            "### 📝 Execution Plan",
            "",
            "What CORTEX will do:",
            ""
        ])
        for bullet in self._get_execution_plan():
            lines.append(f"- {bullet}")
        
        # Add Definition of Done section
        lines.extend([
            "",
            "### ✅ Definition of Done",
            "",
            "Success looks like:",
            ""
        ])
        for criterion in self._get_dod_criteria():
            lines.append(f"- {criterion}")
        
        # Add DoR status indicator and approval section
        if dor_met:
            lines.extend([
                "",
                "---",
                "",
                "**⏳ Awaiting Your Decision:**",
                "",
                "1️⃣ **proceed** — Execute with this intent classification",
                "2️⃣ **modify: {changes}** — Adjust the classification and try again",
                "3️⃣ **cancel** — Abort this operation",
                "",
                "Reply with: `proceed` / `modify: {your changes}` / `cancel`",
            ])
        else:
            lines.extend([
                "",
                "---",
                "",
                "**⛔ DoR NOT MET — Execution Blocked**",
                "",
                f"DoR Confidence ({self.dor_confidence:.0%}) is below threshold ({DOR_CONFIDENCE_THRESHOLD:.0%}).",
                "",
                "Please provide clarification:",
                "- More specific details about the request",
                "- Target files, modules, or components",
                "- Expected behavior or acceptance criteria",
                "",
                "Reply with additional context to increase DoR Confidence.",
            ])
        
        return "\n".join(lines)


@dataclass
class ApprovalDecision:
    """User's decision on the intent classification."""
    
    status: ApprovalStatus
    """Approval status"""
    
    feedback: Optional[str] = None
    """Optional user feedback or modification"""
    
    modified_intent: Optional[str] = None
    """Modified intent if user corrected classification"""
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class DoRApprovalGate:
    """
    Definition of Ready (DoR) Approval Gate.
    
    Enforces user approval before orchestration execution.
    Displays intent reflection in concise markdown format.
    
    Flow:
    1. classify_and_reflect() - Classify intent, generate reflection
    2. User reviews markdown reflection
    3. approve() or reject() - User provides decision
    4. execute_if_approved() - Execute only if approved
    
    Usage:
        gate = DoRApprovalGate()
        
        # Step 1: Classify and show reflection
        reflection = gate.classify_and_reflect(
            text="Implement user authentication",
            context={"domain": "security"}
        )
        print(reflection.to_markdown())  # Show to user
        
        # Step 2: Wait for user approval
        # ... user reviews ...
        
        # Step 3: User approves
        gate.approve()
        
        # Step 4: Execute
        result = gate.execute_if_approved(text, context)
    """
    
    def __init__(self) -> None:
        """Initialize DoR Approval Gate."""
        self._router: Optional[IntentRouter] = None
        self._current_reflection: Optional[IntentReflection] = None
        self._approval_decision: Optional[ApprovalDecision] = None
        self._pending_text: Optional[str] = None
        self._pending_context: Optional[Dict[str, Any]] = None
    
    def classify_and_reflect(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> IntentReflection:
        """
        Classify intent and generate reflection for user review.
        
        Args:
            text: User request text
            context: Request context
        
        Returns:
            IntentReflection for markdown display
        
        Raises:
            ValueError: If text empty
            RuntimeError: If classification fails
        """
        if not text or not text.strip():
            raise ValueError("Request text cannot be empty")
        
        # Store for later execution
        self._pending_text = text
        self._pending_context = context
        
        # Get router and classify
        if self._router is None:
            self._router = IntentRouter()
        routing_decision = self._router.classify_intent(text, context)
        
        if routing_decision is None:
            raise RuntimeError("Intent classification returned None")
        
        # Build reflection
        self._current_reflection = self._build_reflection(routing_decision, text, context)
        
        # Reset approval state
        self._approval_decision = None
        
        return self._current_reflection
    
    def _build_reflection(
        self,
        decision: RoutingDecision,
        text: str,
        context: Dict[str, Any]
    ) -> IntentReflection:
        """
        Build IntentReflection from routing decision.
        
        Args:
            decision: Routing decision from classifier
            text: Original request text
            context: Request context
        
        Returns:
            Populated IntentReflection
        """
        # Determine scope from decision or context
        scope = context.get("scope", "MODULE")
        if "file" in text.lower() or "single" in text.lower():
            scope = "FILE"
        elif "system" in text.lower() or "entire" in text.lower():
            scope = "SYSTEM"
        elif "domain" in text.lower():
            scope = "DOMAIN"
        
        # Estimate impact
        impact = "low"
        if decision.intent_type == IntentType.REFACTOR:
            impact = "medium"
        if scope in ["SYSTEM", "DOMAIN"]:
            impact = "high"
        
        # Determine applicable governance rules
        rules: List[str] = ["CORE-008"]  # TDD always applies
        if decision.intent_type == IntentType.IMPLEMENT:
            rules.extend(["CORE-011", "CORE-012"])  # Type hints, docstrings
        if "test" in text.lower():
            rules.append("CORE-008")
        
        # Map business principles to CORE rules based on intent type
        business_principles: Dict[str, str] = {}
        
        # Universal principles
        business_principles["Quality First"] = "TDD (CORE-008)"
        
        if decision.intent_type == IntentType.IMPLEMENT:
            business_principles["Maintainability"] = "Type Safety (CORE-011)"
            business_principles["Documentation"] = "Docstrings (CORE-012)"
        elif decision.intent_type == IntentType.FIX:
            business_principles["Reliability"] = "Test Coverage (CORE-008)"
            business_principles["Root Cause Analysis"] = "Implementation Truth (CORE-030)"
        elif decision.intent_type == IntentType.REFACTOR:
            business_principles["Code Quality"] = "SOLID Principles"
            business_principles["Maintainability"] = "Type Safety (CORE-011)"
        elif decision.intent_type == IntentType.ANALYZE:
            business_principles["Evidence-Based"] = "Implementation Truth (CORE-030)"
        elif decision.intent_type == IntentType.TEST:
            business_principles["Quality First"] = "TDD (CORE-008)"
            business_principles["Coverage"] = "Comprehensive Testing"
        elif decision.intent_type == IntentType.DOCUMENT:
            business_principles["Clarity"] = "Docstrings (CORE-012)"
            business_principles["Accuracy"] = "Implementation Truth (CORE-030)"
        
        # Extract key entities (simple heuristic)
        entities: List[str] = []
        for word in text.split():
            if word.startswith(("AC-", "CORE-", "PHASE-")):
                entities.append(word.rstrip(".,;:"))
        
        return IntentReflection(
            intent_type=decision.intent_type.value,
            target_handler=decision.target_handler,
            dor_confidence=decision.confidence_score,
            scope=scope,
            key_entities=entities,
            estimated_impact=impact,
            requires_tests=True,
            governance_rules=list(set(rules)),
            business_principles=business_principles,
        )
    
    def approve(self, feedback: Optional[str] = None) -> None:
        """
        Approve the current intent classification.
        
        Args:
            feedback: Optional approval feedback
        
        Raises:
            RuntimeError: If no pending classification or DoR not met
        """
        if self._current_reflection is None:
            raise RuntimeError("No pending classification to approve")
        
        # Block execution if DoR confidence is below threshold
        if self._current_reflection.dor_confidence < DOR_CONFIDENCE_THRESHOLD:
            raise RuntimeError(
                f"DoR NOT MET: Cannot approve execution. "
                f"DoR Confidence ({self._current_reflection.dor_confidence:.0%}) "
                f"is below threshold ({DOR_CONFIDENCE_THRESHOLD:.0%}). "
                f"Please provide additional clarification."
            )
        
        self._approval_decision = ApprovalDecision(
            status=ApprovalStatus.APPROVED,
            feedback=feedback,
        )
    
    def reject(self, reason: str) -> None:
        """
        Reject the current intent classification.
        
        Args:
            reason: Reason for rejection
        """
        if self._current_reflection is None:
            raise RuntimeError("No pending classification to reject")
        
        self._approval_decision = ApprovalDecision(
            status=ApprovalStatus.REJECTED,
            feedback=reason,
        )
    
    def modify(self, corrected_intent: str, feedback: Optional[str] = None) -> None:
        """
        Modify the intent classification.
        
        Args:
            corrected_intent: Corrected intent type
            feedback: Optional modification feedback
        """
        if self._current_reflection is None:
            raise RuntimeError("No pending classification to modify")
        
        self._approval_decision = ApprovalDecision(
            status=ApprovalStatus.MODIFIED,
            feedback=feedback,
            modified_intent=corrected_intent,
        )
    
    @property
    def is_approved(self) -> bool:
        """Check if current intent is approved for execution."""
        if self._approval_decision is None:
            return False
        return self._approval_decision.status in [
            ApprovalStatus.APPROVED,
            ApprovalStatus.MODIFIED,
        ]
    
    @property
    def is_dor_met(self) -> bool:
        """Check if Definition of Ready (DoR) is met for execution."""
        if self._current_reflection is None:
            return False
        return self._current_reflection.dor_confidence >= DOR_CONFIDENCE_THRESHOLD
    
    @property
    def is_pending(self) -> bool:
        """Check if approval is pending."""
        return (
            self._current_reflection is not None
            and self._approval_decision is None
        )
    
    def get_reflection_markdown(self) -> str:
        """
        Get current reflection as markdown.
        
        Returns:
            Markdown string or empty if no reflection
        """
        if self._current_reflection is None:
            return ""
        return self._current_reflection.to_markdown()
    
    def execute_if_approved(self) -> Dict[str, Any]:
        """
        Execute orchestration if approved.
        
        Returns:
            Execution result dictionary
        
        Raises:
            RuntimeError: If not approved or no pending request
        
        AC-GOVE-DOR-WIRE-001: Approved operations flow through MasterOrchestrator
        """
        if not self.is_approved:
            raise RuntimeError(
                "Cannot execute: approval required. "
                "Call approve() or modify() first."
            )
        
        if self._router is None or self._pending_text is None:
            raise RuntimeError("No pending request to execute")
        
        # AC-GOVE-DOR-WIRE-001: Route through MasterOrchestrator instead of direct router
        # This ensures ALL orchestrator execution flows through master supervision
        try:
            from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
            
            master = MasterOrchestrator.instance()
            result = master.execute_approved_operation(
                text=self._pending_text,
                context=self._pending_context or {},
            )
            
            # Clear pending state
            self._pending_text = None
            self._pending_context = None
            
            if isinstance(result, Ok):
                return {"status": "success", "result": result.unwrap()}
            else:
                # Result is Err - extract error message
                return {"status": "error", "error": str(result)}
        except ImportError:
            # Fallback to direct router if MasterOrchestrator not available
            text_to_execute = self._pending_text or ""
            result = self._router.execute_orchestrated(
                text=text_to_execute,
                context=self._pending_context or {},
            )
            
            # Clear pending state
            self._pending_text = None
            self._pending_context = None
            
            if isinstance(result, Ok):
                return {"status": "success", "result": result.unwrap()}
            else:
                return {"status": "error", "error": getattr(result, "error", str(result))}




    
    def reset(self) -> None:
        """Reset gate state for new request."""
        self._router = None
        self._current_reflection = None
        self._approval_decision = None
        self._pending_text = None
        self._pending_context = None


# Convenience function for quick reflection
def reflect_intent(text: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Quick function to classify and return markdown reflection.
    
    Args:
        text: Request text
        context: Optional context
    
    Returns:
        Markdown reflection string
    """
    gate = DoRApprovalGate()
    reflection = gate.classify_and_reflect(text, context or {})
    return reflection.to_markdown()

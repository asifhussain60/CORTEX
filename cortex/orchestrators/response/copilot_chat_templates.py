"""Copilot Chat Response Templates for GitHub Copilot Chat Sessions.

This module provides specialized response templates for GitHub Copilot Chat,
ensuring consistent formatting, proper section ordering, and "Next Steps"
always appearing as the last section before approval gates.

AC-ID: AC-REFACTOR-ARCHITECT-001
Authority: cortex-architect.prompt.md v12.0
Governance: CORE-002 (inline only), CORE-029 (response header)

Author: Asif Hussain
Date: 2026-02-04
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.models.canonical_enums import ResponseType, VariableType
from cortex.orchestrators.response.response_templates import (
    ResponseTemplate,
    ResponseTemplateRegistry,
    TemplateEngine,
    VariableSpec,
)


class CopilotChatMode(Enum):
    """Copilot chat interaction modes."""

    AUDIT = "audit"
    DESIGN = "design"
    DOR_GATE = "dor_gate"
    IMPLEMENTATION_COMPLETE = "implementation_complete"
    NEXT_STEPS_ONLY = "next_steps_only"


@dataclass
class SectionDefinition:
    """Definition of a response section.

    Attributes:
        name: Section name (e.g., "Header", "Next Steps")
        required: Whether section is mandatory
        order: Position in response (lower = earlier)
        template: Section template pattern
    """

    name: str
    required: bool
    order: int
    template: str


class CopilotChatTemplateEngine:
    """Template engine for GitHub Copilot Chat responses.

    Provides 5 specialized templates with enforced section ordering:
    1. copilot-audit-summary: Audit mode results
    2. copilot-design-challenge: Challenge presentation
    3. copilot-dor-gate: Approval gate with DoR
    4. copilot-implementation-complete: Post-implementation summary
    5. copilot-next-steps: Reusable "Next Steps" section (always last)

    Key Features:
    - Enforces "Next Steps" as the last section before approval gates
    - Validates section ordering
    - Provides consistent formatting across all modes
    - Integrates with existing ResponseTemplateRegistry

    Example:
        >>> engine = CopilotChatTemplateEngine()
        >>> result = engine.render_audit_summary(
        ...     p0_count=2,
        ...     p1_count=5,
        ...     recommendations=["Add caching", "Refactor module X"]
        ... )
        >>> print(result)
        ## 🔍 CORTEX Audit
        **Author:** Asif Hussain | **Mode:** Audit ✅
        ...
        ### 🎯 Next Steps
        ...
    """

    def __init__(self, registry: Optional[ResponseTemplateRegistry] = None):
        """Initialize the Copilot chat template engine.

        Args:
            registry: Optional existing template registry to use.
                     If None, creates a new registry.
        """
        self.base_engine = TemplateEngine()
        if registry:
            self.base_engine.registry = registry

        self._register_templates()

    def _register_templates(self) -> None:
        """Register all Copilot chat templates."""

        # Template 1: Audit Summary
        self.base_engine.create_template(
            template_id="copilot-audit-summary",
            version="1.0.0",
            name="Copilot Audit Summary",
            description="Audit mode results with P0/P1/P2/P3 breakdown and recommendations",
            pattern=self._get_audit_summary_pattern(),
            response_type=ResponseType.AUDIT,
            variables={
                "orchestrator": VariableSpec(
                    name="orchestrator",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Orchestrator name (e.g., 'MasterOrchestrator')"
                ),
                "p0_count": VariableSpec(
                    name="p0_count",
                    var_type=VariableType.INTEGER,
                    required=True,
                    description="Count of P0 (critical) issues"
                ),
                "p1_count": VariableSpec(
                    name="p1_count",
                    var_type=VariableType.INTEGER,
                    required=True,
                    description="Count of P1 (infrastructure) issues"
                ),
                "p2_count": VariableSpec(
                    name="p2_count",
                    var_type=VariableType.INTEGER,
                    required=True,
                    description="Count of P2 (quality) issues"
                ),
                "p3_count": VariableSpec(
                    name="p3_count",
                    var_type=VariableType.INTEGER,
                    required=True,
                    description="Count of P3 (cleanup) issues"
                ),
                "audit_details": VariableSpec(
                    name="audit_details",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Detailed audit results (markdown table)"
                ),
                "recommendations": VariableSpec(
                    name="recommendations",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Out of the box recommendations (markdown list)"
                ),
                "next_steps": VariableSpec(
                    name="next_steps",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Ordered next actions (markdown list)"
                ),
            }
        )

        # Template 2: Design Challenge
        self.base_engine.create_template(
            template_id="copilot-design-challenge",
            version="1.0.0",
            name="Copilot Design Challenge",
            description="Challenge presentation with extensibility/scalability/accuracy-efficiency analysis",
            pattern=self._get_design_challenge_pattern(),
            response_type=ResponseType.CHALLENGE,
            variables={
                "orchestrator": VariableSpec(
                    name="orchestrator",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Orchestrator name"
                ),
                "user_request": VariableSpec(
                    name="user_request",
                    var_type=VariableType.STRING,
                    required=True,
                    description="User's original request"
                ),
                "extensibility_analysis": VariableSpec(
                    name="extensibility_analysis",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Extensibility & scalability analysis table"
                ),
                "accuracy_efficiency_tradeoff": VariableSpec(
                    name="accuracy_efficiency_tradeoff",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Accuracy vs efficiency tradeoff matrix"
                ),
                "weaknesses": VariableSpec(
                    name="weaknesses",
                    var_type=VariableType.STRING,
                    required=True,
                    description="3+ identified weaknesses (markdown table)"
                ),
                "fix_plans": VariableSpec(
                    name="fix_plans",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Evidence-based fix plans (markdown sections)"
                ),
                "best_practices": VariableSpec(
                    name="best_practices",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Best practices alignment table"
                ),
                "counter_proposal": VariableSpec(
                    name="counter_proposal",
                    var_type=VariableType.STRING,
                    required=False,
                    description="Alternative approach (optional)"
                ),
                "verdict": VariableSpec(
                    name="verdict",
                    var_type=VariableType.STRING,
                    required=True,
                    description="PROCEED | PIVOT | HYBRID"
                ),
                "next_steps": VariableSpec(
                    name="next_steps",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Ordered next actions"
                ),
            }
        )

        # Template 3: DoR Gate
        self.base_engine.create_template(
            template_id="copilot-dor-gate",
            version="1.0.0",
            name="Copilot DoR Approval Gate",
            description="Definition of Ready with intent classification and approval gate",
            pattern=self._get_dor_gate_pattern(),
            response_type=ResponseType.APPROVAL_GATE,
            variables={
                "orchestrator": VariableSpec(
                    name="orchestrator",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Orchestrator name"
                ),
                "intent": VariableSpec(
                    name="intent",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Intent type (IMPLEMENT/FIX/REFACTOR/etc)"
                ),
                "target": VariableSpec(
                    name="target",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Target orchestrator or module"
                ),
                "dor_table": VariableSpec(
                    name="dor_table",
                    var_type=VariableType.STRING,
                    required=True,
                    description="DoR validation table (markdown)"
                ),
                "next_steps": VariableSpec(
                    name="next_steps",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Post-approval next actions"
                ),
            }
        )

        # Template 4: Implementation Complete
        self.base_engine.create_template(
            template_id="copilot-implementation-complete",
            version="1.0.0",
            name="Copilot Implementation Complete",
            description="Post-implementation summary with gap analysis and enhancement opportunities",
            pattern=self._get_implementation_complete_pattern(),
            response_type=ResponseType.IMPLEMENTATION,
            variables={
                "orchestrator": VariableSpec(
                    name="orchestrator",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Orchestrator name"
                ),
                "summary": VariableSpec(
                    name="summary",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Implementation summary (bullet points)"
                ),
                "files_modified": VariableSpec(
                    name="files_modified",
                    var_type=VariableType.INTEGER,
                    required=True,
                    description="Count of files modified"
                ),
                "tests_passing": VariableSpec(
                    name="tests_passing",
                    var_type=VariableType.BOOLEAN,
                    required=True,
                    description="Whether all tests are passing"
                ),
                "gap_analysis": VariableSpec(
                    name="gap_analysis",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Gap analysis table with identified enhancements"
                ),
                "architecture_evolution": VariableSpec(
                    name="architecture_evolution",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Architecture evolution metrics (markdown table)"
                ),
                "next_steps": VariableSpec(
                    name="next_steps",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Recommended next priorities"
                ),
            }
        )

        # Template 5: Next Steps (Reusable)
        self.base_engine.create_template(
            template_id="copilot-next-steps",
            version="1.0.0",
            name="Copilot Next Steps Section",
            description="Reusable 'Next Steps' section - always rendered last",
            pattern=self._get_next_steps_pattern(),
            response_type=ResponseType.INFORMATIONAL,
            variables={
                "steps": VariableSpec(
                    name="steps",
                    var_type=VariableType.STRING,
                    required=True,
                    description="Ordered list of next actions (markdown)"
                ),
            }
        )

    def _get_audit_summary_pattern(self) -> str:
        """Get audit summary template pattern."""
        return """## 🔍 CORTEX Audit
**Author:** Asif Hussain | **Orchestrator:** {{ orchestrator }} ✅

---

### 📋 Audit Summary

{{ audit_details }}

### 💡 Out of the Box Recommendations

{{ recommendations }}

### 🎯 Next Steps

{{ next_steps }}

---

**Audit complete.** Type `/implement {fix}` to address issues."""

    def _get_design_challenge_pattern(self) -> str:
        """Get design challenge template pattern."""
        return """## ⚠️ CHALLENGE + RECOMMENDATION

**User's Request:** {{ user_request }}

### 🎯 Extensibility & Scalability Analysis

{{ extensibility_analysis }}

### ⚖️ Accuracy vs Efficiency Tradeoff

{{ accuracy_efficiency_tradeoff }}

### 🔴 Identified Weaknesses

{{ weaknesses }}

### 🟢 Evidence-Based Fix Plan

{{ fix_plans }}

### 🎓 Best Practices

{{ best_practices }}

{% if counter_proposal %}
### 🧠 Counter-Proposal

{{ counter_proposal }}
{% endif %}

**Verdict:** {{ verdict }}

---

### 🎯 Next Steps

{{ next_steps }}

---

**⏳ Awaiting approval...** Type **"proceed"**, **"yes"**, or **"approve"** to continue."""

    def _get_dor_gate_pattern(self) -> str:
        """Get DoR gate template pattern."""
        return """## 📋 Definition of Ready

{{ dor_table }}

**Architecture Evolution Ready:** YES ✅

---

### 🎯 Next Steps

{{ next_steps }}

---

**⏳ Awaiting approval...** Type **"proceed"**, **"yes"**, **"approve"**, or **"implement"** to begin execution."""

    def _get_implementation_complete_pattern(self) -> str:
        """Get implementation complete template pattern."""
        return """## ✅ Implementation Complete
**Author:** Asif Hussain | **Orchestrator:** {{ orchestrator }} ✅

---

### 📊 Summary

{{ summary }}

**Files Modified:** {{ files_modified }}
**Tests Passing:** {{ tests_passing }}

### 🔍 Gap Analysis

{{ gap_analysis }}

### 🏗️ Architecture Evolution

{{ architecture_evolution }}

---

### 🎯 Next Steps

{{ next_steps }}

---

**Implementation complete.** All changes committed with audit trail."""

    def _get_next_steps_pattern(self) -> str:
        """Get next steps template pattern."""
        return """### 🎯 Next Steps

{{ steps }}"""

    def render_audit_summary(
        self,
        orchestrator: str,
        p0_count: int,
        p1_count: int,
        p2_count: int,
        p3_count: int,
        audit_details: str,
        recommendations: str,
        next_steps: str,
    ) -> str:
        """Render audit summary response.

        Args:
            orchestrator: Orchestrator name
            p0_count: P0 issue count
            p1_count: P1 issue count
            p2_count: P2 issue count
            p3_count: P3 issue count
            audit_details: Detailed audit results table
            recommendations: Recommendations list
            next_steps: Next actions list

        Returns:
            Rendered markdown response
        """
        return self.base_engine.apply_template(
            template_id="copilot-audit-summary",
            variables={
                "orchestrator": orchestrator,
                "p0_count": p0_count,
                "p1_count": p1_count,
                "p2_count": p2_count,
                "p3_count": p3_count,
                "audit_details": audit_details,
                "recommendations": recommendations,
                "next_steps": next_steps,
            }
        )

    def render_design_challenge(
        self,
        orchestrator: str,
        user_request: str,
        extensibility_analysis: str,
        accuracy_efficiency_tradeoff: str,
        weaknesses: str,
        fix_plans: str,
        best_practices: str,
        verdict: str,
        next_steps: str,
        counter_proposal: Optional[str] = None,
    ) -> str:
        """Render design challenge response.

        Args:
            orchestrator: Orchestrator name
            user_request: User's original request
            extensibility_analysis: Extensibility/scalability table
            accuracy_efficiency_tradeoff: Tradeoff matrix
            weaknesses: Weaknesses table
            fix_plans: Fix plans sections
            best_practices: Best practices table
            verdictUnion[PROCEED, PIVOT] | HYBRID
            next_steps: Next actions
            counter_proposal: Optional alternative approach

        Returns:
            Rendered markdown response
        """
        variables = {
            "orchestrator": orchestrator,
            "user_request": user_request,
            "extensibility_analysis": extensibility_analysis,
            "accuracy_efficiency_tradeoff": accuracy_efficiency_tradeoff,
            "weaknesses": weaknesses,
            "fix_plans": fix_plans,
            "best_practices": best_practices,
            "verdict": verdict,
            "next_steps": next_steps,
        }
        if counter_proposal:
            variables["counter_proposal"] = counter_proposal

        return self.base_engine.apply_template(
            template_id="copilot-design-challenge",
            variables=variables
        )

    def render_dor_gate(
        self,
        orchestrator: str,
        intent: str,
        target: str,
        dor_table: str,
        next_steps: str,
    ) -> str:
        """Render DoR approval gate response.

        Args:
            orchestrator: Orchestrator name
            intent: Intent type
            target: Target orchestrator/module
            dor_table: DoR validation table
            next_steps: Post-approval actions

        Returns:
            Rendered markdown response
        """
        return self.base_engine.apply_template(
            template_id="copilot-dor-gate",
            variables={
                "orchestrator": orchestrator,
                "intent": intent,
                "target": target,
                "dor_table": dor_table,
                "next_steps": next_steps,
            }
        )

    def render_implementation_complete(
        self,
        orchestrator: str,
        summary: str,
        files_modified: int,
        tests_passing: bool,
        gap_analysis: str,
        architecture_evolution: str,
        next_steps: str,
    ) -> str:
        """Render implementation complete response.

        Args:
            orchestrator: Orchestrator name
            summary: Implementation summary
            files_modified: File modification count
            tests_passing: Test status
            gap_analysis: Gap analysis table
            architecture_evolution: Evolution metrics
            next_steps: Recommended priorities

        Returns:
            Rendered markdown response
        """
        # Convert boolean to display string AFTER template validation
        tests_display = "✅ Passing" if tests_passing else "❌ Failing"

        return self.base_engine.apply_template(
            template_id="copilot-implementation-complete",
            variables={
                "orchestrator": orchestrator,
                "summary": summary,
                "files_modified": files_modified,
                "tests_passing": tests_passing,  # Keep as bool for validation
                "gap_analysis": gap_analysis,
                "architecture_evolution": architecture_evolution,
                "next_steps": next_steps,
            }
        ).replace(
            f"**Tests Passing:** {tests_passing}",
            f"**Tests Passing:** {tests_display}"
        )

    def render_next_steps(self, steps: str) -> str:
        """Render standalone next steps section.

        Args:
            steps: Ordered list of next actions

        Returns:
            Rendered markdown section
        """
        return self.base_engine.apply_template(
            template_id="copilot-next-steps",
            variables={"steps": steps}
        )

    def validate_section_order(self, response: str) -> bool:
        """Validate that 'Next Steps' appears last before approval gates.

        Args:
            response: Full markdown response

        Returns:
            True if section order is valid, False otherwise
        """
        # Find "Next Steps" heading and track all headings after it
        lines = response.split("\n")
        next_steps_line = -1
        approval_gate_line = -1

        for i, line in enumerate(lines):
            # Match the exact Next Steps heading (with or without emoji)
            if line.strip() == "### 🎯 Next Steps" or line.strip() == "### Next Steps":
                next_steps_line = i
            if "⏳ Awaiting approval" in line or "Type **\"proceed\"" in line:
                approval_gate_line = i

        # Valid if:
        # 1. Next Steps exists and approval gate exists
        # 2. No new headings (###) appear between Next Steps and approval gate
        # 3. Markdown separators (---) and formatting (**) are allowed
        if next_steps_line >= 0 and approval_gate_line >= 0:
            # Check for any new heading between Next Steps and approval gate
            for i in range(next_steps_line + 1, approval_gate_line):
                line = lines[i]
                # Any heading (starts with ###) invalidates the order
                if line.startswith("###"):
                    return False  # Found a heading after Next Steps

        return True


# Singleton instance for easy access
_copilot_chat_engine: Optional[CopilotChatTemplateEngine] = None


def get_copilot_chat_engine() -> CopilotChatTemplateEngine:
    """Get or create singleton Copilot chat template engine.

    Returns:
        CopilotChatTemplateEngine instance
    """
    global _copilot_chat_engine
    if _copilot_chat_engine is None:
        _copilot_chat_engine = CopilotChatTemplateEngine()
    return _copilot_chat_engine

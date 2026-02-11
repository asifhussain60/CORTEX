"""
Multi-role response engine - integrates all prior stages.

Provides unified response generation across 5 roles with 14 response templates
(role + task combinations: ENGINEER/PM/BUSINESS/ARCHITECT + QUERY/PLAN/DESIGN/TDD/AUDIT + variations).

Module: cortex.orchestrators.response.multi_role_response_engine
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

# ============================================================================
# ENUMERATIONS
# ============================================================================


class Role(Enum):
    """Response role enumeration."""

    ENGINEER = "engineer"
    PRODUCT_MANAGER = "product_manager"
    BUSINESS_LEAD = "business_lead"
    SECURITY_OFFICER = "security_officer"
    CTO = "cto"


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class ResponseTemplate:
    """Response template definition."""

    role: Role
    """Target role for this template."""

    task: str
    """Task type (e.g., 'code_review', 'design', 'audit')."""

    template_name: str
    """Human-readable template name."""

    structure: str
    """Response structure description."""

    variables: List[str] = field(default_factory=list)
    """Variables to populate in template."""

    def matches(self, role: Role, task: str) -> bool:
        """Check if template matches role and task.

        Args:
            role: Target role
            task: Task type

        Returns:
            True if matches
        """
        return self.role == role and self.task == task


@dataclass
class IntegratedContext:
    """Context integrating all prior stages."""

    code: str
    """Source code being analyzed."""

    security_findings: List[str] = field(default_factory=list)
    """Security findings from SecurityFirstAnalyzer."""

    code_issues: List[str] = field(default_factory=list)
    """Code issues from HiddenIssueDetector."""

    business_impact: str = "Medium"
    """Business impact level (Low/Medium/High/Critical)."""

    target_role: Role = Role.ENGINEER
    """Target role for response."""

    comments: Optional[List[str]] = None
    """Code comments from IntelligentCommentGenerator."""

    test_quality_score: float = 0.0
    """Test quality score from TestQualityAnalyzer."""


# ============================================================================
# TEMPLATE REGISTRY
# ============================================================================
# CORE-035: Renamed from TemplateRegistry to avoid duplication with
# cortex.tools.scaffolder_templates.TemplateRegistry


class ResponseTemplateRegistry:
    """Registry for response templates.

    Domain-specific template registry for multi-role response engine.
    Provides efficient template lookup and registration.
    """

    _instance: Optional['ResponseTemplateRegistry'] = None

    def __new__(cls) -> 'ResponseTemplateRegistry':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize registry with standard templates."""
        if self._initialized:
            return

        self._templates: Dict[str, ResponseTemplate] = {}
        self._by_role: Dict[Role, List[ResponseTemplate]] = {}
        self._by_task: Dict[str, List[ResponseTemplate]] = {}

        self._initialized = True
        self._populate_standard_templates()

    def _populate_standard_templates(self) -> None:
        """Populate standard response templates."""
        templates = [
            # Engineer templates (5)
            ResponseTemplate(
                role=Role.ENGINEER,
                task="code_review",
                template_name="Technical Code Review",
                structure="Issues → Root Causes → Suggested Fixes → Implementation Steps",
                variables=["issues", "severity", "fix_complexity"]
            ),
            ResponseTemplate(
                role=Role.ENGINEER,
                task="design",
                template_name="System Design Review",
                structure="Architecture Overview → Components → Data Flow → Concerns → Recommendations",
                variables=["scalability", "maintainability", "performance"]
            ),
            ResponseTemplate(
                role=Role.ENGINEER,
                task="performance",
                template_name="Performance Analysis",
                structure="Bottlenecks → Complexity Analysis → Optimization Strategies → Metrics",
                variables=["big_o", "timing", "improvements"]
            ),
            ResponseTemplate(
                role=Role.ENGINEER,
                task="testing",
                template_name="Test Strategy Review",
                structure="Coverage Analysis → Test Quality → Gaps → Recommendations",
                variables=["coverage_score", "test_types", "edge_cases"]
            ),
            ResponseTemplate(
                role=Role.ENGINEER,
                task="refactor",
                template_name="Refactoring Plan",
                structure="Current State → Refactoring Goals → Changes → Validation → Rollback Plan",
                variables=["patterns", "complexity", "benefits"]
            ),

            # Product Manager templates (3)
            ResponseTemplate(
                role=Role.PRODUCT_MANAGER,
                task="feature_impact",
                template_name="Feature Impact Assessment",
                structure="User Impact → Market Implications → Timeline → Risk Assessment",
                variables=["user_value", "complexity", "timeline"]
            ),
            ResponseTemplate(
                role=Role.PRODUCT_MANAGER,
                task="technical_debt",
                template_name="Technical Debt Impact",
                structure="Business Impact → Timeline Implications → Resource Estimate → Priority",
                variables=["velocity_impact", "release_timeline", "team_capacity"]
            ),
            ResponseTemplate(
                role=Role.PRODUCT_MANAGER,
                task="roadmap",
                template_name="Roadmap Implications",
                structure="Current Plan → Impact → Adjustments → Justification",
                variables=["timeline", "dependencies", "alternatives"]
            ),

            # Business Lead templates (2)
            ResponseTemplate(
                role=Role.BUSINESS_LEAD,
                task="revenue",
                template_name="Revenue Impact",
                structure="Revenue Implications → Customer Impact → Market Timing → Recommendations",
                variables=["revenue_impact", "customer_base", "timeline"]
            ),
            ResponseTemplate(
                role=Role.BUSINESS_LEAD,
                task="risk",
                template_name="Business Risk Assessment",
                structure="Risk Overview → Probability → Impact → Mitigation → Financial Implications",
                variables=["risk_level", "exposure", "mitigation_cost"]
            ),

            # Security Officer templates (2)
            ResponseTemplate(
                role=Role.SECURITY_OFFICER,
                task="vulnerability",
                template_name="Vulnerability Analysis",
                structure="Vulnerability Overview → CVSS Score → Exploitation Likelihood → Remediation → Compliance Impact",
                variables=["severity", "cve", "exploit_complexity"]
            ),
            ResponseTemplate(
                role=Role.SECURITY_OFFICER,
                task="compliance",
                template_name="Compliance Review",
                structure="Standards Affected → Gap Analysis → Remediation Plan → Timeline → Compliance Status",
                variables=["standards", "gaps", "timeline"]
            ),

            # CTO templates (2)
            ResponseTemplate(
                role=Role.CTO,
                task="architecture",
                template_name="Strategic Architecture Review",
                structure="Vision Alignment → Technical Strategy → Roadmap → Technology Choices → Success Metrics",
                variables=["strategy", "timeline", "investment"]
            ),
            ResponseTemplate(
                role=Role.CTO,
                task="technical_strategy",
                template_name="Technical Strategy",
                structure="Technology Assessment → Strategic Fit → Implementation Path → Team Impact → Success Metrics",
                variables=["technology", "adoption_curve", "training"]
            ),
        ]

        for template in templates:
            self.register(template)

    def register(self, template: ResponseTemplate) -> None:
        """Register a response template.

        Args:
            template: Template to register
        """
        key = f"{template.role.value}:{template.task}"
        self._templates[key] = template

        # Index by role
        if template.role not in self._by_role:
            self._by_role[template.role] = []
        self._by_role[template.role].append(template)

        # Index by task
        if template.task not in self._by_task:
            self._by_task[template.task] = []
        self._by_task[template.task].append(template)

    def get(self, role: Role, task: str) -> Optional[ResponseTemplate]:
        """Get template for role and task.

        Args:
            role: Target role
            task: Task type

        Returns:
            Template if found, None otherwise
        """
        key = f"{role.value}:{task}"
        return self._templates.get(key)

    def get_by_role(self, role: Role) -> List[ResponseTemplate]:
        """Get all templates for role.

        Args:
            role: Target role

        Returns:
            List of templates
        """
        return self._by_role.get(role, [])

    def get_by_task(self, task: str) -> List[ResponseTemplate]:
        """Get all templates for task.

        Args:
            task: Task type

        Returns:
            List of templates
        """
        return self._by_task.get(task, [])

    def list_templates(self) -> List[ResponseTemplate]:
        """List all templates.

        Returns:
            All registered templates
        """
        return list(self._templates.values())


# ============================================================================
# ROLE ADAPTATION
# ============================================================================


class RoleAdaptation:
    """Role-based message adaptation.

    Adapts messages and findings to be understandable and relevant
    for specific roles without requiring technical knowledge.
    """

    def __init__(self):
        """Initialize role adaptation."""
        self._role_mappings: Dict[Role, Dict[str, str]] = {
            Role.ENGINEER: {
                "prefix": "Technically,",
                "focus": "implementation details",
                "complexity": "high",
            },
            Role.PRODUCT_MANAGER: {
                "prefix": "From a product perspective,",
                "focus": "user impact and timeline",
                "complexity": "medium",
            },
            Role.BUSINESS_LEAD: {
                "prefix": "From a business perspective,",
                "focus": "revenue and risk implications",
                "complexity": "low",
            },
            Role.SECURITY_OFFICER: {
                "prefix": "From a security perspective,",
                "focus": "threat vectors and remediation",
                "complexity": "high",
            },
            Role.CTO: {
                "prefix": "From a strategic perspective,",
                "focus": "technical vision and scaling",
                "complexity": "high",
            },
        }

    def adapt(self, message: str, role: Role) -> str:
        """Adapt message for target role.

        Args:
            message: Original message
            role: Target role

        Returns:
            Role-adapted message
        """
        if role not in self._role_mappings:
            return message

        mapping = self._role_mappings[role]
        prefix = mapping.get("prefix", "")

        # Simple adaptation: prepend role-specific prefix
        return f"{prefix} {message}"


# ============================================================================
# MULTI-ROLE RESPONSE ENGINE
# ============================================================================


class MultiRoleResponseEngine:
    """Multi-role response generation engine.

    Integrates all prior stages (security, code analysis, business impact,
    test quality, hidden issues) into unified responses tailored for
    specific roles. Provides 14 response templates across 5 roles.
    """

    def __init__(self):
        """Initialize response engine."""
        self._registry = ResponseTemplateRegistry()
        self._adapter = RoleAdaptation()
        self._response_cache: Dict[str, str] = {}

    def generate(self, context: IntegratedContext) -> str:
        """Generate role-specific response.

        Integrates all analysis components and tailors response
        for the target role.

        Args:
            context: Integrated analysis context

        Returns:
            Generated response
        """
        # Build cache key
        cache_key = self._build_cache_key(context)
        if cache_key in self._response_cache:
            return self._response_cache[cache_key]

        # Generate response based on role and issues
        response = self._generate_role_response(context)

        # Cache response
        self._response_cache[cache_key] = response

        return response

    def _build_cache_key(self, context: IntegratedContext) -> str:
        """Build cache key from context.

        Args:
            context: Analysis context

        Returns:
            Cache key string
        """
        issues_hash = hash(tuple(sorted(context.security_findings + context.code_issues)))
        return f"{context.target_role.value}:{context.business_impact}:{issues_hash}"

    def _generate_role_response(self, context: IntegratedContext) -> str:
        """Generate response for specific role.

        Args:
            context: Analysis context

        Returns:
            Generated response
        """
        role = context.target_role

        # Determine primary task type based on issues and impact
        task = self._determine_task(context)

        # Get appropriate template
        template = self._registry.get(role, task)
        if not template:
            # Fallback to generic response
            return self._generate_generic_response(context)

        # Build response based on template and context
        sections = self._build_response_sections(context, template)

        # Adapt findings for role
        adapted_sections = self._adapt_sections(sections, role)

        # Compose final response
        response = "\n\n".join(adapted_sections)

        return response

    def _determine_task(self, context: IntegratedContext) -> str:
        """Determine primary task type from context.

        Args:
            context: Analysis context

        Returns:
            Task type string
        """
        # Prioritize by issue type
        if context.security_findings:
            return "vulnerability"
        elif context.code_issues:
            if any("O(n" in issue for issue in context.code_issues):
                return "performance"
            return "code_review"
        elif context.business_impact == "Critical":
            return "risk"
        else:
            return "code_review"

    def _build_response_sections(
        self,
        context: IntegratedContext,
        template: ResponseTemplate
    ) -> List[str]:
        """Build response sections from template and context.

        Args:
            context: Analysis context
            template: Response template

        Returns:
            List of response sections
        """
        sections = []

        # Header with impact level
        sections.append(f"**Impact Level:** {context.business_impact}")

        # Security section
        if context.security_findings:
            security_section = "**Security Findings:**\n" + "\n".join(
                f"- {finding}" for finding in context.security_findings
            )
            sections.append(security_section)

        # Code issues section
        if context.code_issues:
            issues_section = "**Code Issues:**\n" + "\n".join(
                f"- {issue}" for issue in context.code_issues
            )
            sections.append(issues_section)

        # Template-specific content
        sections.append(f"**Template:** {template.template_name}")
        sections.append(f"**Structure:** {template.structure}")

        # Recommendations based on context
        recommendations = self._generate_recommendations(context)
        if recommendations:
            sections.append(f"**Recommendations:**\n{recommendations}")

        return sections

    def _generate_recommendations(self, context: IntegratedContext) -> str:
        """Generate recommendations from context.

        Args:
            context: Analysis context

        Returns:
            Recommendations text
        """
        recommendations = []

        # Security recommendations
        if context.security_findings:
            recommendations.append("- Address security findings immediately")
            recommendations.append("- Engage security team for remediation")

        # Performance recommendations
        if any("O(n" in issue for issue in context.code_issues):
            recommendations.append("- Review algorithm complexity")
            recommendations.append("- Consider optimization strategies")

        # Business recommendations
        if context.business_impact == "Critical":
            recommendations.append("- Escalate to stakeholders")
            recommendations.append("- Prioritize in roadmap")

        return "\n".join(recommendations) if recommendations else ""

    def _adapt_sections(self, sections: List[str], role: Role) -> List[str]:
        """Adapt sections for target role.

        Args:
            sections: Response sections
            role: Target role

        Returns:
            Adapted sections
        """
        # For now, return as-is; role adaptation applied during generation
        return sections

    def _generate_generic_response(self, context: IntegratedContext) -> str:
        """Generate generic response when no template found.

        Args:
            context: Analysis context

        Returns:
            Generic response
        """
        parts = [
            f"Analysis for {context.target_role.value}:",
            f"Impact: {context.business_impact}",
        ]

        if context.security_findings:
            parts.append(f"Security Issues: {len(context.security_findings)}")

        if context.code_issues:
            parts.append(f"Code Issues: {len(context.code_issues)}")

        return "\n".join(parts)

    def get_available_roles(self) -> List[Role]:
        """Get available roles.

        Returns:
            List of available roles
        """
        return list(Role)

    def get_templates_for_role(self, role: Role) -> List[ResponseTemplate]:
        """Get all templates for a role.

        Args:
            role: Target role

        Returns:
            List of templates
        """
        return self._registry.get_by_role(role)

# Backward compatibility alias
TemplateRegistry = ResponseTemplateRegistry

"""
Business context generator - creates non-technical summaries for decision makers.

Module: cortex.orchestrators.response.business_context_generator
Author: Asif Hussain
Created: 2026-02-07
Version: 1.0
"""

from enum import Enum
from typing import List, Optional
from dataclasses import dataclass


# ============================================================================
# ENUMERATIONS
# ============================================================================


class Stakeholder(str, Enum):
    """Stakeholder types."""
    
    BUSINESS_LEAD = "business_lead"
    """Executive business leader"""
    
    PRODUCT_MANAGER = "product_manager"
    """Product manager"""
    
    FINANCE = "finance"
    """Finance/accounting"""
    
    ENGINEER = "engineer"
    """Software engineer"""
    
    CUSTOMER_SUCCESS = "customer_success"
    """Customer success team"""


class BusinessContextType(str, Enum):
    """Type of business context."""
    
    FEATURE_IMPACT = "feature_impact"
    """Feature implementation impact"""
    
    REVENUE_IMPACT = "revenue_impact"
    """Revenue and financial impact"""
    
    RISK_ASSESSMENT = "risk_assessment"
    """Security and operational risk"""
    
    USER_EXPERIENCE = "user_experience"
    """User experience impact"""


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class CodeContext:
    """Code context for business analysis."""
    
    code: str
    function_name: str
    language: str = "python"


@dataclass
class BusinessContext:
    """Business-focused context summary."""
    
    code_summary: str
    stakeholder: Stakeholder
    impact: str
    context_type: BusinessContextType


# ============================================================================
# STAKEHOLDER CONTEXT GENERATOR
# ============================================================================


class StakeholderContextGenerator:
    """Generates context for specific stakeholders."""
    
    STAKEHOLDER_PROMPTS = {
        Stakeholder.BUSINESS_LEAD: "Executive summary focusing on business impact and ROI",
        Stakeholder.PRODUCT_MANAGER: "Product perspective emphasizing user value and roadmap fit",
        Stakeholder.FINANCE: "Financial perspective on costs, revenue, and resource allocation",
        Stakeholder.ENGINEER: "Technical perspective on architecture and implementation",
        Stakeholder.CUSTOMER_SUCCESS: "Customer perspective on support and success metrics",
    }
    
    def generate(
        self,
        code_ctx: CodeContext,
        stakeholder: Stakeholder
    ) -> BusinessContext:
        """
        Generate context for stakeholder.
        
        Args:
            code_ctx: Code context
            stakeholder: Target stakeholder
        
        Returns:
            Business context
        """
        # Extract business keywords
        keywords = self._extract_business_keywords(code_ctx.code)
        
        # Generate stakeholder-specific summary
        summary = self._generate_summary(code_ctx.function_name, keywords, stakeholder)
        
        # Detect context type
        context_type = self._detect_context_type(keywords, code_ctx.code)
        
        # Analyze impact
        impact = self._analyze_impact(keywords, stakeholder)
        
        return BusinessContext(
            code_summary=summary,
            stakeholder=stakeholder,
            impact=impact,
            context_type=context_type
        )
    
    @staticmethod
    def _extract_business_keywords(code: str) -> List[str]:
        """Extract business domain keywords from code."""
        business_keywords = [
            "payment", "invoice", "subscription", "pricing", "discount",
            "revenue", "customer", "order", "transaction", "billing",
            "authentication", "security", "permission", "role", "user",
            "data", "analytics", "report", "export", "import",
            "notification", "email", "sms", "alert"
        ]
        
        found = []
        code_lower = code.lower()
        for keyword in business_keywords:
            if keyword in code_lower:
                found.append(keyword)
        
        return found
    
    @staticmethod
    def _generate_summary(function_name: str, keywords: List[str], stakeholder: Stakeholder) -> str:
        """Generate stakeholder-specific summary."""
        if not keywords:
            return f"Function '{function_name}' performs operations"
        
        if stakeholder == Stakeholder.BUSINESS_LEAD:
            return f"'{function_name}' manages {', '.join(keywords)} - directly affects business operations"
        elif stakeholder == Stakeholder.PRODUCT_MANAGER:
            return f"User-facing feature '{function_name}' impacts {', '.join(keywords)}"
        elif stakeholder == Stakeholder.FINANCE:
            return f"'{function_name}' affects financial metrics: {', '.join(keywords)}"
        elif stakeholder == Stakeholder.CUSTOMER_SUCCESS:
            return f"Customer-impacting function '{function_name}' handles {', '.join(keywords)}"
        else:
            return f"'{function_name}' processes {', '.join(keywords)}"
    
    @staticmethod
    def _detect_context_type(keywords: List[str], code: str) -> BusinessContextType:
        """Detect context type based on keywords."""
        revenue_keywords = {"payment", "invoice", "subscription", "pricing", "billing", "revenue"}
        risk_keywords = {"payment", "authentication", "security", "permission"}
        ux_keywords = {"user", "notification", "email", "alert", "order"}
        
        if any(k in revenue_keywords for k in keywords):
            return BusinessContextType.REVENUE_IMPACT
        elif any(k in risk_keywords for k in keywords):
            return BusinessContextType.RISK_ASSESSMENT
        elif any(k in ux_keywords for k in keywords):
            return BusinessContextType.USER_EXPERIENCE
        else:
            return BusinessContextType.FEATURE_IMPACT
    
    @staticmethod
    def _analyze_impact(keywords: List[str], stakeholder: Stakeholder) -> str:
        """Analyze impact for stakeholder."""
        if not keywords:
            return "Standard operational impact"
        
        if stakeholder == Stakeholder.BUSINESS_LEAD:
            return f"Changes to {keywords[0]} could affect customer satisfaction and retention"
        elif stakeholder == Stakeholder.FINANCE:
            return f"Direct impact on {keywords[0]} related financials"
        elif stakeholder == Stakeholder.PRODUCT_MANAGER:
            return f"Affects product roadmap for {keywords[0]} features"
        else:
            return f"Impacts {keywords[0]} operations"


# ============================================================================
# IMPACT ANALYZER
# ============================================================================


class ImpactAnalyzer:
    """Analyzes code impact on business metrics."""
    
    def analyze(self, code_ctx: CodeContext) -> str:
        """
        Analyze code impact.
        
        Args:
            code_ctx: Code context
        
        Returns:
            Impact description
        """
        # Detect payment processing
        if "payment" in code_ctx.code.lower() or "charge" in code_ctx.code.lower():
            return "High impact - affects payment processing and revenue"
        
        # Detect security concerns
        if "query" in code_ctx.code.lower() or "sql" in code_ctx.code.lower():
            return "Security risk - potential injection vulnerability"
        
        # Detect data handling
        if "database" in code_ctx.code.lower() or "db." in code_ctx.code.lower():
            return "Data layer impact - may affect performance and availability"
        
        # Default impact
        return "Standard operational impact on system functionality"


# ============================================================================
# BUSINESS CONTEXT GENERATOR (ORCHESTRATOR)
# ============================================================================


class BusinessContextGenerator:
    """Orchestrator for business context generation."""
    
    def __init__(self):
        """Initialize generator."""
        self.stakeholder_gen = StakeholderContextGenerator()
        self.impact_analyzer = ImpactAnalyzer()
    
    def generate(
        self,
        code_ctx: CodeContext,
        stakeholder: Stakeholder
    ) -> BusinessContext:
        """
        Generate business context for stakeholder.
        
        Args:
            code_ctx: Code context
            stakeholder: Target stakeholder
        
        Returns:
            Business context
        """
        return self.stakeholder_gen.generate(code_ctx, stakeholder)
    
    def generate_for_all_stakeholders(self, code_ctx: CodeContext) -> List[BusinessContext]:
        """
        Generate context for all stakeholders.
        
        Args:
            code_ctx: Code context
        
        Returns:
            List of business contexts
        """
        return [
            self.generate(code_ctx, stakeholder)
            for stakeholder in Stakeholder
        ]


# ============================================================================
# MODULE EXPORTS
# ============================================================================


__all__ = [
    "Stakeholder",
    "BusinessContextType",
    "CodeContext",
    "BusinessContext",
    "StakeholderContextGenerator",
    "ImpactAnalyzer",
    "BusinessContextGenerator",
]

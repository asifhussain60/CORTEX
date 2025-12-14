"""
Market Intelligence Engine
Fetches domain knowledge from authoritative sources during planning analysis

Provides informed recommendations based on:
- Industry standards and best practices
- Market trends and upcoming changes
- Regulatory compliance requirements
- Technology alternatives and comparisons

Copyright © 2025 Asif Hussain. All rights reserved.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Set
from pathlib import Path
import hashlib
import json


class ResearchValue(Enum):
    """Research value classification based on ROI"""
    CRITICAL = "critical"  # 90-100: MUST research (compliance, security, financial)
    HIGH = "high"          # 70-89: Should research (established standards)
    MEDIUM = "medium"      # 40-69: Consider research (emerging tech)
    LOW = "low"            # 20-39: Skip research (niche tools, well-known)
    TRIVIAL = "trivial"    # 0-19: DO NOT research (internal tools, basic features)


@dataclass
class MarketInsight:
    """Single market intelligence finding"""
    category: str  # "standard", "trend", "risk", "alternative", "compliance"
    title: str
    description: str
    source_url: str
    source_authority: str  # "ISO", "W3C", "OWASP", "Microsoft Docs", etc.
    relevance_score: int  # 0-100
    recommendation: str
    implementation_impact: str  # "HIGH", "MEDIUM", "LOW"


@dataclass
class ResearchReport:
    """Comprehensive market intelligence report"""
    total_score: int  # 0-100
    value_tier: ResearchValue
    insights: List[MarketInsight]
    recommendations: List[str]
    guardrails: List[str]  # When NOT to surface this info
    authoritative_sources: List[str]


class MarketIntelligenceEngine:
    """
    Intelligent domain research system
    
    Research Value Scoring (0-100):
    1. Domain Criticality (0-30): Financial, healthcare, security, compliance
    2. Industry Maturity (0-25): Established standards vs emerging tech
    3. User Expertise Gap (0-20): Novice vs expert developer
    4. Compliance Requirements (0-15): Regulatory mandates
    5. Technology Complexity (0-10): Novel vs well-understood
    
    Guardrails:
    - Only surface insights with relevance ≥ 70 (HIGH/CRITICAL value)
    - Maximum 5 insights per response (avoid overwhelming)
    - Collapse into expandable section if > 3 insights
    - Skip research for internal tools, basic CRUD, trivial features
    
    Authoritative Source Whitelist:
    - Standards: ISO, W3C, IETF, IEEE, NIST, PCI DSS, HIPAA
    - Security: OWASP, CVE, NVD, CIS Benchmarks
    - Industry: Microsoft Docs, Google Cloud, AWS, MDN Web Docs
    - Academic: ACM Digital Library, IEEE Xplore, arXiv
    """
    
    # Critical domains requiring research
    CRITICAL_DOMAINS = {
        "payment": ["PCI DSS", "EMV", "tokenization", "ISO 8583"],
        "healthcare": ["HIPAA", "HL7", "FHIR", "PHI protection"],
        "security": ["OWASP Top 10", "CVE", "zero trust", "OAuth 2.0"],
        "financial": ["ISO 20022", "SWIFT", "accounting standards", "SOX"],
        "compliance": ["GDPR", "CCPA", "SOC 2", "audit trails"],
        "authentication": ["OAuth 2.0", "OpenID Connect", "SAML", "MFA"],
        "accessibility": ["WCAG 2.1", "Section 508", "ARIA", "screen readers"],
        "transit": ["ISO 14443", "MIFARE", "EMV contactless", "smart cards"],
    }
    
    # Authoritative source URLs (whitelist)
    AUTHORITATIVE_SOURCES = {
        "iso": ["iso.org", "standards.iso.org"],
        "w3c": ["w3.org", "w3c.github.io"],
        "ietf": ["ietf.org", "rfc-editor.org"],
        "owasp": ["owasp.org"],
        "nist": ["nist.gov", "csrc.nist.gov"],
        "pci": ["pcisecuritystandards.org"],
        "microsoft": ["docs.microsoft.com", "learn.microsoft.com"],
        "google": ["developers.google.com", "cloud.google.com"],
        "aws": ["docs.aws.amazon.com", "aws.amazon.com"],
        "mdn": ["developer.mozilla.org"],
        "ieee": ["ieee.org", "ieeexplore.ieee.org"],
    }
    
    # Trivial features that DON'T need research
    TRIVIAL_PATTERNS = [
        r"simple\s+crud",
        r"basic\s+form",
        r"display\s+list",
        r"show\s+details",
        r"internal\s+tool",
        r"admin\s+panel",
        r"logging\s+helper",
        r"utility\s+function",
    ]
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize market intelligence engine
        
        Args:
            cache_dir: Directory for caching research results (default: cortex-brain/cache/)
        """
        self.cache_dir = cache_dir or Path("cortex-brain/cache/market-intelligence")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def should_research(self, user_request: str, codebase_context: str) -> ResearchReport:
        """
        Determine if market research adds value for this request
        
        Args:
            user_request: User's feature request
            codebase_context: Existing codebase summary (from AST analysis)
            
        Returns:
            ResearchReport with value assessment
        """
        # Calculate research value score
        score_dimensions = {
            "criticality": self._score_domain_criticality(user_request),
            "maturity": self._score_industry_maturity(user_request),
            "expertise_gap": self._score_expertise_gap(user_request, codebase_context),
            "compliance": self._score_compliance_requirements(user_request),
            "complexity": self._score_technology_complexity(user_request),
        }
        
        total_score = sum(score_dimensions.values())
        value_tier = self._classify_research_value(total_score)
        
        # Check guardrails (should we skip research?)
        guardrails = self._check_guardrails(user_request, total_score)
        if guardrails:
            # Skip research, return empty report
            return ResearchReport(
                total_score=total_score,
                value_tier=value_tier,
                insights=[],
                recommendations=[],
                guardrails=guardrails,
                authoritative_sources=[],
            )
        
        # Research is valuable - generate report
        insights = self._fetch_insights(user_request, codebase_context, score_dimensions)
        recommendations = self._generate_recommendations(insights, user_request)
        sources = [insight.source_authority for insight in insights]
        
        return ResearchReport(
            total_score=total_score,
            value_tier=value_tier,
            insights=insights[:5],  # Max 5 insights
            recommendations=recommendations[:3],  # Max 3 recommendations
            guardrails=[],
            authoritative_sources=list(set(sources)),
        )
    
    def _score_domain_criticality(self, request: str) -> int:
        """Score based on domain criticality (0-30)"""
        request_lower = request.lower()
        
        # Check for critical domains
        for domain, keywords in self.CRITICAL_DOMAINS.items():
            if any(kw.lower() in request_lower for kw in keywords):
                if domain in ["payment", "healthcare", "security"]:
                    return 30  # Critical domains
                elif domain in ["financial", "compliance", "authentication"]:
                    return 25  # High-priority domains
                else:
                    return 20  # Important domains
        
        return 5  # Standard domain
    
    def _score_industry_maturity(self, request: str) -> int:
        """Score based on industry maturity (0-25)"""
        request_lower = request.lower()
        
        # Established standards = higher score (more research available)
        established_keywords = [
            "iso", "standard", "protocol", "specification",
            "payment", "oauth", "saml", "rest api", "graphql"
        ]
        
        if any(kw in request_lower for kw in established_keywords):
            return 25  # Mature industry with established standards
        
        # Emerging tech = medium score
        emerging_keywords = ["blockchain", "ai", "ml", "quantum"]
        if any(kw in request_lower for kw in emerging_keywords):
            return 15  # Emerging tech, fewer standards
        
        return 10  # Standard maturity
    
    def _score_expertise_gap(self, request: str, codebase: str) -> int:
        """Score based on user's expertise gap (0-20)"""
        # Heuristic: If codebase has similar patterns, user likely experienced
        # If new domain for codebase, higher research value
        
        request_domain_keywords = set(re.findall(r'\b\w{4,}\b', request.lower()))
        codebase_keywords = set(re.findall(r'\b\w{4,}\b', codebase.lower()))
        
        overlap = len(request_domain_keywords & codebase_keywords)
        total_keywords = len(request_domain_keywords)
        
        if total_keywords == 0:
            return 10
        
        overlap_ratio = overlap / total_keywords
        
        if overlap_ratio < 0.2:
            return 20  # High expertise gap - new domain for user
        elif overlap_ratio < 0.5:
            return 12  # Medium gap
        else:
            return 5  # Low gap - user familiar with domain
    
    def _score_compliance_requirements(self, request: str) -> int:
        """Score based on compliance requirements (0-15)"""
        request_lower = request.lower()
        
        compliance_keywords = [
            "gdpr", "hipaa", "pci", "sox", "compliance",
            "regulation", "audit", "privacy", "data protection"
        ]
        
        if any(kw in request_lower for kw in compliance_keywords):
            return 15
        
        return 0
    
    def _score_technology_complexity(self, request: str) -> int:
        """Score based on technology complexity (0-10)"""
        request_lower = request.lower()
        
        complex_keywords = [
            "distributed", "microservice", "real-time",
            "high availability", "scalability", "performance"
        ]
        
        complexity_count = sum(1 for kw in complex_keywords if kw in request_lower)
        return min(complexity_count * 3, 10)
    
    def _classify_research_value(self, score: int) -> ResearchValue:
        """Classify research value tier"""
        if score >= 90:
            return ResearchValue.CRITICAL
        elif score >= 70:
            return ResearchValue.HIGH
        elif score >= 40:
            return ResearchValue.MEDIUM
        elif score >= 20:
            return ResearchValue.LOW
        return ResearchValue.TRIVIAL
    
    def _check_guardrails(self, request: str, score: int) -> List[str]:
        """Check if research should be skipped (guardrails)"""
        guardrails = []
        
        # Guardrail 1: Trivial features
        request_lower = request.lower()
        for pattern in self.TRIVIAL_PATTERNS:
            if re.search(pattern, request_lower):
                guardrails.append(f"Trivial feature detected: '{pattern}' - skipping research")
        
        # Guardrail 2: Low value score
        if score < 70:
            guardrails.append(f"Research value too low ({score}/100) - threshold is 70")
        
        # Guardrail 3: Well-known implementation
        well_known = ["todo list", "blog", "contact form", "login page"]
        if any(kw in request_lower for kw in well_known):
            guardrails.append("Well-known implementation pattern - research not needed")
        
        return guardrails
    
    def _fetch_insights(
        self, request: str, codebase: str, dimensions: Dict[str, int]
    ) -> List[MarketInsight]:
        """
        Fetch market intelligence insights
        
        NOTE: In production, this would use the fetch_webpage tool
        For now, returns mock insights based on detected domains
        """
        insights = []
        request_lower = request.lower()
        
        # Detect domain and generate relevant insights
        for domain, keywords in self.CRITICAL_DOMAINS.items():
            if any(kw.lower() in request_lower for kw in keywords):
                # Generate domain-specific insights
                if domain == "transit":
                    insights.append(MarketInsight(
                        category="standard",
                        title="ISO 14443 - Contactless Smart Card Standard",
                        description="Transit cards typically use ISO 14443 Type A/B for contactless communication. MIFARE Classic (deprecated due to security) vs MIFARE DESFire EV3 (recommended).",
                        source_url="https://www.iso.org/standard/73596.html",
                        source_authority="ISO",
                        relevance_score=95,
                        recommendation="Implement MIFARE DESFire EV3 with AES-128 encryption. Avoid MIFARE Classic (cryptographically broken).",
                        implementation_impact="HIGH",
                    ))
                    insights.append(MarketInsight(
                        category="trend",
                        title="EMV Contactless Migration",
                        description="Transit industry moving to EMV open-loop payments (credit/debit cards directly). London, NYC already deployed. Reduces proprietary card costs.",
                        source_url="https://www.emvco.com/emv-technologies/contactless/",
                        source_authority="EMVCo",
                        relevance_score=85,
                        recommendation="Consider EMV contactless as alternative to proprietary cards. Lower infrastructure cost, wider acceptance.",
                        implementation_impact="HIGH",
                    ))
                
                elif domain == "payment":
                    insights.append(MarketInsight(
                        category="compliance",
                        title="PCI DSS 4.0 Requirements",
                        description="Latest PCI DSS 4.0 (March 2024) mandates encryption at rest, tokenization, and MFA for all cardholder data access.",
                        source_url="https://www.pcisecuritystandards.org/",
                        source_authority="PCI Security Standards Council",
                        relevance_score=100,
                        recommendation="Implement tokenization (not storing raw card data), AES-256 encryption, and audit logging. Use payment gateway APIs (Stripe, Adyen) to avoid PCI scope.",
                        implementation_impact="CRITICAL",
                    ))
                
                elif domain == "authentication":
                    insights.append(MarketInsight(
                        category="standard",
                        title="OAuth 2.0 + OIDC Best Practices",
                        description="Use Authorization Code flow with PKCE for SPAs. Avoid Implicit flow (deprecated). Store tokens in httpOnly cookies, not localStorage.",
                        source_url="https://oauth.net/2/",
                        source_authority="IETF OAuth Working Group",
                        relevance_score=90,
                        recommendation="Implement PKCE (RFC 7636) for SPAs. Use refresh token rotation. Set short access token TTLs (5-15 minutes).",
                        implementation_impact="HIGH",
                    ))
        
        return insights
    
    def _generate_recommendations(
        self, insights: List[MarketInsight], request: str
    ) -> List[str]:
        """Generate actionable recommendations based on insights"""
        recommendations = []
        
        # High-impact insights → recommendations
        critical_insights = [i for i in insights if i.implementation_impact == "CRITICAL"]
        high_insights = [i for i in insights if i.implementation_impact == "HIGH"]
        
        if critical_insights:
            recommendations.append(
                f"⚠️ CRITICAL: {len(critical_insights)} compliance/security requirements identified. "
                "Review these BEFORE implementation to avoid costly rework."
            )
        
        if high_insights:
            recommendations.append(
                f"💡 Consider {len(high_insights)} industry best practices for production-ready implementation."
            )
        
        # Standard-based recommendations
        standard_insights = [i for i in insights if i.category == "standard"]
        if standard_insights:
            standards = ", ".join(set(i.title.split("-")[0].strip() for i in standard_insights))
            recommendations.append(
                f"📋 Implement per {standards} for interoperability and future-proofing."
            )
        
        return recommendations


# CLI interface
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python market_intelligence_engine.py <user_request>")
        sys.exit(1)
    
    request = " ".join(sys.argv[1:])
    engine = MarketIntelligenceEngine()
    
    # Mock codebase context
    codebase = "Existing: REST API, PostgreSQL, authentication with JWT"
    
    report = engine.should_research(request, codebase)
    
    print(f"\n{'=' * 80}")
    print(f"MARKET INTELLIGENCE REPORT")
    print(f"{'=' * 80}")
    print(f"\n📊 RESEARCH VALUE: {report.total_score}/100 ({report.value_tier.value.upper()})")
    
    if report.guardrails:
        print(f"\n⏸️  RESEARCH SKIPPED:")
        for guardrail in report.guardrails:
            print(f"  • {guardrail}")
    else:
        print(f"\n💡 KEY INSIGHTS:")
        for i, insight in enumerate(report.insights, 1):
            print(f"\n  {i}. {insight.title}")
            print(f"     Source: {insight.source_authority} ({insight.relevance_score}% relevant)")
            print(f"     {insight.description}")
            print(f"     ➜ {insight.recommendation}")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        for rec in report.recommendations:
            print(f"  {rec}")
        
        print(f"\n📚 AUTHORITATIVE SOURCES:")
        for source in report.authoritative_sources:
            print(f"  • {source}")
    
    print(f"\n{'=' * 80}\n")

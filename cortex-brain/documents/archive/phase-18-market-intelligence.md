# Phase 18: Market Intelligence Engine

**Status:** ✅ Implementation Complete | 🟡 Integration Pending  
**Complexity:** HIGH  
**Estimated Time:** 4 hours (3h implementation + 1h integration)  
**Actual Time:** 2.5h (implementation complete ahead of schedule)  
**Author:** Asif Hussain  
**Last Updated:** 2024-12-14  

---

## 📋 Overview

**Purpose:** Enhance Planning Orchestrator with domain research capability - fetch industry standards, best practices, and compliance requirements from authoritative sources during analysis phase to provide informed recommendations.

**Problem Statement:**
- Planning System relies solely on AST codebase analysis
- Missing industry context: security standards (OWASP), compliance requirements (PCI DSS, GDPR), architectural patterns (Martin Fowler, Clean Architecture)
- Risk of reinventing the wheel without researching proven solutions
- Users lack domain expertise in critical areas (payment processing, authentication, healthcare compliance)

**Solution:**
- 5-dimensional research value scoring (0-100): determines if web research adds value vs overhead
- Authoritative source whitelist: ISO, W3C, IETF, OWASP, NIST, PCI DSS, Microsoft/Google/AWS docs
- Guardrails: Skip research if score < 70, trivial features, well-known implementations
- Conditional response template section: Only show insights when relevant (avoid information overload)
- Integration with Planning Orchestrator analysis phase via `fetch_webpage` tool

---

## 🎯 Success Criteria

**Implementation Complete (✅):**
1. ✅ `market_intelligence_engine.py` with 5-dimensional scoring system
2. ✅ `ResearchReport` dataclass with insights, recommendations, authoritative sources
3. ✅ Guardrails logic (`_check_guardrails()`) with skip patterns
4. ✅ Mock insights for 3 critical domains (transit, payment, authentication)
5. ✅ CLI interface for standalone testing (`python market_intelligence_engine.py "transit card system"`)
6. ✅ Authoritative source whitelist (11 source categories)

**Integration Pending (🟡):**
1. 🟡 Update Planning Orchestrator to call `should_research()` during analysis
2. 🟡 Pass `fetch_webpage` tool to engine (replace mock implementation)
3. 🟡 Populate response template `market_insights` context variable
4. 🟡 Add conditional rendering logic to response templates (tier 3+)
5. 🟡 Create cache layer (5-day TTL) to avoid redundant web fetches

---

## 🏗️ Architecture

### Research Value Scoring (5 Dimensions)

```yaml
dimensions:
  domain_criticality: 30 points  # Security, financial, compliance domains
  domain_maturity: 25 points     # Emerging tech, evolving standards
  expertise_gap: 20 points       # User lacks domain knowledge
  compliance_needs: 15 points    # Regulatory requirements (PCI, GDPR, HIPAA)
  domain_complexity: 10 points   # Integration complexity, edge cases

value_tiers:
  CRITICAL: 90-100  # Always research, high user value
  HIGH: 70-89       # Research recommended, moderate value
  MEDIUM: 40-69     # Optional research, some value
  LOW: 20-39        # Skip research, low value
  TRIVIAL: 0-19     # Never research, waste of time

threshold: 70  # Minimum score to trigger research
```

### Authoritative Source Whitelist

```yaml
authoritative_sources:
  standards_bodies:
    - iso.org          # ISO standards (14443, 27001, etc.)
    - w3.org           # Web standards (WCAG, HTML5, CSS)
    - ietf.org         # Internet standards (RFC, OAuth, JWT)
    - ieee.org         # Technical standards
  
  security_compliance:
    - owasp.org        # Security best practices (Top 10, ASVS)
    - nist.gov         # Security frameworks (Cybersecurity Framework)
    - pcisecuritystandards.org  # Payment security (PCI DSS 4.0)
  
  cloud_providers:
    - docs.microsoft.com        # Azure documentation
    - developers.google.com     # Google Cloud, Android, Firebase
    - docs.aws.amazon.com       # AWS best practices
  
  developer_resources:
    - developer.mozilla.org     # MDN Web Docs
```

### Guardrails (Skip Logic)

```yaml
skip_conditions:
  low_value_score: research_value_score < 70
  
  trivial_features:
    - 'simple crud'
    - 'basic form'
    - 'internal tool'
    - 'prototype'
  
  well_known_implementations:
    - 'todo list'
    - 'blog'
    - 'contact form'
    - 'landing page'
  
  user_expertise:
    - User has 10+ years domain experience
    - User explicitly says "I know the standards"
```

---

## 📂 File Structure

```
src/operations/modules/intelligence/
├── market_intelligence_engine.py  ✅ (550+ lines, complete)
└── __init__.py

cortex-brain/
├── response-base-components.yaml  ✅ (added section_market_insights)
└── documents/planning/cortex-evolution-v3.9/
    └── phase-18-market-intelligence.md  ✅ (this file)
```

---

## 🔧 Implementation Details

### MarketIntelligenceEngine Class

```python
class MarketIntelligenceEngine:
    """
    Fetch domain knowledge from authoritative sources during planning analysis.
    
    Purpose: Provide informed recommendations based on industry standards, 
    not just AST codebase analysis.
    
    Integration: Planning Orchestrator analysis phase (Phase 03)
    """
    
    def should_research(self, user_request: str, codebase_summary: str) -> ResearchReport:
        """
        Determine if web research adds value for this request.
        
        Args:
            user_request: User's feature request
            codebase_summary: AST analysis output
        
        Returns:
            ResearchReport with insights if score >= 70, else empty report
        """
        # 1. Score research value (5 dimensions)
        score = self._calculate_research_value(user_request, codebase_summary)
        
        # 2. Check guardrails (skip logic)
        guardrails = self._check_guardrails(user_request, score)
        if guardrails:
            return ResearchReport(skip_reason=guardrails)
        
        # 3. Fetch insights from authoritative sources
        insights = self._fetch_insights(user_request)
        
        return ResearchReport(
            total_score=score,
            insights=insights,
            authoritative_sources=[...],
            recommendations=[...]
        )
```

### Research Value Scoring Logic

```python
def _calculate_research_value(self, user_request: str, codebase_summary: str) -> int:
    """5-dimensional scoring (0-100)"""
    
    # Dimension 1: Domain Criticality (30 points)
    criticality_score = self._score_domain_criticality(user_request)
    # Detects: payment, healthcare, security, financial, compliance, 
    #          authentication, accessibility, transit
    
    # Dimension 2: Domain Maturity (25 points)
    maturity_score = self._score_domain_maturity(user_request)
    # Detects: emerging tech, evolving standards, new frameworks
    
    # Dimension 3: Expertise Gap (20 points)
    expertise_score = self._score_expertise_gap(user_request, codebase_summary)
    # Detects: missing patterns, no similar implementations in codebase
    
    # Dimension 4: Compliance Needs (15 points)
    compliance_score = self._score_compliance_needs(user_request)
    # Detects: PCI, GDPR, HIPAA, SOC2, ISO 27001 keywords
    
    # Dimension 5: Domain Complexity (10 points)
    complexity_score = self._score_domain_complexity(user_request)
    # Detects: integration complexity, edge cases, security considerations
    
    return criticality_score + maturity_score + expertise_score + compliance_score + complexity_score
```

### Guardrails Implementation

```python
def _check_guardrails(self, user_request: str, score: int) -> Optional[str]:
    """
    Skip research if:
    - Score < 70 (low value)
    - Trivial feature patterns detected
    - Well-known implementation patterns detected
    
    Returns:
        Skip reason if guardrails triggered, else None
    """
    if score < 70:
        return f"Research value score too low ({score}/100)"
    
    trivial_patterns = [r'simple\s+crud', r'basic\s+form', r'internal\s+tool']
    for pattern in trivial_patterns:
        if re.search(pattern, user_request, re.IGNORECASE):
            return f"Trivial feature detected: {pattern}"
    
    well_known = ['todo list', 'blog', 'contact form', 'landing page']
    for impl in well_known:
        if impl in user_request.lower():
            return f"Well-known implementation: {impl}"
    
    return None  # No guardrails triggered, proceed with research
```

---

## 🧪 Mock Insights (3 Critical Domains)

### Transit Card System (Score: 95/100)

```yaml
domain: transit
research_value: 95 (CRITICAL)
insights:
  - title: "ISO 14443 Contactless Smart Cards"
    relevance: 100
    source: iso.org
    description: |
      ISO 14443 defines proximity cards (NFC) used in 80% of transit systems worldwide.
      Part A: RF interface, Part B: initialization/anticollision, Part C: transmission protocol.
    recommendation: |
      Implement ISO 14443 Type A (most common) with MIFARE DESFire EV3 for security.
      Use EMV contactless migration path if integrating payment cards.
```

### Payment Processing (Score: 100/100)

```yaml
domain: payment
research_value: 100 (CRITICAL)
insights:
  - title: "PCI DSS 4.0 Tokenization Requirements"
    relevance: 100
    source: pcisecuritystandards.org
    description: |
      PCI DSS 4.0 (March 2024) mandates tokenization for stored card data.
      Requirement 3.3: Mask PAN when displayed, use tokens for storage.
    recommendation: |
      Use payment gateway tokenization (Stripe, Braintree) instead of storing raw card data.
      Never log full PAN, use first 6 + last 4 digits only.
```

### Authentication System (Score: 88/100)

```yaml
domain: authentication
research_value: 88 (HIGH)
insights:
  - title: "OAuth 2.0 + OpenID Connect with PKCE"
    relevance: 95
    source: ietf.org (RFC 6749, RFC 7636)
    description: |
      OAuth 2.0 Authorization Code flow with PKCE (Proof Key for Code Exchange)
      prevents authorization code interception attacks in mobile/SPA apps.
    recommendation: |
      Implement OAuth 2.0 with PKCE for mobile/SPA, standard flow for server-side.
      Use OpenID Connect (OIDC) for identity layer, JWT for tokens.
```

---

## 🔗 Integration Points

### Planning Orchestrator (Phase 03)

```python
# In planning_orchestrator.py analysis phase:

from operations.modules.intelligence.market_intelligence_engine import MarketIntelligenceEngine

class PlanningOrchestrator:
    def analyze(self, user_request: str):
        # Existing AST analysis
        codebase_summary = self.ast_analyzer.analyze()
        
        # NEW: Market intelligence research
        market_intel = MarketIntelligenceEngine()
        research_report = market_intel.should_research(user_request, codebase_summary)
        
        # Populate response template context
        context = {
            "market_intelligence_enabled": True,
            "research_value_score": research_report.total_score,
            "research_value_tier": research_report.value_tier,
            "market_insights": research_report.insights,
            "has_guardrails": research_report.skip_reason is not None,
            "guardrail_reason": research_report.skip_reason
        }
        
        return self.render_response(template="tier_3_documented", context=context)
```

### Response Template Rendering

```yaml
# In tier_3_documented template:

sections:
  - header_standard
  - section_understanding
  - section_challenge
  - section_market_insights  # NEW: Conditional section (only if score >= 70)
  - section_response
  - section_request_echo
  - section_next_steps

conditional_sections:
  section_market_insights:
    condition: "research_value_score >= 70 and market_insights.length > 0"
    max_insights: 5  # Prevent information overload
    collapsible: true  # Use <details> if > 3 insights
```

---

## 📊 Metrics & Success Tracking

### Key Metrics

```yaml
implementation_metrics:
  lines_of_code: 550+
  functions: 12
  test_coverage: 0% (Phase 05 TDD Orchestrator will add tests)
  complexity: HIGH (5-dimensional scoring + guardrails)
  dependencies: 0 (pure Python stdlib, will use fetch_webpage tool)

value_metrics:
  research_accuracy: TBD (measure after 50 real-world uses)
  false_positive_rate: TBD (research triggered but not useful)
  false_negative_rate: TBD (research skipped but would have been useful)
  user_feedback_score: TBD (1-5 scale, "was this helpful?")

performance_metrics:
  avg_research_time: TBD (web fetch latency)
  cache_hit_rate: TBD (5-day TTL cache)
  guardrail_effectiveness: TBD (% of trivial features correctly skipped)
```

### Success Criteria

```yaml
phase_complete_when:
  - ✅ Implementation: market_intelligence_engine.py functional
  - 🟡 Integration: Planning Orchestrator calls engine during analysis
  - 🟡 Templates: Response templates render market_insights section
  - 🟡 Cache: 5-day TTL cache implemented (avoid redundant fetches)
  - 🟡 Tests: 80%+ coverage with TDD Orchestrator (Phase 05)
  - 🟡 Metrics: Baseline metrics collected (50+ real-world uses)
```

---

## 🚀 Next Steps

### Immediate (Phase 02 → Phase 18 Integration)

1. **Update Planning Orchestrator** (30 minutes)
   - Import `MarketIntelligenceEngine`
   - Call `should_research()` after AST analysis
   - Populate response template context

2. **Pass `fetch_webpage` Tool** (15 minutes)
   - Replace mock `_fetch_insights()` with real web fetches
   - Use authoritative source whitelist for URL filtering
   - Handle fetch errors gracefully (timeout, 404, SSL)

3. **Implement Cache Layer** (45 minutes)
   - Use SQLite for caching (similar to conversation context)
   - Schema: `(domain TEXT, request_hash TEXT, insights JSON, fetched_at TIMESTAMP)`
   - 5-day TTL: Skip research if cache hit < 5 days old

### Phase 05 (TDD Orchestrator Integration)

1. **Add Test Suite** (2 hours)
   - Test scoring logic: `test_score_domain_criticality()`
   - Test guardrails: `test_check_guardrails_trivial_feature()`
   - Test mock insights: `test_fetch_insights_transit_domain()`
   - Test cache layer: `test_cache_hit_skips_research()`

2. **Add Test Value Scoring** (30 minutes)
   - Use `TestValueScorer` to determine if tests add value
   - Expected score: 85/100 (HIGH tier) - critical domain detection logic
   - Generate unit tests for all 5 scoring dimensions

### Phase 16 (Integration & Validation)

1. **End-to-End Testing** (1 hour)
   - Test real-world scenarios: transit card, payment processing, authentication
   - Validate authoritative sources: ISO, OWASP, PCI DSS URLs reachable
   - Measure latency: Web fetch + cache lookup + rendering

2. **User Feedback Loop** (ongoing)
   - Add "Was this helpful?" prompt after market intelligence section
   - Track false positives (research not useful) and false negatives (research missed)
   - Refine scoring weights based on feedback

---

## 🎓 Authoritative Source Citations

**Research Value Scoring Methodology:**
- Kent Beck: "Make it work, make it right, make it fast" - Don't over-engineer (research only when needed)
- Martin Fowler: "YAGNI (You Aren't Gonna Need It)" - Skip research for well-known patterns

**Authoritative Source Selection:**
- ISO: International standards (14443 contactless, 27001 security)
- W3C: Web standards (WCAG accessibility, HTML5, CSS)
- IETF: Internet standards (OAuth RFC 6749, JWT RFC 7519)
- OWASP: Security best practices (Top 10, ASVS)
- NIST: Security frameworks (Cybersecurity Framework)
- PCI DSS: Payment security (PCI DSS 4.0)

**Guardrails Approach:**
- Sandi Metz: "Duplication is cheaper than wrong abstraction" - Skip research for trivial features
- Robert C. Martin: "The first rule of functions is that they should be small" - Don't overwhelm users

---

## 📝 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-12-14 | Asif Hussain | Initial implementation complete - 5-dimensional scoring, guardrails, mock insights |
| 1.1 | 2024-12-14 | Asif Hussain | Added to master plan as Phase 18, created design document |

---

**Status:** ✅ Implementation Complete | Next: Integration with Planning Orchestrator (Phase 02)

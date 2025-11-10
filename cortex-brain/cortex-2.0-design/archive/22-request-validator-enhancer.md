# CORTEX 2.0: Request Validator & Enhancer

**Document:** 22-request-validator-enhancer.md  
**Version:** 2.0.0-alpha  
**Created:** 2025-11-07  
**Status:** Design Phase  
**Component:** Entry Point Enhancement

---

## 🎯 Overview

**Purpose:** Add an intelligent validation and enhancement layer at the CORTEX entry point that reviews user requests holistically against conversation history, previous work, and knowledge patterns to challenge potentially problematic requests and suggest improvements BEFORE work begins.

**Key Principle:** "Challenge Early, Save Later" - Better to spend 30 seconds reviewing a request than 30 minutes implementing the wrong thing.

---

## 🧠 Conceptual Architecture

### The Challenge/Enhance Flow

```
User Request
    ↓
Entry Point (cortex_entry.py)
    ↓
[NEW] Request Validator & Enhancer ← Tier 1 (Recent Context)
    ↓                               ← Tier 2 (Patterns)
    ↓                               ← Tier 3 (Project Health)
    ↓
Three Analysis Paths (Parallel):
    ├─ Viability Analysis (Can this work?)
    ├─ Historical Analysis (Have we done this before?)
    └─ Enhancement Analysis (How can we improve it?)
    ↓
Synthesis & Decision
    ↓
Challenge OR Enhance OR Both
    ↓
Present to User
    ↓
User Decision (Accept/Modify/Override)
    ↓
[Original Flow] Router → Agent(s) → Execution
```

---

## 📊 Component Design

### 1. Request Validator & Enhancer (New Component)

**File:** `src/entry_point/request_validator.py`

**Responsibilities:**
- Extract request intent and scope
- Query all 3 tiers for relevant context
- Perform viability, historical, and enhancement analysis
- Generate challenges or enhancement suggestions
- Present synthesized recommendations
- Track validation decisions for learning

**Integration Point:** Between `RequestParser` and `IntentRouter` in entry point flow

### 2. Three Analysis Engines

#### A. Viability Analyzer
**Purpose:** Determine if request is achievable, sensible, and safe

**Checks:**
- **Scope Feasibility:** Too large? Too vague? Conflicting requirements?
- **Technical Viability:** Does codebase support this? Are dependencies available?
- **Risk Assessment:** High-risk files? Breaking changes? Architectural impact?
- **Definition of Ready:** Clear requirements? Testable? Bounded scope?

**Data Sources:**
- Tier 2: Technical constraints, architectural patterns
- Tier 3: File stability, change patterns, velocity trends
- Tier 0: Rule violations (TDD skip requests, etc.)

**Example Challenges:**
```
⚠️ VIABILITY CONCERN: Scope Too Large

Request: "Add authentication, payment processing, and multi-language support"

Issues:
  - 3 major features in one request (violates bounded scope)
  - Estimated: 40-60 hours total
  - No clear acceptance criteria
  - High interdependency risk

Recommendation: Break into 3 separate features
  1. Authentication (8-12 hours) ✅ START HERE
  2. Payment processing (15-20 hours)
  3. Multi-language (12-15 hours)

Accept phased approach? [Y/n]
```

#### B. Historical Analyzer
**Purpose:** Learn from past successes and failures

**Checks:**
- **Similar Patterns:** Have we done something similar?
- **Success/Failure History:** How did similar requests turn out?
- **Workflow Reuse:** Can we reuse proven workflows?
- **Anti-Pattern Detection:** Have we tried and failed this before?

**Data Sources:**
- Tier 1: Last 20 conversations, recent outcomes
- Tier 2: Pattern library, workflow templates, anti-patterns
- Tier 3: Historical metrics, commit success rates

**Example Enhancements:**
```
✅ HISTORICAL INSIGHT: Similar Pattern Found

Request: "Add PDF export for receipts"

Similar Work:
  - Invoice PDF export (3 weeks ago) - Success ✅
  - Report PDF export (2 months ago) - Success ✅

Proven Workflow:
  1. Service layer generation (tested first)
  2. API endpoint creation
  3. UI component integration
  4. Average time: 4.5 hours
  5. Success rate: 95%

Suggestions:
  - Reuse PDFGenerationService pattern
  - Follow invoice export test structure
  - Use same library (PdfSharp)
  - Estimated: 4-5 hours (based on history)

Apply proven pattern? [Y/n]
```

#### C. Enhancement Analyzer
**Purpose:** Suggest improvements to make request better

**Checks:**
- **Completeness:** Missing edge cases? Error handling? Accessibility?
- **Best Practices:** TDD approach? SOLID compliance? Performance considerations?
- **Quality Enhancements:** Additional tests? Documentation? Examples?
- **User Experience:** Is there a better UX approach?

**Data Sources:**
- Tier 0: Rules and principles (TDD, DoR/DoD, SOLID)
- Tier 2: Best practice patterns
- Tier 3: Quality metrics, test coverage trends

**Example Enhancements:**
```
💡 ENHANCEMENT SUGGESTIONS

Request: "Add a delete button to the user profile page"

Your Request is Viable ✅

Suggested Enhancements:
  1. Confirmation Dialog (Recommended) ⭐
     - Prevent accidental deletions
     - Industry standard UX pattern
     - +5 min implementation

  2. Soft Delete with Recovery (Best Practice) ⭐⭐
     - Keep data for 30 days (recovery window)
     - GDPR compliant approach
     - +15 min implementation

  3. Audit Trail (Enterprise Grade) ⭐⭐⭐
     - Track who deleted and when
     - Meets compliance requirements
     - +10 min implementation

  4. Element ID for Testing (Required) ✅
     - Enable Playwright selector: #user-delete-btn
     - Prevent test fragility
     - +1 min implementation

Total Enhanced Implementation: 31 minutes
Original Implementation: 15 minutes
Value Gained: 3x quality improvement

Accept all enhancements? [Y/n/Select]
```

### 3. Synthesis Engine

**Purpose:** Combine analysis results into coherent recommendation

**Algorithm:**
```python
def synthesize_recommendation(viability, historical, enhancement):
    """
    Combine three analysis results into single recommendation.
    
    Priority:
    1. CRITICAL viability issues → CHALLENGE (block)
    2. HIGH viability issues + good alternatives → CHALLENGE (suggest)
    3. Historical success pattern → ENHANCE (reuse)
    4. Enhancement opportunities → ENHANCE (improve)
    5. No issues → APPROVE (proceed)
    """
    
    if viability.has_critical_issues:
        return Challenge(
            type="BLOCKING",
            message=viability.issues,
            alternatives=viability.alternatives,
            recommendation="Accept alternative"
        )
    
    if viability.has_high_issues and historical.has_better_approach:
        return Challenge(
            type="ADVISORY",
            message=viability.issues,
            alternatives=[historical.better_approach],
            recommendation="Consider proven alternative"
        )
    
    enhancements = []
    if historical.has_reusable_pattern:
        enhancements.append(historical.pattern_reuse)
    
    if enhancement.has_suggestions:
        enhancements.extend(enhancement.suggestions)
    
    if enhancements:
        return Enhancement(
            type="SUGGESTIONS",
            enhancements=enhancements,
            estimated_value=calculate_value(enhancements),
            recommendation="Accept valuable enhancements"
        )
    
    return Approval(
        message="Request looks good!",
        confidence=calculate_confidence(viability, historical, enhancement)
    )
```

---

## 🔧 Technical Implementation

### File Structure

```
src/entry_point/
├── cortex_entry.py (MODIFIED - add validator call)
├── request_parser.py (EXISTING)
├── request_validator.py (NEW)
│   ├── RequestValidator (main class)
│   ├── ViabilityAnalyzer
│   ├── HistoricalAnalyzer
│   └── EnhancementAnalyzer
├── validation_presenter.py (NEW - format challenges/enhancements)
└── validation_tracker.py (NEW - track user decisions)
```

### Integration with Entry Point

**Modified:** `src/entry_point/cortex_entry.py`

```python
class CortexEntry:
    def __init__(self, brain_path: Optional[str] = None, ...):
        # ... existing init ...
        
        # NEW: Initialize validator
        self.validator = RequestValidator(
            tier1_api=self.tier1,
            tier2_kg=self.tier2,
            tier3_context=self.tier3
        )
    
    def process(self, user_message: str, ...):
        try:
            # Step 1: Parse request (EXISTING)
            request = self.parser.parse(user_message, ...)
            
            # Step 2: Validate & Enhance (NEW)
            validation_result = self.validator.validate_and_enhance(
                request=request,
                conversation_id=conversation_id
            )
            
            # Step 3: Present to user if needed (NEW)
            if validation_result.requires_user_input:
                user_decision = self._present_validation(validation_result)
                
                if user_decision.action == "ABORT":
                    return self.formatter.format_abort(user_decision)
                
                elif user_decision.action == "MODIFY":
                    # User provided modified request
                    request = self.parser.parse(
                        user_decision.modified_request
                    )
                    # Re-validate (with flag to skip same checks)
                    validation_result = self.validator.validate_and_enhance(
                        request=request,
                        conversation_id=conversation_id,
                        skip_checks=user_decision.accepted_checks
                    )
                
                elif user_decision.action == "OVERRIDE":
                    # Log override and proceed
                    self.validator.log_override(
                        validation_result,
                        user_decision.justification
                    )
                
                # User accepted or overrode - continue
            
            # Step 4: Apply accepted enhancements (NEW)
            if validation_result.has_enhancements:
                request = self._apply_enhancements(
                    request,
                    validation_result.accepted_enhancements
                )
            
            # Step 5: Route to agent (EXISTING - continues as before)
            response = self.router.execute(request)
            
            # ... rest of existing flow ...
```

### Core Validator Implementation

**New File:** `src/entry_point/request_validator.py`

```python
"""
Request Validator & Enhancer

Reviews user requests holistically and suggests improvements
before work begins. Balances accuracy with efficiency.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import time

from ..tier1.tier1_api import Tier1API
from ..tier2.knowledge_graph import KnowledgeGraph
from ..tier3.context_intelligence import ContextIntelligence
from ..cortex_agents.base_agent import AgentRequest


class ValidationDecision(Enum):
    """Validation decision types."""
    APPROVE = "approve"          # No issues, proceed
    CHALLENGE = "challenge"      # Block with alternatives
    ENHANCE = "enhance"          # Suggest improvements
    ADVISE = "advise"           # Warn but allow


@dataclass
class ValidationResult:
    """Result of validation analysis."""
    decision: ValidationDecision
    confidence: float
    
    # Viability
    viability_score: float
    viability_issues: List[Dict[str, Any]]
    viability_risks: List[str]
    
    # Historical
    similar_patterns: List[Dict[str, Any]]
    success_rate: Optional[float]
    recommended_workflow: Optional[str]
    
    # Enhancements
    enhancements: List[Dict[str, Any]]
    estimated_value: float  # Time saved or quality gained
    
    # Synthesis
    message: str
    alternatives: List[str]
    requires_user_input: bool
    
    # Performance
    analysis_time_ms: float
    
    # Tracking
    validation_id: str
    timestamp: str


class RequestValidator:
    """
    Main validator that orchestrates three analysis engines.
    
    Performance Targets:
    - Viability analysis: <100ms
    - Historical analysis: <150ms (Tier 2 search)
    - Enhancement analysis: <50ms
    - Total validation: <300ms
    
    Efficiency Principles:
    - Run analyses in parallel when possible
    - Cache tier queries within same request
    - Skip redundant checks
    - Fail fast on critical issues
    """
    
    def __init__(
        self,
        tier1_api: Tier1API,
        tier2_kg: KnowledgeGraph,
        tier3_context: ContextIntelligence
    ):
        self.tier1 = tier1_api
        self.tier2 = tier2_kg
        self.tier3 = tier3_context
        
        self.viability = ViabilityAnalyzer(tier2_kg, tier3_context)
        self.historical = HistoricalAnalyzer(tier1_api, tier2_kg)
        self.enhancement = EnhancementAnalyzer(tier2_kg)
    
    def validate_and_enhance(
        self,
        request: AgentRequest,
        conversation_id: str,
        skip_checks: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate request and suggest enhancements.
        
        Args:
            request: Parsed user request
            conversation_id: Current conversation ID
            skip_checks: Checks to skip (for re-validation)
        
        Returns:
            ValidationResult with decision and suggestions
        """
        start_time = time.perf_counter()
        skip_checks = skip_checks or []
        
        # Run three analyses (parallel where possible)
        viability_result = None
        historical_result = None
        enhancement_result = None
        
        if "viability" not in skip_checks:
            viability_result = self.viability.analyze(request)
            
            # Fail fast on critical issues
            if viability_result.has_critical_issues:
                return self._create_blocking_challenge(
                    viability_result,
                    time.perf_counter() - start_time
                )
        
        # Continue with historical and enhancement in parallel
        if "historical" not in skip_checks:
            historical_result = self.historical.analyze(
                request,
                conversation_id
            )
        
        if "enhancement" not in skip_checks:
            enhancement_result = self.enhancement.analyze(request)
        
        # Synthesize results
        validation_result = self._synthesize(
            request,
            viability_result,
            historical_result,
            enhancement_result,
            time.perf_counter() - start_time
        )
        
        # Track for learning
        self._track_validation(validation_result)
        
        return validation_result
    
    def _synthesize(
        self,
        request: AgentRequest,
        viability,
        historical,
        enhancement,
        analysis_time: float
    ) -> ValidationResult:
        """Synthesize analysis results into recommendation."""
        # Implementation of synthesis logic
        # (See "Synthesis Engine" section above)
        pass
    
    def _create_blocking_challenge(
        self,
        viability_result,
        analysis_time: float
    ) -> ValidationResult:
        """Create a blocking challenge for critical issues."""
        pass
    
    def _track_validation(self, result: ValidationResult):
        """Track validation for learning (Tier 2 feedback)."""
        pass


class ViabilityAnalyzer:
    """Analyzes request viability and risks."""
    
    def __init__(self, tier2: KnowledgeGraph, tier3: ContextIntelligence):
        self.tier2 = tier2
        self.tier3 = tier3
    
    def analyze(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Analyze request viability.
        
        Checks:
        1. Scope feasibility (too large? too vague?)
        2. Technical viability (can codebase support?)
        3. Risk assessment (high-risk files? breaking changes?)
        4. Definition of Ready compliance
        
        Returns:
            {
                'viable': bool,
                'confidence': float,
                'has_critical_issues': bool,
                'issues': List[Dict],
                'risks': List[str],
                'alternatives': List[str]
            }
        """
        issues = []
        risks = []
        alternatives = []
        
        # Check 1: Scope analysis
        scope_issue = self._check_scope(request)
        if scope_issue:
            issues.append(scope_issue)
            if scope_issue['severity'] == 'CRITICAL':
                alternatives.extend(scope_issue['alternatives'])
        
        # Check 2: Technical viability (query Tier 3 for file health)
        if request.context.get('files'):
            tech_issues = self._check_technical_viability(
                request.context['files']
            )
            issues.extend(tech_issues)
            risks.extend([i['risk'] for i in tech_issues])
        
        # Check 3: Definition of Ready
        dor_issue = self._check_definition_of_ready(request)
        if dor_issue:
            issues.append(dor_issue)
        
        has_critical = any(i['severity'] == 'CRITICAL' for i in issues)
        
        return {
            'viable': not has_critical,
            'confidence': self._calculate_confidence(issues),
            'has_critical_issues': has_critical,
            'issues': issues,
            'risks': risks,
            'alternatives': alternatives
        }
    
    def _check_scope(self, request: AgentRequest) -> Optional[Dict]:
        """Check if scope is reasonable."""
        # Detect multi-feature requests
        # Detect vague requirements
        # Detect unbounded scope
        pass
    
    def _check_technical_viability(self, files: List[str]) -> List[Dict]:
        """Check technical constraints."""
        # Query Tier 3 for file stability
        # Check for high-churn files (risky)
        # Check for missing dependencies
        pass
    
    def _check_definition_of_ready(self, request: AgentRequest) -> Optional[Dict]:
        """Verify request meets DoR criteria."""
        # Check for clear requirements
        # Check for testable outcomes
        # Check for bounded scope
        pass


class HistoricalAnalyzer:
    """Analyzes past patterns and success rates."""
    
    def __init__(self, tier1: Tier1API, tier2: KnowledgeGraph):
        self.tier1 = tier1
        self.tier2 = tier2
    
    def analyze(
        self,
        request: AgentRequest,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Analyze historical context.
        
        Queries:
        1. Tier 1: Recent similar requests (last 20 conversations)
        2. Tier 2: Pattern library for similar workflows
        3. Tier 2: Success rates for similar patterns
        
        Returns:
            {
                'similar_patterns': List[Dict],
                'success_rate': float,
                'recommended_workflow': str,
                'reusable_components': List[str],
                'anti_patterns': List[Dict]
            }
        """
        # Search Tier 2 for similar patterns
        similar = self.tier2.search_patterns(
            query=request.user_message,
            pattern_type="workflow",
            limit=5
        )
        
        # Calculate success rate from historical data
        success_rate = self._calculate_success_rate(similar)
        
        # Find recommended workflow
        recommended = self._select_best_workflow(similar, success_rate)
        
        # Identify reusable components
        reusable = self._find_reusable_components(request, similar)
        
        # Check for anti-patterns
        anti_patterns = self.tier2.search_patterns(
            query=request.user_message,
            pattern_type="anti_pattern",
            limit=3
        )
        
        return {
            'similar_patterns': similar,
            'success_rate': success_rate,
            'recommended_workflow': recommended,
            'reusable_components': reusable,
            'anti_patterns': anti_patterns
        }


class EnhancementAnalyzer:
    """Suggests improvements to requests."""
    
    def __init__(self, tier2: KnowledgeGraph):
        self.tier2 = tier2
    
    def analyze(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Suggest enhancements.
        
        Categories:
        1. Completeness (edge cases, error handling)
        2. Best practices (TDD, SOLID, performance)
        3. Quality (tests, docs, accessibility)
        4. User experience (better UX patterns)
        
        Returns:
            {
                'enhancements': List[Dict],
                'estimated_value': float,
                'priority_order': List[str]
            }
        """
        enhancements = []
        
        # Query Tier 2 for best practice patterns
        best_practices = self.tier2.search_patterns(
            query=request.intent,
            pattern_type="principle",
            limit=5
        )
        
        # Generate enhancement suggestions
        enhancements.extend(self._suggest_completeness(request))
        enhancements.extend(self._suggest_best_practices(
            request,
            best_practices
        ))
        enhancements.extend(self._suggest_quality(request))
        
        # Calculate value (time saved or quality gained)
        estimated_value = sum(e['value'] for e in enhancements)
        
        # Priority ordering
        priority_order = self._prioritize_enhancements(enhancements)
        
        return {
            'enhancements': enhancements,
            'estimated_value': estimated_value,
            'priority_order': priority_order
        }
    
    def _suggest_completeness(self, request: AgentRequest) -> List[Dict]:
        """Suggest completeness improvements."""
        # Check for missing edge cases
        # Check for error handling
        # Check for accessibility
        pass
    
    def _suggest_best_practices(
        self,
        request: AgentRequest,
        best_practices: List
    ) -> List[Dict]:
        """Suggest best practice improvements."""
        # TDD approach
        # SOLID compliance
        # Performance considerations
        pass
    
    def _suggest_quality(self, request: AgentRequest) -> List[Dict]:
        """Suggest quality improvements."""
        # Additional tests
        # Documentation
        # Examples
        pass
```

---

## 📋 Presentation Layer

### Challenge/Enhancement Presenter

**New File:** `src/entry_point/validation_presenter.py`

```python
"""
Validation Presenter

Formats validation results for user-friendly presentation.
"""

from typing import Dict, Any
from .request_validator import ValidationResult, ValidationDecision


class ValidationPresenter:
    """Formats validation results for display."""
    
    def present(self, result: ValidationResult) -> str:
        """
        Format validation result for user.
        
        Returns formatted string with:
        - Decision (CHALLENGE/ENHANCE/APPROVE)
        - Issues/suggestions
        - Alternatives/enhancements
        - User action prompts
        """
        if result.decision == ValidationDecision.APPROVE:
            return self._format_approval(result)
        
        elif result.decision == ValidationDecision.CHALLENGE:
            return self._format_challenge(result)
        
        elif result.decision == ValidationDecision.ENHANCE:
            return self._format_enhancement(result)
        
        elif result.decision == ValidationDecision.ADVISE:
            return self._format_advisory(result)
    
    def _format_challenge(self, result: ValidationResult) -> str:
        """Format blocking/advisory challenge."""
        template = """
═══════════════════════════════════════════════
⚠️  REQUEST VALIDATION CHALLENGE

Request Analysis: {confidence:.0%} confidence
Analysis Time: {time_ms:.0f}ms

{message}

{issues_section}

{alternatives_section}

{recommendation}

═══════════════════════════════════════════════

Options:
  1. Accept recommended alternative
  2. Modify your request
  3. Override (requires justification)
  4. Abort

Your choice [1-4]:
"""
        return template.format(
            confidence=result.confidence,
            time_ms=result.analysis_time_ms,
            message=result.message,
            issues_section=self._format_issues(result.viability_issues),
            alternatives_section=self._format_alternatives(
                result.alternatives
            ),
            recommendation=self._format_recommendation(result)
        )
    
    def _format_enhancement(self, result: ValidationResult) -> str:
        """Format enhancement suggestions."""
        template = """
═══════════════════════════════════════════════
💡 REQUEST ENHANCEMENT SUGGESTIONS

Your request is viable ✅ ({confidence:.0%} confidence)

{historical_context}

{enhancements_section}

Estimated Value: {value}

═══════════════════════════════════════════════

Options:
  1. Accept all enhancements
  2. Select specific enhancements
  3. Proceed without enhancements
  
Your choice [1-3]:
"""
        return template.format(
            confidence=result.confidence,
            historical_context=self._format_historical(result),
            enhancements_section=self._format_enhancements(
                result.enhancements
            ),
            value=self._format_value(result.estimated_value)
        )
```

---

## 🎯 User Experience Flow

### Example 1: Blocking Challenge (Critical Issue)

```
User: "Skip tests and just implement the payment processor quickly"

CORTEX:
═══════════════════════════════════════════════
⚠️  REQUEST VALIDATION CHALLENGE

Request Analysis: 98% confidence this will cause problems
Analysis Time: 127ms

CRITICAL ISSUE DETECTED: Tier 0 Rule Violation

Your request proposes skipping TDD workflow (Rule #4).
Historical data shows:
  - Test-first approach: 94% success rate
  - Test-skip approach: 67% success rate
  - 2.3x longer delivery time when tests skipped
  - 68% higher rework rate

VIOLATIONS:
  ❌ Violates Definition of DONE (Rule #6)
  ❌ Bypasses quality gates
  ❌ Payment processing is high-risk (security implications)

SAFE ALTERNATIVES:
  1. Minimal test-first approach (RECOMMENDED) ⭐⭐⭐
     - Write 3-5 core tests first (~15 min)
     - Implement against tests
     - Faster overall (no rework)
     - Payment security validated
     
  2. Spike branch with full implementation later
     - Create throwaway spike for exploration
     - Discard and re-implement with tests
     - Learning without tech debt

RECOMMENDATION: Alternative 1 (proven 94% success rate)

═══════════════════════════════════════════════

Options:
  1. Accept recommended alternative ← RECOMMENDED
  2. Modify your request
  3. Override (requires justification)
  4. Abort

Your choice [1-4]: _
```

### Example 2: Enhancement Suggestions (Good Request)

```
User: "Add a share button to the document viewer"

CORTEX:
═══════════════════════════════════════════════
💡 REQUEST ENHANCEMENT SUGGESTIONS

Your request is viable ✅ (92% confidence)
Analysis Time: 143ms

HISTORICAL CONTEXT:
  Similar work found: "Add export button to report viewer" (2 weeks ago)
  ✅ Success rate: 100%
  ⏱️  Average time: 18 minutes
  📋 Proven workflow available

SUGGESTED ENHANCEMENTS:

1. Copy Link to Clipboard (Recommended) ⭐⭐⭐
   Why: Users expect this in share buttons (industry standard)
   Value: Better UX, meets user expectations
   Time: +3 minutes
   
2. Email Share Integration ⭐⭐
   Why: 73% of share buttons include email option
   Value: More sharing options = higher engagement
   Time: +8 minutes
   
3. Element ID for Testing (#doc-share-btn) ⭐⭐⭐
   Why: Enables robust Playwright tests
   Value: Prevents test fragility
   Time: +1 minute
   Required: Yes (learned from past broken tests)
   
4. Accessibility Labels ⭐⭐
   Why: WCAG compliance, screen reader support
   Value: Legal compliance, inclusive design
   Time: +2 minutes

Total Enhanced Implementation: 32 minutes
Original Implementation: 18 minutes
Value Gained: Professional-grade vs basic implementation

RECOMMENDED: Accept enhancements 1, 3, 4 (highest value)

═══════════════════════════════════════════════

Options:
  1. Accept all enhancements ← RECOMMENDED
  2. Select: [1,3,4] (recommended subset)
  3. Proceed without enhancements
  
Your choice [1-3]: _
```

### Example 3: Advisory (Proceed with Warning)

```
User: "Update the HostControlPanel.razor file"

CORTEX:
═══════════════════════════════════════════════
⚠️  REQUEST ADVISORY

Request Analysis: 85% confidence
Analysis Time: 98ms

Your request is viable, but risks detected:

RISK ASSESSMENT:
  ⚠️  HostControlPanel.razor is a HOTSPOT
      - 28% churn rate (high instability)
      - 89 edits in last 30 days
      - Often modified with: HostControlPanelContent.razor (75%)

RECOMMENDATIONS:
  1. Make small, focused changes (not large refactor)
  2. Run extra validation after changes
  3. Check HostControlPanelContent.razor if styles involved
  4. Test thoroughly (file has history of issues)

HISTORICAL CONTEXT:
  - Similar edits: 15 in last month
  - Success rate: 87% (lower than average 94%)
  - Best time: 10am-12pm sessions (94% success)
  - Current time: 2:30pm (81% success rate)

SUGGESTION: Proceed with extra caution ✅

═══════════════════════════════════════════════

Options:
  1. Proceed (aware of risks) ← RECOMMENDED
  2. Modify request (smaller scope)
  3. Abort and reconsider

Your choice [1-3]: _
```

---

## 📊 Performance & Efficiency Considerations

### Performance Targets

| Component | Target | Justification |
|-----------|--------|---------------|
| Viability Analysis | <100ms | Quick checks, Tier 3 queries cached |
| Historical Analysis | <150ms | Tier 2 FTS5 search optimized |
| Enhancement Analysis | <50ms | Rule-based, minimal queries |
| **Total Validation** | **<300ms** | **Acceptable overhead for value gained** |

### Efficiency Principles

1. **Fail Fast:** Critical viability issues abort remaining checks
2. **Parallel Queries:** Historical and enhancement run simultaneously
3. **Smart Caching:** Tier data cached within same request
4. **Confidence Thresholds:** Skip low-value checks if confidence high
5. **User Overrides Learned:** Track which validations users override (reduce false positives)

### Balancing Accuracy vs Efficiency

**High Accuracy Needed (Always Check):**
- Tier 0 rule violations (TDD skip, DoR/DoD bypass)
- Critical file modifications (high-risk files)
- Security implications (auth, payments, data handling)
- Scope creep (multi-feature in single request)

**Medium Accuracy (Check if Time Permits):**
- Enhancement suggestions (nice-to-have)
- Historical pattern matches (helpful but not critical)
- Best practice recommendations (quality improvements)

**Low Priority (Skip if Slow):**
- Minor style suggestions
- Optional documentation improvements
- Low-value enhancements (<1 min implementation)

### Adaptive Thresholds

```python
# Adjust validation depth based on request complexity
if request.estimated_size < 30_minutes:
    validation_depth = "quick"  # <100ms
elif request.estimated_size < 2_hours:
    validation_depth = "standard"  # <300ms
else:
    validation_depth = "thorough"  # <500ms (worth it for large work)
```

---

## 🧪 Testing Strategy

### Unit Tests

```python
# tests/entry_point/test_request_validator.py

def test_validator_blocks_critical_violations():
    """Validator challenges Tier 0 violations."""
    request = create_request("Skip TDD and implement feature")
    result = validator.validate_and_enhance(request, "conv-123")
    
    assert result.decision == ValidationDecision.CHALLENGE
    assert result.requires_user_input == True
    assert "Tier 0" in result.message
    assert len(result.alternatives) > 0

def test_validator_suggests_enhancements():
    """Validator suggests improvements for good requests."""
    request = create_request("Add a delete button")
    result = validator.validate_and_enhance(request, "conv-123")
    
    assert result.decision == ValidationDecision.ENHANCE
    assert len(result.enhancements) > 0
    assert result.estimated_value > 0

def test_validator_performance():
    """Validator meets performance targets."""
    request = create_request("Add feature X")
    result = validator.validate_and_enhance(request, "conv-123")
    
    assert result.analysis_time_ms < 300  # <300ms target

def test_validator_uses_historical_data():
    """Validator finds similar patterns from Tier 2."""
    # Setup: Add similar pattern to Tier 2
    tier2.add_pattern(...)
    
    request = create_request("Add PDF export")
    result = validator.validate_and_enhance(request, "conv-123")
    
    assert len(result.similar_patterns) > 0
    assert result.recommended_workflow is not None
```

### Integration Tests

```python
# tests/entry_point/test_validation_integration.py

def test_entry_point_validation_flow():
    """Full flow: parse → validate → challenge → decision → route."""
    entry = CortexEntry()
    
    # Should trigger challenge
    response = entry.process("Skip tests for this feature")
    
    assert "CHALLENGE" in response
    assert "Tier 0" in response
    # (In real test, would mock user input)

def test_validation_learns_from_overrides():
    """System learns when users frequently override validation."""
    # Track: User overrides "add confirmation dialog" 5 times
    # Expect: System reduces priority of this suggestion
    pass
```

---

## 📈 Metrics & Learning

### Track Validation Decisions

**New Table:** `tier1/validation_decisions.db`

```sql
CREATE TABLE validation_decisions (
    validation_id TEXT PRIMARY KEY,
    conversation_id TEXT,
    timestamp TEXT,
    
    request_intent TEXT,
    request_content TEXT,
    
    viability_score REAL,
    historical_confidence REAL,
    enhancement_count INTEGER,
    
    decision_type TEXT,  -- CHALLENGE/ENHANCE/APPROVE/ADVISE
    
    user_action TEXT,  -- ACCEPT/MODIFY/OVERRIDE/ABORT
    user_justification TEXT,
    
    outcome_success BOOLEAN,  -- Did request ultimately succeed?
    outcome_time_actual REAL,
    outcome_time_estimated REAL,
    
    learned_feedback TEXT  -- What we learned
);
```

### Learning Loop

```python
def learn_from_validation_outcome(validation_id: str):
    """
    Learn from validation outcome to improve future validations.
    
    Scenarios:
    1. User overrides frequently → Reduce false positive rate
    2. Challenge prevents failure → Reinforce pattern
    3. Enhancement accepted + success → Increase enhancement priority
    4. Challenge ignored + failure → Strengthen challenge message
    """
    decision = get_validation_decision(validation_id)
    outcome = get_request_outcome(decision.conversation_id)
    
    if decision.user_action == "OVERRIDE" and outcome.success:
        # User was right, reduce false positive
        tier2.adjust_pattern_confidence(
            pattern_id=decision.matched_pattern,
            adjustment=-0.05
        )
    
    elif decision.user_action == "ACCEPT" and outcome.success:
        # Validation helped, reinforce
        tier2.adjust_pattern_confidence(
            pattern_id=decision.matched_pattern,
            adjustment=+0.1
        )
    
    # ... more learning rules ...
```

---

## 🛠️ Configuration

### Enable/Disable Validation

**In:** `cortex.config.json`

```json
{
  "entry_point": {
    "enable_validation": true,
    "validation_depth": "standard",  // quick/standard/thorough
    "validation_timeout_ms": 300,
    
    "viability_checks": {
      "scope_analysis": true,
      "technical_viability": true,
      "definition_of_ready": true
    },
    
    "historical_checks": {
      "pattern_matching": true,
      "success_rate_threshold": 0.7,
      "max_similar_patterns": 5
    },
    
    "enhancement_checks": {
      "completeness": true,
      "best_practices": true,
      "quality_improvements": true,
      "min_value_threshold": 0.1  // Skip low-value (<6 min)
    },
    
    "challenge_rules": {
      "block_tier0_violations": true,
      "block_critical_risks": true,
      "advise_medium_risks": true,
      "suggest_enhancements": true
    }
  }
}
```

### User Preferences

```json
{
  "validation_preferences": {
    "always_suggest_tests": true,
    "always_suggest_element_ids": true,
    "skip_minor_enhancements": false,
    "auto_accept_proven_patterns": false
  }
}
```

---

## 🚀 Implementation Phases

### Phase 1: Core Validator (8-10 hours)

**Tasks:**
1. Create `request_validator.py` skeleton
2. Implement `ViabilityAnalyzer` (basic checks)
3. Implement `HistoricalAnalyzer` (Tier 2 queries)
4. Implement `EnhancementAnalyzer` (rule-based)
5. Integrate with `cortex_entry.py`
6. Add configuration support
7. Write unit tests

**Deliverable:** Basic validation working for simple cases

### Phase 2: Synthesis & Presentation (4-6 hours)

**Tasks:**
1. Implement synthesis engine (combine analyses)
2. Create `validation_presenter.py`
3. Format challenges beautifully
4. Format enhancements clearly
5. Add user input handling
6. Write integration tests

**Deliverable:** Full validation flow with user interaction

### Phase 3: Learning & Metrics (3-4 hours)

**Tasks:**
1. Create `validation_tracker.py`
2. Add validation_decisions table (Tier 1)
3. Implement learning loop
4. Track override patterns
5. Adjust confidence based on outcomes
6. Add validation metrics to dashboard

**Deliverable:** System learns from validation outcomes

### Phase 4: Polish & Optimization (2-3 hours)

**Tasks:**
1. Performance profiling
2. Add caching for common queries
3. Optimize Tier 2/3 queries
4. Add adaptive thresholds
5. User preference support
6. Documentation

**Deliverable:** Production-ready validator

**Total Estimated Time:** 17-23 hours

---

## 💡 Advanced Features (Future)

### Context-Aware Validation

```python
# Adjust validation based on conversation context
if conversation_has_recent_failures(conversation_id):
    # User struggling, be more helpful
    validation_depth = "thorough"
    enhancement_threshold = 0.0  # Show all suggestions
else:
    # User succeeding, be less intrusive
    validation_depth = "quick"
    enhancement_threshold = 0.2  # Only high-value suggestions
```

### Team Learning

```python
# Learn from team patterns (multi-user CORTEX)
if team_frequently_overrides(validation_pattern):
    # This validation doesn't work for this team
    disable_pattern_for_team(pattern_id, team_id)
```

### Proactive Suggestions

```python
# Suggest improvements before user asks
if recent_commits_lack_tests(user_id):
    proactive_suggest("Consider adding tests for recent commits")
```

---

## ✅ Success Criteria

**Validation is successful if:**

1. **Accuracy:** >90% of critical challenges are correct (prevent actual problems)
2. **Efficiency:** <300ms average validation time (acceptable overhead)
3. **Value:** >50% of enhancements accepted by users (relevant suggestions)
4. **Learning:** Override rate decreases over time (fewer false positives)
5. **Adoption:** Users enable validation (don't disable it)

---

## 📝 Summary

### What We're Building

An intelligent "second pair of eyes" at the CORTEX entry point that:
- ✅ Challenges risky requests before work begins
- ✅ Suggests improvements based on history and patterns
- ✅ Balances accuracy with efficiency (<300ms validation)
- ✅ Learns from user decisions over time
- ✅ Prevents wasted effort on flawed requests

### Key Benefits

1. **Catch Problems Early:** Block tier 0 violations, scope creep, technical impossibilities
2. **Leverage History:** Reuse proven workflows, avoid past mistakes
3. **Improve Quality:** Suggest enhancements that add value
4. **Save Time:** 30 seconds of validation prevents 30 minutes of rework
5. **Continuous Learning:** System gets smarter with each interaction

### Integration Points

- **Entry Point:** Between parser and router
- **Tier 1:** Recent conversation context
- **Tier 2:** Pattern library and historical success rates
- **Tier 3:** Project health and file stability
- **Brain Protector:** Shares tier 0 violation detection logic

---

**Status:** Design Complete ✅  
**Ready for Implementation:** Yes  
**Estimated Effort:** 17-23 hours  
**Expected Value:** High (prevents costly mistakes, improves quality)

**Recommendation:** Implement in Phase 1 of CORTEX 2.0 (after core refactoring complete)

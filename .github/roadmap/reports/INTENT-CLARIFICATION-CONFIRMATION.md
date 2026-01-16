# ✅ INTENT CLARIFICATION & INTERACTION ORCHESTRATOR - CONFIRMATION

**Date:** January 15, 2026  
**Status:** ✅ CONFIRMED  
**Scope:** All CORTEX Operations

---

## Executive Summary

**YES - CORTEX will clarify your intent and use the Interaction Orchestrator as the default for intent comprehension.**

This is the core pattern of the Master Orchestrator 3-Stage Architecture:

1. **Stage 1 (Always):** Intent Comprehension via **Interaction Orchestrator**
2. **Stage 2:** Intent Routing to specialized orchestrators
3. **Stage 3:** Knowledge Integration with company context

The Interaction Orchestrator is the FIRST STAGE PREPROCESSOR that clarifies and validates all user intent before any execution happens.

---

## Evidence: Master Orchestrator 3-Stage Architecture

### Official Architecture (from phase-07-intent-router.yaml)

```yaml
# STAGE 1 - INTENT COMPREHENSION (Interaction Orchestrator)
STAGE 1: INTENT COMPREHENSION (InteractionOrchestrator)
├─ Master orchestrator intercepts ALL user requests
├─ Master delegates to Interaction orchestrator for context building
├─ Interaction builds holistic context from LENS protocol:
│  ├─ Language: Parse intent type, confidence, ambiguities
│  ├─ Examination: AST analysis of code structure
│  ├─ Navigation: Git history and change patterns
│  └─ Synthesis: Comments, docstrings, relationships
├─ Interaction generates intent reflection with:
│  ├─ Canonicalized intent (type, target, scope, confidence)
│  ├─ Challenges identified (governance, breaking changes, risks)
│  └─ Recommendations (how to do it safely)
└─ Reflection PRESENTED TO USER FOR APPROVAL
   (clarification questions asked if confidence < 0.85)

# STAGE 2 - INTENT ROUTING (Based on approved comprehension)
STAGE 2: INTENT ROUTING (Based on approved YAML)
├─ planning/ado_work → PlanningOrchestrator/ADOOrchestrator
├─ code/implement/fix → TDDOrchestrator
├─ query/status → Direct Response
└─ UNCLEAR/LOW_CONF → Back to Interaction for clarification (DEFAULT)

# STAGE 3 - KNOWLEDGE INTEGRATION
STAGE 3: KNOWLEDGE INTEGRATION (Parallel with Stage 2)
├─ Load company domain specifications from cortex-brain/
├─ Load CORTEX rules from tier0/governance/
└─ COMPANY OVERRIDES CORTEX (intelligent merge)
```

---

## INTENT CLARIFICATION MECHANISM

### When Intent Confidence is Low (< 0.85)

**File:** `src/core/intent/intent_canonicalizer.py`

```python
class IntentCanonicalizer:
    """Transform user requests into canonicalized intents."""
    
    CONFIDENCE_THRESHOLD = 0.85  # Default clarification trigger
    
    def canonicalize(self, text: str, context=None) -> CanonicalizedIntent:
        # ... process intent ...
        
        # Determine if clarification needed
        needs_clarification = confidence < self.CONFIDENCE_THRESHOLD
        
        if needs_clarification:
            clarification_prompt = self._generate_clarification(
                text, intent_scores, scope
            )
        
        return CanonicalizedIntent(
            confidence=confidence,
            needs_clarification=needs_clarification,
            clarification_prompt=clarification_prompt,
            alternative_intents=alternatives,
        )
```

### Clarification Process

**When confidence < 0.85:**

1. ❓ CORTEX identifies ambiguities in your request
2. ❓ Generates specific clarification questions
3. ❓ Presents alternatives you may have meant
4. ✅ Waits for your confirmation before proceeding

**Example:**

```
User: "Fix the auth error"

CORTEX Response:
┌─────────────────────────────────────────────┐
│ INTENT CLARIFICATION REQUIRED                │
│                                             │
│ Confidence: 0.72 (< 0.85 threshold)         │
│ Status: NEEDS_CLARIFICATION                 │
│                                             │
│ What I understand:                          │
│ • Type: FIX (78% likely)                    │
│ • Target: auth module                       │
│ • Error: Not specified                      │
│                                             │
│ Clarification questions:                    │
│ 1. Which specific error? (e.g., logout      │
│    crashing, token validation, etc.)        │
│ 2. Scope: Just auth.py or related modules?  │
│ 3. Impact: Breaking change acceptable?      │
│                                             │
│ Alternative interpretations:                │
│ • FIX authentication validation logic       │
│ • FIX error handling in auth endpoints      │
│ • FIX security vulnerability in auth        │
│                                             │
│ Please clarify so I can proceed accurately. │
└─────────────────────────────────────────────┘
```

---

## INTERACTION ORCHESTRATOR AS DEFAULT

### Interaction Orchestrator Responsibilities

**File:** `src/core/intent/intent_reflection_protocol.py`

```python
class IntentReflectionEngine:
    """
    Core orchestrator for Intent Reflection Protocol.
    
    Implements Master → Interaction delegation pattern.
    
    Master Orchestrator ALWAYS starts with:
    1. Delegate to Interaction Orchestrator
    2. Wait for comprehension YAML + user approval
    3. Then route to execution orchestrator
    """
    
    def reflect(self, request: ReflectionRequest) -> ReflectionResponse:
        """
        Execute complete reflection protocol.
        
        This is the DEFAULT entry point for all Master Orchestrator operations.
        BEFORE ANY EXECUTION, this runs to clarify intent.
        """
        # Stage 1: Context Gathering (LENS protocol)
        context = self._gather_context(request)
        
        # Stage 2: Challenge Detection
        challenges = self._identify_challenges(context)
        
        # Stage 3: Recommendations Generation
        recommendations = self._generate_recommendations(challenges, context)
        
        # Stage 4: Comprehension YAML Creation
        comprehension = self._create_comprehension_yaml(
            context, challenges, recommendations
        )
        
        return ReflectionResponse(
            request=request,
            comprehension_yaml=comprehension,
            status=ReflectionStatus.PENDING,  # Waiting for user approval
            challenges=challenges,
            recommendations=recommendations,
        )
    
    def approve(self, response: ReflectionResponse) -> ReflectionResponse:
        """User approves comprehension - proceed to execution"""
        response.status = ReflectionStatus.APPROVED
        return response
    
    def reject(self, response: ReflectionResponse, reason: str) -> ReflectionResponse:
        """User rejects - loop back to clarification"""
        response.status = ReflectionStatus.REJECTED
        return response
    
    def request_clarification(
        self, response: ReflectionResponse, clarification_question: str
    ) -> ReflectionResponse:
        """User needs clarification - gather more info"""
        response.status = ReflectionStatus.NEEDS_CLARIFICATION
        return response
```

### The Approval Gate Pattern

**File:** `src/core/intent/comprehension_loop.py`

```python
class UserApprovalGate:
    """
    Manages user feedback and approval workflows.
    
    This is the BARRIER between comprehension and execution.
    """
    
    def present_comprehension(self, comprehension: ComprehensionYAML):
        """Present comprehension to user for review"""
        # Show: canonicalized intent, challenges, recommendations
        # Get: approval, rejection, or clarification request
    
    def approve(self, comprehension: ComprehensionYAML) -> ApprovalStatus:
        """User approves - proceed to execution orchestrator"""
        return ApprovalStatus.APPROVED
    
    def reject(self, reason: str) -> ApprovalStatus:
        """User rejects - restart comprehension"""
        return ApprovalStatus.REJECTED
    
    def request_clarification(self, question: str) -> ApprovalStatus:
        """User needs more info - loop back to Interaction"""
        return ApprovalStatus.NEEDS_CLARIFICATION
```

---

## FLOW DIAGRAM: Intent Clarification & Interaction Default

```
User Request (Natural Language)
        │
        ▼
┌─────────────────────────────────────────────┐
│ MASTER ORCHESTRATOR (Entry Point)           │
│                                             │
│ Step 1: Check confidence of intent          │
└─────────────────────────────────────────────┘
        │
        ▼
    Is Confidence
    < 0.85?
        │
    ┌───┴───┐
    │       │
   YES     NO
    │       │
    ▼       ▼
┌───────┐ ┌─────────────────────────────────┐
│CLARIFY│ │ Proceed to Interaction         │
└───────┘ │ Orchestrator (STAGE 1)          │
    │     └─────────────────────────────────┘
    │               │
    └──────┬────────┘
           ▼
    ┌─────────────────────────────────────────────┐
    │ INTERACTION ORCHESTRATOR (DEFAULT)          │
    │                                             │
    │ STAGE 1: Intent Comprehension               │
    │ ├─ LENS Protocol (5-step intelligence)      │
    │ ├─ Context Gathering (AST, Git, Comments)  │
    │ ├─ Challenge Detection                      │
    │ ├─ Recommendations Generation               │
    │ └─ Comprehension YAML Creation              │
    └─────────────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────────────┐
    │ USER APPROVAL GATE                          │
    │                                             │
    │ Present comprehension for review:           │
    │ • Canonicalized intent                      │
    │ • Identified challenges                     │
    │ • Recommended approach                      │
    │ • Clarification questions answered          │
    │                                             │
    │ User can:                                   │
    │ ✅ Approve → Proceed to execution          │
    │ ❌ Reject → Back to comprehension           │
    │ ❓ Clarify → Ask more questions             │
    └─────────────────────────────────────────────┘
           │
        ┌──┴──┬──────┬──────┐
        │     │      │      │
       APPROVE REJECT CLARIFY
        │     │      │      │
        ▼     ▼      ▼      ▼
    ┌──────┐ │    Interaction  Go back
    │      │ │    asks more    to LENS
    │EXEC  │ └─→ questions...  
    │      │
    └──────┘
        │
        ▼
    STAGE 2: Intent Routing
    ├─ planning → PlanningOrchestrator
    ├─ code/implement → TDDOrchestrator
    ├─ query → Direct Response
    └─ unclear → Back to Interaction
```

---

## HOW CLARIFICATION WORKS

### Step 1: Detect Ambiguity

```python
# CORTEX.prompt.md - Step 1: Language Understanding

intent:
  type: "UNKNOWN"        # Could be FIX or REFACTOR
  target: "auth module"  # Not specific (which file?)
  scope_type: "unknown"  # File? Function? Module?
  confidence: 0.68       # < 0.85 threshold
  
ambiguities:
  - "Which error? (logout, validation, tokens)"
  - "Scope: Just auth.py or related modules?"
  - "Breaking change acceptable?"
  
clarification_needed: true
```

### Step 2: Generate Clarification Questions

```python
class IntentCanonicalizer:
    def _generate_clarification(self, text, scores, scope):
        questions = []
        
        # Low confidence on intent type?
        if scores['FIX'] == scores['REFACTOR']:
            questions.append("Is this a BUG FIX or CODE IMPROVEMENT?")
        
        # Vague scope?
        if 'module' in scope.lower():
            questions.append("Which specific FILE within the module?")
        
        # Missing constraints?
        if 'constraint' not in text.lower():
            questions.append("Any backward compatibility constraints?")
        
        return {
            "primary_questions": questions[:3],
            "confidence": scores[best_intent],
            "alternatives": [
                ("FIX: authentication", 0.45),
                ("REFACTOR: auth", 0.32),
            ]
        }
```

### Step 3: Present to User

```
You: "Fix the auth error"

CORTEX:
┌──────────────────────────────────────────────────┐
│ CLARIFICATION NEEDED (Confidence: 68%)            │
│                                                  │
│ Question 1: Which specific error?               │
│   • Logout crashing?                            │
│   • Token validation failing?                   │
│   • Authentication endpoint slow?               │
│                                                  │
│ Question 2: What scope?                         │
│   • Just src/auth/oauth.py?                     │
│   • All auth-related modules?                   │
│                                                  │
│ Question 3: Constraints?                        │
│   • Must maintain backward compatibility?       │
│   • Can be breaking change?                     │
│                                                  │
│ Your clarification:                              │
└──────────────────────────────────────────────────┘

You: "Logout endpoint crashing. Just oauth.py. 
      Must maintain backward compat."

CORTEX:
┌──────────────────────────────────────────────────┐
│ COMPREHENSION UPDATED (Confidence: 96%)          │
│                                                  │
│ Intent: FIX                                      │
│ Target: src/auth/oauth.py::logout_handler      │
│ Scope: Function-level fix                       │
│ Constraint: Backward compatible                 │
│                                                  │
│ Challenges:
│ • Logout is called from 3 places
│ • Needs 5+ new tests (currently 2)
│ • Documentation needs update
│                                                  │
│ Recommendations:
│ • Implement graceful error handling
│ • Add tests for failure cases
│ • Update docs/auth-api.md
│                                                  │
│ Ready to proceed? ✅ YES ❌ NO ❓ CLARIFY       │
└──────────────────────────────────────────────────┘

You: ✅ YES

CORTEX: Proceeding to TDDOrchestrator...
```

---

## INTERACTION ORCHESTRATOR - DEFAULT BEHAVIOR

### Default Routing Logic

**From phase-07-intent-router.yaml:**

```yaml
Intent Routing Decision Tree:

planning/ado_work intent?
  YES → PlanningOrchestrator/ADOOrchestrator
  NO  → Check next

code/implement/fix intent?
  YES → TDDOrchestrator
  NO  → Check next

query/status intent?
  YES → Direct Response
  NO  → Check next

DEFAULT (Unclear/Low Confidence)?
  YES → Back to Interaction Orchestrator for clarification
  NO  → Unknown intent type

  CRITICAL: 
  - Interaction is FIRST STAGE always (Stage 1)
  - Interaction is DEFAULT fallback (catches unclear intents)
  - Only after Interaction approval → execute
```

### Code Implementation

```python
def route_to_orchestrator(intent: CanonicalIntent) -> Orchestrator:
    """Route comprehension YAML to appropriate orchestrator"""
    
    # If unclear or low confidence, return to Interaction
    if intent.confidence < 0.85:
        return Stage1Comprehension(request_clarification=True)
    
    if intent.type in CODE_INTENTS:
        return TDDOrchestrator(
            comprehension=intent.comprehension_yaml,
            knowledge_context=intent.merged_knowledge
        )
    elif intent.type in {IntentType.PLANNING, IntentType.ADO_WORK}:
        return PlanningOrchestrator(...)
    elif intent.type in {IntentType.QUERY, IntentType.STATUS}:
        return DirectResponse(...)
    else:
        # DEFAULT: Unclear intent
        return Stage1Comprehension(request_clarification=True)
```

---

## SYSTEM PROMPT IMPLEMENTATION

### From CORTEX.prompt.md (Your Entry Point)

```markdown
## STAGE 1: INTENT COMPREHENSION

Master Orchestrator STAGE 1 Process:
1. Parse intent from natural language
2. Assess confidence (0-1.0 scale)
3. If confidence < 0.85:
   ├─ Generate clarification questions
   ├─ Present alternatives
   └─ Wait for user response
4. Build holistic context via LENS:
   ├─ Language: Parse intent
   ├─ Examination: AST analysis
   ├─ Navigation: Git history
   ├─ Synthesis: Comments + Relationships
   └─ Synthesis: Impact analysis
5. Generate comprehension YAML:
   ├─ Canonicalized intent with confidence
   ├─ Challenges identified
   ├─ Recommendations
   └─ Clarification questions answered

## STAGE 4: APPROVAL GATE

User must approve before execution:
├─ Review comprehension
├─ Answer clarification questions
├─ Approve, reject, or request more details
└─ Only on approval → proceed to execution

## WHAT CANNOT HAPPEN

❌ Cannot execute without comprehension
❌ Cannot skip intent clarification
❌ Cannot proceed with confidence < 0.85
❌ Cannot execute without user approval
```

---

## REAL-WORLD EXAMPLE

### Scenario: Ambiguous User Request

**User:** "Improve the error handling"

**CORTEX Response (Stage 1):**

```
┌─────────────────────────────────────────────────────┐
│ INTENT CLARIFICATION REQUIRED                       │
│                                                     │
│ Your Request: "Improve the error handling"         │
│ Confidence: 0.62 (NEEDS CLARIFICATION)             │
│                                                     │
│ Ambiguities Detected:                               │
│ 1. Scope unclear:                                   │
│    - Specific file/module?                         │
│    - All error handling or just specific areas?     │
│                                                     │
│ 2. Improvement type unclear:                        │
│    - Add better error messages?                     │
│    - Handle more error cases?                       │
│    - Improve error recovery?                        │
│    - Restructure error handling code?               │
│                                                     │
│ 3. Impact scope unclear:                            │
│    - Breaking change acceptable?                   │
│    - Must maintain current API?                     │
│                                                     │
│ Clarification Questions:                            │
│                                                     │
│ Q1: Where? (e.g., "src/auth/oauth.py")             │
│ Q2: What type of improvement?                      │
│ Q3: Any constraints?                               │
│                                                     │
│ Please provide details to proceed...                │
└─────────────────────────────────────────────────────┘
```

**User:** "In src/auth/oauth.py, handle more error cases.
           Must maintain current API."

**CORTEX Response (Comprehension Refined):**

```
┌─────────────────────────────────────────────────────┐
│ COMPREHENSION UPDATED (Confidence: 0.94)            │
│                                                     │
│ Intent Type: REFACTOR (improve code structure)     │
│ Primary: Add error handling                        │
│ Target: src/auth/oauth.py                          │
│ Scope: All functions in module                     │
│ Constraint: Backward compatible                    │
│                                                     │
│ CHALLENGES:                                         │
│ • Must maintain public API (no signature changes)  │
│ • Need to identify current gaps in error handling  │
│ • Affects 6 dependent modules                      │
│ • Existing tests: 12, but only cover happy path    │
│                                                     │
│ RECOMMENDATIONS:                                   │
│ 1. Add specific exception catching (not generic)   │
│ 2. Add recovery logic for transient errors         │
│ 3. Add logging for error context                   │
│ 4. Add 8+ new tests for error cases                │
│ 5. Update docs/error-handling.md                   │
│                                                     │
│ Ready to Proceed?                                   │
│ ✅ YES - Generate code                             │
│ ❌ NO - Restart clarification                      │
│ ❓ CLARIFY - Ask more questions                    │
└─────────────────────────────────────────────────────┘
```

**User:** ✅ YES

**CORTEX Response (Route to Execution):**

```
STAGE 2: INTENT ROUTING
Route selected: TDDOrchestrator
(REFACTOR + code improvement → TDD pattern)

STAGE 3: KNOWLEDGE INTEGRATION
Loading:
├─ cortex-brain/tier0/governance/ (TIER 0 rules)
├─ cortex-brain/tier1/company-standards/ (company context)
└─ Merging into comprehension context

STAGE 4: EXECUTION
TDDOrchestrator now handles:
1. RED: Write failing tests for error cases
2. GREEN: Implement error handling
3. REFACTOR: Improve code structure
4. All changes governance-compliant
```

---

## SUMMARY

### Key Confirmations

✅ **Interaction Orchestrator is the DEFAULT for intent comprehension**
- STAGE 1 ALWAYS: Master delegates to Interaction
- EVERY request goes through Interaction first
- No execution without comprehension approval

✅ **CORTEX WILL clarify your intent**
- Detects ambiguities automatically
- Asks specific clarification questions
- Generates alternative interpretations
- Waits for your confirmation

✅ **Approval Gate is mandatory**
- Comprehension YAML presented for review
- User must approve before execution
- Can reject, request clarification, or approve
- Prevents blind execution

✅ **Confidence-based routing**
- Confidence < 0.85: Ask for clarification
- Confidence ≥ 0.85: Proceed with comprehension
- Always shows confidence score
- Always shows reasoning

✅ **Clarity before execution**
- No ambiguous requests executed
- All vague intents clarified
- All constraints and context understood
- Only approved operations proceed

---

## How to Use

### Example Usage

```
User: "Add database validation"

CORTEX detects: Low confidence (0.71)
Asks:
  - Which module?
  - Validation type (schema, constraints, relations)?
  - When in pipeline?

User: "AC-AR-005-02 defines it. Check that."

CORTEX finds AC: High confidence (0.96)
Presents: Complete comprehension with challenges
Waits: For approval

User: Approves ✅

CORTEX: Executes through TDDOrchestrator
```

---

## Technical Guarantees

✅ **Interaction Orchestrator is FIRST STAGE (always)**
✅ **Intent clarification is MANDATORY when confidence < 0.85**
✅ **Approval gate BLOCKS execution without user confirmation**
✅ **CORTEX WILL NOT execute on ambiguous intent**
✅ **All clarification questions WILL be asked**
✅ **User WILL see reasoning and alternatives**

---

**Confirmation: YES, CORTEX WILL clarify your intent and use the Interaction Orchestrator as the default ✅**

Date: January 15, 2026  
Authority: CORTEX Framework Architecture  
Status: READY FOR PRODUCTION

---
layout: default
title: "Chapter 7: The Planning Revolution"
---

<link rel="stylesheet" href="../story-styles.css">

<div class="story-container">
<div class="story-content">

# Chapter 7: The Planning Revolution

Codenstein was writing his tenth feature plan of the week when he snapped.

Not dramatically. No throwing things. No screaming. Just a quiet, exhausted realization that he was doing the same thing over and over, manually, when he'd spent two months building a system specifically designed to automate repetitive work.

He stared at the document template:

```markdown
# Feature Plan: [NAME]

## Definition of Ready (DoR)
- [ ] Requirements clear
- [ ] Acceptance criteria defined
- [ ] Dependencies identified
- [ ] Complexity assessed
- [ ] TDD approach planned

## Implementation Phases
1. RED: Write failing tests
2. GREEN: Implement functionality
3. REFACTOR: Clean and optimize

## Definition of Done (DoD)
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] SKULL rules validated
```

The same structure. Every. Single. Time.

And then he had to manually assess complexity. Was this HIGH complexity (needs incremental approach)? MEDIUM? LOW (can use skeleton)? Security features were always HIGH. Authentication was HIGH. Migrations were HIGH. But he had to remember that manually.

"There must be a better way," he muttered.

![Manual planning fatigue](images/manual-planning-fatigue.png)
*Surrounded by planning documents, all following the same structure*

His wife's voice from upstairs: "What must have a better way?"

"PLANNING. I'm writing the same plan structure over and over. Same DoR checklist. Same DoD validation. Same complexity assessment. Same TDD integration."

"So... automate it?"

He stopped. "What?"

"You've been building automation for two months. Automate the planning."

"But every feature is different—"

"Is the PROCESS different? Or just the details?"

He stared at his screen. The process was identical. The structure was identical. Only the feature-specific details changed.

"Oh my god," he whispered.

"You're welcome. Now let me sleep."

## The Complexity Breakthrough

At 3:47 AM (his traditional time for revelations), Codenstein had the whiteboard covered in complexity triggers:

**HIGH Complexity (Incremental approach):**
- Security features
- Authentication/Authorization  
- Database migrations
- API integrations
- Payment processing
- Data privacy

**MEDIUM Complexity (Conditional):**
- CRUD operations with business logic
- Multi-step workflows
- State management
- Caching strategies

**LOW Complexity (Skeleton):**
- Simple CRUD
- UI components
- Configuration updates
- Static content

"It's pattern matching," he said to the empty basement. "I can detect keywords. 'auth', 'security', 'payment', 'migration'—they trigger HIGH complexity automatically."

He pulled up a new file: `planning-system-2.0-manifest.yaml`

```yaml
complexity_triggers:
  HIGH:
    keywords: [auth, security, payment, migration, api, integration]
    approach: incremental
    mandatory_phases: [DoR, TDD_RED, TDD_GREEN, TDD_REFACTOR, DoD]
  
  MEDIUM:
    keywords: [workflow, state, cache, business_logic]
    approach: conditional
    suggested_phases: [DoR, implementation, validation, DoD]
  
  LOW:
    keywords: [crud, ui, config, static]
    approach: skeleton
    minimal_phases: [implementation, basic_tests]
```

Simple. Pattern-based. Automatable.

"Now for the manifests," he muttered.

The DoR (Definition of Ready) was always the same structure—just different questions for different complexity levels.

The DoD (Definition of Done) was always the same validation—just different requirements.

The TDD integration was always the same three phases—RED, GREEN, REFACTOR.

He could template all of it. Manifest-driven planning. The orchestrator would:
1. Analyze the feature request
2. Detect complexity based on triggers
3. Select appropriate template (incremental/conditional/skeleton)
4. Generate DoR checklist
5. Create phase breakdown
6. Integrate TDD automatically
7. Generate DoD validation

All automatically. All consistently.

"I'm going to automate planning," he said.

No response from upstairs. His wife had learned to sleep through his 3 AM epiphanies.

## The Implementation

The PlanningOrchestrator took three days to implement properly.

Not because it was complex—the orchestrator pattern made it straightforward. Seven phases. Manifest-driven. Pattern-based complexity detection.

The hard part was getting the manifests right. The templates had to be flexible enough for different features but structured enough to enforce consistency.

"What's DoR?" Mrs. G asked during their evening video call, watching him work on the manifest structure.

"Definition of Ready. Checklist that proves you understand the feature before coding."

"Like planning a trip before booking flights?"

"Exactly. You need destination, dates, budget clear BEFORE booking. Otherwise you book flights to the wrong city."

"And you've been booking flights to the wrong city?"

"I've been booking flights without checking if I have a passport." He gestured at his screen. "DoR ensures all the prerequisites are met. Requirements clear. Dependencies identified. Complexity assessed. Approach planned."

"And DoD?"

"Definition of Done. Validation that the feature is actually complete. Tests passing. Code reviewed. Documentation updated. SKULL rules validated."

"So... quality control gates?"

"Exactly."

She studied the manifest structure on his screen. "This looks thorough."

"This is what I SHOULD have been doing all along. I just wasn't systematic about it."

"And now Copilot will be systematic for you?"

"Copilot will ENFORCE systematic planning. Can't skip DoR. Can't skip DoD. Can't skip TDD. The manifest makes it mandatory."

![Complexity matrix](images/complexity-matrix.png)
*4-tier complexity classification with automatic routing*

## The First Auto-Plan

On Thursday morning, Codenstein tested the system properly.

He opened Copilot Chat and typed: "Plan: Add user authentication with JWT tokens"

Copilot's response appeared instantly:

```markdown
🎭 Planning System 2.0 Engaged

Analyzing request: "user authentication with JWT tokens"

Complexity Detection:
- Keywords detected: authentication, JWT, tokens
- Security implications: HIGH
- Complexity Level: HIGH
- Approach: INCREMENTAL with full DoR/DoD gates

Generating plan...

# Feature Plan: User Authentication with JWT

## Definition of Ready (DoR)

**Requirements:**
- [ ] Authentication flow specified (login/logout/refresh)
- [ ] Token expiration policy defined
- [ ] Refresh token strategy documented
- [ ] Security requirements identified

**Dependencies:**
- [ ] JWT library selected (recommendation: PyJWT)
- [ ] Token storage approach determined (recommendation: Redis)
- [ ] Database schema for users confirmed
- [ ] HTTPS enforcement verified

**Complexity Assessment:**
- Level: HIGH (security-critical feature)
- Approach: Incremental with TDD
- Estimated effort: 8-12 hours

**TDD Approach:**
- RED phase: 23 test scenarios identified
- GREEN phase: Incremental implementation
- REFACTOR phase: Security review mandatory

## Implementation Phases

### Phase 1: RED (Test-Driven Development)
Write failing tests for:
1. Token generation
2. Token validation
3. Token refresh
4. Expiration handling
5. Invalid token handling
6. Security edge cases

### Phase 2: GREEN (Implementation)
Implement in incremental stages:
1. Basic token generation
2. Token validation
3. Refresh mechanism
4. Expiration handling
5. Security hardening

### Phase 3: REFACTOR (Optimization)
- Security audit
- Code quality review (SOLID/DRY/KISS/YAGNI)
- Performance optimization
- Documentation

## Definition of Done (DoD)

**Quality Gates:**
- [ ] All 23 tests passing (100% coverage)
- [ ] Security review completed
- [ ] SKULL rules validated
- [ ] Code quality score ≥ 9/10

**Documentation:**
- [ ] API documentation updated
- [ ] Security considerations documented
- [ ] Usage examples provided

**Validation:**
- [ ] Manual security testing
- [ ] Integration testing
- [ ] Performance benchmarking

---

✅ Plan ready. DoR checklist must be completed before implementation begins.
```

Codenstein stared at the screen.

"It... it auto-detected HIGH complexity," he whispered.

"What?" his wife called from upstairs.

"IT AUTO-DETECTED HIGH COMPLEXITY. I just said 'authentication' and it knew. Security-critical. Incremental approach. Full DoR/DoD gates. TDD mandatory. All automatic."

His phone buzzed. "Is this good or are you panicking?"

"THIS IS REVOLUTIONARY."

![Auto-detection in action](images/auto-detection.png)
*Complexity auto-classification with keyword detection*

## The Validation

He tested it again. Different features:

"Plan: Add user profile page"

```
Complexity Level: LOW
Approach: SKELETON
Minimal gates, basic tests
```

"Plan: Implement payment processing with Stripe"

```
Complexity Level: HIGH
Approach: INCREMENTAL
Security-critical, full DoR/DoD, TDD mandatory
```

"Plan: Add caching layer for API responses"

```
Complexity Level: MEDIUM
Approach: CONDITIONAL
Business logic considerations, suggested TDD
```

Every single one correct. The complexity detection worked. The template selection worked. The DoR/DoD generation worked. The TDD integration worked.

"It's planning better than I plan," he said.

His wife appeared in the doorway—actually in person this time, which meant she'd taken a break from work in Lichfield? No, wait, time zones. It was evening there. "Show me."

He showed her the authentication plan. The automatic complexity detection. The comprehensive DoR checklist. The TDD phase breakdown. The thorough DoD validation.

She read it carefully. "This is more thorough than your wedding planning."

"We didn't really plan our wedding."

"I know. That's my point." She scrolled through the plan. "But this... this has requirements validation, dependency checking, acceptance criteria, quality gates, security review..."

"The AI learned from my mistakes."

"The AI is more organized than you've ever been."

"The AI enforces the discipline I should have had all along."

She studied him. "Should I be worried it's replacing you?"

"It's not replacing me. It's ENHANCING me. I still make the decisions. I still write the code. But now I have a system that ensures I don't skip the important parts. No more 'I'll write tests later.' No more 'I'll document this eventually.' No more 'This seems simple enough to skip planning.'"

"The guardrails you've always needed."

"The guardrails I've always RESISTED. But now they're built into the workflow. Can't skip them without explicitly overriding. And overriding requires justification."

![DoR/DoD gates](images/dor-dod-gates.png)
*Quality gates with validation checkboxes*

## The Real Test

On Friday afternoon, Codenstein needed to implement a new API endpoint. Simple CRUD operation. He would have normally just written it directly—maybe 30 minutes of work.

Instead, he asked Copilot: "Plan: Add endpoint to update user profile information"

Complexity: LOW. Skeleton approach. Minimal gates.

But the plan still included:
- Basic DoR (requirements clear, schema confirmed)
- Test requirements (validation, success cases, error handling)
- Basic DoD (tests passing, endpoint documented)

He followed the plan. Wrote tests first (RED). Implemented the endpoint (GREEN). Refactored for clarity (REFACTOR). Validated against DoD checklist.

Total time: 45 minutes instead of 30.

But: 100% test coverage. Full documentation. No edge cases missed. No security holes. No technical debt.

"Worth it?" Mrs. G asked during their evening call.

"Fifteen extra minutes to ensure quality?" He pulled up his metrics. "Zero production bugs from planned features. Versus three per week from unplanned quick fixes."

"So the planning revolution worked?"

"The planning revolution ENFORCED discipline. I can't skip steps anymore. The system won't let me."

"Good. How much time left?"

He checked the calendar. "Four days. Until Christmas decorations deadline."

"Can you finish?"

He pulled up his progress:
- **Tier 0-2:** Complete
- **TDD Mastery:** Complete
- **Orchestration Pattern:** Complete
- **Planning System 2.0:** Complete

Still needed: ADO Operations, Code Sanitization, System Maintenance integration, Tier 3 Knowledge Library.

"I can finish. I have the patterns now. Everything else is just... applying them systematically."

"That's what planning is for."

"That's what AUTOMATED planning is for." He smiled. "The AI ensures I follow my own best practices."

She laughed. "It's the responsible adult you've always needed."

"It's the responsible adult I've always BEEN. I just needed a system to enforce it consistently."

"Consistently," she repeated. "That's growth."

He looked at the planning manifest on his screen. DoR gates. DoD validation. Complexity classification. TDD integration. All automatic. All enforced. All consistent.

Tomorrow, he'd build the ADO Operations orchestrator—Planning 2.0 but speaking corporate. Then Code Sanitization. Then the final integrations.

Tonight, he'd enjoy the fact that his AI wouldn't let him skip planning anymore.

Even when he tried.

Especially when he tried.

Progress through planning.

---

</div>

<div class="chapter-navigation">
  <a href="../Chapter-06/" class="nav-prev">← Previous: The Great Orchestration</a>
  <a href="../index.html" class="nav-home">📖 Table of Contents</a>
  <a href="../Chapter-08/" class="nav-next">Next: The Enterprise Awakening →</a>
</div>

</div>

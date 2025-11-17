# Interactive Feature Planning Narrative

## For Leadership

Interactive Feature Planning transforms vague ideas into executable roadmaps through guided conversation, similar to consulting with an experienced architect before building.

**Intent Detection** - When you say "plan user authentication," CORTEX recognizes this as a planning request (not immediate implementation) and activates the Work Planner agent.

**Confidence Assessment** - CORTEX evaluates how much detail you provided:
- High confidence (80-100%): "Plan JWT authentication with OAuth2" → Proceeds directly
- Medium confidence (50-79%): "Plan authentication" → Asks 1-2 clarifying questions
- Low confidence (<50%): "Plan something for users" → Interactive clarification session

**Interactive Questions** - CORTEX asks targeted questions to fill gaps: authentication methods, user types, integration requirements, security constraints. You can skip questions or answer "later" for anything uncertain.

**Plan Generation** - Creates a multi-phase implementation plan with tasks, dependencies, risks, and acceptance criteria. Each phase includes specific deliverables and Definition of Done checkpoints.

**Business Impact:** Prevents scope creep, identifies risks early, estimates effort accurately, ensures team alignment before coding starts.

## For Developers

**Architecture Pattern:** Confidence-driven interactive planning with phase breakdown

```
User Request ──▶ Detect Intent (PLAN) ──▶ Assess Confidence
                                               ↓
                                         High (80-100%)
                                           ↓
                                    Direct to Breakdown
                                               ↓
                                         Medium (50-79%)
                                           ↓
                                    Ask 1-2 Questions
                                               ↓
                                         Low (<50%)
                                           ↓
                                    Interactive Session
                                               ↓
                                    Generate Multi-Phase Plan
```

**Confidence Calculation:**
```python
def calculate_confidence(user_request):
    score = 0.0
    
    # Keyword detection (40% weight)
    keywords = {
        'authentication': 0.4,
        'jwt': 0.3,
        'oauth': 0.3,
        'login': 0.2,
        'user': 0.1
    }
    for keyword, weight in keywords.items():
        if keyword in user_request.lower():
            score += weight * 0.4
    
    # Specificity (30% weight)
    specificity = len(user_request.split()) / 20  # normalized
    score += min(specificity, 0.3)
    
    # Context from Tier 1 (30% weight)
    recent_context = get_recent_conversations()
    if has_related_context(recent_context, user_request):
        score += 0.3
    
    return min(score, 1.0)  # cap at 100%
```

**Question Generation:**
```python
def generate_questions(feature, confidence):
    questions = []
    
    # Essential questions (always ask if missing)
    if not has_implementation_details(feature):
        questions.append({
            "category": "implementation",
            "question": "What technologies/frameworks?",
            "examples": ["JWT", "OAuth", "SAML"]
        })
    
    # Conditional questions (ask if medium/low confidence)
    if confidence < 0.8:
        if not has_user_types(feature):
            questions.append({
                "category": "users",
                "question": "Which user types need access?",
                "examples": ["admins", "users", "guests"]
            })
        
        if not has_security_requirements(feature):
            questions.append({
                "category": "security",
                "question": "Any security constraints?",
                "examples": ["2FA", "password policies", "session timeout"]
            })
    
    return questions[:4]  # limit to 4 questions max
```

**Phase Breakdown Algorithm:**
```python
def generate_phases(feature, requirements):
    phases = []
    
    # Phase 1: Foundation (always first)
    phases.append({
        "phase": 1,
        "name": "Foundation & Design",
        "duration_estimate": "30-60 minutes",
        "tasks": [
            "Define requirements",
            "Review existing architecture",
            "Identify integration points",
            "Create test strategy"
        ],
        "success_criteria": [
            "Requirements documented",
            "Architecture sketch created"
        ]
    })
    
    # Phase 2: Core Implementation
    complexity = estimate_complexity(requirements)
    phases.append({
        "phase": 2,
        "name": "Core Implementation (TDD)",
        "duration_estimate": f"{complexity * 60}-{complexity * 90} minutes",
        "tasks": generate_implementation_tasks(requirements),
        "success_criteria": [
            "All tests passing (GREEN)",
            "Zero errors, zero warnings"
        ]
    })
    
    # Phase 3: Integration (if needed)
    if requires_integration(requirements):
        phases.append({
            "phase": 3,
            "name": "Integration & Testing",
            "duration_estimate": "60-90 minutes",
            "tasks": generate_integration_tasks(requirements),
            "success_criteria": [
                "End-to-end tests passing",
                "No regressions detected"
            ]
        })
    
    # Phase 4: Validation (always last)
    phases.append({
        "phase": len(phases) + 1,
        "name": "Validation & Documentation",
        "duration_estimate": "30-45 minutes",
        "tasks": [
            "Run full test suite",
            "Security audit",
            "Update documentation"
        ],
        "success_criteria": [
            "Definition of Done met",
            "Ready for deployment"
        ]
    })
    
    return phases
```

**Risk Analysis:**
```python
def analyze_risks(feature, requirements):
    risks = []
    
    # Technical complexity risks
    if has_external_dependencies(requirements):
        risks.append({
            "type": "dependency",
            "severity": "medium",
            "description": "External API integration required",
            "mitigation": "Create mock services for testing"
        })
    
    # Security risks
    if involves_authentication(feature):
        risks.append({
            "type": "security",
            "severity": "high",
            "description": "Password storage and session management",
            "mitigation": "Follow OWASP best practices, use bcrypt"
        })
    
    # Performance risks
    if estimated_load_high(requirements):
        risks.append({
            "type": "performance",
            "severity": "medium",
            "description": "High concurrent user load expected",
            "mitigation": "Implement caching, connection pooling"
        })
    
    return risks
```

**Plan Output Format:**
```yaml
plan:
  feature: "User Authentication"
  confidence: 0.72
  complexity: "medium"
  estimated_hours: 4.5
  
  phases:
    - phase: 1
      name: "Foundation & Design"
      tasks: [...]
      success_criteria: [...]
    
    - phase: 2
      name: "Core Implementation"
      tasks: [...]
      success_criteria: [...]
  
  risks:
    - type: "security"
      severity: "high"
      description: "Password storage"
      mitigation: "Use bcrypt + salting"
  
  acceptance_criteria:
    - "Users can login with email/password"
    - "OAuth works for Google and GitHub"
    - "2FA enabled for admin users"
```

## Key Takeaways

1. **Adaptive questioning** - Asks more questions for vague requests
2. **Phase-based planning** - Breaks work into logical stages
3. **Risk identification** - Flags potential issues early
4. **Time estimation** - Realistic effort estimates per phase
5. **Executable plans** - Ready to hand off to Code Executor

## Usage Scenarios

**Scenario 1: High Confidence (Detailed Request)**
```
User: "Plan JWT authentication with OAuth2 for Google/GitHub, 
       including 2FA for admins"

CORTEX Confidence: 92% (high)
Action: Proceeds directly to phase breakdown
Questions: 0 (all details provided)

Plan Generated:
  - Phase 1: JWT setup (30 min)
  - Phase 2: OAuth integration (90 min)
  - Phase 3: 2FA implementation (60 min)
  - Phase 4: Testing & validation (45 min)
  Total: 4.5 hours
```

**Scenario 2: Medium Confidence (Some Details)**
```
User: "Plan authentication system"

CORTEX Confidence: 72% (medium)
Action: Ask 2 clarifying questions

Questions:
  1. "What authentication methods?" (JWT, OAuth, SAML?)
  2. "Any specific security requirements?" (2FA, SSO?)

User Answers:
  1. "JWT and OAuth"
  2. "2FA for admins"

Plan Generated: (same as Scenario 1)
```

**Scenario 3: Low Confidence (Vague Request)**
```
User: "Plan something for users"

CORTEX Confidence: 35% (low)
Action: Interactive clarification session

Questions (4 asked):
  1. "What user capability?" (auth, profiles, permissions?)
  2. "What problem does this solve?"
  3. "Any existing systems to integrate?"
  4. "Technical constraints?" (framework, database?)

After clarification:
  Feature refined: "User authentication with JWT"
  Confidence: 85%
  Plan Generated: (same as Scenario 1)
```

**Scenario 4: Risk Identification**
```
User: "Plan payment processing with external API"

CORTEX Analyzes:
  - External dependency: HIGH RISK
  - Financial data: HIGH RISK
  - PCI compliance: HIGH RISK

Risks Flagged:
  1. External API failure (use circuit breaker)
  2. Payment data security (never store card numbers)
  3. PCI DSS compliance (use certified gateway)
  4. Idempotency (prevent double charges)

Recommendation:
  "Consider using Stripe/PayPal SDK (certified)
   rather than direct API integration."
```

*Version: 1.0*  
*Last Updated: November 17, 2025*

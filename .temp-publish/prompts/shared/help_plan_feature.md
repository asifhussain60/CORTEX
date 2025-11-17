# CORTEX Interactive Feature Planning

**Module:** EPM (Execution Plan Module)  
**Version:** 1.0  
**Status:** ✅ Production Ready  
**Agent:** Work Planner (Right Brain - Strategic)

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms

---

## 🚨 ACTIVATION TRIGGERS

**This module activates automatically when you say:**

| Trigger Phrase | Example Usage | Context Detection |
|----------------|---------------|-------------------|
| `plan` | "plan authentication" | General planning |
| `let's plan` | "let's plan a feature" | Conversational planning |
| `plan a feature` | "plan a feature for users" | Explicit feature planning |
| `plan this` | "plan this ADO enhancement" | Contextual planning |
| `help me plan` | "help me plan the API" | Assistance request |
| `planning` | "planning user dashboard" | Activity-based |
| `feature planning` | "feature planning session" | Explicit workflow |
| `i want to plan` | "i want to plan deployment" | Intent declaration |

**Domain-Specific Context:**
- "let's plan an ADO feature" → Planning workflow + Azure DevOps context
- "plan AWS infrastructure" → Planning workflow + AWS context
- "help me plan Kubernetes migration" → Planning workflow + K8s context

**No separate triggers needed for domain specialization** - CORTEX detects context naturally within the planning workflow.

**Configuration:** Triggers defined in `cortex-brain/response-templates.yaml` under `routing.planning_triggers`

**When activated:**
1. CORTEX loads this module (#file:help_plan_feature.md)
2. Work Planner agent activates (Right Brain - Strategic)
3. Interactive planning workflow begins
4. Confidence assessment determines question depth
5. Phase-based plan generated and saved

---

## 🎯 What Is Feature Planning?

Interactive feature planning helps you break down complex features into actionable tasks through a guided conversation. CORTEX asks clarifying questions, analyzes requirements, and generates a structured roadmap you can execute immediately.

**What you get:**
- ✅ Phase-based breakdown of work
- ✅ Task dependencies identified
- ✅ Risk analysis and mitigation strategies
- ✅ Acceptance criteria for each phase
- ✅ Executable roadmap saved for future reference

---

## 🚀 How to Use It

### Basic Usage (Natural Language)

Just tell CORTEX you want to plan something:

```
plan a feature
let's plan authentication
help me plan user dashboard
I want to plan a new API endpoint
```

**No slash commands needed.** CORTEX automatically detects planning intent and activates the Work Planner agent.

### What Happens Next?

**1. Intent Detection (Automatic)**
```
User: "plan a feature"
      ↓
CORTEX detects PLAN intent
      ↓
Activates Work Planner agent
```

**2. Confidence Assessment**

CORTEX evaluates how much detail you provided:

| Confidence Level | User Input Example | What CORTEX Does |
|------------------|-------------------|------------------|
| **High (80-100%)** | "Plan JWT authentication with OAuth2 integration" | Proceeds directly to breakdown |
| **Medium (50-79%)** | "Plan authentication system" | Asks 1-2 confirming questions |
| **Low (<50%)** | "Plan a feature" | Asks detailed clarifying questions |

**3. Interactive Session**

CORTEX guides you through planning:

```markdown
🧠 CORTEX Interactive Planning

🎯 Understanding: You want to plan a new authentication system

⚠️ Challenge: ✓ Accept
   Planning authentication upfront helps identify security 
   requirements and integration points early.

💬 Response: I'll help you break this down into phases. 
Let me ask a few questions first:

📋 Questions:
   1. What authentication methods? (JWT, OAuth, SAML, etc.)
   2. Which user types need access? (admins, users, guests)
   3. Integration requirements? (existing SSO, third-party services)
   4. Security constraints? (2FA, password policies, session management)

🔍 Next Steps:
   1. Answer questions above (or skip any with "skip")
   2. Review generated plan
   3. Begin execution when ready
```

**4. Plan Generation**

After gathering requirements, CORTEX generates:

```markdown
# Authentication System Implementation Plan

## Phase 1: Foundation (Week 1)
☐ Task 1.1: Design authentication architecture
☐ Task 1.2: Select JWT library and configure
☐ Task 1.3: Create user model and database schema
☐ Task 1.4: Implement password hashing utilities

**Dependencies:** None (start immediately)
**Risks:** Token expiration strategy needs early decision

## Phase 2: Core Authentication (Week 2)
☐ Task 2.1: Implement login endpoint
☐ Task 2.2: Implement token generation/validation
☐ Task 2.3: Add logout and token refresh
☐ Task 2.4: Create authentication middleware

**Dependencies:** Phase 1 complete
**Risks:** Session management complexity

## Phase 3: OAuth Integration (Week 3)
☐ Task 3.1: Configure OAuth providers (Google, GitHub)
☐ Task 3.2: Implement OAuth callback handlers
☐ Task 3.3: Link OAuth accounts to user profiles
☐ Task 3.4: Test OAuth flow end-to-end

**Dependencies:** Phase 2 complete
**Risks:** OAuth provider API changes

## Phase 4: Security & Testing (Week 4)
☐ Task 4.1: Add 2FA support
☐ Task 4.2: Implement rate limiting
☐ Task 4.3: Security audit and penetration testing
☐ Task 4.4: Performance testing under load

**Dependencies:** Phase 3 complete
**Risks:** Performance bottlenecks under load

📝 Acceptance Criteria:
   - Users can log in with email/password
   - OAuth login works for Google and GitHub
   - 2FA can be enabled per user
   - Sessions expire after 24 hours
   - Rate limiting prevents brute force attacks

🎯 Execution Ready: Say "start Phase 1" to begin implementation
```

---

## 🎓 Example Sessions

### Example 1: High Confidence (Detailed Request)

**User:** "Plan JWT authentication with OAuth2 integration for Google and GitHub, including 2FA support"

**CORTEX Response:**
```markdown
🧠 **CORTEX Interactive Planning**
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX

🎯 **My Understanding Of Your Request:**
   You want JWT authentication with OAuth2 (Google, GitHub) and 2FA

⚠️ **Challenge:** ✓ **Accept**
   You've provided clear requirements. I can proceed with planning.

💬 **Response:**
   I'll create a 4-phase roadmap:
   - Phase 1: JWT foundation
   - Phase 2: OAuth integration
   - Phase 3: 2FA implementation
   - Phase 4: Security hardening

   [Generated plan with 15-20 tasks across 4 phases]

� **Your Request:** JWT authentication with OAuth2 and 2FA

�🔍 **Next Steps:**
   ☐ Phase 1: JWT Foundation (Tasks 1-4)
   ☐ Phase 2: OAuth Integration (Tasks 5-8)
   ☐ Phase 3: 2FA Implementation (Tasks 9-12)
   ☐ Phase 4: Security & Testing (Tasks 13-16)
   
   Ready to proceed with all phases, or focus on a specific phase first?
```

### Example 2: Low Confidence (Vague Request)

**User:** "plan something for users"

**CORTEX Response:**
```markdown
🧠 **CORTEX Interactive Planning**
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX

🎯 **My Understanding Of Your Request:**
   You want to plan a user-related feature

⚠️ **Challenge:** ⚡ **Challenge**
   "Something for users" is quite broad. Let me ask questions to understand what you're trying to achieve.

💬 **Response:**
   I need more details to create an effective plan. Here are some clarifying questions:

   1. What user capability are you planning? (authentication, profiles, permissions, notifications, etc.)
   2. What problem does this solve for users?
   3. Are there existing user features to integrate with?
   4. Any specific technical constraints? (database, APIs, frameworks)
   5. Timeline or urgency? (MVP vs full-featured)

   Please answer what you can, or type "skip" for any question.

📝 **Your Request:** Plan something for users

🔍 **Next Steps:**
   1. Answer questions above
   2. I'll generate a tailored plan
   3. Review and refine together
```

---

## 🔧 Advanced Features

### Skipping Questions

If you don't know the answer or want to decide later:

```
User: "skip question 3"
or
User: "skip" (skips current question)
```

CORTEX will work with the information provided and flag unknowns in the plan.

### Refining Plans

After seeing the initial plan:

```
User: "add API rate limiting to Phase 2"
User: "split Phase 3 into two phases"
User: "remove 2FA, we'll add that later"
```

CORTEX updates the plan based on your feedback.

### Continuing Later

Plans are saved automatically. Resume anytime:

```
User: "continue" or "resume"
      ↓
CORTEX: "I see you were planning authentication. 
         Phase 1 is complete. Ready for Phase 2?"
```

### Executing Plans

When ready to implement:

```
User: "start Phase 1" or "let's begin"
      ↓
CORTEX switches to Executor agent
      ↓
Implements tasks with full context from plan
```

---

## 🏗️ How It Works (Technical)

### Agent Coordination

```
User Input ("plan a feature")
        ↓
Intent Detector (identifies PLAN intent)
        ↓
Interactive Planner Agent (assesses confidence)
        ↓
┌─────────────────────────────────────┐
│  High Confidence (80-100%)          │
│  → Activate Work Planner directly   │
└─────────────────────────────────────┘
        ↓
Work Planner Agent
        ↓
┌──────────────────────────────────────┐
│  Phase 1: Discovery                  │
│  • Ask clarifying questions          │
│  • Search Knowledge Graph for        │
│    similar past features             │
│  • Consult Architect for feasibility │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│  Phase 2: Breakdown                  │
│  • Decompose into phases/milestones  │
│  • Identify tasks within each phase  │
│  • Map dependencies                  │
│  • Estimate complexity               │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│  Phase 3: Risk Analysis              │
│  • Identify technical risks          │
│  • Suggest mitigation strategies     │
│  • Flag unknown unknowns             │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│  Phase 4: Roadmap Generation         │
│  • Generate phase-based roadmap      │
│  • Add acceptance criteria           │
│  • Save to Tier 1 memory             │
│  • Create markdown document          │
└──────────────────────────────────────┘
        ↓
Plan saved and ready for execution
```

### Storage

Plans are stored in two locations:

**1. Tier 1 Working Memory (SQLite)**
- Linked to conversation context
- Metadata: feature name, status, phases
- Searchable for "continue" operations

**2. File System**
- Location: `cortex-brain/feature-plans/`
- Format: Markdown
- Filename: `{feature-name}-{timestamp}.md`
- Human-readable backup

### Knowledge Graph Integration (Track C - Optional)

Future enhancement:
- Completed plans stored in Tier 2
- Pattern extraction (successful approaches)
- Adaptive questioning (skip predictable questions)
- User preference learning

---

## 📊 Success Metrics

**Planning Session Quality:**
- Average questions asked: 3-5
- Average tasks generated: 12-20
- Average phases: 3-5
- Confidence accuracy: 90%+

**User Satisfaction:**
- Plans are actionable (ready to execute)
- Dependencies clearly identified
- Risks highlighted with mitigation
- Acceptance criteria well-defined

---

## 🎓 Best Practices

### For Users

**1. Start with what you know:**
```
✅ "Plan user authentication with JWT"
vs
❌ "Plan something"
```

**2. Be specific about constraints:**
```
✅ "Must integrate with existing PostgreSQL database"
✅ "Need to deploy by end of month"
✅ "Team has React experience, not Vue"
```

**3. Use planning iteratively:**
```
Phase 1 → Plan → Execute → Learn
         ↓
Phase 2 → Plan → Execute → Learn
         ↓
Phase 3 → Plan → Execute → Learn
```

**4. Don't over-plan:**
```
✅ Plan 1-2 weeks of work at a time
❌ Plan entire 6-month roadmap upfront
```

### For Developers

**1. Keep questions focused:**
- Max 5 questions per session
- Ask about unknowns that impact architecture
- Skip nice-to-knows (can be answered later)

**2. Structure plans for execution:**
- Each phase should be independently executable
- Tasks should be atomic (completable in 1-4 hours)
- Dependencies should be explicit

**3. Flag risks early:**
- Technical unknowns
- External dependencies (APIs, services)
- Performance concerns
- Security implications

---

## ⚠️ Limitations

**Current Limitations:**
1. **No automatic task tracking** - Plans are documents, not live task trackers
2. **No time estimation** - Complexity indicated, but not time estimates
3. **No resource allocation** - Doesn't assign tasks to team members
4. **No Jira/GitHub integration** - Plans must be manually copied to project management tools

**Workarounds:**
1. Use `continue` to track progress conversationally
2. Ask CORTEX to estimate after planning: "estimate time for Phase 1"
3. Copy plan to your project management tool
4. Use GitHub issues with plan as template

**Future Enhancements (Track C+):**
- [ ] Learn from completed plans (Tier 2 integration)
- [ ] Adaptive questioning (skip predictable)
- [ ] Export to Jira/GitHub Issues
- [ ] Time estimation based on past work
- [ ] Real-time task tracking

---

## 🔗 Related Documentation

| Document | Purpose |
|----------|---------|
| `CORTEX-2.0-FEATURE-PLANNING.md` | Full design specification |
| `CORTEX-2.1-TRACK-A-COMPLETE.md` | Implementation completion report |
| `CORTEX-2.1-TRACK-B-COMPLETE.md` | Quality & polish completion report |
| `agents-guide.md` | Understanding CORTEX agents |
| `operations-reference.md` | All CORTEX operations |

---

## 🆘 Troubleshooting

**Issue:** CORTEX doesn't recognize planning request

**Solution:**
```
✅ Use explicit keywords: "plan", "planning", "feature"
✅ Try: "let's plan [feature name]"
❌ Avoid: "help me with something"
```

---

**Issue:** Too many questions asked

**Solution:**
```
✅ Provide more detail upfront
✅ Skip questions you don't need: "skip"
✅ Request direct plan: "skip questions, just create a plan"
```

---

**Issue:** Plan too detailed or too vague

**Solution:**
```
✅ Request adjustment: "make it more high-level"
✅ Or: "add more detail to Phase 2"
✅ Or: "break Phase 3 into smaller tasks"
```

---

**Issue:** Can't find saved plan

**Solution:**
```
✅ Say "continue" - CORTEX loads from Tier 1 memory
✅ Check: `cortex-brain/feature-plans/` directory
✅ Or: "show me my recent plans"
```

---

## 📚 Quick Reference

| Command | What It Does |
|---------|--------------|
| `plan a feature` | Start interactive planning session |
| `plan [feature name]` | Start planning specific feature |
| `skip` | Skip current question |
| `continue` | Resume saved planning session |
| `start Phase 1` | Begin executing planned work |
| `show plan` | Display current/saved plan |
| `refine plan` | Modify existing plan |

---

## ✅ Success Checklist

After a planning session, you should have:

- [ ] Clear feature name and description
- [ ] 3-5 phases with logical progression
- [ ] 12-20 atomic tasks across all phases
- [ ] Dependencies identified between phases
- [ ] Risks flagged with mitigation strategies
- [ ] Acceptance criteria defined
- [ ] Plan saved for future reference
- [ ] Ready to execute Phase 1

**If any checkbox is unchecked, ask CORTEX to address it:**
```
"Add acceptance criteria to the plan"
"Identify dependencies between tasks"
"Flag potential risks for Phase 3"
```

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Version:** 1.0 (CORTEX 2.1)  
**Last Updated:** November 13, 2025  
**Status:** ✅ Production Ready

*This module is part of the CORTEX 2.1 Interactive Planning release.*

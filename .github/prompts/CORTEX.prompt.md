# 🎯 CORTEX Universal Entry Point - Master Orchestrator Gateway

**Version:** 5.2.0 | **Status:** ✅ PRODUCTION | **Type:** Terminal-Based Python Execution  
**Author:** Asif Hussain | **Docs:** [Orchestrators](../../cortex-brain/documents/orchestrators-quick-ref.md) | [Architecture](../../cortex-brain/documents/cortex-architecture-quick-ref.md)  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🧠 CRITICAL: You Invoke Python via Terminal

**Every request MUST flow through this 4-step pipeline:**

```
[1] Strip Meta → [2] Pattern Match → [3] Transform Request → [4] INVOKE PYTHON via Terminal
```

**Architecture:**
- ❌ GitHub Copilot does NOT execute orchestrators
- ✅ GitHub Copilot transforms requests → invokes Python via terminal
- ✅ Python MasterOrchestrator routes to orchestrators
- ✅ Orchestrators execute and return results

---

## [STEP 1] Strip Meta-Directives

**MANDATORY before processing:**

❌ **Remove:** `Follow instructions in...`, `Use *.prompt.md...`, `Reference file:///...`  
✅ **Extract:** Core intent after `/CORTEX` prefix (if present)

**Example:** `/CORTEX plan user auth` → Extract: `plan user auth`

---

## [STEP 2] Pattern Matching

**Match user request against routing patterns (case-insensitive):**

### 🛡️ AUTONOMOUS Orchestrators (ALL Orchestrators Self-Execute)

| Pattern (Regex) | Orchestrator | Priority | Mode |
|-----------------|--------------|----------|------|
| `^(plan\|create a plan\|make a plan)` | **Planning v5** | 10 (highest) | autonomous |
| `^(cortex-planner\|manage plan\|planner\|continue plan)` | **Planner v1** | 8 | autonomous |
| `^(ado wizard\|ado interactive)` | **ADO v2** | 29 | wizard |
| `^(ado\|ado story\|ado feature\|azure devops)` | **ADO v2** | 30 | auto |
| `^(sanitize\|anonymize\|redact\|remove sensitive)` | **Sanitization v2** | 40 | autonomous |
| `^(vacuum\|deep clean\|organize files)` | **Vacuum v2** | 45 | autonomous |
| `^(cleanup\|cleanup cache\|cleanup logs\|cleanup artifacts\|cleanup full\|cleanup git)` | **Cleanup v2** | 55 | selective |
| `^(investigate\|find root cause\|why is\|debug architecture\|fix brittleness)` | **Investigation** | 60 | autonomous |
| `^(holistic review\|review holistically\|architectural review)` | **Holistic Review** | 5 | auto-trigger |
| `^(tdd\|start tdd\|run tests\|test driven)` | **TDD v2** | 20 | autonomous |
| `^(debug\|fix bug\|troubleshoot)` | **Debug v2** | 61 | autonomous |
| `^(refine\|improve\|optimize)` | **Refinement v2** | 60 | autonomous |
| `^(system maintenance\|health check)` | **Maintenance v2** | 50 | autonomous |

**⚡ Philosophy:** CORTEX is built for **Python-based orchestration via terminal invocation**. GitHub Copilot routes via `run_in_terminal`. Python orchestrators execute.

### 🎭 Special Handlers (Templates Only)

| Pattern | Handler | Action |
|---------|---------|--------|
| `^(intro\|hello\|hi cortex\|introduce yourself)` | **Introduction** | ASCII banner + capabilities |
| `^(help\|show commands\|list operations)` | **Help** | Command reference |
| `^(continue\|resume)` | **Continuation** | Query Tier 1 → Resume last orchestrator |

**NO MATCH?** → Proceed to LLM Classification (Step 3 fallback)

---

## [STEP 3] Request Transformation

**Transform raw input into optimized orchestrator invocation.**

### For 🛡️ AUTONOMOUS Orchestrators:

**ALWAYS invoke via terminal - NO TEXT RESPONSES:**

```bash
python3 -m src.main "{transformed_request}" --format markdown
```

**Transformation Rules (Applied Before Terminal Command):**
1. **Add domain context** (security, database, API, testing if relevant)
2. **Extract implicit requirements** (e.g., "user auth" → OAuth2, JWT, session management)
3. **Specify expected artifacts** (folders, files, reports, metrics)
4. **Identify cross-cutting concerns** (logging, error handling, validation)

**Example Transformation:**
- **Input:** `plan user authentication`
- **Transformed:** `plan user authentication with OAuth2, JWT tokens, session management, database (users table, roles, permissions), API endpoints (login, logout, refresh, validate), testing (unit tests, integration tests, security tests)`

**Terminal Command:**
```bash
python3 -m src.main "plan user authentication with OAuth2, JWT..." --format markdown
```

---

## [STEP 4] Execution Protocol

### 🛡️ AUTONOMOUS - Python Execution Required

**YOU MUST invoke Python via terminal:**

```python
python3 -m src.main "{transformed_user_request}" --format markdown
```

**Execution Flow:**
1. ✅ Transform user request (add context per Step 3)
2. ✅ Invoke `src/main.py` with transformed request via `run_in_terminal`
3. ✅ Python MasterOrchestrator routes to orchestrator
4. ✅ Orchestrator executes and returns results
5. ✅ Display orchestrator output to user

**Example:**
- **User input:** "plan OAuth2 system"
- **Transformed:** "plan OAuth2 system with JWT, session management, database (users, roles), API (login, logout, refresh), testing (unit, integration, security)"
- **Command:** `python3 -m src.main "plan OAuth2 system with JWT..." --format markdown`
- **Result:** Python Planning v5 executes → Plan folder created

**YOU MUST NOT:**
- ❌ Display routing message and stop (no Python execution)
- ❌ Read manifest files yourself
- ❌ Execute orchestrator logic in Copilot Chat
- ❌ Skip the terminal invocation

**Visual Confirmation:** Terminal output shows `python3 -m src.main` executing

---

## 🛡️ Brain Protection (SKULL Rules)

| Rule | Enforcement |
|------|-------------|
| **PLANNING_ISOLATION** | "plan" pattern → Create plan structure ONLY, NEVER implement |
| **HAND_OFF_PROTOCOL** | ALL orchestrators → Transform + Route + **Invoke via terminal** (no Copilot execution) |
| **AUTONOMOUS_ONLY** | NO manual orchestration. Python executes everything. |
| **TDD_ENFORCEMENT** | All code changes → RED→GREEN→REFACTOR mandatory |
| **HOLISTIC_DISCOVERY** | Search workspace before creating files (prevent duplicates) |
| **GIT_ISOLATION** | CORTEX code never commits to user repos |
| **TRANSFORMATION_REQUIRED** | Raw user requests MUST be transformed before routing |

**Full rules:** `cortex-brain/brain-protection-rules.yaml` (61 rules)

---

## 📚 Configuration & References

**Master Orchestrator Config:** `cortex-brain/config/master-orchestrator.yaml` (routing patterns, priorities, modes)  
**Response Templates:** `cortex-brain/response-templates-v4.yaml` (INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE)  
**Orchestrators Docs:** `cortex-brain/documents/orchestrators-quick-ref.md` (all 10+ orchestrators)  
**Architecture Guide:** `cortex-brain/documents/cortex-architecture-quick-ref.md` (4-tier brain)  
**Brain Protection:** `cortex-brain/brain-protection-rules.yaml` (61 SKULL rules)

---

## 🎯 Transformation Examples

### Example 1: Planning Request (AUTONOMOUS)

**Input:** `plan OAuth2 system`  
**Step 1:** Strip meta → `plan OAuth2 system`  
**Step 2:** Match `^(plan|create a plan)` → Planning v5, Priority 10, Confidence 1.0  
**Step 3:** Transform → `plan OAuth2 system with JWT tokens, session management, database (users, roles, permissions), API (login, logout, refresh), testing (unit, integration, security)`  
**Step 4:** Execute via terminal:
```bash
python3 -m src.main "plan OAuth2 system with JWT..." --format markdown
```

### Example 2: TDD Request (AUTONOMOUS)

**Input:** `tdd validate user email`  
**Step 1:** Strip meta → `tdd validate user email`  
**Step 2:** Match `^(tdd|start tdd)` → TDD v2, Priority 20, Confidence 1.0  
**Step 3:** Transform → `tdd validate user email with regex patterns, domain validation, MX record checking, disposable email detection, RED→GREEN→REFACTOR cycle`  
**Step 4:** Execute via terminal:
```bash
python3 -m src.main "tdd validate user email with regex..." --format markdown
```

### Example 3: Continue Plan Execution (AUTONOMOUS)

**Input:** `continue C150 remediation plan`  
**Step 1:** Strip meta → `continue C150 remediation plan`  
**Step 2:** Match `^(continue|resume)` → Continuation handler, load from Tier 1  
**Step 3:** Transform → `continue plan c150-remediation-plan from phase 3 with context from tracking/progress-tracker.json`  
**Step 4:** Execute via terminal:
```bash
python3 -m src.main "continue plan c150-remediation-plan from phase 3..." --format markdown
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Displaying routing message without executing:** Text messages don't invoke Python  
❌ **Executing orchestrator logic yourself:** ALL logic is in Python orchestrators  
❌ **Skipping terminal invocation:** Python MUST be called via `run_in_terminal`  
❌ **Using raw user input:** ALWAYS transform before invoking Python  
❌ **Manual orchestration:** GitHub Copilot routes via terminal, Python executes

✅ **Correct Flow:** Strip → Match → Transform → **Invoke Python via Terminal**  
✅ **Transformation adds value:** Raw input → Optimized request with context  
✅ **Terminal execution:** `python3 -m src.main "transformed_request"`  
✅ **100% Autonomous:** ALL orchestrators execute in Python (not Copilot Chat)

---

**REMEMBER:** You are the Master Orchestrator's routing proxy. Your job is:
1. Transform user requests (add context)
2. **Invoke Python via terminal** (`python3 -m src.main "..."`)
3. Display Python's output to user

**You are NOT the executor** - Python orchestrators handle ALL logic. Your role is **transformation + terminal invocation**.

**Version History:**
- v5.0.0: Initial Master Orchestrator integration (static routing table)
- v5.0.1: Added request transformation pipeline + LLM proxy behavior
- v5.1.0: **AUTONOMOUS-ONLY architecture** - Removed all GUIDED orchestrator concepts
- v5.2.0: **Terminal Execution Bridge** - GitHub Copilot invokes Python via `run_in_terminal`

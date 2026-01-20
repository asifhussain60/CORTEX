# CORTEX Deployment Strategy: The Right Architecture

**Document Type:** Strategic Architecture Decision  
**Audience:** Technical Leadership & Development Team  
**Date:** 2026-01-19  
**Status:** Challenge + Recommendation  

---

## THE PROBLEM WITH CURRENT DESIGN

The cortex-master.yaml describes **CORTEX cloned INTO each parent repo** as a CORTEX/ folder:

```
company-repo/
├── src/
├── tests/
└── CORTEX/                    ← CORTEX lives here (WRONG)
    ├── cortex (CLI)
    ├── cortex_brain/
    └── governance.db
```

**Why this fails:**
- ❌ CORTEX duplicated across N repos → N independent versions, governance.db fragmentation
- ❌ Updates require `cortex upgrade` in EACH repo (operational burden)
- ❌ Inconsistent intelligence across company (some repos v2.5, others v2.8)
- ❌ Governance audit trail split across multiple databases
- ❌ Zero reuse of MCP tools, orchestrators, workflows
- ❌ Scales poorly (100 repos = 100 CORTEX installations to maintain)

---

## THE RIGHT ARCHITECTURE

### **Single Deployment Strategy**

```
◆ cortex-ai/cortex (Top-Level Repo)
  ├── Core system (orchestrators, MCP tools, workflows)
  ├── Brain tiers (governance, knowledge)
  ├── Single governance.db (source of truth)
  ├── One upgrade, one version, one audit trail
  └── [All 100% CORTEX functionality]

◇ company-repo-1 (Any repo)
  ├── .git/
  ├── src/
  ├── tests/
  └── .github/prompts/CORTEX.prompt    ← Lightweight entry point (1 file)

◇ company-repo-2 (Any repo)
  ├── .git/
  ├── src/
  └── .github/prompts/CORTEX.prompt    ← Same reference (1 file)

◇ company-repo-N (Any repo)
  └── .github/prompts/CORTEX.prompt    ← Same reference (1 file)
```

### **How It Works**

```
USER IN ANY REPO:
  1. copy .github/prompts/CORTEX.prompt (from cortex-ai/cortex repo)
  2. Add to GitHub Copilot instructions: @cortex

CORTEX ACTIVATION:
  ├─ Copilot reads CORTEX.prompt from local repo
  ├─ CORTEX.prompt references cortex-ai/cortex (via GitHub URL)
  ├─ Prompt fetches latest intelligence (orchestrators, tools, workflows)
  ├─ All logic runs in Copilot (MCP protocol)
  └─ Works on ANY repo, ZERO local installation

CORTEX UPGRADE:
  ├─ cortex-ai/cortex main branch updates
  └─ NEXT TIME user runs @cortex → automatically pulls latest
     (No manual `cortex upgrade` command needed per repo)

FEEDBACK & INTELLIGENCE:
  ├─ Copilot captures operational data (execution time, errors, user feedback)
  ├─ Batched and sent to cortex-ai/cortex telemetry endpoint
  ├─ Single source of truth for all company operations
  └─ Intelligence improvements deployed once, available everywhere
```

---

## ONE-STEP DEPLOYMENT PATTERN

### **For Users (ANY repo)**

```
Step 1: Add CORTEX to your repo
$ cp https://raw.githubusercontent.com/cortex-ai/cortex/main/.github/prompts/CORTEX.prompt \
       .github/prompts/CORTEX.prompt

Step 2: Update .github/copilot-instructions.md
$ echo '@cortex' >> .github/copilot-instructions.md

Step 3: Use in Copilot
@cortex analyze my code

DONE. Everything else is automatic.
```

### **For CORTEX Development Team**

```
Step 1: Update cortex-ai/cortex repo (main branch)
├─ Add new orchestrator
├─ Add new MCP tool
├─ Update brain tiers
└─ Push to main

Step 2: No additional steps needed
├─ CORTEX.prompt in all repos automatically references @latest
├─ Next @cortex invocation pulls new intelligence
├─ All users get benefits immediately
└─ Single upgrade, global availability
```

---

## ARCHITECTURE COMPARISON: WRONG vs. RIGHT

| Aspect | Current Design (WRONG) | Proposed Design (RIGHT) |
|--------|------------------------|------------------------|
| **Deployment** | Clone full CORTEX into each repo | One-file setup (CORTEX.prompt) |
| **Versions** | N independent versions | One canonical version |
| **Governance DB** | N fragmented databases | One source of truth |
| **Upgrade burden** | Manual `cortex upgrade` × N repos | Automatic on next @cortex call |
| **Intelligence distribution** | Each repo needs sync | Instant availability everywhere |
| **MCP tools** | Registered per repo | Registered once, used everywhere |
| **Operational data** | Split across N telemetry streams | Single unified telemetry |
| **Scalability** | O(N) overhead | O(1) overhead |
| **User friction** | High (setup per repo) | Low (one-time reference) |
| **Governance consistency** | Fragmented | Unified |
| **Audit trail** | Audit trails scattered | Single hash chain |

---

## DETAILED ONE-STEP WORKFLOW

### **What Happens When User Does `@cortex analyze my code`**

```
User invokes: @cortex analyze my code

┌─ GitHub Copilot receives request
├─ Loads .github/prompts/CORTEX.prompt (from user's repo)
│
├─ CORTEX.prompt contains:
│  ├─ Orchestrator definitions (Master, LENS, ResponseComposer, etc.)
│  ├─ MCP tool registry (with pointers to cortex-ai/cortex)
│  ├─ Governance rules (CORE-001 through CORE-037)
│  ├─ Response templates
│  └─ Instructions for intent routing + complexity scoring
│
├─ Copilot executes CORTEX orchestration logic (in-context, fast)
│  ├─ Parse user intent ("analyze my code")
│  ├─ Route to Master Orchestrator
│  ├─ Classify complexity (tier-0, tier-1, tier-2)
│  ├─ Select appropriate orchestrator pattern
│  └─ Invoke MCP tools (if needed)
│
├─ MCP tools execute
│  ├─ Tool: @syntax-check (from cortex-ai/cortex repo)
│  ├─ Tool: @ast-parse
│  └─ Tool: @semantic-analysis
│
├─ Response composed using templates
│
├─ Operational telemetry captured:
│  ├─ Execution time: 1250ms
│  ├─ Tools used: [syntax-check, ast-parse]
│  ├─ Orchestrator: MasterOrchestrator
│  ├─ Complexity: tier-1
│  ├─ Success: true
│  └─ User environment: python-3.11, macos-14
│
└─ Result displayed in chat
   ├─ [CORTEX Response Format]
   ├─ Formatted output
   ├─ Governance markers
   └─ Next steps
```

### **When Telemetry Needs Transmission**

```
Copilot batches telemetry (weekly/monthly)
├─ No raw user code
├─ No secrets
├─ Only aggregates:
│  ├─ Tool execution times
│  ├─ Error categories
│  ├─ Orchestrator usage patterns
│  └─ Environment signatures
│
Send to cortex-ai/cortex/telemetry endpoint
├─ Encrypted HTTPS
├─ User consent verified (30-day rolling)
├─ Transmission logged locally
└─ Sent → processed → GitHub issue auto-creation

Team reviews telemetry insights
├─ "Tool X is timing out in 8% of deployments"
├─ "New intent class detected: config-analysis"
├─ "Performance degradation in LENS stage 3"
└─ Prioritized in cortex-ai/cortex backlog

Team implements fix → pushed to main
├─ Next @cortex call pulls updated intelligence
└─ All users immediately benefit
```

---

## SINGLE STRATEGY: THE IMPLEMENTATION

### **Phase 1: CORTEX Standalone Repo Setup**
- Consolidate CORTEX into `cortex-ai/cortex` (top-level, independently versioned)
- Implement `cortex-ai/cortex/.github/prompts/CORTEX.prompt`
- Define MCP tool registry (refs to cortex-ai/cortex/tools)
- Create telemetry endpoint (`cortex-ai/cortex/api/telemetry`)

### **Phase 2: Child Repo Integration (Ultra-Lightweight)**
- Create reference template `.github/prompts/CORTEX.prompt.template`
- Template points to `cortex-ai/cortex/main/...` (always latest)
- Docs: "To use CORTEX, copy this one file to your repo"
- No installation scripts, no CLI downloads, no local state

### **Phase 3: Copilot Chat Integration**
- CORTEX.prompt loaded automatically by Copilot when invoked
- Inline intelligence updates shown in chat (new tools, workflows)
- Feedback captured transparently (no friction)
- Results formatted per governance rules

### **Phase 4: Telemetry & Intelligence Loop**
- Batch telemetry collection from all repos
- Server-side aggregation (no raw data retained)
- GitHub issues auto-created from patterns
- Team development prioritized by real impact

---

## BUSINESS VALUE ALIGNMENT

| Stakeholder | Benefits |
|-------------|----------|
| **Users** | One-file setup, no maintenance, automatic updates, instant intelligence |
| **CORTEX Team** | Single codebase, unified telemetry, no deployment per-repo overhead |
| **DevEx** | Consistent experience across company, predictable governance |
| **Leadership** | One version, one audit trail, measurable operational impact |
| **Infrastructure** | No distributed state, no sync overhead, minimal network usage |

---

## RISK MITIGATION: Why This is Safe

| Risk | Mitigation |
|------|-----------|
| Dependency on cortex-ai/cortex availability | Cached prompts; local fallback; GitHub reliability |
| Breaking changes in new version | 5-version backward compat; staged rollout; telemetry detects issues |
| User data exposure | Local-first telemetry; opt-in per transmission; hashed identifiers |
| User confusion ("Is this the latest?") | Version hash in CORTEX.prompt; visible in every response header |
| Regional latency (fetch from GitHub) | Prompt cached locally after first load; minimal network overhead |

---

## DECISION: Why This Beats Current Design

**Current Design Problems:**
- Distributed state across N repos = governance fragmentation
- O(N) operational burden = doesn't scale
- Manual updates per repo = user friction
- N separate telemetry streams = no unified insights

**Proposed Design Benefits:**
- Centralized authority (cortex-ai/cortex) = single source of truth
- O(1) operational model = scales infinitely
- Automatic updates = zero user friction
- Unified telemetry = powerful insights for improvement

**Strategic Implication:** One-step deployment means CORTEX can be adopted by 100+ teams with near-zero friction. Current design cannot scale beyond 5-10 repos before becoming unmaintainable.

---

## NEXT STEPS

1. **Approve architecture:** Centralized top-level repo + lightweight child repo setup
2. **Refactor cortex-master.yaml:** Replace PHASE-DEPLOYMENT with correct model
3. **Define CORTEX.prompt:** Template structure, MCP tool registry, versioning strategy
4. **Update copilot-instruction.md:** Integration points, expected behaviors
5. **Implement telemetry endpoint:** Server-side aggregation pipeline
6. **Go-to-market:** One-file adoption playbook for company repos

**Estimated effort:** 2 weeks (vs. current design's 60 hours per deployment point)

---

## RECOMMENDATION

**✅ ADOPT the centralized deployment model.**

This is not just more efficient—it's the only design that scales while maintaining governance integrity and operational control. The current design treats CORTEX as a product to install; the right design treats it as a service to reference.

